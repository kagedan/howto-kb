---
id: "2026-07-19-エージェントai時代の実装入門gpt-56-claude-sonnet-5-を作業を仕上げる道具とし-01"
title: "エージェントAI時代の実装入門：GPT-5.6 / Claude Sonnet 5 を「作業を仕上げる道具として使う"
url: "https://zenn.dev/kairosai/articles/2ae45fbf7fb6e5"
source: "zenn"
category: "ai-workflow"
tags: ["OpenAI", "Gemini", "GPT", "zenn"]
date_published: "2026-07-19"
date_collected: "2026-07-20"
summary_by: "auto-rss"
query: ""
---

## はじめに

2026年7月、OpenAI（GPT-5.6 + ChatGPT Work）、Anthropic（Claude Sonnet 5）、Google（Gemini Spark）が相次いで「エージェント型」のAIを打ち出しました。共通点は、単発の応答ではなく、ゴールを渡すと複数ステップの作業を自律的に進めて成果物を返すという設計思想です。この記事では、その「エージェント的な使い方」をコードレベルでどう実装するかを、最小構成のサンプルで解説します。

## エージェントの基本ループ

エージェントAIの本質は次の流れです。まずゴールを受け取り、次に取るべきアクション（tool呼び出しか完了か）を決め、tool を実行して結果を観測する。これを完了まで繰り返します。疑似コードで表すと以下の通りです（要点を1行ずつ並べています）。

```
# エージェントの基本ループ（要点を1行ずつ・疑似コード）
messages = [{"role": "user", "content": goal}]   # ゴールを受け取る
response = model_call(messages, tools)            # 次アクションを決定
name, args = response.tool_call                   # 呼ぶtoolと引数
result = run_tool(name, args)                     # toolを実行し観測
messages.append({"role": "tool", "content": result})
# tool_callが無くなるまで上を最大max_steps回繰り返し、最後にresponse.contentを返す
```

ポイントは、モデルが「まだ作業が必要」なら tool を呼び、「完成した」と判断したら最終回答を返すという分岐です。ChatGPT Work のような製品も、抽象化すればこの構造の拡張版と言えます。

エージェントに「作業」をさせるには、実際に副作用を持つ関数（tool）を渡します。たとえばレポート書き出しとノート検索を用意すると、「ノートを検索して要点をレポートにまとめて」というゴールを渡すだけで、検索→書き出しの順にエージェントが自分で判断して進められます。tool のシグネチャは次のようなイメージです。

```
# tool = 副作用を持つ関数。名前→関数の辞書で登録する（各行フラット表記）
def write_report(filename, content): ...   # Markdownをファイルに書き出す
def search_notes(keyword): ...             # ローカルのノートを全文検索する
TOOLS = {"write_report": write_report, "search_notes": search_notes}
# エージェントは response.tool_call の name を見て TOOLS[name](**args) を実行する
```

## トークン効率を意識する

Sam Altman は GPT-5.6 の最上位モデル "Sol" について「エージェント型コーディングでトークン効率が54%向上」と述べています。エージェントはループのたびに履歴を送るため、コンテキストの肥大がそのままコスト増になります。実務では、古い tool 結果を要約して履歴を圧縮する（最初のゴールと直近数ターンだけ残す）といった工夫が効きます。長時間タスクほど、この履歴管理の巧拙が体感速度とコストを左右します。

## モデル選定の指針（2026年7月時点）

| 用途 | 推奨 | 理由 |
| --- | --- | --- |
| 汎用・無料で試す | Claude Sonnet 5 | 全ユーザーの標準。Opus 4.8に迫る性能 |
| 高負荷なエージェント処理 | GPT-5.6 "Sol" | トークン効率重視 |
| 速度優先 | GPT-5.6 "Luna" | レイテンシ最小 |
| ローカルファイル横断 | Gemini Spark | Workspace/ローカル連携 |

## まとめ

エージェントAIの実装は、突き詰めれば「モデル呼び出し + tool 実行 + ループ + 履歴圧縮」という素朴な構造です。各社の新モデルは、このループの各要素（判断精度・トークン効率・ツール連携）を強化しているにすぎません。まずは最小エージェントを手元で動かし、自分の業務にある「繰り返しの作業」を1つ tool 化してみることをおすすめします。エージェント時代の差別化は、モデルそのものよりも「どんな tool を持たせるか」の設計にあります。

*本記事は2026年7月19日時点の公開情報に基づきます。コードは解説用の最小構成です。*
