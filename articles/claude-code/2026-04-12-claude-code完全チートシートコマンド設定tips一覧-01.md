---
id: "2026-04-12-claude-code完全チートシートコマンド設定tips一覧-01"
title: "Claude Code完全チートシート：コマンド・設定・Tips一覧"
url: "https://qiita.com/Hurry_Fox/items/3b6a9d24046b1d608db8"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-12"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

[![](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F1291237%2F15d445ec-01b5-4534-8b89-ff7d93c08ca6.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d7c7cdad4e2b1b970b196e965a89554b)](https://www.amazon.co.jp/dp/B0GJTGTT8Z) [![](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F1291237%2Ff8fdab72-ea26-4e40-84a8-6a09b80b035c.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9b7502838f5cdd5025f3b7ddc5e4a2a1)](https://www.amazon.co.jp/dp/B0GKB2XGR8) [![](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F1291237%2F5380c33d-2d4e-417a-b358-ffe8ab656335.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a7ad335e903cf3ce31dc7097805123e4)](https://www.amazon.co.jp/dp/B0GM87MXH2)

# Claude Code完全チートシート：コマンド・設定・Tips一覧

## はじめに

Claude Codeを使いこなすための完全チートシートです。よく使うコマンド、設定、便利なTipsをまとめました。このページをブックマークして、困ったときにすぐ参照できるようにしておきましょう。

---

## 🚀 基本コマンド

### インストールとセットアップ

```
# インストール
curl -fsSL https://install.claude.com | sh

# バージョン確認
claude --version

# 起動
claude

# ログイン
/login

# ログアウト
/logout
```

### セッション管理

```
# 新しいセッション開始
claude

# 過去のセッション再開
claude --resume
/resume

# 最新セッションを自動再開
claude --continue

# セッション名を変更
/rename <session-name>

# セッションをクリア
/clear

# セッション履歴を表示
/history
```

---

## 💬 会話中のコマンド

### ビルトインコマンド

| コマンド | 説明 | 使用例 |
| --- | --- | --- |
| `/help` | ヘルプを表示 | `/help` |
| `/clear` | セッションをクリア | `/clear` |
| `/compact` | 会話を圧縮 | `/compact` |
| `/resume` | セッション再開 | `/resume` |
| `/rename` | セッション名変更 | `/rename auth-feature` |
| `/init` | CLAUDE.md生成 | `/init` |
| `/permissions` | 権限設定表示 | `/permissions` |
| `/context` | コンテキスト使用量 | `/context` |
| `/usage` | 使用量統計 | `/usage` |
| `/config` | 設定を開く | `/config` |
| `/skills` | 利用可能なSkills | `/skills` |
| `/agents` | Subagents一覧 | `/agents` |
| `/plugins` | Plugins一覧 | `/plugins` |
| `/login` | ログイン | `/login` |
| `/logout` | ログアウト | `/logout` |

### 中断と終了

| キー | 動作 |
| --- | --- |
| `Esc` | 実行中のタスクを中断 |
| `Ctrl+C` | 入力をキャンセル |
| `Ctrl+D` または `/exit` | Claude Codeを終了 |

### パーミッションモード切り替え

| キー | モード |
| --- | --- |
| `Shift+Tab` | モード切り替え |
| - | **Normal**: 毎回確認 |
| - | **Auto-accept**: 自動承認 |
| - | **Plan**: 読み取り専用 |

---

## 📁 ファイル参照

### @メンション

```
# ファイル全体を参照
@src/auth/login.ts

# 特定の行範囲を参照
@src/auth/login.ts#10-50

# ディレクトリを参照
@src/components/

# ファジーマッチング
@auth
（auth関連のファイルを検索）

# MCPリソース参照
@github:repos/owner/repo/issues
@slack:channels/engineering
```

### ファイル操作の依頼例

```
# ファイルを読む
「@src/auth/login.ts を読んでください」

# 複数ファイルを参照
「@src/auth/login.ts と @src/auth/session.ts を比較してください」

# ディレクトリ全体を分析
「@src/api/ の構造を説明してください」

# 画像を参照
「@design/mockup.png のUIを実装してください」
```

---

## ⚙️ 設定ファイル（settings.json）

### ファイルの場所

```
~/.claude/settings.json              # グローバル設定
<project>/.claude/settings.json      # プロジェクト設定
```

### 基本設定

```
{
  "defaultPermissionMode": "normal",
  "respectGitIgnore": true,
  "maxTurns": 50,
  "timeout": 300,
  "defaultModel": "claude-sonnet-4.5"
}
```

### パーミッション設定

```
{
  "defaultPermissionMode": "normal",
  
  "allowedTools": [
    "Read",
    "Edit",
    "Bash"
  ],
  
  "disallowedTools": [
    "Delete"
  ],
  
  "commandWhitelist": [
    "npm test",
    "npm run lint",
    "git status"
  ],
  
  "commandBlacklist": [
    "rm -rf",
    "sudo",
    "curl *",
    "wget"
  ]
}
```

### 監査ログ

```
{
  "audit": {
    "enabled": true,
    "logFile": "~/.claude/audit.log",
    "logLevel": "info",
    "events": [
      "file_read",
      "file_edit",
      "command_execution"
    ]
  }
}
```

### MCP設定

```
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}",
        "SLACK_TEAM_ID": "${SLACK_TEAM_ID}"
      }
    }
  }
}
```

---

## 📝 CLAUDE.md（プロジェクト設定）

### 配置場所

```
project-root/
├── CLAUDE.md              # 推奨
└── .claude/
    └── CLAUDE.md          # 代替
```

### テンプレート

```
# Project: Your Project Name

## Overview
Brief description of the project

## Tech Stack
- Frontend: React 18, TypeScript 5.3
- Backend: Node.js 20, Express
- Database: PostgreSQL 15
- Testing: Jest, React Testing Library

## Commands
Build: `npm run build`
Test: `npm test`
Dev: `npm run dev`
Lint: `npm run lint`
Deploy: `./scripts/deploy.sh`

## Code Style
- Use TypeScript strict mode
- Prefer `const` over `let`
- Use async/await (not .then())
- Maximum line length: 100 characters

## Architecture
- Follow domain-driven design
- Keep services stateless
- Use dependency injection

## Testing
- Write tests for all new features
- Maintain 80%+ coverage
- Run tests before committing

## Known Issues
- [Issue description]
  Workaround: [Solution]
```

---

## 🛠️ Skills

### Skillの配置場所

```
.claude/skills/              # プロジェクト固有
~/.claude/skills/            # ユーザー共通
```

### Skillの基本構造

```
---
name: deploy
description: Deploy to production
version: 1.0.0
tags: [deployment, production]
---

# Deploy Skill

## Steps

### 1. Run tests
```bash
npm test
```

### 2. Build

### 3. Deploy

```
./scripts/deploy.sh production
```

## Success Criteria

* All tests pass
* Build completes
* Deployment successful

# Skills一覧表示

/skills

# Skillを実行

/deploy

# Skill情報を表示

/skill-info deploy

```
---

## 🤖 Subagents

### ビルトインSubagents

| Subagent | 用途 |
|----------|------|
| `code-reviewer` | コードレビュー |
| `debugger` | バグ調査 |
| `test-engineer` | テスト作成 |

### カスタムSubagentの作成

```markdown
<!-- .claude/agents/security-reviewer.md -->
---
name: security-reviewer
description: Security vulnerability scanner
model: claude-opus-4.5
tools:
  - Read
  - Grep
  - WebSearch
---

# Security Reviewer

Scan for security vulnerabilities following OWASP guidelines.

## Scan Strategy
1. SQL Injection
2. XSS vulnerabilities
3. CSRF weaknesses
4. Authentication issues
```

---

## 🔧 ヘッドレスモード

### 基本的な使い方

```
# ワンショット実行
claude -p "バグを修正してください"

# パイプ入力
cat error.log | claude -p "このエラーの原因を説明してください"

# セッション継続
claude --continue -p "次のタスクを実行してください"

# 出力フォーマット指定
claude -p "コードレビューを実行" --format json

# タイムアウト設定
claude -p "テストを実行" --timeout 600

# 最大ターン数設定
claude -p "バグ修正" --max-turns 20

# 自動承認モード
claude -p "テストを修正" --permission-mode auto-accept
```

### CI/CDでの使用例

```
# GitHub Actions
- name: Code Review
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: |
    claude -p "このPRをレビューしてください" \
      --format json \
      --max-turns 5 \
      > review.json
```

---

## 💡 便利なTips

### 1. コンテキスト管理

```
# コンテキスト使用量確認
/context

# 80%を超えたら圧縮
/compact

# 新しいタスクならクリア
/clear
```

### 2. 効率的なプロンプティング

```
❌ 非効率：
「このファイルについて教えて」
「バグはある？」
「セキュリティは？」

✅ 効率的：
「このファイルについて、以下を分析してください：
1. 概要
2. バグの有無
3. セキュリティ問題
4. 改善提案」
```

### 3. 段階的なリファクタリング

```
1. /permission plan          # プランモードに切り替え
2. 「リファクタリング計画を作成」
3. [計画をレビュー]
4. Shift+Tab                 # Normalモードに戻る
5. 「計画を実行してください」
```

### 4. 複数ファイルの一括更新

```
「@src/api/ のすべてのファイルで、
エラーハンドリングを統一してください。

標準形式：
try {
  // logic
} catch (error) {
  logger.error(error);
  throw new ApiError(error.message);
}」
```

### 5. Git worktreesで並行作業

```
# 新しいworktree作成
git worktree add ../project-feature-a -b feature-a
git worktree add ../project-bugfix bugfix-123

# 各worktreeでClaude Code起動
cd ../project-feature-a
claude

cd ../project-bugfix
claude
```

---

## 🔐 セキュリティのベストプラクティス

### 環境変数の設定

```
# APIキーを環境変数で管理
export ANTHROPIC_API_KEY=sk-ant-api03-...

# .bashrc / .zshrc に追加
echo 'export ANTHROPIC_API_KEY=sk-ant-api03-...' >> ~/.bashrc

# macOS Keychain使用
security add-generic-password \
  -a "$USER" \
  -s "anthropic-api-key" \
  -w "sk-ant-api03-..."
```

### .gitignoreに追加

```
# .gitignore
.env
.env.local
.claude/settings.local.json
credentials.json
*.key
*.pem
```

### 安全な設定

```
{
  "defaultPermissionMode": "normal",
  "disallowedTools": ["Delete"],
  "commandBlacklist": [
    "rm -rf",
    "sudo",
    "curl *",
    "wget"
  ],
  "audit": {
    "enabled": true
  }
}
```

---

## 📊 使用量の管理

### 使用量の確認

```
# 今日の使用量
/usage

# コンテキストトークン
/context
```

### トークン削減テクニック

1. **CLAUDE.mdを簡潔に**（500トークン以下）
2. **Skillsに分離**（必要なときだけ読み込み）
3. **定期的に/compact**（会話を圧縮）
4. **適切なモデル選択**（Haiku < Sonnet < Opus）

---

## 🐛 トラブルシューティング

### よくある問題と解決法

| 問題 | 解決法 |
| --- | --- |
| コマンドが見つからない | `export PATH="$HOME/.claude/bin:$PATH"` |
| 認証失敗 | `/login` で再ログイン |
| ネットワークエラー | プロキシ設定確認 |
| 応答がない | `Esc`で中断、`--timeout`設定 |
| ファイルが読めない | `.gitignore`確認、`respectGitIgnore: false` |
| 権限エラー | `Shift+Tab`でモード確認 |

### ログの確認

```
# Claude Codeのログ
tail -f ~/.claude/logs/claude.log

# 監査ログ
tail -f ~/.claude/logs/audit.log

# MCPサーバーログ
cat ~/.claude/logs/mcp-github.log
```

### デバッグモード

```
# 詳細ログ
claude --verbose

# デバッグモード
claude --debug
```

---

## 🎯 実践例

### バグ修正ワークフロー

```
1. エラーログを共有
   「以下のエラーが発生しています：
   [エラー内容を貼り付け]」

2. 原因を特定
   「@src/auth/login.ts を確認してください」

3. 修正を依頼
   「このバグを修正してください」

4. テストを実行
   「npm testを実行して確認してください」

5. コミット
   「変更をコミットしてください」
```

### PR作成ワークフロー

```
1. 変更をサマリー
   「今回の変更内容をサマリーしてください」

2. PR作成
   「PRを作成してください。
   タイトル：認証機能の改善
   説明：詳細な変更内容を含めて」

3. テスト情報追加
   「テスト方法を追加してください」
```

### リファクタリングワークフロー

```
1. プランモードに切り替え
   Shift+Tab → Plan

2. 計画作成
   「@src/utils/ をモダンなES2024記法に
   リファクタリングする計画を作成してください」

3. 計画をレビュー
   [Claude Codeが生成した計画を確認]

4. 実行
   Shift+Tab → Normal
   「計画を実行してください」

5. テストで検証
   「リファクタリング後のコードでテストを実行」
```

---

## 📚 参考リンク

---

## まとめ

このチートシートをブックマークして、Claude Codeを使いこなしましょう！

困ったときは：

1. `/help` でヘルプを確認
2. このチートシートを参照
3. 公式ドキュメントを確認
4. コミュニティで質問

Happy Coding with Claude Code! 🚀
