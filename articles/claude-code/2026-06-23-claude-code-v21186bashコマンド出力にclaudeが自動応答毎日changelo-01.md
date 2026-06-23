---
id: "2026-06-23-claude-code-v21186bashコマンド出力にclaudeが自動応答毎日changelo-01"
title: "Claude Code v2.1.186｜bashコマンド出力にClaudeが自動応答｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/c8e4090853e599e25b4a"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "qiita"]
date_published: "2026-06-23"
date_collected: "2026-06-23"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.186 で、インラインの bash コマンドの挙動がデフォルトで変わりました。実行結果を文脈に足すだけだったのが、Claude がその出力を読んで自動で返答するようになっています。`respondToBashCommands` を明示しない限り、デフォルトで全員に効きます。

## 今回の注目ポイント

1. **bash コマンド出力への自動応答** — インライン bash の結果に Claude が自動で反応。従来動作は `respondToBashCommands: false` で維持 (v2.1.186)
2. **MCP サーバーを CLI から認証** — `claude mcp login` / `claude mcp logout` が追加。`--no-browser` で SSH 越しも対応 (v2.1.186)
3. **named サブエージェントの権限制限が無視されていたバグを修正** — `Agent(type)` の deny ルールと `Agent(x,y)` の許可リストが効くように (v2.1.186)
4. **バックグラウンドサブエージェントの権限プロンプトをメインに表示** — 従来の自動拒否をやめ、どのエージェントの要求か明示 (v2.1.186)
5. **`/review <pr>` が `/code-review medium` と同じエンジンに統一** (v2.1.186)
6. **`CLAUDE_CODE_MAX_RETRIES` の上限が 15 に** — 無人運用は `CLAUDE_CODE_RETRY_WATCHDOG` へ誘導 (v2.1.186)

## bash の出力に Claude が口を挟むようになった

:::note alert
`!` 始まりの bash コマンドを多用しているなら、このアップデートで挙動が変わります。settings.json を確認してください。
:::

これまでインラインの bash コマンドは、出力を会話の文脈に積むだけでした。Claude はそれを黙って受け取り、次の指示を待つ。v2.1.186 からは、その出力に対して Claude が自動で返答します。

例えばテストコマンドを流すと、結果を見て「3 件落ちている、原因はここ」と続けて動く。出力を読ませてそのまま次の作業に繋げたいときは速くなります。逆に、ただ結果を貼っておきたいだけの場面では口数が増える。

従来どおり「文脈に足すだけ」に戻すなら、settings.json に 1 行:

```json
{
  "respondToBashCommands": false
}
```

## claude mcp login で CLI から認証が完結する

```bash
# 対話メニュー(/mcp)を開かずにサーバー認証
claude mcp login <name>
claude mcp logout <name>

# SSH 越しはブラウザを開かず stdin で
claude mcp login <name> --no-browser
```

MCP サーバーの認証が `/mcp` の対話メニュー専用ではなくなりました。CLI から直接 login / logout が叩けます。`--no-browser` を付けると認証フローを stdin にリダイレクトするので、SSH 先のサーバーでもブラウザなしで完了する。CI や踏み台サーバーなど、ブラウザを開けない環境で認証できます。

## 権限まわりの穴が塞がった

:::note warn
`Agent(type)` の deny ルールや `Agent(x,y)` の許可タイプ制限を権限設定に書いている場合、named サブエージェントの spawn でこれらが素通りしていました。v2.1.186 で enforce されます。
:::

サブエージェントを名前付きで spawn したとき、`Agent(type)` の拒否ルールと `Agent(x,y)` の許可タイプ制限が効いていなかったバグが修正されました。権限設定で spawn を絞っているなら、実際の挙動が変わります。

あわせて、バックグラウンドサブエージェントの権限プロンプトの扱いも変更。これまで自動拒否していたものを、メインセッション側にダイアログを出すようになりました。どのエージェントが要求しているか表示され、Esc でそのツールだけ拒否できる。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| 2.1.186 | 改善 | `/review <pr>` | レビューエンジンを `/code-review medium` に統一 |
| 2.1.186 | 追加 | `/workflows` | エージェント詳細にステータス絞り込み (`f` キー) |
| 2.1.186 | 追加 | `/plugin` | Installed タブに「Skills」セクション |
| 2.1.186 | 追加 | `teammateMode` | `"iterm2"` 設定を追加。`it2` CLI 不在時は警告 |
| 2.1.186 | 改善 | `claude mcp get/remove` | タイポ時に最も近いサーバー名を提案 |
| 2.1.186 | 改善 | skill frontmatter | kebab / snake / camel ケースを許容 |
| 2.1.186 | 修正 | streaming | スリープ復帰後の "Content block not found" を修正 |
| 2.1.186 | 修正 | `~~打ち消し~~` | アシスタント表示でチルダが残っていたのを修正 |
| 2.1.186 | 修正 | Workflow | `agent({schema})` の検証失敗ループを 5 回で中断 |

## まとめ

v2.1.186 の本体は、bash コマンド出力への自動応答と MCP の CLI 認証、そして権限制限の取りこぼし修正。特に `Agent(type)` の deny が効いていなかった件は、権限を絞っている構成だと実挙動が変わります。権限を絞っている構成なら、ここだけ確認しておけば足ります。
