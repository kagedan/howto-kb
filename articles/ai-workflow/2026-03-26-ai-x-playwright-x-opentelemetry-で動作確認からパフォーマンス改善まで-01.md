---
id: "2026-03-26-ai-x-playwright-x-opentelemetry-で動作確認からパフォーマンス改善まで-01"
title: "AI x Playwright x OpenTelemetry で動作確認からパフォーマンス改善まで全部やる"
url: "https://zenn.dev/urahiroshi/articles/f54f2bcb945cef"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-03-26"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

Learn4 の [@urahiroshi](https://x.com/urahiroshi) です。

この記事では、個人で開発しているプログラミング学習サービス [Learn4](https://learn4.jp/) において、AIを活用して E2E テストの実装・安定化からデータベースのパフォーマンス自動改善までを一気通貫で実現した取り組みについて記載します。

## 概要

Learn4 は、理解度測定のためのクイズ、AI による課題チェック、Stripe を使ったサブスクリプションなど、さまざまな機能を持つプログラミング学習サービスです。AI を使うことで高速に機能が開発できるようになりましたが、機能を追加すればするほどリグレッションテストの負担が増えていき、開発スピードや品質に影響が出てしまいかねないという問題がありました。

そこで、Claude Code や Cursor を用いて E2E テスト環境を整備し、以下のような開発・テストフローを構築することで、「開発スピードを保ちながら品質を担保する」ことをある程度実現することができました。

## 実現した開発・テストフロー

### 1. 仕様ドキュメントの作成

新しい機能を開発する際に、画面ごとの振る舞いを自然言語でまとめた仕様ドキュメントを作成します。以下に例を記載します。

```
# コース詳細画面 (/play/description/<courseId>)

## 動画表示機能

- コースに動画が設定されていれば動画が表示される
- コースに動画が設定されていなければ動画は表示されない

## 理解度テスト実施機能

### 理解度テストを実施するボタン

理解度テストを実施するボタンの挙動は以下の３通りで分岐します
1. 途中まで実施した理解度テストがある場合
2. 間違った問題が残っている場合
3. 1, 2 に該当しない場合

- 1の場合、モーダルダイアログを表示し、
  「最初から実施する」「前回の続きから実施する」の2つのボタンを表示します
- 2の場合、モーダルダイアログを表示し、
  「すべての問題に回答する」「前回間違えた問題を繰り返す」の2つのボタンを表示します
- 3の場合、コースのクイズ全体を対象としたクイズセットを開始します
```

### 2. 仕様ドキュメントをベースに AI で実装

仕様ドキュメントを AI に読ませ、フロントエンドとバックエンドの実装を行います。このあたりは今回のトピックとあまり関係ないため、詳細は割愛します。

### 3. 動作確認とテスト計画の作成

実装したものをまず自分で動作確認します。それと並行して、[Playwright Test Agent](https://playwright.dev/docs/test-agents) の Planner を使って、テスト計画を作成します (以下例)。

```
# コース詳細画面 (Course Description Screen) E2E Test Plan

## Test Scenarios

### 1. 動画表示機能

**Seed:** `packages/e2e/seed.spec.ts`

#### 1.1. 動画ありコースでは動画が表示される
**File:** `packages/e2e/specs/course-description-screen/video-display-with-video.spec.ts`
**Steps:**
  1. Inject test user: injectTestUser(context)
    - expect: テスト用ユーザーが注入される
  2. Navigate to http://localhost:8081/play/description/<courseId>
     and wait for networkidle
    - expect: page.locator('iframe') is visible (動画がiframeとしてレンダリングされる)

#### 1.2. 動画なしコースでは動画が表示されない
**File:** `packages/e2e/specs/course-description-screen/video-display-without-video.spec.ts`
**Steps:**
  1. Inject test user: injectTestUser(context)
    - expect: テスト用ユーザーが注入される
  2. Navigate to http://localhost:8081/play/description/<courseId>
     and wait for networkidle
    - expect: page.locator('iframe').count() is 0 (動画が表示されない)

### 2. 理解度テスト実施機能

**Seed:** `packages/e2e/seed.spec.ts`

#### 2.1. 「理解度テストを実施する」ボタンで最初のクイズ画面に遷移する
**File:** `packages/e2e/specs/course-description-screen/start-assessment-navigation.spec.ts`
**Steps:**
  1. deleteCourseProgressでDB進捗をリセット、injectTestUserでテスト用ユーザーを注入
    - expect: セットアップ完了
  2. コース詳細画面に遷移し「理解度テストを実施する」ボタンをクリック
    - expect: URL が /play/<courseId>/0 にマッチする

#### 2.2. 途中まで実施した場合、「前回の続きから実施する」と「最初から実施する」のモーダルが表示される
**File:** `packages/e2e/specs/course-description-screen/start-assessment-navigation.spec.ts`
**Steps:**
  1. deleteCourseProgressでリセット後、クイズ開始→Q0回答→×で詳細に戻る→再度「理解度テストを実施する」クリック
    - expect: 「前回の続きから実施する」ボタンが表示される
    - expect: 「最初から実施する」ボタンが表示される

#### 2.3. 全設問回答済みで間違いがある場合、「前回間違えた問題を繰り返す」と「すべての問題に回答する」のモーダルが表示される
**File:** `packages/e2e/specs/course-description-screen/start-assessment-navigation.spec.ts`
**Steps:**
  1. deleteCourseProgressでリセット後、全設問を選択肢1で回答→×で詳細に戻る→再度「理解度テストを実施する」クリック
    - expect: 「前回間違えた問題を繰り返す」ボタンが表示される
    - expect: 「すべての問題に回答する」ボタンが表示される
```

仕様ドキュメントが簡潔に記述されていても、AI がソースコードを参照しながらテストシナリオの詳細を補完してくれます。テスト計画を見て、実行するユースケースが必要十分かを判断します。

### 4. テストコードの生成と安定化

次にテスト計画を AI (Playwright Test Agent の Generator) に渡し、Playwright のテストコードを生成します。ローカル環境でテストを実行し、生成されたテストが安定して通るようになるまで、AI (Playwright Test Agent の Healer) が自律的にテストの実行・調査・修正を繰り返します。

### 5. スクリーンショット付き HTML レポートによる確認

最終的なテスト結果を、全テストのスクリーンショットを掲載した HTML ファイルとして出力します。ブラウザでこの HTML を開くだけで、すべてのテストケースの実行結果を視覚的に一覧で確認できます。テストコードの中身を読まなくても、スクリーンショットを順に眺めるだけで「正しく動いているか」を最小限のコストでチェックできます。

![HTML レポートの例](https://static.zenn.studio/user-upload/b077768debc5-20260326.jpeg)

### 6. OpenTelemetry による API・SQL の記録

E2E テスト実行中にローカルで [Jaeger](https://www.jaegertracing.io/) も起動しており、テスト中に呼び出された API に対応する OpenTelemetry の trace ID を記録できるような仕組みも整えました。trace ID から Jaeger API を通じて「どの API 呼び出し時にどの SQL が呼び出されているか」を収集し、テスト実行後にその一覧情報をファイルに出力します。

### 7. EXPLAIN によるパフォーマンス分析と AI による改善

E2Eテスト実行後、API と SQL の呼び出し情報を読み取り、個々の SQL に対してローカルの PostgreSQL サーバーに対して EXPLAIN を実行するスクリプトを実行し、その結果をファイルに記録します。API に対する SQL の呼び出し情報と EXPLAIN の結果を AI に読み込ませ、「API に N+1 問題などがないか」「インデックスを付与すべきカラムはあるか」といった点を判定させ、必要に応じてコードの修正まで行わせます。その修正結果も再度 E2E テスト実施とその後のEXPLAIN実行で確認できるため、AIが自律的に改善のサイクルを回すことができます。以下がAIが作成したインデックスの改善計画の例です。

```
インデックス追加計画

Context

EXPLAINの結果から、頻繁に実行されるSELECTクエリの多くがSeq Scan（全件走査）を
使用しており、データ量が増えるとパフォーマンスが劣化する。適切なインデックスを追加して、
データ増加時にもIndex Scanが選択されるようにする。

現状分析

既にインデックスが効いているクエリ (対応不要)

- courses: idx_courses_publication_status (publication_statusでの検索)
- answer_histories: answer_histories_pkey (idでの検索)
- course_try_counts: idx_course_try_counts_user_course (user_id, course_idでの検索)
- quizzes: PKインデックス (idでの検索 - 現在はテーブルが小さいためSeq Scanだが、
  PKが存在するのでデータ増加時に自動的に使われる)

Seq Scanが発生しているクエリ (インデックス追加が必要)

追加するインデックス (5個)

1. idx_quiz_histories_quiz_id on quiz_histories(quiz_id)
   - 対象クエリ: 計4クエリ
   - パターン: WHERE quiz_id IN (...) AND archived_at IS NULL
              / ORDER BY quiz_id, created_at DESC
   - 最も頻繁に使われるテーブルの1つ

2. idx_chapters_course_id on chapters(course_id)
   - 対象クエリ: 計2クエリ
   - パターン: WHERE course_id IN (...) AND is_draft = ...

3. idx_chapter_quizzes_chapter_id on chapter_quizzes(chapter_id)
   - 対象クエリ: 計5クエリ
   - パターン: WHERE chapter_id IN (...) ORDER BY order_index
   - 最も頻繁に使われるテーブル

4. idx_quiz_explanations_quiz_histories_id on quiz_explanations(quiz_histories_id)
   - 対象クエリ: 計2クエリ
   - パターン: WHERE quiz_histories_id IN (...)

5. idx_quiz_choice_options_quiz_histories_id on quiz_choice_options(quiz_histories_id)
   - 対象クエリ: 計2クエリ
   - パターン: WHERE quiz_histories_id IN (...) ORDER BY order_index

実装手順

1. schema.tsにインデックス定義を追加
2. マイグレーションファイルを生成: bun run drizzle-kit generate
3. マイグレーションを適用して検証
   - マイグレーション適用後、同じE2Eテストを実行してSQLのEXPLAIN結果を再取得
   - Seq ScanだったクエリがIndex ScanまたはBitmap Index Scanに変わることを確認
```

---

こうした開発・検証フローによって、機能要件だけでなくパフォーマンスの確認とその改善まで AI に一気通貫で行わせることができました。

## 補足: なぜユニットテストではなく E2E テストなのか

今の個人開発では、「リスクが高い箇所や大まかなモジュール設計以外はコードの中身をほとんど見ない」という Vibe Coding の開発スタイルでやっています。AI が書く個々のコードを見ていくと突っ込みたくなるところはありますが、それを一つ一つ修正して得られる保守性・パフォーマンスの向上と、それによる開発スピードの低下はトレードオフです。「開発スピードを最大にしながら、最終的なプロダクトとしての品質はキープする」ことを最大限目指したいという方針もあり、上記のような Vibe Coding のスタイルを選択しました。

一方で AI にユニットテストを書かせると、結局テストを通すだけのためのテストなどを書かれるリスクがあります。しかし、「妥当なテストをしているかどうか」はユニットテストの中身を見なければわかりません。中身を見なければいけないのでは、せっかくメインの実装を Vibe Coding ベースにしていても片手落ちになります。  
そこで、「FrontendとBackendの結合部分も含めてカバーできるE2EテストをAIで実装し、自分は E2E テストの中身を見なくても正しく動いていることが最小限のコストで確認できる」という方向を目指すことにしました。

## 工夫したポイント

以下、こうした開発・検証フローを構築するにあたって工夫したポイントを個別に記載します。

### (1) Playwright Test Agent によるテスト計画・コード生成・安定化

E2E テストの生成と安定化には、[Playwright Test Agent](https://playwright.dev/docs/test-agents) を使っています。Playwright Test Agent は Playwright 公式が提供している AI エージェント統合の仕組みで、以下の 3 つのエージェントで構成されています。

* Planner: アプリケーションを探索し、マークダウン形式のテスト計画を作成します
* Generator: テスト計画を Playwright のテストファイルに変換します。セレクタと検証を実行時に確認しながら、実行可能なテストスイートを生成します
* Healer: テスト実行時に失敗を検出し、UI を検査して同等の要素を特定し、ロケータ更新や待機調整を自動で実施します

私の場合は、初期化で生成されたエージェント定義に対応する Claude Code の Skill を作成し、Planner / Generator / Healer をそれぞれ Skill 経由で呼び出せるようにしています。

特に Healer が便利で、E2E テストが 1 回だけ成功して OK ではなく、何回か実行してすべて成功するまで繰り返し行ってくれます。何か不安定な部分があれば自律的に調査・修正・確認を行ってくれるので、フレーキーなテストの安定化にかかるコストが大幅に減りました。

一方で、「テストを成功させるために 1 秒待つ」とか「要素を選択するために Tailwind のスタイル用クラスを参照している」といった場当たり的な修正をされることも結構ありました。そのあたりは見つけたら都度 Claude Code の Skill に追記しています。以下は Healer のスキルの例です。

```
playwright-test-healer を使い、以下のルールに従ってテストケースを修正してください。

- テストを安定化させるために "1秒待つ" といった場当たり的な修正を行うのではなく、"特定の要素が見えるまで待つ" といったように確実な方法で修正してください。
- テストではなくプロダクトのソースコードのバグが原因と考えられる場合はそれを調査して修正してください。
- 要素を選択する場合、複数の要素で利用されうるスタイル用のセレクターを使って選択するのではなく、アクセシビリティ属性などを使って選択してください。利用できるアクセシビリティ属性がない場合は、ソースコードに属性を追加する修正を行なってください。
```

こうしたルールを蓄積することで、AI が生成するテストコードの品質が徐々に向上していきます。

### (2) テスト用の Injection 設定

「AIがE2Eテストを書きやすい環境にする」という方針を持ち、Frontend/Backendのソースコード上にもE2Eテストを実装しやすくするための機能を入れています。その一部として、テスト用の Injection 設定を紹介します。

#### Auth Injection: 認証のバイパス

Learn4 では Google ログインが必須となっていますが、E2E テストから Google のログイン処理をそのまま実行することはできません。そこで、Auth Injection という仕組みを導入しました。

仕組みはシンプルです。環境変数 `ENABLE_AUTH_INJECTION=true` かつ `NODE_ENV=development` の環境では、`auth-injection` という名前の cookie にメールアドレスを入れておくと、そのメールアドレスに対応するユーザーでログインした状態としてAPIが振る舞うようにします。API の認証ミドルウェアで、通常の JWT 認証の前にこの cookie をチェックし、cookie が存在すればそのメールアドレスでユーザーを検索してセットするという流れです。

E2E テスト側では、Playwright の `addCookies` を使って cookie を設定するだけです。

```
await page.context().addCookies([
  {
    name: 'auth-injection',
    value: 'test-user@learn4.jp',
    domain: 'localhost',
    path: '/',
  },
]);
```

ユーザー新規作成の Endpoint にも同様に環境変数で制御されたテスト用のバイパス機能を実装しており、毎回のテスト実行のたびに API を介してテストユーザーを作成し、そのテストユーザーを使ってテストを行うようにしています。

#### Error Injection: エラーケースのテスト

「API がこのエラーを出した時、画面上でこのエラーメッセージが出るか」といった確認は、E2E テストはもちろん手動でのテストでもやりにくいものです。それを簡単にできるようにするため、Error Injection という機能も入れました。

仕組みとしては、環境変数 `ENABLE_ERROR_INJECTION=true` かつ `NODE_ENV=development` の場合、API リクエストに `error-injection` ヘッダー (もしくは cookie) を付与すると、そのヘッダーの値をエラーコードとして扱い、対応するエラーレスポンスを返すというものです。

```
export const errorInjectionMiddleware = createMiddleware(async (c, next) => {
  if (env.ENABLE_ERROR_INJECTION && env.NODE_ENV === 'development') {
    const errorCode = c.req.header('error-injection');
    if (errorCode) {
      const { response, statusCode } = createErrorResponse(errorCode as ErrorCode);
      return c.json(response, statusCode);
    }
  }
  await next();
});
```

なお、backend ではエラーが発生した場合はエラーコード (`CURRICULUM_STATE_NOT_FOUND` など) を送り、frontend ではそれに対応したエラーメッセージを画面に表示する、という設計にしています。これによって i18n などにも対応しやすく、また上記のような Error Injection の機能も実装しやすいというメリットがありました。

なお、「API 側でこの条件の場合にこのエラーが起きるかどうか」というテストケースは別途必要ですが、それは E2E テストではなく API テストでカバーすべきものです。Error Injection が担うのはあくまで「エラーが返ってきた場合にフロントエンドが正しく表示するか」の確認です。

### (3) テスト結果レポートの表示

E2E テストでは、「画面が期待する状態になったか」を確認するために Playwright の `expect` メソッドが呼び出されます。今回の仕組みでは、すべての `expect` 実行タイミングにおいてスクリーンショットも一緒に取得するラッパーメソッド `expectWithScreenShot` を作成しました。

`expectWithScreenShot` は内部で `expect` の処理実行時にスクリーンショットを取得します。E2E テストの `expect` で確認しているのはあくまで一要素の一部分であるため、実際はそれ以外の箇所で問題が発生しているというケースはよくあります。また、スクリーンショットがあればE2Eテストのコード自体を見ずとも最終的な表示が正しいかというのを人間がすぐに確認できるため、すべての `expect` の処理で機械的にスクリーンショットを撮らせる形式にしました。

なお、こうした `expectWithScreenShot` の呼び出し方や、Auth Injection によるテストユーザーの注入方法は、Playwright Test Agent の seed file を通じて AI に伝えています。seed file とは、テスト環境のセットアップや基本的な動作確認を行うテストファイルで、Planner はこの seed file を実行してアプリケーションの画面を確認しながらテスト計画を作成し、Generator はこの seed file のコードパターンを参考にテストコードを生成します。以下は seed file の例です。

```
import { test } from '@playwright/test';
import { expectWithScreenShot, setCurrentTestName } from './lib/expect-with-screenshot';
import { injectTestUser } from './lib/injection';
import { withRecord } from './lib/with-record';

test.describe('Test group', () => {
  test('seed test', async ({ page, context }, testInfo) => {
    const testName = 'seed-test';
    setCurrentTestName(testName, testInfo.titlePath);

    await withRecord(page, __dirname + '/seed.spec.ts', async () => {
      // auth-injection cookieを設定
      await injectTestUser(context);

      // http://localhost:8081/ を開く
      await page.goto('http://localhost:8081/');

      // SPA描画完了を待つ
      await page.getByTestId('play-home-content').waitFor({ state: 'visible' });
    });

    // 画面が表示されていることを確認
    await expectWithScreenShot(page, async (expect) => {
      await expect(page.locator('body')).toBeVisible();
    });
  });
});
```

このように seed file に `expectWithScreenShot` や `injectTestUser` の使い方を示しておくことで、AI が生成するテストコードでも同じパターンが自然に踏襲されます。

すべての E2E テスト終了後に、各テストケースが生成したスクリーンショットを集約して 1 枚の HTML ファイルを作成します。テスト終了後にこの HTML ファイルを自動的にブラウザで開き、全テストの実行結果を視覚的に確認します。これにより、テストコードの中身を読まなくても、テストケースに対応するスクリーンショットをざっと確認していくだけで「正しく動いているか」を最小限のコストで確認できるようにしました。

なお、取得したスクリーンショットを前回実行時のスクリーンショットと比較することで Visual Regression Test もできそうですが、スクリーンショットが大量にあり、AIのコストや false-positive の運用コストも大きそうなので現時点では行っていません。

### (4) OpenTelemetry との連携によるパフォーマンス分析

E2E テストの実行中に取得した情報を使って、データベースのパフォーマンス分析まで自動で行う仕組みを構築しました。

#### アーキテクチャ

ローカル環境では docker-compose で PostgreSQL と Jaeger を動かしています。

```
services:
  db:
    image: postgres:18
    ports:
      - "${PG_PORT:-5432}:5432"
  jaeger:
    image: jaegertracing/all-in-one:1.76.0
    ports:
      - "16686:16686"  # Jaeger UI
      - "4317:4317"    # OTLP gRPC
      - "4318:4318"    # OTLP HTTP
```

バックエンドでは開発環境のみ OpenTelemetry を起動しています。ORM として Drizzle ORM を利用しており、SQL のトレースには `@kubiks/otel-drizzle` を使っています。

#### trace ID の記録

APIの環境変数が `ENABLE_TRACE_ID_HEADER=true` かつ `NODE_ENV=development` の場合、API のレスポンスに `X-Trace-Id` ヘッダーとして OpenTelemetry の trace ID を出力させるようにしています。E2E テスト側では、各テストケースで呼び出されている API のレスポンスを取得し、APIと trace ID の紐付けを `apis.json` というファイルに記録します。

#### explain コマンドによる分析

npm-scripts に `explain` というコマンドを用意し、以下の処理を実行しています。

まず、Jaeger API を呼び出して、`apis.json` から取得した trace ID を使って対象の trace に紐づく SQL 呼び出しのリストを取得し、API と SQL のマッピングを `sqls.json` に記録します。以下はその出力の一部です。

```
{
  "byPath": {
    "/play/courses": {
      "traceId": "763428c9064ac9cfe441d7beb139d02a",
      "statements": [
        "select \"quiz_id\" from \"quiz_histories\" where ...",
        "select \"id\", \"title\", ... from \"courses\" where ...",
        "select \"chapter_id\", \"quiz_id\", \"order_index\" from \"chapter_quizzes\" where ..."
      ]
    },
    "/play/courses/cff9d485-...": {
      "traceId": "3d20eb7274c2f10aadda2dff7a6d7b1a",
      "statements": [
        "select ... from \"quiz_histories\" where ...",
        "select ... from \"quiz_explanations\" where ...",
        "select ... from \"chapters\" where ..."
      ]
    }
  },
  "allStatements": ["select ...", "select ...", ...]
}
```

次に、個々の SQL に対して EXPLAIN を実行します。ここで一つ工夫が必要でした。トレースで取得できる SQL クエリにはパラメータが入っておらず、`$1`, `$2` のようなプレースホルダーのままです。そこで、`information_schema` からカラムの型情報を取得し、カラムの型に応じた適当なダミー値 (uuid なら `'00000000-0000-0000-0000-000000000000'`、text なら `'dummy'` など) を埋めるような処理を施した上で EXPLAIN を実行するようなスクリプトを作成しました。あまり筋が良くないなと思いつつ、AI を使うとこういったパワープレイもできるのがいいですね。

EXPLAIN の結果は `indexes.json` というファイルに出力します。以下はその出力の一部です。

```
{
  "results": [
    {
      "sql": "select \"quiz_id\" from \"quiz_histories\" where ...",
      "explainOutput": "Seq Scan on quiz_histories  (cost=0.03..5.53 ...)\n  Filter: ...",
      "usesIndex": false,
      "error": null
    },
    {
      "sql": "select ... from \"courses\" where \"courses\".\"publication_status\" = 'dummy' ...",
      "explainOutput": "...Index Scan using idx_courses_publication_status on courses...",
      "usesIndex": true,
      "error": null
    }
  ]
}
```

#### AI による改善提案と実行

`sqls.json` や `indexes.json` を AI に読み込ませ、パフォーマンス観点の改善計画を提案させます。以下のような SKILL で、E2Eテストから一気通貫で実行できるようにしています。

```
e2eパッケージ内で `bun run test:explain` を実行し、テストが成功した場合に出力された indexes.json, sqls.json を確認してください。
これらのファイルには、API呼び出し時に呼び出されるSQLやインデックスの有無が書いてあるため、この内容やソースコードを分析して、以下のようにパフォーマンスが改善できる箇所を調査してください。

- N+1問題などで無駄にクエリを呼び出しているような箇所がないか
- インデックスを付与した方が良い箇所がないか
- デッドロックやロックに起因するパフォーマンスの問題を生じうる箇所がないか
```

#### 補足: 開発環境での EXPLAIN の限界

EXPLAIN の結果はレコードの数などにも左右されるため、開発環境で EXPLAIN するよりも本番環境の Query Insight などを使った方がより実態に即した情報が得られます。それを理解した上で、それでも本番にリリースする前に大まかなパフォーマンスリスクの検知と修正確認を行いたいというモチベーションから、開発環境での EXPLAIN を実行しています。開発環境ではデータ量が少ないため、本番では Index Scan が選ばれるクエリでも Seq Scan になったりすることがある点はご留意ください。

## 最後に

私はこれまでエンジニアとしてプロダクトのE2Eテストを実装・メンテナンスすることもしばしばあったのですが、E2Eテストはユニットテストに比べるとかなり不安定で1回の実行時間も長いため、AI以前では実装・運用コストが非常に高いものでした。そのため、E2Eテストが生じるメリットに対して労力が釣り合っていないと感じるケースが多かったのですが、今の時代にAIを使ってその状況がどれだけ変えられるかを試したいというモチベーションもありました。

結果として、AIを使うことでE2Eテストの実装・安定化をするためのコストが格段に下がったことが実感でき、こうしたプラクティスがより広まってほしいという気持ちから今回の記事を執筆したものです。参考になった部分があればぜひ活用ください！

また、個人として開発している [Learn4](https://learn4.jp/) のプロダクトを応援いただけると嬉しいです。開発プラクティスやアップデートなどは適宜 [X のアカウント](https://x.com/urahiroshi) を中心に発信していきますので、フォローいただければ励みになります！
