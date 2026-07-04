---
id: "2026-07-04-claude-code-opus-48-が数分固まる問題188セッション実測したら原因はapiでもネ-01"
title: "Claude Code (Opus 4.8) が数分固まる問題、188セッション実測したら原因はAPIでもネットワークでもなかった"
url: "https://zenn.dev/yuki_fujisawa/articles/a155d388e61acc"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "AI-agent", "Python", "zenn"]
date_published: "2026-07-04"
date_collected: "2026-07-05"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code を使っていると、応答が数分間「無音」になる停滞に遭遇することがあります。特にOpus 4.8で頻発していたため、体感や推測ではなく**セッションログの実測**で原因を特定しました。

この記事で分かること

* Claude Code の停滞を定量調査する方法(ログの場所と集計の考え方)
* 「固まって見える」現象の意外な正体
* 停滞を減らすための、標準機能ベースの実装(コード付き)

対象読者: Claude Code を日常的に使うエンジニア、subagent / hooks をまだ活用していない人。

## TL;DR

* 60秒超の停滞 **376件のうち、本当の「API待ち」は1件だけ**。残り375件は、止まっていたのではなくモデルがトークンを出し続けている「生成中」だった(分類の定義は後述)
* 正体は、重いturnでthinking + 出力を数千〜数万トークン一気に生成する長考。完了まで画面が無音になる
* サーバ混雑・巨大コンテキスト・生成速度の差は、いずれも実測で棄却
* 対策の本命は「**親 turn に探索を溜めない**」こと。探索専用のsubagentへの委譲を、定義・規則・監視の三層で構造化した

## 調査方法

### ログの場所

Claude Code はセッションの全イベントを JSONL で記録しています。

```
~/.claude/projects/<プロジェクトごとのディレクトリ>/<セッションID>.jsonl
```

各行に `type`(user / assistant)、`timestamp`、`message.model`、`message.usage`(トークン内訳)が入っており、これだけで応答レイテンシの分析ができます。

### 計測の定義

**応答 gap** = ユーザー入力(または tool 結果)の記録から、次の assistant 記録までの経過秒数。体感の「待ち時間」に相当します。

集計スクリプトの骨子は以下の通りです

```
import json
from datetime import datetime
from pathlib import Path

gaps = {}  # model -> [gap_seconds]

for f in Path.home().glob(".claude/projects/*/*.jsonl"):
    prev_ts = None
    for line in open(f, encoding="utf-8", errors="replace"):
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = rec.get("timestamp")
        if not ts:
            continue
        t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if rec["type"] == "user":
            prev_ts = t
        elif rec["type"] == "assistant" and prev_ts:
            model = rec["message"].get("model", "?")
            gap = (t - prev_ts).total_seconds()
            if 0 <= gap < 3600:
                gaps.setdefault(model, []).append(gap)
            prev_ts = None
```

### 停滞中の「状態」の分類

gap(停滞)の間にシステムが取りうる状態は、大きく2つです。

| 状態 | 中で起きていること | ログ上の見え方 |
| --- | --- | --- |
| **待ち** | API がまだトークンを返し始めていない(キュー滞留・接続・リトライ) | gap のわりに output\_tokens がほぼゼロ |
| **生成中** | モデルが thinking / 本文のトークンを出し続けている(長い thinking は画面に出ないため無音に見える) | gap に見合う大量の output\_tokens |

判別は**出力レート = `message.usage.output_tokens` ÷ gap 秒**で行い、5 tok/s 未満を「待ち」、以上を「生成中」と分類しました。応答自体が失敗したケースは `isApiErrorMessage` 付きの別レコードになるため、エラーとして別集計できます。

計測対象: 直近7日・188セッション・約14,000 turn。

## 結果1: 4つの仮説はすべて棄却された

停滞の原因としてまず疑うのはこのあたりだと思います。全部実測で消えました。

| 仮説 | 検証方法 | 結果 |
| --- | --- | --- |
| API 待ち・リトライ | gap 中の出力レートを計測(出力ほぼゼロ = 待ち) | **376件中1件のみ**。残りは生成継続中 → 棄却 |
| サーバ混雑・ネットワーク(529 / 接続エラー) | エラー記録の分布を集計 | 41件が**単一セッションに集中**した突発事象。時間帯も分散 → 恒常要因ではない |
| 巨大コンテキスト | 停滞 turn の入力トークン量と突合 | 400k 超は **2/376** のみ(中央値 153k)→ 無相関 |
| 生成速度が遅い | モデル別 tok/s を計測 | 3モデルほぼ同等(79 vs 88 tok/s)→ 棄却 |

## 結果2: モデル比較 — 差が出るのは「裾」だけ

| モデル | 中央値 | p90 | p99 | 最大 | >120s 停滞率 | 生成速度 |
| --- | --- | --- | --- | --- | --- | --- |
| **Opus 4.8** | 6.6s | 40.2s | **167s** | **945s** | **1.7%** | 79 tok/s |
| Fable 5 | 7.2s | 32.3s | 116s | 349s | 0.9% | 70 tok/s |
| Sonnet 5 | 4.8s | 19.5s | 79s | 451s | 0.5% | 88 tok/s |

面白いのは、**中央値と生成速度はほぼ同等**という点です。普段の応答は速い。差が出るのは p99 以降の「裾」だけで、Opus 4.8 の 120秒超停滞は Sonnet 5 の約3.4倍でした。

## 根本原因: 長考生成 turn

消去法で残り、実測でも一致した結論

> 複雑な依頼を受けた turn で、thinking + 出力を数千〜数万トークン一気に生成する。生成速度は普通でも、量が多いので完了まで数分かかり、その間画面が無音になる。

ここで「では、なぜ長考が起きるのか」まで遡ると、原因は2つの掛け算に分解できます。

| 層 | 内容 | 実測根拠 |
| --- | --- | --- |
| **誘因**(使い方側) | 重い turn を作る使い方 — 複合依頼(調査+設計+実装を1メッセージに詰める)が代表例。探索結果を親 turn に溜め込むだけでも肥大する | 停滞は76セッションに分散し、特定の依頼だけでは説明できない |
| **素因**(モデル側) | Opus 4.8 は重い turn で thinking を深くする傾向 | 速度・中央値は同等なのに「裾」だけ Sonnet 5 の3.4倍 = 同じ重さの turn でより長く考える |

```
誘因(重い turn を作る使い方)× 素因(Opus 4.8 の深い thinking)
  → 親 turn の thinking が肥大
  → 生成完了まで無音
  → 「固まった」と体感
```

つまりこれは障害ではなく、**高性能モデルに重い turn を渡したときの仕様上の挙動**です。素因(モデルの thinking 傾向)は使う側から変えられないので、**介入点は誘因側** — 対策は「待つ・リトライする」ではなく「**重い turn を作らない**」になります。

## 対策: 探索の subagent 委譲を構造化する

誘因には2つの形がありました。「探索の溜め込み」と「複合依頼」です。

* **探索の溜め込み** → 本章の主役。探索を軽量 subagent へ確実に逃がす仕組みを三層で作る
* **複合依頼** → 直接対策は「依頼を段階に分ける」(調査 → 結果を見て設計 → 実装)という運用習慣。ただし習慣は形骸化しやすい。委譲の仕組みがあれば、複合依頼を受けた場合でも調査部分は自動的に親から剥がれるため、**仕組み側を本命**に置く

そこで、探索を軽量 subagent へ確実に逃がす仕組みを三層で作ります。

### 第1層: 探索専任 subagent の定義(標準機能)

`~/.claude/agents/explorer.md` を作ります。ポイントは frontmatter の `model:` / `effort:` — **呼び出すだけで必ず軽量実行になる**よう、定義に焼き込みます。

```
---
name: explorer
description: Read-only exploration specialist for
  multi-file investigation, spec reading, log scans,
  and web research. Returns a structured summary
  (path:line + verdict) only — never raw dumps.
tools: ["Read", "Grep", "Glob", "Bash", "WebFetch", "WebSearch"]
model: sonnet     # ← モデルを焼き込み(Sonnet 5)
effort: medium    # ← 思考量も固定
---

# Explorer

Role: 読み取り専用の探索専任。multi-file grep / 仕様調査 /
log scan / web research を引き受け、構造化サマリ
(path:line + 判定)のみ返す。mutation 禁止 —
Edit/Write は持たず、Bash は読み取り操作に限定。
raw dump 返却禁止。
```

同様に、解釈が不要な機械的 grep・件数集計用に `scanner.md`(`effort: low`)も用意しました。

### 第2層: 委譲規則を CLAUDE.md に書く

定義があっても使われなければ意味がないので、ルーティングを指示ファイルに明文化します。

```
## 探索の委譲

- 読み取り専用の探索(複数ファイル grep / 仕様調査 /
  ログ調査 / Web リサーチ)は subagent へ委譲する
  - 意味理解を伴う調査 → explorer
  - 機械的な grep 列挙・件数集計 → scanner
- 読み取りツールを連続 8 回以上使う見込み、
  または 5 ファイル以上を読む探索は委譲必須
- subagent は構造化サマリ(path:line + 判定)のみ返す
- 編集・commit は親セッションが行う(subagent 内での mutation 禁止)
```

「連続8回」「5ファイル以上」のように**発火条件を定量化**しておくのがコツです。曖昧な「なるべく委譲」は形骸化します。

### 第3層: 委譲忘れを hooks で監視する

規則を書いても、委譲忘れは起きます。そこで Claude Code 標準の **hooks 機構**(`Stop` イベント)に自作の検査スクリプトを登録します。

```
{
  "env": {
    "CLAUDE_DELEGATION_CHECK": "1",
    "CLAUDE_DELEGATION_STREAK_N": "8"
  },
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/scripts/stop_delegation_check.py",
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```

検査スクリプトの中身は「transcript を走査して、read-only ツールが委譲なしに連続 N 回続いた形跡があれば警告ファイルを書く」だけ。警告は次回セッション開始時に表示され、**作業は止めません**。

`stop_delegation_check.py` の実装例

```
#!/usr/bin/env python3
"""Stop hook: 探索委譲の検査 — read-only ツールが委譲なしに
連続 N 回続いた形跡があれば警告ファイルを書く(warn のみ、block しない)."""
import json
import os
import re
import sys
from pathlib import Path

READONLY_TOOLS = {"Read", "Grep", "Glob", "Bash"}            # 探索系
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}  # 編集系
DELEGATION_TOOLS = {"Agent", "TaskCreate"}                   # 委譲成立
# Bash のうち変更系コマンドは連続数を切る(正規表現の近似で十分 — warn 用途)
BASH_MUTATE_RE = re.compile(
    r"(?:^|[;&|]\s*)(?:rm|mv|cp|mkdir|touch|sed\s+-i"
    r"|git\s+(?:commit|push|add|reset|checkout))\b|>>?\s*\S"
)
WARN_FILE = Path.home() / ".claude" / "delegation_warn.md"

def scan_max_streak(tpath: str) -> int:
    """transcript を走査し、read-only 連続数の最大値を返す."""
    max_streak = streak = 0
    with open(tpath, encoding="utf-8", errors="replace") as f:
        for line in f:
            if '"assistant"' not in line:  # 前段フィルタで json.loads を節約
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("type") != "assistant":
                continue
            for c in rec.get("message", {}).get("content", []):
                if not isinstance(c, dict) or c.get("type") != "tool_use":
                    continue
                name, inp = c.get("name", ""), c.get("input") or {}
                if name in DELEGATION_TOOLS or name in EDIT_TOOLS:
                    streak = 0  # 委譲成立 or 編集フェーズ移行でリセット
                elif name in READONLY_TOOLS:
                    if name == "Bash" and BASH_MUTATE_RE.search(
                        str(inp.get("command") or "")
                    ):
                        streak = 0
                    else:
                        streak += 1
                        max_streak = max(max_streak, streak)
    return max_streak

def main() -> int:
    if os.environ.get("CLAUDE_DELEGATION_CHECK", "0") != "1":
        return 0
    data = json.load(sys.stdin)  # Stop hook は stdin で JSON を受け取る
    tpath = str(data.get("transcript_path") or "")
    if not os.path.exists(tpath):
        return 0
    threshold = int(os.environ.get("CLAUDE_DELEGATION_STREAK_N", "8"))
    if scan_max_streak(tpath) >= threshold:
        WARN_FILE.write_text(
            "探索の subagent 委譲忘れ: read-only ツールが委譲なしに"
            f"{threshold} 回以上連続。explorer / scanner への委譲を検討。\n"
        )
    elif WARN_FILE.exists():
        WARN_FILE.unlink()  # 健全なセッションなら古い警告を消す
    return 0  # 常に exit 0 = warn のみで block しない

if __name__ == "__main__":
    sys.exit(main())
```

警告の表示側は、SessionStart hook に1行足すだけです:

```
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cat ~/.claude/delegation_warn.md 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

#### なぜ Stop イベントなのか

1. **「連続 N 回」の判定には応答全体の集計が必要** — Stop は応答完了時に transcript のパスを受け取れる
2. **1応答に1回しか走らない** — PreToolUse / PostToolUse に置くと探索のたびにスクリプトが走り、遅さ対策が遅さを足す本末転倒になる
3. **誤検知を含む検査なので「事後に warn」が正解** — ブロックすると正当な作業まで止めてしまう

## 効果の考え方

この構成のポイントは、対策がすべて「生成量を削る」方向を向いていることです。

| 層 | 削るもの |
| --- | --- |
| explorer / scanner 定義 | 探索 turn の thinking 量(Sonnet 5 + effort 固定で構造的に保証) |
| 委譲規則 | 親 turn に流れ込む探索コンテキスト |
| Stop hook 監視 | 規則の形骸化(委譲忘れの検知) |

副次効果として、探索が Sonnet 5 に流れるぶん**コストも下がります**。

## まとめ

* Claude Code の「固まる」問題は、ログを実測すると原因を特定できる(JSONL に全部残っている)
* Opus 4.8 の停滞の正体は API でもネットワークでもなく**長考生成**(376件中375件)
* 対策は「重い turn を作らない」こと。探索専任 subagent(model/effort 焼き込み)+ 委譲規則の定量化 + Stop hook 監視の三層で構造化する
* subagent の model/effort 指定・hooks はいずれも Claude Code の標準機能なので、今日から同じ構成を作れる

## 注意

* 数値はすべて筆者の一環境における直近7日間の実測値です。負荷状況・使い方によって変わります
* Claude Code の仕様(hooks / subagent frontmatter)はバージョンにより変更される可能性があります。公式ドキュメント([Model configuration](https://code.claude.com/docs/en/model-config.md) / [Sub-agents](https://code.claude.com/docs/en/sub-agents.md) / [Hooks](https://code.claude.com/docs/en/hooks.md))を併せて確認してください
