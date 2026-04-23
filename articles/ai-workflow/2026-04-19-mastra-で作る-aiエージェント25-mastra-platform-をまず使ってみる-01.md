---
id: "2026-04-19-mastra-で作る-aiエージェント25-mastra-platform-をまず使ってみる-01"
title: "Mastra で作る AIエージェント(25) Mastra Platform をまず使ってみる"
url: "https://zenn.dev/shiromizuj/articles/9ccd85865dca81"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-19"
date_collected: "2026-04-20"
summary_by: "auto-rss"
query: ""
---

[Mastra で作る AI エージェント](https://zenn.dev/shiromizuj/articles/a0a1659e9f05b6) というシリーズの第25回です。

---

[本連載の第19回目](https://zenn.dev/shiromizuj/articles/dd6c48328b961b) で、Mastra AI エージェントのさまざまなデプロイ方法をご紹介しました。その中に、Mastra社が運営するクラウドサービス「Mastra Cloud」があり「Mastra Cloudについては、別途解説記事を掲載します」と予告していました。

しかし先日、Mastra社の新しいマネージド環境「Mastra Platform」がアナウンスされ、「Mastra Cloud」は非推奨になってしまいました（原稿用意していたのに・・・）。

![](https://static.zenn.studio/user-upload/53e7e8dde2eb-20260410.png)  
*Deprecated（非推奨）になってしまった、Mastra Cloud*

そんなわけで、今回から何回かに分けて、Mastra Platformを実際に使ってみます。

**Mastra Platform とは何か ーーという解説が必要な方は、まずこちらをご一読ください**。

<https://zenn.dev/shiromizuj/articles/ba80b4694382b3>

## Mastra Platform にサインアップ

まずは、[Mastra Platform のアカウント](https://projects.mastra.ai/) を作成しましょう。

私はふつうに「Googleアカウント」でサインアップしました。Mastra Cloud の頃は「Googleアカウント認証」か「GitHubアカウント認証」の選択でしたが、「GitHubアカウント認証」がなくなって「メールアドレスの認証」が追加された形です。

![](https://static.zenn.studio/user-upload/b9145f680d5b-20260412.png)

Googleログインすると、Studioが表示されますが、まだ何もデプロイされていない状態です。  
![](https://static.zenn.studio/user-upload/effc33da9c51-20260412.png)

左上のプルダウンから、Studio、Server、Memory Gatewayを切り替え可能です。  
![](https://static.zenn.studio/user-upload/15947fa87c07-20260412.png)

## まずは手元のリポジトリをMastra Platformにデプロイしてみる

実験用に作ったいつものお天気エージェントを、まずは何も考えずにMastra Platformにデプロイしてみます。

### デプロイ手順1. `mastra` CLI をグローバルにインストール

pnpm を使う場合は、先に下記を実行してグローバル bin ディレクトリをセットアップしてください。

```
pnpm setup   # 初回のみ（シェルを再起動または source ~/.bashrc などで PATH を反映）
pnpm add -g mastra
```

### デプロイ手順2. Server（APIサーバ）をデプロイ

* Mastra Platform に未認証の場合はログインが促されます
* 内部で `mastra build` を実行し、アーティファクトをアップロードして **Docker** イメージをビルド、**Railway** にデプロイします
* デプロイの状態は `queued → uploading → building → deploying → running` と遷移します
* ビルドが 15 分以上かかると自動的に失敗とみなされます  
  ![](https://static.zenn.studio/user-upload/98ef1b966010-20260412.png)  
  ：  
  ![](https://static.zenn.studio/user-upload/79ae59910a8b-20260412.png)

### デプロイ成功、Mastra Platformの画面を確認

デプロイが成功したら、Mastra Platform にアクセスして、左上のプルダウンから Mastra Server を選んでみましょう。先ほど空っぽだった画面に、いまデプロイした我々のプロジェクトがカード表示されています。  
![](https://static.zenn.studio/user-upload/d1890fbe124c-20260412.png)

カードの中のURLの部分をクリックしてみます。  
![](https://static.zenn.studio/user-upload/e227201c94d3-20260412.png)

**Swagger UI** のようなAPI仕様が表示されます。  
![](https://static.zenn.studio/user-upload/ffdf405a70a4-20260412.png)

先ほどの画面に戻り、プロジェクト名をクリックしてみます。  
![](https://static.zenn.studio/user-upload/86bb086e1628-20260412.png)

プロジェクトの詳細画面が表示されます。こちらは「Overview」画面です。  
![](https://static.zenn.studio/user-upload/d73a40c84be6-20260412.png)

こちらは「Deploys」画面です。デプロイ履歴が表示されます。1行選んでクリックしてみます。  
![](https://static.zenn.studio/user-upload/1d3e58ea3f1c-20260412.png)

当該デプロイの詳細が表示されます。  
![](https://static.zenn.studio/user-upload/af19a5b505dd-20260412.png)

こちらは「Settings」画面です。  
![](https://static.zenn.studio/user-upload/dfef23e42423-20260412.png)

特に、`.env` に書いていたような環境変数をここで設定することができます。初回デプロイの際には、`.env`の内容が自動設定されますが、2回目以降のビルドでは反映されないので手動で編集することになります（2回目以降反映されてしまうと、デグレードを引き起こしてしまいますからね）。  
![](https://static.zenn.studio/user-upload/4f2a7c0d1fa5-20260412.png)

## CI/CD での利用

初回デプロイ時に `.mastra-project.json` が生成されます。  
このファイルにはプロジェクトの `projectId` / `projectName` / `organizationId` が記録されており、  
CI/CD から同じプロジェクトへデプロイするために必要です。  
**必ずリポジトリにコミットしてください。**

```
{
  "projectId": "xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxx",
  "projectName": "my-mastra-app",
  "projectSlug": "my-mastra-app-xxxx",
  "organizationId": "org_xxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

### 実際に API を動かしてみる

では、デプロイしたAIエージェントについて、実際にAPIを呼び出してみましょう。CLI が出力した URL の末尾に /api/agents を付けてアクセスし、エージェント一覧の JSON が返れば成功です。

![](https://static.zenn.studio/user-upload/cd5ee91f97a4-20260412.png)

`/agents` API を実行したら、無事にエージェントの一覧が返ってきました。正しくデプロイされています。  
![](https://static.zenn.studio/user-upload/64897f91959e-20260412.png)

## Studio もデプロイする

現段階では、API Server だけがデプロイされていて、Studioはまだデプロイされておらず使えない状態です。Studioもデプロイしましょう。

### デプロイ手順1. Studio をDeploy

![](https://static.zenn.studio/user-upload/fb71c963ef35-20260412.png)  
：  
![](https://static.zenn.studio/user-upload/3e7a8564e27a-20260412.png)

### デプロイ成功、Mastra Platformの画面を確認

「Deploy succeeded」と表示されたので、成功したようです。Mastra Platform で 左上のプルダウンから Studio を選択してみます。無事、こちらでも我々のプロジェクトが表示されています。  
![](https://static.zenn.studio/user-upload/ccf3dae1867c-20260412.png)

URLの部分をクリックすると、いつもの見覚えがある Studio が起動します。  
![](https://static.zenn.studio/user-upload/c0ea87997a3b-20260412.png)

### 実際に Studio を動かしてみる

Studio から お天気エージェントを動かしてみます。ちゃんと動くことを確認できました。  
![](https://static.zenn.studio/user-upload/1d1f1e30a5d9-20260412.png)

## セキュリティ設定で関係者以外は利用不可に

ちょっと長くなりましたが、ここまではやっちゃいましょう。

現在は、**世界中にAPIを公開している**状態です。 [認証設定](https://mastra.ai/docs/server/auth)をすることで、限られた人だけが利用できるようにしましょう。

### 最も手軽な方法: SimpleAuth（APIキー認証）

認証設定には様々な方法があるのですが、ここでは最も手軽な `SimpleAuth（APIキー認証）` をご紹介します。`@mastra/core` に同梱されており、追加パッケージ不要なのです。

### 手順1.index.ts に設定追加

src/mastra/index.ts に設定を追加します

```
import { Mastra } from '@mastra/core/mastra';
+ import { SimpleAuth } from '@mastra/core/server';
import { PinoLogger } from '@mastra/loggers';
import { LibSQLStore } from '@mastra/libsql';
import { DuckDBStore } from "@mastra/duckdb";
import { MastraCompositeStore } from '@mastra/core/storage';
import { Observability, DefaultExporter, CloudExporter, SensitiveDataFilter } from '@mastra/observability';
import { weatherWorkflow } from './workflows/weather-workflow';
import { weatherAgent } from './agents/weather-agent';
import { toolCallAppropriatenessScorer, completenessScorer, translationScorer } from './scorers/weather-scorer';

export const mastra = new Mastra({
+  server: {
+    auth: new SimpleAuth({
+      tokens: {
+        [process.env.API_TOKEN!]: { id: 'user-1', name: 'Admin', role: 'admin' },
+      },
+    }),
+  },
  workflows: { weatherWorkflow },
  agents: { weatherAgent },
```

### 手順2.環境変数にAPIキーを追加設定

`API_TOKEN` という名前で、環境変数を追加します。

`.env` は2回目以降のデプロイ時には自動反映されないため、Platform の Web ダッシュボードで設定します。

1. [projects.mastra.ai](https://projects.mastra.ai/) を開く
2. `my-mastra-app` プロジェクト → **Server → Environment Variables**
3. `API_TOKEN` = `sk-your-secret-token-here`（任意の値）を追加
4. `mastra server deploy` で再デプロイ

![](https://static.zenn.studio/user-upload/7f7b07ba4e14-20260412.png)

**API リクエスト時はヘッダーにトークンを付与：**

```
curl https://your-app.up.railway.app/api/agents \
  -H "Authorization: Bearer sk-your-secret-token-here"
```

### Mastra Platform デプロイ時の認証の全体像

Mastra Platform にデプロイした場合、アクセス経路ごとに認証レイヤーが異なります。

| アクセス経路 | 認証 | 備考 |
| --- | --- | --- |
| 直接 API 呼び出し（curl / 外部サービス） | SimpleAuth（`API_TOKEN`） | 設定しないと無認証で公開される |
| Platform Studio → Server | Mastra Platform アカウント | Platform のアカウントがないと使えない |

Platform 上の Studio は Mastra Platform アカウントで認証されるため、SimpleAuth のトークンを入力する画面は表示されません。Studio のアクセス制御は Platform の Organization / Project メンバー管理で行います。

#### SimpleAuth の制限事項

* トークンはメモリ内に保持（期限切れ・リフレッシュなし）
* 起動時にすべてのトークンを事前定義する必要がある
* 本番の大規模サービスには向かない → その場合は [JWT](https://mastra.ai/docs/server/auth/jwt) / [Clerk](https://mastra.ai/docs/server/auth/clerk) / [Auth0](https://mastra.ai/docs/server/auth/auth0) を推奨

---

# 次回は、会話履歴

いかがでしたか。今回はシンプルなエージェントを最低限の形でPlatformにデプロイする手順を確認しました。次回はMastra Platform における「会話履歴」を扱います。

[>> 次回 : (26) Mastra Platform のDBをNeon（PostgreSQL）に切り替える](https://zenn.dev/shiromizuj/articles/3ed824b8d97648)
