---
id: "2026-06-11-claude-code-最新機能ガイド-precompact-hookworktree強化チームオン-01"
title: "Claude Code 最新機能ガイド — PreCompact Hook・Worktree強化・チームオンボーディング"
url: "https://zenn.dev/kai_kou/articles/231-claude-code-precompact-worktree-guide"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "zenn"]
date_published: "2026-06-11"
date_collected: "2026-06-12"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code は2026年4月に入ってからも精力的なアップデートを続けています。v2.1.101〜v2.1.107 では、開発チームに直結する実用的な機能が複数追加されました。

本記事では以下の新機能を公式ドキュメントとチェンジログに基づいて解説します。

### この記事で学べること

* **PreCompact Hook**: コンテキスト圧縮をフックで制御する方法
* **EnterWorktree パラメータ強化**: 既存 worktree へのスムーズな切り替え
* **/team-onboarding**: チームのクイックスタートガイドを自動生成
* **Background Plugin Monitors**: プラグインのバックグラウンド監視
* その他の信頼性・パフォーマンス改善

### 対象読者

* Claude Code を日常的に使っている開発者
* フック機能やプラグイン機能を活用したい方
* 開発チームへの Claude Code 導入を検討している方

### 前提環境

* Claude Code v2.1.101 以上（`claude --version` で確認）
* Node.js 環境

## TL;DR

* **PreCompact Hook** で自動コンパクトをブロック・制御できるようになった（v2.1.105）
* **EnterWorktree の path 指定**で既存 worktree に切り替え可能に（v2.1.105）
* **/team-onboarding** コマンドがチームのオンボーディングドキュメントを自動生成（v2.1.101）
* ストリーミングの信頼性が向上し、5分間データなしで自動リトライ（v2.1.105）
* `/proactive` が `/loop` のエイリアスとして追加（v2.1.105）

---

## 1. PreCompact Hook — コンパクト処理を完全制御

### 概要

[Claude Code Hooks ドキュメント](https://code.claude.com/docs/en/hooks)によると、v2.1.105 で新たに **PreCompact Hook** が追加されました。このフックはコンテキストのコンパクト処理（`/compact` または自動コンパクト）が始まる**直前**に実行され、処理をブロックしたり制御したりできます。

### フックの入力形式

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../transcript.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "PreCompact",
  "trigger": "auto"
}
```

`trigger` には以下の値が入ります:

| 値 | トリガー |
| --- | --- |
| `"manual"` | `/compact` コマンドによる手動実行 |
| `"auto"` | コンテキストが大きくなったときの自動実行 |

### コンパクトをブロックする方法

コンパクトをブロックするには **exit code 2** で終了するか、JSON で `"decision": "block"` を返します。

**シェルスクリプト例（自動コンパクトのみブロック）:**

```
#!/bin/bash
# block-auto-compact.sh
REASON=$(jq -r '.trigger' < /dev/stdin)

if [ "$REASON" = "auto" ]; then
  echo "自動コンパクトはポリシーにより無効化されています" >&2
  exit 2  # exit 2 でコンパクトをブロック
fi

exit 0  # 手動コンパクトは許可
```

**JSON 出力でブロックする例:**

```
{
  "decision": "block",
  "reason": "現在アクティブなセッションがあるためコンパクト不可"
}
```

### `.claude/settings.json` への設定方法

```
{
  "hooks": {
    "PreCompact": [
      {
        "matcher": "auto",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/block-auto-compact.sh"
          }
        ]
      }
    ]
  }
}
```

### 関連フックとの組み合わせ

| フック | タイミング |
| --- | --- |
| `PreCompact` | コンパクト処理開始前 |
| `PostCompact` | コンパクト処理完了後 |
| `InstructionsLoaded` | コンパクト後に `"load_reason": "compact"` で再発火 |

`PreCompact` でコンパクト前のトランスクリプトを外部ログに保存し、`PostCompact` でコンパクト後の状態を確認する、といった運用が可能になります。

### exit code のまとめ

| exit code | 動作 |
| --- | --- |
| `0` | コンパクトを許可 |
| `2` | **コンパクトをブロック**（手動 `/compact` の場合は stderr メッセージが表示される） |
| その他 | 非ブロッキングエラー（stderr を表示しコンパクトは続行） |

---

## 2. EnterWorktree — 既存 worktree への切り替え

### v2.1.105 の変更点

[Claude Code 公式チェンジログ](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)によると、`EnterWorktree` ツールに **`path` パラメータ**が追加されました。

**変更前（v2.1.104 以前）:**

* `claude --worktree <name>` で新規 worktree を作成するのみ

**変更後（v2.1.105 以降）:**

* 既存 worktree のパスを指定してシームレスに切り替えられる

### 典型的なユースケース

複数の機能開発を並列で進める場合、従来は worktree を作成し直す必要がありましたが、`path` パラメータで既存 worktree に即座に切り替えられます。

```
# 新規 worktree の作成（従来から可能）
claude --worktree feature-auth

# 別のターミナルで同じ worktree に接続（v2.1.105 で追加）
# Claude Code 内から既存 worktree へ切り替えるよう指示可能
```

Claude Code のセッション内では「既存の worktree `feature-auth` に切り替えて」と自然言語で指示すると、`EnterWorktree` ツールが `path` パラメータを使って既存の作業ディレクトリに移動します。

### worktree のセットアップ

```
# worktree の基本セットアップ
git worktree add .claude/worktrees/feature-auth -b feature-auth

# .gitignore に追加
echo ".claude/worktrees/" >> .gitignore
```

---

## 3. /team-onboarding — チームオンボーディングの自動化

### 概要

v2.1.101 で追加された `/team-onboarding` コマンドは、**ローカルの Claude Code 使用状況を分析してチームのクイックスタートガイドを自動生成**します。

### 使い方

```
# Claude Code 内で実行
/team-onboarding
```

コマンドを実行すると、以下の内容を含むガイドが生成されます:

* プロジェクト固有の設定情報
* チームでよく使われるワークフローパターン
* 新規メンバー向けのセットアップ手順
* 共通のフックやスキルの説明

### 活用シナリオ

新規メンバーが参加した際、従来は手動でオンボーディング資料を作成していましたが、`/team-onboarding` を実行するだけでプロジェクトの実情に合ったガイドが自動生成されます。生成されたドキュメントは `CLAUDE.md` や `docs/` ディレクトリに保存して活用できます。

---

## 4. Background Plugin Monitors

### 概要

v2.1.105 で、プラグインの `monitors` マニフェストキーが追加されました。これにより、**セッション開始時またはスキル起動時に自動でバックグラウンドモニターが起動**します。

### マニフェスト設定例

プラグインの `manifest.json` や `SKILL.md` のトップレベルに `monitors` キーを追加します:

```
{
  "name": "my-plugin",
  "monitors": [
    {
      "name": "log-watcher",
      "command": "tail -f /var/log/app.log",
      "on_output": "notify"
    }
  ]
}
```

セッション開始時にモニターが自動起動し、バックグラウンドでログ監視やヘルスチェックを継続実行できます。

---

## 5. その他の改善点

### ストリーミング信頼性の向上（v2.1.105）

**スタックしたAPIストリームの自動リカバリー:**

* データが届かない状態が **5分間** 続くと、ストリームを自動的にアボート
* 非ストリーミングモードに切り替えてリトライ
* ハングしたまま待機し続ける問題が解消

**ネットワークエラー時のフィードバック改善:**

* 接続エラー発生時にスピナーのまま固まらず、即座にリトライメッセージを表示

### /proactive エイリアス（v2.1.105）

`/loop` コマンドのエイリアスとして `/proactive` が追加されました。

```
# どちらも同じ動作
/loop
/proactive
```

エージェントが定期的にタスクを実行する「プロアクティブモード」を直感的な名前で呼び出せます。

### OS CA 証明書ストアの対応（v2.1.101）

エンタープライズ環境でのTLSプロキシに対応するため、OS の CA 証明書ストアがデフォルトで信頼されるようになりました。

```
# 従来のバンドル済みCAのみを使う場合
export CLAUDE_CODE_CERT_STORE=bundled
```

### セキュリティ修正（v2.1.101）

POSIX 環境での `which` フォールバック処理にあったコマンドインジェクション脆弱性が修正されました。これは LSP バイナリ検出に関するものでした。v2.1.101 以上への更新が推奨されます。

### メモリ最適化（v2.1.101）

長いセッションで過去のメッセージリストのコピーが大量に蓄積する問題が解消されました。長時間のセッションでのメモリ消費が改善されます。

### Thinking ヒントの早期表示（v2.1.107）

長い処理中に thinking ヒントがより早く表示されるようになり、Claude Code が処理中であることを視覚的に確認しやすくなりました。

---

## バージョンアップ方法

```
# npm でアップデート
npm update -g @anthropic-ai/claude-code

# バージョン確認
claude --version
```

---

## まとめ

v2.1.101〜v2.1.107 での主な改善点をまとめます:

| バージョン | 主な機能 |
| --- | --- |
| v2.1.107 | Thinking ヒントの早期表示 |
| v2.1.105 | PreCompact Hook・EnterWorktree path パラメータ・Background Plugin Monitors・/proactive エイリアス |
| v2.1.101 | /team-onboarding・OS CA証明書ストア対応・セキュリティ修正・メモリ最適化 |

特に **PreCompact Hook** は、自動コンパクトを制御したい本番環境での利用や、コンパクト前後のログ保存などに活用できる重要な機能です。**EnterWorktree の path パラメータ**は並列開発ワークフローをよりスムーズにし、**/team-onboarding** は開発チームへの導入を加速します。

公式の[リリースノート](https://github.com/anthropics/claude-code/releases)と[フック リファレンス](https://code.claude.com/docs/en/hooks)を参照しながら、自チームのワークフローに合わせて活用してください。

## 参考リンク
