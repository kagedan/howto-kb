---
id: "2026-04-30-claude-code-v21122v21123-リリース毎日changelog解説-01"
title: "Claude Code v2.1.122〜v2.1.123 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/6241bfa89543f382f375"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "qiita"]
date_published: "2026-04-30"
date_collected: "2026-05-01"
summary_by: "auto-rss"
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.122〜v2.1.123 の計2本をまとめて解説。v2.1.122 は Bedrock のサービスティア指定や `/resume` の PR URL 検索など実務で効く中粒度の追加が並び、v2.1.123 は OAuth ループの一点修正です。

### 今回の注目ポイント

1. **BedrockのService Tier指定** - `ANTHROPIC_BEDROCK_SERVICE_TIER` で flex / priority を選べる
2. **/resume にPR URLを貼ると元セッションが見つかる** - GitHub / GitHub Enterprise / GitLab / Bitbucket の4つに対応
3. **OAuth 401ループ修正** - `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1` を入れていた環境がやっとログインできるように
4. **settings.json の hooks 不正でも全体は壊れない** - 1ヶ所のtypoで設定ファイル全滅、を回避
5. **画像が2576px→2000pxに正しくリサイズ** - 新モデル送信時の解像度誤差を是正
6. **OpenTelemetry の数値属性が文字列ではなく数値に** - ダッシュボード集計の地味な落とし穴を解消

## Bedrockのサービスティアを環境変数1つで切り替えられる

:::note info
対象: Amazon Bedrock経由で Claude Code を動かしている人
:::

v2.1.122で `ANTHROPIC_BEDROCK_SERVICE_TIER` が追加されました。`default` / `flex` / `priority` の3択で、値はそのまま `X-Amzn-Bedrock-Service-Tier` ヘッダとして Bedrock API に渡ります。

```bash
# レイテンシ重視・対話用
export ANTHROPIC_BEDROCK_SERVICE_TIER=priority

# 安価で待てるバッチ用
export ANTHROPIC_BEDROCK_SERVICE_TIER=flex

claude
```

これまでBedrockのサービスティア機能を使うにはSDK直叩きやプロキシ層でヘッダを挿し込むしかなく、Claude Code単体では選択不能でした。プロセス分離での使い分けが手軽です。具体的には大規模リファクタを裏で `flex` で流しつつ、対話セッションは `priority` で待たない、という構成が環境変数のexportだけで成立します。AWS側の利用枠が逼迫したときの逃げ道としても効くでしょう。

---

## /resume の検索ボックスがPR URLを理解する

:::note info
対象: Claude Code で作業 → PRを出す → 後日戻ってきて続きをやる、を繰り返す人
:::

`/resume` の検索ボックスにPR URLを貼ると、そのPRを生成したセッションを引っ張ってこられるようになりました(v2.1.122)。GitHub・GitHub Enterprise・GitLab・Bitbucket の4プラットフォームに対応しています。

```
/resume https://github.com/your-org/your-repo/pull/1234
```

これまでセッション履歴をタイトル文字列で漁るか、リポジトリ名で絞り込むしかなく、レビューバックの再開で「あのPRどこから手をつけたんだっけ」になる場面が多発していました。PR URLコピー1発で復元、という導線が一直線に通ります。

---

## CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1 環境のログイン不能が解消

:::note info
対象: 実験ベータを切るために `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1` を設定していたユーザー
:::

v2.1.123の唯一の修正。`CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1` を設定した状態でOAuth認証すると、401を返されては再試行を繰り返す無限ループに陥り、ログインそのものが完了しない状態でした。

```bash
export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1
claude  # v2.1.122以前: 401ループで進まない
        # v2.1.123以降: 認証完了
```

回避のため変数を一時的に外していた方は、v2.1.123に上げて元に戻して問題ありません。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.122 | /mcp | claude.ai connector の重複表示 | 同一URLの手動MCPサーバーで隠れていた claude.ai connector を表示し、削除ヒントを出す |
| v2.1.122 | /mcp | 未認証メッセージの明確化 | ブラウザサインイン後も未認証のまま残った場合の文言を改善 |
| v2.1.122 | OpenTelemetry | 数値属性の型修正 | `api_request` / `api_error` の数値属性が文字列でなく数値で出力される |
| v2.1.122 | OpenTelemetry | at_mention ログ追加 | `claude_code.at_mention` ログイベントを `@` メンション解決時に発火 |
| v2.1.122 | settings.json | hooks不正の影響範囲縮小 | `hooks` の1エントリが malformed でも他の設定は読み込まれる |
| v2.1.122 | Voice mode | Caps Lock バインドエラー | ターミナルが Caps Lock をキーイベントとして送らないため、エラーで明示 |

### バグ修正(展開して読む)

<details><summary>v2.1.122 のバグ修正一覧</summary>

- `/branch` で巻き戻し済みタイムラインを含むセッションを fork すると `tool_use ids were found without tool_result blocks` で失敗する不具合を修正
- `/model` で Bedrock の application inference profile ARN に Effort オプションが表示されず、`output_config.effort` も送られない不具合を修正
- Vertex AI / Bedrock がセッションタイトル生成や構造化出力で `invalid_request_error: output_config: Extra inputs are not permitted` を返す不具合を修正
- Vertex AI の `count_tokens` エンドポイントがプロキシゲートウェイ越しで400を返す不具合を修正
- `spinnerTipsOverride.excludeDefault` が時間ベースのスピナーTipsを抑制しない不具合を修正
- ToolSearch がノンブロッキングモードでセッション開始後に接続したMCPツールを取りこぼす不具合を修正
- bash モードで `!exit` / `!quit` がシェルコマンド扱いされず、CLIごと終了していた不具合を修正
- 新モデル送信時に画像が1辺2000px上限ではなく2576pxにリサイズされていた不具合を修正
- リモートコントロールセッションのアイドル状態が秒2回再描画され、`tmux -CC` の制御パイプを溢れさせて端末を停止させる不具合を修正
- 古いビュー設定が残っていてアシスタントメッセージが空白に見える不具合を修正

</details>

## まとめ

v2.1.122はBedrock運用と `/resume` の体験改善が当たり、v2.1.123は `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1` 環境のログイン不能を解いた1点修正です。Bedrock利用者は `ANTHROPIC_BEDROCK_SERVICE_TIER` の導入を、settings.json に複数の hooks を書いている人は v2.1.122 への更新で「1箇所のtypoで全部死ぬ」リスクが消える点を押さえておくと良さそうです。
