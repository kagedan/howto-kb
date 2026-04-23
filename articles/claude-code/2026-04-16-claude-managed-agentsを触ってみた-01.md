---
id: "2026-04-16-claude-managed-agentsを触ってみた-01"
title: "Claude Managed Agentsを触ってみた"
url: "https://zenn.dev/solvio/articles/7f8d2008526234"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "zenn"]
date_published: "2026-04-16"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

## はじめに

2026年4月、Anthropicが新機能「Claude Managed Agents」を公開ベータとしてリリースしました。  
<https://x.com/claudeai/status/2041927687460024721?s=20>  
<https://platform.claude.com/docs/ja/managed-agents/overview>  
普段Claude CodeをCLIで使っている自分としては、「APIでClaude Codeみたいなことができるようになった」という理解だったのですが、実際に触ってみるまで何がすごいのかよくわかりませんでした。

本記事では、Claude Managed Agentsをまったく触ったことがない・知らない状態から、概要の理解から実際にAPIを叩いてエージェントを動かすところまでをまとめます。

## この記事のGoal

* Claude Managed Agentsとは何かを理解する。
* MessageAPIとの違いを理解する。

## Claude Managed Agentsってなに？？

公式ドキュメントには以下のように記載されています。

> Claude Managed Agents は、Claude を自律型エージェントとして実行するためのハーネスとインフラストラクチャを提供します。独自のエージェントループ、ツール実行、ランタイムを構築する代わりに、Claude がファイルを読み取り、コマンドを実行し、ウェブを閲覧し、コードを安全に実行できる完全にマネージされた環境を取得します。このハーネスは、組み込みのプロンプトキャッシング、圧縮、およびその他のパフォーマンス最適化をサポートし、高品質で効率的なエージェント出力を実現します。

?

正直、初見だとよくわからなかったので、次の項から整理しながら解説いたします。

### Messages APIとの違い

Messages APIは、ClaudeのAPIを使ったことがある人なら必ず触っている、最も基本的なAPIです。claude.aiのチャット画面も裏側ではこれが動いています。テキストを送ったらテキストが返ってくる、それだけのシンプルな仕組みで、コードを書いてもらうことはできるが、実行するのは自分です。

Managed Agentsは、Anthropicが用意したクラウドコンテナの中でClaudeが自律的に動き、ファイルの読み書き、シェルコマンドの実行、Web検索まで、Claudeが自分で判断してやってくれます。

通常のMessages APIとの違いを表にするとこうなります。

| 項目 | Messages API | Claude Managed Agents |
| --- | --- | --- |
| 何ができる | テキストの入出力 | ファイル操作・コマンド実行・Web検索など自律的に作業 |
| 実行環境 | なし | Anthropic管理のクラウドコンテナ |
| エージェントループ | 自分で構築が必要 | Anthropicが提供 |
| 向いている用途 | チャットボット、テキスト生成 | 長時間実行タスク、コード生成・実行、非同期作業 |

Claude Codeを使ったことがある人なら、「あれのAPI版」と思ってもらえればイメージしやすいかもしれません。

### つまり何ができるの？

「AIエージェントが自律的にコードを書いて実行する」サービスを自分で作ろうとすると、以下をすべて自前で用意する必要があります。

* サンドボックス環境（コンテナの構築・管理）
* エージェントループ（考える → ツール使う → 結果見る → また考える の繰り返し）
* ツール実行基盤（ファイル操作、シェルコマンド、Web検索などの統合）
* セッション管理（会話履歴の永続化、途中再開）
* セキュリティ（悪意あるコマンドの防止）

Managed Agentsはそのあたりを全部Anthropicが面倒を見てくれるので、APIを叩くだけで済みます。

| コンセプト | 説明 |
| --- | --- |
| Agent | モデル・システムプロンプト・使用するツールの定義。一度作れば使い回せる |
| Environment | 実行コンテナの設定。パッケージやネットワークアクセスを定義 |
| Session | Agent + Environmentで起動する実行インスタンス。実際のタスク処理を行う |
| Events | アプリとエージェント間のメッセージのやり取り。SSEでリアルタイムストリーミング |

## 事前準備

### 1. Anthropic APIキーの取得

**APIキーの取得方法**

[Anthropic Console](https://console.anthropic.com/settings/keys)からAPIキーを取得します。

Claude Console画面の「+ Cteate key」を選択  
![](https://static.zenn.studio/user-upload/68b6d920252b-20260415.png)  
「Name your key:」にキーに設定したい名前を入力する。  
![](https://static.zenn.studio/user-upload/1133d5e8187c-20260415.png)  
キーが発行されるので「Copy key」をクリックして、キーをコピーする。  
![](https://static.zenn.studio/user-upload/90679dcc89ed-20260415.png)

### 2. SDKのインストール

本記事ではPythonを使います。

### 3. 環境変数の設定

```
export ANTHROPIC_API_KEY="your-api-key-here"
```

## 試しに実行してみる

今回は、Managed Agentsに「Web検索して調査レポートをMarkdownファイルにまとめる」というタスクをやらせてみます。

Web検索→情報整理→ファイル書き出しという一連の流れを、自前でオーケストレーションを組まずに一つのAPIリクエストで完結させられるのがManaged Agentsの便利なところです。

以下が全体のコードになる。`run_agent.py` として保存します。

## Step 1: エージェントの作成

モデル・プロンプト・使えるツールを定義します。

```
from anthropic import Anthropic

client = Anthropic()

# エージェントを作成
agent = client.beta.agents.create(
    name="Research Assistant",
    model="claude-sonnet-4-6",
    system="You are a research assistant. Search the web, gather information, and produce well-structured reports in Markdown.",
    tools=[
        {"type": "agent_toolset_20260401"},
    ],
)
print(f"Agent ID: {agent.id}, version: {agent.version}")

# 環境を作成
environment = client.beta.environments.create(
    name="research-env",
    config={
        "type": "cloud",
        "networking": {"type": "unrestricted"},
    },
)
print(f"Environment ID: {environment.id}")

# セッションを開始
session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
    title="Research session",
)
print(f"Session ID: {session.id}")

# メッセージを先に送信
client.beta.sessions.events.send(
    session.id,
    events=[
        {
            "type": "user.message",
            "content": [
                {
                    "type": "text",
                    "text": "以下の手順を必ずすべて実行してください。\n\n1. 「Claude Managed Agents」についてWeb検索で情報を集める\n2. 集めた情報をもとに、概要・主な機能・ユースケース・制限事項を含む調査レポートを作成する\n3. そのレポートをreport.mdとしてファイルに書き出す（writeツールを使うこと）\n4. 書き出したファイルの内容を表示して確認する\n\n必ずファイルの書き出しまで完了してください。",
                },
            ],
        },
    ],
)

# ストリームを開いてイベントを処理
with client.beta.sessions.events.stream(session.id) as stream:
    for event in stream:
        match event.type:
            case "agent.message":
                for block in event.content:
                    print(block.text, end="")
            case "agent.tool_use":
                print(f"\n[Using tool: {event.name}]")
            case "session.status_idle":
                print("\n\nAgent finished.")
                break
```

コードの流れを簡単に説明します。

1. **エージェントの作成** — モデル、システムプロンプト、使用するツールを定義します。
2. **環境の作成** — エージェントが動くクラウドコンテナの設定。ネットワークアクセスは `unrestricted`（制限なし）と `limited`（特定ドメインのみ許可）が選べる。今回はWeb検索させたいので `unrestricted` にしているが、本番環境では必要なアクセス先だけ許可する `limited` の方が安全です。
3. **セッションの開始** — AgentとEnvironmentを紐付けて起動します。
4. **メッセージ送信 & ストリーミング** — 指示を送り、Claudeの作業をSSEでリアルタイムに受け取ります。

`agent_toolset_20260401`を指定すると、以下のツールがすべて有効になります：

| ツール | 説明 |
| --- | --- |
| bash | シェルコマンドの実行 |
| read | ファイルの読み取り |
| write | ファイルの書き込み |
| edit | ファイルの編集（文字列置換） |
| glob | ファイルパターンマッチング |
| grep | テキスト検索 |
| web\_fetch | URLからコンテンツ取得 |
| web\_search | Web検索 |

特定のツールだけ使いたい場合は、以下のように設定できます：

```
tools=[
    {
        "type": "agent_toolset_20260401",
        "default_config": {"enabled": False},  # 全部オフにしてから
        "configs": [
            {"name": "bash", "enabled": True},   # 必要なものだけTrueに設定
            {"name": "read", "enabled": True},
            {"name": "write", "enabled": True},
        ],
    },
]
```

## 実行してみる

`python run_agent.py`  
以下が実際の出力です。

```
Agent ID: agent_011CZye6mRRRFP9PCpDpZtKM, version: 1
Environment ID: env_012zacc9VaxGhgJ9E1evYSmQ
Session ID: sesn_011CZye6q1EUSypPU5hFg5wS
承知しました。4つの手順をすべて実行します。まずWeb検索から始めます。
[Using tool: web_search]

[Using tool: web_search]
情報が十分集まりました。次にレポートを作成してファイルに書き出します。
[Using tool: write]
ファイルの書き出しが完了しました。次に内容を表示して確認します。
[Using tool: read]
4つの手順がすべて完了しました。

Agent finished.
```

流れを追ってみます。

1. `[Using tool: web_search]`  — 「Claude Managed Agents」について複数のキーワードでWeb検索して情報を収集
2. `[Using tool: write]` — 集めた情報を整理して `report.md` としてファイルに書き出し
3. `[Using tool: read]` — 書き出したファイルの中身を読んで、ちゃんと書けたか確認

自分がやったのは `python run_agent.py` を実行しただけですが、Web検索、情報の整理、ファイルへの書き出し、確認まで、すべてClaudeが自律的にやっている。

### 出力されたファイル

```
# Claude Managed Agents 調査レポート

> 作成日: 2026年4月16日  
> 情報源: Anthropic 公式ブログ・ドキュメント・各種メディア報道

---

## 1. 概要

**Claude Managed Agents** は、Anthropic が提供するクラウドホスト型の自律エージェント実行サービスです。  
開発者が独自のエージェントループ・サンドボックス・ツール実行レイヤーを構築する必要なく、Claude を自律エージェントとして動作させるためのフルマネージド環境を提供します。

> *"a hosted service in the Claude Platform that runs long-horizon agents on your behalf through a small set of interfaces meant to outlast any particular implementation"*  
> — Anthropic Engineering Blog

現在（2026年4月時点）**パブリックベータ**として提供中であり、API エンドポイント利用時には `managed-agents-2026-04-01` ベータヘッダーが必要です。  
料金は **$0.08 / セッション時間** が目安とされています。

---

## 2. 背景・設計思想

Anthropic は「エージェントハーネス（AIモデルを取り巻くソフトウェアインフラ）はモデルの進化とともに陳腐化する」という課題に直面しました。  
例えば、Claude Sonnet 4.5 では「コンテキスト上限が近づくと早々にタスクを終了してしまう（コンテキスト不安）」という問題があり、ハーネス側でコンテキストリセットを追加で対処していました。しかし Claude Opus 4.5 では同じ問題は発生しなかったため、ハーネスに組み込まれた前提が無効になりました。

この課題を解決するため、Managed Agents は**OSがハードウェアを抽象化した方式**にならい、以下の構成要素を仮想化しています：

| 構成要素 | 説明 |
|----------|------|
| **Session** | すべての出来事を記録する追記専用ログ（コンテキストウィンドウ外に永続化） |
| **Harness** | Claude を呼び出しツール呼び出しをルーティングするループ |
| **Sandbox** | コードが実行される安全な分離環境 |

.........省力

## 5. 制限事項・注意点

| 項目 | 内容 |
|------|------|
| **ベータ段階** | 現在パブリックベータのため、挙動が予告なく改善・変更される可能性がある |
| **モデルロックイン** | Claude モデルに限定。LangChain・CrewAI など他フレームワークとの統合ギャップが残る |
| **サードパーティ制限** | 2026年4月4日以降、Claude Pro/Max サブスクリプションでサードパーティエージェントフレームワーク（OpenClaw 等）を利用するためにはペイパーユーズへの移行が必要 |
| **コスト** | 長時間・大量並列実行ではトークン消費・セッション費用が急増するリスクあり（$200/月の Max プランが $1,000〜$5,000 相当の計算量を消費したケースも報告あり） |
| **コンテキスト管理の複雑性** | コンテキストを選択的に保持・破棄する不可逆な判断はエラーにつながる可能性があり、設計に注意が必要 |
| **ハーネスの陳腐化リスク** | モデルアップグレードのたびにハーネスの前提が無効化される可能性がある（Managed Agents 自体がこの解決策であるが、内部実装の変化に注意） |
| **プラットフォーム限定** | `platform.claude.com` のAPI機能であり、一般ユーザー向けの claude.ai では利用不可 |

---

## 6. まとめ

Claude Managed Agents は、企業や開発者が**エージェントインフラを自前構築するコスト・複雑さ**を大幅に削減し、プロトタイプから本番稼働まで最短数日で到達できる仕組みを提供します。  
Notion・Rakuten・Sentry・Asana といった企業がすでに本番活用しており、長時間タスク・非同期ワークロード・マルチエージェント協調において特に威力を発揮します。  

一方でモデルロックイン・コスト増大リスク・現在のベータステータスによる変更の可能性といった制限事項も存在するため、導入前に要件・コスト・長期的な戦略を慎重に評価することが推奨されます。

---

*参考リンク*
- [Anthropic 公式発表](https://claude.com/blog/claude-managed-agents)
- [API ドキュメント](https://platform.claude.com/docs/en/managed-agents/overview)
- [Engineering Blog: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents)
```

### **生成されたファイルはどこにあるのか**

ここで「report.mdはどこに保存されたのか」というと、ローカルではなく、Anthropicのクラウドコンテナの中に保存されています。

ただし、セッションが生きている間はコンテナの状態が保持されるので、同じセッションIDに追加のメッセージを送ればファイルの中身を確認したり、追加の作業を指示したりできる。チャットの続きを行っているような感覚に近いかと思いました。

## 今後の発展

今回は「Web検索してレポートを作る」という単純なタスクを試しましたが、Managed AgentsはMCPサーバーとの連携にも対応しています。つまり、SlackやGitHub、データベースなど外部サービスと接続したエージェントを構築できます。

例えば以下のようなユースケースが考えられます。

* Slackでユーザーから質問を受けたら、社内ドキュメントを検索して回答を投稿するサポートボット
* GitHub Issueが作成されたら、コードを調査して修正PRを自動で出すエージェント
* 定期的にWebから情報を収集して、レポートを生成・配信するリサーチエージェント

他にも、Multi-agent（複数エージェントの協調）やMemory（セッション間の記憶保持）が研究プレビューとして公開されています。

## **おわりに**

今回、Claude Managed Agentsを初めて触ってみた。エージェントの作成からセッション内でのコード実行、ファイルの確認まで、数十行のPythonコードで一通り動かすことができました。

自前でエージェント基盤を組もうとすると、サンドボックスの構築やエージェントループの実装だけでかなりの工数が必要になります。そのあたりをAPI一本で済ませられるのは、プロダクトにエージェント機能を組み込みたい場面では大きいです。

まだベータ版ということもあり、今後仕様が変わる可能性はある。ただ、すべてのAPIアカウントでデフォルト有効になっているので、気になった方は手元で動かしてみてもいいと思いました。

## 参考

## 最後に宣伝

Solvio株式会社は、生成AIを軸に企業の課題解決を行う会社です。これまでの支援の中でもHumanが行っていた業務を生成AIエージェントに置き換えて、業務効率を高めた事例もあります。ご興味があればお気軽にご連絡いただけると幸いです！  
お問い合わせページ：<https://solvio.co.jp/contact>
