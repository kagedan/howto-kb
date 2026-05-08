---
id: "2026-05-07-code-with-claude-2026-完全解説-spacex提携とclaude-codeレート-01"
title: "Code with Claude 2026 完全解説 — SpaceX提携とClaude Codeレート制限2倍"
url: "https://qiita.com/kai_kou/items/ba88f403caf78fe5242b"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "qiita"]
date_published: "2026-05-07"
date_collected: "2026-05-08"
summary_by: "auto-rss"
---

![Code with Claude 2026 — SpaceX Colossus1提携とClaude Codeレート制限2倍を示すヒーロー画像](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/code-with-claude-2026-spacex-colossus-guide/01-hero-event-spacex.png)

## はじめに

2026年5月6日、AnthropicはサンフランシスコでClaude Codeユーザー向け開発者イベント「Code with Claude 2026」を開催しました。このイベントで発表された内容は、Claude Codeを利用する開発者にとって直接影響のある重大なアップデートを含んでいます。

### この記事で解説すること

- **SpaceX Colossus 1提携**の詳細と、Claudeのインフラ戦略の全貌
- **Claude Codeのレート制限変更**（2倍化・ピーク時間制限撤廃）の影響
- **Opus APIのレート制限増量**による開発者への恩恵
- **Code with Claude 2026**のその他の発表内容

### 対象読者

- Claude Code（Pro/Max/Team/Enterprise）のユーザー
- Claude APIを利用してアプリ・エージェントを構築している開発者
- Anthropicのインフラ戦略・ロードマップに関心のあるエンジニア

---

## TL;DR

- **SpaceX Colossus 1の全計算資源をAnthropicが利用開始**（NVIDIA GPU 22万台超、300MW以上）
- **Claude Code 5時間レート制限が全プランで2倍**（Pro/Max/Team/Enterprise）
- **Pro/Maxのピーク時間制限を完全撤廃**
- **Opus APIのレート制限も増量**
- Code with Claude 2026は**サンフランシスコ（5/6）・ロンドン（5/19）・東京（6/10）**の3都市開催

---

## SpaceX Colossus 1提携：2週間で220,000 GPUが追加

![Anthropicの計算資源ポートフォリオ — 各パートナーとの提携規模](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/code-with-claude-2026-spacex-colossus-guide/02-compute-portfolio-diagram.png)

### 提携の概要

Anthropicは2026年5月6日、SpaceXとの計算資源利用協定を発表しました。Anthropicは[Colossus 1データセンター](https://www.anthropic.com/news/higher-limits-spacex)の全計算資源へのアクセス権を取得しています。

**Colossus 1の仕様：**

| 項目 | 詳細 |
|------|------|
| GPU数 | 22万台以上 |
| GPU種別 | NVIDIA H100、H200、GB200 |
| 電力容量 | 300 MW以上 |
| 利用開始 | 協定締結から1ヶ月以内 |

ColossusはもともとxAI（Elon Muskが設立したAI企業、2026年2月にSpaceXが買収して子会社化）が構築したAIスーパーコンピュータです。xAIチームがColossus 2施設へ移行するタイミングで、AnthropicがColossus 1の全容量を引き継ぐ形となりました。

### Anthropicの既存計算資源ポートフォリオ

今回のSpaceX提携は、Anthropicが進めてきた大規模な計算資源確保戦略の一環です。[公式発表](https://www.anthropic.com/news/higher-limits-spacex)によると、既存のインフラパートナーシップは以下の通りです：

| パートナー | 規模 |
|-----------|------|
| Amazon（AWS） | 最大 5 GW |
| Google + Broadcom | 5 GW |
| Microsoft + NVIDIA | $300億 Azure容量 |
| Fluidstack | $500億（AnthropicのUSインフラ整備計画のパートナー） |
| SpaceX（今回） | 300 MW以上（22万台GPU） |

これだけの計算資源確保の背景には、2026年後半のIPO計画（CoinDeskが報道、6月）と、金融・医療・政府向けエンタープライズ展開のための国際的なデータレジデンシー対応があります。

### 将来の軌道上AI計算

発表の中でAnthropicは、SpaceXとの協力によって**数GW規模の軌道上AI計算資源**の開発を検討していると述べています。ただし、この計画は現時点では検討段階であり、具体的なタイムラインは示されていません。

---

## Claude Code：レート制限2倍とピーク時間制限撤廃

2026年5月6日より、Claude Codeのレート制限が大幅に緩和されました。

### 変更内容

**Claude Code 5時間レート制限（2倍化）：**

| プラン | 変更前 | 変更後 |
|--------|--------|--------|
| Pro | 通常制限 | 2倍 |
| Max | 通常制限 | 2倍 |
| Team | 通常制限 | 2倍 |
| Enterprise（シートベース） | 通常制限 | 2倍 |

具体的な上限値はプランによって異なるため、各自の[Claude Codeアカウント設定](https://claude.ai/settings)で確認することをお勧めします。

**ピーク時間制限の撤廃（Pro・Max）：**

これまでPro・Maxプランでは、混雑するピーク時間帯にClaudeへのアクセスが制限されていました。今回の変更でこの制限が完全に撤廃され、時間帯に関わらず安定したアクセスが可能になります。

### Opus APIのレート制限増量

Claude Code向けに加え、Opus APIのレート制限も増量されています。これにより、Opus 4.7を使ったエージェントの並列処理や長時間タスクがより実行しやすくなります。

---

## Code with Claude 2026：その他の発表内容

### Code Reviewの全社展開

Anthropicは**Code Review機能**を同社内の全チームで活用していることを明かしました。CI環境でのPR自動修正（CI auto-fix）機能と組み合わせることで、PRのバグ検出と自動修正が可能です。

### Claude Code CLIアップデート（v2.1.126〜v2.1.131）

イベントに合わせてClaude Code CLIも複数のアップデートが行われました：

- `--plugin-url` フラグを追加（URLで配布されたプラグインZIPを直接インストール可能）
- `skillOverrides` 設定が機能するように（`off`、`user-invocable-only`、`name-only`）
- `claude project purge` コマンドを追加（プロジェクトの完全削除）
- ローカルHEADからGitブランチを作成するよう変更
- Windows VS Code起動の問題を修正

### 金融サービスとMicrosoft 365

Code with Claude 2026では財務領域の発表も行われました：

- 10の金融サービスエージェントテンプレート（ピッチブック、KYCスクリーニング、損益計算など）
- Moody's MCPアプリ（6億社以上の信用格付けをClaudeから参照可能）
- Microsoft 365アドイン（Excel、PowerPoint、Word）のGA

これらの詳細は[Claude金融サービスエージェント入門（記事313）](/articles/313-claude-finance-agents-microsoft365-guide)、[Claude for Microsoft 365入門（記事312）](/articles/312-claude-microsoft365-office-suite-guide)でそれぞれ解説しています。

---

## 開発者への影響：実際に何が変わるか

### Claude Code利用者

**長時間エージェントタスクがより実行しやすくなる**ことが最大の変化です。これまでのレート制限では、大規模なリファクタリングや複数ファイルにわたる実装タスクが途中で止まるケースがありました。2倍のレート制限により、継続的な処理が可能になります。

また、ピーク時間制限の撤廃により、日本時間の午前中（米国西海岸の業務時間）もストレスなく利用できます。

### Opus API利用開発者

Opusのレート制限増量は、以下のユースケースで特に恩恵があります：

- **マルチエージェント並列処理**：複数Opusエージェントを同時実行するワークフロー
- **バッチ処理**：大量のドキュメント解析・変換タスク
- **長時間自律タスク**：数十ステップにわたるエージェントループ

### 展望：計算資源拡充がもたらすもの

22万台のGPUが新たに追加されることで、Anthropicは今後のモデル拡充とサービス安定性に余裕を持てます。Claude API・Claude Codeの安定性向上が期待されます。

---

## Code with Claude 2026 スケジュール

| 都市 | 日程 |
|------|------|
| サンフランシスコ（開催済） | 2026年5月6日 |
| ロンドン | 2026年5月19日 |
| 東京 | 2026年6月10日 |

バーチャル参加も可能です。詳細は[Anthropicの公式サイト](https://www.anthropic.com)で確認できます。

---

## まとめ

Code with Claude 2026 SFで発表された主要ポイントを整理します：

- **SpaceX Colossus 1の全計算資源**（22万台GPU、300MW以上）をAnthropicが利用開始（1ヶ月以内）
- **Claude Code 5時間制限を全プランで2倍**に拡大
- **Pro・Maxのピーク時間制限を撤廃**
- **Opus APIのレート制限を増量**
- 将来的な**軌道上AI計算資源**の開発も検討中

Claude Codeを日常的に使う開発者にとっては、ピーク時間制限の撤廃とレート制限2倍化は即日効果のある改善です。Anthropicの計算資源戦略の急拡大を背景に、今後もサービス品質の向上が期待されます。

## 参考リンク

- [Higher usage limits for Claude and a compute deal with SpaceX — Anthropic公式](https://www.anthropic.com/news/higher-limits-spacex) — レート制限変更の公式発表
- [Code with Claude SF 2026: What Anthropic Actually Shipped](https://blakecrosley.com/blog/code-with-claude-sf-2026-recap) — イベントレポート
- [Anthropic to use all of SpaceX-xAI's Colossus 1 data center compute — Data Center Dynamics](https://www.datacenterdynamics.com/en/news/anthropic-to-use-all-of-spacex-xais-colossus-1-data-center-compute/) — Colossus 1の技術詳細
