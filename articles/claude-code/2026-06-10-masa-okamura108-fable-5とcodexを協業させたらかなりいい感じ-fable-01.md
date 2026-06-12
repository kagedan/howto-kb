---
id: "2026-06-10-masa-okamura108-fable-5とcodexを協業させたらかなりいい感じ-fable-01"
title: "@masa_okamura108: Fable 5とCodexを協業させたらかなりいい感じ。 Fable 5がサブスク外になって従量課金になってもこの方法な"
url: "https://x.com/masa_okamura108/status/2064841547624145269"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "OpenAI", "x"]
date_published: "2026-06-10"
date_collected: "2026-06-12"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

Fable 5とCodexを協業させたらかなりいい感じ。
Fable 5がサブスク外になって従量課金になってもこの方法なら効率的にFable 5を利用できて継続できるかも。

やり方は以下の3ステップ。CLAUDE .mdに実際に記載した内容はリプに貼っておきます👇

概要としてはFable 5はトークン消費が激しいので実装をCodexに依頼する方法です。

Fable 5：設計、リサーチ、レビュー
Codex：実装、レビュー

※レビューは両者で行いクオリティを高める。

ステップ① Claude CodeをCodex と協業できるようにする
OpenAIの公式「codex-plugin-cc」を利用します。
プラグイン型MCPで、Claude Code のマーケットプレイスから /install コマンドでインストール可能

ステップ② CLAUDE .md にFable 5とCodexの協業方針を記載する
リプのテキストをCLAUDE .mdにコピペする

ステップ③ 実装したい内容でプロンプトを実行すればFable 5が適宜Codexを呼び出してくれる🎉

CLAUDE .md に追記する内容
------------
## Claude Code 計画と実装時の利用モデルについて
あなたがFable 5で動いているなら以下に従ってください。
設計、コードベースのリサーチ、レビューはメインセッションであるFable 5で行ってください。
実装はトークンを節約するためにCodexに依頼してください。
ただし、実装難易度が高く、Codexには難しいと判断した場合にはメインセッション（Fable 5）で実装してください。

## Claude Code と Codex の役割分担

### Codex が担当する作業
- 実装
- コードレビュー（実装完了後に必ず実施）
- リファクタリング・テスト生成

### 委譲ルール
1. 実装タスクを受けたら、規模を判断して Codex への委譲を検討する
2. 実装完了後は `/codex:rescue` または `mcp__codex__codex` でレビューを依頼する
3. Claude Code が詰まったら `/codex:rescue` スキルで Codex に引き継ぐ

### Codex の呼び出し方
```bash
# CLI から直接
codex <<EOF
<依頼内容>
EOF
```

または Claude Code が MCP ツール `mcp__codex__codex` を使って直接呼び出す。
