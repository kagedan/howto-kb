---
id: "2026-07-23-minimax-m27入門-自己進化aiがswe-pro-56を達成するmoeコーディングエージェン-01"
title: "MiniMax M2.7入門 — 自己進化AIがSWE-Pro 56%を達成するMoEコーディングエージェント"
url: "https://zenn.dev/kai_kou/articles/250-minimax-m27-self-evolving-agent-guide"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "OpenAI", "GPT", "Python"]
date_published: "2026-07-23"
date_collected: "2026-07-24"
summary_by: "auto-rss"
query: ""
---

## はじめに

2026年4月12日、中国のAIスタートアップ MiniMax が **MiniMax M2.7** をオープンウェイトとして公開しました。M2.7 は同社初の「自己進化型（Self-Evolving）」AIで、100ラウンドを超える自律的な最適化ループを通じて自分自身の開発に参加し、コーディング性能を **30%** 向上させた記録を持ちます。

実際のソフトウェアエンジニアリング能力を測る **SWE-bench Pro**（通称: SWE-Pro）ベンチマークでは **56.22%** を達成しました。OpenAI の GPT-5.3-Codex（56.8〜57.0%）に迫る水準です。本記事では MiniMax M2.7 のアーキテクチャ、性能、API での使い方を公開情報をもとに解説します。

### この記事で学べること

* MiniMax M2.7 の「自己進化」とは何か
* MoE アーキテクチャによる高効率推論の仕組み
* ベンチマーク性能の比較（SWE-Pro・Terminal Bench 2）
* MiniMax API を使った Python 実装
* Hugging Face / Ollama でのローカル実行方法
* ライセンスと商用利用の注意事項

### 対象読者

* 最新のオープンウェイト LLM を業務や研究で活用したいエンジニア
* AIエージェント開発に取り組んでいる方
* GPT/Claude 以外のモデルを評価・比較したい方

### 前提環境

---

## TL;DR

* MiniMax M2.7 は **229B パラメータ（MoE）** で、推論時は **10B のみ** アクティブ化する高効率モデル
* SWE-bench Pro **56.22%**・Terminal-Bench 2.0 **57.0%** を達成（GPT-5.3-Codex に迫る水準）
* API 料金は **$0.30/M 入力・$1.20/M 出力** でコスト優位
* 非商用利用は自由だが、**商用利用は MiniMax への申請** が必要
* Hugging Face・Ollama でローカル実行も可能（457GB / 量子化版 108GB）

---

## MiniMax M2.7 の概要

### 自己進化（Self-Evolving）とは

MiniMax M2.7 は、モデルが単独で以下のサイクルを繰り返すことで自分自身を改善する設計です：

1. **ログ読み取り（Log Reading）**: 実行ログから失敗パターンを分析
2. **自己フィードバック（Self-Feedback）**: 改善点を特定してプランを立案
3. **自己最適化（Self-Optimization）**: スキャフォールドのコードを修正して再実行

[公式ブログ](https://www.minimax.io/news/minimax-m27-en)によると、M2.7 はこのループを **100 ラウンド以上** 自律実行し、プログラミング性能を **30%** 向上させました。内部の強化学習チームのワークフローを **30〜50%** 自動化したことも報告されています。

自己進化のコアコンポーネントは 3 つです：

| コンポーネント | 役割 |
| --- | --- |
| 短期記憶（Short-Term Memory） | 実行中の状態とコンテキストを保持 |
| 自己フィードバック | 失敗軌跡を分析して改善点を特定 |
| 自己最適化 | コード修正を計画・実行するループ |

### スペック一覧

| 項目 | 値 |
| --- | --- |
| 総パラメータ数 | 229B（約 230B） |
| 推論時アクティブパラメータ | 約 10B（8/256 エキスパート） |
| コンテキストウィンドウ | 196,608 トークン（約 200K） |
| アーキテクチャ | Sparse MoE（62 レイヤー、256 エキスパート） |
| 推奨推論フレームワーク | SGLang、vLLM |
| 公開形式 | オープンウェイト（Hugging Face） |

---

## ベンチマーク性能

### SWE-bench Pro と Terminal-Bench 2.0

従来の SWE-bench は "パッチを当てれば修正完了" というシンプルな評価でした。**SWE-bench Pro**（通称: SWE-Pro）はより複雑な本番レベルのタスクを想定した上位版ベンチマークです。**Terminal-Bench 2.0** はターミナル操作を伴う長期的なタスク遂行能力を評価します。

[MarkTechPost の報告](https://www.marktechpost.com/2026/04/12/minimax-just-open-sourced-minimax-m2-7-a-self-evolving-agent-model-that-scores-56-22-on-swe-pro-and-57-0-on-terminal-bench-2/)によると：

| モデル | SWE-Pro | Terminal Bench 2 |
| --- | --- | --- |
| MiniMax M2.7 | **56.22%** | **57.0%** |
| GPT-5.3-Codex | 56.8〜57.0% | — |
| （参考）GPT-5.4 | — | — |

### エージェントスキルの安定性

[MiniMax 公式](https://www.minimax.io/models/text/m27)によると、M2.7 は 2,000 トークンを超える複雑なスキル **40 以上** にわたって **97% のスキル遵守率** を維持します。Agent Teams での役割境界も安定しており、マルチエージェント構成での実用性が高いとされています。

---

## API での利用方法

### 環境準備

MiniMax API キーは [platform.minimax.io](https://platform.minimax.io) から取得します。

```
export MINIMAX_API_KEY="your_api_key_here"
```

### 基本的なチャット補完

[MiniMax API リファレンス](https://platform.minimax.io/docs/api-reference/text-api)に基づく実装例です。

```
import os
import requests

API_KEY = os.environ["MINIMAX_API_KEY"]
url = "https://api.minimax.io/v1/text/chatcompletion_v2"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

payload = {
    "model": "MiniMax-M2.7",
    "messages": [
        {
            "role": "user",
            "content": "Write a Python function to parse a JSON log file and extract ERROR lines."
        }
    ],
    "temperature": 1.0,
    "top_p": 0.95,
    "top_k": 40,
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()
print(result["choices"][0]["message"]["content"])
```

### Anthropic SDK との互換エンドポイント

MiniMax は Anthropic SDK との互換エンドポイントも提供しています：

```
import anthropic
import os

client = anthropic.Anthropic(
    api_key=os.environ["MINIMAX_API_KEY"],
    base_url="https://api.minimax.io/anthropic",
)

message = client.messages.create(
    model="MiniMax-M2.7",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Refactor this Python function to use async/await."}
    ]
)
print(message.content[0].text)
```

### API 料金

[platform.minimax.io/docs/guides/pricing-paygo](https://platform.minimax.io/docs/guides/pricing-paygo) より（2026年4月時点）：

| モデル | 入力 | 出力 |
| --- | --- | --- |
| MiniMax-M2.7 | $0.30 / 1M トークン | $1.20 / 1M トークン |
| MiniMax-M2.7-highspeed | $0.30 / 1M トークン | $1.20 / 1M トークン |

`MiniMax-M2.7-highspeed` は同じ料金ですが、より高速なレスポンスを提供します。

---

## ローカル実行（Hugging Face / Ollama）

### Hugging Face からのダウンロード

```
# モデルカードの確認
# https://huggingface.co/MiniMaxAI/MiniMax-M2.7

# SGLang での推論（推奨）
pip install sglang
python -m sglang.launch_server \
  --model-path MiniMaxAI/MiniMax-M2.7 \
  --trust-remote-code \
  --tp 8  # テンソル並列数（GPU数に応じて調整）
```

#### ストレージ要件

| 形式 | 必要容量 |
| --- | --- |
| BF16（フル精度） | 約 457GB |
| 4-bit 量子化（UD-IQ4\_XS） | 約 108GB |

### Ollama での実行

```
# Ollama がインストール済みの場合
ollama pull minimax-m2.7
ollama run minimax-m2.7
```

推論の推奨パラメータは `temperature=1.0`、`top_p=0.95`、`top_k=40` です。

---

## ライセンスと商用利用

### 非商用利用

個人プロジェクト・研究・ファインチューニング（プライベートデプロイ）は、申請なしで自由に利用できます。

### 商用利用

[MiniMax M2.7 ライセンス](https://huggingface.co/MiniMaxAI/MiniMax-M2.7/blob/main/LICENSE)によると、商用利用（製品・サービスへの組み込み、API の商用提供等）には **MiniMax への事前書面申請** が必要です。

* 申請先メール: `api@minimax.io`
* 件名: `M2.7 licensing`
* 商用製品への表示義務: `Built with MiniMax M2.7` の明記

MiniMax は「申請プロセスは迅速かつ合理的に対応する」と述べています。

---

## 他モデルとの比較

| 項目 | MiniMax M2.7 | GPT-5.3-Codex | Claude Opus 4.7 |
| --- | --- | --- | --- |
| SWE-bench Pro | 56.22% | 56.8〜57.0% | — |
| コンテキスト | 196K | 128K | 1M |
| 入力料金 | $0.30/M | $1.75/M | $5.00/M |
| オープンウェイト | ○（非商用） | ✕ | ✕ |
| 自己進化機能 | ○ | ✕ | ✕ |

コスト面では MiniMax M2.7 は GPT-5.3-Codex の **約 1/6**、Claude Opus 4.7 の **約 1/17** という優位性があります。

---

## まとめ

* MiniMax M2.7 は 229B パラメータ MoE モデルで、推論時は **10B のみ** アクティブ
* 自己進化機能により SWE-bench Pro **56.22%** を達成（GPT-5.3-Codex の 56.8〜57.0% に迫る水準）
* API 料金は **$0.30/M トークン** とコスト競争力が高い
* 非商用は申請不要、商用利用は `api@minimax.io` への申請が必要
* SGLang・vLLM でのローカル実行も可能（ただし 108GB 以上が必要）

コーディングエージェントの構築に GPT/Claude を使っている場合、MiniMax M2.7 はコスト削減の有力な代替選択肢になります。

## 参考リンク
