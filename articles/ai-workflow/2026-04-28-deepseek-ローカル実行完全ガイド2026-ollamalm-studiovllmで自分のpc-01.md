---
id: "2026-04-28-deepseek-ローカル実行完全ガイド2026-ollamalm-studiovllmで自分のpc-01"
title: "DeepSeek ローカル実行完全ガイド2026 — Ollama・LM Studio・vLLMで自分のPCに導入"
url: "https://zenn.dev/agdexai/articles/deepseek-local-deploy-2026"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "LLM", "zenn"]
date_published: "2026-04-28"
date_collected: "2026-04-29"
summary_by: "auto-rss"
---

DeepSeekのモデルはMITライセンスでオープンソース公開されています。自分のPCやサーバーで動かせば、APIキーなし・月額費用なし・データは自分のマシンの中だけ。

本記事では3つの方法を解説します。

## どのモデルを選ぶか

| モデル | パラメータ | 必要VRAM（Q4量子化） | おすすめ用途 |
| --- | --- | --- | --- |
| R1 Distill 7B | 7B | 約5GB | RTX 3060・M2 Pro以上 |
| R1 Distill 14B | 14B | 約10GB | RTX 3090・M2 Max以上 ⭐ |
| R1 Distill 32B | 32B | 約22GB | RTX 4090・A100以上 |
| V3 / V4（フル） | 671B〜1.6T | 400GB以上 | マルチGPUサーバー |

**一般的な開発者には R1 Distill 14B（Q4量子化）が最もコスパが良い**です。

---

## 方法1：Ollama（最も簡単）

### インストール

```
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows：ollama.com からインストーラーをダウンロード
```

### モデルのダウンロードと起動

```
ollama run deepseek-r1:7b
ollama run deepseek-r1:14b   # おすすめ
ollama run deepseek-r1:32b
ollama run deepseek-v3:latest
```

### PythonからAPIとして使う

OllamaはOpenAI互換APIを `http://localhost:11434` で公開します：

```
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # 任意の文字列
)

response = client.chat.completions.create(
    model="deepseek-r1:14b",
    messages=[{"role": "user", "content": "AIエージェントとは何ですか？"}]
)
print(response.choices[0].message.content)
```

### LangChainと組み合わせる

```
from langchain_ollama import ChatOllama

llm = ChatOllama(model="deepseek-r1:14b")
result = llm.invoke("MCPプロトコルを3行で説明してください")
```

### CrewAIと組み合わせる

```
from crewai import LLM

llm = LLM(
    model="ollama/deepseek-r1:14b",
    base_url="http://localhost:11434"
)
```

---

## 方法2：LM Studio（GUIで手軽に）

GUIアプリで、技術的な知識が少なくても使えます。

1. [lmstudio.ai](https://lmstudio.ai) からアプリをダウンロード
2. 「Discover」タブで「deepseek」を検索
3. `DeepSeek-R1-Distill-Qwen-14B-GGUF` を選択してダウンロード
4. モデルをロードしてチャット開始
5. 「Local Server」を有効にするとポート1234でAPIが使える

```
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)
```

---

## 方法3：vLLM + Docker（本番グレード）

GPUサーバーで高スループットが必要な場合：

```
docker pull vllm/vllm-openai:latest

docker run --runtime nvidia --gpus all \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -p 8000:8000 \
  vllm/vllm-openai:latest \
  --model deepseek-ai/DeepSeek-R1-Distill-Qwen-14B
```

`http://localhost:8000/v1` でAPIが使えます。

---

## 方法の比較

| 方法 | 難易度 | 速度 | おすすめシーン |
| --- | --- | --- | --- |
| Ollama | ⭐ 簡単 | 良好 | 開発・実験 |
| LM Studio | ⭐ 簡単 | 良好 | 非エンジニア・Windows |
| vLLM + Docker | ⭐⭐⭐ 難 | 最高 | 本番・高スループット |

---

ローカルで動かせるDeepSeek以外のAIエージェントツールを探すなら **[AgDex.ai](https://agdex.ai)** をご覧ください。400以上のツールを比較できます。
