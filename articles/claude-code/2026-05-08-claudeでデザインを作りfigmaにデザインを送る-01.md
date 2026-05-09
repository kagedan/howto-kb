---
id: "2026-05-08-claudeでデザインを作りfigmaにデザインを送る-01"
title: "Claudeでデザインを作りFigmaにデザインを送る"
url: "https://zenn.dev/misumith/articles/0375e7f455bd47"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-05-08"
date_collected: "2026-05-09"
summary_by: "auto-rss"
query: ""
---

こちらの記事を参考にAIにデザインを作ってもらい、それをFigmaに送るのをやってみました。  
<https://dev.classmethod.jp/articles/claude-code-seminar-design-talk-report/>

記事と違うのはClaudeでデザインをしています。  
Claude Designを使うと現状は週間制限の上限にあっという間に達してしまうので、Claudeでできないか試してみました。

Claude Designの場合はデザインを作ったあとに「Handoff to Claude Code」で表示されたプロンプトをClaude Codeにに貼り付けるとNext.jsでアプリ化してくれて、それをFigmaに送ります。

Claudeには「Handoff to Claude Code」がないので、別の方法でやりました

## 1. デザインを作ってもらう

適当にスムージーのLPをデザインしてもらいました。  
![](https://static.zenn.studio/user-upload/e536d404eeca-20260508.png)

## 2. HTMLを保存

HTMLをダウンロードなどと伝えると、スタイリングした状態のhtmlファイルをダウンロードできます。

## 3. Claude Codeに渡す

ダウンロードしたhtmlをClaude Codeに貼り付け、「このHTMLファイルを参考に、Next.jsでLPを実装して」と指示します。  
複数画面の場合は「このHTMLファイルを参考に、同じデザインのLPをNext.jsで実装して。  
App Routerを使い、画面ごとにコンポーネントを分けてほしい。」と指示します。

## 4. Figmaに送る

作成されたアプリを`npm run dev`で立ち上げ、「<http://localhost:3000/> をFigmaに送信してください」と指示します。

### Figma MCPの設定がまだの場合

ターミナルで以下を実行

```
claude mcp add --transport http figma https://mcp.figma.com/mc
```

`/mcp` でfigmaを選択し、認証する。

---

Claude Designで「Handoff to Claude Code」をやっていたところを、htmlで書き出す手間を追加しただけです。

これでClaude Design使わなくても制限を気にせずデザイン作れると思いましたが、デザインのクオリティや修正の意図の汲み取り方はClaude Designの方がはるかに良いです

Claude Designもhtmlで書き出せるので、Claude Designである程度のところまで作り、Claudeにhtmlを渡して修正してもらうこともできましたが、なかなか意図を汲み取ってくれなかったりしました。

Claude Designが制限を気にせず使えるようになったら嬉しいです。
