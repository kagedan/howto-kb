---
id: "2026-04-09-claude公式のユースケース集を読むと分かるai活用の本体はプロンプトではなく最小ハーネスだhir-01"
title: "Claude公式のユースケース集を読むと分かる、AI活用の本体は「プロンプト」ではなく「最小ハーネス」だ｜hirokaji"
url: "https://note.com/tasty_dunlin998/n/n4c7956a61d6e"
source: "note"
category: "cowork"
tags: ["cowork", "note"]
date_published: "2026-04-09"
date_collected: "2026-04-09"
summary_by: "auto-rss"
query: ""
---

## Connectors・Projects・Skills・Coworkの事例を、4回路＋証跡基盤で読み解く

## はじめに

Claude や Claude Cowork を見ていると、つい「何ができるのか」に意識が向きます。  
しかし、実務で本当に効く問いはそこではありません。

問うべきなのは、**どの仕事に、どの接続面を使い、どんな文脈を渡し、何を成果物として固定し、どこで人間が承認するか**です。

いまの Claude 公式の use cases ページは、そのことをかなり露骨に示しています。ページは単なる業種別一覧ではなく、**Category** だけでなく **Features** や **Product** でも絞り込める構造になっており、整理軸が「職種」だけでなく「どの実行面を使うか」に寄っています。  
ここで前面に出ているのは、Connectors、Extended Thinking、Projects、Skills、Cowork、Claude in Chrome といった“機能名”です。  
つまり、見せたい本体が「賢い返答」ではなく、**仕事の配線面**に移ってきているのです。

  

---

## 事例集に見えて、実際は「仕事の設計書」になっている

![](https://assets.st-note.com/img/1775037150-pKaIP7H1wuZWBhfJANmyzMgt.png?width=1200)

ユースケースは、質問例ではなく、  
入力・文脈・成果物を束ねた仕事パッケージとして設計されている。

このページ群をよく見ると、ほとんどのユースケースが似た骨格で作られています。  
「Describe the task」「Give Claude context」「Required context」「What Claude creates」という流れです。  
これは単なるプロンプト集ではありません。**仕事の依頼文、必要な材料、実行条件、期待成果物**を一つの単位に束ねた、ミニ設計書です。  
営業提案資料の例でも、単に“提案書を作って”と頼むのではなく、Google Drive 上の discovery notes や RFP、競合分析、ロゴまで文脈として渡し、そのうえで完成物として deck を作らせています。

ここが大事です。  
AI導入が止まる現場では、モデル性能より前に「何を渡せばよいか」「どこまでやらせればよいか」「何が完成なのか」が曖昧です。  
Claude の公式ページがやっているのは、その曖昧さを減らすことです。  
タスクを一段抽象化してから、**その仕事に必要な入力と出力を先に固定する**。  
この考え方は、そのまま実務の再現性につながります。

---

## 見るべきはカテゴリではない。接続面である

![](https://assets.st-note.com/img/1775037191-JFDnEK3jVl4MP17ZH5GUhLu0.png?width=1200)

AI活用の差は、モデルの賢さだけでなく、どの接続面に仕事を載せるかで決まる。

このページを本気で読むなら、Personal や Sales というカテゴリ名だけを眺めてもあまり意味がありません。  
見るべきなのは、「Claude がどこに触っているか」です。

たとえば daily briefing の例では、Cowork が Claude Desktop 上の workspace として説明され、Slack や Notion などの **connectors** と、ブラウザの情報を読む **Claude in Chrome** を束ねて扱います。しかも説明文の中で、これらを **parallel** に問い合わせ、sidebar に plan を作ってから実行する流れまで示されています。  
これは、単発のチャットではなく、**複数ソースを束ねて仕事を回すための制御面**が、もう製品の前面に出てきているということです。

一方で、Google Drive 整理、Salesforce への営業ログ記録、分析ダッシュボードからの指標抽出のような仕事は、Claude in Chrome と Browser Use が前に出ています。  
いずれも既存のブラウザセッションを使い、Drive のフォルダ構成を提案したり、カレンダーと Salesforce をまたいで activity log を下書きしたり、Amplitude や Mixpanel から数値を拾って週次サマリに整えたりする構成です。  
ここで重要なのは、**API を組まなくても GUI 上の仕事を読める**ことではなく、AI が “読む面” と “触る面” を獲得し始めていることです。

---

## 4回路＋証跡基盤で読むと、このページの意味が変わる
