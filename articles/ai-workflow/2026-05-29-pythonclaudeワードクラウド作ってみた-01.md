---
id: "2026-05-29-pythonclaudeワードクラウド作ってみた-01"
title: "[Python・Claude]ワードクラウド作ってみた"
url: "https://qiita.com/biyorasu/items/9c06843665eb22777328"
source: "qiita"
category: "ai-workflow"
tags: ["API", "VSCode", "Python", "qiita"]
date_published: "2026-05-29"
date_collected: "2026-05-30"
summary_by: "auto-rss"
query: ""
---

今回はPythonとClaudeを使ってワードクラウド生成アプリを作成しました。

### そもそもワードクラウドってなんですか?
ワードクラウドは、文章やテキストデータから抜き出した単語を出現する頻度の高さに応じて文字の大きさにして、視覚的に表現するテキスト分析の手法になります。

### プログラミング

#### 準備
使用言語:Python
フレームワーク:Streamlit
使用ツール:Claude(生成AI)
実行環境:vsCode
その他:Claudeに対するプロンプト

#### プログラミング

CLaudeで全て生成はせず、まずはPythonで下書き的な形のプログラムを作りました。

```pyton:word_cloud_app_model.py

import streamlit as st
from urllib.parse import urlparse
#クエリパラメータ
query_params = st.query_params
default_url = query_params.get("my_url", "")
#ワードクラウド
st.title("ワードクラウド生成アプリ")


#この辺りにワードクラウドを生成するために出力するぶひんがほしい
#文章挿入用のテキストエリア
st.text_area("文章を入力")
#url挿入用のテキストボックス
url = st.text_input("URLを入力",value=default_url)

if url:
    # URLの解析
    parsed_url = urlparse(url)
    if parsed_url.scheme and parsed_url.netloc:
        # クエリパラメータを更新
        st.query_params["my_url"] = url
        st.write(f"アクセス中のURL: {url}")
    else:
        st.warning("URLを入力してください。")
```
以下のプロンプトと先述したプログラムをClaoudeに読み込ませました。

```txt:プロンプト.txt
WordCloud.pyを元にワードクラウドを生成するアプリを作りたいです。使用は以下の通りです。
・使用言語はPython
・フレームワークはStreamlit
・実行環境はvscode
・タイトルはワードクラウド生成アプリ
・ソースコード11行目あたりからワードクラウドを出力する部品を作りたい
・ワードクラウドを出力する部品と入力フォームの間は1行開ける
・ワードクラウドに出力するために必要なラジオボタン付き入力ボックスフォームを2種類作る。種類は以下のとおりである
1.文章入力用のテキストエリア
2.url読み込み用テキストボックス
・ラジオボタン付き入力ボックスフォームの入力内容を送信するボタンの名前は生成。背景色は青、文字の色は白とする

```
その後、助動詞を除外する選択肢を追加するなど、プログラムの実行と修正を繰り返して完成したプログラムとワードクラウドがこちらになります。

```python:WordCloud_app.py
import streamlit as st
from urllib.parse import urlparse

# クエリパラメータ
query_params = st.query_params
default_url = query_params.get("my_url", "")

# ワードクラウド
st.title("ワードクラウド生成アプリ")

# ワードクラウド出力エリア（プレースホルダー）
wordcloud_placeholder = st.empty()

# 入力フォームとの間に1行開ける
st.write("")

# ラジオボタンで入力方式を選択
input_mode = st.radio(
    "入力方式を選択してください",
    options=["文章入力", "URL読み込み"],
    horizontal=True,
)

# 選択に応じた入力フォームを表示
if input_mode == "文章入力":
    user_text = st.text_area("文章を入力", height=200, placeholder="ここにテキストを入力してください...")
    input_url = ""
else:
    user_text = ""
    input_url = st.text_input("URLを入力", value=default_url, placeholder="https://example.com")

    if input_url:
        parsed_url = urlparse(input_url)
        if parsed_url.scheme and parsed_url.netloc:
            st.query_params["my_url"] = input_url
            st.write(f"アクセス中のURL: {input_url}")
        else:
            st.warning("有効なURLを入力してください。")

# 助動詞除去オプション
filter_auxiliary = st.checkbox("助動詞を除去する（れる・られる・する・いる など）", value=True)

# 生成ボタン（青背景・白文字）
st.markdown(
    """
    <style>
    div.stButton > button {
        background-color: #1a73e8;
        color: white;
        border: none;
        padding: 0.5em 2em;
        font-size: 1rem;
        border-radius: 6px;
        cursor: pointer;
    }
    div.stButton > button:hover {
        background-color: #1558b0;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

generate_btn = st.button("生成")

# ボタン押下時の処理
if generate_btn:
    # ライブラリのインポート（エラーハンドリング）
    try:
        from wordcloud import WordCloud
        import matplotlib.pyplot as plt
        WORDCLOUD_AVAILABLE = True
    except ImportError:
        WORDCLOUD_AVAILABLE = False
        st.error("wordcloud と matplotlib が必要です。`pip install wordcloud matplotlib` を実行してください。")

    try:
        from janome.tokenizer import Tokenizer
        JANOME_AVAILABLE = True
    except ImportError:
        JANOME_AVAILABLE = False

    try:
        import requests
        from bs4 import BeautifulSoup
        SCRAPING_AVAILABLE = True
    except ImportError:
        SCRAPING_AVAILABLE = False

    combined_text = ""

    # テキスト取得
    if input_mode == "文章入力":
        combined_text = user_text.strip()
        if not combined_text:
            st.warning("テキストを入力してください。")
    else:
        if not input_url.strip():
            st.warning("URLを入力してください。")
        elif not SCRAPING_AVAILABLE:
            st.error("requests と beautifulsoup4 が必要です。`pip install requests beautifulsoup4` を実行してください。")
        else:
            try:
                with st.spinner("URLからテキストを取得中..."):
                    res = requests.get(input_url, timeout=10)
                    res.encoding = res.apparent_encoding
                    soup = BeautifulSoup(res.text, "html.parser")
                    for tag in soup(["script", "style"]):
                        tag.decompose()
                    combined_text = soup.get_text(separator=" ", strip=True)
                st.success(f"テキスト取得成功（{len(combined_text)}文字）")
            except Exception as e:
                st.error(f"URLの取得に失敗しました: {e}")

    # ワードクラウド生成
    if combined_text and WORDCLOUD_AVAILABLE:
        with st.spinner("ワードクラウドを生成中..."):

            # 日本語分かち書き
            if JANOME_AVAILABLE:
                # 助動詞リスト（base_form で照合）
                AUXILIARY_VERBS = {
                    "れる", "られる", "せる", "させる", "ない", "ぬ", "ん",
                    "た", "だ", "ます", "です", "ぬ", "まい", "う", "よう",
                    "らしい", "そう", "ようだ", "ようです", "みたいだ",
                    "てる", "でる", "いる", "おる", "ある", "くる", "する",
                    "なる", "もらう", "あげる", "くれる",
                }
                t = Tokenizer()
                tokens = t.tokenize(combined_text)
                words = []
                for token in tokens:
                    pos = token.part_of_speech.split(",")[0]
                    base = token.base_form
                    # 品詞フィルタ：名詞・動詞・形容詞のみ
                    if pos not in ("名詞", "動詞", "形容詞"):
                        continue
                    # 助動詞除去オプションが有効な場合はスキップ
                    if filter_auxiliary and base in AUXILIARY_VERBS:
                        continue
                    if len(base) > 1:
                        words.append(base)
                processed_text = " ".join(words)
            else:
                processed_text = combined_text

            if not processed_text.strip():
                st.warning("有効な単語が抽出できませんでした。")
            else:
                import os
                font_candidates = [
                    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
                    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
                    "C:/Windows/Fonts/msgothic.ttc",
                ]
                font_path = next((fp for fp in font_candidates if os.path.exists(fp)), None)

                wc_kwargs = dict(width=800, height=400, max_words=100, background_color="white")
                if font_path:
                    wc_kwargs["font_path"] = font_path

                wc = WordCloud(**wc_kwargs).generate(processed_text)
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wc, interpolation="bilinear")
                ax.axis("off")

                # 出力エリアにワードクラウドを表示
                with wordcloud_placeholder.container():
                    st.pyplot(fig)

                # ダウンロードボタン
                from io import BytesIO
                buf = BytesIO()
                fig.savefig(buf, format="png", bbox_inches="tight")
                st.download_button(
                    label="画像をダウンロード（PNG）",
                    data=buf.getvalue(),
                    file_name="wordcloud.png",
                    mime="image/png",
                )

```



ワードクラウド生成アプリの画面と生成したワードクラウドは次の通りです。

ワードクラウド生成アプリ
![スクリーンショット (57).png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4422568/d437393a-f23c-462a-a552-2444412790bb.png)

生成したワードクラウド
![Yahoo_News.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4422568/bc2f4949-7d6d-4494-9e81-cd2021c79cff.png)

ワードクラウドについてはYahooニュースの記事の文章を参考に作成しました。

https://news.yahoo.co.jp/articles/07272359babc6ee82fdf7f37440d5ef0819074dc

### 最後に

今回はテキスト分析の一種であるワードクラウドに触れてみました。
正に言葉の雲という感じで面白いと分析手法だと思いました。
