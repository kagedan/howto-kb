# NotebookLM MCP CLI セットアップ結果

## 1. インストール

| ツール | バージョン | インストール方法 |
|---|---|---|
| uv | 0.10.11 | `irm https://astral.sh/uv/install.ps1 \| iex` |
| notebooklm-mcp-cli | 0.4.9 | `uv tool install notebooklm-mcp-cli` |

### インストール先

- uv: `C:\Users\KazuhisaMiyake\.local\bin\`
- nlm / notebooklm-mcp: `C:\Users\KazuhisaMiyake\.local\bin\`（uv tool経由）
- 認証情報: `C:\Users\KazuhisaMiyake\.notebooklm-mcp-cli\profiles\default`

### 依存パッケージ

74パッケージが隔離環境にインストール済み（fastmcp, mcp, httpx, pydantic, authlib 等）。

## 2. Google認証

- アカウント: kagedan3@gmail.com
- プロファイル: default
- プロバイダー: builtin（Chrome DevTools Protocol経由）
- Cookie: 48件抽出、CSRFトークンあり

## 3. 動作確認（ノートブック一覧）

| ノートブック名 | ソース数 | 最終更新 |
|---|---|---|
| 株 | 2 | 2026-03-17 |
| Claude Code | 30 | 2026-03-15 |
| Antigravity | 9 | 2026-03-13 |
| AI全般 | 1 | 2026-03-12 |
| Claude Cowork | 2 | 2026-03-01 |
| LANTECでのAI活用について | 2 | 2026-02-26 |
| 大阪市建設局共通仕様書 令和3年3月 | 46 | 2026-02-19 |
| ドライブで行きたいところ | 45 | 2025-11-01 |

## 4. Windows環境での注意事項

nlm コマンドは Rich ライブラリを使用しており、Windows の cp932 環境ではUnicodeエラーが発生する。
実行時は以下の環境変数が必要：

```bash
export PYTHONIOENCODING=utf-8
```

または bash 起動時に設定しておく。

## 5. 利用可能なコマンド（主要なもの）

| コマンド | 用途 |
|---|---|
| `nlm login` | Google認証 |
| `nlm login --check` | 認証状態確認 |
| `nlm notebook list` | ノートブック一覧 |
| `nlm source list <notebook_id>` | ソース一覧 |
| `nlm query <notebook_id> "質問"` | ノートブックに質問 |
| `nlm setup` | MCP サーバー設定 |
| `nlm doctor` | インストール診断 |

## 6. 次のステップ

- [ ] howto-kb との連携フロー設計（NotebookLM → ナレッジDB取り込み）
- [ ] MCP サーバーとしての設定（`nlm setup`）
- [ ] Claude Desktop / Claude Code からの接続テスト
