---
id: "2026-06-07-claude-code-openrouter-free-モデルコスト0円で始めるai駆動開発の5つの-01"
title: "Claude Code × OpenRouter Free モデル：コスト0円で始めるAI駆動開発の5つの設定ポイント"
url: "https://qiita.com/locallab/items/31da7494387e2c6f69c2"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "OpenAI", "Gemini", "Python", "qiita"]
date_published: "2026-06-07"
date_collected: "2026-06-08"
summary_by: "auto-rss"
query: ""
---

## TL;DR

- Claude Code のバックエンドを OpenRouter 経由で繋ぐと、無料モデルで AI 駆動開発が試せる
- 2026年時点で使える `:free` モデルの特性とユースケースを整理
- レート制限・コンテキスト長・用途別の使い分けで実用十分なワークフローを組める

---

## 背景

Claude Code は Anthropic の claude-sonnet / opus をデフォルトで使うが、`ANTHROPIC_API_KEY` の代わりに `ANTHROPIC_BASE_URL` を差し替えることで **任意の OpenAI 互換エンドポイント**を向かせることができる。

OpenRouter は数十社のモデルを一本のエンドポイントで束ねるプロキシサービスで、`/api/v1` が OpenAI 互換。さらに **`:free` サフィックス付きモデル**を選べば料金ゼロで推論を走らせられる。

PoC・個人学習・オープンソース貢献など「とにかく試したい」フェーズで重宝する組み合わせだ。

---

## 1. OpenRouter `:free` モデルとは

OpenRouter では一部モデルを `<provider>/<model>:free` という ID で提供している。2026年5月時点で代表的なものをまとめる。

| モデル ID | コンテキスト長 | 特性 | 主なユースケース |
|---|---|---|---|
| `google/gemini-2.0-flash-exp:free` | 1M tokens | 高速・マルチモーダル | 大規模ファイル読み込み・画像解析 |
| `qwen/qwen3-235b-a22b:free` | 128K tokens | MoE・多言語強い | コード生成・日本語 README 生成 |
| `qwen/qwen3-30b-a3b:free` | 128K tokens | 軽量 MoE・速い | 補完・lint 修正・コミットメッセージ |
| `meta-llama/llama-4-maverick:free` | 1M tokens | Meta 最新・強力 | 設計レビュー・長文サマリ |
| `deepseek/deepseek-r1:free` | 64K tokens | 推論特化 | アルゴリズム設計・バグ仮説立案 |
| `mistralai/mistral-7b-instruct:free` | 32K tokens | 最軽量・低レイテンシ | コメント生成・短いリファクタ |

> **注意**: `:free` モデルはレート制限が厳しく（通常 20 req/min、1日200req 程度）、重い並列処理には向かない。有料プランと使い分けが前提。

---

## 2. 接続設定の5ポイント

### ポイント① BASE_URL の差し替え

Claude Code は環境変数 `ANTHROPIC_BASE_URL` を尊重する。OpenRouter のエンドポイントを指定する。

```bash
export ANTHROPIC_BASE_URL="https://openrouter.ai/api/v1"
export ANTHROPIC_API_KEY="<your-openrouter-api-key>"
```

`ANTHROPIC_API_KEY` には Anthropic のキーではなく **OpenRouter のキー**を渡す。OpenRouter 側が Anthropic 互換ヘッダを受け付けて正しくルーティングしてくれる。

### ポイント② モデル名の指定

Claude Code はデフォルトで `claude-sonnet-4-5` などを要求するが、`--model` フラグまたは設定ファイルで上書きできる。

```bash
claude --model "qwen/qwen3-235b-a22b:free" "この関数をリファクタしてください"
```

または `.claude/settings.json` に固定する方法も使える：

```json
{
  "model": "google/gemini-2.0-flash-exp:free",
  "fallbackModel": "qwen/qwen3-30b-a3b:free"
}
```

> **注意**: OpenRouter が Claude 互換レスポンスを返さない場合、一部の Claude Code 機能（`thinking` ブロック等）は無効化またはエラーになる。基本的なチャット・コード補完・ファイル編集は問題なく動作する。

### ポイント③ HTTP ヘッダの追加 (推奨)

OpenRouter は `HTTP-Referer` と `X-Title` を見てダッシュボードの Usage 集計に使う。Claude Code のカスタムヘッダ設定（`apiKeyHelper` スクリプト or プロキシ）で付与しておくと使用量追跡が楽になる。

```python
# openrouter-proxy.py (ローカル単純プロキシ例: Flask)
from flask import Flask, request, Response
import requests

app = Flask(__name__)
UPSTREAM = "https://openrouter.ai/api/v1"

@app.route("/<path:path>", methods=["GET","POST","DELETE"])
def proxy(path):
    headers = dict(request.headers)
    headers["HTTP-Referer"] = "https://locallab.jp"
    headers["X-Title"] = "Claude Code Dev"
    resp = requests.request(
        method=request.method,
        url=f"{UPSTREAM}/{path}",
        headers=headers,
        json=request.get_json(silent=True),
        stream=True,
    )
    return Response(resp.iter_content(chunk_size=4096),
                    status=resp.status_code,
                    headers=dict(resp.headers))

if __name__ == "__main__":
    app.run(port=8080)
```

```bash
export ANTHROPIC_BASE_URL="http://localhost:8080"
```

### ポイント④ レート制限への対処

`:free` モデルは RPM/RPD(requests per day) 制限が低い。Claude Code がインタラクティブに連打する状況では詰まりやすい。

実用的な回避策：

```bash
# .claude/settings.json で並列ツール呼び出し数を制限
{
  "maxConcurrentTools": 1,
  "requestTimeout": 60000
}
```

また `429 Too Many Requests` が返ってきたら指数バックオフで自動リトライする仕組みをプロキシ層に入れると安定する：

```python
import time, random

def call_with_retry(fn, max_retries=5):
    for i in range(max_retries):
        try:
            return fn()
        except RateLimitError:
            wait = (2 ** i) + random.uniform(0, 1)
            time.sleep(wait)
    raise Exception("max retries exceeded")
```

### ポイント⑤ モデルを用途別に使い分ける

全タスクを 1 モデルに投げると RPD を無駄遣いする。以下の分担が実用的：

| タスク | 推奨モデル | 理由 |
|---|---|---|
| コミットメッセージ自動生成 | `qwen3-30b-a3b:free` | 速い・短文で十分 |
| 大きなログファイルのサマリ | `gemini-2.0-flash-exp:free` | 1Mトークン |
| アルゴリズム設計レビュー | `deepseek-r1:free` | 推論ステップが丁寧 |
| 長い仕様書からコード生成 | `llama-4-maverick:free` | 1M + 高品質 |
| 日本語ドキュメント整形 | `qwen3-235b-a22b:free` | 日本語強い |

---

## 3. 動作確認：最小 curl テスト

接続が正しいか確認する最短コマンド：

```bash
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen/qwen3-30b-a3b:free",
    "messages": [{"role":"user","content":"Hello, reply in one sentence."}]
  }'
```

`choices[0].message.content` に返答が来れば OK。

---

## 4. よくあるハマりポイントと対処

### ハマり① `model_not_found` エラー

`:free` モデルは提供状況が流動的。[openrouter.ai/models?q=:free](https://openrouter.ai/models?q=%3Afree) で常時確認し、廃止されたモデルを `.claude/settings.json` から除去する。

### ハマり② ストリーミングが切れる

OpenRouter の `:free` エンドポイントはストリーミングを途中で切ることがある。Claude Code の `stream: false` オプション（非ストリーム）に切り替えると安定することがある。ただし応答が長い場合は返ってくるまで待機が必要。

### ハマり③ `thinking` ブロックがエラーになる

Claude 3.7+ の extended thinking を有効化すると、OpenRouter 経由では対応モデル以外でエラーになる。`--no-thinking` フラグで無効化するか、モデルを変える。

```bash
claude --no-thinking --model "deepseek/deepseek-r1:free" "..."
```

### ハマり④ Tool use (function calling) の非対応

一部の `:free` モデルは tool use (JSON function calling) に非対応で、Claude Code のファイル編集ツールが動作しない場合がある。モデル詳細ページの **"Tools"** 対応バッジを確認すること。

**Tool use 対応確認済みの `:free` モデル例:**
- `google/gemini-2.0-flash-exp:free` ✅
- `qwen/qwen3-235b-a22b:free` ✅
- `meta-llama/llama-4-maverick:free` ✅
- `deepseek/deepseek-r1:free` ⚠️（推論は得意だが tool use は限定的）

---

## 5. 実際のワークフロー例：README 自動生成

```bash
#!/bin/bash
# gen-readme.sh: OpenRouter :free で README を生成

export ANTHROPIC_BASE_URL="https://openrouter.ai/api/v1"
export ANTHROPIC_API_KEY="$OPENROUTER_API_KEY"

# 日本語 README 生成は Qwen3 が得意
claude \
  --model "qwen/qwen3-235b-a22b:free" \
  --output-format text \
  "以下の package.json と src/index.ts を読んで、
   日本語の README.md を生成してください。
   バッジ・インストール手順・使用例・ライセンスセクションを含めること。" \
  --add-file package.json \
  --add-file src/index.ts \
  > README.md

echo "README.md を生成しました"
```

コスト: $0.00（`:free` モデル使用）

---

## まとめ

| ポイント | 内容 |
|---|---|
| ① BASE_URL 差し替え | `ANTHROPIC_BASE_URL` を OpenRouter エンドポイントに変えるだけ |
| ② モデル名指定 | `--model <provider>/<name>:free` で無料モデルを選択 |
| ③ ヘッダ追加 | `HTTP-Referer` / `X-Title` でダッシュボード追跡を有効化 |
| ④ レート制限対処 | 並列数制限 + 指数バックオフで安定運用 |
| ⑤ 用途別使い分け | コンテキスト長・推論品質・言語強度でモデルを選ぶ |

`:free` モデルは本番 SaaS 開発に使い続けるには制限がきついが、**PoC・個人プロジェクト・OSS 貢献・学習**のフェーズなら実用十分。課金モデルへの移行コストもゼロ（BASE_URL を戻すだけ）なので、最初の一歩としてコスパが高い。

---

## 参考リンク

- [OpenRouter 公式ドキュメント](https://openrouter.ai/docs)
- [OpenRouter モデル一覧（:free フィルタ）](https://openrouter.ai/models?q=%3Afree)
- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)
- [Claude Code カスタムエンドポイント設定](https://docs.anthropic.com/en/docs/claude-code/settings)
- [Qwen3 技術レポート（Hugging Face）](https://huggingface.co/Qwen/Qwen3-235B-A22B)

---

✍️ 本記事の著者: **合同会社ジモラボ**

ジモラボは、八王子を拠点に AI を活用した SaaS を多数開発しています。本記事の技術検証もそうした開発過程の副産物です。

- 🌐 公式サイト: https://locallab.jp
- 🔍 AI SEO 最適化 SaaS: [lookupai.jp](https://lookupai.jp)
- 📺 YouTube: [@locallab_llc](https://www.youtube.com/@locallab_llc)
- ✉️ お問い合わせ: info@locallab.jp

> 興味を持っていただけたら、ぜひ各 SNS のフォローもお願いします！
