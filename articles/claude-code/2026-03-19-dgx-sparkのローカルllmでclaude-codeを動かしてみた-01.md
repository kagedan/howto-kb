---
id: "2026-03-19-dgx-sparkのローカルllmでclaude-codeを動かしてみた-01"
title: "DGX SparkのローカルLLMでClaude Codeを動かしてみた"
url: "https://zenn.dev/caists/articles/ed05fa15da72ee"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "LLM", "zenn"]
date_published: "2026-03-19"
date_collected: "2026-03-20"
summary_by: "auto-rss"
---

DGX Sparkが手元にあるなら、ローカルLLMでClaude Codeを動かせないだろうか？

そう思って試してみたら、意外とちゃんと動いた。ファイルの読み書き、コマンド実行、コード探索といった基本的なコーディング作業が、Anthropic APIなしでローカル完結でできるようになり、**Webアプリを約1時間で自律的に構築する**ところまで到達した。

この記事では、そのために作った「Claude Local Proxy」の仕組みと、小型モデルをClaude Codeで実用するために必要だった工夫をまとめておく。

ソースコードはGitHubで公開している。  
<https://github.com/CaistsAI/claude-local-proxy>

---

## Claudeをローカルで使いたい

Claude Codeを使っている方なら共感してもらえると思うが、業務でClaude Codeを使いたいのに、セキュリティポリシーの関係でクラウドに接続できないという状況がある。社内のソースコードをクラウドのAPIに送るのは、コンプライアンス上NGという会社は少なくないと思う。

でも、Claude Codeの便利さは手放したくない。

だったら、同じようなレベルの体験をローカルで実現できないかと考えた。同じことを考えている方は多いのではないだろうか。少しでも参考になればと思い、今回のプロジェクトをGitHubで公開することにした。

小型で机の横に置けて低電力で使えるのが魅力的なDGX Spark。ただし、DRAM帯域の関係でToken/s的には不利なマシンでもある。この環境で実用的に使える構成にすることを目標にした。DGX Sparkは本当に使えるの？と思っている読者の方も多いのではないだろうか。

### DGX Sparkのスペック

DGX Sparkは、NVIDIAが「デスクトップに置けるAIスーパーコンピュータ」として2025年にリリースしたマシンだ。

* **プロセッサ**: NVIDIA GB10 Grace Blackwell Superchip（Grace CPU 20コア + Blackwell GPU を1チップに統合）
* **メモリ**: 128GB LPDDR5x（CPU/GPU統合メモリ、NVLink-C2C接続）
* **AI性能**: 最大1 PFLOPS（FP4）
* **ストレージ**: NVMe SSD 1〜4TB（SKUにより選択）
* **OS**: Ubuntu ベースのDGX OS（NVIDIA AIソフトウェアスタック プリインストール）
* **対応モデル規模**: 最大2000億パラメータのモデルをローカル推論可能
* **マルチノード**: 2台をConnectX-7で接続すれば最大4050億パラメータにも対応

128GBの統合メモリがポイントで、VRAMとシステムメモリの区別がない。この128GBをまるごとLLMに使えるので、それなりに大きなモデルも動かせる。このメモリの大きさを上手く活かせるかもポイントになる。

---

## やりたいことと課題

やりたいことはシンプルだ。

```
Claude Code CLI → ローカルのLLM
```

ところが、これがそのままでは動かない。理由は**APIの形式が違う**から。

* Claude CodeはClaude API（Anthropic独自フォーマット）でしか通信しない
* ローカルLLMの推論エンジン（vLLM）はOpenAI互換APIを提供する

エンドポイントも違う、メッセージの形式も違う、ストリーミングのイベント形式も違う、ツール呼び出しの方法も違う。全部違う。

既にオープンソースのclaude-code-proxyなど先行のプロジェクトはある。そちらを使う選択肢もあったが、Claude Code CLIの内部の仕組み（どんなAPIリクエストを送っているのか、ツール呼び出しはどう動いているのか）を深く理解したかったので、プロキシをゼロから自作することにした。

---

## Claude Codeが求めるもの — 200Kトークンの世界

モデル選びの前に、Claude Codeがバックエンドに何を求めているのかを整理しておく。

Claude Codeの公式ドキュメントによると、Claude Codeは**固定200Kトークンのコンテキストウィンドウ**内で動作する。この200Kトークンは、システムプロンプト、CLAUDE.mdファイル、ツール定義、会話履歴、レスポンスバッファのすべてで共有される。

実際にプロキシのログを見ると、Claude Code CLIが送ってくるシステムプロンプトは約61,000文字、ツール定義は20個以上で数万トークンに達する。MCP（Model Context Protocol）サーバーを接続するとさらに増え、Anthropicの事例では**ツール定義だけで134Kトークン**を消費したケースもあるという（[Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use)）。

つまり、ローカルLLMには以下が求められる。

* **200Kトークン以上のコンテキスト長に対応**できること
* **巨大なシステムプロンプトを正しく理解**できること
* **20以上のツールを使い分けるツール呼び出し能力**があること
* **エージェントとして何十回もリクエストを受けるので、応答速度が速い**こと

これを踏まえた上で、モデルを選ぶ。

---

## モデル選定の変遷 — Nemotronから Qwen3.5へ

### 最初の選択: Nemotron-3-Nano-30B-A3B

初期開発ではNVIDIA Nemotron-3-Nano-30B-A3B-FP8を使用した。総パラメータ30Bだがアクティブパラメータは3BのMoEモデルで、DGX Sparkで約40 tok/sの生成速度が出る。大容量メモリだがメモリ帯域は広くないDGX Sparkには、MoEモデルが最適解だった。

しかし、Claude Codeのエージェントとして使うと限界が見えてきた。

* **検証・デバッグ能力の不足**: HTTP 500を成功と報告する、修正の横展開を見落とす、307リダイレクトの原因を特定できない
* **ツールパラメータの頻繁なミス**: パラメータ名の間違い（`cmd`→`command`）、必須パラメータの省略、Python形式の値出力（`True`→`true`）
* **vLLMのバグ**: `max-num-seqs=4`設定時にthinking-onlyの出力のみになるNemotron固有のバグがあった

### 中間: Qwen3-Coder-Next-FP8

Qwen3-Coder-Next-FP8（80B MoE/3Bアクティブ）も試したが、エージェント能力が不足していた。エラーループに陥りやすく、ステップをスキップする傾向があった。

### 現在の選択: Qwen3.5-27B-FP8

最終的にQwen/Qwen3.5-27B-FP8に落ち着いた。27Bの密（Dense）モデルで、Gated DeltaNet hybridアテンション機構を持つ。

MoEではなくDenseモデルを選んだのは、アクティブパラメータ3Bでは推論能力に限界があり、27B全パラメータがアクティブなDenseモデルのほうがエージェント能力が高いためだ。生成速度は約7 tok/sとNemotronの40 tok/sから大幅に落ちるが、実用上の成果（正しく動くコードを出力する能力）で上回った。

#### ベンチマーク: GPT-5 mini相当のソフトウェア開発能力

このモデルを選んだ決め手はベンチマークスコアだ。ソフトウェア開発に直結するベンチマークで、27Bという小さなモデルにもかかわらずGPT-5 miniと同等以上のスコアを叩き出している。

| ベンチマーク | Qwen3.5-27B | GPT-5 mini | 説明 |
| --- | --- | --- | --- |
| **SWE-bench Verified** | **72.4** | 72.0 | 実際のGitHubイシュー修正能力 |
| **LiveCodeBench v6** | **80.7** | 80.5 | ライブコーディング能力 |
| **Terminal-Bench 2** | **41.6** | 31.9 | ターミナル操作・デバッグ能力 |
| **FullStackBench (en)** | **60.1** | 30.6 | フルスタック開発能力 |
| **FullStackBench (zh)** | **57.4** | 35.2 | フルスタック開発能力（中国語） |
| **IFEval** | **95.0** | 93.9 | 指示追従能力 |

特にSWE-bench Verified 72.4は注目に値する。これは実際のGitHubリポジトリのイシューをモデルが自律的に解決する能力を測るベンチマークで、**GPT-5 mini（72.0）を上回っている**。FullStackBenchでは60.1対30.6と倍近い差をつけており、フルスタックのアプリケーション開発能力ではGPT-5 miniを大きく凌駕する。

エージェント関連のベンチマークも強力だ。

| ベンチマーク | Qwen3.5-27B | GPT-5 mini | 説明 |
| --- | --- | --- | --- |
| **BFCL-V4** | **68.5** | 55.5 | Function Calling（ツール呼び出し）能力 |
| **TAU2-Bench** | **79.0** | 69.8 | エージェントタスク遂行能力 |

BFCL-V4（ツール呼び出しベンチマーク）で68.5対55.5と13ポイントもの大差がある。これはClaude Codeのようなツール呼び出し主体のエージェントにとって極めて重要な指標で、Nemotron-3-Nanoで苦しめられたパラメータミスの問題がQwen3.5では大幅に改善された理由を裏付けている。

#### 体感: クラウドのClaude Codeと遜色ない

ベンチマークの数字だけでなく、実際の体感も大きく変わった。

正直に言うと、Qwen3.5-27Bに切り替えてからは**ローカルで動いていることを忘れるほど自然に使えている**。ファイルの読み書き、コード生成、バグの発見と修正、開発計画の策定 — どれもClaude Codeをクラウドのネイティブ環境で使っているときと遜色がない。実際、ある日の開発作業中に「今日はAPIレスポンスが速いな」と思っていたら、ローカルのプロキシ経由で動いていたことに後から気づいた、ということもあった。

もちろん速度面ではクラウドに劣る。7 tok/sの生成速度はThinking有効時に数分の待ち時間を生む。ただし、**頭出しの速さはローカルならではの強み**がある。クラウドAPIではネットワークのレイテンシやサーバー側のキューイングで最初のトークンが返ってくるまでに数秒かかることがあるが、ローカルではプレフィックスキャッシュがヒットすれば0.5〜1.4秒で最初のトークンが出てくる。ネットワークを経由しない分、レスポンスの「取りかかり」が圧倒的に速い。この頭出しの速さが、7 tok/sという生成速度のハンデを体感上かなりカバーしている。ツール呼び出しのような短い出力（数十〜数百トークン）では、頭出しが速い分むしろクラウドより軽快に感じることすらある。

これは、**出力の質** — ツール呼び出しの正確さ、コード構造の妥当さ、指示への追従性 — ではクラウドのモデルに肉薄するレベルに達した。プロキシの各種補正機能（Thinking制御、Stall検出、フェーズ管理）と組み合わせることで、速度のハンデを補って余りある実用性が実現できている。

Nemotron-3-Nanoの時代には「ローカルLLMで頑張っている感」が常にあった。パラメータの間違い、検証能力の不足、エラーループ…。それがQwen3.5-27Bでは消えた。**27Bのローカルモデルがクラウドのフラッグシップモデルに匹敵する体験を提供できる時代になった**のだと実感している。

なお、NVIDIAが2026年前半にリリースを予定しているNemotron-3 Super（約100B/10Bアクティブ）にも期待している。FP8量子化で約100GBのメモリが必要になるが、DGX Sparkの128GBに収まる。Nanoの3Bアクティブではエージェント能力に限界があったが、10Bアクティブになれば推論能力が大幅に向上するはずだ。さらにlatent MoE、multi-token prediction、NVFP4といった新技術も搭載予定で、MoEならではの高スループット（Denseの27Bより速い可能性がある）とDenseに近い推論能力を両立できるかもしれない。NVIDIAのモデルをNVIDIAのGPUで動かすネイティブ最適化の強みもある。Qwen3.5-27Bで「クラウドと遜色ない体験」が実現できた今、Nemotron-3 Superではさらにその先 — 速度面でもクラウドに迫る体験 — が期待できるだろう。

| 項目 | Nemotron-3-Nano | Qwen3.5-27B |
| --- | --- | --- |
| パラメータ | 30B (3B active) | 27B (Dense) |
| 生成速度 | ~40 tok/s | ~7 tok/s |
| メモリ使用量 | ~30.5 GiB | ~31 GiB |
| ツール呼び出し精度 | 低（頻繁なパラメータミス） | 高（vLLMネイティブtool\_call対応） |
| 検証・デバッグ能力 | 弱（3B active） | 良好（27B） |
| コンテキスト長 | 1M | 200K（運用値） |
| Thinkingサポート | `<think>` タグ | `<think>` タグ（reasoning-parser対応） |
| SWE-bench Verified | — | 72.4（GPT-5 mini相当） |
| BFCL-V4 | — | 68.5（GPT-5 mini超） |

### vLLMの環境構築

Qwen3.5-27B-FP8には専用のvLLMイメージが必要だ。GB10のCUDA Capability 12.1（sm\_121a）では、標準のvLLMイメージやcu130-nightlyイメージではTriton JITコンパイルがハングする。`vllm/vllm-openai:qwen3_5-cu130`イメージを使えば解決する。

```
services:
  vllm:
    image: vllm/vllm-openai:qwen3_5-cu130
    container_name: vllm-llm
    network_mode: host
    ipc: host
    command: >
      Qwen/Qwen3.5-27B-FP8
      --host 0.0.0.0
      --port 8000
      --tensor-parallel-size 1
      --max-model-len 200000
      --gpu-memory-utilization 0.80
      --max-num-seqs 2
      --enforce-eager
      --language-model-only
      --enable-auto-tool-choice
      --tool-call-parser qwen3_coder
      --reasoning-parser qwen3
      --enable-prefix-caching
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    restart: "no"
```

主要なフラグの解説：

* **`--enforce-eager`**: GB10ではCUDAグラフ最適化が不安定なため必須
* **`--language-model-only`**: Qwen3.5はマルチモーダルモデルだがテキスト推論のみ使用
* **`--tool-call-parser qwen3_coder`**: Qwen3用のネイティブツール呼び出しパーサー
* **`--reasoning-parser qwen3`**: `<think>...</think>`タグを構造化して返す
* **`--enable-prefix-caching`**: 毎回送られる巨大なシステムプロンプトをキャッシュ。TTFTを大幅短縮

---

## システム構成

全体像はこんな感じ。

```
Claude Code CLI ──[Claude API]──> Claude Local Proxy ──[OpenAI API]──> vLLM + Qwen3.5
                                   (FastAPI)                            (Docker)
                                   port:8082                            port:8000
```

登場人物は3つ。

* **Claude Code CLI**: Anthropic公式のコーディングアシスタント。Claude APIフォーマットでリクエストを送ってくる
* **Claude Local Proxy**: 今回作ったもの。PythonのFastAPIで書いた。Claude APIとOpenAI APIを双方向に変換するだけでなく、小型モデルを実用するための多数の補正・制御機能を持つ
* **vLLM + Qwen3.5**: vLLMコンテナでQwen3.5-27B-FP8を走らせる

Claude Code CLIから見ると、普通にClaude APIサーバーと通信しているように見える。裏側でローカルLLMが動いていることは意識しなくていい。

---

## 小型モデルでClaude Codeを動かすための課題

Claude Codeは本来、Claude Opus/Sonnetクラスの大規模モデルで動かすことを前提に設計されている。27Bの小型モデルで動かすと、以下のような問題が次々に発生した。

1. **巨大なシステムプロンプト**: 毎回約61,000文字のプロンプトが送られてくる。トークン量が膨大で小型モデルの処理能力を圧迫する
2. **Thinking（拡張思考）の暴走**: モデルが思考ブロックに数千トークンを費やし、肝心の回答が出力されない
3. **Thinking-onlyレスポンス**: 思考だけして何も返答しない（ツール呼び出しもテキスト出力もない）
4. **テキストのみのレスポンス（stall）**: テキストで説明するだけで実際にツールを使って作業しない
5. **フェーズの混乱**: 計画・実装・検証の区別がつかず、実装中にテストを始めたり、未完成なのに完了宣言する
6. **トークン消費の管理**: コンテキストウィンドウの肥大化を適切にコンパクション（圧縮）させる必要がある

これらの問題に対応するため、プロキシに多数の機能を実装した。

---

## Claude Local Proxyの機能一覧

プロキシには2つの動作モードがある。

* **Passthroughモード**: Claude Codeの元のシステムプロンプト（61K文字）をそのまま維持する。Claude Codeの全機能（サブエージェント、コンパクション、自律的判断）がそのまま使え、プロキシは最小限の補正とThinking制御のみを行う。大規模モデルや、Claude Codeの挙動を忠実に再現したい場合に適している。
* **Rewriteモード**: システムプロンプトをフェーズ別の軽量プロンプト（playbook.md）に置き換える。トークン量を大幅に削減し、計画→実装→検証のフェーズ管理で小型モデルの行動を制御する。27Bクラスのモデルで安定した開発を行うために設計されたモード。

以下の24機能がどちらのモードで有効かを示す。

| # | 機能 | Passthrough | Rewrite | カテゴリ |
| --- | --- | --- | --- | --- |
| 1 | Claude→OpenAI形式変換 | ○ | ○ | 基本変換 |
| 2 | モデル名マッピング | ○ | ○ | 基本変換 |
| 3 | Deferred Tool展開 | ○ | ○ | 基本変換 |
| 4 | Passthroughモード（元プロンプト維持） | ○ | — | プロンプト |
| 5 | Rewriteモード（フェーズ別プロンプト） | — | ○ | プロンプト |
| 6 | フェーズ検出 | — | ○ | プロンプト |
| 7 | フェーズ別プロンプト | — | ○ | プロンプト |
| 8 | Thinking有効/無効切り替え | ○ | ○ | Thinking |
| 9 | フェーズ別Thinking Budget | ○ | ○ | Thinking |
| 10 | Thinking-onlyリトライ | ○ | ○ | Thinking |
| 11 | Stall検出 | ○ | ○\* | レスポンス |
| 12 | 完了宣言検証 | — | ○ | レスポンス |
| 13 | トークンInflation | ○ | ○ | トークン |
| 14 | コンパクション検出 | ○ | ○ | トークン |
| 15 | サンプリングパラメータ注入 | ○ | ○ | サンプリング |
| 16 | プロキシ自殺防止 | ○ | ○ | ツール安全 |
| 17 | Git安全チェック | ○ | ○ | ツール安全 |
| 18 | ツールパラメータ補正 | — | ○ | ツール安全 |
| 19 | cdコマンドブロック | — | ○ | ツール安全 |
| 20 | reasoning\_content分離 | ○ | ○ | ストリーミング |
| 21 | `<think>`タグ除去 | ○ | ○ | ストリーミング |
| 22 | Task/TaskOutput説明パッチ | ○ | ○ | ストリーミング |
| 23 | Thinking指示注入 | ○ | ○ | プロンプト |
| 24 | Working Dir指示注入 | ○ | ○ | プロンプト |

\*Rewriteモードではアクションフェーズ（実装・検証）のみ発動

基本変換・Thinking制御・ストリーミング処理は両モード共通だが、フェーズ管理（#5-7, #12）とツールパラメータ補正（#18-19）はRewrite専用機能。以下、各機能の詳細を整理する。

### リクエスト変換（基本機能）

| # | 機能 | なぜ必要か | 処理内容 |
| --- | --- | --- | --- |
| 1 | **Claude→OpenAI形式変換** | APIフォーマットが完全に異なる | エンドポイント、メッセージ形式、ツール定義、ストリーミングイベントを双方向変換 |
| 2 | **モデル名マッピング** | Claude Codeはclaude-opus/haiku等のモデル名で送ってくる | model\_mapping設定でvLLMのモデル名に変換 |
| 3 | **Deferred Tool展開** | Claude Code v2.1.63+ではツール定義がdeferred（遅延読み込み）で送られる | `<available-deferred-tools>`タグを検出し、フルスキーマを注入。vLLMはdefer\_loading非対応 |

### システムプロンプト制御（2モード）

| # | 機能 | なぜ必要か | 処理内容 |
| --- | --- | --- | --- |
| 4 | **Passthroughモード** | Claude Codeの元のシステムプロンプトをそのまま使いたい場合 | 元プロンプトを維持し、最小限の補正（Thinking指示、Working Dir指示）のみ注入 |
| 5 | **Rewriteモード** | 小型モデルでは61K文字のプロンプトが大きすぎる | フェーズ別の軽量プロンプト（playbook.md）に置き換え。トークン量を大幅削減し、フェーズに応じた具体的な行動指示を与える |
| 6 | **フェーズ検出** | 計画・実装・検証で必要な能力と制約が異なる | メッセージ中のキーワード（「計画フェーズ」「実装フェーズ」等）を走査し、最新のフェーズを検出 |
| 7 | **フェーズ別プロンプト** | 各フェーズで適切な行動ルールを与える | 計画: 設計に集中、実装: ファイル作成必須、検証: 必ずコマンド実行、報告: コードから事実を抽出 |

### Thinking（拡張思考）制御

| # | 機能 | なぜ必要か | 処理内容 |
| --- | --- | --- | --- |
| 8 | **Thinking有効/無効切り替え** | haiku（サブエージェント）やコンパクションではThinking不要 | モデル名にhaikuを含む場合、またはコンパクション検出時にenable\_thinking=falseに設定 |
| 9 | **フェーズ別Thinking Budget** | フェーズにより必要な思考量が異なる | 計画/検証: 8000トークン、通常: 4000、実装: 2000（コード生成はThinkingが短くてよい） |
| 10 | **Thinking-onlyリトライ** | モデルが思考だけして何も出力しないことがある | 出力トークン≤1またはThinkingブロックのみの場合を検出。Thinkingを無効にしてリトライ、それでもダメならThinking有効+ツール使用を促すプロンプトで再リトライ |

### レスポンス検証・リトライ

| # | 機能 | なぜ必要か | 処理内容 |
| --- | --- | --- | --- |
| 11 | **Stall検出** | テキストだけ出力してツールを呼ばない「停滞」が発生する | テキストのみの出力（100文字以上でツールコールなし）を検出し自動リトライ。Rewriteモードではアクションフェーズ（実装・検証）のみ発動 |
| 12 | **完了宣言検証** (Rewrite) | 未完成なのに「実装フェーズ完了」と宣言することがある | 完了トリガーキーワードを検出すると、自動検証プロンプト（ファイル存在確認、構文チェック等）を注入してリトライ |

### トークン管理

| # | 機能 | なぜ必要か | 処理内容 |
| --- | --- | --- | --- |
| 13 | **トークンInflation** | Claude Codeのコンパクション（コンテキスト圧縮）を適切なタイミングで発動させたい | messagesのトークン数を4倍にinflateしてClaude Code CLIに報告。CLIが閾値に達したと判断しコンパクションを発動する |
| 14 | **コンパクション検出** | コンパクション時はThinkingが有害（要約がThinkingに吸収される） | 「Your task is to create a detailed summary」を含むメッセージを検出し、Thinkingを無効化 |

### サンプリング制御

| # | 機能 | なぜ必要か | 処理内容 |
| --- | --- | --- | --- |
| 15 | **サンプリングパラメータ注入** | Qwen3.5に最適なサンプリング設定を適用 | playbook.mdのSAMPLING設定（temperature=0.6, top\_p=0.95, top\_k=20）をリクエストに注入 |

### ツールコール安全機構

| # | 機能 | なぜ必要か | 処理内容 |
| --- | --- | --- | --- |
| 16 | **プロキシ自殺防止** | LLMがプロキシプロセスを誤ってkillする | `kill <proxy_pid>`, `pkill proxy`, `fuser -k 8082`等のコマンドをブロック |
| 17 | **Git安全チェック** | 危険なGitコマンドの誤実行を防ぐ | `push --force`, `reset --hard`, `clean -f`, `branch -D`等をブロック（playbook.mdで設定） |
| 18 | **ツールパラメータ補正** (Rewrite) | 小型モデルはパラメータ名を間違える | `cmd`→`command`, `path`→`file_path`, Task→TaskOutput自動修正等 |
| 19 | **cdコマンドブロック** (Rewrite) | cdでディレクトリ移動するとワーキングディレクトリの認識がずれる | `cd dir && cmd`を`cmd`に変換し相対パスを調整 |

### ストリーミング処理

| # | 機能 | なぜ必要か | 処理内容 |
| --- | --- | --- | --- |
| 20 | **reasoning\_content分離** | vLLMのreasoning parserがThinkingとテキストを分離して返す | `reasoning_content`フィールドをClaude APIのThinkingブロックとしてリアルタイム送出 |
| 21 | **`<think>`タグ除去** | Thinkingが無効な場合でもモデルがタグを出力することがある | 設定に応じてレスポンスから`<think>...</think>`を除去 |
| 22 | **Task/TaskOutput説明パッチ** | LLMがフォアグラウンドTask後に不要なTaskOutputを呼ぶ | システムプロンプト内のTask説明を「結果はtool\_resultに直接含まれる」に書き換え |

### ランタイムプロンプト注入

| # | 機能 | なぜ必要か | 処理内容 |
| --- | --- | --- | --- |
| 23 | **Thinking指示注入** | ThinkingがONでもモデルが内部推論と出力を混同する | 「`<think>`は内部推論のみ、回答は必ず`</think>`の後に出力せよ」を注入 |
| 24 | **Working Dir指示注入** | モデルがプロジェクト外にファイルを作成することがある | 「Primary working directory内でのみ作業せよ、相対パスを使え」を注入 |

---

## Rewriteモード — 小型モデルのための独自プロンプト戦略

Claude Codeの61,000文字のシステムプロンプトは、Claude Opus/Sonnetクラスの大規模モデルを前提に設計されている。27Bの小型モデルにこれをそのまま渡すと、いくつかの問題が発生する。

1. **トークン量の圧迫**: 61K文字のプロンプト＋ツール定義で入力トークンの大部分を消費
2. **指示の埋没**: 大量の指示の中で重要な行動ルールが埋もれる
3. **フェーズの混乱**: 計画・実装・検証の区別がつかず、場当たり的な行動をとる

Rewriteモードでは、Claude Codeのシステムプロンプトを**フェーズ別の軽量プロンプト**に完全に置き換える。

### playbook.md — Markdownベースのフェーズ定義

フェーズごとのプロンプトは`playbook.md`というMarkdownファイルで管理している。チェックボックス形式で機能のON/OFFを制御できる。

```
# Common
- [x] LANGUAGE: Reply in the SAME language as the user.
- [x] TOOL USAGE: You MUST call tools to perform actions.
- [x] THINKING: Do NOT deliberate on formatting.
- [x] SAMPLING: temperature=0.6, top_p=0.95, thinking_budget=2000

# Phase: planning
- name: 計画フェーズ
- keywords: 計画フェーズ, planning phase
- role: software architect
---
<phase-planning>
You are a software architect.
Your job: analyze requirements, design systems, create development plans.
...（フェーズ固有のプロンプト）
</phase-planning>

# Phase: implementation
- name: 実装フェーズ
- keywords: 実装フェーズ, implementation phase
...
```

各フェーズでは以下を定義する:

* **role**: LLMが演じる役割（architect、developer、QA engineer等）
* **keywords**: フェーズ遷移を検出するキーワード
* **tools**: フェーズで使用可能なツール（実装フェーズではBash許可、計画フェーズでは禁止等）
* **completion\_triggers**: 完了宣言を検出するキーワード（自動検証トリガー）
* **プロンプト本文**: フェーズ固有のワークフロー、ルール、禁止事項

### Passthroughモードとの使い分け

| 観点 | Rewriteモード | Passthroughモード |
| --- | --- | --- |
| システムプロンプト | playbook.mdの軽量プロンプトに置き換え | Claude Codeの元プロンプトをそのまま使用 |
| トークン消費 | 少ない | 大きい（61K文字） |
| フェーズ管理 | あり（計画→実装→検証→報告） | なし |
| 完了宣言検証 | あり | なし |
| ツールパラメータ補正 | あり | なし（モデルの能力に依存） |
| 適用場面 | 小型モデル、構造化されたタスク | 高能力モデル、自由度の高いタスク |

---

## Thinking制御の詳細

Thinking（拡張思考）の制御は、小型モデルでClaude Codeを実用するための最も重要な機能の一つだ。

### 問題: Thinkingの暴走

Qwen3.5は`<think>`ブロックに数千トークンを費やすことがある。`max_tokens`の上限に達し、肝心の回答本文が途切れるケースがあった。さらに深刻なのは**Thinking-onlyレスポンス**で、モデルが思考だけして何も出力しない（ツール呼び出しもテキスト出力もない）状態になる。

### 対策1: フェーズ別Thinking Budget

```
計画フェーズ:     8000トークン（設計判断に思考が必要）
検証フェーズ:     8000トークン（デバッグに思考が必要）
通常フェーズ:     4000トークン
報告フェーズ:     4000トークン
実装フェーズ:     2000トークン（コード生成はThinkingが短くてよい）
```

### 対策2: Thinking無効化の自動判定

以下の条件でThinkingを自動的に無効化する:

1. **haiku（サブエージェント）**: モデル名にhaikuを含む場合。サブエージェントはファイル検索などの軽量タスクで、Thinkingは不要
2. **コンパクション**: 「Your task is to create a detailed summary」を検出。コンパクション応答がThinkingに吸収されるバグを防ぐ

### 対策3: Thinking-onlyリトライ

Thinking-onlyレスポンスの検出とリトライは3段階で行う:

1. **検出**: 出力トークン≤1、またはThinkingブロックのみで終了
2. **1回目リトライ**: Thinkingを無効にして再リクエスト
3. **2回目リトライ**: Thinkingを有効に戻し、「ツールを使って作業を進めてください」というプロンプトを追加

---

## テストプロジェクト — 家計簿アプリの開発

プロキシの実用性を評価するため、同じ仕様書（PROJECT\_KAKEIBO\_APP.md）から家計簿Webアプリの開発をQwen3.5-27B-FP8に繰り返し行わせた。Rewriteモード（フェーズ管理あり）とPassthroughモード（Claude Codeの元プロンプト）の両方で実施し、比較した。

### Rewrite vs Passthrough 比較

ユーザ待ち時間を除いた実質開発時間で比較する。いずれもQwen3.5-27B-FP8で同一仕様書から構築。

| 比較項目 | Rewrite | Passthrough | 備考 |
| --- | --- | --- | --- |
| **開発時間**（ユーザ待ち除外） | **1h00m** | 4h25m | Rewriteが4.4倍速い |
| **GPU推論時間** | 59.6分 | 253分 |  |
| **平均生成速度** | 6.2 tok/s | 2.8 tok/s | Passthroughはretryで実効速度が低下 |
| **リクエスト数** | 96 | 214 |  |
| **Thinking-only retry** | 4回 | 544回 | Passthroughの最大課題 |
| **Stall検出** | 4回 | 0回 |  |
| **仕様充足** | 6/6 | 5/6 | Passthroughは月別推移グラフが逆順 |
| **致命的バグ** | 0件 | 1件（CORS不一致） |  |
| **中程度バグ** | 3件 | 7件 |  |
| **コード構造** | 4層分離 | 2層 | Rewriteはmodels→schemas→crud→routers |
| **技術選定** | React+Vite+Tailwind | React+CRA+カスタムCSS |  |
| **ファイル数 / 行数** | 42 / 1,350行 | 15 / 1,200行 |  |
| **総合スコア** | **85/100 (B+)** | 78/100 (B-) | Claude自身が全コードを読んで採点 |

### Rewriteモードの特徴

* **致命的バグ0件**: フェーズ管理により実装漏れや検証不足を防止。完了宣言検証が効果的
* **技術選定の安定性**: フェーズプロンプトが技術スタックを誘導し、毎回モダン構成を選定
* **コード品質が高い**: 計画フェーズで詳細な開発計画を作成してから実装するため、4層分離が安定
* ただし**playbook.mdの品質に依存**し、Claude Codeのサブエージェント機能を一部制限する

### Passthroughモードの特徴

* **Claude Codeの全機能が使える**: サブエージェント、コンパクション、自律的判断がそのまま活きる
* **LLMが自発的に開発計画を作成**: 342行の計画書を自ら書いてから実装に入る
* **Thinking-onlyリトライが最大の課題**: 544回のリトライが発生し、開発時間が膨張。61K文字のシステムプロンプトが原因でモデルがThinkingのみ出力してしまう
* **コード構造が薄い**: routers層にビジネスロジックが集約され、CRUD層の分離がない

### 成果物

完成したアプリはFastAPIバックエンドとReactフロントエンドで構成され、収支の登録・編集・削除、月別サマリ、カテゴリ別円グラフ、月別推移棒グラフの全機能を備える。

### 残存課題（両モード共通）

* API URLがlocalhost固定（Vite proxy未使用、外部アクセス未対応）
* Float型で金額管理（Decimalが望ましい）
* テストコード未作成

---

## Claude Local Proxyのコード構成

```
claude-local-proxy/
├── app/
│   ├── main.py              (72行)   FastAPIアプリ初期化
│   ├── config.py            (88行)   環境変数ベースの設定管理
│   ├── pipeline.py          (270行)  パイプライン/フィルタパターンのオーケストレーション
│   ├── models/
│   │   ├── claude.py        (197行)  Claude APIスキーマ定義
│   │   └── openai.py        (88行)   OpenAI APIスキーマ定義
│   ├── routers/
│   │   └── messages.py      (735行)  ストリーミング処理、リトライロジック
│   ├── services/
│   │   ├── converter.py     (315行)  Claude⇔OpenAI形式変換、SSEイベント生成
│   │   └── vllm_client.py   (104行)  vLLMへの非同期HTTP通信
│   ├── filters/
│   │   ├── request.py       (511行)  リクエスト変換フィルタチェーン
│   │   ├── response.py      (100行)  レスポンス検証フィルタ
│   │   └── tool.py          (209行)  ツールコール安全チェック
│   ├── prompts/
│   │   ├── phase_config.py  (630行)  playbook.mdパーサー、フェーズ設定管理
│   │   ├── phase_prompts.py (23行)   後方互換re-export
│   │   ├── behavior_instructions.py (232行) 行動制御プロンプト
│   │   ├── phases/
│   │   │   └── playbook.md  (583行)  フェーズ定義（Markdown）
│   │   └── plugins/
│   │       ├── __init__.py           プラグインレジストリ
│   │       ├── thinking_only_handler.py  Thinking-onlyリトライ
│   │       ├── stall_detector.py     Stall検出
│   │       ├── completion_verifier.py 完了宣言検証
│   │       └── git_safety.py         Git安全チェック
│   └── tools/
│       └── tool_schemas.py  (40行)   Deferred Toolスキーマレジストリ
├── envs/
│   └── qwen3.5-27b-fp8.env          モデル別環境変数
├── docker-compose.yml                vLLMコンテナ定義
└── scripts/
    └── claude-local.sh               Claude Code起動ラッパー
```

### アーキテクチャ: パイプライン/フィルタパターン

プロキシの中核は`pipeline.py`が管理するフィルタチェーンだ。

```
Claude API Request
  ↓
[Request Filters] ← mode別（passthrough/rewrite）で異なるチェーン
  extract_system_prompt → detect_model_type → apply_thinking_config → ...
  ↓
OpenAI API Request → vLLM
  ↓
[Streaming Response]
  reasoning_content → Thinking Block
  content → Text / Tool Calls
  ↓
[Response Filters]
  thinking_only_retry → stall_detect → (completion_verify)
  ↓
Claude API Response (SSE)
```

各フィルタは独立した関数で、`RequestContext`を共有する。フィルタの追加・削除・順序変更が容易で、モードの切り替えもフィルタチェーンの差し替えで実現している。

---

## パフォーマンス評価

### Qwen3.5-27B-FP8 on DGX Spark

| 指標 | 値 |
| --- | --- |
| 生成速度 | ~7 tok/s |
| TTFT（キャッシュヒット時） | 0.5〜1.4秒 |
| TTFT（キャッシュミス時） | 10〜21秒 |
| メモリ使用量 | ~31 GiB（128GB中、約24%） |
| Thinking有効時の応答時間 | 数千トークン生成で数分 |
| REQUEST\_TIMEOUT | 600秒（Thinking長時間生成対応） |

### 実際の体感速度

* **単純なツール呼び出し**（Read/Glob等）: 5〜15秒。テンポよく作業できる
* **コード生成**（Write、200〜500トークン）: 30〜60秒。待てるレベル
* **計画・分析**（Thinking有効、1000〜3000トークン）: 2〜8分。最長リクエストは478秒（開発計画作成）

7 tok/sはNemotron-3-Nanoの40 tok/sと比べて大幅に遅いが、Thinking-onlyリトライの激減により**実効的な開発速度は大幅に向上**した。生成速度だけでなく、正しい出力を出す確率が重要だ。

---

## まとめ

DGX SparkのローカルLLM（Qwen3.5-27B-FP8）でClaude Codeを動かし、**家計簿Webアプリを約1時間で自律的に構築する**ことに成功した。

**うまくいったこと**

* Claude API ↔ OpenAI APIの双方向変換とストリーミング処理
* Rewriteモードによるフェーズ管理（計画→実装→検証→報告）
* Thinking Budget制御によるトークン消費の最適化
* Thinking-onlyリトライ（538回→1回に激減）
* Stall検出によるテキストのみ出力の自動リカバリ
* トークンInflationによるコンパクション制御
* プレフィックスキャッシュによるTTFT短縮
* Deferred Tool展開によるClaude Code最新版への対応
* パイプライン/フィルタパターンによる拡張性の確保

**学んだこと**

* 小型モデルでは生成速度よりも「正しい出力を出す確率」が全体の効率を左右する
* 61K文字のシステムプロンプトを小型モデルにそのまま渡すのは非効率。フェーズ別の軽量プロンプトに置き換えることで品質と速度の両方が向上する
* Thinkingの制御はフェーズ別Budget + 自動無効化 + リトライの3層防御が有効
* vLLMのreasoning parserでThinking/Content分離をサーバー側で行うのが確実
* プレフィックスキャッシュは巨大なシステムプロンプトの再処理を避けるために必須
* Claude Codeのバージョンアップ（Deferred Tool等）への追従がプロキシ開発の継続的な課題

**まだ課題なこと**

* 7 tok/sの生成速度。Thinking有効時は数分の待ち時間が発生する
* テストコードの自動生成（全Runで未達成）
* API URLのlocalhost固定（Vite proxy未使用）がテストプロジェクトの共通課題
* NVFP4量子化による高速化の可能性（GB10はBlackwell SM121a、FP4ネイティブ対応）

ソースコードはGitHubで公開しているので、DGX Sparkを持っている方は試してみてほしい。

<https://github.com/CaistsAI/claude-local-proxy>

**注意:** 本記事で紹介した構成は個人の実験的な取り組みであり、十分に検証されたものではない。Claude Code CLIの仕様変更やvLLMのアップデートにより動作しなくなる可能性もある。利用する場合は自己責任でお願いしたい。
