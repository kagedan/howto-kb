---
id: "2026-04-16-claude活用術playwright-mcpで開けないサイト問題を解決する方法-01"
title: "【Claude活用術】Playwright MCPで「開けないサイト」問題を解決する方法"
url: "https://note.com/shuu_10to1000/n/n465229255705"
source: "note"
category: "ai-workflow"
tags: ["MCP", "note"]
date_published: "2026-04-16"
date_collected: "2026-04-16"
summary_by: "auto-rss"
query: ""
---

※ この記事は約2分で読めます。

---

■ 「Claudeでサイトが開けない！」という壁

Claude Desktopには「Chrome拡張」という機能があって、ブラウザを操作してWebサイトを見に行ってくれます。

「今日の天気を調べて」「このサイトの情報をまとめて」

こんなお願いができる、とても便利な機能です。

ところが、一部のサイトにアクセスしようとすると……開けない。エラーになる。

「なんで？」と思いますよね。

実はこれ、Chrome拡張の技術的な制約が原因なんです。でも、ある方法を使えば簡単に解決できました。

それが「Playwright MCP」です。

■ Playwright MCPってなに？

ざっくり言うと、Claudeが「もうひとつ別のブラウザ」を使えるようになる仕組みです。

普段のChrome拡張は、あなたが使っているChromeブラウザの中で動きます。一方、Playwright MCPは新しいブラウザを別に立ち上げて、そこで操作を行います。

イメージとしては：

・Chrome拡張 → あなたのブラウザの「中」で動く  
・Playwright MCP → 新しいブラウザを「外」に用意して動く

この「外に用意する」というのがポイントで、Chrome拡張の制約を受けないため、今まで開けなかったサイトにもアクセスできるようになります。

■ なぜChrome拡張だと開けないの？

少しだけ技術的な話をすると、Chrome拡張はブラウザの「拡張機能API」という仕組みを使っています。

この仕組みには、セキュリティ上の制限がいくつかあります。

・サイト側が「拡張機能からの操作をブロック」している場合がある  
・CSP（コンテンツセキュリティポリシー）という仕組みで、外部からのスクリプト実行が制限される  
・一部の保護されたページにはそもそもアクセスできない

一方、Playwright MCPは「Chrome DevTools Protocol」というブラウザをもっと低いレベルで直接制御する方式を使っています。拡張機能APIを経由しないので、これらの制約を受けにくいんです。

■ 使い分けはこうする！

じゃあ全部Playwrightでいいの？というと、そうでもありません。

それぞれに得意なことがあります。

【Chrome拡張を使う場面】  
・ログイン済みのサービスを操作したい（Gmail、Xなど）  
・今見ているタブの内容を読み取りたい  
・自分のアカウントのCookieやセッションが必要な作業

【Playwright MCPを使う場面】  
・ログイン不要なサイトの情報収集  
・Chrome拡張ではアクセスできなかったサイト  
・天気、ニュース、価格比較などの調べもの

ひとことでまとめると：

「ログインが要る → Chrome拡張」  
「調べるだけ → Playwright MCP」

これだけ覚えておけばOKです！

■ 導入方法（5分で完了）

実際にPlaywright MCPを導入する手順を紹介します。

【ステップ1】Node.jsをインストール  
Playwright MCPを動かすにはNode.jsが必要です。  
公式サイト（[https://nodejs.org/）からダウンロードしてインストールしてください。](https://nodejs.org/%EF%BC%89%E3%81%8B%E3%82%89%E3%83%80%E3%82%A6%E3%83%B3%E3%83%AD%E3%83%BC%E3%83%89%E3%81%97%E3%81%A6%E3%82%A4%E3%83%B3%E3%82%B9%E3%83%88%E3%83%BC%E3%83%AB%E3%81%97%E3%81%A6%E3%81%8F%E3%81%A0%E3%81%95%E3%81%84%E3%80%82)

【ステップ2】設定ファイルを編集  
エクスプローラーのアドレスバーに以下を入力してEnter：

%APPDATA%\Claude

このフォルダにある「claude\_desktop\_config.json」をメモ帳で開きます。  
（ファイルがなければ新規作成）

以下の内容を追記します：

{  
"mcpServers": {  
"playwright": {  
"command": "npx",  
"args": ["@playwright/mcp@latest"]  
}  
}  
}

※ 既に他の設定がある場合は、mcpServersの部分だけ追加してください。

【ステップ3】Claude Desktopを再起動  
タスクバーの右下にあるClaudeのアイコンを右クリックして「終了」。  
その後、もう一度Claude Desktopを起動すればOK！

【確認方法】  
Claudeに「Playwrightを使ってGoogleを開いて」とお願いしてみてください。  
新しいブラウザが立ち上がってGoogleが表示されたら成功です！

■ まとめ

・Chrome拡張で開けないサイトがある → Playwright MCPで解決！  
・仕組みの違い：拡張機能API vs ブラウザ直接制御  
・使い分け：ログインが要る作業はChrome拡張、調べものはPlaywright  
・導入は設定ファイルに数行追記するだけ

Claudeをもっと便利に使いたい方は、ぜひ試してみてください。  
ブラウザ操作の幅がグッと広がりますよ！

---

[#Claude](https://note.com/hashtag/Claude) [#AI活用](https://note.com/hashtag/AI%E6%B4%BB%E7%94%A8) [#PlaywrightMCP](https://note.com/hashtag/PlaywrightMCP) [#Claude活用術](https://note.com/hashtag/Claude%E6%B4%BB%E7%94%A8%E8%A1%93) [#AI初心者](https://note.com/hashtag/AI%E5%88%9D%E5%BF%83%E8%80%85)
