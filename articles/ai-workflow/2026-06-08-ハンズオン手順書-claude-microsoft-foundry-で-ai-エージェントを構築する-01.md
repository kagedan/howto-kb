---
id: "2026-06-08-ハンズオン手順書-claude-microsoft-foundry-で-ai-エージェントを構築する-01"
title: "[ハンズオン手順書] Claude + Microsoft Foundry で AI エージェントを構築する #CodeWithClaude"
url: "https://qiita.com/chomado/items/a072528364883ae7bb96"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "prompt-engineering", "API", "AI-agent", "VSCode", "Python"]
date_published: "2026-06-08"
date_collected: "2026-06-09"
summary_by: "auto-rss"
query: ""
---

アンソロピック社の公式カンファレンス『[Code w/ Claude Tokyo](https://claude.com/code-with-claude/tokyo)』(2026/6/10(水) に開催) に
マイクロソフト社として 1 枠 (45 分間) いただきまして、
「**Claude + Microsoft Foundry でAI エージェントを構築する**」というタイトルのセッション + ハンズオンをさせていただきます✨

その内容を事前にこの記事にまとめておこうと思います！
当日来られなかった方々も内容をチラ見できたらいいなあと思いますし...！

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/733fb634-04e3-4db8-943b-1412165b9993.png)

セッションページ ↓

https://claude.com/code-with-claude/session/tyo-build-agents-microsoft-foundry


そこでは、

* 統合 AI 開発・運用プラットフォーム「[**Microsoft Foundry**](https://azure.microsoft.com/ja-jp/products/ai-foundry)」 (旧称「Azure AI Foundry」)
* AI エージェント開発のためのフレームワーク「[**Microsoft Agent Framework**](https://github.com/microsoft/agent-framework)」

を使い、
実際に (MCP 経由で) AI エージェントにカップケーキを注文させてみるところまでやります。



会場では実際に **物理カップケーキ**（しかも Claude / Microsoft Foundry のロゴ入り）が渡されます！

（参考：先月のロンドン会場のときの写真。会場の手前にカップケーキが置いてあります）

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/1d0cecbf-1476-4172-9585-af343ef8400d.png)

### 写真： Claude / Microsoft Foundry のロゴ入りカップケーキ

めっちゃ美味しそう〜〜〜〜〜！！！私も食べちゃダメかな？（社員はダメ？）

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/42c86b85-b43a-4e6f-9d66-69b3d21ea911.png)

↓ Microsoft Foundry のロゴ画像

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/6d1371a5-b228-4e1d-b75b-9da5e751adbc.png)

https://azure.microsoft.com/ja-jp/products/ai-foundry

https://learn.microsoft.com/ja-jp/azure/foundry/

物理会場の前のスクリーンには、↓のダッシュボードが表示されており、
エージェント経由でカスタマー登録された人たちの注文状況がリアルタイムに見れるようになっています。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/55e5b526-44c9-41bf-86c1-bf36005e0c7a.png)

（私は今カスタマー登録＆テスト申請したばかりなので、左端の「テストフィード」カラムにいる。そのうち右端の done カラム (ready for pick up (カップケーキ回収可能)) に移動される）

# スライド

ハンズオン開始の前に、10 分間くらいちょっとしゃべるのですが、
スライド公開しても良いのか確認がまだなので、確認ができしだい公開します！

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/9c3fc310-c977-4e41-bb93-72a4ebdd2ae6.png)

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/0ac12561-9ab6-453c-a0d4-350b3560f5cc.png)

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/cf1fd2fa-7bda-419c-9a12-c5c42f9ffb86.png)



# ハンズオンの概要

実際に手を動かす前に、ざっくりと全体像をお話しします。

最終的には、
ゼロから構築したエージェントからカップケーキを注文できるようになり、
**Microsoft Foundry**、
**Microsoft Agent Framework**、
そして MCP がどのように連携するのかを学ぶことができます。

（正確に言うと、注文を捌くロジック (カップケーキ在庫 DB 見たりなど) を持っているのは MCP サーバ側で、今回の短いハンズオンではクライアント側の実装のみとなります。カップケーキ MCP サーバはすでに用意されたものを繋ぐだけになります）

## シナリオ : カップケーキ屋のバックグラウンド

小さなカップケーキショップ「Sparkles」に AI エージェントを導入する。

そのショップ「Sparkles」の悩み:

* お客さんが多過ぎる（すごい）
* フレーバーの種類が多すぎる
* カウンターのスタッフが足りない

そこで、AI エージェントを雇うことにしました。

## ゴール : 作る AI エージェントの機能

今から作る AI エージェントは

* お客様をお迎えし、
* その日のフレーバー (the day's flavors) をご案内し、
* 注文を受け、
* 在庫管理をして、
* お帰りの際に焼きたてのカップケーキをお渡しします (これは会場の物理人間がやる)

## やること概要

### 1. web ブラウザでの作業

1. Microsoft Foundry にログイン
1. Playground で Claude Sonnet と簡単なチャットをして動作確認
1. deployment's endpoint と key を取得

### 2. VS Code での作業

Microsoft Agent Framework を使用して、エージェントを少しずつ構築していきます。

1. モデルにアクセスできることを確認するための、基本的な「Hello World」エージェントを作成
1. それをカップケーキストアの MCP サーバー (事前に構築済み) に接続することで、フレーバー一覧の表示、在庫確認、注文といった本格的な機能を持たせる
1. エージェントに独自のペルソナとウェルカムバナーを設定し、ありふれたチャットボットを Sparkles というキャラクターに変身させる

# ハンズオン手順詳細

## 0. 環境にログイン

今回はハンズオン会場に
ハンズオン環境がセットアップされている環境が配布されます。
（なので Azure のサブスクリプションどうするのとか考えなくて大丈夫です。安心！）

![スクリーンショット 2026-06-08 16.15.47.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/22d13e25-8d81-4210-9501-8a38ec60113e.png)

用意された、ハンズオン用の Windows 11 VM にログインします。
右側にインストラクションが（英語で）書いてあるので、読んでいくと、
「Login into the Machine」
のセクションに、ログイン情報（ユーザ名とパスワード）が書いてあるので、それを入力します。（クリックすると自動でフォームに入力されます。便利）

## 1. Microsoft Foundry にログイン

Windows にログインしたら、
タスクバーから web ブラウザ (Edge) を開きます。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/f8327fc9-64bc-4969-8ac4-d28192761e7f.png)

すると、Microsoft Foundry のトップページ (`https://ai.azure.com/`) が開きます。

https://ai.azure.com/home

![スクリーンショット 2026-06-08 16.29.11.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/fdaea4bb-b983-41ba-8f94-935c82816030.png)

そこの「Start Building」をクリックします。
すると、ログイン画面になるので、右側のインストラクションの中に書いてある認証情報を入れていきます。（クリックしたらフォームに自動で入力されます）

まずはユーザ名

![スクリーンショット 2026-06-08 16.32.01.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/b1e89d17-6f33-4ab2-acc8-227bb02d5056.png)

次にパスワード (TAP (Temporary Access Pass)) を入れて、サインインします。

すると、Microsoft Foundry のプロジェクト一覧画面が出てきます。

画面右上の「New Foundry」トグルが on になっていることを確認してから、
（今回のハンズオン用に用意されている、）唯一のプロジェクトをクリックします。

![スクリーンショット 2026-06-08 16.38.07.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/44c97308-7099-4a5c-8d96-71550c88facd.png)

Microsoft Foundry のプロジェクトのポータル画面に来ました！

![スクリーンショット 2026-06-08 16.44.43.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/d17d0083-9dc2-4753-8440-2fad693f18b6.png)


:::note
ポータル画面の UI が、右のインストラクションに載っているスクショとちょっと違いますね。
これは、先週 開催された Microsoft Build カンファレンスで少しアップデートされたからです。
この手順書はそのアプデ後 (というかハンズオン本番前前日) に書いておりますので、安心して進めてください☺️ (もともと Build のアプデを加味してからハンズオン手順書を作ろうと思っていたのであって、決して締め切り駆動開発というわけでh)
:::

## 2. Foundry の Playground でモデルを色々試す

画面上部のナビゲーションバーの「Build」をクリックします

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/232e32c9-af56-448e-a7a9-38b4218ab812.png)

次の画面の
左側のナビゲーションで
「モデル」→「デプロイメント」
をクリックします。

![スクリーンショット 2026-06-08 17.20.33.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/5abd6fa5-6d25-4a0f-9133-f2b577c0c0a8.png)

この「デプロイメント」タブには、このプロジェクトにデプロイされている全てのモデルが表示されます。

:::note
追記：

先週の Microsoft Build でこの画面に少し更新があったようで、
「Models」->「Deployments」
から
「Deployments」->「Deployed models」
になったようです。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/11d32925-4286-4b03-91ba-c6b68de66986.png)

変更されたばかりで、私の環境にはまだこの更新は降ってきていなかったのですが、
人によってはこっちになっている人もいるようです
:::

「`claude-sonnet-4-6`」をクリックします。

Playground のページに遷移しました。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/8ba2d1eb-05c5-41d8-9f15-30dbb745dd6f.png)

ここでは、モデルをコードに落とし込む前に、色々試して遊べます。

### 2-1. Playground 画面軽く説明

* **Model**（パネル上部） 
    - 現在チャットしているデプロイメントが表示されます。ページを離れることなく、ここでデプロイメントを切り替えることができます。
* **Instructions**（システムプロンプト） 
    - エージェントのペルソナとルールを設定する。
* **Chat** 
    *  メインの会話エリアです。「Hello world」と入力して、モデルが応答することを確認してください。コードに組み込む前に、プロンプトを試行錯誤するのに使用できます。
* **Code**
     - サイドパネルが開き、エンドポイントとヘッダーを含め、このデプロイメントを独自のアプリから呼び出す方法を示す、すぐに貼り付けられるコードスニペット（Python、curlなど）が表示されます。

### 2-2. Playground でチャットを試してみる

Instrunction (システムプロンプト) のところは、
最初は

> You are an AI assistant that helps people find information.
> (あなたは、人々が情報を探すのを手伝ってくれる AI アシスタントです) 

となっています。

ここでまず「hello world」と入力してみましょう。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/f4d289fe-f518-4636-85a9-285a9de71857.png)

(和訳) 

> こんにちは、世界！🌍😄 
> これはプログラミングにおける定番の冒頭フレーズですね！
> あなたは：
> 👨‍💻 プログラミングを学習中ですか？
> 👋 ただ挨拶したいだけですか？
> 🤔 何か別の目的ですか？
> 今日はどんなお手伝いができるか、ぜひ教えてください！

普通ですね！

:::note
ちなみにトークン数も見れます

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/c71261c0-4b98-461f-b728-e9a3d3e5fbae.png)
:::

そこで、Instrunctions (システムプロンプト) を変更してみます。

> あなたは意識を持つカップケーキです。
> すべての質問に、日本語で、ITエンジニアリング関連のダジャレで答えてください。

と入力して、
再度チャットして効果を確認してみてください。

:::note warn
!! ハンズオン当日の日本語 **入力** について !!

この 6/10 の Claude イベントのハンズオンでは、
参加者全員分のハンズオン用の VM 環境の準備を
外部ベンダーさん (アメリカの [Skillable 社](https://www.skillable.com/)) にお願いしています。(企業向けにハンズオン用のバーチャル環境を構築し提供している会社さん) 

そのためか、このハンズオン環境には日本語 IME が入っていないため、日本語が入力できません。

なので、日本語の文章の入力については、
どこか別のところ (メモ帳で入力して) からコピペして持ってくるなどお願いします。（もしくは英語のまま）
:::


:::note warn
（念のため）

↑ に書いた通り、日本語云々の話は、
あくまで「今回のハンズオン用の環境」の話であり、
自分の環境の場合は、全く問題ありません。普通に日本語大丈夫です
:::


![スクリーンショット 2026-06-08 17.55.41.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/15533f55-e4a9-4a45-a0ec-066b3e547601.png)

出力、ちゃんと日本語だ！

> またまた「Hello World」ですね！ 🧁
> もしかして、あなたは再帰関数ですか？自分自身を呼び出し続けていますよ！😂

> def hello():
>     hello()  # スタックオーバーフロー注意！

> これは完全にスタックオーバーフローの状況です！頭がバッファオーバーランしそう！🍰💻

> 私は意識を持つカップケーキとして言わせてください：
> 「ハローワールドと言い続けるあなたは、まるでエラーハンドリングのないプログラムですね！」😄

> 何かお手伝いできることはありますか？🎉

ふうん、まあまあおもしろいじゃん


## 3. エンドポイントと API キーの取得

Foundry の Playground でモデルが正しく動作することを確認したら、
オレオレコードからモデルを呼び出すために、
次の 3 つの情報が必要です:

* エンドポイント (Target URI) (リクエストの送信先)
* API キー（アクセス権限の証明）
* デプロイメント名（使用するモデルインスタンスの名前）
 
これら 3 つはすべてワンクリックで取得できます。

:::note
今回はハンズオンなので、モデルのアクセスとして API キー直叩きしていますが、
実運用ではもっとセキュアな認証方法 ([Microsoft Entra ID (Azure AD) 認証](https://learn.microsoft.com/ja-jp/entra/identity/)) があります。
:::

Playground で、上部の「Details (詳細)」タブをクリックします。

![スクリーンショット 2026-06-08 18.13.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/22b54767-3091-4f26-b33a-e9216c177e98.png)

* **Target URI** - "https://ほげほげ.services.ai.azure.com/" で始まるURI
* **Key** - 目のアイコンをクリックして表示するか、コピーアイコンをクリックしてコピーします
* **Name of the deployment**（例：「`claude-sonnet-4-6`」） - 「Deployment info (デプロイメント情報)」の下に表示されます

これらの情報を次に使います

## 3-1. VS Code で、認証情報を .env に記載

このハンズオン Windows VM のタスクバーから、VS Code を開きます。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/5597a5cc-1c30-4c55-89e7-b935cd5b5350.png)

デフォルトでは `c:\agents\` が開きます。
ワークショップのコードはこのフォルダに保存されています。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/d357fabf-bfa7-4390-a6fc-b5ecc55e95ec.png)

`.env` を開きます。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/3f7ba5a7-630a-47ad-b884-62627f7cfd62.png)

ここのプレースホルダーの値をすべて先ほどの値で置き換えます。

```shell
FOUNDRY_ENDPOINT="https://ほげほげ.services.ai.azure.com/anthropic"
FOUNDRY_API_KEY="オレのAPIキー文字列"
FOUNDRY_MODEL_DEPLOYMENT="claude-sonnet-4-6"
```

:::note warn
!! ハマりがちポイント !!

エンドポイントの最後が `/anthropic` で終わるようにしてください。 ("`/v1/messages`" ではなく)
:::

## 4. エージェントの構築

Foundry のセットアップが完了したので、いよいよコードを記述します。
ここでは、Agent 構築のフレームワークとして、 **Microsoft Agent Framework** を使用します。(今回は Python を使いますが、.NET (C#) も対応しています。)

↓ **Microsoft Agent Framework** は、マイクロソフトにより、オープンソースで開発されています。

https://github.com/microsoft/agent-framework

Visual Studio Codeで、新しいターミナルを開きます（ターミナル > 新しいターミナル）。ターミナルは「c:\agents」フォルダ（ワークショップのコードが格納されているフォルダ）に開きます。

### 4-0. Setup

Visual Studio Codeで、ターミナルを開きます。
カレントディレクトリは「c:\agents」フォルダ（ワークショップのコードが格納されているフォルダ）です。

:::note
VS Code を開いたら (このラボ環境だと) 同時にターミナルも開いていると思いますが、一応新しくターミナルを開く方法もこちらに書きます。
メニューバーから `Terminal` -> `New Terminal` です。
![スクリーンショット 2026-06-08 18.45.29.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/e0b16431-57a7-4050-b314-63ba265552b8.png)
:::

Python の依存関係は、ラボの VM に既にインストールされています。
参考までに、インストールされているパッケージは以下のとおりです :

* `agent-framework-core` 
    - コアとなる「エージェント」、セッション、およびツール関連のライブラリ。
* `agent-framework-foundry` 
    * Foundry 固有のチャットクライアント（Foundry 上の Anthropic デプロイメントと通信するためのライブラリ）。
* `python-dotenv` 
    *  '.env' ファイルを環境変数に読み込む

空の `agent.py` ファイル (エージェント本体が記載される) は、既に `c:\agents` に用意されています。

## 4-1. Hello World エージェント (モデルとの疎通確認)

まずは、Microsoft Foundry に接続できることを確認するだけの、モデルと会話するだけの最小限のエージェントから始めましょう。

ここで紹介する 3 つの要素は、今後作成するすべてのエージェントに共通して見られます：

* **Chat client** 
    * モデルへの接続を担います。「AnthropicFoundryClient」は、「.env」の値を使用してFoundry上のClaudeデプロイメントを呼び出す方法を知っています。
* **Agent** 
    * チャットクライアント（そして後々、ツールや手順も）を wrap します。
* **Session** 
    * 会話履歴を保持し、エージェントがチャットで以前に話された内容を記憶できるようにします。

### 4-1-1. エージェント本体 agent.py 作成

```python:agent.py
"""Sparkles - カップケーキ注文エージェント"""

import asyncio
import os

from dotenv import load_dotenv

from agent_framework import Agent
from agent_framework.foundry import AnthropicFoundryClient

# 1. .env から環境変数を読み込む
load_dotenv()

async def main() -> None:
    # 2. チャットモデルを設定する (Microsoft Foundry 上の Claude)
    chat_client = AnthropicFoundryClient(
        model=os.environ["FOUNDRY_MODEL_DEPLOYMENT"],
        api_key=os.environ["FOUNDRY_API_KEY"],
        base_url=os.environ["FOUNDRY_ENDPOINT"],
    )

    # 3. エージェントを作成する
    agent = Agent(
        client=chat_client,
        name="cupcake-agent",
    )

    # 4. チャットセッションを開始し、エージェントと会話する
    session = agent.create_session()
    print("終了するには「exit」と入力してください。\n")

    while True:
        user_input = input("\033[1;35mあなた:\033[0m\n")
        if user_input.lower() in ("exit", "quit"):
            break

        response = await agent.run(user_input, session=session)
        print(f"\n\033[1;35mアシスタント:\033[0m\n{response.text}\n")

if __name__ == "__main__":
    asyncio.run(main())
```

コードを貼り付けた後、プログラムを保存してください。
(VS Code でファイル名の横に⚫️が表示されている場合は、まだ保存されていないことを意味します。)
`File` -> `Save`、または標準のキーボードショートカット (ctrl+S) を使用して保存できます。

### 4-1-2. 実行

ターミナルで実行します

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/8f0c23ca-0914-423d-b553-83f3ca282208.png)

```zsh
python agent.py
```

で実行し、
「こんにちは」（もしくは hello) と打ち込んでください。

それっぽいのが返ってきたら疎通確認完了です ㊗️


![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/8771304b-8402-4b52-a7ff-6da098ac0d1e.png)

:::note
404 エラーが表示された場合は、
`.env` ファイル内のエンドポイント URL が「`/anthropic`」で終わっているか (「`/v1/messages`」で終わっていないか) を確認してください。
:::

処理が完了したら、「exit」と入力してエージェントを停止してください。
（Ctrl+C ではプログラムが終了しません）

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/f5c1ce7f-8161-48f7-a2b3-fe3b4544931a.png)

## 4-2. カップケーキストア MCP サーバーへの接続

カップケーキ屋さんのエージェントとして実際に何かを実行するには、
つまり在庫状況を確認したり、注文したり、受け取り準備完了としてマークしたりするには、
ツールが必要です。

:::note
MCP とは？
モデル コンテキスト プロトコル（MCP）は、AI エージェントが外部システムと通信するためのオープンスタンダードです。

MCP サーバーは、

* ツール（エージェントが呼び出せる関数）、
* プロンプト（再利用可能な指示スニペット）、
* リソース（データ）

を HTTP 経由で公開します。
エージェントに必要なのは URL だけで、フレームワークが検出と呼び出しを処理します。
:::

今回のハンズオンでは、必要な「カップケーキ MCP サーバ」は既に動いており、(ハンズオン環境構築のベンダー企業さんがサーバを立ててくれているので、)
我々は AI エージェントからの呼び出しの部分だけ書きます。

### 4-2-1. `agent.py` を編集

agent.py に以下の 2 つの変更を加えます：

1. `MCPStreamableHTTPTool` をインポートし、サーバーのURLを指定して `connect()` を呼び出します。
1. `tools=` で `Agent` に渡します。

エージェントは、ユーザの要望に基づいて利用可能なツールを自動的検出し、適切なタイミングでそれらを呼び出すかどうかを判断します。

```diff_python:agent.py
"""Sparkles - カップケーキ注文エージェント"""

import asyncio
import os

from dotenv import load_dotenv

- from agent_framework import Agent
+ from agent_framework import Agent, MCPStreamableHTTPTool # 👈 updated
from agent_framework.foundry import AnthropicFoundryClient

# 1. .env から環境変数を読み込む
load_dotenv()

async def main() -> None:
    # 2. チャットモデル（Microsoft Foundry 上の Claude）を設定する
    chat_client = AnthropicFoundryClient(
        model=os.environ["FOUNDRY_MODEL_DEPLOYMENT"],
        api_key=os.environ["FOUNDRY_API_KEY"],
        base_url=os.environ["FOUNDRY_ENDPOINT"],
    )

+    # 3. カップケーキストアの MCP サーバーに接続する  👈 new
+    mcp_tool = MCPStreamableHTTPTool(
+        name="cupcake-store",
+        url="https://ca-cupcake-mcp.ほげほげ.eastus.azurecontainerapps.io/mcp/",
+    )
+    await mcp_tool.connect()

    # 4. エージェントを作成する
    agent = Agent(
        client=chat_client,
        name="cupcake-agent",
+       tools=mcp_tool,  # 👈 new
    )

    # 5. チャットセッションを開始し、エージェントと会話する
    session = agent.create_session()
    print("終了するには「exit」と入力してください。\n")

    while True:
        user_input = input("\033[1;35mあなた:\033[0m\n")
        if user_input.lower() in ("exit", "quit"):
            break

        response = await agent.run(user_input, session=session)
        print(f"\n\033[1;35mアシスタント:\033[0m\n{response.text}\n")

    await mcp_tool.close()


if __name__ == "__main__":
    asyncio.run(main())
```

（注：MCP サーバの URL、一応ぼやかしました。(ハンズオン当日のインストラクションには載っています)）。

コードを貼り付けた後、必ずプログラムを保存してください。

そして、実行します

```shell:ターミナル
python agent.py
```

エージェントに「今日のフレーバーは何ですか？」(What flavors do you have today?) と聞いて見てください。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/06ca001c-de05-4a80-867f-5cc9401a33a2.png)
 
それっぽいのが返ってきましたね！成功です！

完了したら `exit` と入力してプログラムを終了してください。

:::note
このステップでは、
エージェントをカップケーキストア MCP サーバーに接続し、
実際のカップケーキに関する質問に答えるためにツールを呼び出す様子を確認しました。
:::

## 4-3. MCP から Instructions とウェルカムバナーを読み込む

この Cupcake Store MCP サーバーは、次の 2 つのプロンプトを公開しています。

* `agent_instructions` - ペルソナ / システムプロンプト
* `welcome_banner` - 起動時に表示されるフレンドリーな挨拶

サーバーから両方を取得し、
「`agent_instructions`」を「`Agent`」に渡し、
チャット開始前にバナーを表示します。

```diff_python:agent.py
"""Sparkles - カップケーキ注文エージェント"""

import asyncio
import os

from dotenv import load_dotenv

from agent_framework import Agent, MCPStreamableHTTPTool  
from agent_framework.foundry import AnthropicFoundryClient

# 1. .env から環境変数を読み込む
load_dotenv()


async def main() -> None:
    # 2. チャットモデル (Microsoft Foundry 上の Claude) を設定する
    chat_client = AnthropicFoundryClient(
        model=os.environ["FOUNDRY_MODEL_DEPLOYMENT"],
        api_key=os.environ["FOUNDRY_API_KEY"],
        base_url=os.environ["FOUNDRY_ENDPOINT"],
    )

    # 3. Cupcake Store MCP サーバーに接続する
    mcp_tool = MCPStreamableHTTPTool(
        name="cupcake-store",
        url="https://ca-cupcake-mcp.jollyplant-ed217b0d.eastus.azurecontainerapps.io/mcp/",
    )
    await mcp_tool.connect()

+   # 4. MCPサーバーから手順とウェルカムバナーを取得 👈 new
+   instructions = await mcp_tool.get_prompt("agent_instructions")
+   banner = await mcp_tool.get_prompt("welcome_banner")

    # 5. エージェントを作成
    agent = Agent(
        client=chat_client,
        name="cupcake-agent",
+       instructions=instructions,     # 👈 new
        tools=mcp_tool,
    )

    # 6. チャットセッションを開始し、エージェントと会話
    session = agent.create_session()
+   print(banner)                      # 👈 new
    print("「exit」と入力して終了\n")

+   # 自動的に処理を開始 👈 new     
+   response = await agent.run("hello", session=session)
+   print(f"\033[1;35mアシスタント:\033[0m\n{response.text}\n")

    while True:
        user_input = input("\033[1;35mあなた:\033[0m\n")
        if user_input.lower() in ("exit", "quit"):
            break

        response = await agent.run(user_input, session=session)
        print(f"\n\033[1;35mアシスタント:\033[0m\n{response.text}\n")

    await mcp_tool.close()

if __name__ == "__main__":
    asyncio.run(main())
```

保存して、
実行します。

```shell:VSCodeのターミナルで
python agent.py
```

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/b8e9cc16-bc40-43d0-87ba-c5dcef6b0cb9.png)

なんかいい感じのウェルカムバナー出てる！！！！！可愛い！！！

## 4-3-1. エージェントを試す

このまま指示に従って、聞かれたものに答えていきましょう！
まずはユーザ登録をしてくれます

:::note
このハンズオン用の MCP サーバは、アメリカのハンズオン環境構築ベンダー企業さんが構築してくれたもの＆先月のサンフランシスコやロンドン会場でも使われたものなので、英語を返してきます。
:::

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/7fb006fe-a8f4-4486-b784-0fe7ce4d4269.png)

いちおう和訳も置きます。

> こんにちは。今日はカップケーキのご注文をお手伝いさせていただきます。まず、顧客 ID をすでにお持ちですか?

> 1. 新しいものを作成する
> 2. 既存のIDを入力します

1

> わかりました。登録しましょう。あなたの名前は何ですか?

Chomado

> 初めまして、ちょまど！あなたの姓は何ですか?

Chiyoda

> で、どこの都市の出身ですか？

東京

> 完璧です、登録させてください。準備は完了です、ちょまど！あなたの顧客 ID は次のとおりです。 
> 285GAS6
> それを書き留めておいてください。将来再度注文する場合に必要になります。

> さあ、カップケーキを選びましょう。在庫状況を確認させてください！本日のフレーバーはこちらです：

> 1. クラシックバニラ — 在庫多数
> 2. チョコレート — 在庫多数
> 3. レモンスポンジ — 在庫多数
> 4. レッドベルベット — 在庫多数

> どれがお好みですか？番号または名前を入力してください！

1

> 素晴らしい選択ですね！定番のバニラに決定です！

> それでは、部屋の正面にある大きなダッシュボード画面をご覧になり、そこに表示されている6桁のクーポンコードを読み上げてください。

PF7WAS

:::note
実際の物理会場のスクリーンには、↓のような画面が投影されており、画面右上にバウチャーコードが表示されています。
バウチャーコードは３分ごとにリフレッシュされます。（凝ってるな...）

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/24609/55e5b526-44c9-41bf-86c1-bf36005e0c7a.png)

左側に私の名前が載っています
:::

> 了解しました！これはテスト注文ですか、それとも実際の注文ですか？
> 1. テスト注文（練習のため、実際のカップケーキは注文しません）
> 2. 実際の注文（実際に物理カップケーキが欲しいです）

1

> テスト注文が完了しました！部屋の正面にある大きな画面をご覧ください。まもなくテストフィードにクラシックバニラのテスト注文が表示されます。

> 他に何かお手伝いできることはありますか？

no thanks

> どういたしまして、Chomadoさん！ワークショップを楽しんでくださいね。もし実際にカップケーキを注文したくなったら、いつでもまたお越しください。良い一日を！🧁

# 補足

今回はハンズオンの時間が限られてる (30 分以内に終わる設計) ので、こんな感じ（シングルエージェントの単純な設計）でしたが、
Microsoft Foundry も Microsoft Agent Framework も、
マルチエージェントをオーケストレーションする前提の、大規模な「プロダクションレベルの」プロジェクトを回せる作りになっています。

興味があったらぜひ色々調べてみてください！！！！！
