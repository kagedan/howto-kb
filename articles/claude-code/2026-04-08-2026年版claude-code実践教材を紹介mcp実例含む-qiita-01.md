---
id: "2026-04-08-2026年版claude-code実践教材を紹介mcp実例含む-qiita-01"
title: "【2026年版】Claude Code実践教材を紹介（MCP実例含む） - Qiita"
url: "https://qiita.com/aakan/items/1a9a367eecc8fa0ebc5d"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "qiita"]
date_published: "2026-04-08"
date_collected: "2026-04-09"
summary_by: "auto-rss"
query: ""
---

# Claude Code 実践教材を紹介

※MCP☞server側／Client側両面実践詳解！

*教材の URL: [Claude Code 実践ガイド](https://gokokuyi.github.io/index.html)*

## はじめに

Anthropic の CLI ツール **Claude Code** を使い始めたのはいいものの、  
「チームメンバーにも使ってほしいけど、どう教えればいいか分からない」という壁にぶつかりました。

公式ドキュメントは英語で量も多く、初めての人にはハードルが高い。  
かといって毎回ハンズオンを開催するコストもかかる。

そこで、**自分のペースで学べる HTML ベースのセルフラーニング教材** を作りました。  
全 5 ステップ、各ステップに Lesson・Quiz・ハンズオンの 3 点セットで構成しています。

*教材の URL: [Claude Code 実践ガイド](https://gokokuyi.github.io/index.html)*

---

## 教材の構成

| ステップ | テーマ | 対象 |
| --- | --- | --- |
| Step 1 | Claude Code 入門（概要・インストール・権限モード） | 全員 |
| Step 2 | ファイル操作と基本ツール（Read/Write/Edit/Grep/Glob） | 全員 |
| Step 3 | エージェント機能と自動化（Agent・TodoWrite・並列処理） | 中級 |
| Step 4 | カスタマイズと高度な設定（CLAUDE.md・Hooks・MCP） | 中〜上級 |
| Step 5 | チーム活用とベストプラクティス（セキュリティ・CI/CD） | 全員 |

各ステップは **Lesson（読む）→ Quiz（確認）→ ハンズオン（動かす）** の流れで進みます。

---

## 教材の特徴

### 1. Quiz はその場で採点

静的に答えが書かれているだけのクイズではなく、ラジオボタンで選択して「回答完了」を押すと即採点されます。

* 正解は緑、不正解は赤でハイライト
* 10問・100点満点でスコア表示
* 記述問題はなし（採点の手間ゼロ）

### 2. ハンズオンはブラウザだけで Python が動く

**Pyodide**（Python の WebAssembly 移植版）を使っているので、環境構築なしでブラウザ上で Python を実行できます。

```
# こういう穴埋め問題をブラウザ上で実行できます

def parse_claude_md(content):
    """CLAUDE.md からセクションを抽出する"""
    sections = {}
    current_section = None
    for line in content.splitlines():
        if line.startswith("# "):
            current_section = line[2:].strip()
            sections[current_section] = []
        elif current_section and line.strip():
            # TODO: ここを完成させてください
            pass
    return sections
```

「▶ 実行」「正解を見る」「リセット」の 3 ボタンで、その場で試行錯誤できます。

### 3. MCP Challenge（上級者向け）

Step 4 の発展として、MCP（Model Context Protocol）クライアントの実装チャレンジを用意しました。

MCP は LLM がツールを動的に発見・実行するためのプロトコルです。

MCP クライアント ──── SSE ────▶ MCP サーバー  
① ツール一覧を問い合わせる◀─ ツール定義を返す  
② LLM にツール定義を渡す  
③ ツール実行を委譲する─▶ 実行して結果を返す  
3 箇所の穴埋めを完成させると、ローン計算・日時取得・日数計算の 3 つのツールを持つ MCP サーバーに接続して動かせます。API キー不要の MockLLM 版サンプルも同梱しています。

## 各ステップの内容ダイジェスト

#### Step 1: Claude Code 入門

Claude Code がどういうものかを押さえます。

権限モード（auto-approve / manual / full-auto）の違いと使い分け  
インストールから初回起動まで  
CLAUDE.md の役割（プロジェクトへの指示書）

#### Step 2: ファイル操作と基本ツール

日常的に使う 6 つのツールを体系的に整理しています。

ツール 用途  
Read ファイルを読む  
Write ファイルを新規作成・上書き  
Edit 既存ファイルを部分変更  
Grep 内容をキーワード検索  
Glob ファイル名パターン検索  
Bash シェルコマンド実行  
「Grep と Glob はどう使い分けるか」「Edit と Write の違い」といった実践的な判断基準も説明しています。

#### Step 3: エージェント機能と自動化

Claude Code の真価はここにあります。複雑なタスクを サブエージェント に委任できます。

ユーザーの依頼  
↓  
メイン Claude（調整役）  
↓  
┌────────────────────────┐  
│ サブエージェントA（調査担当）　　　　　　　　 　│  
│ サブエージェントB（実装担当）　　 　　 　 　 　 　│  
│ サブエージェントC（テスト担当）　　　　　　　 　│  
└────────────────────────┘  
↓  
結果をまとめてユーザーに報告  
general-purpose・Explore・Plan・claude-code-guide の 4 種類のエージェントと、並列処理・バックグラウンド実行の使い方を解説しています。

#### Step 4: カスタマイズと高度な設定

チームで使うための設定を整備する内容です。

CLAUDE.md: プロジェクトへの永続的な指示書の書き方  
Hooks: ツール実行前後に自動でコマンドを走らせる仕組み（Lint・フォーマットの自動実行など）  
settings.json: 権限の allow/deny リストの管理  
MCP: 外部サーバーとのツール連携

#### Step 5: チーム活用とベストプラクティス

個人の試行錯誤からチーム展開まで、段階的な導入アプローチを解説しています。

セキュリティ面で特に重要なポイント:

NG（渡してはいけない） OK（渡して良い）  
本番環境の API キー・パスワード 開発環境のコード・設定  
個人情報（氏名・メール等） 匿名化されたサンプルデータ  
社外秘の設計書・仕様書 公開情報・ドキュメント  
良いプロンプトの 5 原則（具体的・コンテキスト付き・出力形式指定・制約明示・段階的）も整理しています。

### 使い方

**リンク先へ移動してそのままオンラインで学習が可能です。**  
*教材の URL: [Claude Code 実践ガイド](https://gokokuyi.github.io/index.html)*

### おわりに

Claude Code は非常に強力なツールですが、「どこまで任せて良いか」「どう安全に使うか」の感覚を掴むまでに少し時間がかかります。この教材がその助けになれば嬉しいです。

チームへの展開を考えている方、Claude Code を体系的に学びたい方にとって参考になれば幸いです。

フィードバック・改善提案は歓迎です！

*教材の URL: [Claude Code 実践ガイド](https://gokokuyi.github.io/index.html)*
