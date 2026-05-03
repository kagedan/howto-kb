---
id: "2026-05-02-cursor-sdkで何ができるのかlocal-cloud-self-hosted-と閉域化の範囲を-01"
title: "Cursor SDKで何ができるのか。Local / Cloud / Self-hosted と閉域化の範囲を整理する"
url: "https://zenn.dev/ropital_dev/articles/b6a8159631bc98"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "OpenAI", "TypeScript", "zenn"]
date_published: "2026-05-02"
date_collected: "2026-05-03"
summary_by: "auto-rss"
query: ""
---

Cursor SDKは、CursorのAIコーディングエージェントをTypeScriptから呼び出すためのSDKです。

この記事では、Cursor SDKで何ができるのか、3つの実行モードで何がどこに置かれるのか、Self-hostedでどこまで閉域化できるのかを整理します。

![](https://static.zenn.studio/user-upload/31c8c686f0ce-20260502.png)

## 1. Cursor SDKとは

Cursor SDKは、普段使っているCursor IDEやCLI、Webアプリなどの裏側で使われているエージェントを、自前のアプリから呼び出すことができるSDKです。

2026年5月時点ではTypeScriptのみサポートし、パブリックベータ版として公開されています。

使用イメージは以下です。

```
import { Agent } from "@cursor/sdk";

const agent = await Agent.create({
  apiKey: process.env.CURSOR_API_KEY!,
  model: { id: "composer-2" }, // モデル指定が可能
  local: { cwd: process.cwd() }, // Localモードで現在のディレクトリを作業対象にする
});

const run = await agent.send("Summarize what this repository does");

for await (const event of run.stream()) {
  console.log(event);
}
```

出典: [Cursor公式ブログ: Build programmatic agents with the Cursor SDK](https://cursor.com/ja/blog/typescript-sdk)

## 2. 何ができるのか

Cursor SDKを使うことで、自前のアプリケーションにCursorのAgentを組み込めたり、独自の開発ワークフローに組み込めたりします。

例えば、

* **Slack botから起動する**: Slackで「このバグ調べて」と投稿すると、バックエンドがCursor SDKを呼び出し、Agentが該当コードを調査して修正PRを作る
* **CI失敗時に起動する**: GitHub ActionsやJenkinsの失敗ログを渡し、原因調査、修正案作成、必要ならPR作成まで任せる
* **タスク管理ツールに組み込む**: Kanbanのカードを「Agentに依頼」へ移動すると、Cursor AgentがCloud上またはSelf-hosted worker上で作業し、結果をPRやコメントとして返す

つまり、Cursor SDKは「Cursor IDEの中でAIに頼む」ためだけのものではなく、**Slack、CI、社内ツール、プロダクトUIなどからCursor Agentを呼び出すための入口**になります。

その他、アプリケーションへの組み込み例として、当社のDefineAI（要件や設計などの定義を行うAI）への組み込みを想定した場合、以下のようなことが可能になりました。

* 元々はCursorからDefineAIのMCPを追加してCursorから指示をすることしかできなかったが、DefineAI側から「この要件定義を元に実装をして」のような形でCursor Agentに指示を出せるように
* DefineAIからリポジトリを元に要件定義や設計へのリバースエンジニアリングをする際に、Cursor Agentにリバースエンジニアリングの依頼を出せるように

## 3. 3パターンのアーキテクチャ（Local, Cursor Cloud, Self-host）

Cursor SDKでまず理解すべきなのは、Agentを「どこで動かすか」を3つのパターンから選べることです。

ただし、ここでいう「どこで動かすか」は、すべてがその場所で完結するという意味ではありません。

変わるのは主に **repo本体をどこに置くか** と **terminal実行・ファイル編集などのtool実行をどこで行うか** です。モデル推論と、コードベースインデックスを使う場合のVector DBは、基本的にCursor Cloud側にあります。

| ランタイム | SDKでの指定 | repo本体 | tool実行 | モデル推論 | Vector DB（indexing利用時） | 向いている用途 |
| --- | --- | --- | --- | --- | --- | --- |
| **Local** | `local: { cwd }` | 自分のマシン / CI | 自分のマシン / CI | Cursor Cloud | Cursor Cloud | 手元検証、開発スクリプト、軽いCIチェック |
| **Cloud (Cursor-hosted)** | `cloud: { repos }` | CursorのVM | CursorのVM | Cursor Cloud | Cursor Cloud | 非同期実行、自動PR、並列実行、長時間タスク |
| **Cloud (Self-hosted)** | `cloud: { repos, env: { type: "pool" } }` | 自社worker | 自社worker | Cursor Cloud | Cursor Cloud | 社内ネットワーク接続、シークレット管理、組織運用 |

なお、コードベースインデックスは無効化できます。その場合、Vector DBへのembedding保存は避けられますが、セマンティック検索やコードベース理解の精度は大きく落ちます。インデックスOFFでも、プロンプト、明示的に読ませたコード、tool実行結果などは、推論のためにCursor Cloudへ送られます。

### 3.1 Local: 手元やCIでAgentを動かす

Localは、自分のPCやCIランナー上の作業ディレクトリを対象にAgentを動かすモードです。

アーキテクチャとしては、repo本体とtool実行は手元のマシンにあり、モデル推論とVector DBはCursor Cloud側にある、という形です。

特徴をまとめると、Localは「開発者の手元で動くAgent」です。

* repo本体は自分のマシンまたはCIランナー上にある
* terminal実行やファイル編集も、そのマシン上で行われる
* SDKの検証、小さな修正、コード要約、テスト追加などに向く
* ただし、モデル推論とVector DBまでローカルに閉じるわけではない

```
const agent = await Agent.create({
  apiKey: process.env.CURSOR_API_KEY!,
  model: { id: "composer-2" },
  local: { cwd: process.cwd() },
});
```

`cwd` は「current working directory」の略で、Agentが作業対象にするディレクトリです。たとえばリポジトリ直下でスクリプトを実行すれば、そのリポジトリを対象にファイル検索・読み取り・編集・terminal実行を行います。

Localが向いているのは、まずSDKの挙動を確認したいときや、開発者個人のワークフローに組み込みたいときです。小さな修正、コードベース要約、テスト追加、CI上での簡単なチェックなどはLocalから始めるのが自然です。

注意点として、Localという名前でも完全にローカルで閉じるわけではありません。モデル推論はCursor Cloud側で行われ、コードベースインデックスを使う場合はembeddingもCursor側のVector DBに保存されます。

### 3.2 Cloud (Cursor-hosted): CursorのVMでAgentを動かす

Cloud (Cursor-hosted) は、Cursorが用意するsandboxed VM上でAgentを実行するモードです。

この場合、呼び出し元はSDKでタスクを投げるだけです。repoのclone、ファイル編集、terminal実行はCursor側のVMで行われます。

特徴をまとめると、Cloud (Cursor-hosted) は「Cursorが管理するリモート実行環境で動くAgent」です。

* 呼び出し元にrepoがなくても実行できる
* 呼び出し元が切断してもrunを継続できる
* 複数Agentの並列実行や長時間タスクに向く
* PR作成まで自動化しやすい
* repo本体とtool実行はCursor側のVMに置かれる

```
const agent = await Agent.create({
  apiKey: process.env.CURSOR_API_KEY!,
  model: { id: "composer-2" },
  cloud: {
    repos: [{ url: "https://github.com/your-org/your-repo", startingRef: "main" }],
    autoCreatePR: true,
  },
});
```

このモードでは、Cursor側のVMが指定されたリポジトリをcloneし、そのVM内でファイル編集やterminal実行を行います。呼び出し元のプロセスが途中で終了してもAgentのrunは継続でき、完了後にPRを自動作成することもできます。

Slack bot、GitHub Webhook、Linear連携、社内Webアプリなどから「このissueを調査してPRを作って」と非同期に依頼するような用途に向いています。自分のマシンにrepoがなくても実行できる点もメリットです。

一方で、repo本体や実行環境はCursor側のVMに置かれます。機密性の高いリポジトリや、社内ネットワーク内のprivate registry / DB / APIにアクセスする必要がある場合は、次のSelf-hostedを検討することになります。

### 3.3 Cloud (Self-hosted): 自社管理のworkerでAgentを動かす

Self-hostedは、CursorのCloud Agentsの仕組みを使いながら、tool実行だけを自社ネットワーク内のworkerに寄せるモードです。SDK上はCloud runtimeの一種として指定します。

この場合、呼び出し元とworkerは自社ネットワーク内に置けます。repo本体、シークレット、ビルド、テスト、内部サービスアクセスは自社worker側に残しつつ、Cloud Agents APIとモデル推論はCursor Cloudを経由します。

特徴をまとめると、Self-hostedは「会社が管理するAgent実行基盤」です。

* repo本体とtool実行を自社worker側に置ける
* private registry、内部API、DB、ビルドキャッシュにアクセスしやすい
* シークレットや実行権限を組織側で管理しやすい
* Slack / CI / Cronなどから継続運用する用途に向く
* ただし、モデル推論・Cloud Agents API・Vector DBはCursor Cloud側に残る

```
const agent = await Agent.create({
  apiKey: process.env.CURSOR_API_KEY!,
  model: { id: "composer-2" },
  cloud: {
    repos: [{ url: "https://github.com/your-org/your-repo", startingRef: "main" }],
    env: { type: "pool", name: "backend" },
    autoCreatePR: true,
  },
});
```

worker側では、たとえば次のようにpool workerを起動します。

```
agent worker start --pool --pool-name backend
```

この構成では、repoのclone、ファイル編集、terminal実行、ビルド、テスト、内部サービスへのアクセスは自社worker上で行われます。社内のpackage registry、private API、DB、ビルドキャッシュ、シークレットを使う必要がある場合に向いています。

ただし、Self-hostedは「完全閉域」を意味しません。AgentのオーケストレーションはCloud Agents APIを通り、モデル推論もCursor Cloud側で行われます。また、コードベースインデックスを使う場合は、embeddingと難読化メタデータがCursor側のVector DBに保存されます。

つまりSelf-hostedは、**repo本体・シークレット・tool実行を自社側に残すための構成**であって、Cursor Cloudへの依存をゼロにする構成ではありません。

## 4. 閉域化できる範囲

ここからはSelf-hostedを使う前提で、どこまで閉域化できるのかを整理します。

先に結論を書くと、Self-hostedを使っても完全閉域にはなりません。Self-hostedで閉じられるのは、主に **repo本体、シークレット、ビルドキャッシュ、内部サービスへのアクセス、tool実行** です。一方で、Agentのオーケストレーション、モデル推論、推論に必要なコードチャンク、tool実行結果、コードベースインデックスのembeddingはCursor Cloud側を通ります。

つまりSelf-hostedは、「Cursorを一切外部接続なしで動かす仕組み」ではなく、**コード本体と実行環境を自社側に残しながら、CursorのAgent基盤を使うための構成**です。

### 4.1 Self-hostedで自社内に残せるもの

Self-hostedの一番大きな価値は、Agentが実際に作業する環境を自社ネットワーク内に置けることです。

| 自社内に残せるもの | 説明 |
| --- | --- |
| repo本体 | workerが自社ネットワーク内でcloneし、作業する |
| ファイル編集 | 変更は自社worker上のworking treeで行われる |
| terminal実行 | build、test、lint、migrationなどは自社worker上で実行される |
| シークレット | 環境変数、認証情報、deploy keyなどをworker側に閉じられる |
| 内部サービスアクセス | private registry、社内API、DB、社内Git、ビルドキャッシュなどにアクセスできる |
| 実行権限 | service accountやworker単位で管理しやすい |

たとえば、社内のprivate npm registryや社内APIにアクセスしないとテストが通らない場合、Cursor-hostedのVMではその環境を再現しづらいです。Self-hosted workerを社内ネットワーク内に置けば、普段のCIに近い環境でAgentを動かせます。

### 4.2 Cursor Cloudに届くもの

一方で、Self-hostedでもCursor Cloudを通るものがあります。

| Cursor Cloudに届くもの | 説明 |
| --- | --- |
| プロンプト | `agent.send()` で渡した依頼内容 |
| 推論用コードチャンク | モデルが判断に使うために読むファイル断片 |
| tool call / tool結果 | Agentが次に何をするか判断するための実行結果 |
| run metadata | agent ID、run ID、status、conversation stateなど |
| artifacts | screenshots、videos、log referencesなど |
| embedding | コードベースインデックスを使う場合に生成されるベクトル |

公式の [Self-Hosted Pool ドキュメント](https://cursor.com/docs/cloud-agent/self-hosted) でも、Self-hosted workerはCursor Cloudにoutbound HTTPSで接続し、Agent loop、つまり推論とプランニングはCursor Cloud側で動くと説明されています。workerはその指示を受け取り、自社環境内でterminal実行やファイル編集を行う役割です。

### 4.3 Vector DBとコードベースインデックス

注意が必要なのは、コードベースインデックスです。

Cursorのコードベース理解は、リポジトリを小さなチャンクに分割し、embeddingを作成してVector DBに保存することで実現されています。このVector DBはCursor側にあります。

インデックス作成時には、plaintextのコードチャンクがembedding計算のためにCursorサーバへ一時的に送られます。ただし、[Privacy and Data Governance](https://cursor.com/docs/enterprise/privacy-and-data-governance) の説明では、plaintextコードはembedding生成後に破棄され、永続保存されるのはembedding、難読化されたファイルパス、行番号、hashなどのメタデータです。

ここで重要なのは、「repo本体はSelf-hosted worker側に残せる」が、「コードベース理解のためのembeddingはCursor側に残る」という点です。もしembeddingすら外部に置きたくない場合は、コードベースインデックスを無効化する必要があります。ただし、その場合はセマンティック検索やコードベース理解の精度が大きく落ちます。

### 4.4 完全閉域にできるのか

ネットワーク的に外部接続を一切許可しない、いわゆる完全air-gappedな環境では、Cursor SDKは適しません。

理由はシンプルで、Self-hostedでも以下はCursor Cloudに依存するためです。

* Cloud Agents API
* モデル推論
* Agent loopのオーケストレーション
* コードベースインデックスのVector DB
* artifactsのアップロード

Privacy Modeで保存・学習の扱いを制御し、BYOKでモデル提供元や課金先を制御できます。たとえば [BYOK(\*1)](https://cursor.com/help/models-and-usage/api-keys) や [AWS Bedrock連携](https://cursor.com/docs/customizing/aws-bedrock) を使えば、モデル利用を自社契約に寄せることはできます。ただし、その場合でもCursorのバックエンドはリクエスト構築やオーケストレーションの経路として残ります。

(\*1) BYOKとは、Cursor側が用意しているモデル利用枠ではなく、自分たちが契約しているOpenAI / Anthropic / Azure OpenAI / AWS BedrockなどのAPIキーをCursorに登録して、そのモデルを使う方式です。

したがって、Self-hostedの位置づけは「完全閉域」ではなく、**閉域に寄せられる部分と、Cursor Cloudに依存する部分を分離する仕組み**と捉えるのが正確です。

実務的には、以下のような判断になります。

| 要件 | Self-hostedで満たせるか |
| --- | --- |
| repo本体をCursor-hosted VMに置きたくない | 満たせる |
| シークレットを外部VMに置きたくない | 満たせる |
| 社内DB / private registry / 内部APIにアクセスしたい | 満たせる |
| tool実行を自社管理環境に限定したい | 満たせる |
| コードを学習に使わせたくない | Privacy Modeで対応 |
| embeddingをCursor側に保存したくない | indexing OFFが必要 |
| 外部通信を完全にゼロにしたい | 満たせない |

この章の結論としては、Self-hostedは「Cursorを完全に閉域で動かす機能」ではありません。

ただし、repo本体・シークレット・tool実行・内部サービスアクセスを自社側に残せるため、エンタープライズやSIerでCursor Agentを運用するうえではかなり重要な選択肢になります。

## 5. 活用例

ここまでを踏まえると、Cursor SDKが向いているのは「人間がCursorを開いて毎回依頼する作業」ではなく、**開発ワークフローの中で繰り返し発生する作業をAgentに渡す**用途です。

特に相性が良いのは、入力と完了条件がある程度はっきりしているタスクです。たとえば、CIログがある、Issueがある、対象リポジトリが決まっている、テストで正否を確認できる、といったものです。

### 5.1 Slack / Linear / GitHub Issue 起点の自動PR

イメージしやすいのは、SlackやLinear、GitHub IssueからAgentを起動するパターンです。

たとえば、Slackのバグ報告チャンネルなどで、バグ報告が投稿されると、Slack botのbackendがCursor SDKを呼び出します。Agentは障害内容を読み、原因調査を行い、原因が確定したら修正を行いPRを作ることもできます。

もしくは、原因調査を行うための情報が足りなければ、Slackに追加で必要な情報を返信することもできます。

### 5.2 PRレビュー

PRレビューも実用的です。

たとえば、以下のような使い方です。

* 変更内容を要約する
* 影響範囲を整理する
* テスト不足を指摘する
* リスクの高そうな変更を分類する
* reviewer向けの確認観点を作る

この用途は、低リスクな変更で特に効果が出やすいです。

### 5.3 タスク管理ツールと統合

Cursor SDKの面白いところは、Cursor IDEの外からAgentを呼び出せることです。

たとえば、Kanbanツールでカードを「Agentに依頼」に移動すると、Cursor Agentが該当リポジトリで作業し、完了後にPRリンクやartifactをカードに返す、といったUIが作れます。

### 5.4 サービスへの組み込み

あるいは、当社のDefineAIのような要件定義・設計支援ツールから、以下のような流れも考えられます。

* 作成した要件定義をもとに、Cursor Agentへ実装依頼を出す
* 既存リポジトリを調査させ、仕様書や設計情報へリバースエンジニアリングする
* 変更方針を要件・設計側で確認してから、実装PRを作らせる

これまでは「CursorからMCP経由で外部ツールを呼ぶ」方向が中心でした。Cursor SDKによって、逆に**外部アプリケーション側からCursor Agentを呼ぶ**設計が取りやすくなります。

## 6. まとめ

* Cursor SDKは、Cursor AgentをTypeScriptから呼び出すSDK
* 重要なのは、Local / Cloud / Self-hosted の実行モードを選べること
* ただし、推論とVector DBはCursor Cloud側に残る
* Self-hostedは完全閉域ではなく、repo本体・secret・tool実行を自社側に寄せるための構成
