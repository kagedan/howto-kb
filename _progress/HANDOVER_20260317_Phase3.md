# 引継書: Phase 3 - X + NotebookLM

## 1. 完了タスク

### Phase 2: ソース拡張 (全完了)
- [x] feeds.yaml 修正
  - Zenn AI Agent: `topics/ai-agent/feed` → `topics/aiagent/feed` (404修正)
  - note Claude: `?rss` → `/rss` (パス形式に修正)
  - `qiita_api` セクション新設
- [x] crawl_rss.py に Qiita API v2 対応追加
  - `fetch_qiita_articles()`, `load_qiita_feeds()` 関数追加
- [x] 全7フィード動作確認済み (345件検出)
- [x] git commit & push 完了 (94888da)

### 本セッション追加作業
- [x] 設計仕様書 (howto-kb-design-spec.md) のPhase 2チェックリスト更新
- [x] 設計仕様書のフィードURL情報を実態に合わせて修正 (セクション6, 8)
- [ ] 設計仕様書の変更は未コミット

## 2. 現在の状態

- ブランチ: main
- 未コミットの変更: `howto-kb-design-spec.md` (Phase 2チェック + URL修正)
- XAI_API_KEY: Windows環境変数に設定済み、bashシェルから利用可能

## 3. 残タスク

### Phase 3: X + NotebookLM
- [ ] **crawl_x.py 作成** — Grok API (xAI) 経由の X 検索
  - 環境変数 `XAI_API_KEY` を使用
  - `config/x_queries.yaml` のクエリ定義に従って検索
  - x_queries.yaml の設定: 4クエリ (Claude Code tips, Cowork Anthropic, Claude MCP活用, Claude Code best practices)
  - search_settings: max_results=20, exclude_retweets=true, min_likes=5
  - 出力形式は crawl_rss.py と同じ JSON (title, url, date_published, description, source="x", ...)
  - **Grok API 仕様の調査が未完了** — エンドポイント・認証方法・レスポンス形式を確認する必要あり
- [ ] NotebookLM MCP連携の取り込みフロー
- [ ] x_queries.yaml のチューニング

### その他
- [ ] 設計仕様書の変更をコミット

## 4. 変更ファイル一覧

| ファイル | 状態 | 内容 |
|---|---|---|
| `config/feeds.yaml` | コミット済 | Zenn/note URL修正, qiita_api追加 |
| `scripts/crawl_rss.py` | コミット済 | Qiita API v2 対応追加 |
| `howto-kb-design-spec.md` | **未コミット** | Phase 2チェック, フィードURL修正 |
| `_progress/` | 新規 | 本引継書 |

## 5. 次セッションへの注意事項

- Grok API の仕様調査から再開。xAI docs (https://docs.x.ai/api) を確認すること
- crawl_x.py は crawl_rss.py と同じパターン (設定読み込み→API呼び出し→新規記事JSON出力) で作る
- 設計仕様書の未コミット変更を先にコミットしてから Phase 3 作業に入ること
- XAI_API_KEY が環境変数にあることは確認済み
