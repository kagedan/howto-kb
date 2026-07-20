---
id: "2026-07-21-claude-enterpriseのssoscim設定情シス向け導入の勘所-01"
title: "Claude EnterpriseのSSO/SCIM設定。情シス向け導入の勘所"
url: "https://note.com/daikidomon/n/n32dd3676cbed"
source: "note"
category: "ai-workflow"
tags: ["API", "GPT", "note"]
date_published: "2026-07-21"
date_collected: "2026-07-21"
summary_by: "auto-rss"
query: ""
---

Claudeを全社に配るなら、情シスが押さえるべきはSSO・SCIM・監査ログです。個人が勝手にアカウントを作る状態を避け、統制の効いた形で配布する。Claude Enterpriseの管理機能と、導入の勘所を整理します。

## なぜ情シスの統制が要るか

社員が個人アカウントでClaudeを使い始めると、会社は「誰が何に使っているか」を把握できません。これはシャドーAI(非公認利用)の温床です([『シャドーAIを防ぎつつClaudeを解禁する』](https://note.com/daikidomon/n/nfa6b3a2a7b4c))。

統制して配るには、認証・プロビジョニング・監査を会社の仕組みに載せます。Claude Enterpriseは、その管理機能を備えています。

## SSO(シングルサインオン)

まず、認証を会社のIDに寄せます。

* **SAMLベースのSSO**に対応。Okta・Entra IDなどのIdPと連携
* **ドメインキャプチャ**: 自社ドメインのメールで作られたアカウントを組織管理下に取り込む
* 社員は会社のIDでログインし、退職時はIdP側で止められる

個人のメールでバラバラにログインする状態を、会社の認証基盤に統一できます。

## SCIM(自動プロビジョニング)

次に、アカウントの発行・削除を自動化します。

人の出入りが多い組織ほど、SCIMの効果が大きい。管理の抜け漏れ(退職者のアカウントが残る等)を防げます。

## 監査ログとアクセス制御

統制には、記録と権限管理が要ります。

* **監査ログ**: 組織の操作記録を残す(Enterpriseで提供、一定期間分をエクスポート可能)
* **ロールベースアクセス制御(RBAC)**: 役割に応じた権限管理
* **データ保持コントロール**: データの保持方針を組織で設定できる

「誰が・いつ・何をしたか」を追える状態が、ガバナンスの土台になります。

## 導入の勘所

情シスが進めるときの順番です。

* IdP(Okta/Entra ID等)との連携方式を確認する
* ドメインキャプチャで既存の個人利用を組織に取り込む
* SCIMで入退社フローに載せる
* 監査ログ・RBAC・データ保持を組織方針に合わせて設定

加えて、Enterprise/APIはデータを学習に使わない契約である点も、全社展開の安心材料です([『Claudeに入力した情報は学習される?』](https://note.com/daikidomon/n/n20204a50152d))。

## まとめ

* 全社配布は情シスの統制が前提。個人アカウント乱立(シャドーAI)を避ける
* SSO(SAML)+ドメインキャプチャで認証を会社のIDに統一
* SCIMでアカウント発行・削除を入退社フローに自動連動
* 監査ログ・RBAC・データ保持コントロールで記録と権限を管理。学習不使用の契約も土台

主な参考資料: [Claude for Enterprise(公式)](https://claude.com/solutions/enterprise)、[監査ログへのアクセス(公式ヘルプ)](https://support.claude.com/en/articles/9970975-access-audit-logs)、[SSO設定(公式ヘルプ)](https://support.claude.com/en/articles/13132885-set-up-single-sign-on-sso)

TodoONadaでは、情シス向けにClaude Enterpriseの導入・統制設計を支援しています。研修の全体像は「[ChatGPT研修と何が違うのか。Claude特化研修という選択肢](https://note.com/daikidomon/n/n9b83451fe1c7)」をご覧ください。
