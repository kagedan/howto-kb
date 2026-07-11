---
id: "2026-07-12-claudemicrosoft-learn-mcpで試験問題集を作ってみた-01"
title: "【Claude】Microsoft Learn MCPで試験問題集を作ってみた"
url: "https://note.com/kyosukesakaki/n/nc3866b864d21"
source: "note"
category: "ai-workflow"
tags: ["MCP", "API", "Python", "note"]
date_published: "2026-07-12"
date_collected: "2026-07-12"
summary_by: "auto-rss"
query: ""
---

こんにちは。榊です。

そう感じたこと、ありませんか？

僕もそうでした。

特に出たばかりのMicrosoft資格は、練習問題の数も質も安定していなくて、勉強の取っかかりに困るんですよね。

そこで、そのモヤモヤをMCPで解消してみました。

この記事で最新の問題集が自分で作成できるばかりか、質の悪い問題集に引っかかることもないでしょう。

今回はその話を書きます。ぜひご一読ください。

## なぜ問題集を自分で作ろうと思ったのか

![](https://assets.st-note.com/img/1783802155-qH6ShnGRDOUmL7WgaYBuZ2Kf.jpg?width=1200)

僕はこれから、MicrosoftのABシリーズ資格に挑戦しようと思っています。

今回題材にしたのはAB-410（Intelligent Applications Builder Associate）です。

このABシリーズって今ちょうどPL系の資格から移行する真っただ中になります。

ざっくり整理するとこんな状況です。

<https://techcommunity.microsoft.com/blog/skills-hub-blog/the-ai-job-boom-continues-build-the-skills-that-move-business-forward/4494139>

見ての通り、どれも登場したばかりの資格です。

AB-410も正式版になりたてで、練習問題の数も少ない上に、質もいいものがありません。

つまり、勉強したいのに、頼れる教材がない。

ネット上のものは出どころが不明なものも多く、正直そのまま使うのは怖いですよね。

**それなら、生成AIで作ってしまえばいいじゃないか。**

とはいえ、生成AIであっても世の中に情報がなければ話になりません。

そう考えて行き着いた答えが、MCPでした。

## そもそもMCPって何なの？

![](https://assets.st-note.com/img/1783802163-yilxGh6KVadrFMU9Qneu5WAD.jpg?width=1200)

MCPとは、Claudeのような生成AIを外部のサービスやデータとつなぐための仕組みを指します。

たとえば、Claudeとチャットしているだけで、GmailやGoogleドライブの操作が可能です。

「あのメール見て」とお願いすれば、Claudeが実際に確認しに行ってくれる。そんな外部連携を実現するのがMCPになります。

故に具体的にプロンプトを書かないと、全然違う行動することもあるんですけどね（苦笑）

今回使うMCPは、そのつなぎ先がMicrosoft Learnという公式ドキュメントになります。

**つまり、Claudeに作成してもらう問題集のソースをMicrosoft Learnにすることで質を担保するというわけです。**

## Microsoft Learn MCPの設定手順

Microsoft LearnはClaudeが直接提供している公式コネクタなので無料で使えます。

まずはClaudeのホーム画面から「カスタマイズ」を開きます（画面はClaude Desktopになります）。

![](https://assets.st-note.com/img/1783715112-awPpRgH6jxl9Zk5VIXELzsJn.png?width=1200)

画面が変わったら、左下の「コネクタ」をクリックします。

![](https://assets.st-note.com/img/1783715158-ezJaxHFCYRSQfMyE7InuVGl1.png?width=1200)

画面左上の「追加」をクリックしましょう。

![](https://assets.st-note.com/img/1783715227-oKZj7kvNCEgOnuRPdbFLehp6.png?width=1200)

「コネクタを参照」をクリックします。

![](https://assets.st-note.com/img/1783715312-TJg5MtpHwm17yvuKjiC3qEWP.png?width=1200)

画面が変わったら、検索欄で「Microsoft Learn」と入力します。

![](https://assets.st-note.com/img/1783715387-LPkE1YJ5KbwnXRy4rfF0xovQ.png?width=1200)

Microsoft Learnが表示されたら、右の＋ボタンをクリックします。

![](https://assets.st-note.com/img/1783715454-M8OWzZ0EKTYPku3IcQ9XSDw6.png?width=1200)

画面が変わって、Microsoft Learnが追加されたら完了です。

![](https://assets.st-note.com/img/1783715503-iIY4f6mzTQXLnENxuOs8lhAZ.png?width=1200)

ちなみに色んなMCPを繋いでおり、研究してます。

具体的にMicrosoft LearnのMCPで何ができるかについては、以下のページをご覧ください。

ざっくりいうと（DeepL翻訳）こんなかんじ。

> Microsoft Learn MCP サーバーは、GitHub Copilot やその他の AI エージェントなどのクライアントが、Microsoft の公式ドキュメントから信頼性が高く最新の情報を直接取得できるようにするものです。これは、ストリーム可能な HTTP を使用するリモート MCP サーバーです。ドキュメントの検索、記事全体の取得、コードサンプルの検索が可能です。  
>   
> Microsoft Learn では、次のような使い方ができます。  
>   
> **クイック検索と参照:**  
> 「マネージド ID を使用して Azure Container App を作成するための Azure CLI コマンドを教えて。Microsoft Learn を検索」  
>   
> **コードの検証とベストプラクティス:**  
> 「.NET 8 のミニマル API で IHttpClientFactory を実装するこの方法は正しいですか？ Microsoft Learn を検索して、ドキュメント全文を取得」  
>   
> **包括的な学習と詳細な掘り下げ:**  
> 「Azure Functions をエンドツーエンドで理解したい。Microsoft Learn を検索して詳細を掘り下げる」  
>   
> **コードサンプルの検索:**  
> 「Azure AI Foundry 評価 SDK を使用して harms eval を実行するための、詳細で実行可能な Python コードサンプルを表示する」

今回は、この「包括的な学習と詳細な掘り下げ」を利用している感じですね。

設定が済んだら、新しいチャットの「検索とツール」からMicrosoft Learnが有効になっているか確認できます。

あとはClaudeが、必要なタイミングで勝手にこのコネクタを使ってくれます。

**ちなみにコネクタ機能を活用するなら、Claudeの有料プラン（Pro以上）がおすすめです。**

無料プランでも使えますが、すぐにトークンが枯渇するので有料プランの方が断然快適です。

## Microsoft Learnを使えば「誰が書いたか問題」が消える

![](https://assets.st-note.com/img/1783802176-yXYrHpNauURsGvcfix3mzBP9.jpg?width=1200)

**Microsoft Learnコネクタを使うと、Microsoftの公式ドキュメントを直接参照しながら問題を生成できます。**

これが本当に大きいんですよね。

先ほど書いた通り、Udemyの問題集は出所が不明なため質にムラがあります。

特に、新しい資格ほどその傾向が強いです。

しかし、公式ドキュメントを土台にできるなら、情報の正確さという最大の不安が消えます。

白状すると、僕はこれまでMCPをほとんど使っていませんでした💦

「便利って言うけど、何がいいの？」くらいの距離感だったんですが今回触ってみてMCPがこんなに素晴らしいものかと痛感しました。

## 実際にやってみた

![](https://assets.st-note.com/img/1783802185-aDz9LqBViGr1KsbOdMkSgtFZ.jpg?width=1200)

実際に使ったプロンプトは下記になります。

> Microsoft learnのMCPを使って、AB-410の予想問題集を作ってください。問題は4択式で正解と丁寧な解説をお願いします。

そして返ってきたのが、この問題です。

> **Q. Dataverseデータモデリング（ドメイン①）** ある企業で、案件情報を管理するテーブルを設計している。「見積金額」列は、明細テーブルの複数レコードの金額を自動的に合計して表示したい。この要件を満たすために設定すべき列の種類は？  
>   
> A. テキスト列（手入力）  
>  B. ロールアップ列（Rollup）  
>  C. 検索列（Lookup）  
>  D. 選択肢列（Choice）  
>   
>  正解：B 解説：ロールアップ列は、関連する複数レコード（子テーブル）の値を集計（合計・平均・最大値など）して自動反映させる列です。手入力にすると更新漏れが発生するため、この用途ではロールアップが適切です。検索列は単一の関連レコードを参照するだけで集計はできません。

いかがでしょうか。解説まで含めて、なかなかしっかりした出来です。

答えまで見せちゃうのはちょっとアレですけどね笑

ただ、これだけシンプルな指示でこの精度の問題が出るのは、MCPが裏でMicrosoft Learnを参照してくれているからでしょう。

**凝ったプロンプトを書き込まなくても、情報源の正しさが土台を支えてくれる。ここにMCPの強さを感じました。**

注意点は、これがあくまで「Microsoft Learnの内容に則った問題」だということで、本番の試験問題そのものではありません。

MCPだけで合格が保証されるわけではないので、公式ドキュメントや学習パスも併用して勉強しましょう。

## まとめ

以上、Microsoft Learn MCPで問題集を作ってみた話でした。

実際に触ってみて「これは使える！」と素直に感じました。

情報が乏しい新しい資格ほど、公式ドキュメントを起点に問題を作れる価値は大きいです。

まだMCPを使ったことがない方は、こういう身近なところから試してみると、その便利さが一気に腹落ちすると思います。

今回の記事がよかったら、ぜひ[フォロー](https://note.com/kyosukesakaki)をSNSシェアをお願いします。

ではでは。
