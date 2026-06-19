---
id: "2026-06-17-hermes-agentを読み解く-nousresearch本家とzapabob-forkの設計比較-01"
title: "Hermes Agentを読み解く — NousResearch本家とzapabob forkの設計比較"
url: "https://zenn.dev/zapabob/articles/hermes-agent-nous-vs-zapabob-fork"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "LLM"]
date_published: "2026-06-17"
date_collected: "2026-06-19"
summary_by: "auto-rss"
query: ""
---

2026年に入って、オープンソースの自律エージェントの話題で名前がよく出るのが **Hermes Agent** だ。Nous Research が MIT で公開しているフレームワークで、CLI・メッセージング Gateway・デスクトップアプリを同じエージェントコアで回し、**スキルとメモリでセッションをまたいで賢くなる** 設計が売りになっている。

一方、自分のマシンでは [zapabob/hermes-agent](https://github.com/zapabob/hermes-agent) という fork を触っている。本家 [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) をベースに、**Windows 常駐ワークステーション向けの運用レイヤー** が載っている。

この記事では、公式ドキュメントと両リポジトリの README・`AGENTS.md`・プラグイン構成を読んだうえで、エンジニア目線の比較メモを残す。インストール手順の写経ではなく、「どこが同じで、どこが分岐するか」に焦点を当てる。

## Hermes Agent とは何か

ひとことで言うと、**ターミナルとチャットアプリに住む、ツール呼び出し付きの個人用エージェント** だ。

Claude Code や Codex が IDE に寄っているのに対し、Hermes は次のような立ち位置になる。

* **ホストは自分のマシンや VPS** — ラップトップに縛られない
* **入口は CLI と Gateway** — Telegram、Discord、Slack など 20 以上のプラットフォームから同じエージェントに話しかけられる
* **モデルは差し替え自由** — Nous Portal、OpenRouter、OpenAI、Anthropic、ローカル llama.cpp など
* **学習ループが製品機能** — うまくいった手順を Skill（`SKILL.md`）として残し、メモリと組み合わせて再利用する

公式サイトの [Architecture](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture) を読むと、内部はかなり整理されている。中心は `AIAgent`（`run_agent.py`）で、周辺に Prompt Builder、Provider 解決、Tool Dispatch、SQLite + FTS5 のセッションストレージが並ぶ。CLI・Gateway・ACP（エディタ連携）・Cron は **同じコア** を共有する。

エンジニアが最初に押さえるべき設計原則は、ドキュメントにも `AGENTS.md` にも繰り返し出てくる次の2つだ。

1. **会話中のプロンプトキャッシュは神聖** — システムプロンプトやツールセットを途中で変えると、キャッシュが壊れてコストが跳ねる（例外はコンテキスト圧縮）
2. **コアは細い腰（narrow waist）** — 新しい能力は CLI + Skill、プラグイン、MCP に寄せ、コアの model tool スキーマは増やしすぎない

これは「機能を足すな」という意味ではない。**製品の表面（プラットフォーム、チャンネル、デスクトップ UI）は積極的に広げるが、毎ターン API に載るツール定義は慎重に**、というバランスだ。

## 本家の強み — なぜ注目されるか

### 閉ループの学習

公式が強調するのは **closed learning loop** だ。

* 複雑なタスクのあと、エージェントが Skill を自動生成する
* 使用中に Skill を改善する
* FTS5 で過去セッションを検索し、LLM で要約して横断 recall する
* Honcho などのメモリバックエンドでユーザーモデルを深める

Skill 形式は [agentskills.io](https://agentskills.io) 準拠で、Codex や Cursor の Skill エコシステムとも親和性が高い。ポータブルな手順書としてディスクに残るのは、エンジニアにとって扱いやすい。

### Gateway と Cron

`hermes gateway` は長寿命プロセスで、プラットフォームアダプタがメッセージを `AIAgent` に流し、応答を返す。Cron は **シェルタスクではなくエージェントタスク** — 自然言語のジョブ定義を任意のチャンネルに配信できる。

「夜中にレポートを Telegram に送れ」は、スクリプト cron より宣言的で、失敗時の文脈もエージェント側に残りやすい。

### ツールと実行環境

70 以上のツール、28 前後の toolset、ターミナル 6 バックエンド（local / Docker / SSH / Daytona / Modal / Singularity）、MCP 動的接続、サブエージェントの `delegate_task`、`execute_code` によるパイプライン圧縮。

研究用途では trajectory エクスポートや RL 連携（Atropos）まで言及がある。モデル屋が作ったエージェント.harness という印象が強い。

### 開発者向けの入口

* ドキュメント: <https://hermes-agent.nousresearch.com/docs/>
* LLM 向け索引: `/llms.txt`（約 17KB）、`/llms-full.txt`（全文連結）
* テスト規模: アーキテクチャページでは pytest が約 25,000 テストと記載
* インストール: `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`（Windows ネイティブも PowerShell ワンライナーあり）

本家の `plugins/` には、memory、context\_engine、kanban、spotify、teams\_pipeline など **汎用寄りの公式プラグイン** が置かれている。fork 固有の AITuber や X 投稿系はここにはない。

## zapabob fork とは何か

[zapabob/hermes-agent](https://github.com/zapabob/hermes-agent) は 2026年3月に fork されたリポジトリで、2026年6月時点では本家 `main` に対し **331 コミット先行・16 コミット遅れ** という規模感だった（`gh api compare` の結果）。

README の冒頭がはっきりしている。

> **常時稼働する Windows ワークステーション**向けの運用レイヤーを載せた fork

マーケティング用の汎用 README ではなく、**この checkout に入っている独自機能の索引** として書かれている。正直、この誠実さは好きだ。fork を「本家のミラー」だと思って clone すると、README の長さと `plugins/` の中身でギャップに気づく。

### fork だけのプラグイン例

本家の `plugins/` 一覧と比較すると、fork 側にだけ見える（または大幅に拡張された）領域がある。

| プラグイン | ざっくり役割 |
| --- | --- |
| `aituber_onair` | AITuber OnAir / FBX・VRoid 配信、TTS、YouTube 準備 |
| `lm-twitterer` | Hermes 生成 + X cookie 投稿、はくあ署名、cron 連携 |
| `notebooklm` | 実装ログ収集、NotebookLM 向けソース、投稿案ブレスト |
| `surfsense` | ナレッジベース + 動画パイプライン（Manim、HeyGen、HyperFrames 等） |
| `irodori_tts` | 音声合成パイプライン |
| `google_colab` | Colab 連携 |
| `questframe_fh6vr` | Quest / VR 周辺 |
| `unsloth_studio` | 学習・チューニング周辺 |
| `openclaw-vendor` | OpenClaw 資産の取り込み |
| `plugin_doctor` | プラグイン診断 |
| `memory/ebbinghaus` | エビングハウス曲線ベースのローカル SQLite メモリ |

本家にも `plugins/memory/` はあるが、fork では **Ebbinghaus 忘却曲線** を明示的な Memory Provider として実装している。Codex 側の `human-memory-emulation` スキルがこのパスを参照する、という連携も個人環境では自然だ。

### 運用面の差分（README から）

fork の README が詳しく書いているのは、クラウド推論とローカル fallback の **二段構え** だ。

**OpenCode Zen `auto-free`**

* 仮想モデル `auto-free` で無料カタログをローテーション
* レート制限時は次候補へ
* `fallback_providers` で llama.cpp に落とす

**Local Secretary（RTX 3060 想定）**

* llama.cpp OpenAI 互換 API（`:8080`）
* `--jinja` 必須（tool calling 契約）
* コンテキスト目標 65536
* **書き込み系は確認ゲート**（X 投稿、メール、カレンダー変更、シェル等）

ここがエンジニア向けに重要だ。エージェントに「常時フル権限」ではなく、**読み取りは自動・破壊的操作は人間承認** をコード（`agent/local_secretary/write_action_gate.py`）で切っている。本家の Security ドキュメントの精神と一致するが、fork は **自分の GPU と秘書用途に合わせて具体化** している。

**Windows 常駐**

* Task Scheduler で Gateway 自動起動
* UTF-8 / サブプロセス周りの修復
* `scripts/windows/start-hermes-llama-fallback-rtx3060.ps1` など GPU プロファイル別スクリプト

**兄弟リポ**

### CI の違い

fork には `.github/workflows/aituber-onair-plugin.yml` のように **個別プラグイン契約テスト** がある。本家の巨大 `tests.yml` に加え、運用で壊れやすいプラグインをパス限定で守る、という実務的な割り切りだ。

## 比較表 — どちらを選ぶか

| 観点 | NousResearch 本家 | zapabob fork |
| --- | --- | --- |
| **目的** | 汎用 OSS エージェント、コミュニティ拡大 | 1 台の Windows WS で 24/7 運用 |
| **追従** | 最新機能・リリースの正 | 本家 + 個人運用プラグイン（先行 300+ commits） |
| **モデル** | Portal / OpenRouter / 多数プロバイダ | 上記 + OpenCode Zen `auto-free` + llama ロールバック |
| **メモリ** | 公式 memory プラグイン、Honcho 等 | + Ebbinghaus SQLite、SurfSense 連携 |
| **出力チャネル** | 20+ Gateway プラットフォーム | 同上 + X（lm-twitterer）、AITuber、NotebookLM 集約 |
| **VR / 配信** | コミュニティ MCP（例: computer-use-linux） | aituber\_onair、questframe、VRChat ドクター文書 |
| **README** | 製品全体の入門 | fork 独自機能の索引（日本語セクションあり） |
| **貢献先** | 本家 PR | 基本は個人 fork；本家に戻せるものは cherry-pick |
| **リスク** | 更新が速い、issue も多い | 本家との merge 負債、個人 secret 前提の設定 |

**本家を選ぶべきとき**

* 初めて Hermes を試す
* コミュニティスキル Hub や公式 Desktop インストーラをそのまま使いたい
* 本家への PR を出したい
* Linux / macOS / VPS が主戦場

**fork を選ぶべきとき**

* Windows で Gateway + ローカル llama + Telegram を常時回す
* X 自動投稿、NotebookLM、AITuber、VRChat など **個人メディア運用** が主目的
* OpenCode Zen 無料枠と GPU fallback の組み合わせを既に使っている
* 本家にまだないプラグインに依存している

## アーキテクチャは同じ — 差分は「縁」

両方とも `run_agent.py` の `AIAgent`、同じ Gateway モデル、同じ Skill 規約を共有する。fork の `AGENTS.md` も本家と同型で、**prompt caching sacred** と **narrow waist** が冒頭に置かれている。

つまり比較の軸は「別フレームワークかどうか」ではなく、**同じハーネスの上に載せたプラグインと運用スクリプトが違う** という理解でよい。

```
                    ┌─────────────────────────┐
                    │   AIAgent (共通コア)     │
                    │  prompt / tools / session│
                    └───────────┬─────────────┘
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
   本家 plugins          fork 追加 plugins      ~/.hermes/config
   memory, kanban…       aituber, lm-twitterer…  auto-free, fallback
          │                     │                     │
          └─────────────────────┴─────────────────────┘
                              ▼
                    Gateway / CLI / Desktop / Cron
```

エージェント設計の授業として読むなら、Hermes は **「コアを薄く保ち、能力をプラグインと Skill に逃がす」** 良い見本だ。fork はその原則を守ったまま、**個人の生活圏（SNS、配信、ノート、GPU）に合わせたプラグイン群** を増やしている。

## Codex / Cursor ユーザーとの接点

Hermes は Claude Code や Codex の **代替というより隣人** だ。同じ Skill 形式、同じ「手順をファイルに残す」思想。

個人環境では次のような棲み分けが現実的だ。

| ツール | 向いている仕事 |
| --- | --- |
| **Codex / Cursor** | リポジトリ編集、PR、CI、IDE 統合 |
| **Hermes Gateway** | 移動中の Telegram、定期 cron、マルチチャネル |
| **Hermes ローカル秘書** | プライベートメモ、読み取り中心の調査、GPU 上の無料推論 |
| **fork プラグイン** | X 投稿案、NotebookLM 同期、配信キュー |

Hermes には MCP サーバー（`mcp_serve.py`）もあり、Cursor から会話・メッセージを扱う MCP ツール（`conversations_list` など）と接続できる。 **「エディタでコード、Hermes で常駐オペレーション」** は競合ではなく二層になる。

本書 [OpenAI Codex実践設計入門](https://zenn.dev/zapabob/books/openai-codex-design-book) で扱っている AGENTS.md・MCP・CI の話は、Hermes 側では `AGENTS.md`（リポジトリ）、`SOUL.md`（人格）、`~/.hermes/config.yaml`（実行設定）に分散する。名前は違うが、**コンテキストをファイルで固定する** 発想は同じ家族だ。

## 実務メモ — fork を本家に近づけ続ける

fork を長く使うなら、次の3つだけ意識した。

1. **本家の遅れ（behind）を定期的に確認** — 16 commits behind なら、セキュリティや Gateway 修正を取りこぼす可能性がある
2. **プラグインは `hermes plugins` で明示的に enable** — fork 固有機能はデフォルト OFF のことが多い
3. **秘密は `~/.hermes/.env` のみ** — README も警告しているが、UTF-8 BOM でキーが読めない事故は Windows あるある

本家へ還流できる改善（Windows PTY、Gateway UTF-8、write gate パターン）は cherry-pick 可能な単位でコミットしておくと、後の merge が楽になる。fork の `AGENTS.md` も「Contributor credit preserved」と書いており、履歴を残す文化と一致する。

## おわりに

Hermes Agent は、2026年時点で **「個人用エージェント OS」** に最も近い OSS のひとつだと思う。学習ループ、Gateway、Skill 標準、MCP、Cron が一つの製品として揃っている。

[zapabob/hermes-agent](https://github.com/zapabob/hermes-agent) は、その上に **Windows ワークステーション運用** という厚いレイヤーを載せた実験場だ。本家の地図を読んだうえで fork の README を索引として使うと、迷子になりにくい。

初めてなら本家の [Quickstart](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart) から。すでに Codex で AGENTS.md や Skill を育てているなら、Hermes は **同じ手順書を Telegram 越しに実行する別プロセス** として試す価値がある。

エージェントを増やすほど、大切なのはモデルの賢さより **どこにコンテキストを書き、どこで権限を切るか** だ。Hermes はその問いに、かなりはっきり答えを出している。

## 参考リンク
