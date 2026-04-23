---
id: "2026-04-08-最近claude-codeが雑-effortlevel-highにしたらマシになるか軽く検証-01"
title: "最近Claude Codeが雑？ effortLevel: highにしたらマシになるか軽く検証"
url: "https://zenn.dev/mtk0/articles/claude-code-effort-level-high-benchmark"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-08"
date_collected: "2026-04-09"
summary_by: "auto-rss"
query: ""
---

## 最近Claude Code雑になってない？

最近のClaude Code、特に上流設計や影響調査みたいなタスクでなんか浅いなと感じることが増えた。同じこと言ってる人も多い。Xでこのポストを見かけて、本当にマシになるのかちょっと気になったので軽く試してみた。

<https://x.com/PawelHuryn/status/2041418614557802747>

この人がGitHub issue #42796（6,852セッション・17,871件のthinking blockを分析）を調べたところ、内部のthinking budget（思考予算）のデフォルトが`medium`に下がったタイミングで、モデルの振る舞いが「まず調べる」から「まず編集する」にシフトしていたらしい。設定で`high`（またはお好みでmax）にすればマシになるとのこと。

~/.claude/settings.json

```
{
  "effortLevel": "high",
  "showThinkingSummaries": true
}
```

## defaultとhighで同じ質問を投げてみた

テスト条件はシンプル。同じ質問を新規セッションで、設定なし（default = medium）とeffortLevel: highそれぞれで実行した。以下「default」は設定未変更の状態を指す。

### Q1: スクリプトファイルのリネーム影響調査

`.claude/scripts/`内のシェルスクリプトをリネームしたとき、設定ファイルやドキュメントへの参照をすべてリストアップする調査を投げてみた。

* **default**: ツール7回、38秒。主要な参照箇所はカバーしていたけど、rules/ディレクトリ内の参照チェックが漏れていた
* **high**: ツール15回、59秒。行番号付きで全箇所を列挙し、名前衝突の可能性チェックまで実施。該当なしの箇所も「確認して該当なし」と明示

トークン量は38k→45kで1.18倍。時間は1.5倍かかるけど、rules/内の参照漏れは実際にリネームしたら壊れるところなので、この差は大きい。

### Q2: 自動記録hookの設計

自作アプリの実行結果をログに自動記録するhookの設計案を出してもらった。

* **default**: ツール3回、31秒。代替案3つの提示で、基本的な設計判断は良好
* **high**: ツール25回、137秒。実際のコードを読み込んで既存hookのパターンを全件参照し、5つの観点×4案の比較テーブルと実装時の注意点6項目を出してきた

defaultの「コードを読まずに一般論で答える」と、highの「コードを読んでから答える」の差がはっきり出た。

### 比較まとめ

| 観点 | default | high |
| --- | --- | --- |
| ツール使用数 | 3〜7回 | 15〜25回 |
| 所要時間 | 31〜38秒 | 59〜137秒 |
| トークン量（Q1実測） | 38k | 45k（1.18倍） |
| 調査の網羅性 | 主要箇所カバー | 全箇所＋該当なし明示 |
| 既存コード参照 | 最小限 | 実コードまで読む |

## showThinkingSummaries — 浅い思考の異常検知

思考過程のサマリーをターミナルに表示する設定。トークン量にはほぼ影響しないらしい。

「浅い調査で結論出そうとしてる」がリアルタイムで見えるので、気づいた時点で軌道修正できる。effortLevelとセットで。

## 使い分け

常時highにしてもコスト増は約1.2倍で、思ったほど大きくない。

* **high or max推奨**: 上流設計、影響範囲の調査、リファクタ計画、既存コードの理解が必要な作業
* **defaultで十分**: typo修正、コード実装の指示、フォーマット変更などの定型作業

設計や調査をよくやる人は、デフォルトhighかmaxでいいと思う。settings.jsonに2行足すだけ。

## 追記: これもやるとよさそう

HNスレッド（[news.ycombinator.com/item?id=47664442](https://news.ycombinator.com/item?id=47664442)）でClaude Codeチームの人がコメントしていた設定。effortLevelと併せて `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` も入れておくとよさそう。

~/.claude/settings.json

```
{
  "effortLevel": "high",
  "showThinkingSummaries": true,
  "env": {
    "CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING": "1"
  }
}
```

いわく、2月末時点でthinking depthが約67%低下していたらしく、adaptive thinkingがターンによってreasoningトークンを絞りすぎて fabrication を誘発しているのが原因らしい。これを無効化すれば固定 budget に切り替わる。
