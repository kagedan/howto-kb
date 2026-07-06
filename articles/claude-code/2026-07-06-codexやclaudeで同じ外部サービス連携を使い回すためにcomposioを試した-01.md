---
id: "2026-07-06-codexやclaudeで同じ外部サービス連携を使い回すためにcomposioを試した-01"
title: "CodexやClaudeで同じ外部サービス連携を使い回すためにComposioを試した"
url: "https://zenn.dev/straydog/articles/8f8a5dd8a84a2f"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "OpenAI"]
date_published: "2026-07-06"
date_collected: "2026-07-07"
summary_by: "auto-rss"
query: ""
---

# はじめに

GitHub は Claude Code では使えるのに、Codex ではまだ設定していない。Slack は別の MCP サーバーを入れていて、Gmail は認証が途中で止まっている。

複数の LLM ツールを使い分けていると、こういう小さなズレが増えていきます。

Codex や Claude Code など、それぞれのツール自体は便利です。一方で、外部サービス連携を増やしていくと、MCP の設定や認証情報の管理がだんだん面倒になります。

たとえば GitHub、Slack、Gmail、Notion などを使いたい場合、LLM ツールごとに MCP サーバーを設定したり、認証を通したり、どの環境で何が使えるのかを把握したりする必要があります。

このあたりをまとめて扱えるサービスとして Composio を触ってみたところ、単に「たくさんの SaaS とつながる」以上の便利さを感じました。

この記事では、Composioを触った感想やドキュメントの内容をまとめていきます。

<https://composio.dev/>

# Composio とは

Composio は、AI エージェントから外部サービスを扱うための接続 Platform です。

公式ドキュメントでは、AI エージェントに 1000 以上の toolkits、ユーザー単位の認証、triggers、sandbox などを提供するものとして説明されています。

Gmail、Slack、GitHub、Notion などの外部サービスを、AI エージェントからツールとして呼び出せるようにするための基盤、と捉えるとわかりやすいです。

使い方はいくつかあります。

* SDK からツールを呼び出す
* MCP endpoint として LLM ツールに接続する
* CLI から検索、認証、実行を行う
* Triggers を使って外部サービスのイベントを受け取る

個人的に面白いと感じたのは、Composio を個別の MCP サーバーとして見るよりも、LLM ツール横断の外部サービス接続 Platform として見ると価値がわかりやすい点です。

# Platform として見ると価値がわかりやすい

Composio の便利さは、単に MCP サーバーを増やせることではないと思っています。

むしろ価値があるのは、MCP と外部サービス認証を LLM ツールから切り離して、Composio 側で管理できることです。

LLM ツールは今後も増えると思います。Codex が得意な場面もあれば、Claude Code が使いやすい場面もあります。Cursor のようにエディタに深く統合された体験が合う場面もあります。

そのたびに GitHub、Slack、Gmail、Notion などの接続を個別に設定していくのはつらいです。

Composio を Platform として挟むと、LLM ツールは使い分けつつ、外部サービス連携は一箇所に寄せる、という構成が取りやすくなります。

この体験は、複数の LLM ツールを日常的に使っている人ほど刺さると思います。

# 何が便利だったのか

## LLM ツールごとに MCP 設定を持たなくてよい

Codex、Claude Code、Cursor、Claude Desktop などを併用していると、MCP 設定がツールごとに散らばりがちです。

GitHub は Claude Code 側に設定しているけれど、Codex 側にはまだ入れていない。Slack は別の MCP サーバーを使っている。Gmail は認証が途中で止まっている。

こうした状態になると、便利なはずのエージェント環境が、だんだん設定管理の対象になっていきます。

Composio を挟むと、外部サービスとの接続を Composio 側に寄せられます。LLM ツール側では Composio の MCP endpoint を参照し、Composio 側で GitHub や Slack などの接続を管理する、という形にできます。

これは「どの LLM ツールを使うか」と「どの外部サービスに接続するか」を分離できる、ということです。

この分離がかなり体験として良いです。

LLM ツールは用途によって使い分けたい。一方で、外部サービス連携は毎回作り直したくない。Composio はこの間に入って、接続の再利用をしやすくしてくれます。

## プロジェクトごとに設定を分けられる

もう一つ良いと感じたのが、Composio の Platform としての管理単位です。

公式ドキュメントでは、Composio の Project は organization の中にある分離された環境として説明されています。Project ごとに API keys、connected accounts、auth configs、webhook configurations が scope され、別 Project のリソースにはアクセスできないとされています。

これにより、たとえば次のように用途ごとに接続を分けられます。

* 仕事用 Project では GitHub、Slack、Linear を使う
* 個人開発用 Project では GitHub、Notion、Gmail を使う
* 記事執筆用 Project では Google Drive や Notion だけを使う
* 検証用 Project では一時的な接続だけを試す

複数の LLM ツールを使っていると、「どのツールに何を設定したか」だけでなく、「この作業ではどの外部サービスにアクセスしてよいのか」も曖昧になりがちです。

Project 単位で分けておくと、LLM ツール側ではなく、外部サービス接続側を中心に管理できます。

これは安全面でも運用面でもわかりやすいです。

## SDK 経由で MCP endpoint を作れる

Composio は SDK から session を作り、その session に対応する MCP endpoint を取得できます。

公式ドキュメントでは、session 作成時に `mcp: true` を渡し、`session.mcp.url` と `session.mcp.headers` を参照する例が紹介されています。

```
import { Composio } from "@composio/core";

const composio = new Composio();

const session = await composio.create("user_123", {
  mcp: true,
  toolkits: ["github", "slack"],
});

const mcpUrl = session.mcp.url;
const mcpHeaders = session.mcp.headers;
```

この形にできると、MCP 設定を完全に手作業で管理するのではなく、コード側で「どの user に、どの toolkits を使わせるか」を表現できます。

また、Project ごとに API key を分けておけば、開発用、検証用、本番用のように Composio 側の接続環境も分離しやすくなります。

個人利用でも便利ですが、チームやプロダクトに組み込むことを考えると、この「コードで MCP endpoint を生成できる」点はかなり重要だと思いました。

## OpenAI Agents SDK にも渡せる

Composio は OpenAI Agents SDK 向けの provider も用意しています。

MCP endpoint を直接扱う場合は `HostedMCPTool` に渡す形になりますが、Agents SDK と Composio SDK を組み合わせるだけなら、`session.tools()` を `Agent` に渡す書き方のほうがシンプルです。

```
from agents import Agent
from composio import Composio
from composio_openai_agents import OpenAIAgentsProvider

composio = Composio(provider=OpenAIAgentsProvider())

session = composio.create(
    user_id="user_123",
    toolkits=["github", "slack"],
)

agent = Agent(
    name="Assistant",
    tools=session.tools(),
)
```

この場合は、OpenAI Agents SDK の実行ループに、Composio 側で整形された tools を渡す形になります。MCP endpoint の URL を意識しなくてよいので、アプリケーションに組み込むならこちらのほうが見通しが良さそうです。

一方で、Composio の MCP endpoint を明示的に OpenAI Agents SDK の hosted MCP tool として渡したい場合は、次のように `session.mcp.url` と `session.mcp.headers` を使います。

```
from agents import Agent, HostedMCPTool

composio_mcp_tool = HostedMCPTool(
    tool_config={
        "type": "mcp",
        "server_label": "composio",
        "server_url": session.mcp.url,
        "headers": session.mcp.headers,
        "require_approval": "never",
    }
)

agent = Agent(
    name="Assistant",
    tools=[composio_mcp_tool],
)
```

LLM ツール側に手で MCP 設定を書く使い方だけでなく、アプリケーションコード側で session を作り、その MCP endpoint を Agents SDK に渡すこともできます。

つまり、個人の作業環境では Codex や Claude Code から使い、プロダクト側では OpenAI Agents SDK から同じように接続する、といった構成も考えやすくなります。

## Triggers で外部サービス側のイベントも受けられる

Composio は、LLM から外部サービスを操作するだけでなく、外部サービス側で起きたイベントを受け取る Triggers も提供しています。

たとえば、GitHub の commit、Slack の message、Gmail の新着メールなどを trigger として受け取り、自分のアプリケーションの webhook に流せます。

MCP や tools が「AI から外部サービスへ操作する口」だとすると、Triggers は「外部サービスから AI / アプリケーション側へイベントを持ち込む入口」として使えます。

公式ドキュメントでは、Trigger は大きく `trigger type` と `trigger instance` に分けて説明されています。

| 概念 | 説明 |
| --- | --- |
| Trigger type | `GITHUB_COMMIT_EVENT` のようなイベント種別。toolkit ごとに用意され、必要な config が決まっている |
| Trigger instance | 特定 user / connected account に対して有効化された trigger。`ti_*` ID を持ち、enable / disable / delete できる |
| Webhook subscription | Composio がイベントを送る先の URL、署名 secret、受信する event type の設定 |

また、イベントの検知方法には realtime と polling があります。

| 種類 | 仕組み | レイテンシ | 例 |
| --- | --- | --- | --- |
| Realtime | provider が Composio に push | ほぼ即時 | Slack, Asana, Notion, Outlook |
| Polling | Composio が provider を定期確認 | 最大約 15 分 | Gmail, Google Calendar |

trigger の作成は、対象 toolkit の connected account を用意したうえで、trigger type を確認し、必要な config を渡して行います。

```
import { Composio } from "@composio/core";

const composio = new Composio();

const triggerType = await composio.triggers.getType("GITHUB_COMMIT_EVENT");
console.log(triggerType.config);

const trigger = await composio.triggers.create("user-id-123435", "GITHUB_COMMIT_EVENT", {
  triggerConfig: {
    owner: "your-repo-owner",
    repo: "your-repo-name",
  },
});

console.log(`Trigger created: ${trigger.triggerId}`);
```

受信側は、開発中であれば `subscribe()` でイベントを見ることもできますが、本番では webhook handler を用意し、署名検証したうえで payload を処理するのが基本です。

本番での受け手側は、たとえば次のような構成になります。

1. 自分のアプリケーションに `/webhooks/composio` のような公開 endpoint を用意する
2. Composio の webhook subscription にその URL を登録する
3. handler で `COMPOSIO_WEBHOOK_SECRET` を使って署名検証する
4. `triggerSlug` や `rawPayload.type` を見て、GitHub commit、Slack message、Gmail 新着などの処理に振り分ける
5. 重い処理はその場で実行せず、queue や background job に渡す

Next.js の Route Handler で書くなら、イメージは次のようになります。

```
// app/api/webhooks/composio/route.ts
import { Composio } from "@composio/core";

const composio = new Composio();

export async function POST(request: Request) {
  const result = await composio.triggers.parse(request, {
    verifySecret: process.env.COMPOSIO_WEBHOOK_SECRET,
  });

  if (result.rawPayload.type !== "composio.trigger.message") {
    return Response.json({ status: "ignored" });
  }

  const event = result.payload;

  if (event.triggerSlug === "GITHUB_COMMIT_EVENT") {
    const data = event.payload;

    // ここで直接 LLM を呼ぶより、queue に積むほうが本番運用では扱いやすいです。
    console.log("commit:", data);
  }

  return Response.json({ status: "ok" });
}
```

つまり、Composio が GitHub や Slack などの provider 側のイベントを受け取り、自分のアプリケーションには正規化された webhook payload として届けてくれる、という役割分担です。

Project ごとに webhook 設定も分離できるため、ここでも Composio を Platform として扱うメリットがあります。

# 注意点

便利な一方で、いくつか注意点もあります。

## Webhook endpoint は署名検証で守る

Triggers の webhook endpoint は公開 URL になるので少し不安になりますが、この場合は IP 制限やドメイン制限ではなく、署名検証で守るのが基本です。

公式ドキュメントでも、Composio の outbound IP は dynamic なので、IP allowlist や VPN-only endpoint は向かないと説明されています。つまり、公開 URL として受けつつ、Composio から送られてきた正当な payload かどうかを `COMPOSIO_WEBHOOK_SECRET` で検証する形になります。

実運用では、署名検証に加えて次のような対策を組み合わせるのがよさそうです。

* HTTPS の endpoint にする
* `POST` 以外を拒否する
* request body の size limit を設定する
* `COMPOSIO_WEBHOOK_SECRET` をサーバー側の secret として管理する
* `parse()` の `verifySecret` で署名検証に通った payload だけ処理する
* WAF や API Gateway で rate limit をかける
* `webhook-id` などを使って重複処理を避ける
* 重い処理は queue や background job に渡し、handler は早めに `200` を返す

ドメインや `Origin` header を見ることは補助的なチェックにはなりますが、それだけで webhook の信頼判定をするのは弱いです。Composio の webhook は、署名検証を中心に守るものとして考えるのが自然だと思います。

## MCP は Sessions 前提で見る

Composio には MCP server config を作成、更新、削除する API もあります。

ただし、これから使う場合は `composio.create(..., { mcp: true })` で session を作り、そこから MCP endpoint を取得する形を前提にしたほうがよさそうです。

## CLI は便利だが、用途を分けたほうがよい

Composio CLI は、ローカルで接続状況を見たり、ツールを検索したり、実行を試したりするのに便利です。

一方で、公式ドキュメントでは、安定した production integration には SDK や API を使うことが推奨されています。

CLI は開発や検証の補助として使い、アプリケーションに組み込む場合は SDK/API を使う、という整理が良さそうです。

## Rate limit は Composio 側と接続先側の両方を見る

Composio には API 全体の rate limit があります。

公式ドキュメントでは、組織単位の固定 1 分ウィンドウで、プランごとに次のように説明されています。

| Plan | Rate limit | Window |
| --- | --- | --- |
| Starter | 2,000 requests | 1 minute |
| Hobby | 2,000 requests | 1 minute |
| Growth | 10,000 requests | 1 minute |
| Enterprise | Custom | - |

また、Pro tools は標準 tool calls より制限が低く、spending tier ごとに次のように説明されています。

| Spending tier | Standard tool calls | Pro tool calls |
| --- | --- | --- |
| Free | 100/min | 1,000/hour |
| Paid | 5,000/min | 10,000/hour |
| Enterprise | Custom | Custom |

さらに GitHub や Google など、接続先サービス側の rate limit に当たることもあります。

Composio 経由だから rate limit を意識しなくてよい、というわけではなく、Composio 側と upstream 側の両方を見る必要があります。

# おわりに

Composio を触ってみて一番便利だと感じたのは、MCP や外部サービス連携を LLM ツールごとに抱えなくてよい点でした。

Codex、Claude Code、Cursor などを使い分ける場合、LLM ツール自体は用途に応じて選びたいです。一方で、GitHub や Slack などの外部サービス接続は毎回作り直したくありません。

Composio を挟むことで、LLM ツールと外部サービス接続を分離できます。

さらに Project 単位で接続や API key を分けられるため、仕事用、個人開発用、検証用のように用途ごとの管理もしやすくなります。

Composio は「MCP を増やすためのサービス」というより、複数の LLM ツールを使う時代の外部サービス接続 Platform として見ると、かなり納得感がありました。

今後は、Project 単位での権限分離や、SDK 経由での MCP endpoint 生成をもう少し試していきたいです。

# 参考
