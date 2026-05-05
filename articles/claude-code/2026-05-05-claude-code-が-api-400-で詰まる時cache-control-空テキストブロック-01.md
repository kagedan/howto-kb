---
id: "2026-05-05-claude-code-が-api-400-で詰まる時cache-control-空テキストブロック-01"
title: "Claude Code が API 400 で詰まる時——cache_control 空テキストブロックの根本原因と復旧"
url: "https://qiita.com/yurukusa/items/fbe51b3ce6b025dd089c"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-05-05"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

2026 年 4-5 月の Claude Code の自動運用の中で、 短いセッションでも突然 `400` エラーで動かなくなる事故が複数回起きた。 GitHub Issue を遡ると同じ根本原因 (cache_control が空テキストブロックに付いている状態) で 12 本以上のスレッドが立っていた。 個別の報告は散発的だが、 1 つの原因にまとまっている。

公式の更新の通知には記載が無いため、 利用者の側で発見して、 利用者の側で復旧する必要がある型の不具合。 この記事は実際の復旧の手順と、 5 つの予防の指針をまとめる。

## 何が起きるか

短いセッションでも突然、API から `400` エラーが返り続けて作業が止まる。代表的なメッセージは次の 3 つで、順番にこの形で出ることが多い。

```
messages.N.content.M.text: cache_control cannot be set for empty text blocks
messages: text content blocks must be non-empty
```

「Try again」も `claude --resume` も同じエラーで止まる。新しいセッションを始めると直るが、それまでの文脈は捨てることになる。

## なぜ詰まるか

会話履歴のどこかの content block が `text: ""` のまま `cache_control: { type: "ephemeral" }` を付けた状態で残り、API がそれを拒否する。一度この壊れたブロックが履歴に入ると、再送のたびに同じブロックが含まれるので、resume も Try again も同じ理由で落ちる。

「短いセッションだから長文ではない」と感じても、ツールを 1 回使うごとに `assistant tool_use` と `user tool_result` の 2 メッセージが追加される。ツール多用のセッションなら数ターンで `messages[48]` 程度まですぐ伸びる。

## どんなときに発生しているか (2026 年 4-5 月の集積から)

- 画像をキャプションなしで貼り付けた直後
- ストリームの待機タイムアウト後の自動再送
- AskUserQuestion の回答が空のまま送られたとき
- セッション再開直後に履歴が壊れていたとき

GitHub Issue では同じ根本原因で別々のスレッドが 12 本以上立っている。本ガイドの公開前に各スレッドの本文を確認し、エラー文言と再現手順が一致するものだけを残した: #55369 / #55156 / #55302 / #55283 / #55118 / #54988 / #54421 / #54314 / #53632 / #50738 / #50681 / #50010 など。

## 壊れた行の見え方

JSONL の 1 行は 1 つのやり取りに対応し、 配列の中に複数の小さな塊が入る。 詰まりを起こす典型は、 中身の文字が空のまま、 印だけが付いている状態である。 API はそれを拒む。

具体的には、配列の中に次のような形のブロックが残っている。

```
{"type":"text","text":"","cache_control":{"type":"ephemeral"}}
```

最初の発見の手段は、 該当のファイルに対して以下を流して、 空の塊が何件あるかの大まかな見当を付けることである。

```
grep -c '"text":""' <session>.jsonl
```

0 件でも、 印のキーごと欠けた亜種で詰まっている可能性があるので、 0 件のときも次の節の復旧手順に進む。

## 現場での復旧手順

セッションは JSONL 形式で保存されているので、壊れたブロックを取り除けば文脈ごと復活できる。

1. 該当プロジェクトの session ファイルを探す
   - Linux/macOS: `~/.claude/projects/-<sanitized-cwd>/<session-id>.jsonl`
   - Windows: `%USERPROFILE%\.claude\projects\-<sanitized-cwd>\<session-id>.jsonl`
2. 元ファイルを別名で必ず先に保全しておく (`cp` で `.bak` を取る)
3. 空テキストブロックを除去するスクリプトを通す
4. 出力された `.fixed.jsonl` で元ファイルを置き換えて `claude --resume`
5. 念のため、 置き換え後のファイルに対して再度 `grep` で空の塊を数え、 0 件になっていることを確かめてから本格的に再開する

```python
import json, sys, pathlib

src = pathlib.Path(sys.argv[1])
dst = src.with_suffix('.fixed.jsonl')

with src.open(encoding='utf-8') as f, dst.open('w', encoding='utf-8') as g:
    for line in f:
        d = json.loads(line)
        msg = d.get('message')
        if isinstance(msg, dict) and isinstance(msg.get('content'), list):
            msg['content'] = [
                b for b in msg['content']
                if not (isinstance(b, dict) and b.get('type') == 'text' and not b.get('text'))
            ]
            if not msg['content']:
                continue  # 空になったメッセージは行ごと捨てる
        g.write(json.dumps(d, ensure_ascii=False) + '\n')

print(f'Wrote {dst}')
```

## 復旧スクリプトでも直らない時

スクリプトを通したあとでも `400` が再発する時は、 空テキストブロックではなく別の壊れ方が混ざっている可能性がある (画像の塊が壊れている、 道具の呼び出しと結果の対が崩れている、 など)。 その場合は、 文脈の損失を最小にする手順として次の 2 段に分けて対処する。

1. 詰まったやり取りの直近の進行を、 別の場所 (`mission.md` や引き継ぎメモ) に手で抜き書きする
2. 新しいやり取りを始め、 1 で抜き書きした内容を最初の 1 通として貼り付けて再開する

直近の本文だけを抜き出すには、 `jq` を使った 1 行の絞り込みが早い。

```
jq -r '.message.content[]?.text // empty' <session>.jsonl | tail -200
```

大半の文脈はこの出力から手で復元できる。

## 予防

- 画像をキャプションなしで貼らない。一文字でも文字を添える
- 「Stream idle timeout — partial response received」が出たときは、同じターンを再送せず、新しいプロンプトから始める
- 長時間セッションの再開地点は、履歴ではなく再開専用ファイル (mission.md など) に集約する。履歴破損で文脈を失っても、再開ファイルで復帰できる体制を作っておく

## 月次の安全チェック追加項目

- 重要セッションを始める前に session ファイルの場所を確認しておく
- セッションが API 400 で詰まったら、まず `claude --resume` を試す前に session ファイルをコピーしておく
- 長時間セッションは、内容が膨らむ前に区切ってコミット・記録する

## 参考

- 大元のエラーは Anthropic API 側のバリデーション (`cache_control` を空テキストブロックには設定できない) なので、Claude Code 側で送信前に空ブロックを落とすかキャッシュ印を外せば再発しなくなる
- 復旧スクリプトの肝は「空 text block を消す」ことと「全部消えたメッセージは丸ごと捨てる」こと。この 2 つで `400` が止まる
---
同じ時期に発生した別の根本原因の事故事例 (cache_creation の急増、 子エージェントが親の会話履歴を漏らす、 子エージェントの作業領域の境界の不在、 自動の運用での利用枠の焼き) は、 月次でまとめた解説の取り組みを始めた。 この記事の本文は 5 月号の事故事例の章の全文の抜粋で、 5/5 配信予定。
販売ページ: https://yurukusa.github.io/cc-safe-setup/safety-lab.html
