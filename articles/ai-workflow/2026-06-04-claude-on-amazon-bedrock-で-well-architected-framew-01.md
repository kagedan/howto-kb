---
id: "2026-06-04-claude-on-amazon-bedrock-で-well-architected-framew-01"
title: "Claude on Amazon Bedrock で Well-Architected Framework Review アシスタントを作ってみた"
url: "https://qiita.com/yuta_satake/items/1398f4e0be99801b519d"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "Python", "qiita"]
date_published: "2026-06-04"
date_collected: "2026-06-04"
summary_by: "auto-rss"
query: ""
---

## 1. はじめに

よく語られる話ですが、「知っている」と「できている」は別物です。

社内で AWS Well-Architected Review が話題になったとき、「6 本柱、全部ちゃんと見られているかな」と思いました。設計時は意識しているつもりでも、レビューを体系的にやろうとすると意外と抜け漏れが出るものです。

そこで、システム構成を入力するだけで 6 本柱を自動レビューしてくれるアシスタントを Claude on Amazon Bedrock で作ってみました。

Claude は初心者ですが、AWS の知識を活かしてどこまで作れるか——その記録です。

---

## 2. 作ったもの

システム構成の概要をテキストで入力すると、Well-Architected Framework の 6 本柱でレビューし、優先度の高い改善事項トップ 3 を出力します。

![スクリーンショット 2026-06-04 1.19.18.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3333253/1df32ed9-7e96-4902-b16d-18d6d6a0da16.png)

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3333253/5b36fec2-a22e-4f60-9286-546c4d4cb7a0.png)

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3333253/d627817f-6e1e-43dd-b430-fd39d6879c49.png)

---

## 3. 技術スタック
Steamlit については [2024 年のアドベントカレンダー](https://qiita.com/yuta_satake/items/47ebe23aa814c084fbd2)で触りました。UX がPython で簡単に作れちゃうのは本当に便利です。

| 要素 | 使用技術 |
|---|---|
| AI モデル | Claude Sonnet 4.6（Amazon Bedrock） |
| 接続方法 | boto3（`converse_stream` API） |
| UX | Streamlit |
| 実行環境 | ローカル Mac（Python 3.9） |

---

## 4. 実装のポイント

### 4.1. Inference Profile を使う

Bedrock でモデルを呼び出す際は、モデル ID ではなく Inference Profile ID を使います。

```python
MODEL_ID = "us.anthropic.claude-sonnet-4-6"
```

直接モデル ID を指定するとリージョンによってエラーが発生します。Inference Profile はクロスリージョンで自動的にルーティングしてくれます（利用可能な ID は後述の方法で確認できます）

### 4.2. Streaming でリアルタイム表示

`converse` ではなく `converse_stream` を使うことで、生成中のテキストをリアルタイムに表示できます。

```python
response = client.converse_stream(
    modelId=MODEL_ID,
    system=[...],
    messages=messages,
    inferenceConfig={"maxTokens": 4000, "temperature": 0.3}
)

for event in response["stream"]:
    if "contentBlockDelta" in event:
        delta = event["contentBlockDelta"].get("delta", {})
        if "text" in delta:
            yield delta["text"]
```

Streamlit 側では `st.empty()` を使って差分更新します：

```python
result = st.empty()
full_text = ""

for chunk in review_architecture(architecture_input):
    full_text += chunk
    result.markdown(full_text)
```

### 4.3. Prompt Caching でコスト削減

Well-Architected Framework の指示を含むシステムプロンプトはリクエストごとに変わりません。Prompt Caching を使うとシステムプロンプトを 5 分間キャッシュし、入力コストを最大 90% 削減できます。

```python
system=[
    {"text": SYSTEM_PROMPT},
    {"cachePoint": {"type": "default"}}  # ここまでをキャッシュ
]
```

キャッシュポイントより前のコンテンツが対象です。`cache_read_input_tokens` が増えていればキャッシュが効いているようです。

---

## 5. Inference Profile ID の確認方法

利用可能な ID は以下のコードで確認できます：

```python
import boto3

bedrock = boto3.client("bedrock", region_name="us-east-1")
response = bedrock.list_inference_profiles()

for profile in response.get("inferenceProfileSummaries", []):
    print(profile.get("inferenceProfileId", ""))
```

---

## 6. 全コード

```python
import boto3
import streamlit as st
import warnings
warnings.filterwarnings("ignore")

client = boto3.client("bedrock-runtime", region_name="us-east-1")
MODEL_ID = "us.anthropic.claude-sonnet-4-6"

SYSTEM_PROMPT = """あなたは AWS Well-Architected Framework の専門家レビュアーです。
（省略 - 上記参照）"""


def review_architecture(architecture_description: str):
    messages = [
        {
            "role": "user",
            "content": [{"text": f"以下のシステム構成をレビューしてください。\n\n{architecture_description}"}]
        }
    ]
    response = client.converse_stream(
        modelId=MODEL_ID,
        system=[
            {"text": SYSTEM_PROMPT},
            {"cachePoint": {"type": "default"}}
        ],
        messages=messages,
        inferenceConfig={"maxTokens": 4000, "temperature": 0.3}
    )
    for event in response["stream"]:
        if "contentBlockDelta" in event:
            delta = event["contentBlockDelta"].get("delta", {})
            if "text" in delta:
                yield delta["text"]


st.set_page_config(page_title="Well-Architected Review アシスタント", page_icon="🏗️", layout="wide")
st.title("🏗️ Well-Architected Review アシスタント")
st.caption("Powered by Claude on Amazon Bedrock")
st.markdown("AWS Well-Architected Framework の **6 本柱** でシステム構成を自動レビューします。")

architecture_input = st.text_area("システム構成の概要を入力してください", height=250)

if st.button("レビュー開始 ▶", type="primary", disabled=not architecture_input):
    st.markdown("---")
    st.subheader("📋 Well-Architected レビュー結果")
    result = st.empty()
    full_text = ""
    with st.spinner("Claude がレビュー中..."):
        for chunk in review_architecture(architecture_input):
            full_text += chunk
            result.markdown(full_text)
    st.success("✅ レビュー完了！")
```

---

## 7. 実行方法

```bash
pip3 install boto3 streamlit
aws configure  # 個人アカウントの認証情報を設定
python3 -m streamlit run app.py
```

---

## 8. コスト

Claude Sonnet 4.6 の料金は `$3 / 100万入力トークン`、`$15 / 100万出力トークン`。
1 回のレビューあたり約 6円なので、躊躇することなくレビューができます。

| 利用回数 | 概算コスト |
|---|---|
| 10回 | 約 60円 |
| 100回 | 約 600円 |

Prompt Caching が効くと連続実行時は入力コストがさらに下がります。

---

## 9. まとめ

Claude on Amazon Bedrock を使うことで、約 80 行のコード（システムプロンプト除く）で実用的な Well-Architected Review アシスタントが作れました。

**実装のポイント：**
- `converse_stream` でリアルタイムストリーミング
- `cachePoint` でシステムプロンプトをキャッシュ
- Inference Profile ID でリージョン問題を回避

---

## 参考リンク

- [Amazon Bedrock ドキュメント](https://docs.aws.amazon.com/bedrock/)
- [Claude with Amazon Bedrock e-learning](https://anthropic.skilljar.com/claude-in-amazon-bedrock)
- [前回記事①： Claude 公式 e-learning 2本を受講してわかった「Bedrock で Claude を使う」ための5つの勘所](https://qiita.com/yuta_satake/items/8939f42f4585374a8543)
- [前回記事②： AWS Certified Generative AI Developer - Professional (AIP-C01) 受験・合格記](https://qiita.com/yuta_satake/items/4af2aaf5963b2b9ec351)
