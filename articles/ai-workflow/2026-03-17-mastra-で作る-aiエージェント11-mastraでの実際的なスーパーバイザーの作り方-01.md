---
id: "2026-03-17-mastra-で作る-aiエージェント11-mastraでの実際的なスーパーバイザーの作り方-01"
title: "Mastra で作る AIエージェント(11) Mastraでの実際的なスーパーバイザーの作り方"
url: "https://zenn.dev/shiromizuj/articles/aa951dd3d08d6f"
source: "zenn"
category: "ai-workflow"
tags: ["LLM", "zenn"]
date_published: "2026-03-17"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

[Mastra で作るAI エージェント](https://zenn.dev/shiromizuj/articles/a0a1659e9f05b6) というシリーズの第11回です。

---

# マルチエージェント

連載の第8回から複数のAIエージェントがタスクを分担・協業する「マルチエージェント」の章に突入し、1つ目の方法論として「ワークフロー」を、そして2つ目の方法論として「エージェント・スーパーバイザー」を確認しました。

もともと、AIエージェントの構成を「三国志」になぞらえて以下のように把握しました。

* フロントに立つリーダーの劉備＝**エージェント**：何をやるにしても軍師に相談
* 天才軍師・諸葛孔明＝**LLM**：劉備に何かと助言するが、決して自分が直接前面に出ない
* 将軍たち＝**ツール**：劉備に呼ばれて定型作業を遂行、RAG／API／MCPなどなど

![](https://static.zenn.studio/user-upload/f590eabc3cad-20260302.png)

マルチエージェントの1つ目は、エージェントを順次つないだ「ワークフロー」でした。

![](https://static.zenn.studio/user-upload/22006c5f38c0-20260302.png)

マルチエージェントの2つ目は他のサブエージェントを調整・管理することに特化した「エージェント・スーパーバイザー」でした。

![](https://static.zenn.studio/user-upload/7a2e7b3f3c1d-20260302.png)

前回は「エージェント・スーパーバイザーとは何ぞや」の説明で終わってしまったので、今回は「本番障害解析システム」を題材に、実際にMastraでスーパーバイザーパターンのエージェントネットワークを開発していく流れを示します。以下の手順で作成していきます。

* Phase 1: 要件定義
* Phase 2: 設計
* Phase 3: 実装準備
* Phase 4: 実装

# Phase 1：要件定義

## 1.1 解決したい問題の明確化

まず、どのような複雑なタスクを複数のエージェントで協調して解決するのかを明確にします。

* どんな問題を解決するのか？
* タスクは事前に完全に定義できるか？（No ならネットワークが適切）
* どのような専門知識が必要か？
* 複数の視点や専門性が必要か？
* 期待される最終的な出力は何か？

例えば、今回の本番障害解析システムで考えると以下のようになります。

```
問題: システム本番障害が発生した際、迅速かつ正確に原因を特定したい
タスクの性質:
  - 障害の種類や原因は事前に予測できない（動的判断が必要）
  - ログ、構成、パフォーマンスなど複数の視点からの分析が必要
  - 仮説検証のループが必要
必要な専門知識:
  - 本番環境の確認（ログ、データベース、ファイル）
  - システムの理解（構成、仕様、ソースコード）
  - 仮説立案と検証
期待される出力:
  - 障害の根本原因
  - 影響範囲
  - 推奨される対応策
```

## 1.2 専門エージェントの洗い出し

タスクを遂行するために必要な専門エージェントを特定します。

**洗い出しの観点**:

1. **専門性**: 各エージェントは特定領域の専門家
2. **独立性**: 他のエージェントと独立して動作可能
3. **協調性**: 互いの結果を活用できる
4. **責務の明確性**: 何をするエージェントなのかが明確

例えば、今回の本番障害解析システムで考えると以下のようになります。

```
専門エージェント案:
1. logAnalysisAgent          // ログ解析の専門家
   - エラーログ、警告ログ、およびそのスタックトレースの確認
   - 指定されたログ種別とタイムレンジに対応したトレースログなどの確認
   - タイムライン構築

2. specificationCheckAgent   // 仕様確認の専門家
   - 各種設計ドキュメントの参照
   - 設計書上の記載の確認

3. sourceCodeAnalysisAgent   // ソースコード確認の専門家
   - 関連コードの特定と分析
   - 指定された仮説に対しソースコードを確認して見解

4. databaseAnalysisAgent     // データベース確認の専門家
   - DBデータの確認
   - 指定された仮説に対しSQLを発行して結果を確認して見解
   - SQLを発行するにあたってDB定義書なども確認

5. fileSystemCheckAgent      // ファイル確認の専門家
   - 設定ファイルや業務ファイル（インタフェースファイルなど）の確認
   - 指定された仮説に対しファイルの中身を確認して見解
   - パーミッション、ディスク容量の確認も含む

6. configCheckAgent          // 構成確認の専門家
   - インフラ状態のチェック
   - 直近のリリース履歴のチェック
   - 指定された仮説に対しインフラ状態を確認して見解

7. hypothesisAgent           // 仮説検証の専門家
   - 仮説立案
   - 検証計画の作成
   - 証拠の評価
```

## 1.3 スーパーバイザーの役割定義

スーパーバイザー（ルーティングエージェント）がどのような判断をするのかを定義します。

* ユーザーのリクエストを解釈
* 適切なサブエージェント／ワークフロー／ツールを選択
* サブエージェントの結果を統合
* メモリ内の仮説管理（keyFacts、activeHypotheses、rejectedHypothesesの更新）
* 必要に応じて追加のエージェントを呼び出し
* 最終的な回答を生成

例えば、今回の本番障害解析システムで考えると以下のようになります。

```
スーパーバイザーの役割:

【初期調査フェーズ】
1. 障害報告を受け取る（サービス名、発生時刻、症状）
2. ログ解析エージェントを呼び出してエラー内容を確認
3. 判明した事実（エラーメッセージ、タイムラインなど）をkeyFactsに記録

【仮説立案フェーズ】
4. 収集した事実を元に、仮説検証エージェントを呼び出して複数の仮説を立案
5. 各仮説をactiveHypothesesに記録
   - 例: 「DBのuser_idカラムにnullが入っている」
   - 例: 「v2.1.0デプロイ時にmax_connections設定が変更された」
   - 例: 「config.jsonのtimeout値が小さすぎる」

【検証フェーズ】
6. 各仮説を検証するために、適切な専門エージェントに「論理的な仮説」を渡す
   - DB仮説 → データベース確認エージェント
     「user_id=123のレコードのemailカラムがnullになっているか確認」
   - デプロイ仮説 → 構成確認エージェント
     「14:00-15:00の間にデプロイがあり、max_connectionsが変更されたか確認」
   - 設定仮説 → ファイル確認エージェント
     「config.jsonのrequest_timeoutが30より小さいか確認」

7. 検証結果を受け取る
   - 真と判明 → confirmedCausesに移動、証拠を記録
   - 偽と判明 → rejectedHypothesesに移動、理由を記録
   - 新しい事実が判明 → keyFactsに追加

【反復フェーズ】
8. 新しい事実や検証結果から、追加の仮説が浮上した場合
   - rejectedHypothesesを確認（類似仮説を調べていないか）
   - 新仮説をactiveHypothesesに追加
   - 再び検証フェーズへ

【結論フェーズ】
9. すべての仮説が検証されたら、仮説検証エージェントに結果を渡して根本原因を特定
10. 包括的な障害分析レポートを生成
    - 根本原因（confirmedCauses）
    - タイムライン（keyFacts）
    - 検証した仮説の履歴（activeHypotheses、rejectedHypotheses）
    - 推奨対策
```

# Phase 2：設計

## 2.1 エージェント構成の設計

各エージェントの役割と責務を詳細に設計します。

**設計のポイント**:

1. **単一責任**: 各エージェントは1つの専門領域に特化
2. **明確な境界**: エージェント間の責務の重複を避ける
3. **適切な粒度**: 大きすぎず、小さすぎず
4. **説明の明確性**: スーパーバイザーが選択できるよう明確な説明
5. **仮説検証志向**: 各エージェントは「仮説」を受け取り、それを「検証」する役割

**エージェント設計テンプレート**:

```
エージェント名: [名前]
ID: [id]
目的: [どのような仮説を検証するのか]
専門領域: [専門知識の範囲]
入力: [論理的な仮説の形式]
出力: [検証結果の形式（真／偽、証拠、詳細）]
使用するツール: [必要なツール一覧]
処理フロー: 
  1. xxx
  2. xxx
  3. xxx
  4. xxx
```

例えば、今回の本番障害解析システムで考えると以下のようになります。

```
// 仕様確認エージェント
エージェント名: Specification Check Agent
ID: spec-check-agent
目的: 「仕様上、システムはこう動くべき」という仮説を検証する
専門領域: 仕様解釈、設計意図の理解、ドキュメント検索
入力: 論理的な仮説（例: 「このAPIは400エラーを返すべきではない」）
出力: 仮説の検証結果（真／偽）、仕様上の期待動作、証拠となる仕様記述
使用するツール: specDocFetchTool, apiSchemaValidatorTool, docSearchTool
処理フロー:
  1. 仮説を受け取る
  2. 関連する仕様書・設計ドキュメントを検索
  3. 仕様上の期待動作を特定
  4. 仮説と仕様を照合して検証

// ソースコード確認エージェント
エージェント名: Source Code Analysis Agent
ID: source-code-agent
目的: 「コードはこう動くはず」「この変更が原因のはず」という仮説を検証する
専門領域: コード解析、変更履歴追跡、コードフロー理解
入力: 論理的な仮説（例: 「この関数でnullチェックが漏れているはず」）
出力: 仮説の検証結果、関連コードスニペット、変更履歴、潜在的な問題箇所
使用するツール: codeSearchTool, gitHistoryTool, codeAnalysisTool
処理フロー:
  1. 仮説を受け取る
  2. 関連するコード箇所を検索・特定
  3. コードフローを解析
  4. 最近の変更履歴を確認
  5. 仮説を検証（コードが仮説通りか）

// 以下、同様
```

## 2.2 プリミティブ選択戦略の設計

スーパーバイザーがどのようにプリミティブ（エージェント、ワークフロー、ツール）を選択するかを設計します。※Mastraでは、スーパーバイザーが呼び出せる要素を「**プリミティブ**」と総称します：

* **エージェント**: 専門的なタスクを実行するサブエージェント
* **ワークフロー**: 定型的な処理フロー
* **ツール**: 個別の機能（API呼び出し、データ取得など）

**プリミティブの登録方法**:

スーパーバイザーに各プリミティブを登録する方法は異なります：

```
export const supervisor = new Agent({
  id: "supervisor",

  // ✅ サブエージェント: agentsプロパティで直接登録
  // ツール化は不要。LLMが自動的に呼び出し可能
  agents: {
    logAnalysis: logAnalysisAgent,
    database: databaseAnalysisAgent,
    hypothesis: hypothesisAgent
  },

  // ✅ ワークフロー: workflowsプロパティで直接登録
  // こちらもツール化不要
  workflows: {
    fullAnalysis: fullIncidentAnalysisWorkflow
  },

  // ✅ ツール: toolsプロパティで登録
  tools: {
    logFetch: logFetchTool,
    dbQuery: dbQueryTool
  }
});
```

**重要**: サブエージェントやワークフローは**ツール経由で呼び出す必要はありません**。  
スーパーバイザーのLLMが、各プリミティブの`description`を読んで、適切なものを自動的に選択・呼び出します。

**選択戦略の要素**:

1. **説明の質**: 各プリミティブの明確な説明（`description`）
2. **スキーマの明確性**: 入出力スキーマが明確
3. **優先順位**: 重複する機能がある場合の選択基準
4. **組み合わせパターン**: 複数のプリミティブを組み合わせる場合

**設計のガイドライン**:

スーパーバイザーは各プリミティブの`description`を読んで、どれを使うか判断します。そのため、descriptionは「何をするか」はもちろん、「**いつ使うか**」が明確である必要があります。

```
// ---------------------------
// エージェントの例
// ---------------------------
// ✅ GOOD: 明確で具体的な説明
description: `アプリケーションログを解析してエラー、警告、異常パターンを特定する
              専門エージェントです。システムログで何が起きたかを調査する必要が
              ある場合に使用してください。`

// ❌ BAD: 曖昧な説明
description: `ログを解析します`

// ---------------------------
// ワークフローの例
// ---------------------------
// ✅ GOOD: 具体的な使用条件を記載
description: `インシデント分析の全パイプラインを実行するワークフローです。
              ユーザーがインシデントIDまたはタイムスタンプを提供した場合に
              使用してください。`

// ❌ BAD: いつ使うか不明確
description: `インシデント分析`

// ---------------------------
// ツールの例
// ---------------------------
// ✅ GOOD: ツールの具体例
description: `指定されたサービスのデプロイ履歴を取得するツールです。
              最近のデプロイがインシデントと関連しているか確認したい場合に
              使用してください。デプロイイベントのタイムスタンプ、バージョン、
              変更内容を返します。`
```

## 2.3 データフローとインテグレーションの設計

エージェント間のデータの流れと、外部システムとの統合を設計します。

**データフローの観点**:

1. **入力データ**: 各エージェントが必要とするデータ
2. **出力データ**: 各エージェントが提供するデータ
3. **データ共有**: エージェント間で共有されるデータ
4. **外部システム**: API、データベース、ログシステムなど

例えば、今回の本番障害解析システムで考えると以下のようになります。

```
データフロー:
1. ユーザー → Supervisor
   - 障害報告（サービス名、発生時刻、症状）

2. Supervisor → Log Analysis Agent
   - サービス名、時間範囲

3. Log Analysis Agent → ログシステム API
   - ログクエリ

4. Log Analysis Agent → Supervisor
   - エラーサマリー、異常パターン

5. Supervisor → Config Check Agent
   - サービス名、時間範囲

6. Config Check Agent → デプロイシステム API
   - デプロイ履歴クエリ

7. 両エージェントの結果 → Hypothesis Agent
   - 統合された調査結果

8. Hypothesis Agent → Supervisor
   - 根本原因、推奨対策

9. Supervisor → ユーザー
   - 包括的な障害分析レポート
```

## 2.4 メモリ戦略の設計

エージェントネットワークでは、メモリが必須です。タスク履歴を保存し、タスクの完了判定に使用されます。

**メモリ設計のポイント**:

1. **スレッド管理**: ユーザー／セッションごとのスレッド
2. **リソース管理**: タスクごとのリソース識別子
3. **履歴保持**: 会話履歴とタスク履歴
4. **状態管理**: 進行中のタスク状態
5. **構造化データの保存**: 仮説、調査結果、事実などを体系的に保存

例えば、今回の本番障害解析システムで考えると以下のようになります。

```
メモリ戦略:
- スレッドID: ユーザーID + セッションID
- リソースID: インシデントID
- 保存内容:
  - 障害報告の詳細
  - 各エージェントの調査結果
  - 仮説と検証結果
  - 最終的な根本原因分析
```

### 仮説管理とループ防止のためのメモリ設計

例えば今回のような複雑な障害解析では、「過去に調べて違うと判明した仮説を再度調べてしまう」ことを防ぐため、メモリ内で仮説の状態を管理することが重要です。

**仮説管理メモリの構造**:

```
// メモリに保存する構造化データ
interface InvestigationMemory {
  // 重要な事実: 調査で判明した確定情報
  keyFacts: Array<{
    id: string;
    timestamp: Date;
    source: string;        // どのエージェントが発見したか
    category: string;      // "error" | "config" | "performance" | "data"
    description: string;
    evidence: string;      // 証拠（ログ、コードスニペットなど）
    confidence: number;    // 0-1の信頼度
  }>;

  // 現在調査中の仮説
  activeHypotheses: Array<{
    id: string;
    hypothesis: string;
    basedOnFacts: string[];  // 根拠となるkeyFactsのID
    priority: number;         // 1-5の優先度
    createdAt: Date;
    investigationPlan: string;
  }>;

  // 潰れた仮説（検証済みで否定されたもの）
  rejectedHypotheses: Array<{
    id: string;
    hypothesis: string;
    rejectedAt: Date;
    reason: string;           // なぜ違うと判明したか
    evidence: string;          // 否定の証拠
    investigatedBy: string;    // どのエージェントが調査したか
  }>;

  // 確定した根本原因（検証完了した仮説）
  confirmedCauses: Array<{
    id: string;
    cause: string;
    confirmedAt: Date;
    evidence: string[];
    impact: string;
    recommendedAction: string;
  }>;
}
```

**メモリ検索の活用**:

```
// エージェントがメモリから過去の仮説を検索
const checkPreviousInvestigation = async (hypothesis: string) => {
  // セマンティック検索で類似の仮説を確認
  const similarRejected = await memory.search({
    query: hypothesis,
    filter: {
      type: "rejected_hypothesis"
    },
    limit: 5
  });

  if (similarRejected.length > 0) {
    return {
      shouldInvestigate: false,
      reason: `Similar hypothesis was already rejected: ${similarRejected[0].reason}`
    };
  }

  return { shouldInvestigate: true };
};
```

**実装時の注意点**:

1. **構造化データの保存方法**:
   * メッセージのメタデータとして保存
   * または専用のデータストアと連携
2. **検索の活用**:
   * セマンティック検索で類似仮説を検出
   * タグやカテゴリでフィルタリング
3. **可視化**:
   * 調査の進捗状況をユーザーに提示
   * 「現在3つの仮説を調査中、2つが否定済み」など

# Phase 3：実装準備

## 3.1 必要なツールの実装

各エージェントが使用するツールを実装します。  
シングルエージェントの場合と同じなので、詳細は割愛します。

## 3.2 サブエージェントの実装

各専門エージェントを実装します。  
シングルエージェントの場合と同じなので、詳細は割愛します。

## 3.3 ストレージの準備

ネットワークの承認機能や suspend／resume を使う場合、ストレージが必要です。

**ストレージ設定**:

```
// src/mastra/index.ts
import { Mastra } from "@mastra/core/mastra";
import { LibSQLStore } from "@mastra/libsql";

export const mastra = new Mastra({
  storage: new LibSQLStore({
    id: "mastra-storage",
    url: "file:./mastra.db"  // 本番環境では適切な URL を使用
  })
});
```

# Phase 4：実装

## 4.1 スーパーバイザーの実装

スーパーバイザー（ルーティングエージェント）を実装します。

**実装のポイント**:

1. **包括的な指示**: スーパーバイザーの役割を明確に
2. **全プリミティブの登録**: サブエージェント、ワークフロー、ツール
3. **メモリの設定**: 必須
4. **適切なモデル**: 複雑な推論が必要なので高性能モデルを推奨

**実装例**:

```
// agents/incident-supervisor.ts
import { Agent } from "@mastra/core/agent";
import { Memory } from "@mastra/memory";
import { LibSQLStore } from "@mastra/libsql";

import { logAnalysisAgent } from "./log-analysis-agent";
import { specCheckAgent } from "./spec-check-agent";
import { sourceCodeAgent } from "./source-code-agent";
import { databaseAgent } from "./database-agent";
import { fileSystemAgent } from "./file-system-agent";
import { configCheckAgent } from "./config-check-agent";
import { hypothesisAgent } from "./hypothesis-agent";

export const incidentSupervisor = new Agent({
  id: "incident-supervisor",
  name: "Incident Analysis Supervisor",
  instructions: `
    あなたは本番障害解析を統括するスーパーバイザーです。
    専門エージェントチームを指揮して、障害の根本原因を特定します。

    ## あなたのチーム構成

    1. **ログ解析エージェント (logAnalysis)**:
       - ログファイルからエラー、警告、異常パターンを抽出

    2. **仕様確認エージェント (specCheck)**:
       - 「仕様上こう動くべき」という仮説を検証
       - 仕様書・設計ドキュメントを参照

    3. **ソースコード確認エージェント (sourceCode)**:
       - 「コードはこう動くはず」という仮説を検証
       - コード解析、変更履歴の確認

    4. **データベース確認エージェント (database)**:
       - 「このデータが存在する／しない」という仮説を検証
       - DB定義書を参照してSQLを構築・実行

    5. **ファイル確認エージェント (fileSystem)**:
       - 「設定値が○○のはず」という仮説を検証
       - 設定ファイル、パーミッションの確認

    6. **構成確認エージェント (configCheck)**:
       - 「この時点でデプロイがあったはず」という仮説を検証
       - デプロイ履歴、構成変更の確認

    7. **仮説検証エージェント (hypothesis)**:
       - 事実から仮説を立案し、根本原因を特定

    ## メモリ管理（重要）

    会話の中で以下の情報を構造化して記録・参照してください：

    1. **keyFacts（重要な事実）**:
       - 各エージェントの調査で判明した確定情報を記録
       - 既に判明している事実を繰り返し調査しない

    2. **activeHypotheses（現在の仮説）**:
       - 現在調査中の仮説を明確に記録
       - 仮説ごとに根拠となる事実IDを紐付け
       - 優先度をつけて調査順序を管理

    3. **rejectedHypotheses（潰れた仮説）**:
       - 検証の結果、否定された仮説を記録
       - なぜ違うと判明したかの理由を明記
       - **重要**: 過去に調査して否定された仮説は再調査しない

    4. **confirmedCauses（確定した原因）**:
       - 検証完了した根本原因を記録

    ## 障害解析の進め方

    ユーザーから障害報告を受け取ったら、以下のフェーズで進めてください：

    ### 【フェーズ1: 初期調査】
    1. ログ解析エージェントを呼び出してエラー内容を確認
    2. 判明した事実（エラーメッセージ、タイムラインなど）をkeyFactsに記録

    ### 【フェーズ2: 仮説立案】
    3. 収集した事実を元に、仮説検証エージェントを呼び出して複数の仮説を立案
    4. 各仮説をactiveHypothesesに記録
       - 例: 「DBのuser_idカラムにnullが入っている」
       - 例: 「v2.1.0デプロイ時にmax_connections設定が変更された」
       - 例: 「config.jsonのtimeout値が小さすぎる」

    ### 【フェーズ3: 検証】
    5. 各仮説を検証するために、適切な専門エージェントに**論理的な仮説**を渡す：
       - DB仮説 → databaseエージェント
         「user_id=123のレコードのemailカラムがnullになっているか確認」
       - デプロイ仮説 → configCheckエージェント
         「14:00-15:00の間にデプロイがあり、max_connectionsが変更されたか確認」
       - 設定仮説 → fileSystemエージェント
         「config.jsonのrequest_timeoutが30より小さいか確認」
       - コード仮説 → sourceCodeエージェント
         「この関数でnullチェックが漏れているか確認」
       - 仕様仮説 → specCheckエージェント
         「このAPIは400エラーを返すべきではないか確認」

    6. 検証結果を受け取る：
       - 真と判明 → confirmedCausesに移動、証拠を記録
       - 偽と判明 → rejectedHypothesesに移動、理由を記録
       - 新しい事実が判明 → keyFactsに追加

    ### 【フェーズ4: 反復】
    7. 新しい事実や検証結果から、追加の仮説が浮上した場合：
       - rejectedHypothesesを確認（類似仮説を調べていないか）
       - 新仮説をactiveHypothesesに追加
       - 再び検証フェーズへ

    ### 【フェーズ5: 結論】
    8. すべての仮説が検証されたら、仮説検証エージェントに結果を渡して根本原因を特定
    9. 包括的な障害分析レポートを生成

    ## 効率的な調査のために

    - **同じ調査を繰り返さない**: 各フェーズでメモリを確認
    - **事実ベースで仮説を立てる**: keyFactsを根拠に
    - **否定された仮説のパターンから学習する**: rejectedHypothesesを活用

    ## レポート形式

    # インシデント概要
    [障害の簡潔な概要]

    # タイムライン
    [時系列での出来事]

    # 根本原因
    [特定された根本原因と証拠]

    # 影響範囲
    [影響の範囲と深刻度]

    # 推奨対策
    [即時対応と再発防止策]

    # 調査履歴
    - 確認した仮説: [activeHypotheses]
    - 否定された仮説: [rejectedHypotheses]
    - 判明した重要事実: [keyFacts]
  `,
  model: "openai/gpt-5.2",  // 複雑な推論が必要なので高性能モデル

  // サブエージェントを登録（ツール化は不要）
  // 登録されたエージェントは、スーパーバイザーのLLMが自動的に呼び出し可能
  agents: {
    logAnalysis: logAnalysisAgent,
    specCheck: specCheckAgent,
    sourceCode: sourceCodeAgent,
    database: databaseAgent,
    fileSystem: fileSystemAgent,
    configCheck: configCheckAgent,
    hypothesis: hypothesisAgent
  },

  // メモリは必須
  memory: new Memory({
    storage: new LibSQLStore({
      id: "incident-memory",
      url: "file:./incident-memory.db"
    })
  })
});
```

**重要な仕組み**:

スーパーバイザーは、登録されたサブエージェントを**ツール経由ではなく直接呼び出します**。

```
// ❌ 間違い: サブエージェントをツール化する必要はありません
const agentTool = createTool({
  id: "call-log-agent",
  execute: async () => {
    // これは不要
  }
});

// ✅ 正しい: agentsプロパティに直接登録
const supervisor = new Agent({
  agents: {
    logAnalysis: logAnalysisAgent  // これで十分
  }
});
```

スーパーバイザーのLLMは：

1. 各サブエージェントの`description`を読む
2. ユーザーのリクエストに応じて適切なエージェントを選択
3. 自動的にそのエージェントを呼び出す
4. 結果を受け取って次の判断をする

この仕組みにより、複雑なルーティングロジックを書かなくても、LLMが動的に適切なエージェントを選べます。

---

いかがでしたしょうか。「スーパーバイザー＋サブエージェント」のパターンは実践の現場でも結構使っていますし、作っていて楽しいです。

[>> 次回 : (12) コンテキスト・エンジニアリングを理解する](https://zenn.dev/shiromizuj/articles/e1e0717a663845)
