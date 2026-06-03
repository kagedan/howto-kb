---
id: "2026-06-03-ai-daily-digest-2026年6月3日-microsoft-build-maiモデルnv-01"
title: "AI Daily Digest: 2026年6月3日 — Microsoft Build MAIモデル、NVIDIA Cosmos 3、Claude Code Dynamic Workflows"
url: "https://qiita.com/lhjjjk4/items/8d588043ac49614b6cb1"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "OpenAI", "Gemini", "GPT"]
date_published: "2026-06-03"
date_collected: "2026-06-03"
summary_by: "auto-rss"
query: ""
---

![Cover](https://files.catbox.moe/d64m8q.png)

> **5分で読める** · AIシステムアーキテクトが毎日厳選
> *注力分野: AIコーディング基盤 · エージェントインフラ · 物理AI*

---

## 1. Microsoft Build 2026: MAIモデルファミリー + Project Polaris 発表

**【技術コア】**
Microsoft は Build 2026（6月2〜3日、サンフランシスコ）で、完全自社開発の AI コーディングモデル「Project Polaris」を発表した。MoE（Mixture-of-Experts）アーキテクチャを採用し、言語別に特化したサブモジュールを搭載。2026年8月より、GitHub Copilot の全サブスクライバーに対して GPT-4 Turbo に代わるデフォルトエンジンとして展開される。Azure の自社 Maia AI アクセラレータ上で動作し、Pro ティアでは最大10万行のマルチファイルコンテキストをサポート。HumanEval および MBPP ベンチマークで GPT-4 Turbo を上回り、特に Rust と Haskell で最大の改善を示したとされる。

**【なぜ注目すべきか】**
Microsoft が OpenAI への依存から最も決定的な一歩を踏み出した瞬間だ。モデル、推論インフラ、開発者体験をエンドツーエンドで掌握することで、OpenAI と Copilot の商業的に微妙な関係が解消される。MAI ファミリーには画像生成、多言語音声合成、文字起こしモデルも含まれ、Microsoft 製品全体で OpenAI モデルを置き換える協調的な動きだ。

🔗 [Microsoft Build 2026: MAI Keynote Transcript](https://microsoft.ai/news/microsoft-build-2026-mai-keynote-transcript/) · [GitHub Copilot Replaces GPT-4 (TechTimes)](https://www.techtimes.com/articles/317596/20260602/github-copilot-replaces-gpt-4-project-polaris-ships-multi-agent-vs-code-build.htm)

---

## 2. NVIDIA Cosmos 3 + Isaac GR00T: 初の完全オープン物理AIスタック

**【技術コア】**
NVIDIA は5月31日、物理AI向け初の「オムニモデル」Cosmos 3 をリリースした。20兆マルチモーダルトークンで学習された MoT（Mixture-of-Transformers）アーキテクチャを採用し、Reasoner と Generator の2つのトランスフォーマーが連携。テキスト・画像・動画・環境音・アクションシーケンス（関節角度、グリッパー位置、軌道ウェイポイント）の5モダリティを入力・出力の両方でネイティブ処理する。Nano（16B）、Super（64B）、Edge（2B、未定）の3バリアントが OpenMDW 1.1 商用ライセンスで提供される。同時に、Isaac GR00T リファレンス人型ロボット（75自由度、Jetson AGX Thor T5000、Sharpa Wave 触覚ハンド）がオープンハードウェアプラットフォームとして発表され、Unitree が製造を担当、2026年後半に出荷予定。

**【なぜ注目すべきか】**
Cosmos 3 は、これまで別々だった言語モデル・動画生成・ロボットポリシーを単一アーキテクチャに統合した。テキストプロンプト → 5秒動画 → 関節軌道 というフルチェーン能力は、単一モデルでの推論・シミュレーション・物理実行を意味する。Stanford、ETH Zurich、Ai2 などの学術パートナーとオープンライセンスにより、NVIDIA は「2027年半ばまでにロボティクススタートアップが GR00T 上に構築する姿は、今日の AI スタートアップが CUDA 上に構築する姿と同じ」という賭けに出ている。

🔗 [NVIDIA Cosmos 3 + Isaac GR00T: Full Review (BuildFastWithAI)](https://www.buildfastwithai.com/blogs/nvidia-cosmos-3-isaac-groot-physical-ai-2026) · [NVIDIA Isaac GR00T Developer Page](https://developer.nvidia.com/isaac/gr00t)

---

## 3. Claude Code v2.1.154–160: Dynamic Workflows、6日間で7バージョン

**【技術コア】**
Anthropic は5月28日から6月2日までの6日間で、Claude Code の7バージョンをリリースした。中心は v2.1.154（Opus 4.8 + Dynamic Workflows のローンチ）。Dynamic Workflows は、単一プロンプトから数十〜数百の並列バックグラウンドエージェントを生成するオーケストレーションパターンを定義可能で、`/workflows` で実行状況を可視化できる。その他の注目点：自動モードが Bedrock / Vertex / Foundry に対応（v2.1.158）、`.claude/skills` ディレクトリからのプラグイン自動読み込み（v2.1.157）、OTEL リソース属性によるチーム別使用量分析（v2.1.160）、リーンシステムプロンプトが Haiku / Sonnet / Opus 4.7 を除く全モデルでデフォルト化。

**【なぜ注目すべきか】**
6日間で7バージョン —— この速度自体が Anthropic の継続的デリバリーへの移行を示している。Dynamic Workflows はマルチエージェントオーケストレーションのギャップに直接応えるものだ。Opus 4.8 の2.5倍高速モードとクロスクラウド自動モードの組み合わせにより、Claude Code は単なるツールからプラットフォームインフラへと進化している。

🔗 [Claude Code Changelog (gradually.ai)](https://www.gradually.ai/en/changelogs/claude-code/) · [Claude Code Official Changelog](https://code.claude.com/docs/en/changelog)

---

## 4. GitHub Copilot マルチエージェント GA + Copilot Workspace Fleet/Autopilot

**【技術コア】**
Build 2026 で、GitHub は VS Code 向け Copilot マルチエージェントサポートを発表。オーケストレーターエージェントがリンティング、テスト生成、ドキュメンテーション、セキュリティレビュー用の並列サブエージェントを起動する。Copilot Workspace はベータを終了し一般提供開始。Fleet モード（確認不要の自律CLIタスク）、Autopilot モード（スケジュールされた無人実行）、Jira / Datadog / ServiceNow 向け Copilot Extensions が追加された。2026年7月には、Enterprise 向け自律エージェントモード（機能ブランチ全体の作成・テスト・コミット）とエージェントサンドボックス（タスクごとの一時Linuxコンテナ）が予定されている。

**【なぜ注目すべきか】**
AI支援コーディングとAI委任コーディングの境界が消えつつある。人間が意図を定義し、エージェントが実行するソフトウェアエンジニアリングの予告編だ。

🔗 [Microsoft Build 2026 Recap (ChatForest)](https://chatforest.com/builders-log/microsoft-build-2026-recap-windows-agent-platform-project-polaris-copilot-workspace/)

---

## 5. Windows Agent Framework MITライセンス化 + Agent Store 85% 収益分配

**【技術コア】**
Microsoft は Build 2026 で Windows Agent Framework（WAF）v1.0 を MIT ライセンスでオープンソース化した。エージェントは YAML で定義され、同一マニフェストがローカルPC、Windows 365 Cloud PC、Azure サービスで動作する。Windows Agent Runtime（プレビュー、2026年6月）はエージェントをOSのファーストクラス市民とするネイティブAPIを提供。Windows Agent Store は開発者に85%の収益分配を保証。Adobe（InDesignテンプレート自動準備エージェント）や Zoom（会議参加＋要約の Microsoft Planner 連携エージェント）がデザインパートナーとして参加。

**【なぜ注目すべきか】**
WAF の MIT ライセンスは、Azure 外でのフォークと展開を可能にする戦略的布石だ。3層アーキテクチャ（WAF → Runtime → Store）は、自律ソフトウェア向けの App Store 的瞬間を Microsoft にもたらす。

🔗 [Windows Agent Framework (ChatForest)](https://chatforest.com/builders-log/microsoft-build-2026-recap-windows-agent-platform-project-polaris-copilot-workspace/)

---

## 6. OpenAI Codex Sites: Codex 内で Web サイト構築・デプロイ

**【技術コア】**
OpenAI は6月2日、Codex アプリ内で Web プロジェクトを作成・保存・デプロイ・検証できる Sites をローンチした。Webサイト、ダッシュボード、社内ツール、Webアプリに対応し、すべて OpenAI がホスティングする。v0.136.0（6月1日）ではセッションアーカイブ（`/archive`）、TUI マークダウンリンク処理、Windows サンドボックスプロビジョニング（`codex sandbox setup --elevated`）、Python SDK ベータ（`pip install openai-codex`）が追加された。ChatGPT Business/Enterprise ワークスペース向けに RBAC もサポート。

**【なぜ注目すべきか】**
Sites により Codex は AI コーディングエージェントから、開発〜デプロイまでのフルプラットフォームへと拡張された。セッションアーカイブと Python SDK の組み合わせで、OpenAI は永続的エージェントワークスペースのインフラを構築しつつある —— Replit、Vercel、GitHub Codespaces との直接競合だ。

🔗 [Codex Updates June 2026 (Releasebot)](https://releasebot.io/updates/openai/codex) · [OpenAI Codex Releases (GitHub)](https://github.com/openai/codex/releases)

---

## 7. Gemini 3.5 Pro: 6月 GA 確定、Vertex AI ホワイトリスト公開

**【技術コア】**
Google は Gemini 3.5 Pro の2026年6月一般提供を確定した（Flash は5月20日の Google I/O でローンチ済み）。内部ベンチマークでは GPQA 90%超、SWE-bench Pro 65%超を目標としており、フロンティア級のエージェント推論モデルとして位置づけられる。Vertex AI では早期企業導入者向けのホワイトリストアクセスが開始されている。

**【なぜ注目すべきか】**
2026年6月の AI モデル競争は3つの戦線で激化している：Microsoft の MAI ファミリー（垂直統合・自社開発）、Anthropic の Opus 4.8（継続的デリバリー）、Google の Gemini 3.5 Pro（エコシステムバンドル）。勝者は単体で最強のモデルではなく、最も強力なエージェントランタイムと配信力を持つプレイヤーとなるだろう。

🔗 [Gemini 3.5 Complete Guide (Codersera)](https://codersera.com/blog/gemini-3-5-complete-guide-2026/) · [Google Gemini 3.5 Official (The Keyword)](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-5/)
