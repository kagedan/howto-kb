---
id: "2026-03-24-mastra-で作る-aiエージェント13-可観測性observabilityでaiエージェントの動-01"
title: "Mastra で作る AIエージェント(13) 可観測性（Observability）でAIエージェントの動きの中身を覗く"
url: "https://zenn.dev/shiromizuj/articles/71866dccab1931"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-03-24"
date_collected: "2026-03-25"
summary_by: "auto-rss"
---

[Mastra で作るAI エージェント](https://zenn.dev/shiromizuj/articles/a0a1659e9f05b6) というシリーズの第13回です。

---

本シリーズでは、AIエージェントを三国志になぞらえて理解し、

![](https://static.zenn.studio/user-upload/f590eabc3cad-20260302.png)

エージェントを複数並べるマルチエージェントの１つ目としてワークフローを確認し、

![](https://static.zenn.studio/user-upload/e4d6ae5da34f-20260209.png)

マルチエージェントの２つ目としてエージェント・スーパーバイザーを確認しました。

![](https://static.zenn.studio/user-upload/3bec084386cd-20260209.png)

このように、まずは「やりたいことを実現する」「動くものを作る」ということを重視して連載を進めてきましたが、[前回](https://zenn.dev/shiromizuj/articles/e1e0717a663845)から「よりよく動かす」という応用問題に軸足が移ってきました。

今回のテーマは**可観測性**（**Observability**）。以下に示したGoogleトレンドのグラフの通り、AIエージェント元年と呼ばれる2025年になって急上昇した重要ワードです。いわゆる従来のシステム開発における「ログ記録」「デバッグ」に近い概念で、「**よりよく動かす**」**ための第一歩**です。そして、AIエージェント特有の「見えにくさ」が、このワードの注目度を上げた理由になっています。

![](https://static.zenn.studio/user-upload/99eb5bb75399-20260320.png)

# なぜ AIエージェントは「見えにくい」のか

**ケース1**  
AIエージェントを本番環境にリリース後しばらくが経ったころ。上司から突然「**最近コストが高くない？**」と言われた。調べると先月比で**LLMの請求額が3倍**になっている。どのリクエストが原因か、なぜトークンが増えたのかを調べようとするが、手元には「**エラーなく完了した**」というログしかない。

**ケース2**  
ユーザーから「エージェントが明らかに**的外れな回答**を返してくる」という苦情が届いた。再現を試みるが、問題の会話ログもなく、「どのツールが呼ばれたか」「LLMがどう判断したか」の**糸口すらつかめない**。

**ケース3**  
開発フェーズで精度向上に取り組んでいる。プロンプトを変えたら良くなりました、と報告したが「**本当にそう？　定量的に言える？**」と問われた。直感ではなく定量的に比べたい。

こういった場面がAIエージェントを開発・運用する現場では繰り返し訪れます。そしてたいていは「**情報が足りない**」という壁に突き当たるのです。

## 問題は AIエージェントの構造にある

従来のWebアプリケーションであれば、ある程度の経験のある開発者はログを見ながら問題を追うことができました。「このAPIが呼ばれた」「このDBクエリに200msかかった」「ここでエラーが発生した」という情報を積み上げると、問題の輪郭が見えてきます。

AIエージェントはそうではありません。一回の「ユーザーの質問に答える」という処理の中で、LLMへの問い合わせが複数回走り、そのたびにLLMが「次に何をすべきか」を判断し、ツールを呼び出し、その結果を踏まえてまた考え、最終的に回答を返します。さらにワークフローが絡むと、複数のエージェントが並列または直列に動き、お互いの出力を入力として受け取ります。

この構造は**ツリー状、あるいはグラフ状**になっており、**一本の線ではありません**。従来の「リクエストが来て、処理して、レスポンスを返す」という直線的な流れとは本質的に異なります。`console.log` を数行仕込んだだけでは、このツリー構造の全体像は見えません。

## Observability が必要になる場面

Observability（可観測性）が必要になる場面は、開発フェーズと本番運用フェーズの両方にわたります。

**開発中** は、「実装が意図通りに動いているか」を確かめる場面が何度もあります。プロンプトを調整するとLLMの判断経路がどう変わるか。ツールの引数が正しく渡されているか。RAGで取得した文書が実際に使われているか。これらは動作確認の域を超えており、実行の**証跡**として記録することが不可欠です。また、プロンプトの変更やアーキテクチャの改善効果を「変更前後の数字」で示せることも重要です。

**本番運用中** は別の緊張感があります。**コストの急増**、**応答速度の劣化**、特定の入力パターンでの**エラー**、夜間バッチの**失敗**——これらの**原因**を「後から遡って調べる」ためには、起きた瞬間の実行記録が必要です。問題が起きてから計測を始めようとしても遅いのです。

観点で分けると、**機能性**の問題（「おかしな回答を返している」）、**コスト**の問題（「トークンを使いすぎている」）、**性能**の問題（「どのステップがボトルネックか」）、**エラー**の問題（「どのツール呼び出しが失敗しているか」）と、それぞれまったく異なる情報が必要です。

目的で分けると、インシデント発生時の事後**解析**、日次・月次の**統計調査**、A/Bテストやプロンプト改善の**効果測定**、監査や品質保証のための**証跡取得**と、多岐にわたります。

観測したい対象もさまざまです。ユーザーへの**入力**とLLMからの**出力**、各LLM呼び出しの**トークン数**（promptTokens / completionTokens）、各処理ステップの**実行時間**、ツール呼び出しの**順序・引数・戻り値**、ワークフローの**分岐やループの経路**——これら全部がそろって初めて「エージェントが何をしたか」が分かります。

## Mastra の回答：Logging と Tracing の2本柱

Mastra はこうした Observability のニーズに対して、2つの仕組みを提供しています。

**Logging** は「何が起きているか」をテキストとして記録します。ワークフローのステップが完了した、ツールが特定の入力を受け取ったといった情報をログとして出力します。**シンプルで軽量**ですが、AIエージェントの**階層構造を表現するには限界**があります。

**Tracing** はその限界を埋めるものです。エージェントの実行を**スパン（処理単位）の木構造として記録**します。「ワークフローがエージェントを呼び、エージェントがLLMを呼び、LLMがツールを呼んだ」という**親子関係**が可視化され、それぞれの入出力・トークン数・実行時間が記録されます。これは**OpenTelemetryという標準規格**をベースにしており、外部の監視ツールとも連携できます。

どちらか一方ではなく、両方を組み合わせることで、AIエージェントを多角的に観察できます。

---

# Logging：まず「何が起きているか」を記録する

Logging は、Mastra のすべてのコンポーネント（ワークフロー・ツール・エージェント）から利用できる構造化ログの仕組みです。

## PinoLogger のセットアップ

Mastra CLI でプロジェクトを生成すると、`PinoLogger` が初期設定として含まれています。`@mastra/loggers` パッケージが必要です。

```
// src/mastra/index.ts
import { Mastra } from '@mastra/core/mastra';
import { PinoLogger } from '@mastra/loggers';

export const mastra = new Mastra({
  logger: new PinoLogger({
    name: 'Mastra',
    level: 'info',
  }),
});
```

`level` には `debug`・`info`・`warn`・`error` が指定できます。開発中は `debug` にしておくと詳細が見えますが、本番では `info` 以上に絞るのが一般的です。

Logger を設定しない場合、Mastra Studio と Mastra Cloud の「Logs」タブには何も表示されません。Tracing（後述）とは独立した機能なので、片方だけ設定することも可能ですが、両方設定しておくのが基本です。

## ワークフローステップからログを出す

ワークフローのステップ内では、`execute` 関数の引数として渡される `mastra` オブジェクト経由でロガーを取得します。

```
// src/mastra/workflows/my-workflow.ts
import { createWorkflow, createStep } from '@mastra/core/workflows';

const step1 = createStep({
  execute: async ({ mastra }) => {
    const logger = mastra.getLogger();
    logger.info('ステップ1を開始しました');

    // 追加データを第2引数で渡すこともできる
    const agent = mastra.getAgent('myAgent');
    logger.info('エージェントを取得しました', { agent });

    return { output: '' };
  },
});
```

## ツールからログを出す

ツールでは `execute` 関数の第2引数 `context` 経由でロガーを取得します。

```
// src/mastra/tools/my-tool.ts
import { createTool } from '@mastra/core/tools';
import { z } from 'zod';

export const myTool = createTool({
  execute: async (inputData, context) => {
    const logger = context?.mastra.getLogger();
    logger?.info('ツールを実行します', { input: inputData });

    // ... 処理 ...

    logger?.info('ツールの実行が完了しました');
    return { output: '' };
  },
});
```

---

# Tracing：AIエージェントの実行を「丸裸」にする

Tracing は Logging とは別パッケージとして提供されており、別途インストールが必要です。エージェントやワークフローの実行をスパンの**階層構造として記録**し、LLMの**トークン使用量**・**ツール呼び出しの詳細**・**各処理の実行時間**を可視化します。

Tracing を設定しない場合、Mastra Studio の「Traces」タブは空になります。トークン使用量やツール実行の詳細は一切記録されません。

## 自動で記録されるもの

Tracing を有効にすると、Mastra は以下の情報を自動でインストルメンテーション（計装）します。**追加のコードは不要**です。

エージェントに関しては、エージェントの実行（instructions・使用ツール一覧）・LLMへの呼び出し（モデル名・プロバイダー・promptTokens・completionTokens・totalTokens）・ツール実行（ツール名・入力パラメータ・出力・実行時間）・メモリ操作（スレッドの読み書き・セマンティック検索）が記録されます。

ワークフローに関しては、ワークフロー全体の実行・各ステップの入出力・条件分岐やループの経路・並列実行の状況が記録されます。

## セットアップ

まずパッケージをインストールします。

```
npm install @mastra/observability
```

ストレージの設定も必須です。トレースデータの保存先として `LibSQLStore`（ローカル）または PostgreSQL が必要です。

```
// src/mastra/index.ts
import { Mastra } from '@mastra/core';
import { PinoLogger } from '@mastra/loggers';
import { LibSQLStore } from '@mastra/libsql';
import {
  Observability,
  DefaultExporter,
  CloudExporter,
  SensitiveDataFilter,
} from '@mastra/observability';

export const mastra = new Mastra({
  logger: new PinoLogger({ name: 'Mastra', level: 'info' }),
  storage: new LibSQLStore({
    id: 'mastra-storage',
    url: 'file:./mastra.db', // ローカル開発用。本番ではサーバーレスに注意
  }),
  observability: new Observability({
    configs: {
      default: {
        serviceName: 'mastra',
        exporters: [
          new DefaultExporter(),  // Mastra Studio 用に storage へ保存
          new CloudExporter(),    // Mastra Cloud へ送信（MASTRA_CLOUD_ACCESS_TOKEN が必要）
        ],
        spanOutputProcessors: [
          new SensitiveDataFilter(), // パスワード・トークン・キーなどを自動でマスク
        ],
      },
    },
  }),
});
```

## Mastra Studio でトレースを確認する

`npm run dev` で Mastra Studio（`http://localhost:4111`）を起動し、左メニューから「Traces」を開きます。エージェントを実行すると、エントリが追加されます。

トレースをクリックすると、スパンの階層構造が展開されます。`agent.run` > `llm.generate` > `tool.execute` という親子関係が視覚的に確認でき、各スパンに実行時間・トークン数・入出力が表示されます。

![](https://static.zenn.studio/user-upload/78c19713ffae-20260318.png)  
*StudioのObservability画面。エージェントに質問してから回答されるまでの、サブエージェント、LLM、ツールの呼び出し関係が階層的に表示され、ドリルダウンしながら確認することができる。それぞれの開始終了タイミングも分かりやすくビジュアル表示されている。*

![](https://static.zenn.studio/user-upload/fa9a1419e819-20260318.png)  
*その中からLLMをクリックして詳細表示したところ。開始終了のタイムスタンプやInputやOutputのほか、入出力トークン数などを確認することができる。*

---

# エクスポーター：トレースをどこに送るか

エクスポーターは、収集したスパンデータを「**どの先に送るか**」を決めるコンポーネントです。複数のエクスポーターを同時に指定でき、同じトレースデータを複数の宛先に送ることができます。

## 内部エクスポーター

Mastra が標準で提供するエクスポーターです。

**DefaultExporter** は、トレースデータをMastraの storage（LibSQLやPostgreSQL）に書き込みます。Mastra Studio でトレースを確認するにはこれが必要です。開発環境では基本的に常に有効にしておきます。

**CloudExporter** は、Mastra Cloud ダッシュボードにトレースを送信します。`MASTRA_CLOUD_ACCESS_TOKEN` 環境変数が設定されている場合に動作します。チームで共有できる本番監視基盤として機能します。

## 外部エクスポーター：Langfuse を例に

チームがすでに外部のLLM監視ツールを利用していたり、長期的なトレース保存・アラート・ダッシュボードが必要な場合は、外部エクスポーターを利用します。

**Langfuse** はオープンソースのLLMエンジニアリングプラットフォームで、セルフホストも可能なため、データの外部送信を嫌う環境でも使いやすいのが特徴です。

```
npm install @mastra/langfuse
```

```
import { LangfuseExporter } from '@mastra/langfuse';
import {
  Observability,
  DefaultExporter,
  SensitiveDataFilter,
} from '@mastra/observability';

const langfuseExporter = new LangfuseExporter({
  publicKey: process.env.LANGFUSE_PUBLIC_KEY!,
  secretKey: process.env.LANGFUSE_SECRET_KEY!,
  baseUrl: process.env.LANGFUSE_BASE_URL, // セルフホストの場合
});

export const mastra = new Mastra({
  // ... 他の設定 ...
  observability: new Observability({
    configs: {
      default: {
        serviceName: 'mastra',
        exporters: [
          new DefaultExporter(),  // Studio アクセスを維持
          langfuseExporter,       // Langfuse にも送信
        ],
        spanOutputProcessors: [new SensitiveDataFilter()],
      },
    },
  }),
});
```

外部エクスポーターを追加する際も `DefaultExporter` を残しておけば、Studio でのローカル確認と外部サービスへの送信を同時に行えます。

## 対応している外部プラットフォーム

Mastra が公式に対応しているエクスポーターは以下の通りです（いずれも個別パッケージが必要）。

| プラットフォーム | パッケージ | 特徴 |
| --- | --- | --- |
| Langfuse | `@mastra/langfuse` | オープンソース、セルフホスト可 |
| Braintrust | `@mastra/braintrust` | eval・評価機能が充実 |
| Arize Phoenix | `@mastra/arize` | MLフルスタック監視、OpenInference準拠 |
| Datadog | `@mastra/datadog` | 既存インフラとの統合、フルスタックAPM |
| LangSmith | `@mastra/langsmith` | LangChainエコシステムとの親和性 |
| PostHog | `@mastra/posthog` | プロダクトアナリティクスとAI計測の統合 |
| Sentry | `@mastra/sentry` | エラー監視との統合 |
| OpenTelemetry | `@mastra/otel` | OTEL互換の任意のバックエンドに送信 |

OpenTelemetry（OTEL）エクスポーターを使えば、Dash0・MLflow・New Relic・SigNoz・Traceloop・Zipkinなど、OpenTelemetry対応のほぼすべてのプラットフォームにトレースを送ることができます。

また、**Bridge**（`@mastra/otel-bridge`）という別の仕組みもあります。エクスポーターがMastraから外部へデータを送信するのに対して、ブリッジは既存の分散トレーシングシステムにMastraのスパンを統合するためのものです。すでにOpenTelemetryベースのトレーシング基盤が社内にある場合に利用します。

---

# サンプリング：本番コストをコントロールする

トレースは全件収集するほど詳細な情報が手に入りますが、高トラフィックな本番環境では、すべてのリクエストをトレースすると storage や外部サービスへの書き込みコストが膨大になります。サンプリングはこのコストをコントロールするための仕組みです。

## 4つのサンプリング戦略

**`always`（デフォルト）** はすべてのトレースを収集します。開発環境や低トラフィックな環境では、これで問題ありません。

```
sampling: { type: 'always' }
```

**`never`** はトレースを完全に無効化します。特定の環境で一時的にトレースを止めたい場合に使います。

```
sampling: { type: 'never' }
```

**`ratio`** は指定した確率でランダムにサンプリングします。本番環境で全体の傾向をつかみたいが全件取る必要はない、という場合に最もよく使われます。

```
sampling: { type: 'ratio', probability: 0.1 } // 10% だけ収集
```

**`custom`** は独自のロジックでサンプリング可否を決めます。たとえば「プレミアムユーザーのリクエストは50%、それ以外は1%」のような条件を実装できます。

```
sampling: {
  type: 'custom',
  sampler: (options) => {
    if (options?.metadata?.userTier === 'premium') {
      return Math.random() < 0.5; // プレミアムは 50% サンプリング
    }
    return Math.random() < 0.01; // その他は 1%
  },
}
```

---

# 環境別設定（Multi-Config）

開発・ステージング・本番で異なるサンプリング率やエクスポーター先を使い分けたい場面はよくあります。Multi-Config 設定と `configSelector` を組み合わせると、`NODE_ENV` に応じて自動的に設定を切り替えられます。

```
import { LangfuseExporter } from '@mastra/langfuse';
import {
  Observability,
  DefaultExporter,
  CloudExporter,
  SensitiveDataFilter,
} from '@mastra/observability';

const langfuseExporter = new LangfuseExporter({
  publicKey: process.env.LANGFUSE_PUBLIC_KEY!,
  secretKey: process.env.LANGFUSE_SECRET_KEY!,
});

export const mastra = new Mastra({
  // ... 他の設定 ...
  observability: new Observability({
    configs: {
      // 開発環境：全件収集、Studio のみ
      development: {
        serviceName: 'mastra-dev',
        sampling: { type: 'always' },
        exporters: [new DefaultExporter()],
      },
      // ステージング環境：50% 収集、Langfuse にも送信して確認
      staging: {
        serviceName: 'mastra-staging',
        sampling: { type: 'ratio', probability: 0.5 },
        exporters: [new DefaultExporter(), langfuseExporter],
      },
      // 本番環境：1% 収集、Cloud + Langfuse に送信
      production: {
        serviceName: 'mastra-prod',
        sampling: { type: 'ratio', probability: 0.01 },
        exporters: [
          new CloudExporter(),
          langfuseExporter,
        ],
        spanOutputProcessors: [new SensitiveDataFilter()],
      },
    },
    // NODE_ENV に応じて設定を自動選択
    configSelector: (context, availableTracers) => {
      const env = process.env.NODE_ENV || 'development';
      if (availableTracers.includes(env)) {
        return env;
      }
      return 'development';
    },
  }),
});
```

`configSelector` は実行時に呼ばれる関数で、第1引数の `context` にはリクエストコンテキストが、第2引数の `availableTracers` には `configs` に定義したキーの一覧が渡されます。`NODE_ENV` だけでなく、リクエストのメタデータや特定のフラグを見て動的に切り替えることも可能です。1回のリクエストに対して使えるのは1つの設定のみですが、その設定の中で複数のエクスポーターを同時に使うことはできます。

---

# まとめ

Mastra の Observability は、Logging と Tracing という2つの軸で構成されています。

Logging（`PinoLogger`）はセットアップが簡単で、ワークフローやツールの実行状況をテキストログとして残します。Tracing（`@mastra/observability`）は少し準備が必要ですが、エージェントの実行階層・トークン使用量・ツールの入出力・実行時間といったAIエージェント固有の情報を丸ごと記録します。

エクスポーターを切り替えることで、ローカルの Studio から Langfuse・Braintrust・Datadog などの外部サービスまで対応でき、サンプリング設定と Multi-Config を組み合わせると開発・本番でのコストバランスも取れます。

AIエージェントは「動いている」だけでは不十分で、「何をしているか見える」状態にして初めて、改善・デバッグ・コスト管理が可能になります。ここで紹介した仕組みを早い段階から導入しておくことを推奨します。

[>> 次回 : (14) 2026年大注目のRalph Wiggum Loop](https://zenn.dev/shiromizuj/articles/6eb3e898b98d58)
