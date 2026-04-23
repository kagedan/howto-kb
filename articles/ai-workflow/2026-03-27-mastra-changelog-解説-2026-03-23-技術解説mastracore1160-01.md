---
id: "2026-03-27-mastra-changelog-解説-2026-03-23-技術解説mastracore1160-01"
title: "[Mastra Changelog 解説] 2026-03-23 技術解説（@mastra/core@1.16.0）"
url: "https://zenn.dev/shiromizuj/articles/7ddbfd95a779e3"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-03-27"
date_collected: "2026-03-28"
summary_by: "auto-rss"
---

[Mastra](https://mastra.ai/) の[公式 Blog](https://mastra.ai/blog) で発表された [Changelogs](https://mastra.ai/blog/category/changelogs) を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。速報性重視で AI の力を多分に使っているので、私自身の考察は少なめです。

---

2026-03-23 の Mastra リリース（`@mastra/core@1.16.0`）は、**評価・認証・コスト効率**の 3 本柱が中心です。Observational Memory のトークン閾値ベースモデルルーティング、MongoDB への datasets/experiments サポート拡張、Okta SSO + RBAC パッケージの新設が主要ハイライトです。加えて、ワークフロー評価の強化、ツール中断ハンドリング、可観測性の大幅強化など多岐にわたる改善が含まれています。

今回の焦点は大きく 3 つです。

1. **Observational Memory のスマートなモデル選択** — トークン数に応じてモデルを自動切り替えし、コストと品質を両立する `ModelByInputTokens`
2. **MongoDB への datasets/experiments サポート** — バージョン管理付きでデータセットと実験を MongoDB に保存できるようになった
3. **Okta 認証と RBAC** — エンタープライズ向け SSO + グループベースパーミッションを提供する `@mastra/auth-okta` パッケージ

---

## ハイライト1: Observational Memory のスマートなモデル選択

### なぜトークン閾値ベースのモデルルーティングが必要なのか

Observational Memory（OM）は、会話の中でエージェントが「観察」を蓄積し、そこから洞察を抽出しコンテキストを圧縮する仕組みです。この処理には LLM を使いますが、入力サイズ（トークン数）が大きく変動するという特性があります。

* **小さな入力**（数千トークン程度）：シンプルな観察や短い会話。高性能モデルを使うのはオーバースペックでコスト的に非効率。
* **大きな入力**（数万〜数十万トークン）：長い会話履歴や大量のコンテキスト。安価なモデルでは精度や品質が落ちる。

v1.16.0 以前は、OM に対してモデルを 1 つだけ設定する構造でした。開発者は「安いモデルで品質を犠牲にする」か「高いモデルをすべての呼び出しに使う」かの二択を迫られていました。

### ModelByInputTokens の仕組み

```
import { Memory, ModelByInputTokens } from "@mastra/memory";

const memory = new Memory({
  options: {
    observationalMemory: {
      model: new ModelByInputTokens({
        upTo: {
          10_000: "google/gemini-2.5-flash",   // 1万トークン以下 → 軽量モデル
          40_000: "openai/gpt-4o",              // 4万トークン以下 → 中級モデル
          1_000_000: "openai/gpt-4.5"            // 100万トークン以下 → 高性能モデル
        }
      })
    }
  }
});
```

**動作の詳細:**

1. `upTo` のキーは包含的な上限（≤）として評価されます
2. モデルの解決は、オブザーバーまたはリフレクターの呼び出し時に実際の入力トークン数を使って行われます
3. 最大閾値を超えた場合はエラーをスローするため、予期せぬ巨大入力を明示的にハンドリングできます

また、トレーシング機能も強化され、どのモデルが選択されたか・その理由（入力トークン数）がスパンに記録されるようになりました。これにより、コスト最適化の効果を可視化しながら運用できます。

---

## ハイライト2: MongoDB へのデータセットと実験サポート

### 評価ワークフローにおける MongoDB の位置付け

Mastra の評価（eval）システムは、**データセット**（テスト入力の集合）と**実験**（モデル・プロンプトの組み合わせ試行）を中心に構成されています。v1.16.0 まで、このデータは主にリレーショナルDB（PostgreSQL など）に保存される構成でした。

MongoDB を使っているチームは、評価ストレージのために別のバックエンドを立ち上げるか、評価機能を諦めるかの選択を迫られていました。

### 追加された機能

`@mastra/mongodb` の `MongoDBStore` が `datasets` と `experiments` ストレージをサポートしました：

```
import { MongoDBStore } from "@mastra/mongodb";

const store = new MongoDBStore({
  uri: "mongodb://localhost:27017",
  dbName: "my-app"
});

// データセット操作
const dataset = await store.getStorage("datasets").createDataset({ name: "my-dataset" });
await store.getStorage("datasets").addItem({
  datasetId: dataset.id,
  input: { prompt: "テスト入力" },
  output: { expected: "期待する出力" }
});

// 実験操作
const experiment = await store.getStorage("experiments").createExperiment({
  name: "run-1",
  datasetId: dataset.id
});
```

**バージョン管理と「タイムトラベル」クエリ:**  
データセットアイテムには自動的にバージョンが付与され、特定の時点のデータセットの状態を再現できます。これは再現可能な評価実行（reproducible eval runs）に不可欠な機能で、「先月の実験結果を再現したい」というケースで威力を発揮します。

---

## ハイライト3: Okta 認証と RBAC

### エンタープライズ認証の課題

Mastra をエンタープライズ環境でデプロイする場合、社内の ID プロバイダー（IdP）との統合が必須になります。Okta は多くの企業で標準的に使われている IdP であり、SSO・グループ管理・JWT 発行を提供しています。

`@mastra/auth-okta` は、この統合を簡単に行うためのパッケージです：

```
import { OktaAuth } from "@mastra/auth-okta";

const auth = new OktaAuth({
  domain: "your-org.okta.com",
  clientId: process.env.OKTA_CLIENT_ID!,
  groupPermissionMap: {
    "mastra-admins": ["read", "write", "admin"],
    "mastra-users": ["read"]
  }
});
```

**セキュリティ強化の詳細:**  
今回のリリースでは、コードレビューを経た複数のセキュリティ改善が含まれています：

* **キャッシュポイズニング対策**: グループ取得エラーが確実に伝播し、エラーキャッシュが後続リクエストを誤って通過させることを防ぐ
* **クッキーサイズ制限**: アクセス/リフレッシュトークンをクッキーに保存しないことでブラウザの 4KB 制限内に収める（セッション ID のみ保存）
* **適切なログアウト**: Okta の `id_token_hint` パラメータをログアウト時に送信し、正常な SSO セッション終了を保証

また、Okta RBAC と他の認証プロバイダーを組み合わせた「ミックスアンドマッチ」構成もサポートされています。例えば、認証は GitHub OAuth で行いながら、権限管理だけ Okta グループで制御するといった構成が可能です。

---

## その他の主要な更新

### 評価ワークフローの大幅アップグレード

評価（eval）システムに多数の機能が追加されました：

* **データセットターゲティング**: データセットをエージェント・スコアラー・ワークフローに `targetType` と `targetIds` で紐付け可能
* **実験結果ステータス**: `needs-review`、`reviewed`、`complete` の 3 状態でレビューサイクルを管理
* **エージェントバージョン固定**: `agentVersion` パラメータで特定のエージェントバージョンに実験を固定し、横断的な比較を可能にする
* **LLM 支援タグ提案**: 実験の失敗ケースをクラスタリングし、タグ候補を LLM が自動提案

```
await client.triggerDatasetExperiment({
  datasetId: "my-dataset",
  targetType: "agent",
  targetId: "my-agent",
  version: 3,               // データセットバージョン 3 に固定
  agentVersion: "ver_abc123"  // 特定のエージェントバージョンに固定
});
```

### ツール中断（Suspension）ハンドリング

テストハーネスが `suspend()` を呼び出すツールに対応しました。ツールが中断すると `tool_suspended` イベントが発行され、`respondToToolSuspension()` でユーザーデータを渡して再開できます。これにより、人間の確認が必要なツール（例：支払い承認、外部システムへの書き込み）のテストが容易になります。

### 可観測性の強化

* **コスト追跡**: トレースに推定コストが含まれ、`observabilityStorageType` エンドポイントで永続化状態も確認可能
* **新しいメトリクス API**: 集計・時系列・パーセンタイルなど豊富なメトリクスエンドポイント
* **ストリーミングのツールリスト修正**: ストリーミング実行でも Datadog などのエクスポーターがツールリストを受け取れるよう修正

### バグ修正

* **連続ツールのみのループ**: 連続する純粋なツール呼び出しイテレーション間に `step-start` 境界を挿入し、並列呼び出しとの誤解釈を防止
* **Anthropic ツール順序**: クライアントツールとプロバイダーツールが並列実行される際のブロック分割を修正し、メッセージ履歴の不整合エラーを回避
* **Zod v3/v4 互換性**: ESM 環境での `createRequire` 問題を解消しつつ両バージョンをサポート

---

## まとめ

`@mastra/core@1.16.0` は、**プロダクション運用**に必要な要素を着実に強化したリリースです。

| 機能 | 効果 |
| --- | --- |
| `ModelByInputTokens` | トークン数に応じたモデル自動選択でコストと品質を両立 |
| MongoDB datasets/experiments | MongoDB ユーザーが追加インフラなしに評価ワークフローを利用可能 |
| `@mastra/auth-okta` | エンタープライズ向け SSO + RBAC をすぐに組み込める |
| エージェントバージョン固定 | 実験の再現性を確保し、モデル変更前後の品質比較が容易に |
| ツール中断ハンドリング | 人間承認フローを含むエージェントのテストが可能に |

評価ワークフローの充実と可観測性の強化が続いており、Mastra が「プロトタイプ」から「プロダクション」へのステージを確実に意識していることが伝わるリリースです。

---

参照:
