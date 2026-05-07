---
id: "2026-05-06-microsoft-agent-framework-をローカルllmで試してみる-その13ミドルウェ-01"
title: "Microsoft Agent Framework をローカルLLMで試してみる その13(ミドルウェア)"
url: "https://zenn.dev/yy7613/articles/bb5fa8cdb6bf64"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "OpenAI", "GPT", "zenn"]
date_published: "2026-05-06"
date_collected: "2026-05-07"
summary_by: "auto-rss"
query: ""
---

## シリーズ一覧

一覧

## はじめに

Microsoft Agent FrameworkをローカルLLMで試してみるその12では、Structured Outputでモデル出力をJSON Schemaに合わせる方法を確認しました。

その13ではAgentにミドルウェアを設定する方法と設定した時の動作を確認します。

* ミドルウェアをどう登録して使うのか
* どの順序、どのタイミングで呼ばれるのか
* 呼ばれた時にどのようなステート、引数が渡されるのか

## 環境

Microsoft Agent Framework 1.3.0

## 今回確認するフロー

確認するフローは次のようになります。

## ミドルウェアの使い方

### ミドルウェアの一覧

このサンプルで確認するミドルウェアは次の5つです。

| 表記 | 登録先 | サンプルの実装 | 用途 |
| --- | --- | --- | --- |
| チャットクライアントミドルウェア | `IChatClient` | `LoggingChatClientMiddleware` | LLM呼び出し直前のリクエスト/レスポンスを確認する |
| チャットクライアントストリーミングミドルウェア | `IChatClient` | `LoggingChatClientStreamingMiddleware` | ストリーミング実行時のLLM呼び出しと更新件数を確認する |
| エージェント実行ミドルウェア | `AIAgent` | `LoggingAgentRunMiddleware` | 通常実行時のエージェント全体の入口と出口を確認する |
| エージェント実行ストリーミングミドルウェア | `AIAgent` | `LoggingAgentRunStreamingMiddleware` | ストリーミング実行時のエージェント全体と更新件数を確認する |
| 関数呼び出しミドルウェア | `AIAgent` | `LoggingFunctionCallingMiddleware` | ツール呼び出しごとの状態、引数、戻り値を確認する |

### ミドルウェアの登録

チャットクライアント（`IChatClient`）側とエージェント（`AIAgent`）側の両方にミドルウェアを登録します。

```
IChatClient middlewareEnabledChatClient = baseChatClient
    .AsBuilder()
    .Use(getResponseFunc: LoggingChatClientMiddleware, getStreamingResponseFunc: LoggingChatClientStreamingMiddleware)
    .Build();

AIAgent originalAgent = middlewareEnabledChatClient.AsAIAgent(new ChatClientAgentOptions
{
    Name = "MiddlewareSampleAgent",
    Description = "Agent Framework の middleware を確認するローカル実行サンプルです。",
    ChatOptions = new ChatOptions
    {
        Instructions = "あなたは簡潔に回答する assistant です。現在日時を尋ねられたら必ず GetDateTime を使って取得してください。",
        Tools =
        [
            AIFunctionFactory.Create(GetDateTime)
        ]
    }
});

AIAgent middlewareEnabledAgent = originalAgent
    .AsBuilder()
    .Use(runFunc: LoggingAgentRunMiddleware, runStreamingFunc: LoggingAgentRunStreamingMiddleware)
    .Use(LoggingFunctionCallingMiddleware)
    .Build();
```

チャットクライアントミドルウェア、エージェント実行ミドルウェア、関数呼び出しミドルウェアのそれぞれで値を確認します。

登録部分で出てくる変数は、次のように役割を分けています。

| 変数 | 表しているもの |
| --- | --- |
| baseChatClient | LM Studioに接続する素の`IChatClient` |
| middlewareEnabledChatClient | チャットクライアントミドルウェアを挟んだ`IChatClient` |
| originalAgent | チャットクライアントミドルウェアを登録した`IChatClient`から作成した、追加のミドルウェア適用前の`AIAgent` |
| middlewareEnabledAgent | エージェント実行ミドルウェアと関数呼び出しミドルウェアを挟んだ`AIAgent` |

## コンソール出力で確認する内容

このサンプルでは、ミドルウェアの動作をコンソール出力から次の観点で整理します。

### 実行オプション（RunOptions）の設定

ミドルウェアに渡される実行オプションの中身を確認するため、今回のサンプルでは実行単位に最大出力トークン数を変更しています。

```
static ChatClientAgentRunOptions CreateRunOptions(int maxOutputTokens)
{
    return new ChatClientAgentRunOptions(new ChatOptions
    {
        MaxOutputTokens = maxOutputTokens
    })
    {
        ChatClientFactory = static chatClient => chatClient
    };
}
```

```
ChatClientAgentRunOptions nonStreamingOptions = CreateRunOptions(maxOutputTokens: 1000);
ChatClientAgentRunOptions streamingOptions = CreateRunOptions(maxOutputTokens: 400);
```

通常実行では`1000`、ストリーミング実行では`400`を渡して実行時に差異が出るようにしています。

この設定は後半の実際のコンソール出力で、通常実行側の`AgentRunMiddleware`と`ChatClientMiddleware`に`maxTokens=1000`、ストリーミング実行側の`AgentRunStreamingMiddleware`と`ChatClientStreamingMiddleware`に`maxTokens=400`として反映されます。

### メッセージ本文（`ChatMessage.Contents`）の表示

チャット履歴を出力します。

```
static void DumpMessageSummary(string name, IEnumerable<ChatMessage> messages)
{
    List<ChatMessage> materializedMessages = messages.ToList();
    Console.WriteLine($"[{name}.Count] {materializedMessages.Count}");

    for (int index = 0; index < materializedMessages.Count; index++)
    {
        ChatMessage message = materializedMessages[index];
        Console.WriteLine($"[{name}[{index}]] {message.Role}: {FormatMessageContents(message)}");
    }
}

static string FormatContent(AIContent content)
{
    return content switch
    {
        TextContent textContent when !string.IsNullOrWhiteSpace(textContent.Text)
            => $"Text(\"{Preview(textContent.Text)}\")",
        TextContent => "Text(<empty>)",
        FunctionCallContent functionCall
            => $"FunctionCall({functionCall.Name}{FormatFunctionCallArguments(functionCall.Arguments)})",
        FunctionResultContent functionResult
            => $"FunctionResult({Preview(functionResult.Result?.ToString())})",
        _ => content.GetType().Name
    };
}
```

表示する値は次の通りです。

| 変数 | 内容 |
| --- | --- |
| name | どのミドルウェアの出力かを示すラベル |
| messages | ミドルウェアに渡された会話履歴 |
| materializedMessages | 複数回読み取れるようにリスト化した会話履歴 |
| index | 会話履歴の何番目のメッセージか |
| message | 1件分のチャットメッセージ |
| content | チャットメッセージ本文を構成する1要素 |

### ミドルウェアごとの要約出力

各ミドルウェアでは、必要な項目だけを文字列にまとめて出力しています。

```
static string FormatAgentRunOptionsSummary(AgentRunOptions? options)
{
    if (options is ChatClientAgentRunOptions chatClientOptions)
    {
        ChatOptions? chatOptions = chatClientOptions.ChatOptions;
        return $"{options.GetType().Name}(maxTokens={chatOptions?.MaxOutputTokens?.ToString() ?? "<null>"}, customFactory={chatClientOptions.ChatClientFactory is not null})";
    }

    return options?.GetType().Name ?? "<null>";
}

static string FormatChatOptionsSummary(ChatOptions? options)
{
    if (options is null)
    {
        return "options=<null>";
    }

    string instructions = string.IsNullOrWhiteSpace(options.Instructions)
        ? "<null>"
        : Preview(options.Instructions);

    return $"options=ChatOptions(maxTokens={options.MaxOutputTokens?.ToString() ?? "<null>"}, tools={options.Tools?.Count() ?? 0}, responseFormat={options.ResponseFormat is not null}, instructions=\"{instructions}\")";
}

static string FormatFunctionContextSummary(FunctionInvocationContext context)
{
    return $"function={context.Function.Name} iteration={context.Iteration} index={context.FunctionCallIndex}/{context.FunctionCount} messageCount={context.Messages.Count} isStreaming={context.IsStreaming} terminate={context.Terminate}";
}
```

チャット実行設定（`ChatOptions`）、エージェント実行設定（`AgentRunOptions`）、関数呼び出しの状態を確認します。

| 出力項目 | 意味 |
| --- | --- |
| 最大出力トークン数（`maxTokens`） | この実行でモデルに許可する最大出力トークン数 |
| ツール数（`tools`） | LLMに渡されているツール定義の数 |
| レスポンス形式指定（`responseFormat`） | Structured Outputなどの応答形式指定があるか |
| システム指示（`instructions`） | LLMに渡されるシステム側の指示 |
| カスタムファクトリ有無（`customFactory`） | 実行単位で`ChatClientFactory`が渡されているか |
| 反復回数（`iteration`） | 関数呼び出しループの何周目か |
| 呼び出し位置（`index`） | 同じ反復内で何番目の関数呼び出しか |
| メッセージ件数（`messageCount`） | その時点までに積み上がった会話履歴の件数 |
| 終了要求（`terminate`） | 関数呼び出し処理をここで終了する指定があるか |

後半の出力例では、これらの項目が`options=...`、`session=...`、`iteration=...`、`messageCount=...`のような形で表示されます。

## 実際のコンソール出力

ここからは、実際に出力された内容を見ながら、呼び出し順序と各ミドルウェアで出力される内容を整理します。

### 呼び出し順序がわかる出力

次の順序でミドルウェアが呼ばれることを実行して確認してみます。

1. エージェント実行ミドルウェアが最初に呼ばれる
2. その内部でチャットクライアントミドルウェアが呼ばれてLLMへリクエストが送られる
3. 関数呼び出しが返ると関数呼び出しミドルウェアが呼ばれる
4. ツール実行結果を含めて再度チャットクライアントミドルウェアが呼ばれる
5. 最終回答が返った後にエージェント実行ミドルウェアが終了する

#### 実行結果

```
[AgentRunMiddleware] session=ChatClientAgentSession(conversationId=<null>) options=ChatClientAgentRunOptions(maxTokens=1000, customFactory=True) innerAgent=FunctionInvocationDelegatingAgent(name=MiddlewareSampleAgent)
[AgentRunMiddleware.messages.Count] 1
[AgentRunMiddleware.messages[0]] user: Text("現在時刻を教えてください。")
```

```
[ChatClientMiddleware] options=ChatOptions(maxTokens=1000, tools=1, responseFormat=False, instructions="あなたは簡潔に回答する assistant です。現在日時を尋ねられたら必ず GetDateTi...") innerChatClient=OpenAIChatClient
[ChatClientMiddleware.messages.Count] 1
[ChatClientMiddleware.messages[0]] user: Text("現在時刻を教えてください。")
[ChatClientMiddleware.responseMessages.Count] 1
[ChatClientMiddleware.responseMessages[0]] assistant: Text(<empty>), FunctionCall(GetDateTime)
```

* 次にチャットクライアントミドルウェアが呼び出される

```
[FunctionMiddleware] agent=ChatClientAgent function=GetDateTime iteration=0 index=0/1 messageCount=2 isStreaming=False terminate=False arguments=<none>
[GetDateTime] called
[FunctionMiddleware] result GetDateTime => 2026-05-01 00:08:37 +09:00
```

* ToolCalling時に関数呼び出しミドルウェアが呼び出される

```
[ChatClientMiddleware] options=ChatOptions(maxTokens=1000, tools=1, responseFormat=False, instructions="あなたは簡潔に回答する assistant です。現在日時を尋ねられたら必ず GetDateTi...") innerChatClient=OpenAIChatClient
[ChatClientMiddleware.messages.Count] 3
[ChatClientMiddleware.messages[0]] user: Text("現在時刻を教えてください。")
[ChatClientMiddleware.messages[1]] assistant: Text(<empty>), FunctionCall(GetDateTime)
[ChatClientMiddleware.messages[2]] tool: FunctionResult(2026-05-01 00:08:37 +09:00)
[ChatClientMiddleware.responseMessages.Count] 1
[ChatClientMiddleware.responseMessages[0]] assistant: Text("現在の日時は **2026‑05‑01 00:08:37 +09:00** です。")
```

* 再度チャットクライアントミドルウェアが呼び出される

```
[AgentRunMiddleware.responseMessages.Count] 3
```

この出力結果から、次の構造で動いていることが分かります。

* エージェント実行ミドルウェアは最も外側
* チャットクライアントミドルウェアはLLM呼び出し単位
* 関数呼び出しミドルウェアはツール呼び出し単位

### ミドルウェアごとの出力例

次に、各ミドルウェアで実際に出力された内容を見ながら、受け取る値と確認ポイントを整理します。

#### エージェント実行ミドルウェア

通常実行の先頭では、`AgentRunMiddleware`に次の値が出力されていました。

ここでは、先ほど`nonStreamingOptions`に設定した`maxOutputTokens: 1000`が`options=ChatClientAgentRunOptions(maxTokens=1000, ...)`として反映されています。

```
[AgentRunMiddleware] session=ChatClientAgentSession(conversationId=<null>) options=ChatClientAgentRunOptions(maxTokens=1000, customFactory=True) innerAgent=FunctionInvocationDelegatingAgent(name=MiddlewareSampleAgent)
[AgentRunMiddleware.messages.Count] 1
[AgentRunMiddleware.messages[0]] user: Text("現在時刻を教えてください。")
```

ここから、次の点が分かります。

* 実行セッション（`session`）は`ChatClientAgentSession`として渡されていました
* 会話ID（`conversationId`）は今回のLM Studio構成では`null`でした
* 実行オプション（`options`）には実行単位で指定した最大出力トークン数（`maxTokens=1000`）が入っていました
* 次に呼び出されるエージェント（`innerAgent`）は関数呼び出しミドルウェアを含んだラッパーになっていました

#### チャットクライアントミドルウェア

1回目のLLM呼び出しでは、`ChatClientMiddleware`に次の値が入りました。

この出力では、先ほどの`nonStreamingOptions(maxOutputTokens: 1000)`が、マージ後の`ChatOptions(maxTokens=1000, ...)`として現れています。

```
[ChatClientMiddleware] options=ChatOptions(maxTokens=1000, tools=1, responseFormat=False, instructions="あなたは簡潔に回答する assistant です。現在日時を尋ねられたら必ず GetDateTi...") innerChatClient=OpenAIChatClient
[ChatClientMiddleware.messages.Count] 1
[ChatClientMiddleware.messages[0]] user: Text("現在時刻を教えてください。")
```

この出力から、最終的にLLMへ渡るチャット実行設定（`ChatOptions`）とメッセージ列が分かります。

関数呼び出し（function call）を挟んだ2回目の呼び出しでは、メッセージ列が次のように増えていきます。

```
[ChatClientMiddleware.messages[1]] assistant: Text(<empty>), FunctionCall(GetDateTime)
[ChatClientMiddleware.messages[2]] tool: FunctionResult(2026-04-30 21:05:04 +09:00)
```

アシスタントメッセージとツールメッセージは、テキスト本文（`Text`）が空でも、関数呼び出し内容（`FunctionCallContent`）や関数戻り値内容（`FunctionResultContent`）を持っています。

このミドルウェアの引数として見ておきたいのは次の点です。

* 会話メッセージ（`messages`）
* チャット実行設定（`options`）
* 次に呼び出されるチャットクライアント（`innerChatClient`）

#### 関数呼び出しミドルウェア

`GetDateTime`の呼び出し時には次のコンソール出力が出ました。

ここでは、直前のチャットクライアントミドルウェアが返した関数呼び出し結果が`FunctionInvocationContext`に反映され、`iteration`や`index`、`arguments`として出力されています。

```
[FunctionMiddleware] agent=ChatClientAgent function=GetDateTime iteration=0 index=0/1 messageCount=2 isStreaming=False terminate=False arguments=<none>
[FunctionMiddleware] result GetDateTime => 2026-04-30 21:05:04 +09:00
```

この出力から、次の点が分かります。

* どの関数（function）が呼ばれたか
* 関数呼び出しループ（function call loop）の何周目か
* その時点でメッセージ件数（`Messages.Count`）が何件か
* 関数引数に何が入っているか
* ツールの戻り値が何だったか

関数呼び出しミドルウェアでは、特に関数呼び出しコンテキスト（`FunctionInvocationContext`）の次の値が確認ポイントになります。

* 呼び出された関数（`Function`）
* 反復回数（`Iteration`）
* 呼び出し位置/呼び出し総数（`FunctionCallIndex` / `FunctionCount`）
* 会話状態（`Messages`）
* 関数引数（`Arguments`）

#### エージェント実行レスポンスとストリーミング

`AgentRunMiddleware`のレスポンス側では、最終レスポンス（`AgentResponse`）にアシスタント/ツール/アシスタントの3件が積み上がっていることが分かります。

```
[AgentRunMiddleware.responseMessages.Count] 3
[AgentRunMiddleware.responseMessages[0]] assistant: Text(<empty>), FunctionCall(GetDateTime)
[AgentRunMiddleware.responseMessages[1]] tool: FunctionResult(2026-05-01 00:08:37 +09:00)
[AgentRunMiddleware.responseMessages[2]] assistant: Text("現在の日時は **2026‑05‑01 00:08:37 +09:00** です。")
```

ストリーミング実行では、エージェント実行ストリーミングミドルウェアとチャットクライアントストリーミングミドルウェアで、最大出力トークン数（`maxTokens`）と更新件数（`update count`）が分かります。

ここでは、先ほど`streamingOptions`に設定した`maxOutputTokens: 400`が、両方のストリーミングミドルウェアで`maxTokens=400`として反映されています。

```
[AgentRunStreamingMiddleware] session=ChatClientAgentSession(conversationId=<null>) options=ChatClientAgentRunOptions(maxTokens=400, customFactory=True) innerAgent=FunctionInvocationDelegatingAgent(name=MiddlewareSampleAgent)
[AgentRunStreamingMiddleware.messages.Count] 1
[AgentRunStreamingMiddleware.messages[0]] user: Text("直前の回答を一文で要約してください。")
[ChatClientStreamingMiddleware] options=ChatOptions(maxTokens=400, tools=1, responseFormat=False, instructions="あなたは簡潔に回答する assistant です。現在日時を尋ねられたら必ず GetDateTi...") innerChatClient=OpenAIChatClient
[ChatClientStreamingMiddleware.messages.Count] 5
[ChatClientStreamingMiddleware.messages[0]] user: Text("現在時刻を教えてください。")
[ChatClientStreamingMiddleware.messages[1]] assistant: Text(<empty>), FunctionCall(GetDateTime)
[ChatClientStreamingMiddleware.messages[2]] tool: FunctionResult(2026-05-01 00:08:37 +09:00)
[ChatClientStreamingMiddleware.messages[3]] assistant: Text("現在の日時は **2026‑05‑01 00:08:37 +09:00** です。")
[ChatClientStreamingMiddleware.messages[4]] user: Text("直前の回答を一文で要約してください。")
[ChatClientStreamingMiddleware] update count: 141
[AgentRunStreamingMiddleware] update count: 141
[AgentRunStreamingMiddleware] response message count: 1
```

```
[Streaming update count] 141
[Streaming response]
現在の日時は2026‑05‑01 00:08:37 +09:00です。
```

エージェントの既定値を使わなくても、通常実行では`1000`、ストリーミング実行（streaming）では`400`を渡すことで、実行単位の設定差分がコールバックに反映されることが分かります。

## ソース

Program.cs

```
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using OpenAI;
using System.ClientModel;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Text;

Console.OutputEncoding = Encoding.UTF8;

const string endpoint = "http://localhost:1234/v1";
const string modelName = "openai/gpt-oss-20b";
const string apiKey = "sk-dummy";

Console.WriteLine("=== Microsoft Agent Framework Middleware Sample ===");
Console.WriteLine($"Endpoint: {endpoint}");
Console.WriteLine($"Model: {modelName}");

var clientOptions = new OpenAIClientOptions
{
    Endpoint = new Uri(endpoint)
};

var openAIClient = new OpenAIClient(new ApiKeyCredential(apiKey), clientOptions);

IChatClient baseChatClient = openAIClient
    .GetChatClient(modelName)
    .AsIChatClient();

IChatClient middlewareEnabledChatClient = baseChatClient
    .AsBuilder()
    .Use(getResponseFunc: LoggingChatClientMiddleware, getStreamingResponseFunc: LoggingChatClientStreamingMiddleware)
    .Build();

AIAgent originalAgent = middlewareEnabledChatClient.AsAIAgent(new ChatClientAgentOptions
{
    Name = "MiddlewareSampleAgent",
    Description = "Agent Framework の middleware を確認するローカル実行サンプルです。",
    ChatOptions = new ChatOptions
    {
        Instructions = "あなたは簡潔に回答する assistant です。現在日時を尋ねられたら必ず GetDateTime を使って取得してください。",
        Tools =
        [
            AIFunctionFactory.Create(GetDateTime)
        ]
    }
});

AIAgent middlewareEnabledAgent = originalAgent
    .AsBuilder()
    .Use(runFunc: LoggingAgentRunMiddleware, runStreamingFunc: LoggingAgentRunStreamingMiddleware)
    .Use(LoggingFunctionCallingMiddleware)
    .Build();

try
{
    AgentSession session = await middlewareEnabledAgent.CreateSessionAsync();
    ChatClientAgentRunOptions nonStreamingOptions = CreateRunOptions(maxOutputTokens: 1000);
    ChatClientAgentRunOptions streamingOptions = CreateRunOptions(maxOutputTokens: 400);

    Console.WriteLine();
    Console.WriteLine("=== Non-streaming run ===");
    AgentResponse response = await middlewareEnabledAgent.RunAsync("現在時刻を教えてください。", session, nonStreamingOptions);
    Console.WriteLine("[Non-streaming response]");
    Console.WriteLine(response);

    Console.WriteLine();
    Console.WriteLine("=== Streaming run ===");
    List<AgentResponseUpdate> updates = [];
    await foreach (AgentResponseUpdate update in middlewareEnabledAgent.RunStreamingAsync("直前の回答を一文で要約してください。", session, streamingOptions))
    {
        updates.Add(update);
    }

    Console.WriteLine($"[Streaming update count] {updates.Count}");
    Console.WriteLine("[Streaming response]");
    Console.WriteLine(updates.ToAgentResponse());
}
catch (Exception ex)
{
    Console.WriteLine();
    Console.WriteLine("実行時に推論バックエンドへ接続できませんでした。LM Studio などの OpenAI 互換エンドポイントを起動してから再実行してください。");
    Console.WriteLine(ex.Message);
}

[Description("現在の日時を取得します。")]
static string GetDateTime()
{
    Console.WriteLine("[GetDateTime] called");
    return DateTimeOffset.Now.ToString("yyyy-MM-dd HH:mm:ss zzz");
}

static ChatClientAgentRunOptions CreateRunOptions(int maxOutputTokens)
{
    return new ChatClientAgentRunOptions(new ChatOptions
    {
        MaxOutputTokens = maxOutputTokens
    })
    {
        ChatClientFactory = static chatClient => chatClient
    };
}

static async Task<ChatResponse> LoggingChatClientMiddleware(
    IEnumerable<ChatMessage> messages,
    ChatOptions? options,
    IChatClient innerChatClient,
    CancellationToken cancellationToken)
{
    List<ChatMessage> materializedMessages = messages.ToList();

    Console.WriteLine($"[ChatClientMiddleware] {FormatChatOptionsSummary(options)} innerChatClient={innerChatClient.GetType().Name}");
    DumpMessageSummary("ChatClientMiddleware.messages", materializedMessages);

    ChatResponse response = await innerChatClient.GetResponseAsync(materializedMessages, options, cancellationToken);

    DumpMessageSummary("ChatClientMiddleware.responseMessages", response.Messages);

    return response;
}

static async IAsyncEnumerable<ChatResponseUpdate> LoggingChatClientStreamingMiddleware(
    IEnumerable<ChatMessage> messages,
    ChatOptions? options,
    IChatClient innerChatClient,
    [EnumeratorCancellation] CancellationToken cancellationToken)
{
    List<ChatMessage> materializedMessages = messages.ToList();

    Console.WriteLine($"[ChatClientStreamingMiddleware] {FormatChatOptionsSummary(options)} innerChatClient={innerChatClient.GetType().Name}");
    DumpMessageSummary("ChatClientStreamingMiddleware.messages", materializedMessages);

    var updateCount = 0;
    await foreach (ChatResponseUpdate update in innerChatClient.GetStreamingResponseAsync(materializedMessages, options, cancellationToken))
    {
        updateCount++;
        yield return update;
    }

    Console.WriteLine($"[ChatClientStreamingMiddleware] update count: {updateCount}");
}

static async Task<AgentResponse> LoggingAgentRunMiddleware(
    IEnumerable<ChatMessage> messages,
    AgentSession? session,
    AgentRunOptions? options,
    AIAgent innerAgent,
    CancellationToken cancellationToken)
{
    List<ChatMessage> materializedMessages = messages.ToList();

    Console.WriteLine($"[AgentRunMiddleware] session={FormatSessionSummary(session)} options={FormatAgentRunOptionsSummary(options)} innerAgent={FormatAgentSummary(innerAgent)}");
    DumpMessageSummary("AgentRunMiddleware.messages", materializedMessages);

    AgentResponse response = await innerAgent.RunAsync(materializedMessages, session, options, cancellationToken);

    DumpMessageSummary("AgentRunMiddleware.responseMessages", response.Messages);

    return response;
}

static async IAsyncEnumerable<AgentResponseUpdate> LoggingAgentRunStreamingMiddleware(
    IEnumerable<ChatMessage> messages,
    AgentSession? session,
    AgentRunOptions? options,
    AIAgent innerAgent,
    [EnumeratorCancellation] CancellationToken cancellationToken)
{
    List<ChatMessage> materializedMessages = messages.ToList();

    Console.WriteLine($"[AgentRunStreamingMiddleware] session={FormatSessionSummary(session)} options={FormatAgentRunOptionsSummary(options)} innerAgent={FormatAgentSummary(innerAgent)}");
    DumpMessageSummary("AgentRunStreamingMiddleware.messages", materializedMessages);

    List<AgentResponseUpdate> updates = [];
    await foreach (AgentResponseUpdate update in innerAgent.RunStreamingAsync(materializedMessages, session, options, cancellationToken))
    {
        updates.Add(update);
        yield return update;
    }

    Console.WriteLine($"[AgentRunStreamingMiddleware] update count: {updates.Count}");
    Console.WriteLine($"[AgentRunStreamingMiddleware] response message count: {updates.ToAgentResponse().Messages.Count}");
}

static async ValueTask<object?> LoggingFunctionCallingMiddleware(
    AIAgent agent,
    FunctionInvocationContext context,
    Func<FunctionInvocationContext, CancellationToken, ValueTask<object?>> next,
    CancellationToken cancellationToken)
{
    Console.WriteLine($"[FunctionMiddleware] agent={agent.GetType().Name} {FormatFunctionContextSummary(context)} arguments={FormatArguments(context.Arguments)}");

    object? result = await next(context, cancellationToken);

    Console.WriteLine($"[FunctionMiddleware] result {context.Function.Name} => {FormatScalar(result)}");

    return result;
}

static void DumpMessageSummary(string name, IEnumerable<ChatMessage> messages)
{
    List<ChatMessage> materializedMessages = messages.ToList();
    Console.WriteLine($"[{name}.Count] {materializedMessages.Count}");

    for (int index = 0; index < materializedMessages.Count; index++)
    {
        ChatMessage message = materializedMessages[index];
        Console.WriteLine($"[{name}[{index}]] {message.Role}: {FormatMessageContents(message)}");
    }
}

static string FormatMessageContents(ChatMessage message)
{
    if (message.Contents.Count == 0)
    {
        return "<no content>";
    }

    return string.Join(", ", message.Contents.Select(FormatContent));
}

static string FormatContent(AIContent content)
{
    return content switch
    {
        TextContent textContent when !string.IsNullOrWhiteSpace(textContent.Text) => $"Text(\"{Preview(textContent.Text)}\")",
        TextContent => "Text(<empty>)",
        FunctionCallContent functionCall => $"FunctionCall({functionCall.Name}{FormatFunctionCallArguments(functionCall.Arguments)})",
        FunctionResultContent functionResult => $"FunctionResult({Preview(functionResult.Result?.ToString())})",
        UriContent uriContent => $"Uri({uriContent.Uri})",
        DataContent dataContent => $"Data({dataContent.MediaType ?? "unknown"})",
        _ => content.GetType().Name
    };
}

static string FormatSessionSummary(AgentSession? session)
{
    if (session is null)
    {
        return "<null>";
    }

    string conversationId = session is ChatClientAgentSession chatClientSession
        ? chatClientSession.ConversationId ?? "<null>"
        : "<not available>";

    return $"{session.GetType().Name}(conversationId={conversationId})";
}

static string FormatAgentRunOptionsSummary(AgentRunOptions? options)
{
    if (options is null)
    {
        return "<null>";
    }

    if (options is ChatClientAgentRunOptions chatClientOptions)
    {
        ChatOptions? chatOptions = chatClientOptions.ChatOptions;
        return $"{options.GetType().Name}(maxTokens={chatOptions?.MaxOutputTokens?.ToString() ?? "<null>"}, customFactory={chatClientOptions.ChatClientFactory is not null})";
    }

    return options.GetType().Name;
}

static string FormatChatOptionsSummary(ChatOptions? options)
{
    if (options is null)
    {
        return "options=<null>";
    }

    string instructions = string.IsNullOrWhiteSpace(options.Instructions)
        ? "<null>"
        : Preview(options.Instructions);

    return $"options=ChatOptions(maxTokens={options.MaxOutputTokens?.ToString() ?? "<null>"}, tools={options.Tools?.Count() ?? 0}, responseFormat={options.ResponseFormat is not null}, instructions=\"{instructions}\")";
}

static string FormatAgentSummary(AIAgent agent)
{
    return $"{agent.GetType().Name}(name={agent.Name})";
}

static string FormatFunctionContextSummary(FunctionInvocationContext context)
{
    return $"function={context.Function.Name} iteration={context.Iteration} index={context.FunctionCallIndex}/{context.FunctionCount} messageCount={context.Messages.Count} isStreaming={context.IsStreaming} terminate={context.Terminate}";
}

static string FormatArguments(IEnumerable<KeyValuePair<string, object?>> arguments)
{
    List<KeyValuePair<string, object?>> items = arguments.ToList();
    if (items.Count == 0)
    {
        return "<none>";
    }

    return string.Join(", ", items.Select(item => $"{item.Key}={FormatScalar(item.Value)}"));
}

static string FormatFunctionCallArguments(IDictionary<string, object?>? arguments)
{
    if (arguments is null || arguments.Count == 0)
    {
        return string.Empty;
    }

    string formatted = string.Join(", ", arguments.Select(item => $"{item.Key}={FormatScalar(item.Value)}"));
    return $": {formatted}";
}

static string FormatScalar(object? value)
{
    if (value is null)
    {
        return "<null>";
    }

    return value switch
    {
        string text => Preview(text),
        _ => Preview(value.ToString())
    };
}

static string Preview(string? text, int maxLength = 48)
{
    if (string.IsNullOrWhiteSpace(text))
    {
        return "<empty>";
    }

    string normalized = text.Replace("\r", " ").Replace("\n", " ").Trim();
    return normalized.Length <= maxLength
        ? normalized
        : normalized[..maxLength] + "...";
}
```

## まとめ

このサンプルではミドルウェアの登録方法と挙動、呼び出し順序、確認すべきステートを整理しました。

* ミドルウェアは`IChatClient`側と`AIAgent`側に登録できる。
* 実行の呼び出し順序は「エージェント実行 → チャットクライアント → 関数呼び出し → 再度チャットクライアント → エージェント実行」の順番となる。
