---
id: "2026-06-09-claude-desktopを活用したbacklogの確認-01"
title: "Claude Desktopを活用したBacklogの確認"
url: "https://qiita.com/tosimitsu104/items/9777550d469f35057504"
source: "qiita"
category: "claude-code"
tags: ["MCP", "API", "qiita"]
date_published: "2026-06-09"
date_collected: "2026-06-17"
summary_by: "auto-rss"
query: ""
---

## はじめに

最近、Claudeを契約してもらい業務利用を始めました。手始めにBacklogの状況確認を試してみたので記事にします。
この内容にした理由は、マネージャー職がタスク確認作業に関してプロジェクトを横断的に確認したいというニーズがあったためです。

## 手順

まず、以下の準備をします。

- Claude Desktop
- Backlog API Key

※ ClaudeとBacklogは契約済み前提です

https://claude.com/ja/download

`Customize`からコネクタの設定を開きます。

![スクリーンショット 2026-06-08 12.02.45.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3635206/5104d3fd-8f63-49cb-b42a-9aee432fccfb.png)

コネクタのプラスマークをクリックして`Backlog MCP Server`を検索します。
`Backlog MCP Server`とは、ClaudeがBacklogのプロジェクト管理を行うために必要なMCP Serverです。

![スクリーンショット 2026-06-08 13.18.56.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3635206/879dd64e-747d-46b2-88fa-2df4bd193cf1.png)

![スクリーンショット 2026-06-08 13.21.14.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3635206/5bef8596-1918-412c-bdb9-697736470440.png)

表示された`Backlog MCP Server`をクリックしインストールします。
「必要な条件」を満たしていることを確認してください。

![スクリーンショット 2026-06-08 13.27.35.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3635206/f36d7e7c-81dc-4b3b-9aa9-47eb565943d5.png)

インストールすると`Backlog API Key`と`Backlog Domain`の入力が求められるので入力します。

`Backlog API Key`はBacklogヘルプセンターの[APIの設定](https://support-ja.backlog.com/hc/ja/articles/360035641754-API%E3%81%AE%E8%A8%AD%E5%AE%9A)を参考にAPI Keyを取得して入力します。
`Backlog Domain`は現在利用中のBacklogドメインです。
`xxxxx.backlog.com`、`xxxxx.backlog.jp` など

入力したら機能が有効になっていることを確認して、有効になっていない場合は有効にします。

![スクリーンショット 2026-06-08 13.41.53.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3635206/32c9d43a-2172-473e-a83d-2a3aa4f05284.png)

ここまでで、準備は完了です。

## 使用方法

チャット欄で`Backlog`を含む文章を入力すると、自動的に`Backlog MCP Server`を使用してデータを取得してくれます。

![スクリーンショット 2026-06-08 14.01.41.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3635206/d00279a7-3e30-480b-b584-3a983887c5a8.png)

:::note warn
注意
取得できるプロジェクトは、**Backlog API Keyを発行したユーザーがメンバーのプロジェクト**のみです。
Backlog API Keyは必ずClaude利用者と同じユーザーが発行するようにしてください。
:::

プロジェクトの取得については次のこともできます。
- 取得する期間の指定
- 任意のプロジェクトメンバーのタスク確認
- 複数プロジェクトの横断確認

チャットの入力内容によってはチェックボックスから複数選択できるようになります。

![スクリーンショット 2026-06-08 14.31.09.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3635206/cfb86f20-2733-4711-bc0b-86b070267945.png)

また、各月のタスク総数をグラフで出力させて繁忙期の把握に繋げることも可能です。

![backlog_monthly_tasks_2026.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3635206/c021f6f9-7c1c-43f1-a299-d3710c042216.png)

## Skillの活用

ここまで出来ることをまとめましたが、毎回プロンプトを入力するのは手間がかかります。そこで、Skillを活用することでその手間を省けます。
Skillとは、AIに与える知識や手順をパッケージ化し必要な時に呼び出せる機能です。

手動での作成も可能ですが、「スキルを作りたい」とClaudeに伝えるだけで、対話形式でスキル作成を進めてくれます。

![スクリーンショット 2026-06-08 15.12.07.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3635206/8339e32c-298e-46ba-9cbe-e35870cec669.png)

もしくは、より細かい指示を伝えることで沿った内容のスキルを作成してくれます。
例えば、プロジェクトの誤った更新を防ぐためAPI利用はデータ取得のみに制限するなど。

作成したスキルは、`Customize`のスキルに作成されます。Claudeユーザー同士で共有することも可能です。今回私は、`backlog-report`というスキルを作成しました。
状況把握のパターンを選んで欲しい情報のレポートをBacklogから得るスキルです。

![スクリーンショット 2026-06-08 15.18.38.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3635206/b59bba61-5ad0-449c-9c87-83d8a47fe199.png)

スキルを使用したい場合は、スラッシュコマンド `/backlog-report`で使用することができます。

![スクリーンショット 2026-06-08 15.21.47.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3635206/4c34f72a-ec34-40dc-9cc7-89b48b756d5d.png)

得られた情報からAIに状況の分析などさせるとMCPを活用している感が増して良いですね。

![スクリーンショット 2026-06-11 11.31.40.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3635206/6f5e644e-4b96-441b-afb1-aff7d5d7448e.png)

※画像の内容はあくまでも仮データを分析させた例です。

## まとめ

今回は、`Claude`と`Backlog API`、`Backlog MCP Server`を使用してプロジェクトを横断的にタスク確認できるようにしました。Skillを活用することで、毎回のチャット入力をすることなく必要な処理を実行させることができます。

プロジェクト管理者によって重点的に確認する内容は異なると思うので、Skillをカスタマイズしていくことが大切です。今回の投稿が、皆さんの業務改善に繋がることができれば幸いです。
