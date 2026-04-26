---
id: "2026-04-25-claudecode-love-httpstcoqze5gqubxt-01"
title: "@ClaudeCode_love: https://t.co/qZe5gqubxt"
url: "https://x.com/ClaudeCode_love/status/2047992961175277791"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "x"]
date_published: "2026-04-25"
date_collected: "2026-04-26"
summary_by: "auto-x"
---

https://t.co/qZe5gqubxt


--- Article ---
Claude Codeの生みの親『Boris Cherny』が「これだけは押さえとけ」って言ってる運用Tipsを30個、今回の記事に自力で全部まとめました。マジで神記事です。

![](https://pbs.twimg.com/media/HGvZYP-aEAApgtR.jpg)

正直、これ知ってるか知らないかでClaude Codeの使い心地が天と地ほど変わります。毎回同じ指示繰り返してたあの時間、手戻りで溶かしてた1時間、全部要らなかったって気づきます。

ところで皆さん普段ClaudeCode使ってて、こんな悩み、ないですか？

![](https://pbs.twimg.com/media/HGvXwoJbIAAz2lF.jpg)

・Claude Code使ってるけど、毎回同じこと指示してる気がする。学習してくれよって思う 
・大きめの変更を任せると手戻りばっかりで、結局自分で直した方が早かったってなる
 ・機能が多すぎて、結局どれから手をつければいいのか分からない
 ・会話が長くなると途中から噛み合わなくなって、「あれ、さっき言ったよね？」ってなる

Claude Codeって、マジで文脈の持たせ方、検証のさせ方、権限の決め方、並列で動かす設計、自動化、このあたりをちゃんと組んで使うと、体感がガラッと変わります。

この記事は、Boris Cherny（Claude Codeを作った人）のX投稿、Anthropicの公式ドキュメント、GitHubの公式リポジトリと公式Action、このあたりを中心に2026年4月23日時点の一次情報を優先してClaudeCodeStudioが独自で調査し、執筆したものです！

![](https://pbs.twimg.com/media/HGvY10UawAATYKw.png)

Borisは「I created Claude Code（Claude Code作ったの俺です）」って明言してるので、彼の運用発言を現場の生の声として重視しつつ、CLIのオプションとか設定の細かいところは公式Docsで裏取りして今回の記事を書きました！😆

絶対にClaudeCode使ってる人なら見てください！！！

保存も必須です！！！！

リアルに生産性１０倍は変わります！ではいきましょう！👇

■ まず押さえてほしい3つの原則

![](https://pbs.twimg.com/media/HGvXzzyasAArZKq.jpg)

Claude Codeを実戦で強くする最大の要因って、突き詰めると本当に3つしかないです。

Plan Modeで「調べる」と「実装する」を分けること。Claudeに自分の仕事を検証させること。そして並列セッションを前提に働くこと。

Borisも「Almost always use Plan mode（ほぼ常にPlan mode使え）」「give Claude a way to verify its output（Claudeに自分の出力を検証する手段を持たせろ）」「3〜5 git worktrees（worktreeを3〜5本並列で）」って繰り返し言ってます。

■ 「唯一の正解はない」という考え方

Borisの投稿をいろいろ読んでいくと、Claude Codeに唯一の正解なんてないけど、めちゃくちゃカスタマイズできる運用ツールとして使え、というスタンスがよく出てきます。彼自身「there is no one right way to use Claude Code（使い方に唯一の正解はない）」と何度も繰り返してる。

その前提の上で、彼が言ってる一番効くワークフローはこんな感じ👇

![](https://pbs.twimg.com/media/HGvX8ezbUAAtu7F.jpg)

Plan Modeで調査・計画 　

↓ 実装セッション 　

↓ テスト・スクリーンショット・CLIで自己検証 　

↓ PR作成 　

↓ Code Review / Ultrareview 　

↓ 学びをCLAUDE.md・Hook・Skillに還元

この流れを頭に入れた状態で、具体的な30個のTipsを見ていきましょう。

■ 30個の運用Tips

現場で効くやつから順に並べてます。BorisのX投稿で方向性が出てるやつはXを主にして、設定とか制約の細かい話は公式DocsとGitHubで補強。研究プレビュー機能はその旨ちゃんと明記してます。

■ Tip 1：大きい変更はまずPlan Modeで分離する

![](https://pbs.twimg.com/media/HG
