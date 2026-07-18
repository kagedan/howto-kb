---
id: "2026-07-18-claude-code-v21212暴走ループにセッション上限毎日changelog解説-01"
title: "Claude Code v2.1.212｜暴走ループにセッション上限｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/9be8047b5f9980465623"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "qiita"]
date_published: "2026-07-18"
date_collected: "2026-07-19"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.212 で WebSearch とサブエージェント生成に、セッション単位の上限が入りました。どちらもデフォルト 200 回で頭打ち、無限に検索・委譲を繰り返すループを止める安全弁。あわせて Plan mode が許可なしにファイルを書き換えていたバグも塞がれました。

## 今回の注目ポイント

1. **WebSearch とサブエージェントにセッション上限** - どちらもデフォルト 200 回で頭打ち。暴走ループを止める安全弁 (v2.1.212)
2. **MCP ツールは 2 分で自動バックグラウンド** - 長い呼び出しでセッションが固まらなくなった (v2.1.212)
3. **`/fork` がバックグラウンドセッション化** - 会話を別セッションに複製して並行作業、旧来の挙動は `/subtask` に分離 (v2.1.212)
4. **Plan mode の権限バイパスを修正** - `touch` や `rm` を許可プロンプト無しで実行していた (v2.1.212)
5. **worktree の symlink 追従を修正** - コミット済み `.claude/worktrees` symlink でリポジトリ外に書き込む問題 (v2.1.212)
6. **Task ツールの `mode` パラメータを非推奨化** - サブエージェントは親セッションの権限モードを継承 (v2.1.212)

## 検索も委譲も 200 回で止まる

**セッション単位で回数の天井ができました。** WebSearch とサブエージェント生成に、それぞれデフォルト 200 回の上限。無限に検索・委譲を繰り返して API を無駄に叩くループを、上限で強制的に止める仕組みです。

```bash
# WebSearch のセッション上限(デフォルト 200)
CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION=200
# サブエージェント生成のセッション上限(デフォルト 200)
CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION=200
```

サブエージェント側の予算は `/clear` でリセットされます。2 分を超える MCP ツール呼び出しは、自動でバックグラウンドに回ってセッションを固めない。閾値は `CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS` で変える、あるいは無効化できます。暴走したセッションが API を延々と叩き続ける事故は、200 回で頭が打たれる。

## Plan mode が許可なしにファイルを書き換えていた

Plan mode を「読み取り専用で安全」と思って使っていた人に効く修正です。v2.1.212 以前は、Plan mode 中でも `touch` や `rm` のようなファイル変更を伴う Bash コマンドが、許可プロンプトや SDK の `canUseTool` コールバックを通らずに実行されていた。

:::note alert
Plan mode 実行中に `touch`・`rm` などのファイル変更コマンドが承認なしで走っていました。SDK 経由では `canUseTool` も呼ばれません。Plan mode を破壊的操作の防波堤にしていたなら、v2.1.212 に上げてから挙動を確認してください。
:::

worktree 作成にも似た経路がありました。`.claude/worktrees` がリポジトリにコミットされた symlink だと、その参照をたどってリポジトリ外にファイルを生成できてしまう。この 2 つとも v2.1.212 で塞がれています。

## `/fork` の役割が変わった

`/fork` の挙動がまるごと変わりました。これまではセッション内のサブエージェントを起動していたのが、v2.1.212 からは会話ごと新しいバックグラウンドセッションに複製する動きに。`claude agents` に独立した行として並び、元の作業を止めずに済みます。従来のセッション内サブエージェントは `/subtask` に分離されました。

タイトルの無いセッションなら、複製はプロンプト名で命名される。`claude agents` の一覧で、どのフォークか一目で分かる。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.212 | 新機能 | `claude auto-mode reset` | auto-mode 設定を既定に戻す。確認プロンプトあり(`--yes` でスキップ) |
| v2.1.212 | 改善 | `/resume` の過去セッションピッカー | エージェントビューで過去セッション(削除済み含む)を選んで再開 |
| v2.1.212 | 破壊的変更 | `forceLoginMethod` の適用拡大 | VS Code 拡張・SDK・`setup-token`・`install-github-app` にも強制 |
| v2.1.212 | 変更 | `set_model` のターン中適用 | headless/SDK で次のモデル往復から新モデルを使う |
| v2.1.212 | 修正 | 画像多数で "Request too large" | 大量画像の会話が誤って失敗する問題を修正、原因を説明する文言に改善 |
| v2.1.212 | 修正 | Web 検索/取得の信頼性 | API 過負荷時の "API Error" 混入を修正、529 とレート制限をバックオフ付きで再試行 |
| v2.1.212 | 改善 | プロンプトキャッシュ | LLM ゲートウェイや独自 base URL(Bedrock/Vertex/1P)でも中間 system ブロックが効く |

## まとめ

v2.1.212 の軸は、暴走ループを止める 3 つの上限(WebSearch・サブエージェント・MCP の自動バックグラウンド)。加えて Plan mode と worktree の権限まわりの穴が塞がれました。権限モードや Plan mode を運用の前提に組み込んでいるなら、v2.1.212 に上げて挙動を確認する。
