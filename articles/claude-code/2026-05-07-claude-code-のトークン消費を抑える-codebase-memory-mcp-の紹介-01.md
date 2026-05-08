---
id: "2026-05-07-claude-code-のトークン消費を抑える-codebase-memory-mcp-の紹介-01"
title: "Claude Code のトークン消費を抑える - codebase-memory-mcp の紹介"
url: "https://zenn.dev/omeroid/articles/fb40dd4136bc78"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-07"
date_collected: "2026-05-08"
summary_by: "auto-rss"
---

## はじめに

Claude Code のコード探索系ツール（`Grep` / `Glob` / `Read`）を、コードベースをグラフ DB として問い合わせる MCP サーバー [`codebase-memory-mcp`](https://github.com/DeusData/codebase-memory-mcp) に置き換える話です。

公式ベンチでは、5 件の構造クエリで **約 3,400 トークン** に収まります。同じ調査を grep + read の往復でやると **約 412,000 トークン** かかります。**99.2% 削減**、トークン換算で 120 倍の差です。

長時間セッションでは、これがコンテキスト枯渇とまともに会話できる時間を分ける一因になります。

## きっかけ

Claude Code を業務で使い倒していて、調査タスクの途中でコンテキストが詰まる事象が頻発していました。原因は明らかで、`Grep` の長大な出力と `Read` の多重呼び出しでウィンドウが埋まることです。トークン消費を抑える MCP がないか調べていたところ、Reddit の r/ClaudeAI で `DeusData/codebase-memory-mcp` の存在を知りました。

実際に手元の中規模リポジトリ（約 4 万ファイル）で試したら、index は数秒、`Grep` の代わりに `search_graph` を呼ぶだけでトークン消費が体感で 1〜2 桁減ったので、紹介します。

## これは何か

[`DeusData/codebase-memory-mcp`](https://github.com/DeusData/codebase-memory-mcp) は、AI コーディングエージェント向けのコード理解エンジンです。README から要点を抜き出すと次のとおりです。

* **超高速インデックス** ── Linux カーネル（28M LOC、75K ファイル）を **3 分** で index、平均的なリポジトリはミリ秒単位。構造クエリは 1ms 未満で返る
* **155 言語対応** ── tree-sitter 製の文法を全部 binary に同梱。追加インストール不要
* **Pure C / 単一バイナリ** ── ランタイム依存ゼロ。Docker も不要、API キーも不要
* **macOS / Linux / Windows** をサポート。release から落として `install` するだけ
* **ローカル完結** ── コードは外に出ない、API 呼び出しなし
* **11 種類のエージェント対応** ── Claude Code / Codex / Gemini CLI / Zed / OpenCode / Antigravity / Aider / KiloCode / VS Code / OpenClaw / Kiro
* **14 個の MCP ツール** ── 構造検索、呼び出しトレース、影響範囲、Cypher、dead code 検出、サービス間 HTTP 連結、ADR 管理など
* **3D グラフ可視化 UI**（オプション）── `localhost:9749` でブラウザから探索できる

設計の根拠と評価は arXiv preprint [*Codebase-Memory: Tree-Sitter-Based Knowledge Graphs for LLM Code Exploration via MCP*](https://arxiv.org/abs/2603.27277) に書かれています。31 のリアルなリポジトリで評価し、**回答品質 83%、トークン 1/10、ツール呼び出し回数 1/2.1**（vs ファイル探索）。

## 何が問題か

Claude Code が標準で持つコード探索系ツールには、それぞれ次のような役割と限界があります。

* `Grep` ── ripgrep ベースの全文検索。テキストパターンには強いが、構造（呼び出し関係・実装関係）は読めない
* `Glob` ── ファイル名パターン照合。ファイルの存在は分かるが、中身の関係は分からない
* `Read` ── ファイル単位での読み込み。前後関係を把握するために何度も呼ばれ、トークンを大量に消費する
* `WebFetch` ── 外部ドキュメント取得用。コードベースの探索ではない

これらはすべて **テキスト処理** であり、コードを「構造」として扱えません。たとえば次のような問いに、テキストベースの三点セットだけで答えるのは難しいか、答えられても非効率です。

* `UserService.Create` を呼んでいる関数を全部教えて
* このファイルを変更したとき、影響が及ぶ箇所はどこか
* どこからも呼ばれていない関数（dead code）を一覧してほしい
* HTTP 越しに別サービスを叩いているエッジを全部出して
* 同じコミットでよく一緒に変わるファイル群を出して

`Grep` は呼び出し名にマッチする箇所を返せますが、メソッド名が衝突するとノイズが増えます。インターフェース実装や override の関係はテキストでは表せません。`Read` で周辺を辿ろうとすると、間接呼び出しを 1 ファイルずつ追うことになり、出力サイズもコンテキスト消費も雪だるま式に膨らみます。

## インストール

### macOS / Linux ── ワンライナー

```
curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash
```

graph 可視化 UI 込みで入れるとき:

```
curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash -s -- --ui
```

主なオプション:

* `--ui` ── 3D グラフ可視化 UI を含める
* `--skip-config` ── binary だけ配置し、エージェント設定は触らない
* `--dir=<path>` ── インストール先を指定

### Windows ── PowerShell

```
Invoke-WebRequest -Uri https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.ps1 -OutFile install.ps1
notepad install.ps1   # 中身を確認してから
.\install.ps1
```

SmartScreen が出たら「詳細情報」→「実行」で進めます。`checksums.txt` で SHA-256 を検証できます。

### 手動インストール

[releases ページ](https://github.com/DeusData/codebase-memory-mcp/releases/latest) から自分の OS 向けの archive を落として展開し、同梱の `install.sh`（macOS/Linux）または `install.ps1`（Windows）を実行します。

| プラットフォーム | 標準版 | UI 付き |
| --- | --- | --- |
| macOS Apple Silicon | `darwin-arm64.tar.gz` | `ui-darwin-arm64.tar.gz` |
| macOS Intel | `darwin-amd64.tar.gz` | `ui-darwin-amd64.tar.gz` |
| Linux x86\_64 | `linux-amd64.tar.gz` | `ui-linux-amd64.tar.gz` |
| Linux ARM64 | `linux-arm64.tar.gz` | `ui-linux-arm64.tar.gz` |
| Windows x86\_64 | `windows-amd64.zip` | `ui-windows-amd64.zip` |

macOS の quarantine 属性除去と ad-hoc 署名は `install` が自動でやってくれます。`xattr` や `codesign` を手で叩く必要はありません。

### Claude Code から会話で導入

Claude Code 自身に頼む方法もあります。

```
You: 「この MCP サーバーを入れて: https://github.com/DeusData/codebase-memory-mcp」
```

### ソースから build

C / C++ コンパイラと zlib があれば build できます。

```
git clone https://github.com/DeusData/codebase-memory-mcp.git
cd codebase-memory-mcp
scripts/build.sh                    # 標準版
scripts/build.sh --with-ui          # UI 付き
# binary: build/c/codebase-memory-mcp
```

### 手動の MCP 設定

`install` を使わず自分で MCP 設定を書きたいときは、`~/.claude/.mcp.json` または プロジェクトの `.mcp.json` に次を追記します。

```
{
  "mcpServers": {
    "codebase-memory-mcp": {
      "command": "/path/to/codebase-memory-mcp",
      "args": []
    }
  }
}
```

エージェントを再起動して `/mcp` で `codebase-memory-mcp` が 14 ツールで認識されていれば成功です。

`install` コマンドは、検出した全エージェントの設定を自動で書き換えます。

| エージェント | MCP 設定先 | 追加されるもの |
| --- | --- | --- |
| Claude Code | `.claude/.mcp.json` | 4 つの Skill + PreToolUse hook |
| Codex CLI | `.codex/config.toml` | `.codex/AGENTS.md` |
| Gemini CLI | `.gemini/settings.json` | `.gemini/GEMINI.md` + BeforeTool hook |
| Zed | `settings.json` (JSONC) | — |
| OpenCode | `opencode.json` | `AGENTS.md` |
| Antigravity | `mcp_config.json` | `AGENTS.md` |
| Aider | — | `CONVENTIONS.md` |
| KiloCode | `mcp_settings.json` | `~/.kilocode/rules/` |
| VS Code | `Code/User/mcp.json` | — |
| OpenClaw | `openclaw.json` | — |
| Kiro | `.kiro/settings/mcp.json` | — |

## セットアップ・初期化

### プロジェクトを index する

エージェントを再起動して、こう言うだけです。

エージェントが裏で `index_repository(repo_path="...")` を呼びます。完了するとノード数とエッジ数が返ってきます。

CLI から直接叩くなら次のとおりです。

```
codebase-memory-mcp cli index_repository '{"repo_path": "/path/to/repo"}'
```

### 自動 index を有効化

プロジェクトに初めて接続したときに自動で index させたいときは次の設定を入れます。

```
codebase-memory-mcp config set auto_index true
codebase-memory-mcp config set auto_index_limit 50000
```

すでに index 済みのプロジェクトは、background watcher に登録されて git 経由の差分検出で継続的に追従します。

### graph 可視化 UI を起動

UI 付きで導入していれば、次のコマンドで可視化サーバーが立ち上がります。

```
codebase-memory-mcp --ui=true --port=9749
```

ブラウザで `http://localhost:9749` を開くと 3D のグラフを操作できます。MCP サーバーと並行で動くので、エージェントが繋がっている間はずっと見られます。

### 更新

```
codebase-memory-mcp update
```

起動時にも更新確認が走り、新しい release があると最初のツール呼び出し時に通知されます。

### アンインストール

```
codebase-memory-mcp uninstall
```

エージェント側の設定・skill・hook・instruction はすべて削除されます。binary 本体と SQLite DB（`~/.cache/codebase-memory-mcp/`）は残るので、不要なら手で消します。

## 使い方

### 探索ワークフロー

1. `list_projects` ── index 済みか確認
2. 未 index なら `index_repository` を実行
3. `get_graph_schema` ── ノード・エッジ種別を把握（最初に必ず呼ぶ）
4. `search_graph(label="Function", name_pattern=".*Handler.*")` ── 候補を絞る
5. `get_code_snippet(qualified_name="project.path.FuncName")` ── 本体を読む

### トレースワークフロー

1. `search_graph(name_pattern=".*FuncName.*")` で qualified name を確定
2. `trace_call_path(function_name="FuncName", direction="both", depth=3)` で呼び出し関係を辿る
3. `detect_changes()` で git diff を影響シンボルにマップする

### Cypher で書く高度なクエリ

複雑な問いは `query_graph` に Cypher を渡します。

```
// HTTP 越しの呼び出しを 20 件まで取得
MATCH (a)-[r:HTTP_CALLS]->(b)
RETURN a.name, b.name, r.url_path, r.confidence
LIMIT 20
```

```
// Handler という名前のついた関数をすべて取得
MATCH (f:Function)
WHERE f.name =~ '.*Handler.*'
RETURN f.name, f.file_path
```

```
// main から直接呼ばれている関数
MATCH (a)-[r:CALLS]->(b)
WHERE a.name = 'main'
RETURN b.name
```

サポートする Cypher のサブセット: `MATCH`（label・関係種別・可変長パス）、`WHERE`（比較・regex・`CONTAINS`）、`RETURN`（プロパティ・`COUNT`・`DISTINCT`）、`ORDER BY`、`LIMIT`。`WITH` `COLLECT` `OPTIONAL MATCH` および書き込み系は未対応です。

### CLI モード

すべての MCP ツールはコマンドラインからも叩けます。

```
codebase-memory-mcp cli index_repository '{"repo_path": "/path/to/repo"}'
codebase-memory-mcp cli search_graph '{"name_pattern": ".*Handler.*", "label": "Function"}'
codebase-memory-mcp cli trace_call_path '{"function_name": "Search", "direction": "both"}'
codebase-memory-mcp cli query_graph '{"query": "MATCH (f:Function) RETURN f.name LIMIT 5"}'
codebase-memory-mcp cli list_projects
codebase-memory-mcp cli --raw search_graph '{"label": "Function"}' | jq '.results[].name'
```

## 14 個の MCP ツール

### インデックス系

| ツール | 役割 |
| --- | --- |
| `index_repository` | リポジトリを graph に取り込む |
| `list_projects` | index 済みプロジェクト一覧（ノード/エッジ数つき） |
| `delete_project` | プロジェクトと graph データを削除 |
| `index_status` | index の進捗・状態を確認 |

### クエリ系

| ツール | 役割 |
| --- | --- |
| `search_graph` | label・name pattern・file pattern・degree フィルタで構造検索 |
| `trace_call_path` | BFS で呼び出し関係を辿る（depth 1〜5） |
| `detect_changes` | git diff を影響シンボルにマップしリスク分類 |
| `query_graph` | Cypher 風の読み取り専用クエリ |
| `get_graph_schema` | ノード・エッジの統計とプロパティ定義 |
| `get_code_snippet` | qualified name でソースを取得 |
| `get_architecture` | 言語・パッケージ・routes・hotspots・clusters・ADR を一括取得 |
| `search_code` | 索引済みファイルだけを対象にした grep |
| `manage_adr` | Architecture Decision Records の CRUD |
| `ingest_traces` | 実行時 trace を取り込み `HTTP_CALLS` を補強 |

## グラフのデータモデル

### ノード種別

`Project` `Package` `Folder` `File` `Module` `Class` `Function` `Method` `Interface` `Enum` `Type` `Route` `Resource`

### エッジ種別

`CONTAINS_PACKAGE` `CONTAINS_FOLDER` `CONTAINS_FILE` `DEFINES` `DEFINES_METHOD` `IMPORTS` `CALLS` `HTTP_CALLS` `ASYNC_CALLS` `IMPLEMENTS` `HANDLES` `USAGE` `CONFIGURES` `WRITES` `MEMBER_OF` `TESTS` `USES_TYPE` `FILE_CHANGES_WITH`

`HTTP_CALLS` や `FILE_CHANGES_WITH` のように、テキスト検索では復元が難しいエッジを持つ点が特徴です。

### 標準ツールとの対応

| 標準ツール | 置き換え先 | 違い |
| --- | --- | --- |
| `Grep` | `search_graph` / `query_graph` | 構造的にフィルタできる（label・degree・関係） |
| `Glob` | `search_graph(label="File")` / `get_architecture` | パッケージ構造とあわせて取得できる |
| `Read` | `get_code_snippet(qualified_name)` | qualified name 単位で必要部分だけ返る |
| 構造的な問いには対応できない | `trace_call_path` / `query_graph` | 呼び出し関係・実装関係をそのまま辿れる |

## Before / After 比較

公式ベンチ（5 件の構造クエリでコード調査）の結果は次のとおりです。

| 指標 | Before（grep + read） | After（codebase-memory-mcp） |
| --- | --- | --- |
| トークン消費 | 約 412,000 | 約 3,400 |
| 削減率 | 基準 | **99.2% 削減** |
| ツール呼び出し回数 | 基準 | **2.1 倍少ない** |
| 回答品質（31 リポジトリ評価） | — | **83%** |

性能ベンチ（Apple M3 Pro）:

| 操作 | 時間 | 補足 |
| --- | --- | --- |
| Linux カーネル full index | **3 分** | 28M LOC → 2.1M ノード、4.9M エッジ |
| Linux カーネル fast index | 1m 12s | 1.88M ノード |
| Django full index | 約 6s | 49K ノード、196K エッジ |
| Cypher クエリ | 1ms 未満 | 関係トラバース |
| 名前検索（regex） | 10ms 未満 | SQL LIKE 前段フィルタ |
| dead code 検出 | 約 150ms | degree フィルタ込みの全走査 |
| 呼び出しパス追跡（depth=5） | 10ms 未満 | BFS |

index は in-memory SQLite と LZ4 圧縮の RAM-first パイプラインで走り、終わると OS にメモリを返却します。

## hook でテキスト探索系ツールを抑制する

`install` で Claude Code を選ぶと、`~/.claude/hooks/` に 2 つの hook が入ります。

1. `cbm-session-reminder` ── SessionStart 時に「コード探索はまず codebase-memory-mcp を使え」というプロトコルを Claude に流す
2. `cbm-code-discovery-gate` ── PreToolUse hook で `Grep` / `Glob` / `Read` の最初の呼び出しに対し、グラフツール優先のリマインドを出す

リマインドは exit code 0 の advisory なので、ツール呼び出し自体はブロックされません。設定値・YAML/JSON・コメントなどテキスト検索が必要なケースを潰さない、現実的な落としどころです。Gemini CLI 用にも同等の BeforeTool hook が入ります。

## チーム共有 ── `.codebase-memory/graph.db.zst`

graph を zstd 圧縮した 1 ファイルとしてリポジトリに commit すると、チームメンバーは初回の full index をスキップできます。

* フォーマット ── SQLite を `VACUUM INTO` で詰めて zstd 圧縮（圧縮率 8〜13:1）
* 2 階層保存 ── `index_repository` の明示実行で **best**（`zstd -9` + index 削除）、watcher の自動更新で **fast**（`zstd -3`）
* bootstrap ── ローカル DB がなく artifact だけある状態で起動すると、artifact を import してから差分 index を走らせる
* merge コンフリクト回避 ── 初回 export 時に `.gitattributes` に `merge=ours` を自動追加
* オプション ── 嫌なら `.codebase-memory/` を `.gitignore` に入れて使わない選択もできる

## 設定

```
codebase-memory-mcp config list                          # 全設定を表示
codebase-memory-mcp config set auto_index true           # 自動 index
codebase-memory-mcp config set auto_index_limit 50000    # 自動 index の上限ファイル数
codebase-memory-mcp config reset auto_index              # 既定値に戻す
```

### 環境変数

| 変数 | 既定値 | 用途 |
| --- | --- | --- |
| `CBM_CACHE_DIR` | `~/.cache/codebase-memory-mcp` | DB 保存先を上書き |
| `CBM_DIAGNOSTICS` | `false` | `1` / `true` で `/tmp/cbm-diagnostics-<pid>.json` に periodic 診断を出力 |
| `CBM_DOWNLOAD_URL` | GitHub releases | 更新ダウンロード元の上書き（自前ホスト用） |

```
export CBM_CACHE_DIR=~/my-projects/cbm-data
```

### 拡張子マッピング

`.blade.php` のようなフレームワーク固有拡張子を既存言語に紐づけられます。

プロジェクト単位（リポジトリ root）:

```
// .codebase-memory.json
{"extra_extensions": {".blade.php": "php", ".mjs": "javascript"}}
```

グローバル:

```
// ~/.config/codebase-memory-mcp/config.json
{"extra_extensions": {".twig": "html", ".phtml": "php"}}
```

衝突したらプロジェクト設定が優先されます。

### 無視ルール

階層的に適用されます。

1. ハードコーディング済みのパターン（`.git`、`node_modules` ほか）
2. `.gitignore` 階層
3. `.cbmignore`（プロジェクト固有、gitignore 構文）

シンボリックリンクは常にスキップされます。

## 落とし穴

| 症状 | 対処 |
| --- | --- |
| `/mcp` でサーバーが見えない | `.mcp.json` のパスが絶対パスか確認、エージェント再起動。`echo '{}' | /path/to/binary` で JSON が返るかテスト |
| `index_repository` が失敗する | `repo_path` を絶対パスで渡す |
| `trace_call_path` の結果が 0 件 | 先に `search_graph(name_pattern=".*PartialName.*")` で正確な名前を取得 |
| プロジェクトが混ざった結果が返る | `project="name"` を引数に追加。`list_projects` で名前確認 |
| install 後 binary が見つからない | `export PATH="$HOME/.local/bin:$PATH"` |
| UI が開かない | UI 付き variant を入れたか、`--ui=true` 起動か、ポート 9749 が空いているか |

ドキュメント由来の細かい注意:

1. `search_graph(relationship="HTTP_CALLS")` はノードを degree でフィルタするだけです。実際のエッジを見たいときは `query_graph` で Cypher を書きます
2. `query_graph` には 200 行の上限があります。件数を数える用途では `search_graph` の degree フィルタを使います
3. `direction="outbound"` ではサービスを越える呼び出し元を取りこぼします。両方向が必要なら `direction="both"` を使います
4. 結果はデフォルトで 10 件ずつ返ります。`has_more` を確認して `offset` でページングします

## 言語サポート

155 言語、すべて binary 同梱の tree-sitter 文法で parse します。64 のリアルなオープンソースリポジトリでベンチした結果は次のとおりです。

| ティア | 含まれる言語 |
| --- | --- |
| Excellent (>=90%) | Lua, Kotlin, C++, Perl, Objective-C, Groovy, C, Bash, Zig, Swift, CSS, YAML, TOML, HTML, SCSS, HCL, Dockerfile |
| Good (75-89%) | Python, TypeScript, TSX, Go, Rust, Java, R, Dart, JavaScript, Erlang, Elixir, Scala, Ruby, PHP, C#, SQL |
| Functional (<75%) | OCaml, Haskell |

このほか、Solidity・GraphQL・Terraform/HCL・Protobuf・Gleam・Vue・Svelte などフレームワーク・DSL を含む 100 以上の言語も parse できます。

## 永続化と所在

SQLite DB は `~/.cache/codebase-memory-mcp/` に保存されます。WAL モードで ACID-safe、再起動を跨いで残ります。リセットしたいときは次のとおりです。

```
rm -rf ~/.cache/codebase-memory-mcp/
```

## セキュリティ

release は多層パイプラインで検証されてから公開されます。

* VirusTotal ── 70 以上のアンチウイルスエンジンでスキャン（検出ゼロが必須）
* SLSA Level 3 ── GitHub Actions が暗号学的 build provenance を発行。`gh attestation verify` で検証可能
* Sigstore cosign ── キーレス署名つき
* SHA-256 checksum ── `checksums.txt` を release に同梱、install スクリプトが自動検証
* CodeQL SAST ── 未解決の alert があると release pipeline が止まる
* ランタイム依存ゼロ ── ライブラリは全部 vendored

コードは外に出ない、API キーも要らない、binary は単体で完結する、という前提が崩れない設計です。

## 向き不向き

向いている場面は次のとおりです。

* 中〜大規模なコードベースで影響範囲調査をしたいとき
* リファクタリング前に dead code や fan-out を洗い出したいとき
* マイクロサービス間の HTTP 呼び出しグラフを把握したいとき
* 長時間セッションでコンテキストを温存したいとき
* チームで graph を共有して新メンバーの初回 index コストを削りたいとき

向いていない場面もあります。

* 小規模リポジトリでは index コストが見合わない場合があります
* コメント・文字列リテラル・設定値・YAML/JSON など、純粋なテキスト探索には `Grep` か `search_code` のほうが向きます
* ファイル名規約だけを当てたいときは `Glob` のほうが速いです
* ファイル全体を頭から読みたいとき（README・設定ファイル）は `Read` のままで良いです
* 言語サポートに穴がある場合、グラフが疎になります（事前に `get_graph_schema` で確認すると安全です）

## おわりに

`codebase-memory-mcp` は、Claude Code を「ファイルを順に読むエージェント」から「コードベースを構造として問い合わせるエージェント」に引き上げる MCP です。`Grep` / `Glob` / `Read` が暗黙に消費していたトークンと時間を、構造クエリに置き換えると、長いタスクの完走率が体感で大きく変わります。

導入後は最初の数回、テキスト探索系ツールを使おうとしてリマインドが出ますが、これは設計どおりの行動なので慌てずグラフツールへ切り替えれば問題ありません。

### 参考
