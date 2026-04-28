---
id: "2026-04-27-python-claude-api非エンジニアでもできるclaude-を使った自動要約ツールの作り方-01"
title: "【Python × Claude API】非エンジニアでもできる！Claude を使った自動要約ツールの作り方"
url: "https://qiita.com/hjvideocom/items/ffee301a582df8eaf422"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "Gemini", "GPT", "Python", "qiita"]
date_published: "2026-04-27"
date_collected: "2026-04-28"
summary_by: "auto-rss"
query: ""
---

# 【Python × Claude API】非エンジニアでもできる！Claude を使った自動要約ツールの作り方

## はじめに

最近、AI ツールの進化がすごいですよね。ChatGPT、Gemini、そして Claude——毎日のように新しい機能が追加されています。

私は普段 Claude をブラウザで使っていますが、ある日ふと思いました。

**「これ、Python から API で呼び出せば、もっと便利に使えるのでは？」**

そこで今回は、Python + Claude API を使って**テキスト自動要約ツール**を作ってみました。初心者でも 10 分で動かせる内容にまとめたので、ぜひ試してみてください。

## 対象読者

- Python の基本的な文法がわかる方
- Claude API を触ったことがない方
- AI を使った自動化に興味がある方

## 完成イメージ

```
$ python summarize.py input.txt

📝 要約結果:
この記事は、Pythonを使ったWebスクレイピングの基本的な手法について
解説しています。主にrequestsとBeautifulSoupの使い方を...
```

長い文章を渡すと、Claude が自動で要約してくれるシンプルなツールです。

## 環境構築

### 必要なもの

| 項目 | バージョン |
|------|-----------|
| Python | 3.9 以上 |
| anthropic（Python SDK） | 最新版 |

### API キーの取得

1. [Anthropic Console](https://console.anthropic.com/) にアクセス
2. アカウントを作成（またはログイン）
3. 「API Keys」から新しいキーを発行
4. キーをコピーして保存（⚠️ 一度しか表示されません）

### インストール

```bash
pip install anthropic
```

## コードの全体像

```python
import anthropic
import sys


def summarize_text(text: str) -> str:
    """Claude API を使ってテキストを要約する"""
    client = anthropic.Anthropic(
        api_key="YOUR_API_KEY"  # ← ここにAPIキーを入れる（本番では環境変数推奨）
    )

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"以下のテキストを日本語で300文字以内に要約してください。\n\n{text}",
            }
        ],
    )

    return message.content[0].text


def main():
    # コマンドライン引数からファイルを読み込む
    if len(sys.argv) < 2:
        print("使い方: python summarize.py <ファイル名>")
        sys.exit(1)

    filepath = sys.argv[1]

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    print("⏳ Claude に要約を依頼中...")
    result = summarize_text(text)
    print(f"\n📝 要約結果:\n{result}")


if __name__ == "__main__":
    main()
```

## コードのポイント解説

### 1. クライアントの初期化

```python
client = anthropic.Anthropic(api_key="YOUR_API_KEY")
```

本番環境では、API キーをコードに直書きせず、**環境変数**から読み込むのがベストプラクティスです。

```bash
export ANTHROPIC_API_KEY="sk-ant-xxxxx"
```

```python
# 環境変数から自動で読み込まれる
client = anthropic.Anthropic()
```

### 2. モデルの選択

```python
model="claude-sonnet-4-20250514"
```

Claude には複数のモデルがあります。

| モデル | 特徴 | 用途 |
|--------|------|------|
| claude-opus-4-6 | 最高性能・高コスト | 複雑な分析・創作 |
| claude-sonnet-4-6 | バランス型 | 一般的なタスク |
| claude-haiku-4-5 | 高速・低コスト | 軽量タスク・大量処理 |

今回のような要約タスクなら **Sonnet** で十分です。

### 3. プロンプトの工夫

```python
content=f"以下のテキストを日本語で300文字以内に要約してください。\n\n{text}"
```

プロンプトのコツ：

- **言語を指定する**（「日本語で」）→ 入力が英語でも日本語で返してくれる
- **文字数を指定する**（「300文字以内」）→ 出力の長さをコントロール
- **具体的に指示する** → 曖昧な指示だと出力もブレる

## 応用：もっと便利にする

### 箇条書きモードを追加

```python
def summarize_text(text: str, bullet: bool = False) -> str:
    if bullet:
        prompt = f"以下のテキストの要点を5つの箇条書きにまとめてください。\n\n{text}"
    else:
        prompt = f"以下のテキストを日本語で300文字以内に要約してください。\n\n{text}"

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
```

### 複数ファイルの一括処理

```python
import glob

files = glob.glob("articles/*.txt")
for filepath in files:
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    result = summarize_text(text)
    print(f"📄 {filepath}\n{result}\n{'='*50}")
```

## 料金の目安

Claude API は従量課金です。Sonnet の場合：

- **入力**: $3 / 100万トークン
- **出力**: $15 / 100万トークン

日本語の場合、1文字 ≒ 1〜2トークン程度です。1,000文字の記事を要約すると、**1回あたり約 0.01ドル（約1.5円）** 程度なので、個人利用なら非常にリーズナブルです。

## ハマりやすいポイント

### ❌ `AuthenticationError` が出る

→ API キーが間違っている、または期限切れ。Console で再発行してください。

### ❌ `RateLimitError` が出る

→ 短時間にリクエストを送りすぎ。`time.sleep(1)` を入れて間隔を空けましょう。

### ❌ 長いテキストでエラーになる

→ モデルの入力上限を超えている可能性があります。テキストを分割して送りましょう。

```python
# テキストを分割する簡易的な方法
def chunk_text(text: str, max_chars: int = 10000) -> list[str]:
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
```

## まとめ

今回は Python × Claude API で自動要約ツールを作りました。

- ✅ `anthropic` ライブラリで簡単に API を呼び出せる
- ✅ プロンプトの書き方次第で出力を柔軟にコントロールできる
- ✅ 料金も安く、個人開発で気軽に試せる

Claude API は要約以外にも、翻訳・コード生成・データ抽出など、さまざまなタスクに使えます。ぜひ自分なりのツールを作ってみてください！

## 参考リンク

- [Anthropic 公式ドキュメント](https://docs.anthropic.com/)
- [Claude モデル一覧](https://docs.anthropic.com/en/docs/about-claude/models)
- [Anthropic Python SDK（GitHub）](https://github.com/anthropics/anthropic-sdk-python)
---
もし参考になれば、X でもAI活用の tips を発信しています → [@你的帐号](https://hjvideo.com/)
