---
id: "2026-04-13-claude-cowork-ga入門-rbacopentelemetryzoom-mcp完全ガイド-01"
title: "Claude Cowork GA入門 — RBAC・OpenTelemetry・Zoom MCP完全ガイド"
url: "https://qiita.com/kai_kou/items/2d902b97012815564b4f"
source: "qiita"
category: "cowork"
tags: ["MCP", "qiita"]
date_published: "2026-04-13"
date_collected: "2026-04-14"
summary_by: "auto-rss"
---

## はじめに

2026年4月9日、Anthropicは **Claude Cowork** をリサーチプレビューからGeneral Availability（GA）に移行させると同時に、組織向けの6つのエンタープライズ機能を発表しました。

[公式ブログ「Making Claude Cowork ready for enterprise」](https://claude.com/blog/cowork-for-enterprise) によれば、Claude CoworkはPro/Team/Enterpriseの全有料プランで利用可能になっています。

### この記事で学べること

* Claude Cowork GAで追加された6つのエンタープライズ機能の詳細
* RBAC・Group Spend Limits・Usage Analyticsによる組織展開の設計方法
* OpenTelemetryによる監査・可観測性の構成
* Zoom MCPコネクターとPer-Tool Connector Controls の活用
* Plugin Marketplaceと Sandbox構成のベストプラクティス
* 監査ログの制限と回避策

### 対象読者

* 組織にClaude Coworkを展開しようとしているエンジニア・IT管理者
* AIエージェントのセキュリティ・監査要件に取り組んでいる方
* Claude APIの運用管理を担当している方

---

## TL;DR

* Claude Coworkが2026-04-09にGAへ移行。Pro/Team/Enterprise全有料プランで利用可能
* 6つのエンタープライズ機能追加: RBAC・Group Spend Limits・Usage Analytics・OpenTelemetry・Zoom MCP・Per-Tool Controls
* Cowork活動はAudit Logs/Compliance APIに**記録されない**→ OpenTelemetryでSIEM連携が必須
* Plugin管理は4ティア配布制御（Required/Available/Installed by default/Not available）でITポリシー準拠

---

## GA移行で何が変わったか

Claude Coworkはもともと2026年1月のリサーチプレビューとして登場したデスクトップAIエージェントです。GAへの移行とともに、以下が確定しました。

| 項目 | リサーチプレビュー | GA |
| --- | --- | --- |
| 対象プラン | Pro/Max/Team/Enterprise（招待制） | Pro/Max/Team/Enterprise（全有料プラン） |
| エンタープライズ機能 | なし | 6機能追加 |
| Sandbox設定 | 基本設定のみ | VM強制実行オプション追加 |
| Plugin管理 | 基本カタログ | 4ティア配布制御 |

> ソース: [Claude Help Center — Use Claude Cowork on Team and Enterprise plans](https://support.claude.com/en/articles/13455879-use-claude-cowork-on-team-and-enterprise-plans)（2026年4月9日）

---

## 6つのエンタープライズ機能

### 1. Role-Based Access Controls（RBAC）

管理者はユーザーをグループに整理し、各グループが使用できるClaude Capabilityをカスタムロールで定義できます。

**グループ管理の方法**:

1. アドミンコンソールで手動作成
2. SCIM（System for Cross-domain Identity Management）を使ってIdentity Provider（Okta、Microsoft Entra ID等）から自動同期

**ユースケース例**:

* 営業チーム: Web検索・メール作成コネクターのみ有効
* エンジニアチーム: コード実行・GitHub MCPを追加許可
* 管理職: 全機能+Zoom MCP（会議要約）を有効

```
組織管理画面 → Groups → グループ作成 → ロール割り当て → SCIM同期設定
```

> **Teamプランとの差異**: Teamプランの場合、RBAC（グループ単位の粒度制御）は利用不可です。組織全体のオン/オフ切り替えのみ対応しています。RBACはEnterpriseプラン専用機能です。

### 2. Group Spend Limits

チームごとに月次予算の上限を設定できます。アドミンコンソールの `Organization settings → Groups → Spend Limits` から設定可能です。

* 採用初期は小さく始め、実際の利用パターンを見ながら上限を調整する運用が推奨されています
* 上限到達時には管理者に通知が送信されます

### 3. Usage Analytics

Cowork利用状況をAdminダッシュボードとAnalytics APIで確認できます。

**Admin Dashboard で確認できるメトリクス**:

* 日付範囲指定でCoworkセッション数・アクティブユーザー数を確認
* スキル呼び出し回数、コネクター利用回数

**Analytics API で取得できるデータ**:

* ユーザー単位のCowork活動量
* スキル・コネクター別の呼び出し数
* DAU/WAU/MAU（Chatおよびclaude-code使用量と並列取得可能）

> Analytics APIの詳細なエンドポイント・パラメーター仕様は [Claude Enterprise Analytics API リファレンス](https://support.claude.com/en/articles/13703965-claude-enterprise-analytics-api-reference-guide) を参照してください。

### 4. OpenTelemetry Support（Team・Enterpriseプラン）

Claude CoworkはOpenTelemetry準拠のイベントをエミットするようになりました。これにより企業の既存の可観測性基盤へ統合できます。

**エミットされるイベント種別**:

| イベント | 説明 |
| --- | --- |
| `tool_call` | MCPツール・ビルトインツールの呼び出し |
| `connector_invoke` | コネクター（Gmail、GitHub等）の呼び出し |
| `file_read` / `file_modified` | ファイルの読み書き操作 |
| `action_approved` | AI起動アクションの承認（手動/自動） |

**SIEM連携**:

* Splunk、Criblなど標準的なSIEMパイプラインと互換
* ユーザー識別子がCompliance APIレコードと共通のため、Coworkイベントと他のAPIログを横断的に関連付けられます

> **重要な制限**: Claude Coworkの活動は **Audit Logs・Compliance API・Data Exportsには記録されません**。コンプライアンス要件がある組織では、OpenTelemetryによるSIEM連携を必ず構成してください。OpenTelemetryはAuditLogの代替ではなく補完手段です。

### 5. Zoom MCP Connector

Zoom MCP ConnectorによってZoomの会議情報をCoworkワークフローへ取り込めます。

**利用できる情報**:

* AI Companion による会議要約
* アクションアイテム一覧
* 会議トランスクリプト
* スマートレコーディング

**活用例**:

```
「先週の製品レビュー会議の決定事項をまとめて、Jira にタスクを登録して」
→ Coworkがトランスクリプト取得 → アクションアイテム抽出 → Jira MCPでチケット作成
```

### 6. Per-Tool Connector Controls

管理者はMCPコネクター内の特定アクションを組織全体で制限できます。

**設定例**:

| コネクター | 許可 | 禁止 |
| --- | --- | --- |
| Gmail | 読み取り・下書き作成 | 送信 |
| GitHub | リポジトリ閲覧・PR確認 | プッシュ・マージ |
| Google Drive | ファイル閲覧 | ファイル削除 |

この制御により、AIエージェントが組織の承認なしに外部システムへ書き込む「野良エージェント」リスクを低減できます。

---

## Plugin Marketplace — 4ティア配布制御

エンタープライズでは、管理者がPlugin配布を4つのティアで制御できます。

| ティア | 動作 | ユーザーの操作 |
| --- | --- | --- |
| **Installed by default** | 自動インストール | アンインストール可能 |
| **Available** | カタログに表示 | セルフサービスでインストール |
| **Required** | 自動インストール | アンインストール不可 |
| **Not available** | カタログに非表示 | インストール不可 |

グループ単位でプラグイン設定を変更できるため、部署ごとのAIツールポリシーを実現できます。

---

## Sandbox設定（Enterpriseプラン）

Enterpriseプランの管理者は、Coworkのサンドボックスがメンバーデバイス上でどのように実行されるかを設定できます。

**注意点**:

* **VM強制実行**: セキュリティ要件が高い組織向けに、全Cowork活動を仮想マシン（VM）内で実行するよう強制できます
* **ネットワークエグレス**: コード実行に対してのみ適用。Web検索ツールやMCPへのネットワークアクセスには適用されません
* **Web検索の無効化**: `Organization settings → Capabilities` からWebサーチツールをオフに設定可能

---

## 組織展開の推奨ステップ

1. **初期展開**: 1チームのみRBACグループを作成し、Coworkを有効化（選択的展開）
2. **OpenTelemetry設定**: SIEM連携を先に構成してから展開を広げる（後付け困難）
3. **Plugin審査**: 利用するコネクターをRequired/Availableの2ティアに整理
4. **Per-Tool Controls**: 最小権限原則に基づき、書き込み系アクションをデフォルト禁止
5. **Spend Limits設定**: 小さい上限から始め、実測値に基づいて調整

---

## まとめ

Claude Cowork GAで追加された6つのエンタープライズ機能により、組織での本番展開が現実的な選択肢になりました。特に以下の点が重要です。

* **OpenTelemetry連携は必須**: Audit Logsに記録されないという制限から、コンプライアンス要件のある組織はSIEM連携を構成する必要があります
* **Per-Tool Controlsで最小権限**: AIエージェントに与える権限を細粒度で制御し、書き込み系操作は明示的に許可制にする設計を推奨
* **SCIMによるRBACスケール**: 手動グループ管理はすぐに限界を迎えるため、IDプロバイダーとのSCIM連携を早期に設計する

Claude Coworkは「個人の生産性ツール」から「組織のAIエージェント基盤」へと本格移行しています。

## 参考リンク
