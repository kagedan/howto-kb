---
id: "2026-04-17-anthropic-claude-opus-47リリース開発者が押さえておきたい主要変更点と移行ポイ-01"
title: "Anthropic Claude Opus 4.7リリース：開発者が押さえておきたい主要変更点と移行ポイント"
url: "https://qiita.com/lavellehatcherjr/items/00b9853b205dd5c3fdc3"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-17"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

[![qiita-opus47-thumbnail.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4398742%2F83a3f829-7d48-4fd0-857c-423676b50b40.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4eeed11db07c1d6feb770867ead61d01)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4398742%2F83a3f829-7d48-4fd0-857c-423676b50b40.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4eeed11db07c1d6feb770867ead61d01)  
Anthropicは2026年4月16日、Claude Opus 4.7を一般公開しました。Opus 4.6の後継として、コーディング、ビジョン、エージェント性能の各方面でアップグレードが入っています。

※本記事は公開情報をもとにした個人的なまとめであり、Anthropicの公式見解ではありません。

## Opus 4.7の位置づけ

Claude Opus 4.7は、現時点でAnthropicが一般提供する最も高性能なモデルです。ただし、先週発表されたProject Glasswingの対象であるClaude Mythos Previewが、ベンチマーク上ではさらに上に位置しています。Mythos Previewは一部のプラットフォームパートナーにのみ限定公開されており、一般利用はできません。

Opus 4.7はOpus 4.6と同じ価格設定（入力$5/出力$25 per 1Mトークン）を維持しており、モデルIDは`claude-opus-4-7`です。Claude API、Amazon Bedrock、Google Cloud Vertex AI、Microsoft Foundryで利用可能です。

## 主なベンチマーク成績

公開されている数値をいくつか並べます。

* SWE-bench Verified: 87.6%（Opus 4.6から大幅改善）
* SWE-bench Pro: 64.3%（Opus 4.6: 53.4%、GPT-5.4: 57.7%）
* CursorBench: 70%（Opus 4.6: 58%）
* MCP-Atlas（マルチツール制御）: 77.3%（同カテゴリ最高スコア）
* CharXiv視覚推論: 82.1%（Opus 4.6: 69.1%）
* XBOW視覚精度: 98.5%（Opus 4.6: 54.5%）  
  Rakutenからは「Opus 4.6と比較してプロダクション環境で解決可能なタスクが3倍に増えた」との報告も出ています。

## 新機能：何が追加されたか

### 高解像度画像サポート

Opus 4.7はClaude初の高解像度画像対応モデルです。最大画像解像度がロング辺1,568px（約1.15MP）から2,576px（約3.75MP）へ、3倍以上に拡大されました。

Computer Use（スクリーンショットの理解）やドキュメント解析で特に効果が大きく、座標がピクセルと1:1で対応するようになったため、従来必要だったスケール係数の計算が不要になっています。

### xhigh effortレベルの追加

effortパラメータに新たに`xhigh`が追加され、5段階構成（low / medium / high / xhigh / max）になりました。`high`よりも深い推論を行い、`max`ほどのコストは掛からないバランスを狙った設定です。

Claude Codeでは全プランのデフォルトが`xhigh`に設定されています。コーディングやエージェント用途では`high`または`xhigh`からの評価が推奨されています。

### タスクバジェット（パブリックベータ）

エージェントループ全体にトークン予算を設定できる機能です。1ターンではなく、思考・ツール呼び出し・出力を含む全体に対してトークン上限を指定できるため、長時間実行のエージェントでコスト暴走を防ぐ用途に向いています。

### Claude Codeの `/ultrareview` コマンド

コードレビュー専用の新コマンドで、バグ、エッジケース、セキュリティ問題、ロジックエラーをより深くチェックするマルチパスレビューを実行します。

## 破壊的変更（Breaking Changes）

API利用者にとって重要な変更が3点あります。

### 1. Extended Thinking Budgetの廃止

`thinking: {"type": "enabled", "budget_tokens": N}` は400エラーを返します。Opus 4.7では`thinking: {"type": "adaptive"}`のみがサポートされます。なお、adaptive thinkingはデフォルトでオフになっており、`thinking`フィールドを指定しないリクエストでは思考なしで実行されます。有効にするには明示的に設定が必要です。

### 2. サンプリングパラメータの廃止

`temperature`、`top_p`、`top_k`にデフォルト以外の値を設定すると400エラーになります。出力の制御はプロンプティングで行う方式に変更されています。

### 3. Thinkingコンテンツがデフォルトで非表示

思考ブロックはレスポンスに含まれますが、内容は空です。表示が必要な場合は`"display": "summarized"`をオプトインで指定します。

## 移行時のコード例

```
# Before (Opus 4.6)
model = "claude-opus-4-6"
thinking = {"type": "enabled", "budget_tokens": 8192}
temperature = 0.7
 
# After (Opus 4.7)
model = "claude-opus-4-7"
thinking = {"type": "adaptive"}
# temperature は削除（プロンプトで制御）
# max_tokens はヘッドルームを持たせて拡大推奨
```

## 挙動の変化

APIの破壊的変更ではないものの、プロンプト調整が必要になり得る挙動変化もあります。

* 指示をより文字通りに解釈する傾向（暗黙の推論が減少）
* 応答の長さがタスクの複雑さに連動して調整される（固定的な冗長さが減少）
* デフォルトでのツール呼び出し回数が減少（effortを上げると増加）
* より直接的でオピニオネイテッドなトーン（Opus 4.6のやや丁寧な文体から変化）
* 長時間のエージェント実行中に定期的な進捗報告を自動で挿入
* デフォルトで生成するサブエージェント数が減少

## トークナイザの変更

Opus 4.7は新しいトークナイザを使用しており、同じ入力に対して従来比で1.0〜1.35倍のトークンを消費する場合があります。1トークンあたりの単価は据え置きですが、同じプロンプトで実効コストが上がる可能性があるため、本番移行前にワークロードでの検証が推奨されます。

## サイバーセキュリティ関連のガードレール

Opus 4.7には、禁止されたまたはハイリスクなサイバーセキュリティ用途を自動検知・ブロックするガードレールが搭載されています。Mythos Previewと比較してサイバー関連の能力は意図的に低減されており、正当な目的（脆弱性調査、ペネトレーションテスト等）での利用希望者向けにCyber Verification Programが用意されています。

## まとめ：誰がいつ移行すべきか

* **コーディングエージェントを本番運用しているチーム**：SWE-benchの改善幅が大きく、移行のメリットがコスト増を上回る可能性が高い
* **Computer UseやOCR的な画像処理を組んでいるチーム**：3.75MPの解像度対応だけで移行する理由になる
* **シンプルなQ&AやFAQボット**：Haiku 4.5やSonnet 4.6のほうがコスト効率が良いため、無理にOpusへ移行する必要はない  
  移行の際は、Opus 4.6を1〜2週間フォールバックとして残しつつ、本番ワークロードでの検証を並行して進めるのが安全なアプローチです。

## 参考
