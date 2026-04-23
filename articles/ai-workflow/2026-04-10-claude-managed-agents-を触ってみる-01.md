---
id: "2026-04-10-claude-managed-agents-を触ってみる-01"
title: "Claude Managed Agents を触ってみる"
url: "https://qiita.com/ny7760/items/07af9d3facaf4af3d9f2"
source: "qiita"
category: "ai-workflow"
tags: ["API", "AI-agent", "qiita"]
date_published: "2026-04-10"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

## はじめに

Anthropic が [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/quickstart) のパブリックβ版を公開しました。  
ざっくり言うと、エージェントのマネージドな実行環境を提供するサービスです。

コンソールからも数クリックで試せたので、試した記録を共有します。

## 前提

* Claude API でクレジットは購入済み  
  ※ Managed Agents はPro/Maxプランには含まれません。従量課金のみです。

## 手順

### エージェントの作成

* [Claude Console](https://platform.claude.com/) にアクセスすると Managed Agents のメニューが登場しています。Quickstart を選択すると、エージェントのテンプレートが選択できます。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F451175%2F5922fd83-1dd5-454b-abb0-a64fb72a15ee.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a92510205395dfb3c76b97ede88a9a3f)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F451175%2F5922fd83-1dd5-454b-abb0-a64fb72a15ee.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a92510205395dfb3c76b97ede88a9a3f)

いくつかピックアップして紹介します。今回は Deep researcher を選択しました。

| 名前 | 日本語訳 | 説明の日本語訳 |
| --- | --- | --- |
| Blank agent config | 空のエージェント | コアツールセットを備えた、何も設定されていない開始用テンプレート。 |
| Deep researcher | ディープリサーチ | 出典の整理と引用付きで、複数段階のウェブ調査を行う。 |
| Structured extractor | 構造化抽出 | 非構造テキストを、型付き JSON スキーマに沿って解析する。 |
| Field monitor | 情報監視 | 特定テーマについてソフトウェア関連ブログを巡回し、週ごとの変更点レポートを書く。 |
| Support agent | サポートエージェント | ドキュメントやナレッジベースをもとに顧客の質問に答え、必要に応じてエスカレーションする。 |
| Incident commander | インシデント司令役 | Sentry のアラートを振り分け、Linear の障害チケットを作成し、Slack の対応ルームを進行する。 |

* 選択すると、すぐに "Agent created" のメッセージが出ます。エージェントの作成プロセスは、チャットUIになっていますが、ボタンが表示されるのでポチポチ押すだけで進みます。
* Curlコマンドも表示されますが、特に実行する必要はありません。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F451175%2Fc8678e33-ae21-4b96-9ec2-c0b1c014bedd.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=67024b79931ac3c6d4a6b678cc60794a)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F451175%2Fc8678e33-ae21-4b96-9ec2-c0b1c014bedd.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=67024b79931ac3c6d4a6b678cc60794a)

選択したエージェントのYAML定義もコンソールに表示されます。

```
name: Deep researcher
description: Conducts multi-step web research with source synthesis and citations.
model: claude-sonnet-4-6
system: |-
  You are a research agent. Given a question or topic:

  1. Decompose it into 3-5 concrete sub-questions that, answered together, cover the topic.
  2. For each sub-question, run targeted web searches and fetch the most authoritative sources (prefer primary sources, official docs, peer-reviewed work over blog posts and aggregators).
  3. Read the sources in full — don't skim. Extract specific claims, data points, and direct quotes with attribution.
  4. Synthesize a report that answers the original question. Structure it by sub-question, cite every non-obvious claim inline, and close with a "confidence & gaps" section noting where sources disagreed or where you couldn't find good coverage.

  Be skeptical. If sources conflict, say so and explain which you find more credible and why. Don't paper over uncertainty with confident-sounding prose.
tools:
  - type: agent_toolset_20260401
metadata:
  template: deep-research
```

* Deep researcher のエージェントはWebアクセスを行うため、インターネットアクセスの許可設定も質問されます。"Unrestricted" を選択して進みます。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F451175%2F960c7761-ed0b-4b01-ac2f-61063d16d4e8.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=3bf6bbe706ae447e8f9f4b8d381c1259)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F451175%2F960c7761-ed0b-4b01-ac2f-61063d16d4e8.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=3bf6bbe706ae447e8f9f4b8d381c1259)

### セッション実行

* 環境の作成後、コンソールに従いポチポチ進めていくと、 "Session created" のメッセージが表示されます。これでセッションが開始され、エージェントにメッセージが送信できる状態になります。エージェントはここから待機中となるため、実行時間あたりの課金もここから始まると考えられます。（0.08ドル/1時間）
* 表示されるコマンドは、新しいセッションを作成するためのコマンドですが実行する必要はありません。Python版なども表示可能です。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F451175%2Fec8fd226-7f81-4efc-918e-8f9df4685ddf.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2f020bb7879f4fc8e89e80be847ec56f)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F451175%2Fec8fd226-7f81-4efc-918e-8f9df4685ddf.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2f020bb7879f4fc8e89e80be847ec56f)

* 右側のパネルでエージェントにメッセージを送信できます。
* メッセージを送ると、エージェントによるリサーチが始まります。Deep researchを使ったことがある人には馴染みのある挙動が確認できます。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F451175%2F5d15e98f-b710-4333-a3ca-f2cf4f6bbaae.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0bd575d9a1ed122c94c48f670c16c8eb)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F451175%2F5d15e98f-b710-4333-a3ca-f2cf4f6bbaae.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0bd575d9a1ed122c94c48f670c16c8eb)

* 右上の "View session" を押すと、Tool や思考プロセスのトレースが参照できます。こちらも、トレースツールを使ったことがある人には馴染みのあるUIかと思います。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F451175%2F5e337c7f-c3ad-455a-9264-2d791c13d27b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e1a2bacdf2b2978a0f153b1bb65249c3)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F451175%2F5e337c7f-c3ad-455a-9264-2d791c13d27b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e1a2bacdf2b2978a0f153b1bb65249c3)

### 停止

* 一通りの動作確認はできました。最後にセッションを忘れず停止しておきます。**セッションを停止しないと、従量課金が発生し続けることになります。**
* 停止時に、利用したエージェントを自分たちのアプリケーションから実行するための Scaffold として、サンプルコードが表示されます。このあたりは親切で面白いなと思いました。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F451175%2F4601170d-16c6-4970-a86b-07e64ab6909f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=04669bce48f407c448769bf83e0cd87d)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F451175%2F4601170d-16c6-4970-a86b-07e64ab6909f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=04669bce48f407c448769bf83e0cd87d)

サンプルコード

```
import anthropic

client = anthropic.Anthropic()

session = client.beta.sessions.create(
    agent={"type": "agent", "id": "agent_xxx"},
    environment_id="env_xxx",
    betas=["managed-agents-2026-04-01"],
)

with client.beta.sessions.events.stream(
    session_id=session.id,
    betas=["managed-agents-2026-04-01"],
) as stream:
    client.beta.sessions.events.send(
        session_id=session.id,
        events=[
            {
                "type": "user.message",
                "content": [{"type": "text", "text": "What are the most effective evidence-based interventions for improving sleep quality in adults?"}],
            },
        ],
        betas=["managed-agents-2026-04-01"],
    )

    for event in stream:
        if event.type == "agent.message":
            for block in event.content:
                print(block.text, end="")
        elif event.type == "agent.tool_use":
            print(f"\n[Using tool: {event.name}]")
        elif event.type == "session.status_idle":
            print("\n\nAgent finished.")
            break
```

* 利用したエージェントは、Claude Console から参照できます。再びセッションを開始することで、試すことができます。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F451175%2F0927cfaf-86ac-49eb-aff2-359d486df4c0.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=fcaba9c08ba114afaf69e142d9aaff26)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F451175%2F0927cfaf-86ac-49eb-aff2-359d486df4c0.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=fcaba9c08ba114afaf69e142d9aaff26)

## 所感

思っていた以上に、簡単にエージェントを起動することができました。LLM を試すというよりは、AWS や Google Cloud を触っている感覚に近かったです。（Bedrock の AgentCore Runtime と似た印象を受けました。）  
実際、Anthropic のインフラ上でエージェントが実行されるため、エージェントの実行基盤を提供する領域を獲得したいのかなと感じました。ただ、インフラの信頼度で言えば他のクラウドが圧倒している状況ですし、今後どのようにサービスをスケールさせたいのかは気になりました。

サクッとエージェントを動かしてみるには面白いサービスなので、ぜひ試してみてください。

## Managed Agents とは何なのか

Managed Agents のブログを読むと、「ハーネスはモデルの進化によって陳腐化していく」という考えが強く表現されています。実際、Claude Sonnet 4.5 利用時に用意したハーネス（コンテキストのリセット）が Opus 4.5 では不要になったとブログでは紹介されています。  
そのため、特定のハーネスに依存しないよう、ハーネスを自由に差し替えられるインターフェース（メタ構造）を設計したのが、Managed Agents のポイントと言えます。

実は過去の Anthropic ブログでも同様の考えは示されています。[Context engineering のブログ](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) にて、以下の通り「モデルの性能が向上するから、人間による介入を最小限としつつ、シンプルで効果的な方法を取るべき」という趣旨の記載があります。

> As model capabilities improve, agentic design will trend towards letting intelligent models act intelligently, with progressively less human curation. Given the rapid pace of progress in the field, "do the simplest thing that works" will likely remain our best advice for teams building agents on top of Claude.
>
> モデルの性能が向上するにつれ、エージェント設計の傾向は、人間による介入を最小限に抑えつつ、インテリジェントなモデルが自律的に判断を下せる方向へと進化していくでしょう。 この分野の進展が急速な現状を踏まえると、「最もシンプルで効果的な方法を採用する」というアプローチが、Claudeを基盤としたエージェント開発チームにとって今後も最善の指針となるでしょう（PLaMo翻訳）

以上から、Managed Agents は、**ハーネスが陳腐化するという思想のもと、「モデルが賢くなったら、ハーネスを薄くする」という運用を、ハーネスを差し替え可能にすることで継続的・低コストで実行できるようにした仕組み**と考えられます。

とは言っても、今回触ってみた中ではそこまで感じ取れませんでしたが、今後サービスを使う際にはそこを意識してみようと思います。

### 余談

Anthropic はモデル開発を行っているので、それを踏まえた主張という前提はあります。  
一方で、Claude Code の開発者が「Claude Codeはハーネスそのもの」という趣旨の発言をどこかでしていましたが、その発言通り、Anthropicはいま世界で最も使われているAIプロダクトのハーネスを開発している立場でもあります。

それを踏まえると、主張にも説得力があり面白いなと感じました。
