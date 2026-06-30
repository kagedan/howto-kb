---
id: "2026-06-30-kurono-ai-ura-httpstcoddctnead0u-01"
title: "@kurono_ai_ura: https://t.co/dDCTnEAd0u"
url: "https://x.com/kurono_ai_ura/status/2071877071828332580"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "prompt-engineering", "API", "AI-agent", "x"]
date_published: "2026-06-30"
date_collected: "2026-07-01"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

https://t.co/dDCTnEAd0u


--- Article ---
- 「CLAUDE.mdにルール書いたのに、全然守ってくれない」
- 「/initで生成したCLAUDE.md、これで合ってるのかわからない」
- 「なんか出力がイマイチだけど、どこを直せばいいかわからない」
そんな人に、僕から伝えたいことがあります。

![](https://pbs.twimg.com/media/HMC6tfjWsAAjjH0.jpg)

> **AIエージェントでの稼ぎ方はこちら👇

[>> くろのの公式LIN**E](https://utage-system.com/line/open/29eSgDJcxiWv?mtid=YdgBFzRGGHTL)

AI×SNSでのマネタイズ7,000万。放置で月300万。Claude Code 2,000時間超え。

**ほとんどの人のCLAUDE.mdはクオリティが低い。** 問題は「何を書いたか」じゃない。「書き方の設計」が根本的に間違っている。

そこで今日は僕が2,000時間かけて辿り着いたルール設計の全技術と、そのままコピペで使えるテンプレート4種を全公開します。

# ■ 9割の人のCLAUDE.mdはクオリティが低い

![](https://pbs.twimg.com/media/HL-GlQBa4AA9OZj.jpg)

## ▍「CLAUDE.mdに全部書け」という常識が、そもそも間違い

99%のCLAUDE.md解説記事はこう言っています。「CLAUDE.mdに書けば強くなる」と。

半分嘘です。

僕が2,000時間使い倒して気づいたんですが、Claude Codeには**7つの指示メカニズム**があります。CLAUDE.mdはその1つに過ぎない。

- CLAUDE.md
- .claude/rules/
- Skills
- Subagents
- Hooks
- Output Styles
- System Prompt
この7つを適材適所で使い分けるのが正解。

しかもCLAUDE.mdは「ガイダンス」であって「命令」ではない。**100%守る保証なんてどこにもありません。**

全部CLAUDE.mdに書くのは、全社員宛メールで1人への連絡をするのと同じ。ノイズだらけになって、本当に大事なルールが埋もれるだけ。

CLAUDE.mdに書くべきは「全セッションで必要な情報だけ」。僕はこの大前提に気づくまでに数百時間かかりました。ここを間違えている人が多すぎます。

## ▍/initで自動生成したCLAUDE.mdは微妙

![](https://pbs.twimg.com/media/HL-GqWDbMAEpFaU.jpg)

/initはClaude Codeが自動でCLAUDE.mdを生成する機能。公式にもある。でもこれ、**最悪手です。**

HumanLayerのブログにこんな一節があります。「CLAUDE.mdはAIチームメイトとの最高レバレッジポイント。ここを自動生成するのは、採用面接の質問をAIに任せるのと同じ」。

僕も最初は/initで生成したCLAUDE.mdを使っていました。でも中身を見てください。「良いコードを書いてください」みたいな一般論。冗長な言い回し。

**あなた固有の知識がゼロ。** これで出力が良くなるわけがない。

僕が調べた限り、**よくある失敗とその結果**はこうなっています。

- 冗長な表現の繰り返し → 処理速度が2倍に遅くなる
- 不要な例外処理を50パターン列挙 → ふつうの質問に答えられなくなる
- 「あなたはAIアシスタントです」で300字消費 → AIは自分が何者か知ってる
- 具体例を20〜30個並べる → 逆に応用が効かなくなる
- API仕様を3,000字コピペ → 実際に使うのは3エンドポイントだけ
- 出力形式を20行で規定 → 「Markdown形式で」の1行で済む
- 人格設定に500字 → 回答品質がむしろ下がる
/initで出てきたものは「スタート地点」じゃない。**僕に言わせれば、捨てるべき下書き。**

## ▍CLAUDE.mdが「無視される」3つの構造的原因

![](https://pbs.twimg.com/media/HL-Gsa2bEAAq6vC.jpg)

「書いたのに守ってくれない」。僕も最初はClaude Codeのバグだと思っていました。でも違う。仕様なんです。

**★ 原因①: ファイルが長すぎる。** 

Anthropic公式が明言しています。200行を超えると、重要なルールがノイズに埋もれて無視される確率が跳ね上がります。500行超えは論
