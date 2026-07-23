---
id: "2026-07-23-kawai-design-httpstcompqrlaj9lf-01"
title: "@kawai_design: https://t.co/MPqRlAJ9lf"
url: "https://x.com/kawai_design/status/2080229698685259882"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "AI-agent", "x"]
date_published: "2026-07-23"
date_collected: "2026-07-24"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

https://t.co/MPqRlAJ9lf


--- Article ---
Claude Codeを使い始めると、最初は**「コードを書いてもらう」**だけで十分便利です。

しかし、何度も同じ説明をする、外部サービスから情報をコピーする、変更後の確認を毎回手作業で行う状態では、まだAI作業は仕組みになっていません。

この記事では、Claude Codeの中級者を**「機能をたくさん知っている人」**ではなく、AIとの作業を再現可能な運用へ変えられる人と定義します。

読後には、**MCP、Hooks、API**をどの順番で学び、どこまで使えれば中級者と言えるかを判断できます。

この記事が向く人は、Claude Codeで開発や業務を始めたものの、毎回の指示、確認、外部ツール連携に限界を感じている人です。

完全な初心者向けのインストール解説や、個別サービスのMCP一覧を探している人には向きません。

> 見出し画像はAIで生成しました。
プロンプトは[240,000文字超えの記事](https://note.com/kawaidesign/n/n5cfbd87d1d4d)に掲載中。
毎日プロンプトは増えていきます。

---

## 目次

- Claude Codeの初級者と中級者を分けるもの
- 最初にCLAUDE.mdとSkillsで作業を標準化する
- MCPでAIを外部ツールと接続する
- Hooksで決めたルールを自動実行する
- APIとAgent SDKでClaude Codeを業務へ組み込む
- 中級者チェックリストと最初の実践課題
---

**初心者も安心！0からわかる
Claude Code完全授業｜Claude Camp 2**

🔽 詳細・お申込みはこちら

## 

# Claude Codeの初級者と中級者を分けるもの

![](https://pbs.twimg.com/media/HN50v4WbwAA9iiP.jpg)

Claude Codeを使えることと、Claude Codeで安定して成果を出せることは別です。

初級者は、目の前の作業を依頼します。

中級者は、同じ作業が次回も同じ品質で進むように、前提、手順、確認方法を残します。

![](https://pbs.twimg.com/media/HN50ylAbIAAV7Cw.jpg)

中級者になるための順番は、次の通りです。

1. **前提を固定する**
1. **外部情報とツールを接続する**
1. **決めた確認を自動化する**
1. **必要な処理をアプリケーションへ組み込む**
いきなりAPIから始める必要はありません。

まずは、Claudeが毎回迷う理由をプロジェクトのルールへ移します。

# 最初にCLAUDE.mdとSkillsで作業を標準化する

![](https://pbs.twimg.com/media/HN502eLbYAAYMtQ.jpg)

MCPやHooksを導入しても、プロジェクトの前提が曖昧なら、AIは迷い続けます。

中級者の最初の仕事は、便利な拡張を増やすことではなく、判断基準を整理することです。

CLAUDE.mdに書くもの

- プロジェクトの目的
- 使用する言語、フレームワーク、コマンド
- ファイル構成
- テストやレビューの方法
- 触ってはいけないファイル
- 完了条件
CLAUDE.mdは百科事典ではありません。

毎回の作業で参照する、短い運用ルールに絞ります。

Skillsに切り出すもの

複数のプロジェクトで使う手順や、長い定型作業はSkillsへ切り出します。

たとえば**「LPを作る」「公開前にチェックする」「顧客向けレポートを作る」**といった作業です。

ここでの判断基準は単純です。

- **プロジェクト固有の前提はCLAUDE.md**
- **繰り返し使う作業手順はSkills**
- **外部サービスへアクセスする機能はMCP**
- **必ず実行したい機械的な処理はHooks**
この4つの役割を混ぜないことが、後の保守性を決めます。

# MCPでAIを外部ツールと接続する

MCPは、Claude Codeと外部のツール、データベース、APIを接続するためのオープンな標準です。

Anthropicの公式ドキュメントでは、MCPサーバーを接続すると、別のツールから情報をコピーして貼り付ける代わりに、Claude Codeがそのシステムを直接読み書きできると説明されています。

つまりMCPは、Claudeに知識を追加するだけの仕組みではありません。**AIを仕事の置き場所へ届ける接続口**です。

実務例は次の通りです。
