---
id: "2026-06-21-bedrock-agentcoreにclaude-agent-sdkをデプロイしてみよう-01"
title: "Bedrock AgentCoreにClaude Agent SDKをデプロイしてみよう！"
url: "https://zenn.dev/tom1414/articles/4a5b47d074fa2f"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "LLM"]
date_published: "2026-06-21"
date_collected: "2026-06-22"
summary_by: "auto-rss"
query: ""
---

こんにちは。とむです。  
せっかくAWS AIPを取得したのに、AWSのAIサービスを全く触ったことない！というステータスだったものなので、今回はBedrock AgentCoreとClaude Agent SDKを使ってAIチャットボットたるものを作りました。  
最近、Bedrock AgentCore HarnessがGAしましたが、自分でAgentの細かな設定をできるという利点を活かせるのは、従来のAgentCoreだという解釈をしています！

さて、本題に入りますと、今回はS3に格納した「**設計書とソースコードの整合性一致を確認するAIチャットボット**」を作成しました。

# 1. アーキテクチャ

構成図、各サービスの役割は以下の通りです！  
![](https://static.zenn.studio/user-upload/e7f77634bbf0-20260621.png)

| サービス | 役割 |
| --- | --- |
| Amazon Cognito | ログインしたユーザーのJWTを発行 |
| API Gateway | リクエストの受付 + JWTの検証 |
| AWS Lambda | API Gatewayからのリクエストを受け取り、ブラウザの代わりにAWS認証情報でAgentCoreを呼び出し、レスポンスをAPI Gatewayに返却 |
| AgentCore Runtime | Claude Agent SDKが動く場所を提供 |
| Claude Agent SDK | Claude Codeのエンジンの仕組みを使用できるSDK。設計書とソースコードをKnowledge Basesから取得したり、整合性チェックの判断結果を返却したりする「ツールを動かす存在」 |
| Amazon Bedrock | 次に実行すべき内容を推論し、Agentに対して指示するLLM本体 |
| Amazon Bedrock Knowledge Bases | S3の元データをベクトル化してS3 Vectorsに格納し、クエリ時には類似検索を実行する司令塔 |
| S3 Vectors | 設計書とソースコードのベクトルデータを格納するベクトルDB |
| S3 | 設計書とソースコードの元データを格納 |

# 2. 構築手順

ここから構築手順に入ります。  
構成図にある通り、今回はAnthropicモデル（Claude Sonnet 4.5）を使用します。  
執筆時点（2026年6月21日）では、初回利用時にユースケースの提出が必要でしたので、Anthropicのモデルを利用される際は、事前提出をお忘れないように！  
提出前の状態は、以下の赤枠の注意書きが表示される可能性があります。  
![](https://static.zenn.studio/user-upload/aa3f3cad753f-20260621.png)

## 2-1. S3に資材を格納

今回は設計書とソースコードの比較を題材にしておりますので、それぞれ別のバケットに格納しました。

> 設計書格納先プレフィックス  
> ![](https://static.zenn.studio/user-upload/d590c490cb5c-20260621.png)

> ソースコード格納先プレフィックス  
> ![](https://static.zenn.studio/user-upload/b9bad94afee3-20260621.png)

### KMSキーの話

今回は個人学習用途で作成しているので**SSE-S3**を選んでいますが、業務で似たような構成を構築される場合は、業務要件に合わせて**SSE-KMS**も選択肢に入れてみましょう！

## 2-2. Knowledge BasesとS3 Vectorsの作成

ナレッジベースを作成する際は、▲のボタンから、**Unstructured Vector Store KB**を選びましょう！  
執筆時点で、ManagedタイプのKBの作成がPreview版で登場しています。  
選び間違えないように！  
![](https://static.zenn.studio/user-upload/40e7963d8fc1-20260621.png)

データソースには先ほど格納した資材を使うためにS3を選択し、ベクトルデータベースでは**S3 Vectors**を使用します！  
S3 Vectorsにした理由は、単に比較的最近GAした（確か去年の冬あたり）という情報を耳にしたので使ってみたかったというのがありますが、他にもコスト面を考えてもOpenSearch等と比較して圧倒的に安いので、選ばせていただきました！  
S3 Vectorsは、ナレッジベース作成と同時に作成できるので、特に事前作成はしておりません。  
![](https://static.zenn.studio/user-upload/5b75f5577377-20260621.png)  
データソースの設定では、今回は設計書とソースコードを別々にしました！  
設計書のデータソースでは、セマンティックチャンキングを、ソースコードのデータソースでは、設定無しで戦略を組みました。  
![](https://static.zenn.studio/user-upload/bc57c908a250-20260621.png)  
![](https://static.zenn.studio/user-upload/ff5fd1fc7bb8-20260621.png)  
ナレッジベースの作成が完了したら、データの同期まで行って、完了したことを確認してから次の手順に進みましょう！

## 2-3. フロントエンドと認証基盤の作成

### 2-3-1. Cognito User Pool設定

| 項目 | 値 | 理由 |
| --- | --- | --- |
| アプリケーションタイプ | SPA | ブラウザで動くReactアプリにしたかった |
| サインイン識別子 | メールアドレス | 一意・パスワードリセット容易・SMS 課金なし |
| 自己登録 | 無効化推奨 | 有効だとインターネットの誰でもアカウント作れてしまう |
| 必須属性 | （空でOK） | メールが既に取得される |
| URL | <http://localhost:3000> | 開発用。本番運用時はAmplify URL等を利用 |

作成後、開発プラットフォームとして「React」を今回は選択しました。  
その上で、必要なライブラリインストールとindex.jsとApp.jsの変更内容が提示されるため、まずは提示された内容に従って進めていきました。  
User Poolの作成が完了したら、対象のUser Poolでユーザーの作成をしましょう！

#### 自己登録とは？

コンソール画面より、以下引用になります。

### 2-3-2. 挙動確認①

筆者は執筆時点でWindowsを使用しておりましたので、ユーザーの作成後は**WSL**上で`npm start`を実行し、React Appを起動しました。  
起動後、localhostでブラウザが立ち上がるので、Sign inでログインができるところまで確認しましょう。  
![](https://static.zenn.studio/user-upload/78fc6bbc32d0-20260621.png)

### 2-3-3. Lambda作成

LambdaではPythonを利用しました。  
ランタイムはPython3.14（執筆時点での最新版）を選択しました。

この後の疎通確認用に、まずはハリボテのソースコードを利用します。

```
import json

def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {"message": "ハリボテ：疎通OK。後でAgentCoreに差し替えます。"},
            ensure_ascii=False  # 日本語が \uXXXX にならないように
        )
    }
```

### 2-3-4. API Gateway作成とcurlコマンドでの疎通確認

今回はシンプルに「リクエストを受けてLambdaに流す」という流れにしたかったため、**HTTP API**を選定しました。  
また、ルートには、App.jsにてPOSTメソッドを指定していたことから、**POST/chat**を設定しました。

API Gatewayの作成完了後は、curlコマンドを叩いて応答が返ってくるか確認してみましょう！  
POST先は、API Gateway作成時に取得可能なURLを指定してください。

```
curl -X POST https://xxxxxx.execute-api.ap-northeast-1.amazonaws.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

### 2-3-5. Cognito JWTオーソライザの付与とルートの設定

2-3-4にて作成したAPI Gatewayに、Cognito JWTオーソライザを付けてみましょう。

> アプリクライアント ID  
> ![](https://static.zenn.studio/user-upload/cde185ae02d3-20260621.png)

ルート設定には、**POST/chat**を設定しましょう。

### 2-3-6. 挙動確認②

アクセストークン無と有で挙動が変わるので、それぞれ確認してみましょう！  
トークン有で設定する<access\_token>は、2-3-2で取得した**Access Token**で置換してください！

```
# トークン無 → 401 が返ればオーソライザが効いてる
curl -X POST https://xxxxxx.execute-api.ap-northeast-1.amazonaws.com/chat \
  -H "Content-Type: application/json" -d '{"message":"test"}'

# トークン有 → 200 が返る
curl -X POST https://xxxxxx.execute-api.ap-northeast-1.amazonaws.com/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"message":"test"}'
```

> トークン無  
> ![](https://static.zenn.studio/user-upload/2a1f462b8e80-20260621.png)

> トークン有  
> ![](https://static.zenn.studio/user-upload/7e70cec643f3-20260621.png)

### 2-3-7. CORS設定

筆者が非常に沼ったポイントです。  
私と同じ末路を辿らないようにしましょう。。  
作成したAPI Gatewayにて、CORSの設定ができます！

| 項目 | 値 |
| --- | --- |
| Access-Control-Allow-Origin | <http://localhost:3000>（Amplifyを使用した構築にする場合、そのURLもここに追加） |
| Access-Control-Allow-Headers | content-type と authorization を**別タグ**で入力 |
| Access-Control-Allow-Methods | POST、OPTIONS |

!

【超重要】**Allow-Headers をカンマ区切りの1タグ**にすると詰みます！

コンソールの入力欄で "content-type,authorization" と打ち込むと、「カンマ込みの 1 個のヘッダー名」として登録され、Authorization ヘッダーが許可リストに入らずプリフライトで弾かれる。  
必ず Enter で 2 つの別タグに分けて入力。

```
# 確認用 CLI:
bashaws apigatewayv2 get-apis --region ap-northeast-1 \
  --query "Items[?Name=='chatbot-api'].{Cors:CorsConfiguration}"
```

AllowHeaders が 2 要素の配列になっていれば OK。1 要素なら詰んでる状態。

#### OPTIONSメソッドとは

OPTIONSは普段あまり目にしないメソッドですが、**CORSプリフライトのために必須**で、リクエストを送って良いか確認するために、ブラウザが裏で自動で送っています。

## 2-4. AgentCore へエージェントをデプロイ！

ここからはコンソールぽちぽちではなく、ターミナルでの作業になります。

### 2-4-1. WSL準備

```
# 作業ディレクトリ
mkdir -p ~/projects/code-design-chatbot
cd ~/projects/code-design-chatbot

# venv（Ubuntu の externally-managed-environment 対策）
python3 -m venv .venv
source .venv/bin/activate  # WSL を開き直すたびに必要

# パッケージ（必ず WSL 側にインストール。Windows 側は引き継がれない）
pip install bedrock-agentcore-starter-toolkit claude-agent-sdk bedrock-agentcore

# AWS CLI（公式インストーラー。apt 版は古い）
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# AWS 認証情報
aws configure  # アクセスキー / シークレット / region: ap-northeast-1 / output: json
aws sts get-caller-identity  # アカウントIDが返ればOK
```

### 2-4-2. Claude Codeのエンジンを用いたagent.pyの作成

agent.py

```
import os
import json
import boto3
from claude_agent_sdk import (
    query,
    tool,
    create_sdk_mcp_server,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
)
from bedrock_agentcore import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

# ===== 設定（自分の値に置換）=====
KB_ID = os.environ.get("KB_ID", "XXXXXX")  # Knowledge Base ID
REGION = os.environ.get("AWS_REGION", "ap-northeast-1")

# Bedrock の Retrieve 用クライアント
agent_runtime = boto3.client("bedrock-agent-runtime", region_name=REGION)

# ===== カスタムツール：S3 Vectors（KB）を検索する =====
@tool(
    "search_knowledge_base",
    "設計書やソースコードのサマリを意味検索する。機能名やキーワードを渡すと、"
    "関連する設計書・コードのチャンクを返す。整合性チェックの情報収集に使う。",
    {"query_text": str},
)
async def search_knowledge_base(args):
    query_text = args["query_text"]

    response = agent_runtime.retrieve(
        knowledgeBaseId=KB_ID,
        retrievalQuery={"text": query_text},
        retrievalConfiguration={
            "vectorSearchConfiguration": {"numberOfResults": 5}
        },
    )

    results = response.get("retrievalResults", [])

    # 結果ゼロのときは「見つからない」シグナルを返す
    if not results:
        return {
            "content": [
                {"type": "text", "text": "NO_RESULTS: 該当する情報が見つかりませんでした。"}
            ]
        }

    # 取得したチャンクを整形して返す
    chunks = []
    for r in results:
        text = r.get("content", {}).get("text", "")
        score = r.get("score", 0)
        source = r.get("location", {})
        chunks.append(
            f"[score={score:.3f}] {text}\n(source: {json.dumps(source, ensure_ascii=False)})"
        )

    return {"content": [{"type": "text", "text": "\n\n---\n\n".join(chunks)}]}

# カスタムツールを in-process MCP サーバとして束ねる
kb_server = create_sdk_mcp_server(
    name="kb-tools",
    version="1.0.0",
    tools=[search_knowledge_base],
)

SYSTEM_PROMPT = """あなたはコードと設計書の整合性を確認するエージェントです。

ユーザーは「ログイン機能の設計とコードは一致している?」のように、
機能名や確認したい内容を自然な言葉で伝えてきます。

## 厳守するルール
- ファイルパスや設計書の場所をユーザーに尋ねてはいけません。
  ユーザーはそれらを知りません。あなたが search_knowledge_base ツールを使って
  自分で設計書とコードのサマリを探し出してください。
- 必要に応じて複数回 search_knowledge_base を呼び、設計書側とコード側の
  両方の情報を集めてください。
- ツールの結果が NO_RESULTS の場合、または明らかに無関係なものしか
  返ってこない場合は、推測で回答せず、必ず次の一文だけを返してください:
  「お探しの設計書・ソースは見つかりませんでした。」
- 情報が揃った場合のみ、整合性を 一致 / 部分一致 / 矛盾 / 未実装 の
  いずれかで分類し、根拠とともに簡潔に報告してください。
"""

@app.entrypoint
async def run_agent(payload):
    user_message = payload.get("message", "")

    options = ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        permission_mode="bypassPermissions",
        max_turns=10,
        mcp_servers={"kb": kb_server},
        allowed_tools=["mcp__kb__search_knowledge_base"],
    )

    async for message in query(prompt=user_message, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    yield block.text

app.run()
```

requirements.txt

```
claude-agent-sdk
bedrock-agentcore
boto3
```

### 2-4-3. AgentCoreへのデプロイ準備

```
agentcore configure -e agent.py --disable-memory
```

#### コマンド解説

`-e`：エントリーポイントを指定するオプションです。`-e` は `--entrypoint` の短縮形になります。  
「エージェントの本体はこのファイルですよ」とAgentCoreに教えるためのものです！

`--disable-memory`：AgentCoreの**Memory機能を無効化**するオプションです。  
AgentCoreには「**セッションをまたいで会話の文脈を保持する**」機能（Memory）があり、デフォルトで有効化されています。  
今回の構成は 「**ユーザーが質問するたびに、独立して整合性チェックを実行する**」というシンプルな使い方でしたので、会話の文脈を覚える必要がないと思い。

#### agentcore configureコマンドで何をしている？

実は裏側でこんなことが。

1. AgentCore Runtime用のIAMロール作成
2. CodeBuild用のIAMロール作成
3. CodeBuildプロジェクトの作成（クラウド側でDockerイメージをビルドするため）
4. ECRリポジトリの作成（ビルドしたイメージを保管する場所）
5. CloudWatchロググループの作成

### 2-4-4. Dockerfileの編集

2-4-3にて作成された `.bedrock_agentcore/agent/Dockerfile` に Node.js + Claude Code CLI を追加しましょう。  
Dockerfile内に記載されている、`COPY requirements.txt` の前に以下を追加してください！

```
# Claude Agent SDK は内部で Claude Code CLI（Node.js製）を呼ぶため必要
RUN apt-get update && apt-get install -y nodejs npm git \
    && rm -rf /var/lib/apt/lists/*
RUN npm install -g @anthropic-ai/claude-code

ENV HOME=/home/bedrock_agentcore \
    CI=true \
    CLAUDE_NO_VERSION_CHECK=1 \
    CLAUDE_CODE_USE_BEDROCK=1 \
    ANTHROPIC_MODEL=jp.anthropic.claude-sonnet-4-5-20250929-v1:0
```

### 2-4-5. いざデプロイ

AWS側で S3 → CodeBuild → ECR → Runtime 作成 → READY、まで自動です。10 分くらいかかるかな。  
Runtime ARN がターミナルのコンソール出力に表示されます。  
無事完了したら、AWSのAgentCore Runtimeを覗いてみましょう！  
ランタイムリソースが作成されていれば、OKです。  
![](https://static.zenn.studio/user-upload/68311bad85b9-20260621.png)

## 2-5. ハリボテ達の修正

### 2-5-1. LambdaのハリボテをAgentCore呼び出しに差し替え

Lambda の boto3 は古く bedrock-agentcore を知らないそうです（Claude君より）。  
まずは、最新版を zip に同梱しましょう。

```
mkdir lambda_package && cd lambda_package
pip install boto3 --target .
```

次に、lambda\_function.pyを書き直しましょう。  
ただし、zip内に同梱したいので、ここではWSL上で作成してください！

lambda\_function.py

```
import json
import os
import boto3

client = boto3.client("bedrock-agentcore", region_name="ap-northeast-1")
# 注意: サービス名は "bedrock-agentcore"、"bedrock-agentcore-runtime" ではない
RUNTIME_ARN = os.environ["RUNTIME_ARN"]  # Lambda の環境変数に設定

def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    user_message = body.get("message", "")

    response = client.invoke_agent_runtime(
        agentRuntimeArn=RUNTIME_ARN,
        payload=json.dumps({"message": user_message}),
    )

    # レスポンスは StreamingBody。outputStream ではなく "response" キー
    result = response["response"].read().decode("utf-8")

    return {
        "statusCode": 200,
    "headers": {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "http://localhost:3000",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Access-Control-Allow-Methods": "POST,OPTIONS"
    },
        "body": json.dumps({"message": result}, ensure_ascii=False)
    }
```

そうしましたら、zip化しちゃいましょう。  
無事zip化できましたら、このzipファイルごとLambdaにアップロードを。

```
zip -r ../lambda_function.zip .
```

### 2-5-2. App.jsをよりチャット画面ぽくしてみよう

よりチャット画面ぽくしてみたかったので、app.jsにも手を加えました（ありがとうClaude）。

app.js

```
import { useState } from "react";
import { useAuth } from "react-oidc-context";

const API_URL = "https://xxxxx.execute-api.ap-northeast-1.amazonaws.com/chat";

function App() {
  const auth = useAuth();
  const [messages, setMessages] = useState([]); // {role: "user"|"agent", text: string}
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;

    // ユーザーのメッセージを画面に追加
    setMessages((prev) => [...prev, { role: "user", text }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${auth.user?.access_token}`,
        },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();

      // レスポンスは "data: \"...\"\n\n" 形式なので整形する
      const cleaned = extractText(data.message);
      setMessages((prev) => [...prev, { role: "agent", text: cleaned }]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        { role: "agent", text: `エラーが発生しました: ${e.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // "data: \"本文\"\n\n" のような形式から本文だけ取り出す簡易パーサ
  const extractText = (raw) => {
    if (!raw) return "(空の応答)";
    try {
      // data: で始まる行を集めて、JSON文字列をパースする
      const lines = raw.split("\n").filter((l) => l.startsWith("data: "));
      let result = "";
      for (const line of lines) {
        const payload = line.replace(/^data: /, "");
        try {
          const parsed = JSON.parse(payload);
          if (typeof parsed === "string") {
            result += parsed;
          } else if (parsed.error) {
            result += `[エラー] ${parsed.error}`;
          }
        } catch {
          result += payload;
        }
      }
      return result || raw;
    } catch {
      return raw;
    }
  };

  const handleKeyDown = (e) => {
    // Enterで送信、Shift+Enterで改行
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (auth.isLoading) return <div style={styles.center}>Loading...</div>;
  if (auth.error)
    return <div style={styles.center}>エラー: {auth.error.message}</div>;

  // 未ログイン
  if (!auth.isAuthenticated) {
    return (
      <div style={styles.center}>
        <h1 style={{ fontSize: 20 }}>コード × 設計書 整合性チェッカー</h1>
        <button style={styles.primaryBtn} onClick={() => auth.signinRedirect()}>
          ログイン
        </button>
      </div>
    );
  }

  // ログイン済み：チャット画面
  return (
    <div style={styles.app}>
      <header style={styles.header}>
        <span style={{ fontWeight: 600 }}>コード × 設計書 整合性チェッカー</span>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{ fontSize: 12, color: "#666" }}>
            {auth.user?.profile.email}
          </span>
          <button style={styles.signoutBtn} onClick={() => auth.removeUser()}>
            ログアウト
          </button>
        </div>
      </header>

      <main style={styles.chatArea}>
        {messages.length === 0 && (
          <div style={styles.placeholder}>
            設計書とコードの場所を教えてください。整合性をチェックします。
          </div>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              ...styles.bubbleRow,
              justifyContent: m.role === "user" ? "flex-end" : "flex-start",
            }}
          >
            <div
              style={{
                ...styles.bubble,
                ...(m.role === "user" ? styles.userBubble : styles.agentBubble),
              }}
            >
              {m.text}
            </div>
          </div>
        ))}
        {loading && (
          <div style={styles.bubbleRow}>
            <div style={{ ...styles.bubble, ...styles.agentBubble }}>
              考え中...
            </div>
          </div>
        )}
      </main>

      <footer style={styles.inputArea}>
        <textarea
          style={styles.textarea}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="メッセージを入力（Enterで送信 / Shift+Enterで改行）"
          rows={2}
        />
        <button
          style={{
            ...styles.primaryBtn,
            opacity: loading || !input.trim() ? 0.5 : 1,
          }}
          onClick={sendMessage}
          disabled={loading || !input.trim()}
        >
          送信
        </button>
      </footer>
    </div>
  );
}

const styles = {
  app: {
    display: "flex",
    flexDirection: "column",
    height: "100vh",
    maxWidth: 800,
    margin: "0 auto",
    fontFamily: "sans-serif",
  },
  center: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    height: "100vh",
    gap: 16,
    fontFamily: "sans-serif",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "12px 16px",
    borderBottom: "1px solid #e0e0e0",
  },
  chatArea: {
    flex: 1,
    overflowY: "auto",
    padding: 16,
    display: "flex",
    flexDirection: "column",
    gap: 12,
    background: "#fafafa",
  },
  placeholder: {
    color: "#999",
    textAlign: "center",
    marginTop: 40,
  },
  bubbleRow: { display: "flex" },
  bubble: {
    maxWidth: "75%",
    padding: "10px 14px",
    borderRadius: 12,
    whiteSpace: "pre-wrap",
    lineHeight: 1.6,
    fontSize: 14,
  },
  userBubble: { background: "#2563a8", color: "#fff" },
  agentBubble: { background: "#fff", border: "1px solid #e0e0e0", color: "#222" },
  inputArea: {
    display: "flex",
    gap: 8,
    padding: 12,
    borderTop: "1px solid #e0e0e0",
  },
  textarea: {
    flex: 1,
    resize: "none",
    padding: 10,
    borderRadius: 8,
    border: "1px solid #ccc",
    fontSize: 14,
    fontFamily: "sans-serif",
  },
  primaryBtn: {
    padding: "10px 20px",
    background: "#2563a8",
    color: "#fff",
    border: "none",
    borderRadius: 8,
    cursor: "pointer",
    fontSize: 14,
  },
  signoutBtn: {
    padding: "6px 12px",
    background: "#fff",
    color: "#666",
    border: "1px solid #ccc",
    borderRadius: 6,
    cursor: "pointer",
    fontSize: 12,
  },
};

export default App;
```

## 2-6. IAMロールの修正

LambdaとAgentCoreにアタッチしているIAMロールに、それぞれ以下を足してください！

Lambda実行ロール

```
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "bedrock-agentcore:InvokeAgentRuntime",
    "Resource": "*"
  }]
}
```

AgentCore Runtimeロール

```
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "bedrock:Retrieve",
    "Resource": "arn:aws:bedrock:ap-northeast-1:<アカウントID>:knowledge-base/*"
  }]
}
```

# 3. 動作確認

長かったですね、ようやく動作確認になります。  
![](https://static.zenn.studio/user-upload/aacc0abc45c2-20260621.png)  
![](https://static.zenn.studio/user-upload/d83daafc7686-20260621.png)

存在する設計書とソースコードの組み合わせに対してはちゃんと回答を返し、存在しない場合はその旨を出力してくれていますね！  
一先ず、今回やりたかったことを実現することができました。

# 4. おわりに

これまで実務で触ったことのなかった、Cognito、API Gateway、Bedrock等々を触って構築することが出来て非常に楽しかったです！  
今までは「お金かかっちゃうしなあ...」と思って全然コンソール画面を触っていませんでしたが、いよいよそんなこと言ってる場合じゃないなと思い・・・  
結果的に学びの多い学習になったので、これからももっと取り組んでいきたいなと感じました！

今後やりたいなと思ったことは、

* ストリーミングレスポンスの実装：今回は質問を投げたら、推論が完了するまでメッセージが全く返ってきませんでした。これはUI/UX的にあまりよくないなと感じたので、改善点でもあります。
* 複数Agentを稼働して何かする：今回は単一Agentをデプロイして実装してみましたが、複数Agentをデプロイしてみて何か面白いことができないかなと、ぼんやりと思いました。
* データソースが複数あった時の挙動確認：現場では大量のデータソースがあることが想定されますよね。今回は設計書もソースコードも1つ1つしか格納していなかったので、あまり効果的だったとは言い切れません。是非誰かチャレンジしてみてください👀

ここまでご覧いただき、ありがとうございます！  
次回もよろしくお願いいたします👐
