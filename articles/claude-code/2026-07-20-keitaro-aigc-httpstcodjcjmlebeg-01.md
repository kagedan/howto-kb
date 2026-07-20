---
id: "2026-07-20-keitaro-aigc-httpstcodjcjmlebeg-01"
title: "@keitaro_aigc: https://t.co/DjcjMLEbeg"
url: "https://x.com/keitaro_aigc/status/2079312549783466415"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "x"]
date_published: "2026-07-20"
date_collected: "2026-07-21"
summary_by: "auto-x"
query: "Claude プロンプト 書き方 OR Claude 業務効率化 実例"
---

https://t.co/DjcjMLEbeg


--- Article ---
Claude CodeとObsidianを両方使っていて、こんな場面はありませんか。

- Wikilinkにしてほしいのに、普通のMarkdownリンクになる
- propertiesやcalloutの書き方が微妙に違う
- .baseや.canvasを編集させるのが怖い
- Web記事をメモにするたび、広告やナビを手で消している
先に結論をお伝えします。 AIにObsidianを触らせるなら、毎回長いプロンプトを書くより、Obsidianの流儀をスキルとして渡す方が自然です。 その完成例を、Obsidian CEOのSteph Ango（kepano）氏がGitHubで公開しています。

この記事で分かるのは、次の5つです。

1. 42,700スターを集めたobsidian-skillsの正体
1. 公開されている5スキルの役割
1. Claude Codeへの現在の導入方法
1. 導入前に知っておきたい限界と安全面
1. この設計を自分の仕事へ転用する型
Obsidianユーザーは、そのまま使えます。 Obsidianを使っていない人も、「自分の仕事ルールをAIへ渡す方法」の実例として保存する価値があります。

## 42,700スターの正体は、AIに渡せる「仕事の作法」です

この動きを紹介したAI情報アカウントchewadot氏の投稿は、2026年7月12日時点の表示で約57.9万ビューを記録しました。 参照URL: https://x.com/chewadot/status/2076107957277008100 投稿では、kepano氏が自分のVaultで使っていたAgent Skillsを公開し、数週間で4万スターを超えたと紹介されています。

GitHubの一次情報を確認すると、2026年7月21日時点でリポジトリは42,700スター。 参照URL: https://github.com/kepano/obsidian-skills 5つのスキルが公開され、ライセンスはMITです。

ここで大事なのは、単なる「Claude CodeとObsidianの連携プラグイン」ではないことです。 中に入っているのは、AIに仕事の作法を教えるための指示書です。 たとえば、普通のMarkdownとObsidian Flavored Markdownは似ています。

しかし、Wikilink、埋め込み、callout、propertiesまで正しく扱うには、Obsidian固有の知識が必要です。 人間なら無意識に守っているルールを、AIが読めるSKILL.mdへ落とす。 この「暗黙知のファイル化」が、リポジトリの正体です。

なお、42,700スターは品質を保証する数字ではありません。 注目度の目安としては強い一方、自分のVaultで安全に動くかは別に確認する必要があります。

## 5つのスキルが、Obsidianの壊れやすい部分を分担します

公開されているのは、次の5つです。

1. obsidian-markdown

Obsidian Flavored Markdownを作成・編集するためのスキルです。 Wikilink、埋め込み、callout、propertiesなど、Obsidian固有の記法をAIへ教えます。 普通のMarkdownとしては正しくても、Obsidianでは使いにくい。

その微妙なズレを減らす役目です。

2. obsidian-bases

Obsidian Basesの.baseファイルを扱うためのスキルです。 views、filters、formulas、summariesなどを使い、ノート群を表やリストとして見られる形へ整えます。 案件一覧、読書リスト、コンテンツ企画、タスク管理のような用途と相性がよさそうです。

3. json-canvas

JSON Canvasの.canvasファイルを作成・編集するためのスキルです。 nodes、edges、groups、connectionsの構造を理解させ、AIがキャンバスを扱うときの事故を減らします。 ただし、「絶対に壊れない」という保証ではありません。

大事なCanvasは複製かGit管理をしてから編集させるのが安全です。

4. obsidian-cli

Obsidian CLIを通じてVaultを操作するためのスキルです。 ノートを読む・作るだけではなく、プラグインやテーマ開発まで含むCLI操作の知識をAIへ渡します。

5. defuddle

Webページから本文を抽出し、きれいなMarkdownへ変換するスキルです。 広告、ナビゲーシ
