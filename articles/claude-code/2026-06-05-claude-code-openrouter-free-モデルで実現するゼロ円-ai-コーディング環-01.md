---
id: "2026-06-05-claude-code-openrouter-free-モデルで実現するゼロ円-ai-コーディング環-01"
title: "Claude Code + OpenRouter Free モデルで実現する「ゼロ円 AI コーディング環境」構築 3 ステップ"
url: "https://qiita.com/locallab/items/fbd5358cb58768cde586"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "LLM", "GPT"]
date_published: "2026-06-05"
date_collected: "2026-06-06"
summary_by: "auto-rss"
query: ""
---

## TL;DR

- OpenRouter の `:free` モデルは商用利用可能な LLM を API キー 1 本で無料使用できる
- Claude Code の `--model` フラグと環境変数で外部エンドポイントに向ける方法を解説
- 月額 0 円スタートでも Qwen3-235B・Llama-4-Maverick など高品質モデルが使える

---

## 背景: AI コーディングツールのコスト問題

Claude Code、GitHub Copilot、Cursor——AI コーディングアシスタントは 2025〜2026 年にかけて爆発的に普及したが、いずれも月 $20〜$100 の課金が伴う。「個人学習・OSS 貢献・副業プロジェクトに使いたいが、まず無料で試したい」というニーズは根強い。

OpenRouter が提供する **`:free` サフィックスモデル** はこの問題を解決するエントリーポイントになる。本記事ではその仕組みと、Claude Code (Anthropic 公式 CLI) を OpenRouter 経由で動かすセットアップ手順を解説する。

> **注意**: Claude Code 自体は Anthropic のプロダクトであり、公式にサポートされたプロキシ設定以外は Anthropic の利用規約に従う。本記事の内容は 2026 年 5 月時点の公開ドキュメントに基づく。

---

## 1. OpenRouter `:free` モデルとは

OpenRouter (openrouter.ai) はさまざまな LLM プロバイダーへの統一 API ゲートウェイを提供するサービスだ。モデル名の末尾に `:free` が付くバリアントは **レート制限あり・商用利用は各モデルのライセンス次第** だが、API 呼び出しに金銭的コストがかからない。

### 代表的な `:free` モデル (2026 年 5 月時点)

| モデル名 | パラメータ規模 | 特徴 |
|---|---|---|
| `qwen/qwen3-235b-a22b:free` | 235B (MoE) | コーディング・推論が強力 |
| `meta-llama/llama-4-maverick:free` | Maverick サイズ | マルチモーダル対応 |
| `mistralai/mistral-7b-instruct:free` | 7B | 軽量・高速 |
| `google/gemma-3-27b-it:free` | 27B | 日本語も比較的安定 |

ライセンス: Qwen3 は Apache 2.0、Llama 4 は Llama 4 Community License、Mistral は Apache 2.0、Gemma 3 は Gemma Terms of Use (商用利用に条件あり)。**商用プロダクトへの組み込みは各ライセンスを必ず確認すること。**

---

## 2. 環境構築 3 ステップ

### ステップ 1: OpenRouter API キーを取得する

1. [openrouter.ai](https://openrouter.ai) にアクセスしてアカウント作成
2. 「Keys」ページで API キーを生成
3. `:free` モデルのみ使う場合、クレジットチャージは不要

```bash
# 動作確認 (curl)
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen/qwen3-235b-a22b:free",
    "messages": [{"role": "user", "content": "Hello, world!"}]
  }'
```

---

### ステップ 2: Claude Code を OpenRouter エンドポイントへ向ける

Claude Code は環境変数 `ANTHROPIC_API_KEY` に加えて、`ANTHROPIC_BASE_URL` でベース URL を差し替えられる。OpenRouter は Anthropic Messages API 互換エンドポイント (`/v1/messages`) を提供しているため、この仕組みを活用できる。

```bash
export ANTHROPIC_BASE_URL="https://openrouter.ai/api/v1"
export ANTHROPIC_API_KEY="sk-or-v1-xxxxxxxxxx"  # OpenRouter キーを使用
```

> **ポイント**: `ANTHROPIC_API_KEY` の値は OpenRouter キーに差し替える。Claude Code は内部でこのキーを Authorization ヘッダーに付与するため、OpenRouter がリクエストを受け取って適切なモデルにルーティングする。

次にモデルを指定する:

```bash
claude --model "qwen/qwen3-235b-a22b:free" "このコードのバグを直して"
```

または `CLAUDE_MODEL` 環境変数で固定することもできる (バージョンによって異なるため `claude --help` で確認):

```bash
export CLAUDE_MODEL="qwen/qwen3-235b-a22b:free"
claude "関数のテストを書いて"
```

---

### ステップ 3: `.env.local` で設定をプロジェクト単位に管理

毎回 `export` するのは煩雑なので、`direnv` と組み合わせるとプロジェクトディレクトリに入るだけで自動適用できる。

```bash
# direnv のインストール
brew install direnv           # macOS
sudo apt install direnv       # Ubuntu

# プロジェクトルートに .envrc を作成
cat > .envrc << 'EOF'
export ANTHROPIC_BASE_URL="https://openrouter.ai/api/v1"
export ANTHROPIC_API_KEY="sk-or-v1-xxxxxxxxxx"
export CLAUDE_MODEL="qwen/qwen3-235b-a22b:free"
EOF

direnv allow .
```

> **セキュリティ注意**: `.envrc` は `.gitignore` に追加し、リポジトリに API キーを含めないこと。

```gitignore
# .gitignore
.envrc
.env.local
```

---

## 3. レート制限と実用上の注意点

`:free` モデルには以下の制約がある:

| 制限種別 | 目安 |
|---|---|
| RPM (requests per minute) | 10〜20 rpm 程度 (モデルにより異なる) |
| TPM (tokens per minute) | 50,000〜200,000 tpm |
| コンテキスト長 | モデル依存 (Qwen3-235B は 32K〜128K) |
| 優先度 | 有料ユーザーより低い (混雑時に遅延) |

実運用では **Backoff + Retry** を実装するか、Claude Code のタイムアウト設定を長めにとるのが現実的だ:

```python
# Python で OpenRouter を直接呼ぶ場合の Retry 例
import time
import httpx

def call_with_retry(payload, max_retries=3):
    for attempt in range(max_retries):
        resp = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json=payload,
            timeout=60,
        )
        if resp.status_code == 429:
            wait = 2 ** attempt  # exponential backoff
            print(f"Rate limited. Waiting {wait}s...")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError("Max retries exceeded")
```

---

## 4. モデル選定の指針

用途別に使い分けるのがおすすめだ:

### コーディング・バグ修正

```
qwen/qwen3-235b-a22b:free
```

Qwen3-235B は HumanEval・LiveCodeBench 系のベンチマークで GPT-4 クラスに匹敵するスコアを記録しており (Qwen チームの公式ブログ参照)、無料モデルの中では最高品質の選択肢の一つ。

### 軽量タスク (コメント生成・変数名提案)

```
mistralai/mistral-7b-instruct:free
```

7B モデルなので応答が速く、レート制限に引っかかりにくい。繰り返し実行するスクリプト系 CI タスクに向く。

### 日本語ドキュメント生成

```
google/gemma-3-27b-it:free
```

Gemma 3 は多言語対応が改善されており、日本語の README 生成や PR 説明文の作成に使いやすい。ただし Gemma Terms of Use により **特定の商用用途には制限あり** なので利用前に確認を。

---

## 5. よくある落とし穴と対処法

### 落とし穴 1: モデルが「現在利用不可」になる

`:free` モデルは OpenRouter 側の需要に応じて提供が一時停止される場合がある。

**対処**: フォールバックモデルを用意する。

```bash
# シェルスクリプトで主/副モデルを切り替え
PRIMARY_MODEL="qwen/qwen3-235b-a22b:free"
FALLBACK_MODEL="mistralai/mistral-7b-instruct:free"

claude --model "$PRIMARY_MODEL" "$@" || \
  claude --model "$FALLBACK_MODEL" "$@"
```

### 落とし穴 2: コンテキスト長不足でコードが途中で切れる

大きなファイルをそのまま渡すと max_tokens に引っかかる。

**対処**: 関数・クラス単位に分割して渡す。`git diff HEAD~1` の差分だけを渡すのも有効。

```bash
# 差分だけ Claude に渡す
git diff HEAD~1 | claude "この変更のコードレビューをして"
```

### 落とし穴 3: Anthropic API との非互換

OpenRouter の Anthropic 互換エンドポイントでも、`system_prompt` の扱いや `tool_use` の実装がネイティブ Anthropic API と微妙に異なる場合がある。

**対処**: Claude Code の高度な機能 (MCP ツール呼び出し等) を使う際は、ネイティブ Anthropic API キーに切り替えて動作確認を行う。

---

## まとめ

| ステップ | 内容 |
|---|---|
| 1 | OpenRouter でアカウント作成・API キー取得 |
| 2 | `ANTHROPIC_BASE_URL` と `ANTHROPIC_API_KEY` を設定して Claude Code を向ける |
| 3 | `direnv` で `.envrc` に設定を集約しプロジェクト単位で管理 |

月額ゼロ円で Claude Code ライクなコーディング体験をスタートできる。モデルの品質・速度に満足できたら OpenRouter のクレジットを追加するか、Anthropic ネイティブ API に切り替えるという段階的な移行も自然にできる。

AI コーディング環境への投資ハードルを下げ、まず動かしてみることが重要だ。

---

## 参考リンク

- [OpenRouter 公式ドキュメント](https://openrouter.ai/docs)
- [OpenRouter モデル一覧](https://openrouter.ai/models)
- [Claude Code 公式ドキュメント](https://docs.anthropic.com/ja/docs/claude-code/overview)
- [Qwen3 技術レポート (Qwen チーム公式)](https://qwenlm.github.io/blog/qwen3/)
- [Llama 4 Community License](https://llama.meta.com/llama4/license/)
- [direnv 公式](https://direnv.net/)

---

✍️ 本記事の著者: **合同会社ジモラボ**

ジモラボは、八王子を拠点に AI を活用した SaaS を多数開発しています。本記事の技術検証もそうした開発過程の副産物です。

- 🌐 公式サイト: https://locallab.jp
- 🔍 AI SEO 最適化 SaaS: [lookupai.jp](https://lookupai.jp)
- 📺 YouTube: [@locallab_llc](https://www.youtube.com/@locallab_llc)
- ✉️ お問い合わせ: info@locallab.jp

> 興味を持っていただけたら、ぜひ各 SNS のフォローもお願いします!

---

## 投稿前セルフレビュー

- [x] 4-A〜4-D に該当する記述は 1 件もないか? → **YES** (社内構成・環境変数・社内コード不含)
- [x] コード断片は OSS / 公式 docs / 学習用最小例のみか? → **YES**
- [x] 引用した OSS のライセンスを明記したか? → **YES** (Qwen3/Apache 2.0, Llama 4/Llama 4 Community, Mistral/Apache 2.0, Gemma 3/Gemma Terms)
- [x] 引用した数値・ベンチマークの出典 URL を記載したか? → **YES** (Qwen チーム公式ブログ)
- [x] タイトルに数字を入れて検索性を高めたか? → **YES** (「3 ステップ」)
- [x] タグは Qiita の慣習に合っているか? → 推奨タグ: `OpenRouter`, `ClaudeCode`, `LLM`, `AI`, `開発環境`
- [x] 末尾にプロフィール+lookupai リンクを付けたか? → **YES**
- [x] lookupai への自然な誘導が 1〜2 箇所あるか? → **YES** (フッターで 1 箇所)
- [x] 誤字脱字・コードブロックの言語指定は OK か? → **YES**
