---
id: "2026-06-15-amazon-bedrock-の-fable-5-で-pdf-チャート画像の認識精度を検証する-01"
title: "Amazon Bedrock の Fable 5 で PDF チャート画像の認識精度を検証する"
url: "https://qiita.com/revsystem/items/dd9688ca06d952efecf1"
source: "qiita"
category: "construction"
tags: ["prompt-engineering", "API", "LLM", "Python", "qiita"]
date_published: "2026-06-15"
date_collected: "2026-06-16"
summary_by: "auto-rss"
query: ""
---

## はじめに

2026 年 4 月に Opus 4.7 が公開された際、[Amazon Bedrock の Claude モデルで PDF チャート画像の認識精度を検証する](https://nulab.com/ja/blog/nulab/amazon-bedrock-claude-pdf-chart-recognition/)という記事を書きました。この記事では、Sonnet 4.6、Opus 4.6、Opus 4.7 の 3 つのモデルで PDF チャート画像の認識精度を検証しています。その後、2026 年 5 月に Opus 4.8、6 月に Claude Fable 5 が公開されました。そこで、これらの新しいモデルでも同じ検証を行いました。

AWS News Blog「[Anthropic Claude Fable 5 on AWS: Mythos-class capabilities with built-in safeguards now available](https://aws.amazon.com/blogs/aws/anthropic-claude-fable-5-on-aws-mythos-class-capabilities-with-built-in-safeguards-now-available/)」では、以下のように紹介されており、PDF 内の図やチャートの認識精度が期待できます。

> **Advanced vision capabilities** — Claude Fable 5 understands diagrams, charts, and tables nested in files and PDFs. This opens up research and document-heavy work in finance, legal, analytics, architecture, and gaming.

> **高度なビジョン機能** — Claude Fable 5 は、ファイルや PDF にネストされた図、チャート、表を理解します。これにより、財務、法務、分析、建築、ゲームにおけるリサーチや文書を多用する作業が可能になります。

前回の記事との比較を行うため、同一の PDF ファイルを使用します。スクリプトは、今回使用するモデルを呼び出す部分と DPI 変更を行う部分のみを変更しました。

:::note info
2026 年 6 月 12 日、アメリカ政府の輸出管理規制により Anthropic は `Claude Fable 5` へのアクセスを停止しました。このため、十分な検証が行えませんでした。本記事では、取得した数回分のデータで前回の記事との比較を行います。
:::

## 参考情報

https://aws.amazon.com/blogs/aws/anthropic-claude-fable-5-on-aws-mythos-class-capabilities-with-built-in-safeguards-now-available/

https://aws.amazon.com/jp/blogs/news/anthropic-claude-fable-5-on-aws-mythos-class-capabilities-with-built-in-safeguards-now-available/

https://docs.aws.amazon.com/bedrock/latest/userguide/data-retention.html

https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-fable-5.html

https://docs.aws.amazon.com/ja_jp/bedrock/latest/userguide/claude-messages-adaptive-thinking.html

https://nulab.com/ja/blog/nulab/amazon-bedrock-claude-pdf-chart-recognition/

https://qiita.com/revsystem/items/707ff4519d33da406922

## 検証内容

本記事では、次の内容を検証します。

1. Claude Opus 4.8 と Claude Fable 5 は、Opus 4.7 と比べて、PDF 内のチャート画像を具体的にどの程度詳細に読めるのか

1. PDF を丸ごと LLM に渡す方式（Approach 1）と、画像化して RAG を構築する方式（Approach 2）でどう変わるのか

1. Approach 2 の場合、前回の記事の DPI 300 と今回の記事の DPI 500 で精度にどの程度影響するのか

## 検証対象

検証対象 PDF は、[前回の記事](https://nulab.com/ja/blog/nulab/amazon-bedrock-claude-pdf-chart-recognition/)で使用したものと同じです。総務省「[情報通信白書令和7年版 PDF版](https://www.soumu.go.jp/johotsusintokei/whitepaper/ja/r07/pdf/index.html)」第Ⅰ部第 1 章第 2 節「[AIの爆発的な進展の動向](https://www.soumu.go.jp/johotsusintokei/whitepaper/ja/r07/pdf/n1120000.pdf)」の 12 ページを対象とします。主要チャートとして「図表Ⅰ-1-2-4 AI活力ランキング上位10カ国（2023年）」を使用します。このチャートは 8 つの評価カテゴリー（R&D、Responsible AI、Economy、Education、Diversity、Policy and Governance、Public Opinion、Infrastructure）で構成された横棒スタックチャートです。細部の読み取りが問われる題材です。

:::note info
本記事の検証結果は単発実行によるものです。LLM の出力には確率的な揺らぎがあり、再実行で結果が変わる可能性があります。Opus 4.7 以降では temperature（および top_p、top_k）が廃止され、thinking と effort で制御するようになりました（Amazon Bedrock のドキュメント[Claude Opus 4.7](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-7.html#model-card-anthropic-claude-opus-4-7-parameters-change) 参照）。また、Fable 5 では temperature は 1.0 もしくは未設定のみ許可されています（top_p は 0.99 以上 1.0 未満または未設定、top_k は非対応。Amazon Bedrock のドキュメント[Claude Fable 5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-fable-5.html) 参照）。そのため、本記事では temperature を設定せず、thinking と effort を設定しています。
:::

![AI活力ランキング上位10カ国（2023年）](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/61809/fce0714f-1208-4671-8f13-901a8d4d5579.png)
図表Ⅰ-1-2-4 AI活力ランキング上位10カ国（2023年）

## 検証環境

### 使用サービスとモデル

| 項目 | 値 |
| :-- | :-- |
| リージョン | us-east-1 |
| 推論モデル | `us.anthropic.claude-opus-4-7`, `us.anthropic.claude-opus-4-8`, `us.anthropic.claude-fable-5` |
| 埋め込みモデル | `amazon.titan-embed-text-v2:0` |
| ベクトルストア | Amazon S3 Vectors |

### スクリプト配置

```text
Bedrock-Claude/
├── data/
│   └── n1120000.pdf  # 情報通信白書令和7年版 PDF版
├── scripts/
│   ├── common.py
│   ├── questions.json
│   ├── approach1_pdf_direct.py
│   ├── approach2_ingest.py
│   ├── approach2_query.py
│   └── build_summary.py
├── results/
│   ├── approach1-pdf-direct.{md,json}
│   ├── approach2-rag_ingest-*_answer-*.{md,json}
│   └── summary.md
├── requirements.txt
└── README.md
```

### Python 環境

```python:requirements.txt
boto3>=1.35
pdf2image>=1.17
Pillow>=10.0
```

`pdf2image` がシステム依存として `poppler-utils` を必要とします。

```console
sudo apt install poppler-utils
uv venv
uv pip install -r requirements.txt
```

### S3 Vectors バケットの作成

Approach 2 の事前準備として、S3 Vectors バケットを 1 つ作成しておきます。インデックスは Python スクリプト内で作成・削除します。

```console
aws s3vectors create-vector-bucket \
  --vector-bucket-name bedrock-claude-chart \
  --profile YOUR_PROFILE --region us-east-1
```

### Data Retention API の有効化

Fable 5 モデルを呼び出す前に、Data Retention API を使用して `provider_data_share` を設定し、データ共有を有効にする必要があります。Bedrock の API Keys から `Generate Short-Term API Key` をクリックして、短期的な API キーを発行します。そのキーを使って、以下のように Data Retention API を実行します。

![short-term APIキーの発行](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/61809/23b49078-759d-4b27-b852-82aecefad69c.png)

```console
curl -X PUT https://bedrock.us-east-1.amazonaws.com/data-retention \
  -H "Authorization: Bearer YOUR_SHORT_TERM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "mode": "provider_data_share" }'
```

### 評価質問

評価質問は 1 問に絞り、人手で回答の正誤と粒度を判定します。複数の評価質問で検証を行う場合は q02、q03 … というように追加します。

```json:questions.json
[
  {
    "id": "q01",
    "question": "AI活力ランキングで5位の国はどこですか? そのほかの順位も教えてください。また、それぞれの国はどのような分野で優れているかも教えてください。",
    "notes": "AI活力ランキングの基本読み取り"
  }
]
```

### 共通コード

`scripts/common.py` に Bedrock/S3 Vectors クライアントの初期化と、Converse/埋め込み/チャンク分割のユーティリティをまとめます。
`DPI=300` で、PDF を画像化する際の DPI を設定しています。DPI 500 で画像化する場合は `DPI=500` に変更します。

<details><summary>scripts/common.py</summary>

```python:scripts/common.py
"""Bedrock-Claude PDFチャート認識検証の共通ユーティリティ。"""
import json
import time
from pathlib import Path

import boto3

REGION = "us-east-1"
PROFILE = "YOUR_PROFILE"

MODELS = {
    "opus-4-7":   "us.anthropic.claude-opus-4-7",
    "opus-4-8":   "us.anthropic.claude-opus-4-8",
    "fable-5":    "us.anthropic.claude-fable-5",
}

EMBED_MODEL_ID = "amazon.titan-embed-text-v2:0"
EMBED_DIM = 1024
CHUNK_SIZE = 1024
CHUNK_OVERLAP = CHUNK_SIZE // 10  # 10%オーバーラップでチャンク境界の文脈を保持
DPI = 300

ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = ROOT / "data" / "n1120000.pdf"
QUESTIONS_PATH = ROOT / "scripts" / "questions.json"
RESULTS_DIR = ROOT / "results"


def session():
    """AWS SSO プロファイルを使ったセッションを返す。"""
    return boto3.Session(profile_name=PROFILE, region_name=REGION)


def bedrock_runtime():
    """Bedrock Runtime クライアントを返す。"""
    return session().client("bedrock-runtime")


def s3vectors():
    """S3 Vectors クライアントを返す。"""
    return session().client("s3vectors")


def load_questions():
    """questions.json から評価質問リストを読み込む。"""
    return json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))


def load_pdf_bytes():
    """検証対象 PDF をバイト列で返す。"""
    return PDF_PATH.read_bytes()


def converse(client, model_id, content, max_tokens=2048):
    """Bedrock Converse API を呼び出し、テキスト回答とトークン使用量を返す。

    Opus 4.8 は temperature が廃止されているため additionalModelRequestFields で
    thinking と effort を設定する。他モデルは temperature=0 で出力を固定する。
    失敗時は指数バックオフで最大3回リトライする。
    """
    inference_config = {"maxTokens": max_tokens}
    extra = {}
    if any(key in model_id for key in ("opus-4-8", "opus-4-7", "fable-5")):
        # Opus 4.7以降: temperature・top_p・top_k は Breaking Change で廃止。thinking と effort で制御する
        extra["additionalModelRequestFields"] = {
            "thinking": {"type": "adaptive"},
            "output_config": {"effort": "high"},
        }
    else:
        # Opus 4.7より古いモデル(Sonnet4.6含む): temperature=0 で出力のランダム性を抑制する
        inference_config["temperature"] = 0

    started = time.monotonic()
    for attempt in range(3):
        try:
            resp = client.converse(
                modelId=model_id,
                messages=[{"role": "user", "content": content}],
                inferenceConfig=inference_config,
                **extra,
            )
            break
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)  # 指数バックオフ: 1s → 2s
    blocks = resp["output"]["message"]["content"]
    text = next(b["text"] for b in blocks if "text" in b)
    usage = resp.get("usage", {})
    return text, {
        "input_tokens": usage.get("inputTokens", 0),
        "output_tokens": usage.get("outputTokens", 0),
        "latency_sec": round(time.monotonic() - started, 2),
    }


def embed(client, text):
    """Titan Embed Text v2 でテキストを 1024 次元のベクトルに変換する。"""
    resp = client.invoke_model(
        modelId=EMBED_MODEL_ID,
        body=json.dumps({"inputText": text, "dimensions": EMBED_DIM, "normalize": True}),
    )
    return json.loads(resp["body"].read())["embedding"]


def chunk_text(text):
    """テキストを CHUNK_SIZE 文字ごとに分割し、CHUNK_OVERLAP 文字のオーバーラップを持たせる。"""
    step = CHUNK_SIZE - CHUNK_OVERLAP
    return [text[i:i + CHUNK_SIZE] for i in range(0, len(text), step)]


def write_results(name, md, payload):
    """結果を Markdown と JSON の2形式で results/ ディレクトリに書き出す。"""
    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / f"{name}.md").write_text(md, encoding="utf-8")
    (RESULTS_DIR / f"{name}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
```

</details>

## Approach 1: PDF 直接読み取り

Bedrock Converse API の `document` ブロックに PDF のバイナリを直接渡して質問する最小構成です。

<details><summary>scripts/approach1_pdf_direct.py</summary>

```python:scripts/approach1_pdf_direct.py
"""Approach 1: Bedrock Converse API の document ブロックでPDFを直接読ませる。"""
import common


def ask(client, model_id, pdf_bytes, question):
    """PDF バイナリを document ブロックに渡してモデルに質問する。"""
    content = [
        # PDF を document ブロックとして直接渡す（Bedrock は最大 4.5MB をサポート、Claude モデルは最大 100 ページをサポート）
        {"document": {"format": "pdf", "name": "target", "source": {"bytes": pdf_bytes}}},
        {"text": question},
    ]
    return common.converse(client, model_id, content)


def to_markdown(results):
    """全モデルの回答結果を1つの Markdown レポートにまとめる。"""
    lines = ["# Approach 1: PDF直接読み取り", ""]
    any_key = next(iter(results))
    for i, row in enumerate(results[any_key]):
        q = row["question"]
        lines += [f"## {q['id']}: {q['question']}", "", f"観点: {q.get('notes', '')}", ""]
        for key, rows in results.items():
            r = rows[i]
            header = f"### {key} (in/out={r['input_tokens']}/{r['output_tokens']}, {r['latency_sec']}s)"
            lines += [header, "", r["answer"], ""]
    return "\n".join(lines)


def main():
    """3モデル × 全質問で PDF 直接読み取りを実行し、結果を保存する。"""
    client = common.bedrock_runtime()
    pdf_bytes = common.load_pdf_bytes()
    questions = common.load_questions()

    results = {}
    for key, model_id in common.MODELS.items():
        print(f"== {key} ==")
        rows = []
        for q in questions:
            print(f"  {q['id']}")
            answer, m = ask(client, model_id, pdf_bytes, q["question"])
            rows.append({"question": q, "answer": answer, **m})
        results[key] = rows

    common.write_results("approach1-pdf-direct", to_markdown(results), results)
    print("results/approach1-pdf-direct.md")


if __name__ == "__main__":
    main()
```
</details>

実行します。

```console
uv run python scripts/approach1_pdf_direct.py
```

### Approach 1 の結果

| モデル | input tokens | output tokens | latency |
|:--|:--|:--|:--|
| Opus 4.7 | 77,200 | 1,555 | 50.72s |
| Opus 4.8 | 77,195 | 1,241 | 29.39s |
| Fable 5 | 77,195 | 1,471 | 37.38s |

[前回の記事での Approach 1 の結果](https://nulab.com/ja/blog/nulab/amazon-bedrock-claude-pdf-chart-recognition/#Approach_1_%E3%81%AE%E7%B5%90%E6%9E%9C)と比較すると、Opus 4.7 の input tokens は 77,200 で、まったく同じでした。output tokens は、出力内容の揺れから今回の方が 1.5 倍ほど多い結果でした。Opus 4.8 と Fable 5 も同様の結果でした。いずれも画像を高い解像度で処理しており、その分が input tokens に反映されているようです。

回答の精度をみると、Opus 4.7 がチャートのカテゴリーごとの内容を分析して回答しているのに対し、Opus 4.8 と Fable 5 はそれが行えなかったようです。

<details><summary>Opus 4.7の結果</summary>

```markdown
# AI活力ランキング（2023年）について

## 5位の国
**アラブ首長国連邦（United Arab Emirates / UAE）** です。

## 上位10カ国の順位
スタンフォード大学HAI（Human-Centered Artificial Intelligence）が2024年11月に発表した2023年AI活力ランキングは以下のとおりです（図表Ⅰ-1-2-4）。

| 順位 | 国 |
|------|-----|
| 1位 | 米国（United States） |
| 2位 | 中国（China） |
| 3位 | 英国（United Kingdom） |
| 4位 | インド（India） |
| 5位 | アラブ首長国連邦（United Arab Emirates） |
| 6位 | フランス（France） |
| 7位 | 韓国（South Korea） |
| 8位 | ドイツ（Germany） |
| 9位 | 日本（Japan） |
| 10位 | シンガポール（Singapore） |

## 評価分野について

このランキングは、以下の8つの分野（指標）の合計で評価されています。

- **R&D**（研究開発）
- **Responsible AI**（責任あるAI）
- **Economy**（経済）
- **Education**（教育）
- **Diversity**（多様性）
- **Policy and Governance**（政策とガバナンス）
- **Public Opinion**（世論）
- **Infrastructure**（インフラ）

## 各国が優れている分野（図表より読み取れる傾向）

文書中のグラフから読み取れる範囲でお伝えします（細かい数値は本文には記載されていません）。

- **米国（1位）**：すべての指標で突出しており、特に **R&D（研究開発）、Economy（経済）、Infrastructure（インフラ）** の比重が大きく、圧倒的なリードを示しています。
- **中国（2位）**：**R&D、Economy** の領域で特に強さを発揮しており、米国と並ぶAI大国です。
- **英国（3位）**：R&D、Economy、Policy and Governanceなどでバランスの取れた高評価。
- **インド（4位）**：R&DやEconomyに加え、**Public Opinion（世論）** の面でも強みを見せています。
- **アラブ首長国連邦（5位）**：**Policy and Governance（政策とガバナンス）** や **Infrastructure** の比重が大きく、国家戦略としてAIに注力している姿勢が反映されていると考えられます。
- **日本（9位）**：米国・中国・英国といった上位国からは水をあけられている、と本文で指摘されています。

## 補足

なお、AI研究力（論文数等）でランキングしている **AIRankings** では、近年の上位は米国・中国・英国・ドイツの順で、日本は11〜12位で推移しているとされています。

※ 各国の指標別の詳細な数値や順位については、本文中には記載されていないため、グラフからの読み取りに基づく傾向の説明となります。正確な値は出典のスタンフォード大学HAIの「Global AI Vibrancy Tool」を参照する必要があります。
```

</details>

<details><summary>Opus 4.8の結果</summary>

```markdown
# AI活力ランキング（2023年）について

図表Ⅰ-1-2-4（スタンフォード大学HAI「Global AI Vibrancy Tool」）によると、**5位はアラブ首長国連邦（United Arab Emirates）**です。

## 上位10カ国の順位

| 順位 | 国名 |
|------|------|
| 1位 | アメリカ（United States） |
| 2位 | 中国（China） |
| 3位 | イギリス（United Kingdom） |
| 4位 | インド（India） |
| **5位** | **アラブ首長国連邦（United Arab Emirates）** |
| 6位 | フランス（France） |
| 7位 | 韓国（South Korea） |
| 8位 | ドイツ（Germany） |
| 9位 | 日本（Japan） |
| 10位 | シンガポール（Singapore） |

## 各国が優れている分野について

この図表は、以下の8つの評価分野（カテゴリー）ごとの値を積み上げた棒グラフで表現されています。

- R&D（研究開発）
- Responsible AI（責任あるAI）
- Economy（経済）
- Education（教育）
- Diversity（多様性）
- Policy and Governance（政策・ガバナンス）
- Public Opinion（世論）
- Infrastructure（インフラ）

ただし、**ご提示の資料（図表）からは、各国がどの分野で具体的にどれだけ優れているかという数値は読み取れません**。グラフ上では各カテゴリーが色分けされて積み上げられていますが、文章中には個別分野の詳細な評価結果についての記述はなく、視覚的な棒グラフのみで示されています。

おおまかにグラフから見て取れる傾向としては、**1位の米国が全分野にわたって突出して長い棒（特にInfrastructure＝インフラや R&D＝研究開発の部分が大きい）**を持ち、各国を大きく引き離していることが特徴的です。

正確な分野別の評価値が必要な場合は、出典元であるスタンフォード大学HAIの「Global AI Vibrancy Tool」（https://hai.stanford.edu/ai-index/global-vibrancy-tool）をご参照いただくことをおすすめします。

なお、本文では、日本は総合9位で米国・中国・英国などから「水をあけられている」とされ、また論文数を基にした別のランキング（AIRankings）では日本は11〜12位で推移していると記載されています。
```

</details>

<details><summary>Fable 5の結果</summary>

```markdown
## AI活力ランキング（2023年）上位10カ国

スタンフォード大学のHAI（Human-Centered Artificial Intelligence）が2024年11月に発表した、2023年のAI活力ランキング（図表Ⅰ-1-2-4）によると、**5位はアラブ首長国連邦（UAE）** です。

全体の順位は以下のとおりです。

| 順位 | 国名 |
|---|---|
| 1位 | 米国 |
| 2位 | 中国 |
| 3位 | 英国 |
| 4位 | インド |
| 5位 | アラブ首長国連邦（UAE） |
| 6位 | フランス |
| 7位 | 韓国 |
| 8位 | ドイツ |
| 9位 | 日本 |
| 10位 | シンガポール |

なお、日本は総合9位に位置付けられており、白書では「米国、中国、英国といった国から水をあけられている」と評価されています。

## 各国が優れている分野について

このランキングは、以下の**8つの評価分野**のスコアを合算して算出されています。

- R&D（研究開発）
- Responsible AI（責任あるAI）
- Economy（経済）
- Education（教育）
- Diversity（多様性）
- Policy and Governance（政策・ガバナンス）
- Public Opinion（世論）
- Infrastructure（インフラ）

ただし、本資料（白書）には各国がどの分野で何点を獲得したかという具体的な数値の記載はありません。図表のグラフ（積み上げ棒グラフ）から読み取れる範囲では、以下のような傾向が見られます。

- **米国**：全分野にわたってバランスよく高いスコアを獲得しており、特にR&D、経済、政策・ガバナンス、インフラの分野で他国を大きく引き離しています。
- **中国**：R&D（研究開発）とインフラの分野のスコアが大きく、これらが総合2位を支えています。
- **3位以下の国々**：米中と比較するとスコアの差が大きく、R&Dや政策・ガバナンスなどを中心に得点している様子がうかがえます。

より詳細な分野別スコアについては、出典であるStanford Universityの「Global AI Vibrancy Tool」で確認できます。

```

</details>

## Approach 2: RAG

Approach 2 は ingest と query の2ステップに分けます。

- ingest: ページを画像化し、Claude で Markdown に変換。Titan Embed v2 で埋め込んで S3 Vectors に格納する
- query: 質問を埋め込んで S3 Vectors から top-5 を検索し、その文脈で Claude に回答させる

### Ingest 側

<details><summary>scripts/approach2_ingest.py</summary>

```python:scripts/approach2_ingest.py
"""Approach 2 / Step 1: PDFをベクトル化してS3 Vectorsへ登録する。"""
import argparse
import io
import json
import uuid

from pdf2image import convert_from_bytes

import common

IMAGE_PROMPT = """\
Extract the content from an image page and output in Markdown syntax. Enclose the content in the <markdown></markdown> tag and do not use code blocks. If the image is empty then output a <markdown></markdown> without anything in it.

Follow these steps:

1. Examine the provided page carefully.

2. Identify all elements present in the page, including headers, body text, footnotes, tables, images, captions, and page numbers, etc.

3. Use markdown syntax to format your output:
    - Headings: # for main, ## for sections, ### for subsections, etc.
    - Lists: * or - for bulleted, 1. 2. 3. for numbered
    - Do not repeat yourself

4. If the element is an image (not table)
    - If the information in the image can be represented by a table, generate the table containing the information of the image
    - Otherwise provide a detailed description about the information in image
    - For charts specifically, work through the following steps in order before writing the final table:
        - Step 1 - Structure: Identify the chart type (bar, stacked bar, line, pie, etc.), read the title, axis labels with units, and list all legend categories with their colors or patterns
        - Step 2 - Scale: Note the numerical range of each axis (min, max, major gridlines) so you can derive estimates
        - Step 3 - Per-item extraction: For every item (row/country/data point), read or estimate the value of EACH series separately. Do not skip any item
        - Step 4 - Estimate unlabeled values: When no label is printed, estimate by comparing bar length to the axis scale. Mark each estimate with a leading ~. Provide numeric estimates (e.g., ~85) rather than qualitative labels (e.g., "large")
        - Step 5 - Table: Output a table with one row per item and one column per series. Add a total column when totals are visible. Do not omit any item or series
    - Classify the element as one of: Chart, Diagram, Logo, Icon, Natural Image, Screenshot, Other. Enclose the class in <figure_type></figure_type>
    - Enclose <figure_type></figure_type>, the table or description, and the figure title or caption (if available), in <figure></figure> tags
    - Do not transcribe text in the image after providing the table or description

5. If the element is a table
    - Create a markdown table, ensuring every row has the same number of columns
    - Maintain cell alignment as closely as possible
    - Do not split a table into multiple tables
    - If a merged cell spans multiple rows or columns, place the text in the top-left cell and output ' ' for other
    - Use | for column separators, |-|-| for header row separators
    - If a cell has multiple items, list them in separate rows
    - If the table contains sub-headers, separate the sub-headers from the headers in another row

6. If the element is a paragraph
    - Transcribe each text element precisely as it appears

7. If the element is a header, footer, footnote, page number
    - Transcribe each text element precisely as it appears

Output Example:
<markdown>
<figure>
<figure_type>Chart</figure_type>
Figure 3: This chart shows annual sales in millions. The year 2020 was significantly down due to the COVID-19 pandemic.
A bar chart showing annual sales figures, with the y-axis labeled "Sales ($Million)" and the x-axis labeled "Year". The chart has bars for 2018 ($12M), 2019 ($18M), 2020 ($8M), and 2021 ($22M).
</figure>

<figure>
<figure_type>Chart</figure_type>
Figure 3: This chart shows annual sales in millions. The year 2020 was significantly down due to the COVID-19 pandemic.
| Year | Sales ($Million) |
|-|-|
| 2018 | $12M |
| 2019 | $18M |
| 2020 | $8M |
| 2021 | $22M |
</figure>

# Annual Report

## Financial Highlights

<figure>
<figure_type>Logo</
