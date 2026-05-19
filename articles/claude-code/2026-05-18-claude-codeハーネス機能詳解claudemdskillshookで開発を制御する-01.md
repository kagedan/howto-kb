---
id: "2026-05-18-claude-codeハーネス機能詳解claudemdskillshookで開発を制御する-01"
title: "Claude Codeハーネス機能詳解：CLAUDE.md・SKILLS・HOOKで開発を制御する"
url: "https://zenn.dev/yuki1027/articles/e82bf4b89552ae"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "API", "Python"]
date_published: "2026-05-18"
date_collected: "2026-05-19"
summary_by: "auto-rss"
query: ""
---

# はじめに

Claude Codeには多くのビルトイン機能がありますが、その中でも**ハーネス機能**は、AI支援開発の振る舞いを制御する重要な仕組みです。

**ハーネス機能**とは、Claude Codeの動作を制御・カスタマイズするための設定ファイルや機能の総称で、以下が含まれます：

* **CLAUDE.md**: プロジェクトコンテキストの定義
* **Memory**: 永続的な記憶の管理
* **SKILLS**: 定型タスクのコマンド化
* **HOOK**: イベント駆動の自動実行
* **settings.json**: プロジェクト固有設定

この記事では、これらのハーネス機能を詳しく解説し、実践的な活用方法と長期運用時の注意点（コンテキスト劣化問題）を紹介します。

**対象読者**:

* Claude Codeの基本操作は理解している
* より高度な制御・カスタマイズをしたい
* 長期的なプロジェクトでClaude Codeを活用したい

**前提記事**:

---

# 1. CLAUDE.md：プロジェクトコンテキストの中核

## 1.1 CLAUDE.mdとは

`CLAUDE.md` はプロジェクトルートに配置するMarkdownファイルで、Claude Codeが会話の開始時に自動的に読み込むプロジェクトコンテキストです。

**役割**:

* プロジェクトの全体像をAIに伝える
* コーディング規約・開発フローを定義
* よく使うコマンドを記録

## 1.2 CLAUDE.mdに書くべき内容

### 1. プロジェクト概要

```
# プロジェクト名

このプロジェクトは〇〇を目的とした××です。

## 技術スタック
- 言語: Python 3.11
- フレームワーク: FastAPI
- データベース: PostgreSQL
- インフラ: Docker Compose
```

### 2. ファイル構成・命名規則

```
## ディレクトリ構造

- `src/`: アプリケーションコード
  - `api/`: APIエンドポイント
  - `models/`: データモデル
  - `services/`: ビジネスロジック
- `tests/`: テストコード
- `docs/`: ドキュメント

## 命名規則
- モジュール: `snake_case.py`
- クラス: `PascalCase`
- 関数: `snake_case()`
- 定数: `UPPER_SNAKE_CASE`
```

### 3. コーディング規約

```
## コーディング規約

- Linter: ruff
- Formatter: black (line-length=100)
- 型ヒント必須
- Docstring: Google Style
- テストカバレッジ: 80%以上
```

### 4. 開発フロー

```
## 開発フロー

1. Issueから機能ブランチを作成 (`feature/issue-123`)
2. 実装・テスト
3. `ruff check && pytest` でチェック
4. PRを作成（テンプレートに従う）
5. レビュー後にマージ
```

### 5. よく使うコマンド

```
## よく使うコマンド

- テスト実行: `pytest tests/ -v`
- カバレッジ確認: `pytest --cov=src tests/`
- ローカルサーバー起動: `uvicorn src.main:app --reload`
- マイグレーション: `alembic upgrade head`
- Lintチェック: `ruff check src/`
- フォーマット: `black src/`
```

### 6. プロジェクト固有の制約・注意事項

```
## 注意事項

- **認証**: 現在OAuth 2.0に移行中（2026-06-30まで）。新規実装はOAuthを使用。
- **データベース**: テストは実DBを使用（モック禁止）。過去にモックとの乖離で障害発生。
- **API**: RESTful設計に従う。破壊的変更はバージョニング。
```

## 1.3 CLAUDE.mdの実践例

### Zenn記事リポジトリの例

```
# Zenn記事リポジトリ

Zennプラットフォームへの技術ブログ記事投稿用リポジトリ。

## プロジェクト構成

- `articles/`: 記事ファイル（.md）
- `books/`: 書籍コンテンツ

## 記事フォーマット

### Frontmatter（必須項目）
- `title`: 記事タイトル
- `emoji`: 記事のアイコン
- `type`: "tech" または "idea"
- `topics`: トピックの配列（最大5つ）
- `published`: 公開状態（true/false）

### ファイル命名規則
- 12桁のランダム英数字.md（例: `5cb9fa060a139d.md`）
- Zenn CLIで自動生成

## Claude Codeの役割

- 記事のアイデア出し、構成提案
- 文章の校正・改善（日本語の自然さ、読みやすさ）
- 技術的正確性のチェック
- メタデータ管理（topics、emoji提案）

## Zenn CLIコマンド

- 新規記事: `npx zenn new:article`
- プレビュー: `npx zenn preview`（http://localhost:8000）
- 記事リスト: `npx zenn list:articles`

## 記事執筆のベストプラクティス

- 技術的に正確な情報を提供
- コード例は動作確認済みのものを使用
- 1記事1テーマ（最大2テーマ）で簡潔に
- 読者に寄り添った自然な日本語
```

## 1.4 CLAUDE.mdのメンテナンス

CLAUDE.mdは**生きたドキュメント**です。定期的に更新しないと、情報が陳腐化します（詳細はセクション6で解説）。

### 更新タイミング

* 技術スタックの変更時
* 開発フローの見直し時
* 新しい制約・注意事項が発生した時
* 月1回の定期レビュー

---

# 2. Memory：永続的な記憶の管理

## 2.1 Memoryとは

Claude Codeは会話から重要な情報を自動的に抽出し、`.claude/projects/[project-path]/memory/` ディレクトリに永続的に保存します。

**CLAUDE.mdとの違い**:

* **CLAUDE.md**: プロジェクト全体の静的な情報
* **Memory**: 会話から学習した動的な情報

## 2.2 Memoryの種類と構造

各Memoryは個別のMarkdownファイルとして保存されます：

```
---
name: memory_slug
description: 一行の説明文
metadata:
  type: user | feedback | project | reference
---

メモリの本文

**Why:** 理由・背景

**How to apply:** 適用方法
```

### 1. user：ユーザー情報

```
---
name: user_role
description: ユーザーの役割と専門性
metadata:
  type: user
---

ユーザーはデータサイエンティストで、Python/機械学習に精通している。
フロントエンド開発は初心者レベル。

**How to apply:** 
- バックエンド実装は詳細な説明不要
- フロントエンドは丁寧に説明
```

### 2. feedback：過去のフィードバック

```
---
name: feedback_testing
description: テスト方針についてのフィードバック
metadata:
  type: feedback
---

統合テストは実データベースを使用する。モックは使わない。

**Why:** 2025年にモックとプロダクションの乖離で本番障害が発生した経緯がある

**How to apply:** テスト作成時は常に実データベースを使用。モック提案は避ける。
```

### 3. project：プロジェクト状態

```
---
name: project_auth_migration
description: 進行中の認証システム移行
metadata:
  type: project
---

認証システムをJWTからOAuth 2.0に移行中（2026-06-30まで）

**Why:** コンプライアンス要件により、OAuth 2.0対応が必須に

**How to apply:** 
- 新規実装は必ずOAuth 2.0を使用
- 既存のJWT実装は段階的に移行
- 両方式の共存期間は最小限に
```

### 4. reference：外部リソース

```
---
name: reference_issue_tracker
description: 課題管理システムの場所
metadata:
  type: reference
---

- バグトラッキング: Linear project "BUG"
- 機能要望: GitHub Discussions
- 設計ドキュメント: Notion workspace

**How to apply:** 
- バグ報告時はLinearにリンク
- 新機能提案時はGitHub Discussionsを参照
```

## 2.3 Memoryの活用方法

### 明示的な記録

```
ユーザー: 「プロジェクトではPytestを使うことを覚えておいて」
Claude: Memoryに保存しました（project_testing_framework.md）
```

### 自動抽出

会話中に以下を検出すると自動保存：

* ユーザーの好み・スキルレベル
* プロジェクトの重要な決定事項
* 繰り返される指摘（フィードバック）

### MEMORY.mdでの管理

`.claude/projects/[project-path]/memory/MEMORY.md` がインデックスファイル：

```
- [ユーザー役割](user_role.md) — データサイエンティスト、Python専門
- [テスト方針](feedback_testing.md) — 実DB使用、モック禁止
- [認証移行](project_auth_migration.md) — OAuth 2.0移行中（〜2026-06-30）
- [課題管理](reference_issue_tracker.md) — Linear/GitHub Discussions
```

## 2.4 Memoryのメンテナンス

### 定期的な整理（月1回推奨）

```
# Memoryディレクトリを確認
ls -lt ~/.claude/projects/[project-path]/memory/

# 確認項目
□ 完了したプロジェクト記録を削除
□ 変更された方針を更新
□ 陳腐化したreferenceを削除
□ MEMORY.mdのインデックスを整理
```

### 古い情報の削除

```
# 例: 完了した移行作業のMemoryを削除
rm ~/.claude/projects/my-project/memory/project_auth_migration.md

# MEMORY.mdからもエントリを削除
```

---

# 3. SKILLS：定型タスクのコマンド化

## 3.1 SKILLSとは

定型的なタスクを `/skill-name` コマンドとして登録し、再利用可能にする機能です。

**配置場所**: `.claude/skills/[skill-name].md`

## 3.2 SKILLSの作成方法

### 基本構造

```
<!-- .claude/skills/review.md -->
---
name: review
description: コードレビューを実施する
---

# Instructions

1. `git diff` で変更内容を確認
2. 以下の観点でレビュー：
   - コーディング規約遵守（CLAUDE.md参照）
   - セキュリティ脆弱性（OWASP Top 10）
   - パフォーマンス問題
   - テストカバレッジ
3. 問題があれば具体的な修正案を提示
4. 問題がなければ「LGTM」と報告
```

呼び出し方：

## 3.3 実践的なSKILLS例

### 1. コードレビュー

```
<!-- review.md -->
---
name: review
description: 変更内容を多角的にレビュー
---

# Review Checklist

## 1. コーディング規約
- CLAUDE.mdの規約に準拠しているか
- 命名規則が一貫しているか

## 2. セキュリティ
- 入力値のバリデーションは十分か
- SQLインジェクション対策はあるか
- 認証・認可の実装は適切か

## 3. パフォーマンス
- N+1クエリはないか
- 不要なループ処理はないか

## 4. テスト
- テストケースは十分か
- エッジケースをカバーしているか

## 5. ドキュメント
- Docstringは適切か
- 複雑なロジックにコメントがあるか
```

### 2. テスト実行

```
<!-- test.md -->
---
name: test
description: テストを実行し、結果を分析
---

# Test Execution Flow

1. `pytest tests/ -v --cov=src` を実行
2. テスト結果を確認：
   - ✅ 全テストPass → 「テスト成功」と報告
   - ❌ 失敗あり → 失敗理由を分析
3. カバレッジを確認（目標: 80%以上）
4. カバレッジ不足の箇所を指摘
```

### 3. デプロイ手順

```
<!-- deploy.md -->
---
name: deploy
description: ステージング環境へのデプロイ
---

# Deployment Checklist

## Pre-deployment
1. `git status` で変更がすべてコミット済みか確認
2. `/test` でテストを実行
3. `ruff check && black --check src/` でLintチェック

## Deployment
4. `docker-compose build` でビルド
5. `docker-compose up -d` でコンテナ起動
6. ヘルスチェック: `curl http://localhost:8000/health`

## Post-deployment
7. 主要エンドポイントの動作確認
8. ログ確認: `docker-compose logs -f`

## ⚠️ 注意
- 本番デプロイは承認後に手動で実行
```

### 4. Zenn記事執筆支援

```
<!-- zenn-draft.md -->
---
name: zenn-draft
description: Zenn記事の構成案を作成
---

# Article Drafting Flow

1. トピックを確認
2. 対象読者を明確化（初心者/中級者/上級者）
3. 構成案を3パターン提示：
   - パターンA: 入門編（基礎から丁寧に）
   - パターンB: 実践編（ハンズオン形式）
   - パターンC: 深掘り編（内部実装・原理）
4. ユーザーが選択したパターンでアウトラインを作成
5. 各セクションの概要（2-3行）を提示
```

## 3.4 SKILLSの管理

### スキル一覧の確認

### 不要なスキルの削除

```
rm .claude/skills/old-skill.md
```

### チームでの共有

```
git add .claude/skills/
git commit -m "Add code review skill"
```

---

# 4. HOOK：イベント駆動の自動実行

## 4.1 HOOKとは

特定のイベント時に自動実行されるシェルコマンドを定義できます。`settings.json` で設定します。

**役割**:

* プロンプト送信時の注意喚起
* ファイル編集後の自動チェック
* セッション開始時の初期化

## 4.2 主要なHOOKの種類

### 1. user-prompt-submit-hook

ユーザーがプロンプトを送信した直後に実行：

```
{
  "hooks": {
    "user-prompt-submit-hook": "echo '📝 記事執筆モード: 校正と正確性を重視してください'"
  }
}
```

ツール実行後に実行（`$TOOL_NAME`, `$FILE_PATH` が利用可能）：

```
{
  "hooks": {
    "tool-result-hook": "[ \"$TOOL_NAME\" = \"Edit\" ] && echo '✅ ファイル編集完了: $FILE_PATH'"
  }
}
```

### 3. session-start-hook

セッション開始時に実行：

```
{
  "hooks": {
    "session-start-hook": "echo \"セッション開始: $(date)\" && cat CONTRIBUTING.md"
  }
}
```

## 4.3 実践的なHOOK例

### パターン1: プロジェクトモードの明示

```
{
  "hooks": {
    "session-start-hook": "echo '🚀 API開発モード: RESTful設計・テストカバレッジ80%以上を厳守'"
  }
}
```

### パターン2: 認証移行の注意喚起

```
{
  "hooks": {
    "user-prompt-submit-hook": "grep -qi 'auth\\|jwt\\|token' <<< \"$USER_PROMPT\" && echo '⚠️ 認証システム移行中：OAuth 2.0を使用してください（〜2026-06-30）' || true"
  }
}
```

### パターン3: ファイル編集時の自動フォーマット

```
{
  "hooks": {
    "tool-result-hook": "[ \"$TOOL_NAME\" = \"Edit\" ] && [[ \"$FILE_PATH\" == *.py ]] && black \"$FILE_PATH\" && echo '✨ フォーマット完了' || true"
  }
}
```

### パターン4: コミット前のチェックリスト表示

```
{
  "hooks": {
    "user-prompt-submit-hook": "grep -qi 'commit' <<< \"$USER_PROMPT\" && cat <<'CHECKLIST'\n📋 コミット前チェックリスト\n□ テスト実行済み\n□ Lintチェック済み\n□ コミットメッセージは明確\nCHECKLIST\n || true"
  }
}
```

### パターン5: 統計情報の記録

```
{
  "hooks": {
    "session-start-hook": "mkdir -p .claude/logs && echo \"$(date),session_start\" >> .claude/logs/activity.csv",
    "tool-result-hook": "echo \"$(date),$TOOL_NAME\" >> .claude/logs/activity.csv"
  }
}
```

## 4.4 HOOKの設計パターン

### 原則

1. **冪等性**: 何度実行しても安全
2. **エラーハンドリング**: `|| true` で失敗を許容
3. **パフォーマンス**: 重い処理は避ける
4. **可読性**: 複雑なロジックはスクリプトファイルに分離

### 悪い例

```
{
  "hooks": {
    // ❌ エラーで停止する
    "session-start-hook": "some-command-that-might-fail",
    
    // ❌ 重すぎる処理
    "tool-result-hook": "npm install && npm test"
  }
}
```

### 良い例

```
{
  "hooks": {
    // ✅ エラーを許容
    "session-start-hook": "some-command || true",
    
    // ✅ 軽量な処理のみ
    "tool-result-hook": "[ \"$TOOL_NAME\" = \"Edit\" ] && echo '編集完了' || true"
  }
}
```

---

# 5. settings.json：プロジェクト固有設定

## 5.1 settings.jsonでできること

`.claude/settings.json` でプロジェクト全体の設定を定義します。

### 主な設定項目

1. 権限管理（`permissions`）
2. 環境変数（`env`）
3. HOOK設定（`hooks`）
4. MCP（Model Context Protocol）サーバー設定

## 5.2 権限管理

頻繁に使うコマンドを自動許可：

```
{
  "permissions": {
    "allow": [
      "Bash(npx zenn *)",
      "Bash(pytest tests/*)",
      "Bash(ruff check *)",
      "Read(src/**/*.py)",
      "Read(tests/**/*.py)"
    ]
  }
}
```

**注意**: ワイルドカード展開はシェル依存です。安全な範囲で設定してください。

## 5.3 環境変数

プロジェクトモードや設定を定義：

```
{
  "env": {
    "PROJECT_MODE": "api-development",
    "REVIEW_LEVEL": "strict",
    "TEST_COVERAGE_TARGET": "80"
  }
}
```

Claude Codeは`$PROJECT_MODE`等を参照できます（HOOKで利用可能）。

## 5.4 MCP（Model Context Protocol）サーバー設定

外部サービスとの連携：

```
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"]
    }
  }
}
```

## 5.5 完全な設定例

Zenn記事リポジトリの`.claude/settings.json`：

```
{
  "permissions": {
    "allow": [
      "Bash(npx zenn *)",
      "Bash(ls articles/*)",
      "Bash(ls books/*)",
      "Bash(cat articles/*.md)",
      "Bash(cat books/*.md)",
      "Bash(find articles -name '*.md')",
      "Read(articles/*.md)",
      "Read(books/*.md)"
    ]
  },
  "env": {
    "PROJECT_MODE": "article-writing",
    "ARTICLE_MAX_LENGTH": "10000",
    "TARGET_AUDIENCE": "beginner-intermediate"
  },
  "hooks": {
    "session-start-hook": "echo '📝 Zenn記事執筆モード: 校正・正確性・簡潔さを重視'",
    "user-prompt-submit-hook": "grep -qi 'publish' <<< \"$USER_PROMPT\" && echo '⚠️ 公開前チェック: frontmatter確認・校正完了・画像リンク確認' || true"
  }
}
```

## 5.6 settings.local.jsonとの使い分け

* **settings.json**: プロジェクト全体で共有（Gitにコミット）
* **settings.local.json**: 個人固有の設定（Gitで除外）

```
# .gitignore
.claude/settings.local.json
.claude/logs/
```

個人設定の例：

```
{
  "env": {
    "MY_EDITOR": "vim",
    "DEBUG_MODE": "true"
  },
  "hooks": {
    "session-start-hook": "echo 'Welcome back!'"
  }
}
```

---

# 6. ハーネス機能の真価：コンテキスト劣化への対抗策

ハーネス機能は単なる「便利機能」ではありません。長期運用でAIが信頼できるパートナーであり続けるための**必須の対抗策**です。

## 6.1 コンテキスト劣化の2つの面

コンテキスト劣化には、異なるメカニズムで発生する2つの面があります：

### 面1：運用面の劣化（ドキュメント陳腐化）

**問題**: プロジェクトは日々進化するが、CLAUDE.md/Memoryは手動更新しないと古いまま

**メカニズム**:

* 技術スタック変更（Jest → Vitest）
* アーキテクチャ変更（REST → GraphQL）
* ルール追加・変更を文書に反映し忘れ

**対策**: Claude自身にドキュメントメンテを依頼することで解決可能（後述）

---

### 面2：長期セッション面の劣化（コンテキストの腐敗）

**問題**: ドキュメントが最新でも、長期セッションでは優先度が下がり、ルールが守られなくなる

**メカニズム**:

1. **優先度の低下**: 会話が長くなると、直近のやりとりが優先され、CLAUDE.mdの重要度が下がる
2. **Compaction（圧縮）**: コンテキストウィンドウが限界に近づくと、古い情報が要約・切り落とされる
3. **実コードからの暗黙学習**: AIは実際のコードパターンを学習し、ドキュメントより実態を優先し始める

**対策**: ハーネスツール（SKILLS、HOOK）で**毎回イベント駆動で喚起**することが必須（次セクション）

---

## 6.2 運用面の劣化：ドキュメント陳腐化

### 症状

```
【2ヶ月前】
CLAUDE.md: 「テストはJestを使用」
Memory: 「REST API設計を採用」

↓ プロジェクトの進化

【現在】
実際: Vitestに移行済み、GraphQLに移行済み

↓ 結果

Claude: 古いコンテキストに基づいて誤った提案
「Jestのテストを追加しました」
「RESTエンドポイントを実装しました」
```

### 対策：Claude自身にメンテさせる

**方法1：月次レビューを依頼**

```
「先月のgit logを確認して、CLAUDE.mdとMemoryを最新化してください」
```

**方法2：大きな変更時に明示的指示**

```
「VitestへのJest移行が完了したので、CLAUDE.mdを更新してください」
```

**方法3：SKILLSで定期メンテを自動化**

```
<!-- .claude/skills/context-refresh.md -->
---
name: context-refresh
description: CLAUDE.mdとMemoryを最新の状態に同期
---

# Context Refresh Flow

1. 過去1ヶ月のgit logを確認
   ```bash
   git log --oneline --since="1 month ago" --all
```

2. 大きな変更をリストアップ

   * 技術スタック変更
   * アーキテクチャ変更
   * 新しい規約・制約
3. CLAUDE.mdの該当箇所を更新

   * 廃止された技術を削除
   * 新しい技術を追加
   * 規約を最新化
4. Memoryを整理

   ```
   ls -lt ~/.claude/projects/[project-path]/memory/
   ```

   * 完了したproject Memoryを削除
   * 古いfeedback Memoryを更新
   * 変更されたreference Memoryを修正
5. 変更内容を報告

```
→ `/context-refresh` で定期メンテ完了

---

## 6.3 長期セッション面の劣化：コンテキストの腐敗

こちらが**より深刻**かつ**ハーネスツールが必須になる理由**です。

### 症状：ドキュメントが最新でもルールを守らなくなる

以下のようなケースで発生します：

**症状1：優先度低下によるルール無視**
```

【CLAUDE.md（最新）】  
命名規則: snake\_case

【長期セッション（100往復後）】  
Claude: camelCaseで関数を実装  
→ 会話の流れでCLAUDE.mdの優先度が低下

```
**症状2：Compactionによる切り落とし**
```

【CLAUDE.md】  
「モックは使わず実DBでテストする」

【長期セッション（150往復後、Compaction発生）】  
Claude: 「モックを使ったテストを追加しました」  
→ コンテキスト圧縮時にCLAUDE.mdの該当部分が要約・削除された

【CLAUDE.md（最新）】  
「OAuth 2.0を使用」

【実際のコードベース】  
古いJWT実装が多数残存（移行途中）

【長期セッション】  
Claude: 「既存コードに合わせてJWTで実装しました」  
→ 実コードのパターンを学習し、CLAUDE.mdより優先

```
### なぜ守らなくなるのか：優先順位のメカニズム

Claude Codeは複数の情報源を参照しますが、長期化で優先順位が変化します：

**初期（会話開始〜50往復）**
```

1. CLAUDE.md / Memory（高優先）
2. 現在の会話内容
3. 実際のコードベース

1. 現在の会話内容（最新）← 最優先に
2. 実際のコードベース（現実）← 学習強化
3. Memory（中期記憶）← 優先度低下
4. CLAUDE.md（静的情報）← さらに低下

```
結果：**ドキュメントが最新でも、会話の流れや実コードに引きずられて無視される**

---

## 6.4 ハーネスツールによる対抗：イベント駆動で常時喚起

**解決策の核心**: HOOKとSKILLSで**毎回イベント時に強制的にルールを思い出させる**

### パターン1：HOOK - イベントごとに自動喚起

**user-prompt-submit-hook**: プロンプト送信時にルールを表示

```json
{
  "hooks": {
    "user-prompt-submit-hook": "grep -qi 'auth\\|jwt\\|token' <<< \"$USER_PROMPT\" && echo '⚠️ 認証実装時の注意：OAuth 2.0を使用（JWT非推奨）' || true"
  }
}
```

→ 認証関連の会話が始まるたびに、**会話コンテキストに直接注意事項が挿入される**

→ Claudeは「直近の指示」として認識し、CLAUDE.mdより優先度が高くなる

**tool-result-hook**: ファイル編集後に自動チェック

```
{
  "hooks": {
    "tool-result-hook": "[ \"$TOOL_NAME\" = \"Edit\" ] && [[ \"$FILE_PATH\" == *test*.py ]] && echo '✅ テスト実装時の確認：実DBを使用していますか？（モック禁止）' || true"
  }
}
```

→ テストファイル編集のたびに注意喚起

→ Compactionで古い情報が消えても、**イベント駆動で毎回再注入**

### パターン2：SKILLS - 手順の標準化でブレを防ぐ

**問題**: 長期セッションで「どうやるんだっけ？」となりがち

**解決**: SKILLSで手順を固定化

```
<!-- .claude/skills/add-auth.md -->
---
name: add-auth
description: 認証機能を追加する標準手順
---

# 認証実装の標準手順

⚠️ **必須**: OAuth 2.0を使用（JWT非推奨）

## 手順

1. 必要なライブラリをインストール
   ```bash
   pip install authlib
```

2. `src/auth/oauth.py` を作成（テンプレートを使用）
3. 環境変数を設定

   * `OAUTH_CLIENT_ID`
   * `OAUTH_CLIENT_SECRET`
4. 実DBを使った統合テストを追加（`tests/test_auth.py`）
5. CLAUDE.mdの「認証」セクションを更新

```
→ `/add-auth` で呼び出せば、**長期セッションでもブレずに正しい手順で実装**

### パターン3：settings.json - 権限管理で意図しない動作を防ぐ

**問題**: 古い技術（Jest）を使おうとしてしまう

**解決**: 新しい技術（Vitest）のみ許可

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run test)",
      "Bash(vitest *)"
    ],
    "deny": [
      "Bash(jest *)"
    ]
  }
}
```

→ 仮にClaude CodeがJestを使おうとしても、**システムレベルでブロック**

---

## 6.5 なぜHOOK/SKILLSが効くのか：コンテキスト注入のメカニズム

**CLAUDE.mdの限界**:

* 会話開始時に1回だけ読み込まれる
* 長期化すると優先度が下がる
* Compactionで切り落とされる可能性

**HOOK/SKILLSの強み**:

* **イベントごとに毎回実行** → 常に「最新の指示」として認識される
* **会話コンテキストに直接注入** → 優先度が最も高い
* **Compactionの影響を受けない** → イベント発生のたびに再注入

### 図解：コンテキストの優先度

**CLAUDE.mdのみの場合**:

```
[会話開始]
CLAUDE.md読み込み（高優先）

↓ 50往復

CLAUDE.md（優先度↓）< 会話履歴

↓ 100往復

CLAUDE.md（優先度↓↓）< 会話履歴 < 実コード学習

↓ 150往復（Compaction）

CLAUDE.md（一部切り落とし）< 会話履歴 < 実コード学習

→ ルール無視
```

**HOOK併用の場合**:

```
[会話開始]
CLAUDE.md読み込み

↓ 50往復

[認証関連プロンプト]
→ user-prompt-submit-hook発火
→ 「OAuth 2.0を使用」が会話に注入（最高優先）

↓ 100往復

[テストファイル編集]
→ tool-result-hook発火
→ 「実DB使用」が会話に注入（最高優先）

↓ 150往復（Compaction）

[認証関連プロンプト]
→ user-prompt-submit-hook発火
→ Compactionで消えた情報も再注入

→ ルール遵守を維持
```

---

## 6.6 まとめ：ハーネスツールは長期運用の生命線

### 運用面の劣化 → Claude自身にメンテさせる

* `/context-refresh` SKILLで定期更新
* 大きな変更時に明示的指示

### 長期セッション面の劣化 → HOOK/SKILLSで常時喚起

* **HOOK**: イベント駆動で毎回ルールを注入
* **SKILLS**: 標準手順を固定化してブレを防ぐ
* **settings.json**: 権限管理で物理的にブロック

**結論**: ハーネス機能（特にHOOK/SKILLS）は、長期セッションでAIが信頼できるパートナーであり続けるための**必須の対抗策**です。

---

# 7. ハーネス機能の組み合わせ戦略

プロジェクトの規模に応じた推奨構成を紹介します。

## 7.1 小規模プロジェクト（個人開発）

```
CLAUDE.md: 基本情報のみ（30-50行）
  - 技術スタック
  - よく使うコマンド
  - 最低限の規約

Memory: 自動記憶に任せる
  - 明示的な記録は最小限

SKILLS: 2-3個
  - deploy
  - test
  - review

HOOK: なし or 1個
  - session-start-hook（モード表示）

settings.json: 最小限
  - 権限管理のみ
```

**メンテナンス**: 3ヶ月に1回CLAUDE.mdをレビュー

## 7.2 中規模プロジェクト（小チーム）

```
CLAUDE.md: 詳細なコンテキスト（100-200行）
  - プロジェクト概要
  - 詳細なファイル構成
  - コーディング規約
  - 開発フロー
  - よく使うコマンド
  - 注意事項

Memory: 積極的に活用
  - user: チームメンバーの役割
  - feedback: 過去の失敗事例
  - project: 進行中のタスク
  - reference: 外部リソース

SKILLS: 5-10個
  - 定型タスクをコマンド化
  - チームで共有

HOOK: 2-3個
  - lint自動実行
  - プロジェクトモード表示
  - 注意喚起

settings.json: 詳細設定
  - 権限管理
  - 環境変数
  - HOOKチェーン
```

**メンテナンス**: 月1回CLAUDE.md/Memoryをレビュー

## 7.3 大規模・複雑なワークフロー

ハーネス機能だけでは限界があります：

**限界のサイン**:

* 複数AIの協調動作が必要（Claude + Copilot の役割分担）
* タスクの段階的実行を自動化したい（計画→実装→テスト→レビュー）
* 失敗時の自動リトライが必要
* 外部システムとの連携が多い（GitHub、CI/CD、Slack等）

→ **オーケストレーションツール**（TAKT等）の検討が必要

詳しくは次の記事で解説します：  
[AIオーケストレーションツールの選び方：TAKT採用までの検討プロセス](/yuki1027/articles/5cb9fa060a139d)

---

# 8. まとめ

## ハーネス機能は開発制御の中核

Claude Codeのハーネス機能（CLAUDE.md、Memory、SKILLS、HOOK、settings.json）は、AI支援開発の振る舞いを細かく制御できる強力な仕組みです。

## コンテキスト劣化への2つの対策

**運用面の劣化**: Claude自身にメンテさせる

* `/context-refresh` SKILLで定期更新
* 大きな変更時に明示的指示

**長期セッション面の劣化**: HOOK/SKILLSで常時喚起

* **HOOK**: イベント駆動で毎回ルールを注入
* **SKILLS**: 標準手順を固定化してブレを防ぐ
* **settings.json**: 権限管理で物理的にブロック

```
📅 推奨メンテナンス
□ /context-refresh で月1回ドキュメント更新
□ 重要ルールはHOOKで自動喚起
□ 定型タスクはSKILLSで標準化
□ HOOKが正しく動作しているか確認
```

## プロジェクトに合った最小構成から

すべての機能を使う必要はありません。必要最小限から始め、段階的に拡張していきましょう。

## 限界を感じたら次のステップへ

ハーネス機能だけでは対応できない場合は、オーケストレーションツールの検討タイミングです。

## シリーズ記事

1. [Claude Code入門 - ビルトイン機能の全体像](/yuki1027/articles/529b8644986509)（前提記事）
2. **Claude Codeハーネス機能詳解：CLAUDE.md・SKILLS・HOOKで開発を制御する**（この記事）
3. [AIオーケストレーションツールの選び方：TAKT採用までの検討プロセス](/yuki1027/articles/5cb9fa060a139d)（次のステップ）

## 参考リンク
