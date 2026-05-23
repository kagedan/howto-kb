---
id: "2026-05-22-mastra-announce-mastra-エージェントを開発運用しやすくする-cli-強化-01"
title: "[Mastra Announce] Mastra エージェントを開発・運用しやすくする CLI 強化"
url: "https://zenn.dev/shiromizuj/articles/60c5564a579f49"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "zenn"]
date_published: "2026-05-22"
date_collected: "2026-05-23"
summary_by: "auto-rss"
query: ""
---

# [Mastra Announce] Mastra エージェントを開発・運用しやすくする CLI 強化

[Mastra](https://mastra.ai/) の[公式Blog](https://mastra.ai/blog)で発表された[Announcements](https://mastra.ai/blog/category/announcements)を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。速報性重視でAIの力を多分に使っているので、私自身の考察は少なめです。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

## Mastra が外部コーディングエージェント向けの CLI 操作面を広げた

2026年5月20日、Mastra は **Upgraded Mastra CLI** を発表しました。

今回の発表をひとことで言うと、**コーディングエージェントが Mastra のコードを「書く」段階から一歩進み、「実行、検証、観測、デプロイ」までを CLI 経由で扱えるようにした**という話です。

「**Mastra フレームワークを利用した AI エージェント**」**を開発する時の利便性を上げる**という話題です。以前に書いた以下の記事でも、Mastra公式ドキュメントにアクセスできる**MCPサーバや、Agent Skills** のことを紹介しましたが、今回はそこにさらに **CLI** が加わり、「作るための知識アクセス」だけでなく「作ったあとに実行・検証・運用する操作面」までコーディングエージェントから触りやすくなった、と理解するとつながりが見えやすいと思います。例えば **Claude Code、Codex、GitHub Copilot** を使ったMastra 開発がますます便利になります。

<https://zenn.dev/shiromizuj/articles/3852cf542ea8c1>

発表本文で示されている価値は、単にコマンドが増えたことではありません。Mastra Skills や MCP Docs Server と組み合わせることで、エージェントが「コード生成担当」に留まらず、**プロジェクト運用の実務ループを閉じられる**ようになった点にあります。

Mastra が例として挙げているのは次のような流れです。

* エージェントを複数のプロンプトで試し、結果を見て改善案を出す
* 最近のトレースを取得して傾向を見つけ、面白いケースを eval 用データセット化する
* 変更後のログやトレースを確認し、そのまま修正をデプロイする

必要要件として、CLI は `mastra@1.9.0` 以降が必要です。これは [PR #16128](https://github.com/mastra-ai/mastra/pull/16128) で追加されました。

---

## 背景: なぜ CLI 強化が重要なのか

最近の Mastra は、単にフレームワークとしてエージェントを「作れる」ことより、AI と一緒に実際の開発・運用ループをどう回すかにかなり重心を移しています。

その流れはすでにいくつかの発表に出ていました。

* Mastra Skills によるタスク別の作業手順の明示
* MCP Docs Server による Mastra ドキュメントへの機械的アクセス
* Evals、Observability、Platform まわりの継続的な強化

これまでも、コーディングエージェントは Mastra のコード自体は書けました。しかし現実の開発では、「コードを書ける」だけでは足りません。

* エージェントを実際に呼び出して挙動を見たい
* 変更後にワークフローを動かして確かめたい
* メモリの状態や長期記憶を調べたい
* eval を回して品質差を見たい
* トレースやログを見て不具合を追いたい
* 最後にデプロイしたい

このあたりは従来、人間が Studio やダッシュボード、ローカルスクリプト、各種 API 呼び出しを行き来しながら進めることが多かったはずです。今回の CLI 強化は、そこを **コーディングエージェントが扱いやすいコマンド面にそろえた** と見るのが本質です。

つまり、「Mastra を書く AI」から「Mastra を回す AI」へ一段進めたリリースだと言えます。

---

## 何ができるようになったのか

今回の発表は、CLI の機能を 6 つのまとまりで整理しています。

### 1. Runtime: 実行中サーバーを直接操作する

`Runtime` コマンドは、`--url` で指定した稼働中の Mastra サーバーに対して実行されます。ここで重要なのは、CLI が単なるローカル開発用ではなく、**起動中の Mastra システムへの操作面**になっていることです。

たとえば次のようなことができます。

```
mastra api --url http://localhost:4111 agent run weather-agent '{"messages":"What is the weather in London?"}'
mastra api --url http://localhost:4111 workflow run start weather-workflow '{"inputData":{"city":"London"}}'
mastra api --url http://localhost:4111 tool execute get-weather '{"location":"London"}'
mastra api --url http://localhost:4111 mcp list
```

これで、エージェント実行、ワークフロー開始、ツール実行、MCP サーバー一覧確認までをまとめて CLI から叩けます。本番環境では `--url` を `https://acme.com/api` のようなデプロイ済み URL に差し替えるだけです。

ここが意味するのは、コーディングエージェントが「書いたコードをその場で試す」だけでなく、**既存の Mastra 実行系をオペレーション対象として扱える**ようになったということです。

### 2. Memory: スレッド、長期記憶、ワーキングメモリを読む

Mastra の特徴の一つは、単発の応答ではなく、継続的なメモリやスレッドを扱えることです。今回の CLI 強化では、その部分にも直接アクセスできます。

```
mastra api thread create '{"agentId":"weather-agent","resourceId":"user_123","title":"Support conversation"}'
mastra api memory search '{"agentId":"weather-agent","resourceId":"user_123","searchQuery":"London weather","limit":10}'
mastra api memory current get '{"threadId":"thread_abc123","agentId":"weather-agent"}'
```

この種のコマンドが重要なのは、エージェントの振る舞いを調整するとき、コードだけでなく **記憶状態そのものを確認したい** 場面が多いからです。どんな長期記憶がヒットしているのか、現在の working memory がどうなっているのかをエージェント自身が調べられれば、デバッグや改善の仕方がかなり変わります。

### 3. Evals: データセットと実験を CLI から回す

Mastra がここ数か月強く押しているのが eval です。今回の CLI 強化でも、データセット作成、実験実行、結果取得が含まれています。

```
mastra api dataset create '{"name":"weather-eval"}'
mastra api experiment run <dataset-id> '{"name":"baseline"}'
mastra api experiment results <dataset-id> <experiment-id>
```

この意味はかなり大きいです。コーディングエージェントが変更を入れたあと、すぐに eval を回し、結果を比較して、さらに改善案を出す、というループを CLI だけで組めるからです。

従来の「コード生成 AI」はコードを書いて終わりになりがちでしたが、Mastra はそこに **評価まで含めた改善ループ** を閉じ込めようとしているように見えます。

### 4. Observability: トレース、ログ、スコア、メトリクスを見る

運用フェーズで重要なのは、当然ながら何が起きたかを観測できることです。今回の CLI では、Mastra Platform の observability もコマンド面に入っています。

```
mastra api trace list
mastra api log list
mastra api score list
mastra api metric aggregate '{"name":["mastra_model_total_output_tokens"],"aggregation":"sum"}'
```

これらのコマンドは `.env` にある `MASTRA_PLATFORM_ACCESS_TOKEN` と `MASTRA_PROJECT_ID` を使って各プロジェクトへ問い合わせます。

ここで面白いのは、エージェントが「コードを書く」「実行する」に加えて、**トレースとログを読み、異常傾向を見つける** ところまで担当できるようになることです。人間が observability UI を開かずとも、CLI を通じて同じ情報を扱えるので、AI による運用補助の幅が広がります。

### 5. Platform: デプロイと環境管理までコマンド化する

Mastra はすでに Studio / Server 系の運用面も持っていますが、そこも CLI から触れられるようになります。

```
mastra studio deploy --yes
mastra server env pull > .env.production
mastra server restart
mastra studio deploy suggestions <deploy-id>
```

この部分が強いのは、単にデプロイできるだけでなく、**失敗したデプロイの診断や環境変数の同期まで含めて運用コマンドとしてそろえている** ことです。

つまり、コーディングエージェントが実装後にデプロイまで進み、問題があれば suggestions を取り、必要に応じて再起動や env pull まで行う流れが、かなり現実的になっています。

### 6. Project: 出荷前の検証と管理作業をまとめる

最後に `Project` コマンド群では、lint、migration、auth login のような出荷前・管理系作業が扱われます。

```
mastra lint --preflight
mastra migrate -y
mastra auth login
```

ここは派手ではありませんが、実務上はかなり大事です。どれだけコードを書けても、出荷前に preflight lint を回し、必要な migration を適用し、認証まわりを整えられなければ、本当に「プロジェクトを回せる」とは言いづらいからです。

---

## 何がうれしいのか

今回の発表の価値は、CLI が便利になったこと自体ではなく、**コーディングエージェントに与える操作面が、Mastra のライフサイクル全体に広がった**ことです。

これによって、次のような一連の流れがかなり自然になります。

1. エージェントが Mastra のコードを書く
2. CLI で agent / workflow / tool を実行して確認する
3. memory や observability を見ながら振る舞いを調べる
4. eval を回して品質差を比較する
5. lint / migrate を通して問題がなければ deploy する

この「書く → 試す → 観測する → 評価する → 出す」というループが、Mastra Skills、MCP Docs Server、そして今回の CLI 強化でかなり閉じてきました。タイトルにある `Close the Loop` は、まさにこの意味だと読むのが自然です。

特に重要なのは、運用面を別製品・別画面・別 API に分けず、**エージェントが扱いやすいコマンド面へ統一している**ことです。これにより、人間にとっても AI にとっても、Mastra の開発体験が一段「実務の導線」に近づいたと言えます。

---

## まとめ

Upgraded Mastra CLI は、Mastra にコマンドを少し足したというより、**コーディングエージェントの担当範囲をコード生成から運用ループ全体へ広げるための整備** と見るべき発表です。

Runtime、Memory、Evals、Observability、Platform、Project という 6 つのまとまりを見ると、Mastra が意図しているのは明らかです。エージェントにコードを書かせるだけでなく、Mastra プロジェクトを実行し、状態を読み、評価し、運用し、デプロイするところまで任せられるようにすることです。

Mastra Skills と MCP Docs Server で「どう作るか」を支え、CLI で「どう回すか」を支える。この組み合わせによって、Mastra は AI と一緒にソフトウェアを作るだけでなく、**AI と一緒にソフトウェアを回す** フレームワークへ進んでいるのだと思います。

---

参照:
