---
id: "2026-05-29-claudeとfreee-mcpを接続メールから見積作成salesforce商談作成を自動化-01"
title: "Claudeとfreee MCPを接続！メールから見積作成、Salesforce商談作成を自動化"
url: "https://note.com/nueshima/n/n64069bd6050c"
source: "note"
category: "ai-workflow"
tags: ["MCP", "note"]
date_published: "2026-05-29"
date_collected: "2026-05-29"
summary_by: "auto-rss"
query: ""
---

![](https://assets.st-note.com/img/1779949241-Ndl8cH7kPJegUm25R6bVGCYv.png?width=1200)

今回は、Claudeをfreeeと接続し、SalesforceやGmailと連携させた業務自動化の検証を行いました。  
  
見積依頼メールから見積書作成、商談受注から請求作成までの作業をClaudeが大幅に削減してくれるのでそのシナリオをご紹介いたします。

  

### 環境構築

freeeMCPとClaudeの接続。

freeeの開発用環境を取得します。mcpのコネクターとその接続手順はfreeeのヘルプページに詳しく掲載されており、その手順に沿って設定するとわずか1時間程度で完了します。

<https://support.freee.co.jp/hc/ja/articles/56390747520537-freee-mcp-%E3%83%AA%E3%83%A2%E3%83%BC%E3%83%88%E7%89%88-%E3%82%92%E8%A8%AD%E5%AE%9A%E3%81%97%E3%81%A6%E5%88%A9%E7%94%A8%E3%81%99%E3%82%8B>

コネクターに追加されました。

![](https://assets.st-note.com/img/1779949721-U65P12TCKpL74RrduJWMwhOf.png?width=1200)

では接続できるかテストしてみます。次の指示をします。

> freeeに接続して取引先一覧を表示して。

freeeに登録されているテスト用の取引先が表示されました。成功しているようです。

![](https://assets.st-note.com/img/1779951034-zZfAcVkQ7pJg6wr0UXHly9Mb.png?width=1200)

コネクターの設定はメチャクチャ簡単です。こんな簡単な作業で業務が自動化できるとは、大変おどろきですね。

---

### ユースケース１：メール受信→freee見積作成→メール返信

前の投稿でメールからSalesforceの商談を自動作成する流れを検証しましたが、今度はメールからfreeeの見積り作成を実行してみたいと思います。

前の投稿

まずこのようなサンプルメールを作成し、自分宛に送信します。

> 上嶌様  
> いつも大変お世話になっております。  
> 株式会社テクノソリューションズ の吉井です。  
> 本日はお時間をいただきありがとうございました。  
> 募集要項を本文末にて共有させていただきます。  
> 募集要項をご確認いただき要員スキルシートのご提案をお願いします。  
> ---以下募集要項---  
> 案件募集要項①（SE：開発要員１名）  
> 【商流】  
> エンド→弊社→貴社  
> ※ 再々委託は不可、貴社プロパーのみ  
> 【作業概要】  
> 運用中Salesforce環境における追加開発・改修対応の実施  
> 【作業内容】  
> Salesforce保守・新規Salesforce環境構築、  
> Salesforce外部連携などの機能追加・改善プロジェクトにおいて、  
> 基本設計～テストまでを一貫して一人称で担当いただく  
> 【期間】  
> 2026年7月～9月（ただし最長1年の延長の可能性あり）  
> 【スキル】  
> <必須>  
> ・SalesforceプロジェクトでのSE経験  
> ・Apex/Visualforce/LWCの知見  
> ・積極的にコミュニケーションが取れる方  
> ・未経験の作業(技術)に消極的にならない方  
> <尚可>  
> ・Salesforce外部連携の対応実績  
> ・Apex/Visualforce/LWCの実績  
> ・Salesforce関連資格  
> ・お客様技術部門の方/他システムベンダーと技術的な会話が出来る方  
> ※ 国籍問わず(日本語レベル:ビジネスレベル、日本在住に限る）  
> 【契約形態】  
> SESor派遣  
> 勤務時間は、9:00～18:00（SESの場合、月あたりの基準時間は160時間）  
> フルリモート想定（エンドは、東京）  
> ※ 弊社東京オフィスに週2程度で出社できるメンバーであればより良い  
> 【金額】  
> 1200000  
> 【ご回答期限】  
> 2026/6/10

![](https://assets.st-note.com/img/1779953490-5cG2rxFfon3saKEMitvjk0Ny.png?width=1200)

サンプルメールがGmailの受信boxに来たのでClaudeに指示をします。

> 本日、受信したメールからfreeeで見積書を作成してください。

Claudeが動きだし、まず本日受信したメールの中から見積に関連しそうなメールを探します。メールを確認したあと、freee側で取引先が存在するか確認しています。

![](https://assets.st-note.com/img/1779954066-lBYHjsqy1UKmzkAcf8edVIJZ.png?width=1200)

見積書作成完了と結果が返ってきたので、freeeにログインし確認します。

![](https://assets.st-note.com/img/1779954177-QNqOKsDV8YfFWUxLR6A019bz.png?width=1200)

取引先と納期も正しく入力されていて、PDFも生成されています。本当にすごい！

![](https://assets.st-note.com/img/1779954313-9leWXzEvoM6bF0aDwBROq4Ii.png?width=1200)

指示していませんでしたが、明細も月別に分割されて作成されています。  
Claudeなんと賢いことか！！

![](https://assets.st-note.com/img/1779954404-soNOTDaQifCRgu5H8IehzyvV.png?width=1200)

見積の返事はfreeeのメール送信ボタンから行うと文書も考えてくれて1クリックで送れるのでそこから送信します。下の画像は受信したメール画像です。

![](https://assets.st-note.com/img/1779954607-29tFAdpabKjzguVXHGmMPfyS.png?width=1200)

ここまで私がPCに入力したのはClaudeへの指示とfreeeからの見積もり送信ボタンのクリックのみです。それだけで見積作成と見積送信作業が完了しています！

---

### ユースケース２：メール受信→freee見積作成→Salesforce商談作成

今度は、同じメールからSalesforceの商談も一緒に作成し、メール送信まで一気にできないか確認します。

見積書を区別しやすくするため追加要員の提案に修正してメールを受信します。

![](https://assets.st-note.com/img/1779955308-iMZfV7u6qe8bhTCr0oLUKcHk.png?width=1200)

今度はfreeeだけでなくSalesforceの商談の作成も指示します。一緒に作成してくれと手間がかなり減ります。

> 本日、受信したメールからfreeeで見積書を作成し、Salesforceの商談も作成してください。

まず、メールの確認が行われ、処理する内容がまとめられます。

![](https://assets.st-note.com/img/1779955569-fRqKP5T246vgLhpENwQBkt8b.png?width=1200)

次にfreee見積書とSalesforce商談が同時に作成したと回答あります。

![](https://assets.st-note.com/img/1779955624-wzUfSTLZAmt3sEhBqWcjxpiv.png?width=1200)

freeeを確認します。見積書は作成されています。

![](https://assets.st-note.com/img/1779955709-EipJZscfqtdyuQ8S1b2DKx5F.png?width=1200)

Salesforceの商談も作成されていました。

![](https://assets.st-note.com/img/1779955882-U2PjgTrhYK6e3s1m7wcMHCFf.png?width=1200)

凄くないですか？  
Gmail受信 → freee見積書作成 → Salesforce商談登録 の3システム連携を1回の指示で完結しています。

人材派遣・SES業では日常的に発生するこのフローを自動化することで営業担当者の入力工数を大幅に削減できます。

---

### ユースケース３：Salesforce商談受注→freee請求書作成

最後にもう一度Salesforceとfreeeの更新が1つのプロンプトでできるか試してみます。

> 次の商談を受注にして、freeeで6月末分の請求書を作成してください 「Salesforce開発要員 ご提案（SES）追加 」

あまりにも簡単にできます。入力していたら10分程度かかる作業が数秒で完了です。

![](https://assets.st-note.com/img/1779956679-65qKBw7I0DbJOHAZy3nN4kj9.png?width=1200)

Salesforceの画面

![](https://assets.st-note.com/img/1779956755-bvhDxNg2TcEiqk8WlYj07nK6.png?width=1200)

freeeの画面

![](https://assets.st-note.com/img/1779956818-6jf3L8ukYUEG2AyiKmlRdHot.png?width=1200)

指示どおり6月分のみの請求になっていました。

![](https://assets.st-note.com/img/1779956852-NJRLHVmTMtguq8v6ChSF0aP7.png?width=1200)

今回のシナリオは以上になります。

---

### わかったこと

今回の一連のフローをまとめると、**メール受信 → 見積書作成 → 商談登録 → 受注更新 → 請求書発行**まで、Claude経由で完結できました。

> **Claudeにできること**●メール文書からfreeeへ見積書、請求書作成、Salesforceへの商談登録  
> ●取引先の有無判定とない場合は作成  
> ●見積作成時の明細登録、請求作成時の請求日付の考慮 SES・人材派遣業の営業〜請求サイクルをほぼノーコードで自動化できる実用的なデモになったと思います。

本日わかったことは、MCPサーバーの大きな効果が生まれる場面が2つありました。

> ●SaaS間でのデータ連携がある時  
> ●同じタイミングで複数のSaaSにデータ登録する時

このような場面があるとMCPでは大きなメリットを生むことがわかりました。

「SaaSが十分使えてない」「AIの効果を感じられない」など相談がありましたら、是非ご連絡ください。DMお待ちしています。

---

過去の記事
