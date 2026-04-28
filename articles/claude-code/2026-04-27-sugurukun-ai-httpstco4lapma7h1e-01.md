---
id: "2026-04-27-sugurukun-ai-httpstco4lapma7h1e-01"
title: "@SuguruKun_ai: https://t.co/4lAPMA7h1E"
url: "https://x.com/SuguruKun_ai/status/2048729561089888571"
source: "x"
category: "claude-code"
tags: ["claude-code", "API", "LLM", "Gemini", "GPT", "x"]
date_published: "2026-04-27"
date_collected: "2026-04-28"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/4lAPMA7h1E

これも読むべき：
https://t.co/GPPgJ0UVg6


--- Article ---
# 自分のClaude Codeのログを見てみた。直近30日で、Claude以外のLLMを呼び出した回数が**6,866回**あった...

Grok 3,252回。Qwen 2,165回。Codex 1,200回。Gemini CLI 249回。

全部スキルとして組み込んでいて、Claude Codeの中から自然に呼び出せる状態にしてある。「Xで調べて」と言えばGrokが検索し、「Codexに聞いて」と言えばGPT-5.4がセカンドオピニオンを返してくれる。

正直、ここまで使ってるとは自分でも思ってなかった、、

## Grokを使ったリサーチ

毎朝のブリーフィングで最初に動くのがGrok。xAIのAPIで、Xのリアルタイム検索をかける。

![](https://pbs.twimg.com/media/HGbF7GQbIAArYTl.jpg)

![](https://pbs.twimg.com/media/HGbF8w_asAAR6An.jpg)

「AI関連で昨晩バズった投稿」「Claude Code関連の新しい動き」「自分のアカウントへのリプライ」。これを全部Grokが拾ってくる。Claude Code単体だとXの検索はできないんですよ。WebSearchでXの投稿を探しても、ツイートの中身は取れない。GrokならXのデータに直接アクセスできる。

料金はgrok-4-1-fastで$0.20/Mトークン。1回の検索で数円。

で、Grokが拾ってきた情報と、メール・Slack・カレンダーの情報を合わせて、Claude Codeが1つのブリーフィングにまとめてくれる。これが/ohayoコマンド。朝の30分が30秒になります。

## Codexに「これどう思う？」と聞く

![](https://pbs.twimg.com/media/HGbGDsnbcAAOzIx.jpg)

![](https://pbs.twimg.com/media/HGbGFYAbMAADBBG.jpg)

Codexの使い方が一番意外かもしれない。自分のログを見返したら直近30日で1,200回呼んでたんですけど、用途がコードレビューだけじゃなかった。

**UIデザインレビュー**: Draftflow（自作のX投稿管理アプリ）のフロントエンドをリデザインしたとき、「このカラーパレットとフォント選択は適切か」「カードの情報量が多すぎないか」をCodexに聞いた。4ラウンドくらいやりとりして、毎回具体的に「ここのインディゴをニュートラルに」みたいな指摘が返ってきた。

**800人講座の準備チェック**: 4月に800人以上のClaude Code講座を開催したんですけど、準備の最終チェックをCodexに投げました。「漏れやリスクがないか網羅的にチェックして」と。Zoom設定、スライド枚数、ワークショップの進め方、全部GPT-5.4にレビューさせた。

**SEO戦略の相談**: 3サイトのSEO改善戦略を聞いたり、「この交流会に行く価値あるか」みたいなビジネス判断まで。

要するにCodexの役割は「コードレビュアー」というより**「経営アドバイザー」**に近い。GPT-5.4の推論力で「この方針で問題ないか」という高レベルの判断を聞く。Claudeが実行する側、Codexが判断する側。

# Geminiでデザイン・コーディングしてみる

![](https://pbs.twimg.com/media/HGbGL6YacAIpt_9.jpg)

![](https://pbs.twimg.com/media/HGbGNx-bUAAhQD_.jpg)

![](https://pbs.twimg.com/media/HGbGPXgbEAAdVbj.jpg)

Gemini CLI（249回）はもう少し技術寄りで、Claude Codeが書いたコードを別のLLM（Gemini 3.1 Pro）に見せて「違う視点で指摘してもらう」。同じAIに書かせてレビューさせても同じバイアスがかかるんですよね。別のモデルに見せると全然違う指摘が飛んでくる。

##  Qwenが2,165回動いてた

ログを見て一番驚いたのがQwen。直近30日で2,165回。Grokに次いで2番目に多い。

![](https://pbs.twimg.com/media/HGbGRMubgAA38Bi.jpg)

Ollama経由でQwen 3.5をローカルで動かしてます。オフライン。API代ゼロ。データが外部に送信
