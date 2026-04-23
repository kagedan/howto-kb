---
id: "2026-03-22-ウワサのclaude-code-channels-素人でもできるwindows版セットアップ解説-01"
title: "【ウワサのClaude Code channels】 素人でもできるWindows版セットアップ解説"
url: "https://note.com/yamachas0/n/nfe7dff0db243"
source: "note"
category: "claude-code"
tags: ["claude-code", "note"]
date_published: "2026-03-22"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

**「Claude Code channels」**来ましたね！  
何といっても、**スマホからClaude Code触れる！！**

先行のサービスで[Openclaw](https://openclaw.ai/)がありますが、怖くて手を付けられなかった皆さん。  
これは**Anthropicのインフラの上でほぼ同じことができます**ので、いよいよ試す価値ありです。

**私自身ノンエンジニアですが、AIに聞きながらセットアップできました**。  
簡単だとは言いませんが、ここはひとつ頑張って、3連休のお土産にセットアップしてみましょう！

![](https://assets.st-note.com/img/1774098280-ij9eroyWs1INK0pVkY2DHAhc.png?width=1200)

Openclaw と Claude Code Channels の違い

---

  

## Claude Code Channelsって何？

2026年3月20日にAnthropicが正式発表した、**Claude Codeを外部のメッセージアプリから操作できるようにする機能**です。

ざっくりイメージを言うと、

という感じ。  
3/20時点ではDiscordとTelegramがオフィシャル対応しています。

何がすごいのか、一言で言います。

**「Claude Codeに何かを頼むとき、PCの前に座っている必要がなくなること」**

これまで、Claude Codeに何か頼むにはPCの前でプロンプトを打つしかなかった。  
でもこれが動くと、極端な話**お風呂に入りながらスマホからDiscordでClaude Codeに「あのバグ修正しといて」と送れる。**

Claude Codeは自分のPCの中で黙々と作業して、終わったら**Discordで「終わりました」と返してくれる**。

---

### OpenClawとどう違うの？

「それって以前からあったOpenClawでよくない？」という疑問、間違いではないと思います。

**OpenClaw**は、ピーター・スタインバーガーが作ったオープンソースの自律型AIエージェント環境で、まさに同じことを実現していたツールです。

WhatsApp・Telegram・Discord・Signal・iMessageなどに幅広く対応していて、シェルコマンドの実行からファイル操作、ブラウザ制御まで何でもできるやつですね。

まさに**できることはClaude Code Channelsとほぼ同じ**です。

ただ、OpenClawには初心者からすると怖い問題がありました。

**セキュリティのリスク**。

研究者が「最初の主要なAIエージェントセキュリティ危機」と呼んだほどの事態を引き起こしていて、プロンプトインジェクション攻撃、悪意のあるスキルのアップロード、不正なファイルアクセスといったリスクが指摘されてきました。  
CiscoはOpenClawを「セキュリティの悪夢」と呼び、Gartnerは「デフォルトで安全でない」と評価していたくらい。

### Anthropic公式のインフラで動くことの重要性

そういう意味で今回のchannelsが重要なのは、これが**Anthropic公式のインフラで動く**という点です。

OpenClawがオープンソースであるゆえに抱えていたセキュリティ上の怖さに対し、これはAnthropicが一定のセキュリティを担保してくれる中で動く。

もちろん、**PCの自動操作という点においては危険性は同様にある**のですが、何があっても自己責任のOpenclawと比べれば、一番最初の導入ハードルはだいぶ下がったと思います。

---

## STEP 1｜PowerShell 7をインストールする

さて、前置きが長くなりましたが、早速セットアップしてみましょう。

私はノンエンジニアなのでコードもプログラミングも正直自力では無理です。

下記の公式ドキュメントに従ってセットアップする方法をweb版のClaudeに聞きながらやっただけです。

つまり、**特別な知識は不要で、根気強く最後までやり切れるかどうかだけ**です。

この記事では、タイトルの通り**Windows環境でのセットアップ**について手順を追って紹介します。

とりあえず、PowerShell（黒い画面。ターミナルとか言ったりする）はさすがに通らないわけにはいかないのでここから入りますね笑  
基本的にClaude Codeを使う人向けの話なので、ターミナルは一度通過儀礼は受けているものと前提します笑

STEP4までが一旦PowerShellでの操作です。

いきなりですが、**まず最初の落とし穴がここ**です。

Windowsに最初から入っている「Windows PowerShell」（バージョン5）は、Claude Codeのインストーラーと相性が悪くて正常に動きません。  
（私もここで引っかかった）

**PowerShell 7という別バージョンを追加インストールしておきましょう。**

```
winget install Microsoft.PowerShell
```

インストール後、スタートメニューで「PowerShell 7」または「pwsh」を検索して起動します。  
タイトルバーに「PowerShell 7 (x64)」と表示されていればOK。

![](https://assets.st-note.com/img/1774098929-dADKsxLwYGz3VkcN762i8plt.png?width=1200)

PowerShell 7

> ⚠️ ここから先の作業は、**必ずPowerShell 7で行うこと。** 「Windows PowerShell」と「PowerShell 7」は別物だと思ってください。

---

## STEP 2｜Git for Windowsを確認する

Claude CodeはWindows上でコマンドを実行するとき、内部で「Git Bash」というツールを使っています。  
（これも、ふーんでいいと思います）

これはGit for Windowsに含まれていて、入っていないとClaude Code自体が正常に動きません。

Claude Codeのセットアップですでに入っているはずですが、改めて入っているか確認しましょう。

```
git --version
```

バージョン番号が表示されればOK。

![](https://assets.st-note.com/img/1774099093-P08Hymglaov7JpthInLAK2Sr.png)

表示されない場合は <https://git-scm.com> からインストール。  
インストール時の選択肢はすべてデフォルトのままで問題ありません。

---

## STEP 3｜Bunをインストールする

「Bun」はたぶん知らないですよね。私も知りませんでした笑  
JavaScriptの実行環境（ランタイム）で、まぁchannelsを動かすために必要なんだな、でいいと思います。

DiscordのBotサーバーはこのBun上で動くため、**これがないとBotがDiscordでオフラインのまま**になります。

厄介なのが、セットアップ後半で、**Claude Code自体は動いているように見えても、BotだけDiscordに接続できないという状態になる**こと。  
Bunが入っていないとそういう挙動をします。  
（私もなりました笑）

```
irm bun.sh/install.ps1 | iex
```

インストール後は、**一度ターミナルを閉じて新しく開き直します**（PATHという設定を反映させるため）。

```
bun --version
```

バージョン番号が出ればOKです。

![](https://assets.st-note.com/img/1774099471-IUNuToglKx1rcCyAepvFQ5wO.png)

---

## STEP 4｜Claude Codeをインストールする

ここは、インストールできている人は飛ばしてください。

```
irm https://claude.ai/install.ps1 | iex
```

インストール後はターミナルを閉じて開き直す。

```
claude --version
```

バージョンが表示されれば完了です。

![](https://assets.st-note.com/img/1774099547-98yP4qJvanlicdLe0b7FQVpr.png)

---

## STEP 5｜Discord BotをDeveloper Portalで作る

STEP５，６はDiscord側の設定です。

Developer Portalと聞くと開発者向けで構えちゃうと思うんですが、手順通りやれば変なことはおきないので、大丈夫です。

最近日本語にも対応したので、あまりビビらずに開いてみてください。

（１）<https://discord.com/developers/applications> を開く

（２）アカウント持っていない人はサインイン、持ってる人はログイン

（３）右上「新しいアプリケーション」→ 好きな名前をつけて「作成」（いつでも変えれます）

![](https://assets.st-note.com/img/1774099890-kOI9MCxlBZc6zE1YR3g2fXD5.png)

（４）左サイドバー「概要」の中の「Bot」→アイコン、バナーはまだなくてOK

![](https://assets.st-note.com/img/1774099947-Rztrceqd1L3Aa6MJTYK8uINj.png?width=1200)

（５）同じページの「公開Bot」と「Privileged Gateway Intents」3つをすべてONにして「変更を保存」  
公開Bot**←公開することはないですがONにしておかないと認証ができない**  
Presence Intent  
Server Members Intent  
Message Content Intent ← **これがOFFだとBotがメッセージを受け取れない**

![](https://assets.st-note.com/img/1774100603-zhVapvboi8OL2un1gN0A3YHq.png?width=1200)

（６）「トークンをリセット」→「実行します！」→セキュリティ認証

![](https://assets.st-note.com/img/1774100167-rKOsDI6LXBufaYCmU5ji4ncT.png?width=1200)

![](https://assets.st-note.com/img/1774100182-6TrvKfHUQBlCyJXkd38R7Z1A.png)

![](https://assets.st-note.com/img/1774100418-8EPA5O0MuSLotn2HTxdigzYp.png)

（７）トークンが表示されるので「コピー」（**一度しか表示されないので必ずメモ**）  
**※これは絶対に公開しないこと**

![](https://assets.st-note.com/img/1774100530-7m5KTXFfg4ZpEDxiWAj9oaJL.png?width=1200)

これでBOTが存在するための準備が一旦できました。ただしまだ生まれたてで何もできません。

---

## STEP 6｜BotをDiscordサーバーに招待する

BOTの存在ができても、サーバーにJoinしていないと何もできません。  
自分用のサーバーか、使いたいサーバーに追加しておく必要があります。  
生まれた病院から自宅に迎え入れるイメージですね。

（１）左サイドバー「概要」の中の「OAuth2」→「OAuth2URLジェネレーター」の中の「スコープ」で、「bot」にのみチェック

![](https://assets.st-note.com/img/1774100898-1YcmyvpUnwPVt7EC2xQ0G8MD.png?width=1200)

（２）下に「Botの権限」を選択する場所が出てくるので、以下にチェック  
**＜最低限以下２つ＞**  
メッセージを送る  
メッセージ履歴を読む  
**＜入れておくとよいと個人的に思うもの＞**  
リンクを埋め込み  
ファイルを添付  
リアクションをつける  
ボイスメッセージを送信

※権限を後から追加することも可能ですが、BOTごとサーバーに入れ直すことになるので、現時点で使いそうだなと思うものに限っては入れておいた方がよいと思います。

> ⚠️ 一般権限の列にある権限（「管理者」などの強い権限）は付けないこと。必要最低限にとどめるのがセキュリティの基本です。

（３）下の方に表示される「生成されたURL」をブラウザで開いて、入れたいサーバーを選択して「はい」  
→先ほど選択した権限が合っているか確認して「認証」

![](https://assets.st-note.com/img/1774101412-pAwFMn0Xy4CrdLki8l1Oajc3.png?width=1200)

![](https://assets.st-note.com/img/1774101465-EzjWA2DrHTGhqUVwydpBs5t9.png)

![](https://assets.st-note.com/img/1774101487-R0KgFYmbNfpVxorMuJWd9aUO.png)

![](https://assets.st-note.com/img/1774101536-D9S2po4LjxcveqAYwQB36EI8.png)

![](https://assets.st-note.com/img/1774101618-wEdS8VrAIRN2MQCyLJPcv3pn.png)

（４）DiscordにBOTが入ったことを確認  
右上のステータス欄の「オフライン」のところに、今入れたBOTがグレーアウト状態でいると思います。  
まずはこうなっていれば、**BOTをDiscordサーバーに入れることに成功した**、という状態です。

![](https://assets.st-note.com/img/1774101720-yKOs7SpdFmoETbRfiL6Pq1kZ.png)

余談ですが、DiscordにBOTを入れるのは、どんなBOTでも基本的にこの手順です。  
意外と入れるだけなら簡単だと思いません？

BOTに何をさせるかは、させたいことに特化したプログラムに先ほどのトークンを設定することで機能するんですね。  
今回の場合、Claude Code Channelsというプログラムにトークンを紐づけることで、先ほど入れたBOTに魂が宿り、ステータスが「オンライン」の方に移動していよいよ動き始める、というわけです。

---

## STEP 7｜Claude CodeにDiscordプラグインを入れる

さて、ターミナル（PowerShell 7）に戻ります。  
（１）Claude Codeを --channelsオプション付きで起動します。  
→私はここでPowerShellのバージョン問題にぶち当たり、たどり着いたのがPowerShell 7でのこのコード実行でした。  
エラー出たら、スクショ撮ってweb版のClaudeに聞いてを繰り返しましょう。必ず突破できますから、根気強くやりましょう。

```
claude --channels plugin:discord@claude-plugins-official
```

簡易の安全チェックが聞かれるので、問題なければYes。

![](https://assets.st-note.com/img/1774102830-BVWyIA8vjctXnfRENwpQ6bqi.png?width=1200)

（２）Claude Codeの起動を確認  
うまくいっていれば、いつものClaude Code画面になります。  
 Listening for channel messages from: plugin:discord@claude-plugins-officialと赤字で表示されていますね。channelsがうまく起動できている証拠です。

![](https://assets.st-note.com/img/1774102321-nE70NretzJYVQLPhRcS6kZWB.png?width=1200)

（３）ClaudeのDiscordプラグインをインストール  
以下のコードを上記画面の入力欄で入力してエンター。ターミナルを別で開く必要はなし。

```
/plugin install discord@claude-plugins-official
```

同じような安全チェックがあり、インストールが始まります。  
終わったらもう一度上記コードを入力欄に打ってみましょう。

ちゃんとインストールができていれば、already installed globally.といった文字が出ているはずです。

（４）プラグインをリロード  
そのまま入力欄に移以下を入力してエンター。

```
/reload-plugins
```

Reloaded: 1 plugin　と記載されていれば、プラグインが正常に読み込まれている状態です。

![](https://assets.st-note.com/img/1774103288-EIKceBNCLHYxgtuXai5n7jR8.png?width=1200)

![](https://assets.st-note.com/img/1774102367-P5lEVjDo2HiNLm9kGR8T4Sat.png?width=1200)

---

## STEP 8｜BotトークンをClaude Codeに設定する

STEP８,９は、BOTとClaudeをつなげる作業です。

まず、STEP 5でコピーしたDiscordトークンを設定します。

```
/discord:configure <STEP5でコピーしたトークン>
```

＜＞の中にトークンを入れてください。＜＞は残っていてOK。  
STEP7と同様の簡易安全チェックが出るので、問題なければYES。

![](https://assets.st-note.com/img/1774103637-72AgHev3RzNmlbjUZ8XCa0Od.png?width=1200)

プログラムが走り、うまくいけばトークンが設定された旨Claude Codeが返してくれます。  
（以下はすでに設定できたあとの私の画面なので、同じコメントではないと思いますが、設定できていればOK！）

![](https://assets.st-note.com/img/1774103924-lYo01rx2VkuCfW4i5TaqbNch.png?width=1200)

この時点で、Discord画面右側のステータスで「オフライン」にいたBOTは「オンライン」に来たはずです。  
※僕のBOTは「サブちゃそ」になってもらいましたw

![](https://assets.st-note.com/img/1774105434-Yx7fPOWC6yiFl085vbX4NIKs.png)

---

## STEP 9｜ペアリングする

いよいよBOTに魂を吹き込む瞬間です。

（１）DiscordでBotにDMを送る（内容は何でもOK）  
「オフライン」のところにいるBOTのプロフィールを開いて、メッセージマークをクリックしてDM画面に行きます。

![](https://assets.st-note.com/img/1774104948-WDeX6kE8bQBT03ainxMC4qsg.png)

何か適当に入力してください。  
※DiscordでDM許可してない場合は一旦許可しましょう

**Pairing required — run in Claude Code:  
/discord:access pair ●●●●●●**  
と返ってくれば大成功！  
●●●●●●の部分がペアリングコードです。

![](https://assets.st-note.com/img/1774105048-e16aRd2j5nqEbHCKWUSB3XMg.png)

（２）Claude Codeにペアリングコードを入力せよという表示が出ていると思うので、コピペして貼り付け。

すると、DiscordのDMのほうに

**Paired! Say hi to Claude.**

と返ってきているはずです。  
なんでもいいので打ち込んでみましょう。  
会話が返ってくるはずです。

![](https://assets.st-note.com/img/1774105589-io2q7va1kuPpdAVxgUCyMGS5.png)

**おめでとうございます！！ついにBOTに魂が吹き込まれました！！**

**これでClaude Code channelsのセットアップが完了しました！！**

詰まりポイントは正直多いと思います。  
**私も上記淡々と進んでいるように書いてますが、途中で何度も止まってます。**  
ですが、**Claudeに「次これどうやるの？」と聞いてスクショを添えて投げる**、というやり方を繰り返していれば、こうしてエンジニアじゃなくてもちゃんとたどり着けます。

---

## 実際に使ってみた感想

僕はもともとOpenClawを使っていたので、比較してみていますが、できることの幅は大差なく、**ほぼ同じことができるという印象**です。

何ならターミナル上ではチャットのやり取りと生成経過も見れるので、OpenclawよりUIはいいです。  
（スマホで指示するときはあまり意識しないけど）

一点挙げるとすれば、**承認フロー**ですね。

Claude Codeには、コマンドを実行したりする前に「これ実行していいですか？」と確認を取るステップがありますよね。

Discordを窓口にしているだけでPC上のClaude Codeを触っていることには変わりないので、スマホのDiscordで何かお願いしたとしても、**承認はPCでターミナル上のClaude Codeで行う**必要が当初設定ではありました。

つまり、せっかくスマホで指示できるのに承認で止まってDiscordには何も返ってこない状態w  
意味ないw

ただし簡単に回避できます。  
**「承認が必要なアクションが発生したらDiscordで聞いて」と最初に指示しておく**と、Discordのチャット上で「〜を実行してよいですか？」と確認してくれます。  
逆に言うとこれだけは指示しておかないと、何かあるたびにPCの前に戻らないといけなくなるので、最初に一言送っておくのがおすすめです。

---

無事にセットアップ完了した皆さん、お疲れ様でした！  
**Claude Code channelsでステキなAI agentライフを！！**
