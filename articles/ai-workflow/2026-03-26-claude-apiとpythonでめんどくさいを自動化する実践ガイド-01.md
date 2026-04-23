---
id: "2026-03-26-claude-apiとpythonでめんどくさいを自動化する実践ガイド-01"
title: "Claude APIとPythonで「めんどくさい」を自動化する実践ガイド"
url: "https://zenn.dev/soushu/articles/2026-03-26-claude-api-python"
source: "zenn"
category: "ai-workflow"
tags: ["API", "Python", "zenn"]
date_published: "2026-03-26"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

## はじめに：自動化は「怠惰」じゃなく「投資」

個人開発をしていると、繰り返し発生する作業に時間を奪われがちです。ドキュメントの整理、データの変換、定型メールの下書き、コードレビューの初期チェック……。どれも1回あたりは数分で終わるけれど、積み重なると無視できない時間になります。

私自身、暗号資産関連のツール開発や運用をしながら、こうした「小さなめんどくさい」をClaude APIとPythonで片っ端から自動化してきました。この記事では、実際に使っているパターンをベースに、Claude APIを活用した自動化の始め方と実践的なTipsを紹介します。

## Claude APIを選ぶ理由

LLMのAPIはOpenAI、Gemini、Claudeなど選択肢が増えてきましたが、私がClaude APIをメインで使っている理由はシンプルです。

* **指示への忠実度が高い**：「JSON形式で出力して」と言えば、余計な前置きなしにJSONを返してくれる確率が高い
* **長文コンテキストに強い**：大量のログやドキュメントをまとめて投げても安定している
* **コードの生成品質**：Pythonのコード生成において、そのまま動くコードが返ってくることが多い

もちろんタスクによって使い分けるのがベストですが、「まず1つ選んで自動化を始める」ならClaude APIはかなり扱いやすいです。

## 最小構成：PythonからClaude APIを叩く

まずは基本の形を押さえましょう。`anthropic`パッケージを使います。

```
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Pythonでファイルサイズを人間が読みやすい形式に変換する関数を書いて"}
    ]
)

print(message.content[0].text)
```

これだけで動きます。ここから先は、この基本形をどうやって「実用的な自動化」に育てるかの話です。

## 実践パターン3選

### パターン1：ログ解析の自動要約

開発中のツールのログが溜まったとき、目視で追うのは限界があります。私はこんなスクリプトを回しています。

```
def summarize_logs(log_text: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system="あなたはシステムログの解析者です。エラーや警告を優先的に抽出し、箇条書きで要約してください。正常な動作は省略してください。",
        messages=[
            {"role": "user", "content": f"以下のログを解析してください:\n\n{log_text}"}
        ]
    )
    return message.content[0].text
```

ポイントは**systemプロンプトで役割と出力形式を明確にすること**です。「箇条書きで」「正常な動作は省略して」のような指示を入れると、出力の安定度が大きく上がります。

### パターン2：CSVデータの前処理・分類

手動で分類していたデータの仕分けも、Claude APIに任せられます。

```
import csv
import json

def classify_transactions(csv_path: str) -> list[dict]:
    with open(csv_path, "r") as f:
        raw_data = f.read()

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system="CSVデータの各行を分析し、カテゴリを付与してJSON配列で返してください。カテゴリは 'income', 'expense', 'transfer', 'unknown' のいずれかです。",
        messages=[
            {"role": "user", "content": raw_data}
        ]
    )

    return json.loads(message.content[0].text)
```

LLMの出力をプログラムで後続処理する場合、**JSON出力を明示的に指示する**のが鉄則です。Claude はこの指示への追従性が高いので助かっています。

### パターン3：定型ドキュメントの下書き生成

READMEの更新、リリースノートの作成、技術ブログの下書きなど、「書く内容は決まっているけど文章にするのがめんどくさい」系のタスクです。

```
def generate_release_note(changes: list[str], version: str) -> str:
    changes_text = "\n".join(f"- {c}" for c in changes)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system="あなたは開発者向けのテクニカルライターです。簡潔で読みやすいリリースノートを書いてください。",
        messages=[
            {"role": "user", "content": f"バージョン {version} のリリースノートを作成してください。変更点:\n{changes_text}"}
        ]
    )
    return message.content[0].text
```

出力をそのまま使うのではなく、**下書きとして生成→人間が確認・修正**のフローにすると、品質を保ちつつ時間を大幅に短縮できます。

## 自動化する上でのTips

### コストを意識する

Claude APIは従量課金です。何も考えずに大量リクエストを投げると請求が膨らみます。

* **`max_tokens`を適切に絞る**：不必要に大きな値を設定しない
* **モデルを使い分ける**：単純な分類タスクならHaikuで十分。高度な推論が必要なときだけSonnetやOpusを使う
* **キャッシュを活用する**：同じ入力に対して何度もAPIを叩かない仕組みを入れる

### エラーハンドリングを忘れない

APIは必ず失敗します。レートリミット、タイムアウト、予期しない出力形式。本番運用するスクリプトにはリトライ処理を入れましょう。

```
import time

def call_with_retry(func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except anthropic.RateLimitError:
            wait = 2 ** i
            print(f"Rate limited. Retrying in {wait}s...")
            time.sleep(wait)
    raise Exception("Max retries exceeded")
```

### プロンプトはコードと同じく管理する

プロンプトが散在すると、どれが最新か分からなくなります。私はプロンプトを別ファイル（YAML or テキスト）に切り出して、Gitで管理しています。プロンプトのバージョニングは、地味ですが後で確実に効いてきます。

## まとめ：小さく始めて、育てていく

自動化で大事なのは、最初から完璧なシステムを作ろうとしないことです。

1. まず、繰り返している作業を1つ選ぶ
2. Pythonスクリプト + Claude APIで最小限の自動化を書く
3. 動いたら少しずつ改善する

私もETHの定期購入を自動化するツールや、ランサーズの案件を自動スクリーニングしてClaude APIで提案文まで生成するツールを運用していますが、どちらも最初はほんの数十行のスクリプトから始まりました。自動化は一度軌道に乗ると、「次はこれも自動化できるんじゃないか」と連鎖的にアイデアが湧いてきます。

Claude APIは、その最初の一歩を踏み出すハードルがかなり低いツールです。まだ触ったことがない方は、ぜひ「自分の作業の中で一番めんどくさいこと」を1つ選んで、今日から自動化を始めてみてください。
