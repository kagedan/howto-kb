---
id: "2026-05-09-claude-code-v21133v21136-リリース毎日changelog解説-01"
title: "Claude Code v2.1.133〜v2.1.136 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/f55caa82337f0894a793"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "VSCode"]
date_published: "2026-05-09"
date_collected: "2026-05-10"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.133〜v2.1.136 の計 2 本を 1 本にまとめて解説します。複数 MCP サーバを使っているなら毎日の再認証から抜けられる修正が 2.1.136、`--worktree` のベース挙動を再度切り替える設定が 2.1.133 です。

今回の注目ポイント:

1. **MCP OAuth refresh トークンの並列消失を修正**: 複数 MCP サーバを使うと毎日再認証していた問題が止まる(2.1.136)
2. **`worktree.baseRef` 設定を追加**: `--worktree` / `EnterWorktree` のベースが `origin/<default>` に戻る、`head` で旧挙動を維持(2.1.133)
3. **plan mode が `Edit` allow ルールを抜けて書き込んでいた問題を修正**: plan mode のガードが効く(2.1.136)
4. **Hooks に effort level を渡す**: `effort.level` JSON と `$CLAUDE_EFFORT` で hooks 側が effort 別の挙動を取れる(2.1.133)
5. **`settings.autoMode.hard_deny` を追加**: auto mode で無条件ブロックする classifier ルールを定義できる(2.1.136)
6. **`@` ファイルピッカーが 100 件超ディレクトリで動かない問題を修正**: 大規模ディレクトリで使い物になる(2.1.136)

## MCP OAuth refresh トークンの並列消失を修正

:::note info
対象: 複数の remote MCP サーバを使っており、毎朝再認証を強いられていた人
:::

複数の MCP サーバが同時に OAuth refresh token をリフレッシュすると、共有のクレデンシャルファイルへの書き込みが競合する。結果として片方のトークンが消えるレースがありました。2.1.136 でこの並列リフレッシュ時の上書き問題が直り、毎日の再認証から解放されます。

似たレースは Claude Code 本体側のセッションでも踏まれていました。2.1.133 で並列セッションが refresh-token race で全部 401 dead-end に落ちる問題が修正されています。

複数 MCP サーバ運用者にとって、2.1.136 は 1 日 1 回の再ログインを止めるためのアップデートです。

---

## `worktree.baseRef` で `--worktree` のベースを切り替える

:::note info
対象: `--worktree` / `EnterWorktree` / agent-isolation を使い、新規ワークツリーをローカルの未 push commit から派生させていた人
:::

2.1.133 で、`--worktree`、`EnterWorktree`、agent-isolation worktree のベースをどこから切るか選べる設定が追加されました。

```jsonc
{
  "worktree": {
    "baseRef": "fresh"  // origin/<default> から派生(デフォルト)
    // "head"           // 現在の HEAD から派生
  }
}
```

ただ、`EnterWorktree` のベースは 2.1.128 から `head` (ローカル HEAD) に変わっていました。2.1.133 でデフォルトが `fresh` (`origin/<default>`) に戻ります。**未 push のコミットが新しいワークツリーから消えて見える**挙動になります。それが必要なら `worktree.baseRef: "head"` を明示してください。

---

## Hooks に effort level を渡す

:::note info
対象: hooks や Bash コマンドで effort level 別の挙動を組みたい人
:::

2.1.133 から hooks の JSON 入力に `effort.level` フィールドが追加され、Bash tool 経由で実行されるコマンドからは `$CLAUDE_EFFORT` 環境変数として読めます。

```bash
#!/usr/bin/env bash
# PreToolUse hook example
if [ "$CLAUDE_EFFORT" = "high" ]; then
  npm run test
else
  npm run lint
fi
```

effort=high のときだけ全テストを走らせ、low では lint だけ通す。hook 側でこの分岐が書けます。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| 2.1.136 | 設定 | `CLAUDE_CODE_ENABLE_FEEDBACK_SURVEY_FOR_OTEL` 追加 | OTEL でセッション品質サーベイを再有効化(エンタープライズ向け) |
| 2.1.136 | UI | スラッシュコマンドダイアログのスタイル統一 | フッターヒント・ダイアログ間隔・矢印キーを揃え、ロード中もフレームが即時表示 |
| 2.1.136 | UI | plugin marketplace の削除キーを `d` に変更 | 旧 `r` は retry と衝突していた |
| 2.1.136 | WSL2 | Windows クリップボードからの画像貼り付け | xclip / wl-paste で読めない場合は PowerShell に fallback |
| 2.1.133 | サンドボックス | `sandbox.bwrapPath` / `sandbox.socatPath` 追加 | Linux/WSL で bubblewrap と socat のバイナリパスを指定可能 |
| 2.1.133 | エンタープライズ | `parentSettingsBehavior` 追加 | SDK `managedSettings` をポリシー merge に組み込むかを admin が選べる(`first-wins` / `merge`) |
| 2.1.133 | パフォーマンス | warm-spare background workers のメモリ解放 | メモリ圧迫時に解放してメモリ使用量を改善 |

<details><summary>バグ修正一覧</summary>

**2.1.136**

- `.mcp.json` / プラグイン / claude.ai connector で設定した MCP サーバが `/clear` 後に黙って消える(VS Code 拡張・JetBrains プラグイン・Agent SDK)
- 同時クレデンシャル書き込みでローテーション直後の OAuth トークンが上書きされ強制再ログイン
- extended thinking が tool call 後に redacted thinking block を出すと API が 400 エラー
- `--resume` / `--continue` がプロジェクトパスにアンダースコアを含むとセッションを見つけない
- plan mode が `Edit(...)` allow ルールがあるとファイル書き込みをブロックしない
- plugin の `Stop` / `UserPromptSubmit` フックが、稼働中バージョンをキャッシュ削除されると失敗
- bash コマンド出力と markdown コードブロックで色が誤った位置に出る
- ReasonML diff の word-diff 境界で "undefined" アーティファクト
- worktree exit ダイアログが削除済み worktree の方向で警告
- `@` ファイルピッカーが、小規模 non-git ディレクトリでセッション中作成のファイルを見つけない
- `@` ファイルピッカーが、100 件超のディレクトリでファイルを見つけない
- 失敗した tool call がフルスクリーンで truncate された出力でクリック展開できない
- Ctrl+G で外部エディタを開いた後、persistent extended-key mode の端末で Backspace と Ctrl+Backspace が逆になる
- `/usage` の週次リセットが日付でなく時刻表示になっていた
- ウェルカムバナーの省略記号が CJK 端末で列幅オーバーフロー
- `/insights` がマルフォームの tool call input でクラッシュ
- tool の collapsibility 分類がセッション中に変わるとレンダラがクラッシュ
- `plugin.json` の `skills` エントリがプラグインのデフォルト `skills/` を隠す問題、ファイルパス指定で黙って失敗していた問題
- IDE shell-integration ロックファイルが `CLAUDE_CONFIG_DIR` を尊重しない
- ストリーミング中の端末出力コピーで末尾空白
- プラグインの uninstall / enable / disable が slug を case-insensitive に matching しない
- tool error truncation marker が surrogate pair 文字列で負のカウント表示
- `CLAUDE_ENV_FILE` SessionStart hook の env が `/resume` `/clear` 後に stale
- `/branch` がペーストされた複数行をそのままセッションタイトルに保存
- ラップされたテキストの 2 行目に列境界で先頭空白が残る
- Esc が `/install-github-app` `/desktop` `/resume` `/web-setup` のダイアログを閉じない
- `/doctor` の MCP スキーマエラーが欠落フィールド名やソースファイルパスを示さない
- Bash パーミッションプロンプトが内部パーサ診断を表示
- スペース入りのプラグイン slash command (`/myplugin review`) が namespaced 形式に解決されない
- `AskUserQuestion` が multi-select の配列回答を破棄
- `/clear <name>` がクリア後のセッションを `/resume` 用にラベル付けしない
- `CronList` 出力が修飾子と scheduled prompt を欠落
- 「Jump to bottom」オーバーレイが CJK 文字に色アーティファクトを残す
- 幅広 markdown テーブルがストリーミング中に古い枠線を残す
- 長いプロンプトで pasted-text プレースホルダが auto-truncate されるとペーストテキストが silent drop
- `/release-notes` が changelog refresh 失敗後に古いバージョンで stuck
- `/mcp` サーバ一覧が端末に収まらないとスクロールしない
- 初回スラッシュコマンド後に途中入力でスラッシュコマンド autocomplete が動かない
- `autoScrollEnabled: false` でスクロール下端到達時に auto-follow が再開
- 空入力で Enter するとプロンプト候補が auto-submit される(Tab か矢印で確定するべき)
- `keybindings.json` で再バインドしたキーがキーボードショートカットヒントに反映されない
- `/settings` での言語変更が確定後 Escape で巻き戻る
- `/terminal-setup` が autocomplete に完全一致でしか出ず prefix で出ない
- `AskUserQuestion` ダイアログの「Chat about this」が質問テキストを消す
- MCP tool 結果が、サーバが content block を返すと invisible
- `--worktree` が既存 / stale worktree と衝突する際のエラーメッセージ改善

**2.1.133**

- 並列セッションが refresh-token race で全部 401 dead-end
- ドライブルート(`C:\`)や POSIX `/` にスコープした `Edit` / `Write` allow ルールがマッチを誤りプロンプトを常時表示
- 履歴 / セッションログのファイルロックが clock skew や遅いディスクで compromise されたときの未処理 rejection (`ECOMPROMISED`)
- 会話 compaction 中に Esc を押すと「Error compacting conversation」の偽エラー通知
- `HTTP(S)_PROXY` / `NO_PROXY` / mTLS が MCP OAuth フロー全体(discovery / DCR / token 交換 / refresh)で尊重されない
- マップしたネットワークドライブが `--add-dir` / SDK `additionalDirectories` 経由で Read/Write/Edit 拒否
- claude.ai からの Remote Control stop/interrupt が CLI セッションを完全キャンセルしない、stuck な tool 中断後にキューが進まない
- `/effort` が他の concurrent セッションの effort level を変える、IDE での effort 変更が silent drop されることがある
- subagents が project / user / plugin skills を Skill tool で発見できない
- `claude --help` が `--remote-control` を `--remote-control-session-name-prefix` と並べてリスト
- VSCode: 拡張ビルドに Claude binary が同梱されていないと `claudeCode.claudeProcessWrapper` が「Unsupported platform」で失敗

</details>

## まとめ

複数 MCP サーバ常用者は 2.1.136 への更新優先度が高い。`--worktree` のベース挙動が 2.1.133 で再度変わるため、未 push commit 起点で運用していたなら `worktree.baseRef: "head"` を明示する必要があります。
