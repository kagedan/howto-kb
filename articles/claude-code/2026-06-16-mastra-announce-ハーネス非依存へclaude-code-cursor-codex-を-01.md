---
id: "2026-06-16-mastra-announce-ハーネス非依存へclaude-code-cursor-codex-を-01"
title: "[Mastra Announce] ハーネス非依存へ、Claude Code / Cursor / Codex をサブエージェントとして統合"
url: "https://zenn.dev/shiromizuj/articles/7718a9a0f33b8b"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "OpenAI", "TypeScript"]
date_published: "2026-06-16"
date_collected: "2026-06-17"
summary_by: "auto-rss"
query: ""
---

# [Mastra Announce] ハーネス非依存へ、Claude Code / Cursor / Codex をサブエージェントとして統合

[Mastra](https://mastra.ai/) の[公式Blog](https://mastra.ai/blog)で発表された[Announcements](https://mastra.ai/blog/category/announcements)を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。速報性重視でAIの力を多分に使っているので、私自身の考察は少なめです。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

2026年6月15日、Mastra は **"Introducing Claude Code, Cursor, and Codex agents in Mastra"** を公開しました。

今回の発表を短く言うと、Mastra は「モデル非依存（model-agnostic）」からさらに進んで、**エージェント実行ハーネス非依存（harness-agnostic）** を明確に打ち出した、ということです。

つまり、Claude Code / Cursor / OpenAI Agents（Codex 含む）それぞれの SDK が持つランタイムや権限制御を活かしながら、Mastra 側では同じ呼び出し面（`generate`/`stream` など）・可観測性・ワークフロー統合で扱えるようになりました。

---

## 今回の発表をひとことで言うと

**「外部のコーディング系 Agent SDK を、Mastra の標準エージェント面に正規化して載せる機能」** です。

Mastra で SDK エージェントを使うと、見た目は通常の Mastra エージェントと同じように扱えます。

* 呼び出し: `.generate()` / `.stream()` / `.resumeGenerate()` / `.resumeStream()`
* 実行オプション: `requestContext` / `abortSignal` / `instructions` / `structuredOutput` / `runId` / `tracingContext`
* 合成: workflow step への組み込み、サブエージェント委譲、ツール併用
* 可観測性: Studio でのログ、トレース、トークン、推定コスト

一方で、実際の agent loop（実行ループ）やツール機構、権限モデルは各 SDK が引き続き担います。ここが重要です。Mastra が全部を置き換えるのではなく、**共通の実行インターフェースと観測レイヤを提供する**設計です。

---

## 背景: なぜ「ハーネス非依存」が必要だったのか

### 1) 現場で「どのモデルを使うか」より「どの実行系を使うか」が差別化要因になった

2025〜2026 の実務では、モデル選択だけでなく次の観点が実装体験を大きく左右します。

* ファイル編集・シェル実行・コードベース探索のしやすさ
* ツール呼び出しの表現力（MCP 連携含む）
* 権限昇格や許可フロー
* ストリーミング品質と中断・再開

これらは「モデル」よりも「ハーネス（SDK の実行系）」の差として現れます。Mastra が harness-agnostic を掲げたのは、まさにこの実務変化への対応です。

### 2) 単一ハーネス固定は、アプリの拡張性を下げやすい

プロダクトではしばしば、用途ごとに最適な実行系が異なります。

* 調査・コード読解中心: ある SDK が強い
* ツール連携・厳密な structured output: 別 SDK が強い
* リアルタイムの対話体験: さらに別の選択肢が有利

このときアプリ本体が特定 SDK 呼び出しに深く依存していると、差し替えコストが大きくなります。SDK Agents は、その依存を薄くするための中間層です。

---

## 何が追加されたのか（実装レベル）

公式 docs と PR の内容を合わせると、今回の追加点は次のとおりです。

### 対応 SDK とパッケージ

* Claude Agent SDK: `@mastra/claude` + `@anthropic-ai/claude-agent-sdk`（peer）
* Cursor Agent SDK: `@mastra/cursor` + `@cursor/sdk`（peer）
* OpenAI Agents SDK: `@mastra/openai` + `@openai/agents`（peer）

それぞれ `*SDKAgent` ラッパーを提供し、Mastra 側の `generate/stream` に合わせた形へ変換します。

### 既存 SDK インスタンスのラップに対応

`OpenAISDKAgent` / `CursorSDKAgent` などは、`sdkOptions` から内部生成するだけでなく、すでにアプリ側で作っている SDK agent を `agent` オプションで受け取れます。

これにより「既存資産を捨てず、Mastra 統合だけを追加する」導線が用意されています。

### 可観測性の統合が初手から入っている

PR #16906 / #17525 の要点として、単に「呼べる」だけでなく以下が強化されています。

* agent/model span の生成と関連付け
* SDK が提供する usage の正規化
* tool-call のトレース化
* Claude の `total_cost_usd` のような provider 側コスト情報の取り込み

「あとで observability を足す」のではなく、最初から計測可能な形で実装されているのが実務上の強みです。

---

## 既存手法との位置づけ

| アプローチ | 特徴 | 強み | 注意点 |
| --- | --- | --- | --- |
| 素の Mastra Agent のみ | モデルとツールを Mastra 側で統一管理 | シンプル・統一感が高い | 外部 SDK 固有機能は活かしづらい |
| 各 SDK を直接アプリに埋め込む | SDK 固有 API をそのまま利用 | 柔軟で機能を最大活用できる | SDK ごとに実装が分岐しやすい |
| **Mastra SDK Agents** | SDK 実行系を保持しつつ Mastra 面に接続 | 差し替えや混在がしやすい、観測を統一しやすい | SDK ごとの差異（例: structured output 可否）は理解が必要 |

特に最後の行がポイントです。**統一 API で扱えること**と、**各 SDK の完全同一挙動**は別物です。たとえば docs では Cursor SDK の TypeScript 実装事情により、structured output リクエスト時に明示的エラーになる旨も示されています。

---

## もう一歩深掘り: ACP / Supervisor / Code Mode との関係

今回の announcement は単発機能というより、6月前半の Mastra の流れにきれいにつながっています。

* ACP (`@mastra/acp`): 外部の ACP 互換コーディングエージェントを subagent/tool として利用
* Code Mode (`createCodeMode`): 既存ツールをその場生成コードで合成し multi-tool 計算を圧縮
* SDK Agents（今回）: Claude/Cursor/OpenAI の既存 SDK runtime を Mastra 面へ接続

この 3 つを並べると、Mastra が目指しているのは「単一の最強 runtime」を作ることではなく、**複数の runtime を同じオーケストレーション層で扱える状態**だと読み取れます。

---

## 実務でのうれしさ（利用シーン別）

### 1) 既存エージェント基盤の段階移行

すでに SDK ベースで動いている機能を急に書き換えず、`agent` オプションで包んで Mastra へ寄せられます。移行時のリスクが小さいです。

### 2) プロダクト内でのハーネス併用

同一アプリで「この領域は Claude SDK」「ここは OpenAI Agents SDK」のような併用をしつつ、運用ダッシュボードやトレース観察の入口を揃えられます。

### 3) 評価（eval）と運用（observability）の接続

announcement 本文にもあるとおり、SDK subagent を eval 対象にしつつ Studio で追えるため、「ベンチで良かったが本番で崩れる」を追跡しやすくなります。

---

## 導入時のチェックポイント

### 1. バージョン要件

* `@mastra/core@1.38.0` 以降が前提
* 各 SDK は peer dependency なので、対応版を明示的に入れる

### 2. API キー / 実行環境

* Claude: `ANTHROPIC_API_KEY`
* Cursor: `CURSOR_API_KEY`
* OpenAI: `OPENAI_API_KEY`

CI / Preview / Local でキー管理方法を揃えておくとトラブルが減ります。

### 3. structured output / resume の差分把握

`resumeGenerate` / `resumeStream` や structured output は「呼び出し面は共通」ですが、内部挙動や制約は SDK 依存です。運用前に対象 SDK の docs を必ず確認するのが安全です。

### 4. まずは観測設計を先に置く

導入初期は「動いた」で満足しがちですが、SDK 混在ほどトレース粒度が重要になります。Observability を有効化し、token/cost/latency を最初から見える化しておくのがおすすめです。

---

## まとめ

今回の SDK subagents 発表は、単なる「対応 SDK が増えた」ニュースではありません。Mastra が

1. モデル非依存を維持しつつ、
2. ハーネス非依存へ踏み込み、
3. そのうえで observability と workflow 合成を共通化する

という、プラットフォームとしての方向性を明確にしたアップデートです。

今後の実装では、「どのモデルか」だけでなく「どのハーネスで走らせるか」を場面ごとに最適化する設計が増えていくはずです。SDK Agents はそのための実務的な接着層で、Mastra を中心に据えたまま選択肢を広げられる点が大きな価値だと感じます。

---

## 参考リンク
