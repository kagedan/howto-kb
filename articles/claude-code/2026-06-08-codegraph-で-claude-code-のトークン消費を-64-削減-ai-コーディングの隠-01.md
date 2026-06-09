---
id: "2026-06-08-codegraph-で-claude-code-のトークン消費を-64-削減-ai-コーディングの隠-01"
title: "CodeGraph で Claude Code のトークン消費を 64% 削減 -- AI コーディングの隠れコストを可視化する"
url: "https://qiita.com/lhjjjk4/items/ce30725427c5bb3c1c0d"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "Gemini", "GPT"]
date_published: "2026-06-08"
date_collected: "2026-06-09"
summary_by: "auto-rss"
query: ""
---

# 🚀 CodeGraph で Claude Code のトークン消費を 64% 削減 — AI コーディングの隠れコストを可視化する

## はじめに

あなたが Claude Code に「このプロジェクトの認証フローってどうなってる？」と質問したとき、Agent は**知らない**ところからスタートします。

プロジェクトの記憶がないため、まず `grep` で検索し、ファイルを読み込み、また検索し…というループを繰り返します。この「探索」だけで、実は**トークン消費の 50〜70%** が費やされているのです。

CodeGraph は、この無駄を根本から断ち切るツールです。プロジェクトのコードを**知識グラフ（Knowledge Graph）**として事前にインデックス化し、Agent が必要な情報を一発で取得できるようにします。

VS Code（約 10,000 ファイル）での実測では、**トークン 64% 削減、ツール呼び出し 81% 削減**を達成。7 つの OSS プロジェクト平均でも **47% のトークン削減**という結果が出ています。

---

## 🔍 なぜ Agent はこんなにトークンを消費するのか？

典型的な探索フローを見てみましょう。

```
grep "payment"          → 47 件ヒット → 800 トークン
read payment.service.ts  → なにか見つかった → 1,200 トークン
grep "processPayment"   → 3 件ヒット → 700 トークン
read order.handler.ts   → 近いけど違う → 950 トークン
grep "db.query"         → 8 件ヒット → 650 トークン
read db.repository.ts   → ここだ！ → 1,100 トークン
```

**合計：6 回のツール呼び出し、5,400 トークン。** これがただ「ファイルを探す」だけのコストです。

この探索税（exploration tax）が、1 日 20 回の質問で積み上がると、月額で数千円〜数万円の無駄になります。

---

## 🧠 CodeGraph の仕組み：知識グラフで grep を置き換える

CodeGraph の核心は「**事前に索引を作っておく**」ことです。

### 4 層アーキテクチャ

| 層 | 処理 | 説明 |
|---|------|------|
| **Layer 1** | ソースコードスキャン | `codegraph init -i` でプロジェクトを読み込み、`node_modules` やビルド成果物は自動除外 |
| **Layer 2** | tree-sitter AST 解析 | 正規表現ではなく、言語文法を理解したパーサーで関数・クラス・メソッドを正確に抽出（20+ 言語対応） |
| **Layer 3** | SQLite 知識グラフ | 抽出した Nodes（関数/クラス/メソッド）と Edges（呼び出し/import/継承）を `.codegraph/codegraph.db` に保存。FTS5 全文検索付き。**100% ローカル** |
| **Layer 4** | MCP サーバー | Agent に 8 つのクエリツールを提供 |

### MCP ツール一覧

| ツール | 用途 |
|--------|------|
| `codegraph_explore` | 「この機能の仕組みは？」→ 関連シンボル + ソースコードを一括返却 |
| `codegraph_search` | シンボル名で検索 |
| `codegraph_callers` | この関数を呼び出しているのは？ |
| `codegraph_callees` | この関数が呼び出しているのは？ |
| `codegraph_impact` | このシンボルを変更したら何が壊れる？ |
| `codegraph_node` | 特定シンボルの完全なソースコード |
| `codegraph_files` | ファイル構造を高速表示 |
| `codegraph_status` | インデックスの状態確認 |

ポイント：grep は「この文字列がどこにあるか」しか教えてくれません。CodeGraph は「**この関数が誰に呼ばれ、誰を呼び、変更するとどこに影響するか**」まで教えてくれます。

---

## 📊 実測データ：7 プロジェクトでのベンチマーク

Claude Opus 4.8 を使い、同一のアーキテクチャ質問を CodeGraph あり/なしで比較（各 4 回実行、中央値）：

| プロジェクト | 言語 | ファイル数 | トークン削減 | ツール呼出削減 | コスト削減 |
|-------------|------|-----------|-------------|---------------|-----------|
| **VS Code** | TS | ~10,000 | **-64%** | **-81%** | -18% |
| **Alamofire** | Swift | ~110 | **-64%** | -58% | **-40%** |
| **Django** | Python | ~3,000 | -60% | -77% | -8% |
| **OkHttp** | Java | ~645 | -54% | -50% | -25% |
| **Tokio** | Rust | ~790 | -38% | -57% | ±0% |
| **Gin** | Go | ~110 | -23% | -44% | -19% |
| **Excalidraw** | TS | ~640 | -25% | -40% | ±0% |

### VS Code の詳細（最高効果）

| 指標 | CodeGraph なし | CodeGraph あり | 削減 |
|------|---------------|---------------|------|
| ファイル読み取り | 9 回 | **0 回** | -9 |
| grep 実行 | 11 回 | **0 回** | -11 |
| ツール呼出合計 | 21 回 | 4 回 | -81% |
| トークン合計 | 179 万 | 64 万 | -64% |
| コスト | $0.83 | $0.68 | -18% |
| 所要時間 | 2 分 13 秒 | 1 分 59 秒 | -11% |

---

## 💰 コスト換算：あなたのプロジェクトでは？

1 日 20 回のアーキテクチャ質問をする場合：

```
CodeGraph なし：20 回 × $0.83 = $16.60/日 → $498/月 → $5,976/年
CodeGraph あり：20 回 × $0.68 = $13.60/日 → $408/月 → $4,896/年
年間削減額：$1,080
```

設定にかかる時間は **3 分**。運用コストは **$0**（すべてローカル、API 不要）。

---

## 🛠️ 5 分で始める導入手順

### Step 1：CLI のインストール

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh

# Windows (PowerShell)
irm https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.ps1 | iex
```

Node.js 不要。インストール後は**新しいターミナルを開いてください**。

### Step 2：Agent に接続

```bash
codegraph install
```

Claude Code、Cursor、Codex、Gemini CLI、Antigravity などを自動検出します。

### Step 3：プロジェクトを初期化

```bash
cd your-project
codegraph init -i
```

`-i` で即座にインデックスを構築します。

### Step 4：Agent を再起動

これだけ。次の質問から Agent が自動的に CodeGraph ツールを使います。

### 動作確認

```bash
codegraph status    # インデックス状態を確認
codegraph query <シンボル名>  # CLI で直接検索
```

---

## ✅ どんな人におすすめ？

**強くおすすめ：**
- **500 ファイル以上のプロジェクト** — コードベースが大きいほど効果が高い
- **Claude Code / Cursor / Codex のヘビーユーザー** — Explore サブ Agent のオーバーヘッドを削減
- **Swift + ObjC、React Native などクロス言語プロジェクト** — grep では追えない言語境界を横断
- **CI/CD で `codegraph affected` を使いたいチーム**

**不要なケース：**
- 50 ファイル未満の小規模プロジェクト
- ChatGPT Web のみを使用（MCP 非対応）
- シンプルな CRUD 作業のみでアーキテクチャ質問をしない

---

## まとめ

CodeGraph は魔法ではありません。事前にコードをインデックス化し、Agent が grep ではなく構造化クエリで知識を取得できるようにする — それだけのツールです。

しかしそのシンプルさゆえに、効果は明確です。

- **平均 47% のトークン削減**
- **平均 58% のツール呼出削減**
- **セットアップ 3 分、ランニングコスト $0**

「grep は文字列の位置を教える。CodeGraph はコードの関係を教える。」

AI コーディングに本気で取り組むなら、この 3 分の投資は今月最高の時間の使い方になるでしょう。

---

**リソース：**
- GitHub: [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph)
- ドキュメント: [colbymchenry.github.io/codegraph](https://colbymchenry.github.io/codegraph/)
