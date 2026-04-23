---
id: "2026-03-23-mastra-changelog-解説-2026-03-17-技術解説mastracore1140-01"
title: "[Mastra Changelog 解説] 2026-03-17 技術解説（@mastra/core@1.14.0）"
url: "https://zenn.dev/shiromizuj/articles/e72650e2f396bc"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "zenn"]
date_published: "2026-03-23"
date_collected: "2026-03-24"
summary_by: "auto-rss"
---

[Mastra](https://mastra.ai/) の[公式 Blog](https://mastra.ai/blog) で発表された [Changelogs](https://mastra.ai/blog/category/changelogs) を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。速報性重視で AI の力を多分に使っているので、私自身の考察は少なめです。

---

2026-03-17 の Mastra リリース（`@mastra/core@1.14.0`）は、**エージェントループとメモリまわりの信頼性強化**が中心です。AI Gateway ツールのファーストクラス対応、Observational Memory のキャッシュ安定化と時点取得 API、MCP クライアントのサーバー単位診断機能という 3 本柱に加え、トレーシング・スキーマ互換性・セキュリティ改善など多岐にわたる修正が含まれています。

今回の焦点は大きく 3 つです。

1. **AI Gateway ツールのエージェントループ統合** — `gateway.tools.perplexitySearch()` のような Gateway ツールが、プロバイダーツールと同等に扱われるようになった
2. **Observational Memory の信頼性向上** — キャッシュ安定化と `getObservationsAsOf()` による時点取得
3. **MCP クライアントの診断・修復機能** — サーバー単位の再接続・エラー確認・stderr 取得

---

## ハイライト1: AI Gateway ツールのエージェントループ統合

### なぜ Gateway ツールは特別扱いが必要なのか

Mastra ではツールを大きく 2 種類に分けて考えることができます。

**ローカルツール**は、Mastra アプリ内の TypeScript 関数として実装されます。エージェントがツールを呼び出すと、Mastra フレームワーク側が関数を実行して結果を LLM に戻します。  
**プロバイダーツール**は、LLM プロバイダー（OpenAI や Anthropic など）が自前でサーバーサイドで管理するツールです。`openai.tools.webSearch()` や Anthropic の `web_search` がこれに該当し、プロバイダーが実行結果をサーバー側に保持した上で LLM コンテキストへ統合します。

v1.14 で新たに注目されるのが **AI Gateway ツール**です。例として挙げられているのは `gateway.tools.perplexitySearch()` で、Mastra の AI Gateway 機能を通じて外部サービスを呼び出すツール群です。これらは「プロバイダーが実行する（providerExecuted）」という意味ではプロバイダーツールに似ていますが、**プロバイダーがサーバーサイドで結果を永続化しない**という点で根本的に異なります。

この差異が、以下のような問題を引き起こしていました。

* ストリーミング生成中にツール呼び出しの順序が乱れ、結果が欠落する
* ツール呼び出しの記録はあるのに結果が存在しない「歯抜け」状態のメモリリプレイ
* `providerExecuted` フラグや `providerMetadata` がツール結果への状態遷移時に意図せず除去される

### 修正の要点

`@mastra/core@1.14.0` では、エージェントループが Gateway ツールに対して以下の処理を行うようになりました。

1. ツール呼び出しが Gateway ツールかどうかを自動で推論し、`providerExecuted` を適切に設定
2. ストリームから届く「プロバイダーが実行した結果」を元のツール呼び出しにマージ
3. プロバイダーがすでに結果を返している場合は、Mastra 側のローカル実行をスキップ
4. ツール呼び出しのパーツを「ストリームで届いた順」に正しく永続化

特に 4 の「ストリーム順の永続化」は、ストリーミング環境ではプロバイダーがツール実行を「遅延（defer）」させることがあるため、従来は順序が乱れがちでした。今回の修正で、仮に遅延実行があっても最終的にストリームで結果が届いた順序で記録されるようになります。

```
// AI Gateway ツールを通常ツールと同じように定義・利用できる
const agent = new Agent({
  name: "research-agent",
  tools: {
    search: gateway.tools.perplexitySearch(),
    // ... ローカルツールと混在も可能
  },
  // エージェントループが providerExecuted を自動推論する
});
```

---

## ハイライト2: Observational Memory の信頼性向上

### Observational Memory とは何か

Observational Memory（観察的メモリ）は Mastra の高度なメモリ機能のひとつで、エージェントとの会話履歴を定期的に「観察」し、重要な事実・パターン・ユーザー特性などを抽出して構造化されたメモリとして蓄積します。

簡単に言えば「エージェントが会話から学んで要点を記憶していく仕組み」です。長期的な会話コンテキストを保持しながら、トークン消費を抑えるための重要な仕組みです。

### 問題: メモリキャッシュの不安定さ

従来の実装では、観察データをプロンプトに組み込む際の「区切り」が曖昧で、次のような問題がありました。

* 観察データの小さな順序変動が「大きなプロンプト差分」として現れ、LLM のキャッシュを壊す
* プロバイダー実行ツールの結果がまだ届いていない間に観察を開始し、メッセージが中途半端な状態で分割される
* 長文の `encryptedContent` などを含むツール結果が観察プロンプトを肥大化させ、実際にモデルが見るトークン数とのズレが生じる

### 修正の要点

**① 日付付きのメッセージ境界デリミタ（Cache Stability）**

観察データを「区切り」で分割して永続化する際、各チャンクに日付付きのメッセージ境界を挿入するようになりました。これにより、キャッシュヒット率が安定し、観察対象の更新があったとき以外は既存のキャッシュが有効に働きます。libsql・MongoDB・PostgreSQL の各ストアアダプターにも同じ変更が適用されています。

**② `getObservationsAsOf()` による時点取得**

新たに追加された `getObservationsAsOf()` 関数は「あるメッセージが作成された時点でアクティブだった観察データセット」を取得できます。

```
import { getObservationsAsOf } from "@mastra/memory";

// message.createdAt の時点での観察データを取得
const observations = getObservationsAsOf(
  record.activeObservations,
  message.createdAt
);
```

これが特に役立つシナリオは 3 つあります。

| シナリオ | 活用方法 |
| --- | --- |
| **会話リプレイ** | リプレイ時点のコンテキストを再現し、一貫したプロンプティングを行う |
| **デバッグ** | 「そのとき何を知っていたか」を後から正確に確認できる |
| **評価ワークフロー** | 時刻精度に依存する eval タスクで正確な過去コンテキストを使用する |

**③ ツール結果のサイズ制限**

過大なツール結果がオブザーバープロンプトに流れ込まないよう、観察処理の前段で自動的にサイズ制限が行われるようになりました。大きな `encryptedContent` フィールドは除去され、残りのペイロードも切り詰められます。

---

## ハイライト3: MCP クライアントの診断・修復機能

### MCP サーバーの「現実的な問題」

Model Context Protocol（MCP）は、LLM エージェントが外部ツール・データソース・サービスと標準的なプロトコルで通信するための仕様です。Mastra の `@mastra/mcp` パッケージは複数の MCP サーバーを同時に扱えますが、実運用では様々な問題が起きます。

* stdio サーバーが予期せず落ちて、そのサーバーのツールだけが使えなくなる
* 一部のサーバーが設定ミスで起動しているが、エラーの詳細を確認する手段がない
* 問題のあるサーバーを修復するために、すべてのサーバーを再起動しなければならない

### 新しい診断・制御 API

`@mastra/mcp@1.3.0` では 3 つの API が追加されました。

```
// 特定サーバーのみを再接続（全体の再起動は不要）
await mcpClient.reconnectServer("slack");

// ツールセットをサーバー単位のエラーと一緒に取得
const { toolsets, errors } = await mcpClient.listToolsetsWithErrors();
// errors: { serverName: Error | null } の形でサーバーごとの状態を確認できる

// stdio サーバーの stderr を取得（デバッグや診断に）
const stderr = mcpClient.getServerStderr("slack");
```

`listToolsetsWithErrors()` は特に重要で、以前の `listToolsets()` では一部のサーバーが失敗しても他のサーバーのツールは問題なく返ってくる一方、どのサーバーがエラーになっているかがわかりませんでした。今回の API ではエラー情報をサーバー単位で同時に取得できるため、「自己修復型」の MCP 統合を構築しやすくなります。

またこのリリースで `@modelcontextprotocol/sdk` が `^1.17.5` から `^1.27.1` へ大幅更新されました。

#### プロンプトバージョンの非推奨化

`@mastra/mcp` のプロンプト `version` 指定が非推奨になりました。MCP プロトコル仕様にプロンプトバージョンの概念は存在しないためです。

```
// Before（非推奨）
client.prompts.get({ name: 'explain-code', version: 'v1', args });

// After（推奨）
client.prompts.get({ name: 'explain-code-v1', args });
```

---

## その他の注目アップデート

### `spanId` がトレーシング識別子に追加

エージェントの `.stream()`・`.generate()` やワークフロー実行結果に、`traceId` と並んで `spanId` が含まれるようになりました。Datadog・Jaeger・OpenTelemetry 対応のオブザーバビリティベンダーでは、「あの実行」を素早く特定するためにスパン ID を使ってフィルタリングすることが一般的なためです。（[PR #14327](https://github.com/mastra-ai/mastra/pull/14327)）

### Cloudflare デプロイのセキュリティ修正

`@mastra/deployer-cloudflare@1.1.12` で、`.env` の変数が `wrangler.jsonc` に書き込まれなくなりました（[#14302](https://github.com/mastra-ai/mastra/pull/14302)）。

以前は `.env` の内容が `vars` フィールドとして wrangler 設定ファイルに展開されており、ソースコード管理に意図せずシークレットがコミットされるリスクがありました。今後はシークレットを `npx wrangler secret bulk .env` で明示的にアップロードする運用が推奨されます。

### `@mastra/schema-compat` での `ZodIntersection` 対応

JSON Schema の `allOf`（Zod 変換後の `ZodIntersection`）を使った MCP ツールが、これまで Anthropic・Google・OpenAI 系プロバイダーとの互換性レイヤーで `'does not support zod type: ZodIntersection'` というエラーを投げていました。v1.14 でこれが解消されました（[#14255](https://github.com/mastra-ai/mastra/pull/14255)）。

### PinoLogger の JSON 出力対応

`@mastra/loggers@1.0.3` で `PinoLogger` に `prettyPrint` オプションが追加されました。これまで常に pino-pretty による人間向けの複数行カラー出力しかできず、Datadog・Loki・CloudWatch などのログアグリゲーターで正しく取り込めないケースがありました（[#14306](https://github.com/mastra-ai/mastra/pull/14306)）。

```
new PinoLogger({
  prettyPrint: false, // false にすると単一行 JSON 出力（ログアグリゲーター向け）
});
```

### Agent セッションページの追加（playground-ui）

`@mastra/playground-ui@17.0.0` で `/agents/<agentId>/session` に新しいページが追加されました。サイドバーや情報パネルを省いたシンプルなチャット画面で、内部テストや非技術者向けの共有に適しています（[#13754](https://github.com/mastra-ai/mastra/pull/13754)）。

### 新しい可観測性 API エンドポイント（server / client-js）

`@mastra/server@1.14.0` と `@mastra/client-js@1.9.0` で、ログ・スコア・フィードバック・メトリクス（集計・時系列・パーセンタイル）・ディスカバリー情報を扱う API エンドポイントとクライアントメソッドが追加されました。前回の v1.13 で整備されたスキーマ基盤を活かした、より完全な可観測性 API の第二弾です（[#14270](https://github.com/mastra-ai/mastra/pull/14270)）。

---

## まとめ

| 分類 | 変更内容 |
| --- | --- |
| **コア** | AI Gateway ツールの`providerExecuted` 自動推論、ストリーム順永続化 |
| **メモリ** | Observational Memory のキャッシュ安定化、`getObservationsAsOf()` |
| **MCP** | `reconnectServer`・`listToolsetsWithErrors`・`getServerStderr` 追加 |
| **トレーシング** | `spanId` を実行結果に追加 |
| **セキュリティ** | Cloudflare デプロイで `.env` が `wrangler.jsonc` に漏れない修正 |
| **互換性** | ZodIntersection / `allOf` を全プロバイダー互換レイヤーで対応 |
| **ロギング** | PinoLogger で JSON 出力オプション追加 |
| **Studio** | エージェントセッション専用ページ、可観測性 API の充実 |

破壊的変更はありません。特にプロバイダー実行ツールを使っている開発者には、メモリリプレイの信頼性改善と `getObservationsAsOf()` が即効性のある恩恵をもたらすでしょう。

---

**参考リンク**
