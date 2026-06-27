---
id: "2026-06-26-vscode-claude-code-llm-task-router-で記事作成パイプラインを動かす-01"
title: "VSCode × Claude Code × llm-task-router で記事作成パイプラインを動かす：Windows セットアップ入門"
url: "https://qiita.com/rex0220/items/65ae2a95bfd31f7fca4a"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "LLM", "OpenAI", "GPT"]
date_published: "2026-06-26"
date_collected: "2026-06-27"
summary_by: "auto-rss"
query: ""
---

本記事では、Windows 上で VSCode の Claude Code を編集長として据え、Claude と OpenAI 系モデルを役割分担させながら記事を生成する `llm-task-router` の最初の 1 本を動かすまでを、環境構築から疎通確認まで順を追って解説します。

スコープは、**疎通確認 ＋ 短い実ウォークスルーで 1 run の流れを眺めるところまで**です。実運用の細かい回し方や、レビュー工程の深掘りは別記事に譲ります。

## 導入：何を作る記事かと完成形のゴール

まず、この構成の立ち位置を整理します。

**llm-task-router** は、複数ステップの記事作成工程を駆動する薄い ModelRouter 系 CLI です。実際に本文を書くのは内部で呼ばれる LLM であり、VSCode 上の Claude Code はその工程を進行・調整する編集長のような役割を担います。

役割分担のイメージは次のとおりです。

```mermaid
flowchart LR
    A[VSCode] --> B[Claude Code]
    B --> C[llm-task-router]
    C --> D[OpenAI系モデル<br/>本文ドラフト作成]
    C --> E[Claude系モデル<br/>編集レビュー・改善]
    C --> F[runs配下に成果物保存]
```

この記事で目指すゴールは、次の状態まで到達することです。

- Windows で必要な環境を用意できている
- Claude Code を VSCode で使える
- Anthropic / OpenAI の API キーを取得している
- `llm-task-router` を初期化できている
- `.env` と `config/models.yaml` の最小設定ができている
- 疎通確認と短い実ウォークスルーで、1 run の流れを眺められる

所要時間の目安は **30〜60 分程度** です。

必要なものは以下です。

| 項目 | 必要内容 |
|---|---|
| OS | Windows 10（22H2 以降）/ Windows 11。`winget` を使う場合は `winget` が利用可能なこと |
| エディタ | VSCode |
| VSCode 拡張 | Claude Code |
| Node.js | 20 以上 |
| アカウント | Anthropic アカウント |
| アカウント | OpenAI アカウント |
| 支払い設定 | `llm-task-router` で使う API の課金設定 |
| 認証 | Claude Code で必要なサインインまたは利用権 |

:::note info
本記事は外部サービスやサードパーティ CLI に依存する構成を扱います。画面ラベル、料金、コマンド仕様、利用可能モデル ID は更新されることがあります。必ず各公式ドキュメントと対象リポジトリの最新情報も確認してください。
:::

## 先に確認：課金の種類と API キーの扱い

セットアップ前に、課金とセキュリティの前提を押さえておきます。

重要なのは、**Claude Code の利用**と **`llm-task-router` が内部で叩く API** は、同じではないという点です。

- **Claude Code** は VSCode 上で使う編集支援・対話の入口
- **Anthropic API / OpenAI API** は `llm-task-router` が記事生成やレビューで直接利用する課金対象
- ChatGPT Plus などのサブスクリプション契約は、通常 **OpenAI API の従量課金とは別**です

つまり、Claude Code にサインインできても、**`llm-task-router` 用の API キーと課金設定が別途必要**になる場合があります。

:::note info
価格、無料枠、管理画面の UI、認証フローは時期によって変わります。本記事の記述は一般的な流れとして読み、最新情報は必ず公式で確認してください。
:::

次に、**API キーは秘密情報**です。最低限、次は守りましょう。

- `.env` を Git にコミットしない
- 公開リポジトリに API キーを書かない
- `.gitignore` に `.env` を含める
- 誤コミットしたら **即座にキーを失効して再発行する**
- チーム共有時は安全なシークレット管理を使う

## 先に入れる：VSCode で Claude Code を使えるようにする

本記事の中心は **VSCode × Claude Code** なので、先にここを整えます。ここが未設定だと、後半の **Claude Code を起動する** ステップで詰まります。

Claude Code は VS Code の拡張として提供され、利用には対応する VS Code バージョンと、Claude の有料サブスクリプションまたは Claude Console アカウントが必要です。

大まかな流れは次のとおりです。

1. VSCode をインストールする
2. Extensions から **Claude Code** を検索してインストールする
3. 必要に応じて Anthropic アカウントでサインインする
4. Claude Code がコマンドやチャット UI から起動できることを確認する

VSCode の拡張一覧から対象拡張を開き、案内に従って認証します。必要なプランや利用権は時期によって変わるため、拡張の配布ページや公式案内を確認してください。

確認の観点は次のとおりです。

- VSCode に Claude Code 拡張が入っている
- サインインが完了している
- ワークスペース上で Claude Code を開ける
- コマンドパレットやチャット UI から利用できる

:::note warn
Claude Code が使えることと、`llm-task-router` が内部で Anthropic / OpenAI API を使えることは別です。Claude Code の認証だけでは、`OPENAI_API_KEY` や `ANTHROPIC_API_KEY` の設定は代替できません。
:::

## Anthropic で Claude API キーを取得する

Claude API キーは Anthropic のコンソールから発行します。画面ラベルは時期で変わることがあるため、細かな UI 名は公式画面に従ってください。

基本の流れは次のとおりです。

1. Anthropic のアカウントを作成する
2. 支払い方法を登録する
3. API キー発行画面へ進む
4. 新しいキーを作成する
5. 安全な場所に控える

実務上のポイントは次の 2 つです。

- **キーは発行時に一度しか表示されない**場合がある
- 用途ごとにキー名やメモを分けると後で管理しやすい

たとえば記事作成用なら、次のように分けておくと便利です。

- `article-pipeline-main`
- `article-pipeline-test`

## OpenAI で API キーを取得する

OpenAI 側も同様に、Platform から API キーを発行します。

基本の流れは次のとおりです。

1. OpenAI アカウントを作成する
2. 支払い方法、クレジット、請求設定を確認する
3. API キー管理画面を開く
4. 新しいキーを作成する
5. 安全な場所に保管する

OpenAI では Project や Organization 単位で管理できることがありますが、本記事ではそこには深入りしません。最初は **記事用に分けたキーを 1 本作る**くらいで十分です。

:::note warn
OpenAI も Anthropic も、UI 名称や価格体系は変わることがあります。発行手順が多少違って見えても、基本的には **課金設定 → キー発行** の順で追えば大丈夫です。
:::

## Windows に Node.js 20 以上を用意する

`llm-task-router` には **Node.js 20 以上**が必要です。ここでは推測ではなく、**ツール側が要求するバージョン条件に従う**前提で進めます。理由の詳細はパッケージの `package.json` や README の対応バージョン記載を確認してください。

Windows での導入方法は主に次の 3 つです。

- 公式インストーラを使う
- `winget` で入れる
- `nvm-windows` や `fnm` で複数バージョン管理する

最初の 1 回なら、**公式インストーラ** か **winget** が簡単です。`winget` が使えない環境では、公式インストーラを使って進めてください。

PowerShell でバージョン確認します。

```powershell
node -v
npm -v
```

未導入なら、`winget` ではたとえば次のように入れられます。

```powershell
winget install OpenJS.NodeJS.LTS
```

インストール後、あらためて確認します。

```powershell
node -v
npm -v
```

Node.js 20 以上になっていれば OK です。

## `llm-task-router` の前提情報を確認する

次に、利用する CLI の前提を確認します。

本記事で扱うのは npm パッケージ **`@rex0220/llm-task-router`** です。これはサードパーティの scoped パッケージなので、利用前に次を確認するのをおすすめします。

- リポジトリ URL
- README / ドキュメント
- ライセンス
- 対応 Node.js バージョン
- 最新リリース日や保守状況

少なくとも npm 上で次を見ておくと安心です。

```powershell
npm view @rex0220/llm-task-router version
npm view @rex0220/llm-task-router license
npm view @rex0220/llm-task-router repository.url
```

:::note info
以降の `--help`、`init`、`/draft-topic`、`/write-article` などの説明は、対象パッケージの提供仕様に依存します。実際の利用時は、必ずパッケージの README と `--help` 出力を合わせて確認してください。
:::

## `llm-task-router` をグローバルインストールする

CLI 本体をグローバルインストールします。

パッケージ名は `@rex0220/llm-task-router` ですが、コマンド名は **`llm-task-router`**です。

```powershell
npm install -g @rex0220/llm-task-router
```

インストール後、CLI の存在を確認します。

```powershell
llm-task-router --version
llm-task-router --help
```

`-v` がバージョン表示に対応している CLI もありますが、Node 製 CLI では `--version` または `-V` が一般的です。実際の対応フラグは `llm-task-router --help` で確認してください。

ここではまだ API キーが未設定でも、**CLI が起動するかの確認**までは進められます。

もし Windows で `llm-task-router` が見つからない場合は、次を確認してください。

```powershell
npm prefix -g
```

確認ポイントは以下です。

- グローバル npm の配置先がどこか
- その配下の実行パスが `PATH` に通っているか
- PowerShell を再起動したか

## 記事作成フォルダーを作り、`llm-task-router init` を実行する

この CLI は、**カレントディレクトリ基準**で `config/`、`.env`、`runs/` などを扱います。なので、まず作業フォルダーを作ります。

```powershell
mkdir article-pipeline
cd article-pipeline
llm-task-router init
```

`init` により、カレントディレクトリへ初期ファイル群が展開されます。実際に何が生成されるかはバージョンで差があり得ますが、初心者向けには次を把握しておけば十分です。

- `config/`  
  `models.yaml`、`profiles/`、`criteria/` などの設定一式です
- `.env.example`  
  API キーを書き込むための雛形です。実際に使う `.env` 本体ではありません
- `.claude/`  
  編集長セットです。サブエージェント、スラッシュコマンド、allowlist、フックなどが入ります
- `CLAUDE.md`  
  Claude Code が参照するワークスペース側の指示書です

このフォルダーを今後の作業基準にします。以後は **このフォルダーを開いた状態で操作する**と覚えておけば大丈夫です。

通常の `init` は、既存ファイルがあっても**上書きせずにスキップして保護**します。つまり、初回セットアップでは素の `init` で問題ありません。

既存ファイルをバンドル版で上書きして再展開したいときだけ、`--force` を使います。

```powershell
llm-task-router init --force
```

`--force` を使う場面は、主に **CLI をアップグレードしたあと**です。アップグレード時には、編集長セットである `.claude/` 配下のサブエージェント、スラッシュコマンド、allowlist、フックや、`CLAUDE.md`、設定テンプレートが更新されることがあります。

ただし、素の `init` は既存ファイルをスキップするため、すでに作ったワークスペースにはそれらの更新が自動では届きません。新しい編集長セットやテンプレートを既存ワークスペースへ反映したいときに、`llm-task-router init --force` で再展開します。

初心者向けには、次のように覚えておくと分かりやすいです。

- **初回セットアップ**: `llm-task-router init`
- **CLI 更新後にテンプレート類も取り込み直したいとき**: `llm-task-router init --force`

:::note warn
`--force` は既存ファイルを**上書き**します。自分で編集した `config/models.yaml` の実在モデル ID や、手で書き換えた `CLAUDE.md` も置き換わるので注意してください。

安全に反映するなら、次の順がおすすめです。

1. CLI を更新する
2. 自分で直したモデル ID などの編集箇所を控える、またはバックアップする
3. `llm-task-router init --force` を実行する
4. `config/models.yaml` のモデル ID などを再適用し、`CLAUDE.md` にカスタムがあれば取り込み直す

なお、安心材料として **`.env` は `init` が生成も上書きもしません**。展開対象は `.env.example` だけです。したがって、`--force` を使っても **API キーを入れた `.env` は消えず、上書きもされません**。
:::

## `.env` を作成し、API キーを設定する

次に、雛形から `.env` を作ります。

```powershell
Copy-Item .env.example .env
```

その上で `.env` を開き、API キーを設定します。

本記事の最小構成では、環境変数名は **標準名**で揃えます。

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`

`.env` の最小例です。

```dotenv
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxx
```

OpenAI のキーは現在 `sk-proj-` で始まるプロジェクトスコープが既定ですが、プレフィックスは時期で変わるため、ここはダミー値として公式の発行画面に従ってください。

設定の考え方は次の対応です。

| 設定箇所 | 役割 |
|---|---|
| `.env` | 実際の API キーを保持する |
| `providers.*.api_key_env` | どの環境変数名を使うか指定する |
| 未指定時 | 標準名を使う実装が多い |

初心者向けには、まず **最小構成**から始めるのがおすすめです。

| 構成 | `.env` に置くもの | 向いているケース |
|---|---|---|
| 最小構成 | `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | まず動かしたい |
| 発展構成 | 用途別の環境変数名 | 用途別にキーを分けたい |

## Windows で `.env` を安全に扱う

`.env` は便利ですが、**平文ファイル**です。ローカル検証ではよく使われる一方で、誤コミット対策は必須です。

まず、`.gitignore` に `.env` が含まれているか確認します。

```powershell
Get-Content .gitignore
```

まだ無ければ追記します。

```powershell
Add-Content .gitignore ".env"
```

Git 管理下なら、コミット前に次も確認します。

```powershell
git status
```

ここで `.env` が出てこないことを確認してください。

もしすでに誤ってコミットした場合は、**履歴から消したつもりでもキー自体は漏えいした前提**で扱い、次を実施します。

1. Anthropic / OpenAI の管理画面で該当キーを失効する
2. 新しいキーを発行する
3. `.env` を新しい値に更新する
4. 必要なら Git 履歴の対処を行う

また、Windows では `.env` 以外の選択肢として、次の方法もあります。

- ユーザー環境変数として設定する
- Windows 資格情報マネージャなどの仕組みを使う
- CI/CD やチーム運用ではシークレット管理基盤を使う

最初の検証では `.env` が簡単ですが、長期運用では **平文管理を減らす**方向をおすすめします。

:::note warn
`.env` を絶対にコミットしないでください。公開リポジトリに一度でも出たキーは、削除ではなく **失効と再発行**が基本です。
:::

## `config/models.yaml` のモデル ID を実在するものに直す

ここはセットアップ時の **典型的なつまずきポイント**です。

サンプル設定に入っている `model` の値は、そのままだと失敗することがあります。理由は、**利用可能モデル ID が更新される**ためです。したがって、各 provider の現行 API で実在するモデル ID に更新してください。

本記事ではモデル ID を固定の設定例として提示しません。OpenAI / Anthropic とも利用可能・推奨モデルは更新されるので、設定前に必ず各 provider の公式モデル一覧で実在を確認してください。

本記事では考え方が分かる最小断片だけ示します。最小構成では、`.env` の標準名に揃えて指定するか、実装が標準名にフォールバックするなら `api_key_env` 行自体を省略してもかまいません。

```yaml
providers:
  openai:
    api_key_env: OPENAI_API_KEY
    model: <OpenAIの現行モデルID>

  anthropic:
    api_key_env: ANTHROPIC_API_KEY
    model: <Anthropicの現行モデルID>
```

ここで押さえるべきポイントは 2 つです。

- `providers.openai` には **OpenAI の現行モデル ID**
- `providers.anthropic` には **Anthropic の現行モデル ID**

具体的な確認方法は次のとおりです。

| Provider | 確認先 |
|---|---|
| OpenAI | 公式ドキュメント、Platform、モデル一覧 API など |
| Anthropic | 公式ドキュメント、Console、対応モデル一覧など |

例示 ID をそのまま固定で信じるより、**使う直前に最新の一覧で存在確認する**ほうが安全です。

## 疎通確認と VSCode からの最初の入口

`.env` と `config/models.yaml` を整えたら、まず CLI 側の基本確認をもう一度しておきます。

```powershell
llm-task-router --version
llm-task-router --help
```

ここでも、`-v` が使えるかどうかは `--help` で確認してください。一般的には `--version` のほうが安全です。

その後、VSCode で **作業フォルダーごと開きます**。この状態で Claude Code を使うと、作業基準がズレにくくなります。

最初の入口としては、次の流れだけ押さえれば十分です。

1. VSCode で対象フォルダーを開く
2. Claude Code を起動する
3. `"/draft-topic <テーマ>"` で指示ファイルを起案する
4. 内容を承認する
5. `"/write-article"` で記事化へ進む

```mermaid
flowchart TD
    A[VSCodeで作業フォルダーを開く] --> B[Claude Code起動]
    B --> C["/draft-topic テーマ"]
    C --> D[指示内容を確認・承認]
    D --> E["/write-article"]
    E --> F[runs/runId 配下に成果物保存]
```

## 短い実ウォークスルー：実際に 1 記事がどう進むか

以下は、成功時にどんなログ・成果物が残るかをイメージするための例です。テーマ・モデル・設定・CLI バージョンによって、出力やコストは変わります。

ここでは雰囲気をつかむために、1 本の run がどう進むかを短く見ます。題材は軽めにして、**`llm-task-router` が汎用の記事パイプライン**であることを伝えます。

:::note warn
以下のモデル ID・料金・ラウンド数は筆者環境での実績であり、設定例ではありません。`gpt-5.4` / `claude-opus-4-8` はこの記事の推奨設定ではなく、コピペ対象でもありません。各 provider の現行一覧で実在を確認してから設定してください。
:::

たとえばテーマを **ハンドドリップコーヒーの始め方**にすると、全体の流れは次のようになります。

```mermaid
flowchart TD
    A["/draft-topic で指示起案"] --> B[承認]
    B --> C["/write-article 開始"]
    C --> D[create]
    D --> E[refine]
    E --> F[方向性ゲート]
    F --> G[factcheck]
    G --> H[編集レビュー]
    H --> I[公開前ゲート]
    I --> J[承認後 export]
```

各工程の意味をまとめると、以下のイメージです。

| 工程 | 役割 |
|---|---|
| `draft-topic` | テーマから記事方針、想定読者、構成の種を起こす |
| `create` | 本文ドラフトを作る |
| `refine` | 表現や構成を磨く |
| 方向性ゲート | 記事の向きが狙いと合っているか確認する |
| `factcheck` | 断定表現や要確認点を洗う |
| 編集レビュー | 読みやすさ、構成、トーンを編集観点で詰める |
| 公開前ゲート | 最終的に出してよい品質かを確認する |
| `export` | 完成物を最終出力する |

この構成で見えてくるのは、役割分担です。

- **本文執筆**は OpenAI 系の `gpt-5.4`
- **編集レビュー**は Claude 系の `claude-opus-4-8`
- **全体進行**は VSCode 上の Claude Code

つまり、1 モデルに全部やらせるのではなく、**書く役**と **別レンズで見る役**を分けているのがポイントです。なお、この役割分担のモデル名は筆者環境での一例であり、この記事の推奨設定ではなく、コピペ対象でもありません。筆者の実 run では、`refine` は自動ループで **2 ラウンドで clean 停止**しました。

以下は、筆者の実 run（2026-06-22 時点）の実績です。数値・モデル ID・停止ラウンド数は環境やテーマで変わります。

- `[1/7] create`
- `[2/7] refine (clean, 2 rounds)`
- `[3/7] direction`
- `[4/7] factcheck`
- `[5/7] editorial-review`
- `[6/7] verify-artifacts`
- `[7/7] export`
- `factcheck: 14 claims verified, blocking 0, 12 sources reachable`
- `total: ~$0.73 (estimate)`
- `runs/2026-06-22-hand-drip-coffee/`
  - `draft.md`
  - `final.md`
  - `review/`
  - `factcheck/`
  - `completion-report.json`

`runs/<runId>/` 配下には、少なくとも次のような成果物が残ることがあります。

- `draft.md`
- `final.md`
- `review/`
- `factcheck/`
- `completion-report.*`

1 記事あたりの概算コストは、設定モデルや往復回数で変わります。この実 run では **総概算コスト $0.7262**（estimate）、つまり **1 記事 1 ドル未満程度**でした。なお、表示コストは **CLI 側の内部モデル利用に対するローカル概算**であり、**編集長として動く Claude Code 自体の使用量はこの合計に含まれません**。

本記事はセットアップと流れの体感までです。各ゲートの判定基準や運用の作法は別記事で扱います。

## 検証時に確認しておきたいこと

外部依存が多い構成なので、再現性のために次の情報を手元に残しておくと便利です。

| 項目 | 例 |
|---|---|
| Windows バージョン | Windows 11 |
| Node.js | `node -v` の結果 |
| npm | `npm -v` の結果 |
| `llm-task-router` | `llm-task-router --version` の結果 |
| Claude Code 拡張 | VSCode の拡張バージョン |
| 使用モデル | `config/models.yaml` の設定値 |

特に不具合報告や後日の再現では、CLI バージョンや設定値が重要です。

## まとめ：つまずきやすい点と次の一歩

最後に、よくある詰まりどころをまとめます。

| 詰まりどころ | 症状 | まず確認すること |
|---|---|---|
| Claude Code 未導入・未認証 | VSCode から起動できない | VSCode 拡張の導入有無・サインイン状態・VSCode の再読み込み |
| Node.js のバージョン不足 | 起動失敗 | `node -v`（20 以上か） |
| グローバル PATH 問題 | `llm-task-router` が見つからない | `npm prefix -g` の配下が PATH にあるか・PowerShell を再起動したか |
| API キー未設定 | 認証エラー | `.env` の変数名・`config/models.yaml` の `api_key_env` |
| 課金未設定 | billing 関連エラー | OpenAI / Anthropic の請求（billing）設定 |
| `models.yaml` のモデル ID 不一致 | モデル未存在エラー、実行失敗 | 各 provider の公式モデル一覧・provider 指定 |
| `.env` の誤管理 | キー漏えい、運用事故 | `.gitignore` に `.env` があるか・`git status` に出ないか |

本記事で到達したのは、**疎通確認 ＋ 短い実ウォークスルーで 1 run の流れを眺めるところまで**です。

ここまで進めば、Windows でも **Claude Code の導入、API キー取得、Node.js 20 以上の準備、`llm-task-router` の `init`、`.env` と `models.yaml` の最小設定**を順に整えることで、VSCode 上の Claude Code を編集長にした記事作成パイプラインを動かし始められます。

次の一歩として、別記事ではたとえば次の論点を扱います。

- `factcheck` や編集レビューの各ゲートが、何を入力に何を判定しているか
- `refine` の `clean` 停止条件をどう読むか
- 台帳、出典、レビュー記録をどう運用するか
- 実運用でのモデル切り替え、コスト、失敗時リトライの考え方

また、用途別に API キーを分けたい場合は **発展構成**として、`.env` をたとえば次のように分離できます。

```dotenv
OPENAI_API_KEY_ARTICLE=sk-proj-xxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY_ARTICLE=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxx
```

その場合は、`config/models.yaml` 側の `api_key_env` も対応して揃えます。

```yaml
providers:
  openai:
    api_key_env: OPENAI_API_KEY_ARTICLE
    model: <OpenAIの現行モデルID>

  anthropic:
    api_key_env: ANTHROPIC_API_KEY_ARTICLE
    model: <Anthropicの現行モデルID>
```

最小構成では **標準名で一本道**に、分離したくなったら **発展構成として `.env` と `api_key_env` を一緒に切り替える**と覚えておくと混乱しにくいです。

## 参考

<!-- sources:begin -->
- [S001] npm registry metadata: @rex0220/llm-task-router（primary, retrieved: 2026-06-22）
  https://registry.npmjs.org/@rex0220/llm-task-router
- [S003] Node.js Releases / Release schedule（primary, retrieved: 2026-06-22）
  https://nodejs.org/en/about/previous-releases
- [S004] What is ChatGPT Plus? | OpenAI Help Center（primary, retrieved: 2026-06-22）
  https://help.openai.com/en/articles/6950777-what-is-chatgpt-plus
- [S008] Download Node.js | Node.js 公式ダウンロード（primary, retrieved: 2026-06-22）
  https://nodejs.org/en/download
- [S009] API overview / Getting started - Claude API Docs（Anthropic 公式）（primary, retrieved: 2026-06-22）
  https://docs.anthropic.com/en/api/getting-started
- [S010] Claude Console - API Keys（Anthropic 公式コンソール）（primary, retrieved: 2026-06-22）
  https://console.anthropic.com/settings/keys
- [S011] Where do I find my OpenAI API Key? | OpenAI Help Center（primary, retrieved: 2026-06-22）
  https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key
- [S012] Use Claude Code in VS Code - Claude Code Docs（Anthropic 公式）（primary, retrieved: 2026-06-22）
  https://docs.anthropic.com/en/docs/claude-code/vs-code
- [S013] llm-task-router init 実装（src/cli/init.ts ＋ src/index.ts の init コマンド定義・同梱 config/・templates/）（primary, retrieved: 2026-06-26）
  https://github.com/rex0220/llm-task-router/blob/main/src/cli/init.ts
<!-- sources:end -->
