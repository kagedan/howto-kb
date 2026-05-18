---
id: "2026-05-17-xプレミアムプランでgrokとx-searchツールを使う-01"
title: "XプレミアムプランでGrokとx_searchツールを使う"
url: "https://zenn.dev/robustonian/articles/x_premium_grok_search"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-17"
date_collected: "2026-05-18"
summary_by: "auto-rss"
query: ""
---

# はじめに

今朝、Xのプレミアムプランユーザーはhermes-agent経由でX検索が使えるようになったというポストを見かけた。

<https://x.com/xai/status/2055745332919808181>

気になったので調べてみると、SuperGrokの契約が必要だとかX Premium+が必要とか、いやいやPremiumでいけるとかそういう情報が錯綜していた。

私が実際に導入した結果、

* SuperGrokは不要
* Xプレミアムプランだけで`grok-4.3`も動かせて、X検索もできる

という結論に至ったのだが、環境構築にやや苦労したため本記事で備忘録的にまとめる。具体的な内容は下記の通り。

* hermes-agentの導入
* XプレミアムプランでのxAI OAuth認証
* `x_search`ツールの設定
* Grokモデルおよび`x_search`ツールの簡単な使い方

# 手順

## hermes-agentの導入

hermes-agentの導入自体は非常に簡単で、GitHubリポジトリのREADME.mdに従う。

<https://github.com/nousresearch/hermes-agent>

```
$ curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

これだけでインストールが完了する。

## x\_searchツールの導入

hermes-agentのインストール後に下記のコマンドを実行する。

すると下記が表示される（数字は微妙に違うかもしれない）。

![](https://static.zenn.studio/user-upload/2d4f0c251bc5-20260517.png)

ここでまず`Configure 🖥️ CLI`を選択し、Enterキーを押す。

![](https://static.zenn.studio/user-upload/5c8e3cb50c09-20260517.png)

ここで`🐦 X (Twitter) Search (x_search (requires xAI OAuth or XAI_API_KEY))`を選択しスペースキーで☑をつけてEnter。

続いて下記の画面に戻り、`Reconfigure an existing tool's provider or API key`を選択してEnter。

![](https://static.zenn.studio/user-upload/2d4f0c251bc5-20260517.png)

さらに`🐦 X (Twitter) Search`を選択しEnter。

![](https://static.zenn.studio/user-upload/79f7b1072011-20260517.png)

ここもそのままEnter。

![](https://static.zenn.studio/user-upload/4771faf2eea7-20260517.png)

ここもSuperGrok Subscriptionという気になる単語が出てくるが、無視してEnter。

![](https://static.zenn.studio/user-upload/174aeebc8ccb-20260517.png)

すると下記のようなメッセージが出てくる。ここからが少しややこしい。

```
  --- 🐦 X (Twitter) Search - Choose a provider ---

      xAI needs credentials. Choose one:
    Skipped (keeping current)

  Signing in to xAI Grok OAuth (SuperGrok Subscription)...
Open this URL to authorize Hermes with xAI:
https://auth.x.ai/oauth2/authorize?response_type=code&client_id=*****.....

Waiting for callback on http://127.0.0.1:56121/callback

Remote session detected. Your browser will redirect to
  http://127.0.0.1:56121/callback
which the loopback listener on THIS machine is waiting on. If your
browser is on a different machine, forward the port first from your
local machine in a separate terminal:

  ssh -N -L 56121:127.0.0.1:56121 <user>@<this-host>

Then open the authorize URL above in your local browser.
Provider docs:      https://hermes-agent.nousresearch.com/docs/guides/xai-grok-oauth
SSH/jump-box guide: https://hermes-agent.nousresearch.com/docs/guides/oauth-over-ssh
```

ここからは場合分けをする。

### ①ターミナルを操作しているPCでhermes-agentを動かしている場合

この場合は簡単で、`https://auth.x.ai/oauth2/authorize?response_type=code&client_id=*****`をブラウザで開くと下記の画面が出てくる。ただし、Xのログインはすでに完了しているとする。

![](https://static.zenn.studio/user-upload/46386d32d290-20260517.png)

許可を選択すれば認証が終わる。

![](https://static.zenn.studio/user-upload/76f266c44b4a-20260517.png)

### ②リモートPCでhermes-agentを動かしている場合

この場合は少しややこしくて、上記のターミナルを放置したまま別のターミナルを開き、以下のコマンドを実行することでSSHトンネルを張る必要がある。

```
$ ssh -N -L 56121:127.0.0.1:56121 <user>@<this-host>
```

ここで`<user>`、`<this-host>`はそれぞれhermes-agentを動かしているPCのログインユーザーとIPアドレスである。例えば`gosrum`、`192.168.0.11`など。

これを実行するとログインパスワードを求められ、正しい入力をすると下記の表示のまま動かなくなる。

```
🐔@EVO-X2:~$ ssh -N -L 56121:127.0.0.1:56121 gosrum@192.168.0.11
gosrum@192.168.0.11's password:
```

一瞬不安になるが、これでSSHトンネルを張ることができている。この状態で元のターミナルに表示されている`https://auth.x.ai/oauth2/authorize?response_type=code&client_id=*****`をブラウザで開けば、同じように認証できる。

## プロバイダー・モデルの選択

実はモデルの選択がすでに完了している場合はこの時点で`x_search`ツールが使えるようになっている。

つまり`x_search`ツールを使うことだけが目的なら、わざわざGrokのモデルに切り替える必要はなく、自分の好きなプロバイダー/モデルを使えば良い。もちろんローカルLLMでも良い。

仮にGrokのモデルを使いたい場合は、下記のコマンドでモデルの選択ができる。

するとこのような形でプロバイダーがずらっと表示されるので、`xAI Grok OAuth (SuperGrok Subscription)`を見つけてEnter。

![](https://static.zenn.studio/user-upload/94c36ccf88e0-20260517.png)

Xプレミアムの認証は先ほど済ませているので、`1. Use existing credentials`を選択しEnter。

![](https://static.zenn.studio/user-upload/447fc8819d28-20260517.png)

好みのモデル（例えば`grok-4.3`）を選択することで、以後は`grok-4.3`モデルを使うことができる。

![](https://static.zenn.studio/user-upload/29f6ab4b9b2c-20260517.png)

これでプロバイダー・モデルの設定が完了した。

# 使ってみる

hermes-agentはDiscord等の外部ツールと連携することもできるのだが、その話は本記事の本筋ではないため割愛する。

ここでは簡単にCLIとして使う方法を示す。使い方は至ってシンプルで、ターミナルで下記のコマンドを実行すればよい。

すると下記のようなCLIが立ち上がり、ここからは通常のAIエージェントと同じようにコミュニケーションを取ることができる。

![](https://static.zenn.studio/user-upload/97d32c48c78f-20260517.png)

`x_search`ツールを使って○○を検索して、とお願いすればX検索が可能になる。

<https://x.com/gosrum/status/2055894690571161848>

以上！

x\_searchツールでできること、できないこと（参考）

x\_searchツールでできることを、ツール定義に基づき以下にまとめる。

* 基本機能
  + X（旧Twitter）の投稿・プロフィール・スレッドを検索
  + 通常のキーワード検索に加え、Xのadvanced search operators（from:, since:, until:, filter:media など）がqueryで使用可能
  + 現在の話題・反応・主張を調べるのに適している（一般的なWeb検索ではなくX特化）

利用可能なパラメータと効果

* 必須

  + query（string）  
    検索キーワードやクエリを指定。advanced search構文も有効。
* オプション

  + allowed\_x\_handles（配列、最大10件）  
    指定したユーザーの投稿のみに検索を限定（例: ["gosrum"]）
  + excluded\_x\_handles（配列、最大10件）  
    指定したユーザーの投稿を除外
  + from\_date（string、YYYY-MM-DD形式）  
    この日付以降の投稿に絞る
  + to\_date（string、YYYY-MM-DD形式）  
    この日付以前の投稿に絞る
  + enable\_image\_understanding（boolean）  
    一致した投稿に画像が添付されている場合、xAIが画像の内容を分析・理解して回答に反映
  + enable\_video\_understanding（boolean）  
    一致した投稿に動画が添付されている場合、xAIが動画の内容を分析・理解して回答に反映
* 出力の特徴

  + 生の投稿リストではなく、要約された回答形式で返される
  + アカウントのプロフィール情報や文脈も補足される場合がある
  + 関連する投稿のURLがcitationsとして提供される
  + 認証が必要（SuperGrok OAuth または XAI\_API\_KEY）
* できないこと

  + いいね履歴の取得
  + ブックマークの取得
  + DMや非公開投稿の閲覧
  + フォロワー一覧やフォロー一覧の取得
  + いいねした投稿の検索（filter:likes などの公開検索では機能しない）

# まとめ

本記事では、**XプレミアムプランでGrokと`x_search`ツールを使う方法**として、下記について備忘録的にまとめた。

* hermes-agentの導入
* XプレミアムプランでのxAI OAuth認証
* `x_search`ツールの設定
* Grokモデルおよび`x_search`ツールの簡単な使い方

X検索ツール（`x_search`）の追加とGrokモデルの利用は独立しているため、自分の好きなプロバイダー/モデルで`x_search`を使うこともできる。

しかもhermes-agentをDiscord等と連携していれば、そのUIから検索も行うことができるし、cron jobによる定期実行と連携させればかなり活用の幅が広がりそう。今後具体的な活用方法の検討を行っていきたい。

最後まで読んでいただきありがとうございました。今後も面白い使い方や便利な活用法を見つけたら、Xや記事で発信していこうと思います。
