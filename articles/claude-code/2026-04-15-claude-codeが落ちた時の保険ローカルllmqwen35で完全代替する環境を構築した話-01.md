---
id: "2026-04-15-claude-codeが落ちた時の保険ローカルllmqwen35で完全代替する環境を構築した話-01"
title: "Claude Codeが落ちた時の保険：ローカルLLM(Qwen3.5)で完全代替する環境を構築した話"
url: "https://qiita.com/ryun818/items/a2f7fa6d76d2d48b121a"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "LLM", "qiita"]
date_published: "2026-04-15"
date_collected: "2026-04-16"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Codeが障害で使えない時のフォールバックとして、ローカルLLMで置き換える仕組みを構築しました。

ネット上の情報は断片的で、実際にやってみると**既知のバグや設定の罠が大量**にあり、動くまでに半日溶かしました。同じ道を辿る人のために、ハマりポイントと最終的な動作する構成をまとめます。

**結論**: llama.cpp + Qwen3.5-35B-A3B (Unsloth GGUF) + 適切な環境変数で、Claude Code CLIの対話モードがローカルLLMで動きます。

## 環境

* Apple MacBook Pro M2 Max (64GB統合メモリ、38GPUコア)
* Claude Code v2.1.104
* llama.cpp (最新)
* zsh

## 最終的な性能

| 項目 | Ollama (最初の試み) | llama.cpp (最終構成) |
| --- | --- | --- |
| 初回応答 | 2分40秒〜8分24秒 | **1分30秒** |
| 2回目以降（キャッシュヒット） | 2分前後 | **8秒** |
| プロンプト処理速度 | 40-52 tok/s | **237-763 tok/s** |
| 動作モード | 対話モード不安定 | ✅ 対話モード動作 |

## なぜOllamaではダメだったのか

最初にOllamaで試しましたが、応答に2〜8分かかり実用不可でした。原因は複数：

1. **Thinkingモード** - Qwen3.5はデフォルトで思考プロセスを大量出力（800+トークンの無駄）
2. **コンテキストサイズ** - デフォルト262,144トークンでメモリを圧迫（34GB占有）
3. **プロンプト処理速度** - Ollamaは40-52 tok/s、llama.cppの1/5程度
4. **パラメータ調整の自由度不足** - KVキャッシュ量子化やバッチサイズの細かい制御ができない

Ollama v0.19 + MLXバックエンドでも改善したものの、根本解決には至らず llama.cpp 直接実行に切り替えました。

## 構築手順

### 1. llama.cppのビルド

```
git clone --depth 1 https://github.com/ggml-org/llama.cpp /Users/ryun/llama.cpp
cmake /Users/ryun/llama.cpp -B /Users/ryun/llama.cpp/build \
    -DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=OFF
cmake --build /Users/ryun/llama.cpp/build --config Release -j$(sysctl -n hw.ncpu)
```

Apple SiliconではMetalサポートが自動有効になるため、`-DGGML_CUDA=OFF` のままでOK。

### 2. モデルのダウンロード

Unslothの動的量子化版を使います。**Ollamaが持っているGGUFは独自メタデータで、llama.cppで読めない**点に注意。

```
# 64GB Macなら Q4_K_XL (22GB) が最適
python3 -c "
from huggingface_hub import snapshot_download
snapshot_download(
    'unsloth/Qwen3.5-35B-A3B-GGUF',
    local_dir='/Users/ryun/models/Qwen3.5-35B-A3B-GGUF',
    allow_patterns=['*UD-Q4_K_XL*']
)
"
```

| 量子化 | サイズ | 64GB Macで動くか |
| --- | --- | --- |
| Q4\_K\_XL | 22GB | ✅ 余裕 |
| Q6\_K | 29GB | ✅ 快適 |
| Q8\_0 | 37GB | △ ギリギリ |

### 3. llama-serverの起動パラメータ

ここで最初のハマりポイント。**`-np 1` が必須**です。

```
/Users/ryun/llama.cpp/build/bin/llama-server \
    --model /Users/ryun/models/Qwen3.5-35B-A3B-GGUF/Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf \
    --alias "unsloth/Qwen3.5-35B-A3B" \
    --host 0.0.0.0 --port 8001 \
    -np 1 \
    --temp 0.6 --top-p 0.95 --top-k 20 \
    --cache-type-k q4_0 --cache-type-v q4_0 \
    --flash-attn on --fit on \
    --ctx-size 131072 \
    --reasoning off
```

**重要な指定**:

* `-np 1` — 並列スロット数を1に。**デフォルトの4だとスロット切り替えで0.7 tok/sまで遅くなる**（109 tok/s → 0.7 tok/sという激遅化を確認）
* `--ctx-size 131072` — Claude Codeのシステムプロンプトは40,000+トークンある。65,536でも日本語回答だとオーバーフローするので131,072推奨
* `--cache-type-k q4_0 --cache-type-v q4_0` — KVキャッシュを4bit量子化してメモリ節約
* `--flash-attn on` — プロンプト評価の高速化
* `--reasoning off` — Thinkingモード無効化（これでシステムプロンプト内の`/no_think`と等価）

### 4. Claude Code設定の罠（最重要）

ここが一番ハマりました。**Claude Codeには4つの既知バグ/仕様があり、すべて対処が必要**です。

#### ① 全モデルティアを上書きする必要がある

Claude Codeは内部でHaiku/Sonnet/Opus/Subagentの4つのモデルを使い分けます。指定したモデル以外はAnthropic APIに行こうとして404になります。

```
export ANTHROPIC_DEFAULT_HAIKU_MODEL="unsloth/Qwen3.5-35B-A3B"
export ANTHROPIC_DEFAULT_SONNET_MODEL="unsloth/Qwen3.5-35B-A3B"
export ANTHROPIC_DEFAULT_OPUS_MODEL="unsloth/Qwen3.5-35B-A3B"
export CLAUDE_CODE_SUBAGENT_MODEL="unsloth/Qwen3.5-35B-A3B"
```

#### ② 実験的ベータヘッダーで400エラー

Claude Code v2.1.100+ が送るbetaヘッダーをllama.cppが拒否します ([#46105](https://github.com/anthropics/claude-code/issues/46105))。

```
export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1
```

#### ③ 対話モードがANTHROPIC\_BASE\_URLを無視する ([#36998](https://github.com/anthropics/claude-code/issues/36998))

**これが一番ハマった。** `-p`（非対話モード）では動くのに対話モード(TUI)では動かないという謎の挙動。

対話モード起動時にClaude Codeは以下の通信を試みます：

* Autoupdater check
* Sentry (error tracking)
* Statsig (feature flags)
* Org/auth/telemetry validation

これらが`ANTHROPIC_BASE_URL`を無視して `api.anthropic.com` に直接接続して失敗する。修正PRはなく、以下の環境変数で回避：

```
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
export CLAUDE_CODE_SKIP_FAST_MODE_NETWORK_ERRORS=1
```

#### ④ APIキー確認ダイアログで止まる

起動時に「Detected a custom API key in your environment」というダイアログが出てユーザー入力を待ちます。`~/.claude.json` に**APIキーの最後20文字を事前承認リスト**に入れることでスキップできます。

```
python3 -c "
import json
api_key = 'sk-local-no-key-required-for-llamacpp'
last20 = api_key[-20:]
with open('/Users/ryun/.claude.json') as f:
    data = json.load(f)
data['customApiKeyResponses'] = {'approved': [last20], 'rejected': []}
data['primaryApiKey'] = api_key
data['hasCompletedOnboarding'] = True
with open('/Users/ryun/.claude.json', 'w') as f:
    json.dump(data, f, indent=2)
"
```

**注意**: APIキーは20文字以上必要です。`sk-no-key-required`（18文字）だとダメ。

#### ⑤ OAuth認証トークンとの競合 → `--bare` で解決

普段Claude Codeを使っているとキーチェーンにOAuthトークンが残っていて、`ANTHROPIC_API_KEY`と競合して`Auth conflict`エラーが出ます。

`--bare`フラグは「フック、LSP、プラグイン同期、キーチェーン読み取り、CLAUDE.md自動検出」をすべてスキップするモードです。

```
claude --model unsloth/Qwen3.5-35B-A3B --bare
```

### 5. settings.jsonの追加設定

環境変数だけでは効かない設定もあり、`~/.claude/settings.json` にも書きます。特に `CLAUDE_CODE_ATTRIBUTION_HEADER=0` は**KVキャッシュ無効化による90%の速度低下を防ぐ重要な設定**で、環境変数ではなくこのファイルに書く必要があります。

```
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "0",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    "CLAUDE_CODE_ATTRIBUTION_HEADER": "0",
    "CLAUDE_CODE_SKIP_FAST_MODE_NETWORK_ERRORS": "1",
    "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": "1",
    "DISABLE_TELEMETRY": "1"
  }
}
```

### 6. 最終的な.zshrc関数

すべてを統合した起動用関数：

```
function claude-local {
  local MODEL="unsloth/Qwen3.5-35B-A3B"

  # llama-serverが起動していなければ起動
  if ! curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "Starting llama-server..."
    /Users/ryun/llama.cpp/build/bin/llama-server \
      --model /Users/ryun/models/Qwen3.5-35B-A3B-GGUF/Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf \
      --alias "$MODEL" \
      --temp 0.6 --top-p 0.95 --top-k 20 \
      --host 0.0.0.0 --port 8001 -np 1 \
      --cache-type-k q4_0 --cache-type-v q4_0 \
      --flash-attn on --fit on \
      --ctx-size 131072 \
      --reasoning off \
      > /tmp/llama-server.log 2>&1 &
    while ! curl -s http://localhost:8001/health > /dev/null 2>&1; do sleep 1; done
    echo "Ready!"
  fi

  unset ANTHROPIC_AUTH_TOKEN
  export ANTHROPIC_BASE_URL=http://localhost:8001
  export ANTHROPIC_API_KEY="sk-local-no-key-required-for-llamacpp"
  export ANTHROPIC_DEFAULT_HAIKU_MODEL="$MODEL"
  export ANTHROPIC_DEFAULT_SONNET_MODEL="$MODEL"
  export ANTHROPIC_DEFAULT_OPUS_MODEL="$MODEL"
  export CLAUDE_CODE_SUBAGENT_MODEL="$MODEL"
  export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1
  export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
  export CLAUDE_CODE_SKIP_FAST_MODE_NETWORK_ERRORS=1
  export DISABLE_TELEMETRY=1

  claude --model "$MODEL" --bare "$@"

  unset ANTHROPIC_BASE_URL ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN \
    ANTHROPIC_DEFAULT_HAIKU_MODEL ANTHROPIC_DEFAULT_SONNET_MODEL ANTHROPIC_DEFAULT_OPUS_MODEL \
    CLAUDE_CODE_SUBAGENT_MODEL CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS \
    CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC DISABLE_TELEMETRY
}
```

## 使い方

```
# 普段
claude

# Claude Codeが落ちた時
claude-local
```

## 最後のハマりポイント：古いセッションの環境変数

「全部設定したのに動かない！」となった時は、**新しいターミナルウィンドウで試してください**。過去にOllamaなどを使った痕跡で `ANTHROPIC_BASE_URL` などがシェルのセッションに残っていて、新しい `.zshrc` 設定を上書きする場合があります。

```
# 新しいターミナルウィンドウで確認
echo "AUTH_TOKEN=$ANTHROPIC_AUTH_TOKEN"
echo "BASE_URL=$ANTHROPIC_BASE_URL"
# 空ならOK
```

## まとめ：ハマりポイント一覧

1. ❌ Ollamaは対話エージェント用途だと遅い → llama.cpp直接実行
2. ❌ ThinkingモードON → `--reasoning off`
3. ❌ `-np 4`（デフォルト）だと激遅 → `-np 1`
4. ❌ コンテキスト32K/64Kだとオーバーフロー → `131072`
5. ❌ 指定モデルしか上書きされない → 全4ティア上書き
6. ❌ betaヘッダーで400エラー → `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1`
7. ❌ 対話モードがBASE\_URL無視 → `CLAUDE_CODE_SKIP_FAST_MODE_NETWORK_ERRORS=1`
8. ❌ APIキー承認ダイアログで停止 → `.claude.json`の`customApiKeyResponses`に最後20文字登録
9. ❌ OAuthキーチェーン競合 → `--bare`フラグ
10. ❌ attribution headerでKVキャッシュ無効化 → `settings.json`で`CLAUDE_CODE_ATTRIBUTION_HEADER=0`
11. ❌ Ollama GGUFは llama.cpp で読めない → UnslothのGGUFをダウンロード
12. ❌ 古いシェルセッションの環境変数が残る → 新しいターミナルウィンドウ

## トレードオフ

`--bare` モードなので以下は使えません：

* MCPプラグイン（freee、pencil等）
* カスタムフック
* CLAUDE.mdの自動読み込み
* メモリ機能

純粋なコーディング支援フォールバックとしては十分ですが、完全な代替にはなりません。**Claudeが落ちた時のつなぎ**として割り切って使うのが現実的です。

## 参考

## おわりに

「ローカルLLMでClaude Code」は検索すると簡単そうに書いてありますが、**実際には罠だらけ**でした。特に対話モードを動かすには`--bare`フラグと`customApiKeyResponses`の事前承認が必須で、これを書いてる記事は日本語圏ではほぼ見つかりませんでした。

誰かの時間節約になれば幸いです。
