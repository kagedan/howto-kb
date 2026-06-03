---
id: "2026-06-02-aws-bedrock-で-gpt-55-を-c-から使う-01"
title: "AWS Bedrock で GPT-5.5 を C# から使う"
url: "https://qiita.com/karuakun/items/a73bd8bcd46d5300d318"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "AI-agent", "OpenAI", "GPT", "qiita"]
date_published: "2026-06-02"
date_collected: "2026-06-03"
summary_by: "auto-rss"
query: ""
---

# AWS Bedrock で GPT-5.5 を C# から使う

## はじめに

2026年6月1日、AWS が Amazon Bedrock で GPT-5.5 / GPT-5.4 / Codex を GA として提供開始しました。

https://aws.amazon.com/jp/blogs/machine-learning/openai-models-and-codex-on-amazon-bedrock-are-now-generally-available/

Bedrock では以前から Claude が使えていたので、「同じ Bedrock なら Claude Sonnet 4.6 も GPT-5.5 も同じように呼べるだろう」と思って C# で書き始めたのですが、これが思ったより一筋縄ではいきませんでした。

## まず Sonnet 4.6 を呼んでみる

Claude Sonnet 4.6 は `bedrock-runtime` の Converse API で呼び出せるので、`AWSSDK.Extensions.Bedrock.MEAI` パッケージを使えば、`IAmazonBedrockRuntime` から `Microsoft.Extensions.AI` の `IChatClient` に変換して利用するだけです。

```cs:sonnet.cs
#:package AWSSDK.Extensions.Bedrock.MEAI@4.0.8.6
#:package AWSSDK.SSO@4.0.3
#:package AWSSDK.SSOOIDC@4.0.4.2

using Amazon;
using Amazon.BedrockRuntime;
using Amazon.Runtime;
using Amazon.Runtime.CredentialManagement;
using Microsoft.Extensions.AI;


var awsProfileName = Environment.GetEnvironmentVariable("AWS_PROFILE") ?? "default";
var chain = new CredentialProfileStoreChain();
chain.TryGetAWSCredentials(awsProfileName, out var creds);
var bedrock = new AmazonBedrockRuntimeClient(creds, RegionEndpoint.APNortheast1);

// Converse API → IChatClient
var claude = bedrock.AsIChatClient("jp.anthropic.claude-sonnet-4-6");

var response = await claude.GetResponseAsync("C# の async/await を一言で説明してください。");
Console.WriteLine(response.Text);
```

```bash
# 事前に SSO ログイン（bedrock-runtime の呼び出しに必要）
aws sso login --profile your-sso-profile

dotnet run sonnet.cs
```

認証は AWS の標準的なクレデンシャルチェーン（環境変数、`~/.aws` のプロファイル、SSO など）に従います。プロファイルを明示したい場合は環境変数 `AWS_PROFILE` を設定しておけば OK です。

## GPT-5.5 は？

同じ調子で `AsIChatClient("openai.gpt-5.5")` と書きたくなるのですが、これは動きません。`AWSSDK.Extensions.Bedrock.MEAI`（v4）はまだ GPT-5.5 が使う `bedrock-mantle` に対応していないためです。

今回の例では、代わりに OpenAI .NET SDK を直接使います。まずは Bedrock API キー（Bearer トークン）で動かしてみましょう。

```csharp:gpt55.cs
#:package OpenAI@2.10.0
#:package Microsoft.Extensions.AI.OpenAI@10.6.0

#pragma warning disable OPENAI001  // ResponsesClient は experimental API

using OpenAI;
using OpenAI.Responses;
using Microsoft.Extensions.AI;
using System.ClientModel;

var apiKey = Environment.GetEnvironmentVariable("BEDROCK_API_KEY")!;

// GPT-5.5: bedrock-mantle の Responses API を OpenAI SDK 経由で呼ぶ
var responseClient = new OpenAIClient(
        new ApiKeyCredential(apiKey),
        new OpenAIClientOptions
        {
            Endpoint = new Uri("https://bedrock-mantle.us-east-2.api.aws/openai/v1/"),
        })
    .GetResponsesClient();

var gpt55 = responseClient.AsIChatClient("openai.gpt-5.5");

var response = await gpt55.GetResponseAsync("C# の async/await を一言で説明してください。");
Console.WriteLine(response.Text);
```

```bash
# Bedrock API キーを環境変数で渡す
export BEDROCK_API_KEY="<BEDROCK_API_KEY>"

dotnet run gpt55.cs
```

Sonnet 4.6 と比べると呼び出し側のコードはほぼ同じ形ですが、裏側の仕組みは大きく異なります。この違いについては次のセクションで整理します。

## 2 モデルの違いを整理する

Bedrockの各モデルがどのようなエンドポイントで提供されているか、どのようなAPIを持つかはモデルカードで確認できます。

https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-4-6.html

https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-oss-120b.html

https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-55.html

https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-54.html

表にしてみます

| | Claude Sonnet 4.6 | GPT-OSS-120B | GPT-5.5 | GPT-5.4 |
|---|---|---|---|---|
| **エンドポイント** | `bedrock-runtime` のみ | `bedrock-runtime` および `bedrock-mantle` | `bedrock-mantle` のみ | `bedrock-mantle` のみ |
| **Invoke API** | ✅ | ✅ | ❌ | ❌ |
| **Converse API** | ✅ | ✅ | ❌ | ❌ |
| **Chat Completions API** | ❌ | ✅ | ❌ | ❌ |
| **Responses API** | ❌ | ✅ | ✅ | ✅ |
| **MEAI アダプタ対応** | ✅ | ✅ | ❌ | ❌ |


Claude や GPT-OSS は `bedrock-runtime` の Converse API で呼べるので `AWSSDK.Extensions.Bedrock.MEAI` がそのまま使えます。ところが GPT-5.5 / GPT-5.4 はともに `bedrock-mantle` エンドポイントの Responses API 専用で、リージョンも `us-east-2`（オハイオ）固定です（現時点では東京リージョン等は非対応）。

なお GPT-OSS-120B は `bedrock-runtime` と `bedrock-mantle` の両エンドポイントに対応しているため、Converse / Invoke も使えます。ただし AWS ドキュメントでは可能な限り `bedrock-mantle` の利用を推奨しています。

`AWSSDK.Extensions.Bedrock.MEAI` は `IAmazonBedrockRuntime`（= `bedrock-runtime`）の拡張メソッドなので、`bedrock-mantle` には対応していません。そのため GPT-5.5 だけは OpenAI SDK を直接使う必要があります。

> 2026年6月時点の注記　`AWSSDK.BedrockRuntime`（v4 系）に `bedrock-mantle` / Responses API 用の型やクライアントは存在せず、GitHub（aws/aws-sdk-net）にも関連の Issue・PR はまだ立っていません。SDK 側が正式対応すれば、この記事の実装の一部は不要になるはずです。

ここまでで両モデルが動くことは確認できました。次のセクションでは、この 2 モデル（と GPT-OSS）を `IChatClient` という統一インターフェースに揃えて呼び出してみます。

## 3 モデルを IChatClient で統一する

`extensions-ai.cs` として保存します。Claude / GPT-OSS は `bedrock-runtime`、GPT-5.5 は `bedrock-mantle` と裏側のエンドポイントは違いますが、いったん `IChatClient` に変換してしまえば呼び出し側は同じコードで書けます。

```csharp:extensions-ai.cs
#:package AWSSDK.Extensions.Bedrock.MEAI@4.0.8.6
#:package AWSSDK.SSO@4.0.3
#:package AWSSDK.SSOOIDC@4.0.4.2
#:package OpenAI@2.10.0
#:package Microsoft.Extensions.AI.OpenAI@10.6.0

#pragma warning disable OPENAI001  // ResponsesClient は experimental API

using Amazon.BedrockRuntime;
using OpenAI;
using Microsoft.Extensions.AI;
using System.ClientModel;

var apiKey = Environment.GetEnvironmentVariable("BEDROCK_API_KEY")!;

// Claude / GPT-OSS: bedrock-runtime (Converse API)
var bedrock = new AmazonBedrockRuntimeClient();

// GPT-5.5: bedrock-mantle (Responses API)
var gpt55 = new OpenAIClient(
        new ApiKeyCredential(apiKey),
        new OpenAIClientOptions
        {
            Endpoint = new Uri("https://bedrock-mantle.us-east-2.api.aws/openai/v1/"),
        })
    .GetResponsesClient()
    .AsIChatClient("openai.gpt-5.5");

// どのモデルも IChatClient として同じヘルパーで扱える
await ChatAsync(bedrock.AsIChatClient("jp.anthropic.claude-sonnet-4-6"), "C# の async/await を一言で説明してください。");
await ChatAsync(bedrock.AsIChatClient("openai.gpt-oss-120b-1:0"),        "C# の async/await を一言で説明してください。");
await ChatAsync(gpt55,                                                   "C# の async/await を一言で説明してください。");

// ストリーミングも IChatClient で統一
await StreamingChatAsync(bedrock.AsIChatClient("jp.anthropic.claude-sonnet-4-6"), "AWS Bedrock の利点を 3 点挙げてください。");

// 1 回の問い合わせ
static async Task ChatAsync(IChatClient client, string prompt)
{
    var response = await client.GetResponseAsync(prompt);
    Console.WriteLine(response.Text);
}

//ストリーミング
static async Task StreamingChatAsync(IChatClient client, string prompt)
{
    await foreach (var update in client.GetStreamingResponseAsync(prompt))
    Console.Write(update.Text);
    Console.WriteLine();
}
```

```bash
export BEDROCK_API_KEY="<BEDROCK_API_KEY>"
aws sso login --profile your-sso-profile

dotnet run extensions-ai.cs
```

`ChatAsync` / `StreamingChatAsync` は単なる薄いヘルパーです。どのモデルでも `IChatClient` として同じ呼び出しになっている点に注目してください。

## ツール実行

`calltool.cs` として保存します。`ChatClientBuilder.UseFunctionInvocation()` を挟むだけで、どのモデルでもあらかじめ設定したツール呼び出しが動きます。

```csharp:calltool.cs
#:package AWSSDK.Extensions.Bedrock.MEAI@4.0.8.6
#:package AWSSDK.SSO@4.0.3
#:package AWSSDK.SSOOIDC@4.0.4.2
#:package OpenAI@2.10.0
#:package Microsoft.Extensions.AI@10.6.0
#:package Microsoft.Extensions.AI.OpenAI@10.6.0

#pragma warning disable OPENAI001  // ResponsesClient は experimental API

using Amazon.BedrockRuntime;
using OpenAI;
using Microsoft.Extensions.AI;
using System.ClientModel;
using System.ComponentModel;

var apiKey = Environment.GetEnvironmentVariable("BEDROCK_API_KEY")!;

var bedrock = new AmazonBedrockRuntimeClient();

var gpt55 = new OpenAIClient(
        new ApiKeyCredential(apiKey),
        new OpenAIClientOptions
        {
            Endpoint = new Uri("https://bedrock-mantle.us-east-2.api.aws/openai/v1/"),
        })
    .GetResponsesClient()
    .AsIChatClient("openai.gpt-5.5");

var tools = new[]
{
    AIFunctionFactory.Create(GetCurrentWeather),
    AIFunctionFactory.Create(CalculateTax),
};
var chatOptions = new ChatOptions { Tools = [.. tools] };

// Claude Sonnet 4.6 でエージェント実行
var claudeAgent = new ChatClientBuilder(bedrock.AsIChatClient("jp.anthropic.claude-sonnet-4-6"))
    .UseFunctionInvocation()
    .Build();
var r1 = await claudeAgent.GetResponseAsync(
    "東京の現在の天気を調べて、気温が20度以上なら消費税10%で1000円の税額を計算してください。", chatOptions);
Console.WriteLine(r1.Text);

// GPT-5.5 でも同じパターンで動く
var gpt55Agent = new ChatClientBuilder(gpt55)
    .UseFunctionInvocation()
    .Build();
var r2 = await gpt55Agent.GetResponseAsync(
    "東京と札幌の天気を調べて、気温差を教えてください。", chatOptions);
Console.WriteLine(r2.Text);

[Description("指定した都市の現在の天気と気温を返します。")]
static string GetCurrentWeather([Description("都市名（例: 東京, 大阪）")] string city)
    => $"{city} は晴れ、気温は 23 度です。";

[Description("指定した金額に対する消費税額を計算します。")]
static decimal CalculateTax(
    [Description("税抜き金額")] decimal amount,
    [Description("税率（例: 0.1 で 10%）")] decimal rate) => amount * rate;
```

```bash
export BEDROCK_API_KEY="<BEDROCK_API_KEY>"
aws sso login --profile your-sso-profile

dotnet run calltool.cs
```

ツール定義は `[Description]` 属性を付けたメソッドを `AIFunctionFactory.Create()` に渡すだけです。`UseFunctionInvocation()` がツール呼び出しと結果の差し戻しを自動でループしてくれるので、Claude でも GPT-5.5 でも呼び出し側のコードは変わりません。

## まとめ（API キー版）

`AWSSDK.Extensions.Bedrock.MEAI` の `AsIChatClient()` を使うことで、Claude や GPT-OSS のような Converse API 対応モデルは追加実装なしで `IChatClient` に変換できることが確認できました。

GPT-5.5 は `bedrock-mantle` の Responses API 専用という制約があり、現時点では OpenAI .NET SDK を直接使う必要がありますが、`IChatClient` に変換してしまえばその後は同じインターフェースで扱えます。Tool Calling も `UseFunctionInvocation()` を挟むだけで、Claude でも GPT-5.5 でも同じパターンで動きます。

ここまでが API キー（Bearer トークン）認証の実装です。次のセクションでは、本番運用で使いたくなる SSO（SigV4）認証への拡張を扱います。

## 拡張：SSO（SigV4）で呼び出す

Bedrock API キーは長期クレデンシャルのため、本番環境では SSO（SigV4）を使いたい場面もあります。Claude / GPT-OSS 側はクレデンシャルチェーンで自動的に SSO が効くので、ここで対応するのは GPT-5.5 だけです。

`bedrock-mantle` は `IAmazonBedrockRuntime` が対応していないため、OpenAI SDK の Transport に `DelegatingHandler` を差し込む形で SigV4 署名を自前で付与します。`sigv4.cs` として保存します。

```csharp:sigv4.cs
#:package AWSSDK.Extensions.Bedrock.MEAI@4.0.8.6
#:package AWSSDK.SSO@4.0.3
#:package AWSSDK.SSOOIDC@4.0.4.2
#:package OpenAI@2.10.0
#:package Microsoft.Extensions.AI.OpenAI@10.6.0

#pragma warning disable OPENAI001  // ResponsesClient は experimental API

using Amazon.BedrockRuntime;
using Amazon.BedrockRuntime.Model;
using Amazon.Runtime;
using Amazon.Runtime.CredentialManagement;
using Amazon.Runtime.Internal;
using Amazon.Runtime.Internal.Auth;
using Amazon.Runtime.Internal.Util;
using OpenAI;
using Microsoft.Extensions.AI;
using System.ClientModel;
using System.ClientModel.Primitives;
using System.Security.Cryptography;

const string region  = "us-east-2"; // オハイオ固定
var profile = Environment.GetEnvironmentVariable("AWS_PROFILE") ?? "default";

var chain = new CredentialProfileStoreChain();
chain.TryGetAWSCredentials(profile, out var credentials);

var httpClient = new HttpClient(new BedrockSigningHandler(credentials!, region));
var openAiOptions = new OpenAIClientOptions
{
    Endpoint  = new Uri($"https://bedrock-mantle.{region}.api.aws/openai/v1/"),
    Transport = new HttpClientPipelineTransport(httpClient),
};

// SigV4 認証なので ApiKeyCredential の値は使われない
var gpt55 = new OpenAIClient(new ApiKeyCredential("dummy"), openAiOptions)
    .GetResponsesClient()
    .AsIChatClient("openai.gpt-5.5");

var response = await gpt55.GetResponseAsync("C# の async/await を一言で説明してください。");
Console.WriteLine(response.Text);


// bedrock-mantle 向けに SigV4 署名を付与する DelegatingHandler
// SHA256 / HMAC は自前実装せず、AWS SDK 内部の AWS4Signer に委譲する
public class BedrockSigningHandler(AWSCredentials credentials, string region)
    : DelegatingHandler(new HttpClientHandler())
{
    private static readonly AWS4Signer Signer = new();
    private static readonly AmazonBedrockRuntimeConfig Config = new();

    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
    {
        var body        = request.Content is null ? [] : await request.Content.ReadAsByteArrayAsync(cancellationToken);
        var payloadHash = Convert.ToHexString(SHA256.HashData(body)).ToLowerInvariant();
        var internalRequest = new DefaultRequest(new ConverseRequest(), "bedrock")
        {
            HttpMethod           = request.Method.Method,
            Endpoint             = new Uri($"https://{request.RequestUri!.Host}"),
            ResourcePath         = request.RequestUri.AbsolutePath,
            Content              = body,
            AuthenticationRegion = region,
        };
        // AWS4Signer は x-amz-content-sha256 を internalRequest.Headers から読む
        internalRequest.Headers["x-amz-content-sha256"] = payloadHash;

        // クエリパラメーターを移送
        foreach (var param in request.RequestUri.Query.TrimStart('?').Split('&')
            .Where(p => p.Contains('=')).Select(p => p.Split('=', 2)))
            internalRequest.Parameters[Uri.UnescapeDataString(param[0])] = Uri.UnescapeDataString(param[1]);

        // AWS4Signer に署名させる（SigV4 の実装はすべて SDK に委譲）
        Config.AuthenticationRegion = region;
        var immutableCredentials = await credentials.GetCredentialsAsync();
        var signingResult = Signer.SignRequest(
            internalRequest, Config, new RequestMetrics(),
            immutableCredentials.AccessKey, immutableCredentials.SecretKey);

        // OpenAI SDK が付与した "Authorization: Bearer ..." を除去して SigV4 に差し替え
        request.Headers.Remove("Authorization");
        request.Headers.TryAddWithoutValidation("Authorization",         signingResult.ForAuthorizationHeader);
        request.Headers.TryAddWithoutValidation("x-amz-date",            signingResult.ISO8601DateTime);
        request.Headers.TryAddWithoutValidation("x-amz-content-sha256",  payloadHash);
        if (!string.IsNullOrEmpty(immutableCredentials.Token))
            request.Headers.TryAddWithoutValidation("x-amz-security-token", immutableCredentials.Token);

        return await base.SendAsync(request, cancellationToken);
    }
}
```

```bash
aws sso login --profile your-sso-profile

dotnet run sigv4.cs
```

OpenAI SDK は `Authorization: Bearer ...` を自動付与するため、最初に `Remove("Authorization")` してから SigV4 の値を設定し直しています。また `x-amz-content-sha256` を `internalRequest.Headers` にセットしておかないと、`AWS4Signer` が生成する Canonical String のペイロードハッシュが空になって署名不一致になります（ハマりポイントです）。

API キー版（`gpt55.cs`）との違いは、`OpenAIClientOptions.Transport` に署名用のハンドラーを挟んでいる点だけです。`IChatClient` に変換してしまえば、その後の呼び出しコードは Bearer 版とまったく同じになります。

## おわりに
Claude / GPT-OSS / GPT-5.5 を、すべて IChatClient という統一インターフェースで扱えることを確認しました。エンドポイントや API の違いは IChatClient に変換した時点で吸収され、Tool Calling まで含めて呼び出し側のコードは共通化できます。
GPT-5.5 だけは bedrock-mantle 専用で、現時点では OpenAI SDK の直接利用と SigV4 の自前署名が必要ですが、これは GA 直後で SDK の対応が追いついていない過渡期の話です。SDK が正式対応すれば不要になるはずです。
