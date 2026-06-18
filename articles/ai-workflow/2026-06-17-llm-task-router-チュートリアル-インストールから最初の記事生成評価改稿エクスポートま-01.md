---
id: "2026-06-17-llm-task-router-チュートリアル-インストールから最初の記事生成評価改稿エクスポートま-01"
title: "llm-task-router チュートリアル — インストールから最初の記事生成・評価・改稿・エクスポートまで手を動かして学ぶ"
url: "https://qiita.com/rex0220/items/788554bfd0c69a6c470c"
source: "qiita"
category: "ai-workflow"
tags: ["API", "LLM", "OpenAI", "GPT", "TypeScript", "qiita"]
date_published: "2026-06-17"
date_collected: "2026-06-18"
summary_by: "auto-rss"
query: ""
---

この記事は `llm-task-router` の思想や比較を紹介するものではなく、実際にコマンドを上から順に実行して、最初の1本を生成し、評価・改稿・エクスポートまで一周するハンズオンガイドです。具体的には、

- インストール
- 初期化
- 記事生成
- 評価
- 改稿
- エクスポート

までを一通り体験します。手順どおりに進めれば `runs/<runId>/` に成果物が残り、最終的に `final.md` まで到達できる構成です。

なお、表示例やモデル名、価格、ファイル名の一部は理解しやすさを優先した簡略化例です。実際の既定値、利用可能なプロファイル、出力ファイル、工程名はバージョンによって異なる場合があるため、手元では必ず `llm-task-router --help` と README を確認してください。

また、この記事のコマンドは **bash（macOS / Linux / Git Bash など）前提**で書いています。`cp` や `cat <<EOF`、行末の `\` での継続、`which` などは PowerShell や cmd ではそのまま動かないため、Windows ネイティブのシェルを使う場合は適宜読み替えてください。

## 前提条件を確認する

最初に、つまずきやすい前提を3つ確認しておきます。

### 1. Node.js は 20 以上を使う

`llm-task-router` を使う前に、Node.js のバージョンを確認します。

```bash
node -v
npm -v
```

Node.js は **20 以上** を使ってください。  
Node.js 18 を含む 20 未満は対象外として扱う前提で進めるのが安全です。

### 2. API キーを自分で用意する

OpenAI や Anthropic など、利用するプロバイダの API キーは自分で用意する必要があります。  
CLI 側がキーを発行してくれるわけではありません。

### 3. 専用の作業ディレクトリを作る

`config/`、`.env`、`runs/` はすべて**カレントディレクトリ基準**で読み書きされます。  
そのため、専用の作業ディレクトリを1つ作って、その中で操作するのが分かりやすいです。

:::note warn
よくあるつまずきは次の3つです。

- Node.js のバージョンが古い
- `.env` に API キーを設定していない
- 別ディレクトリで実行していて `config/` や `runs/` が見つからない

動かないときは、まずこの3点を確認してください。
:::

## ステップ1: インストールする

まずはグローバルインストールします。

パッケージ名はスコープ付きの `@rex0220/llm-task-router` ですが、実行コマンド名は **`llm-task-router`** です。

```bash
npm install -g @rex0220/llm-task-router

llm-task-router --version
llm-task-router --help
```

- `llm-task-router --version` でバージョン確認
- `llm-task-router --help` でコマンド一覧確認

という流れです。

`-v` がバージョン表示に割り当てられているかどうかは CLI 実装によって異なることがあるため、まずは `--version` を使うのが安全です。

もしここで `command not found` になる場合は、グローバル npm バイナリの PATH を確認してください。  
また、Node.js が古いとインストールや起動に失敗することがあります。

## ステップ2: 作業ディレクトリを初期化する

次に、専用の作業ディレクトリを作って `init` します。

```bash
mkdir my-llm-task-router-work
cd my-llm-task-router-work

llm-task-router init

cp .env.example .env
```

`init` を実行すると、たとえば次のような雛形が展開されます。

- `config/`
- `.env.example`

その後、`.env.example` を `.env` にコピーして、利用する API キーを設定します。

```bash
# 例（標準名を使う場合）
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

:::note warn
**`.env` の変数名は、`config/models.yaml` の `providers.*.api_key_env` と必ず一致させてください。** ここがハンズオンで一番つまずきやすいポイントです。

同梱テンプレートの `config/models.yaml` は `api_key_env: OPENAI_API_KEY_ARTICLE` / `ANTHROPIC_API_KEY_ARTICLE` を参照しているため、テンプレートをそのまま使うなら `.env` 側も `_ARTICLE` 付きの名前で入れる必要があります。

```bash
# 例（同梱テンプレートのまま使う場合）
OPENAI_API_KEY_ARTICLE=your_openai_api_key
ANTHROPIC_API_KEY_ARTICLE=your_anthropic_api_key
```

逆に上記のような標準名（`OPENAI_API_KEY` など）を使いたいなら、`config/models.yaml` 側の `api_key_env` を消すか標準名に書き換えます（`api_key_env` を省略すると標準名にフォールバックします）。モデル ID だけ直して API キー名の不一致に気づかず失敗、というのが典型的なミスです。
:::

既存ファイルは基本的に上書きしません。  
どうしても強制上書きしたい場合だけ `--force` を使います。

```bash
llm-task-router init --force
```

:::note warn
`.env` は Git にコミットしないでください。  
API キーが含まれるため、`.gitignore` に入っているかも確認しておくと安心です。
:::

## ステップ3: `config/models.yaml` を設定する

記事生成に使うモデルは `config/models.yaml` で設定します。  
`init` で展開された雛形をベースに、タスクごとの `primary` / `fallback`、モデル ID、価格情報などを編集していくのが基本です。

`init` 直後の雛形に近い構造は、おおよそ次のとおりです（モデル名はダミー、構造は実装に合わせています）。

```yaml
# この例は標準名（OPENAI_API_KEY / ANTHROPIC_API_KEY）を使うパターン。
# 同梱テンプレートは OPENAI_API_KEY_ARTICLE などを参照するので、
# .env の変数名と api_key_env は必ず揃える（ステップ2の注意書きを参照）。
providers:
  openai:
    api_key_env: OPENAI_API_KEY
  anthropic:
    api_key_env: ANTHROPIC_API_KEY

# コスト概算用の単価（USD / 1M tokens）。provider → model の下にぶら下げる。
prices:
  openai:
    example-strong-model:
      input_usd_per_1m_tokens: 2.5
      output_usd_per_1m_tokens: 15
    example-writing-model:
      input_usd_per_1m_tokens: 10
      output_usd_per_1m_tokens: 30
  anthropic:
    example-review-model:
      input_usd_per_1m_tokens: 5
      output_usd_per_1m_tokens: 25
    example-fallback-model:
      input_usd_per_1m_tokens: 3
      output_usd_per_1m_tokens: 15

defaults:
  timeout_ms: 120000

tasks:
  article_brief:
    primary:
      provider: openai
      model: example-strong-model
    fallback:
      - provider: anthropic
        model: example-review-model
    temperature: 0.4
    max_tokens: 4000

  outline:
    primary:
      provider: anthropic
      model: example-review-model
    fallback:
      - provider: openai
        model: example-strong-model
    max_tokens: 8000

  draft_markdown:
    primary:
      provider: openai
      model: example-writing-model
    fallback:
      - provider: anthropic
        model: example-fallback-model
    max_tokens: 12000

  technical_review:
    primary:
      provider: anthropic
      model: example-review-model
    fallback:
      - provider: openai
        model: example-strong-model

  rewrite:
    primary:
      provider: openai
      model: example-writing-model
    fallback:
      - provider: anthropic
        model: example-fallback-model
    max_tokens: 12000

  # final.md の評価（審査役）。本文(rewrite)とは別系統のプロバイダを主審査に置く。
  final_review:
    primary:
      provider: anthropic
      model: example-review-model
    fallback:
      - provider: openai
        model: example-strong-model
```

ここでは `example-strong-model` のようなダミー名を使っています。  
実際には、自分が使いたいプロバイダとモデル ID に置き換えてください。タスク名（`article_brief` / `outline` / `draft_markdown` / `technical_review` / `rewrite` / `final_review` など）は実装が参照するキーなので、**同梱の `config/models.yaml` に合わせる**のが安全です。

押さえておきたい構造上のポイントは次の3つです。

- `fallback` は**配列**で書く（上から順に試される）。単一でも `- provider: ...` のリスト形式にする。
- 価格は `tasks` の下ではなく、トップレベルの `prices.<provider>.<model>` の下に `input_usd_per_1m_tokens` / `output_usd_per_1m_tokens`（USD / 1M tokens）で持つ。
- `providers.*.api_key_env` を省略すると、`OPENAI_API_KEY` / `ANTHROPIC_API_KEY` などの標準名にフォールバックする。

:::note warn
モデル名や価格は変動します。この記事中の値をそのまま使わず、必ず各プロバイダの公式ドキュメントで最新情報を確認してください。タスク名・キー名の正は、手元の `config/models.yaml` です。
:::

### 同梱テンプレートの設定例（執筆時点）

ダミー名だとイメージしにくいので、`init` で展開される同梱テンプレートの中身（執筆時点・2026-06）も載せておきます。**モデル ID と価格は当時のものなので、そのまま使わず必ず最新を確認してください。**

```yaml
# モデルIDは利用時点の公式ドキュメント/ダッシュボードで必ず確認すること。
# - OpenAI:    https://developers.openai.com/api/docs/pricing
# - Anthropic: https://docs.anthropic.com/en/docs/about-claude/models/overview

providers:
  openai:
    api_key_env: OPENAI_API_KEY_ARTICLE
  anthropic:
    api_key_env: ANTHROPIC_API_KEY_ARTICLE

# コスト概算用の単価（USD / 1M tokens）。価格改定でドリフトするため要定期確認。
# 取得時点: 2026-06（OpenAIは公式pricing、Anthropicはモデル概要に基づく概算）。
prices:
  openai:
    gpt-5.4:
      input_usd_per_1m_tokens: 2.5
      output_usd_per_1m_tokens: 15
    gpt-5.4-mini:
      input_usd_per_1m_tokens: 0.75
      output_usd_per_1m_tokens: 4.5
  anthropic:
    claude-opus-4-8:
      input_usd_per_1m_tokens: 5
      output_usd_per_1m_tokens: 25
    claude-sonnet-4-6:
      input_usd_per_1m_tokens: 3
      output_usd_per_1m_tokens: 15

defaults:
  timeout_ms: 120000

tasks:
  article_brief:
    primary:
      provider: openai
      model: gpt-5.4
    fallback:
      - provider: anthropic
        model: claude-opus-4-8
    temperature: 0.4
    max_tokens: 4000

  outline:
    primary:
      provider: anthropic
      model: claude-opus-4-8
    fallback:
      - provider: openai
        model: gpt-5.4
    temperature: 0.4
    # 比較記事など節数が多いテーマでは構成JSONが4000では打ち切られ、
    # 途中で切れたJSONがArticleOutline検証に失敗する。余裕を持たせる。
    max_tokens: 8000

  draft_markdown:
    primary:
      provider: openai
      model: gpt-5.4
    fallback:
      - provider: anthropic
        model: claude-sonnet-4-6
    temperature: 0.6
    max_tokens: 12000
    timeout_ms: 180000

  technical_review:
    primary:
      provider: anthropic
      model: claude-opus-4-8
    fallback:
      - provider: openai
        model: gpt-5.4
    temperature: 0.2
    max_tokens: 6000

  rewrite:
    primary:
      provider: openai
      model: gpt-5.4
    fallback:
      - provider: anthropic
        model: claude-sonnet-4-6
    temperature: 0.5
    max_tokens: 12000
    timeout_ms: 180000

  # final.md の評価（審査役）。本文(rewrite)は openai 主体なので、別系統の anthropic を主審査に置く。
  final_review:
    primary:
      provider: anthropic
      model: claude-opus-4-8
    fallback:
      # opus 混雑時も審査役を Anthropic に保ち、本文(openai)との別系統性を維持する。
      - provider: anthropic
        model: claude-sonnet-4-6
      - provider: openai
        model: gpt-5.4
    temperature: 0.2
    max_tokens: 6000

  markdown_format:
    primary:
      provider: openai
      model: gpt-5.4-mini
    temperature: 0.2
    max_tokens: 8000

  title_suggestions:
    primary:
      provider: openai
      model: gpt-5.4-mini
    temperature: 0.5
    max_tokens: 1200
```

ここから読み取れる実運用上の工夫がいくつかあります。

- **本文と審査の系統を分ける** — 本文生成（`draft_markdown` / `rewrite`）は openai 主体、審査役（`technical_review` / `final_review`）は anthropic 主体にして、書き手と評価者の独立性を保っている。
- **タスクごとに `temperature` を変える** — `final_review` / `technical_review` は `0.2` と低め（採点のブレを抑える）、本文は `0.5〜0.6` とやや高め。
- **長文・重い工程に余裕を持たせる** — `outline` の `max_tokens` を 8000 に上げ（JSON 打ち切り対策）、`draft_markdown` / `rewrite` は `timeout_ms: 180000` で既定より長くしている。
- **安い工程は軽量モデルに振る** — `markdown_format` / `title_suggestions` は `gpt-5.4-mini` を使う。
- **API キー名は `_ARTICLE` 付き** — テンプレートは `OPENAI_API_KEY_ARTICLE` を参照するので、`.env` 側も同じ名前で入れる（ステップ2の注意書きを参照）。

:::note warn
上のモデル ID（`gpt-5.4` / `claude-opus-4-8` など）と価格は執筆時点の例です。提供状況・モデル名・価格はプロバイダ側で変わるため、実運用では必ず公式ドキュメントで確認してください。手元の `config/models.yaml` が常に正です。
:::

### 生成AIに `models.yaml` を作らせるプロンプト

タスク構成やフォールバックの考え方を一から手書きするのが面倒なら、構造ルールを渡して生成AI（ChatGPT / Claude など）にたたき台を作らせる手もあります。下のプロンプトの「あなたの状況」だけ埋めて投げてください。

```text
あなたは llm-task-router の設定ファイル config/models.yaml を作る手伝いをします。
出力は、そのまま config/models.yaml に貼って動く YAML のみにしてください。
Markdown のコードフェンス（```）・前置き・後書き・YAML 外の説明文は一切出さないでください。
補足したいことは YAML コメント（# で始まる行）として YAML 内に書いてください。
以下の【スキーマ規約】を厳密に守ってください。

【スキーマ規約】
- トップレベルキーは providers / prices / defaults / tasks の4つ。
- providers.<name>.api_key_env に、その provider の API キーを入れる環境変数名を書く。
  省略すると OPENAI_API_KEY / ANTHROPIC_API_KEY などの標準名にフォールバックする。
- tasks のキー（タスク名）は次の固定名のみ。勝手に増減・改名しない:
  article_brief, outline, draft_markdown, technical_review, rewrite,
  final_review, markdown_format, title_suggestions
- 各タスクは primary: { provider, model } を必須で持つ。
- fallback は配列。要素は { provider, model }。単一でも "- provider:" のリスト形式で書く。
- 任意で temperature / max_tokens / timeout_ms をタスクごとに指定できる。
- 価格は tasks の下ではなく、トップレベル prices.<provider>.<model> の下に
  input_usd_per_1m_tokens / output_usd_per_1m_tokens（USD / 1M tokens）で持つ。
- defaults.timeout_ms に全体の既定タイムアウト（ミリ秒）を置ける。

【設計方針】
- 本文生成（draft_markdown / rewrite）と審査役（technical_review / final_review）は、
  できるだけ別プロバイダにして書き手と評価者の独立性を保つ。
- final_review / technical_review は temperature を低め（例: 0.2）にして採点のブレを抑える。
- draft_markdown / rewrite は max_tokens を大きめ（例: 12000）、必要なら timeout_ms も長め。
- outline は JSON が途中で切れないよう max_tokens に余裕を持たせる（例: 8000）。
- markdown_format / title_suggestions は軽量・安価なモデルでよい。
- fallback には primary と同等以上で役割が近いモデルを置く（出力形式を崩しにくいもの）。

【重要な制約】
- モデル ID を勝手に発明しない。下の「使えるモデル」で渡したものだけを使う。
- 不明な価格は推測で埋めず、その行を空けて「要確認」とコメントする。

【あなたの状況】（ここを埋める）
- 使うプロバイダ: 例) openai, anthropic
- 使えるモデル（provider: model-id: 用途/おおよその単価がわかれば併記）:
  例) openai: <model-id>（高品質・本文向き） / openai: <model-id>（安価・整形向き）
      anthropic: <model-id>（審査向き） / anthropic: <model-id>（フォールバック向き）
- API キーの環境変数名: 例) OPENAI_API_KEY_ARTICLE, ANTHROPIC_API_KEY_ARTICLE
- 予算/速度の優先度: 例) 品質優先 / コスト優先 / バランス
```

:::note warn
生成AIはモデル ID や価格をもっともらしく**捏造する**ことがあります。出力された YAML は、タスク名が固定名どおりか、`fallback` が配列か、`prices` の位置と単位が正しいか、そして**モデル ID と価格が実在の最新値か**を必ず人間が確認してください。プロンプトでも「モデル ID を発明しない／不明な価格は要確認とする」よう縛っていますが、最終チェックは省略しないでください。
:::

## ステップ4: 最初の記事を作る

ここから実際に記事を生成します。  
最初は短いテーマを `--topic` でインライン指定するのが簡単です。

まず、オプションや既定値を手元で確認しておきます。

```bash
llm-task-router article:create --help
```

なお `--help` は `--profile` オプションの存在を示すだけで、**利用可能なプロファイル名の一覧までは表示しません**。使えるプロファイル名は `config/profiles/` 配下のファイル（`qiita.yaml` / `zenn.yaml` など）か README で確認してください。

そのうえで記事を作成します。

```bash
llm-task-router article:create \
  --topic "社内ナレッジ検索における AI 活用の落とし穴" \
  --profile qiita
```

長文の指示を渡したい場合は `--topic-file` を使います。

```bash
mkdir -p topics

cat > topics/ai-ir.txt <<'EOF'
社内情報検索に AI を導入するときの設計上の注意点をテーマに、
Qiita 向けの実践記事を書いてください。

含めたい論点:
- 検索対象データの整備
- 権限管理
- hallucination 対策
- 評価指標
- スモールスタートの進め方
EOF

llm-task-router article:create \
  --topic-file topics/ai-ir.txt \
  --profile qiita
```

`--topic` と `--topic-file` は**排他**です。  
同時指定はできません。

また、`runId` の決まり方は実装依存です。`--topic-file` のファイル名が反映される場合もありますが、**以後のコマンドでは推測せず、生成完了時に stdout に表示された `runId:` の値をそのまま使う**のが安全です。

## ステップ5: 進捗表示と `runs/<runId>/` の成果物を確認する

生成を実行すると、進捗は主に **stderr** に出力され、機械処理しやすい情報は **stdout** に出力されます。

たとえば表示例は次のようになります。

```text
[1/5] brief (article_brief) ...
[1/5] brief - done via openai/example-strong-model (842ms, ~$0.0021)
[2/5] outline (outline) ...
[2/5] outline - done via anthropic/example-review-model (1104ms, ~$0.0034)
[3/5] draft (draft_markdown) ...
[3/5] draft - done via openai/example-writing-model (5321ms, ~$0.0218)
[4/5] review (technical_review) ...
[4/5] review - done via anthropic/example-review-model (2877ms, ~$0.0069)
[5/5] final (rewrite) ...
[5/5] final - done via openai/example-writing-model (4012ms, ~$0.0152)
total: ~$0.0494 (estimate)

runId: 2026-06-16-ai-ir
final: runs/2026-06-16-ai-ir/final.md
```

工程は開始時に `[i/total] <step名> (<task名>) ...`、完了時に `[i/total] <step名> - done via <provider>/<model> (...)` の**2行**で出ます。step 名と task 名は別物で、たとえば最終工程は step 名が `final`、task 名が `rewrite` です（`final.md` を生成）。

`runId` と `final` のパスは `stdout` 側に `runId: ...` / `final: ...` の形式で出ます（`=` ではなくコロン区切り）。スクリプトで拾うときはこの形式に合わせてください。

読み方のポイントは次のとおりです。

- `[1/5]` のような表記は工程番号
- `brief` / `outline` / `draft` などは工程名
- `via openai/...` は実際に使われたプロバイダとモデル
- `(xxxms, ~$0.0xxx)` は処理時間と概算コスト
- `total: ~$... (estimate)` は全体の概算コスト

`primary` に設定したものと異なるプロバイダが表示されていたら、`fallback` が使われたサインです。

ここで大事なのは、`article:create` の内部工程と、後続の `article:evaluate` / `article:revise` は別物だという点です。

- `article:create` は、初稿作成後にレビュー結果を踏まえて**自動で整える工程**を含むことがあります
- `article:evaluate` は、完成した `final.md` をあとから評価してレビュー資料を作るコマンドです
- `article:revise` は、その評価結果や自分の指示をもとに**ユーザー主導で改稿する**コマンドです

つまり、create 中に `rewrite` のような工程が見えても、それは初回生成フローの一部であり、ステップ7以降の評価・改稿とは役割が異なります。

進捗表示と成果物の対応は、たとえば次のように読むと分かりやすいです。

| 進捗表示 | 内部タスク例 | 主な生成物 |
| --- | --- | --- |
| `[1/5] brief` | `article_brief` | `brief.json` |
| `[2/5] outline` | `outline` | `outline.json` |
| `[3/5] draft` | `draft_markdown` | `draft.md` |
| `[4/5] review` | `technical_review` | `review.json` |
| `[5/5] final` | `rewrite` | `final.md` |

この例では、**`rewrite` 工程の出力が `final.md`** です。  
そのため、成果物一覧に `rewrite.md` のような別ファイルが見当たらなくても不自然ではありません。

:::note info
上の進捗表示やファイル対応はあくまで一例です。実際の工程名、タスク名、出力ファイル名はバージョンによって異なる場合があります。手元では `--help`、README、実際に生成された `runs/<runId>/` の中身を優先して確認してください。
:::

生成後は `runs/<runId>/` に成果物が並びます。代表的には次のようなファイルです。

- `brief.json`  
  記事の要件整理結果
- `outline.json`  
  構成案
- `draft.md`  
  初稿
- `review.json`  
  初稿レビュー結果
- `final.md`  
  最終稿
- `meta.json`  
  実行メタ情報や解決済み profile 情報

どの工程で何が作られたかを追うと、生成フロー全体が把握しやすくなります。

:::note info
後続の `resume`、`review`、`evaluate`、`revise`、`export` では `--run` に `runId` を渡します。手入力で推測せず、直前の実行結果に表示された `runId:` の値をコピーして使うのが確実です。
:::

## ステップ6: 途中から再開する・レビューだけ再実行する

途中で失敗した場合も、最初から全部やり直す必要はありません。

### 途中から再開する

```bash
llm-task-router article:resume --run 2026-06-16-ai-ir
```

### レビュー以降を再実行する

`draft.md` まではそのまま使って、レビュー→再生成だけやり直したい場合は `article:review` を使います。

```bash
llm-task-router article:review --run 2026-06-16-ai-ir
```

再実行時には、完了済みステップが `skip (done)` のように表示されることがあります。  
これを見れば、どこまで再利用され、どこから再実行されたかが分かります。

失敗時に毎回ゼロから作り直さなくてよいのは、運用上かなり便利です。

## ステップ7: 記事を評価する

記事が完成したら、`article:evaluate` で評価レポートと改稿指示を作れます。

```bash
llm-task-router article:evaluate \
  --run 2026-06-16-ai-ir \
  --min-severity major
```

このコマンドで、たとえば次のような成果物が生成されます。

- `final-review.json`  
  機械処理しやすい評価結果
- `final-review.md`  
  人が読みやすい評価レポート
- `revise-instruction.md`  
  改稿のための指示書

ポイントは、`revise-instruction.md` はローカル組み立てで作られ、**追加 API コールなし**で生成されることです。

ただし、`revise-instruction.md` は**常に作られるとは限りません**。`--min-severity` で指定した重大度以上の指摘が0件だった場合は改稿指示ファイルは生成されず、stdout には `instruction: (none ...)` のように表示されます（過去の実行で残っていた古い `revise-instruction.md` は削除されます）。指摘が出ているかどうかは `final-review.md` のサマリで確認できます。

また、この段階では**自動改稿は走りません**。  
まず人が `final-review.md` や `revise-instruction.md` を確認して、「この修正を入れるか」を判断する前提です。

## ステップ8: 改稿する

評価結果を見て修正したくなったら、`article:revise` を実行します。

まずは改稿指示を確認します（前のステップで `revise-instruction.md` が生成された場合のみ。`instruction: (none ...)` だった場合はこのファイルは存在しません）。

```bash
cat runs/2026-06-16-ai-ir/revise-instruction.md
```

問題なければ、`--instruction-file` で渡して改稿します。

```bash
llm-task-router article:revise \
  --run 2026-06-16-ai-ir \
  --instruction-file runs/2026-06-16-ai-ir/revise-instruction.md
```

短い指示なら `--instruction` を使う方法もありますが、`--instruction` と `--instruction-file` は**排他**です。

改稿時には、改稿前の `final.md` が `final.bak.md` のような名前でバックアップされる場合があります。  
ただし、この挙動や複数回実行時の扱いはバージョンや実装によって異なる可能性があります。`final.bak.md` が毎回更新される実装も考えられるため、README や実際の出力を確認してください。

そのため、連続で試す場合は `git` 管理か手動バックアップを前提にしておくのが安全です。

```bash
cp runs/2026-06-16-ai-ir/final.md runs/2026-06-16-ai-ir/final.before-second-revise.md
```

特に、

- 改稿前後の差分確認
- 必要ならロールバック判断

をしやすくするには、`git diff` や手動バックアップを併用するのがおすすめです。

改稿後は新しい `final.md` を確認し、必要なら再度 `article:evaluate` → `article:revise` を回せます。

:::note warn
バックアップファイルの有無や命名規則を記事の記述だけで決め打ちしないのが安全です。運用では `git` 管理を基本にし、必要に応じて手動コピーも残す、という方針に寄せるのがおすすめです。
:::

## ステップ9: プロファイルを切り替える

利用可能なプロファイル名は `config/profiles/` 配下のファイル名（`qiita` / `zenn` / `blog` / `note` など）で確認できます。README にも一覧があります（`--help` には一覧は出ません）。

```bash
ls config/profiles/
```

そのうえで、たとえば Zenn 向けにしたい場合はこうです。

```bash
llm-task-router article:create \
  --topic "TypeScript CLI 開発でハマったポイントまとめ" \
  --profile zenn
```

利用できるプロファイル名や既定値は、バージョンや設定によって異なる場合があります。  
この記事では例として `qiita`、`zenn`、`blog`、`note` のような名前を挙げていますが、**実際に使えるものは `config/profiles/` の中身と README を優先**してください。

プロファイルによって、内部的には次のような情報が解決されることがあります。

- `platform`
- `style`
- `language`
- `criteria_file`

そして、この解決済みの profile 情報は `meta.json` に残り、以後の

- `resume`
- `review`
- `revise`
- `evaluate`

でも再利用されます。

:::note info
Qiita 向けプロファイルでは、`:::note info` や `:::note warn` のような記法を使う前提の出力になることがあります。
:::

## ステップ10: 完成記事をエクスポートする

完成した `final.md` を外に書き出すには `article:export` を使います。

```bash
llm-task-router article:export \
  --run 2026-06-16-ai-ir \
  --out ../zenn-content/articles/my.md
```

必要に応じて `--force` で上書きできます。

```bash
llm-task-router article:export \
  --run 2026-06-16-ai-ir \
  --out ../zenn-content/articles/my.md \
  --force
```

`article:export` は、**`final.md` だけを書き出す外部出力コマンド**です。

安全寄りの挙動として、たとえば次の特徴があります。

- `.env*` への出力は拒否
- ワークスペース外への書き出しには警告
- 既存ファイルは `--force` なしでは上書きしない

うっかり事故を防ぎやすい設計です。

## 補足1: 出力ガードとコスト表示の見方

生成系の工程には、出力ガードが入っていることがあります。  
たとえば `draft` / `rewrite` / `revise` では次のような仕組みがあります。

- `max_tokens` 到達による打ち切り警告
- 外側コードフェンス除去
- ラップ文検出

ラップ文検出は**警告**として扱われる前提で読み取るのがよいです。

また、コスト表示は API の実請求額そのものではありません。  
`usage` トークン数 × `config/models.yaml` の `prices` で計算する**ローカル概算**です。

そのため、次の理由で実請求額とはズレることがあります。

- リトライ集計
- キャッシュやバッチ割引
- 価格改定の反映遅れ
- 実プロバイダ側の課金仕様差分

予算感の把握用途として見るのがよいです。

## 補足2: 開発中にローカル版を試す方法

CLI 自体を開発中なら、グローバルインストール済み版だけでなくローカルソースから直接試す方法も便利です。

```bash
# package.json の scripts 経由で実行
npm run article:create -- --topic "テストテーマ"

# TypeScript エントリを直接実行
npx tsx src/index.ts article:create --topic "テストテーマ"

# ローカル版を llm-task-router コマンドとしてリンク
npm link
llm-task-router --help
```

`npm run ... --` のように `--` を付けることで、後続のフラグを CLI に渡せます。

`npm link` を使う場合は、グローバルインストール版とどちらが呼ばれるか混乱しやすいため、必要なら先にグローバル版を外しておくと安全です。

```bash
npm uninstall -g @rex0220/llm-task-router
which llm-task-router
```

この方法を使うと、README に書かれているのと近い操作感のまま、ローカル変更をすぐ検証できます。

## 補足3: セキュリティ方針と運用上の注意

`llm-task-router` は CLI とローカルファイルを中心に扱うツールです。  
ただし、セキュリティに関する具体的な保証範囲は**README と実装を確認してください**。

少なくとも利用者側では、次の管理が必要です。

- `.env` の保護
- 生成物の共有前確認
- Git の ignore 設定
- 社内外への持ち出し判断

とくに「ログに API キーやプロンプト全文を残すかどうか」「外部アクセス方針」は、バージョンや設定差分があると影響が大きいため、運用前に README の該当箇所と実際の出力を一度確認しておくのが安全です。

困ったときの最終確認先は次の3つです。

- `llm-task-router --help`
- 各サブコマンドの `--help`
- README

## まとめ

ここまでで、インストールから `init`、`article:create`、`article:evaluate`、改稿指示の確認、`article:revise`、`article:export` までを一周し、最初の `final.md` を出力する流れを追いました。

特に重要なのは次の3点です。

- `runId` は推測せず、実行結果に `runId:` で表示された値をそのまま使う
- `article:create` の内部工程と、`article:evaluate` / `article:re
