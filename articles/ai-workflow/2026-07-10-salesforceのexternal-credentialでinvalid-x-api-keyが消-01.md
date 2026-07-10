---
id: "2026-07-10-salesforceのexternal-credentialでinvalid-x-api-keyが消-01"
title: "# SalesforceのExternal Credentialで「invalid x-api-key」が消えなかった話 ― 真因は `allowMergeFieldsInHeader`"
url: "https://qiita.com/hibiki-ishida/items/167c16b7b764f55bc247"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-07-10"
date_collected: "2026-07-11"
summary_by: "auto-rss"
query: ""
---

## 何をやろうとしていたか

Salesforce（Apex）から外部API（Claude API）を叩く。APIキーはコード直書きせず、**Named Credential + External Credential** に格納し、カスタムHTTPヘッダー `x-api-key` に流し込む構成。

- External Credential `Anthropic`（認証プロトコル = Custom）
- Named Principal `AnthropicPrincipal` に認証パラメーター `ApiKey` を手入力
- Named Credential のカスタムヘッダー: `x-api-key = {!$Credential.Anthropic.ApiKey}`
- Apex: `req.setEndpoint('callout:Anthropic_API/v1/messages')`

## 症状

コールアウトすると毎回これ:

```json
{"type":"error","error":{"type":"authentication_error","message":"invalid x-api-key"}}
```

HTTP 401。`request_id` が返る＝**リクエストはAnthropicまで届いている**。つまりヘッダー自体は送られているが、中身が空 or 不正。

## やってしまった遠回り（と、そこから得た学び）

### 遠回り1: 「APIキーが未設定なのでは」

最初はキー未入力を疑った。→ 入力済みでも401。

### 遠回り2: 「認証パラメーターが保存されていないのでは」

`tooling API` と `metadata retrieve` で External Credential を確認したら、`AnthropicPrincipal`（NamedPrincipal）しか出てこない。`ApiKey` が見当たらない → 「保存できていない」と判断してしまった。

**これが誤り。** 秘密値をもつ認証パラメーターは、**metadata retrieve にも tooling API にも出てこない**（セキュリティのため）。“見えない” ことは “保存されていない” を意味しない。retrieveでの有無判定は不可。

### 遠回り3: 「metadataでスロットを配布してしまえ」

`AuthParameter` 型で配布を試みる → ドライランで一撃拒否:

```
The authentication protocol "Custom" doesn't support the following
external credential parameter type(s): AuthParameter.
```

**学び**: Customプロトコルの秘密パラメーターは metadata では配布できない（UIまたはConnect API経由でのみ格納）。

### 切り分け: キー単体をcurlで検証

Salesforceと切り離して、キーそのものの有効性をターミナルで確認:

```bash
curl https://api.anthropic.com/v1/models \
  -H "anthropic-version: 2023-06-01" -H "x-api-key: sk-ant-..."
```

→ モデル一覧が返った＝**キーは有効**。よって原因は100% Salesforce側の「値が解決されていない」問題に絞れた。

## 真因

Named Credential の設定:

```xml
<allowMergeFieldsInHeader>false</allowMergeFieldsInHeader>
```

これが **false** だと、カスタムヘッダーに書いた `{!$Credential.Anthropic.ApiKey}` という**マージフィールド（式）が評価されない**。リテラル文字列のまま（あるいは空として）送信され、Anthropic側で「invalid x-api-key」になる。

### 修正

```xml
<allowMergeFieldsInHeader>true</allowMergeFieldsInHeader>
```

（UIなら「HTTPヘッダーで式を許可 / Allow Formulas in HTTP Header」にチェック）

デプロイして再コールアウト → **一発で成功、構造化JSONが返ってきた。** APIキーは最初からちゃんと保存されていた。

## 副次的にハマった小ネタ

- **日本語UIラベル**: 「Named Credentials」の日本語は "名前付き資格情報" ではなく **「指定ログイン情報」**。クイック検索で出なくて詰まった。External Credentials タブ = **「外部ログイン情報」**。
- **認証パラメーターはリネーム不可**: 名前を間違えて（`Apikey`→`ApiKey`）直そうとすると「更新する既存の認証ログイン情報がありません」。値は書き込み専用で別保管のため、リネームは非対応 → **削除して入れ直す**。

## チェックリスト（同じ轍を踏まないために）

`$Credential` マージフィールドをヘッダーに使うなら:

1. Named Credential: `generateAuthorizationHeader = false`
2. Named Credential: **`allowMergeFieldsInHeader = true`** ← 忘れがちな本命
3. External Credential: 認証プロトコル Custom + プリンシパルに認証パラメーターで秘密を格納（UI手入力）
4. 権限セットに External Credential Principal Access を付与し、実行ユーザーに割当
5. 401が出たら、まず **curlでキー単体の有効性** を切り分ける（Salesforce側かキー側か）
6. 秘密パラメーターは metadata/tooling に出ない。retrieveの有無で保存判定しない

## 教訓

「見えない＝無い」ではない。切り分けは、**疑っている層を1つずつ外部から独立に検証**する（curlでキー、metadataで構造、apexで疎通）。今回は真因が設定1フラグだったのに、"保存できていない" という誤った前提で2手ほど無駄足を踏んだ。
