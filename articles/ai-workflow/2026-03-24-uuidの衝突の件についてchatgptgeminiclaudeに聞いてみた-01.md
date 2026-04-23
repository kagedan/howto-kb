---
id: "2026-03-24-uuidの衝突の件についてchatgptgeminiclaudeに聞いてみた-01"
title: "UUIDの衝突の件についてChatGPT、Gemini、Claudeに聞いてみた"
url: "https://note.com/asobi_spec/n/n85b0c68395d1"
source: "note"
category: "ai-workflow"
tags: ["Gemini", "GPT", "note"]
date_published: "2026-03-24"
date_collected: "2026-03-24"
summary_by: "auto-rss"
---

どうも、かすみ草を枯れた後もなんちゃってドライフラワーとして飾り続けている「遊びの仕様書」です。

2026年3月、「UUIDの衝突についてレビューで指摘されたとき、どうすればいいのか？」という話題がXで注目を集めました。

正直なところ、私自身はUUIDの衝突についてそこまで深く考えたことがなく、また、大規模かつ高い信頼性が求められるシステム開発に携わってきたわけでもないため明確な答えを持っているわけではありません。

ただ、AIに聞いてみる題材としては面白いと思ったので、今回はエンタメとして記事を書くことにしました。

この記事は、UUIDの衝突に関する技術的な指南書ではありません。ちょっと役に立つかもしれないエンタメとして、あるいは各AIの挙動を眺めるための参考程度に読んでいただければと思います。

ChatGPT 5.4 Thinking 拡張モード、Gemini 3.1 Pro、Claude Opus 4.6 に、以下のプロンプトを投げてみようと思います。

> UUIDの衝突についてレビューで指摘を受けたとき、どう答えるべきか？ また、この問題の本質についても、全体で1000文字以内で答えてください。

気になるのは、単に確率や技術論だけでなく、以下の点まで踏み込んで考慮してくれるかどうかです。

- 人間の心理的な問題  
- UUIDの脆弱性

## ChatGPT 5.4 Thinking 拡張モードの答え

![](https://assets.st-note.com/img/1774313691-t2jJeG5wXc8s1RYMAfLyBvpo.png?width=1200)

人間の心理的な問題やUUIDの脆弱性への直接的な言及はありませんが、UUIDを絶対視せず、一意性の最終保証はストレージ制約や再試行などで担保すべき、という立場です。

## Gemini 3.1 Proの答え

![](https://assets.st-note.com/img/1774313717-vWKh81GiFwBlOnCNoQfsbgSt.png?width=1200)

Geminiも一意性の最終保証はストレージ制約や再試行などで担保すべき、という立場でした。加えて、理論上の衝突確率だけでなく、乱数生成器のバグのような実装上の問題にも触れていたのはいいなと思いました。

## Claude Opus 4.6の答え

![](https://assets.st-note.com/img/1774313744-nRdGfLPoV4YCXFgSHKD3IEhx.png?width=1200)

こちらはかなりユニークな答えですね！ChatGPTやGeminiとは違い確率的に無視していいという答えです。  
コミュニケーションの問題という切り口もユニークですね。

ここではどの答えが良かったか、どうすべきかという「答え」は出しませんがもう一つ聞いてきましょう。

> 例えばGoogleやFacebook.、Appleほどの規模のサービスでUUIDの衝突は気にするのかな？500文字以内で答えて

## ChatGPT 5.4 Thinking 拡張モードの答え

![](https://assets.st-note.com/img/1774313798-XYyJmI4v51lkzLBEMOohsCTf.png?width=1200)

ChatGPTは一貫して気にするという立場でした。

## Gemini 3.1 Proの答え

![](https://assets.st-note.com/img/1774313826-7uid4Aarn6IjLYs0Eh9Ct8qM.png?width=1200)

パフォーマンスの観点からそもそもUUIDはあまり使わないという立場です。

## Claude Opus4.6の答え

![](https://assets.st-note.com/img/1774313848-GrJsqupL6UKW0hoOY175fzcM.png?width=1200)

こちらもGeminiと同じくパフォーマンスに言及しています。  
Geminiより一歩踏み込んでいてわかりやすいかなと思いました。

今回は、どの答えが良かったかという優劣はあえてつけませんが、それぞれ立場が微妙に違っていたのが印象的でした。

AI同士ですらこうして意見が分かれるのですから、人間のあいだで意見が割れるのも自然なことなのかもしれません。
