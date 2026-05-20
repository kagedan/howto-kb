---
id: "2026-05-20-claude-code-v21144v21145-リリース毎日changelog解説-01"
title: "Claude Code v2.1.144〜v2.1.145 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/2df74a3fd85dcbe60cad"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "qiita"]
date_published: "2026-05-20"
date_collected: "2026-05-20"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.144〜v2.1.145 の計 2 本を 1 本にまとめて解説します。background session 周りの抜け穴を整理した回と、Bash 権限プロンプトのバイパス修正が目立つ回。

## 今回の注目ポイント

1. **`/resume` が background sessions に対応** - `claude --bg` や agent view 由来のセッションも resume picker に並ぶ。`bg` バッジ付きで識別可能 (v2.1.144)
2. **Bash 権限プロンプトのバイパス修正** - allowlist 外の環境変数への bare 代入が auto-approve されていたセキュリティ穴を塞いだ (v2.1.145)
3. **`claude agents --json`** - 動作中セッション一覧を JSON 出力。tmux-resurrect や status bar 連携の口が開いた (v2.1.145)
4. **`/model` がセッションスコープに変更** - 現在セッションだけ変わる。デフォルト更新は `d` キー押下に分離 (v2.1.144)
5. **起動 75 秒ハング問題を解消** - `api.anthropic.com` 到達不能時の側 API 呼び出しに 15 秒タイムアウトを入れた (v2.1.144)
6. **`/plugin` Discover / Browse がインストール前にコンテンツ表示** - commands / agents / skills / hooks / MCP / LSP servers の中身が見える (v2.1.145)

---

## `/resume` が background sessions を拾うようになった (v2.1.144)

:::note info
対象読者: `claude --bg` や agent view で長時間タスクを回している人
:::

`/resume` picker に background session が並ぶようになった。これまでは `claude agents` か `claude logs <id>` 経由でしか辿り着けず、対話的セッションと別世界に分かれていた。v2.1.144 から両者が統合され、各エントリに `bg` のバッジが付くので何を resume したか取り違える心配は無い。

```bash
claude --bg --name "refactor-auth"
# 後で別の場所から
claude
> /resume
# picker に refactor-auth が bg バッジ付きで並ぶ
```

派生として、background session から fork したセッションも `/resume` picker に出るようになった。完了通知の方も `Agent completed · 3h 2m 5s` のように経過時間が入る。

---

## Bash 権限プロンプトの抜け穴を塞いだ (v2.1.145)

:::note info
対象読者: Bash tool の allowlist でセキュリティ制御している全ユーザー
:::

allowlist 外の環境変数に bare 代入する Bash コマンドが、権限プロンプトをスキップして auto-approve されるバグがあった。例えば許可していない `FOO=bar` のような単独代入がそのまま通る。

セキュリティ修正なので、allowlist で Bash を絞っているチームは v2.1.145 まで上げる。

合わせて、MCP prompt の slash command で必須引数を渡し忘れた時、サーバ側 validation error の raw を出していたのが、不足引数名と期待される usage を表示するように改善されている。

---

## `claude agents --json` でセッション一覧をスクリプタブルに (v2.1.145)

:::note info
対象読者: tmux や status bar、session picker を自作している人
:::

`claude agents` の出力を JSON で取れるようになった。これまで TUI 経由でしか見えなかったセッション情報が、jq でパイプできる素材になる。

```bash
claude agents --json | jq '.[] | select(.status == "awaiting") | .name'
```

合わせて `claude agents` のターミナルタブタイトルに「入力待ちセッション数」が表示されるようになった。alt-tab で別ウィンドウに切り替えていても、タブを見ればどのエージェントが反応待ちか分かる。

OTEL 側の改善も入った。`claude_code.tool` span に `agent_id` と `parent_agent_id` が付き、background subagent の span が dispatch 元の Agent tool span の下にネストする。Honeycomb や Jaeger でトレースを追いやすくなる。

---

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.145 | 機能 | Status line JSON | GitHub repo と PR 情報を自動付与 |
| v2.1.145 | 機能 | Stop / SubagentStop hook | 入力に `background_tasks` と `session_crons` フィールド追加 |
| v2.1.145 | UI | Suggestion list のマウス対応 | slash command と @-mention 候補をフルスクリーンでホバー・クリック可能 |
| v2.1.145 | UI | Read tool の挙動変更 | 全ファイル読みがトークン超過してもハードエラーにせず "PARTIAL view" を返す |
| v2.1.144 | 機能 | `/usage-credits` | "extra usage" を "usage credits" に改称 (`/extra-usage` も互換維持) |
| v2.1.144 | UI | `/plugin` browse | プラグインの最終更新日を表示 |
| v2.1.144 | UI | spinner 軽量化 | VS Code でのレンダリンググリッチ軽減 |
| v2.1.144 | 高速化 | SDK / headless MCP startup | pre-wait を起動とオーバーラップさせ最大 2 秒短縮 |
| v2.1.144 | 高速化 | pre-response stream stall リトライ | 非ストリーミングへフォールバックせずストリーミング再試行 |

<details>
<summary>バグ修正(全バージョンまとめて折りたたみ)</summary>

**v2.1.145**

- spinner / elapsed-time 表示がターミナルのリサイズ・フォーカス変更後にフリーズしキー押下まで動かない
- cross-project resume hint が Windows PowerShell 5.1 で失敗 (区切り文字を `;` に変更)
- voice push-to-talk が agent view の reply pane で動かない
- 複数 task 同時作成時に list 表示順がランダムになる
- "Failed to install Anthropic marketplace" バナーが既存インストール済みでも残る
- footer の PR バッジが `gh pr create` 等のセッション内コマンド後に即時更新されない
- Agent Teams で teammate 名が非 ASCII だと header encoding 無効で API 失敗
- `/review` が deprecated な `projectCards` GraphQL を使い Classic Projects 利用リポでエラー
- `claude plugin validate` が `skills:` のディレクトリ指定漏れを検出しない
- `context: fork` の skill が無限自己再呼び出しするケース

**v2.1.144**

- macOS で Full Disk Access 保護フォルダ配下の project だと background session が "exit 1 before init" で crash (v2.1.143 regression)
- ターミナルのウィンドウリサイズイベント取りこぼし時、表示崩れが Ctrl+L 無しでは戻らない
- 長時間セッションで stale / garbled glyph が累積していく
- 画像拡張子と内容が不一致 (HTML を .png 等) のファイル読み込みでセッションが復帰不能
- `head` / `tail` が read-before-edit チェックを通らない
- `egrep` / `fgrep` / `git grep` / `git diff` の "no matches" (exit 1) を command failure として扱う
- `/branch` が worktree 移動後や一部の background session で "No conversation to branch"
- AskUserQuestion の notes フィールドで Escape を押すとターン中断 (本来は回答選択に戻る)
- model 変更が IDE picker や `applyFlagSettings` 後に反映されない
- resume したセッションが別セッションの `/model` 選択を引き継ぐ
- Bedrock / Vertex で "Opus (1M context)" が選べない (v2.1.129 regression)
- `forceLoginMethod` / `forceLoginOrgUUID` 設定済みユーザーの remote-session login 失敗
- MCP server の `tools/list` ページネーション応答で 1 ページ目以外が捨てられる
- MCP image の MIME type 不対応 (SVG など) でセッション復帰不能
- skill ディレクトリ内ビルド時の file descriptor 枯渇 (`.md` 以外の reload を停止)
- session title が plugin monitor output から生成される
- Skill tool が headless mode で permission error (v2.1.141 regression)
- 自分の settings で有効化したプラグインが初回起動後に "not cached"
- プロジェクトの `.claude/settings.json` だけで有効化されたプラグインに `claude plugin install` のヒントを出す
- `claude mcp list` が `.mcp.json` parse 失敗時に「サーバなし」と無言で出力 (VS Code 流の `"servers"` キー使用時など)
- `ANTHROPIC_BASE_URL` カスタム設定 / Bedrock Mantle で background side-query が Haiku を選ばない
- Windows: PgUp / PgDn / マウスホイール / Ctrl+O が attached background session で効かない
- Windows: background session attach 中にターミナルを閉じると crash
- Windows: `claude agents` で ← キーを押すとリストがキー入力を受け付けなくなる
- Windows Terminal の CJK content で Agent View pane 切替時に左端 ghost characters
- `/bg` と ← デタッチで `/add-dir` 追加ディレクトリが失われる
- detach 直後の Edit / Write が "background session hasn't isolated its changes yet" で拒否
- `claude respawn <id>` が stopped セッションに対して "stopped" 表示のまま動く
- `/resume` picker に background session から fork したセッションが出ない
- background サービス無応答時の `claude agents` / `claude logs <id>` 起動 hang (10s タイムアウト追加)
- subagent が起こした background Bash task が SDK task panel で "Running" のまま残る
- 完了 / 停止済み background session が wake 失敗で startup crash 扱いになる
- `claude agents` 添付セッションで markdown link が plain text 表示
- `spinnerVerbs` カスタム値が post-turn duration メッセージにも適用される ("Worked for 5s" 等の過去形組み込みが復活)
- `claude agents` / `--bg` 拒否メッセージに具体ゲート名 (非 TTY / 環境変数 / 設定) を表示
- `claude --bg --name <label>` の名前が post-spawn 確認に表示されない
- Ctrl+R リネーム時に attached banner が即時更新されない
- `WorktreeCreate` hook 経由の非 git VCS で worktree isolation guard が効かない
- Plugin marketplace add / update が `CLAUDE_CODE_PLUGIN_PREFER_HTTPS` を尊重しない
- `/plugin` 操作後に Installed list に戻らない
- `/doctor` が command hook の `command` フィールド欠落時に exec-form 例示を出さない
- Skill 一覧が truncate された時の startup notification を `/doctor` 案内に変更

</details>

## まとめ

v2.1.144 は background session 周りの抜け穴を一気に塞いだ整理回。v2.1.145 は Bash 権限プロンプトのバイパス修正と、`claude agents --json` でのスクリプタブル化が目立つ。allowlist で Bash を制御しているチームは v2.1.145 まで上げておきたい。
