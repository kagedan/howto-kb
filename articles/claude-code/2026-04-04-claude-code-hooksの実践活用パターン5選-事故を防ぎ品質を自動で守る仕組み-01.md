---
id: "2026-04-04-claude-code-hooksの実践活用パターン5選-事故を防ぎ品質を自動で守る仕組み-01"
title: "Claude Code Hooksの実践活用パターン5選 — 事故を防ぎ、品質を自動で守る仕組み"
url: "https://qiita.com/joinclass/items/cc45d196d7f5b6613f50"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-04"
date_collected: "2026-04-04"
summary_by: "auto-rss"
---

## はじめに

Claude Codeを業務で使い込んでいくと、「AIが勝手にやらかす」瞬間に必ず遭遇する。

僕は一人会社でAIエージェント10部門を運用し、17個のlaunchdジョブで自動化率98%の体制を構築している。その過程で **git push --forceでブランチが消えた事故** や **敬語がおかしい営業メールが取引先に届いた事件** など、痛い失敗を何度も経験した。

これらの事故を防ぎ、安心してAIに委任するために欠かせないのが **Claude Code Hooks** だ。

この記事では、僕が実際の運用で使っている5つのHooksパターンを、失敗談と共に紹介する。

## Claude Code Hooksとは

Hooksは、Claude Codeの特定イベント（ツール実行前後、会話開始時など）にシェルコマンドを自動実行する仕組みだ。`.claude/settings.json` に定義する。

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": ["bash /path/to/script.sh"]
      }
    ]
  }
}
```

主なイベント:

| イベント | タイミング |
| --- | --- |
| `PreToolUse` | ツール実行前（ブロック可能） |
| `PostToolUse` | ツール実行後 |
| `Notification` | 通知発生時 |
| `Stop` | Claude応答完了時 |

## パターン1: 危険コマンドの完全ブロック（絶対禁止リスト）

### 背景: git push --forceでブランチが消えた

ある日、AIが自動でコードを整理した際に `git push --force` を実行し、リモートブランチの履歴が消えた。CLAUDE.mdに「やらないで」と書いても、コンテキストが長くなると無視されることがある。Hooksなら**コンテキストの長さに関係なく確実に防げる**。

### 実装

```
#!/bin/bash
# hooks/block-dangerous.sh
INPUT=$(cat -)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

BLOCKED_PATTERNS=(
  "git push.*--force"
  "git push.*-f"
  "git reset --hard"
  "git clean -fd"
  "rm -rf /"
  "DROP TABLE"
  "DROP DATABASE"
)

for pattern in "${BLOCKED_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qiE "$pattern"; then
    echo "BLOCKED: このコマンドは禁止リストに含まれています: $pattern"
    exit 2
  fi
done
```

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": ["bash hooks/block-dangerous.sh"]
      }
    ]
  }
}
```

`exit 2` でClaude Codeはツール実行をブロックする。ブロック時のメッセージはAIにフィードバックされるので、理由を書くとAIが代替手段を考えてくれる。

## パターン2: 対外アクション承認パイプライン

### 背景: AIが敬語のおかしいメールを自動送信

営業メールをAIに書かせて確認なしで送信したら、取引先から「文面が不自然」と指摘された。AIは実行に使う。だが判断は人間がすべきだ。

この経験から、対外アクションはすべて **draft → CEO承認 → 実行** のパイプラインを通す設計に変えた。

### 実装

```
#!/bin/bash
# hooks/require-approval.sh
INPUT=$(cat -)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

EXTERNAL_PATTERNS=(
  "curl.*-X POST"
  "curl.*-X PUT"
  "gh pr create"
  "gh issue create"
  "npm publish"
  "git push"
)

for pattern in "${EXTERNAL_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qE "$pattern"; then
    echo "APPROVAL_REQUIRED: 対外アクション検出。承認パイプラインを通してください"
    exit 2
  fi
done
```

Hooksで強制することで、AIが勝手に外部へアクションすることを構造的に防いでいる。「お願い」ではなく「仕組み」で制御する。

## パターン3: 機密ファイルの書き込みブロック

### 背景: .envにAIが値を追加しようとする

自動化環境では、AIが「便利だから」と `.env` や認証情報ファイルに書き込もうとすることがある。一度でも秘密鍵がgit履歴に入ると取り返しがつかない。

### 実装

```
#!/bin/bash
# hooks/protect-secrets.sh
INPUT=$(cat -)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // empty')

PROTECTED_PATTERNS=(
  "\.env$"
  "\.env\."
  "credentials"
  "secrets"
  "\.pem$"
  "\.key$"
)

for pattern in "${PROTECTED_PATTERNS[@]}"; do
  if echo "$FILE_PATH" | grep -qiE "$pattern"; then
    echo "BLOCKED: 機密ファイルへの書き込みは禁止: $FILE_PATH"
    exit 2
  fi
done
```

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": ["bash hooks/protect-secrets.sh"]
      }
    ]
  }
}
```

## パターン4: ファイル変更の自動バリデーション

### 背景: CLAUDE.mdが1,000行超えてAIが混乱

ルールを追加し続けた結果、CLAUDE.mdが肥大化して矛盾が発生。AIが指示と逆の動作を始めた。200行以内に抑え、詳細は `.claude/agents/` に分離するルールを作った。

### 実装

```
#!/bin/bash
# hooks/validate-files.sh
INPUT=$(cat -)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# CLAUDE.mdの行数チェック
if [[ "$FILE_PATH" == *"CLAUDE.md" ]]; then
  LINES=$(wc -l < "$FILE_PATH" | tr -d ' ')
  if [ "$LINES" -gt 200 ]; then
    echo "WARNING: CLAUDE.mdが${LINES}行です（上限200行）。.claude/agents/への分離を検討してください"
  fi
fi

# package.jsonの変更検知
if [[ "$FILE_PATH" == *"package.json" ]]; then
  echo "INFO: package.jsonが変更されました。npm installの実行を忘れずに"
fi
```

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": ["bash hooks/validate-files.sh"]
      }
    ]
  }
}
```

PostToolUseのstdout出力はClaudeにフィードバックされる。警告でAIの次の行動を誘導できる。

## パターン5: 環境コンテキストの自動注入

### 背景: cronがmacOSで動かない

以前cronジョブを設定したが、macOSのフルディスクアクセス制限で全滅した。launchdに移行して解決したが、こうした環境固有の制約をAIに毎回説明するのは非効率だ。

### 実装

```
#!/bin/bash
# hooks/inject-context.sh
INPUT=$(cat -)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# crontab使用を検知してlaunchdを推奨
if echo "$COMMAND" | grep -qE "crontab|cron"; then
  echo "NOTE: macOSではcronにフルディスクアクセスの制限があります。launchdを使ってください"
  exit 0
fi

# Node.jsバージョンの注入
if echo "$COMMAND" | grep -qE "^(node|npm|npx|pnpm)"; then
  NODE_V=$(node -v 2>/dev/null || echo "not found")
  echo "INFO: Node.js $NODE_V"
fi
```

`exit 0` で処理を許可しつつ、stdoutでコンテキストを渡す。AIはこの情報を踏まえて適切な判断をしてくれる。

## Hooks設計の3原則

実運用で学んだ原則をまとめる。

### 1. 禁止はHooksで、推奨はCLAUDE.mdで

「絶対にやってはいけないこと」はHooksで物理的にブロックする。「こうしてほしい」という推奨事項はCLAUDE.mdに書く。この使い分けが安定運用の鍵だ。

### 2. exit codeで制御する

* `exit 0`: 正常（ツール実行を許可、stdoutはフィードバック）
* `exit 2`: ブロック（ツール実行を中止、メッセージをAIにフィードバック）

### 3. 軽量に保つ

Hooksはツール実行のたびに呼ばれる。重い処理を入れるとClaude Code全体が遅くなる。外部API呼び出しは `Stop` イベントなど頻度の低いタイミングに限定する。

## まとめ

| パターン | 目的 | イベント |
| --- | --- | --- |
| 危険コマンドブロック | 事故防止 | PreToolUse |
| 承認パイプライン | 対外アクション制御 | PreToolUse |
| 機密ファイル保護 | 情報漏洩防止 | PreToolUse |
| ファイルバリデーション | 品質維持 | PostToolUse |
| コンテキスト注入 | 環境適応 | PreToolUse |

自動化率98%の運用を支えているのは、こうした地味だが確実な仕組みだ。

自動化は「AIの能力を制限する」ためではなく「安心して委任するための仕組み」。月5万円のAI投資で会社を回している身として、事故のコストを最小化するHooksへの投資は最もリターンが大きいと実感している。

---

Claude Codeの実践ノウハウをさらに深く知りたい方は、Zennで書籍を公開しています。Hooks以外にも、CLAUDE.mdの設計、エージェント分割、自動化パイプラインの構築など、実運用で得た知見をまとめています。

👉 [Zenn 書籍一覧](https://zenn.dev/joinclass?tab=books)
