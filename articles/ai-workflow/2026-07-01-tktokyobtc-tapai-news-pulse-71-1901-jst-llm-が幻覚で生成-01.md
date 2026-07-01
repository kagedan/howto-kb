---
id: "2026-07-01-tktokyobtc-tapai-news-pulse-71-1901-jst-llm-が幻覚で生成-01"
title: "@tktokyoBTC: TapAI News Pulse （7/1 19:01 JST） LLM が幻覚で生成する「存在しないドメイン」を攻撃"
url: "https://x.com/tktokyoBTC/status/2072260470463971399"
source: "x"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "LLM", "Gemini", "GPT"]
date_published: "2026-07-01"
date_collected: "2026-07-02"
summary_by: "auto-x"
query: "Claude プロンプト 書き方 OR Claude 業務効率化 実例"
---

TapAI News Pulse
（7/1 19:01 JST）

LLM が幻覚で生成する「存在しないドメイン」を攻撃者が先回り取得し、フィッシング拠点に転用する「Phantom Squatting」が報告された。AIの回答の自信がそのまま攻撃面と化す構図であり、朝方の API キー大量漏洩に続き、エージェント時代の防御設計が問い直されている。
今夜はそのほか、複数 LLM を相互評価させる Bloome を François Chollet が称賛、RAG を刷新する context engineering の設計論、モバイル対応した OpenClaw など4件をピックアップ。

- - - - - - - - - - - - - - - - - - - - - - - 

▸ LLMが「存在しないドメイン」を幻覚生成——攻撃者がそのURLを先回り取得してフィッシングに悪用
AIが存在しないウェブアドレスを「ハルシネーション」で生成する挙動を利用した新手法「Phantom Squatting（幻影スクワッティング）」が報告された。攻撃者はLLMが頻繁に作り出す架空ドメインを先回りして取得し、フィッシングサイトやマルウェア配布拠点として運用する。ユーザーがAIの回答に従ってURLを踏んだ瞬間、罠にはまる構造だ。

AIの「回答の自信」がそのまま攻撃面になった、という構図。

https://t.co/l2TASDhF4Y

▸ 自動運転スタートアップWayve、8500万ドルの従業員持株売却——評価額85億ドルで実施
英国の自動運転AIスタートアップWayveが、評価額85億ドルで8500万ドルの従業員向けテンダーオファーを実施すると発表した。テンダーオファーはAIスタートアップが人材の獲得・定着を図るための戦略的手段として急増しており、Wayveもその流れに乗る形だ。同社はIPOを視野に入れながら非公開のまま成長を続けている。

IPO前の「流動性供給」が優秀人材の引き留め策になっている構図は、業界全体で定着しつつある。

https://t.co/CgvJ5C3TgH

▸ François Chollet、クロスエージェントフィードバックループを称賛——Bloomeが複数LLMを相互評価させる仕組みを公開
Keras作者でAI研究者のFrançois Cholletが、複数AIエージェントが互いにフィードバックを与え合う仕組みに高い効果があると言及し、スタートアップBloomeが開発中のプラットフォームを紹介した。BloomeはClaude・ChatGPT・Geminiなどを同一ワークフロー内に統合し、相互評価・改善ループを実現するツールだ。

Cholletが名指しで推す、というシグナルの重さ。

https://t.co/lS4oq0P07P

▸ コンテキストエンジニアリングがRAGを刷新——4種の入力タイプでLLMの回答精度を高める設計論
Andrej KarpathyやShopify CEOのトビアス・リュッケが提唱した「コンテキストエンジニアリング」の考え方がRAG（検索拡張生成）設計に応用されている。従来の「一塊のテキストを渡す」方式から脱し、取得情報・指示・例示・作業記憶の4種類に入力を分類して構造化することで、LLMの回答精度が向上するという。開発者だけでなく、AIツールをカスタマイズして使う人にも関係する考え方だ。

「プロンプトの書き方」という発想が「コンテキストの設計」へ格上げされている。

https://t.co/tUvVoeF0Af

▸ OpenClaw、AndroidとiOSに正式対応——オープンソースのAIエージェントがスマホで動作
オープンソースのAIエージェントプログラム「OpenClaw」がAndroidとiOSに正式対応した。無料で利用でき、スマートフォン上でエージェント的なタスクを自律実行できる。これまでPCが前提だったオープンソースエージェントがモバイルに広がることで、一般ユーザーの導入ハードルが大きく下がる。

オープンソースエージェントがポケットに入った、という転換点。

https://t.co/PvXXts0n8H

- - - - - - - - - - - - - - - - - - - - - - - 

過去アーカイブは: https://t.co/GZ1yDgBJhb

#AI #海外ニュース


--- 引用元 @fchollet ---
Cross-agent feedback loops are incredibly effective -- for a reason. Check out what @leon2mcp and team at @B
