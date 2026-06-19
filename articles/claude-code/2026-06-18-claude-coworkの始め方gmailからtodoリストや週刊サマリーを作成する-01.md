---
id: "2026-06-18-claude-coworkの始め方gmailからtodoリストや週刊サマリーを作成する-01"
title: "Claude Coworkの始め方。GmailからToDoリストや週刊サマリーを作成する"
url: "https://zenn.dev/kameoncloud/articles/58a7fa72a4d640"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "cowork", "zenn"]
date_published: "2026-06-18"
date_collected: "2026-06-19"
summary_by: "auto-rss"
query: ""
---

<https://serverless.co.jp/blog/j8fthdly-m/>  
へ投稿した記事の微修正版です。

今日は、Anthropic版パーソナルアシスタントのClaude Cowork を使ってみます。

#### Claude Cowork とは

「AIにアドバイスをもらうだけでなく、実際の作業を任せたい」——そんな声に応えるように、Anthropicが2026年1月に発表し、同年4月9日に正式リリース（GA）したのが Claude Cowork（コワーク） です。

CoworkはClaudeをチャット相手から「自分のPCで実際に作業するAI同僚」へと変える機能です。プログラミングの知識は一切不要。指示を出してあとは任せれば、Claudeがファイルを読み込み、複数の処理をこなし、完成した成果物を届けてくれます。

従来のAIチャットは「相談相手」でした。たとえば「報告書の書き方を教えて」と聞けば構成案を返してくれますが、実際に文章を書いてファイルにまとめるのはユーザー自身の仕事でした。Coworkは「このメモから報告書を作成して」と指示するだけで、AIが自らファイルを作成し、内容を記述し、体裁の整ったドキュメントとして完成させてくれます。つまり、作業の「やり方」を聞くフェーズから、作業そのものを「丸投げ」できるフェーズへと移行したのです。

Coworkを使えば、必要な成果物を説明してその場を離れ、戻ってきたときには整形されたドキュメント、整理されたファイル、まとめられたリサーチなどが完成しています。ターミナル操作は不要で、Claude DesktopアプリのUIから操作できるため、ターミナルに馴染みのない方でも利用できることが特徴です。

### さっそくやってみる

まず第一回はチャットベースの指示でGmailの内容を纏め Weekly Report を Google Drive に出力してみます。利用には最低Proプラン以上の有料プランが必要となりますので注意してください。

Cowork は少しわかりづらいですが、Claude Desktopのこのタブにあります。  
![](https://static.zenn.studio/user-upload/59467c37542b-20260618.png)  
普段は以下の様に Chat になっていますのでその右のアイコンをクリックすれば出てきます。  
![](https://static.zenn.studio/user-upload/eb044861f90d-20260618.png)  
シンプルに gmail をサマリーできますか？ と聞いてみます。そうすると

```
Gmailコネクタはまだ接続されていないようです。Gmailをサマリーするには、まずGmailコネクタを接続する必要があります。
```

と表示されコネクターのインストールとGmailへのログインが求められます。  
![](https://static.zenn.studio/user-upload/7da0b8282187-20260618.png)  
![](https://static.zenn.studio/user-upload/3765d33a07e7-20260618.png)  
![](https://static.zenn.studio/user-upload/e18b785a877a-20260618.png)  
以下の様なメッセージが表示されます。

```
接続が完了したら、「今日のメールをサマリーして」「未読メールをまとめて」など、お好みの粒度でお知らせください。例えば期間（今日／今週／過去24時間）、対象（未読のみ／全部／特定の差出人）などを指定していただくと、より的確にお応えできます。
```

例えば `今日のメールをサマリー` と入力してみます。  
しばらく待つと以下のメッセージ(一部を抜粋）が表示されます。

```
過去24時間（4/25夕方〜4/26朝）に届いた約40件のメールを、カテゴリ別にサマリーします。
重要・要対応

Googleセキュリティ通知（4/26 13:26）: Claude にGoogleアカウントへのアクセスを許可した旨の確認通知。心当たりがあるので対応不要です。
JCBカード利用通知 3件（同一スレッド）:

4/26 01:11 xxx ¥3,211
4/26 10:01 yyy ¥11,540
4/26 10:11 zzz ¥840

仕事・キャリア関連

ビズリーチ 6通: 日産自動車・自動車部品の求人案内、人事・労務特集が4/30締切、プラチナスカウトの説明、リカレント講座（5/15まで配信）、AI時代のキャリアコラムなど。
HiPro Direct: スキルマッチ案件の新着紹介。
LinkedIn 3通: プロフィール検索37回、メッセージ通知、つながり提案（aaaa一さん）。

イベント / 勉強会（connpass・TechPlay）

「はじめてのAI駆動開発：Claude CodeでToDoアプリを爆速実装」 → 募集終了が明日（4/27）
「Google Cloud Next'26 Recap」（クラスメソッド日比谷、4/28開催） → 募集終了が明日
AWS麻雀（5/23 大阪）新規公開
JAWS-UG横浜 #100、Midosuji Tech に資料追加
TechPlayから新着イベント通知
```

次に `メールの内容をまとめた週次レポートをGoogle Driveに保存してください` として追加の依頼を行います。

今度は Google Drive 用コネクターのインストールとアカウントへの接続が求められますので先ほどのGmailと同じ様に許可して接続します。  
![](https://static.zenn.studio/user-upload/9f903355589f-20260618.png)  
以下のメッセージが表示されています。

```
レポートの形式についても確認させてください：

形式: Googleドキュメント形式 / Word（.docx） / Markdown のいずれが良いですか？
粒度: 全メールをカテゴリ別にまとめる / 重要なものだけ抽出 / 仕事関連だけ など
保存先: Driveのマイドライブ直下 / 特定フォルダ（フォルダ名を教えてください）
```

`markdownで重要なものだけ抽出して直下にお願いします。` と入力してしばらく待つとレポートが完成します。  
![](https://static.zenn.studio/user-upload/1cd8a1e5216e-20260618.png)  
Google Drive の方にもファイルが保存されています。  
![](https://static.zenn.studio/user-upload/183ae3110a0e-20260618.png)  
中身を見ると以下の様なサマリーが出力されています。  
![](https://static.zenn.studio/user-upload/fe51348ce75f-20260618.png)  
内容は省略していますがメールの内容から `9. 今週のアクションアイテム` には確認すべきメール、対応すべき事項が一覧としてまとまっています。

```
- [ ] xxx社 yyy様への返信（案件の社内展開状況）
- [ ] 4/26 aa動物病院 ¥11,540 の利用内容確認（JCB明細）
- [ ] connpass 4/27 Claude Code イベントへの参加可否判断
- [ ] connpass 4/28 Google Cloud Next'26 Recap への参加可否判断
- [ ] zzz社 NDA+Advisory Agreement 署名済PDFの保管
- [ ] bbb証券 4/24 ログイン通知の確認
```
