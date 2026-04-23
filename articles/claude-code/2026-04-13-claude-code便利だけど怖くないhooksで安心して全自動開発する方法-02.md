---
id: "2026-04-13-claude-code便利だけど怖くないhooksで安心して全自動開発する方法-02"
title: "Claude Code、便利だけど怖くない？Hooksで安心して全自動開発する方法"
url: "https://qiita.com/DevMasatoman/items/46725346c5a2f6416937"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-04-13"
date_collected: "2026-04-14"
summary_by: "auto-rss"
---

## TL;DR

* **Hooks** = Claude Code がツールを実行する前後に、自分のスクリプトを自動で走らせる仕組み
* `settings.json` に数行書くだけで、**危険操作のブロック・シークレット漏洩検知・作業ログ自動化**ができる
* この記事では**コピペで使える実践レシピ5選**を紹介します

## Claude Code が勝手に .env を消す世界線

Claude Code、めちゃくちゃ便利ですよね。

「このバグ直して」で直る。「テスト書いて」で書いてくれる。「デプロイして」で…… **ちょっと待って。**

便利すぎるがゆえに、こんな不安ありませんか？

* `.env.local` を「不要ファイル」と判断して消される
* `rm -rf` で想定外のディレクトリを吹き飛ばされる
* `git push --force` で main ブランチを上書きされる
* コードに API キーをベタ書きされる

全部、実際に起こりうる事故です。

**「便利だけど怖い」—— この問題を解決するのが Hooks です。**

## Hooks の仕組み（30秒で理解）

Hooks は Claude Code の **イベント駆動フック** です。

```
Claude Code がツールを実行
    ↓
【PreToolUse】実行前にあなたのスクリプトが走る
    → 危険なら exit 2 でブロック！
    ↓
ツール実行
    ↓
【PostToolUse】実行後にあなたのスクリプトが走る
    → ログ記録、警告表示など
```

設定場所は `~/.claude/settings.json`。構造はシンプルです：

```
{
  "hooks": {
    "イベント名": [
      {
        "matcher": "対象ツール名",
        "hooks": [
          {
            "type": "command",
            "command": "実行するコマンド"
          }
        ]
      }
    ]
  }
}
```

たったこれだけ。あとはイベントとレシピを知れば使えます。

## 全イベント一覧

| イベント | 発火タイミング | ブロック | 主な用途 |
| --- | --- | --- | --- |
| **PreToolUse** | ツール実行**前** | ✅ | 危険操作の阻止、入力検証 |
| **PostToolUse** | ツール実行**後** | ❌ | ログ記録、警告表示 |
| **UserPromptSubmit** | プロンプト送信時 | ✅ | 入力チェック・修正 |
| **Stop** | Claude の応答完了時 | ✅ | リマインダー表示 |
| **SessionStart** | セッション開始時 | ❌ | 初期化、コンテキスト注入 |
| **SessionEnd** | セッション終了時 | ❌ | クリーンアップ |
| **PreCompact** | コンテキスト圧縮前 | ❌ | 重要情報の退避 |
| **Notification** | 通知送出時 | ❌ | 外部連携（Slack等） |

**ブロックの仕組み**: スクリプトが `exit 2` を返すと、Claude Code はそのツール実行を中止します。`stderr` に出力したメッセージが Claude にフィードバックされるので、「なぜダメなのか」を伝えられます。

`matcher` にはツール名を指定します：

```
"matcher": "Bash"              // Bash のみ
"matcher": "Edit|Write"        // Edit または Write
"matcher": ""                  // すべてのツール
```

## 実践レシピ5選

### レシピ1: 危険コマンドをブロックする

**やりたいこと**: `rm -rf /`、`git push --force` など取り返しのつかないコマンドを止める

~/.claude/settings.json

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/bash-safety-check.sh"
          }
        ]
      }
    ]
  }
}
```

~/.claude/hooks/bash-safety-check.sh

```
#!/bin/bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command')

# rm -rf でルートやホームを削除しようとしていないか
if echo "$COMMAND" | grep -qE 'rm\s+-rf\s+(/|~|\$HOME|/Users)'; then
  echo "BLOCKED: 危険な rm -rf コマンドを検出しました" >&2
  exit 2
fi

# git push --force を main/master に実行しようとしていないか
if echo "$COMMAND" | grep -qE 'git\s+push\s+.*(-f|--force)' && \
   echo "$COMMAND" | grep -qE '(main|master)'; then
  echo "BLOCKED: main/master への force push はできません" >&2
  exit 2
fi

# 本番 Stripe キーを使おうとしていないか
if echo "$COMMAND" | grep -q 'sk_live_'; then
  echo "BLOCKED: 本番 Stripe キーの使用を検出しました" >&2
  exit 2
fi

exit 0
```

**ポイント**: `exit 2` がブロック、`exit 0` が許可。`stderr` に出力したメッセージが Claude に伝わります。

### レシピ2: 機密ファイルの編集を防ぐ

**やりたいこと**: `.env`、`credentials.json` など触ってほしくないファイルへの書き込みを止める

~/.claude/settings.json（hooks.PreToolUse に追加）

```
{
  "matcher": "Edit|Write|MultiEdit",
  "hooks": [
    {
      "type": "command",
      "command": "bash ~/.claude/hooks/file-safety-check.sh"
    }
  ]
}
```

~/.claude/hooks/file-safety-check.sh

```
#!/bin/bash
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# 保護対象パターン
PROTECTED=(".env" ".env.local" ".env.production" "credentials.json" ".pem" "id_rsa")

for pattern in "${PROTECTED[@]}"; do
  if [[ "$FILE_PATH" == *"$pattern"* ]]; then
    # .env.example は許可
    if [[ "$FILE_PATH" == *".example"* ]]; then
      continue
    fi
    echo "BLOCKED: $FILE_PATH は保護対象ファイルです" >&2
    exit 2
  fi
done

exit 0
```

**ポイント**: `.env.example` は開発に必要なので除外しています。プロジェクトに応じてパターンを調整してください。

### レシピ3: 編集後のシークレット漏洩スキャン

**やりたいこと**: コードを編集した後に API キーがベタ書きされていないかスキャンする

~/.claude/settings.json（hooks.PostToolUse に追加）

```
{
  "matcher": "Edit|Write|MultiEdit",
  "hooks": [
    {
      "type": "command",
      "command": "bash ~/.claude/hooks/post-edit-scan.sh"
    }
  ]
}
```

~/.claude/hooks/post-edit-scan.sh

```
#!/bin/bash
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# 対象拡張子のみスキャン
case "$FILE_PATH" in
  *.ts|*.tsx|*.js|*.jsx|*.py|*.go|*.json|*.yaml|*.yml) ;;
  *) exit 0 ;;
esac

[ ! -f "$FILE_PATH" ] && exit 0

# シークレットパターン検出
PATTERNS=(
  'sk_live_[a-zA-Z0-9]+'        # Stripe 本番キー
  'AKIA[A-Z0-9]{16}'            # AWS Access Key
  'ghp_[a-zA-Z0-9]{36}'         # GitHub PAT
  'xox[bpsa]-[a-zA-Z0-9-]+'     # Slack トークン
)

for pattern in "${PATTERNS[@]}"; do
  if grep -qE "$pattern" "$FILE_PATH" 2>/dev/null; then
    echo "⚠️ WARNING: $FILE_PATH にシークレットらしき文字列を検出しました（パターン: $pattern）" >&2
    # PostToolUse なので exit 2 してもブロックできない。警告のみ。
    exit 0
  fi
done

exit 0
```

**ポイント**: `PostToolUse` は実行**後**なので `exit 2` してもブロックできません。ただし `stderr` に出力すると Claude に警告が伝わり、修正を促せます。

### レシピ4: git commit 後のリマインダー

**やりたいこと**: コミットしたら「テスト通した？ドキュメント更新した？」と自動確認

~/.claude/settings.json（hooks.PostToolUse に追加）

```
{
  "matcher": "Bash",
  "hooks": [
    {
      "type": "command",
      "command": "bash -c 'INPUT=$(cat); CMD=$(echo \"$INPUT\" | jq -r \".tool_input.command\"); if echo \"$CMD\" | grep -q \"git commit\"; then echo \"REMINDER: テストは通しましたか？ドキュメントの更新は必要ですか？\"; fi'"
    }
  ]
}
```

**ポイント**: `stdout` に出力したテキストは Claude のコンテキストに追加されます。Claude がリマインダーを読んで、必要なら自分でテストを実行してくれます。

### レシピ5: セッション終了リマインダー

**やりたいこと**: 毎回の応答後に「作業ログ保存してね」と表示する

~/.claude/settings.json

```
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'echo \"💡 セッションを終える前に作業ログを保存しましょう\"'"
          }
        ]
      }
    ]
  }
}
```

**ポイント**: `Stop` は Claude が応答を完了するたびに発火します。`matcher` は不要（ツール実行ではないため）。

## おまけ: こんな使い方もできる

Hooks のポテンシャルはまだまだあります：

| やりたいこと | イベント | 概要 |
| --- | --- | --- |
| 自動フォーマット | PostToolUse (Edit) | Prettier / Biome を自動実行 |
| 型チェック | PostToolUse (Edit) | `tsc --noEmit` を自動実行 |
| Slack 通知 | Notification | Claude の通知を Slack に転送 |
| セッション開始時に情報注入 | SessionStart | プロジェクトの状態を Claude に伝える |
| コンテキスト圧縮前の退避 | PreCompact | 重要な情報をファイルに書き出す |

これらの実践的な設定テンプレートは別記事で詳しく紹介予定です。

## 注意点・ハマりどころ

### 1. 設定変更はセッション再起動で反映

`settings.json` を編集しても、今のセッションには反映されません。`/clear` するか、新しいセッションを開始してください。

### 2. stdout に余計な出力を混ぜない

フックが JSON を返す場合、シェルの `.bashrc` や `.zshrc` から出る `echo` が混ざるとパースエラーになります。

### 3. PostToolUse ではブロックできない

**実行後**に発火するイベントなので、`exit 2` を返しても止められません。ブロックしたいなら `PreToolUse` を使いましょう。

### 4. 外部 API 呼び出しはタイムアウトに注意

デフォルトのタイムアウトは 600 秒ですが、外部 API を叩く場合はレスポンスが遅いとフックが詰まります。非同期にするか、タイムアウトを短めに設定しましょう。

## まとめ

* **Hooks は Claude Code の安全装置**。`settings.json` に数行書くだけで使える
* **PreToolUse** で危険操作をブロック、**PostToolUse** でログ・警告
* `exit 2` + `stderr` でブロック＆理由通知、`exit 0` + `stdout` でコンテキスト追加
* 個人開発で一人で回しているからこそ、**人間が見落とすミスを自動で防ぐ仕組み**が大事

---

## 関連リンク
