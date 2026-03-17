# howto-kb

Claude関連 + 建設業（土木）のハウツー情報を自動収集・管理するナレッジベース。

## 概要

- **対象ジャンル**: Claude関連ツール（Claude Code, Cowork, Antigravity）、AI活用全般、建設業・土木
- **用途**: 自分用ナレッジベースとして検索・参照、業務中にClaudeからRAG的に参照
- **更新方法**: Coworkスケジュールタスクによる自動収集 + 手動登録

## カテゴリ

| カテゴリ | 対象範囲 |
|---|---|
| `claude-code` | Claude Code開発Tips、CLAUDE.md、コンテキスト管理 |
| `cowork` | Cowork活用法、トラブルシュート、スキル開発 |
| `antigravity` | Antigravity（VSCode拡張版Claude Code）固有情報 |
| `ai-workflow` | AI活用全般（プロンプト技法、MCP、API） |
| `construction` | 土木・建設業全般 |

## 使い方

`index.json` で記事を検索し、`articles/{category}/` 内のMarkdownファイルを参照。
