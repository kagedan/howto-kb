---
id: "2026-05-22-claude-for-legal-を触ってみました-契約大臣と連携して契約レビューを自動化-01"
title: "Claude for Legal を触ってみました ~契約大臣と連携して契約レビューを自動化~"
url: "https://zenn.dev/teradox_blog/articles/e25178b03748f5"
source: "zenn"
category: "cowork"
tags: ["MCP", "cowork", "zenn"]
date_published: "2026-05-22"
date_collected: "2026-05-23"
summary_by: "auto-rss"
query: ""
---

## はじめに

2026年5月12日にAnthropic社から発表された「**Claude for Legal**」を動かしてみました。  
[（Anthropic社公式ブログ）](https://claude.com/blog/claude-for-the-legal-industry)

**Claude for Legal**とは、ざっくり「Claudeを法律業務に特化させて使えるようにする仕組み一式」です。  
主に法務系SaaSとつなぐ20種類以上のMCPコネクタと、業務領域ごとに用意された12種類のプラグインなどがリリースされました。

このプラグインは、弊社が提供する電子契約サービス「[契約大臣](https://keiyaku-daijin.com/)」と親和性が高いのではないかと思っています。

さっそくClaude Cowork上で動作させてみました。  
契約大臣には[リモートMCPサーバー](https://keiyaku-daijin.com/content/mcp)があるので、コネクタとしてClaude Coworkに接続することができます！  
契約大臣のMCPサーバーは、契約書情報の取得や契約書の送信が可能です。

今回試してみたいことは、**契約大臣で作成している契約書のレビューから、契約書送信までの自動化**です。

まずは動かしてみることが目的のため、細かい設定や解説は省略しております。  
また、今回はダミーの契約書を利用するためレビュー結果の良し悪しについては触れません。  
あらかじめご了承ください。

## 注意点

プラグインの公式リポジトリのREADMEに下記のような注意書きがありました。

> Every output from these plugins is a draft for attorney review — not legal advice, not a legal conclusion, not a substitute for a lawyer. They are built with guardrails that reflect that: source attribution on every citation, conservative defaults on privilege and subjective legal calls, jurisdiction assumptions surfaced, and explicit gates before anything is filed, sent, or relied on. A lawyer reviews, verifies, and takes professional responsibility for anything that leaves the building. These plugins make that review faster; they do not replace it.

*[出典: anthropics/claude-for-legal](https://github.com/anthropics/claude-for-legal)*

* AIが出力するものはすべて「弁護士がチェックする前の下書き」である。
* AIは「弁護士のレビューを速くする」ためのツールであり、「弁護士を不要にする」ツールではない。

主にこのような内容が記載されており、あくまでこのプラグインは弁護士の業務を軽減するためのものとして提供されているようです。

AIの出力結果に対する判断を含め、最終的な責任は人間が負うことを前提として利用する必要があります。  
本記事も、AIのレビューだけで契約業務を完結させることを推奨するものではありません。

また、法務実務で生成AIを活用する際には、機密情報や個人情報の取り扱いには十分注意してください。

## プラグインについて

12の法律分野ごとに、すぐ使えるプラグインが用意されています。  
下記はその中の一部ですが、様々な分野に特化されているのがわかります。

* **Commercial Legal (商取引・契約)**  
  契約書(NDA、ベンダー契約、SaaS契約など)のレビュー、更新日の管理
* **Corporate Legal (会社法務・M&A)**  
  M&Aの資料調査、取締役会の議事録、グループ会社の法令遵守チェック
* **Privacy Legal (プライバシー・個人情報保護)**  
  個人情報の取扱い判定、プライバシー影響評価、本人からの開示請求(DSAR)対応
* **Employment Legal (人事労務)**  
  退職書類のレビュー、雇用区分の判定、労働時間のQ&A、社内調査のサポート

今回は契約レビューに使える [**Commercial Legal**](https://github.com/anthropics/claude-for-legal/tree/main/commercial-legal)を入れてみました！  
こちらは自社のルールに照らして契約書をレビューしてくれる機能が入っているようです。

## インストールと準備

まずはClaude CoworkのCustomizeからマーケットプレイスを追加します。  
![](https://static.zenn.studio/user-upload/88bfa872c4c2-20260522.png)

**マーケットプレイス**は「プラグインのカタログ」のようなものです。  
このマーケットプレイスを登録すると今回リリースされた12種類のプラグインが個人用という部分に表示されます。

その中から**Commercial Legal**をインストールします。  
![](https://static.zenn.studio/user-upload/f3a2a2f8b8d7-20260522.png)

**プラグイン**とは「機能のまとめ」です。  
インストールすると下記のようなものが利用できる状態になります。

* スキル(できること)
* エージェント(自動的に動く仕組み)
* コネクタ(つながる外部ツール)

![](https://static.zenn.studio/user-upload/daf84462afa7-20260522.png)

マーケットプレイスの中にプラグインがあり、プラグインの中にスキル・エージェント・コネクタが入っている、という入れ子の関係です。  
このあたりの詳しい説明は省略しますが、今回使ってみたい**契約書レビューはスキルに該当**します。

プラグインのインストールが完了したら、まず初期設定を行います。

「自社のルールに照らして契約書をレビュー」を実現するために、まずはここでどういったレビューを希望するかをAIに伝えておく必要があります。

初期設定は以下のコマンド(スキル)を入力して実行します。

![](https://static.zenn.studio/user-upload/18b15dcc6b13-20260522.png)

最初は英語で表示されたので、追加で「日本語でお願いします。」と依頼しました。  
すると以下のような選択肢が表示されました。

![](https://static.zenn.studio/user-upload/d204bcde2658-20260522.png)

とりあえず今回は「クイック」を選択。

![](https://static.zenn.studio/user-upload/9f5b6d7f9fbf-20260522.png)

ウィザード形式で方針・承認ルールなどを回答していきます。  
クイックの場合は上図のような4問でした。

より自社のやり方に合わせてレビューを依頼したいときはフルを選択すると良いでしょう。  
今回はこの設定内容については割愛します。

設定が完了したらどういったことができるか質問してみました。

![](https://static.zenn.studio/user-upload/480fd815daad-20260522.png)

組み込まれているスキルについて説明してくれました。  
その中でもNDA(秘密保持契約)についてのレビューはGREEN / YELLOW / REDで仕分けしてくれるような機能があるので、今回はこれを試してみようと思います。

`nda-review`スキルは、内部的には`review`スキルを実行し、その結果を元に3段階の判定をしてくれるようです。

## 契約大臣のMCPと連携させてみた

ここからが本題です。

`nda-review`のレビューを想定し、契約大臣にレビュー対象の秘密保持契約書を4件準備しました。  
![](https://static.zenn.studio/user-upload/3c91e627d458-20260522.png)

**今回は次のプロンプトを投げてみようと思います**

```
契約大臣で今日作成した「下書き」状態の契約を全てレビューしてください。

GREEN判定のものは送信してください。
署名タイプは電子サイン、送信方法はEメール、
送付先はGoogleドライブ内のスプレッドシート「送付先一覧」に記載されている情報を元に設定してください。

RED判定の場合は該当の部分を修正した改訂版契約書を作成し契約大臣で下書きしてください。 
その場合に管理用タイトルには(改訂版)を追記し、 グループは「管理部」でお願いします。  

送信完了したものはSlackのkeiyaku-daijinチャンネルに通知。
改訂版は変更点とそれについての説明をMDファイルにまとめてください。 
レビューにはskillを使用してください。

今から2分後に実行してほしい。
```

せっかくなので契約書レビューだけでなく、業務自動化という観点でも活かせるようなものにしました。

> Googleドライブ内のスプレッドシート「送付先一覧」に記載されている情報を元に設定

Googleドライブのコネクタを連携させました。契約書1件ずつGUIから送付先を設定する手間を省略することを目的としています。  
スプレッドシートには仮の送付先メールアドレスを記載しておきました。

![](https://static.zenn.studio/user-upload/ea1239821e74-20260522.png)

> 送信完了したものはSlackのkeiyaku-daijinチャンネルに通知

自動化して別の業務を行う想定なので、完了後の通知は必要ですね。

> 今から2分後に実行してほしい。

この部分は実際の業務では「毎日朝10時に実行してほしい。」みたいなことを実現したいです。

必要なMCPサーバーはコネクタとして設定します。

![](https://static.zenn.studio/user-upload/98e6cbde130f-20260522.png)

さて、先ほどのプロンプトを入力するとさっそくスケジュールに設定されました。実行を待ちます！

![](https://static.zenn.studio/user-upload/cd4bc1c986e2-20260522.png)

時間になると実行されました！動作をリアルタイムで追っていきます。

![](https://static.zenn.studio/user-upload/2e157c4c7c67-20260522.png)

開始されるとAIエージェントが達成したいことに向けてタスクを組み立て順番に実行していきます。

![](https://static.zenn.studio/user-upload/c89e0ccb97b8-20260522.png)

しばらくすると「秘密保持契約書」のレビューが完了しました！  
契約大臣で作成している契約書本文をMCP経由で取得し`nda-review`スキルでレビューをしています。

![](https://static.zenn.studio/user-upload/e8ac88a26eb1-20260522.png)

およそ7分で完了しました。  
スクリーンショットでは伝わりにくいですが、AIエージェントが自動的にコネクタやスキルを使って目的を達成してくれました！  
RED判定の契約書は改訂版が作成されており、詳細についてはマークダウンファイルにまとめてくれました。  
![](https://static.zenn.studio/user-upload/ca7402301e22-20260522.png)

![](https://static.zenn.studio/user-upload/ac8d3622e824-20260522.png)

GREEN判定の契約書はスプレッドシートの送付先に送信されていました。  
![](https://static.zenn.studio/user-upload/822ec0869c80-20260522.png)

Slackにも通知されています。  
![](https://static.zenn.studio/user-upload/1ead72b8ba1c-20260522.png)

今回はダミーの契約書を使ったため、レビュースキルそのものの実力までは実感できませんでした。  
この点は今後、自社の基準に合わせてセットアップしたうえで、実際の契約書で改めて試してみたいと思います。  
また今回はレビューから送信まで一気に走らせてみましたが、実務で運用するなら、送付先の設定までを自動化し、人の承認が済んでいないものは送信直前の「内容確定」ステータスで一度止めるのが現実的でしょう。

## まとめ

想定通りの挙動になったので大変満足です！！

AIエージェントが動いている間に別の作業ができますし、定期実行にしていれば処理漏れも防げます。

法務関連の業務についてどこまでAIに任せることができるのか？といったテーマについては、これからもいろいろと課題となる部分はあると思いますが、法務に特化したAIエージェントの誕生が、これからの業務のあり方を大きく変えていくことは間違いないでしょう。

レビューについては、まずは契約書を送信する前の最終チェックに使ってみるところから始めてみるのがよさそうですね。意外な発見があるかもしれません。

そのほか感じたこととしては、作業の自動化ができるClaude Coworkと契約大臣MCPサーバーとの相性が抜群だった点です。  
現時点で国内電子契約サービスでMCPサーバーを提供しているのは契約大臣だけです！  
ご興味があれば、ぜひ[お問い合わせ](https://keiyaku-daijin.com/contact?utm_source=Zenn&utm_medium=article&utm_campaign=Claude-for-Legal-keiyaku-daijin)ください。お待ちしております。
