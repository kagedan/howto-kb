---
id: "2026-04-21-find-mcp-serverスキルで公開mcpサーバーを探そう-01"
title: "「find-mcp-server」スキルで公開MCPサーバーを探そう"
url: "https://zenn.dev/tetradice/articles/7a962c51d452b8"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "AI-agent", "zenn"]
date_published: "2026-04-21"
date_collected: "2026-04-22"
summary_by: "auto-rss"
---

公開されているスキルを検索するために、Vercel製のAgent Skill「[find-skills](https://zenn.dev/hjpotter1/articles/c187f5123112bb)」を使っている人は多いと思います。  
あれ、AIエージェントに「Vercelへのデプロイに関するスキルを探して」のような曖昧な質問をするだけで、自動でスキルの検索・選別から有効性の検証、インストールまで進めてくれるのがとても便利ですよね。

![image.png](https://res.cloudinary.com/zenn/image/fetch/s--FLp33b-P--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/17947/9876f138-1886-44b4-a8f9-1e8eedfa69e4.png?_a=BACAGSGT)

**公開MCPサーバーも同じように探せると便利！**  
……なのですが、公開MCPサーバーだけをピンポイントで探せるよいスキルは、私が探した限りでは見つかりませんでした。

そこで、**公開MCPサーバー検索用のスキル**を作りました。 [find-mcp-server](https://github.com/tetradice/agent-skills/blob/main/find-mcp-server-ja/SKILL.md)です。

## インストール手順

[Node.js](https://nodejs.org/ja) がインストールされている環境であれば、 `npx skills add` コマンドで一発追加できます。

```
% npx skills add https://github.com/tetradice/agent-skills --skill find-mcp-server-ja --global
または
% npx skills add https://github.com/tetradice/agent-skills --skill find-mcp-server --global
```

## 使い方

AIエージェントに「○○についてのMCPサーバーを探して」のような質問をすると、自動で `find-mcp-server` スキルが読み込まれ、公開MCPサーバーを検索・比較選定したうえでインストールまで行ってくれます。

![image.png](https://res.cloudinary.com/zenn/image/fetch/s--svbmG4Wn--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/17947/249e798c-cfad-46f2-955d-f92af6346a84.png?_a=BACAGSGT)

![image.png](https://res.cloudinary.com/zenn/image/fetch/s--LVnTAdYv--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/17947/9b41459e-46ee-4335-b8d7-173c8f6c962a.png?_a=BACAGSGT)

※どんな感じの回答が返ってくるのかについては、「[実際の動作例](#%E5%AE%9F%E9%9A%9B%E3%81%AE%E5%8B%95%E4%BD%9C%E4%BE%8B)」を参照してください。

検索対象は以下の3サイトです。

## 特徴

* [find-skills](https://zenn.dev/hjpotter1/articles/c187f5123112bb) と同じくらいの気軽さで、公開MCPサーバーの検索とインストールが行えます。
* [find-skills](https://zenn.dev/hjpotter1/articles/c187f5123112bb) と同様に、「ユーザーの目的に合っているかどうか」「人気度（GitHubならスター数やダウンロード数）」「公式か非公式かどうか」など複数の観点で比較検討して、おすすめのものを提示してくれます。
* インストールには `npx add-mcp` を使うので、2026年4月現在、以下すべてのAIツール（AIエージェント）で利用可能です。

  + Antigravity
  + Cline (Visual Studio Code拡張)
  + Cline CLI
  + Claude Code
  + Claude Desktop
  + Codex
  + Cursor
  + Gemini CLI
  + Goose
  + VSCode (GitHub Copilot Chat)
  + GitHub Copilot CLI
  + MCPorter
  + OpenCode
  + Zed

  なお、`npx add-mcp` についての詳細は、以下記事をご参照ください。

<https://zenn.dev/tetradice/articles/b83529348043dd>

## 実際の動作例

例えば、VSCode (GitHub Copilot Chat) から「ExcelファイルをMarkdownに変換できるMCPサーバーを探して」と質問すると、以下のような流れでインストールまで進めてくれます。

![image.png](https://res.cloudinary.com/zenn/image/fetch/s--dRmybkXP--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/17947/6a61363b-a868-488a-96b9-a8a40d76f616.png?_a=BACAGSGT)

![image.png](https://res.cloudinary.com/zenn/image/fetch/s--ba0RarHM--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/17947/f318fa6a-1c16-4a8b-92de-eabe874d4b09.png?_a=BACAGSGT)

![image.png](https://res.cloudinary.com/zenn/image/fetch/s--UsylrX74--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/17947/3c662c32-de93-4bec-91a8-399e69cebe6e.png?_a=BACAGSGT)

![image.png](https://res.cloudinary.com/zenn/image/fetch/s--L6mDLJ0K--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/17947/91aa3a3d-2ff4-4936-9ef4-39611b7fd44e.png?_a=BACAGSGT)

## おわりに

普段からMCPサーバーを利用していて、「便利だけどちょうどいいMCPサーバーを探すのが面倒……」と思っていた方は、ぜひこのスキルを試してみてください！

改善点や気になる点があれば、以下レポジトリでお気軽にIssuesやPull Requestを作成してください。

<https://github.com/tetradice/agent-skills/tree/main>
