# Phase 3-2: NotebookLM連携 実装報告

## 1. 概要

NotebookLMの指定ノートブックからソースを差分検出し、howto-kbに取り込むスクリプトを実装した。
`nlm` コマンド（notebooklm-mcp-cli v0.4.9）を利用してソース一覧を取得し、
既存のcrawl_rss.py / crawl_x.py と同じJSON出力形式で新規ソースを出力する。

## 2. 作成・変更ファイル

| ファイル | 種別 | 内容 |
|---|---|---|
| `config/notebooklm.yaml` | 新規 | ノートブック→カテゴリのマッピング定義 |
| `config/notebooklm_last_sync.json` | 新規（自動生成） | 同期済みソースID管理 |
| `scripts/crawl_notebooklm.py` | 新規 | 差分検出・JSON出力スクリプト |
| `howto-kb-design-spec.md` | 更新 | Phase 3チェックリスト完了マーク |
| `_progress/20260318_notebooklm_mcp_setup.md` | 新規 | セットアップ記録 |

## 3. 対象ノートブックとカテゴリマッピング

| ノートブック名 | NotebookLM ID | カテゴリ | ソース数 |
|---|---|---|---|
| Claude Code | 592fb4af-3eff-4afd-b23d-433b40fe412b | claude-code | 30 |
| Antigravity | 446402a1-3906-4f25-8bf0-abe3429e669b | claude-code | 9 |
| AI全般 | ade05b0b-af6e-4bb8-a245-48eb0bc96a8f | ai-workflow | 1 |
| Claude Cowork | 702ea8ce-a3e1-4fd1-ace0-62cd974e2233 | cowork | 2 |

## 4. 差分検出の仕組み

NotebookLMのソース一覧API（`nlm source list`）にはタイムスタンプが含まれないため、
**ソースIDベース**で差分を管理する。

```
[nlm source list 実行]
    ↓
各ソースのIDを取得
    ↓
notebooklm_last_sync.json の記録済みIDと比較
    ↓
新規ID → 新規ソースとして出力
既存ID → スキップ
    ↓
現在の全ソースIDを notebooklm_last_sync.json に保存
```

追加の重複チェック:
- URL付きソースは `index.json` の既存URLとも照合し、二重登録を防止

## 5. 出力形式

crawl_rss.py / crawl_x.py と同一のJSON形式:

```json
{
  "title": "ソースタイトル",
  "url": "https://example.com/article（URL付きソースのみ）",
  "date_published": "",
  "description": "[NotebookLM source: web_page] ソースタイトル",
  "source": "notebooklm",
  "default_category": "claude-code",
  "date_collected": "2026-03-18",
  "notebook_name": "Claude Code",
  "source_type": "web_page",
  "source_id": "efa60877-a595-4233-a417-75abd608902a"
}
```

### ソースタイプ別の扱い

| ソースタイプ | URLの有無 | 取り込み |
|---|---|---|
| web_page | あり | URL + タイトルを取得 |
| youtube | なし（IDのみ） | タイトルのみで取得 |
| pdf | なし | タイトルのみで取得 |

## 6. テスト結果

### 初回実行（全件取得）

| ノートブック | ソース数 | 新規検出 | 備考 |
|---|---|---|---|
| Claude Code | 30 | 30 | web_page 16, pdf 5, youtube 9 |
| Antigravity | 9 | 9 | web_page 3, pdf 4, youtube 2 |
| AI全般 | 1 | 1 | youtube 1 |
| Claude Cowork | 2 | 1 | 1件はindex.jsonのURL重複でスキップ |
| **合計** | **42** | **41** | |

### 2回目実行（差分検出テスト）

| ノートブック | ソース数 | 新規検出 |
|---|---|---|
| Claude Code | 30 | 0 |
| Antigravity | 9 | 0 |
| AI全般 | 1 | 0 |
| Claude Cowork | 2 | 0 |
| **合計** | **42** | **0** |

差分検出が正しく動作することを確認。

## 7. Windows環境での注意事項

- `nlm` コマンドは Rich ライブラリを使用しており、cp932 環境ではUnicodeエラーが発生する
- `crawl_notebooklm.py` はサブプロセス呼び出し時に `PYTHONIOENCODING=utf-8` を自動設定済み
- 手動で `nlm` を直接実行する場合は `export PYTHONIOENCODING=utf-8` が必要

## 8. Git

- コミット: `80485df`
- ブランチ: main
- プッシュ済み
