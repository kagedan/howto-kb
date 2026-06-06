---
id: "2026-06-05-google-colabに3行コピペするだけでclaudeaiを動かす最短手順-01"
title: "Google Colabに3行コピペするだけでClaude（AI）を動かす最短手順"
url: "https://zenn.dev/randy_epiccat/articles/455f8a8e733ad3"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-06-05"
date_collected: "2026-06-06"
summary_by: "auto-rss"
query: ""
---

「AIを“使う”だけでなく“コードで動かしたい”。でも環境構築でつまずいた」——そんな人向けに、**インストール不要・ブラウザだけ**でClaude APIを動かす最短手順をまとめます。所要5分。

用意するもの

* Googleアカウント（Colabを開くため）
* Anthropic APIキー（`console.anthropic.com` で発行。最初は数百円分の少額でOK）

手順

1. `colab.research.google.com` を開き「ノートブックを新規作成」
2. 左の🔑（シークレット）に `ANTHROPIC_API_KEY` という名前でキーを保存（コードに直書きしない）
3. セルに以下をコピペして再生ボタン▶

```
from google.colab import userdata
import os, anthropic
os.environ["ANTHROPIC_API_KEY"] = userdata.get("ANTHROPIC_API_KEY")

client = anthropic.Anthropic()
res = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=200,
    messages=[{"role": "user", "content": "AI自動化を初心者向けに3行で説明して"}],
)
print(res.content[0].text)
```

これで初めての“AIに仕事をさせるコード”が動きます。

つまずきポイント

* `userdata.get` が None になる → シークレット名のスペル／アクセス許可トグルを確認
* 課金が不安 → まずは少額チャージ＋ `max_tokens` を小さく

まとめ

ここまでが「最初の一歩」。この続きとして、**①文章自動生成 ②Webリサーチ自動化 ③Googleドライブ整理** のコピペで動く実例フルセットと、副業ロードマップまでを1冊にまとめた教材を用意しました（全129ページ）。

👉 [Google ColabではじめるAI自動化入門（BOOTH）](https://booth.pm/ja/items/8378051)

次の記事では、APIキーを安全に扱うための「Colabシークレット機能」を解説します。
