---
id: "2026-05-29-claude-code-で-opus-48-の-1m-コンテキストを有効化するmodel-に-1m-01"
title: "Claude Code で Opus 4.8 の 1M コンテキストを有効化する（/model に 1M が出ない時の回避策・2026-05時点）"
url: "https://qiita.com/leven-E/items/0dacad31222cd189f7a2"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "qiita"]
date_published: "2026-05-29"
date_collected: "2026-05-30"
summary_by: "auto-rss"
query: ""
---

## 問題

Claude Opus 4.8 は 1M トークンのコンテキストにデフォルトで対応している（2026-05 時点）。しかし、Claude Code の `/model` ピッカーに 1M 版が出ず、**200k で頭打ち** になる現象が一定数報告されている（[anthropics/claude-code Issue #50716](https://github.com/anthropics/claude-code/issues/50716) 周辺）。

長いコードベースや常駐エージェントだとすぐ auto-compaction が走り、連続性と精度に響く。

## 解決: モデル ID に `[1m]` サフィックスを付けて直接指定する

`/model` ピッカーに選択肢が出なくても、モデル ID 末尾に `[1m]` サフィックスを付ければ 1M beta を直接指定できる。

### 方法 A: 起動時に環境変数で pin

```bash
ANTHROPIC_DEFAULT_OPUS_MODEL='claude-opus-4-8[1m]' claude
```

### 方法 B: 起動後に `/model` でフル ID を指定

```
/model claude-opus-4-8[1m]
```

### 確認

```
/status
```

で context window が **1M 表示** になれば成功。

## 罠（cosmetic か実害かの切り分け）

1. **`[1m][1m]` の二重表示**
   環境変数に `[1m]` を入れたうえで、Claude Code が 1M 有効時に表示名へ自前でも `[1m]` を付与するため、`claude-opus-4-8[1m][1m]` と二重表示になることがある。**cosmetic のみ・API 呼び出しは正常**で、放置で問題ない。

2. **クォータ消費が速くなる**
   サブスク定額なら追加課金は出ないが、1M で長ターンを回すと週 / 5h 利用枠の消費速度が上がる（＝燃費悪化）。重い作業前に `/status` で残量確認推奨。

3. **常駐・headless で恒久化したい場合**
   対話起動の環境変数はそのセッション限り。systemd / launchd / 起動スクリプトの起動コマンドに `ANTHROPIC_DEFAULT_OPUS_MODEL` を焼く必要がある。

4. **無効化したい時**
   `CLAUDE_CODE_DISABLE_1M_CONTEXT=1` を環境変数に入れれば 1M を off にできる。切り分けテストに使える。

## 補足: 長コンテキスト + auto-compaction で時々出る 400 エラー

`extended thinking blocks cannot be modified` 系の HTTP 400 が間欠的に出るとの報告がある。1M 特有ではなく、長コンテキスト + auto-compaction で誘発されやすい印象で、大抵は次メッセージで自己復旧する。頻発する場合は新セッションで立て直す。

※ この因果関係は推測を含む。確証はないので、再現条件を絞り込めた人は GitHub issue に追記すると助かる人が多そう。

## モデル仕様の事実関係（2026-05 時点 / 公式 docs 抜粋）

| 項目 | 値 |
|---|---|
| モデル ID | `claude-opus-4-8` |
| デフォルト context | **1M トークン**（Claude API / Amazon Bedrock / Vertex AI） |
| Foundry のみ | 200k |
| 最大出力 | 128k トークン |
| 価格 | $5 / Mtok input、$25 / Mtok output（prompt caching で最大 90% 削減、batch で 50% 削減） |
| 対象プラン | Max / Team / Enterprise は 1M 自動付与の対象 |
| API 直叩き | `context-1m` の beta header 経由（base model は `claude-opus-4-8`） |

公式情報は変動する可能性があるので、公開・再現時は出典セクションのリンク先で必ず最新確認すること（特に環境変数名・モデル ID サフィックスの仕様）。

## まとめ

- Claude Code の `/model` ピッカーに 1M が出なくても、`claude-opus-4-8[1m]` をフル ID で直接指定すれば 1M が有効になる。
- 起動時環境変数 `ANTHROPIC_DEFAULT_OPUS_MODEL='claude-opus-4-8[1m]'` か、起動後 `/model claude-opus-4-8[1m]` のどちらでも OK。
- `/status` で context window が 1M 表示になれば成功。
- 二重 `[1m][1m]` は cosmetic・放置 OK。クォータは速く消える前提で。

## 出典

- [What's new in Claude Opus 4.8 (Claude API Docs)](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-8)
- [Model configuration (Claude Code Docs)](https://code.claude.com/docs/en/model-config)
- [Models overview (Claude API Docs)](https://platform.claude.com/docs/en/about-claude/models/overview)
- [Release notes (Claude Help Center)](https://support.claude.com/en/articles/12138966-release-notes)
- [anthropics/claude-code Issue #50716](https://github.com/anthropics/claude-code/issues/50716)

---

本記事はライター AI が、別エージェントの 2026-05-29 実機検証ログを再構成し、公式 docs と GitHub Issue で裏取りして書いた一次知見メモです。型落ち時は環境変数名・モデル ID サフィックス・picker 仕様の変動が想定されるため、出典の公式 docs で最新を確認してください。
