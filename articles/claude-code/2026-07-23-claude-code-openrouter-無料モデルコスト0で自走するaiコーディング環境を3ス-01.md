---
id: "2026-07-23-claude-code-openrouter-無料モデルコスト0で自走するaiコーディング環境を3ス-01"
title: "Claude Code × OpenRouter 無料モデル：コスト$0で自走するAIコーディング環境を3ステップで構築する"
url: "https://qiita.com/locallab/items/8c69ac03862e7f396322"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "OpenAI", "qiita"]
date_published: "2026-07-23"
date_collected: "2026-07-24"
summary_by: "auto-rss"
query: ""
---

## TL;DR

- Claude Code の `ANTHROPIC_API_KEY` を差し替えるだけで OpenRouter 経由の無料モデルが使える
- `deepseek/deepseek-r1:free` や `google/gemma-3-27b-it:free` など高品質モデルが **月$0** で利用可能
- 無料枠の RPM/TPM 制限を `.claude/settings.json` のタイムアウト設定で吸収するコツを解説

---

## 背景：Claude Code のコストをゼロに近づけたい

Claude Code は強力なコーディングエージェントだが、Anthropic API を直接使うと **Sonnet 3.7 で 1 MTok あたり $3（入力）** のコストがかかる。ある程度の規模のタスクをこなすと日に数ドルが飛んでいく。

一方、[OpenRouter](https://openrouter.ai) は OpenAI 互換 API として多数のモデルをルーティングしており、`:free` サフィックス付きのモデルは **レートリミット内であれば課金ゼロ** で使える。

この 2 つを組み合わせると「Claude Code の UX + 無料モデルの推論」が実現できる。本記事ではその具体的な設定手順と注意点をまとめる。

---

## 前提知識

| 項目 | 内容 |
|---|---|
| Claude Code バージョン | `@anthropic-ai/claude-code` ≥ 0.2（2025年後半〜） |
| OpenRouter `:free` モデル | 同一モデルに `:free` タグが付いたバリアント。RPM 20〜60 程度・コンテキスト制限あり |
| OpenAI 互換性 | OpenRouter は `https://openrouter.ai/api/v1` で OpenAI Chat Completions 仕様に準拠 |

---

## ステップ 1：OpenRouter のベースURL と APIキー を環境変数にセット

Claude Code は内部で Anthropic SDK を呼ぶが、以下の環境変数を上書きすると **OpenAI 互換エンドポイント** に切り替わる。

```bash
# ~/.zshrc or ~/.bashrc に追記
export ANTHROPIC_BASE_URL="https://openrouter.ai/api/v1"
export ANTHROPIC_API_KEY="sk-or-v1-xxxxxxxxxxxxxxxxxxxx"   # OpenRouter のキー
```

> **注意**: `ANTHROPIC_API_KEY` という変数名のまま OpenRouter のキーを入れる。Claude Code が参照するのはあくまで `ANTHROPIC_API_KEY` であり、値が OpenRouter キーであっても動作する。

設定後に新しいシェルを開くか `source ~/.zshrc` を実行して反映させる。

---

## ステップ 2：使用モデルを `:free` モデルに指定

Claude Code の起動時オプション `--model` でモデルを指定する。

```bash
# DeepSeek R1 無料枠（推論特化・128K context）
claude --model deepseek/deepseek-r1:free

# Google Gemma 3 27B（バランス型・高品質）
claude --model google/gemma-3-27b-it:free

# Meta Llama 3.3 70B Instruct（コーディング安定）
claude --model meta-llama/llama-3.3-70b-instruct:free
```

または `.claude/settings.json`（プロジェクト単位）に固定することもできる。

```json
{
  "model": "google/gemma-3-27b-it:free",
  "apiTimeoutMs": 120000
}
```

> `apiTimeoutMs` を長めに設定する理由はステップ 3 で説明する。

---

## ステップ 3：レートリミットと戦う設定チューニング

`:free` モデルには制約がある。主なものを整理する。

### 3-A. 代表的 `:free` モデルのスペック比較（2025年末〜2026年前半時点）

| モデル | Context | RPM | 特徴 |
|---|---|---|---|
| `deepseek/deepseek-r1:free` | 128K | ~20 | 推論強い・CoT 長め |
| `deepseek/deepseek-chat-v3-0324:free` | 128K | ~60 | コーディング向き・高速 |
| `google/gemma-3-27b-it:free` | 96K | ~30 | 多言語・バランス型 |
| `meta-llama/llama-3.3-70b-instruct:free` | 131K | ~20 | 汎用・英語強い |
| `qwen/qwen3-14b:free` | 40K | ~30 | 日本語・コード両立 |

> RPM は OpenRouter の状況により変動。公式の [openrouter.ai/models](https://openrouter.ai/models) で最新値を確認すること。

### 3-B. 429 Too Many Requests を減らす

Claude Code はデフォルトでリトライ間隔が短い。以下の設定で緩和できる。

```json
// .claude/settings.json
{
  "model": "deepseek/deepseek-chat-v3-0324:free",
  "apiTimeoutMs": 180000,
  "maxRetries": 5
}
```

また、作業セッションを **1 タスクずつ順番に流す**（並列実行しない）ことで RPM 超過を防げる。

### 3-C. コンテキストが長い場合の注意

`:free` モデルはコンテキスト上限が有料版より低い場合がある。大規模リポジトリで `claude` を使う際は `/compact` コマンドを早めに発行してコンテキストを圧縮しておく。

```
# Claude Code 内でのコマンド
/compact
```

---

## 実運用：どのモデルをいつ使うか

| シーン | 推奨モデル | 理由 |
|---|---|---|
| バグ修正・小規模リファクタ | `deepseek/deepseek-chat-v3-0324:free` | RPM 高め・応答速い |
| 設計レビュー・複雑推論 | `deepseek/deepseek-r1:free` | CoT が強い |
| 日本語コメント・ドキュメント生成 | `qwen/qwen3-14b:free` | 日本語品質が高い |
| 英語中心・大型コードベース | `meta-llama/llama-3.3-70b-instruct:free` | 131K context |

---

## フォールバック構成：無料枠を使い切ったら有料へ自動切替

OpenRouter には **Route 機能** がある。`:free` モデルが 429 を返したとき、同名の有料モデルへ自動フォールバックさせる設定が可能だ。

`ANTHROPIC_BASE_URL` のクエリパラメータは使えないが、**モデル名を `:free` なしにするだけ**で有料枠に切り替わる。

スクリプトで切り替える場合はこのようなラッパーが使える：

```bash
#!/bin/bash
# claude-free.sh: 無料モデルで起動、失敗時は有料モデルで再試行

MODEL_FREE="deepseek/deepseek-chat-v3-0324:free"
MODEL_PAID="deepseek/deepseek-chat-v3-0324"

claude --model "$MODEL_FREE" "$@"
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  echo "⚠️ Free model failed (exit $EXIT_CODE). Retrying with paid model..."
  claude --model "$MODEL_PAID" "$@"
fi
```

---

## よくあるトラブルシューティング

### `model not found` エラー

OpenRouter のモデル名は `/` 区切りの完全修飾名が必要。`deepseek-r1` ではなく `deepseek/deepseek-r1:free` と指定する。

```bash
# NG
claude --model deepseek-r1:free

# OK
claude --model deepseek/deepseek-r1:free
```

### レスポンスが返ってこない（タイムアウト）

R1 などの思考モデルは CoT が長く、初回応答まで 60 秒以上かかることがある。`apiTimeoutMs: 180000`（3 分）を設定しておくと安定する。

### ツール呼び出し（function calling）が動かない

一部の `:free` モデルはツール呼び出しをサポートしていない。Claude Code はファイル読み書き等に内部ツールを使うため、**必ず tool use 対応モデルを選ぶ**こと。

対応確認は OpenRouter の各モデルページ（`Features` 欄）で `Tools` が ✅ のものを選ぶ。

---

## まとめ

| ポイント | 内容 |
|---|---|
| 環境変数 2 つ | `ANTHROPIC_BASE_URL` + `ANTHROPIC_API_KEY` を差し替えるだけ |
| コスト | `:free` モデルなら $0（RPM 制限内） |
| 品質 | DeepSeek V3 / R1 は有料モデルと遜色ない水準 |
| 注意点 | RPM 制限・tool use 対応確認・タイムアウト設定が必要 |

Claude Code の UX はそのままに、推論コストをほぼゼロに抑えられる。日常的なコーディングサポートや CI 上の自動レビューなど、コスト感度が高いユースケースから試してみることをおすすめする。

---

## 参考リンク

- [Claude Code 公式ドキュメント — Model Configuration](https://docs.anthropic.com/ja/docs/claude-code)
- [OpenRouter — モデル一覧](https://openrouter.ai/models)
- [OpenRouter — API Reference](https://openrouter.ai/docs/api-reference)
- [DeepSeek R1 技術レポート (arXiv:2501.12948)](https://arxiv.org/abs/2501.12948)
- [Qwen3 技術ブログ](https://qwenlm.github.io/blog/qwen3/)

---

✍️ 本記事の著者: **合同会社ジモラボ**

ジモラボは、八王子を拠点に AI を活用した SaaS を多数開発しています。本記事の技術検証もそうした開発過程の副産物です。

- 🌐 公式サイト: https://locallab.jp
- 🔍 AI SEO 最適化 SaaS: [lookupai.jp](https://lookupai.jp)
- 📺 YouTube: [@locallab_llc](https://www.youtube.com/@locallab_llc)
- ✉️ お問い合わせ: info@locallab.jp

> 興味を持っていただけたら、ぜひ各 SNS のフォローもお願いします！
