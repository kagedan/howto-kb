---
id: "2026-04-10-masahirochaen-claude-cowork-エンタープライズ向け新機能はこちら-http-01"
title: "@masahirochaen: Claude Cowork エンタープライズ向け新機能はこちら https://t.co/hLThNffFC2 1."
url: "https://x.com/masahirochaen/status/2042613412149313902"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "OpenAI", "Gemini", "cowork"]
date_published: "2026-04-10"
date_collected: "2026-04-11"
summary_by: "auto-x"
---

【🔥朗報】Claude Coworがすべての有料プランで一般提供

CopilotにもCoworkが搭載されましたし、今後OpenAIやGeminiでも似たようなツールが発表されるかと思います。

https://t.co/gLHLqFfxBR

Claude Cowork エンタープライズ向け新機能はこちら
https://t.co/hLThNffFC2

1. ロールベースアクセス制御（RBAC）
・ユーザーをグループに分類（手動 or SCIMで自動連携）
・グループごとに使用できるClaude機能をカスタム設定
・Claude Coworkを特定チームだけに有効化し、段階展開可能

2. グループ別支出上限
・チームごとの予算をアドミンコンソールから設定
・コストを予測可能に管理、チームの状況に応じて調整可能

3. 利用状況アナリティクス
・アドミンダッシュボードでCoworkセッション数・アクティブユーザーを確認
・Analytics APIでより詳細なデータ取得が可能
  - ユーザーごとのCowork利用状況
  - スキル・コネクター呼び出し回数
  - DAU / WAU / MAU（Chat・Claude Code含む）

4. OpenTelemetry対応の拡張
・ツール・コネクター呼び出し、ファイル操作、スキル使用をイベント出力
・手動 or 自動承認の区別も記録
・SplunkやCriblなど標準SIEMパイプラインに対応
・Compliance APIとのユーザーID紐付けも可能
・対象：TeamプランおよびEnterpriseプラン

5. Zoom MCPコネクター
・ZoomのAI Companion会議サマリー・アクションアイテムをCoworkに統合
・文字起こし・スマートレコーディングも活用可能
・Claudeの設定内コネクターディレクトリから追加

6. コネクター単位のツール制御
・MCPコネクターごとに許可するアクションを制限可能
  例）読み取りは許可、書き込みは禁止
・設定はアドミンコンソールから組織全体に適用

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

対象プラン：Team / Enterprise（一部機能はEnterprise限定）
展開方法：https://t.co/CLtO229IBd よりデスクトップアプリをDL
管理者向けウェビナー：2026年4月16日（PayPal共催）
