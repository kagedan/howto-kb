---
id: "2026-06-03-aiエージェント自作ローカルllmollamaとclaude-apiを切り替えるアーキテクチャ-01"
title: "【AIエージェント自作】ローカルLLM（Ollama）とClaude APIを切り替えるアーキテクチャ"
url: "https://zenn.dev/pekopugu/articles/agent01-a2-llm-client"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "AI-agent", "LLM", "OpenAI", "Python"]
date_published: "2026-06-03"
date_collected: "2026-06-04"
summary_by: "auto-rss"
query: ""
---

## この記事で作るもの

シリーズ第2回です。前回はAIエージェントの設計思想を整理しました。今回はいよいよ実装に入り、**Phase A（土台）のStep 01〜03**を解説します。

作るのは以下の3点です。

* **LLMクライアント抽象化レイヤー**：OllamaとClaude APIを同じ `chat()` で呼び出せる仕組み
* **システムプロンプト設定**：エージェントの行動原則をLLMに伝える
* **ターミナルREPLループ**：会話履歴を保持しながらLLMと対話し続けるループ

完成すると、次のように起動して会話できます。

```
$ python src/agent.py --llm ollama

[起動] LLM：ollama / モデル：デフォルト

╔══════════════════════════════════╗
║   Code Maintenance Agent         ║
║   'exit' または 'quit' で終了    ║
╚══════════════════════════════════╝

> Pythonの型ヒントについて教えて
[考え中...]

型ヒント（Type Hints）は Python 3.5 以降で導入された...
```

---

## なぜOllamaとClaude APIを両対応にするのか

ローカルLLM（Ollama）をメインにする理由は3つです。

* **コスト**：ローカルで動くので何度試しても無料
* **速度**：APIのネットワーク遅延がない
* **学習効果**：モデルをローカルで動かすことでLLMへの理解が深まる

ただし、Claude APIと比べると精度に差があります。そこで**同じコードで両方を動かせる**設計にし、品質確認のときだけClaude APIに切り替えられるようにします。

OllamaはOpenAI互換のエンドポイントを提供しているため、`openai` ライブラリをそのまま使って接続できます。

```
Ollama エンドポイント：http://localhost:11434/v1
```

---

## LLMクライアントの抽象化設計

まず抽象基底クラスを定義します。`chat()` メソッドだけを持つシンプルな設計で、OllamaとClaude APIで戻り値のフォーマットを統一します。

src/llm/base.py

```
from abc import ABC, abstractmethod

class LLMClientBase(ABC):

    @abstractmethod
    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        system: str | None = None,
    ) -> dict:
        """
        Returns:
            {
                "content": str | None,
                "tool_calls": list | None,
                "stop_reason": str    # "end_turn" | "tool_use"
            }
        """
        pass
```

`stop_reason` で「回答して終了」か「ツール呼び出しを要求」かを判定する設計です。この統一フォーマットがあることで、エージェントループ側はLLMの種類を意識せずに動作できます。

---

## Ollama接続の実装

`openai` ライブラリの `base_url` をOllamaのエンドポイントに向けるだけで接続できます。

src/llm/ollama\_client.py

```
from openai import OpenAI
from .base import LLMClientBase

class OllamaClient(LLMClientBase):

    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        )
        self.model = model

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        system: str | None = None,
    ) -> dict:
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        kwargs: dict = {"model": self.model, "messages": full_messages}
        if tools:
            kwargs["tools"] = tools

        response = self.client.chat.completions.create(**kwargs)
        choice = response.choices[0]

        if choice.finish_reason == "tool_calls":
            return {
                "content": None,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    }
                    for tc in choice.message.tool_calls
                ],
                "stop_reason": "tool_use",
            }

        return {
            "content": choice.message.content,
            "tool_calls": None,
            "stop_reason": "end_turn",
        }
```

`api_key="ollama"` はOllamaに認証が不要なため、任意の文字列で問題ありません（openaiライブラリが空文字を拒否するための回避策です）。

---

## Claude API接続の実装

`anthropic` ライブラリを使います。`ANTHROPIC_API_KEY` は `.env` ファイルから読み込みます。

src/llm/claude\_client.py

```
import anthropic
from .base import LLMClientBase

class ClaudeClient(LLMClientBase):

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic()
        self.model = model

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        system: str | None = None,
    ) -> dict:
        kwargs: dict = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": messages,
        }
        if system:
            kwargs["system"] = system
        if tools:
            kwargs["tools"] = tools

        response = self.client.messages.create(**kwargs)

        if response.stop_reason == "tool_use":
            return {
                "content": None,
                "tool_calls": [
                    {"id": block.id, "name": block.name, "arguments": block.input}
                    for block in response.content
                    if block.type == "tool_use"
                ],
                "stop_reason": "tool_use",
            }

        text = next(
            (block.text for block in response.content if hasattr(block, "text")), ""
        )
        return {"content": text, "tool_calls": None, "stop_reason": "end_turn"}
```

`.env` ファイルにAPIキーを記述します。

```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
```

---

## ファクトリ関数で切り替える

クライアントの生成はファクトリ関数に集約します。

src/llm/\_\_init\_\_.py

```
from .base import LLMClientBase
from .ollama_client import OllamaClient
from .claude_client import ClaudeClient

def create_client(llm: str = "ollama", model: str | None = None) -> LLMClientBase:
    """LLMクライアントのファクトリ関数。"""
    if llm == "ollama":
        return OllamaClient(model=model or "qwen2.5-coder:7b")
    elif llm == "claude":
        return ClaudeClient(model=model or "claude-sonnet-4-20250514")
    else:
        raise ValueError(f"未対応のLLM: {llm}。'ollama' または 'claude' を指定してください。")
```

起動時の引数で切り替えます。

```
python src/agent.py                                    # Ollama（デフォルト）
python src/agent.py --llm ollama --model qwen2.5-coder:7b
python src/agent.py --llm claude
```

---

## ターミナルREPLの実装

会話履歴を `messages` リストで管理し、LLMへ毎回全履歴を渡します。

src/repl.py

```
def run_repl(client: LLMClientBase) -> None:
    messages: list[dict] = []

    while True:
        user_input = input("> ").strip()
        if user_input.lower() in EXIT_COMMANDS:
            break

        messages.append({"role": "user", "content": user_input})

        response = client.chat(messages=messages, system=SYSTEM_PROMPT)

        assistant_message = response["content"] or ""
        print(f"\n{assistant_message}\n")

        messages.append({"role": "assistant", "content": assistant_message})
```

`messages` の構造はシンプルです。

```
messages = [
    {"role": "user",      "content": "最初の質問"},
    {"role": "assistant", "content": "最初の回答"},
    {"role": "user",      "content": "続きの質問"},  ← 新しいメッセージを追加
]
```

LLMに全履歴を渡すことで、前の会話の文脈を踏まえた回答が得られます。

---

## 躓いた点・気づき

### Windows環境のcp932エンコーディング問題

Windowsのデフォルトエンコーディング（cp932）のため、日本語を含むLLMの出力をターミナルに表示するとエラーが発生しました。

```
# 各ファイルの先頭に追加することで解決
import sys
sys.stdout.reconfigure(encoding="utf-8")
```

`agent.py` と `repl.py` の両方に記述する必要がありました。

### PowerShellのBOM問題

PowerShellのパイプ（`echo "質問" | python src/agent.py`）を使うと、BOM付きでstdinに流されるためテストが失敗しました。対処法はbashのリダイレクト（`< input.txt`）を使うか、インタラクティブに起動することです。本番用途ではインタラクティブ起動が前提なので、実運用上の問題はありません。

---

## まとめ

Phase Aで作ったものを振り返ります。

* **LLM抽象化**：`LLMClientBase` を定義することで、OllamaもClaude APIも同じ `chat()` で呼び出せるようになりました
* **システムプロンプト**：エージェントの行動原則を一か所で管理できます
* **REPLループ**：会話履歴を `messages` リストで積み上げることで、文脈を保った対話が実現できました

次回はこの土台の上に**ツール**を乗せていきます。LLMが自分でファイルを読んだりディレクトリを探索したりできるようになると、いよいよ「エージェント」らしい動作になります。

## 次回

**【AIエージェント自作】tool\_useを理解してツールを作る**  
→ Step 04でtool\_useの仕組みを実装し、`read_file` / `list_files` をLLMが呼べるようにします。

---

## シリーズリンク
