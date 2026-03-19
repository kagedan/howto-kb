# howto-kb - ナレッジベース

Claude関連 + 建設業（土木）のハウツー情報を自動収集・管理するナレッジベース。

## リポジトリ構造

- `articles/` — カテゴリ別のMarkdown記事
  - `claude-code/` — Claude Code開発Tips、CLAUDE.md、コンテキスト管理、Handover
  - `cowork/` — Cowork活用法、トラブルシュート、グローバル指示、スキル開発
  - `antigravity/` — Antigravity（VSCode拡張版Claude Code）固有の情報
  - `ai-workflow/` — その他AI活用全般（プロンプト技法、MCP、API、他AIツール）
  - `construction/` — 土木・建設業全般（施工管理、書類作成、ICT施工、新技術）
- `index.json` — 全記事のメタデータ一覧（検索・フィルタリング用）
- `config/` — RSSフィードURL、X検索クエリの設定
- `scripts/` — 収集・インデックス構築スクリプト

## 記事の参照方法

1. `index.json` で記事一覧を確認し、カテゴリ・タグで絞り込む
2. 該当記事のMarkdownファイルを読んで詳細を参照する

## 記事フォーマット

各記事はfrontmatter付きMarkdown。主なフィールド:
- `id` — `{YYYY-MM-DD}-{slug}-{連番}` 形式
- `title` — 記事タイトル（原文のまま）
- `category` — 上記5カテゴリのいずれか
- `tags` — 英語タグの配列
- `summary_by` — `cowork` / `manual`

## index.json について
- index.json: 全記事の検索インデックス
- index-latest.json: 直近30日分（軽量版）
- index-YYYY-MM.json: 月別アーカイブ

## カテゴリ判定基準

- `claude-code` — Claude Code、CLAUDE.md、コンテキスト管理、Handover関連
- `cowork` — Cowork、デスクトップ自動化関連
- `antigravity` — Antigravity（VSCode拡張）固有の情報
- `ai-workflow` — 上記以外のAI活用全般（プロンプト、MCP、API、他ツール）
- `construction` — 土木・建設業関連
