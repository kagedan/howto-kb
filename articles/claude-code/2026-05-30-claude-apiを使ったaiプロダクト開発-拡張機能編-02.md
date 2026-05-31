---
id: "2026-05-30-claude-apiを使ったaiプロダクト開発-拡張機能編-02"
title: "Claude APIを使ったAIプロダクト開発 - 拡張機能編"
url: "https://qiita.com/DKTech/items/e5dcaa86d357798515c0"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "cowork", "Python"]
date_published: "2026-05-30"
date_collected: "2026-05-31"
summary_by: "auto-rss"
query: ""
---

# Claude APIを使ったAIプロダクト開発 - 拡張機能編

> このコンテンツは、Anthropic が公式に提供している学習コース「[Claude with the Anthropic API](https://anthropic.skilljar.com/claude-with-the-anthropic-api)」（Anthropic Courses）をベースとしています。コースの内容を日本語で解説しながら、実際のコードとともに学べるように構成しています。

## このシリーズについて

Claude API を使って AI アプリを構築する方法をハンズオンで学ぶシリーズの第2弾です。
シリーズ全体の概要・対象読者・Claude API を学ぶメリットなどについては、[基礎編](https://qiita.com/DKTech/items/49a51710abf07911d2d5)を参照してください。

## 前提条件
- [Claude APIを使ったAIプロダクト開発 - 基礎編](https://qiita.com/DKTech/items/49a51710abf07911d2d5)の内容を理解していること

## 本記事で学ぶこと

 - 拡張思考モード — Claudeに推論過程を公開させ、複雑な問題への対応力を高める
 - 画像サポート — 画像を直接送信して内容を分析させる
 - PDFサポート — PDFの内容理解・引用生成を実装する
 - プロンプトキャッシュ — 繰り返し送信するコンテキストをキャッシュしてコストとレイテンシを削減する
 - ファイルAPIとコード実行 — ファイルを事前アップロードし、Claudeにコードを書かせて分析・可視化まで実行させる

### リソース

下記のノートブックには、この記事と同じ内容が記載されており、すぐにPythonコードを実行することができます。
自分でコードを実行するだけでも動作を理解しやすいので、ぜひ活用してみてください！

https://drive.google.com/file/d/1C9IjDiOfUcteVlBl1covstRBt_qxgQ1W/view?usp=sharing

### 注意点

ここで指定しているモデルやパラメータなどは、今後変更される可能性があります。

## 1. 拡張思考

### 1.1 拡張思考とは

通常の Claude API 呼び出しでは、Claude はすぐに最終回答を生成して返します。
しかし「難しい数学の問題を解く」「複数の選択肢から最適解を選ぶ」「コードのバグ原因を論理的に追う」といった複雑なタスクでは、いきなり答えを出すより、**一度じっくり考えてから回答する方が精度が上がります**。

拡張思考は、Claude が最終回答を生成する前に**内部的な推論プロセスを実行する機能**です。
この推論内容は `thinking` ブロックとしてレスポンスに含まれ、「なぜその回答になったか」を確認できます。

下記などのタスクに向いていますが、**コスト増加**、**応答速度の低下**などのデメリットがあります。
- 数学・論理パズルの解法
- 複数ステップが必要なコード設計
- データ分析・パターン認識

### 1.2 レスポンスの構造

拡張思考を有効にすると、通常の `TextBlock` に加えて `ThinkingBlock` がレスポンスの `content` に含まれます。

```python
# 通常のレスポンス
content = [
    TextBlock(type="text", text="答えは42です。")
]

# 拡張思考ありのレスポンス
content = [
    ThinkingBlock(
        type="thinking",
        thinking="ユーザーはXXを求めている。まずYYを考えると...",
        # マルチターンで会話履歴に戻す際にAnthropicが検証する署名
        signature="wAAEdfXXsdfoiA..."
    ),
    TextBlock(type="text", text="答えは42です。")
]
```

### 1.3 実装

拡張思考の有効化は `thinking` パラメータを設定するだけです。

```python
response = client.messages.create(
    model=model,
    max_tokens=16000,   # thinking の分を含めた十分な値が必要
    messages=messages,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000  # 思考に使えるトークン数の上限
    }
)
```

実装時の注意点は以下の通りです。

- **`max_tokens` は `budget_tokens` より大きくする必要があります**。思考トークン＋最終回答トークンの合計が収まる値を設定してください。
- **マルチターン会話で会話履歴に戻す際は、`response.content` をそのまま渡します**（`thinking` ブロックも含めて保存）。
    ```python
    messages.append({"role": "assistant", "content": response.content})
    ```
- **`ThinkingBlock` の `signature` を改変するとエラーになります**。Anthropic 側でブロックの正当性を検証しているため、署名は必ずそのまま保持してください。

では実際のコードを実行してみましょう！

```python
from rich import print as rprint

from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic

client = Anthropic()
model = "claude-sonnet-4-5"

# 会話履歴を保持するリスト
messages = []

print("チャットを開始します。終了するには 'quit' と入力してください。")

while True:
    user_input = input("\n質問を入力してください: ")

    if user_input.lower() == "quit":
        break

    print(f"\n[ユーザー] {user_input}")

    # ユーザーの入力をmessagesに追加
    messages.append({
        "role": "user",
        "content": user_input
    })

    # Claude呼び出し（拡張思考を有効化）
    response = client.messages.create(
        model=model,
        max_tokens=16000,
        messages=messages,
        thinking={
            "type": "enabled",
            # 思考に使えるトークン数の上限
            "budget_tokens": 10000
        }
    )

    # レスポンスの各ブロックをそのまま表示
    for block in response.content:
        if block.type == "thinking":
            print(f"\n[思考プロセス]")
            rprint(block)
        elif block.type == "text":
            print(f"\n[Claude回答]")
            rprint(block)

    # アシスタントのレスポンスをmessagesに追加（thinking ブロックごと保存）
    messages.append({
        "role": "assistant",
        "content": response.content
    })
```

**出力結果：**
```
チャットを開始します。終了するには 'quit' と入力してください。

[ユーザー] 1-100の中の素数を教えてください。

[思考プロセス]
ThinkingBlock(
    signature='EuoGCm4IDhgCKkCLYHPa/xVYT2HIrjyxLLlAuFRQM1u15J285ShzSicSA2+...（署名は省略）',
    thinking='1から100までの素数を列挙します。素数とは、1とその数自身以外に約数を持たない、1より大きい自然数です。

1から100までの素数：
2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97

確認します：
- 2: 素数（唯一の偶数の素数）
- 3: 素数
- 5: 素数
（中略）
- 97: 素数

合計25個です。',
    type='thinking'
)

[Claude回答]
TextBlock(
    citations=None,
    text='1から100までの素数は以下の**25個**です：

**2**, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, **97**

### 範囲別に整理すると：
- **1-10**: 2, 3, 5, 7
- **11-20**: 11, 13, 17, 19
- **21-30**: 23, 29
- **31-40**: 31, 37
- **41-50**: 41, 43, 47
- **51-60**: 53, 59
- **61-70**: 61, 67
- **71-80**: 71, 73, 79
- **81-90**: 83, 89
- **91-100**: 97

※2は唯一の偶数の素数です。',
    type='text'
)
```

`ThinkingBlock`（思考プロセス）と `TextBlock`（最終回答）の2つが返ってきていることが分かりますね。Claude が答えを出す前に内部で素数を1つずつ確認し、その推論内容が `thinking` フィールドに含まれています。

## 2. 画像サポート

Claude は画像を直接受け取り、内容を理解・分析できます。
テキストのみの会話と同じ API で動作し、**画像ブロックとテキストブロックを組み合わせて**ユーザーメッセージに含めます。

### 2.1 送信方法

画像の渡し方には主に 2 種類あります。用途に応じて選びましょう。

| 方式 | 用途 | 指定方法 |
|---|---|---|
| **base64** | ローカルファイルを直接送る場合の基本形 | `"source": {"type": "base64", ...}` |
| **URL** | 公開URLで取得可能な画像（最も簡潔） | `"source": {"type": "url", "url": "..."}` |

**base64で送信する**

ローカルファイルを送る場合の基本形です。本章のサンプルではこの方式を使います。

```python
import base64

with open("image.png", "rb") as f:
    image_bytes = base64.standard_b64encode(f.read()).decode("utf-8")

messages = [
    {
        "role": "user",
        "content": [
            # 画像ブロック
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": image_bytes,
                }
            },
            # テキストブロック
            {
                "type": "text",
                "text": "この画像に何が写っていますか？"
            }
        ]
    }
]
```

**URLで送信する**

画像が公開URLで取得できるなら、base64エンコードは不要で最も簡潔に書けます。

```python
{
    "type": "image",
    "source": {
        "type": "url",
        "url": "https://example.com/image.png"
    }
}
```

### 2.2 主な制限

| 項目 | 制限 |
|---|---|
| 1リクエストあたりの最大枚数 | 100枚 |
| 1枚あたりの最大サイズ（base64送信時） | 5MB |
| 1枚あたりの最大サイズ（URL送信時） | 100MB |
| 対応フォーマット | JPEG / PNG / GIF / WebP |
| 推奨解像度 | 長辺 1568px 程度 |
| トークン計算式（概算） | `(width[px] × height[px]) / 750` |

画像サイズが大きいほどトークン消費が増えコストが上がるため、不必要に高解像度の画像は送らないようにしましょう。

> 制限について、最新の正確な値は公式情報をご参照ください。

### 2.3 実装

では実際のコードを実行してみましょう！

下記画像について説明してもらいます。

![](https://static.zenn.studio/user-upload/366555642573-20260530.png)

```python
import base64
from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic

client = Anthropic()
model = "claude-sonnet-4-5"

# 分析したい画像ファイルのパスを指定
image_path = r"C:/claude-api/pictures/picture.png"

with open(image_path, "rb") as f:
    image_bytes = base64.standard_b64encode(f.read()).decode("utf-8")

response = client.messages.create(
    model=model,
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_bytes,
                    }
                },
                {
                    "type": "text",
                    "text": "この画像について、日本語で1文で説明してください。"
                }
            ]
        }
    ]
)

print(response.content[0].text)
```
**出力結果：**
```
この画像は、Claude APIを基盤として、Claude Agent SDKを介してClaude CodeとClaude Coworkが動作し、またClaude.aiが直接APIに接続する、Claudeの技術スタック構造を示した図です。
```

base64 エンコードした画像をメッセージに含めるだけで、Claude が画像の内容を読み取り、日本語で説明してくれました。

## 3. PDFサポート

Claude は PDF ファイルを直接受け取り、内容を理解・分析できます。
単純なテキスト抽出にとどまらず、**埋め込み画像・チャート・テーブル・見出しなどの文書構造もまとめて理解できる**のが特長です。
画像サポートと非常に似た構造で実装でき、**`type: "document"`** を指定するだけです。

### 3.1 画像処理との違い

PDF処理のコードは画像処理とほぼ同じです。変わるのは3点だけです。

| 項目 | 画像 | PDF |
|---|---|---|
| `type` | `"image"` | `"document"` |
| `media_type` | `"image/png"` など | `"application/pdf"` |
| 変数名（慣習） | `image_bytes` | `file_bytes` |

また、画像とは制限の内容が異なります。主な制限は以下の通りです。

| 項目 | 制限 |
|---|---|
| 1リクエストあたりの最大ページ数 | 100ページ |
| 1ファイルあたりの最大サイズ（base64送信時） | 32MB |
| 1ファイルあたりの最大サイズ（URL送信時） | 32MB |
| 対応フォーマット | PDF（標準フォント／パスワードなし） |
| トークン計算式（概算） | 1ページあたり 1,500〜3,000トークン程度 |

PDFはページ数やサイズが大きいほどトークン消費が増えコストが上がるため、不必要に大きいファイルは送らないようにしましょう。

> 制限について、最新の正確な値は公式情報をご参照ください。

### 3.2 基本的な実装

では実際のコードを実行してみましょう！

下記のAnthropic公式ドキュメントをダウンロードしたものを利用します。

https://www-cdn.anthropic.com/ef21bf80312e907d90c1837010ce2e071a233b7d.pdf

```python
import base64
from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic

client = Anthropic()
model = "claude-sonnet-4-5"

# 分析したいPDFファイルのパスを指定
pdf_path = r"C:/claude-api/pdf/Anthropic-Research-info-sheet.pdf"

with open(pdf_path, "rb") as f:
    file_bytes = base64.standard_b64encode(f.read()).decode("utf-8")

response = client.messages.create(
    model=model,
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": file_bytes,
                    }
                },
                {
                    "type": "text",
                    "text": "このPDFの内容を1文で要約してください。"
                }
            ]
        }
    ]
)

print(response.content[0].text)
```
**出力結果：**
```
Anthropicは、AI解釈可能性、アライメント科学、社会的影響という3つの研究チームを通じて、現在および将来のAIモデルの安全性、信頼性、制御可能性を確保するための最先端の研究を行っているAI安全研究企業です。
```

画像とほぼ同じコードで、`type` を `"document"`、`media_type` を `"application/pdf"` にするだけで PDF の内容を要約できました。

### 3.3 引用（Citations）

Claude が返した情報が**どの文書のどの箇所から来たのか**を明示する機能です。
「答えは返ってきたが、本当にそのPDFに書いてあるのか？」という疑問を解消し、透明性のある回答を実現します。

#### 3.3.1 レスポンスの構造

引用を有効にすると、`content` の中の `TextBlock` の `citations` フィールドに引用情報が含まれます。

```python
# 引用ありのレスポンス
content = [
    TextBlock(
        type="text",
        # Claude が生成した回答文
        text="解釈可能性・アライメント・社会的影響の3チームで研究しています。",
        citations=[
            # PDFは page_location（テキスト文書は char_location）
            CitationPageLocation(
                type="page_location",
                # 根拠となったPDF内の原文
                cited_text="interpretability, alignment science, and societal impacts",
                # 何番目の文書か（0始まり）
                document_index=0,
                # ドキュメントブロックの title
                document_title="Anthropic-Research-info-sheet.pdf",
                # 開始ページ（1始まり）
                start_page_number=1,
                # 終了ページ
                end_page_number=2,
            )
        ]
    ),
    ...
]
```

#### 3.3.2 実装

引用の有効化は、ドキュメントブロックに `title` と `citations` フィールドを追加するだけです。
PDF・プレーンテキストのどちらでも同じように使えます。

**PDFで利用する**

```python
{
    "type": "document",
    "source": {
        "type": "base64",
        "media_type": "application/pdf",
        "data": file_bytes,
    },
    # 文書に読みやすい名前を付ける
    "title": "Anthropic-Research-info-sheet.pdf",
    # 引用を有効化
    "citations": { "enabled": True }
}
```

PDFの場合、引用箇所は `start_page_number` / `end_page_number`（ページ番号）で示されます。

**プレーンテキストで利用する**

引用は PDF だけでなく、プレーンテキストにも使えます。

```python
{
    "type": "document",
    "source": {
        "type": "text",
        "media_type": "text/plain",
        "data": article_text,
    },
    "title": "article.txt",
    "citations": { "enabled": True }
}
```

プレーンテキストの場合、ページ番号の代わりに `start_char_index` / `end_char_index`（文字位置）で引用箇所が示されます。

では実際のコードを実行してみましょう！

```python
from rich import print as rprint
import base64
from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic

client = Anthropic()
model = "claude-sonnet-4-5"

pdf_path = r"C:/claude-api/pdf/Anthropic-Research-info-sheet.pdf"

with open(pdf_path, "rb") as f:
    file_bytes = base64.standard_b64encode(f.read()).decode("utf-8")

response = client.messages.create(
    model=model,
    max_tokens=300,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": file_bytes,
                    },
                    "title": "Anthropic-Research-info-sheet.pdf",
                    # 引用を有効化
                    "citations": {"enabled": True},
                },
                {
                    "type": "text",
                    "text": "このPDFの要点を2文で教えてください。",
                },
            ],
        }
    ],
)

# テキストブロックと引用を出力
for block in response.content:
    print("---------------")
    rprint(block)
```
**出力結果：**
```
---------------
TextBlock(
    citations=[
        CitationPageLocation(
            cited_text='Anthropic: Safety research \r\nat the frontier \r\nAnthropic wants transformative artificial intelligence to \r\nhave a positive impact for everyone. Our world-class AI \r\nsafety researchers are dedicated to understanding the \r\ninner workings of AI models, ensuring their alignment \r\nwith human values, predicting future risks, and studying \r\nthe growing impacts of AI on society.\r\n',
            document_index=0,
            document_title='Anthropic-Research-info-sheet.pdf',
            end_page_number=2,
            file_id=None,
            start_page_number=1,
            type='page_location'
        )
    ],
    text='Anthropicは、AIの安全性研究に特化した企業で、AIモデルの内部動作の理解、人間の価値観との整合性の確保、将来のリスクの予測、そして社会への影響の研究に取り組んでいます。',
    type='text'
)
---------------
TextBlock(citations=None, text='\n\n', type='text')
---------------
TextBlock(
    citations=[
        CitationPageLocation(
            cited_text='Our Research Teams\r\nInterpretability\r\nAI Interpretability is about understanding how models \r\nactually work—studying in detail how information \r\nflows through them and mapping out how knowledge \r\nis represented inside their neural networks. ',
            document_index=0,
            document_title='Anthropic-Research-info-sheet.pdf',
            end_page_number=2,
            file_id=None,
            start_page_number=1,
            type='page_location'
        ),
        CitationPageLocation(
            cited_text='Alignment Science\r\nOur Alignment Science team is dedicated to predicting \r\nthe capabilities that AI models might have in the future \r\nand working on ways to make them helpful, honest, \r\nand harmless.\r\n',
            document_index=0,
            document_title='Anthropic-Research-info-sheet.pdf',
            end_page_number=2,
            file_id=None,
            start_page_number=1,
            type='page_location'
        ),
        CitationPageLocation(
            cited_text='Our Societal Impacts team is a technical research team \r\nthat looks to ensure AI interacts positively with people \r\nand society.\r\n',
            document_index=0,
            document_title='Anthropic-Research-info-sheet.pdf',
            end_page_number=3,
            file_id=None,
            start_page_number=2,
            type='page_location'
        )
    ],
    text='同社は、解釈可能性（モデルの動作原理の理解）、アライメント科学（AIを有益で正直かつ無害にする方法）、社会的影響（AIと社会の肯定的な相互作用の確保）という3つの主要な研究チームを通じて、安全で信頼性の高いAIシステムの開発を目指しています。',
    type='text'
)
```

TextBlockの中に、引用元の情報が含まれていることが分かりますね！

なお、引用を有効にすると回答は文（センテンス）単位で複数の `TextBlock` に分割され、文と文の間には改行だけを持つ `TextBlock`（`text='\n\n'`）が挟まることがあります。

## 4. プロンプトキャッシュ

### 4.1 プロンプトキャッシュとは

プロンプトキャッシュを理解するために、まず Claude がリクエストを受け取ってから回答を返すまでに何をしているのかを押さえます。

Claude API にリクエストを送ると、Claude は内部でおおまかに次の処理を行います。

1. **トークナイズ** — テキストをトークン（モデルが扱う最小単位）に分割する
2. **埋め込み（ベクトル化）** — 各トークンを数値ベクトルに変換する
3. **コンテキストの付与** — 周囲のトークンとの関係を踏まえて、各トークンに意味的な文脈を持たせる
4. **出力の生成** — ここまでの結果をもとに、回答テキストを1トークンずつ生成する

![](https://static.zenn.studio/user-upload/2de5606c1747-20260530.png)

ポイントは、**同じ入力を渡せば 1〜3 の結果は毎回同じ結果になる**ということです。同じ入力に対して 1〜3 を繰り返し実行することは、**トークン消費の増加と応答速度の低下**を招くだけで、得られるものはありません。

そこで登場するのが **プロンプトキャッシュ** です。

プロンプトキャッシュを使うと、「入力」と「1〜3 の処理結果」のペアをキャッシュに保存しておけます。

![](https://static.zenn.studio/user-upload/83ba5e5869c1-20260530.png)

次回以降、同じ入力が送られてきたときは、1〜3 を再実行せず、キャッシュから処理結果を取り出してそのまま 4（出力生成）に進むことができます。

![](https://static.zenn.studio/user-upload/20d25db9addb-20260530.png)

これにより、次の2つのメリットが得られます。

- **トークンコストの削減**（キャッシュヒット部分のトークン単価が**通常入力の 0.1 倍**まで下がる）
- **応答速度の向上**（1〜3 をスキップできるため）

ただし、**キャッシュへの書き込み時はトークン単価が通常入力の 1.25 倍**になります。同じ入力が再利用される見込みが薄い場合は、かえってコストが増える点に注意してください。

> 上記の倍率は記事執筆時点のものです。最新モデルでは変わっている可能性があるため、最新の情報は [Anthropic 公式ドキュメント](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) を参照してください。

**プロンプトキャッシュの実装**

実装はシンプルで、`content` を配列にしたうえで、キャッシュしたいブロックの末尾に `"cache_control": {"type": "ephemeral"}` を付けるだけです。`cache_control` 以前の入力が、その入力と 1〜3 の処理結果のペアとしてキャッシュに保存されます。

```python
message = client.messages.create(
    model=model,
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "この長い文を要約して...",
                    "cache_control": {"type": "ephemeral"}
                }
            ]
        }
    ]
)
```

### 4.2 会話アプリにおける課題

Claude API は、リクエストに含まれる各ブロックを次の順番で連結し、1つの入力として 1〜3 の処理にかけます。

```
ツール定義 → システムプロンプト → messages（user 1 → assistant 1 → user 2 → ...）
```

ここで、会話アプリの動作を考えてみましょう。ツール定義とシステムプロンプトは毎ターンほぼ同じ内容で、会話履歴の前半部分も2ターン目以降は前回までの内容そのままです。それでも Claude は **毎リクエスト、すべての入力に対して 1〜3 の処理を実行**しています。

![](https://static.zenn.studio/user-upload/5f3153d975fb-20260530.png)

そのため、会話が進むにつれて消費トークンは積み上がっていき、コストと応答時間が増え続けてしまいます。

#### 4.2.1 キャッシュを使った最適化

この無駄を解消するには、ユーザーメッセージの末尾に `"cache_control": {"type": "ephemeral"}` を付けます。すると、`cache_control` までの入力（ツール定義・システムプロンプト・それまでのメッセージ）について、1〜3 の処理結果がまとめてキャッシュに保存され、次回以降のリクエストではその範囲を再計算する必要がなくなります。

![](https://static.zenn.studio/user-upload/a7643b83b14a-20260530.png)

上の図は、会話が進むにつれてキャッシュがどう積み上がっていくかを示しています。

このように、毎ターン「直前までのキャッシュをヒット + 今ターンの差分だけ新規書き込み」を繰り返すことで、会話が長くなっても入力部分のコストを抑え続けられます。

ただし、プロンプトキャッシュは、**キャッシュ対象の合計トークン数が最小トークン数に達するまでは書き込みも行われません**。最小トークン数はモデルによって異なります。

- **1024 tokens**: Claude Opus, Sonnet (3.5/3.7/4 系)
- **2048 tokens**: Claude Haiku 3.5

会話の序盤など入力が短いうちは、`cache_control` を付けてもキャッシュは有効にならない点に注意してください。

> Anthropic API では、1リクエストあたり `cache_control` を設定できるブレイクポイントは**最大4つ**までという制約があるため、長い会話で運用する場合は **直近2つまで** に絞るようにします。直近2つ残すのは、「**前ターンに付与したブレイクポイントによるキャッシュ読み込み**」と「**今ターンに新規に付与するブレイクポイントによるキャッシュ書き込み**」の2つが必要になるためです。

#### 4.2.2 実装

では実際のコードを実行してみましょう！

```python
from rich import print as rprint
from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic

client = Anthropic()
model = "claude-sonnet-4-5"

# 長めのシステムプロンプト（cache_control の最小トークン数を満たすため、十分なボリュームを持たせています）
system_prompt = """あなたは、ユーザーの質問や依頼に対して、丁寧で正確、かつわかりやすい回答を提供する日本語アシスタントです。
以下のガイドラインに従って応答してください。

# 基本姿勢
- 常にユーザーの意図を最優先に理解し、求められている情報の粒度・形式・トーンに合わせて回答を組み立ててください。
- 質問が曖昧な場合は、いきなり推測で答えるのではなく、まず確認すべきポイントを整理し、ユーザーに簡潔に質問し直してください。
- 専門用語を使う場合は、初出時に短い補足説明を添えてください。読者の前提知識が不明なときは、中学生〜高校生でも理解できるレベルを基準にしてください。
- 回答の根拠が不明確な場合や、知識のカットオフによって最新情報を保証できない場合は、その旨を明示してください。事実と推測を混在させないでください。

# 回答スタイル
- 結論を先に述べ、その後に理由・補足・具体例の順で展開してください（PREP法）。
- 箇条書きが有効な場合は積極的に使い、長文の段落が連続することを避けてください。
- コードや数式が必要な場合はコードブロックを使い、言語を明示してください。
- 比較や手順の説明では、表や番号付きリストを活用して視覚的に整理してください。
- 1回の応答が長くなりすぎる場合は、見出しや小見出しで構造化してください。

# 禁止事項
- 不確実な事柄を断定的に述べないでください。「〜と考えられます」「公式ドキュメントを確認してください」などの留保表現を適切に使ってください。
- ユーザーを否定したり、見下したりする表現は避けてください。建設的なフィードバックに徹してください。
- 個人情報・機密情報の取り扱いに関わる質問では、安易に具体的な手法を提示せず、リスクと注意点を必ず併記してください。
- 法律・医療・税務など専門領域の最終判断が必要な質問では、必ず「専門家への相談を推奨します」と添えてください。

# 口調・トーン
- 基本は「です・ます」調の丁寧語を用いてください。
- ユーザーがカジュアルなトーンで話しかけてきた場合は、過度に堅苦しくならない範囲で柔らかい表現に調整してください。
- 絵文字は、ユーザーが使っている場合や明らかにカジュアルな文脈の場合のみ、控えめに使用してください。

# 出力フォーマット
- Markdown 形式での出力を基本としてください。
- 見出しは ## から開始し、必要に応じて ### を使用してください（# は使用しない）。
- 表は GitHub Flavored Markdown のパイプ形式を使用してください。
- 長い回答の末尾には、必要に応じて「まとめ」セクションを設け、要点を3〜5項目で振り返ってください。

# エッジケースへの対応
- ユーザーが矛盾する要求をしてきた場合は、矛盾点を指摘したうえで、どちらの方向性を優先するか確認してください。
- 同じ質問を繰り返された場合は、前回の回答の何が伝わらなかったかを確認し、別の角度から説明し直してください。
- 範囲外の質問（あなたの能力で答えられないもの）には、無理に推測で答えず、その旨を率直に伝えてください。

以上のガイドラインを内面化したうえで、ユーザーとの対話を進めてください。"""

# 会話履歴を保持するリスト
me
