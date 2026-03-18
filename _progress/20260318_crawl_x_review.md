# crawl_x.py 現状レビューと改善案

## 1. 現状の説明

### 検索クエリ（4件）

| # | クエリ | カテゴリ | 言語 | テスト結果 |
|---|---|---|---|---|
| 1 | `Claude Code tips` | claude-code | ja | 20件取得 |
| 2 | `Cowork Anthropic` | cowork | ja | 20件取得 |
| 3 | `Claude MCP活用` | ai-workflow | ja | **タイムアウト（0件）** |
| 4 | `Claude Code best practices` | claude-code | en | 19件取得 |

### 取得件数・設定

- `max_results_per_query: 20` — 各クエリ最大20件
- `exclude_retweets: true` / `min_likes: 5` — yaml に定義はあるが**スクリプト側で未使用**（x_search ツールにはフィルタパラメータがなく、プロンプト経由での指示にも限界がある）

### 出力形式

各投稿を以下のJSON形式で stdout に出力（crawl_rss.py と同一パターン）:

```json
{
  "title": "@author: 投稿テキスト冒頭60文字",
  "url": "https://x.com/user/status/ID",
  "date_published": "2026-03-17",
  "description": "投稿テキスト（最大500文字）",
  "source": "x",
  "default_category": "claude-code",
  "date_collected": "2026-03-18",
  "query": "Claude Code tips"
}
```

### API構成

| 項目 | 内容 |
|---|---|
| エンドポイント | `POST https://api.x.ai/v1/responses` |
| ツール | `{"type": "x_search"}` サーバーサイドツール |
| モデル | `grok-4`（x_search はgrok-4ファミリー限定） |
| タイムアウト | 300秒（1リクエストに約60秒かかる） |
| パース | annotations の url_citation → JSON配列パース → URL抽出（3段フォールバック） |

### 現状の課題

1. **クエリ3がタイムアウト** — `Claude MCP活用` は日本語混在で検索に時間がかかり300秒超え
2. **title/description が空になるケース** — Grok がJSON配列を返さず自然文で回答した場合、`extract_urls_from_content` フォールバックでURLのみ取得されメタ情報が欠落
3. **search_settings の `exclude_retweets` と `min_likes` が未反映**
4. **自分のRT収集** — 現在の仕組みでは対応していない

---

## 2. 改善案

### 2-1. タイムアウトしたクエリの修正

`Claude MCP活用` → **英語キーワードに変更するか、分割する**

```yaml
# 案A: 英語に統一（x_search は英語クエリの方が安定）
- query: "Claude MCP"
  category: "ai-workflow"
  lang: "ja"

# 案B: より具体的なキーワードに変更
- query: "Claude MCP server"
  category: "ai-workflow"
  lang: "ja"
```

日本語の「活用」が曖昧すぎてGrokが検索範囲を広げすぎている可能性が高い。

### 2-2. 自分のアカウントのRT収集

x_queries.yaml に `user_timelines` セクションを新設する案。

```yaml
user_timelines:
  - username: "kagedan"        # ← 要確認：実際のXアカウント名
    include_retweets: true
    category_default: "ai-workflow"
```

**スクリプト側の対応:**

- `search_x()` とは別に `fetch_user_timeline()` 関数を追加
- プロンプト: `"List recent retweets by @kagedan related to AI/Claude"`
- RTの元投稿URLを収集する形にする（RT自体のURLではなく、RTされた投稿の内容が重要なため）

### 2-3. 検索クエリの最適化

現在のクエリは**範囲が広く、重複も多い**。再編案:

```yaml
queries:
  # --- claude-code ---
  - query: "Claude Code tips OR CLAUDE.md"
    category: "claude-code"
    lang: "ja"
  # ↑ 「tips」と「best practices」を統合し、CLAUDE.md も拾う

  - query: "Claude Code best practices OR agentic coding"
    category: "claude-code"
    lang: "en"
  # ↑ 英語圏はそのまま維持 + agentic coding を追加

  # --- cowork ---
  - query: "Claude Cowork OR Claude Desktop automation"
    category: "cowork"
    lang: "ja"
  # ↑ 「Cowork Anthropic」→ 実際のユーザーは「Claude Cowork」で投稿するので修正

  # --- ai-workflow ---
  - query: "Claude MCP server"
    category: "ai-workflow"
    lang: "ja"
  # ↑ タイムアウト対策：「活用」を削除し具体的に

  # --- 新規 ---
  - query: "Claude Code hooks OR subagents"
    category: "claude-code"
    lang: "ja"
  # ↑ 最新機能のTipsを拾うために追加

  # --- ユーザーRT ---
  # user_timelines セクションで別処理
```

---

## 3. 改善まとめ

| 改善項目 | 変更内容 | 影響範囲 |
|---|---|---|
| タイムアウト修正 | `Claude MCP活用` → `Claude MCP server` | yaml のみ |
| RT収集 | `user_timelines` セクション新設 + `fetch_user_timeline()` 追加 | yaml + py |
| クエリ最適化 | OR演算子で統合・具体化、5〜6クエリに再編 | yaml のみ |

---

## 4. 未確認事項

- Xアカウント名（@の後の部分）の確認が必要
- OR演算子が x_search ツール経由で正しく機能するかの検証が必要
- クエリ数増加に伴うAPI応答時間の確認（現状4クエリで約3〜4分）
