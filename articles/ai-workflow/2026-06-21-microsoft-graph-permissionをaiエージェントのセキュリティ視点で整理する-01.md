---
id: "2026-06-21-microsoft-graph-permissionをaiエージェントのセキュリティ視点で整理する-01"
title: "Microsoft Graph PermissionをAIエージェントのセキュリティ視点で整理する"
url: "https://zenn.dev/sec_dog/articles/4961935bb9edca"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-06-21"
date_collected: "2026-06-22"
summary_by: "auto-rss"
query: ""
---

## はじめに

この記事では、MicrosoftテナントにおいてAIエージェントのセキュリティリスクをレビューする際に重要なポイントの一つとなるMicrosoft GraphのPermissionについて解説します。

Microsoft環境でAIエージェントを使いM365などのMicrosoftの様々なクラウドサービス・リソースにアクセスするためにはMicrosoft Graphを利用することが一般的です。

各サービスデータにアクセスするためには、Microsoft Graphで公開されているREST APIやクライアントライブラリを利用することになりますが、その際に注意して検討しなければならない要素が2つあります。  
ひとつが「アクセス許可の種類」。もう一つがMicrosoft Graphによって付与される「アクセス許可権限」です。

### 1. アクセス許可の種類（Delegated Permission と Application Permission）

AIエージェントが誰の権限を継承するのか？という考え方です。ここでは通常「Delegated」と「Application」の2種類のパーミッションのうちいずれかが各アプリケーションの特性から選択されます。  
「Delegated」はセッションが「ユーザーIdentity」によって開始される場合にAIエージェントがユーザー権限を継承するパーミッションです。Delegated Permissionは、ユーザーがサインインし、そのユーザーの権限を利用してアクセスする場合に使用されます。  
一方の「Application Permission」は、サービスプリンシパルやバックグラウンドサービスなど、ユーザーが存在しない状態で動作するアプリケーションに付与されます。

### 2. アクセス許可権限

Files.Read、Sites.Read、Mail.Sendなどアクセス先のM365の各リソースに対して「何ができるか？」を定義することになります。実際には「認可」の考え方に近い概念ですが、実際の認可判断は、Resource ServerであるMicrosoft Graphおよびその背後のサービスによって行われます。混乱を避けるためにここでは「許可（パーミッション）」と定義します。

## 何が問題なのか？

まずは最初に下記図をみてください。

| アクセス許可の種類 | 最小特権アクセス許可 | 誰の権限か？ |
| --- | --- | --- |
| Delegated Permission | Files.Read | ユーザー権限を継承する |
| Application Permission | Files.Read.All | アプリケーションの固定権限 |

#### Delegated Permissionの場合：

ユーザーが営業部の一般社員の場合、そのユーザーがアクセスできるのは

1. 自分自身の個人領域
2. 自分のチーム／部門（営業部）の領域
3. 全社員がアクセスできる領域

など、ユーザー自身に許可された範囲に限定されます。

ここで重要なのは、同じ Files.Read であっても、誰の権限を継承するかによって参照可能な情報が大きく異なる点です。

例えば、一般社員であれば日常業務に必要な情報のみを参照できますが、経営層であれば経営計画やM&A関連資料、人事部であれば個人情報や人事情報にアクセスできる場合があります。

Delegated PermissionではAIエージェントがユーザー権限を継承するため、技術的には同じPermissionであっても利用者によってリスクが変化します。

そのため、Permissionだけではなく「どのユーザーが利用するのか」という観点を含めて評価することが重要です。また、AIエージェントは人間よりも高速かつ網羅的に情報を参照できるため、Read権限であっても最小権限を徹底する必要があります。

#### Application Permissionの場合：

「人以外のIdentity(Non-Human-Identity)」利用時はアプリケーション固定の許可が与えられることになります。「Files.Read.All」はテナント内のファイルリソースに対して広範なアクセスを許可します。  
Application Permissionは広範なアクセス権を持つことが多いため、必要性を十分に検討したうえで付与し、可能な限り権限およびアクセス可能なリソース範囲を制限することが重要です。

Delegated PermissionとApplication Permissionでは権限の持ち方や到達可能なリソースが異なります。しかし、どちらだから安全というものではありません。重要なのは「どの権限が付与されているか」「どのリソースへ到達できるか」「参照可能な情報が漏えいした場合にどのような影響があるか」を評価することです。

Delegated PermissionかApplication Permissionかという分類だけで安全性を判断することはできないのでこの点には十分注意してください。

## AIエージェントの権限レビューで確認すべき6つの観点

Microsoft GraphのPermissionをレビューする際、Files.Read や Mail.Read などの権限名だけを確認しても十分ではありません。

AIエージェントのリスクを正しく評価するためには、「誰が」「どの権限で」「どのリソースにアクセスできるのか」を段階的に確認する必要があります。

```
1. Identity（誰が利用するのか？）
    ↓
2. Authorization Model（DelegatedかApplicationか？）
    ↓
3. Authorization Scope（どのPermissionが付与されているのか？）
    ↓
4. Resource Boundary（どのリソースへ到達できるのか？）
    ↓
5. Business Impact（リスクを最大化した場合の影響は何か？）
    ↓
6. Control（どのような対策で制御するのか？）
```

例えば、同じ Files.Read であっても、

* 一般社員の Delegated Permission
* 経営層の Delegated Permission
* Application Permission + Files.Read.All

では参照可能な情報や想定される被害が大きく異なります。

そのため、AIエージェントのセキュリティレビューでは Permission の有無だけではなく、

1. どのIdentityが利用するのか
2. DelegatedかApplicationか
3. どのPermissionが付与されているのか
4. 実際にどのリソースへ到達できるのか
5. リスクを最大化した場合の影響は何か？
6. リスクをどのように制御するのか

という観点で評価することが重要です。

## Access Tokenから2つのPermissionの違いによるリスクを評価する

### Delegated Permission + Files.Read の場合

Access Token例

```
{
sub = userA
scp = Files.Read
aud = Microsoft Graph
}
```

| 評価レイヤ | 誰が・どの権限で・どのリソースを参照可能か？ |
| --- | --- |
| Identity（誰が？） | userA |
| Authorization Model（認可モデルは？） | Delegated |
| Authorization Scope（許可された操作は？） | Files.Read |
| Resource Boundary（どのリソースに？） | userAがアクセス可能なSharePoint |
| Business Impact（最大化した想定リスク） | userAの権限範囲に依存（※ユーザー毎にリスクが異なる点に注意) |
| Control（必要対策） | RBAC、Conditional Access、Audit(Logging,Monitoring)の実装 |

### Application Permission + Files.Read.All の場合

Access Token例

```
{
sub = Application Identity（例：service-principalなど）
roles = Files.Read.All
aud = Microsoft Graph
}
```

| 評価レイヤ | 誰が・どの権限で・どのリソースを参照可能か？ |
| --- | --- |
| Identity（誰が？） | Service Principal |
| Authorization Model（認可モデルは？） | Application |
| Authorization Scope（許可された操作は？） | Files.Read.All |
| Resource Boundary（どのリソースに？） | テナント全体になり得る（リソース側制限に依存） |
| Business Impact（最大化した想定リスク） | 全社情報の漏えい |
| Control（必要対策） | Admin Consent、Sites.Selected、Application RBAC、Conditional Access、Audit |

## 比較表

| 項目 | Delegated | Application |
| --- | --- | --- |
| Identity | User | Service Principal |
| 権限元 | ユーザー | アプリ |
| 到達範囲 | ユーザー依存 | テナント全体になりやすい |
| リスク | ユーザー権限に依存 | 権限設計・リソース制限に依存 |
| レビュー難易度 | 中 | 高 |
| 主な確認項目 | 対象ユーザーの役割・ユーザー権限 | Application権限・対象リソースのアクセス制御 |

Permissionだけではなく、誰の権限なのか（Identity）と、どのリソースに到達できるのか（Resource Boundary）を合わせて評価することが重要です。

## おわりに

Microsoft GraphのPermissionをレビューする際、多くの場合は Files.Read.All や Mail.Read といった権限名そのものに注目しがちです。しかし実際のリスクは、権限名だけでは判断できません。

重要なのは、そのPermissionがDelegated PermissionなのかApplication Permissionなのか、どのIdentityによって利用されるのか、そして最終的にどのリソースへ到達できるのかを合わせて評価することです。

特にAIエージェントは、人間よりも高速かつ網羅的に情報へアクセスできるため、従来のアプリケーション以上に権限設計やリソース境界の管理が重要になります。

AIエージェントのセキュリティレビューでは、Permissionの有無だけではなく、

* 誰が利用するのか（Identity）
* DelegatedかApplicationか（Authorization Model）
* どのPermissionが付与されているのか（Authorization Scope）
* どのリソースへ到達できるのか（Resource Boundary）
* リスクを最大化した場合の影響は何か（Business Impact）
* どのような対策で制御するのか（Control）

という観点で評価することが重要です。

Microsoft GraphのPermissionは単なる設定項目ではなく、AIエージェントの行動範囲そのものを決定する重要なセキュリティ要素であることを意識して設計・レビューを行うようにしてください。
