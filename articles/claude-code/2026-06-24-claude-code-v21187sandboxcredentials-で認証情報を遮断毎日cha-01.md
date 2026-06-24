---
id: "2026-06-24-claude-code-v21187sandboxcredentials-で認証情報を遮断毎日cha-01"
title: "Claude Code v2.1.187｜sandbox.credentials で認証情報を遮断｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/f08f0805f8e40a670757"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "VSCode"]
date_published: "2026-06-24"
date_collected: "2026-06-24"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.187 の主役は `sandbox.credentials`。サンドボックスで動かしたコマンドから、認証ファイルと秘密の環境変数を読めなくする新設定です。信頼できないコマンドをサンドボックスで試す運用なら、まず確認したい設定。

## 今回の注目ポイント

1. **`sandbox.credentials` で認証情報を遮断** サンドボックス内のコマンドが認証ファイルと秘密の環境変数を読めなくなる (v2.1.187)
2. **組織のモデル制限がCLIに反映** model picker・`--model`・`/model`・`ANTHROPIC_MODEL` で制限モデルを選ぶと警告が出る (v2.1.187)
3. **リモート MCP の無期限ハングに5分タイムアウト** 応答が5分途切れると無限ブロックせずエラーで打ち切る (v2.1.187)
4. **構造化出力の無限ループを修正** `--json-schema` と workflow `agent({schema})` の `StructuredOutput` 再呼び出しを停止 (v2.1.187)
5. **`/install-github-app` でワークフロー設定が任意に** GitHub App だけ入れて secret 設定をスキップ可能 (v2.1.187)
6. **全画面モードでマウスクリック選択** permission prompt・`/model`・`/config` のメニューをクリックで選べる (v2.1.187)

## sandbox.credentials で認証情報を隔離する

:::note info
対象読者: Bash ツールやコマンド実行をサンドボックス前提で運用している人。
:::

サンドボックスはコマンドの副作用を閉じ込める仕組み。ただこれまでは、サンドボックス内のプロセスが `~/.aws/credentials` のような認証ファイルや、API キーを入れた環境変数まで読めてしまった。`sandbox.credentials` を設定すると、サンドボックス実行時にこれらへのアクセスを遮断できる。

外部から降ってきたコマンドや、信頼度の低いスクリプトをサンドボックスで試すとき、認証情報の露出を設定1つで止められる。これまで副作用だけを閉じ込めていたサンドボックスが、認証情報の読み取りまで遮断対象に含めるようになった。

## リモート MCP の無期限ハングが止まる

リモート MCP ツールの呼び出しが、応答の返らないまま無期限にブロックし続ける問題があった。v2.1.187 では応答が5分間途切れた時点でエラーで中断する。ハングしたツール1つにセッション全体を巻き込まれなくなる。

タイムアウトの挙動は環境変数 `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT` で上書きできる。

:::note warn
正規の処理で数分かかるリモート MCP ツールを使っている場合、アイドルタイムアウトで途中中断されることがある。その場合は `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT` を実行時間に合わせて延ばしてください。
:::

## 組織が選べるモデルを制限できる

組織の設定で、利用可能なモデルを絞れるようになった。制限対象のモデルを model picker や `--model`、`/model`、`ANTHROPIC_MODEL` で選ぶと、「restricted by your organization's settings」と表示されて弾かれる。

個人利用には関係ない変更。チームで使うモデルを統一したい管理者向けの設定です。コスト管理や特定モデルへの集約を、CLI レベルで強制できるようになる。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| 2.1.187 | 修正 | 構造化出力の無限再呼び出し | `--json-schema` / workflow `agent({schema})` が成功後も `StructuredOutput` を呼び続ける問題を解消 |
| 2.1.187 | 修正 | `--resume` の "No conversation found" | `-p` 実行がモデルターンを生まなかった場合の resume 失敗を修正 |
| 2.1.187 | 改善 | `/install-github-app` | GitHub Actions ワークフロー設定を任意化。App だけ入れて secret 設定をスキップ可能 |
| 2.1.187 | 改善 | 全画面でマウスクリック選択 | permission prompt・`/model`・`/config` などの選択メニューでクリック対応 |
| 2.1.187 | 修正 | CJK ペーストの mojibake | per-byte extended-key でペーストを渡す端末での韓国語・CJK 文字化けを修正 |
| 2.1.187 | 改善 | `/plugin` で未使用プラグイン表示 | 最近使っていないプラグインを出して整理しやすく |
| 2.1.187 | 修正 | サブエージェント深度トラッキング | resume したサブエージェントの深度復元、fork が深度上限にカウント |
| 2.1.187 | 修正 | [VSCode] 大規模セッション resume の無応答 | 拡張機能が固まる問題を修正 |

## まとめ

v2.1.187 はサンドボックスとリモート実行まわりの守りを固めるリリース。`sandbox.credentials` で認証情報の露出を1設定で塞ぎ、リモート MCP のハングはエラーで打ち切られる。組織のモデル制限と合わせ、チーム運用で効く変更が並ぶ。
