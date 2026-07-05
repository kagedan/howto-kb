---
id: "2026-07-05-今週のaiニュース総まとめ62975claude-sonnet-5からアリババのclaude-cod-01"
title: "今週のAIニュース総まとめ（6/29〜7/5）Claude Sonnet 5からアリババのClaude Code禁止まで"
url: "https://zenn.dev/siromiya/articles/ai-news-weekly-20260705"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "JavaScript", "zenn"]
date_published: "2026-07-05"
date_collected: "2026-07-06"
summary_by: "auto-rss"
query: ""
---

毎朝7時に「finecalm」というメルマガでAIニュースを3分で要約配信しています。この記事はその1週間分（2026/6/29〜7/5・全35本）から、特に押さえておきたい8本を再構成したものです。全文をそのまま毎朝読みたい方は末尾の登録リンクからどうぞ（無料）。

## 1. Anthropic、低価格で動く中型モデル「Claude Sonnet 5」を公開

Anthropicが中型モデルの新版Claude Sonnet 5を公開し、無料・Pro版の既定モデルに採用した。計画立案やブラウザ・ターミナル操作など自律的なエージェント性能を高め、Opus 4.8に近い性能を低価格で提供するとしている。価格は当初100万トークンあたり入力2ドル・出力10ドルで、8月31日以降は3ドル・15ドルへ上がる。  
出典: [TechCrunch](https://techcrunch.com/2026/06/30/anthropic-launches-claude-sonnet-5-as-a-cheaper-way-to-run-agents/)（2026-07-01）

## 2. 米政府命令で停止した「Fable 5」が復活、Anthropicが対応策を公開

米政府の命令で世界的に停止していたAnthropicの「Claude Fable 5」が復活し、同社が対応策の詳細を公開した。Amazonのセキュリティ部門が指摘した脆弱性を受け、危険な指示で止める安全機構「番犬」の仕組みを強化。有料プランで再開し、米CAISIの研究者は新方式を高く評価したとしている。  
出典: [ITmedia AI＋](https://www.itmedia.co.jp/news/articles/2607/02/news095.html)（2026-07-03）

## 3. アリババが従業員のClaude Code使用を禁止、セキュリティリスクの懸念のため

アリババがClaude Codeを高リスクソフトウェアに指定し、7月10日から従業員による使用を禁止すると報じられた。発端は、プロキシ利用時に中国のユーザーかどうかを密かに判定し送信する隠しコードを研究者が発見したこと。Anthropicのエンジニアは無許可再販や蒸留への対策実験だったと説明し、7月1日のリリースで撤回すると述べている。  
出典: [GIGAZINE](https://gigazine.net/news/20260704-alibaba-bans-claude-code/)（2026-07-05）

## 4. 中国のオープンウェイト「GLM-5.2」、脆弱性検出ベンチでClaude Codeを上回る

Z.aiのオープンウェイトモデルGLM-5.2が、脆弱性検出のベンチマークでClaude Code(Opus系)を7ポイント上回る39%対32%を記録。約7500億パラメータのMoEで、コストは同等モデルの約6分の1、検出1件あたり約0.17ドルに抑えられたと報告された。米中のモデル性能差が縮まっている実例のひとつ。  
出典: [GIGAZINE](https://gigazine.net/news/20260630-glm-5-2-beats-claude-cyber-benchmarks/)（2026-07-01）

## 5. カリフォルニア州がAnthropicと提携、Claudeを州機関・自治体が半額で利用可能に

ニューサム知事が、Anthropicとの提携により州機関や地方自治体がClaudeを50%割引で使えるようになると発表した。あわせて無料研修や開発者による技術支援も提供される。州ではすでに審議型民主主義基盤「Engaged California」や業務ツール「Poppy」でClaudeが活用されている。  
出典: [GIGAZINE](https://gigazine.net/news/20260630-california-anthropic-partnership/)（2026-06-30）

## 6. Cloudflareの新方針、AI企業に出版社コンテンツの対価支払いを促す

Cloudflareは9月15日から、広告掲載ページで用途混在のクローラーを既定でブロックすると発表した。検索用と、エージェント・学習用のクローラーを分離させる狙いで、従量課金のPay Per CrawlはPay Per Useへ拡張。Ceramic.aiとYou.comが初期パートナーとなる。ブログ・note運用者にも関わる話題。  
出典: [TechCrunch](https://techcrunch.com/2026/07/01/cloudflares-new-policy-pushes-ai-companies-to-pay-for-publishers-content/)（2026-07-02）

## 7. フィジカルAIに挑む日の丸連合「Noetra」が始動

ソフトバンクやソニーグループ、NEC、産総研などが出資する新会社「Noetra」が7月1日に事業を開始したと発表された。フィジカルAI・ロボット開発の基盤となる「マシンリーダブル基盤」の構築を目指し、約3800億円規模の出資を計画。産総研やNEDOと連携し、2031年3月までの約5年計画で実世界向けAI基盤を共同開発する。  
出典: [ITmedia AI＋（MONOist）](https://monoist.itmedia.co.jp/mn/articles/2607/04/news016.html)（2026-07-04）

## 8. AIでSafariを自動操作できる「Safari MCP server」が登場

Safari Technology Preview 247のリリースで、AIエージェントにSafariの自動操作を任せられる「Safari MCP server」が利用可能に。MCPはAnthropicが2024年11月に提唱した規格で、AIに各種サービス・データへのアクセス能力を与えるもの。コンソールログ取得やJavaScript実行、スクリーンショット取得などのツールを備え、テストやデバッグの自動化に使える。  
出典: [GIGAZINE](https://gigazine.net/news/20260703-safari-mcp-server/)（2026-07-04）

---

## まとめ

今週は「Claude Sonnet 5の低価格化」「Fable 5の規制解除・復活」「アリババのClaude Code禁止」と、Anthropic関連の値付け・規制・信頼を巡る動きが同時多発した週でした。並行して、GLM-5.2による米中の技術差縮小、Cloudflareの出版社対価問題、日本発のフィジカルAI連合など、AIを取り巻く経済・地政学的な話題も濃い1週間でした。

毎朝7時、こうしたAIニュースを3分で読める形にして無料でメール配信しています。続きが気になる方はこちらからどうぞ。

**→ 毎朝7時にAIニュースが届く無料メルマガ「finecalm」に登録する**  
<https://finecalm.substack.com>
