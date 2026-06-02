---
id: "2026-06-01-microsoft-foundry-で補助金aiエージェントを作った話-新foundryの落とし穴と-01"
title: "Microsoft Foundry で補助金AIエージェントを作った話 — 新Foundryの落とし穴と実装で詰まった全部"
url: "https://zenn.dev/ayanokishi/articles/205ad705d26d19"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "OpenAI"]
date_published: "2026-06-01"
date_collected: "2026-06-02"
summary_by: "auto-rss"
query: ""
---

こんにちは！Anamarchyの青木です。  
Microsoft Agent Hackathon 2026 に「補助金確認・申請フォローAI」という作品で参加しました。

## はじめに

中小企業やスタートアップにとって、補助金は公的資金を活用した強力な資金調達手段です。しかし、公募要項の複雑さ、日々更新される情報の多さ、そして莫大な申請書類の作成タスクが原因で、多くの企業がその恩恵を受けきれていません。

今回作成したのは、そういった中小企業向けに補助金候補を AI が見つけ、申請書まで自動で作ってくれる、というアプリです。  
**Microsoft Foundry Agent Service の最新パターン**を全面採用し、6つのエージェントを連携させて動かしています。

ただ、実装してみると **新 Foundry はまだまだドキュメントと実装の間にギャップが多い**、というのが正直なところでした。  
旧 OpenAI Assistants API の癖が抜けないまま設計を始めると、何度もエラーで詰まります。私自身、Agent ID 周りで4回もハマって判断ミスを繰り返しました。

今回はその試行錯誤を、 **新 Foundry を使う人に同じ罠を踏ませない** という視点で、できるだけ正直に共有してみようと思います。

## プロジェクト概要（対象ユーザーと課題）

### 対象ユーザー

* 中小企業・スタートアップにおける、経営企画・システム担当などの「補助金兼任担当者」

### 解決したい2つのリアルなペイン

* **兼任担当者の情報限界による「機会損失」**  
  中小企業では補助金対応の専任担当者を置く余裕はなく、他の重要業務の傍らで日々更新・追加される複雑な補助金情報を常に追うことは不可能なため、「実は自社が対象となる強力な補助金があったのに、気づいた時には公募が終わっていた」という機会喪失が構造的に発生しています。
* **初期段階での「タスク負荷の不透明さ」による申請断念**  
  補助金は、数百ページに及ぶ公募要項を熟読しなければ「最終的にどれだけの証憑書類が必要で、どれほどの業務負荷がかかるのか」が分かりません。最初の時点でタスク量が不透明なため、心理的・リソース的ハードルから、申請の検討すら諦めてしまうケースが後を絶ちません。

## この記事でわかること

* 補助金AIエージェントの全体アーキテクチャ
* 6つのエージェント(Search / Profiling / Matching / Task Decompose / Draft Assist / Followup)の役割と連携
* 新 Foundry Responses API パターン(`agent_reference`)の正しい使い方
* 実装で詰まった5つの罠と、その回避方法
* 今後どう改善していくかの構想

## まず結論

先に成果物のスクリーンショットを置いておきます。

公式の補助金申請様式を画面に再現し、「AI素案生成」ボタンを押すと、自社プロファイル(業種・規模・所在地)に基づいて各フィールドに記述が自動入力されていく、というアプリケーションが動いています。

このアプリで採用した構成は、次の通りです。

* **Frontend**: Next.js 14 (App Router)、Container Apps にデプロイ
* **Backend**: Microsoft Foundry Agent Service、6エージェント構成
* **Data Layer**: Cosmos DB for NoSQL(Vector Search + DiskANN、9コンテナ)
* **AI Tools**: Bing Grounding(Web検索)、Foundry の text-embedding-3-small
* **Infrastructure**: Terraform で IaC 化(10モジュール、2,372行)

このうち、 **Microsoft Foundry の新 Responses API パターン**を採用したのが今回のチャレンジでした。  
これは旧 OpenAI Assistants API(Threads → Messages → Runs のポーリング方式)から、新しい `agent_reference` を使ったシンプルな1リクエスト方式へ移行する設計です。

## 補助金AIエージェントとは何を作ったか

中小企業の経営者・経理担当の方に、 **補助金活用の最初の一歩から申請書提出までを伴走する AI アシスタント**です。

具体的には次の流れで使えます。

1. **自社情報を登録する**: 法人名、業種、規模、所在地、関心領域などをプロファイルとして登録
2. **AIが補助金候補を探す**: Bing Grounding で実在の補助金を網羅検索、自社にマッチする5〜10件を提示
3. **適合度を判定する**: 各補助金に対して「採択可能性: 高/中/低」と推薦理由を付与
4. **申請を決めたら、AIがタスク分解する**: 「決算書取得」「事業計画書作成」「申請様式記入」など、必要なタスクを期限付きで自動生成
5. **申請書をAIが下書きする**: 公式様式を再現した画面で、AI が各フィールドに自社プロファイルに基づいた文章を自動入力
6. **AIが査読する**: 完成したドラフトを補助金の評価ポイントに照らして添削、差分提案を返す

「補助金は使いたいけれど、何から始めればよいかわからない」というユーザーが、 **AI と対話するだけで申請書のドラフトまで到達できる** ことを目指しました。

## 全体アーキテクチャ

システム全体の構成は次の通りです。  
![](https://static.zenn.studio/user-upload/eaba8e798add-20260601.png)

ポイントは次の通りです。

* **Container Apps Environment** を中心に置き、Frontend と JグランツMCP を内包
* **Cosmos DB** はベクトル検索(DiskANN)を含む9コンテナで構成
* **Foundry Agent Service** が AI 機能の中核、6エージェントを定義
* **Managed Identity** で全リソース間の認証を統一(シークレットレス)
* **Terraform** で全インフラを IaC 化、再現性を確保

リージョンは全て `japaneast` で統一しています。

## デモ動画

<https://youtu.be/W761nDhW1Nc>

## 6つのエージェントとワークフロー

このアプリの「頭脳」が、Foundry Agent Service に定義した6体のエージェントです。  
![](https://static.zenn.studio/user-upload/72604efd5cec-20260601.png)

各エージェントの責務を分けることで、 **プロンプトを単機能で書き切れる**ようにしています。  
オーケストレーター(7体目)も最初は計画していましたが、これは後述する理由で諦めました。

## ここからが詰まったポイント本編

ここからが本題、というか、本記事の主役です。  
新 Foundry で実装して詰まった4つの罠を順番に共有していきます。

## 罠1: 新 Foundry の Agent ID は `asst_xxxx` ではない

最初に詰まったのは、Agent ID の形式です。

旧 OpenAI Assistants API では、エージェントは `asst_xxxxxxxxxxxxxxxxxxxxxxxx` という形式の一意 ID で識別されます。  
私もこの感覚で `agent-client.ts` を実装し、Foundry portal に作成したエージェントを呼ぼうとしました。

結果、こんなエラーが出ました。

```
Error: Run creation failed: {
  "error": {
    "message": "Invalid 'assistant_id': 'followup-agent'. Expected an ID that begins with 'asst'.",
    "type": "invalid_request_error",
    "param": "assistant_id",
    "code": "invalid_value"
  }
}
```

「`asst` で始まる ID を渡せ」と書かれています。  
なるほど、ということで Foundry portal を探し回ったのですが、 **`asst_xxxx` 形式の ID がどこにも見つかりません**。YAML タブを開いても、こんな表示しかありません。

```
id: matching-agent:2
name: matching-agent
version: "2"
agent_guid: 22d268f4-dc9e-441e-b7b5-694b9ce4ae7a
```

ID らしきものは3つ並んでいるのに、どれも `asst_` で始まらない。

色々と試行錯誤した結果、 **Microsoft 公式の Python サンプルコード** にたどり着いて、ようやく答えがわかりました。

```
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

endpoint = "https://foundry-subsidy-hack-prod.services.ai.azure.com/api/projects/foundry-subsidy-hack-pr-project"

project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

openai_client = project_client.get_openai_client()

response = openai_client.responses.create(
    input=[{"role": "user", "content": "Tell me what you can help with."}],
    extra_body={
        "agent_reference": {
            "name": "orchestrator-agent",
            "version": "1",
            "type": "agent_reference"
        }
    },
)
```

ここに全部書いてありました。

* 旧: `assistant_id: "asst_xxxx"` で識別する
* 新: `agent_reference: {name, version, type}` オブジェクトで識別する

つまり **新 Foundry には `asst_xxxx` 形式の ID という概念自体が存在しない**。  
人間可読な `name` と `version` でエージェントを参照する設計に変わっていました。

旧 OpenAI Assistants API の常識で実装すると、ここで完全に詰まります。  
私はこれに気付くまで、Yuya や Claude Code と3往復ほど Agent ID の取得方法で議論を重ねました。「ポータルで asst\_xxxx をコピーしてください」と何度も指示したのですが、 **存在しないものを探させていた**わけです。

### 教訓

新 Foundry を使うときは、 **Microsoft 公式の Python サンプルコードを最初に見る**のが正解です。  
旧 OpenAI Assistants API のドキュメントを参照すると、ほぼ全てが間違った方向に進みます。

罠1を解決し、`agent_reference` で呼ぶように書き直したのですが、今度は 401 Unauthorized が返ってきました。

```
// 最初に書いたコード(動かない)
const token = await credential.getToken(
  'https://cognitiveservices.azure.com/.default'
);
```

これは旧 OpenAI API のスコープです。新 Foundry では別のスコープが必要でした。

```
// 正しいコード
const token = await credential.getToken(
  'https://ai.azure.com/.default'
);
```

スコープを `cognitiveservices.azure.com` → `ai.azure.com` に変えたら認証が通りました。

実は、エンドポイントの形式も変わっていました。

```
旧: https://foundry-subsidy-hack-prod.cognitiveservices.azure.com/
新: https://foundry-subsidy-hack-prod.services.ai.azure.com/api/projects/<プロジェクト名>
```

ドメインが `cognitiveservices` から `services.ai` に変わり、パスにプロジェクト名が含まれるようになっています。  
Container App の環境変数に設定する `FOUNDRY_ENDPOINT` も、当初の旧形式から新形式に書き換える必要がありました。

### 教訓

新 Foundry のドキュメントが「Azure OpenAI Service と互換」と書いていても、 **エンドポイントとトークンスコープは独立して新しい**ものになっています。  
旧 OpenAI のスコープを使い回すと、認証が通らないという地味なハマり方をします。

## 罠2.5: API バージョンも新しいものに変える必要がある

トークンスコープを直しても、まだ 400 Bad Request が返る場合があります。  
API バージョンが原因です。

```
// 動かないバージョン(例)
const url = `${FOUNDRY_ENDPOINT}/openai/responses?api-version=2025-04-01-preview`;

// 動くバージョン
const url = `${FOUNDRY_ENDPOINT}/openai/responses?api-version=2025-05-15-preview`;
```

`2025-04-01-preview` より前のバージョンは全て 400 を返しました。 `2025-05-15-preview` のみ動作することを確認しています。

ドキュメントに記載のバージョン文字列と実際に動くバージョンが異なるケースがあるため、 エラーが解消しない場合は API バージョンも疑うようにしてください。

### 教訓

新 Foundry の API バージョンは変化が速く、ドキュメント記載のバージョンが **既に廃止・未対応になっていること**があります。  
公式 Changelog を確認し、最新の preview バージョンを試してください。

## 罠3: Bing Grounding を使うエージェントのレスポンス構造

Agent 呼出が動き始めて、ようやく `/api/draft/generate` から応答が返ってきました。  
ところが、エディタ画面が空のまま動かない。

ログを見ると、応答のパースで `undefined` が出ています。  
レスポンス構造を実際に出力してみると、こんなことになっていました。

```
{
  "output": [
    { "type": "bing_grounding_call", "..." },
    { "type": "bing_grounding_call_output", "..." },
    { "type": "message", "content": [{ "type": "output_text", "text": "..." }] }
  ]
}
```

旧 Assistants API の感覚で `data.output[0].content[0].text` を取ろうとすると、 **`bing_grounding_call`(ツール呼出ログ)を誤って取得** してしまいます。  
実際の応答は `output[2]` の `type: "message"` に入っているのですが、Bing Grounding を使わないエージェントだと `output[0]` が message になるので、 **エージェントによって配列の位置が変わる**わけです。

正しい取り方は `type` ベースの検索です。

```
// 修正後(正解)
const messageOutput = data.output.find((item: any) => item.type === "message");
const targetOutput = messageOutput ?? data.output[data.output.length - 1];
```

これで、Bing Grounding の有無に関わらず正しく応答を取れるようになりました。

### 教訓

新 Foundry の Responses API のレスポンス構造は、 **ツールを使うかどうかで配列の中身が変わります**。  
インデックス指定ではなく、必ず `type` フィールドで検索する。これは MCP や他のツールを足したときにも壊れない設計です。

## 罠4: AI Project と AI Services リソースの接続問題

これが地味に難しかった話です。

新 Foundry には3つのリソース種別があります。

* **Azure AI Services**(旧 Cognitive Services 系)
* **Azure AI Hub**(プロジェクトの親)
* **Azure AI Project**(エージェント定義の置き場所)

Terraform で Foundry を構築するとき、私は「AI Services があれば動く」と思っていたのですが、 **エージェント呼出には AI Project + AI Hub の接続が前提**でした。

Terraform で構築した直後、エージェント呼出 API が以下のエラーを返したことがあります。

```
"No Azure Open AI connection associated with this project.
Please add a connection in AI studio."
```

プロジェクトに AI Services 接続が未設定だと、API は通っていてもエージェントが見えない、という現象です。

私の場合は Foundry portal の **「Connected resources」** で手動で接続を追加することで解決しました。  
ただ、本来は Terraform の `azapi_resource` でこの接続も自動化すべきだと思います。

### 教訓

新 Foundry を Terraform で組むときは、 **AI Services + AI Hub + AI Project + 接続まで一式構築** しないと、エージェントが動きません。  
公式ドキュメントの Bicep テンプレートを必ず参照することをお勧めします。

## 設計判断:諦めたもの、選んだもの

ここからは、ハッカソン期間中に下した設計判断のうち、特に「諦めたもの」と「選んだもの」を共有します。

### 諦めたもの1: 3層MCP構成

最初の設計では、3層のMCPサーバーで補助金情報を扱う予定でした。

* **Bing Grounding**(Microsoft純正、Web検索)
* **JグランツMCP**(デジタル庁公式OSS、補助金マスタ)
* **Cosmos MCP**(Microsoft純正、社内データアクセス)

これがあれば、「3層MCP構成のAIエージェント」というかなり強いアピールができるはずでした。

ところが、JグランツMCP を Container Apps に internal-only でデプロイしたところ、 **Foundry Agent からは到達できない**ことが判明しました。Internal ドメイン(`*.internal.azurecontainerapps.io`)は同じ Container Apps Environment 内のサービスからしか名前解決できないので、Foundry のような外部サービスからは見えません。

これを external に公開する選択肢もあったのですが、 **認証なしで公開すると DDoS リスクが高い**ことに気づいて止めました。  
Container Apps は従量課金なので、攻撃を受けると簡単に月数百ドル単位でコストが膨らみます。

最終的に、 **Bing Grounding のみ採用、JグランツMCP は internal で残したまま使わない**という判断に落ち着きました。  
Cosmos MCP は .NET 9.0 のビルドが必要で時間切れになりそうだったため、 **Foundry → @azure/cosmos SDK 経由の直接接続** に置き換えました。

### 諦めたもの2: Orchestrator Agent

7体目に Orchestrator Agent を計画していました。  
Connected Agents 機能を使って、5つの専門エージェントを統括する設計です。

しかし、Foundry portal で Connected Agents が見当たりません。  
調べると、Connected Agents は **旧 Foundry (classic) portal の機能** で、2027年3月で deprecated 予定。新 Foundry portal では **Multi-agent orchestration workflows** という別の仕組みに置き換わっていました。

新方式は学習コストが高く、ハッカソン期間中に習得するのは厳しいと判断。  
**フロントエンド側から各エージェントを個別呼び出しする設計**に切り替えました。

結果としてこれが良くて、フロント側でエージェントの呼び出し順序を明示的に管理できるため、デバッグ性が大幅に上がりました。

### 選んだもの1: Cosmos Vector Search (DiskANN)

ベクトル検索基盤として、当初は Azure AI Search を検討していました。  
しかし、**月額 $150〜225** のコストが審査期間(2-3ヶ月)で大きく響くため、 **Cosmos DB の Vector Search 機能** に切り替えました。

Cosmos の Vector Search は DiskANN インデックスを使っていて、`text-embedding-3-small` の1536次元埋め込みと完全に統合できます。Serverless モードなら使った分だけの課金で、ハッカソン規模ならほぼ無料です。

ただし、ここでもひとつ罠がありました。 **az CLI 2.86 では `--vector-indexes` オプションが未対応** で、Terraform からもベクトルインデックスを作れません。  
仕方なく、Cosmos の Management REST API を直接叩いてインデックスポリシーを設定しました。

```
for container in subsidy_docs past_applications company_documents; do
  az rest --method PATCH \
    --url "https://management.azure.com/.../containers/${container}?api-version=2024-05-15" \
    --body "{
      \"properties\": {
        \"resource\": {
          \"id\": \"${container}\",
          \"vectorEmbeddingPolicy\": {
            \"vectorEmbeddings\": [
              {\"path\": \"/embedding\", \"dataType\": \"float32\", \"dimensions\": 1536, \"distanceFunction\": \"cosine\"}
            ]
          },
          \"indexingPolicy\": {
            \"vectorIndexes\": [{\"path\": \"/embedding\", \"type\": \"diskANN\"}]
          }
        }
      }
    }"
done
```

az CLI の preview 拡張機能(`cosmosdb-preview`)もありますが、preview なので動く保証がなく、REST API 直叩きが最も確実です。

### 選んだもの2: 公式申請様式の HTML/CSS 再現

これは最後に追加した機能で、デモのインパクトが大きく変わりました。

各補助金マスタに `applicationTemplate` フィールドを追加し、 **公式公募要領から抽出した申請様式の構造**(様式1: 補助金交付申請書 / 様式2: 事業計画書 など)を JSON として持たせます。

```
"applicationTemplate": {
  "officialGuidelineUrl": "https://...",
  "forms": [
    {
      "formId": "form-1",
      "formName": "様式1: 補助金交付申請書",
      "sections": [
        {
          "title": "1. 申請者",
          "layout": "table",
          "fields": [
            {
              "fieldId": "applicant-name",
              "label": "申請者名(法人名)",
              "type": "text",
              "required": true,
              "guideline": "登記簿謄本記載の正式名称を記入"
            }
          ]
        }
      ]
    }
  ]
}
```

エディタ画面では、このテンプレートから HTML を動的生成し、各 placeholder に `data-field-id` 属性を付けて表示します。  
AI素案生成ボタンを押すと、エージェントが各 `fieldId` に対応する記述を生成して返し、フロント側で機械的に置換する、という仕組みです。

```
// AI からの応答
{
  "fieldFills": {
    "applicant-name": "テックメタル工業株式会社",
    "applicant-address": "〒222-0001 神奈川県横浜市港北区xxx-x",
    "representative": "青木 雄哉",
    "business-summary": "当社は神奈川県横浜市にて金属プレス加工業を営む..."
  }
}
```

これにより、 **公式様式の見た目を再現したまま AI が各フィールドを埋めていく**演出が可能になりました。  
ユーザー視点では「自分が書くべき申請書がそのまま表示され、AI が下書きしてくれる」体験になります。

## 冷静に見ると、まだまだ"魔法"ではない

正直に書くと、このアプリは現時点でいくつかの限界があります。

### 1. タスク分解は実在の公募要領を読んでいない

Task Decompose Agent は、補助金マスタの「対象事業 / スケジュール / 補助対象経費」のテキストを受け取って、 **一般常識から推定される必要書類**を返します。  
**実際の公募要領 PDF を逐条で読んでいるわけではない**ので、補助金によっては実際の必要書類と細かい部分でズレる可能性があります。

観測した範囲では概ね妥当な内容(決算書、事業計画書、各種様式)が生成されますが、 **「事業計画書」が本当にその補助金で必須かどうか**は、補助金次第で答えが変わります。

### 2. 申請書のフォーマットは一部標準テンプレで代替

横浜市Y-SDGs認証取得補助金については、申請様式 PDF が Web 上で見つけられず、 **標準的な補助金申請書テンプレート**で代替しました。  
他4補助金(ものづくり / IT導入 / 新事業進出 / 神奈川県)は公募要領を Web 取得して構造化していますが、ここも 100% 公式と一致する保証はありません。

### 3. セキュリティ層が当初設計より薄い

当初は **8層の多層防御**(L1 HTTPS / L2 国外IPブロック / L3 入力サニタイズ / L4 Azure AI Content Safety Prompt Shields / L5 agent-governance-toolkit / L6 Foundry実行 / L7 出力フィルタ / L8 App Insights監視)を計画していました。

このうち、L2 の国外IPブロックは `ipapi.co` のレート制限(1000リクエスト/日)に達した場合のフェイルオープン時のリスクを考慮して **無効化**しました。  
本番運用では、Container Apps の Ingress IP Security Restrictions か、MaxMind GeoLite2 のオフラインDB をコンテナにバンドルする方式への移行が必要です。

### 4. MCP の活用が限定的

当初の「3層MCP構成」から「Bing単独+JグランツMCP内部維持」まで縮小しました。  
JグランツMCP は Container Apps にデプロイされたまま動いているのですが、 **DDoS リスクを考えて外部公開せず**、Foundry Agent からも接続していません。

## 今後どう改善していくか

ハッカソン提出版の限界を踏まえて、次バージョンで実装したい改善は次の3つです。

### 改善1: 公募要領 PDF の Vector Search 統合

Task Decompose Agent と Draft Assist Agent の精度向上のため、 **各補助金の公募要領 PDF を Cosmos の subsidy\_docs コンテナにベクトル投入**したいです。

Cosmos の `subsidy_docs` コンテナは既に DiskANN ベクトルインデックス(1536次元、cosine類似度)を構築済みで、 **RAG 構成の素地は整っている**状態です。  
あとは PDF パーサーで章単位に分割し、`text-embedding-3-small` で埋め込みを生成して投入するだけ。

これが完成すれば、 **「事業計画書が必要かどうか」を実在の公募要領根拠で判定**できるようになり、タスク分解の精度が大きく上がります。

### 改善2: JグランツMCP の Foundry 接続(認証付き)

JグランツMCP を完全活用するため、 **Foundry Agent と JグランツMCP の間に認証層を入れて external 公開**したいです。

具体的には、Foundry の Managed Identity が発行するアクセストークンを JグランツMCP 側で検証する仕組みです。  
これにより DDoS リスクを抑えつつ、Foundry Agent からのみアクセス可能な状態で公開できます。

実装としては、JグランツMCP のリポジトリ (digital-go-jp/jgrants-mcp-server) に Azure AD 認証ミドルウェアを追加する PR を出すか、間に薄い認証プロキシ(Azure Functions あたり)を挟む構成が現実的です。

### 改善3: Multi-agent Orchestration Workflows への移行

現在はフロント側で各エージェントを個別呼び出ししていますが、新 Foundry の **Multi-agent orchestration workflows**(preview API — 執筆時点で動作確認済み: 2025-05-15-preview)を採用すれば、 **チャット1往復で複雑な多段推論を実行**できるようになります。

ユーザーが「金属加工業で IoT 導入したい補助金教えて」と1回打ったら、内部で Profiling → Search → Matching → Task Decompose が連鎖実行されて、最終的な提案が返ってくる、という UX です。

これは新 Foundry の真の主役機能なので、次バージョンで採用する価値が高いと考えています。

## この実装の読みどころ3つ

最後に、もし他のエンジニアの方が新 Foundry で似たような実装をする際、 **私の試行錯誤の中で特に役立ちそうな知見**を3つだけまとめておきます。

**1つ目は、新 Foundry の API は完全に別物だと割り切ること。**  
旧 OpenAI Assistants API のドキュメントを参照しないでください。エンドポイント、トークンスコープ、エージェント識別子、レスポンス構造、すべて違います。Microsoft 公式の Python サンプルコードが最も信頼できる情報源です。

**2つ目は、Cosmos Vector Search は Foundry との相性がとても良いこと。**  
Azure AI Search に比べてコストが圧倒的に安く、Foundry の埋め込みモデルと統合が自然です。az CLI のサポートがまだ追いついていない点だけ要注意ですが、REST API 直叩きで回避できます。

**3つ目は、設計判断を正直に記録することの価値。**  
ハッカソン期間中に「諦めたもの」「選んだもの」を都度文書化していたことで、 **この記事を書くときに当時の判断理由がそのまま素材になりました**。新 Foundry のような変化の早い領域では、判断の記録こそが最大のアウトプットだと感じます。

## まとめ

「補助金確認・申請フォローAI」というハッカソン作品を、新 Microsoft Foundry の **Responses API + agent\_reference パターン**で実装しました。

実装で詰まったポイントは大きく5つ。

1. Agent ID は `asst_xxxx` ではなく `name + version`
2. トークンスコープは `ai.azure.com` (`cognitiveservices` ではない)  
   2.5. API バージョンは最新 preview(`2025-05-15-preview`)を使う
3. レスポンスは `type: "message"` で検索(Bing Grounding使用時に配列位置が変わる)
4. AI Project / AI Services / AI Hub の接続を一式構築する必要がある

新 Foundry はまだまだドキュメントと実装の間にギャップが多く、 **論文の美しさと現場の最適解には乖離がある**タイプのプロダクトです。  
ただ、設計が綺麗で agent\_reference パターンの抽象度も高いので、慣れれば旧 API より圧倒的に書きやすい。

これから新 Foundry を触る方の役に立てば嬉しいです。

## 公開URL

ハッカソン提出版を、しばらく公開しています。よければ触ってみてください。

```
https://ca-subsidy-hack-prod-app.delightfulbeach-deadfb50.japaneast.azurecontainerapps.io/
```

(国内限定アクセス、テストデータあり、テックメタル工業株式会社というダミー企業でログイン済みの状態になっています)

## 参考リンク

### Microsoft 公式

### OSS

### 業界の動き
