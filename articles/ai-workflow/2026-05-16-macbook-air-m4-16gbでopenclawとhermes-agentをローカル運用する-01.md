---
id: "2026-05-16-macbook-air-m4-16gbでopenclawとhermes-agentをローカル運用する-01"
title: "MacBook Air M4 16GBでOpenClawとHermes Agentをローカル運用するベストプラクティス"
url: "https://zenn.dev/sonder01/articles/macbook-air-m4-local-ai-agents"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "prompt-engineering", "API", "AI-agent", "LLM", "OpenAI"]
date_published: "2026-05-16"
date_collected: "2026-05-17"
summary_by: "auto-rss"
query: ""
---

MacBook Air M4 16GBでローカルAIエージェントを動かすとき、最初に決めるべきことは「全部ローカルLLMで完結させるか」ではなく、**どの権限をローカルに置き、どの推論を外部モデルに逃がすか**です。

M4 Airは軽い常駐エージェント、CLIエージェント、8B前後の量子化モデルには十分です。一方で、ブラウザ操作、ファイル編集、メッセージ連携、長いコンテキストを同時に走らせると、16GB unified memoryはすぐに狭くなります。

この記事では、OpenClawとHermes AgentをMacBook Air M4 16GBで安全に試し、日常運用に近づけるための構成をまとめます。

## 前提

調査時点は2026年5月16日です。対象は以下です。

* MacBook Air M4、16GB unified memory
* OpenClaw: 常駐Gateway型のパーソナルAIアシスタント
* Hermes Agent: Nous ResearchのCLI/TUI中心のAIエージェント
* ローカルLLM実行基盤: Ollama、llama.cpp、MLX/MLX-LM

「Hemes agent」と表記されることもありますが、この記事ではNous Researchの **Hermes Agent** を対象にします。

## 全体像

ローカルAIエージェントは「モデル」だけではありません。実際には、エージェントランタイム、ツール権限、メモリ、セッション、外部チャネル、サンドボックス、ログが一体になります。

M4 Air 16GBで安定させるには、モデルサイズより先に次の3点を決めます。

| 項目 | 推奨 |
| --- | --- |
| 通常チャット | 3B-9B級の量子化ローカルモデル |
| コード編集・ツール実行 | 強いAPIモデルを primary、ローカルモデルを fallback |
| shell/file/browser権限 | Dockerまたはワークスペース限定 |
| 常駐チャネル | 最初はTelegram/Slack等を1つだけ |
| 長時間自動化 | cron/automationは明示的に小さく始める |

## M4 Air 16GBで何が現実的か

Apple公式仕様では、M4 MacBook Airは16-core Neural Engine、120GB/s memory bandwidth、16GB unified memory構成を選べます。つまりCPU/GPU/Neural Engineが同じメモリプールを共有します。

この構造はローカルLLMに向いていますが、同時に「モデルの重み」「KV cache」「ブラウザ」「Docker」「エージェント本体」「普段のアプリ」が同じ16GBを取り合います。

実用ラインは次のように考えると安全です。

| 用途 | 目安 |
| --- | --- |
| 軽い会話、分類、要約 | 3B-8B、4bit量子化 |
| 日本語を含む日常作業 | 7B-9B、4bit/5bit量子化 |
| コーディング補助 | 7B-14Bの小さめ量子化。ただし長いrepo解析はAPIモデル推奨 |
| ブラウザ操作込みの自動化 | ローカルモデル単独より、APIモデル + sandbox推奨 |
| 70B級や長文高精度推論 | M4 Air 16GBの主戦場ではない |

OllamaはmacOSで簡単に導入でき、Ollama公式ドキュメントでもmacOS/Windows/Linux向けの導入とAPI利用が案内されています。よりApple Silicon寄りに詰めるなら、Apple ML ResearchのMLXも候補です。MLXはApple Silicon向けのNumPyライクな配列フレームワークで、CPU/GPU間コピーを避けやすい unified memory model を前提にしています。

## OpenClawの使いどころ

OpenClawは、自分のデバイス上で動かすパーソナルAIアシスタントです。公式READMEでは、Gatewayを制御面として、WhatsApp、Telegram、Slack、Discord、Google Chat、Signal、iMessage、LINEなど多数のチャネルに接続できることが説明されています。

OpenClawが向いているのは次の用途です。

* スマホやチャットアプリからローカルエージェントに話しかけたい
* Gatewayを常駐させ、メッセージ、スケジュール、ブラウザ、ファイル操作を連携したい
* 複数チャネルを後から増やしたい
* 個人アシスタントとして「いつも起きている」状態を作りたい

インストールはNode.jsが前提です。公式Getting StartedではNode 24推奨、Node 22.14+対応とされ、基本フローは次の通りです。

```
curl -fsSL https://openclaw.ai/install.sh | bash
openclaw onboard --install-daemon
openclaw gateway status
openclaw dashboard
```

ただし、M4 Airでいきなりフル権限・複数チャネル・ブラウザ操作まで開けるのは避けます。最初はローカルGateway、1チャネル、読み取り中心のツールから始めます。

OpenClawの公式セキュリティガイドは、1つのGatewayを敵対的な複数ユーザーの境界として扱わない方針を明示しています。つまり「同じGatewayに話しかけられる人」は、実質的に同じツール権限を誘導できると考えるべきです。

最初にやるべき設定はこれです。

```
openclaw security audit
openclaw security audit --deep
```

設定方針は次の通りです。

```
{
  "gateway": {
    "mode": "local",
    "bind": "loopback",
    "auth": {
      "mode": "token"
    }
  },
  "tools": {
    "fs": {
      "workspaceOnly": true
    },
    "exec": {
      "security": "deny",
      "ask": "always"
    },
    "elevated": {
      "enabled": false
    }
  }
}
```

OpenClawは便利ですが、ツールが強いぶん危険です。DMやグループチャットから命令できる構成では、`dmPolicy`をpairing/allowlistにし、グループではmention必須にします。

## Hermes Agentの使いどころ

Hermes Agentは、Nous ResearchのエージェントCLI/TUIです。公式READMEでは、CLI、メッセージングGateway、スキル、記憶、cron、MCP、複数バックエンド、OpenClawからの移行機能が説明されています。

Hermesが向いているのは次の用途です。

* ターミナルで開発・調査・ファイル作業を進めたい
* プロファイル単位でエージェントを分けたい
* Docker/SSH/Modal/Daytonaなど実行環境を切り替えたい
* スキルや記憶を育てながら使いたい
* OpenClawから設定やメモリを移行したい

導入は公式のクイックスタートに従います。

```
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
hermes setup
hermes doctor
hermes --tui
```

Hermesの設定は `~/.hermes/` に分かれて保存されます。公式ドキュメントでは、通常設定は `config.yaml`、APIキーやトークンは `.env`、記憶は `memories/`、スキルは `skills/`、ログは `logs/` と整理されています。

```
hermes config set model anthropic/claude-sonnet-4
hermes config set terminal.backend docker
hermes config set OPENROUTER_API_KEY sk-or-...
```

複数エージェントを同じMacで動かすなら、プロファイルを使います。

```
hermes profile create coder
coder setup
coder chat
```

プロファイルごとにconfig、APIキー、記憶、セッション、スキル、cronが分離されるため、個人用・開発用・調査用を混ぜずに済みます。

## 16GB Macでの推奨構成

### 1. まずはHermes CLIを開発用にする

最初の1週間はOpenClawよりHermesを先に入れるのが無難です。理由は、CLI中心で挙動を観察しやすく、危険なコマンド承認やDocker backendを設定しやすいからです。

```
hermes setup
hermes config set terminal.backend docker
hermes config set approvals.mode manual
hermes doctor
```

`--yolo` は使わないでください。公式セキュリティドキュメントでも、YOLO modeは危険コマンドの承認を無効化するため、信頼済みの使い捨て環境以外では避けるべき設定です。

### 2. OpenClawは「常駐・チャネル連携」用途に絞る

OpenClawは最初から全部やらせるより、常駐Gatewayとして使うのが合っています。

```
openclaw onboard --install-daemon
openclaw gateway status
openclaw security audit --deep
```

最初のチャネルは1つだけにします。TelegramやSlackなど、ユーザーIDとallowlistを確認しやすいものが扱いやすいです。

### 3. ローカルLLMはOllamaかMLX-LMで小さく始める

Ollamaは運用が簡単です。

```
curl -fsSL https://ollama.com/install.sh | sh
ollama run qwen3:8b
```

MLX-LMはApple Siliconに寄せて実験したい場合に向いています。

```
pip install mlx-lm
mlx_lm.generate --model mlx-community/Mistral-7B-Instruct-v0.3-4bit --prompt "hello"
```

16GBでは、ローカルモデルをprimaryにするより、次のような役割分担が現実的です。

| 役割 | 推奨モデル |
| --- | --- |
| 雑な分類・要約・下書き | ローカル小型モデル |
| shell実行やファイル変更を伴う作業 | APIの強いモデル |
| 個人情報を含むメモ整理 | ローカルモデル。ただし外部連携を切る |
| 長いrepo解析 | APIモデル、または対象ファイルを絞る |

### 4. Docker Desktopのメモリを絞る

HermesのDocker backendやOpen WebUIを使うと、Dockerがメモリを持っていきます。M4 Air 16GBでは、Docker DesktopのMemoryを4-6GB程度から始め、モデル実行はホスト側Ollamaに寄せる方が安定します。

Open WebUIを使う場合も、OllamaはMacホストで動かし、Web UIだけDockerで動かす構成にします。Open WebUI公式ドキュメントでも、OllamaとOpenAI互換APIをバックエンドとして使える構成が説明されています。

## セキュリティのベストプラクティス

ローカルAIエージェントは、チャットアプリからshell・ブラウザ・ファイルに触れる仕組みです。便利さではなく、先に境界を設計します。

### やること

* Gatewayは `localhost` / `loopback` bindから始める
* DMはpairingまたはallowlistにする
* グループではmention必須にする
* shell実行は `ask always` またはDocker backendにする
* file操作はworkspace限定にする
* APIキーは `.env` やSecrets管理に置き、記事やrepoに入れない
* agent用の専用OSユーザー、専用ブラウザプロファイルを使う
* 定期的に `openclaw security audit` と `hermes doctor` を走らせる

### やらないこと

* `--yolo` や自動承認を日常環境で使う
* 個人Google/Apple/パスワードマネージャにログイン済みのブラウザをagentに操作させる
* 複数人が触れるチャネルに広いshell/file権限を渡す
* 未確認のskills/pluginsをそのまま入れる
* `curl | sh` をagentに自動実行させる
* 70B級モデルを16GB Airの日常運用前提にする

## 実運用テンプレート

M4 Air 16GBでのおすすめはこの構成です。

```
MacBook Air M4 16GB
├─ Hermes Agent
│  ├─ profile: coder
│  ├─ terminal.backend: docker
│  ├─ approvals.mode: manual
│  └─ model: API strong model primary / local fallback
├─ OpenClaw
│  ├─ gateway: loopback
│  ├─ dmPolicy: pairing
│  ├─ tools: workspaceOnly + ask always
│  └─ channel: Telegram or Slack one at first
├─ Ollama or MLX-LM
│  └─ 3B-9B quantized local model
└─ Dedicated workspaces
   ├─ ~/agent-work/coder
   ├─ ~/agent-work/research
   └─ ~/agent-work/personal
```

OpenClawとHermesを同時に入れる場合、役割は分けます。

| ツール | 役割 |
| --- | --- |
| Hermes Agent | 開発、調査、CLI/TUI、プロファイル分離 |
| OpenClaw | 常駐Gateway、メッセージング、個人アシスタント |
| Ollama/MLX | 低コスト・ローカル推論 |
| APIモデル | 高精度・長文・ツール実行時の判断 |

## 最小セットアップ手順

```
# 1. ローカルLLM
curl -fsSL https://ollama.com/install.sh | sh
ollama run qwen3:8b

# 2. Hermes
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
hermes setup
hermes config set terminal.backend docker
hermes config set approvals.mode manual
hermes doctor

# 3. OpenClaw
curl -fsSL https://openclaw.ai/install.sh | bash
openclaw onboard --install-daemon
openclaw security audit --deep
openclaw dashboard
```

この状態で、最初に試すプロンプトは小さくします。

```
この作業ディレクトリを読み取り専用で確認し、主要ファイルを5個だけ列挙して。
ファイル変更やコマンド実行が必要なら、実行前に理由を説明して止まって。
```

いきなり「全部自動で直して」ではなく、読み取り、提案、限定実行の順に広げます。

## まとめ

MacBook Air M4 16GBは、ローカルAIエージェントの学習・日常実験には十分です。ただし、全部をローカルモデルに寄せるより、エージェントの実行面をローカルに置き、重要な推論は必要に応じて外部モデルへ逃がす方が安定します。

OpenClawは常駐Gatewayとメッセージング連携に強く、Hermes AgentはCLI/TUI、プロファイル、サンドボックス、開発作業に強いです。両方を同じMacに入れるなら、同じ仕事をさせるのではなく、OpenClawは「入口」、Hermesは「作業場」として分けると扱いやすくなります。

**ローカルAIエージェント構築の本質は、モデル選びではなく権限設計です。** M4 Air 16GBでは、小さく動かし、ログを見て、権限を一つずつ広げる運用が一番長続きします。

## 参考リンク
