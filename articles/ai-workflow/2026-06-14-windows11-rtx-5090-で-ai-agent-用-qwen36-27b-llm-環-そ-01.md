---
id: "2026-06-14-windows11-rtx-5090-で-ai-agent-用-qwen36-27b-llm-環-そ-01"
title: "Windows11 RTX 5090 で AI Agent 用 Qwen3.6-27B LLM 環 その2: チューニング"
url: "https://zenn.dev/supertaro/articles/618ea37a7819c6"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "AI-agent", "LLM", "OpenAI", "Python"]
date_published: "2026-06-14"
date_collected: "2026-06-15"
summary_by: "auto-rss"
query: ""
---

以前、RTX 5090 環境で `Qwen3.6-27B-MTP-GGUF` を動かす構成を作りました。

当時は、Windows 11 + WSL Ubuntu 24.04 + Docker + llama.cpp server CUDA で、`Qwen3.6-27B-MTP-GGUF` を OpenAI-compatible API として起動し、Open WebUI から使えるようにするところまでを確認しました。

前編はこちらです。  
[Windows11 RTX 5090 で AI Agent 用 Qwen3.6-27B LLM 環境構築](https://zenn.dev/supertaro/articles/14678514727616)

今回の主な変更点は以下です。

* LiteLLM Proxy 追加
* llama.cpp server を直接外部公開せず、LiteLLM 経由に変更
* Client から見える model alias を3つ用意
* 通常 Agent 用は thinking off を既定値に設定
* 設計判断・原因分析用に thinking on の alias も用意
* context length を 192K tokens まで利用可能に設定
* Needle-in-a-Haystack 形式で 190K 付近まで動作確認

最終的な接続構成は以下です。

```
OpenCode / curl / external OpenAI-compatible client
        |
        | http://ip-or-hostname:30000/v1
        v
LiteLLM Proxy
        |
        | http://llama-qwen36-27b-mtp-gguf:29999/v1
        v
llama.cpp server
        |
        v
Qwen3.6-27B-MTP-GGUF
```

Open WebUI も llama.cpp に直接つながず、LiteLLM 経由にしました。

```
Open WebUI
        |
        | http://litellm-qwen-gateway:4000/v1
        v
LiteLLM Proxy
```

## 環境

環境は以下です。

```
GPU: RTX 5090 32GB
OS: Windows 11 + WSL Ubuntu 24.04
Runtime: Docker
Backend: llama.cpp server-cuda
Gateway: LiteLLM Proxy
UI: Open WebUI
Model: unsloth/Qwen3.6-27B-MTP-GGUF
Quant: UD-Q4_K_XL
Context: 196608 tokens
KV cache: q8_0 / q8_0
MTP: draft-mtp, draft n=2
```

作業ディレクトリは以下にしました。

```
# 前回構成を残したまま、今回の Agent 用構成を分けて作成します。
mkdir -p ~/llm/qwen36-27b-mtp-gguf

# llama.cpp の GGUF cache を保存するディレクトリです。
# 初回起動で取得した model file を再利用するために bind mount します。
mkdir -p ~/llm/qwen36-27b-mtp-gguf/llama-cache

# docker logs 以外に、必要な補助ログを置けるようにするディレクトリです。
mkdir -p ~/llm/qwen36-27b-mtp-gguf/logs

# 今回の docker-compose.yml / .env / litellm_config.yaml を置く場所へ移動します。
cd ~/llm/qwen36-27b-mtp-gguf
```

## model alias の方針

LiteLLM 側では model alias を3つ定義しました。

```
qwen3.6-27b-mtp-gguf
  passthrough 用です。
  enable_thinking は client 側で制御します。

qwen3.6-27b-mtp-gguf-fast
  通常の AI Agent 作業用です。
  enable_thinking=false を既定値にします。

qwen3.6-27b-mtp-gguf-think
  設計判断、原因分析、短〜中 context のレビュー用です。
  enable_thinking=true を既定値にします。
```

実際の backend model は3つとも同じです。

違いは LiteLLM の `extra_body` で、`chat_template_kwargs.enable_thinking` を既定値として付けるかどうかだけです。

通常作業では、以下を使う想定です。

```
qwen3.6-27b-mtp-gguf-fast
```

難しい設計判断や原因分析では、以下を使う想定です。

```
qwen3.6-27b-mtp-gguf-think
```

この分け方にした理由は、Agent 作業では thinking を常時有効にするより、通常は速く安定して応答してほしい場面が多かったためです。

一方で、設計判断や複雑な原因分析では、thinking on の方が向いている場合もあります。

そのため、client 側で都度 request body を変えるのではなく、model 名で切り替える運用にしました。

## `.env`

今回の `.env` は、llama.cpp、LiteLLM、Open WebUI の設定をまとめています。

```
# ==============================================================================
# Hugging Face
# ==============================================================================

# Hugging Face access token です。
#
# unsloth/Qwen3.6-27B-MTP-GGUF は public model なので、
# 通常は空でも動作します。
# ただし、大きな model を取得するため、
# rate limit や download speed の面で token を設定した方が安定する場合があります。
HF_TOKEN=

# ==============================================================================
# LiteLLM public gateway settings
# ==============================================================================

# 外部クライアントから接続する LiteLLM Proxy の公開 port です。
#
# OpenCode、curl、その他 OpenAI-compatible client は、
# http://localhost:30000/v1 を base URL として使います。
# llama.cpp server 本体は外部公開せず、LiteLLM だけを公開します。
LITELLM_PORT=30000

# LiteLLM の master key です。
#
# 管理 API や OpenAI-compatible client 認証に使います。
# 必ず自分で生成した値に置き換えます。
# 生成例:
# openssl rand -hex 32
#
# OpenAI-compatible client で扱いやすいように sk- prefix にします。
LITELLM_MASTER_KEY=sk-replace-with-your-generated-master-key

# LiteLLM の key 管理や内部暗号化用途で使う salt です。
#
# master key とは別のランダム値にします。
# 生成例:
# openssl rand -hex 32
LITELLM_SALT_KEY=replace-with-your-generated-salt-key

# ==============================================================================
# llama.cpp server internal settings
# ==============================================================================

# llama.cpp server 本体の内部 port です。
#
# docker-compose.yml では ports ではなく expose を使います。
# そのため、ホストや LAN から http://localhost:29999 へ直接接続する構成にはしません。
#
# LiteLLM container から Docker network 内部でのみ接続します。
LLAMA_PORT=29999

# LiteLLM から見た llama.cpp server の OpenAI-compatible API base URL です。
#
# Docker Compose の service 名を host 名として使います。
LLAMA_BASE_URL=http://llama-qwen36-27b-mtp-gguf:29999/v1

# LiteLLM が upstream OpenAI-compatible endpoint に渡す dummy key です。
#
# llama.cpp server 側では API key 認証を使いません。
# ただし LiteLLM の openai provider では api_key が必要なため、
# 空ではなく dummy 値を渡します。
LLAMA_DUMMY_API_KEY=llama-local-dummy-key

# ==============================================================================
# Model identity
# ==============================================================================

# llama.cpp server が起動時に取得する Hugging Face GGUF model repository です。
MODEL_REPO=unsloth/Qwen3.6-27B-MTP-GGUF

# GGUF quantization name です。
#
# RTX 5090 32GB + 192K context + OpenCode Agent 用途では、
# UD-Q4_K_XL を本命にしました。
# Q5_K_M も品質検証用の候補にはなりますが、
# 192K 常用では VRAM 余白が厳しくなりやすいため、
# 今回は UD-Q4_K_XL を使います。
MODEL_QUANT=UD-Q4_K_XL

# llama.cpp server 上で提供する実モデル名です。
#
# LiteLLM 側では、この backend model に対して3つの alias を定義します。
MODEL_SERVED_NAME=qwen3.6-27b-mtp-gguf

# LiteLLM の model_info metadata に表示する実 checkpoint 名です。
MODEL_PATH=unsloth/Qwen3.6-27B-MTP-GGUF:UD-Q4_K_XL

# ==============================================================================
# LiteLLM model alias names
# ==============================================================================

# enable_thinking を client 側に任せる model alias です。
LITELLM_MODEL_PASSTHROUGH=qwen3.6-27b-mtp-gguf

# enable_thinking=false を既定値にする model alias です。
#
# OpenCode Agent の通常作業、tool calling、長 context、速度優先、
# patch 生成、ファイル編集ではこちらを使います。
LITELLM_MODEL_FAST=qwen3.6-27b-mtp-gguf-fast

# enable_thinking=true を既定値にする model alias です。
#
# 設計判断、原因分析、難しいレビューなど、
# 短〜中 context で高品質な推論が必要な場合に使います。
LITELLM_MODEL_THINK=qwen3.6-27b-mtp-gguf-think

# ==============================================================================
# llama.cpp long context / GPU settings
# ==============================================================================

# llama.cpp server 側の最大 context size です。
#
# 196608 は 192K tokens です。
# Qwen3.6 の native context 範囲内ですが、
# RTX 5090 32GB では 192K を実用上限寄りの本命値にします。
LLAMA_CTX_SIZE=196608

# GPU offload layer 数です。
#
# 99 のように大きめにして、可能な限り GPU に載せます。
LLAMA_N_GPU_LAYERS=99

# parallel sequence 数です。
#
# MTP speculative decoding は -np > 1 と相性が悪い、または未対応のケースがあります。
# OpenCode Agent 専用・単一ユーザー運用では 1 固定にします。
LLAMA_PARALLEL=1

# prompt processing batch size です。
#
# 大きいほど prefill が速くなる場合がありますが、VRAM 消費も増えます。
# 192K context では 2048 より少し保守的に 1536 から始めます。
# VRAM に余裕がある場合:
# LLAMA_BATCH_SIZE=2048
# OOM が出る場合:
# LLAMA_BATCH_SIZE=1024
LLAMA_BATCH_SIZE=1536

# physical micro-batch size です。
#
# CUDA 実行時の小分け batch size です。
# 192K context では 384 から始めます。
# VRAM に余裕がある場合:
# LLAMA_UBATCH_SIZE=512
# OOM が出る場合:
# LLAMA_UBATCH_SIZE=256
LLAMA_UBATCH_SIZE=384

# Flash Attention を有効化します。
#
# 長 context では特に重要です。
LLAMA_FLASH_ATTN=on

# KV cache の K 側 quantization です。
#
# OpenCode Agent 用途では長文参照と品質を優先し、q8_0 を本命にします。
LLAMA_CACHE_TYPE_K=q8_0

# KV cache の V 側 quantization です。
#
# OpenCode Agent 用途では q8_0 を本命にします。
# 192K で OOM が出る場合の最初の妥協案:
# LLAMA_CACHE_TYPE_K=q8_0
# LLAMA_CACHE_TYPE_V=q4_0
LLAMA_CACHE_TYPE_V=q8_0

# ==============================================================================
# Qwen3.6 MTP speculative decoding
# ==============================================================================

# speculative decoding type です。
#
# 現在の ghcr.io/ggml-org/llama.cpp:server-cuda では、
# --spec-type mtp ではなく draft-mtp を使います。
LLAMA_SPEC_TYPE=draft-mtp

# MTP draft token count です。
#
# Agent 用では安定性を重視し、2 を基準にします。
# 速度比較だけなら 3 も試す価値があります。
LLAMA_MTP_DRAFT_N=2

# draft token を採用する最小確率です。
#
# 0.0 は緩めの設定です。
LLAMA_DRAFT_P_MIN=0.0

# ==============================================================================
# llama.cpp reasoning / thinking settings
# ==============================================================================

# reasoning output format です。
#
# deepseek:
# thought / reasoning 部分を message.reasoning_content に分離します。
# OpenCode / LiteLLM gateway では、分離できる deepseek を初期値にします。
LLAMA_REASONING_FORMAT=deepseek

# reasoning budget です。
#
# -1:
# thinking を許可します。
# 0:
# server 全体で thinking を無効化します。
#
# 今回は fast / think alias を LiteLLM で分けるため -1 にします。
LLAMA_REASONING_BUDGET=-1

# server read/write timeout seconds です。
#
# 192K context、長い tool result、長い patch 出力を考慮して長めにします。
LLAMA_TIMEOUT=600

# performance timings です。
#
# llama.cpp server の応答や log で性能確認しやすくします。
LLAMA_PERF=1

# Prometheus metrics endpoint を有効化します。
LLAMA_ENABLE_METRICS=1

# slot monitoring endpoint を有効化します。
LLAMA_ENABLE_SLOTS=1

# ==============================================================================
# llama.cpp generation parameters for OpenCode AI Agent
# ==============================================================================

# Agent 用の生成温度です。
#
# チャットの自然さより、コード編集、tool calling、長 context 安定性を優先します。
LLAMA_TEMPERATURE=0.6

# nucleus sampling の上限です。
LLAMA_TOP_P=0.95

# top-k sampling です。
LLAMA_TOP_K=20

# min-p sampling です。
LLAMA_MIN_P=0.0

# repeat penalty です。
#
# コード、JSON、diff、変数名、SQL では繰り返しが正しいことが多いため、
# Agent 用では 1.0 を基準にします。
LLAMA_REPEAT_PENALTY=1.0

# presence penalty です。
LLAMA_PRESENCE_PENALTY=0.0

# frequency penalty です。
LLAMA_FREQUENCY_PENALTY=0.0

# ==============================================================================
# LiteLLM model_info token limits
# ==============================================================================

# LiteLLM の passthrough / fast model_info に表示する最大入力 token 数です。
LITELLM_MAX_INPUT_TOKENS=196608

# LiteLLM の think model_info に表示する最大入力 token 数です。
#
# think alias は reasoning を有効にするため、
# fast alias と同じ 192K までは広げず、128K までにします。
LITELLM_THINK_MAX_INPUT_TOKENS=131072

# LiteLLM の model_info に表示する最大出力 token 数です。
#
# 長い設計メモ、修正方針、レビュー結果、patch 説明などを出す場合、
# 不足する可能性があるため 64K にします。
# 実際に常に 64K 出すという意味ではなく、
# client 側から必要な場合に大きめの max_tokens を指定できる余地を持たせます。
LITELLM_MAX_OUTPUT_TOKENS=65536

# ==============================================================================
# LiteLLM local model cost metadata
# ==============================================================================

# ローカルモデルなので、LiteLLM の model_info 上の単価は 0 にします。
LITELLM_INPUT_COST_PER_TOKEN=0
LITELLM_OUTPUT_COST_PER_TOKEN=0

# ==============================================================================
# Open WebUI settings
# ==============================================================================

# Open WebUI の公開 port です。
#
# Windows 側ブラウザから http://localhost:3000 でアクセスできます。
WEBUI_PORT=3000

# Open WebUI から見た OpenAI-compatible API base URL です。
#
# Open WebUI は llama.cpp に直接つながず、LiteLLM を経由します。
WEBUI_OPENAI_API_BASE_URL=http://litellm-qwen-gateway:4000/v1

# Open WebUI が LiteLLM に渡す API key です。
#
# まずは LITELLM_MASTER_KEY と同じ値を設定します。
# 運用時は LiteLLM の virtual key を発行し、その key に置き換える方針が安全です。
WEBUI_OPENAI_API_KEY=sk-replace-with-your-generated-master-key

# Open WebUI では Ollama API を使わず、OpenAI-compatible API のみ使います。
WEBUI_ENABLE_OLLAMA_API=false

# Open WebUI 側の既定モデルです。
#
# 通常 Agent 用の thinking off alias を初期選択にします。
WEBUI_DEFAULT_MODEL=qwen3.6-27b-mtp-gguf-fast

# ==============================================================================
# Open WebUI request-side default generation parameters
# ==============================================================================

# Open WebUI から送る既定生成パラメータです。
#
# Open WebUI は OpenCode のような Agent 実行環境ではなく、
# ブラウザから Chat AI 的に使う補助 UI として扱います。
# そのため、OpenCode Agent 用の厳しめ・安定寄り設定に完全には合わせず、
# 通常会話、文章作成、軽い相談で使いやすい値にします。
WEBUI_GEN_TEMP=0.7

# nucleus sampling の上限です。
# Chat AI 的な自然さを少し優先し、0.95 のままにします。
WEBUI_GEN_TOP_P=0.95

# top-k sampling です。
# llama.cpp / Agent 側と同じく 20 を基準にします。
WEBUI_GEN_TOP_K=20

# min-p sampling です。
# まずは無効相当の 0.0 にします。
WEBUI_GEN_MIN_P=0.0

# Open WebUI の既定最大出力 token 数です。
# 通常のチャットでは大きすぎる値を毎回使う必要はないため、
# 既定値は 8192 のままにします。
#
# 長い出力が必要な場合は、client 側または model 設定側で個別に増やします。
WEBUI_GEN_MAX_TOKENS=8192

# presence penalty です。
# 会話用途でも、まずは癖を増やさないため 0.0 にします。
WEBUI_GEN_PRESENCE_PENALTY=0.0

# frequency penalty です。
# コード、設定、表現の繰り返しが必要な場面もあるため 0.0 にします。
WEBUI_GEN_FREQUENCY_PENALTY=0.0

# repeat penalty です。
# Chat AI 用途でも、ローカルモデルで過度な繰り返しが気になる場合は
# 1.05 〜 1.1 程度を試す余地があります。
#
# ただし、コードや設定ファイルを扱うこともあるため、まずは 1.0 にします。
WEBUI_GEN_REPEAT_PENALTY=1.0

# seed です。
# -1 は固定 seed なしです。
WEBUI_GEN_SEED=-1

# ==============================================================================
# Runtime behavior
# ==============================================================================

# Python stdout / stderr を buffer しない設定です。
#
# docker logs -f で LiteLLM のログをリアルタイム確認しやすくします。
RUNTIME_PYTHONUNBUFFERED=1

# tokenizer 並列処理 warning を抑制します。
RUNTIME_TOKENIZERS_PARALLELISM=false

# llama.cpp の Hugging Face / GGUF cache 先です。
#
# docker-compose.yml で ./llama-cache に bind mount して永続化します。
LLAMA_CACHE_DIR=/llama-cache
```

## docker-compose.yml

`docker-compose.yml` は3 service 構成にしました。

```
llama-qwen36-27b-mtp-gguf
  llama.cpp server です。
  Docker network 内にだけ公開します。

litellm-qwen-gateway
  LiteLLM Proxy です。
  外部 client にはこの service だけを公開します。

open-webui
  ブラウザ確認用です。
  LiteLLM 経由で model alias を使います。
```

実際の内容です。

```
services:
  llama-qwen36-27b-mtp-gguf:
    # llama.cpp の CUDA 対応 server image です。
    #
    # ホスト側に llama.cpp や Python 環境を作らず、
    # llama.cpp server 実行環境を Docker container 内に閉じ込めます。
    image: ghcr.io/ggml-org/llama.cpp:server-cuda

    # コンテナ名です。
    container_name: llama-qwen36-27b-mtp-gguf

    # Docker daemon やホスト再起動後に自動復旧させます。
    restart: unless-stopped

    # ログ肥大化によるディスク枯渇を防ぎます。
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "3"

    # NVIDIA GPU をコンテナに渡します。
    gpus: all

    # llama.cpp / CUDA 実行時の共有メモリ不足を避けるため host IPC を使います。
    ipc: host

    # 共有メモリを明示的に大きめに確保します。
    shm_size: "8g"

    # llama.cpp server は Docker network 内だけで公開します。
    #
    # expose はコンテナ間通信用です。
    # ホスト側や LAN には 29999 を公開しません。
    expose:
      - "${LLAMA_PORT:-29999}"

    # .env から llama.cpp と LiteLLM 共通の環境変数を読み込みます。
    env_file:
      - .env

    environment:
      # Hugging Face token です。
      HF_TOKEN: ${HF_TOKEN:-}

      # llama.cpp の cache 基準ディレクトリです。
      LLAMA_CACHE: ${LLAMA_CACHE_DIR:-/llama-cache}

      # 使用する GPU を固定します。
      CUDA_VISIBLE_DEVICES: "0"

    volumes:
      # llama.cpp / Hugging Face GGUF cache をホストへ永続化します。
      - ./llama-cache:/llama-cache

      # ログや補助ファイルを保存するためのディレクトリです。
      - ./logs:/logs

    extra_hosts:
      # Docker container から host.docker.internal を解決するための設定です。
      - "host.docker.internal:host-gateway"

    command:
      # Hugging Face repository から GGUF を取得して起動します。
      - "-hf"
      - "${MODEL_REPO:-unsloth/Qwen3.6-27B-MTP-GGUF}:${MODEL_QUANT:-UD-Q4_K_XL}"

      # OpenAI-compatible API 上で返す model alias です。
      - "--alias"
      - "${MODEL_SERVED_NAME:-qwen3.6-27b-mtp-gguf}"

      # コンテナ内で listen するアドレスです。
      - "--host"
      - "0.0.0.0"

      # llama.cpp server の内部 listen port です。
      - "--port"
      - "${LLAMA_PORT:-29999}"

      # GPU offload layer 数です。
      - "-ngl"
      - "${LLAMA_N_GPU_LAYERS:-99}"

      # 最大 context size です。
      - "-c"
      - "${LLAMA_CTX_SIZE:-196608}"

      # prompt processing batch size です。
      - "-b"
      - "${LLAMA_BATCH_SIZE:-1536}"

      # physical micro-batch size です。
      - "-ub"
      - "${LLAMA_UBATCH_SIZE:-384}"

      # Flash Attention を有効化します。
      - "-fa"
      - "${LLAMA_FLASH_ATTN:-on}"

      # parallel sequence 数です。
      - "-np"
      - "${LLAMA_PARALLEL:-1}"

      # KV cache の K 側 quantization です。
      - "--cache-type-k"
      - "${LLAMA_CACHE_TYPE_K:-q8_0}"

      # KV cache の V 側 quantization です。
      - "--cache-type-v"
      - "${LLAMA_CACHE_TYPE_V:-q8_0}"

      # Qwen3.6 MTP speculative decoding を有効化します。
      #
      # 現在の server-cuda image では draft-mtp を指定します。
      - "--spec-type"
      - "${LLAMA_SPEC_TYPE:-draft-mtp}"

      # MTP draft token count です。
      #
      # draft-mtp では --spec-draft-n-max を使います。
      - "--spec-draft-n-max"
      - "${LLAMA_MTP_DRAFT_N:-2}"

      # draft token を採用する最小確率です。
      - "--draft-p-min"
      - "${LLAMA_DRAFT_P_MIN:-0.0}"

      # server-side default temperature です。
      - "--temp"
      - "${LLAMA_TEMPERATURE:-0.6}"

      # server-side default top-p です。
      - "--top-p"
      - "${LLAMA_TOP_P:-0.95}"

      # server-side default top-k です。
      - "--top-k"
      - "${LLAMA_TOP_K:-20}"

      # server-side default min-p です。
      - "--min-p"
      - "${LLAMA_MIN_P:-0.0}"

      # repeat penalty です。
      - "--repeat-penalty"
      - "${LLAMA_REPEAT_PENALTY:-1.0}"

      # Jinja chat template を有効化します。
      #
      # Qwen3.6 の chat template、tool calling、chat_template_kwargs を扱うために使います。
      - "--jinja"

      # reasoning / thought extraction format です。
      - "--reasoning-format"
      - "${LLAMA_REASONING_FORMAT:-deepseek}"

      # reasoning budget です。
      #
      # -1 は unrestricted、0 は disable です。
      - "--reasoning-budget"
      - "${LLAMA_REASONING_BUDGET:--1}"

      # server の read/write timeout です。
      - "--timeout"
      - "${LLAMA_TIMEOUT:-600}"

      # llama.cpp server 内蔵 Web UI を無効化します。
      - "--no-webui"

      # Prometheus metrics endpoint を有効化します。
      - "--metrics"

      # slot monitoring endpoint を有効化します。
      - "--slots"

      # performance timings を出します。
      - "--perf"

    healthcheck:
      # llama.cpp server の health endpoint を確認します。
      #
      # もし image に curl が含まれていない場合は、
      # この healthcheck を削除し、depends_on を service_started に変更します。
      test: ["CMD-SHELL", "curl -fsS http://localhost:${LLAMA_PORT:-29999}/health >/dev/null || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 20
      start_period: 300s

  litellm-qwen-gateway:
    # LiteLLM Proxy の公式コンテナイメージです。
    #
    # OpenAI-compatible gateway、API key 管理、model alias、
    # extra_body による thinking preset などを担当します。
    image: ghcr.io/berriai/litellm:main-latest

    # コンテナ名です。
    container_name: litellm-qwen-gateway

    # Docker daemon やホスト再起動後に自動復旧させます。
    restart: unless-stopped

    # ログ肥大化を防ぎます。
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "3"

    # LiteLLM だけを外部公開します。
    #
    # クライアントは http://localhost:30000/v1 に接続します。
    ports:
      - "0.0.0.0:${LITELLM_PORT:-30000}:4000"

    # .env から master key、model alias、llama.cpp 接続先などを読み込みます。
    env_file:
      - .env

    environment:
      # LiteLLM の master key です。
      LITELLM_MASTER_KEY: ${LITELLM_MASTER_KEY}

      # LiteLLM の key 管理・暗号化用途で使う salt です。
      LITELLM_SALT_KEY: ${LITELLM_SALT_KEY}

      # LiteLLM から llama.cpp server に接続する URL です。
      LLAMA_BASE_URL: ${LLAMA_BASE_URL}

      # llama.cpp upstream に渡す dummy API key です。
      LLAMA_DUMMY_API_KEY: ${LLAMA_DUMMY_API_KEY}

      # 実モデル情報です。
      MODEL_REPO: ${MODEL_REPO}
      MODEL_QUANT: ${MODEL_QUANT}
      MODEL_PATH: ${MODEL_PATH}
      MODEL_SERVED_NAME: ${MODEL_SERVED_NAME}

      # LiteLLM から client に見せる model alias です。
      LITELLM_MODEL_PASSTHROUGH: ${LITELLM_MODEL_PASSTHROUGH}
      LITELLM_MODEL_FAST: ${LITELLM_MODEL_FAST}
      LITELLM_MODEL_THINK: ${LITELLM_MODEL_THINK}

      # llama.cpp upstream に渡す Agent 用の生成パラメータです。
      LLAMA_TEMPERATURE: ${LLAMA_TEMPERATURE}
      LLAMA_TOP_P: ${LLAMA_TOP_P}
      LLAMA_PRESENCE_PENALTY: ${LLAMA_PRESENCE_PENALTY}
      LLAMA_FREQUENCY_PENALTY: ${LLAMA_FREQUENCY_PENALTY}

      # LiteLLM の /model/info に表示する token 上限や cost metadata です。
      LITELLM_MAX_INPUT_TOKENS: ${LITELLM_MAX_INPUT_TOKENS}
      LITELLM_THINK_MAX_INPUT_TOKENS: ${LITELLM_THINK_MAX_INPUT_TOKENS}
      LITELLM_MAX_OUTPUT_TOKENS: ${LITELLM_MAX_OUTPUT_TOKENS}
      LITELLM_INPUT_COST_PER_TOKEN: ${LITELLM_INPUT_COST_PER_TOKEN}
      LITELLM_OUTPUT_COST_PER_TOKEN: ${LITELLM_OUTPUT_COST_PER_TOKEN}

      # Python の標準出力を即時出力します。
      PYTHONUNBUFFERED: ${RUNTIME_PYTHONUNBUFFERED:-1}

      # tokenizer 並列処理 warning を抑制します。
      TOKENIZERS_PARALLELISM: ${RUNTIME_TOKENIZERS_PARALLELISM:-false}

    volumes:
      # LiteLLM の設定ファイルです。
      - ./litellm_config.yaml:/app/config.yaml:ro

    command:
      # LiteLLM Proxy に設定ファイルを渡します。
      - --config
      - /app/config.yaml

      # コンテナ内部の listen port です。
      - --port
      - "4000"

      # コンテナ内の全 network interface で listen します。
      - --host
      - 0.0.0.0

    depends_on:
      # llama.cpp server のモデルロードと health check 完了後に LiteLLM を起動します。
      llama-qwen36-27b-mtp-gguf:
        condition: service_healthy

  open-webui:
    # Open WebUI の公式コンテナイメージです。
    #
    # ブラウザから LiteLLM 経由で Qwen3.6 を利用するために使います。
    image: ghcr.io/open-webui/open-webui:main

    # コンテナ名です。
    container_name: open-webui

    # Docker daemon やホスト再起動後に自動復旧させます。
    restart: unless-stopped

    # Open WebUI は LiteLLM の起動後に開始します。
    depends_on:
      - litellm-qwen-gateway

    # Windows 側ブラウザから http://localhost:3000 でアクセスできます。
    ports:
      - "${WEBUI_PORT:-3000}:8080"

    # .env から Open WebUI と共通設定を読み込みます。
    env_file:
      - .env

    environment:
      # Open WebUI から見た OpenAI-compatible API base URL です。
      #
      # llama.cpp に直接つながず、LiteLLM を経由します。
      OPENAI_API_BASE_URL: ${WEBUI_OPENAI_API_BASE_URL:-http://litellm-qwen-gateway:4000/v1}

      # Open WebUI が LiteLLM に渡す API key です。
      #
      # まずは LITELLM_MASTER_KEY と同じ値を .env に設定します。
      # 運用時は LiteLLM の virtual key に置き換える方針です。
      OPENAI_API_KEY: ${WEBUI_OPENAI_API_KEY}

      # Ollama API は使わず、OpenAI-compatible API のみ使います。
      ENABLE_OLLAMA_API: ${WEBUI_ENABLE_OLLAMA_API:-false}

      # Open WebUI の既定モデルです。
      DEFAULT_MODELS: ${WEBUI_DEFAULT_MODEL:-qwen3.6-27b-mtp-gguf-fast}

      # Open WebUI 側の既定生成パラメータです。
      DEFAULT_MODEL_PARAMS: >
        {
          "temperature": ${WEBUI_GEN_TEMP:-0.6},
          "top_p": ${WEBUI_GEN_TOP_P:-0.95},
          "top_k": ${WEBUI_GEN_TOP_K:-20},
          "min_p": ${WEBUI_GEN_MIN_P:-0.0},
          "max_tokens": ${WEBUI_GEN_MAX_TOKENS:-8192},
          "presence_penalty": ${WEBUI_GEN_PRESENCE_PENALTY:-0.0},
          "frequency_penalty": ${WEBUI_GEN_FREQUENCY_PENALTY:-0.0},
          "repeat_penalty": ${WEBUI_GEN_REPEAT_PENALTY:-1.0},
          "seed": ${WEBUI_GEN_SEED:--1}
        }

    volumes:
      # Open WebUI の DB、設定、ユーザーデータを永続化します。
      - open-webui:/app/backend/data

    extra_hosts:
      # container から host.docker.internal を解決するための設定です。
      - "host.docker.internal:host-gateway"

volumes:
  # Open WebUI の永続化 volume です。
  open-webui:
```

## LiteLLM config

LiteLLM の設定では、1つの llama.cpp backend に対して、3つの model alias を定義しました。

```
# ==============================================================================
# LiteLLM Proxy configuration
# ==============================================================================
#
# この設定では、1つの llama.cpp OpenAI-compatible backend に対して、
# クライアントから見える3つの model alias を定義します。
#
# 1. qwen3.6-27b-mtp-gguf
#    - passthrough
#    - enable_thinking はクライアント側で制御します。
#
# 2. qwen3.6-27b-mtp-gguf-fast
#    - OpenCode Agent の通常作業向けです。
#    - クライアント未指定時に chat_template_kwargs.enable_thinking=false を付与します。
#
# 3. qwen3.6-27b-mtp-gguf-think
#    - 設計判断、原因分析、短〜中 context のレビュー向けです。
#    - クライアント未指定時に chat_template_kwargs.enable_thinking=true を付与します。
#
# 実際の backend model は3つとも同じです。
# 違いは、LiteLLM の extra_body で thinking preset を付けるかどうかです。
#
# 注意:
# extra_body は「未指定時の preset」として扱います。
# クライアントが chat_template_kwargs.enable_thinking を明示した場合は、
# クライアント側指定が優先される可能性があります。
# ==============================================================================

model_list:
  # --------------------------------------------------------------------------
  # 1. Passthrough model
  # --------------------------------------------------------------------------
  - model_name: os.environ/LITELLM_MODEL_PASSTHROUGH
    litellm_params:
      # llama.cpp server の --alias / MODEL_SERVED_NAME と一致させます。
      model: os.environ/MODEL_SERVED_NAME

      # llama.cpp server を OpenAI-compatible endpoint として扱います。
      custom_llm_provider: openai

      # LiteLLM から見た llama.cpp server の API base URL です。
      api_base: os.environ/LLAMA_BASE_URL

      # llama.cpp 側では認証しませんが、LiteLLM の provider が api_key を要求するため渡します。
      api_key: os.environ/LLAMA_DUMMY_API_KEY

      # Agent 用の生成パラメータです。
      temperature: os.environ/LLAMA_TEMPERATURE
      top_p: os.environ/LLAMA_TOP_P
      presence_penalty: os.environ/LLAMA_PRESENCE_PENALTY
      frequency_penalty: os.environ/LLAMA_FREQUENCY_PENALTY

      # 長 context / 長生成に備えて長めにします。
      timeout: 600
      stream_timeout: 600

    model_info:
      # /model/info で見える内部 ID です。
      id: os.environ/LITELLM_MODEL_PASSTHROUGH

      # chat completion 用 model として扱います。
      mode: chat

      # ローカルモデルなので単価は 0 です。
      input_cost_per_token: os.environ/LITELLM_INPUT_COST_PER_TOKEN
      output_cost_per_token: os.environ/LITELLM_OUTPUT_COST_PER_TOKEN

      # 表示上の最大入力 token 数です。
      max_input_tokens: os.environ/LITELLM_MAX_INPUT_TOKENS

      # 表示上の最大出力 token 数です。
      max_output_tokens: os.environ/LITELLM_MAX_OUTPUT_TOKENS

      # 説明です。
      description: Qwen3.6 27B MTP GGUF UD-Q4_K_XL via llama.cpp. enable_thinking はクライアント側で制御します。

      # 運用時に確認しやすい metadata です。
      metadata:
        backend: llama.cpp
        real_model: os.environ/MODEL_PATH
        quant: os.environ/MODEL_QUANT
        context_tokens: os.environ/LITELLM_MAX_INPUT_TOKENS
        thinking_mode: passthrough

  # --------------------------------------------------------------------------
  # 2. Fast preset model
  # --------------------------------------------------------------------------
  - model_name: os.environ/LITELLM_MODEL_FAST
    litellm_params:
      # llama.cpp server の --alias / MODEL_SERVED_NAME と一致させます。
      model: os.environ/MODEL_SERVED_NAME

      # llama.cpp server を OpenAI-compatible endpoint として扱います。
      custom_llm_provider: openai

      # LiteLLM から見た llama.cpp server の API base URL です。
      api_base: os.environ/LLAMA_BASE_URL

      # llama.cpp 側では認証しませんが、LiteLLM の provider が api_key を要求するため渡します。
      api_key: os.environ/LLAMA_DUMMY_API_KEY

      # Agent 用の生成パラメータです。
      temperature: os.environ/LLAMA_TEMPERATURE
      top_p: os.environ/LLAMA_TOP_P
      presence_penalty: os.environ/LLAMA_PRESENCE_PENALTY
      frequency_penalty: os.environ/LLAMA_FREQUENCY_PENALTY

      # fast preset です。
      #
      # クライアントが chat_template_kwargs を送らない場合、
      # llama.cpp server に enable_thinking=false が渡ります。
      extra_body:
        chat_template_kwargs:
          enable_thinking: false

      # 長 context / 長生成に備えて長めにします。
      timeout: 600
      stream_timeout: 600

    model_info:
      # /model/info で見える内部 ID です。
      id: os.environ/LITELLM_MODEL_FAST

      # chat completion 用 model として扱います。
      mode: chat

      # ローカルモデルなので単価は 0 です。
      input_cost_per_token: os.environ/LITELLM_INPUT_COST_PER_TOKEN
      output_cost_per_token: os.environ/LITELLM_OUTPUT_COST_PER_TOKEN

      # fast alias は OpenCode Agent の 192K メイン endpoint です。
      max_input_tokens: os.environ/LITELLM_MAX_INPUT_TOKENS

      # 表示上の最大出力 token 数です。
      max_output_tokens: os.environ/LITELLM_MAX_OUTPUT_TOKENS

      # 説明です。
      description: Qwen3.6 27B MTP GGUF UD-Q4_K_XL via llama.cpp. enable_thinking=false を既定値にします。

      # 運用時に確認しやすい metadata です。
      metadata:
        backend: llama.cpp
        real_model: os.environ/MODEL_PATH
        quant: os.environ/MODEL_QUANT
        context_tokens: os.environ/LITELLM_MAX_INPUT_TOKENS
        thinking_mode: false
        thinking_control: preset_when_unspecified

  # --------------------------------------------------------------------------
  # 3. Think preset model
  # --------------------------------------------------------------------------
  - model_name: os.environ/LITELLM_MODEL_THINK
    litellm_params:
      # llama.cpp server の --alias / MODEL_SERVED_NAME と一致させます。
      model: os.environ/MODEL_SERVED_NAME

      # llama.cpp server を OpenAI-compatible endpoint として扱います。
      custom_llm_provider: openai

      # LiteLLM から見た llama.cpp server の API base URL です。
      api_base: os.environ/LLAMA_BASE_URL

      # llama.cpp 側では認証しませんが、LiteLLM の provider が api_key を要求するため渡します。
      api_key: os.environ/LLAMA_DUMMY_API_KEY

      # Agent 用の生成パラメータです。
      temperature: os.environ/LLAMA_TEMPERATURE
      top_p: os.environ/LLAMA_TOP_P
      presence_penalty: os.environ/LLAMA_PRESENCE_PENALTY
      frequency_penalty: os.environ/LLAMA_FREQUENCY_PENALTY

      # think preset です。
      #
      # クライアントが chat_template_kwargs を送らない場合、
      # llama.cpp server に enable_thinking=true が渡ります。
      extra_body:
        chat_template_kwargs:
          enable_thinking: true

      # 長い reasoning content に備えて長めにします。
      timeout: 600
      stream_timeout: 600

    model_info:
      # /model/info で見える内部 ID です。
      id: os.environ/LITELLM_MODEL_THINK

      # chat completion 用 model として扱います。
      mode: chat

      # ローカルモデルなので単価は 0 です。
      input_cost_per_token: os.environ/LITELLM_INPUT_COST_PER_TOKEN
      output_cost_per_token: os.environ/LITELLM_OUTPUT_COST_PER_TOKEN

      # think alias は短〜中 context の難しい判断向けです。
      max_input_tokens: os.environ/LITELLM_THINK_MAX_INPUT_TOKENS

      # 表示上の最大出力 token 数です。
      max_output_tokens: os.environ/LITELLM_MAX_OUTPUT_TOKENS

      # 説明です。
      description: Qwen3.6 27B MTP GGUF UD-Q4_K_XL via llama.cpp. enable_thinking=true を既定値にします。

      # 運用時に確認しやすい metadata です。
      metadata:
        backend: llama.cpp
        real_model: os.environ/MODEL_PATH
        quant: os.environ/MODEL_QUANT
        context_tokens: os.environ/LITELLM_THINK_MAX_INPUT_TOKENS
        thinking_mode: true
        thinking_control: preset_when_unspecified

# ==============================================================================
# LiteLLM runtime settings
# ==============================================================================

litellm_settings:
  # クライアントから渡された unsupported parameter を落とします。
  #
  # OpenCode や一部クライアントが reasoning_effort などを送る場合、
  # LiteLLM が 400 を返すのを避けるため true にします。
  #
  # 注意:
  # reasoning_effort は落とされるだけで、thinking 制御には使われません。
  # thinking 制御は fast / think alias で行います。
  drop_params: true

  # 詳細ログを抑制します。
  #
  # 調査時だけ true にすると、LiteLLM の挙動を追いやすくなります。
  set_verbose: false

  # 全体の request timeout です。
  request_timeout: 600

  # HTTP クライアントの接続 timeout です。
  async_http_client_connect_timeout: 60.0

  # HTTP クライアントの読み取り timeout です。
  async_http_client_read_timeout: 600.0

# ==============================================================================
# LiteLLM proxy settings
# ==============================================================================

general_settings:
  # LiteLLM の master key です。
  #
  # .env の LITELLM_MASTER_KEY を使います。
  master_key: os.environ/LITELLM_MASTER_KEY
```

## 起動

ファイルを配置したあと、以下で起動します。

```
# 今回の構成ファイルを置いた作業ディレクトリへ移動します。
cd ~/llm/qwen36-27b-mtp-gguf

# cache と logs の保存先を作成します。
# すでに存在していても問題ありません。
mkdir -p logs llama-cache

# 既存 container が残っている場合に停止・削除します。
# 設定変更を確実に反映するために一度 down します。
docker compose down

# llama.cpp server、LiteLLM、Open WebUI をバックグラウンドで起動します。
docker compose up -d
```

初回起動では、GGUF の取得と model load に時間がかかります。

起動状況は以下で確認します。

```
# llama.cpp server のログを確認します。
# model download、load、context size、KV cache、MTP 設定などを見ます。
docker compose logs -f llama-qwen36-27b-mtp-gguf
```

別 terminal で LiteLLM も確認します。

```
# LiteLLM Proxy のログを確認します。
# config 読み込み、model alias、upstream 接続エラーがないかを見ます。
docker compose logs -f litellm-qwen-gateway
```

Open WebUI も確認します。

```
# Open WebUI のログを確認します。
# LiteLLM への接続や model list 取得に失敗していないかを見ます。
docker compose logs -f open-webui
```

## LiteLLM 経由で疎通確認

LiteLLM が起動したら、まず `qwen3.6-27b-mtp-gguf-fast` で確認します。

```
# .env の値を shell に読み込みます。
# API key や model alias を curl で使うためです。
set -a
. ./.env
set +a

# LiteLLM 経由で chat completions を呼びます。
# model には通常 Agent 用の fast alias を指定します。
curl -N http://localhost:30000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
  -d '{
    "model": "qwen3.6-27b-mtp-gguf-fast",
    "messages": [
      {
        "role": "user",
        "content": "Say OK only."
      }
    ],
    "max_tokens": 64,
    "temperature": 0.2,
    "stream": true
  }'
```

`OK` のような応答が返れば、以下の経路は通っています。

```
curl
  -> LiteLLM
    -> llama.cpp server
      -> Qwen3.6-27B-MTP-GGUF
```

think alias も確認します。

```
# think alias の疎通確認です。
# 設計判断や原因分析用に enable_thinking=true preset で通す alias です。
curl -N http://localhost:30000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
  -d '{
    "model": "qwen3.6-27b-mtp-gguf-think",
    "messages": [
      {
        "role": "user",
        "content": "この構成で LiteLLM を挟む利点を短く説明してください。"
      }
    ],
    "max_tokens": 512,
    "temperature": 0.2,
    "stream": true
  }'
```

## 192K context と KV cache

今回の context size は以下です。

```
# llama.cpp server 側の最大 context size です。
# 196608 は 192K tokens です。
LLAMA_CTX_SIZE=196608
```

KV cache は、K/V ともに `q8_0` にしました。

```
# KV cache の K 側 quantization です。
LLAMA_CACHE_TYPE_K=q8_0

# KV cache の V 側 quantization です。
LLAMA_CACHE_TYPE_V=q8_0
```

Agent 用途では、長い repository context、tool result、ログ、patch、設定ファイルなどを読むため、できるだけ長文参照の品質を落としたくありませんでした。

そのため、まずは `q8_0 / q8_0` を本命にしています。

ただし、192K では VRAM 余白が厳しくなる可能性があります。

OOM が出る場合は、以下の順で落とす想定です。

```
# まず batch / ubatch を下げます。
LLAMA_BATCH_SIZE=1024
LLAMA_UBATCH_SIZE=256
```

それでも厳しい場合は、V cache だけ q4 にします。

```
# V 側だけ q4_0 に落とします。
LLAMA_CACHE_TYPE_K=q8_0
LLAMA_CACHE_TYPE_V=q4_0
```

最後の手段として、K/V の両方を q4 にします。

```
# 最後の手段として K/V 両方を q4_0 にします。
LLAMA_CACHE_TYPE_K=q4_0
LLAMA_CACHE_TYPE_V=q4_0
```

今回の本命は、あくまで以下です。

```
192K context
q8_0 / q8_0 KV cache
MTP draft-mtp n=2
fast alias
```

## benchmark.py

長 context が本当に使えているかを見るために、Needle-in-a-Haystack 形式の benchmark を作りました。

この script では、長い filler text の中央に以下のような needle を埋め込みます。

```
SECRET_PASSWORD = 'RTX5090_QWEN36_MTP_GGUF_PERFORMANCE_TEST'
```

そのうえで、4K から 190K まで段階的に prompt を増やし、以下を見ます。

```
- usage.prompt_tokens
- first token までの時間
- prefill throughput
- decode throughput
- needle を回答できたか
```

script は LiteLLM 経由で呼びます。

```
import json
import os
import time

import requests

# LiteLLM Proxy の chat completions endpoint です。
# llama.cpp server へ直接投げず、今回追加した LiteLLM 経由で測ります。
url = "http://localhost:30000/v1/chat/completions"

# LiteLLM の model alias に合わせます。
# 通常 Agent 用は qwen3.6-27b-mtp-gguf-fast です。
model_name = os.getenv("SERVED_MODEL_NAME", "qwen3.6-27b-mtp-gguf-fast")

# LiteLLM の API key 認証に使います。
api_key = os.getenv("API_KEY", "")

# API_KEY が未設定のまま benchmark を実行しないようにします。
# .env を読み込んでから実行する想定です。
if not api_key:
    raise RuntimeError("API_KEY is not set. Run: set -a; . ./.env; set +a")

headers = {
    # LiteLLM の Bearer token です。
    "Authorization": f"Bearer {api_key}",

    # OpenAI-compatible API として JSON を送ります。
    "Content-Type": "application/json",
}

# ==============================================================================
# コンテキスト長ごとの multiplier 設定
# ==============================================================================
#
# RTX 5090 / Qwen3.6-27B-MTP-GGUF / llama.cpp / LiteLLM 用です。
#
# 注意:
#   4k / 8k / 128k などは「目標ラベル」です。
#   実際の token 数は、レスポンスの usage.prompt_tokens を正として見ます。
#
# 190k は LLAMA_CTX_SIZE=196608 に近いため、
# max_tokens=512 でも context 超過する場合があります。
# その場合は 190k の multiplier を少し下げます。
# ==============================================================================
CONTEXT_CONFIGS = {
    "4k":   40,
    "8k":   80,
    "16k":  160,
    "32k":  320,
    "64k":  640,
    "96k":  960,
    "128k": 1280,
    "160k": 1600,
    "190k": 1900,
}

# 長文の中央に埋め込む needle です。
# モデルが長 context の中からこの値を見つけられるかを確認します。
needle_value = "RTX5090_QWEN36_MTP_GGUF_PERFORMANCE_TEST"
needle = f"SECRET_PASSWORD = '{needle_value}'"

# prompt を長くするための filler text です。
# 内容は単純にして、長 context の prefill と needle retrieval を見ます。
base_sentence = (
    "The sky is blue, the grass is green. "
    "Software engineering requires careful reasoning, reliable tools, and clear benchmarks. "
    "Long context language models must preserve facts across many unrelated sentences. "
    "This filler text is intentionally simple and repeated for prefill performance measurement.\n"
)

print("==============================================================")
print(" RTX 5090: Qwen3.6-27B-MTP-GGUF Context Benchmark")
print("==============================================================")
print(f"URL   : {url}")
print(f"MODEL : {model_name}")
print("APIKEY: <hidden>")

results = []

for label, multiplier in CONTEXT_CONFIGS.items():
    print(f"\n[{label} テスト] multiplier={multiplier} でコンテキストを構築中...")

    # filler text を multiplier 回繰り返します。
    haystack_part = base_sentence * multiplier

    # needle を長文の中央に埋め込みます。
    full_context = f"{haystack_part}\n[SYSTEM NOTE: {needle}]\n{haystack_part}"

    # モデルへの指示です。
    # 最初の行に needle の値だけを答えさせ、その後に分析文を書かせます。
    prompt_instruction = (
        "\n[タスク]\n"
        "1. テキスト内に隠されている SECRET_PASSWORD は何ですか？ "
        "最初の行に、正確なパスワードだけを答えてください。\n"
        "2. 続けて、現代のLLMフレームワークにおいて、このような大規模コンテキストを"
        "処理することの技術的なメリットと、それを支えるアーキテクチャについて、"
        "詳細な分析を日本語で最低3段落記述してください。\n"
        "\n"
        "重要:\n"
        "- 最初の行には SECRET_PASSWORD の値だけを書いてください。\n"
        "- 見つからないとは言わず、必ずコンテキスト内の値を探してください。\n"
    )

    payload = {
        # LiteLLM の model alias を指定します。
        "model": model_name,

        # OpenAI-compatible chat messages 形式です。
        "messages": [
            {
                "role": "user",
                "content": full_context + prompt_instruction,
            }
        ],

        # 各 context 長で同じ出力 token 数を目標にします。
        "max_tokens": 512,

        # benchmark なので温度は 0.0 にします。
        "temperature": 0.0,

        # first token time と streaming usage を見るため stream します。
        "stream": True,

        # stream の最後に usage を含めるための設定です。
        "stream_options": {
            "include_usage": True,
        },

        # Qwen3.6 の thinking を明示的に無効化します。
        #
        # fast alias 側でも enable_thinking=false の preset ですが、
        # benchmark では明示します。
        "chat_template_kwargs": {
            "enable_thinking": False,
        },
    }

    print("リクエスト送信中（Prefillを実行しています）...")

    start_time = time.perf_counter()
    first_token_time = None
    output_text = ""
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=1800,
            stream=True,
        )

        if response.status_code != 200:
            print(f"サーバーエラーが発生しました (HTTP {response.status_code})")
            print(f"エラー詳細: {response.text}")
            results.append(
                {
                    "label": label,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "input_speed": 0,
                    "output_speed": 0,
                    "total_time": 0,
                    "needle_found": False,
                    "error": response.text,
                }
            )
            continue

        for line in response.iter_lines():
            if not line:
                continue

            line_str = line.decode("utf-8", errors="replace").strip()

            if not line_str.startswith("data:"):
                continue

            data_str = line_str[len("data:"):].strip()

            if data_str == "[DONE]":
                continue

            try:
                chunk = json.loads(data_str)
            except json.JSONDecodeError:
                continue

            # stream_options.include_usage=true の usage を拾います。
            if "usage" in chunk and chunk["usage"]:
                prompt_tokens = chunk["usage"].get("prompt_tokens", prompt_tokens)
                completion_tokens = chunk["usage"].get("completion_tokens", completion_tokens)
                total_tokens = chunk["usage"].get("total_tokens", total_tokens)

            # content delta を拾います。
            if "choices" in chunk and len(chunk["choices"]) > 0:
                delta = chunk["choices"][0].get("delta", {})
                content = delta.get("content", "")

                if content:
                    # 最初の content chunk を受信した時刻を first token time とします。
                    if first_token_time is None:
                        first_token_time = time.perf_counter()
                        print("-> 最初の chunk を受信。生成（Decode）を開始します。")

                    output_text += content

                    # usage が最後まで取れない場合の簡易 fallback です。
                    if completion_tokens == 0:
                        completion_tokens += 1

        end_time = time.perf_counter()

        if first_token_time is None:
            first_token_time = end_time

        # prefill は request 開始から first token までの時間として扱います。
        prefill_duration = first_token_time - start_time

        # decode は first token から stream 完了までの時間として扱います。
        decode_duration = end_time - first_token_time

        # request 全体の経過時間です。
        total_time = end_time - start_time

        # input throughput です。
        # prompt_tokens は usage.prompt_tokens を正として使います。
        input_throughput = prompt_tokens / prefill_duration if prefill_duration > 0 and prompt_tokens > 0 else 0

        # output throughput です。
        output_throughput = completion_tokens / decode_duration if decode_duration > 0 and completion_tokens > 0 else 0

        # needle の値が応答内に含まれているかを確認します。
        needle_found = needle_value in output_text

        print(f"\n================ {label} 結果 ================")
        print(f" Needle検出                  : {needle_found}")
        print(f" 入力トークン数 (Prompt)     : {prompt_tokens:,} tokens")
        print(f" 出力トークン数 (Completion) : {completion_tokens:,} tokens")
        print(f" 合計トークン数 (Total)      : {total_tokens:,} tokens")
        print("--------------------------------------------------")
        print(f" インプット（Prefill）速度   : {input_throughput:.2f} tokens/s (時間: {prefill_duration:.2f}秒)")
        print(f" アウトプット（Decode）速度  : {output_throughput:.2f} tokens/s (時間: {decode_duration:.2f}秒)")
        print(f" 総経過時間                  : {total_time:.2f} 秒")
        print("--------------------------------------------------")
        print("出力先頭:")
        print(output_text[:300].replace("\n", "\\n"))
        print("==================================================\n")

        results.append(
            {
                "label": label,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "input_speed": input_throughput,
                "output_speed": output_throughput,
                "prefill_time": prefill_duration,
                "decode_time": decode_duration,
                "total_time": total_time,
                "needle_found": needle_found,
                "error": "",
            }
        )

    except Exception as exc:
        print(f"エラーが発生しました: {exc}")
        results.append(
            {
                "label": label,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "input_speed": 0,
                "output_speed": 0,
                "prefill_time": 0,
                "decode_time": 0,
                "total_time": 0,
                "needle_found": False,
                "error": str(exc),
            }
        )

print("\n\n================ 最終サマリー ================")
print(
    f"{'Context':<10} | "
    f"{'Prompt Tokens':>14} | "
    f"{'Completion':>10} | "
    f"{'Needle':>6} | "
    f"{'Prefill tok/s':>14} | "
    f"{'Decode tok/s':>13} | "
    f"{'Total sec':>10}"
)
print("-" * 96)

for item in results:
    print(
        f"{item['label']:<10} | "
        f"{item['prompt_tokens']:>14,} | "
        f"{item['completion_tokens']:>10,} | "
        f"{str(item['needle_found']):>6} | "
        f"{item['input_speed']:>14.2f} | "
        f"{item['output_speed']:>13.2f} | "
        f"{item['total_time']:>10.2f}"
    )

print("==================================================")
```

実行時は以下のようにしました。

```
# 作業ディレクトリへ移動します。
cd ~/llm/qwen36-27b-mtp-gguf

# .env を shell に読み込みます。
# LITELLM_MASTER_KEY を benchmark.py の API_KEY として渡すためです。
set -a
. ./.env
set +a

# benchmark.py が読む API_KEY を設定します。
# 実運用では master key ではなく、benchmark 用の virtual key を使う方が安全です。
export API_KEY="${LITELLM_MASTER_KEY}"

# benchmark 対象の model alias を指定します。
# 通常 Agent 用の fast alias で測ります。
export SERVED_MODEL_NAME="qwen3.6-27b-mtp-gguf-fast"

# benchmark を実行します。
python3 benchmark.py
```

## benchmark 結果

最終的に 4K から 190K まで完走しました。

Needle も全段階で検出できました。

```
Context    |  Prompt Tokens | Completion | Needle |  Prefill tok/s |  Decode tok/s |  Total sec
------------------------------------------------------------------------------------------------
4k         |          4,156 |        512 |   True |        2487.28 |         76.82 |       8.34
8k         |          8,156 |        512 |   True |        2813.02 |         78.01 |       9.46
16k        |         16,156 |        512 |   True |        2718.03 |         77.12 |      12.58
32k        |         32,156 |        512 |   True |        2610.28 |         75.42 |      19.11
64k        |         64,156 |        512 |   True |        2459.31 |         62.10 |      34.33
96k        |         96,156 |        512 |   True |        2220.07 |         56.54 |      52.37
128k       |        128,156 |        512 |   True |        1984.34 |         50.69 |      74.68
160k       |        160,156 |        481 |   True |        1672.18 |         46.36 |     106.15
190k       |        190,156 |        512 |   True |        1473.21 |         42.56 |     141.11
```

190K の代表値は以下です。

```
prompt_tokens: 190,156
completion_tokens: 512
needle_found: True
prefill: 1,473.21 tok/s
decode: 42.56 tok/s
total: 141.11 sec
```

この結果から、今回の構成では、少なくとも実テキスト prompt で 190K 付近まで通せることを確認できました。

前回の 128K 構成から見ると、今回は Agent 用途にかなり寄せられたと思います。

## benchmark の読み方

今回の benchmark では、`usage.prompt_tokens` を正として見ています。

以前、別の bench tool も試しましたが、random ids 系の benchmark では、指定した input length と実際の token 数が一致しないケースがありました。

そのため、今回の判断基準は以下にしました。

```
cold prefill:
  Needle benchmark の usage.prompt_tokens / first content chunk 時刻を採用します。

decode:
  Needle benchmark の completion_tokens / decode_duration を採用します。

long context success:
  Needle found=True かつ 190K prompt 完走を重視します。
```

特に、Agent 用途では synthetic benchmark の最大値だけを見てもあまり意味がないと感じています。

実際に OpenCode や tool result で大きな context を流したときに、長文中の必要な情報を拾えるかが重要です。

その意味では、今回の Needle-in-a-Haystack 形式は、完璧ではありませんが、最低限の確認としては役に立ちました。

## OpenCode から使う想定

OpenCode 側では、通常 model を以下にする想定です。

```
qwen3.6-27b-mtp-gguf-fast
```

base URL は以下です。

```
http://ip-or-hostname:30000/v1
```

LiteLLM を挟んだことで、OpenCode 側からは llama.cpp 固有の事情をあまり意識しなくてよくなりました。

通常作業では `fast` alias を使い、必要なときだけ `think` alias に切り替えます。

```
通常作業:
  qwen3.6-27b-mtp-gguf-fast

設計判断・原因分析:
  qwen3.6-27b-mtp-gguf-think

client 側で thinking を明示制御したい場合:
  qwen3.6-27b-mtp-gguf
```

## Open WebUI から使う想定

Open WebUI も LiteLLM 経由にしたため、Open WebUI の model list にも alias が見える想定です。

Open WebUI の既定 model は以下にしました。

```
WEBUI_DEFAULT_MODEL=qwen3.6-27b-mtp-gguf-fast
```

Open WebUI は補助 UI として使います。

主用途は OpenCode / Agent ですが、手元で prompt を投げたり、`fast` と `think` の挙動を比較したりするには便利です。

## セキュリティ上の注意

今回のように LiteLLM を入れると、API key を扱う箇所が増えます。

特に benchmark や curl で `Authorization: Bearer sk-...` を出力してしまうと、ログに key が残る可能性があります。

そのため、今後は以下を守ります。

```
- benchmark 用には master key ではなく virtual key を使います
- ログ共有時は sk-... を必ずマスクします
- .env を Git に入れません
- ブログには実 key を書きません
- terminal history に残る command にも注意します
```

この記事内の key はすべて placeholder です。

## OOM が出た場合の調整順

192K context は RTX 5090 32GB ではかなり上限寄りです。

環境差や llama.cpp image の更新によって、OOM になる可能性があります。

その場合は、まず batch / ubatch を下げます。

```
# prompt processing batch size を下げます。
# prefill は少し遅くなる可能性がありますが、VRAM 使用量を下げます。
LLAMA_BATCH_SIZE=1024

# physical micro-batch size を下げます。
# CUDA 実行時のメモリ使用量を抑えるためです。
LLAMA_UBATCH_SIZE=256
```

それでも厳しい場合は、V cache だけ q4 にします。

```
# K 側は q8_0 を維持します。
LLAMA_CACHE_TYPE_K=q8_0

# V 側だけ q4_0 に落として VRAM 使用量を抑えます。
LLAMA_CACHE_TYPE_V=q4_0
```

最後の手段として、K/V 両方を q4 にします。

```
# K 側も q4_0 に落とします。
LLAMA_CACHE_TYPE_K=q4_0

# V 側も q4_0 に落とします。
LLAMA_CACHE_TYPE_V=q4_0
```

ただし、今回の本命は以下です。

```
LLAMA_CTX_SIZE=196608
LLAMA_CACHE_TYPE_K=q8_0
LLAMA_CACHE_TYPE_V=q8_0
LLAMA_BATCH_SIZE=1536
LLAMA_UBATCH_SIZE=384
```

## 今回の結論

今回の変更で、RTX 5090 上の Qwen3.6-27B-MTP-GGUF 環境を、AI Agent 用にかなり寄せることができました。

最終的な構成は以下です。

```
RTX 5090 32GB
Qwen3.6-27B-MTP-GGUF
UD-Q4_K_XL
llama.cpp server-cuda
LiteLLM Proxy
Open WebUI
192K context
q8_0 / q8_0 KV cache
MTP draft-mtp n=2
```

LiteLLM を挟んだことで、model alias を以下のように分けられました。

```
qwen3.6-27b-mtp-gguf
  passthrough

qwen3.6-27b-mtp-gguf-fast
  通常 Agent 用
  enable_thinking=false

qwen3.6-27b-mtp-gguf-think
  設計判断・原因分析用
  enable_thinking=true
```

また、Needle-in-a-Haystack benchmark では、190K 付近まで通せました。

```
190,156 prompt tokens
512 completion tokens
Needle True
prefill 1,473.21 tok/s
decode 42.56 tok/s
total 141.11 sec
```

これで、前回の「RTX 5090 で Qwen3.6-27B-MTP-GGUF を動かす」段階から、今回は「OpenCode / AI Agent の実作業に使うための gateway 構成」へ進められました。

今後は、この構成で OpenCode の実作業ログを見ながら、timeout、max\_tokens、MTP draft n、KV cache、batch size あたりを少しずつ詰めていきます。
