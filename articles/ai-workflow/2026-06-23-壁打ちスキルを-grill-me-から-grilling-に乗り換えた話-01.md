---
id: "2026-06-23-壁打ちスキルを-grill-me-から-grilling-に乗り換えた話-01"
title: "壁打ちスキルを grill-me から grilling に乗り換えた話"
url: "https://zenn.dev/kjmboy/articles/3d4960a3ffbbf3"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-06-23"
date_collected: "2026-06-24"
summary_by: "auto-rss"
query: ""
---

設計や計画を Claude に壁打ちさせるスキルとして、長らく grill-me を使っていた。やることは単純で、いろんな角度から超しつこく質問をしてくれる。

このスキルの魅力は自分では見つけられなかった考慮漏れを発見する機械を与えてくれることだ。

この grill-me がアップデートされた **grilling** が公開されていたので紹介する。

## grill-me のつらみ

一言で言うと、**「質問を一撃で大量に投げてくる」** に尽きる。

一撃、がポイントで。それによって以下のような現象が起きる。

* 回答によっては他の質問の前提が変わる
* 多すぎて無量空処（思考停止）になる

複数ある質問の関連性を人間が推論しないといけない。しかもその質問はこちらの考慮が漏れた観点を多分に含んでいる。

## 一問一答になった

![](https://static.zenn.studio/user-upload/0270e5a9fa67-20260623.png)

ひとつずつ質問することを要求するプロンプトが追加された。  
前段で触れた部分が改善された。以下のような体験になった。

* 回答に合わせて次の質問を構築してくれる
* ひとつの話題に集中して考えることができる

エージェントの余計な推論も排除されたことで体感ではあるがレスポンスも高速になり最終的な合意形成までのラリーも少なくなった。

## 導入

CLIで作業してる人は以下のコマンドから導入が可能です。  
古い grill-me を使っている方はそちらの削除もお忘れなく。

```
npx skills add https://github.com/mattpocock/skills --skill grilling
```

GUIで作業している方も以下のリンクをエージェントに渡せば問題なく導入可能だと思います。

<https://www.skills.sh/mattpocock/skills/grilling>

## 関連

<https://zenn.dev/kjmboy/articles/a2ab823195a4c6>
