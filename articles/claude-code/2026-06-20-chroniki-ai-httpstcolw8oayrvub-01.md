---
id: "2026-06-20-chroniki-ai-httpstcolw8oayrvub-01"
title: "@chroniki_ai: https://t.co/Lw8OAyrvub"
url: "https://x.com/chroniki_ai/status/2068460320159633455"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "x"]
date_published: "2026-06-20"
date_collected: "2026-06-21"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

https://t.co/Lw8OAyrvub


--- Article ---
■ 地形も草木も動物も、全部AIが配置してしまった

「こんな感じの自然マップにして」って自然言語で指示したら、地形が生まれて、木が植わって、動物が追加されて、歩行アニメーションまでセットアップされてしまった——そんなデモ動画が公開されて、僕もじっくり調べてみました🐾

コードを1行も書かず、アセットを手動で配置することもなく、ゲームのステージがほぼ完成しているんです。

「ゲーム開発の話でしょ」って思った方もいるかもしれないんですが、これって実はClaude Codeを使っているすべての人に関係する話で、「AIに外部ツールを直接操作させる」という考え方の最前線なんです。

今回はUnreal Engine 5.8とMCPの組み合わせで何が起きているのか、MCPって何？というところから順番に整理してみます。

![](https://pbs.twimg.com/media/HLSkYN5b0AAZTHu.jpg)

■ そもそもMCPって何？

MCP（Model Context Protocol）は、ClaudeなどのAIを外部ツールと繋ぐための標準規格のことです。

プロトコル（Protocol）というのは「共通のやりとりのルール」みたいなイメージで、異なるソフトウェア同士が「同じ言葉で会話できる」ようにするための仕様のことです。

Anthropicが2024年末にオープン仕様として公開していて、今ではClaude Code・Cursor・Windsurfといった主要なAI開発ツールが対応しています。

ざっくり言うと「ClaudeがいろんなツールのAPIや機能を、統一された方法で呼び出せるようにする窓口」みたいなものです。

これ以前は、AIを外部ツールと連携させようとすると、ツールごとにバラバラな実装が必要で、開発者にとってなかなかしんどい作業でした。

MCPがあることで「つなぎ方の共通ルール」ができて、一度覚えれば色々なツールに応用できるようになってきているんです。

![](https://pbs.twimg.com/media/HLSkkWPbAAAjl5Q.jpg)

■ Unreal Engine 5.8で何が変わったのか

Unreal Engine 5.8では、MCPプラグインが公式に組み込まれました。

Unreal Engine（アンリアルエンジン）というのは、Epic Gamesが開発している有名なゲームエンジンで、フォートナイトや多くのAAAゲームのベースになっているツールです。映像制作や建築ビジュアライゼーションにも使われています。

5.8でMCPプラグインが入ったことで何が変わるかというと、Unreal Editorの中にMCPサーバーが立ち上がって、Claude CodeやCodexといったAIツールがエディタを直接操作できるようになったんです。

今まで「AIにコードを書いてもらう」という使い方が主流でしたが、ここではAIが「エディタそのものを動かす」という段階になっています。

地形を生成する、アセットを配置する、アニメーションを設定する、といった操作を、人間がボタンを押す代わりにAIが実行してくれる感じです。

Epic Gamesの公式ドキュメントでも「Unreal MCP」として整備が進んでいて、実験的な機能ながらも公式サポートがある状態です。

![](https://pbs.twimg.com/media/HLSkwiHbYAA3xPE.jpg)

■ セットアップの手順を整理すると

実際にどうやって動かすのか、手順を整理してみます。

① Unreal Engine 5.8を開いて「Edit → Plugins」でUnreal MCPプラグインを有効化

② エディタ設定（Editor Preferences）→「General」→「Model Context Protocol」から「Auto Start Server」をONにする

　→ これでエディタを起動するたびに自動でMCPサーバーが立ち上がります（アドレスはhttp://127.0.0.1:8000/mcp）

③ Claude Code（またはCodexなどMCP対応のAIツール）の設定ファイルに、UnrealのMCPサーバーアドレスを追加する

④ あとはClaude Codeのターミナルから自然言語で指示するだけ

ポイントは②の「Auto Start Server」のあたりで、これをONにしておくと毎回手動でサーバーを起動しなくてよくなるんです。

③のMCP設定ファイルへの追加については、Claude Codeのド
