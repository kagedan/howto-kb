---
id: "2026-07-16-intro-to-agent-skillsはじめに-01"
title: "Intro to Agent Skills｜はじめに"
url: "https://note.com/konitan_ai/n/nb58efdfb56df"
source: "note"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "AI-agent", "note"]
date_published: "2026-07-16"
date_collected: "2026-07-16"
summary_by: "auto-rss"
query: ""
---

本編（全6レッスン）は、有料マガジン「Claude検定：Intro to Agent Skills」にまとまっています（¥980）。Claude Codeのskillを自分で作り、鍛え、配れるようになる実践コースで、Anthropic公式の修了クイズ「Claude検定」対策にもなります。

このコースは、Anthropic（アンソロピック）の公式コース「Introduction to Agent Skills」を、英語の原典を読まなくても学べるよう日本語で書き直した教材です。

## このコースで学べること

skillは、Claude Codeに同じ指示を何度も説明しなくて済むようにする仕組みです。一度教えておけば、関連する依頼のときにClaudeが自動で読み込んで適用します。このコースでは、そのskillを自分で作り、確実に発動するよう鍛え、チームや組織に配るところまでを扱います。

skillの正体と発動のしくみ、最初のskillの作り方と名前衝突の優先順位、descriptionの型やallowed-tools・progressive disclosureといった設定、skills・[CLAUDE.md](http://CLAUDE.md)・subagents・hooks・MCPの使い分け、3つの配布路、そして症状別のトラブルシューティングまでを通します。

学び終えると、次のことができるようになります。

* SKILL.mdとdescriptionで、依頼に合致したときだけ発動するskillを作れる
* allowed-toolsとprogressive disclosureで、大きなskillを安全かつ軽く設計できる
* skills・[CLAUDE.md](http://CLAUDE.md)・subagents・hooks・MCPから、用途に合う道具を選べる
* リポジトリ・プラグイン・enterprise管理設定の3つの配布路を使い分けられる
* 「発動しない」「読み込まれない」などの不具合を、症状から診断して直せる

## こんな人に向いています

* Claude Codeで同じ指示を繰り返していて、それを一度で済ませたい人
* チームの規約やレビュー基準を、全員に自動で行き渡らせたい人
* CLAUDE.mdやsubagentsに触れ、次はskillでカスタマイズを深めたい人

Claude Codeを使ったことがあり、CLAUDE.mdやsubagentsの考え方に触れていると、すんなり入れます。

## 腕試し

次の5つに、自分の言葉で答えてみてください。

1. 同じ指示を何度もClaudeに説明しています。これを一度で済ませる仕組みは何ですか？
2. skillが発動するかどうかを決めるのは、SKILL.mdのどのフィールドですか？
3. skillをたくさん持っても、context windowが太りにくいのはなぜですか？
4. 「常時適用」[はCLAUDE.md](http://xn--CLAUDE-he4e.md)、「依頼で発動」はskills。では「イベントで発火」「委任」「外部接続」はそれぞれ何ですか？
5. カスタムsubagentに特定のskillを持たせるには、どうしますか？

詰まらずに答えられるなら、skillをかなり深く理解しています。どこかで言葉に詰まるなら、その部分がこのコースで埋まります。

## 目次（全6レッスン）

1. skillとは何か（同じ説明を繰り返さない仕組み）
2. 最初のskillを作る（舞台裏と優先順位）
3. 設定と複数ファイル構成（大きなskillの分け方）
4. skills と他の道具（5つの道具の使い分け）
5. skillを共有する（3つの配布路と、subagentの注意点）
6. トラブルシューティング（症状別チェックリスト）

各レッスンは、本文・演習・まとめ・英語のまま覚える用語・確認クイズ（英語＋日本語訳）で構成しています。

## Claude検定について

このコースの原典は、Anthropic公式の学習コース「Introduction to Agent Skills」です。原典には修了クイズがあって、合格すると公式の修了証（Certificate of Completion）がもらえます。本シリーズでは、この修了クイズを「Claude検定」と呼んでいます。

本コースは、その英語のクイズに日本語で備えて合格するための教材です。確認クイズを英語でも出しているのは、本番の英語に慣れてもらうためです。本番を目標に学ぶと、力がしっかり身につきます。

修了証には検証用のURLが付いていて、期限はありません。SNSに載せたり、職務経歴書のスキルや学習歴として書いたりもできます。取ったぶんを並べる楽しみもあります。

登録から受験・合格までの手順と、シリーズ全体の地図は、Claude検定対策マップ（ <https://note.com/konitan_ai/n/nd267433454ab> ）にまとめています。合格したら、修了証に「#Claude修了証」を付けて報告してもらえると、次に挑戦する人の励みになります。

## 本編へ

本編（レッスン1〜6）は、有料マガジン「Claude検定：Intro to Agent Skills」にまとめています。

<https://note.com/konitan_ai/m/m83a46a10083d>

---

本シリーズはAnthropic非公式の独自教材です。2026年7月時点の公式コース構成に基づいています。

[#生成AI](https://note.com/hashtag/%E7%94%9F%E6%88%90AI) [#Claude](https://note.com/hashtag/Claude) [#ClaudeAI](https://note.com/hashtag/ClaudeAI) [#Anthropic](https://note.com/hashtag/Anthropic) [#AIエージェント](https://note.com/hashtag/AI%E3%82%A8%E3%83%BC%E3%82%B8%E3%82%A7%E3%83%B3%E3%83%88) [#Claude検定対策](https://note.com/hashtag/Claude%E6%A4%9C%E5%AE%9A%E5%AF%BE%E7%AD%96) [#基礎から独学で身につけるAIの教科書](https://note.com/hashtag/%E5%9F%BA%E7%A4%8E%E3%81%8B%E3%82%89%E7%8B%AC%E5%AD%A6%E3%81%A7%E8%BA%AB%E3%81%AB%E3%81%A4%E3%81%91%E3%82%8BAI%E3%81%AE%E6%95%99%E7%A7%91%E6%9B%B8)
