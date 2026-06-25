---
id: "2026-06-23-chatgpt定期タスク時代の自動化エージェントを自作するpythonマルチllmで放置リサチを組む-01"
title: "ChatGPT「定期タスク」時代の自動化エージェントを自作する—Python×マルチLLMで“放置リサチ”を組む"
url: "https://zenn.dev/kairosai/articles/95e5fc0f1f6d04"
source: "zenn"
category: "ai-workflow"
tags: ["API", "LLM", "OpenAI", "Gemini", "GPT", "Python"]
date_published: "2026-06-23"
date_collected: "2026-06-25"
summary_by: "auto-rss"
query: ""
---

2026年6月17日、OpenAIがChatGPTに「定期タスク（Scheduled Tasks）」を正式投入しました。リマインドや定期作業、Web監視を自動スケジュール実行できる機能です。Google も Gemini Spark（個人エージェント）や Daily Brief を展開し、AIは「指示待ち」から「自律稼働」へ一気にシフトしています。

この記事では、そうした"予約実行型"AIの中身を理解するために、毎朝AIニュースを自動収集して要約する最小限の自動化エージェントをPythonで自作します。マルチLLM（OpenAI / Gemini / Claude）を差し替え可能な構成にして、モデルが退役しても壊れにくい設計にします。

## 設計方針：モデルを抽象化する

自動化スクリプトで最も避けたいのは、特定モデルにロジックを密結合させることです。`Provider` を抽象化し、環境変数でモデル名を切り替えられるようにします。

```
import os
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """LLMプロバイダの共通インターフェース"""
    @abstractmethod
    def summarize(self, text: str) -> str:
        ...

class OpenAIProvider(LLMProvider):
    def __init__(self, model: str | None = None):
        # モデル名は外から差し替え可能に（GPT-5.2退役対策）
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5.5")

    def summarize(self, text: str) -> str:
        from openai import OpenAI
        client = OpenAI()
        resp = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": f"次のニュースを3行で要約:\n{text}"}],
        )
        return resp.choices[0].message.content
```

ポイントは `model` をコンストラクタ引数 + 環境変数のフォールバックにしていることです。GPT-5.2が退役しても `OPENAI_MODEL=gpt-5.5` を設定するだけで動き続けます。

## スケジューラ部分：定期実行を組む

ChatGPTの定期タスクの「自前版」にあたる部分です。`schedule` ライブラリで毎朝実行します。

```
import schedule
import time
import datetime

def build_provider() -> LLMProvider:
    backend = os.getenv("LLM_BACKEND", "openai")
    return {"openai": OpenAIProvider}[backend]()

def daily_job():
    provider = build_provider()
    raw_news = fetch_latest_ai_news()  # RSS/News APIから取得
    summary = provider.summarize(raw_news)
    stamp = datetime.date.today().isoformat()
    with open(f"brief_{stamp}.md", "w", encoding="utf-8") as f:
        f.write(f"# AIデイリーブリーフ {stamp}\n\n{summary}\n")

# 毎朝7時に実行（Gemini "Daily Brief" 風）
schedule.every().day.at("07:00").do(daily_job)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(30)
```

## エラーハンドリング：止まらない設計にする

自律稼働するエージェントは、止まらないことが最優先です。1つのプロバイダが落ちても別系統で継続するフォールバックを入れます。

```
def summarize_with_fallback(text: str, providers) -> str:
    last_err = None
    for p in providers:
        try:
            return p.summarize(text)
        except Exception as e:  # API障害・モデル提供終了など
            last_err = e
            continue
    raise RuntimeError(f"all providers failed: {last_err}")
```

これで、たとえばClaude Fable 5が輸出規制で停止していても、OpenAI側で処理が続きます（逆もまた然り）。本番では指数バックオフのリトライも足すとさらに堅牢です。

## まとめ

「定期タスク」「Gemini Spark」「Daily Brief」のようなマネージドな自律実行機能は便利ですが、中身は今回作ったような「取得 → LLM処理 → 保存 → スケジュール実行 → フォールバック」のループです。仕組みを理解しておくと、モデルが退役しても設定変更だけで延命でき、複数プロバイダで冗長化でき、マネージド機能と自前スクリプトを使い分けられます。モデルは数週間で入れ替わりますが、こうした自動化の設計スキルは腐りません。まずは1つ、毎朝動く小さなエージェントから始めてみてください。
