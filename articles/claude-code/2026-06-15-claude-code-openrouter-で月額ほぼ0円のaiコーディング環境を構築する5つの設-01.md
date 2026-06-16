---
id: "2026-06-15-claude-code-openrouter-で月額ほぼ0円のaiコーディング環境を構築する5つの設-01"
title: "Claude Code + OpenRouter で月額ほぼ0円のAIコーディング環境を構築する5つの設定"
url: "https://qiita.com/locallab/items/b82b56fc1fe44bd26f15"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "LLM", "qiita"]
date_published: "2026-06-15"
date_collected: "2026-06-16"
summary_by: "auto-rss"
query: ""
---

## TL;DR

- OpenRouter の `:free` モデルを Claude Code の `ANTHROPIC_API_KEY` 互換エンドポイントとして使う
- モデルルーティング・フォールバック設定で無料枠を最大活用
- 5 つの設定ポイントを押さえれば、有料 Claude Pro に近い体験を月額ほぼ 0 円で再現できる

---

## はじめに

Claude Code は Anthropic のターミナル完結型 AI コーディングツールで、2025 年に OSS 公開されました。デフォルトでは Anthropic 課金が発生しますが、OpenRouter 経由で `:free` タグ付きモデルを使うことで**コストをほぼゼロに抑えながら**コーディング支援を使い続けられます。

本記事では、その構成を実現するための 5 つの設定ポイントを解説します。

---

## 背景: なぜ OpenRouter 経由なのか

OpenRouter は複数の LLM プロバイダを統一 API で提供するプロキシサービスです。多くのモデルに `:free` バリアントが用意されており、レート制限はあるものの **API キー 1 本でさまざまなモデルを無料試用** できます。

Claude Code は `ANTHROPIC_BASE_URL` 環境変数でエンドポイントを上書きできるため、OpenRouter の互換エンドポイントを指定することで透過的に切り替えが可能です。

```
Anthropic API (デフォルト)
    ↓
[ANTHROPIC_BASE_URL を上書き]
    ↓
OpenRouter Endpoint
    ↓
Qwen3-235B-A22B:free / DeepSeek-R1:free / ...
```

---

## 前提

| 要件 | バージョン/備考 |
|---|---|
| Node.js | 18 以上 |
| Claude Code | `npm install -g @anthropic-ai/claude-code` で最新版 |
| OpenRouter アカウント | https://openrouter.ai — 無料登録 |
| シェル | bash / zsh いずれも可 |

---

## 設定ポイント 1: ANTHROPIC_BASE_URL を OpenRouter に向ける

Claude Code が使う Anthropic SDK は `ANTHROPIC_BASE_URL` を参照します。

```bash
export ANTHROPIC_BASE_URL="https://openrouter.ai/api/v1"
export ANTHROPIC_API_KEY="sk-or-v1-xxxxxxxxxxxx"   # OpenRouter のキー
```

OpenRouter のキーは Anthropic の `sk-ant-` キーとは形式が異なりますが、Claude Code 側はキーの中身を検証しないため問題ありません。

> **注意**: `.bashrc` / `.zshrc` に直接書かず、`direnv` や専用の `.env` ファイルで管理して誤ってコミットしないようにしてください。

---

## 設定ポイント 2: 使用モデルを `:free` 枠に固定する

Claude Code はデフォルトで `claude-opus-4-5` など Anthropic の最新モデルを選ぼうとします。OpenRouter 経由では **モデル名をフルパスで指定** する必要があります。

```bash
export ANTHROPIC_MODEL="qwen/qwen3-235b-a22b:free"
```

2026 年時点で `:free` タグが付いていて品質が高いモデルの例:

| モデル名 (OpenRouter スラッグ) | 特徴 |
|---|---|
| `qwen/qwen3-235b-a22b:free` | 235B MoE・コード生成に強い |
| `deepseek/deepseek-r1:free` | 推論特化・複雑なリファクタに有効 |
| `microsoft/phi-4:free` | 軽量・補完速度が速い |
| `meta-llama/llama-4-maverick:free` | 長コンテキスト対応 |

`:free` モデルはレート制限 (通常 20〜200 req/min) があるため、高頻度連打には向きません。**コーディング作業のペースなら十分** です。

---

## 設定ポイント 3: システムプロンプトでモデルの癖を補正する

Qwen3 や DeepSeek は Claude とプロンプト相性が異なるため、Claude Code のシステムプロンプトを微調整すると精度が上がります。

Claude Code は `~/.claude/CLAUDE.md` (グローバル) または プロジェクトルートの `CLAUDE.md` をシステムプロンプトに追記します。

```markdown
# CLAUDE.md (グローバル補正用)

- コードの説明は日本語で行うが、コードブロック内のコメントは英語で書く
- 変更差分は必ず unified diff 形式で提示する
- 推測で実装せず、不明な仕様は質問してから進める
- ファイルを新規作成する前に既存ファイルの確認を必ず行う
```

これは Claude Code の公式ドキュメントでも推奨されている設定で、**モデルによらず有効** です。

---

## 設定ポイント 4: モデルフォールバックを手動で設定する

`:free` モデルはサーバー混雑時に `429 Too Many Requests` を返すことがあります。シェルスクリプトでラッパーを作り、失敗時に別モデルへフォールバックさせましょう。

```bash
#!/usr/bin/env bash
# claude-free.sh — フォールバック付き Claude Code 起動ラッパー

FREE_MODELS=(
  "qwen/qwen3-235b-a22b:free"
  "deepseek/deepseek-r1:free"
  "meta-llama/llama-4-maverick:free"
)

for model in "${FREE_MODELS[@]}"; do
  echo "→ trying model: $model"
  ANTHROPIC_MODEL="$model" claude "$@"
  exit_code=$?

  # 429 or 503 以外なら終了
  if [[ $exit_code -ne 1 ]]; then
    break
  fi
  echo "  rate limited, trying next model..."
  sleep 2
done
```

```bash
chmod +x claude-free.sh
alias cc="./claude-free.sh"
```

`claude "$@"` の終了コードは Claude Code の内部エラーハンドリングに依存しますが、実用上は **モデルを切り替えるだけで解消** することがほとんどです。

---

## 設定ポイント 5: コスト上限を `.claude/settings.json` で設定する

無料枠を超えて誤って有料モデルを呼ばないよう、Claude Code の設定ファイルでガードをかけます。

```json
// ~/.claude/settings.json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://openrouter.ai/api/v1"
  },
  "autoApprove": [],
  "largeContextThreshold": 50000
}
```

`largeContextThreshold` を下げることで、長大なコンテキストを誤って投げてしまうことを抑制できます（無料モデルはコンテキスト上限が有料より小さいケースがあるため）。

また、OpenRouter のダッシュボードから **月次クレジット上限** を $0 に設定しておくと、有料モデルへの誤ルーティングを完全にブロックできます。

---

## 実際の動作確認

設定後、以下のコマンドで動作確認してください。

```bash
# 環境変数の確認
echo $ANTHROPIC_BASE_URL   # https://openrouter.ai/api/v1
echo $ANTHROPIC_MODEL       # qwen/qwen3-235b-a22b:free

# Claude Code 起動
claude --version
claude "hello, which model are you?"
```

正常に動作すれば、モデルが自己申告で `Qwen3` や `DeepSeek` と答えるはずです。

---

## 各設定のまとめ

| # | 設定内容 | ファイル / 変数 |
|---|---|---|
| 1 | Base URL を OpenRouter に向ける | `ANTHROPIC_BASE_URL` |
| 2 | 使用モデルを `:free` に固定 | `ANTHROPIC_MODEL` |
| 3 | システムプロンプトで癖を補正 | `CLAUDE.md` |
| 4 | フォールバックラッパーを作成 | `claude-free.sh` |
| 5 | コスト上限をゼロに設定 | `settings.json` + OpenRouter ダッシュボード |

---

## 注意事項・制限

- `:free` モデルは **レート制限・可用性が有料プランより劣る** ため、締め切り直前の本番作業には不向きです
- OpenRouter の `:free` バリアントは提供が打ち切られることがあります。モデルスラッグは定期的に https://openrouter.ai/models で確認してください
- Claude Code 自体のライセンスは Apache 2.0 (OSS 公開部分) です。利用前に [公式リポジトリ](https://github.com/anthropics/claude-code) を確認してください

---

## まとめ

5 つの設定を組み合わせることで、Claude Code + OpenRouter `:free` モデルによる**月額ほぼ 0 円のAI コーディング環境**が実現できます。

1. `ANTHROPIC_BASE_URL` で OpenRouter に向ける
2. `ANTHROPIC_MODEL` で `:free` モデルを指定
3. `CLAUDE.md` でシステムプロンプトを補正
4. シェルラッパーでフォールバック対応
5. `settings.json` + ダッシュボードでコスト上限をゼロに

無料枠のモデルでも実用十分な品質があります。まずは試してみてください。

---

## 参考リンク

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/ja/docs/claude-code/overview)
- [Claude Code GitHub (Apache 2.0)](https://github.com/anthropics/claude-code)
- [OpenRouter モデル一覧](https://openrouter.ai/models)
- [OpenRouter API ドキュメント](https://openrouter.ai/docs)

---

✍️ 本記事の著者: **合同会社ジモラボ**

ジモラボは、八王子を拠点に AI を活用した SaaS を多数開発しています。本記事の技術検証もそうした開発過程の副産物です。

- 🌐 公式サイト: https://locallab.jp
- 🔍 AI SEO 最適化 SaaS: [lookupai.jp](https://lookupai.jp)
- 📺 YouTube: [@locallab_llc](https://www.youtube.com/@locallab_llc)
- ✉️ お問い合わせ: info@locallab.jp

> 興味を持っていただけたら、ぜひ各 SNS のフォローもお願いします!
