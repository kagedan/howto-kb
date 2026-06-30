---
id: "2026-06-30-taiyo-ai-gakuse-httpstcogxqlaqlobl-01"
title: "@taiyo_ai_gakuse: https://t.co/GxQLAqloBL"
url: "https://x.com/taiyo_ai_gakuse/status/2071867629565001894"
source: "x"
category: "ai-workflow"
tags: ["MCP", "API", "x"]
date_published: "2026-06-30"
date_collected: "2026-07-01"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/GxQLAqloBL


--- Article ---
# X MCP接続入門

CodexからX APIを使うために、X Developer ConsoleでAppを作り、OAuth設定を通し、X MCP/xurlで認証するまでを、初心者向けに順番にまとめます。

## 今回共有するOSS

この記事は、僕がGitHubで公開しているVercel Skills CLI向けのX MCP Skillを共有するために作っています。Codexやエージェント環境で、X API MCPとX Docs MCPの設定・認証・トラブルシュートを再利用しやすくするためのリポジトリです。

GitHub: [https://github.com/nanameru/x-mcp-skill](https://github.com/nanameru/x-mcp-skill)

まずはこのリポジトリを見てもらい、そのうえで「実際にX Developer Consoleで何を設定すれば動くのか」を順番に説明します。

## まず開くリンク

X Developer Console: [https://developer.x.com/en/portal/dashboard](https://developer.x.com/en/portal/dashboard)

最初はこのDeveloper Consoleを開きます。ここでProjectを作り、そのProjectの中にAppを作成します。すでにProjectがある場合は、そのProjectを選んでAppだけ追加すれば大丈夫です。

## 0. Appを作る

1. Developer Consoleを開き、Dashboardに入ります。
1. Projectを新規作成、または既存Projectを選択します。
1. Appsから新しいAppを作成します。今回の例では X-Article-Publish というApp名にしました。
1. Appを作成したら、そのAppの Keys & Tokens を開きます。
1. この時点では、まだユーザー認証の設定が終わっていないので、User authentication settings を設定します。
## 1. App作成後の最初の画面

Appを作った直後にまず見るのがこの画面です。Keys & TokensにはBearer TokenやOAuth 1.0a Keysがあり、下のほうにUser authentication settingsがあります。Xアカウントとしてログインして使う場合は、ここをSet upします。

![](https://pbs.twimg.com/media/HMC23DYXoAAAq-x.jpg)

## 2. 権限を選ぶ

User authentication settingsを開くと、App permissionsを選びます。記事下書き作成や投稿系の操作をするなら、最低限Read and writeが必要です。DMまで扱わないならDirect message付きは選ばなくてOKです。

![](https://pbs.twimg.com/media/HMC23mDWQAAbPGT.jpg)

## 3. Type of Appを選ぶ

ローカルのCodexやMCPからOAuth認証する場合は、Web App, Automated App or Botを選びました。これはConfidential clientとしてClient Secretを使える設定です。

![](https://pbs.twimg.com/media/HMC24HHWgAA_i4p.jpg)

## 4. Callback URLを入れる

Callback URI / Redirect URLには http://localhost:8080/callback を入れます。ここは認証URLに含まれるredirect_uriと完全一致していないと、「アプリにアクセスできません」のようなエラーになります。

Website URLは必須なので、自分のサービスURLや関連リポジトリURLを入れます。今回の例ではX MCP skillのGitHubリポジトリURLを使いました。

![](https://pbs.twimg.com/media/HMC24nIWcAAU56b.jpg)

## 5. Client IDとSecretをCodex側へ設定

保存後に表示されるClient IDとClient Secretを、ローカルの環境変数や秘密情報ファイルに設定します。ここで大事なのは、SecretをGitHubや記事本文に貼らないこと
