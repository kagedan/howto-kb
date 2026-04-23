# howto-kb

Claude関連 + 建設業（土木）のハウツー情報を自動収集・管理するナレッジベース。

## 概要

- **対象ジャンル**: Claude関連ツール（Claude Code, Cowork, Antigravity）、AI活用全般、建設業・土木
- **用途**: 自分用ナレッジベースとして検索・参照、業務中にClaudeからRAG的に参照
- **更新方法**: Desktopスケジュールタスクによる自動収集 + 手動登録

## カテゴリ

| カテゴリ | 対象範囲 |
|---|---|
| `claude-code` | Claude Code開発Tips、CLAUDE.md、コンテキスト管理 |
| `cowork` | Cowork活用法、トラブルシュート、スキル開発 |
| `antigravity` | Antigravity（VSCode拡張版Claude Code）固有情報 |
| `ai-workflow` | AI活用全般（プロンプト技法、MCP、API） |
| `construction` | 土木・建設業全般 |

## 収集ソース

| ソース | スクリプト | 頻度 |
|---|---|---|
| RSS/Atom（Zenn, note, Anthropic等） | crawl_rss.py | 毎日 |
| Qiita API | crawl_rss.py | 毎日 |
| X（SocialData API） | crawl_x.py | 毎日 |
| NotebookLM | crawl_notebooklm.py | 毎週月曜 |

休日等で更新が途切れた場合、次回実行時にキャッチアップ機能が自動で取得件数を増加させる。

## 使い方

`index.json` で記事を検索し、`articles/{category}/` 内のMarkdownファイルを参照。
Supabase経由でのクエリ参照も可能（詳細はCLAUDE.mdを参照）。

## スクリプト

### 収集
- `crawl_rss.py` — RSS/Atom + Qiita APIから新規記事を検出し、readabilityで記事本文も全文取得
- `crawl_x.py` — SocialData API経由でX投稿を検索・深掘り（スレッド正規化・Article本文対応）
- `crawl_notebooklm.py` — NotebookLMの差分ソースを検出（要nlmコマンド）

### 生成・フィルタ
- `_generate_mds.py` — RSS+Xクロール→MD生成→index構築を一括実行
- `_generate_rss_mds.py` — RSS記事のMD生成（stdin JSON入力）
- `_filter_x_auto.py` — X投稿の自動フィルタリング+MD生成（stdin JSON入力）
- `export_clippings.py` — RT記事の外部リンク先を全文取得し、Obsidian clippings/にMD出力（readability-lxml使用）

### インデックス・同期
- `build_index.py` — articles/配下からindex.json, index-latest.json, 月別アーカイブを生成
- `sync_supabase.py` — index.jsonのメタデータをSupabaseにupsert
- `add_manual.py` — 記事の手動登録

### メンテナンス（ワンショット用）
- `refetch_placeholders.py` — 本文がプレースホルダのままのX投稿MDを SocialData APIから再取得（過去分の棚卸し用、2026-04-23実施済み）
- `refetch_rss_fulltext.py` — RSS系MDの本文を記事URLから readability で全文取得（過去分の棚卸し用、2026-04-23実施済み）
