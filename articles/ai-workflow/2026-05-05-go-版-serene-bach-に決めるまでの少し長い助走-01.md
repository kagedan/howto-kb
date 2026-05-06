---
id: "2026-05-05-go-版-serene-bach-に決めるまでの少し長い助走-01"
title: "Go 版 Serene Bach に決めるまでの、少し長い助走"
url: "https://zenn.dev/serendipitynz/articles/3c1d592e31da0e"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-05-05"
date_collected: "2026-05-06"
summary_by: "auto-rss"
---

[Serene Bach v3](https://serenebach.net/) を作り直したい、という気持ちは前からありました。

![](https://static.zenn.studio/user-upload/ee47273699ef-20260505.png)

2007/12/04 に公開開始してからおよそ 10 年ほど開発を細々と続けていて、2017/06/30 以降、ずっと「いつかやる」の棚に入ったまま、およそ 10 年近く放置状態でした。

今回その棚から引っ張り出したきっかけは、単純に「今なら AI と一緒に検討を前に進められそうだな」という感覚です。

最初の問いは、わりと素朴でした。Perl CGI 版の Serene Bach をモダンに作り直すなら、どんな技術スタックがよいのか。

Copilot (Claude Opus) にちょっと問い合わせてみたんです。Visual Studio Code で Serene Bach v3 のソースコード置いたフォルダを開いて、

> **Serene Bach v3 をモダンなアプリケーションとして作り直すとしたら、どんな技術スタックが適切ですか**

## Claude さんが提示した 3 つの選択肢

* **選択肢A: Next.js (App Router) + TypeScript + Prisma + SQLite/Postgres**
  + *構成*: Next.js（公開側は ISR/SSG、管理画面は RSC + Server Actions）、Prisma + SQLite（Turso/LiteFS）または Postgres、認証は Auth.js、画像は next/image + S3 互換ストレージ、フィードは Route Handler で出力。
* **選択肢B: Astro + Content Collections + 軽量API（Hono on Cloudflare Workers + D1）**
  + *構成*: 公開側は Astro（MDX 対応、Islands で必要部分のみ JS）、執筆 UI は Astro 内の管理ルート or 別 SPA、DB は Cloudflare D1（SQLite）、画像は R2、コメント/トラックバックは Hono の API。
* **選択肢C: Go (or Rust) 単一バイナリ + htmx + SQLite**
  + *構成*: Go（chi or Echo）+ templ/html-template + htmx + SQLite（WAL）、画像は local+サムネイル生成、feed/XML-RPC もそのまま実装可能。

ここ数年、ウェブフロントエンド開発を主な業務としていたので、TypeScript はほぼ毎日触れています。 Next.js も Astro もそこそこ触れています。

なので A と B は割とすんなりイメージできました。実際、Serene Bach の管理画面は今なら React 的に作るんだろうな、と思ってもいたので。

だから **Go で作る** というのが全く想像つかず、思わず追加で

> 選択 C は未検討な方向性でした。もう少し具体的に確認したいです。 C はどのような環境で動作させる前提になりますか？

質問して深掘っていきました。

私からの質問（プロンプト）を並べると……

> 選択 C で現在の機能から落ちてしまうものとしてはどんなものがありますか

> 選択 B だとどうでしょうか。どの機能が落ちるでしょうか。

> 選択 C について、Go or Rust という観点だと何を基準に選択することになりそうでしょうか

> 気軽に置くというのをどこまで実現できるか。VPS はレンタルサーバほど気軽でも低コストでもないですよね？

> なるほど一応 Go CGI モードでレンタルサーバ運用は行けるのか

> ちなみに Go 以外の言語選択は全くない感じですか？ Python とか

> Go + htmx + sqlite な既存アプリもあるんですよね？そこに Serene Bach を作っていく意義的なものとしてどんなものがありますか？

## 何を比べると見えてくるか

会話を振り返ってみると、単なる技術比較よりも、比較軸をどこに置くかで答えが変わる話でした。

ひとつは「公開面の強さ」を重視する軸です。ここでは B（Astro + Cloudflare）がかなり強く見えます。静的再構築との相性がよく、配信コストも低く、静的構築されたサイトは速い。Serene Bach でも「静的ファイルを生成する」という軸はそれなりにこだわった部分でもあります。

一方で、自分の環境に構築できるという点もそれなりに意識していたことが分かってきました。

言い換えると「所有感」と「設置の自由度」を重視する軸です。

この点から見ると、 Go を使った技術スタックに俄然興味を引かれます。単一バイナリをただ置けばよく、VPS でも Raspberry Pi でも置けること、そして場合によってはレンタルサーバで Go CGI モードを狙えること。

実のところ、Astro + Cloudflare の運用はすでに実践はしていて、柔軟性や静的生成の強さも知っています。Astro は割と好きなフレームワークのひとつです。Cloudflare の運用コストも信じられないぐらいかからない。

先に挙げた私からの質問にもあった通り、「何が落ちるか」も AI を通して考察しました。Go で Serene Bach を開発し直すと運用コストを全部ゼロにはできなくなるでしょうし、ぶっちゃけ Perl を使わない時点で Perl CGI 版との互換性は基本捨てることになるでしょう。

自分が使うツールとして残しておきたい機能（逆に言うと捨ててもよいと私が思う機能）、今の Serene Bach にはないけど、取り入れたい機能も見えてきました。

## 言語化のその先

いわゆる「壁打ち」ってやつになるんですが、これまで脳内でやってきたひとりブレインストーミングが AI を通すと記録に残ったものになります。

脳内だとどうしても第三者視点を作るのが難しいのですが、AI だとそこもあっさり乗り越えてくれます。

スタートは「どの技術が正解」という問いだった気がしますが、通して得られたのは「Serene Bach という名を冠すとしたらどんな形にしたいか」でした。

> **バイナリ一本配布が気に入ったし、そこは未知の領域なので、Copilot に大いに助けていただけそうです。Go にしましょう**

Go 版 Serene Bach は、<https://go.serenebach.net/> ならびに <https://github.com/serendipitynz/serenebach> でβ版を公開中です。
