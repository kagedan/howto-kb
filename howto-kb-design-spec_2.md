# Howto Knowledge DB - 設計仕様書

> Claude関連 + 建設業（土木）のハウツー情報を自動収集・管理するナレッジベース

## 1. プロジェクト概要

### 目的
- 自分用のナレッジベースとして検索・参照
- 業務中にClaude（Claude Code / Cowork / Claude.ai）からRAG的に参照

### 対象ジャンル
- Claude関連ツール（Claude Code, Cowork, Antigravity）
- AI活用全般（プロンプト技法, MCP, API活用）
- 建設業・土木

### 保存先
- GitHubリポジトリ（`howto-kb`）

### 実行環境
- **Coworkスケジュールタスク**を主軸（MAXプラン内、追加APIコスト不要）
- git pushにはGitHub MCP経由を第一候補とし、不可の場合はCowork直接push設定を検証
- 上記いずれも不可の場合のフォールバックとしてGitHub Actionsを使用

---

## 2. カテゴリ・タグ設計

### カテゴリ（5分類）

| カテゴリID | 対象範囲 |
|---|---|
| `claude-code` | Claude Code開発Tips、CLAUDE.md、コンテキスト管理、Handover |
| `cowork` | Cowork活用法、トラブルシュート、グローバル指示、スキル開発 |
| `antigravity` | Antigravity（VSCode拡張版Claude Code）固有の情報 |
| `ai-workflow` | その他AI活用全般（プロンプト技法、MCP、API、他AIツール） |
| `construction` | 土木・建設業全般（施工管理、書類作成、ICT施工、新技術） |

### タグ
- **英語で統一**（表記ゆれ防止、Claudeが日本語質問にも自然にマッチ可能）
- 例: `context-management`, `handover`, `skill-development`, `excel-vba`, `pipe-replacement`, `specification-search`
- 自由タグ方式（事前定義リストなし、記事登録時にClaudeが自動付与）

---

## 3. Markdownテンプレート

各記事は以下のfrontmatter付きMarkdownファイルとして保存する。

```markdown
---
id: "2026-03-17-claude-code-context-tips-01"
title: "Claude Codeでのコンテキスト管理のコツ"
url: "https://zenn.dev/example/articles/claude-code-context"
source: "zenn"
category: "claude-code"
tags: ["context-management", "CLAUDE-md", "handover"]
date_published: "2026-03-15"
date_collected: "2026-03-17"
summary_by: "cowork"
---

Claude Codeでコンテキストが50%を超えた場合、HANDOVERファイルを出力して
引き継ぐ方法が有効。CLAUDE.mdにルールを記載しておくことで自動的にトリガー
される。キーポイントは...（200〜300字の日本語要約）
```

### frontmatterフィールド定義

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `id` | string | ○ | `{YYYY-MM-DD}-{slug}-{連番}` 形式 |
| `title` | string | ○ | 記事タイトル（原文のまま） |
| `url` | string | - | 元記事のURL（手動登録で無い場合もある） |
| `source` | string | ○ | `x` / `zenn` / `qiita` / `note` / `anthropic` / `notebooklm` / `chat` / `manual` |
| `category` | string | ○ | 上記5カテゴリのいずれか |
| `tags` | string[] | ○ | 英語タグの配列（Claudeが自動付与） |
| `date_published` | string | - | 元記事の公開日（YYYY-MM-DD） |
| `date_collected` | string | ○ | 収集日（YYYY-MM-DD） |
| `summary_by` | string | ○ | `cowork` / `manual` |

---

## 4. リポジトリ構造

```
howto-kb/
├── articles/
│   ├── claude-code/          # Claude Code関連記事
│   ├── cowork/               # Cowork関連記事
│   ├── antigravity/          # Antigravity関連記事
│   ├── ai-workflow/          # AI活用全般
│   └── construction/         # 建設業・土木
├── index.json                # 全記事のメタデータ一覧（検索用）
├── scripts/
│   ├── crawl_rss.py          # RSS取得（Zenn, Qiita, Anthropic, note）
│   ├── crawl_x.py            # Grok API経由X収集
│   ├── build_index.py        # index.json再生成
│   └── add_manual.py         # 手動登録ヘルパー（URLからMD生成）
├── config/
│   ├── feeds.yaml            # RSSフィードURL一覧
│   └── x_queries.yaml        # Grok API検索クエリ一覧
├── .github/
│   └── workflows/
│       └── (フォールバック用、Phase 0の結果次第で使用)
├── CLAUDE.md                 # Claude Code用プロジェクト説明
└── README.md
```

---

## 5. index.json 仕様

全記事のメタデータを1ファイルに集約。検索・フィルタリング用。

```json
{
  "last_updated": "2026-03-17T09:00:00+09:00",
  "total_count": 150,
  "articles": [
    {
      "id": "2026-03-17-claude-code-context-tips-01",
      "title": "Claude Codeでのコンテキスト管理のコツ",
      "url": "https://zenn.dev/example/articles/claude-code-context",
      "source": "zenn",
      "category": "claude-code",
      "tags": ["context-management", "CLAUDE-md", "handover"],
      "date_published": "2026-03-15",
      "date_collected": "2026-03-17",
      "file_path": "articles/claude-code/2026-03-17-claude-code-context-tips-01.md"
    }
  ]
}
```

---

## 6. 情報ソースと取得方法

### 6-1. 自動収集（Coworkスケジュールタスク）

| ソース | 取得方法 | フィードURL / API | 頻度 |
|---|---|---|---|
| **Anthropic公式ブログ** | RSS（GitHub生成） | `Olshansk/rss-feeds` リポジトリの生成フィード | 毎日 |
| **Claude Code Changelog** | RSS（GitHub生成） | 同上 `feed_anthropic_changelog_claude_code.xml` | 毎日 |
| **Zenn** | 公式RSS | `https://zenn.dev/topics/claude/feed` | 毎日 |
| | | `https://zenn.dev/topics/ai-agent/feed` | 毎日 |
| **Qiita** | API v2 | タグ `Claude` で検索 | 毎日 |
| **note** | RSS | `https://note.com/hashtag/claude?rss`（要確認） | 毎日 |
| **X (Twitter)** | Grok API | 検索クエリベース（config/x_queries.yaml） | 毎日 |
| **建設系** | Cowork既存スケジュール | 既存の収集フローにDB取り込みステップを追加 | 週1 |

### 6-2. 手動登録

| 方法 | フロー |
|---|---|
| **NotebookLM MCP経由** | NotebookLM → MCP → Coworkで要約 → Markdown生成 → git push |
| **Claude.ai会話からMD生成** | 会話中に「ナレッジDBに登録」→ MD生成 → 手動git push |

---

## 7. 処理パイプライン

### Coworkスケジュールタスク実行フロー

```
[Cowork スケジュールタスク起動]
    ↓
[RSS/API/Grok] からフィード取得（crawl_rss.py / crawl_x.py）
    ↓
新規記事を検出（既存index.jsonと照合、URLで重複排除）
    ↓
Cowork自身が要約を生成（追加APIコスト不要）
  - 200〜300字の日本語要約
  - カテゴリを自動判定
  - 英語タグを自動付与
    ↓
Markdownファイルを生成 → articles/{category}/ に保存
    ↓
build_index.py → index.json を再生成
    ↓
GitHubにpush（GitHub MCP or git push）
```

### 設計の特徴
- GitHub Actions + Claude API（従量課金）方式ではなく、Coworkスケジュールタスク方式を採用
- 要約生成はCowork自身が行うため、MAXプラン内で追加APIコストが発生しない
- PCが起動中＋Claude Desktop開放時に実行。スリープ中はスキップされるが起動後にキャッチアップ

### Coworkスケジュールタスクのプロンプト（案）

```
howto-kb リポジトリのナレッジベースを更新してください。

1. config/feeds.yaml に記載されたRSSフィードから新しい記事を取得
2. index.json と照合し、未登録の記事のみ抽出
3. 各記事について以下を生成:
   - 200〜300字の日本語要約
   - カテゴリ判定（claude-code / cowork / antigravity / ai-workflow / construction）
   - 英語タグ3〜5個
4. Markdownファイルを articles/{category}/ に保存
5. index.json を再生成
6. GitHubにコミット＆プッシュ

カテゴリ判定基準:
- claude-code: Claude Code、CLAUDE.md、コンテキスト管理、Handover関連
- cowork: Cowork、デスクトップ自動化関連
- antigravity: Antigravity（VSCode拡張）固有の情報
- ai-workflow: 上記以外のAI活用全般（プロンプト、MCP、API、他ツール）
- construction: 土木・建設業関連
```

---

## 8. 設定ファイル

### config/feeds.yaml

```yaml
ai_feeds:
  # Anthropic公式（Olshansk/rss-feeds経由）
  - name: "Anthropic News"
    url: "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml"
    default_category: "ai-workflow"

  - name: "Anthropic Engineering"
    url: "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_engineering.xml"
    default_category: "ai-workflow"

  - name: "Claude Code Changelog"
    url: "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_changelog_claude_code.xml"
    default_category: "claude-code"

  # Zenn
  - name: "Zenn - Claude"
    url: "https://zenn.dev/topics/claude/feed"
    default_category: "ai-workflow"

  - name: "Zenn - AI Agent"
    url: "https://zenn.dev/topics/ai-agent/feed"
    default_category: "ai-workflow"

  # note
  - name: "note - Claude"
    url: "https://note.com/hashtag/claude?rss"
    default_category: "ai-workflow"

construction_feeds:
  # 建設系は Cowork 既存スケジュールから取り込み
  # 将来的にRSSソースを追加する場合はここに記載
  []
```

### config/x_queries.yaml

```yaml
queries:
  - query: "Claude Code tips"
    category: "claude-code"
    lang: "ja"

  - query: "Cowork Anthropic"
    category: "cowork"
    lang: "ja"

  - query: "Claude MCP活用"
    category: "ai-workflow"
    lang: "ja"

  - query: "Claude Code best practices"
    category: "claude-code"
    lang: "en"

search_settings:
  max_results_per_query: 20
  exclude_retweets: true
  min_likes: 5
```

---

## 9. Claudeからの参照方法

### Claude Code / Antigravity
```
# リポジトリをクローン済みの前提
# CLAUDE.md に以下を記載:
"howto-kb/ ディレクトリにナレッジベースがあります。
index.json で記事一覧を確認し、必要な記事のMarkdownを読んでください。"
```

### Cowork
```
# howto-kb リポジトリをローカルに配置
# グローバル指示またはタスク指示で参照パスを指定
```

### Claude.ai
```
# index.json をアップロードして「○○に関する記事を探して」
# → 該当記事のMDファイルを追加アップロードして詳細参照
```

---

## 10. 実装フェーズ

### Phase 0: 環境準備（最優先）

CoworkからGitHubへのpush方法を確定する。
Claude Codeからはgit push可能だが、Coworkからは過去に失敗している。

**テスト順序（優先度順）:**

1. **GitHub MCP経由でのコミット＆プッシュ**
   - CoworkにGitHub MCPが接続されていればAPIベースでpush可能
   - テスト: Coworkから簡単なファイルを1つコミット＆プッシュ
   - 確認: GitHub MCPのcreate_or_update_file等のツールが使えるか

2. **Coworkから直接 git push**
   - Coworkのサンドボックスからのネットワークアクセス設定を調査
   - SSH鍵 or PATがCowork環境から参照できるか確認
   - テスト: Coworkターミナルから `git push` を実行

3. **フォールバック: GitHub Actions**
   - 上記2つが不可の場合、GitHub Actionsで定期pushを行う
   - Coworkでファイル生成のみ → GitHub Actionsで検出＆push
   - この場合、要約にClaude API（従量課金、月$1以下）が必要

**Phase 0 完了条件:**
- [ ] Coworkから何らかの方法でGitHubにpushできることを確認
- [ ] 確定した方法をこの仕様書に反映

---

### Phase 1: 基盤構築（まず動くものを）
- [ ] GitHubリポジトリ `howto-kb` の作成・初期構造
- [ ] Markdownテンプレート + build_index.py
- [ ] crawl_rss.py（Zenn RSSのみ対象）
- [ ] Coworkスケジュールタスク設定（毎日、Zennのみ）
- [ ] 手動登録ワークフロー確立（Claude.ai → MD → git push）

### Phase 2: ソース拡張
- [ ] Anthropic公式ブログ・Changelog RSS追加
- [ ] Qiita API連携追加
- [ ] note RSS追加
- [ ] feeds.yaml の全ソース有効化

### Phase 3: X + NotebookLM
- [ ] Grok API経由のX収集（crawl_x.py）
- [ ] NotebookLM MCP連携の取り込みフロー
- [ ] x_queries.yaml のチューニング

### Phase 4: 建設系統合
- [ ] Cowork既存スケジュールからの取り込みフロー追加
- [ ] 建設系RSSソースの追加（必要に応じて）

---

## 11. コスト見積もり

### Coworkスケジュールタスク方式（推奨）
- **追加APIコスト: $0**
- RSS取得、要約生成、git pushすべてCowork / MAXプラン内
- Grok APIのみ別途料金が発生する可能性あり（X Premium+に含まれる場合あり）

### フォールバック: GitHub Actions方式の場合
- Claude API（Haiku）: 約$0.60/月（600記事/月想定）
- GitHub Actions: 無料枠内（2,000分/月）

---

## 12. 備考

- 実行環境はCoworkスケジュールタスクを主軸とし、PCが起動中＋Claude Desktop開放時に実行される
- PCスリープ中はスキップされるが、起動後にキャッチアップ実行される
- ナレッジDB更新は数時間のずれが許容されるため、厳密な定時実行は不要
- 建設系の自動収集は、既にCoworkでスケジューリングしている収集フローをベースに拡張
- NotebookLM MCPは非公式ツールだが、セキュリティリスクを理解した上で使用する前提
- タグの表記ゆれが増えてきた場合は、タグ正規化スクリプトの追加を検討
- index.json が肥大化した場合は、年別分割やカテゴリ別分割を検討
