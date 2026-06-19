---
id: "2026-06-18-revenue-kun-に-claude-code-project-workflow-を実装した話-01"
title: "revenue-kun に Claude Code project workflow を実装した話"
url: "https://qiita.com/Matsda_K/items/63e7a3e9e0f9c97d9cd8"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "cowork", "Python", "qiita"]
date_published: "2026-06-18"
date_collected: "2026-06-19"
summary_by: "auto-rss"
query: ""
---

## revenue-kun とは

直接還元法（NOI ÷ 還元利回り）による収益試算を補助するOSSのCLIツールです（Apache 2.0）。

レントロール PDF を読み込んで収入側を自動集計し、収益試算 Excel ワークブックを出力します。

> ⚠️ 出力は「収益試算値」であり、鑑定評価による「収益価格」ではありません。  
> 投資判断・法律判断・税務判断は不動産鑑定士・弁護士・税理士にご確認ください。

https://github.com/signal-yield/revenue-kun

## 実装したもの

### 1. Claude Code project workflow（3ファイル）

Claude Code をプロジェクトディレクトリで開くだけで有効になります。

| ファイル | 役割 |
|----------|------|
| `CLAUDE.md` | 安全ルール・Checkpoint・禁止コマンドの定義 |
| `.claude/settings.json` | Bash の自動承認コマンド許可リスト |
| `.claude/commands/revenue-kun.md` | `/revenue-kun` スラッシュコマンド |

`/revenue-kun data/sample_rentroll_simple.pdf` と打つだけで
dry-run → 抽出確認（Checkpoint A）→ Excel 生成 → セルレビュー（Checkpoint B）
の全ステップを Claude が補助します。

### 2. Package Skill（claude.ai / Cowork 対応）

`skill/` ディレクトリにエンジンをバンドルしており、
clone もターミナルも Python 環境構築も不要です。
PDF をアップロードすると収益試算 Excel が出ます。

```bash
# build_skill.py でエンジンを skill/scripts/ に同期
python build_skill.py

# 同期確認
diff -r src/revenue_kun skill/scripts/revenue_kun && echo "in sync"
```

### 3. OER 自動計算モデル

Excel ワークブックの `直接還元法_OER` シートに EGI→NOI→収益試算値の計算式を実装しました。

| セル | 式 |
|------|----|
| E20 | `=E10*(1-N(E13)-N(E14))` EGI |
| E22 | `=E20-E21` NOI |
| E24 | `=IFERROR(E23/E17,"")` 収益試算値 |

E13:E17（空室損失率・貸倒損失率・経費率・資本的支出・還元利回り）はユーザーが手入力します。
Claude は値を提案しません。

## テスト

```bash
python -m pytest -q
# 200 passed
```

## 現在の制限

- 合成サンプルで動作確認済み
- qualifying real-world text-based PDF の評価は未完了（Issue #21 open）
- OCR・スキャン PDF は非対応
- 鑑定評価・投資助言・法律助言・税務助言は対象外
