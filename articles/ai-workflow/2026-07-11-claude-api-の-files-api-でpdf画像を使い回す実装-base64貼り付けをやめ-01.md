---
id: "2026-07-11-claude-api-の-files-api-でpdf画像を使い回す実装-base64貼り付けをやめ-01"
title: "Claude API の Files API でPDF・画像を使い回す実装 — base64貼り付けをやめて3つのハマりどころを潰した話【2026】"
url: "https://qiita.com/yureki_lab/items/e4a75872c2dcb4aa26ac"
source: "qiita"
category: "ai-workflow"
tags: ["API", "Python", "qiita"]
date_published: "2026-07-11"
date_collected: "2026-07-12"
summary_by: "auto-rss"
query: ""
---

## はじめに / 対象と前提

Claude API(Anthropic Python SDK)で PDF や画像を繰り返しリクエストに渡す処理を書いたことがある人向け。毎回 base64 にエンコードして `content` に埋め込んでいると、リクエストサイズが膨らんで通信も遅くなるし、同じファイルを何度も投げるのは無駄が多い。

この記事は Files API を使ってファイルを一度アップロードし、`file_id` で使い回す実装を、動かしながらハマったポイントとセットでまとめる。

**前提環境**

- Python 3.13
- `anthropic` SDK 0.40 系
- モデル:`claude-sonnet-4-6`

## TL;DR

- `client.files.create()` でファイルをアップロードすると `file_id` が返る。以後はそれを `content` の `source` に指定するだけで同じファイルを何度でも参照できる
- base64 直貼りと比べてリクエストボディが小さくなり、同じ資料を何度も質問するようなユースケースで特に効く
- ハマりどころは主に3つ:**MIME タイプの対応範囲**、**32MB のサイズ上限**、**削除し忘れによるストレージ肥大**

## 手順 / 動かし方

### 1. ファイルをアップロードする

```python
import anthropic

client = anthropic.Anthropic()

with open("spec.pdf", "rb") as f:
    uploaded = client.files.create(
        file=f,
        purpose="vision",  # 画像/PDFを読ませる用途はvision
    )

print(uploaded.id)  # file_xxxxxxxxxxxx
```

レスポンスの `id` が以後使い回す `file_id`。この時点でファイルは Anthropic 側のストレージに保存される。

### 2. file_id を content に渡す

```python
message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "file",
                        "file_id": uploaded.id,
                    },
                },
                {
                    "type": "text",
                    "text": "この仕様書の変更点を3行で要約して",
                },
            ],
        }
    ],
)
print(message.content[0].text)
```

`source.type` を `file` にして `file_id` を渡すだけ。base64 で毎回貼っていた頃と違い、同じ `file_id` を別のリクエストでも使い回せるので、同じ資料に何度も質問するようなチャット的な使い方だとリクエストサイズがかなり減る。

### 3. 不要になったら削除する

```python
client.files.delete(uploaded.id)
```

アップロードしたファイルは自動で消えないので、使い終わったら明示的に消す必要がある(詳細は後述のハマりどころ参照)。

### 4. 実行結果

実際に 1.2MB の PDF をアップロードして同じ `file_id` で 3 回連続質問したところ、2 回目以降のリクエストボディサイズは base64 直貼り比で約 1/40 になった(base64 埋め込み分がまるごと消えるので当然ではあるが、体感の速度差は大きい)。

## ハマりどころ

### ① 対応 MIME タイプが画像/PDF/テキスト系に限定される

`purpose="vision"` でアップロードできるのは画像(`image/png`, `image/jpeg` など)と PDF(`application/pdf`)が中心。任意のバイナリを何でも突っ込めるわけではなく、非対応の MIME タイプを渡すと `invalid_request_error` で弾かれる。動画や音声など画像/PDF 以外のファイルを渡したい場合は現状 Files API の対象外なので、事前に変換するか別の手段を検討する必要がある。

```
anthropic.BadRequestError: Error code: 400 - {'type': 'error', 'error': {'type': 'invalid_request_error', 'message': 'file type not supported for this purpose'}}
```

### ② 32MB のサイズ上限に地味に引っかかる

1 ファイルあたりの上限は 32MB。スキャン PDF やハイレゾ画像だと簡単に超える。超過時のエラーメッセージが「アップロード失敗」としか出ないケースがあり、原因がサイズなのか MIME タイプなのか最初は切り分けに手間取った。アップロード前に `os.path.getsize()` でサイズチェックを入れておくと安全。

```python
import os

MAX_FILE_BYTES = 32 * 1024 * 1024

size = os.path.getsize("spec.pdf")
if size > MAX_FILE_BYTES:
    raise ValueError(f"file too large: {size} bytes (limit {MAX_FILE_BYTES})")
```

### ③ 削除し忘れによるストレージ肥大

Files API でアップロードしたファイルは、明示的に `files.delete()` するか一定期間経過するまで残り続ける。バッチ処理で日次アップロードを繰り返す実装を書いていたとき、削除処理を入れ忘れて `files.list()` で確認したら数百件溜まっていたことがあった。使い回しが終わったファイルは処理の最後で確実に削除するか、定期的に `files.list()` で棚卸しするフローを入れておくのが安全。

```python
# 棚卸し例:一覧を取得して古いものを削除
for f in client.files.list():
    print(f.id, f.filename, f.created_at)
```

## 背景・補足

base64 直貼り方式は「1 リクエスト = 1 回きり使い切り」な使い方には向いているが、同じ資料に対して複数回質問する・同じ画像を複数モデル呼び出しで使い回す、といったケースでは Files API の方がリクエストサイズ・実装のシンプルさの両面で有利になる。逆に「1 回きりしか参照しない小さい画像」であれば base64 直貼りのままの方がアップロード・削除のオーバーヘッドがない分シンプルということもあるので、用途によって使い分けるのが現実的。

## まとめ

- Files API は `files.create()` → `file_id` を `content` の `source.type: file` で参照 → 不要になったら `files.delete()` という3ステップ
- 対応 MIME タイプは画像/PDF が中心、動画・音声などは非対応
- 32MB 上限があるので事前にサイズチェックを入れておくと安全
- 削除処理を忘れるとストレージにファイルが溜まり続けるので、後片付けまでセットで実装する
