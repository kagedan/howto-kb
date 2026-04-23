---
id: "2026-04-12-初見リポジトリのclaudemdはrepomixを使うと質が上がるのか検証した-01"
title: "初見リポジトリのCLAUDE.mdはrepomixを使うと質が上がるのか検証した"
url: "https://zenn.dev/aeyesec/articles/20f0df93073692"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-04-12"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

## はじめに

こんにちは。株式会社エーアイセキュリティラボ開発本部の有馬です。

Claude Codeで初見のリポジトリを触るとき、まず `/init` コマンドを実行してCLAUDE.mdを生成することが多いと思います。[公式ドキュメント](https://code.claude.com/docs/ja/best-practices#%E5%8A%B9%E6%9E%9C%E7%9A%84%E3%81%AA-claude-md-%E3%82%92%E6%9B%B8%E3%81%8F)にも「`/init` でスターターファイルを生成し、時間をかけて改善する」と書かれており、私自身も最初の1回だけ実行して、以降は作業しながら手動で加筆していくスタイルをとっています。

つまり、**最初に生成されるCLAUDE.mdが、その後の作業の起点になります**。

しかし実際に生成されたCLAUDE.mdを見てみると、セットアップ方法やコマンド一覧は揃う一方で、「プロジェクトをどう拡張するか」「どこを触れば何が変わるか」といった情報が入ってこないことがあります。

そこで本記事では、**repomixでリポジトリを1ファイルにまとめてClaude Codeに渡す方法**と、**`/init` 単体で生成する方法**を比較し、1回目のCLAUDE.mdの質に差が出るかを検証してみました。

!

**この記事で分かること**

* repomixを使ったCLAUDE.md生成の手順
* `/init` 単体とrepomix経由で生成したCLAUDE.mdの具体的な差分
* 両者の差が生まれる理由と使い分けの考え方

## repomixとは

[repomix](https://github.com/yamadashy/repomix) は、リポジトリ全体をAIが読みやすい単一ファイルにパッケージングするOSSツールです。CLIとWeb版の両方で利用できます。

本記事では[Web版](https://repomix.com/ja/)を使いました。GitHubのURLを入力するだけで変換できます。

類似ツールとしてgitingestや、files-to-promptなどがありますが、GitHubで★22.9k（2026年4月時点）と実績があること、Web版でURL入力だけで手軽に試せることからrepomixを選びました。

出力形式はXML・Markdown・プレーンテキストから選べます。[AnthropicのPromptingベストプラクティス](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#structure-prompts-with-xml-tags)ではコンテキストをXMLタグでセクション分けして渡すことが推奨されており、それに倣ってXML形式で出力しました。

## 検証の準備

### 使用モデル

検証にはClaude Sonnet 4.6を使用しました。

### 題材リポジトリ：simonw/llm

検証の題材には [simonw/llm](https://github.com/simonw/llm)を使いました。Simon Willison氏が開発したCLIツール兼Pythonライブラリで、OpenAI・Anthropic・Geminiなど多数のLLMをコマンドラインから統一的に呼び出せます。プラグイン機構があり規模感も適度なので、検証の題材に選びました。

### repomixの設定

repomix.comのWeb版でsimonw/llmを変換しました。

![repomix設定画面](https://static.zenn.studio/user-upload/24042b1f64eb-20260403.png)

除外パターンには以下を指定しました。

```
docs/**,tests/cassettes/**,.github/**,LICENSE,MANIFEST.in,.readthedocs.yaml
```

| 除外対象 | 除外した理由 |
| --- | --- |
| `docs/**` | 今回はユーザー向けの使い方説明が中心だったのでトークン削減のためにも除外。仕様書等が含まれる場合は読ませた方が良い |
| `tests/cassettes/**` | 記録済みHTTPレスポンス。CLAUDE.md生成には関係ない |
| `.github/**` | CIワークフロー。CLAUDE.md生成には不要 |
| `LICENSE` / `MANIFEST.in` / `.readthedocs.yaml` | 設定ファイル類。本検証には不要 |

また、repomixの**コード圧縮オプション**も有効にしました。Tree-sitter（ソースコードの構文解析ツール）を活用して関数の中身を省略しつつ、関数名やクラス構造だけを残すことでトークン数を大幅に削減できます。

除外前後のトークン数（LLMが処理する文字列の単位。多いほどコストや処理時間が増える）は以下の通りです。

| 状態 | トークン数 |
| --- | --- |
| 除外前 | 155,487 |
| 除外後 | **35,165** |

約78%削減できました。トークン数が少ないほどClaude Codeの処理が速くなり、API利用コストも抑えられます。

## /init だけで生成してみる

simonw/llmをローカルにクローンし、Claude Codeを起動して `/init` を実行します。（repomixのWeb版ならクローン不要ですが、`/init` の実行にはローカルリポジトリが必要です）

![/initの実行画面](https://static.zenn.studio/user-upload/9667b69a64d8-20260403.png)

生成されたCLAUDE.mdは91行でした。

/init 単体で生成したCLAUDE.md（全文）

```
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 開発環境セットアップ

\`\`\`bash
pip install -e '.[test]'
# または
uv sync --all-extras
\`\`\`

## よく使うコマンド

\`\`\`bash
# テスト実行
just test
uv run pytest

# 単一テストファイルの実行
uv run pytest tests/test_llm.py -v

# 特定のテスト関数の実行
uv run pytest tests/test_llm.py::test_function_name -v

# 全リンター実行
just lint

# 自動修正（ruff + black）
just fix

# 型チェックのみ
just mypy

# ドキュメントのcog再生成（README.mdも含む）
just cog

# ドキュメントのライブサーバー
just docs
\`\`\`

## アーキテクチャ概要

**llm** はCLIツール兼Pythonライブラリで、複数のLLMプロバイダーへのアクセスを統一インターフェースで提供する。

### コアモジュール（`llm/`）

- **`cli.py`** — CLIコマンド全体（`llm prompt`、`llm chat`、`llm embed`等）。Click ベース。
- **`models.py`** — 中心的な抽象クラス群：
  - `Model` / `AsyncModel` — モデル実装の基底クラス
  - `KeyModel` / `AsyncKeyModel` — APIキーを必要とするモデル
  - `Response` / `AsyncResponse` — モデル出力（ストリーミング対応）
  - `Conversation` / `AsyncConversation` — チャット履歴管理
  - `Tool` — ツール/関数呼び出しインターフェース
  - `Attachment` — 画像・音声等のバイナリ添付
  - `Fragment` — 外部ソースから読み込むテキスト断片
- **`embeddings.py`** — ベクトル埋め込み機能（`Collection`クラス）
- **`utils.py`** — スキーマDSL、フラグメント処理等のユーティリティ
- **`plugins.py`** / **`hookspecs.py`** — pluggyベースのプラグインシステム
- **`templates.py`** — プロンプトテンプレート管理
- **`default_plugins/`** — 組み込みプラグイン（openai_models.py、default_tools.py）

### データ永続化

全てのログ・会話・埋め込み・フラグメントは **SQLite** に保存される。  
パスは `LLM_USER_PATH` 環境変数で指定（デフォルトはユーザーホームディレクトリ）。  
テストでは `conftest.py` の `user_path` フィクスチャが一時ディレクトリを使用する。

### プラグインシステム

モデルは pluggy のエントリーポイントで動的に読み込まれる。新しいモデルプロバイダーを追加する場合は `hookspecs.py` のフックを実装する。

## テスト構成

\`\`\`
tests/
  conftest.py               # フィクスチャ（user_path, logs_db, env_setup等）
  cassettes/                # pytest-recording の記録済みHTTPレスポンス
  test_llm.py               # コア機能
  test_llm_logs.py          # ログ機能
  test_chat.py              # チャット/会話
  test_embed_cli.py         # 埋め込みCLI
  ...
\`\`\`

テストは `pytest-httpx`（HTTP モック）、`pytest-asyncio`（非同期）、`syrupy`（スナップショット）を使用。

## ドキュメント生成の注意

`README.md` と `docs/*.md` の一部は **cog** によってコードから自動生成される。  
ドキュメントを手動編集した場合、`just cog` を実行しないとリンターが失敗する。
```

コマンドの網羅性・アーキテクチャの概要・テスト構成が揃っており、「このリポジトリで作業するのに最低限必要な情報」はしっかりカバーされています。

## repomix経由で生成してみる

ここではrepomixで用意したファイルを直接渡すことが目的のため、`/init` は使わず `@ファイル名`（Claude Codeでファイルをコンテキストとして渡す記法）でコンテキストを追加してプロンプトで指示する方式をとりました。出力されたXMLファイル（repomix-output-simonw-LLM.xml）をClaude Codeから参照できる場所に配置し、以下を実行しました。

```
@repomix-output-simonw-LLM.xml この内容をもとにCLAUDE.mdを作成してください
```

![repomix経由での実行画面](https://static.zenn.studio/user-upload/9576d9eb8d38-20260403.png)

生成されたCLAUDE.mdは233行になりました。

repomix経由で生成したCLAUDE.md（全文）

```
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 開発環境セットアップ

\`\`\`bash
pip install -e '.[test]'
# または uv を使う場合
uv sync --all-extras
\`\`\`

## よく使うコマンド

\`\`\`bash
# テスト実行
just test
uv run pytest

# 単一テストファイルを実行
uv run pytest tests/test_llm.py -v

# 特定のテスト関数を実行
uv run pytest tests/test_llm.py::test_function_name -v

# 全リンター実行（black チェック・cog チェック・mypy・ruff）
just lint

# 自動修正（ruff + black）
just fix

# 型チェックのみ
just mypy

# ドキュメントの cog 再生成（README.md 含む）
just cog

# ドキュメントのライブサーバー起動
just docs
\`\`\`

> **注意**: `README.md` と `docs/*.md` の一部は cog で自動生成される。手動編集後は `just cog` を実行しないと `just lint` が失敗する。

## アーキテクチャ概要

**llm** は CLI ツール兼 Python ライブラリで、複数の LLM プロバイダーへのアクセスを統一インターフェースで提供する。コアは **プラグインシステム**（pluggy）で構成されており、モデル・埋め込みモデル・ツール・CLI コマンドを外部パッケージとして追加できる。

### コアモジュール（`llm/`）

| ファイル | 役割 |
|---|---|
| `cli.py` | Click ベースの全 CLI コマンド実装 |
| `models.py` | モデル抽象クラス群・Tool・Options・Response |
| `embeddings.py` | ベクトル埋め込み機能（`Collection` クラス） |
| `plugins.py` | pluggy プラグインマネージャーの初期化・読み込み |
| `hookspecs.py` | プラグインフックの仕様定義 |
| `templates.py` | プロンプトテンプレート管理 |
| `tools.py` | 組み込みツール（`llm_version`、`llm_time`） |
| `utils.py` | スキーマ DSL、フラグメント処理等のユーティリティ |
| `default_plugins/openai_models.py` | OpenAI / OpenAI 互換モデルの実装 |
| `migrations.py` / `embeddings_migrations.py` | SQLite マイグレーション |

### データ永続化

全ログ・会話・埋め込み・フラグメントは **SQLite** に保存される。パスは `LLM_USER_PATH` 環境変数で指定（デフォルトはユーザーホームディレクトリ）。テストでは `conftest.py` の `user_path` フィクスチャが一時ディレクトリを使用する。

---

## プラグインシステム

### 利用可能なフック（`hookspecs.py`）

\`\`\`python
@llm.hookimpl
def register_models(register, model_aliases):
    register(MyModel())

@llm.hookimpl
def register_embedding_models(register):
    register(MyEmbeddingModel())

@llm.hookimpl
def register_tools(register):
    @register()
    def my_tool(arg: str) -> str:
        """ツールの説明"""
        return result

@llm.hookimpl
def register_commands(cli):
    @cli.command()
    def my_command():
        pass

@llm.hookimpl
def register_template_loaders(register):
    register("prefix", loader_function)

@llm.hookimpl
def register_fragment_loaders(register):
    register("prefix", loader_function)
\`\`\`

`LLM_LOAD_PLUGINS` 環境変数でロードするプラグインを制御できる。

---

## カスタムモデルの実装

### 同期モデル

\`\`\`python
import llm

class MyModel(llm.Model):
    model_id = "my-model"
    can_stream = True
    supports_tools = False
    supports_schema = False
    attachment_types = set()  # 対応メディアタイプ（例: {"image/png"}）

    class Options(llm.Options):
        temperature: Optional[float] = Field(None, ge=0, le=2)

    def execute(self, prompt, stream, response, conversation):
        # レスポンスを yield（stream=True 時）または response.text に代入
        yield "レスポンステキスト"
        response.set_usage(input=10, output=5)
\`\`\`

### API キーを必要とするモデル

\`\`\`python
class MyKeyModel(llm.KeyModel):
    needs_key = "my-provider"
    key_env_var = "MY_PROVIDER_API_KEY"

    def execute(self, prompt, stream, response, conversation, key):
        # key には解決済みの API キーが渡される
        ...
\`\`\`

非同期版はそれぞれ `llm.AsyncModel` / `llm.AsyncKeyModel` を継承し、`execute` を `async def` にする。

### Options クラス（Pydantic）

`llm.Options` は `BaseModel` を継承。`extra='forbid'` が設定されているため、定義外のフィールドはエラーになる。OpenAI 互換モデルの共通オプションは `default_plugins/openai_models.py` の `SharedOptions` を参照。

---

## Tool システム

### ツール定義

\`\`\`python
from llm.models import Tool, Toolbox

# 関数からツールを作成
tool = Tool.function(my_function, name="optional_name")

# 複数ツールをまとめる Toolbox
class MyTools(Toolbox):
    name = "my_tools"

    def tools(self):
        return [Tool.function(self.my_method)]

    def prepare(self):          # 同期リソース初期化
        ...
    async def prepare_async(self):  # 非同期リソース初期化
        ...
\`\`\`

### ツール呼び出しの流れ

モデルが `ToolCall` を返す → `ToolResult` として実行結果をモデルに送り返す → 最終レスポンスを生成。

---

## OpenAI 互換モデルの追加（`extra-openai-models.yaml`）

`{user_dir}/extra-openai-models.yaml` に記述することで、プラグインなしで OpenAI 互換 API を追加できる：

\`\`\`yaml
- model_id: my-local-model
  model_name: My Local Model
  type: chat                        # "chat" または "completion"
  api_base: http://localhost:8000/v1
  aliases: [local]                  # 省略可
  headers:                          # 省略可
    Authorization: Bearer token
\`\`\`

---

## テスト

### フィクスチャ（`tests/conftest.py`）

| フィクスチャ | 内容 |
|---|---|
| `user_path` | 一時ディレクトリ（`LLM_USER_PATH` を上書き） |
| `logs_db` | テスト用 SQLite DB |
| `mock_model` | `MockModel` インスタンス（キュー方式でレスポンスを制御） |
| `async_mock_model` | 非同期版モックモデル |
| `mock_key_model` | KeyModel バリアント |
| `embed_demo` | テスト用 EmbeddingModel |
| `mocked_openai_chat` | pytest-httpx による OpenAI API モック |
| `templates_path` | 一時テンプレートディレクトリ |

### MockModel のパターン

\`\`\`python
# テスト内でモデルのレスポンスをキューに積む
mock_model.enqueue(["expected response"])
response = model.prompt("test prompt")
assert response.text() == "expected response"
\`\`\`

### プラグインのテスト登録

\`\`\`python
class MockPlugin:
    __name__ = "MockPlugin"

    @llm.hookimpl
    def register_models(self, register):
        register(mock_model)

llm.get_plugin_manager().register(MockPlugin(), name="mock")
\`\`\`

HTTP 通信のモックには `pytest-httpx`、非同期テストには `pytest-asyncio`、スナップショットテストには `syrupy` を使用する。
```

## 比較してみた結果

### 数値で比較

| 項目 | /init 単体 | repomix経由 |
| --- | --- | --- |
| 行数 | 91行 | 233行 |
| 消費トークン（生成時） / 処理時間 | 32.3kトークン・33秒 | 90.7kトークン・42秒 |

### 構成の違い

**`/init` 単体**

```
CLAUDE.md（/init 単体）
├── 開発環境セットアップ
├── よく使うコマンド
├── アーキテクチャ概要
├── テスト構成
└── ドキュメント生成の注意
```

**repomix 経由**

先頭3つは `/init` 単体と同じ見出しです。`← 追加` は、その下に **/init には無かったトップレベルの見出し** として現れたものです。

```
CLAUDE.md（repomix 経由）
├── 開発環境セットアップ
├── よく使うコマンド
├── アーキテクチャ概要
├── プラグインシステム ← 追加
├── カスタムモデルの実装 ← 追加
├── Toolシステム ← 追加
├── OpenAI互換モデル追加 ← 追加
└── テスト（詳細版） ← 追加
```

### 共通して含まれていた情報

どちらの方法でも、以下の情報は生成されていました。

* 開発環境セットアップ（`pip install`、`uv sync`）
* よく使うコマンド（`just test`、`just lint`、`just cog` 等）
* アーキテクチャ概要とコアモジュールの説明
* テスト構成

### repomix経由でのみ含まれていた情報

| 追加された内容 | 具体的な内容 |
| --- | --- |
| **プラグインフック一覧** | `register_models` / `register_tools` 等のコード例付きで列挙 |
| **カスタムモデルの実装パターン** | `Model` / `KeyModel` / `AsyncModel` の継承方法とコード例 |
| **Toolboxクラス** | 複数ツールをまとめる実装パターン |
| **extra-openai-models.yaml** | プラグインなしでOpenAI互換APIを追加する設定例 |
| **MockModelのテストパターン** | `enqueue()` を使った具体的なテスト例 |
| **フィクスチャ一覧** | 8種類のフィクスチャを表形式で整理 |
| **Optionsクラスの詳細** | Pydanticとの統合、`extra='forbid'` の挙動 |

### なぜ差が出たか

[公式ドキュメント](https://code.claude.com/docs/ja/best-practices#%E5%8A%B9%E6%9E%9C%E7%9A%84%E3%81%AA-claude-md-%E3%82%92%E6%9B%B8%E3%81%8F)によると、`/init` は「ビルドシステム、テストフレームワーク、コードパターンを検出する」と説明されています。この結果もそれと一致しており、セットアップ手順・コマンド・テスト構成といった情報はしっかり生成されていました。

一方、プラグインの実装方法やカスタムモデルの作り方は、コードを実際に読み込まなければ拾えない情報です。repomix経由ではソースコード全体（35kトークン分）を明示的に渡しているため、それらもCLAUDE.mdに反映されました。渡したコンテキストの内容の差が、そのまま出力の差につながっています。

本検証はsimonw/llmという1つのリポジトリに基づいており、プラグインシステムを持つ設計上、拡張情報が豊富なリポジトリでした。リポジトリの規模や構造によって差の出方は変わると思いますが、ソースコードを渡した分だけCLAUDE.mdに反映されるという構造は変わらないはずです。

## おすすめワークフロー

検証結果をもとに、以下のワークフローをおすすめします。

1. **repomix.comでリポジトリを1ファイルに変換**
2. **除外パターンで不要なファイルを絞り込む**（docsやテストデータ等）
3. **XML形式で出力し、プロジェクトルートに配置**
4. **Claude Codeで `@ファイル名` → CLAUDE.md生成プロンプトを実行**
5. **生成されたCLAUDE.mdをレビュー・微調整**

### どちらの方法を選ぶか

両者の差は「渡したコンテキストの量と内容」に起因するため、関わり方によって使い分けるのが現実的です。

ツールをコマンドラインから使うだけであれば `/init` で十分です。セットアップ方法とコマンド一覧が揃えば、Claude Codeが作業を進めるのに困りません。

一方、コントリビュートやプラグイン開発をするケース、あるいは業務で既存コードを読み解きながら改修するケースでは、repomixを経由する方が有効です。「どのクラスを継承すればよいか」「フックをどう実装すればよいか」といった拡張に関わる情報がCLAUDE.mdに入るため、Claude Codeへの指示も具体的になります。

## おわりに

この検証を通じて、「**CLAUDE.mdの質はどれだけコンテキストを与えるかで変わる**」ということを改めて実感しました。

`/init` だけでも作業を始めるには十分です。ただ、コントリビュートや業務での改修など、初見のリポジトリに深く入り込む場面では、repomixでソースコードを渡してからCLAUDE.mdを生成する方法をおすすめします。本検証でも、拡張に関わる情報——プラグインの実装方法やカスタムモデルの作り方——は `/init` だけでは得られず、repomix経由で初めてCLAUDE.mdに入ってきました。1回目の精度にこだわる価値は十分あると感じています。

初見リポジトリをClaude Codeで扱う際の参考になれば幸いです。質問や「こんな使い方もあるよ」といったコメントもお気軽にどうぞ。
