---
id: "2026-07-03-googlecolabで無料で文字おこし-01"
title: "Googlecolabで無料で文字おこし"
url: "https://qiita.com/10yama_k/items/845b08ad280ce1c832a6"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "OpenAI", "qiita"]
date_published: "2026-07-03"
date_collected: "2026-07-04"
summary_by: "auto-rss"
query: ""
---

# はじめに
Claude Codeを秘書役にして、頭に浮かんだ開発構想や人生設計の管理をしています。

夜寝る前にふとビジネスプランを思いつくことが多く、いつも次のようなフローでメモを残しています。

1. 紙に殴り書き
2. スマホで録音
3. 音声を文字起こし

このうち3の文字起こしに、Google Colab上でWhisperを実行する方法を使っているので、実行手順を備忘録として残します。

## 実行環境
Google Colab（無料枠でOK。速度を重視する場合はランタイムをGPU（T4など）に変更）
Whisper（OpenAI製の音声認識モデル）

# 手順
## Whisperのインストール


```first.py
!pip install -q openai-whisper
```
-q は quiet オプションで、インストール時のログ出力を抑えて画面をすっきりさせるためのものです。

## 音声ファイルのアップロード

```Second.py
from google.colab import files
uploaded = files.upload()  # 
```

実行するとファイル選択ダイアログが表示されるので、録音した音声ファイル（m4a、mp3、wavなど）を選択します。複数ファイルをまとめてアップロードすることも可能です。

## 文字起こしの実行

```third.py
import whisper
import os

# モデルは精度重視なら medium　や　large 
# 速度重視なら base や small
model = whisper.load_model("medium")

for filename in uploaded.keys():
    print(f"処理中: {filename}")

    result = model.transcribe(filename, language="ja")

    base_name = os.path.splitext(filename)[0]
    txt_filename = f"{base_name}.txt"

    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write(result["text"])

    print(f"→ 保存完了: {txt_filename}\n")

print("完了")
```

アップロードした音声ファイルをすべてループで処理し、同名の.txtファイルとして書き出しています。language="ja"を指定することで日本語として認識させています。
