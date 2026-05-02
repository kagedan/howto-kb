---
id: "2026-05-01-rtk-rust-token-killer-aiコーディングアシスタントのトークン消費を最大80削減-01"
title: "RTK (Rust Token Killer) - AIコーディングアシスタントのトークン消費を最大80%削減するCLIツール"
url: "https://zenn.dev/yamitake/articles/rtk-token-killer-introduction"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "Gemini", "TypeScript", "zenn"]
date_published: "2026-05-01"
date_collected: "2026-05-02"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code、GitHub Copilot、Cursor などの AI コーディングアシスタントを使っていると、トークン消費が気になることはありませんか？

特に長いデバッグセッションや、大きな git diff の確認、テスト結果の分析などでは、あっという間にトークンを消費してしまいます。

今回紹介する **RTK (Rust Token Killer)** は、このトークン消費問題を解決する CLI ツールです。

<https://github.com/rtk-ai/rtk>

## RTK とは？

RTK は、AI コーディングアシスタントが受け取るシェルコマンドの出力を最適化することで、**トークン消費を 60-90% 削減**する CLI プロキシツールです。

仕組みはシンプルです：

1. シェルコマンドの実行をインターセプト
2. 出力から不要なノイズやボイラープレートを除去・圧縮
3. 最適化された出力を AI アシスタントに渡す

これにより、同じトークン予算でより多くの作業ができるようになります。

### 実際の効果

公式の計測によると、30分間の Claude Code セッションで：

| 項目 | フィルタなし | RTK使用時 | 削減率 |
| --- | --- | --- | --- |
| トークン数 | 約118,000 | 約23,900 | **約80%削減** |

## 主な機能

### 4つの最適化戦略

RTK は以下の4つの戦略でコマンド出力を最適化します：

1. **Smart Filtering** - 不要なノイズやボイラープレートを除去
2. **Grouping** - 類似した結果を集約
3. **Truncation** - 重要なコンテキストを保持しつつ冗長性を削除
4. **Deduplication** - 繰り返し行を出現回数付きで折りたたみ

### 100以上のコマンドをサポート

* **バージョン管理**: git status, diff, log, push, pull, commit
* **テスト**: Jest, pytest, cargo test, go test, playwright
* **ビルドツール**: TypeScript, ESLint, cargo clippy, ruff
* **ファイル操作**: ls, cat, grep, find, diff
* **パッケージ管理**: npm, pip, pnpm, bundle, prisma
* **クラウド・コンテナ**: AWS CLI, Docker, kubectl

### 12以上の AI ツールに対応

* Claude Code
* GitHub Copilot
* Cursor
* Gemini CLI
* Windsurf
* Cline
* その他多数

## インストール

### Homebrew（推奨）

### クイックインストール

```
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh
```

### Cargo

```
cargo install --git https://github.com/rtk-ai/rtk
```

### 対応プラットフォーム

* macOS
* Linux
* Windows（WSL 推奨）

## セットアップ

インストール後、使用する AI ツールに応じて初期化します：

```
# Claude Code（デフォルト）
rtk init -g

# Gemini CLI
rtk init -g --gemini

# Cursor
rtk init --agent cursor
```

初期化後は、通常のコマンドがシェルフックを通じて自動的に RTK 経由で実行されます。例えば `git status` は内部的に `rtk git status` として実行されます。

## 特に効果的なユースケース

RTK は以下のようなシーンで特に威力を発揮します：

* **長いデバッグセッション** - 多くのコマンド実行と出力の分析
* **大きな git diff やコミット履歴の確認** - コードレビュー時のトークン節約
* **テスト出力の分析** - 冗長なテスト失敗メッセージの圧縮
* **ログファイル分析** - 大量のログ出力のフィルタリング
* **ビルドエラーの分析** - コンパイラ出力を重要なエラーメッセージに凝縮

## 技術的な特徴

* **単一の Rust バイナリ** - 外部依存なし
* **高パフォーマンス** - コマンドあたり 10ms 未満のオーバーヘッド
* **プライバシー重視** - テレメトリはデフォルトで無効、明示的なオプトインが必要
* **Apache-2.0 ライセンス** - オープンソース

## まとめ

RTK は、AI コーディングアシスタントのトークン消費を大幅に削減できる実用的なツールです。

* **60-90% のトークン削減**で、同じ予算でより多くの作業が可能
* **透過的に動作**するため、普段のワークフローを変える必要がない
* **100以上のコマンド**と**12以上の AI ツール**に対応

AI コーディングアシスタントを日常的に使用している方は、ぜひ試してみてください。

## 参考リンク
