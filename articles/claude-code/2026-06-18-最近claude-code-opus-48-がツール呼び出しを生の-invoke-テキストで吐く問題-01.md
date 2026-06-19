---
id: "2026-06-18-最近claude-code-opus-48-がツール呼び出しを生の-invoke-テキストで吐く問題-01"
title: "最近Claude Code (Opus 4.8) がツール呼び出しを生の `<invoke>` テキストで吐く問題を調べた（tool call could not be parsed の正体）"
url: "https://qiita.com/yousan/items/f9e11dd44bf61c7ae74a"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "Python", "qiita"]
date_published: "2026-06-18"
date_collected: "2026-06-19"
summary_by: "auto-rss"
query: ""
---

## TL;DR

最近、こういうエラーがでます。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/47327/d0202775-427f-443a-90ef-58ca51bef4a7.png)


- Claude Code を **Opus 4.8** で使っていると、ごく稀に **ツール呼び出し（Bash など）が実行されず、`<invoke name="Bash">…</invoke>` という生のマークアップがそのまま出力**されることがあります。あるいは `The model's tool call could not be parsed (retry also failed)` というエラーで止まります。
- 自分の環境で実測したところ、**この症状は Opus 4.8 でしか起きていませんでした**（Fable 5 / Sonnet 4.6 / Haiku 4.5 では 0 件）。発生率は Opus 4.8 で約 **0.2%/ターン**（約 470 ターンに 1 回）。
- これは **上流（モデル / Claude Code CLI）側の既知バグ**で、[anthropics/claude-code](https://github.com/anthropics/claude-code) に同症状の Issue が多数上がっています。**自分のコードのせいではありません**。
- トリガは **1M context + `/compact` + 「散文を書いた直後にツール呼び出し」+ CJK（日本語）+ 長寿命セッションの `--resume`** です。条件が重なるほど出やすくなります。
- 回避策は「モデルを Opus 4.7 / Sonnet に下げる」「`CLAUDE_CODE_DISABLE_1M_CONTEXT=1`[^env-1m] で 200K に戻す」「壊れたターンを含むセッションを resume しない」などです。

---

## 何が起きたか

Discord から Claude Code を動かすフロントエンド（OSS の [c-lord](https://github.com/yousan/c-lord)）越しに長時間セッションを回していたら、Claude の返信に突然こういう「生のツール呼び出し構文」が混ざって流れてきました。

```text
全 CI green。マージ→本番デプロイに進みます。まず現在のログを確認します。

count
<invoke name="Bash">
<parameter name="command">grep -n "no tmux manager" /var/log/app.log | tail -5</parameter>
<parameter name="description">Check current log</parameter>
</invoke>
```

本来 Claude Code は、ツールを使うときは内部の **構造化された `tool_use` ブロック** として呼び出し、CLI 側がそれを実行します。ところがこのときは、**ツール呼び出しが「ただのテキスト」として吐き出されてしまい、実行されていません**。散文（「まずログを確認します」）の直後に、`<invoke …>` がそのまま文字列として出ています。

`<invoke>` の直前にある謎の `count` も特徴的でした（後述しますが、これは上流 Issue でも報告されている指紋です）。

別パターンとして、CLI が「ツール呼び出しのはずなのにパースできない」と判断すると、こう出て止まります。

```text
API Error: The model's tool call could not be parsed (retry also failed).
```

どちらも根は同じ「**モデルがツール呼び出しを壊れた形で出力する**」現象です。

## どう調べたか（自分の環境でも再現可能）

Claude Code は会話の生ログを `~/.claude/projects/<エンコードされた cwd>/*.jsonl` に残しています。assistant メッセージの `content` を見れば、**ツール呼び出しが `tool_use` ブロックとして出たのか、`text` ブロックに `<invoke …>` として漏れたのか**が判別できます。

まずは雑に grep で当たりを付けます。

```bash
# text ブロックに生の invoke 構文が混ざっている transcript を抽出
grep -l "invoke name=" ~/.claude/projects/*/*.jsonl
```

ヒットしたら、モデル別に件数を出して「特定モデル固有か / どのモデルでも一定率で出るのか」を切り分けます。これが今回の肝です。

```python
import json, glob
from collections import Counter

turns = Counter()   # モデル別 assistant ターン総数
leaks = Counter()   # うち <invoke> がテキスト漏れしたターン数

for f in glob.glob("/home/USER/.claude/projects/*/*.jsonl"):
    for line in open(f, encoding="utf-8", errors="replace"):
        try:
            o = json.loads(line)
        except Exception:
            continue
        m = o.get("message")
        if not isinstance(m, dict) or m.get("role") != "assistant":
            continue
        model = m.get("model", "?")
        turns[model] += 1
        c = m.get("content")
        if isinstance(c, list) and any(
            isinstance(b, dict) and b.get("type") == "text"
            and ("invoke name=" in b.get("text", "") or "antml:invoke" in b.get("text", ""))
            for b in c
        ):
            leaks[model] += 1

for model, n in turns.most_common():
    lk = leaks.get(model, 0)
    print(f"{model:24s} turns={n:6d}  leaks={lk:3d}  rate={lk/n*100:.3f}%")
```

## 結果：Opus 4.8 だけが漏らしていた

直近 1 週間ぶん（transcript 197 本 / assistant ターン 13,731）を集計した結果がこれです。

| モデル | assistant ターン | 漏れ件数 | 漏れ率 |
|---|---:|---:|---:|
| **claude-opus-4-8** | 11,231 (81.8%) | **24** | **0.214%** |
| claude-fable-5 | 2,215 (16.1%) | 0 | 0% |
| claude-sonnet-4-6 | 211 (1.5%) | 0 | 0% |
| claude-haiku-4-5 | 42 (0.3%) | 0 | 0% |

ポイントは **Fable 5 が 2,215 ターンも回って漏れ 0 件**だったことです。もし「どのモデルでも一定率で漏れる」なら、Opus の 0.214% を当てはめれば Fable でも期待値で 4〜5 件は出るはずです。それが 0 ということは、**「単に Opus を一番使っているから件数が多い」という交絡では説明できず、Opus 4.8 に固有の挙動**だと言えます。

## 正体：上流の既知バグだった

「Opus 4.8 固有なら、同じことで困っている人が大量にいるはず」と思って検索したら、まさにそのとおりでした。[anthropics/claude-code](https://github.com/anthropics/claude-code) に同症状の Issue がクラスタで上がっています。

- **[#64190 After /compact on Opus 4.8 (1M), whole tool calls emitted as `<invoke>` text instead of executing](https://github.com/anthropics/claude-code/issues/64190)**
  ほぼ完全一致です。`/compact` 後の **Opus 4.8（1M context）** でツール呼び出し全体が生の `<invoke>` テキストになり実行されません。**Opus 4.7 では出ない 4.8 のリグレッション**と報告されており、「autonomous / looping エージェントでは silent failure になり危険」と指摘されています。
- **[#64658 Opus 4.8 "tool call could not be parsed" still reproduces](https://github.com/anthropics/claude-code/issues/64658)**
  `tool call could not be parsed`。**Opus 4.8 のみ**（4.7・Sonnet 4.6 では出ない）で、多数の Issue の duplicate 親として既知追跡中です。トリガに **CJK テキスト + コード** が挙がっており、日本語で使っていると踏みやすくなります。
- **[#60584 tool_use input intermittently malformed — emits literal "court"/"`<invoke>`" text](https://github.com/anthropics/claude-code/issues/60584)**
  壊れた出力に `"court"` という謎トークンが前置される、という報告です。冒頭で触れた自分の環境の `count` と同じ指紋で、同一現象だと確信できました。
- [#65230 Opus 4.8 outputs tool calls as code fences instead of executing them](https://github.com/anthropics/claude-code/issues/65230)
- [#61133 tool call could not be parsed (retry also failed) since 2026-05-20](https://github.com/anthropics/claude-code/issues/61133)
- [#62123 Anthropic API Error: Model's tool call could not be parsed](https://github.com/anthropics/claude-code/issues/62123)
- [#63875 Recurring "tool call could not be parsed" interrupts sessions](https://github.com/anthropics/claude-code/issues/63875)

日本語の解説記事もあります。

- [頻発する "tool call could not be parsed" エラーの原因と対策（note）](https://note.com/quirky_hosta1908/n/n7cb7f431b52d)
- [Opus 4.8 でツール呼び出しが頻繁に stall する（note）](https://note.com/fortune649490/n/n8dff254af49b)

## なぜ起きるのか（根本原因の仮説）

上流 Issue で語られている仮説を要約するとこうです[^root-cause]。

- **`stop_reason: tool_use` なのに `tool_use` ブロックが 0 個**、という状態がたまに発生します。モデルがツール呼び出しを構造化ブロックではなく、**レガシーな `<invoke>` XML をテキストチャネルに**出力してしまいます。
- 特に **1M context + 強い thinking** の組み合わせ、そして **`/compact` 後**に出やすいです。compaction でサマリ内に過去の `tool_use` が「文字列」として畳み込まれ、モデルがそれを **テキストとして pattern-complete** してしまう、という見立てです。
- **散文をツール呼び出しの直前に書くと誘発されやすい**です（"Now I'll edit X:" の直後に Edit、など）。実際、自分の環境で漏れたターンは全部「散文回答 + `<invoke>`」の形でした。
- **一度壊れたターンを含むセッションは self-reinforce する**（`--resume` すると壊れ方が伝播する）。自分の環境でも、漏れは長寿命の resume セッションに集中していました（特定スレッドに 11 件 / 6 件と偏っていました）。

## 対策・回避策

バグ自体は上流案件なので根治はアップデート待ちですが、**発生頻度はこちらの設定で下げられます**。トレードオフがあるので用途で選びます。

1. **モデルを下げる** — `claude-opus-4-7` か `claude-sonnet-4-6` に切り替えます。4.8 固有なので確実に回避できます（その代わり Opus 4.8 の性能は諦めることになります）。
2. **1M context を切る** — 環境変数 `CLAUDE_CODE_DISABLE_1M_CONTEXT=1`[^env-1m] で 200K に戻します。確実ですが長い文脈を失います。
3. **auto-compact を制御する** — 公式の環境変数 [`DISABLE_AUTO_COMPACT=1`](https://code.claude.com/docs/en/settings) で自動 compaction を完全に無効化できます。より細かく閾値を変えたい場合は `CLAUDE_CODE_AUTO_COMPACT_WINDOW=512000`[^env-compact] を試す手もありますが、#64190 は「`/compact` 自体がトリガ」とも報告しており、compact を増やすと逆効果の可能性もあるので過信は禁物です。
4. **壊れたセッションを resume しない** — malformed ターンが出たら、そのセッションは畳んで新規に切り直します（self-reinforce を断つ）。
5. **プロンプトの形を工夫する** — ツール呼び出しをターンの先頭に置き、説明はツール結果の後に回します（[#60584](https://github.com/anthropics/claude-code/issues/60584) で報告されている回避パターン）。長い前置きの直後にツールを呼ばないようにします。

## まとめ

- Claude Code で `<invoke name="…">` の生テキストや `tool call could not be parsed` が出るのは、**Opus 4.8 固有の上流バグ**です。自分のコードを疑う前に、まず `~/.claude/projects/*.jsonl` を grep してモデル別に切り分けるのが速いです。
- 交絡を排除するには「使っていない / 少数派のモデルでも漏れているか」を見るのが効きます（今回は Fable 5 の 0 件が決め手でした）。
- 当面はモデル選択・1M context・compact・resume の運用でしのぎ、上流の修正を待ちます。

[^env-1m]: `CLAUDE_CODE_DISABLE_1M_CONTEXT` は Claude Code バイナリ（v2.1.181）内に確認できる環境変数です。`1` を設定すると 1M context window を無効化して従来の 200K に戻します。公式ドキュメントには現時点で記載がありませんが、[#64190](https://github.com/anthropics/claude-code/issues/64190) など複数の Issue で言及されています。

[^env-compact]: `CLAUDE_CODE_AUTO_COMPACT_WINDOW` は Claude Code バイナリ（v2.1.181）内に確認できる環境変数です。コンテキスト圧縮を起動するトークン数のしきい値を指定します。公式ドキュメントには現時点で記載がありません。auto-compact を完全に止める公式の環境変数は [`DISABLE_AUTO_COMPACT`](https://code.claude.com/docs/en/settings) です。

[^root-cause]: 本セクションの仮説は [#64190](https://github.com/anthropics/claude-code/issues/64190)・[#64658](https://github.com/anthropics/claude-code/issues/64658)・[#60584](https://github.com/anthropics/claude-code/issues/60584) で報告・議論されている内容をもとにまとめたものです。

## 参考リンク

- [anthropics/claude-code #64190 — After /compact on Opus 4.8 (1M), whole tool calls emitted as `<invoke>` text](https://github.com/anthropics/claude-code/issues/64190)
- [anthropics/claude-code #64658 — Opus 4.8 "tool call could not be parsed" still reproduces](https://github.com/anthropics/claude-code/issues/64658)
- [anthropics/claude-code #60584 — tool_use input intermittently malformed — emits literal "court"](https://github.com/anthropics/claude-code/issues/60584)
- [anthropics/claude-code #65230 — Opus 4.8 outputs tool calls as code fences instead of executing them](https://github.com/anthropics/claude-code/issues/65230)
- [anthropics/claude-code #61133 — tool call could not be parsed (retry also failed) since 2026-05-20](https://github.com/anthropics/claude-code/issues/61133)
- [anthropics/claude-code #62123 — Anthropic API Error: Model's tool call could not be parsed](https://github.com/anthropics/claude-code/issues/62123)
- [anthropics/claude-code #63875 — Recurring "tool call could not be parsed" interrupts sessions](https://github.com/anthropics/claude-code/issues/63875)
- [Claude Code 設定リファレンス（環境変数一覧）](https://code.claude.com/docs/en/settings)
- [tool call could not be parsed の原因と対策（note）](https://note.com/quirky_hosta1908/n/n7cb7f431b52d)
- [Opus 4.8 でツール呼び出しが頻繁に stall する（note）](https://note.com/fortune649490/n/n8dff254af49b)
