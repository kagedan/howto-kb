---
id: "2026-06-29-cca-f学習ログ-2基礎編anthropic-academy-のレベル100で土台を固める-01"
title: "【CCA-F学習ログ #2】基礎編：Anthropic Academy のレベル100で土台を固める"
url: "https://zenn.dev/yujmatsu/articles/20260629_cca_foundations_02_basics"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "LLM"]
date_published: "2026-06-29"
date_collected: "2026-06-30"
summary_by: "auto-rss"
query: ""
---

## はじめに

この記事は、Claude Certified Architect – Foundations（CCA-F）合格を目指す学習ログの**第2弾**です。

[#1（概要編）](https://zenn.dev/yujmatsu/articles/20260628_cca_foundations_01_overview)では、CCA-F がどういう試験か・どのコースを使って学ぶかの地図を整理しました。#2 の本記事では、試験ドメインに入る**前の土台**を固めます。具体的には、Anthropic Academy のレベル100コース（基礎）5つのうち「考え方の土台」と「手を動かす土台」に分けて整理し、Claude API の最小実装から順に動くコードを積み上げていきます。

**この記事で扱う範囲のスコープ**

基礎編はレベル100の「土台」に絞ります。tool use・RAG・MCP・Claude Code・agents・extended thinking などの発展トピックは、#3 以降のドメイン別回で扱います。本記事では「次回以降に扱う」と触れる程度にとどめます。

**想定読者**

* Claude / 生成 AI をこれから本格的に触る初学者（用語から丁寧に知りたい）
* Claude API を触り始めたいが、何から手をつけるか・最小の動かし方が分からない方
* CCA-F を見据えて、まず基礎を体系的に固めたい方

**著者の立ち位置**

まだ受験前です。学びながら記録するスタイルで、わからなかった点はそのまま書きます。

## レベル100の全体像：5コースを2層で理解する

Anthropic Academy のレベル100には次の5コースがあります。

| コース名 | 種別 | この記事での位置づけ |
| --- | --- | --- |
| AI Fluency: Framework & Foundations | 概念（コードなし） | 考え方の土台（①） |
| Claude 101 | 製品の使い方 | 考え方の土台（①） |
| Building with the Claude API | 技術（Python） | 手を動かす土台（②）の主軸 |
| Claude with Amazon Bedrock | 技術（Python） | 手を動かす土台（②）の AWS 経路 |
| Claude with Google Cloud's Vertex AI | 技術（Python） | 手を動かす土台（②）の GCP 経路 |

この5コースを「考え方の土台」と「手を動かす土台」の2層に整理すると、学習の流れが見えやすくなります。

**考え方の土台（① AI Fluency / Claude 101）**：生成 AI とは何か・Claude で何ができるか・うまく使うための思考パターン。コードは不要。エンジニアでなくても学べます。

**手を動かす土台（② Building with the Claude API など）**：Python でコードを書きながら Claude API を動かす実践。「最小リクエストから始めて、少しずつ機能を加えていく」構成になっています。

Bedrock / Vertex AI コースは、Claude API コースと内容がほぼ共通で、AWS / GCP それぞれの認証とセットアップ手順が加わる形です（詳しくは後述の「3つのアクセス経路」セクションで比較します）。

tool use / RAG / MCP / エージェント構築などの発展内容は、これらのコースにも含まれますが、レベル200・300の範囲に対応します。本記事では**基礎（土台）部分のみ**を扱い、発展トピックは #3 以降に回します。

![図1: レベル100コースを2層で地図化](https://static.zenn.studio/user-upload/deployed-images/50e55a059efd99f715cb9d21.png?sha=851ad5c6eafeea46673b57b2a300f2d17696fd17)  
*図1: レベル100の5コースを「考え方の土台」と「手を動かす土台」の2層で整理。基礎編の対象範囲（塗りつぶし）と #3 以降に送る発展トピック（破線）を区別している。*

## ① 考え方の土台

### AI Fluency: Framework & Foundations

AI Fluency は、「AI と効果的・効率的・倫理的・安全に協働するための土台」を教えるコースです。コードは一切出てきません。エンジニアから非エンジニアまでを対象にしています。

コース自体は「全レベル向け・修了証あり」と案内されており、AI の使い方に関する考え方の枠組みを学ぶことに特化しています。

#### 生成 AI の超基礎

生成 AI は「テキスト（あるいは画像・音声）を入力すると、それに続く内容を確率的に生成するモデル」です。

もう少し噛み砕くと、こうです。

1. **プロンプト（prompt）を入力する**：ユーザーが書いたテキスト（指示・質問・文章の冒頭など）。AI への入力全般をこう呼びます。
2. **モデルが次のトークンを予測する**：トークン（token）とは、モデルが扱うテキストの最小単位です。単語を細かく分割したものと考えてください（例えば「こんにちは」は複数のトークンに分割されます）。
3. **確率的に出力が生成される**：「次に来る可能性が最も高い単語は何か？」を繰り返し予測して文章を組み立てます。そのため、同じプロンプトを入れても毎回まったく同じ結果にはなりません。

生成 AI が**得意なこと**：文章の要約・翻訳・言い換え・コードの説明・アイデア出し・質疑応答など、テキストを入力として受け取り、テキストを返すタスク全般。

生成 AI の**限界**：学習データの範囲外の最新情報を知らない（学習カットオフ以降の出来事には対応できない）。数値計算や厳密な事実確認は誤る場合がある（「ハルシネーション」と呼ばれる）。長い入力を完全に記憶するわけではない（詳細はコンテキストウィンドウの話として #3 以降で扱います）。

![図2: 生成AIの超概要](https://static.zenn.studio/user-upload/deployed-images/fb507eee9c936d635b424019.png?sha=c81b35336b2d4ef05e15686a12e4cbd8ba1eba51)  
*図2: プロンプト入力→モデルが確率的に続きを生成→出力、の流れ。右側に「できること」と「限界」の注記。*

#### 4D フレームワーク

AI Fluency コースの中核にある「4D フレームワーク」は、AI と協働するための思考の型です。4つの D から成ります。

**Delegation（委譲）**：どのタスクを AI に任せるか・任せないかを判断すること。

全てを AI に丸投げするのも、逆に何も任せないのも、どちらも非効率です。「このタスクは AI が得意か？」「人間が確認する必要があるか？」を考えて仕事を振り分けます。

日常の例：「議事録の文字起こしは AI に任せる。最終的な内容確認は自分でする。」

**Description（記述）**：AI に明確・具体的に指示を書くこと。

生成 AI は文脈を読む能力がある一方で、曖昧な指示からは曖昧な結果しか返ってきません。「何を・どういう形式で・誰向けに・どの程度の長さで」を明確に伝えることが、良い出力への近道です。

日常の例：「メールを書いて」より「社外の取引先に送る、打ち合わせの日程調整メール（200字以内）を書いて」のほうが使える結果が返ってくる。

**Discernment（見極め）**：AI が出力した内容を批判的に評価すること。

生成 AI は事実でないことを自信を持って述べることがあります。特に数値・日付・固有名詞などは要確認です。出力をそのまま使わず、正確か・目的に合っているか・偏りがないかを自分で判断する習慣が必要です。

日常の例：「コードを生成してもらったが、実際に動かして動作確認する。そのまま本番にデプロイしない。」

**Diligence（誠実な検証・責任ある活用）**：倫理的・安全な使い方を守ること。

個人情報・機密情報をプロンプトに書き込まない。生成された内容を検証せずに公表しない。AI ツールの利用ポリシーに従う。こうした「誠実に使う」姿勢のことです。

日常の例：「顧客データが含まれる社内文書を外部の AI ツールに貼り付けない。」

![図3: 4D フレームワーク図](https://static.zenn.studio/user-upload/deployed-images/6dabbe63a1c05114b97b92a9.png?sha=dfe9ba6393698d6e00714de32b3cc2e4e395ed02)  
*図3: 4D フレームワーク。Delegation→Description→Discernment→Diligence の4つと、Description–Discernment を繰り返すループ。*

#### Description–Discernment ループ

4D の中でも「書いて→見極めて→直す」を繰り返す **Description–Discernment ループ**は、日常の AI 活用でよく回るサイクルです。

1. **Description**：プロンプトを書いて AI に送る
2. **Discernment**：出力を評価する（使えるか？ 正確か？ 修正が必要か？）
3. 修正が必要なら **Description** を書き直して再送する

このループを意識すると、最初のプロンプトが完璧でなくても「改善していく」プロセスとして受け入れやすくなります。

### Claude 101

Claude 101 は「Claude を使って仕事を進めるための基本機能とコア概念を学ぶ」コースです。製品の使い方が中心で、コードよりも Claude.ai の機能解説が多いのが特徴です（修了証あり）。

ここでは CCA-F の土台として特に重要な概念・機能を整理します。

**Claudeとは何か**

Claude は Anthropic が開発した AI アシスタントです。文章の生成・翻訳・要約・コードの作成・質疑応答など、多様なテキスト生成タスクに対応しています。

**会話の基本（チャット）**

Claude.ai（Web インターフェース）やデスクトップアプリから、テキストでやり取りするのが基本的な使い方です。Claude はチャット上の会話履歴を参照しながら応答するため、前の発言を踏まえた続きの質問も自然に処理できます。

**Projects（プロジェクト）**

一つのテーマや用途に関連する会話・ファイル・設定をひとまとめにして管理できる機能です。「特定のプロジェクト用にドキュメントを参照させながら質問したい」という場面で使います。例えば、設計書や仕様書をアップロードして「このドキュメントを踏まえて〜を説明して」という使い方ができます。

**Artifacts（アーティファクト）**

コード・文書・HTML など、Claude が生成した成果物を専用のウィンドウで表示・コピー・編集できる機能です。生成されたコードや文書をそのまま使いやすい形で受け取れます。

**Skills（スキル）**

Claude.ai でよく使う操作や情報をカスタマイズして保存できる機能です。繰り返し使いたい指示や、特定の文体・書き方のルールを登録しておくことで、毎回プロンプトに書かなくて済むようになります（機能名や UI はロールアウト段階で変わることがあるため、最新の名称・提供状況は公式サイトで確認してください）。

**ツール接続**

Claude.ai ではウェブ検索・ファイルアップロードなどのツールを接続できます。ウェブ検索を有効にすると、最新情報を参照した回答が得られます（Research mode と合わせて後述）。

**Research mode**

複数の情報源を調査して詳細なレポートを作成する機能です。複数ステップで情報を収集・整理するため、単発の質問よりも深い調査に向いています（2026年6月時点での提供状況は公式で確認してください）。

**エンタープライズ検索**

Claude for Work / Claude Enterprise で利用できる機能です。社内の文書・ナレッジベースを Claude が横断検索して回答を返せます（詳細は公式サイトで要確認）。

**役割別ユースケース**

Claude 101 では「営業向け」「エンジニア向け」「マーケター向け」など、役割別の使い方も紹介されています。CCA-F の試験はエンジニア・ソリューションアーキテクト向けなので、本連載はコードを動かす方向に比重を置きます。

**良い結果を得るコツ**

Claude 101 で繰り返し強調されている点として、「明確で具体的な指示を書く」があります。これは 4D フレームワークの Description と同じ方向性です。後の「プロンプトの基本4テクニック」セクションで具体的に解説します。

![図4: Claude 101 でできることマップ](https://static.zenn.studio/user-upload/deployed-images/a09c5174422115e59bebccb0.png?sha=0683634f01de9723905a8f3d44f919c3649849b3)  
*図4: Claude 101 で紹介されている主な機能の全体像。中央に「Claude」を置き、会話・Projects・Artifacts・Skills・ツール接続・Research mode が枝葉で広がる。*

## ② 手を動かす土台：Claude API の基礎

ここからは実際にコードを動かします。

**API（Application Programming Interface）とは**：アプリケーションが外部のサービスや機能を呼び出すための「窓口」です。Claude API を使うと、自分で作るアプリやスクリプトから Claude の機能をプログラムで呼び出せます。

メインで参照するコースは[「Building with the Claude API」](https://anthropic.skilljar.com/claude-with-the-anthropic-api)です。

### 準備：API キー取得・環境変数設定・インストール

Claude API を使うには、**API キー**が必要です。

**環境変数の設定**

環境変数（environment variable）とは、OS のレベルで設定できる「名前＝値」の組み合わせです。プログラムはコードを変更せずにここから設定値を読み取れます。API キーのように「コードに書きたくないが、プログラムから参照したい値」を管理するのに使います。

```
# macOS / Linux（ターミナルで実行）
export ANTHROPIC_API_KEY="sk-ant-ここに自分のキーを入れる"
```

```
# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-ここに自分のキーを入れる"
```

これはターミナルを閉じると消えます。永続的に設定したい場合は `.bashrc` / `.zshrc`（macOS/Linux）や Windows の「システムの詳細設定」→「環境変数」に追加します。

**SDK のインストール**

SDK（Software Development Kit）は、API を Python から使いやすくするライブラリです。

インストール後、Python から `import anthropic` と書いてエラーが出なければ準備完了です。

（補足: Python 3.8 以上が前提です。ターミナルで `python --version`（環境により `python3 --version`）を実行し、3.8 以上が表示されればOK。プロジェクトごとに仮想環境（venv）を作っておくと、パッケージが他のプロジェクトと競合しにくくなります。）

### 最小リクエスト

「最小リクエスト」とは、Claude API を動かすために最低限必要なコードです。これが動けば、あとはパラメータを足して機能を広げていきます。

```
import anthropic  # anthropic SDK をインポートする

# クライアントを作成する。
# 引数なしの場合、自動で環境変数 ANTHROPIC_API_KEY を読み取る。
client = anthropic.Anthropic()

# messages.create でリクエストを送る。
# model: どのモデルを使うか（モデル ID を文字列で指定）
# max_tokens: 出力の上限トークン数（必須パラメータ）
# messages: 会話のやり取りをリスト形式で渡す
message = client.messages.create(
    model="claude-sonnet-4-6",   # モデル ID（上の注記参照）
    max_tokens=1024,
    messages=[
        {
            "role": "user",      # 発言者（"user" または "assistant"）
            "content": "日本の首都はどこですか？"  # 実際のテキスト内容
        }
    ]
)

# レスポンスはオブジェクトで返ってくる。
# テキスト本文は content リストの先頭要素（type="text"）の .text に入っている。
print(message.content[0].text)
```

**レスポンスの構造について**

`messages.create` が返す `message` オブジェクトには複数のフィールドがあります。主なものを整理します。

| フィールド | 中身 |
| --- | --- |
| `message.content` | 出力内容のリスト（通常は1要素で、`.type="text"` の場合テキストが入る） |
| `message.content[0].text` | テキスト出力の文字列 |
| `message.model` | 実際に使われたモデル ID |
| `message.usage` | 入力・出力それぞれのトークン数（課金に関係） |
| `message.stop_reason` | 出力が終わった理由（通常の完了は `"end_turn"`。ほかに `"max_tokens"`（上限到達）などがある） |

`content` がリスト構造なのは、テキスト以外の出力（後の回で扱う tool\_use など）も同じリストに入る設計のためです。今は「テキストは `content[0].text` で取り出す」とだけ覚えれば十分です。

![図5: Claude API リクエスト→レスポンスの流れ](https://static.zenn.studio/user-upload/deployed-images/abca2cce78471b2b34c2b576.png?sha=d3c82441c5f19d279044883b8d4d6a1ecccdce11)  
*図5: messages[{role, content}] を API に送り、レスポンスの content[0].text にテキストが返ってくる流れ。*

### マルチターン会話

ChatGPT や Claude.ai のように「前の発言を踏まえてやり取りする」のがマルチターン会話です。

Claude API は **ステートレス（stateless）** です。ステートレスとは「サーバー側が会話の状態を持たない」という意味です。毎回のリクエストは独立していて、前のリクエストの内容を API 側は覚えていません。

そのため、**会話の履歴をアプリ側でリストに積んで毎回渡す**必要があります。

```
import anthropic

client = anthropic.Anthropic()

# 会話履歴を保持するリスト
conversation_history = []

def chat(user_message: str) -> str:
    # ユーザーの発言を履歴に追加する
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    # 全履歴を含めてリクエストを送る
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=conversation_history  # ← 毎回全履歴を渡す
    )

    assistant_message = response.content[0].text

    # Claude の応答も履歴に追加する（次のターンで渡すため）
    conversation_history.append({
        "role": "assistant",
        "content": assistant_message
    })

    return assistant_message

# 使い方
print(chat("私の名前は太郎です。"))
print(chat("私の名前を覚えていますか？"))  # 前の発言を踏まえた応答になる
```

### system prompt（システムプロンプト）

system prompt は「Claude にどういう役割や制約を与えるか」を事前に指示する特別な入力です。会話が始まる前に設定し、その後の全てのやり取りに影響を与えます。

**なぜ必要か**：デフォルトの Claude は汎用的に動きます。特定の業務・用途向けにカスタマイズするには、「この会話では〜に徹してください」という事前定義が必要です。

```
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="あなたは日本語で回答する、丁寧なカスタマーサポート担当者です。"
           "製品以外の話題には答えず、「対象外の質問です」と返してください。",
    # ↑ system キーに文字列で渡す。messages とは別のキー。
    messages=[
        {"role": "user", "content": "返品の手続きを教えてください。"}
    ]
)

print(response.content[0].text)
```

system prompt で設定できること（代表的なもの）：

* Claude の役割・ペルソナ（「〜として振る舞ってください」）
* 出力の形式・言語（「日本語で・箇条書きで・〜文字以内で」）
* 行動の制約（「特定のトピック以外は答えない」）
* 前提知識の注入（「以下はプロジェクトの概要です：〜」）

### temperature と streaming

#### temperature（温度パラメータ）

temperature は「出力のランダム性（ばらつき）を調整するパラメータ」です。0〜1 の範囲で指定し、省略時のデフォルトは 1.0（ランダム性が高い側）です。正確な範囲・既定値は公式ドキュメントで確認してください（※一部の最新モデルでは temperature を指定できない場合があります。モデルごとの対応は公式で確認してください）。

* **temperature が低い（0 に近い）**：確率が最も高い次の単語を優先的に選ぶため、出力が安定・一貫する。ファクト確認・コード生成・データ抽出など「正確さが大事なタスク」に向く。
* **temperature が高い（1 に近い）**：確率が低い選択肢も選ばれやすくなるため、出力が多様・創造的になる。ブレインストーミング・物語生成・アイデア出しなど「多様性が欲しいタスク」に向く。

```
import anthropic

client = anthropic.Anthropic()

# temperature を低く設定した例（ファクト系の質問）
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=256,
    temperature=0.2,            # 0〜1 の浮動小数点で指定
    messages=[
        {"role": "user", "content": "東京の緯度を教えてください。"}
    ]
)
print(response.content[0].text)
```

#### streaming（ストリーミング）

通常の `messages.create` は、生成が完了してから全テキストを一度に返します。そのため長い応答は「待ち時間 → 全部一気に表示」になります。

streaming を使うと、生成されたテキストを**1トークンずつリアルタイムで受け取り**ながら表示できます（ユーザー向けのチャット UI のように逐次表示する感覚です）。コードの `with` 構文（コンテキストマネージャと呼ばれる Python の仕組み）は、ストリームの開始・終了処理を自動で管理するための書き方です。

```
import anthropic

client = anthropic.Anthropic()

# with 構文でストリーミングを使う（最小例）
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=256,
    messages=[
        {"role": "user", "content": "生成AIについて3文で説明してください。"}
    ]
) as stream:
    # text_stream はテキストが生成されるたびに1チャンクずつ yield するイテレータ
    for text in stream.text_stream:
        print(text, end="", flush=True)  # flush=True: バッファ（出力の一時保管）を即時書き出す。無いとリアルタイム表示されないことがある

print()  # 最後に改行
```

streaming は Web アプリや CLI ツールで「すぐに最初の文字が表示される」UX を作るときに使います。バックエンド処理や自動化スクリプトで結果を一括取得するだけなら通常の `messages.create` で十分です。

### 構造化出力（structured output）

構造化出力とは「あらかじめ決めたスキーマ（型や形式）に沿ったデータとして出力を受け取ること」です。

通常の Claude の出力は自由なテキストです。「JSON 形式で返してください」とプロンプトに書いても、余分な説明文が付いたり、フォーマットがずれたりすることがあります。構造化出力は、これを機械処理しやすい形に安定させるための仕組みです。

**なぜ必要か**：アプリから Claude の出力を受け取って、自分でパースして次の処理に使いたい場面は多くあります。例えば「ユーザーのメッセージから商品名・数量・要望を抽出して注文オブジェクトにする」などです。この場合、出力が決まった構造でないと処理が安定しません。

**実現方法（tool\_use ベース）**

Anthropic の Claude API で構造化出力を実現する方法の1つが、 **tool\_use（ツール呼び出し）** の仕組みを使うアプローチです。Claude に「このスキーマを持つツールを必ず呼び出す」よう指定すると、スキーマに沿った JSON を返させられます。なお **JSON Schema** とは、JSON データの構造（どんなフィールドがあり・型は何か・どれが必須か）を記述する仕様で、下のコードの `input_schema` 内の `type` / `properties` / `required` がそれにあたります。tool use 自体の詳しい仕組み（複数ツール・エラー処理など）は #3 以降で扱い、ここでは構造化出力の入口として最小例だけを示します。

```
import anthropic
import json

client = anthropic.Anthropic()

# tool として「抽出結果を格納するスキーマ」を定義する
# Claude に「この tool を必ず呼び出せ」と指示することで構造化出力を強制する
extraction_tool = {
    "name": "extract_contact",
    "description": "テキストから連絡先情報を抽出する",
    "input_schema": {
        "type": "object",
        "properties": {
            "name":  {"type": "string", "description": "氏名"},
            "email": {"type": "string", "description": "メールアドレス"},
            "phone": {"type": "string", "description": "電話番号"}
        },
        "required": ["name", "email"]  # 必須フィールドを指定
    }
}

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=256,
    tools=[extraction_tool],    # 使用可能な tool を渡す
    tool_choice={"type": "tool", "name": "extract_contact"},  # この tool を必ず使うよう強制
    messages=[{
        "role": "user",
        "content": "田中花子さん（hanako@example.com, 090-1234-5678）から連絡がありました。"
    }]
)

# tool_use ブロックを探して input（JSON）を取り出す
for block in response.content:
    if block.type == "tool_use":
        extracted = block.input      # dict 形式で構造化されたデータが入っている
        print(json.dumps(extracted, ensure_ascii=False, indent=2))
```

実行すると、`extracted` は `{"name": "田中花子", "email": "hanako@example.com", "phone": "090-1234-5678"}` のような辞書形式になります。テキストのパースが不要で、以降の処理が安定します（tool use の詳しい仕組みは #3 以降で扱います）。

### 評価（eval）の基礎

評価（eval）とは「作ったプロンプトや設定が本当に期待通りに動くかを体系的に確認するプロセス」です。

**なぜ必要か**：プロンプトを1つ手作業で試して「良さそう」と判断するのは危険です。入力パターンが変わった時・モデルのバージョンが変わった時に動作が変わるかもしれません。評価の仕組みを持つことで、変更前後の品質を比較したり、改善が本当に改善かを確認できたりします。

**典型的なワークフロー**

1. **テストデータを用意する**：入力と期待する出力のペアをいくつか準備する（10〜50件程度から始めるのが現実的）
2. **プロンプト/設定で実行する**：用意した入力を Claude に通し、出力を記録する
3. **採点する**：出力を評価する。主な手法は2つ。
   * **model-based（モデル採点）**：Claude や別の LLM に「この出力は期待値に合っているか？」を判断させる
   * **code-based（コード採点）**：正規表現・完全一致・JSONのスキーマチェックなど、プログラムで自動判断する
4. **結果を分析して改善する**：スコアが低いケースを見て、プロンプトを修正する

```
import anthropic

client = anthropic.Anthropic()

# ① テストデータ（入力と期待する出力のペア）
test_cases = [
    {"input": "日本の首都は？",    "expected": "東京"},
    {"input": "1 + 1 は？",       "expected": "2"},
    {"input": "日本語で「こんにちは」は英語で？", "expected": "Hello"},
]

# ② 実行して結果を収集する
results = []
for case in test_cases:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=64,
        messages=[{"role": "user", "content": case["input"]}]
    )
    output = response.content[0].text.strip()
    results.append({
        "input":    case["input"],
        "expected": case["expected"],
        "actual":   output,
    })

# ③ code-based 採点（期待値が出力に含まれるかで判定する簡易版）
for r in results:
    passed = r["expected"].lower() in r["actual"].lower()
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] 入力: {r['input']!r:30s} 期待: {r['expected']!r:10s} 実際: {r['actual']!r}")
```

これは最も簡易な eval です。実際には「期待値に含まれるかどうか」ではなく、意味的な正確さ・安全性・スタイルなど複数の観点で評価します。実務レベルの eval 設計は #3 以降の「プロンプト・構造化出力」ドメインで扱います。

![図6: 評価（eval）ワークフロー](https://static.zenn.studio/user-upload/deployed-images/2c9b90743b2870c670214fbd.png?sha=907bcea613018d7f2183e27a617c9fc64cb4faef)  
*図6: テストデータ → 実行 → model-based / code-based 採点 → 改善のループ。*

### プロンプトの基本4テクニック

Building with the Claude API コースで繰り返し強調されるプロンプト設計の基本を整理します。これは AI Fluency の「Description」とも重なる内容です。

**① 明確に（Be Clear）**：何をしてほしいかを一文でわかるように書く。曖昧さを残さない。

**② 具体的に（Be Specific）**：文字数・形式・ターゲット読者・トーン・例外処理など、具体的な条件を添える。

**③ XML タグで構造化する（Use XML Tags）**：複数の情報をプロンプトに含める場合、XML タグで区切ると Claude が解析しやすくなります。

**④ 例を示す（Give Examples）**：「こういう入力にはこういう出力を返してほしい」という入出力例（Few-shot examples）を1〜3件添えると、期待する形式・スタイルを伝えやすくなります。

Before / After 例で比較します。

```
---- Before（あいまいなプロンプト）----
ユーザー:
「要約して。」

---- After（改善したプロンプト）----
ユーザー:
以下の記事を、日本語で3行以内に要約してください。
対象読者はエンジニアです。専門用語はそのまま使ってください。

<article>
（ここに記事本文を貼る）
</article>

出力形式:
- 箇条書き3点
- 各点は40文字以内

例:
- 〇〇の課題が△△によって解決できる
- 実装には□□が必要で、導入コストは低い
- ユースケースは××と◇◇に限定される
```

4つ全てを毎回盛り込む必要はありません。「うまくいかないとき」に1つずつ改善の軸として使うのが実践的です。

![図7: プロンプト基本4テクニック](https://static.zenn.studio/user-upload/deployed-images/1e13e6542667925df1d8dccb.png?sha=e0f18dd43a767a6ee3a606151fb4e4e306468e69)  
*図7: 明確・具体・XML 構造・例示の4つの軸。各枠に短い一言例を添えた4分割レイアウト。*

## ③ 3つのアクセス経路

Claude API にアクセスする経路は主に3つあります。基礎的な Claude 操作（プロンプト・messages のやり取り・パラメータ調整）は全ての経路で共通です。違いは「認証方法」と「実行環境（どのクラウドで動かすか）」です。

| 経路 | 特徴 | 認証 | 向いているケース |
| --- | --- | --- | --- |
| 直接 API（Anthropic） | Anthropic が提供する API に直接アクセス | `ANTHROPIC_API_KEY` | 手軽に試したい・クラウド依存を最小にしたい |
| Amazon Bedrock | AWS のマネージドサービスを経由 | AWS IAM ロール / 認証情報 | AWS インフラで既に構築しているチーム |
| Google Cloud Vertex AI | GCP のマネージドサービスを経由 | Google Cloud サービスアカウント | GCP インフラで既に構築しているチーム |

**「中身は共通、認証と環境が違う」** が最大のポイントです。

Anthropic の `anthropic` SDK を使った最小リクエストのコードは、API キーの設定さえ変えれば直接 API として動きます。Bedrock 経由にする場合は `anthropic.AnthropicBedrock()` クライアントを使い、Vertex AI 経由では `anthropic.AnthropicVertex()` を使います。基本的な `messages.create` の構造や `system` / `messages` / `temperature` などのパラメータは共通です。

本記事のコード例は全て直接 API（`ANTHROPIC_API_KEY`）で動かせます。チームや本番環境で Bedrock / Vertex AI を使う場合は、それぞれのコースで追加のセットアップ手順を確認してください。

![図8: 3アクセス経路の比較](https://static.zenn.studio/user-upload/deployed-images/b563727994b359b0273bbd32.png?sha=8dabf7d2a7310535e62f925221b061e7c5d447c0)  
*図8: 直接 API / Amazon Bedrock / Google Cloud Vertex AI の3経路。共通部分（Claude 操作・プロンプト）と相違部分（認証・実行環境）を色分けして整理。*

## 初学者のハマりどころ

実際に試した際に詰まりやすいポイントをまとめます。

**① API キーが読み取れない**

```
AuthenticationError: Could not automatically determine credentials...
```

よくある原因：

* 環境変数 `ANTHROPIC_API_KEY` のスペルミス（大文字小文字の違い含む）
* 設定したターミナルと別のターミナルを開いていて環境変数が引き継がれていない（`export` は現在のシェルセッションにのみ有効）
* `.env` ファイルを使っているが `python-dotenv` を読み込んでいない

確認方法：Python の中で `import os; print(os.environ.get("ANTHROPIC_API_KEY"))` を実行して `None` でなければ設定できています。

**② 課金・トークンの概念**

Claude API の利用料金は「入力トークン数」と「出力トークン数」に基づきます。日本語の1文字は英語の1文字より多くのトークンを消費することが多いです（概ね1文字 = 1〜2トークン程度。正確な値はモデル・文章による）。

`message.usage.input_tokens` と `message.usage.output_tokens` で確認できます。意図せず長い入力を繰り返すと費用が積み上がるので、開発中は `max_tokens` を小さめにしておくと安全です。最新の料金は[公式](https://www.anthropic.com/pricing)で確認してください。

**③ モデル ID の指定ミス**

モデル ID（例: `claude-sonnet-4-6`）を間違えるとエラーになります。本記事では `claude-sonnet-4-6` を例として使っていますが、**利用可能なモデル ID は時期によって変わります。** 実行前に[公式ドキュメント](https://docs.anthropic.com/ja/docs/about-claude/models)で最新の ID を確認してください。

**④ temperature の「完全に同じにならない」誤解**

「temperature=0 にすれば常に同じ出力になる」と思いがちですが、実際には出力が揺れることがあります（サーバー側の実装や並列処理の影響などが絡みます）。「安定する傾向がある」と理解しておくと良いです。

**⑤ 日本語の扱い**

Claude は日本語に対応しており、日本語で質問すれば日本語で返ってきます。system prompt で「日本語で回答してください」と明示するとより安定します。プロンプト設計で XML タグを使う場合も、タグ名は英語・内容は日本語、という形が一般的です（例: `<article>日本語の文章</article>`）。

**⑥ ストリーミングでの `flush=True` 忘れ**

streaming で `print(text, end="", flush=True)` と書かないと、バッファリングの影響でリアルタイムに表示されないことがあります（特に出力をファイルにリダイレクトしている場合など）。

## 理解度トラッカー（基礎編後）

基礎編を終えて、各ドメインの理解度を更新します。

| ドメイン | 理解度（/5） | #1→#2 | コメント |
| --- | --- | --- | --- |
| Agentic Architecture & Orchestration | 2 | → 2 | 基礎 API の理解は進んだが、エージェント設計は未学習のまま |
| Claude Code Configuration & Workflows | 3 | → 3 | 変化なし（#3 で扱う） |
| Prompt Engineering & Structured Output | 3 | → 4 | 基本4テクニック・構造化出力の入口を手を動かして確認した |
| Tool Design & MCP Integration | 2 | → 2 | tool\_use の構造に触れた程度。MCP は #3 以降 |
| Context Management & Reliability | 2 | → 2 | マルチターンの履歴管理を理解。本格的なコンテキスト管理は #3 以降 |

**基礎編で底上げできた点**：プロンプト基本・API の最小実装・system prompt・temperature の傾向・streaming の使い方・構造化出力の入口・eval の典型ワークフロー。

**まだ曖昧な点（正直に残す）**：

* `max_tokens` の適切な設定基準（どのタスクにどれくらい必要か）
* temperature の「内部的なランダム性」の詳細な仕組み
* tool\_use を使った構造化出力と、公式の structured output 機能の最新の使い分け（APIの仕様変更を要確認）
* eval のスコアリング設計（model-based でどういうプロンプトを書くのが適切か）

## まとめ

この記事で扱った内容を整理します。

**考え方の土台（① AI Fluency / Claude 101）**

* 生成 AI は確率的にテキストを生成する仕組み。できることと限界を把握する。
* 4D フレームワーク（Delegation / Description / Discernment / Diligence）は AI と協働するための思考の型。
* Description–Discernment のループを回して出力を改善する。
* Claude 101 では Projects・Artifacts・Skills・ツール接続・Research mode など、Claude の主要機能を学べる。

**手を動かす土台（② Claude API の基礎）**

* `ANTHROPIC_API_KEY` を環境変数に設定し、`pip install anthropic` で準備完了。
* 最小リクエストは `client.messages.create()` に `model・max_tokens・messages` を渡すだけ。
* マルチターン会話はアプリ側で履歴リストを積んで毎回渡す。
* system prompt で役割・制約・形式を事前定義できる。
* temperature で出力の安定度を調整。streaming で逐次出力。
* 構造化出力は tool\_use の仕組みを使って安定した JSON を受け取れる。
* eval（評価）は「テストデータ → 実行 → 採点 → 改善」のループが基本。
* プロンプトの基本4テクニック（明確・具体・XML 構造・例示）でアウトプット品質を改善する。

**3つのアクセス経路（③）**

* 直接 API / Amazon Bedrock / Google Cloud Vertex AI の3経路は、Claude 操作の中身は共通で、認証・実行環境が異なる。

**今すぐ手を動かすなら**：`pip install anthropic` → APIキー取得 → 「最小リクエスト」のコードを実行、の順で試してみてください。これが動けば、基礎編の実装環境は完成です。

## 次回予告

**#3「ドメイン① Agentic Architecture & Orchestration — エージェント設計の土台を固める」**

参照する Academy コース: Building with the Claude API（後半）、その他エージェント関連コース

次回は tool use の詳細・複数ステップの処理・オーケストレーションの設計パターンなど、CCA-F で最大の出題比率（27%）を持つドメインに取り組みます。基礎編で触れた「tool\_use の最小構造」を起点に、実際のエージェント設計へと発展させていきます。

## 参考リンク

**Anthropic Academy（レベル100コース）**

**公式ドキュメント・コンソール**

**この連載**
