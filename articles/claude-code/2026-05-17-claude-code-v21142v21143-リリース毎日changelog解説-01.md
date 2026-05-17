---
id: "2026-05-17-claude-code-v21142v21143-リリース毎日changelog解説-01"
title: "Claude Code v2.1.142〜v2.1.143 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/4a177eb40bcf7fb66fba"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "AI-agent", "qiita"]
date_published: "2026-05-17"
date_collected: "2026-05-17"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.142〜v2.1.143 の計 2 本を 1 本にまとめます。Fast mode のデフォルトモデルが Opus 4.7 に昇格し、Opus 4.6 を前提にしていた挙動は再検証が要ります。

## 今回の注目ポイント

1. **Fast mode の既定モデルが Opus 4.7 に昇格** v2.1.142 でデフォルトが Opus 4.6 から 4.7 に。`CLAUDE_CODE_OPUS_4_6_FAST_MODE_OVERRIDE=1` で旧モデルにピン留め可能
2. **`claude plugin disable/enable` が依存関係を enforce** v2.1.143 で、依存元がある場合は無効化を拒否、有効化時は推移的依存も自動 ON
3. **`worktree.bgIsolation: "none"` で背景セッションが本体ディレクトリを直接編集** v2.1.143。worktree が現実的でないリポジトリ向けのオプトアウト設定
4. **`MCP_TOOL_TIMEOUT` がリモート MCP サーバにも反映** v2.1.142。HTTP/SSE 系の per-request fetch timeout が 60 秒で頭打ちだったのが解消
5. **`/bg` と `←`-detach が起動フラグを保持** v2.1.143 で `--fallback-model` `--mcp-config` `--settings` `--allow-dangerously-skip-permissions` 等が respawn 後も維持される
6. **macOS Full Disk Access が背景セッションに効くように** v2.1.143。`~/Documents` `~/Desktop` `~/Downloads` 配下で「Operation not permitted」が出る挙動を修正

## Fast mode、デフォルトモデルが Opus 4.7 へ

:::note info
対象: Fast mode を常用している Claude Code ユーザー
:::

v2.1.142 で、`/fast` で切り替わる Fast mode のデフォルトモデルが Opus 4.6 から Opus 4.7 に切り替わりました。Fast mode は小型モデルへの自動ダウングレードではなく、Opus ファミリーをそのまま高速出力で動かす仕組みです。推論品質は維持したまま出力レイテンシだけ短くなる構成。

旧モデルに固定する場合は環境変数で明示します。

```bash
export CLAUDE_CODE_OPUS_4_6_FAST_MODE_OVERRIDE=1
```

新モデルで回答傾向やスループットが変わるので、CI など決定論寄りの用途で挙動差が困るなら当面ピン留めしておくのが安全です。

---

## プラグインの依存関係を Claude が enforce

:::note info
対象: 複数プラグインを併用しているユーザー、プラグイン作者
:::

v2.1.143 で、`claude plugin disable` と `claude plugin enable` が依存関係を見るようになりました。

- `disable`: 他の有効プラグインが依存している場合は拒否。「これを止めるなら先にこれらを disable して」という disable-chain ヒントがコピペ可能な形で出る
- `enable`: 推移的に必要なプラグインを force-enable

依存元を残したまま依存先だけ無効化してエラーが連鎖していた事故が、disable 時に依存元を検知して止まるようになりました。手動で依存ツリーを掘る手間も消えます。

---

## `worktree.bgIsolation: "none"` で本体ディレクトリを直接編集

:::note info
対象: モノレポや git worktree が現実的に使えないリポジトリで背景エージェントを動かす場合
:::

v2.1.143 で `worktree.bgIsolation: "none"` 設定が追加されました。

通常、`claude agents` から起動する背景セッションは `EnterWorktree` で隔離コピーを作って作業します。ただ、ビルド成果物が巨大、pre-commit が worktree を前提にしていない、といった理由で worktree が現実的でないリポジトリもある。

```json
{
  "worktree": {
    "bgIsolation": "none"
  }
}
```

設定後は `EnterWorktree` をスキップし、背景セッションが本体の working copy をそのまま編集する動きになります。隔離されない以上、フォアグラウンドで同じファイルを触ればコンフリクトは出る。worktree を使えないリポジトリで背景エージェントを動かす用途専用の設定です。コンフリクト管理はユーザー側の責任。

---

## その他の変更

| バージョン | カテゴリ | 変更 | 概要 |
|---|---|---|---|
| 2.1.143 | プラグイン | `/plugin` marketplace に context cost 表示 | per-turn / per-invocation のトークン見積もりが browse pane に追加 |
| 2.1.143 | Windows | PowerShell tool 既定有効化 | Bedrock/Vertex/Foundry で既定 ON。`-ExecutionPolicy Bypass` を渡す。`CLAUDE_CODE_USE_POWERSHELL_TOOL=0` と `CLAUDE_CODE_POWERSHELL_RESPECT_EXECUTION_POLICY=1` でオプトアウト |
| 2.1.143 | UI | Shift+Tab に auto mode を追加 | 添付済みエージェントセッションの permission mode 循環に auto mode が入る |
| 2.1.143 | ループ防止 | stop hook の連続ブロック上限を 8 回に | 8 回連続でブロックされたら警告つきでターン終了。`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` で上書き |
| 2.1.143 | バックグラウンド | モデル・effort 保持 | 背景セッションが idle から wake 後もモデルと effort レベルを維持 |
| 2.1.143 | バックグラウンド | worktree cleanup の安全化 | `git worktree remove` 失敗時に `rm -rf` へフォールバックしないように。gitignored や作業中ファイルの消失を防ぐ |
| 2.1.142 | エージェント | `claude agents` の追加フラグ群 | `--add-dir` `--settings` `--mcp-config` `--plugin-dir` `--permission-mode` `--model` `--effort` `--dangerously-skip-permissions` を dispatched sessions に反映 |
| 2.1.142 | プラグイン | ルート直下 SKILL.md をスキル化 | `skills/` サブディレクトリ無しのプラグインも単一スキルとして表面化 |
| 2.1.142 | プラグイン | `/plugin` details に LSP 表示 | プラグインが提供する LSP サーバを一覧表示 |
| 2.1.142 | コンパクション | reactive compaction 高速化 | 初回 summarize 試行がオーバーフローサイズから seed され、near-full retry を回避 |
| 2.1.142 | UX | `/web-setup` が上書き警告 | 既存の GitHub App 接続を置き換える前に警告 |
| 2.1.142 | エラーメッセージ | hook 設定エラー改善 | `SessionStart`/`Setup`/`SubagentStart` に prompt-/agent-type を指定したら「command-type hook を使え」と明示 |
| 2.1.142 | エラーメッセージ | 古いモデル名提案を削除 | Usage Policy refusal から `claude-sonnet-4-20250514` の提案を除去 |

<details>
<summary>バグ修正(クリックで展開)</summary>

**v2.1.143**

- `.credentials.json` の `scopes` が非配列のとき CLI 起動がハング/OAuth refresh が失敗する問題を修正
- Windows Terminal/WSL の `claude agents` で右クリックペーストが効かない問題を修正
- `/loop` の保留中 wakeup が Claude の idle 中に Esc/Ctrl+C でキャンセルできない問題を修正
- 背景 shell や委任 subagent が走っている間に `/goal` evaluator が発火する問題を修正
- settings.json の `env` の `NO_COLOR`/`FORCE_COLOR` が Claude Code 自身の UI カラーまで剥がしていたのを subprocesses 限定に修正
- Windows で agent view 一覧表示が PowerShell プロセスを連発する問題を修正
- プロンプト無し `/bg` がフォーク先に "continue" を送ってしまう問題を修正
- `--agent <name>` がプラグイン提供の agent を `plugin:` プレフィックス無しで見つけられない問題を修正
- agent view からセッション削除しても transcript ファイルが残る問題を修正
- 添付済みバックグラウンドセッションのスクロール時の stale fragment レンダリング(Windows Terminal)を修正
- host sleep/macOS App Nap 後の worker-stall 検出が誤検知の嵐になる問題を修正
- 5xx エラーメッセージが `status.claude.com` を指していたのを設定済みゲートウェイやクラウドプロバイダ名に切替
- 背景セッションが IDE のファイル参照を無音で吸い込み次のプロンプトに先頭追加する問題を修正
- `/bg` が `--mcp-config` `--settings` `--add-dir` `--plugin-dir` `--strict-mcp-config` を保持しない問題を修正
- `claude agents` から起動した背景セッションが settings.json の `permissions.defaultMode` を尊重せず常に auto mode になる問題を修正
- Windows で応答ストリーミング中に `←` を押すと agents list 全体が入力を受け付けなくなる問題を修正
- 背景 daemon spawn が `~/.local/bin/claude` launcher 欠如/非実行時に走っているバイナリへフォールバックするように
- `claude agents --allow-dangerously-skip-permissions` が dispatched sessions を bypass mode 既定にする問題を修正(permission cycle に含めるだけに)

**v2.1.142**

- 背景セッションが pre-existing git worktree を認識せず、EnterWorktree が重複作成を拒否して Edit がブロックされる問題を修正
- macOS sleep/wake 後に daemon が clock jump を idle 時間と誤認して背景セッションが消える問題を修正
- バイナリ upgrade(`brew upgrade` 等)後に daemon が綺麗に終わらず、dispatched agents が消えたパスで crash-loop する問題を修正
- Claude-in-Chrome 拡張が shared tab 無しで接続されていると背景 agents が crash-loop する問題を修正
- 添付済み `claude agents` セッションでリンククリックが効かない問題を修正(headless browser shim の適用範囲を限定)
- `claude agents` の "v でエディタを開く" が daemon 既定エディタを使い `$EDITOR`/`$VISUAL` を見ない問題を修正
- Windows でネットワークドライブ作業ディレクトリのときの `claude agents` デッドロックを修正
- Apple Terminal や 256 色端末で `claude agents` セッション添付時の background-color bleed を修正
- `claude --bg --dangerously-skip-permissions` が retire/wake で永続化されない問題を修正
- 最初のメッセージがリンクのときセッションタイトルが URL から派生する問題を修正
- リモートクライアントからの冗長な `set_model` リクエストが `/model` breadcrumb を重複させる問題を修正
- `skills: ["./"]` のプラグインで誤って "path escapes plugin directory" が出る問題を修正
- プラグインキャッシュ掃除がインストールメタデータ無しのときアクティブバージョンディレクトリまで削除する問題を修正
- `/plugin` browse pane が新規公開プラグインで "0 installs" 表示する問題を修正
- プラグイン警告が `plugin.json` の各キー名(デフォルトフォルダを shadow するもの)を全て表示しない問題を修正

</details>

## まとめ

v2.1.142 で Fast mode のデフォルトが Opus 4.7 に切り替わり、v2.1.143 ではプラグイン依存解決の自動化とバックグラウンド系の安定化が入りました。2 バージョン合計で Fixed が 39 件、特に `claude agents` と `/bg` 周りを多用しているなら上げる価値があります。
