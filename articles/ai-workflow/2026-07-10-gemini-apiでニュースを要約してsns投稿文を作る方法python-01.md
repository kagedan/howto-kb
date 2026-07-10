---
id: "2026-07-10-gemini-apiでニュースを要約してsns投稿文を作る方法python-01"
title: "Gemini APIでニュースを要約してSNS投稿文を作る方法【Python】"
url: "https://qiita.com/kotajobs0/items/a1d059f6d8affb64a755"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "Gemini", "Python", "JavaScript", "qiita"]
date_published: "2026-07-10"
date_collected: "2026-07-11"
summary_by: "auto-rss"
query: ""
---

## はじめに

こんにちは。ITフィールドセールスをしている長井洸太です。

以前の記事で、複数メディアのRSSを集めてGeminiに要約させ、Xの投稿文を作る仕組みを紹介しました。ただ、Facebook・LinkedIn用の投稿を作るときは「読んでほしい記事のURLが最初から決まっている」ことが多く、わざわざRSSやスクレイピングのコードを書くほどでもありません。

そこで気づいたのが、**Geminiに記事のURLをそのまま渡すだけで、本文を読んで要約してくれる**ということでした。`requests`でHTMLを取得して`BeautifulSoup`でパースする、という処理が丸ごと不要になります。

今回は、このURL要約の仕組みと、要約結果をClaudeでSNS投稿文に整える流れを紹介します。

---

## 作ったもの

```
URL（記事リンク）を渡す
    ↓ Gemini 2.0 Flash が本文を読んで3〜5行に要約
Claude Haiku が要約をもとにFacebook投稿文を生成
    ↓
Markdownに下書き保存 → 確認 → Facebook Graph APIで投稿
```

`facebook_post_generator.py` の `summarize_url()` という関数が要約部分を担当しています。

---

## 必要なもの

```bash
pip install google-genai anthropic python-dotenv requests
```

`.env` に以下を設定します。

```env
GEMINI_API_KEY=AIza...
CLAUDE_API_KEY=sk-ant-...
```

---

## コード

### ① URLをGeminiに渡すだけで要約する

```python
from google import genai

def summarize_url(url: str) -> str:
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
以下のURLの記事を読み、要点を3〜5行で日本語で要約してください。
URL: {url}
※Markdown記号は使わずプレーンテキストで出力してください。
"""
    try:
        resp = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        return resp.text.replace("**", "").strip()
    except Exception:
        return ""
```

`requests.get()` も `BeautifulSoup` も出てきません。URLを文字列としてプロンプトに埋め込んでいるだけです。それでも、記事の見出しや本文の要点を拾って要約が返ってきます。

### ② 要約をもとにClaudeで投稿文を生成

```python
import anthropic

def generate_facebook_post(url_summary: str, source_url: str) -> str:
    client = anthropic.Anthropic(api_key=CLAUDE_KEY)
    prompt = f"""
以下の記事要約をもとに、Facebook投稿文を日本語で作成してください。

【記事要約】
{url_summary}

【出典URL】
{source_url}

【条件】
・300文字以内
・ビジネスパーソン向けに分かりやすく
・最後に出典URLを1行で記載
・投稿文のみを出力
"""
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()
```

役割は明確に分かれています。**Geminiは「読んで要約する」係、Claudeは「読者向けに書き直す」係**です。

---

## 使い方

```bash
# 紹介したいURLを指定して下書き生成
python scripts/facebook/facebook_post_generator.py --generate --url https://example.com/article

# 生成した下書きを投稿
python scripts/facebook/facebook_post_generator.py --publish --draft-id 2026-07-10
```

`--url` を付けずに `--theme` だけ指定した場合は、URL要約の代わりにGemini自身にトレンドを選定させる `collect_trends()` が呼ばれます（こちらはニュースサイトの巡回ではなく、Geminiに直接「今日のビジネストレンドを3つ挙げて」と聞くパターンです）。

---

## 出力サンプル

```
🔎 URL要約中: https://example.com/article-about-remote-work ...

【要約結果】
リモートワークを導入した企業のうち、生産性が向上したと回答した割合は
前年より15ポイント増加。特に「コアタイムなしのフルフレックス」を
採用した企業で顕著な伸びが見られた。一方で新入社員の定着率には
課題が残るとの指摘も。

✍️ Claudeで投稿文を生成中...
💾 下書き保存: Earning/facebook-posts/2026-07/2026-07-10_draft.md
```

---

## やってみてわかったこと

### URLを渡すだけで要約できるのは楽だが、精度は過信しない

スクレイピングのコードを書かなくていいのは大きなメリットですが、Geminiが本文を正確に読み取れているかは記事によってばらつきがあります。特に会員限定記事やJavaScriptで本文を描画するサイトは、要約が薄くなったり、それらしい一般論で埋められたりすることがありました。**投稿前に必ず要約と元記事を見比べる**運用にしています。

### モデルのバージョンがスクリプトごとに違っていた

Facebook用は`gemini-2.0-flash`、X用は`gemini-2.5-flash`と、作った時期によって使っているモデルが違うことに気づきました。動くから放置していましたが、精度・コストの両面で一度揃えたほうが良さそうです。地味に「動いているものは触らない」の弊害だと感じました。

### 「収集」と「要約」を分けて考えるようになった

以前はRSSやスクレイピングで情報を「集める」ことに気を取られていましたが、URLが1つ分かっているだけなら「集める」工程はそもそも不要です。目的（ニュース全体から選ぶのか、決まった記事を紹介するのか）によって、Geminiの使い方を変えるべきだと学びました。

---

## おわりに

「スクレイピングしなきゃ」と思い込んでいた処理が、実はAPIに投げるだけで済むケースは他にもありそうです。作業を自動化するときほど、一度「本当にこの前処理は必要か」を疑ってみると近道が見つかることがあります。

毎日X（Twitter）・Instagram・LinkedInで自動化ツールや開発の話を投稿しています。ぜひ繋がりましょう！

---

## 参考

- [Gemini API ドキュメント](https://ai.google.dev/gemini-api/docs)
- [Anthropic Claude API ドキュメント](https://docs.anthropic.com/)
