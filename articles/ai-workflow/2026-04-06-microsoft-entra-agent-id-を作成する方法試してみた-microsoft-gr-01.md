---
id: "2026-04-06-microsoft-entra-agent-id-を作成する方法試してみた-microsoft-gr-01"
title: "Microsoft Entra Agent ID を作成する方法試してみた！ Microsoft Graph 編 (サンプルコード付き)"
url: "https://zenn.dev/microsoft/articles/91df843374fbde"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-04-06"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

## シリーズ記事

1. [Microsoft Entra Agent ID 入門編](https://zenn.dev/microsoft/articles/a52eae77302ce7#%E7%99%BB%E9%8C%B2%E3%81%95%E3%82%8C%E3%81%9F-agent-%E3%81%AE%E7%A2%BA%E8%AA%8D%E6%96%B9%E6%B3%95)
2. Microsoft Entra Agent ID を作成する方法試してみた！ Microsoft Graph 編 (サンプルコード付き) (本記事)

## はじめに

Microsoft Entra Agent ID の条件付きアクセスや ID Protection などの機能がプレビューで公開されています。  
実際どのようなことができるのか動作を検証するためにも、まずは Agent ID 自体が必要であるということで、Agent ID を作成する方法を試してみました。  
一緒に下準備しておきましょう！

[Microsoft Entra Agent ID 入門編](https://zenn.dev/microsoft/articles/a52eae77302ce7#%E7%99%BB%E9%8C%B2%E3%81%95%E3%82%8C%E3%81%9F-agent-%E3%81%AE%E7%A2%BA%E8%AA%8D%E6%96%B9%E6%B3%95) でもご紹介したように Agent ID が作成されるシナリオには以下などがあります。  
公開情報はこちら：[エージェント ID はどのように作成されますか?](https://learn.microsoft.com/ja-jp/entra/agent-id/agent-id-creation-channels)

* Microsoft Copilot Studio
* Microsoft 365 Agents
* Microsoft Foundry
* Microsoft Security Copilot
* Microsoft Graph API  
  など

この記事では **Microsoft Graph API** による Agent Identity の作成方法をそれぞれ紹介します。  
他の方法で作成されるシナリオは別途記事にしようと思います。

## Agent ID に関連するオブジェクトの関係図

Agent ID、Agent identity blueprint、Agent identity blueprint principal... 各オブジェクトの関係性は混乱しやすい部分もあるかと思います😵‍💫  
まず、それぞれどのような関係となっているか以下にまとめます！

| オブジェクト | わかりやすく言うと |
| --- | --- |
| **Agent identity blueprint** | Agent ID を作成するテンプレートで、認証、アクセス許可、アクティビティ ログなどに関する重要な情報が含まれる。 |
| **Agent identity blueprint principal** | Agent identity blueprint をテナントに登録した時にできるインスタンス。実際にトークンを取得し、エージェント ID を作成し、ブループリントに代わって監査ログに表示される。 |
| **Agent Identity** | エージェント 1 つ 1 つの ID 。この ID で Microsoft サービスにアクセスする。 |
| **Agent's User Account** | Teams や Outlook など「ユーザーでないと動かないシステム」を使用する場合に必要。\*Agent Identity と 1:1。 |

![](https://static.zenn.studio/user-upload/5f7c5260a572-20260406.png)  
*※この画像は公開情報をもとに作成しています。最新情報は[こちら](https://learn.microsoft.com/ja-jp/entra/agent-id/identity-platform/agent-blueprint)をご確認ください。*

## Microsoft Graph API で Microsoft Entra Agent ID を作成する

Microsoft Graph API で Microsoft Entra Agent ID を作成するサンプルコードです。  
以下のコードで実際に Agent ID を作成してみました。

### 必要なライセンス

* **Microsoft 365 Copilot** ライセンス
* **Frontier プログラム** が有効であること
  + M365 管理センター > **Copilot** > **Settings** > **User access** > **Copilot Frontier** で確認

### 必要な Entra ID ロール

* **Agent ID Developer** または **Agent ID Administrator**（Blueprint 作成用）
* **Privileged Role Administrator**（Graph アクセス許可の付与用）

### 必要なツール

* PowerShell 7 以降
* Microsoft Graph PowerShell SDK

```
Install-Module Microsoft.Graph
```

### サンプルコード: Graph API で Agent Identity を作成する

参考になる公開情報はこちら：

Agent ID が作成されるまでの全体の流れは以下の通りです。

```
Step 1: Graph に接続
Step 2: Agent Identity Blueprint を作成
Step 3: Blueprint に資格情報（クライアント シークレット）を追加
Step 4: Blueprint Principal を作成
Step 5: Blueprint のアクセス トークンを取得
Step 6: Agent Identity を作成
Step 7: 確認
```

### Step 1: Graph に接続

```
Connect-MgGraph -Scopes @(
    "AgentIdentityBlueprint.Create",
    "AgentIdentityBlueprint.AddRemoveCreds.All",
    "AgentIdentityBlueprintPrincipal.Create",
    "User.Read"
) -TenantId "<your-tenant-id>"
```

### Step 2: Agent identity blueprint を作成

```
# 現在のユーザーを Sponsor / Owner として設定
$currentUser = Get-MgContext | Select-Object -ExpandProperty Account
$user = Get-MgUser -UserId $currentUser

$body = @{
    "@odata.type"          = "Microsoft.Graph.AgentIdentityBlueprint"
    "displayName"          = "Agent Identity Blueprint Name"
    "sponsors@odata.bind"  = @("https://graph.microsoft.com/v1.0/users/$($user.Id)")
    "owners@odata.bind"    = @("https://graph.microsoft.com/v1.0/users/$($user.Id)")
} | ConvertTo-Json -Depth 5

$blueprint = Invoke-MgGraphRequest `
    -Method POST `
    -Uri "https://graph.microsoft.com/v1.0/applications/graph.agentIdentityBlueprint" `
    -Body $body `
    -ContentType "application/json"

# appId を控える
$blueprintAppId = $blueprint.appId
Write-Host "Blueprint appId: $blueprintAppId"
```

### Step 3: Agent identity blueprint に資格情報を追加

テスト用にクライアント シークレットを追加します。

```
$passwordCredential = @{
    displayName = "Test Secret"
    endDateTime = (Get-Date).AddMonths(6).ToString("o")
}

$secret = Add-MgApplicationPassword `
    -ApplicationId $blueprintAppId `
    -PasswordCredential $passwordCredential

# シークレット値を控える（一度しか表示されません！）
Write-Host "Client Secret: $($secret.SecretText)"
$clientSecret = $secret.SecretText
```

### Step 4: Agent identity blueprint principal を作成

```
$principalBody = @{
    appId = $blueprintAppId
}

Invoke-MgGraphRequest -Method POST `
    -Uri "https://graph.microsoft.com/v1.0/serviceprincipals/graph.agentIdentityBlueprintPrincipal" `
    -Headers @{ "OData-Version" = "4.0" } `
    -Body ($principalBody | ConvertTo-Json)
```

### Step 5: Agent identity blueprint のアクセス トークンを取得

ここからは **Blueprint のアプリとして**（client\_credentials フロー）トークンを取得します。

```
$tenantId = "<your-tenant-id>"

$tokenResponse = Invoke-RestMethod -Method POST `
    -Uri "https://login.microsoftonline.com/$tenantId/oauth2/v2.0/token" `
    -ContentType "application/x-www-form-urlencoded" `
    -Body "client_id=$blueprintAppId&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default&client_secret=$clientSecret&grant_type=client_credentials"

$token = $tokenResponse.access_token
Write-Host "Token acquired (length: $($token.Length))"
```

取得したトークンの中身を確認してみましょう。

```
$tokenParts = $token.Split('.')
$payload = [System.Text.Encoding]::UTF8.GetString(
    [Convert]::FromBase64String($tokenParts[1] + ('=' * (4 - $tokenParts[1].Length % 4)))
)
$payload | ConvertFrom-Json | Select-Object iss, aud, app_displayname, roles
```

`roles` に `AgentIdentity.CreateAsManager` が含まれていれば OK です。

### Step 6: Agent Identity を作成

```
$userId = "<Agent ID のスポンサーにしたいユーザーの ID>"

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type"  = "application/json"
    "OData-Version" = "4.0"
}

$agentBody = @{
    displayName              = "<Agent ID の名前>"
    agentIdentityBlueprintId = $blueprintAppId
    "sponsors@odata.bind"    = @(
        "https://graph.microsoft.com/v1.0/users/$($user.Id)"
    )
} | ConvertTo-Json -Depth 5

$agentIdentity = Invoke-RestMethod -Method POST `
    -Uri "https://graph.microsoft.com/beta/servicePrincipals/microsoft.graph.agentIdentity" `
    -Headers $headers `
    -Body $agentBody

Write-Host "Agent Identity created!"
Write-Host "  ID: $($agentIdentity.id)"
Write-Host "  Display Name: $($agentIdentity.displayName)"
```

同じ Blueprint から複数の Agent Identity を作成できます（最大 250 個）。

```
# 2 つ目の Agent Identity
$agentBody2 = @{
    displayName              = "<Agent ID の名前>"
    agentIdentityBlueprintId = $blueprintAppId
    "sponsors@odata.bind"    = @(
        "https://graph.microsoft.com/v1.0/users/$($user.Id)"
    )
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method POST `
    -Uri "https://graph.microsoft.com/beta/servicePrincipals/microsoft.graph.agentIdentity" `
    -Headers $headers `
    -Body $agentBody2
```

### Step 7: 確認

#### Entra 管理センターで確認

1. [Microsoft Entra 管理センター](https://entra.microsoft.com) にサインイン
2. **Entra ID** > **Agent identities** > **All agent identities** を開く
3. 作成した Agent Identity が一覧に表示される
4. 右上の **View agent blueprint** をクリックすると、Blueprint Principal が確認できる

#### Graph API で確認

```
# Agent Identity の一覧を取得
Connect-MgGraph -Scopes "Application.Read.All" -TenantId "<your-tenant-id>"
Invoke-MgGraphRequest -Method GET `
    -Uri "https://graph.microsoft.com/beta/servicePrincipals?`$filter=servicePrincipalType eq 'ServiceIdentity'" `
    -Headers @{ "OData-Version" = "4.0" }
```

## まとめ

この記事では以下の内容についてまとめました。

* Agent ID に関連するオブジェクトの関係
* Microsoft Graph API で Agent ID を作成する方法

疑問点などある場合はコメントなどでお知らせください！
