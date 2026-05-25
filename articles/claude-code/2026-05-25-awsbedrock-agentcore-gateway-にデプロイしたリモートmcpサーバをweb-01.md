---
id: "2026-05-25-awsbedrock-agentcore-gateway-にデプロイしたリモートmcpサーバをweb-01"
title: "# 【AWS】Bedrock AgentCore Gateway にデプロイしたリモートMCPサーバを、Web版Claudeのカスタムコネクタに繋ぐときに遭遇した問題"
url: "https://qiita.com/fsitlab/items/e71c8ff06b5ee8835f88"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "TypeScript", "qiita"]
date_published: "2026-05-25"
date_collected: "2026-05-25"
summary_by: "auto-rss"
query: ""
---

## なぜ Claude Web に繋ぎたかったか
Web版のClaudeと会話しているとき、Githubにpushできない等、不意にClaude側の制約に引っかかって、やりたいことができないことがある。


Claude Codeのほうが柔軟にMCPと接続できるが、Web版Claude Code は Sandbox コンテナの起動が重く、短い問い合わせや雑談には向かない。
claude.ai のチャット UI なら会話をすぐに始められ、 スマホからも同じ会話履歴やCustom Connector を共有できる。 Web版のClaudeを利用して、雑談の延長で自分の Github にメモを保存させたり、AWS 上にデプロイしたAPIを操作させたいと考えた。

AWS 公式 sample を調査しても、 Claude Web を AgentCore Gateway に接続する組み合わせが見つからなかった。 [awslabs/agentcore-samples](https://github.com/awslabs/agentcore-samples) は Claude Code 経路だけを扱っており、 [AWS Japan の Zenn 記事](https://zenn.dev/aws_japan/articles/agentcore-gateway-remote-mcp) も Auth0 経路で Cognito を使う構成ではない。 

本記事では、独自に実装する中で、公式情報だけでは解決できない2個の課題と、構成上の工夫について述べる。

## 問題 1 GET /mcp に Allow ヘッダが付かないと連携不可

AgentCore Gateway は GET /mcp に対して ELB default の 405 を返すが、 `Allow` ヘッダを付けていない。 Claude Web は `Allow` ヘッダを見て semantic 判断する実装になっているため、 Allow がないと「意図が読み取れない」 と判断して接続を断念してしまう。

これを解決した実装者ブログとして [George Vetticaden 氏「The Missing MCP Playbook」](https://medium.com/@george.vetticaden/the-missing-mcp-playbook-deploying-custom-agents-on-claude-ai-and-claude-mobile-05274f60a970) がある。 

> Return 405 Method Not Allowed with `Allow: POST` header? Claude interprets: POST-only server by design

CloudFront Function (viewer-request) で GET だけを intercept して 405 + `Allow: POST` を直接返せば、 Claude Web は POST フォールバックで接続を継続する。

```typescript
// GET だけ intercept、 POST はそのまま AgentCore Gateway に通す
if (req.method === 'GET') {
  return { statusCode: 405, headers: { 'allow': { value: 'POST' } } };
}
return req;
```

## 問題 2 Claude Web は AS metadata を読まずに path-join する

OAuth フローに入ると、 Claude Web は PRM (`/.well-known/oauth-protected-resource`) の `authorization_servers[0]` を取得する。 その後、 spec が要求する AS metadata (`/.well-known/openid-configuration` または `/.well-known/oauth-authorization-server`) のフェッチを行わず、 取得した URL の origin に対して `/authorize` を path-join した URL (`apps.example.com/authorize`) を直接叩く。

同じ挙動で困っているケースは他にもあり、 [modelcontextprotocol/typescript-sdk #744](https://github.com/modelcontextprotocol/typescript-sdk/issues/744) で議論されているほか、 AWS にも [awslabs/amazon-bedrock-agentcore-samples Issue #1056](https://github.com/awslabs/amazon-bedrock-agentcore-samples/issues/1056) で要望が出ている。 Anthropic または AWS の修正を待つのは現実的ではないため、 サーバー側で実際の挙動に合わせることにした。

`apps.example.com/authorize` を CloudFront で Cognito hosted UI に reverse proxy する。 これは [AWS Security Blog: CloudFront proxy for Cognito](https://aws.amazon.com/blogs/security/protect-public-clients-for-amazon-cognito-by-using-an-amazon-cloudfront-proxy/) で紹介されている公式 supported なパターンを応用したものである。

```typescript
additionalBehaviors['authorize'] = {
  origin: new HttpOrigin('xxx.auth.region.amazoncognito.com'),
  originRequestPolicy: cloudfront.OriginRequestPolicy.ALL_VIEWER_EXCEPT_HOST_HEADER,
  functionAssociations: [{ function: rewriteFn /* /authorize → /oauth2/authorize */, ... }],
};
additionalBehaviors['oauth2/*'] = { origin: cognitoHostedUiOrigin, ... };  // 素通し
```

Cognito の Set-Cookie は Domain 指定なしで発行されるため、 既存アプリが localStorage ベースで認証情報を持っているなら cookie の衝突は起きない。 副次的な効果として、 ブラウザの URL バーが自社ドメインで一貫するため、 フィッシング防止の運用ルールを徹底しやすくなる。

### 同じ仕組みは `/token` でも踏む 予防的に他 endpoint も網羅する

OAuth フローを進めすと、次は token 交換で `apps.example.com/token` に POST が飛び、 同じ理由で S3 fallback になり、 `mcp_token_exchange_failed` となるバグに遭遇した。 対応も同じく `token` literal behavior を追加して `/oauth2/token` に rewrite した。

ここで一度仕組みを理解すれば、 AS metadata に登場する他の endpoint (`/userInfo` / `/revoke` / `/logout` / `/register`) も同じ path-join 挙動の対象になり得ると予測できる。 後続工程で同系統の問題に遭遇しないよう、 まとめて予防的に reverse proxy 登録するとOAuthに成功した。 CloudFront behavior 数のデフォルト上限は 25 なので、 他のアプリ用 behavior と合算して超過しないかを事前に確認する必要がある。

## 工夫 Discovery JSON は S3 + CloudFront で配信する (Lambda 不要)

`/.well-known/openid-configuration` などの discovery JSON は deploy 後に内容が変化しないため、 Lambda を立てる必要はない。 CDK で S3 に静的アップロードして CloudFront から配信すれば、 cold start はゼロになり、 コストも Lambda + API Gateway　より安くなる。

`BucketDeployment` でデプロイしたところ、別 stack の Cognito issuer URL のような SSM 経由の Token を JSON に埋め込む場合は、 BucketDeployment では Token が literal 文字列のまま固まってしまう問題に遭遇した。
解決のため、 `AwsCustomResource` + `cdk.Fn.sub` を使って、 deploy 時に CloudFormation 側で値を解決させた。

```typescript
new cr.AwsCustomResource(this, 'X', {
  onCreate: {
    service: 'S3', action: 'putObject',
    parameters: { Bucket, Key, Body: cdk.Fn.sub(template, { IssuerVar: cognitoIssuer }) },
    physicalResourceId: cr.PhysicalResourceId.of('mcp-openid-config'),
  },
});
```

## まとめ

| 区分 | 内容 | 解決方法 |
|---|---|---|
| 問題 1 | GET /mcp に Allow ヘッダがないため接続初手で断念される | CloudFront Function で 405 + `Allow: POST` を返す |
| 問題 2 | Claude Web が AS metadata を読まずに `/authorize` / `/token` / `/userInfo` などを path-join する | Cognito hosted UI を CloudFront で reverse proxy する。 他 endpoint も予防的に登録する。 |
| 工夫 | Discovery JSON の配信に Lambda を立てない | S3 に静的アップロードして CloudFront から配信する。AwsCustomResource + cdk.Fn.sub でTokenを埋め込み。|

公式ドキュメントを読むだけでは分からないバグに多数であったが、何とかClaudeCodeの力を借りて実装することができた。
皆様もぜひ同じトラブルに遭遇しないよう、本ブログを参考にしてほしい。

## 参考

- [George Vetticaden 「The Missing MCP Playbook」](https://medium.com/@george.vetticaden/the-missing-mcp-playbook-deploying-custom-agents-on-claude-ai-and-claude-mobile-05274f60a970) Allow: POST について決定的な言及がある実装者ブログ
- [awslabs/amazon-bedrock-agentcore-samples Issue #1056](https://github.com/awslabs/amazon-bedrock-agentcore-samples/issues/1056) Gateway missing MCP OAuth spec endpoints
- [modelcontextprotocol/typescript-sdk #744](https://github.com/modelcontextprotocol/typescript-sdk/issues/744) path-join 問題が業界全体で議論されている Issue
- [AWS Security Blog: CloudFront proxy for Cognito](https://aws.amazon.com/blogs/security/protect-public-clients-for-amazon-cognito-by-using-an-amazon-cloudfront-proxy/) CloudFront 前段に Cognito を置く公式 supported な構成
- [AWS Japan: AgentCore Gateway + Auth0 + DCR](https://zenn.dev/aws_japan/articles/agentcore-gateway-remote-mcp) Auth0 を IdP に使った AWS Japan の事例
- [awslabs/agentcore-samples](https://github.com/awslabs/agentcore-samples) Claude Code 経路の公式 sample
- [Amazon Bedrock AgentCore Gateway 公式 docs](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)
