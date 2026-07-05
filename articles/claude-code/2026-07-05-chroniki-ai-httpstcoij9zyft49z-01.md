---
id: "2026-07-05-chroniki-ai-httpstcoij9zyft49z-01"
title: "@chroniki_ai: https://t.co/ij9zYFT49Z"
url: "https://x.com/chroniki_ai/status/2073852336167125224"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "x"]
date_published: "2026-07-05"
date_collected: "2026-07-06"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

https://t.co/ij9zYFT49Z


--- Article ---
■ 1行プロンプトで、チャートが勝手に動いた

「RSIが30以下かつ出来高が200%以上急増しているBTC先物を全部探せ」

この1行をClaudeに渡したら、12秒後にはTradingView上でチャートのスキャン・サポートライン描画・Pine Scriptの実行まで全部終わっていたんです。マウスには一切触れていません。これ、最初に見たときは正直「え、これ本当に動いてる？」ってなりました🤖

トレーダーが毎日何十分もかけていたスクリーニング作業が、自然言語1行で完結するというのは、地味にすごい変化だと思っています。今回はこのデモがどういう仕組みで動いているのか、そしてセットアップに何が必要なのかを丁寧に解説してみます。

![](https://pbs.twimg.com/media/HMfLEU2bkAAfU9g.jpg)

■ 一言でいうと、何が起きているのか

ClaudeがMCP（Model Context Protocol）という仕組みを使って、TradingViewを外部ツールとして直接操作できるようになっています。ユーザーが日本語（または英語）で条件を伝えると、ClaudeがTradingViewに対して一連の操作を自動で実行してくれる、というイメージです。今回のデモで実際にClaudeが行ったのは、次の4ステップです。

・8件以上のBTC先物を自動でスキャン

・該当する全チャートを自動で読み込み

・サポートラインを自動描画

・Pine Scriptを自動で実行

これらすべてを12秒でこなしています。手動でやろうとしたら、チャートを1枚ずつ開いて確認するだけで数十分かかる作業です。

■ そもそもMCPって何？

MCPとは「Model Context Protocol（モデル・コンテキスト・プロトコル）」の略で、AIのClaudeが外部のツールやアプリを操作するための「共通の接続規格」のことです。プロトコルというのは「お互いに話すための決まりごと」みたいなものですね。

わかりやすく言うと、MCPはUSBのコネクタに近いイメージです。パソコンにUSBを挿せばマウスでもキーボードでもカメラでも繋がるように、MCPという共通の口があることで、ClaudeはTradingViewをはじめさまざまな外部ツールと繋がれるようになっています。逆に言うと、MCPがないと、ClaudeはTradingViewの中身に触れることができないんです。

Claudeはこの規格をネイティブ（標準）でサポートしているので、TradingView専用のMCPサーバーと組み合わせると、今回のようなデモが成立します。

![](https://pbs.twimg.com/media/HMfLbiJbAAAzwNg.jpg)

■ どうやって動くのか、仕組みを順番に

「何が何を経由してどうなる」という流れを整理してみると、こんな感じです。

① ユーザーが Claude Code に自然言語でプロンプトを投げる

（「RSI 30以下かつ出来高200%以上のBTC先物を探せ」など）

② Claude がプロンプトを解釈し、必要な操作をリストアップする

（どのチャートを開くか、何を描画するか、どのスクリプトを実行するか）

③ Claude が MCP サーバーを通じて TradingView Desktop に命令を送る

（MCPサーバーは、ClaudeとTradingViewの間に立つ「通訳係」みたいなもの）

④ TradingView Desktop が命令を受け取り、画面上で実際の操作を実行する

（チャートを開く、サポートラインを引く、Pine Scriptを動かすなど）

⑤ 結果がClaudeに返ってきて、ユーザーに報告される

このプロセスが12秒で一気に走るわけです。ClaudeがTradingViewを直接触っているというよりは、MCPサーバーという仲介役を経由して「こうしてほしい」という命令を渡し、TradingViewが実行する、という構造になっています。ここがポイントで、MCPがあることで、ClaudeはTradingViewの内部操作にアクセスできるようになっているんです。

Pine Script（パインスクリプト）というのは、TradingView上で使えるインジケーターや自動描画ツールを作るための専用言語です。今回はこれもClaudeが自動で実行しています。

![](https://pbs.twimg.com/media/HMfLysbbsAAdkgG.jpg)

■ セットアップは何が必要？

「Cla
