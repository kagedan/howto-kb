---
id: "2026-06-04-2つのaiキャラに価格交渉させてみたヒョウ柄オカンvs頑固オオカミの爆笑バトルclaudecodeg-01"
title: "2つのAIキャラに価格交渉させてみた！ヒョウ柄オカン🐆vs頑固オオカミ🐺の爆笑バトル【ClaudeCode×Gemini】"
url: "https://zenn.dev/miki_mini/articles/686981ffeff51b"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "Gemini", "Python", "JavaScript"]
date_published: "2026-06-04"
date_collected: "2026-06-05"
summary_by: "auto-rss"
query: ""
---

![アイキャッチ](https://static.zenn.studio/user-upload/2457b83deaae-20260603.png)

美容系勤務独学初心者マリー・アントワネット系エンジニア目指してます！

今回はAIが価格交渉してくれる機能が無いなら自分で作ればいいじゃない👸🍰です。

読了時間の目安：約8〜10分

!

**3行まとめ**

* **Gemini 2.5 Flash** を使って「ヒョウ柄オカン🐆」と「頑固オオカミ🐺」が値切り交渉するAIシミュレーターを作りました！
* Gemini が JSON の中に生の `"` を出力してしまうバグを、**自前の `_repair_json()` 関数**で自動修正する方法を解説します。
* 将来は AI エージェント同士が交渉する新経済圏が来るかも？という未来妄想も込みです🔮

## こんな人に読んでほしい

* Gemini API（Vertex AI）を使ってみたい人
* FastAPI で AI アプリを作ってみたい Python 初心者
* AI エージェント・マルチエージェントシステムに興味がある人
* **Gemini の JSON 出力でパースエラーに悩んでいる人**（この記事で解決できます！）
* ただただ大阪のおばちゃん AI と頑固オオカミ AI の交渉を見たい人🐆🐺

## レベル別インデックス

| レベル | おすすめジャンプ先 |
| --- | --- |
| 🔰 まずはデモを触ってみたい | 第7章：実際の交渉ログ |
| 🌱 仕組みを理解したい | 第2章：システム全体のアーキテクチャ |
| 🔥 コードを実装したい | 第4章：バックエンド実装 |
| 😱 Gemini JSON エラーで困っている | 第5章：最大の難関：Gemini JSON地獄との戦い |

## 前提条件

* Python 3.10 以上
* Google Cloud プロジェクト（Vertex AI API が有効なもの）
* FastAPI の基本的な知識があると読みやすいです
* ローカル実行の場合は `gcloud auth application-default login` または `GOOGLE_APPLICATION_CREDENTIALS` の設定が必要です

## この記事でわかること

* Gemini 2.5 Flash の `response_schema` を使って**構造化 JSON を強制出力**させる方法
* AI に「キャラクター」を演じさせる**プロンプトエンジニアリング**の実践
* Gemini が JSON に `"` を混入させるバグの**根本原因と自動修正の実装**
* FastAPI + Vertex AI を組み合わせたバックエンドの作り方
* チャット UI のタイピングアニメーション（Vanilla JS）の実装

---

## 1. はじめに 🐆

去年から **Gemini グラス（オーディオグラス）** を待ちわびています！

Google 信者なので他のグラスは絶対に買いません（笑）。  
発売は秋とのことで、それまでの間ふと「Gemini グラスをつけてたら、毎日どうなるんだろう？」と未来を妄想しました。

グラスに「あれ注文しといて」と頼むとすると……

> **🤖「うちの主がこれ欲しいって言ってるんだけど、いくらですか？」**
>
> **🏪「うちなら割引しますよ！」**

え、**AI が勝手に値切り交渉してくれる時代** が来る！？

この妄想が止まらなくて、「じゃあ面白いから作ってみよう！」となりました😂

つまりこの記事は「**人間の代わりに AI が価格交渉してくれるシステム**」を作ってみた開発記です。  
さっそくデモを触ってみたい方や、コード全体をのぞいてみたい方はこちらからどうぞ！👇

![デモサイト](https://static.zenn.studio/user-upload/edaf070e8eb9-20260603.png)

---

## 2. システム全体のアーキテクチャ 🏗️

まず全体像を把握しましょう。

!

**大事なポイント🔑**  
「2つの AI が本当にリアルタイムで通信している」わけではありません。  
Gemini への **1回の API コール**で「交渉劇の脚本（JSON）を丸ごと生成」しています。

Gemini に「演劇の脚本家として、このキャラクターが何往復か交渉する台本を書いて」とお願いするイメージです！  
フロントエンドがその台本をターンごとにアニメーション再生することで、まるでリアルタイム交渉のように見えます。

### 技術スタック

| レイヤー | 技術 | 選んだ理由 |
| --- | --- | --- |
| フロントエンド | HTML + Vanilla JavaScript | フレームワーク不要、シンプルな実装 |
| バックエンド | Python + **FastAPI** | 高速・非同期対応、型安全な API |
| AI | **Gemini 2.5 Flash**（Vertex AI） | 高速・低コスト、response\_schema 対応 |
| インフラ | Google Cloud Run | サーバーレスでスケーラブル |
| レートリミット | IP ベース（カスタム実装） | API コスト乱用を防止 |

---

## 3. キャラクター設定（プロンプトエンジニアリング）🎭

このアプリの肝は **「AI にキャラクターを演じさせる」プロンプト設計** です。

単に「交渉してください」と頼むだけでは面白みのない台本になってしまいます。  
**口癖・行動パターン・目標・キャラクターのアーク（変化）** を明示することで、ドラマチックな展開が生まれます。

### 🐆 買い手：ヒョウ柄オカン（Kansai Leopard O-kan）

* コテコテの大阪弁で話す、値切りのプロ
* 口癖：「そんなん言うたら、**送料こっち持ちやがな！**」「そこをなんとか、**勉強させてもらいまひょ！**」「**アメちゃん**あげるから！」
* 目標：予算以内で 10 円でも安く買いたい。最初から豪快に低い価格をふっかける
* 性格：フレンドリーで図太く、謎のおまけ（アメちゃん・惣菜パック）を交渉材料にする

### 🐺 売り手：頑固オオカミ（Stubborn Wolf Merchant）

* クールで頑固な職人気質のショップ店主
* 口癖：「フン、**無茶言うな**」「これ以上引いたら**赤字**だ」「**職人のプライド**を安売りする気はねぇ」
* 目標：希望価格以上で売りたい。在庫処分したい気持ちはあるが、絶対損はしたくない
* 性格：最初は絶対折れないが、最後はオカンに圧倒されて渋々折れる

---

## 4. バックエンド実装：FastAPI + Vertex AI ⚙️

### 4-1. API のリクエストモデル

Pydantic の `BaseModel` を使って、リクエストの型を定義します。

リクエストモデルの定義（leopard.py 抜粋）

```
from fastapi import APIRouter, Request
from pydantic import BaseModel
from vertexai.generative_models import GenerativeModel

router = APIRouter(
    prefix="/api/leopard",
    tags=["leopard"]
)

class NegotiationRequest(BaseModel):
    item: str    # 商品名（例：「ヒョウ柄の超カワイイ部屋着」）
    budget: int  # オカンの予算（円）
    target: int  # オオカミの最低希望額（円）
```

### 4-2. Vertex AI の `response_schema` で構造化 JSON 出力

**`response_schema`** とは、Gemini に「この形式で JSON を返してね」と強制するための機能です。  
普通にプロンプトで「JSON で返して」と頼むと、形式が安定しないことがありますが、`response_schema` を使うことで**毎回同じ構造の JSON** が返ってきます。

response\_schema の定義と API コール（leopard.py 抜粋）

```
# JSON のスキーマを辞書形式で定義（大文字キーを使用するのが Vertex AI の仕様）
response_schema_dict = {
    "type": "OBJECT",
    "properties": {
        "negotiation_turns": {
            "type": "ARRAY",       # 複数ターンを配列で返す
            "items": {
                "type": "OBJECT",
                "properties": {
                    "speaker": {"type": "STRING"},  # 発言者名
                    "dialogue": {"type": "STRING"}, # セリフ（改行・"禁止をプロンプトで指示）
                    "price": {"type": "INTEGER", "minimum": 0},   # 提示価格（0以上の数値のみ）
                    "mood": {"type": "STRING"}      # 感情タグ（例：「強気」「渋々」）
                },
                "required": ["speaker", "dialogue", "price", "mood"]
            }
        },
        "is_success": {"type": "BOOLEAN"},  # 交渉成立 → true、決裂 → false
        "final_price": {"type": "INTEGER", "minimum": 0}, # 最終取引価格（決裂時は 0、0以上）
        "summary": {"type": "STRING"}       # 交渉全体のまとめ文章
    },
    "required": ["negotiation_turns", "is_success", "final_price", "summary"]
}

model = GenerativeModel("gemini-2.5-flash")

response = model.generate_content(
    prompt,
    generation_config={
        "temperature": 0.8,                        # 0.8：毎回違う個性的な交渉劇になる
        "max_output_tokens": 4096,                 # 長い日本語でも途中で切れないよう大きめに
        "response_mime_type": "application/json",  # JSON 形式で返すよう指定
        "response_schema": response_schema_dict    # スキーマを強制
    }
)
```

### 4-3. レートリミット（API 乱用防止）

公開しているアプリなので、**IP アドレスベースのレートリミット**を実装しています。  
一定回数以上の呼び出しをブロックすることで、API コストの暴発を防ぎます。

レートリミット実装部分（leopard.py 抜粋）

```
@router.post("/negotiate")
async def negotiate(request: NegotiationRequest, raw_request: Request = None):
    try:
        # IPアドレスで使用回数をチェック
        if raw_request:
            from core.rate_limiter import check_and_increment_by_ip
            allowed, limit_msg = check_and_increment_by_ip(None, raw_request, "leopard")
            if not allowed:
                # 制限に引っかかったらエラーレスポンスを返す（例外はスローしない）
                return {
                    "is_success": False,
                    "final_price": 0,
                    "summary": limit_msg,
                    "negotiation_turns": [{
                        "speaker": "システム警告",
                        "dialogue": "API利用制限に達したでヤンス！少し時間を空けて試してヤンス！",
                        "price": 0,
                        "mood": "制限エラー"
                    }]
                }
        # ... 以降に通常の交渉ロジック ...
    except Exception as e:
        # 予期しないエラーもキャラクター口調で返す（ユーザー体験を損なわない）
        print(f"❌ Leopard Negotiation Error: {e}", flush=True)
        return {
            "is_success": False,
            "summary": f"裏取引中にアクシデント発生や！: {str(e)}",
            "negotiation_turns": [{
                "speaker": "システムオカン",
                "dialogue": "堪忍な！交渉中に謎の通信エラーが起きてしもうたわ！アメちゃんあげるから許してな！",
                "price": 0,
                "mood": "トラブル発生"
            }]
        }
```

> **要するにこのステップでは「レートリミット・エラーハンドリング・response\_schema の3点セット」が大事！**

---

## 5. 最大の難関：Gemini JSON 地獄との戦い 😱

ここが今回一番面白い部分です！  
Gemini 3.5Flash でパパっと作ってもらうと**謎のクラッシュが頻発**していたので、ClaudeCodeに修正してもらいました。

### 5-1. 何が起きていたのか？

Gemini に `response_schema` で JSON 形式を指定して、セリフ（dialogue）を生成させていました。  
ところが Gemini は**プロンプトで「`"` を使うな」と指示しても、うっかり `"` を出してしまう**ことがあります。

**壊れた JSON の例：**

```
"dialogue": "そこを "勉強" させてもらいまひょ！"
```

↑ 内側の `"` で JSON パーサーが「あ、文字列終わった！」と誤認識してしまいます。

### 5-2. エラーメッセージの正体

**① `Expecting ',' delimiter`（カンマがありませんエラー）**

コンピューターは `そこを`  の後ろの `"` でセリフが終わったと判断しました。  
JSON のルール上、文字列の終わりにはカンマ（`,`）か閉じカッコ（`}`）が来るはずなのに、  
なぜか `勉強` という普通の文字が現れたので「**カンマがあるべき場所に無いぞ！**」と怒っていたのです。

**② `Unterminated string starting at...`（文字列が閉じてないよエラー）**

`"` が余計に入り込んだせいで開きと閉じのペアがバラバラになり、  
「**セリフの終わりが見つからないまま、データの最後まで行っちゃった！**」とパニックを起こしていました。

### 5-3. なぜプロンプトで指示しても防げなかったのか？

プロンプトで「セリフの中では `"` を絶対に使わず、`「」` を使ってね！」とどれだけ強くお願いしていても、Gemini は何千文字のうち「**たった 1 箇所**」だけうっかりルールを破って、強調の意味で `"アメちゃん"` や `"勉強"` と書いてしまうことがありました。

JSON のパースは**1 文字のミスも許されない超厳格なルール**なので、たった 1 箇所のミスでアプリ全体がクラッシュしていたのです。

### 5-4. Claude Code が考えた解決策：`_repair_json()`

Gemini に「ルールを絶対に守れ！」と説教し続けることではなく、「**AI なんだから、たまにうっかり `"` を出しちゃうこともあるよね。なら、プログラム側で自動的に直してあげればいいじゃん！**」という大人な解決アプローチです。

\_repair\_json() 関数の全コード（leopard.py 抜粋）

```
import json
import re

def _repair_json(text: str):
    """文字列値内の未エスケープ二重引用符を修正してJSONをパースする。"""

    # Gemini がたまに出力する「```json ... ```」形式のコードブロックを除去
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*\n?', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n?```\s*$', '', text)
    text = text.strip()

    # ① まず普通にパースしてみる（大半のケースはこれで成功）
    try:
        return json.loads(text, strict=False)
    except json.JSONDecodeError:
        pass  # 失敗した場合のみ修復処理へ

    # ② 失敗した場合：文字を1文字ずつ調べて余分な " を修復する
    repaired: list[str] = []
    in_string = False  # 今、JSONの文字列値の中にいるかどうか
    skip_next = False  # バックスラッシュのエスケープ処理フラグ

    for i, ch in enumerate(text):
        if skip_next:
            # バックスラッシュの直後の文字はエスケープ済み → そのまま通す
            skip_next = False
            repaired.append(ch)
            continue

        if ch == '\\' and in_string:
            # バックスラッシュを発見 → 次の文字はエスケープ済みなのでスキップ
            repaired.append(ch)
            skip_next = True
            continue

        if ch == '"':
            if not in_string:
                # 文字列の開始
                in_string = True
                repaired.append(ch)
            else:
                # この " は文字列の終わりか、それとも余分な " か？を判定
                rest = text[i + 1:].lstrip(' \t')
                if not rest or rest[0] in ',:}]':
                    # 次がカンマ・閉じカッコ → 正常な文字列の終わり
                    in_string = False
                    repaired.append(ch)
                else:
                    # 次が普通の文字 → 余分な " なので \" にエスケープする
                    repaired.append('\\"')
        else:
            repaired.append(ch)

    return json.loads(''.join(repaired), strict=False)
```

!

**2段階パーサーの考え方と「\_repair\_json」の仕組み解説🔧**

**ステップ1**：まず普通に `json.loads()` を試す → 大半のケースはこれで OK  
**ステップ2**：失敗したら文字単位で走査して、「未エスケープの `"`」を見つけて `\"` に変換してから再パース

特にステップ2の走査ロジックは、細かいですが非常に強力なガードレールになっています。

#### 💡 1. 「未エスケープ」ってなに？

JSONやPythonの世界では、ダブルクォーテーション `"` には **「ここからセリフの始まり／終わり！」** という超特別な役割があるんです。  
でも、セリフの中で飾りとして「"勉強"」とか「"アメちゃん"」みたいに `"` を使いたいときもありますよね。  
その時に、コンピュータに「この `"` はセリフの終わりじゃなくて、ただの文字だからね！」とバックスラッシュ（`\`）を置いて教えてあげることを **「エスケープする」** と言います。

前に `\` がついていない生の `"` のことを **「未エスケープ」** と呼び、これを放置するとコンピュータが「えっ！セリフが終わったのになんで後ろに文字が続いてるの！？キーーー！🤯」とパニックになってエラーでクラッシュしちゃうんです。

#### 🔍 2. 「右隣（次の文字）チェック」で見分ける！

このコードでやっているのは、**「Pythonチェック員による右隣ののぞき見作戦」** です！  
文字を1つずつ読みながら、`"` を見つけたらこう考えます。

* **Python**: 「お、`"` があった！この `"` の**すぐ右隣の文字**を見てみようっと」
* 右隣に `,` や `}` などの記号があれば、「よし、ここで本当にセリフはおしまい！」と判断します。
* でも、右隣に普通の日本語などが続いていたら、**「あ、これはまだセリフの途中だな！」** と見抜いて、裏でこっそり `\"` に書き換えてあげるんです。賢い！

#### 🛡️ 3. 最初から完璧なときはスルーする「スルーパス機能」

Geminiがたまにすごくお利口で、最初から `\"` と綺麗に出力してくれたとき、余計なお節介をしてデータを壊さないための優しさが `ch == '\\'` の部分です。

* バックスラッシュ `\`（Pythonコード上では `\\` と2つ重ねて書きます）を見つけたら、**「この直後の `"` はすでに綺麗にエスケープされてるから、チェックはパスで！」** と目印（`skip_next = True`）を立ててスルーします。
* これにより、最初から正しいものは無傷で優しく通すことができるようになっています！

この「まず試して、ダメなら修復」というパターンは、**AI の出力を扱うときの鉄板テクニック**です！  
AI の出力は「ほぼ正しいけど、たまにルールを守らない」ので、完全に信頼するのではない防御的な処理を用意しておくのがベストプラクティスです。

> **要するにこのステップでは「AI の出力を信頼しすぎず、防御的なパーサーを用意すること」が大事！**

---

## 6. フロントエンド実装：チャット UI 🌐

フロントエンドは **Vanilla JavaScript（フレームワーク無し）** で実装しています。

![アプリの初期状態](https://static.zenn.studio/user-upload/edaf070e8eb9-20260603.png)  
*取引設定パネルと、交渉が始まるのを待つチャットアリーナ。ダークなグラスモーフィズムデザイン。*

### 6-1. タイピングアニメーション

AI が「考えている」ように見せるため、以下の 2 段構えのアニメーションを実装しています。

1. まず「ドットが動くタイピングインジケーター」を表示（考え中の演出）
2. 次に 1 文字ずつテキストが出てくるタイピングアニメーション

タイピングアニメーションのコード（leopard.html 抜粋）

```
// 1ターン分のメッセージを表示する関数
async function displayMessage(speaker, dialogue, price, mood) {
    const chatArea = document.getElementById('chat-area');

    // 発言者がオカンかオオカミかで左右を判定
    const isLeft = (speaker.includes('オカン') || speaker.includes('買い手'));

    // ... バブルの HTML 要素を生成 ...

    // まず「...」のタイピングインジケーターを表示
    const typing = document.createElement('div');
    typing.className = 'typing-indicator';
    typing.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    bubble.appendChild(typing);
    chatArea.scrollTop = chatArea.scrollHeight; // 自動スクロール

    // 800〜1600ms ランダム待機（考えているように見せる）
    await sleep(800 + Math.random() * 800);

    // ドットを消して、1文字ずつタイピング表示に切り替え
    bubble.innerHTML = '';
    let currentText = '';
    for (let i = 0; i < dialogue.length; i++) {
        currentText += dialogue[i];
        bubble.innerText = currentText;
        chatArea.scrollTop = chatArea.scrollHeight;
        await sleep(35); // 1文字 35ms（タイピング速度）
    }

    // 価格バッジを追加表示
    if (price && price > 0) {
        const priceTag = document.createElement('div');
        priceTag.className = 'price-badge';
        priceTag.innerHTML = `💰 提示: <span>${price.toLocaleString()}円</span>`;
        bubble.appendChild(priceTag);
    }
}
```

### 6-2. API コールと結果の順番表示

バックエンドへ POST リクエストを送り、返ってきた交渉ターンを **1 ターンずつ順番に**表示します。  
全ターンを一気に表示せず `await` で待ちながら表示することで、リアルタイム感が生まれます。

API コールとターン表示のコード（leopard.html 抜粋）

```
async function startNegotiation() {
    // ... UIの準備処理 ...

    try {
        // バックエンドに交渉リクエストを送信
        const response = await fetch('/api/leopard/negotiate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                item: itemName,    // 商品名
                budget: budgetVal, // オカンの予算
                target: targetVal  // オオカミの希望額
            })
        });

        if (!response.ok) throw new Error('API通信エラーやで！');

        const data = await response.json();

        // ターンを1つずつ順番に表示（await で前のターンの表示完了を待つ）
        for (let i = 0; i < data.negotiation_turns.length; i++) {
            const turn = data.negotiation_turns[i];
            await displayMessage(turn.speaker, turn.dialogue, turn.price, turn.mood);
        }

        // 取引成立なら紙吹雪（コンフェッティ）を降らせる！
        if (data.is_success) {
            triggerConfetti();
        }

    } catch (err) {
        // エラーも大阪弁で表示してユーザーを和ませる
        chatArea.innerHTML = `
            <div style="color: #ef4444; text-align: center;">
                ⚠️ エラーが発生したで！<br>
                ${err.message || '接続を確認してや。'}
            </div>
        `;
    }
}
```

> **要するにこのステップでは「await で1ターンずつ表示してリアルタイム感を演出すること」が大事！**

---

## 7. 実際の交渉ログを見てみよう 🎬

### 7-1. 通常パターン：予算 3,000円 vs 希望額 2,500円

![部屋着の交渉結果](https://static.zenn.studio/user-upload/7163ebe38dbe-20260603.png)  
*ヒョウ柄部屋着をめぐる交渉。アメちゃん作戦が炸裂した瞬間。*

**Gemini が生成した交渉ログ（要約）：**

| ターン | 発言者 | セリフ（要約） | 提示価格 |
| --- | --- | --- | --- |
| 1 | 🐆 ヒョウ柄オカン（強気） | 「このヒョウ柄めっちゃええやん！1,500円でええやろ！」 | 1,500円 |
| 2 | 🐺 頑固オオカミ（頑固） | 「フン、無茶言うな。3,000円だ。これ以上引いたら赤字だ」 | 3,000円 |
| 3 | 🐆 ヒョウ柄オカン（懐柔） | 「2,000円にしてくれたら、この『アメちゃん』あげるわ！」 | 2,000円 |
| 4 | 🐺 頑固オオカミ（渋々） | 「『アメちゃん』で釣ろうなんて。だが…2,800円が限界だ」 | 2,800円 |
| 5 | 🐆 ヒョウ柄オカン（必死） | 「送料こっち持ちやがな！2,600円で頼むわ！どや？」 | 2,600円 |
| 6 | 🐺 頑固オオカミ（呆れ） | 「チッ…あんたの情熱に免じて…2,600円だ。二度と来るな」 | 2,600円 |

🤝 **取引成立！ 最終価格：2,600円**

オオカミ、「アメちゃん」でちょっと揺らいでるのかわいい😂

### 7-2. 激安チャレンジ：予算 1,000円 vs 希望額 1,500円

オカンの予算がオオカミの希望額より低かったら、どうなるのか実験してみました！

![交渉成立！1,000円](https://static.zenn.studio/user-upload/12610424649f-20260603.png)  
*オカンの予算ピッタリ 1,000円で成立！アメちゃん＋送料持ちの二段構えが刺さった！*

**結果**：なんとオカン予算ピッタリの **1,000円で取引成立**！

アメちゃん作戦 ＋「送料こっち持ちやがな！」の二段構えで、頑固オオカミの職人プライドを完全に崩壊させました（笑）

!

**面白い発見💡**  
「予算 < 希望額」という、通常なら成立しない条件でも Gemini はオカンを勝たせてくれました！

これは「交渉を本当にシミュレーション」しているのではなく、「面白い脚本を書く AI」なので、  
エンタメとして成立する結末に自動的に調整してくれているからです。

本物のエージェント交渉システムを作る場合は、  
**ゲーム理論**（ナッシュ均衡など）や**強化学習**を使った真の交渉アルゴリズムが必要になります。  
今回はあくまで「エンタメとしての交渉シミュレーション」です！

---

## 8. AIエージェント経済圏の未来 🔮

このアプリを作ってみて、将来こうなるんじゃないかなーと思ったことを書きます。

### これまでの EC サイトの戦い方

* SEO（検索上位に表示される）
* サイトデザインの綺麗さ・使いやすさ
* ポイント還元率・クーポン

### これからの AI エージェント時代の戦い方（妄想）

人間ではなく **AI エージェントが買い物をする** 時代が来たとき、  
EC サイトも「人間ではなく AI が見るサイト」になるかもしれません。

> 「このお店の AI 店員、いつもおまけしてくれるし、喋り方が面白いからここで買おう！」

という、**AI 同士の相性や関係性が新しい経済圏を作る**かもしれません。

| 時代 | 競争軸 |
| --- | --- |
| 現在の EC | SEO・デザイン・ポイント還元率 |
| AI エージェント時代 | AI 店員のキャラクター・交渉スタイル・エージェントとの相性 |

商品よりも AI の接客の人気で売れる、そんな未来もあるかも！？

と、想像した6月でした。  
秋の **Gemini グラス**発売が待ちどおしいです😎

---

## 9. 次のステップ 🚀

今後やってみたいこと・実装予定を書いておきます！

---

（独学で勉強中の初心者のため、もし間違っている箇所があれば優しくご指摘いただけると嬉しいです！🙇‍♀️）  
ここまで読んでいただきありがとうございました🐆💕
