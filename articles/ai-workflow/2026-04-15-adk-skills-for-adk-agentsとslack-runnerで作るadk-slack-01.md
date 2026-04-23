---
id: "2026-04-15-adk-skills-for-adk-agentsとslack-runnerで作るadk-slack-01"
title: "[ADK] Skills for ADK agentsとSlack Runnerで作るADK Slack Bot"
url: "https://zenn.dev/soundtricker/articles/73b9ec4d486d29"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "Python", "zenn"]
date_published: "2026-04-15"
date_collected: "2026-04-16"
summary_by: "auto-rss"
query: ""
---

こんにちは、サントリーこと大橋です。

前回の 1.21.0 の記事から、だいぶ間が空いてしまいました...。  
ADK のアップデートが激しすぎて、キャッチアップ記事を書くのが難しかったことをお詫びします。ゴメンネ...

さて、2026/03/26 に **Agent Development Kit (ADK) 1.28.0** がリリースされました。  
さらに 2026/04/02 にはマイナーアップデートの **1.28.1** もリリースされています。

<https://github.com/google/adk-python/releases/tag/v1.28.1>

ぶっちゃけ 2026/04/09に 1.29.0 2026/04/13には 1.30.0 がリリースされていますが、まだ追えてないのでその記事はまだ今度

<https://github.com/google/adk-python/releases/tag/v1.29.0>

<https://github.com/google/adk-python/releases/tag/v1.30.0>

今回は、1.22.0 から 1.28.1 までの怒涛のリリースを振り返りつつ、特に注目の機能である **「Skills for ADK agents」** と、ADK Agent を簡単に Slack ボット化できる **「SlackRunner」** について詳しく調査して、実際に Slack ボットを作ってみようと思います。

### 対象

* ADK を触ったことがある Python ユーザー
* Slack に AI エージェント（Agent）を常駐させたいユーザー
* 複雑な指示（Instruction）の管理に頭を悩ませている開発者

なお本記事中では ADK の Agent を`Agent`、それ以外の AI エージェントを`エージェント`と表記します。

---

## What's new in 1.22.0 ~ 1.28.1

まずは、1.22.0 から 1.28.1 までのリリースノートをざっと見てみましょう。  
量が多いので、主要なものをピックアップして和訳と簡単な説明を添えます。

リリースノート全文(原文と和訳)を見る

### [1.22.0] (2026/01/08)

* **Features**
  + **New JSON-based database schema for DatabaseSessionService**: セッション管理用の新しい JSON ベースのデータベーススキーマを導入しました。
  + **LlmAgent.model optional with default fallback**: `LlmAgent` のモデル指定を任意にし、デフォルトのフォールバックを設定可能にしました。

### [1.23.0] (2026/01/22)

* **Features**
  + **Automatically create a session if one does not exist**: セッションが存在しない場合に自動生成する機能をサポートしました。
  + **thinking\_config support**: 生成設定での思考（Thinking）プロセス設定をサポートしました。

### [1.24.0] (2026/02/04)

* **Highlights**
  + **Rich Developer Tooling**: 関数呼び出しの詳細なツールチップや、クリックで展開できるイベントビューなど、デバッグ体験が大幅に向上しました。

### [1.25.0] (2026/02/11)

* **Features**
  + **Add SkillToolset to adk**: ADK に `SkillToolset` を追加しました。これが「Skills for ADK agents」の核となる機能です。
  + **Add post-invocation token-threshold compaction**: 実行後のトークンしきい値ベースのコンテキスト圧縮機能を追加しました。

### [1.26.0] (2026/02/26)

* **Features**
  + **load\_skill\_from\_dir() method**: ディレクトリからスキル（Skill）をロードするメソッドを追加しました。
  + **Agent Skills spec compliance**: Agent Skills 仕様への準拠を強化しました（バリデーション、エイリアス、スクリプトなど）。

### [1.27.0] (2026/03/12)

* **Features**
  + **durable runtime support**: 中断・再開が可能な「Durable Runtime」をサポートしました。
  + **Add support for Anthropic's thinking\_blocks format**: Anthropic モデルの思考ブロック形式をサポートしました。
  + **Add adk optimize command**: Agent のプロンプトなどを最適化するための `adk optimize` コマンドを追加しました。

### [1.28.0/1.28.1] (2026/03/26 / 2026/04/02)

* **Features**
  + **Add slack integration to ADK**: ADK に Slack 統合を追加しました。
  + **bigquery: Migrate 1P BQ Toolset**: 第1パーティの BigQuery ツールセットを移行しました。
  + **Add Spanner Admin Toolset**: Spanner 管理用ツールセットを追加しました。
  + **Add lifespan parameter to to\_a2a()**: `to_a2a()` メソッドに寿命（lifespan）パラメータを追加しました。

---

## 1.25.0で追加された「Skills for ADK agents」

### 課題：指示（Instruction）の肥大化

Agent を開発していると、ついつい Instruction に「あれもこれも」と詰め込みたくなります。  
「この API を使うときはこうして」「このスタイルを守って」「このドキュメントを参考にして」...。  
結果として、Instruction が数千トークンに膨れ上がり、**「トークンコストが高くなる」「肝心な指示をモデルが忘れる」** という問題が発生します。

### Agent Skills による解決

これを解決するのが **Agent Skills** です。  
これは、指示（Instruction）やリソース（Markdown, Schema など）をパッケージ化し、**必要なときにだけ Agent が自分でロードする** 仕組みです。

ADK のスキルは、メタデータ(L1)、指示(L2)、リソース(L3)の3層構造になっており、Agent は必要に応じてこれらを段階的に読み込みます（段階的開示）。

ADK では `SkillToolset` を使うことで、Agent に以下のツールを自動的に持たせることができます。

* `list_skills`: 利用可能なスキルの一覧を確認。
* `load_skill`: 特定のスキルの詳細な指示をロード。
* `load_skill_resource`: スキルに紐づくリファレンスドキュメントなどをロード。

これにより、ベースラインの Instruction を最小限に抑えつつ、必要な知識をオンデマンドで取得できるようになります。非常に合理的ですね。

---

## 1.28.0で追加された「SlackRunner」

### 課題：Agent をどこで動かすのか問題

せっかく便利な Agent を作っても、開発用の Web UI をわざわざ立ち上げて使ってもらうのは敷居が高いですよね。  
「普段使っている Slack でそのまま使いたい」という要望は非常に多いです。  
しかし、自前で Slack Bolt フレームワークと ADK Runner を繋ぎ込むコードを書くのは、地味にボイラープレートが増えて面倒でした。

### SlackRunner が解決すること

1.28.0 で導入された `SlackRunner` を使えば、数行のコードで ADK Agent を Slack ボットとして公開できます。  
裏側では Slack Bolt が動いており、**Socket Mode** もサポートしているので、パブリックなエンドポイントや ngrok などのトンネリングツールを用意しなくても、ローカルから直接接続可能です。

---

## 実際に触ってみる：データ解析 Agent を Slack で動かす

今回は、Skills と SlackRunner を組み合わせて、**「複数の BigQuery データセットを、コンテキストを分離して解析できる Slack ボット」** を作ってみます。

### アプリケーション構成

* **Main Agent**: ユーザーとの対話と Slack 固有の処理を担当。
* **Data Analysis Agent**: 実際のデータ解析を担当。Skills を使ってデータセットごとに知識を切り替えます。
  + Skill 1: Chicago Taxi Trip (タクシーの乗車データ解析)
  + Skill 2: Google Cloud Release Note (リリースノートの検索)

### 1. プロジェクトの作成

ツールのバージョン管理に `mise`（マルチ言語対応のツールマネージャー）、パッケージ管理に `uv`（高速な Python パッケージマネージャー）を使ってセットアップします。

```
mkdir adk-slack-data-agent
cd adk-slack-data-agent

mise use python@3.12
mise use uv@latest
uv init
uv add "google-adk[slack]" python-dotenv
```

#### 環境変数の設定（.env）

プロジェクト直下に `.env` ファイルを作成し、必要なトークンやプロジェクト情報を設定します。  
※ slackのトークンの取得方法については後述しています。

.env

```
SLACK_BOT_TOKEN=xoxb-***
SLACK_APP_TOKEN=xapp-***
# Google Cloud 用
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=global
GOOGLE_GENAI_USE_VERTEXAI=1
```

#### Google Cloud の準備

エージェントが動作するために、以下の準備が必要です。

* **API の有効化**: [Vertex AI API](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com) を有効にします。また、BigQuery のパブリックデータセットを利用するため [BigQuery API](https://console.cloud.google.com/apis/library/bigquery.googleapis.com) も有効であることを確認してください。
* **権限の付与**: 実行環境（ローカルなら `gcloud auth application-default login` でログインしたユーザー、クラウドならサービスアカウント）に **「Vertex AI ユーザー」** および **「BigQuery ジョブユーザー」**（および参照するデータセットへの閲覧権限）が付与されている必要があります。

### 2. Agent Skills の作成

`skills/` ディレクトリに、各データセットの情報を定義します。

```
skills/
  chicago-taxi/
    SKILL.md  # タクシーデータの解析方法やスキーマ情報を記述
  gcp-release-notes/
    SKILL.md  # GCPリリースノートの情報を記述
```

`skills/chicago-taxi/SKILL.md` の例：

skills/chicago-taxi/SKILL.md

```
---
name: chicago-taxi
description: タクシー乗車データを解析するためのスキルです。
---
# Taxi Analysis Skill
このスキルは、BigQuery のタクシー関連テーブルを検索する際に使用します。

## データセット名
`bigquery-public-data.chicago_taxi_trips`

## テーブル情報

### 1. taxi_trips

#### カラム情報
field name	mode	type	description
unique_key	REQUIRED	STRING	Unique identifier for the trip.
taxi_id	REQUIRED	STRING	A unique identifier for the taxi.
trip_start_timestamp	NULLABLE	TIMESTAMP	When the trip started, rounded to the nearest 15 minutes.
trip_end_timestamp	NULLABLE	TIMESTAMP	When the trip ended, rounded to the nearest 15 minutes.
trip_seconds	NULLABLE	INTEGER	Time of the trip in seconds.
trip_miles	NULLABLE	FLOAT	Distance of the trip in miles.
pickup_census_tract	NULLABLE	INTEGER	The Census Tract where the trip began. For privacy, this Census Tract is not shown for some trips.
dropoff_census_tract	NULLABLE	INTEGER	The Census Tract where the trip ended. For privacy, this Census Tract is not shown for some trips.
pickup_community_area	NULLABLE	INTEGER	The Community Area where the trip began.
dropoff_community_area	NULLABLE	INTEGER	The Community Area where the trip ended.
fare	NULLABLE	FLOAT	The fare for the trip.
tips	NULLABLE	FLOAT	The tip for the trip. Cash tips generally will not be recorded.
tolls	NULLABLE	FLOAT	The tolls for the trip.
extras	NULLABLE	FLOAT	Extra charges for the trip.
trip_total	NULLABLE	FLOAT	Total cost of the trip, the total of the fare, tips, tolls, and extras.
payment_type	NULLABLE	STRING	Type of payment for the trip.
company	NULLABLE	STRING	The taxi company.
pickup_latitude	NULLABLE	FLOAT	The latitude of the center of the pickup census tract or the community area if the census tract has been hidden for privacy.
pickup_longitude	NULLABLE	FLOAT	The longitude of the center of the pickup census tract or the community area if the census tract has been hidden for privacy.
pickup_location	NULLABLE	STRING	The location of the center of the pickup census tract or the community area if the census tract has been hidden for privacy.
dropoff_latitude	NULLABLE	FLOAT	The latitude of the center of the dropoff census tract or the community area if the census tract has been hidden for privacy.
dropoff_longitude	NULLABLE	FLOAT	The longitude of the center of the dropoff census tract or the community area if the census tract has been hidden for privacy.
dropoff_location	NULLABLE	STRING	The location of the center of the dropoff census tract or the community area if the census tract has been hidden for privacy.
```

`skills/gcp-release-notes/SKILL.md` の例：

skills/gcp-release-notes/SKILL.md

```
---
name: gcp-release-notes
description: Google Cloud 各製品のリリースノートを検索・解析するためのスキルです。
---
# GCP Release Notes Skill
このスキルは、Google Cloud の製品アップデートや新機能、修正情報を調査する際に使用します。

## テーブル情報

### 1. release_notes (リリースノート本体)
Google Cloud の製品（一般提供版）のリリースノートが格納されています。
このデータセットを使用することで、全製品の更新情報をプログラムから検索・取得できます。

- `product_name` : 製品名（例: "Compute Engine", "BigQuery"）。
- `description` : リリースノートの本文。アップデート内容の詳細が含まれます。
- `release_note_type` : アップデートの種類（例: "FEATURE", "FIX", "CHANGE"）。
- `published_at` : 公開日。
- `product_id` : 製品の一意なID。
- `product_version_name` : バージョン名。
```

### 3. Agent の定義

`agent.py` で Agent を組み立てます。

agent.py

```
import os
import pathlib
import google.auth

from google.adk import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset, agent_tool
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
import dotenv

dotenv.load_dotenv()

# スキルのロード
base_path = pathlib.Path(__file__).parent / "skills"
taxi_skill = load_skill_from_dir(base_path / "chicago-taxi")
gcp_skill = load_skill_from_dir(base_path / "gcp-release-notes")

# BigQuery Toolset の設定 (読み取り専用)
credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
credentials_config = BigQueryCredentialsConfig(credentials=credentials)
tool_config = BigQueryToolConfig(write_mode=WriteMode.BLOCKED)

bigquery_toolset = BigQueryToolset(
    tool_filter=lambda tool, readonly_context: tool.name != "list_table_ids",
    credentials_config=credentials_config,
    bigquery_tool_config=tool_config
)

# Data Analysis Agent (Skills を活用)
data_agent = Agent(
    name="data_agent",
    model="gemini-flash-latest",
    instruction=f"あなたはデータ解析の専門家です。必要に応じて Skill をロードしてデータセットの仕様を理解し、BigQuery を使って回答してください。利用する Google CloudのプロジェクトIDは {os.environ.get('GOOGLE_CLOUD_PROJECT')} を使用してください",
    tools=[
        skill_toolset.SkillToolset(skills=[taxi_skill, gcp_skill]),
        bigquery_toolset
    ]
)

# Main Agent (Slack との窓口)
root_agent = Agent(
    name="slack_main_agent",
    model="gemini-flash-latest",
    instruction="タクシーの乗車データや、Google Cloudのリリース情報についてユーザーの依頼に応じて data_agent に仕事を依頼してください。それ以外の問い合わせは自分では回答できない旨を回答してください。",
    tools=[agent_tool.AgentTool(agent=data_agent)]
)
```

### 4. Slack App の設定とトークンの取得

ADK Agent を Slack で動かすために、Slack App を作成して設定を行います。  
[Slack API](https://api.slack.com/apps) から「`Create New App`」を選択し、「`From a manifest`」を利用すると設定がスムーズです。

<https://api.slack.com/apps>

![](https://static.zenn.studio/user-upload/33020e9e0fe4-20260415.png)

#### App Manifest の例

以下の YAML 形式のマニフェストを貼り付けることで、必要な権限（スコープ）や Socket Mode、イベント購読の設定を一括で行えます。ボット名などは適宜変更してください。

```
display_information:
  name: ADK Data Agent
features:
  bot_user:
    display_name: ADK Data Agent
oauth_config:
  scopes:
    bot:
      - app_mentions:read
      - chat:write
settings:
  event_subscriptions:
    bot_events:
      - app_mention
  interactivity:
    is_enabled: true
  socket_mode_enabled: true
```

#### トークンの取得

設定完了後、以下の2つのトークンを取得して環境変数に設定してください。

1. **SLACK\_BOT\_TOKEN**: `xoxb-` で始まるトークン。「OAuth & Permissions」メニューから取得できます。
   * トークンが表示されてない場合は、画面中段あたりに「Install to "スペース名"」というボタンが有るので、そのボタンをクリックして、Slack ボットをスペースにインストールしてください。  
     ![](https://static.zenn.studio/user-upload/bcfaf15f5ebd-20260415.png)
2. **SLACK\_APP\_TOKEN**: `xapp-` で始まるトークン。「Basic Information」メニューの「App-Level Tokens」から、`connections:write` スコープを付与して生成してください。  
   ![](https://static.zenn.studio/user-upload/61086244d349-20260415.png)

### 5. SlackRunner で動かす

`main.py` を作成し、`SlackRunner` を起動します。

main.py

```
import asyncio
import os
from dotenv import load_dotenv
from google.adk.integrations.slack import SlackRunner
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.plugins import LoggingPlugin
from slack_bolt.app.async_app import AsyncApp
from agent import root_agent

# .env ファイルから環境変数をロード
load_dotenv()

async def main():
    # ADK Runner の作成
    runner = Runner(app_name="data_agent", agent=root_agent, auto_create_session=True, session_service=InMemorySessionService(), plugins=[LoggingPlugin()])

    # Slack App の初期化
    slack_app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])

    # SlackRunner の起動
    slack_runner = SlackRunner(runner=runner, slack_app=slack_app)

    print("⚡️ Slack Bot is starting...")
    await slack_runner.start(app_token=os.environ["SLACK_APP_TOKEN"])

if __name__ == "__main__":
    asyncio.run(main())
```

!

**SlackRunnerのセッションの単位と`user_id`**

SlackRunnerではメッセージを送ったSlackの `user_id` をADKの `user_id`、SlackのChannel IDとts(スレッドのタイムスタンプ)を `{channel_id}-{thread_ts}` の形式で繋いだものを `session.id` として利用しています。

このため、Agent との会話はSlackのスレッド中は継続される(スレッドが別なら継続されない)ということになります。  
また、別のユーザが同じスレッドで話しかけたとしても、`user_id` が異なるため別のSessionとして扱われる点に注意が必要です。  
なおSession IDが自作のため、Agent EngineのSession Storeなどは利用ができません。

### 6. Slack での動作確認

Socket Mode でSlackと接続しているため、ローカルで動作確認が可能です。  
以下のコマンドで `main.py` を起動します。

Slackにて `/invite` などを利用して作成したアプリ（ボット）をチャネルに招待し、メンションをつけて、  
「タクシー乗車データから全体のチップの平均値を教えて」と聞くと、`Main Agent` -> `Data Agent` -> `Skill (Taxi) ロード` -> `BigQuery 実行` という流れで回答が返ってきます。

![](https://static.zenn.studio/user-upload/6521c660e019-20260415.png)

また「最新のGoogle Cloudのリリース情報をまとめて教えて」と聞くとGoogle Cloudのリリース情報が取得されます。

![](https://static.zenn.studio/user-upload/85d018b747c2-20260415.png)

---

## まとめ

今回は ADK 1.22.0 から 1.28.1 までのアップデートと、目玉機能である Skills および SlackRunner を紹介しました。

* **Skills**: 指示の肥大化など、Agent Skills を利用しない場合の課題を解決し、エージェントが必要な知識を自ら取得する「段階的開示」を実現。
* **SlackRunner**: ADK Agent を爆速で Slack ボット化。実運用へのハードルが劇的に下がりました。

実際に使ってみると、SlackRunner でメッセージを送った際の「Thinking...」という初期メッセージが現状固定だったり、チャンネル ID の取得に少し工夫が必要だったりと、気になる点もありますが、これらはツール自作や `SlackRunner` の継承で簡単にカバーできる範囲だと感じました。  
またAgentはSlackのmkdownフォーマットやメンション方法を知らないため、きれいなフォーマットで返信を求めるのであれば、そういった部分も`Instruction`に記載することをおすすめします。

特に Skills については、公式ブログでも詳しく解説されているので、ぜひチェックしてみてください。  
<https://developers.googleblog.com/developers-guide-to-building-adk-agents-with-skills/>

今後も ADK の進化から目が離せませんね。1-2か月ぐらい目を背いていましたが...これからは凝視したいと思います。

## おまけ

ちなみに私が使っている、これらを解消するために使っているSlack RunnerとSKILL.mdは以下です。

```
class CustomSlackRunner(SlackRunner):
    async def _handle_message(self, event: dict[str, Any], say: Any):
        """Handles a message or app_mention event."""
        text = event.get("text", "")
        user_id = event.get("user")
        channel_id = event.get("channel")
        thread_ts = event.get("thread_ts") or event.get("ts")

        if not text or not user_id or not channel_id:
            return

        # In Slack, we can use the channel_id (and optionally thread_ts) as a session ID.
        session_id = f"{channel_id}-{thread_ts}" if thread_ts else channel_id

        new_message = types.Content(role="user", parts=[types.Part(text=text)])

        thinking_ts: str | None = None
        try:
            thinking_response = await say(text=":loading: 考え中..._", thread_ts=thread_ts)
            thinking_ts = thinking_response.get("ts")

            async for event in self.runner.run_async(
                    user_id=user_id,
                    session_id=session_id,
                    new_message=new_message,
                    state_delta={
                        'slack_user_id': user_id,
                        'slack_channel_id': channel_id,
                        'slack_ts': thread_ts
                    },
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            if thinking_ts:
                                await self.slack_app.client.chat_update(
                                    channel=channel_id,
                                    ts=thinking_ts,
                                    text=part.text,
                                )
                                thinking_ts = None
                            else:
                                await say(text=part.text, thread_ts=thread_ts)
            if thinking_ts:
                await self.slack_app.client.chat_delete(
                    channel=channel_id, ts=thinking_ts
                )
                thinking_ts = None
        except Exception as e:
            error_message = f"Sorry, I encountered an error: {str(e)}"
            logger.exception("Error running ADK agent for Slack:")
            if thinking_ts:
                await self.slack_app.client.chat_update(
                    channel=channel_id,
                    ts=thinking_ts,
                    text=error_message,
                )
            else:
                await say(text=error_message, thread_ts=thread_ts)
```

SKILL.md

```
---
name: slack-markdown-formatter
description: 最終回答を Slack 専用の Markdown 形式に整形するための指示とリファレンスを提供します。
---

# Slack Markdown フォーマット

Slack でメッセージを表示する際は、通常の Markdown とは異なる独自の仕様に従う必要があります。ユーザーへの最終回答を作成する際は、必ず以下のルールを適用してください。

## 基本ルール

| 要素 | Slack での記述方法 | 注意事項 |
| :--- | :--- | :--- |
| **太字** | `*text*` | アスタリスク1つで囲みます（`**` は不可） |
| *イタリック* | `_text_` | アンダースコアで囲みます |
| ~取り消し線~ | `~text~` | チルダで囲みます |
| リスト | `• item` | 箇条書きは中黒（bullet）記号を使用するか、標準的な `-` を使用します |
| 番号付きリスト | `1. item` | 数字とドットを使用します |
| 引用 | `> text` | 行頭に `>` を置きます |
| コード | `` `code` `` | バッククォートで囲みます |
| コードブロック | ` ```code block``` ` | 3つのバッククォートで囲みます |
| リンク | `<URL|表示テキスト>` | 角括弧ではなく `<>` を使用し、パイプ `|` で区切ります |
| メンション | `<@USER_ID>` | ユーザーをメンションする際に使用します。名前ではなく必ず ID を使用してください |

## 指示

1.  最終的な回答を生成する前に、このスキルのルールを確認してください。
2.  回答の冒頭では、必ずユーザーをメンション（`<@USER_ID>`）してください。
3.  特に「太字」に `**` を使用しないよう注意し、必ず `*` を使用してください。
4.  リンクを含める場合は、必ず `<URL|text>` の形式を使用してください。
5.  見出し（# Heading）は Slack ではサポートされていないため、代わりに太字（*Heading*）などを使用して強調してください。
```

---

## お知らせ/宣伝

ADK 開発者が集う日本語の Discord コミュニティがあります。ADK に関する情報交換や議論に興味がある方は、ぜひご参加ください。

<https://discord.gg/BKpGRzjtqZ>

また、ADK の最新のコミットログやリリースノートを分かりやすく解説する Podcast を配信しています。ADK の動向を追いかけたい方は、ぜひ聴いてみてください。

<https://www.youtube.com/playlist?list=PL0Zc2RFDZsM_MkHOzWNJpaT4EH5fQxA8n>
