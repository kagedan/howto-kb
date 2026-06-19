---
id: "2026-06-17-マルチaiを1つのコードで切り替える-openai-claude-gemini-をフェイルオーバーさ-01"
title: "マルチAIを1つのコードで切り替える — OpenAI / Claude / Gemini をフェイルオーバーさせる実装パターン"
url: "https://zenn.dev/kairosai/articles/d32bb069e38eef"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "LLM", "OpenAI", "Gemini", "GPT", "Python"]
date_published: "2026-06-17"
date_collected: "2026-06-19"
summary_by: "auto-rss"
query: ""
---

## なぜ今「マルチAI前提」の実装なのか

2026年6月、Anthropicの最強モデル「Claude Fable 5 / Mythos 5」が公開からわずか3日で外国籍ユーザー向けに停止される、という出来事がありました。同時期にOpenAIはGPT-5.2を提供終了して5.5へ自動移行し、GoogleはGemini Sparkを投入。

ここから得られる実装上の教訓はシンプルです。

> **単一プロバイダにハードコードした連携は、自分の都合と無関係に壊れる。**

そこで本記事では、OpenAI / Claude / Gemini を **1つの抽象インターフェースで扱い、ある提供元が落ちたら自動で次へフェイルオーバーする** 最小実装パターンを紹介します。言語はPythonです。

## 設計方針

ポイントは3つです。

1. **共通インターフェース** — 呼び出し側は「どのAIか」を意識しない
2. **フェイルオーバー** — 優先順位順に試し、例外が出たら次へ
3. **設定の外出し** — モデル名・優先順位は環境変数や設定で差し替え可能に

## 1. 共通インターフェース（Adapter）

各プロバイダの差異を `generate(prompt) -> str` に押し込めます。

```
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    name: str

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        ...

class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, model: str = "gpt-5.5"):
        from openai import OpenAI
        self.client = OpenAI()
        self.model = model

    def generate(self, prompt: str, **kwargs) -> str:
        resp = self.client.responses.create(model=self.model, input=prompt, **kwargs)
        return resp.output_text

class ClaudeProvider(LLMProvider):
    name = "claude"

    def __init__(self, model: str = "claude-opus-4-8"):
        import anthropic
        self.client = anthropic.Anthropic()
        self.model = model

    def generate(self, prompt: str, **kwargs) -> str:
        msg = self.client.messages.create(
            model=self.model, max_tokens=1024,
            messages=[{"role": "user", "content": prompt}], **kwargs)
        return msg.content[0].text

class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self, model: str = "gemini-3.5-flash"):
        from google import genai
        self.client = genai.Client()
        self.model = model

    def generate(self, prompt: str, **kwargs) -> str:
        resp = self.client.models.generate_content(
            model=self.model, contents=prompt, **kwargs)
        return resp.text
```

## 2. フェイルオーバー付きルーター

優先順位順に試し、落ちたら次のプロバイダへ。全滅したら例外を投げます。

```
import logging, time

logger = logging.getLogger("multi_ai")

class MultiAIRouter:
    def __init__(self, providers, retries: int = 1):
        if not providers:
            raise ValueError("at least one provider is required")
        self.providers = providers
        self.retries = retries

    def generate(self, prompt: str, **kwargs):
        last_error = None
        for provider in self.providers:
            for attempt in range(self.retries + 1):
                try:
                    text = provider.generate(prompt, **kwargs)
                    logger.info("ok via %s", provider.name)
                    return text, provider.name
                except Exception as e:
                    last_error = e
                    logger.warning("provider=%s failed: %s", provider.name, e)
                    time.sleep(0.5 * (attempt + 1))
        raise RuntimeError(f"all providers failed: {last_error}")
```

## 3. 使い方

優先順位を変えるだけで主役を差し替えられます。Fable 5が止まった日も、コードは1行も変えずに次へ流れます。

```
router = MultiAIRouter([
    ClaudeProvider(),    # 第1候補: 日本語の執筆・要約に強い
    OpenAIProvider(),    # 第2候補: 汎用・スピード
    GeminiProvider(),    # 第3候補: 低コスト・高速フォールバック
])

text, used = router.generate("AI副業のメリットを3行で説明して")
print(f"[{used}] {text}")
```

## 役割分担のすすめ（コスト最適化）

フェイルオーバーだけでなく、タスク別ルーティングにすると品質とコストのバランスが取れます。ドラフトは安く速いモデル、仕上げは上位モデル、事実確認は別系統で相互チェック——この3段でハルシネーション対策とコスト削減を同時に狙えます。

```
def route_by_task(task: str) -> MultiAIRouter:
    if task == "draft":      # ドラフトは安く速く
        return MultiAIRouter([GeminiProvider(), OpenAIProvider()])
    if task == "polish":     # 仕上げは上位モデル
        return MultiAIRouter([ClaudeProvider(), OpenAIProvider()])
    if task == "factcheck":  # 事実確認は別系統で相互チェック
        return MultiAIRouter([OpenAIProvider(), GeminiProvider()])
    return MultiAIRouter([ClaudeProvider(), OpenAIProvider(), GeminiProvider()])
```

## まとめ

* 単一プロバイダ依存は、規制・料金・モデル廃止で **自分の意思と無関係に壊れる**
* 共通インターフェース＋フェイルオーバーで、**1社が落ちても止まらない** 構成にできる
* さらにタスク別ルーティングで、**品質・速度・コスト** を最適化できる

「最強の1モデル」を追うより、「落ちても止まらない設計」を持つこと。2026年のAI実装で、これがいちばん効く保険です。実運用では、プロバイダ別の例外ハンドリング、レート制限、タイムアウト、ストリーミング対応を足してください。
