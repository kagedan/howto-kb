---
id: "2026-03-20-外出先からスマホでaiに仕事を振るanthropicの新機能claude-dispatchを試してわ-01"
title: "外出先からスマホでAIに仕事を振る。Anthropicの新機能「Claude Dispatch」を試してわかったこと"
url: "https://note.com/k158745/n/n31ec2dfc1b37"
source: "note"
category: "cowork"
tags: ["cowork", "note"]
date_published: "2026-03-20"
date_collected: "2026-03-20"
summary_by: "auto-rss"
---

## 「AIに仕事を投げて寝る」が、ついに公式機能になった

2026年3月17日、AnthropicがClaude Coworkの新機能「Dispatch（ディスパッチ）」を発表しました。  
  
一言でいうと、\*\*スマホからMacに指示を送り、Claudeが自動で処理して、帰宅したら完成している\*\*——そんな機能です。  
  
実はこの「スマホからPCのAIに仕事を振る」というワークフロー自体は、OpenClawというオープンソースのツールを使えばすでに実現できていました。ただ、今回Anthropicが公式機能として出してきたのは大きい。セキュリティの担保、セットアップの簡便さ、そして何より「公式」という安心感は、個人開発のツールとは別次元です。  
  
早速触ってみたので、セットアップの手順から実際の使用感、そして「ここはまだ厳しいな」と感じた点まで正直にレポートします。  
  
-----

## そもそもDispatchって何？

![](https://assets.st-note.com/production/uploads/images/260568698/picture_pc_bd5b3dfd8a8844b740256c6a7a4b6c27.png?width=1200)

### 従来の問題

Claude Coworkは、PCのデスクトップアプリ上でClaudeにファイルの編集やリサーチなどの作業を任せられるツールです。非常に便利なのですが、一つ大きな制約がありました。\*\*PCの前にいないと使えない\*\*ということです。  
  
外出中は作業が止まる。セッションが切れるリスクもある。「あ、さっきの作業どうなったかな」と気になっても、PCを開かない限り確認できない。

### Dispatchが解決すること

Dispatchは、スマホのClaudeアプリとPCのClaude Desktopを「1本の持続的な会話」でつなぎます。  
  
スマホからClaudeに指示を送ると、PC上のClaudeがローカル環境でその作業を実行する。ファイルの読み書き、Google Driveとの連携、ブラウザでのリサーチ、スプレッドシートの作成——Coworkでできることはすべて、スマホから遠隔で指示できるようになります。  
  
そして大事なポイントは、\*\*データはPCのローカルで処理される\*\*ということ。ファイルがクラウドに送られるわけではないので、プライバシーの面でも安心感があります。  
  
-----

## セットアップ：QRコードを読むだけ

実際のセットアップは拍子抜けするほど簡単でした。  
  
\*\*手順1：\*\* Claude Desktopアプリを最新版にアップデート。  
  
\*\*手順2：\*\* アプリ内でDispatchのペアリング画面を開くと、QRコードが表示される。  
  
\*\*手順3：\*\* スマホのClaudeアプリでQRコードをスキャン。  
  
これだけです。特別な設定もポートの開放も不要。5分とかからずに接続が完了しました。  
  
接続が成功すると、スマホのClaudeアプリ内に「Cowork」のスレッドが表示されます。ここに入力した内容が、そのままPC上のClaudeに届く仕組みです。  
  
-----

## 実際に使ってみた：3つの実験

![](https://assets.st-note.com/production/uploads/images/260568903/picture_pc_73cdb0f9e1da75c593ab80cdc2f4b506.png?width=1200)

### 実験1：外出先からファイル整理を指示してみた

まず試したのは、散歩に出かける前にスマホから「デスクトップにある先週の議事録3つを要約して、1つのMarkdownファイルにまとめて」と指示すること。  
  
スマホで送信ボタンを押して、そのまま外出。30分ほどして帰宅すると、デスクトップにきれいにまとまった要約ファイルが生成されていました。  
  
\*\*正直な感想：\*\* これは感動しました。「自分がいない間にAIが仕事をしている」という体験は、頭ではわかっていても実際に目の当たりにすると不思議な感覚です。

### 実験2：移動中にリサーチを依頼してみた

電車に乗っている間に「来週のプレゼンで使う、2026年のクラウドセキュリティ市場のトレンドを調査して、PowerPointの構成案を作って」と投げてみました。  
  
こちらも、到着する頃にはリサーチ結果と構成案がPC上に生成されていました。ブラウザで情報を集め、ローカルのコネクタを通じてファイルを作成する——という一連の作業がスマホからの一言で完了しています。  
  
\*\*正直な感想：\*\* 移動時間が「空白の時間」から「AIが働いている時間」に変わる感覚。通勤時間の価値が根本的に変わるかもしれない。

### 実験3：少し複雑な作業を頼んでみた

調子に乗って、「Googleドライブにある売上データのスプレッドシートを分析して、傾向をまとめたレポートをPDFで出力して」と頼んでみました。  
  
結果は……半分成功、半分失敗。分析とレポートの生成自体はうまくいったのですが、PDFへのエクスポートの段階で止まってしまいました。スマホに戻ってきたのはエラーではなく、中途半端な状態のレポート。  
  
\*\*正直な感想：\*\* 複雑なタスクになると、まだ不安定な部分がある。MacStories.netのレビューでも「成功率は約50%」と報告されており、体感としてもそのくらいの印象でした。  
  
-----

## Remote Controlとの違いは？

![](https://assets.st-note.com/production/uploads/images/260568970/picture_pc_912cd9bebd4f0895a330dd58e2aecf40.png?width=1200)

以前の記事で紹介した「/remote-control」機能を思い出した方もいると思います。両者は似ているようで、実は対象が違います。  
  
\*\*Remote Control（/remote-control）：\*\* Claude Code（ターミナルベースの開発ツール）のセッションをスマホに引き継ぐ。主にエンジニア向け。コードの実行、Git操作、テストなどが対象。  
  
\*\*Dispatch：\*\* Claude Cowork（デスクトップのナレッジワーカー向けツール）のセッションをスマホから操作する。エンジニアに限らず、あらゆる知識労働者が対象。ファイル整理、リサーチ、資料作成、メール処理などが中心。  
  
つまり、Remote Controlが「エンジニアがコーディングを続ける」ための機能なのに対し、Dispatchは「誰でもデスクワークを遠隔で進められる」機能です。技術者でなくても使えるという点で、影響範囲はDispatchの方がはるかに広いと感じます。  
  
-----

## 現時点の制限と注意点

![](https://assets.st-note.com/production/uploads/images/260569028/picture_pc_9ef1d1ac3f5c26a1ecee95c18a7f3b84.png?width=1200)

研究プレビューということもあり、いくつかの制限があります。正直にお伝えします。  
  
\*\*PCの電源とアプリの起動が必須。\*\* Dispatchは「スマホ→クラウド→PC」ではなく「スマホ→PC（直接）」の通信です。そのため、PCがスリープ中だったりClaude Desktopが閉じていると動作しません。バックグラウンドサービスとしては動かないので、長時間の外出時はPCの電源設定に注意が必要です。  
  
\*\*会話スレッドは1本だけ。\*\* 現時点では、DispatchのCoworkスレッドは1つしか持てません。複数のタスクを並行して走らせることはできないので、作業の優先順位を決めてから投げる必要があります。  
  
\*\*タスク完了の通知がない。\*\* 地味に困ったのがこれ。Claudeが作業を完了してもスマホにプッシュ通知が来ません。「終わったかな？」と自分でスレッドを確認しに行く必要があります。今後のアップデートで改善されることを期待しています。  
  
\*\*成功率にムラがある。\*\* 前述の通り、単純なタスクは問題なく完了しますが、複数ステップにまたがる複雑なタスクでは失敗することがあります。「帰宅したら完成している」を100%信頼するのは、まだ早い。  
  
\*\*対応プラン。\*\* 現時点ではMaxプラン（月額100〜200ドル）から順次展開中。Proプラン（月額20ドル）への対応は数日以内とのことです。  
  
-----

## OpenClawとの比較：公式の安心感 vs オープンソースの自由度

ツイートでも触れられていたOpenClawとの比較について、少し補足します。  
  
OpenClawはオープンソースのAIエージェントで、GitHubスターは32万を超えています。Telegram、WhatsApp、Discordなど複数のメッセージングアプリから操作でき、100以上のスキルが搭載されている。LLMも選べる。機能面では正直、現時点のDispatchより上です。  
  
ただし、OpenClawにはプロンプトインジェクション（悪意のある指示の注入）やマルウェア感染などのセキュリティリスクが指摘されており、中国のCNCERTが政府機関に警告を出すほどの問題になりました。  
  
Dispatchの強みは、\*\*サンドボックスによる実行環境の隔離\*\*、\*\*破壊的操作の前に確認プロンプトが出るHuman-in-the-Loopの設計\*\*、そして\*\*エンドツーエンドの暗号化\*\*です。「公式」ゆえの制約はありますが、業務で使うならこの安心感は大きい。  
  
-----

## まとめ：「AIに仕事を投げて出かける」時代が始まった

![](https://assets.st-note.com/production/uploads/images/260569057/picture_pc_443c42886dbfe7f23f41b5e88cf7991e.png?width=1200)

Claude Dispatchは、まだ荒削りな部分もある研究プレビューです。成功率は100%ではないし、通知機能もない。  
  
でも、この機能が示している方向性は明確です。\*\*AIは「相談相手」から「自分がいない間に仕事をしてくれる存在」へと進化している\*\*ということ。  
  
「外出前にスマホでAIに指示を出し、帰宅したら仕事が完成している」——この体験を一度味わうと、もう元には戻れない気がします。数ヶ月後には通知機能も複数スレッドも対応されて、安定性も上がっているでしょう。そのとき、この機能は「便利ツール」ではなく「働き方そのもの」を変える存在になっているはずです。  
  
Maxプランの方は今すぐ、Proプランの方も数日後には試せます。Claude Desktopをアップデートして、スマホとペアリングするところから始めてみてください。  
  
-----  
  
\*この記事は2026年3月19日時点の情報に基づいています。Dispatchは研究プレビュー段階のため、機能や対応プランは今後変更される可能性があります。\*  
  
-----

## 参考サイト

- Anthropic公式リリースノート - Dispatch  
  https://releasebot.io/updates/anthropic/claude  
- MLQ - Anthropic Launches Claude Dispatch for Remote Desktop AI Control  
  https://mlq.ai/news/anthropic-launches-claude-dispatch-for-remote-desktop-ai-control/  
- COEY - Anthropic Dispatch Turns Claude Into Your Always-On Creative Coworker  
  https://coey.com/resources/blog/2026/03/17/anthropic-dispatch-turns-claude-into-your-always-on-creative-coworker/  
- Lapaas Voice - Anthropic Unveils “Claude Dispatch”: Remote Control for Your AI Desktop Agent  
  https://voice.lapaas.com/anthropic-unveils-claude-dispatch-remote-control-for-your-ai-desktop-agent/  
- abit.ee - Anthropic launches Dispatch: the “safe” answer to OpenClaw’s wild success  
  https://abit.ee/en/artificial-intelligence/anthropic-claude-dispatch-openclaw-ai-agent-claude-cowork-desktop-automation-subscription-en  
- Quasa.io - Anthropic Just Shipped Its Own “OpenClaw” — Meet Dispatch for Claude Cowork  
  https://quasa.io/media/anthropic-just-shipped-its-own-openclaw-faster-than-openai-meet-dispatch-for-claude-cowork  
- Aihola - Anthropic shipped Dispatch for Claude Cowork  
  https://aihola.com/article/anthropic-dispatch-cowork-mobile  
- Latent Space - Claude Cowork Dispatch: Anthropic’s Answer to OpenClaw  
  https://www.latent.space/p/ainews-claude-cowork-dispatch-anthropics
