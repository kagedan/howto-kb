---
id: "2026-05-05-速報claude-securityが公開ベータ開始opus-47で脆弱性スキャンが人間のセキュリティ-01"
title: "【速報】Claude Securityが公開ベータ開始！Opus 4.7で脆弱性スキャンが「人間のセキュリティ研究者レベル」に"
url: "https://qiita.com/emi_ndk/items/15e6f0cdd57f03d8bcb0"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-05-05"
date_collected: "2026-05-06"
summary_by: "auto-rss"
---

## あなたのコードベース、本当に安全ですか？

**27年間気づかれなかったOpenBSDのバグ。**
**16年間テストを通過し続けたFFmpegの脆弱性。**

これらを発見したのは、人間ではありません。

Anthropicが5月4日に公開ベータを開始した「Claude Security」です。

---

## 結論から言うと...

- **Claude Security**が5月4日にEnterprise顧客向け公開ベータ開始
- **Opus 4.7**搭載で、従来ツールが見逃す「コンテキスト依存型」の脆弱性を検出
- 設定不要、APIなしで**claude.ai/security**から即使用可能
- CrowdStrike、Microsoft、Palo Alto Networksなど大手セキュリティ企業が採用決定

---

## 【衝撃】従来のセキュリティツールが見逃していた理由

従来の静的解析ツール（Snyk、SonarQube、Checkmarx等）は「パターンマッチング」で脆弱性を見つけます。

:::note warn
**問題点**: パターンマッチングは「既知のパターン」しか検出できない。ゼロデイ脆弱性や、ファイル間でデータが流れる複雑な脆弱性は見逃す。
:::

Claude Securityはアプローチが根本的に違います。

> **「Claude Securityは人間のセキュリティ研究者のようにコードを読む。ソースコードを読み、データフローを追跡し、ファイルやモジュール間でコンポーネントがどう相互作用するかを分析する」**
> — Anthropic公式ブログより

つまり**AIがコード全体を「理解」した上で**脆弱性を探すのです。

---

## 【実践】5分でできる！Claude Securityの使い方

### 1. アクセス方法

Enterpriseプラン加入者は、管理コンソールから機能を有効化。

```
claude.ai/security
```

または、Claude.aiのサイドバーから直接アクセス可能。

### 2. スキャン手順

1. リポジトリを選択（GitHub連携済みなら自動表示）
2. スキャン範囲を指定（全体 or 特定ディレクトリ）
3. 「Scan」をクリック

:::note alert
**注意**: 初回スキャンはコードベースのサイズによって時間がかかります。大規模リポジトリは夜間スケジュール実行がおすすめ。
:::

### 3. 結果の確認

検出された脆弱性には以下が含まれます：

- **深刻度レーティング**（Critical/High/Medium/Low）
- **信頼度スコア**
- **再現手順**
- **修正パッチ案**（コピペ可能）

### 4. 外部ツール連携

```bash
# Webhook連携例
- Slack通知
- Jira自動起票
- CSV/Markdownエクスポート
```

---

## 【背景】なぜ今、Anthropicがセキュリティに本気を出したのか

### Project Glasswing — $100M投入の超大型プロジェクト

4月7日、Anthropicは「Project Glasswing」を発表しました。

参加企業を見れば本気度がわかります：

| 企業 | 役割 |
|------|------|
| Amazon Web Services | クラウドインフラ |
| Apple | OSセキュリティ |
| Google | ブラウザ/Android |
| Microsoft | Windows/Azure |
| NVIDIA | GPU/ドライバ |
| CrowdStrike | EDR統合 |
| Palo Alto Networks | ネットワークセキュリティ |
| JPMorgan Chase | 金融システム |
| Linux Foundation | OSS調整 |

**12社の創業パートナー + 40以上の重要インフラ組織**が参加。

### Claude Mythos Preview — 「危険すぎて公開できない」AI

Project Glasswingの裏にあるのが「Claude Mythos Preview」です。

**ベンチマーク結果**:
- CyberGym脆弱性再現: **83.1%**（Opus 4.6は66.6%）
- SWE-bench Verified: **93.9%**（Opus 4.6は80.8%）

そして驚くべき発見実績：

:::note info
- **27年前のOpenBSDバグ** — リモートシステムクラッシュ可能
- **16年前のFFmpeg脆弱性** — 500万回のテストをすり抜けていた
- **複数のLinuxカーネル脆弱性** — 連鎖させて権限昇格可能
:::

> **「Mythosは完全に自律的に、人間の誘導なしで脆弱性を特定し、悪用コードを作成する」**
> — Anthropic red.anthropic.com

だからこそ**一般公開されていない**のです。

---

## 【比較】Claude Security vs 従来ツール

| 項目 | Claude Security | Snyk | SonarQube |
|------|-----------------|------|-----------|
| 検出方式 | AIコード理解 | パターン | パターン |
| ゼロデイ検出 | ✅ 可能 | ❌ 困難 | ❌ 困難 |
| パッチ生成 | ✅ 自動 | ⚠️ 限定的 | ❌ なし |
| 設定の複雑さ | シンプル | 中程度 | 複雑 |
| コンテキスト理解 | ✅ ファイル横断 | ❌ | ⚠️ 限定的 |

---

## 【実際に使った感想】ここがスゴい3つのポイント

### 1. パッチがそのまま使える

従来ツール「ここに脆弱性があります」で終わり。
Claude Security「この修正を適用してください + なぜこの修正が正しいか説明」。

```diff
// 修正前
- const query = `SELECT * FROM users WHERE id = ${userId}`;
+ const query = `SELECT * FROM users WHERE id = $1`;
+ const values = [userId];
```

### 2. 誤検出の却下理由が残る

「これは誤検出」とマークすると、**却下理由が記録される**。
次にレビューする人が「なぜ無視されたか」を理解できる。

### 3. 定期スキャン + Slack通知

毎日深夜にスキャン → 新規脆弱性があればSlack通知。
CI/CDに組み込まなくても、**受動的にセキュリティ監視**できる。

---

## 【いつ使えるようになる？】提供スケジュール

| プラン | 状況 |
|--------|------|
| Enterprise | ✅ 公開ベータ中 |
| Team | 🔜 近日提供予定 |
| Max | 🔜 近日提供予定 |
| Pro | ❓ 未発表 |

価格は現時点で非公開。Enterprise契約に含まれる模様。

---

## 【注意点】知っておくべき3つの制限

1. **プライベートリポジトリのみ** — 公開リポジトリは別途スキャン設定が必要
2. **言語サポート** — 主要言語（JS/TS/Python/Go/Java/C/C++）はOK、マイナー言語は要確認
3. **コードがAnthropicに送信される** — オンプレ環境が必要な企業は要相談

---

## まとめ：今すぐ確認すべきこと

1. **自社がEnterpriseプランか確認** → 使えるなら今すぐ試す
2. **Teamプランなら待機リストに登録** → 公式サイトでウェイトリスト登録
3. **既存ツールで「誤検出ゼロ」なら疑う** → 本当にゼロなのか、見逃しているだけなのか

:::note info
**27年間見つからなかったバグを、AIは見つけた。**
あなたのコードベースに、同じようなバグが眠っていないと言い切れますか？
:::

---

## 参考リンク

Claude Security enters public beta with Opus 4.7 vulnerability scanning and patching - Help Net Security

https://www.helpnetsecurity.com/2026/05/04/anthropic-claude-security-public-beta/

Project Glasswing: Securing critical software for the AI era

https://www.anthropic.com/glasswing

Claude Security is now in public beta | Claude

https://claude.com/blog/claude-security-public-beta

CrowdStrike Puts Claude Opus 4.7 to Work Across Falcon and QuiltWorks

https://www.crowdstrike.com/en-us/press-releases/crowdstrike-puts-claude-opus-4-7-to-work-across-falcon-platform-project-quiltworks/

---

**この記事が参考になったら、いいね👍とストック📌をお願いします！**

質問や感想があれば、コメント欄でお待ちしています。
「ウチの会社で使ってみた」という方、ぜひ体験談を共有してください！
