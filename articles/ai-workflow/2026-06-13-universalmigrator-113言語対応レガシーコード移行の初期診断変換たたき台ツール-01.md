---
id: "2026-06-13-universalmigrator-113言語対応レガシーコード移行の初期診断変換たたき台ツール-01"
title: "UniversalMigrator — 113言語対応、レガシーコード移行の初期診断＆変換たたき台ツール"
url: "https://zenn.dev/highdefini/articles/e98109a3caf668"
source: "zenn"
category: "ai-workflow"
tags: ["API", "Python", "zenn"]
date_published: "2026-06-13"
date_collected: "2026-06-14"
summary_by: "auto-rss"
query: ""
---

レガシーコード移行の初期診断と変換たたき台を作る GUI / CLI ツールです。113 種類のプログラミング言語（＋一覧に無い言語もカスタム指定可）に対応し、Anthropic Claude API を AI エンジンとして使用します。フォルダ内のファイルを一括解析・変換し、サブフォルダ構造も維持します。

> 目的は「完全自動で本番移行を終えること」ではなく、既存コード資産を読み取り、移行方針・難易度・変換候補を早く見える形にすることです。
>
> ## 🎯 これは何？（30秒で）
>
> * **誰のため**：複数言語のレガシー資産を抱える情シス・SI ベンダー／言語移行の PoC を企画している開発リード
> * + **何が解決される**：113 言語＋カスタム言語に対応した「移行たたき台＋難易度可視化」ツール。言語固定ツールでは扱えない「あらゆる組み合わせ」をカバー

```
git clone https://github.com/highdefinitionaudiodriver/UniversalMigrator
cd UniversalMigrator
python -m pip install -r requirements.txt
# Anthropic API キーを環境変数に設定
set ANTHROPIC_API_KEY=sk-...
python app.py        # GUI
# または CLI でフォルダを指定して一括処理
```

詳細なオプション・対応言語一覧は README を参照してください。

## 関連プロジェクト

---

## リポジトリ / ライセンス
