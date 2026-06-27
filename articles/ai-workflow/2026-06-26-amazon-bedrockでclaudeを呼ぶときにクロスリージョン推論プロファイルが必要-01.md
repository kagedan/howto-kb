---
id: "2026-06-26-amazon-bedrockでclaudeを呼ぶときにクロスリージョン推論プロファイルが必要-01"
title: "Amazon BedrockでClaudeを呼ぶときにクロスリージョン推論プロファイルが必要"
url: "https://zenn.dev/hknote/articles/bedrock-haiku-inference-profile"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-06-26"
date_collected: "2026-06-27"
summary_by: "auto-rss"
query: ""
---

Amazon BedrockでClaude Haikuを使おうとしたときに、モデルIDを直接指定して呼び出すことができませんでした。

エラーメッセージには、以下のような内容が表示されました。

```
Please use a cross-region inference profile.
On-demand throughput isn't supported.
```

結論としては、Claude Haikuを直接 `modelId` に指定するのではなく、**クロスリージョン推論プロファイル**を指定して呼び出す必要がありました。

## クロスリージョン推論プロファイルとは

Amazon Bedrockのクロスリージョン推論は、推論プロファイルを使ってリクエストを複数リージョンへルーティングする仕組みです。

AWS公式ドキュメントでは、推論プロファイルは基盤モデルとルーティング先リージョンを定義するリソースとして説明されています。  
呼び出し元リージョンからリクエストすると、Bedrock側がプロファイルに含まれる宛先リージョンの中から処理先を選びます。

今回の場合も、JPやAPACの複数リージョンのうち、利用可能なリージョンへリクエストを流す形にしました。  
こちらで毎回リージョンを選ぶというより、推論プロファイルに任せるイメージです。

## 呼び出し時は推論プロファイルを指定する

`InvokeModel` や `Converse` で呼び出す場合、モデルIDの代わりに推論プロファイルID、または推論プロファイルARNを指定します。

イメージとしては以下のような形です。

```
const response = await client.send(
  new ConverseCommand({
    modelId: "apac.anthropic.claude-xxx-haiku-xxxx-v1:0",
    messages: [
      {
        role: "user",
        content: [{ text: "こんにちは" }],
      },
    ],
  }),
);
```

実際の推論プロファイルIDは、利用するClaude Haikuのバージョンやリージョンによって変わります。  
AWSコンソール、モデル詳細ページ、または `GetInferenceProfile` で確認するのが安全です。

## IAMでハマったところ

今回ハマったのは、LambdaのIAMロールです。

最初は、東京リージョンから呼び出す推論プロファイルに対する権限だけを付ければよいと思っていました。  
しかし、それだけでは足りませんでした。

クロスリージョン推論プロファイルを使う場合、IAMロールには次の両方の権限が必要です。

* 呼び出す推論プロファイルに対する `bedrock:InvokeModel*`
* 推論先となる各リージョンのfoundation modelに対する `bedrock:InvokeModel*`

AWS公式ドキュメントにも、`Resource` に推論プロファイルを指定する場合は、そのプロファイルに関連する各リージョンのfoundation modelも指定する必要があると説明されています。

## 確認しておくこと

設定時には、以下を確認しておくとよさそうです。

* 呼び出し元リージョンで対象モデルへのアクセスが有効になっているか
* 使用する推論プロファイルIDが正しいか
* 推論プロファイルの宛先リージョンがどこか
* LambdaのIAMロールに、推論プロファイルと宛先foundation modelの両方への権限があるか

## まとめ

Claude HaikuをAmazon Bedrockで使うとき、モデルを直接指定すると以下のようなエラーになることがあります。

```
Please use a cross-region inference profile.
On-demand throughput isn't supported.
```

この場合は、モデルIDではなくクロスリージョン推論プロファイルを指定して呼び出します。

また、Lambdaから呼び出す場合は、推論プロファイルへの権限だけでなく、推論先となる各リージョンのfoundation modelへの実行権限も必要です。

今回の学びとしては、**Bedrockの推論プロファイルは呼び出し口だけ許可すればよいわけではなく、裏側でルーティングされるモデル側の権限も必要**ということでした。

## 参考
