---
id: "2026-04-13-claude-api実践ガイド-haikusonnetopusの使い分けとコスト最適化python実-01"
title: "Claude API実践ガイド: Haiku/Sonnet/Opusの使い分けとコスト最適化【Python実装例付き】"
url: "https://qiita.com/Ai-chan-0411/items/82d06650c1ba83b87486"
source: "qiita"
category: "ai-workflow"
tags: ["API", "Python", "qiita"]
date_published: "2026-04-13"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude APIには **Haiku**、**Sonnet**、**Opus** という3つのモデルファミリーがあり、それぞれ速度・品質・コストのバランスが異なります。

本記事では、各モデルの特徴を比較し、**ユースケース別の最適な使い分け**と**コストを最小化する実践テクニック**を、Pythonコード例付きで解説します。

筆者はRaspberry Pi 5上で自律AIエージェントを24時間稼働させており、**月間APIコストを抑えながら品質を維持する**ノウハウを実運用から得ています。

## Claude APIモデル比較（2026年4月時点）

### 各モデルの位置づけ

| モデル | 特徴 | 入力単価(/1M tokens) | 出力単価(/1M tokens) | 最大コンテキスト |
| --- | --- | --- | --- | --- |
| **Haiku 4.5** | 高速・低コスト | $0.80 | $4.00 | 200K |
| **Sonnet 4.6** | バランス型 | $3.00 | $15.00 | 200K |
| **Opus 4.6** | 最高品質 | $15.00 | $75.00 | 200K |

### コスト比率

Haikuを1とした場合：

* **Haiku : Sonnet : Opus = 1 : 3.75 : 18.75**（入力トークン基準）

つまり、OpusはHaikuの約19倍のコストがかかります。**「とりあえずOpus」は危険**です。

## ユースケース別・最適モデル選定ガイド

### Haiku が最適なケース

```
✅ ログ解析・テキスト分類
✅ JSON構造化・データ抽出
✅ 簡単な質問応答・FAQ bot
✅ バリデーション・フォーマット変換
✅ 大量バッチ処理（1000件以上）
```

Haikuは**応答速度が最速**で、定型的なタスクでは十分な品質を発揮します。

### Sonnet が最適なケース

```
✅ コードレビュー・バグ修正
✅ 技術文書の要約・翻訳
✅ チャットボットの応答生成
✅ 中程度の推論を要するタスク
✅ 日常的なコード生成
```

Sonnetは**コストパフォーマンスが最も良い**モデルです。多くのプロダクション用途ではSonnetが第一選択肢になります。

### Opus が最適なケース

```
✅ 複雑なアーキテクチャ設計
✅ 数学的推論・論理パズル
✅ 長文の創作・高品質なライティング
✅ マルチステップの計画立案
✅ 最終品質が絶対条件のタスク
```

Opusは\*\*「ここぞ」という場面のみ\*\*に使うべきです。

## Python実装：モデル自動選択パターン

### 基本セットアップ

```
import anthropic
import time

client = anthropic.Anthropic()  # ANTHROPIC_API_KEY環境変数から自動取得

# モデルIDの定義
MODELS = {
    "haiku": "claude-haiku-4-5-20251001",
    "sonnet": "claude-sonnet-4-6",
    "opus": "claude-opus-4-6",
}
```

### タスク種別による自動選択

```
def select_model(task_type: str, token_estimate: int) -> str:
    """タスク種別とトークン数からモデルを自動選択"""

    # 大量バッチは常にHaiku
    if token_estimate > 50000:
        return MODELS["haiku"]

    # タスク種別マッピング
    haiku_tasks = {"classify", "extract", "format", "validate", "summarize_short"}
    sonnet_tasks = {"code_review", "translate", "chat", "code_gen", "summarize_long"}
    opus_tasks = {"architecture", "math", "creative_writing", "planning"}

    if task_type in haiku_tasks:
        return MODELS["haiku"]
    elif task_type in opus_tasks:
        return MODELS["opus"]
    else:
        return MODELS["sonnet"]  # デフォルトはSonnet
```

### フォールバック付き呼び出し

```
def call_with_fallback(prompt: str, task_type: str = "general",
                       max_tokens: int = 1024) -> dict:
    """Haiku→Sonnet→Opusの段階的フォールバック"""

    model = select_model(task_type, len(prompt) // 4)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return {
            "model": model,
            "content": response.content[0].text,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }
    except anthropic.RateLimitError:
        # レート制限時は上位モデルにフォールバック
        fallback_order = ["haiku", "sonnet", "opus"]
        current_idx = next(
            i for i, k in enumerate(fallback_order)
            if MODELS[k] == model
        )
        if current_idx < 2:
            time.sleep(1)
            return call_with_fallback(prompt, task_type, max_tokens)
        raise
```

## コスト最適化テクニック5選

### 1. プロンプトキャッシュの活用

```
# システムプロンプトをキャッシュして再利用
response = client.messages.create(
    model=MODELS["sonnet"],
    max_tokens=1024,
    system=[{
        "type": "text",
        "text": "あなたはPythonコードレビューの専門家です。...(長いシステムプロンプト)",
        "cache_control": {"type": "ephemeral"}
    }],
    messages=[{"role": "user", "content": code_to_review}]
)
# キャッシュヒット時、入力コストが90%削減
```

**効果**: 同じシステムプロンプトを繰り返し使う場合、**入力トークンコストが最大90%削減**されます。

### 2. バッチAPI（非同期処理）

大量リクエストにはMessage Batches APIを使います。

```
# バッチリクエストの作成
batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": f"task-{i}",
            "params": {
                "model": MODELS["haiku"],
                "max_tokens": 256,
                "messages": [{"role": "user", "content": text}]
            }
        }
        for i, text in enumerate(texts_to_process)
    ]
)
# バッチAPIは通常料金の50%割引
```

**効果**: **50%のコスト削減**。即時性が不要なバッチ処理に最適。

### 3. max\_tokensの適切な設定

```
# ❌ 悪い例：常に最大値
response = client.messages.create(
    model=MODELS["sonnet"],
    max_tokens=4096,  # 不要に大きい
    messages=[{"role": "user", "content": "この文を英訳して: こんにちは"}]
)

# ✅ 良い例：タスクに応じた適切な値
response = client.messages.create(
    model=MODELS["sonnet"],
    max_tokens=128,  # 翻訳なら十分
    messages=[{"role": "user", "content": "この文を英訳して: こんにちは"}]
)
```

### 4. 2段階処理パターン（Haiku判定→Sonnet実行）

```
def two_stage_process(task: str) -> str:
    """Haikuで難易度判定→必要な場合のみSonnetを使用"""

    # Stage 1: Haikuで難易度判定
    judge = client.messages.create(
        model=MODELS["haiku"],
        max_tokens=10,
        messages=[{
            "role": "user",
            "content": f"次のタスクの難易度をSIMPLE/COMPLEXで答えて:
{task}"
        }]
    )
    difficulty = judge.content[0].text.strip()

    # Stage 2: 難易度に応じてモデル選択
    model = MODELS["haiku"] if "SIMPLE" in difficulty else MODELS["sonnet"]

    result = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": task}]
    )
    return result.content[0].text
```

**効果**: 簡単なタスクが多い場合、**全体コストを40-60%削減**可能。

### 5. トークン使用量の監視

```
import json
from datetime import datetime

def log_usage(response, task_type: str):
    """API使用量をログに記録してコスト可視化"""
    cost_per_m = {
        "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.00},
        "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
        "claude-opus-4-6": {"input": 15.00, "output": 75.00},
    }
    model = response.model
    rates = cost_per_m.get(model, {"input": 3.0, "output": 15.0})
    cost = (
        response.usage.input_tokens * rates["input"] / 1_000_000
        + response.usage.output_tokens * rates["output"] / 1_000_000
    )
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "model": model,
        "task": task_type,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "cost_usd": round(cost, 6),
    }
    with open("api_usage.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "
")
    return cost
```

## Raspberry Piでの実運用コスト実績

筆者のRaspberry Pi 5（NVMe SSD搭載）で自律AIエージェントを24時間運用した際の実績です。

### 構成

* **ハードウェア**: Raspberry Pi 5 (8GB RAM) + NVMe SSD（Pironman5 Pro MAXケース）
* **用途**: OSS PR自動生成・レビュー・記事投稿の自律エージェント
* **モデル使い分け**:
  + タスク振り分け・ログ解析 → **Haiku**
  + コード生成・レビュー → **Sonnet**
  + アーキテクチャ設計・複雑な判断 → **Opus**（1日数回のみ）

### コスト配分の目安

| 用途 | モデル | 1日あたりの呼び出し | 推定コスト/日 |
| --- | --- | --- | --- |
| タスク分類 | Haiku | ~200回 | ~$0.05 |
| コード生成 | Sonnet | ~50回 | ~$0.30 |
| 設計判断 | Opus | ~5回 | ~$0.20 |
| **合計** |  |  | **~$0.55/日** |

**月額約$17**で自律AIエージェントが24時間稼働します。

## まとめ

| ポイント | 内容 |
| --- | --- |
| デフォルトはSonnet | コスパ最強。迷ったらSonnet |
| バッチ処理はHaiku | 大量処理は最安モデルで |
| Opusは切り札 | 複雑な推論のみに限定 |
| キャッシュ活用 | 同一プロンプト繰り返しなら90%削減 |
| 使用量を可視化 | ログを取って無駄を発見 |

**「全部Opusでいいじゃん」は月額が20倍になります。** モデルの使い分けこそがAPI活用の肝です。

---

📝 **より詳しい自律AIエージェントの構築方法**は、Noteの有料記事で設定ファイル・コード例・ハマりどころ10選を含めて解説しています。  
→ [Raspberry Pi 5+NVMe SSDで自律AIエージェントを24時間稼働させる完全実践ガイド](https://note.com/ai_chan_0411)
