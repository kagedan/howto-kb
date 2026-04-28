---
id: "2026-04-27-claude-code-v21120-リリース毎日changelog解説-01"
title: "Claude Code v2.1.120 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/54918006b98ea36880cc"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "VSCode"]
date_published: "2026-04-27"
date_collected: "2026-04-28"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

Claude Code v2.1.120 が公開されました。`/config` の永続化、GitHub以外のPRレビュー対応、Hooksの計測情報拡張など、業務運用を底上げする更新が中心です。

## 今回の注目ポイント

1. **`/config` 設定が永続化** ｜ 変更が `~/.claude/settings.json` に書き込まれ、project/local/policy のoverride precedenceに参加
2. **GitLab / Bitbucket / GHE の PR が `--from-pr` で開ける** ｜ GitLab MR、Bitbucket PR、GitHub Enterprise PR URL を判別して取り込み
3. **`prUrlTemplate` 設定追加** ｜ コードレビューURLを github.com 以外に差し替え可能
4. **Hooks に `duration_ms` 追加** ｜ `PostToolUse` / `PostToolUseFailure` の入力にツール実行時間がミリ秒で渡る
5. **Plugin が git tag 最高版に自動追随** ｜ バージョン制約付きでpinした Plugin が、満たす範囲の最新tagへ更新
6. **Subagent と SDK MCP server の再構成が並列化** ｜ MCPサーバー多めの環境で起動が縮む

## `/config` の変更が次回起動でも消えなくなった

:::note info
対象読者: `/config` で model や theme を切り替え、毎回設定し直していた人
:::

v2.1.120 から、`/config` 経由の変更が `~/.claude/settings.json` に書き込まれて永続化されます。これまではセッション内のみで効くケースがあり、再起動で元に戻ることもしばしば。

保存先は3層の precedence にきちんと参加。グローバル設定よりプロジェクト設定が優先される、という従来の挙動と整合する形です。

```text
~/.claude/settings.json        # global (今回 /config の書き込み先になった)
.claude/settings.json          # project (リポジトリにコミット可)
.claude/settings.local.json    # local (gitignore推奨)
```

この変更は v2.1.120 で入りました。

---

## GitLab / Bitbucket / GitHub Enterprise の PR レビューに対応

:::note info
対象読者: 業務で GitHub.com 以外のリポジトリホスティングを使っている人
:::

`--from-pr` が GitHub.com 専用ではなくなり、URL を判別して以下を受け付けます。

- GitLab merge request URL
- Bitbucket pull request URL
- GitHub Enterprise PR URL

```bash
# GitLab MR から会話を起動
claude --from-pr https://gitlab.example.com/team/repo/-/merge_requests/42

# GitHub Enterprise も同様
claude --from-pr https://github.example.com/team/repo/pull/100
```

合わせて `prUrlTemplate` 設定が追加され、Claude Code が提示するコードレビューURLも github.com 以外へ差し替えられます。`owner/repo#N` 形式のショートハンドも、固定で github.com を見にいくのではなく git remote のホストを参照する仕様に。社内Gitホスト前提でも壊れません。

この変更は v2.1.120 で入りました。

---

## Hooks に `duration_ms` が来た

`PostToolUse` と `PostToolUseFailure` の入力に `duration_ms` が追加されました。ツール単位で実行時間がミリ秒で取れるので、遅いツールの可視化や SLI 集計に直結します。

```json
// .claude/hooks/post_tool_use.* に渡る input 例
{
  "tool_name": "Bash",
  "tool_input": { "command": "npm test" },
  "tool_response": { "...": "..." },
  "duration_ms": 1842
}
```

OpenTelemetry 側でも歩調が揃いました。`tool_result` と `tool_decision` イベントに `tool_use_id` が、`tool_result` には `tool_input_size_bytes` が追加。Hooks 派と OTel 派のどちらでも、ツール呼び出し単位で計測できる粒度になりました。

この変更は v2.1.120 で入りました。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.120 | CLI | `--print` がagentの `tools:` / `disallowedTools:` を尊重 | CIで `--print` 実行時もagent側の権限定義が効く |
| v2.1.120 | CLI | `--agent <name>` がagentの `permissionMode` を尊重 | 組み込みagentの権限モードがそのまま反映 |
| v2.1.120 | 環境変数 | `CLAUDE_CODE_HIDE_CWD` 追加 | 起動ロゴの作業ディレクトリ表示を隠せる |
| v2.1.120 | Plugin | git tag 最高版へ自動更新 | バージョン制約を満たす最新tagに追随 |
| v2.1.120 | MCP | 再構成時に並列接続 | Subagent / SDK MCP server の起動が速くなる |
| v2.1.120 | Permissions | PowerShellコマンドの自動承認対応 | Windows環境でPSコマンドが対象に |
| v2.1.120 | UI | スラッシュコマンド候補で一致文字をハイライト | ファジーマッチの視認性が向上 |
| v2.1.120 | UI | スラッシュコマンドの長い説明を折り返し表示 | 切り捨てされなくなる |
| v2.1.120 | OTel | `tool_use_id` / `tool_input_size_bytes` 追加 | イベント単位の紐付けとサイズ計測 |
| v2.1.120 | Vertex AI | Tool search がデフォルト無効化 | Vertex AI 環境でのデフォルト挙動変更 |
| v2.1.120 | StatusLine | stdin JSON に `effort.level` / `thinking.enabled` | カスタム statusline で参照可能 |
| v2.1.120 | Security | `blockedMarketplaces` の `hostPattern` / `pathPattern` が正しく適用 | パターンマッチが期待通り動作 |

### バグ修正(クリックで展開)

<details><summary>v2.1.120 のバグ修正</summary>

- CRLFペーストで余計な空行が入る不具合を修正
- kitty keyboard protocol で複数行ペーストの改行が消える不具合を修正
- Bash tool が permission で拒否されると Glob / Grep tool が消える不具合を修正
- フルスクリーンモードでツール完了後にスクロールが最下部に戻る不具合を修正
- MCPのHTTP接続でJSON以外のOAuth discoveryレスポンスで失敗する不具合を修正
- Rewind overlay が画像付きメッセージで「(no prompt)」と表示される不具合を修正
- auto mode が plan mode の指示を上書きしてしまう不具合を修正
- 非同期 `PostToolUse` hook で応答が空の場合に空のtranscriptエントリが残る不具合を修正
- スラッシュコマンドでの `@`-file Tab補完がプロンプト全体を置き換える不具合を修正
- macOS Terminal.app の Docker/SSH 起動時に `p` 文字が混入する不具合を修正
- MCPサーバーヘッダーの `${ENV_VAR}` プレースホルダーが置換されない不具合を修正
- MCP OAuth トークン交換時に client secret が送られない不具合を修正
- `/skills` で Enter がダイアログを閉じる不具合を修正(本来は skill 名の pre-fill)
- `/agents` 詳細ビューが利用不可な組み込み tool を誤ラベル表示する不具合を修正
- Windows でキャッシュ不完全時に plugin の MCP server が起動しない不具合を修正
- `/export` が会話の model ではなく default model を表示する不具合を修正
- verbose output 設定が再起動後に消える不具合を修正
- `/usage` のプログレスバーがラベルと重なる不具合を修正
- plugin MCP server が optional の `${user_config.*}` を空のままだと失敗する不具合を修正
- 末尾が数字のリスト項目で数字だけ次行に折り返される不具合を修正
- `/plan` および `/plan open` が plan mode の既存planに作用しない不具合を修正
- auto-compaction 直前に呼ばれた skill が再実行される不具合を修正
- `/reload-plugins` と `/doctor` が無効化済み plugin でエラーを報告する不具合を修正
- Agent tool の `isolation: "worktree"` が古い worktree を再利用する不具合を修正
- 無効化済みMCPサーバーが `/status` で「failed」表示される不具合を修正
- `TaskList` が tasks をソートせず任意順で返す不具合を修正
- PRタイトルから「GitHub API rate limit exceeded」のヒントが誤発火する不具合を修正
- SDK/bridge `read_file` が成長中のファイルでサイズ上限を強制しない不具合を修正
- git worktree でPRがセッションに紐づかない不具合を修正
- `/doctor` が上位スコープの MCP オーバーライドについて警告する不具合を修正
- Windows: cmd ラッパーに関する MCP 設定の誤検知警告を削除
- VSCode: macOS で権限プロンプト中の音声入力が無音になる不具合を修正
- Vim mode で INSERT 中の Esc がキューイング済みメッセージを入力欄に戻す不具合を修正

</details>

## まとめ

v2.1.120 は「Claude Code をチームで運用する」層に効くリリース。`/config` 永続化、GitHub 以外のPRレビュー、Hooks 計測情報の拡充は、いずれも個人開発より企業運用で差が出ます。バグ修正の物量も多く、`auto mode` と `plan mode` の競合や `/export` の model 表示など、地味に困っていた箇所が片付きました。
