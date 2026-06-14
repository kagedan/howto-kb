---
id: "2026-06-13-claude-code-openrouter-free-モデル-で-ai-コーディング支援コストを約-01"
title: "Claude Code × OpenRouter :free モデル で AI コーディング支援コストを約90%削減した5つの設定"
url: "https://qiita.com/locallab/items/a2d6147453852ad3d328"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "LLM", "OpenAI", "Gemini"]
date_published: "2026-06-13"
date_collected: "2026-06-14"
summary_by: "auto-rss"
query: ""
---

## TL;DR

- Claude Code のバックエンドを OpenRouter の `:free` モデルに切り替えるだけで、API コストをほぼゼロに近づけられる
- モデル選択・プロンプト設計・タスク分類の3軸で品質を維持しつつ低コスト運用が可能
- 「思考系タスク」と「定型補完系タスク」を分けるルーティングが鍵

---

## 背景

Claude Code を日常的なコーディング支援に使い始めると、すぐに直面するのが **API コスト問題** です。Claude 3.7 Sonnet をフル活用すると、1 日の開発作業で数ドル〜十数ドルの課金が発生することも珍しくありません。

OpenRouter は複数の LLM プロバイダーを統一 API で呼べるゲートウェイで、**モデル名の末尾に `:free` を付けると無料枠で呼び出せるモデル**が多数用意されています（2026 年時点）。

本記事では、Claude Code の設定ファイルと環境変数を使って **OpenRouter :free モデルへルーティングする構成** を解説します。社内コードは一切含まず、公式ドキュメントと OSS の一般知識のみに基づいています。

---

## 前提知識

| ツール | 役割 |
|---|---|
| [Claude Code](https://docs.anthropic.com/claude-code) | Anthropic 公式の CLI ベース AI コーディング支援ツール |
| [OpenRouter](https://openrouter.ai/docs) | マルチ LLM ゲートウェイ。OpenAI 互換 API を提供 |
| `:free` モデル | OpenRouter が無料枠として提供するモデル群 (レート制限あり) |

---

## ポイント 1: Claude Code の `ANTHROPIC_BASE_URL` オーバーライド

Claude Code は内部で Anthropic Messages API を叩いていますが、環境変数 `ANTHROPIC_BASE_URL` を設定することで **互換 API エンドポイントへのルーティングが可能** です（公式ドキュメント記載の機能）。

```bash
# .env.local または shell の設定ファイルへ記述
export ANTHROPIC_BASE_URL="https://openrouter.ai/api/v1"
export ANTHROPIC_API_KEY="<your-openrouter-api-key>"
```

> ⚠️ API キーの値は絶対に Git にコミットしないでください。`.gitignore` への追加を徹底しましょう。

OpenRouter の API キーは [openrouter.ai/keys](https://openrouter.ai/keys) で発行できます（無料アカウントで即時発行可）。

---

## ポイント 2: `:free` モデルの選定基準（2026 年版）

`:free` モデルはレートリミットが厳しいものの、**タスクの性質に応じて使い分ける**ことでボトルネックを回避できます。

```
タスク分類の目安

■ :free モデルで十分なタスク
  - コメント・ドキュメント生成
  - 単純なリファクタリング (関数名変更、変数整理)
  - 型定義の補完 (TypeScript, Rust など)
  - テストケースのスケルトン生成
  - README / CHANGELOG の草稿

■ 有料モデルが望ましいタスク
  - アーキテクチャ設計・技術選定
  - 複雑なデバッグ (マルチスレッド競合、メモリリーク)
  - 新規ドメインロジックのゼロから実装
  - セキュリティレビュー
```

2026 年 5 月時点で Claude Code との相性が良い `:free` モデルの例：

| モデル ID (OpenRouter) | 特徴 |
|---|---|
| `qwen/qwen3-235b-a22b:free` | 多言語対応・コード補完に強い |
| `google/gemini-2.0-flash-exp:free` | 高速・コンテキスト長が広い |
| `meta-llama/llama-4-maverick:free` | 英語コードに強い・Llama 4 系最大 |
| `deepseek/deepseek-chat-v3-0324:free` | コード生成精度が高評価 |
| `mistralai/mistral-small-3.2-24b-instruct:free` | 軽量・補完系に最適 |

> 📌 利用可能なモデルは [openrouter.ai/models](https://openrouter.ai/models) でフィルタ `Free` を選ぶと一覧できます。ラインナップは頻繁に更新されるので、定期確認を推奨します。

---

## ポイント 3: `CLAUDE.md` でモデルのデフォルトを固定する

Claude Code はプロジェクトルートの `CLAUDE.md` を読み込んで動作指針にします。ここに **「このプロジェクトではコスト抑制のため :free モデルを優先する」** 旨を書いておくと、Claude Code 自身がモデル選択の判断に使います。

```markdown
# CLAUDE.md (プロジェクト用・公開リポジトリ向けサンプル)

## モデル使用ポリシー

このプロジェクトでは OpenRouter :free モデルをデフォルトとして使用します。

- ドキュメント生成・コメント補完・軽微なリファクタリング → :free モデル
- アーキテクチャ判断・複雑なデバッグ → 有料モデルへ手動昇格

## コーディング規約

- TypeScript strict mode を必ず有効にする
- 関数は 40 行以内に収める
- コメントは日本語 OK
```

---

## ポイント 4: `--model` フラグによる都度切り替え

CLI から直接モデルを指定したい場合は `--model` フラグが使えます。

```bash
# :free モデルで起動
claude --model qwen/qwen3-235b-a22b:free

# タスクが複雑なら有料モデルに昇格
claude --model anthropic/claude-sonnet-4-5
```

シェル関数としてエイリアスを定義しておくと便利です：

```bash
# ~/.bashrc または ~/.zshrc

# 軽量タスク向け (無料)
alias cc-free='claude --model qwen/qwen3-235b-a22b:free'

# 重いタスク向け (有料・明示的に使うときだけ)
alias cc-pro='claude --model anthropic/claude-sonnet-4-5'
```

---

## ポイント 5: レートリミット対策 — 指数バックオフの自作スクリプト

`:free` モデルは 1 分あたりのリクエスト数に上限があります。CI 等で複数ファイルを連続処理する場合は、429 エラー時に **指数バックオフ** でリトライするシェルラッパーを挟むと安定します。

```bash
#!/usr/bin/env bash
# claude-with-backoff.sh — :free モデル向け指数バックオフラッパー

MAX_RETRIES=5
DELAY=2

for i in $(seq 1 $MAX_RETRIES); do
  claude "$@" && exit 0

  EXIT_CODE=$?
  if [ $EXIT_CODE -eq 2 ]; then
    # claude コマンドが 429 相当のエラーを返した場合
    echo "[retry $i/$MAX_RETRIES] Rate limited. Waiting ${DELAY}s..." >&2
    sleep $DELAY
    DELAY=$((DELAY * 2))
  else
    # 429 以外のエラーはリトライしない
    exit $EXIT_CODE
  fi
done

echo "Max retries exceeded." >&2
exit 1
```

```bash
chmod +x claude-with-backoff.sh

# 使い方
./claude-with-backoff.sh --model qwen/qwen3-235b-a22b:free \
  "この関数に JSDoc コメントを追加して" \
  --file src/utils/format.ts
```

---

## コスト比較 (概算)

| 構成 | 月間コスト目安 (個人開発・中規模) |
|---|---|
| Claude Sonnet フル使用 | $30 〜 $80 |
| :free モデル中心 + Sonnet を重タスクのみ | $3 〜 $10 |
| :free モデルのみ (軽量プロジェクト) | $0 〜 $1 |

> ※ 上記はあくまで概算です。実際のコストはプロジェクト規模・リクエスト頻度・モデルのコンテキスト長消費によって大きく変動します。OpenRouter ダッシュボードの Usage タブで随時確認してください。

---

## よくある落とし穴

### 1. Messages API 互換性の差異

OpenRouter は OpenAI 互換エンドポイントを提供していますが、Anthropic の独自パラメータ（`thinking`、`betas` ヘッダ等）は一部のモデルでサポートされません。Claude Code が内部で拡張パラメータを送った場合、フォールバックか無視されます。

→ **対策**: 拡張機能（Extended Thinking など）を使う場面では `ANTHROPIC_BASE_URL` をリセットして本家 Anthropic エンドポイントに戻す。

```bash
# Anthropic 本家を使いたいときだけ一時的に上書き
ANTHROPIC_BASE_URL="" claude --model claude-sonnet-4-5 "アーキテクチャを設計して"
```

### 2. :free モデルの突然の廃止・仕様変更

`:free` 枠は OpenRouter のプロモーション施策であり、**予告なく終了・レート変更されることがあります**。

→ **対策**: 使用モデルを `CLAUDE.md` または設定ファイルに一元管理し、切り替えコストを最小化する。

### 3. コンテキスト長の差

`:free` モデルによっては context window が 8K〜32K と短い場合があります。大きなファイルを丸ごと食わせると途中で切れることも。

→ **対策**: `claude --file` で渡す前にファイルを関数単位で分割するか、長大ファイルは有料モデルにルーティングする。

---

## まとめ

| ポイント | 内容 |
|---|---|
| ① エンドポイント切り替え | `ANTHROPIC_BASE_URL` で OpenRouter へ向ける |
| ② モデル選定 | タスク複雑度でルーティングを分離 |
| ③ CLAUDE.md 活用 | プロジェクトポリシーとして明文化 |
| ④ エイリアス | `cc-free` / `cc-pro` でワンコマンド切り替え |
| ⑤ バックオフ | 429 エラーに備えたリトライラッパー |

Claude Code と OpenRouter `:free` モデルの組み合わせは、個人開発・スタートアップの初期フェーズで **品質とコストのバランスを取る現実解** です。まずは `ANTHROPIC_BASE_URL` の 1 行だけ変えてみてください。

---

## 参考リンク

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/claude-code)
- [OpenRouter 公式ドキュメント](https://openrouter.ai/docs)
- [OpenRouter モデル一覧 (Free フィルタ)](https://openrouter.ai/models?max_price=0)
- [OpenRouter API Reference](https://openrouter.ai/docs/api-reference)
- [Qwen3 技術レポート (Hugging Face)](https://huggingface.co/Qwen/Qwen3-235B-A22B)
- [DeepSeek-V3 技術レポート](https://github.com/deepseek-ai/DeepSeek-V3)

---

✍️ 本記事の著者: **合同会社ジモラボ**

ジモラボは、八王子を拠点に AI を活用した SaaS を多数開発しています。本記事の技術検証もそうした開発過程の副産物です。

- 🌐 公式サイト: https://locallab.jp
- 🔍 AI SEO 最適化 SaaS: [lookupai.jp](https://lookupai.jp)
- 📺 YouTube: [@locallab_llc](https://www.youtube.com/@locallab_llc)
- ✉️ お問い合わせ: info@locallab.jp

> 興味を持っていただけたら、ぜひ各 SNS のフォローもお願いします!
