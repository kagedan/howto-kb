---
id: "2026-06-17-llm-task-router-薄い-modelrouter-で記事生成ワークフローを回す-01"
title: "llm-task-router: 薄い ModelRouter で記事生成ワークフローを回す"
url: "https://qiita.com/rex0220/items/f501b9983f26e4434eeb"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "LLM", "OpenAI", "GPT", "TypeScript"]
date_published: "2026-06-17"
date_collected: "2026-06-18"
summary_by: "auto-rss"
query: ""
---

ChatGPT や Claude に大きなプロンプトを 1 回投げて記事を書かせる方法は手軽です。ですが、実際に運用してみると、構成・執筆・レビュー・改稿の責務が 1 つの出力に混ざりやすく、再実行や部分修正、モデル切り替えが難しくなりがちです。

この記事では、記事生成を `brief → outline → draft → review → final` のような小さなタスクに分解し、タスクごとに適したモデルへルーティングする TypeScript CLI `llm-task-router` を紹介します。インストールから最初の記事生成、レビュー・改稿・評価の違い、Qiita / Zenn / blog / note の切り替え、設計上のこだわりまでを、MVP としての現実的な使いどころに絞って整理します。

:::note info
本記事の内容は、執筆時点の `llm-task-router` の挙動を前提にしています。MVP 段階のツールは CLI オプション、出力ファイル名、runId の生成規則などが今後変わる可能性があります。実際に使う際は `--help`、README、パッケージのリリースノートをあわせて確認してください。
:::

:::note info
本記事は、Claude Code + llm-task-router で作成しました。
:::

## 0. 対象バージョンと参照先

再現性のため、まず前提を明記します。

- 対象パッケージ: `@rex0220/llm-task-router`
- 確認対象: `npm view @rex0220/llm-task-router version` で取得できる公開版
- 参照先:
  - npm: `https://www.npmjs.com/package/@rex0220/llm-task-router`
  - リポジトリ / README: パッケージページから参照

手元では、まず次の 3 つを確認しておくと安全です。

```bash
npm view @rex0220/llm-task-router version
npx @rex0220/llm-task-router --help
npx @rex0220/llm-task-router article:create --help
```

たとえば `--help` を見ると、少なくとも `article:create` / `article:review` / `article:resume` / `article:revise` / `article:evaluate` / `article:export` といったサブコマンドの存在を自分の環境で確認できます。

:::note info
この記事では README / `--help` / 実行結果をもとに、現バージョンの挙動として説明しています。将来の変更可能性はありますが、本文中では「現時点の仕様」として書きます。
:::

## 1. 単発プロンプトの限界と、ステップを分けたくなった理由

ChatGPT や Claude に「この記事を書いて」と単発で依頼する運用は、最初の体験としてはとても良いです。短時間で、それらしいアウトプットが返ってきます。

ただ、少し本気で使い始めると限界が見えてきます。

長い 1 本のプロンプトに責務を詰め込むと、次のようなものが混ざりやすくなります。

- 何を書くかの整理
- 読者像や前提の定義
- 見出し構成の設計
- 本文の執筆
- 技術レビュー
- 言い回しの調整
- 最終チェック

この状態だと、出力が微妙だったときに「何が悪かったのか」を切り分けにくくなります。構成が悪いのか、ドラフトが雑なのか、レビューが弱いのかが見えません。

さらに、部分修正もしづらいです。

たとえば「構成だけやり直したい」「レビューだけ別モデルにしたい」と思っても、単発運用ではまた全体を投げ直しがちです。

記事生成を workflow として扱うなら、やはりステップを分けた方が観察しやすいです。`brief / outline / draft / review / final` のように分けておけば、

- どこで品質が落ちたか見やすい
- 途中成果物を残せる
- 部分再実行しやすい
- タスクごとにモデルを変えられる

という利点があります。

`llm-task-router` は、全自動で完成品を出すことよりも、**人が介入しやすい中間成果物を残すこと**を優先しています。

:::note info
このツールは現状 MVP 段階です。万能な自動執筆器というより、実務向けの下敷きを整える CLI として捉えるのがちょうどよいです。
:::

## 2. llm-task-router とは: 薄い ModelRouter という発想

`llm-task-router` は、複数の LLM プロバイダをタスク単位で切り替えながら記事生成を進める TypeScript CLI です。

ポイントは「薄い ModelRouter」という立ち位置です。

ここでいう「薄い」とは、重いオーケストレーション基盤や複雑なエージェントシステムを作るのではなく、

- 各ステップを明示する
- タスク名を固定する
- モデル選択を設定ファイルに寄せる
- CLI とファイル出力で観察可能にする

という設計を指します。

### 進捗表示名・内部タスク名・コマンドの対応

進捗表示のラベル、内部タスク名、コマンド上の役割を 1 つの表にすると次のようになります。

| 進捗表示名 | 内部タスク名 | 主に使われるコマンド | 役割 |
| --- | --- | --- | --- |
| `brief` | `article_brief` | `article:create` | 記事の狙い・読者・方針を固める |
| `outline` | `outline` | `article:create` | 見出し構成を作る |
| `draft` | `draft_markdown` | `article:create` | Markdown の下書きを作る |
| `review` | `technical_review` | `article:create`, `article:review` | 技術的なレビューを行う |
| `final` | `rewrite` | `article:create`, `article:resume`, `article:revise` | レビュー結果を反映して最終稿を書く |
| `-` | `final_review` | `article:evaluate` | `final.md` を評価する |

ここで特に紛らわしいのが `final` と `final_review` です。

- 進捗表示の `final` は、**最終稿を書き直す `rewrite` タスク**
- `final_review` は、**最終稿を審査する評価専用タスク**

であり、別物です。

この設計の良いところは、モデル選択・フォールバック・温度・最大トークン数をコードではなく `config/models.yaml` で管理できることです。

たとえば構造は次のようになります。

```yaml
providers:
  openai:
    api_key_env: OPENAI_API_KEY
  anthropic:
    api_key_env: ANTHROPIC_API_KEY

prices:
  openai:
    example-openai-model:
      input_usd_per_1m_tokens: 0.40
      output_usd_per_1m_tokens: 1.60
  anthropic:
    example-anthropic-model:
      input_usd_per_1m_tokens: 3.00
      output_usd_per_1m_tokens: 15.00

tasks:
  article_brief:
    primary:
      provider: openai
      model: example-openai-model
    fallback:
      - provider: anthropic
        model: example-anthropic-model
    temperature: 0.3
    max_tokens: 2000

  outline:
    primary:
      provider: anthropic
      model: example-anthropic-model
    temperature: 0.4
    max_tokens: 3000

  draft_markdown:
    primary:
      provider: anthropic
      model: example-anthropic-model
    fallback:
      - provider: openai
        model: example-openai-model
    temperature: 0.5
    max_tokens: 6000

  technical_review:
    primary:
      provider: openai
      model: example-openai-model
    temperature: 0.2
    max_tokens: 2500

  rewrite:
    primary:
      provider: anthropic
      model: example-anthropic-model
    temperature: 0.4
    max_tokens: 6000

  final_review:
    primary:
      provider: openai
      model: example-openai-model
    temperature: 0.1
    max_tokens: 2500
```

このようにしておくと、「構成は A モデルが得意」「レビューは B モデルにしたい」といった切り替えが設定変更だけで済みます。

### 既存のオーケストレーション基盤とどう違うか

ここでいう「薄い」は、単に機能が少ないという意味ではありません。意図的に責務を絞っています。

たとえば LangChain や LlamaIndex のような基盤は、エージェント、ツール呼び出し、メモリ、外部データ連携などを含む広い問題を扱えます。一方で、記事生成のように

- ステップが比較的固定されている
- 途中成果物をファイルで残したい
- 人手レビューを前提にしたい
- モデル切り替えを設定だけで済ませたい

という用途では、もっと薄い CLI の方が扱いやすい場面があります。

`llm-task-router` は、汎用エージェント基盤を目指すのではなく、**記事生成という狭いユースケースに絞って、再現性と観察性を優先する**設計です。

## 3. インストールと初期セットアップ

使い始める前に、まず Node.js 環境を用意します。

現バージョンを使う前提では、**`package.json` の `engines` に書かれている最小バージョン以上**を使ってください。実際の値は次で確認できます。

```bash
npm view @rex0220/llm-task-router engines
```

現バージョンの `engines.node` は `>=20` なので、**Node.js 20 以上**を使ってください。曖昧に「最近の LTS」を選ぶより、パッケージ定義に合わせる方が安全です。

まずはバージョンを確認します。

```bash
node -v
npm -v
```

環境差で詰まりやすい場合は、`nvm` などで Node.js を管理しておくと楽です。

グローバルインストールの最小手順は次の通りです。

```bash
npm install -g @rex0220/llm-task-router

# init で config/ と .env.example が生成される
llm-task-router init

cp .env.example .env
```

グローバルインストールを避けたい場合は、`npx` で試す形でも始められます。

```bash
npx @rex0220/llm-task-router init
```

インストール後の実行コマンド名は `llm-task-router` です。

`llm-task-router init` を実行すると、現在のディレクトリに `config/` と `.env.example` がコピーされます。その後、`.env.example` を元に `.env` を作成し、利用するプロバイダの API キーを設定します。

CLI は現在ディレクトリ基準で以下を読み込みます。

- `config/models.yaml`
- `config/profiles/`
- `config/criteria/`
- `.env`

出力先は `runs/` です。

`config/models.yaml` では、主に次の 3 つを定義します。

- `providers`
- `prices`
- `tasks`

特に `providers` では `api_key_env` というキー名を使います。環境変数名をここに寄せておくことで、コード側に秘密情報の扱いを持ち込みにくくしています。

:::note warn
サンプル設定に入っているモデル ID や価格は、**執筆時点の例**として扱ってください。モデル名は廃止・改名されることがあり、価格も更新されます。実運用では各プロバイダの公式ドキュメントや pricing ページで最新のモデル ID / 料金を確認してから `config/models.yaml` を編集するのが安全です。
:::

## 4. 最初の記事を作る: `article:create` と `runs/` の見方

最初の 1 本を作るには `article:create` を使います。

```bash
llm-task-router article:create --topic "AIが解釈しやすい中間言語を設計する"
```

`--topic` と `--topic-file` は**どちらか一方が必須**です。両方指定するとエラーになり、両方とも省略してもエラーになります（暗黙のデフォルトや対話プロンプトはありません）。

デフォルトの `--profile` は `qiita` です。必要に応じて `zenn` / `blog` / `note` に切り替えられます。

```bash
llm-task-router article:create \
  --topic "AIが解釈しやすい中間言語を設計する" \
  --profile zenn
```

### `runId` の生成規則

`--topic-file` を使う場合、`runId` は**実行日 + 入力ファイルのベース名**で生成されます。

たとえば入力が `ai-ir.txt` なら、

- ベース名: `ai-ir`
- 実行日: `2026-06-16`

を組み合わせて、`runId` は `2026-06-16-ai-ir` になります。

つまり規則は次の通りです。

- 日付部分は**実行時点の日付**
- 末尾部分は**拡張子を除いたファイル名**
- 保存先は `runs/<runId>/`

一方、`--topic`（インライン）を使う場合は、**トピック文字列そのものを slug 化**して末尾に使います。具体的には、小文字化したうえで英数字以外を `-` にまとめ、先頭・末尾の `-` を除き、先頭 40 文字に切り詰めます。

ここで注意したいのが、英数字以外がすべて `-` に潰れる点です。たとえば日本語だけのトピック（例: `--topic "AIが解釈しやすい中間言語を設計する"`）では slug がほぼ空になり、`runId` は `2026-06-16-article` のように末尾が `article` というフォールバック名になります。

そのため、`--topic` で日付以外も意味のある `runId` にしたいときは、次のいずれかが確実です。

- `--run <runId>` で明示的に指定する
- `--topic-file` を使ってファイル名で制御する

いずれの場合も、実際に生成された `runId` は標準出力と `meta.json` の `runId` で確認できます。

生成結果は `runs/<runId>/` に保存されます。典型的には次のような構成です。

- `brief.json`
- `outline.json`
- `draft.md`
- `review.json`
- `final.md`
- `meta.json`

この構成が便利なのは、各ステップの成果物を後から見返せることです。

「最終稿が微妙だった」ときでも、`outline.json` や `review.json` を確認すれば、どの段階でズレたか追いやすくなります。

`meta.json` には次のようなメタ情報が記録されます。

- `runId`
- `topic`
- `platform`
- `style`
- `profile`
- `steps`

また、実行時の表示も実務向けです。

- 進捗は `stderr`
- `runId` と `final` のパスは `stdout`

に出力されます。各ステップは開始時に `[i/N] <表示名> (<タスク名>) ...` を出し、完了時に実際に使われた `provider/model`・経過時間（ms）・推定コストを出します。最後に合計概算も出ます。

つまり、**パイプ処理しやすい標準出力**と、**人が読むための進捗表示**が分けられています。

進捗イメージは次のような形です（値はダミー）。

```text
[1/5] brief (article_brief) ...
[1/5] brief - done via openai/example-openai-model (2310ms, ~$0.0123)
[2/5] outline (outline) ...
[2/5] outline - done via anthropic/example-anthropic-model (4120ms, ~$0.0456)
[3/5] draft (draft_markdown) ...
[3/5] draft - done via anthropic/example-anthropic-model (9700ms, ~$0.0410)
[4/5] review (technical_review) ...
[4/5] review - done via openai/example-openai-model (2300ms, ~$0.0025)
[5/5] final (rewrite) ...
[5/5] final - done via anthropic/example-anthropic-model (5100ms, ~$0.0180)
total: ~$0.1194 (estimate)
```

:::note info
コスト表示はローカル概算です。表示の整形や桁揃えはランタイムや将来の実装変更で多少変わる可能性がありますが、概ね「タスク名 / モデル / 経過時間 / 概算コスト」が並ぶイメージです。
:::

出力ファイルのイメージも 1 つ載せておくと掴みやすいです。たとえば `runs/<runId>/final.md` には、次のような Markdown 本文が保存されます。

~~~md
# AIが解釈しやすい中間言語を設計する

## 背景

LLM に複雑な処理を任せるとき、自然言語だけでは曖昧さが残ります。

## 中間言語を挟む理由

- 命令の構造を固定できる
- 入出力の検証がしやすい
- モデル差を吸収しやすい

## 例

```json
{
  "intent": "summarize",
  "constraints": ["keep technical terms", "max 200 words"]
}
```

...
~~~

## 5. レビュー・改稿・評価をどう使い分けるか

`review`、`revise`、`evaluate` は名前が似ていますが、役割はかなり違います。

ここを分けて理解しておくと運用しやすくなります。

### `article:review`

自動レビューを再実行したいときに使います。

```bash
llm-task-router article:review --run 2026-06-16-example
```

ここで渡す `--run` は**パスではなく runId** です。

たとえば `runs/2026-06-16-example/` を直接指定するのではなく、`2026-06-16-example` を渡します。

### `article:resume`

`article:resume` は、中断した run を途中から再開したいときのコマンドです。`review` の再実行とは別概念です。

```bash
llm-task-router article:resume --run 2026-06-16-example
```

長い生成処理が途中で止まった場合に、既存の成果物を使いながら再開できる設計だと、試行回数が多い運用でかなり助かります。

### `article:revise`

`article:revise` は、自由記述の指示で `final.md` を書き換えるコマンドです。

- `--instruction`
- `--instruction-file`

のどちらかを使います。

たとえば「導入を短くする」「Qiita 向けに箇条書きを増やす」「比較表を追加する」といった指示を与えて、最終稿を再生成できます。

### `article:evaluate`

評価は、レビューや改稿とは別の役割です。

```bash
llm-task-router article:evaluate --run 2026-06-16-example --min-severity major
```

このコマンドは `final.md` を**別の審査モデル**で採点し、問題点の洗い出しと改稿指示ドラフトを生成します。内部的には `final_review` タスクを使います。

出力ファイル名は次の通りです。

- `final-review.json`
- `final-review.md`
- `revise-instruction.md`

ここは少し大事で、`evaluate.json` のような名前ではありません。

設計上の重要点は、**自動改稿を即適用しない**ことです。まず `article:evaluate` で改稿指示ドラフトを出し、人がそれをレビューしたうえで、必要なら `article:revise` に渡す流れになっています。

これは LLM-as-judge を過信しないためです。評価モデルは便利ですが、絶対的な審判ではありません。最終判断は人が持つ前提で運用するのが安全です。

:::note info
公開前チェックの標準フローは `create → evaluate → revise → export` です。`article:create` の中で `technical_review → rewrite`（draft のレビューと最終稿づくり）まで自動で走るので、`create` 直後に `article:review` を別途回す必要はありません。`article:review` は「draft から自動レビューと rewrite をやり直したいとき」だけ使う補助コマンドだと捉えると分かりやすいです。特に公開前チェックでは、評価結果から生成された `revise-instruction.md` を人が読んでから反映する運用が扱いやすいです。
:::

## 6. プロファイルで Qiita / Zenn / blog / note を切り替える

`llm-task-router` は、同じワークフローを保ちながら、出力先ごとの文体や評価観点を切り替えられます。

プロファイルは `config/profiles/<name>.yaml` という**個別ファイル**で管理します。1 つの YAML に profiles をまとめる形ではありません。

最小例はこんなイメージです。

```yaml
platform: Qiita
language: ja
criteria_file: config/criteria/default.md
style: |
  Qiita の作法に従う。本文は Markdown。
  - コードブロックは言語指定つきのフェンスを使う。
  - 補足や注意は `:::note info` / `:::note warn` の記法を使ってよい。
  - 記事先頭の front-matter は本文に含めない。
```

`style` は単なるラベルではなく、`|` の複数行ブロックで「そのプラットフォームの作法」を具体的に書きます。ここに書いた内容が draft / final / revise の本文生成プロンプトへ注入されるため、媒体差分をプロンプトにベタ書きせず profile 側に寄せられるのがこのツールの強みです。

各プロファイルファイルは次のキーを持ちます。

- `platform`
- `language`
- `style`
- `criteria_file`

これにより、同じトピックでも

- Qiita 向け
- Zenn 向け
- ブログ向け
- note 向け

で作法や評価基準を差し替えられます。

CLI 側は共通ワークフローを維持しつつ、出力先プラットフォームの文体や観点だけを設定で切り替える構造です。

この方式の良さは、毎回プロンプトをコピペして「今回は Qiita 風で」「今度は Zenn 風で」と調整しなくてよいことです。**プロファイルとして外出しする**ことで、再利用しやすくなります。

たとえば、Qiita では手順重視、Zenn では説明の流れ重視、blog では背景説明を厚め、note では柔らかめの文体、といった差分をファイルで持てます。

### `article:export`

生成した `final.md` を別の場所へ持ち出したいときは `article:export` を使います。

```bash
llm-task-router article:export \
  --run 2026-06-16-example \
  --out ../zenn-content/articles/my.md
```

公開用リポジトリや CMS 用ディレクトリへ最終稿を移す用途を想定するとわかりやすいです。

## 7. 設計上こだわった点: ルーティング・ガード・コスト・セキュリティ

MVP でも実務投入しやすくするために、派手な機能より事故りやすい部分への手当てが優先されています。

### タスクごとのルーティングとフォールバック

タスクごとに得意なモデルを割り当て、失敗時には `fallback` を使える構造です。これにより、品質・コスト・可用性のバランスを取りやすくなります。

たとえば、

- 構成は思考の安定したモデル
- 下書きは長文生成が得意なモデル
- レビューは厳しめのモデル
- 評価は別系統のモデル

といった使い分けができます。

### ローカルなコスト概算

`config/models.yaml` の `prices` を使い、応答の usage トークン数からコストをローカル概算します。追加 API 呼び出しなしで見積もれるのが利点です。

これにより、「このワークフローは 1 本あたりだいたいいくらか」を把握しやすくなります。

:::note warn
ここで出る金額はあくまでローカル概算です。プロバイダ側の請求単位、丸め、キャッシュ、モデル更新、料金改定とは一致しないことがあります。予算管理用途では、最終的に各プロバイダの利用明細も確認してください。
:::

### 出力ガード

地味ですが重要なのが出力ガードです。

- draft / rewrite / revise では、**本文全体を 1 つのコードフェンスで包んで返したケースだけ**外側のフェンスを除去する
- `max_tokens` 打ち切りの可能性があるときは ⚠ 警告
- 「以下が記事です」「以上です」のようなメタ前置き/結び文を検出

といった対策が入っています。

特に、Markdown 本文を期待しているのに、モデルが全体をコードフェンスで包んで返すのはよくある事故です。そこを自動で軽減しています。

重要なのは、**本文中の正当なコードブロックは保持する**ことです。除去対象は、あくまで文書全体を丸ごと囲んでしまったラップ用フェンスです。

一方で、メタ前置きや結びのラップ文は検出しても**自動修正ではなく警告のみ**です。ここは過剰補正を避けるための判断です。

### セキュリティ方針

セキュリティ面では、MVP らしく守備範囲を絞っています。

- CLI のみ
- HTTP API を公開しない
- 任意 URL を取得しない
- ログにキーを残さない
- SDK の生レスポンスを残さない
- 入力全文をログに残さない

機能を増やしすぎるより、事故りやすい部分に先に手当てしている設計です。

:::note info
派手な自律エージェント感はありませんが、そのぶん「普段の執筆フローに静かに入れやすい」タイプの道具です。
:::

## 8. まとめ

`llm-task-router` の価値は、「複数モデルを使えること」そのものより、**記事生成を観察可能なステップに分解したこと**にあります。

単発プロンプト運用から一歩進めて、

- 再実行しやすい
- 比較しやすい
- レビューしやすい
- 評価しやすい

というワークフローに移行できるのが強みです。

最初は次の流れを手元で試すと、設計意図がかなり掴みやすいはずです。

1. `init`
2. `article:create`
3. `article:evaluate`
4. `article:revise`
5. `article:export`

必要に応じて、中断時は `article:resume`、draft からレビュー・rewrite をやり直したいときは `article:review` を使います。

現状は MVP なので、今後はより良いプロファイル、評価基準、運用知見を育てていく段階だと思います。

`llm-task-router` は、記事を一発で完成させるための魔法の CLI ではありません。その代わり、`brief`・`outline`・`draft`・`review`・`final` という段階を明示し、タスクごとにモデルを切り替えながら、人がレビューしやすい形で成果物を残せます。

単発プロンプトの限界を感じているなら、まずは最小構成で導入し、Qiita や Zenn 向けのプロファイルを切り替えながら、自分の執筆ワークフローにどう馴染むかを試してみると、このツールの狙いが見えてくるはずです。
