---
id: "2026-04-10-gemini-enterprisegemini-31-x-claude-46-を連携させて企画マージ-01"
title: "【Gemini Enterprise】Gemini 3.1 x Claude 4.6 を連携させて「企画→マージ」を自動化してみた"
url: "https://zenn.dev/google_cloud_jp/articles/412b26038374a9"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-04-10"
date_collected: "2026-04-11"
summary_by: "auto-rss"
---

![](https://static.zenn.studio/user-upload/77bdbed8a7f1-20260407.png)

## はじめに

「在庫数を商品リストの画面に追加してほしい」── たった一言の要件から、PRD の作成、GitHub Issue の起票、コードの実装、Pull Request の作成、そしてマージまで。通常であれば、要件を PRD にまとめ → Issue を起票し → エンジニアが既存のコードを解析 → 実装 → レビュー → マージという多段階のプロセスを経るため、1 つの機能追加に数時間〜数日を要します。

本記事では、**Gemini Enterprise をエージェントハブとして、Agent Designer で作成した PRD Agent（Gemini 搭載）と、ADK で開発した Coding Agent（Claude 搭載）を連携させ、企画からマージまでを一気通貫で自動化する**アプローチを紹介します。

ポイントは 3 つです：

1. **Gemini Enterprise で複数エージェントを呼び出し・連携できる**
2. **ADK エージェントは Gemini 以外にも Claude モデルを搭載できる**
3. **Gemini Enterprise 上でマルチエージェント × マルチモデルの開発ワークフローが実現できる**

---

## 1. デモ：薬局向け発注アプリへの機能追加

まず、今回構築したデモの全体像を紹介します。

### シナリオ

薬品の卸業者が作成した、薬局（小売店）向けの「薬品発注アプリ」を例にします。現在は、発注対象の商品名・商品コードのみが表示されていますが、これに、「卸業者側で確保している在庫数」と「在庫切れ商品に対する次回入荷予定日」の表示機能を追加するという要件を想定します。

### Before

商品リストには商品名と商品コードのみが表示されています。薬局の人がこの画面から発注すると、実際には在庫切れですぐに商品が届かないことがあります。この課題の解決が必要です。

![商品リスト - 変更前：商品名と商品コードのみ表示](https://static.zenn.studio/user-upload/dbb991560368-20260407.png)

### After

在庫数と入荷予定日が追加され、在庫切れの商品は視覚的に強調されます。

![商品リスト - 変更後：在庫数と入荷予定日が追加](https://static.zenn.studio/user-upload/50951de6fb4d-20260407.png)

各商品の在庫推移をグラフで可視化する機能も追加されました。

![在庫推移グラフ](https://static.zenn.studio/user-upload/4bc37b468a91-20260407.png)

### 実行フロー

1. **要件入力**: 「在庫数と入荷予定日を商品リストに追加してほしい」
2. **PRD Agent**: ユーザーの要件をヒアリングし PRD に変換 → サブエージェント（GitHub Issue Agent）に委譲して GitHub Issue を自動作成
3. **ADK Coding Agent**: Gemini Enterprise 上で `@Coding Agent` とメンションして実装を指示
   * Issue を読み取り
   * 既存コードを分析
   * 新規ブランチを作成
   * 最小限の変更で機能を実装
   * PR を自動作成
4. **PRD Agent**: Gemini Enterprise 上で PRD Agent にマージ処理を指示すると、PR の変更内容を Issue の要件と照合し、合致していることを確認した上でマージを実施

### PRD Agent に生成された GitHub Issue

![PRD Agent が自動生成した GitHub Issue](https://static.zenn.studio/user-upload/53545076dbbe-20260407.png)

### ADK Coding Agent が生成した Pull Request

![ADK Coding Agent が自動生成した Pull Request](https://static.zenn.studio/user-upload/be9951ec7608-20260407.png)

要件を伝えるだけで、PRD → Issue → 実装 → PR → マージが自動完結されます。マージする前に、人間がPRの内容を確認することもできます。

<https://youtu.be/ByJT-vnGyzs>

---

## 2. Gemini Enterprise：エージェントハブとしてのオーケストレーション

### 全体フロー

![](https://static.zenn.studio/user-upload/3e37df3a829a-20260407.png)

今回のデモの核心は、**Gemini Enterprise がエージェントハブとして機能し、複数のエージェントを 1 つのチャットプラットフォーム上で呼び出し・連携させている**点です。

| エージェント | 基盤 | モデル | 役割 |
| --- | --- | --- | --- |
| PRD Agent | Agent Designer | Gemini 3.1 Pro | ユーザーと対話して PRD を生成、PR レビュー・マージ |
| GitHub Issue Agent | Agent Designer（サブエージェント） | Gemini 3.1 Pro | PRD を技術要件に分解し Issue を起票 |
| Coding Agent | ADK → Agent Engine | Gemini or **Claude** | Issue → 実装 → PR 作成 |

Gemini Enterprise のチャット上で、ユーザーが `@` メンションを使ってエージェントを切り替えることで連携が実現します。`PRD Agent` が要件を固めて Issue を作成した後、ユーザーが `@Coding Agent` を呼び出して実装を引き継ぐというように、**1 つのプラットフォーム上でマルチエージェント × マルチモデル**のワークフローが完結します。

### なぜ Agent Designer + ADK の分離構成にしたか

* **Agent Designer 単体でコーディングまでやらせない理由**: Agent Designer はノーコードで手軽にエージェントを作れますが、GitHub API との複雑なインタラクション（ブランチ作成、ファイル操作、PR作成）を行うには、ADK のツール定義の柔軟性が適しています。
* **ADK 単体で要件策定をやらせない理由**: 要件のヒアリングは対話的で反復的なプロセスです。Drive、Jira や GitHub などのコネクタを提供していて、データの横断検索を強みとする Gemini Enterprise のチャット UI と非エンジニア向けの UX が、この用途に適しています。

→ **Gemini Enterprise をエージェントハブとして、適材適所で Google Cloud のエージェントスタックを使い分ける**のが、企業向けのベストプラクティスです。

### Gemini Enterprise における Agent Designer の役割

Agent Designer は、Gemini Enterprise 上でエージェントを構築するための**ノーコード設計ツール**です。

![Agent Designer による親・子エージェントの設定画面](https://static.zenn.studio/user-upload/494c4f5bcf32-20260407.png)

* **PRD Agent（親）**: ユーザーと自然言語で対話しながら要件を明確化し、構造化された PRD を生成
* **GitHub Issue Agent（子）**: PRD を受け取り GitHub Issue を作成
* **コネクタ**: Drive、Google Search、GitHub
* **モデル**: Gemini 3.1 Pro を使用

Agent Designer は**サブエージェント**の概念をサポートしており、上記のように親エージェントが子エージェントに自律的にタスクを委譲できます。

PRD エージェントへのプロンプト

```
あなたは要件策定を支援するプロダクトマネージャーAIです。
ユーザー（事業部門/LoB）から機能要望を聞き取り、開発チームが実装できるPRD（製品要求仕様書）を作成します。

## ワークフロー
1. **ヒアリング** — ユーザーの要望を聞き、以下を明確にする：
    * 誰が使うか（ペルソナ）
    * 何を解決したいか（課題）
    * どんな機能が必要か（要件）
    * 優先度や制約
2. **PRD生成** — 以下のフォーマットでPRDを作成：
（略）
3. **確認** — PRDをユーザーに見せて確認を取る
4. **Issue作成** — 確認が取れたら、サブエージェントにPRDを渡してGitHub Issueを作成させる

## ガイドライン
* ビジネスユーザーでも理解できるように、専門用語を避けてわかりやすく質問する
* 曖昧な要望は具体化するまで深掘りする
* 一度に多くの質問をせず、会話を通じて段階的に情報を引き出す
* PRDは日本語で作成する
```

GitHub Issue Agent へのプロンプト

```
あなたはプロダクトマネージャーAIです。
PRD（製品要求仕様書）を受け取り、GitHub Issueとして開発チームに伝える役割を担います。

## ワークフロー
1. **PRD分析** — PRDを読み、機能を実装単位に分解する
2. **Issue作成** — 各機能について以下の形式でGitHub Issueを作成：
（略）
```

### ADK Coding Agent の役割

ADK（Agent Development Kit）で構築したコーディングエージェントが、Gemini Enterprise 上でユーザーから呼び出され、GitHub Issue を起点に自動実装を行います。

**ツール一覧:**

| ツール | 説明 |
| --- | --- |
| `read_issue` | GitHub Issue を番号で取得 |
| `list_files` / `list_files_recursive` | リポジトリ内のファイル一覧 |
| `read_file` | ファイル内容を取得 |
| `search_code` | GitHub Code Search API でコード検索 |
| `create_branch` | 新しいブランチを作成 |
| `commit_file` / `commit_files` | コミット（単体 / 一括） |
| `create_pull_request` | PR を作成 |
| `get_diff` / `list_pull_requests` / `add_pr_comment` | PR レビュー関連 |

このエージェントは Vertex AI **Agent Engine** 上にデプロイすることで、エンタープライズ要件に対応したマネージド運用が可能です。

### Instruction（プロンプト）の設計ポイント

ADK エージェントの振る舞いは `instruction` で定義します。今回の Coding Agent では、以下の方針で Instruction を設計しました。

#### 「最小限の変更に徹する」ガードレール

エージェントに自由にコードを書かせると、頼んでいないリファクタリングや「改善」を入れてしまうことがあります。実際の開発初期には、Instruction にこの指示がなかったため、エージェントが既存コードの命名規則を勝手に変更し、不要な diff が大量に発生したことがありました。

```
# agent.py の instruction より抜粋
- 機能を実装する際は、最小限の変更にとどめてください。
  バグ修正のために周囲のコードを意図しない破壊的変更したり、
  単純な機能のために余分な設定可能性を追加したりしないでください。
- 要求されていない機能を追加しないでください
  （"improvements" を勝手に加えない）。
```

#### 「必ずコードを読んでから行動する」ルール

LLM は既存コードの構造を確認せずに実装を始めてしまうことがあり、結果として既存のパターンと矛盾したコードを生成するリスクがあります。

```
# agent.py の instruction より抜粋
- 何かのアクションを起こす前に、まずはリポジトリ内の Issue と
  コードを必ず読んでください。
- `search_code` や `list_files_recursive` を駆使して
  既存のコードの構造を把握します。
- 変更を加えるファイルの内容は、必ず `read_file` で
  事前に確認してください。
```

#### Git の安全操作とセキュリティ

デフォルトブランチへの直接コミットを禁止し、常にブランチを切る運用をエージェントに強制します。またOWASP Top 10 の脆弱性を混入させないよう明示的に指示しています。

これらのガードレールは、エージェントを本番環境で運用する際に不可欠です。**プロンプトの設計次第でエージェントの品質が大きく変わる**ため、お客様への導入支援でも最も時間をかけるポイントのひとつです。

---

## 3. マルチモデル：ADK で Gemini 以外のモデルを搭載する

前述のとおり、今回のデモでは PRD Agent（Gemini）が企画・マネジメントを担当し、ADK Coding Agent が実装を担当しています。ここで重要なのは、**ADK Coding Agent は Gemini 以外のモデルも搭載できる**という点です。

エージェント開発では「要件策定」には対話に強いモデル、「コーディング」には論理的推論に強いモデルなど、**タスクに応じてモデルを使い分ける構成**が理想的です。Gemini Enterprise をエージェントハブとすることで、各エージェントに最適なモデルを割り当てることができます。

### ADK のモデル非依存設計

ADK は**フレームワークレベルでモデル非依存**に設計されています。今回の Coding Agent の実コードでは、環境変数 1 つでモデルを切り替えています：

```
# ADK での例：環境変数でモデルを切り替え
import os
from google.adk.agents import Agent

DEFAULT_MODEL = "gemini-2.5-pro"
MODEL = os.environ.get("CODING_AGENT_MODEL", DEFAULT_MODEL)

root_agent = Agent(
    name="coding_agent",
    model=MODEL,  # gemini-2.5-pro / gemini-3.1-pro-preview / claude-opus-4-6
    description="GitHub Issue を読んで実装し、Pull Request を作成するエージェント",
    instruction=INSTRUCTION,
    tools=[read_issue, list_files, read_file, search_code, ...],
)
```

Claude を使用する場合は、追加の依存関係として `anthropic[vertex]` のインストールも必要です：

```
pip install anthropic[vertex]
```

もしくは requirements.txt に記載

```
google-adk>=1.27.0
PyGithub>=2.1.1
anthropic>=0.43.0
```

Vertex AI のマルチモデル統合プラットフォームとしてのメリット（統一課金、共通セキュリティ、シームレスな切り替え）や Model Garden でのセットアップについては、[前回記事](https://zenn.dev/google_cloud_jp/articles/b65dc4d6df7f34)で詳しく解説しています。

### 企業でマルチモデル対応が求められるケース

モデル非依存なエージェント基盤を構築することは、以下のような企業要件に対応する上で重要です：

* **ベンダーロックイン回避**: 特定モデルへの依存を避け、将来の選択肢を確保する
* **A/B テスト・比較検証**: タスクごとに複数モデルで精度やコストを比較し、最適なモデルを選定する
* **コンプライアンス要件**: 組織のポリシーやデータの性質に応じて利用するモデルを切り替える

## 4. Agent Engine デプロイ時の Tips

### global リージョン制約と回避策

Gemini 3 系や Claude は `global` リージョンでのみ利用可能という制約があります。一方、Vertex AI Agent Engine は現在 `global` リージョンにデプロイできません。

この制約を回避するには、ADK Agent の**環境変数でモデル呼び出し時のリージョンを分離**します：

```
# .env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
CODING_AGENT_MODEL=gemini-3.1-pro-preview  # または claude-opus-4-6
GOOGLE_CLOUD_LOCATION=global             # モデル呼び出しは global
```

デプロイ時は `us-central1` を指定します。`--staging_bucket` にはデプロイ時の一時ファイル格納先として GCS バケットを指定してください：

```
adk deploy agent_engine \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=us-central1 \
    --display_name="coding-agent" \
    --env_file=.env \
    --otel_to_cloud \
    --staging_bucket=gs://your-bucket \
    coding_agent
```

#### 内部の仕組み

* `--region us-central1` → Agent Engine のデプロイ先リージョン
* `GOOGLE_CLOUD_LOCATION=global` → エージェントがモデル API を呼び出す際のリージョン
* `GOOGLE_CLOUD_AGENT_ENGINE_LOCATION` → Agent Engine が自動設定（SessionService 等に使用）

### オブザーバビリティ

上記のデプロイコマンドに含まれる `--otel_to_cloud` オプションを指定すると、エージェントのトレース情報が **Cloud Trace** に自動送信されます。

* エージェントの各ステップ（Issue 読み込み → コード分析 → 実装 → PR 作成）の所要時間を可視化
* ツール呼び出しのレイテンシやエラー率のモニタリング
* 本番運用時のデバッグや品質改善に活用

エンタープライズでのエージェント運用では、「エージェントが何をしているか分からない」状態は許容されません。Cloud Trace との統合により、エージェントの動作を透明化できます。

---

## 5. 企業導入時の考慮点

### セキュリティ・ガバナンス

Agent Engine 上でデプロイすることで、以下のエンタープライズ要件に対応できます。

| 観点 | Agent Engine の対応 |
| --- | --- |
| ネットワーク | VPC Service Controls 対応 |
| 暗号化 | CMEK（顧客管理暗号鍵）対応 |
| 監査 | Cloud Logging / Cloud Trace 連携 |
| 認証 | IAM によるアクセス制御 |

### 巨大なコードベースへの適用課題とスケーラビリティ

本デモは小規模なリポジトリを対象としていますが、エンタープライズ規模の巨大なコードベースに本エージェントを適用する場合、以下の課題を考慮し、アーキテクチャを工夫する必要があります。

* **コンテキストの枯渇（迷子リスク）**:  
  エージェントがファイル探索や読み込みを繰り返しすぎると、LLM のコンテキスト上限を圧迫し、本来の「Issue の要件」や「最小限の変更」というルールを忘れてしまう（Lost in the middle）リスクがあります。
* **検索の最適化**:  
  巨大なリポジトリでは `list_files_recursive` などによる力技の探索は非効率です。将来的な拡張として、リポジトリ全体をインデックス化して RAG（検索拡張生成）を用いたり、Gemini Code Assist などの文脈把握に特化したツールをエージェントに統合する最適化が求められます。

---

## まとめ

本記事では、Gemini Enterprise × ADK による「企画→マージ」自動化のアプローチを紹介しました。

### Key Takeaways

1. **Gemini Enterprise × ADK で企画→マージを自動化**

   * PRD Agent で要件策定 → ADK Coding Agent で自動実装 → PRD Agent で PR レビュー・マージ
   * 要件からマージまで一気通貫で自動完結
2. **Vertex AI のマルチモデル基盤 × ADK のモデル非依存設計**

   * Gemini と Claude を単一プラットフォームで提供、統一された課金・セキュリティ
   * ADK は簡単にパートナーや OSS モデル切り替え可能で、ベンダーロックイン回避
3. **Agent Engine でマネージド運用**

   * VPC-SC、CMEK、Cloud Trace 連携
   * エンタープライズ要件に対応

**Gemini Enterprise はエージェントハブとして、Agent Designer で構築したサブエージェント（Gemini 搭載）や ADK エージェント（Claude 搭載）を統合し、マルチエージェント × マルチモデルの開発ワークフローを 1 つのプラットフォーム上で実現します。** さらに Agent Engine によるマネージド運用と Vertex AI の統合基盤により、企業の多様な要件にも柔軟に対応できます。

---

## 参考リンク

---

*本記事の内容は個人の見解であり、所属する企業を代表するものではありません。また、掲載時点の情報に基づいており、最新の仕様とは異なる場合があります。*
