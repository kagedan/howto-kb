---
id: "2026-04-26-7oyakata-claude-codeとx自動化をdiscordで連携する方法-xの投稿を自動化し-01"
title: "@7oyakata: Claude CodeとX自動化をDiscordで連携する方法 Xの投稿を自動化してるけど、スマホからも操作したい…と"
url: "https://x.com/7oyakata/status/2048216087993675997"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "GPT", "Python"]
date_published: "2026-04-26"
date_collected: "2026-04-28"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

Claude CodeとX自動化をDiscordで連携する方法

Xの投稿を自動化してるけど、スマホからも操作したい…という人へ。

Discord MCPを使えば、Discordに送るだけでClaude Codeが動いてポストが飛ぶ仕組みが作れる👇

1. APIキーを2つ用意する
Discord Developer PortalでBot tokenを取得。
X（Twitter）Developer PortalでAPI keyも取得。
この2つが手元にあれば準備完了。

2. 連携スクリプトを用意する
Node.jsかPythonで「Discordのメッセージを受け取ったらClaude APIに渡してXに投稿する」スクリプトを書く。
Claude Codeに「Discord→Claude→X連携スクリプト作って」と頼めば1分で生成してくれる。

3. Claude Codeに投稿ルールを渡す
CLAUDE.mdに「投稿のトーン」「NGワード」「ハッシュタグのルール」を書いておく。
これだけで毎回指示しなくても自分のスタイルで投稿してくれるようになる。

4. スマホのDiscordから動かす
スクリプトを常時起動しておけば、あとはDiscordに「これ投稿して」と送るだけ。
外出先でもスマホ一台で投稿が回るようになる。

ある程度のコード実装は必要だけど、Claude Codeに全部作らせればOK


--- 引用元 @7oyakata ---
Claude Codeをインストールしたら最初にやること7選

ChatGPTは使ってるけどClaude Codeはよくわからない…という人へ。

初期設定をちゃんとやるだけで、ただのAIツールが「自分の代わりに仕事する存在」に変わるわえぐい…👇

1. CLAUDE .md に行動ルールを書く

Claude Codeに「これはやっていい、やってはダメ」を事前に伝えておくファイル。

触ってほしくないファイルや使ってほしくないコマンドをここに書くだけ。毎回ゼロから指示しなくて済むようになる。

2. スキルクリエイター導入

「X投稿を作って」「スライドを作って」という作業を、コマンド一つで自動化できる型を作るプラグイン。

最初にこれを入れておくと、毎回ゼロから指示する手間がなくなる。

3. 自動承認モードを理解する

Claude Codeは普段、作業のたびに「これやっていいですか？」と確認してくる。

オートモードにするとその確認をスキップして一気に進む。

4. Obsidianでナレッジ管理

Obsidianは無料のメモアプリ。Claude Codeと相性が抜群。

作ったスキルの説明書やマニュアルを自動生成してフォルダに保存するだけ

5. モデルを使い分ける

/modelコマンドでAIの種類を切り替えられる。

複雑な作業はOpus（高精度）、単純な作業はSonnet（速い・コスパ良）。これだけでコストがかなり変わる。Sonnetだけでもまぁ十分。

6. Discord MCP接続

Discordと連携するとスマホからClaude Codeに指示できる。

「このサムネ作って」とDiscordに送るだけで完成ファイルが返ってくる。パソコンの前にいなくても作業が回るようになる。
