---
id: "2026-07-11-aws-mcp-serverが普通に使えるようになったよ-01"
title: "AWS MCP Serverが普通に使えるようになったよ！"
url: "https://qiita.com/moritalous/items/6102ef63dc60c7e6ee3d"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "qiita"]
date_published: "2026-07-11"
date_collected: "2026-07-12"
summary_by: "auto-rss"
query: ""
---

タイトルのとおりです。普通って素敵。

:::note warn
[Agent Toolkit for AWSの一部の方のAWS MCP Server](https://docs.aws.amazon.com/ja_jp/agent-toolkit/latest/userguide/mcp-server.html)の話です。[オープンソースのMCP Server](https://awslabs.github.io/mcp/)の話ではありません。
:::

今までは普通じゃなかったのかって？そのことはもう忘れましょう。

## 設定方法

### 1. IAMユーザーを作成

まず、IAMユーザーを作成します。IAM Identity Centerのユーザーでも構いません。

気をつける設定はこのあたりだと思います。

- マネジメントコンソールログインを有効化する
- `AWSMCPSignInOAuthAccessPolicy`ポリシーを付与する
- MCPサーバーにさせて良い権限をIAMユーザーに付与する（AdministratorAccessはやめようね）

今回は検証用に`ReadOnlyAccess`ポリシーを付与しました。

作成できたら、マネジメントコンソールからサインアウトしておきます。

### 2. MCPサーバーの設定を追加

私はClaude Desktopで試しました。

:::note
Claude Codeなど他の環境で試す場合は、公式ドキュメントの記載を参照してください。
https://docs.aws.amazon.com/ja_jp/agent-toolkit/latest/userguide/getting-started-aws-mcp-server.html
:::

メニューの構成が頻繁に変わる印象ですが、2026/7/11時点では

1. `Home`タブを選ぶ
1. `カスタマイズ`を選ぶ
1. `コネクタ`メニューを選ぶ
1. `追加`から`カスタムコネクタを追加`を選ぶ
1. リモートMCPサーバーのURLに`https://aws-mcp.us-east-1.api.aws/mcp`と入力。詳細設定は入力不要

で行けました。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/41574/f0c671c2-c4b9-4167-9e3f-b2eb3a0f920d.png)


## 使ってみる

まずリージョン情報を取得します。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/41574/65864317-4a4e-4869-8ff9-7fcc9c8a911e.png)

「常に許可」を「一度だけ許可」にして続行します。
特に認証操作はしていないですが、リージョン情報は取得できました。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/41574/17ed950f-7cc1-4d11-9366-e50bd5e787ad.png)

次に東京リージョンにあるS3バケットの数を聞いてきましょう。

![](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/41574/8fa27d81-b2f5-4a86-8fbe-69f358a3268a.png)

同じように「一度だけ許可」にして続行します。

すると、もう一度許可を求めてきます。「一度だけ許可」にして続行します。

![](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/41574/43d0f18c-2621-4d20-bf45-e69f9437bf7f.png)

すると、「認証が必要です」と出てきました。「連携/連携させる」ボタン（すごい名前！？）をクリックします。

![](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/41574/e93b4eee-4388-47e5-8f99-175db4a6f1c8.png)

ブラウザが起動し、AWSの認証ページが表示されます。

![](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/41574/4903bf14-966c-4363-a790-3101cbe5606b.png)

先ほど作成したユーザーでサインインします。

![](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/41574/2f0b3cd0-7661-4778-b086-c0277000b9aa.png)

Claude Desktopで回答が取得できました。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/41574/81084916-9715-4b45-9e24-2f80548ddadb.png)

S3バケットの作成を依頼してみたところエラーになりました。ReadOnlyAccess権限なので期待動作ですね！

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/41574/ac4e1416-f93f-464f-88a9-4aff248afb21.png)

---

普通のこと過ぎて、何がすごいのかわからないかもしれませんが、要するに、普通に使えますってことですw
