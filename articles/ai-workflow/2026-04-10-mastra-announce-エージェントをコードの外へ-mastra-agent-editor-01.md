---
id: "2026-04-10-mastra-announce-エージェントをコードの外へ-mastra-agent-editor-01"
title: "[Mastra Announce] エージェントをコードの外へ ― Mastra Agent Editor が開くイテレーションサイクル"
url: "https://zenn.dev/shiromizuj/articles/7ece2af5c09ce9"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-04-10"
date_collected: "2026-04-11"
summary_by: "auto-rss"
---

[Mastra](https://mastra.ai/) の[公式Blog](https://mastra.ai/blog)で発表された[Announcements](https://mastra.ai/blog/category/announcements)を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。速報性重視でAIの力を多分に使っているので、私自身の考察は少なめです。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

## コードの中に閉じ込められた「調整作業」

2026年4月8日 、Mastra は **Agent Editor**を発表しました。

AIエージェントを本番稼働させた経験があれば、開発後の反復作業がいかに面倒かを実感しているはずです。エージェントのシステムプロンプトを少し書き換えたい。新しいツールを追加したい。特定のユーザーロールにだけ使わせるツールを変えたい――どれも小さな変更のはずなのに、コードを開き、テストし、コミットして、デプロイするという一連のサイクルを踏まなければなりません。

もっと本質的な問題もあります。プロダクトマネージャーやカスタマーサポートのリーダーなど、エージェントの動作を最もよく理解している人々が、コードベースを触れないがゆえに変更に関与できません。エンジニアは「橋渡し役」を担わされ、本来の開発作業に集中できなくなります。

---

## Agent Editor とは何か

Mastra Studio に統合された Agent Editor は、コード定義済みエージェントの設定を、Studio の UI 上から編集できるようにする機能です。開発者はこれまでどおり TypeScript でエージェントを定義します。Agent Editor はその定義を「出発点」として読み込み、Studio から行った変更を別のストレージレイヤーに保存していきます。

重要なのは、コードを上書きするわけではない点です。エディタは**ドラフト/公開**というバージョン管理ワークフローを持ち、変更はドラフトとして保存されます。十分にテストして準備ができたタイミングで「Publish」を押せば、エージェントを使うすべてのアプリケーションに新しい設定が即座に反映されます。PR レビューもデプロイも不要です。

いつでもバージョン比較やロールバックができ、変更履歴を完全に管理できます。開発チームとプロダクトチームの間の摩擦を減らしながら、技術的な品質管理も失わないというバランスを実現しています。

---

## セットアップ：ストレージを外に出す設計

Agent Editor を使い始めるには、`@mastra/core` を 1.24.0 以降にアップグレードし、`@mastra/editor` パッケージを追加インストールします。

```
npm install @mastra/editor
```

次に、Mastra インスタンスの設定にエディタを追加します。ここで注目したいのが **MastraCompositeStore** の使い方です。

```
// src/mastra/index.ts

import { Mastra } from "@mastra/core";
import { MastraCompositeStore } from "@mastra/core/storage";
import { LibSQLStore } from "@mastra/libsql";
import { MastraEditor } from "@mastra/editor";

export const mastra = new Mastra({
  storage: new MastraCompositeStore({
    id: "mastra-storage",
    default: new LibSQLStore({ ... }),
    editor: new LibSQLStore({
      id: "mastra-editor",
      url: "file:./editor.db"
    })
  }),
  editor: new MastraEditor(),
});
```

`MastraCompositeStore` の `editor` キーは独立したストレージドメインとして扱われます。つまり、エージェントの設定変更履歴を、アプリケーションの他のデータとは異なるデータベースに分離できます。本番環境では LibSQL ではなく PostgreSQL や MongoDB を選ぶこともできます。バックアップポリシーや可用性要件をエージェント設定専用に最適化できるのは、地味ながら運用上の大きなメリットです。

---

## 4つの編集機能

### 1. エージェント基本設定

Studio でエージェントを開くと、コードで定義された初期状態が表示されます。ここから命令（instruction）や変数の追加・変更が行えます。ただし、エージェントの `id`、`name`、`model` といったフィールドはコードに由来するものとして保護されており、エディタから変更することはできません。設計の核心部分は依然としてコードが持つという方針が貫かれています。

### 2. ツールの設定とオーバーライド

プロジェクト内のツールを追加するだけでなく、MCP クライアントを接続して外部サーバーのツールを取り込むことができます。さらに、どのソースのツールに対しても**ツールの説明文をオーバーライド**できる点が重要だ。LLM がツールをいつどのように使うかはツールの説明文に大きく依存します。エディタから説明文を調整できることで、コードを変更せずにエージェントの判断精度をチューニングできます。

[Composio](https://mastra.ai/docs/editor/tools#composio) や [Arcade](https://mastra.ai/docs/editor/tools#arcade) などの統合プロバイダーのツールを使いたい場合は、`MastraEditor` に `toolProviders` を渡します。

```
import { ComposioToolProvider } from '@mastra/editor/providers/composio'

editor: new MastraEditor({
  toolProviders: {
    composio: new ComposioToolProvider({
      apiKey: process.env.COMPOSIO_API_KEY!,
    }),
  },
})
```

### 3. プロンプトブロックと命令

命令はエージェントにインラインで書く方法と、**プロンプトブロック**として定義する方法の2種類があります。プロンプトブロックは Studio の「Prompts」セクションで独立して管理され、複数のエージェントで共有できます。同じ会社のポリシー文句を複数のエージェントで使い回すようなケースで、一か所の変更を全エージェントに伝播させたいときに威力を発揮します。

どちらの方法も Markdown と `{{変数名}}` 書式による変数補間をサポートしており、変数はエージェント実行時に `requestContext` から実行時解決されます。

### 4. バージョン管理：保存・公開・ロールバック

「Save」を押すと不変のバージョンスナップショットが作成されます。変更メッセージのタグを付けて変更内容を記録できます。「Publish」を押せば公開バージョンが切り替わり、以降のすべてのリクエストに反映されます。公開前にどれだけドラフトを積み重ねても本番には影響しません。

---

## 表示条件：文脈に応じてツールとプロンプトを切り替える

Agent Editor のもっとも実用的な機能の一つが\*\*表示条件（Display Conditions）\*\*だ。ツールとプロンプトブロックのそれぞれに、エージェント実行時の `requestContext` に対して評価されるルールを設定できます。

たとえば、返金処理ツールを `userRole === "admin"` のときだけ有効にしたり、特定のプロンプトブロックを顧客のプランに応じて切り替えたりといったことが、コードを一行も書かずに Studio の UI 上でビジュアルに設定できます。ルールエンジンは `equals`、`contains`、`greater_than`、`in`、`exists` といった演算子と AND/OR グループをサポートしており、複雑な条件も表現可能です。

従来、こうした「コンテキスト依存の動作切り替え」はコード上で条件分岐を実装する必要がありました。表示条件を使えば、その実装をエージェント設定として外部化できます。エージェントの振る舞いをより細かく調整したいが、エンジニアリングリソースを使いたくないプロダクトチームにとって、これは大きな強みです。

---

## バージョン API：環境ピンニングと A/B テスト

バージョン管理はドラフト/公開という UI だけの話ではありません。エージェントのすべてのエンドポイントはバージョンパラメータを受け付けます。`.generate()` や `.stream()` を呼ぶ際に、`versionId` または `status` を渡すことができます。

```
// 公開バージョンを読み込む（デフォルト）
const agent = mastra.getAgentById("support-agent");

// 最新のドラフトを読み込む
const agent = mastra.getAgentById("support-agent", {
  status: "draft",
});

// 特定バージョンを固定して読み込む
const agent = mastra.getAgentById("support-agent", {
  versionId: "abc-123",
});
```

ステージング環境ではドラフト、本番では公開バージョンという環境ピンニングが自然に実現できます。また、異なるリクエストを異なるバージョンにルーティングすることで、エージェントの A/B テストも可能です。新しい命令がどちらの変換率が高いかを比べるような実験を、インフラを変えずに回せます。

---

## アクセス制御：誰が何を変えられるか

Agent Editor は [Studio Auth](https://mastra.ai/blog/announcing-studio-auth) によって保護されています。API エンドポイントと Studio UI の両方が、認証済みユーザーのみに制限されます。

その上で RBAC（ロールベースアクセス制御）が機能します。たとえば `member` ロールはドラフトの編集まで、`admin` ロールだけが「Publish」できるとした場合、プロダクトチームは自由に提案を蓄積しながら、公開の判断権限は技術リードやプロダクトオーナーが握る、という運用が成立します。大規模チームでエージェントを管理する際の品質ゲートとして機能します。

---

## プログラム的アクセス：自己改変するエージェントの可能性

エディタの全 API は `mastra.getEditor()` から利用できます。REST API は `/api/stored/agents` で公開されています。

```
import { mastra } from "./mastra";

const editor = mastra.getEditor();

// 命令を更新（自動的に新しいドラフトが作成される）
await editor.agent.update({
  id: "support-agent",
  instructions: "You are a customer support agent. Always greet the customer by name.",
});
```

CI パイプラインからエージェント設定を自動更新したり、社内のエージェント管理ツールを構築したりする用途で使えます。

より興味深いのは、エージェント自身がこの API を呼べるという点です。エージェントが実行中に学習した内容に基づいて、自分のツール構成を変えたり、命令を調整したりする自己更新の仕組みを作ることができます。これはまだ実験的な使い方ですが、エージェントが自律的に能力を拡張・最適化していく方向性を示しています。詳細は [MastraEditor クラスのリファレンス](https://mastra.ai/reference/editor/mastra-editor) を参照してください。

---

## データセットと実験との組み合わせ

Agent Editor 単体でも有用ですが、[データセット](https://mastra.ai/docs/evals/datasets/overview) と [実験](https://mastra.ai/docs/evals/datasets/running-experiments) 機能との組み合わせが本来の強みを引き出します。命令やツール構成を変えたドラフトを作り、本番に公開する前にデータセットを使って実験的に評価できます。デプロイ前の品質検証を Studio の中で完結させることができます。

さらに [ログ](https://mastra.ai/docs/observability/logging) や [トレース](https://mastra.ai/docs/observability/tracing/overview) と組み合わせることで、変更した設定がどのような影響を与えたかを可観測性の観点から確認しながら反復できます。このエコシステムとしての統合こそが、単なる「UI エディタ」を超えた Agent Editor の価値です。

---

## まとめ：開発とドメイン知識の間を埋める

Agent Editor が解決しようとしているのは、技術的な問題というよりも**組織の問題**です。エージェントを最もよく理解している人とコードを変更できる人が一致しないという現実に対して、エンジニアリングコストをかけずに設定の主権を分散する仕組みを提供しています。

コードが設計の核心（ID、名前、モデル）を守りながら、運用上の調整（命令、ツール選択、表示条件）は Studio から行えるという役割分担は、長期的なメンテナンスの観点からも理にかなっています。

本機能は `@mastra/core` 1.24.0 から利用可能です。完全なセットアップ手順は [Editor ドキュメント](https://mastra.ai/docs/editor/overview) を参照してください。

---

## 参考リンク
