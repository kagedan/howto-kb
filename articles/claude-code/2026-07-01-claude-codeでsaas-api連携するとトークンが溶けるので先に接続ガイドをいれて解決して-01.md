---
id: "2026-07-01-claude-codeでsaas-api連携するとトークンが溶けるので先に接続ガイドをいれて解決して-01"
title: "Claude CodeでSaaS API連携するとトークンが溶けるので、先に接続ガイドをいれて解決してみた"
url: "https://zenn.dev/kanseilink/articles/kanseilink-mcp-token-saving"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "GPT", "zenn"]
date_published: "2026-07-01"
date_collected: "2026-07-02"
summary_by: "auto-rss"
query: ""
---

## この記事で伝えたいこと

Claude CodeやCursorにSaaS API連携を書かせると、便利な一方で、かなりの確率で同じところにハマります。

* OAuth認証で詰まる
* API v1 / v2 を間違える
* 必須パラメータを見落とす
* scope不足で落ちる
* エンドポイントが古い
* 公式APIとMCP経由で挙動が違う

AIはかなり賢いですが、SaaS API連携では **賢さよりも「現在の接続情報」** の方が効く場面があります。

ClaudeやGPTが持っているAPI知識は、常に最新とは限りません。  
その結果、最初にそれっぽいコードを書いて、エラーになって、直して、また落ちて、トークンだけが溶けていく。

そこで、SaaS APIを叩く前に **「このSaaS、今どう繋ぐのが正解？」をMCP経由で確認する** ようにしました。

やっていることは単純です。

> AIにいきなりAPIを叩かせず、先に接続ガイドを渡す

これだけで、Claude Codeでの試行錯誤とトークン消費がかなり減りました。

## よくある失敗パターン

たとえば、Claude Codeにこう頼んだとします。

すると、ありがちな流れはこうです。

```
Claude:
  → freee APIの使い方を思い出す
  → OAuthのコードを書く
  → token取得処理を書く
  → 仕訳登録APIを叩く
  → パラメータが違って落ちる
  → scopeを直す
  → company_idが必要だと気づく
  → もう一回書き直す
```

この時点で、3,000〜5,000トークンくらいは普通に使います。

問題は、Claudeがコードを書けないことではありません。

**最初に持っている接続前提が古いと、その後の修正も全部ズレていく** ことです。

SaaS API連携でトークンが溶ける原因の多くは、実装力不足ではなく、接続前提のズレでした。

## 解決策: APIを叩く前にMCPへ聞く

そこで、KanseiLINK MCPというMCPサーバーを作りました。

SaaS APIを叩く前に、Claude Codeから以下を確認できます。

* 対象サービスがあるか
* 認証方式は何か
* API直接接続か、公式MCPか、サードパーティMCPか
* よくあるハマりどころは何か
* エージェント経由で接続しやすいか

イメージはこうです。

```
Before:
ユーザー → Claude → SaaS API
              ↑
        古い知識で試行錯誤

After:
ユーザー → Claude → KanseiLINK MCP → 接続ガイド
              ↓
           SaaS API
```

AIに根性で調べさせるのではなく、最初に地図を渡す感じです。

## セットアップ

Claude Codeならこれだけです。

```
claude mcp add kansei-link -- npx @kansei-link/mcp-server
```

Claude Desktopの場合は `claude_desktop_config.json` に追加します。

```
{
  "mcpServers": {
    "kansei-link": {
      "command": "npx",
      "args": ["@kansei-link/mcp-server"]
    }
  }
}
```

API keyも認証も不要です。

## 使い方

主に使うのは2つです。

### 1. search\_services

まず対象サービスを探します。

```
search_services({ query: "freee accounting" })
```

返答イメージです。

```
freee会計
- AEOグレード: AAA
- 接続成功率: 90.3%
- 認証方式: OAuth 2.0 + PKCE
- 接続方式: API / MCP
```

ここで見たいのは、単にサービス名があるかではありません。

Claude Codeが実装前に、

* どの接続方式を使うべきか
* OAuthが必要か
* MCP経由で使えるか
* ハマりやすいか

を把握できることが重要です。

### 2. lookup

次に、接続方法の詳細を取ります。

```
lookup({ service_id: "freee-accounting", detail: true })
```

返答イメージです。

```
認証:
  OAuth 2.0 + PKCE

必要になりやすいパラメータ:
  company_id

よくあるミス:
  - OAuth開始時にPKCEを入れ忘れる
  - company_idなしでAPIを叩く
  - v1 / v2 のエンドポイントを混同する
  - scope不足で403になる
```

この情報を最初に渡しておくと、Claudeが「それっぽいけど古いコード」を書きにくくなります。

## 実際にどれくらい変わったか

自分の環境で、いくつかのSaaS接続タスクを比較しました。

厳密なベンチマークではありませんが、Claude Code上でのトークン消費と試行回数を見ています。

| タスク | Before | After | 削減率 |
| --- | --- | --- | --- |
| freee 仕訳登録 | 約4,200 | 約1,400 | 67% |
| SmartHR 従業員一覧取得 | 約3,800 | 約1,100 | 71% |
| Salesforce 商談更新 | 約5,500 | 約1,800 | 67% |
| kintone レコード登録 | 約3,200 | 約1,500 | 53% |

平均すると、だいたい **60〜70%くらいトークンが減りました**。

理由はシンプルです。

```
古いAPI知識で書く
↓
失敗する
↓
修正する
↓
また失敗する
```

このループが減ったからです。

推論性能が上がったわけではなく、最初の前提がズレにくくなっただけです。

でもSaaS API連携では、それがかなり効きます。

## なぜ公式ドキュメントだけでは足りないのか

「公式ドキュメントを読めばいい」は正論です。

ただ、AIエージェントに実装させる場合は少し事情が違います。

公式ドキュメントには正しいことが書いてあります。  
でも、実装で詰まるのはこういうところです。

```
company_idをどこで取るのか
scopeはどこまで必要なのか
v1とv2のどちらを使うべきか
sandboxとproductionで挙動が違うのか
MCP経由だとwriteだけ失敗しないか
```

こういう情報は、ドキュメント内に散らばっていたり、そもそも公式ドキュメントには書かれていなかったりします。

AIに毎回そこを読ませると、またトークンが溶けます。

だから、SaaS API連携では「ドキュメントを読ませる」より先に、**接続前提を短く渡す** 方が効くことがあります。

## 対応サービス

現時点で、11,000以上のSaaS / APIサービスのデータを入れています。

日本のSaaSも入れています。

```
会計:
  freee
  マネーフォワード
  弥生

HR:
  SmartHR
  KING OF TIME
  freee人事労務

CRM / SFA:
  Sansan
  HubSpot
  Salesforce

その他:
  kintone
  Slack
  Notion
  GitHub
  Stripe
```

各サービスには、エージェントから見た接続しやすさのグレードを付けています。

これはサービス自体の良し悪しではありません。

あくまで、

```
AIエージェントがそのサービスを見つけて、
正しく理解して、
実際に接続・実行しやすいか
```

という観点です。

## まとめ

Claude CodeでSaaS API連携するとき、トークンが溶ける原因はコード生成そのものよりも、接続前提のズレにあることが多いです。

KanseiLINK MCPを入れると、APIを叩く前に、

```
このサービスにはどう接続するべきか
どの認証方式を使うべきか
どのエンドポイントを使うべきか
どこでハマりやすいか
```

をClaudeが確認できます。

結果として、自分の環境では、

* セットアップ: 1分
* トークン削減: 60〜70%
* 試行回数: 3回前後 → 1回

くらいの改善がありました。

インストールはこれだけです。

```
claude mcp add kansei-link -- npx @kansei-link/mcp-server
```

GitHubはこちらです。

<https://github.com/kansei-link/kansei-mcp-server>

SaaS API連携で毎回OAuthやエンドポイントに殴られている人は、試してみてください。

AIに根性で調べさせるより、最初に地図を渡した方がだいたい安いです。
