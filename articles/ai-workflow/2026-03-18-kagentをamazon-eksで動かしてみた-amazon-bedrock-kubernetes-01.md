---
id: "2026-03-18-kagentをamazon-eksで動かしてみた-amazon-bedrock-kubernetes-01"
title: "KagentをAmazon EKSで動かしてみた - Amazon Bedrock × Kubernetes × Agentic AI"
url: "https://zenn.dev/aws_japan/articles/1916c8486dda8f"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "LLM", "GPT", "zenn"]
date_published: "2026-03-18"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

## はじめに

「Kubernetesクラスターで障害が起きたとき、エラーログをコピーしてChatGPTに貼り付けて…」という経験、ありませんか？

AIは賢いけれど、あなたのクラスターの中身は見えていません。ログもメトリクスも、Podの状態も知らない。あなたが「コピペの仲介人」になっているだけです。

この課題を解決するのが **Kagent** です。KubernetesネイティブなAgentic AIフレームワークで、AIエージェントがクラスター内部から直接操作・診断を行えます。

本記事では、Amazon EKS上にKagentをデプロイし、**Amazon Bedrock経由のClaude**をLLMバックエンドとして、実際にKubernetesエージェントと対話してみた検証結果をお伝えします。

## Kagentとは

[Kagent](https://kagent.dev/) は、Solo.io が開発し CNCF（Cloud Native Computing Foundation）に寄贈されたオープンソースの Agentic AI フレームワークです。Kubernetes上でAIエージェントを構築・デプロイ・管理するために設計されています。

### 従来のLLM活用との違い

| 観点 | 従来のLLM活用 | Kagent |
| --- | --- | --- |
| クラスターへのアクセス | なし（コピペで情報を渡す） | クラスター内部から直接アクセス |
| ツール連携 | なし | kubectl, Helm, Prometheus, Grafana等と連携 |
| コンテキスト | ユーザーが手動で提供 | クラスターの状態をリアルタイムに把握 |
| アクション実行 | ユーザーが手動で実行 | エージェントが直接実行可能 |

### アーキテクチャ

Kagentは以下の4つのコアコンポーネントで構成されています。

* **Controller**: Kubernetes ControllerとしてCRDを監視し、エージェントの実行に必要なリソースを管理
* **Engine**: Microsoft AutoGen（ADK）ベースのエージェント実行エンジン
* **UI**: エージェントの管理・対話を行うWebダッシュボード
* **CLI**: コマンドラインからエージェントを管理・実行するツール

### 3つのレイヤー

1. **Tools**: MCP（Model Context Protocol）スタイルの関数群。Podログの取得、Prometheusクエリ、マニフェスト生成など
2. **Agents**: ツールを使って自律的にタスクを計画・実行するシステム。Kubernetes CRD（`Agent`）として定義
3. **Framework**: 宣言的なAPI・Controller。UI / CLI / YAMLで管理可能

### 対応LLMプロバイダー

Kagentは多数のLLMプロバイダーをサポートしています。

* **Amazon Bedrock**（ネイティブサポート）
* OpenAI
* Anthropic（Claude 直接）
* Google Vertex AI（Gemini）
* Azure OpenAI
* Ollama
* その他OpenAI互換プロバイダー

今回の検証では **Amazon Bedrockのネイティブプロバイダー** を使用します。KagentはBedrockを `provider: Bedrock` として直接サポートしているため、IAMクレデンシャルだけで設定できるのがポイントです。

### プリビルトエージェント

Kagentにはすぐに使えるエージェントが10種類同梱されています。  
また、カスタムエージェントを作成することもできますので、後ほど詳しく解説します。

| エージェント名 | 役割 |
| --- | --- |
| k8s-agent | Kubernetesクラスターの操作・トラブルシューティング |
| helm-agent | Helmチャートの管理・操作 |
| istio-agent | Istioの運用・トラブルシューティング |
| observability-agent | Prometheus / Grafanaを使った監視 |
| promql-agent | 自然言語からPromQLクエリを生成 |
| cilium-debug-agent | Ciliumのデバッグ |
| cilium-manager-agent | Ciliumの管理 |
| cilium-policy-agent | Cilium Network Policyの生成 |
| kgateway-agent | kGateway（API Gateway）の管理 |
| argo-rollouts-agent | DeploymentからArgo Rolloutsへの変換 |

## 検証環境の構築

### 前提条件

* AWS CLI（設定済み）
* eksctl
* kubectl
* Helm 3
* Amazon Bedrockのモデルアクセス（Claudeモデルを有効化済み）

### Step 1: EKSクラスターの作成

`eksctl` でEKSクラスターを作成します。

```
eksctl create cluster \
  --name kagent-demo \
  --region us-west-2 \
  --version 1.31 \
  --nodegroup-name kagent-nodes \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 3
```

クラスターの作成には15〜20分ほどかかります。完了したら接続を確認しましょう。

```
NAME                                           STATUS   ROLES    AGE   VERSION
ip-192-168-58-138.us-west-2.compute.internal   Ready    <none>   2m    v1.31.14-eks-f69f56f
ip-192-168-85-165.us-west-2.compute.internal   Ready    <none>   2m    v1.31.14-eks-f69f56f
```

### Step 2: Kagent CRDsのインストール

KagentのCustom Resource Definitions（CRD）をインストールします。これにより `Agent`, `ModelConfig`, `ToolServer` などのカスタムリソースがKubernetes APIに追加されます。

```
helm install kagent-crds oci://ghcr.io/kagent-dev/kagent/helm/kagent-crds \
  --namespace kagent \
  --create-namespace
```

### Step 3: Kagentのインストール

Kagent本体をインストールします。初期インストール時はダミーのAPIキーで構いません（後からBedrockのModelConfigを適用します）。

```
helm install kagent oci://ghcr.io/kagent-dev/kagent/helm/kagent \
  --namespace kagent \
  --set providers.openAI.apiKey=dummy-key
```

### Step 4: Amazon Bedrock（Claude）の設定

ここがAWSユーザーにとって嬉しいポイントです。KagentはAmazon Bedrockをネイティブプロバイダーとしてサポートしているため、IAMクレデンシャルだけで設定できます。

まず、AWSクレデンシャルをKubernetes Secretとして作成します。

```
kubectl create secret generic bedrock-credentials -n kagent \
  --from-literal=AWS_ACCESS_KEY_ID=<your-access-key-id> \
  --from-literal=AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
```

次に、`ModelConfig` CRDを作成してBedrock上のClaudeモデルを指定します。

```
apiVersion: kagent.dev/v1alpha2
kind: ModelConfig
metadata:
  name: bedrock-claude
  namespace: kagent
spec:
  provider: Bedrock
  model: us.anthropic.claude-sonnet-4-20250514-v1:0
  apiKeySecret: bedrock-credentials
  bedrock:
    region: us-west-2
```

```
kubectl apply -f bedrock-modelconfig.yaml
```

ModelConfigが正しく受け入れられたか確認します。

```
kubectl get modelconfig -n kagent
```

```
NAME                   PROVIDER   MODEL
bedrock-claude         Bedrock    us.anthropic.claude-sonnet-4-20250514-v1:0
default-model-config   OpenAI     gpt-4.1-mini
```

ステータスも確認しておきましょう。

```
kubectl get modelconfig bedrock-claude -n kagent -o jsonpath='{.status.conditions}' | jq
```

```
[
  {
    "lastTransitionTime": "2026-03-17T09:16:55Z",
    "message": "Model configuration accepted",
    "reason": "ModelConfigReconciled",
    "status": "True",
    "type": "Accepted"
  }
]
```

### Step 5: エージェントのModelConfigをBedrockに切り替え

プリビルトエージェントはデフォルトで `default-model-config`（OpenAI）を使用しています。これをBedrockに切り替えます。

```
# k8s-agentをBedrock Claudeに切り替え
kubectl patch agent k8s-agent -n kagent \
  --type='json' \
  -p='[{"op": "replace", "path": "/spec/declarative/modelConfig", "value": "bedrock-claude"}]'

# helm-agentも同様に切り替え
kubectl patch agent helm-agent -n kagent \
  --type='json' \
  -p='[{"op": "replace", "path": "/spec/declarative/modelConfig", "value": "bedrock-claude"}]'
```

パッチ適用後、エージェントのPodが自動的に再起動されます。

```
kubectl get pods -n kagent -l app.kubernetes.io/name=k8s-agent
```

```
NAME                         READY   STATUS    RESTARTS   AGE
k8s-agent-74fc4476b8-b8bnr   1/1     Running   0          40s
```

### Step 6: デプロイの確認

すべてのPodが正常に起動しているか確認します。

```
kubectl get pods -n kagent
```

```
NAME                                              READY   STATUS    RESTARTS   AGE
argo-rollouts-conversion-agent-6474c6d694-q2pkw   1/1     Running   0          101s
cilium-debug-agent-6586f5cd9b-wds4m               1/1     Running   0          102s
cilium-manager-agent-5dbdb9f6c6-d8xl8             1/1     Running   0          101s
cilium-policy-agent-76f46977f5-plpqn              1/1     Running   0          101s
helm-agent-774d5d8755-79cm7                       1/1     Running   0          101s
istio-agent-59f8f44b8d-4k6fm                      1/1     Running   0          102s
k8s-agent-74fc4476b8-b8bnr                        1/1     Running   0          101s
kagent-controller-db6dcbc67-8c66t                 1/1     Running   0          107s
kagent-grafana-mcp-5885648b74-z5tp8               1/1     Running   0          107s
kagent-kmcp-controller-manager-7456557589-64mw6   1/1     Running   0          107s
kagent-querydoc-76bbb68588-dptlh                  1/1     Running   0          107s
kagent-tools-767dfbb7bc-fgjc6                     1/1     Running   0          107s
kagent-ui-5998bd9b65-q8jv2                        1/1     Running   0          107s
kgateway-agent-cb9dd6c6-skwsn                     1/1     Running   0          102s
observability-agent-686f696646-ff4jp              1/1     Running   0          101s
promql-agent-88d5499c7-lhz2p                      1/1     Running   0          101s
```

16個のPodがすべてRunningとなり、Kagent + Amazon Bedrockの環境が整いました。

## 動作検証：Bedrock Claude × k8s-agentと対話してみる

### ダッシュボードへのアクセス

KagentのWeb UIにアクセスするため、port-forwardを実行します。

```
kubectl port-forward svc/kagent-ui 8080:8080 -n kagent
```

ブラウザで `http://localhost:8080` を開くと、Kagentのダッシュボードが表示されます。

![](https://static.zenn.studio/user-upload/83e6f160e1dd-20260318.png)

### 検証1: CLIからクラスターの状態を聞いてみる

kagent CLIを使って、k8s-agentにクラスターの状態を聞いてみます。

```
# kagent CLIのインストール（macOS arm64の場合）
curl -L -o /usr/local/bin/kagent \
  https://github.com/kagent-dev/kagent/releases/download/v0.8.0-beta7/kagent-darwin-arm64
chmod +x /usr/local/bin/kagent

# Controller APIへのport-forward（別ターミナルで実行）
kubectl -n kagent port-forward service/kagent-controller 8083:8083

# エージェント一覧の確認
kagent get agent
```

```
+----+---------------------------------------+---------------------------+------------------+----------+
| #  | NAME                                  | CREATED                   | DEPLOYMENT_READY | ACCEPTED |
+----+---------------------------------------+---------------------------+------------------+----------+
| 1  | kagent/argo-rollouts-conversion-agent | 2026-03-17T18:16:04+09:00 | true             | true     |
| 2  | kagent/cilium-manager-agent           | 2026-03-17T18:16:04+09:00 | true             | true     |
| 3  | kagent/cilium-policy-agent            | 2026-03-17T18:16:04+09:00 | true             | true     |
| 4  | kagent/helm-agent                     | 2026-03-17T18:16:04+09:00 | true             | true     |
| 5  | kagent/k8s-agent                      | 2026-03-17T18:16:04+09:00 | true             | true     |
| 6  | kagent/cilium-debug-agent             | 2026-03-17T18:16:04+09:00 | true             | true     |
| 7  | kagent/istio-agent                    | 2026-03-17T18:16:04+09:00 | true             | true     |
| 8  | kagent/kgateway-agent                 | 2026-03-17T18:16:04+09:00 | true             | true     |
| 9  | kagent/observability-agent            | 2026-03-17T18:16:04+09:00 | true             | true     |
| 10 | kagent/promql-agent                   | 2026-03-17T18:16:04+09:00 | true             | true     |
+----+---------------------------------------+---------------------------+------------------+----------+
```

10個のエージェントがすべてACCEPTED。では、k8s-agentに質問してみましょう。

```
kagent invoke -t "クラスター内のNamespaceを一覧表示して" --agent k8s-agent
```

エージェントは内部で `k8s_get_resources` ツールを呼び出し、以下のような回答を返してくれました。

> クラスター内のNamespaceの一覧を表示しました。以下の5つのNamespaceが存在しています：
>
> 1. **default** (Active, 29分前作成) - デフォルトのNamespace
> 2. **kagent** (Active, 14分前作成) - Kagentのコンポーネント用
> 3. **kube-node-lease** (Active, 29分前作成) - ノードのリース情報管理
> 4. **kube-public** (Active, 29分前作成) - 公開リソース用
> 5. **kube-system** (Active, 29分前作成) - システムコンポーネント用
>
> すべてのNamespaceがActive状態で正常に動作しています。

なお、ダッシュボードでも同様にチャットで応答してくれます。  
![](https://static.zenn.studio/user-upload/bdfd8a3663db-20260318.png)

Amazon Bedrock経由のClaude Sonnet 4が、EKS上のKagentエージェントとして正しく動作していることが確認できました。

### 検証2: helm-agentにHelmリリースを聞いてみる

```
kagent invoke -t "クラスターにインストールされているHelmチャートを教えて" --agent helm-agent
```

> クラスターには現在2つのHelmリリースがインストールされています：
>
> | リリース名 | ネームスペース | ステータス | チャート |
> | --- | --- | --- | --- |
> | kagent | kagent | deployed | kagent-0.7.23 |
> | kagent-crds | kagent | deployed | kagent-crds-0.7.23 |
>
> 両方のリリースとも正常に動作している状態（deployed）です。

helm-agentは `helm_list_releases` ツールを呼び出して、全Namespaceのリリース情報を取得しています。自然言語で聞くだけで、`helm list -A` 相当の情報が整理された形で返ってくるのは便利ですね。

### 検証3: トラブルシューティング

ここからが本番です。意図的に障害を仕込んで、エージェントに診断・修復してもらいます。

まず、テスト用のリソースを作成します。

```
kubectl create namespace demo-app
kubectl create deployment nginx --image=nginx --replicas=3 -n demo-app
kubectl expose deployment nginx --port=80 --name=nginx-service -n demo-app
```

次に、Serviceのセレクターを壊します。

```
kubectl patch svc nginx-service -n demo-app \
  --type='json' \
  -p='[{"op": "replace", "path": "/spec/selector/app", "value": "nginx-broken"}]'
```

これでServiceからPodへのルーティングが切れました。エージェントに聞いてみましょう。

```
kagent invoke \
  -t "demo-app Namespaceのnginx-serviceに接続できないみたい。調べて直してくれる？" \
  --agent k8s-agent
```

エージェントは以下のような流れで問題を特定・修復します。

1. `k8s_describe_resource` でServiceの詳細を確認
2. `k8s_check_service_connectivity` で接続性をチェック
3. セレクターとPodのラベルの不一致を検出
4. `k8s_apply_manifest` でセレクターを正しい値にパッチ
5. 修復結果のサマリーを報告

人間が `kubectl describe svc` → `kubectl get pods --show-labels` → `kubectl patch svc ...` と手動で行う一連の作業を、エージェントが自律的に実行してくれます。

## Amazon Bedrockをネイティブプロバイダーとして使うメリット

今回の検証で特に良かったのは、KagentがAmazon Bedrockを **ネイティブプロバイダー** としてサポートしている点です。

### OpenAI互換エンドポイント方式との比較

KagentでBedrockを使う方法は2つあります。

| 方式 | provider設定 | 認証 | 設定の手軽さ |
| --- | --- | --- | --- |
| ネイティブBedrock（今回採用） | `provider: Bedrock` | IAMクレデンシャル | ◎ シンプル |
| OpenAI互換API | `provider: OpenAI` + `baseUrl` | Bedrock APIキー | △ APIキー発行が必要 |

ネイティブ方式なら、IAMクレデンシャルだけで完結します。Bedrock APIキーの発行やOpenAI互換エンドポイントのURL指定も不要です。

### AWSエコシステムとの親和性

* **IAM**: 既存のIAMポリシーでBedrockへのアクセスを制御できる
* **CloudTrail**: LLM呼び出しのログがCloudTrailに記録される
* **コスト管理**: AWS Cost Explorerで他のAWSサービスと一元管理
* **リージョン選択**: `bedrock.region` でモデルのリージョンを指定可能
* **モデル選択の柔軟性**: Claude, Titan, Llama, Mistralなど、Bedrockで利用可能な全モデルを切り替え可能

### ModelConfigの設定例

```
# Claude Sonnet 4（推論コスト重視）
apiVersion: kagent.dev/v1alpha2
kind: ModelConfig
metadata:
  name: bedrock-claude-sonnet
  namespace: kagent
spec:
  provider: Bedrock
  model: us.anthropic.claude-sonnet-4-20250514-v1:0
  apiKeySecret: bedrock-credentials
  bedrock:
    region: us-west-2
```

```
# Claude Haiku 4.5（低コスト・高速）
apiVersion: kagent.dev/v1alpha2
kind: ModelConfig
metadata:
  name: bedrock-claude-haiku
  namespace: kagent
spec:
  provider: Bedrock
  model: us.anthropic.claude-haiku-4-5-20251001-v1:0
  apiKeySecret: bedrock-credentials
  bedrock:
    region: us-west-2
```

エージェントごとに異なるモデルを割り当てることで、コストと性能のバランスを取ることもできます。例えば、トラブルシューティング用のk8s-agentにはSonnet、簡単なクエリ用のpromql-agentにはHaikuを割り当てる、といった運用が考えられます。

## こんなこともできる：Kagentの応用シナリオ

### カスタムエージェントの作成

プリビルトエージェントだけでなく、自分のユースケースに合わせたエージェントを作成できます。ダッシュボードの「Create Agent」から、以下を設定するだけです。

* **System Prompt**: エージェントの役割・振る舞いを自然言語で定義
* **Model**: 使用するModelConfig（Bedrock Claudeなど）
* **Tools**: エージェントに与えるツール群を選択

例えば「本番環境では読み取り専用操作のみ許可するエージェント」を作りたい場合、`k8s_delete_resource` や `k8s_apply_manifest` を外して、`k8s_get_pod_logs` や `k8s_describe_resource` だけを付与すれば実現できます。

### MCPサーバーによる拡張

KagentはMCP（Model Context Protocol）をサポートしており、カスタムツールをMCPサーバーとして追加できます。社内ツールや独自のAPIとエージェントを連携させることも可能です。

```
apiVersion: kagent.dev/v1alpha2
kind: ToolServer
metadata:
  name: custom-tool-server
  namespace: kagent
spec:
  url: "http://my-custom-mcp-server:8080"
```

### Prometheusとの連携

`observability-agent` を使えば、自然言語でメトリクスを問い合わせることができます。

```
過去1時間でCPU使用率が80%を超えたPodはある？
```

PromQLの構文を覚えなくても、意図を伝えるだけでメトリクスにアクセスできます。

## EKSで動かす際のポイント

### ノードサイズの選定

Kagentは複数のコンポーネント（Controller, UI, Tools, 各エージェント）をデプロイするため、最低でも `t3.medium`（2 vCPU / 4 GiB）× 2ノード程度は確保しておくのがおすすめです。今回の検証でも `t3.medium` × 2ノードで16個のPodが問題なく動作しました。

### IAMとRBACの考慮

EKS上でKagentを運用する場合、2つのレイヤーでの権限管理が必要です。

1. **IAM**: BedrockのモデルアクセスにはIAMポリシー（`bedrock:InvokeModel`）が必要
2. **Kubernetes RBAC**: エージェントが実行するKubernetes操作に対する権限

本番環境では最小権限の原則に基づいてカスタマイズすることを推奨します。

### クレデンシャルの管理

IAMクレデンシャルはKubernetes Secretとして管理されます。本番環境では以下の対策を検討してください。

* **IRSA（IAM Roles for Service Accounts）** の活用でアクセスキーの管理を不要に
* AWS Secrets Managerとの連携（External Secrets Operatorなど）
* Secretの暗号化（EKS Envelope Encryption）

### コスト面の注意

Kagentを通じたLLM呼び出しにはBedrock利用料が発生します。特にトラブルシューティングのような複数ステップの対話では、トークン消費量が大きくなる場合があります。開発・検証環境での利用から始めて、コスト感を掴んでから本番導入を検討するのが良いでしょう。

## まとめ

Kagentは「AIにクラスターの目と手を与える」フレームワークです。

* **Kubernetesネイティブ**: CRDベースの宣言的な管理。Kubernetesの流儀に沿った設計
* **Amazon Bedrockネイティブサポート**: IAMクレデンシャルだけで設定完了。AWSエコシステムとの親和性が高い
* **すぐに使える**: 10種類のプリビルトエージェントで即座にクラスター操作・トラブルシューティングが可能
* **拡張性**: MCPサーバーによるカスタムツール追加、マルチモデル対応
* **透明性**: エージェントの行動（どのツールを呼んだか）がリアルタイムに表示される

EKS + Bedrock Claudeの組み合わせでの動作も問題なく、Helmチャートによるインストールからエージェントとの対話まで非常にスムーズでした。CNCFサンドボックスプロジェクトとしてまだ発展途上ではありますが、Kubernetes運用におけるAI活用の方向性として面白いプロジェクトだと感じました。

まずは開発・検証環境で試してみて、Agentic AIがKubernetes運用をどう変えるか、体感してみてはいかがでしょうか。

## クリーンアップ

検証が終わったら、リソースを削除しておきましょう。

```
# テスト用Namespaceの削除
kubectl delete namespace demo-app

# Kagentのアンインストール
helm uninstall kagent -n kagent
helm uninstall kagent-crds -n kagent
kubectl delete namespace kagent

# EKSクラスターの削除
eksctl delete cluster --name kagent-demo --region us-west-2
```

## 参考リンク
