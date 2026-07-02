---
id: "2026-07-02-claude-agent-sdkを読んで分かったこと-claude-codeがライブラリになった-01"
title: "Claude Agent SDKを読んで分かったこと 〜 Claude Codeがライブラリになった 〜"
url: "https://qiita.com/miyaguchi_kioku/items/7c8589981783f21b2592"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "AI-agent", "LLM", "GPT"]
date_published: "2026-07-02"
date_collected: "2026-07-03"
summary_by: "auto-rss"
query: ""
---

Anthropicから公開されている **Claude Agent SDK** を一通り読んでみました。

https://code.claude.com/docs/ja/agent-sdk/overview?utm_source=chatgpt.com

一言でいうと、

> **Claude Codeをライブラリとして利用できるようになった**

ということです。

## 今までとの違い

従来のLLMアプリケーションは、

```
LLM
↓
Tool実行
↓
LLM
↓
Tool実行
```

というループを開発者が実装する必要がありました。

Claude Agent SDKでは、

```python
query(...)
```

を呼ぶだけで、

* 判断
* ツール実行
* 結果確認
* 次の行動決定
* コンテキスト管理

までClaudeが自律的に行ってくれます。

つまり「Agent Loop」がSDKに組み込まれています。

---

## 最初から使えるツール

標準で利用できるツールもかなり充実しています。

* Read
* Write
* Edit
* Bash
* Monitor
* Glob
* Grep
* WebSearch
* WebFetch
* AskUserQuestion

これらを自分で実装する必要はありません。

---

## 一番面白かったのは Sub Agent

個人的に最も魅力を感じたのは **Sub Agent** です。

例えば

```
教材生成Agent

↓

レビューAgent

↓

問題生成Agent

↓

改善Agent
```

のように役割を分けることができます。

各Agentは独立したコンテキストを持つため、大規模なワークフローでも管理しやすくなっています。

---

## Hooksもかなり強力

Hooksによって

* 編集前チェック
* 編集後ログ保存
* 危険な操作のブロック
* 品質チェック

などをコードで実装できます。

企業利用ではかなり重要になりそうです。

---

## Claude Codeの資産をそのまま利用できる

SDKから

* CLAUDE.md
* Skills
* Plugins
* Commands

を利用できます。

CLIで育てた資産をそのままアプリケーションへ持ち込めるのは大きなメリットだと思いました。

---

## 私が興味を持った使い方

私は現在、

**PDF教材から講座を自動生成する Loop Engineering**

に取り組んでいます。

イメージとしては

```
PDF
↓

教材生成

↓

レビュー

↓

改善

↓

動画生成

↓

確認テスト生成
```

という一連の流れをAIエージェントに任せる構成です。

Claude Agent SDKは、このようなマルチエージェント型のワークフローと非常に相性が良いと感じました。

---

## まとめ

Claude Agent SDKは単なるSDKではありません。

Claude Codeそのものをプログラムから利用できる「Agent実行基盤」です。

今後は

* Agent Loop
* Sub Agents
* MCP
* Hooks

あたりがAIアプリケーション開発の中心になっていくのではないかと思います。

これから実際に教材自動生成システムを構築しながら、得られた知見もQiitaで共有していく予定です。
