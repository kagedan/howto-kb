---
id: "2026-06-10-obsidianstudio9-httpstcofi0surcnqw-01"
title: "@obsidianstudio9: https://t.co/fi0SurcNqw"
url: "https://x.com/obsidianstudio9/status/2064566152270135673"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "LLM", "x"]
date_published: "2026-06-10"
date_collected: "2026-06-11"
summary_by: "auto-x"
query: ""Model Context Protocol" tutorial OR "Claude MCP" integration"
---

https://t.co/fi0SurcNqw


--- Article ---
Claude×ObsidianにN8Nを取り込むのは完全に盲点だった。これを知らずに使ってる人、かなり損します。実は海外ではいま、Vault が事業を運転する時代に入っています。@cyrilXBT が公開した Obsidian × Claude × N8N の3層業務OSは、これまでの常識を覆します。コピペで動かせる手順を全部書きます。

## **こんな悩み、ありませんか？**

- 案件の状況を更新するだけで午前中が終わる
- メモは溜まっているのに、必要なときに見つからない
- 朝の客先訪問前、過去のやり取りを掘り返すのに30分
- 月末の経理処理で、月の振り返りができないまま翌月に突入
- リサーチして読んで満足、書く前に力尽きる
知識労働者は1日のうち平均で4〜6時間を「事業を進める仕事」ではなく「事業を後退させない仕事」に取られていると言われます。日本の年間労働時間は1,611時間ですが、そのうち事務調整・状況更新・情報探索に消えている割合は、感覚としても無視できない大きさです。

そして日本の時間あたり生産性はOECD加盟38カ国中32位、時間あたり5,543円。海外平均との差は3倍以上。この差は能力ではなく、**業務の組み立て方の差**だと、海外の自動化実装者は口を揃えて言っています。

Karpathy は2025年にこう書いています。

*The problem isn't a lack of information — it's that raw information doesn't scale.*

*（情報が足りないのではない。生のままの情報がスケールしない、それが問題だ）*

![](https://pbs.twimg.com/media/HJn5awIakAAkUeB.jpg)

cyrilXBT の長文は、そのスケール問題を「Obsidian × Claude × N8N の3層」で解く実装手順そのものです。元記事はこちら 👉 [https://x.com/cyrilXBT/status/2054379666316693719](https://x.com/cyrilXBT/status/2054379666316693719)

今回はこの内容を、日本のソロ事業主・1人会社・少人数チーム向けに翻訳ではなく**再構成**します。同じ素材を、日本の朝の風景と日本の業務フローに溶かす形で。徹底的に噛み砕いて日本語で解説していきます👇

## **1. ナレッジ管理が「業務代行」に進化した転換点 — Karpathy から cyrilXBT へ**

Obsidian × AI の本流は、2025年に静かに2段ジャンプしました。

**第1ジャンプは Karpathy の「LLM as compiler & librarian」**。Karpathy は raw articles / papers / notes を「ソースコード」、LLM を「コンパイラ」、生成されるwiki を「実行可能ファイル」と見立てました。Obsidian は単なるメモ帳ではなく、AI が読んで再構成する素材庫になる、という発想の転換です。

ここで重要なのは「ライブラリアン」のほうです。Karpathy はこう続けます。

*Instead of using traditional RAG systems, the LLM acts as a full-time research librarian — actively compiling, linting, and interlinking Markdown files.*

LLM が司書として常駐し、Vault のメモを能動的に編成し、矛盾を検出し、リンクを張り直す。これがあると Vault は「使うほど精度が上がる」状態に入ります。

**第2ジャンプが cyrilXBT の業務OS化**。Karpathy が静的な3層（raw / wiki / reports）を示したのに対し、cyrilXBT は実行レイヤーまで降ろしました。

具体的には、Obsidian の上に N8N の自動化レイヤーと、Claude Code の MCP 接続を重ねて、「メモが溜まる」から「タスクが進む」に変質させた。Obsidian は素材庫から**業務OS の OS 部分**になったわけです。

Greg Isenberg（Late Checkout 創業者、フォロワー約50万）はこの構造をひと言でまとめています。

*how to use obsidian + claude code to bu
