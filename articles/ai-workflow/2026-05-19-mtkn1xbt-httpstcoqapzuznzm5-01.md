---
id: "2026-05-19-mtkn1xbt-httpstcoqapzuznzm5-01"
title: "@MtkN1XBt: https://t.co/qAPzUZnZm5"
url: "https://x.com/MtkN1XBt/status/2056615102120648973"
source: "x"
category: "ai-workflow"
tags: ["API", "AI-agent", "Python", "x"]
date_published: "2026-05-19"
date_collected: "2026-05-20"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/qAPzUZnZm5

ちなみに x_search は grok-4.20-reasoning がデフォルトになっています。~/.hermes/config.yaml の 404 行目辺りを編集すれば grok-4.3 で x_search が使えます。
(Hermes の Docs では grok-4.20-reasoning が recommened default ですが grok-4.3 でも十分機能します)
https://t.co/MTLUoeroXe https://t.co/WjW3RZcimp


--- Article ---
Hermes Agent + x_search の仕組みを詳しく調べたところ現在拡散されている手順よりもシンプルに x_search が使えたのでまとめておきます 📝

**x_search したいだけなら Hermes Agent 本体のインストールや設定は不要
**→ 最小限必要なのは Python (uv) のみ
→ Hermes 内部の Python API を使えば "x_search を使って..." のプロンプト不要
→ さらに Grok X Search の raw 寄りのデータが取れるのでより効果的に他のエージェントと連携可能

(参考: サブスクリプション内で x_search を Hermes で利用可能に)

## 0. 前提: uv のインストール

Python 環境管理ツールの uv をインストールします。 既定の手順で Hermes をインストールしていたら自動で入っています。
https://docs.astral.sh/uv/getting-started/installation/

## 1. xAI の OAuth 認証

uvx コマンドで Hermes の xAI OAuth 認証のみを実行します。 表示された URL をローカルのブラウザで開いて認証します。

```shell
uvx --from hermes-agent hermes auth add xai-oauth
```

リモート (SSH) の場合は SSH のトンネルが必要です。

```shell
ssh -L 56121:127.0.0.1:56121 user@remote-host \
  'uvx --from hermes-agent hermes auth add xai-oauth --no-browser'
```

## 2. x_search_tool の呼び出し

Hermes 内部の Python API にある x_search_tool を呼び出します。 (例: "What are people saying about xAI on X?" を x_search します)

```shell
uvx --from hermes-agent python -c \
  'from tools.x_search_tool import x_search_tool; print(x_search_tool("What are people saying about xAI on X?"))'
```

※ x_search は 30 秒以上掛かる事があります。

さらに Python コードをカスタマイズすればコマンドライン引数でクエリを渡したり回答部分のみ出力する様にも出来ます。

```python
# run_x_search.py
import json
import sys
from tools.x_search_tool import x_search_tool
s = x_search_tool(sys.argv[1])
print(json.loads(s)["answer"])
```

```shell
uvx --from hermes-agent python run_x_search.py \
  'What are people saying about xAI on X?'
```

他のエージェントから連携にはこれらの方法をスキル化するのが効果的です。

現在多く拡散されている情報は Hermes 本体に "x_search を使って..." とプロンプトするものです。 それの問題点としては次のように **"3 度の解釈" が発生して時間が掛かるのと情報が薄まる可能性があります**。

1. x_sarch_tool による Grok の回答
1. それを Hermers のモデルが受け取って回答 (←ここが省ける) 
1. それを目的のエージェントが受け取って利用する
## 3. x
