---
id: "2026-04-11-claude-managed-agents-を試してみた-01"
title: "Claude Managed Agents を試してみた"
url: "https://zenn.dev/kumamo_tone/articles/365845d65e6cf4"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

最近発表された Claude の新機能「Managed Agents」が気になりました。

ニュース。  
<https://www.itmedia.co.jp/aiplus/articles/2604/09/news067.html>

Zennの入門記事。  
<https://zenn.dev/galirage/articles/claude-managed-agents-quickstart>

公式の記事。  
<https://platform.claude.com/docs/ja/managed-agents/overview>

すでにある記事はかなり詳細にしっかり書いてあるので、実際の入門に必要な情報は上記に譲るとして、この記事では逆にライトに理解したい人のため（と自分のため）に、実際に何か作ってみたときの体験だったり、分かったことをかいつまんだり、感想を書いたりして、使えそうな感触を持ってもらうことを目的としようと思います。

## まずこれ何？

> Claude Managed Agents は、Claude を自律型エージェントとして実行するためのハーネスとインフラストラクチャを提供します。独自のエージェントループ、ツール実行、ランタイムを構築する代わりに、Claude がファイルを読み取り、コマンドを実行し、ウェブを閲覧し、コードを安全に実行できる完全にマネージされた環境を取得します。このハーネスは、組み込みのプロンプトキャッシング、圧縮、およびその他のパフォーマンス最適化をサポートし、高品質で効率的なエージェント出力を実現します。

どういうこと？？？？

ざっくりまとめると、Anthropic がホストしてくれるエージェント実行環境らしいです。

* セッションごとにコンテナが立ち上がる
* その中で bash、ファイル操作、コード実行ができる
* GitHub リポジトリをマウントして、実際のコードを読める
* エージェントが自律的にツールを使いながらタスクを進める

普通の Claude API だと「テキストを入れてテキストが返ってくる」だけですが、Managed Agents だとエージェントが実際にシェルコマンドを実行したり、ファイルを探索したりできる のが大きな違いとのこと。

<https://platform.claude.com/>

コンソールのサイドバーを見ると結構良い位置に「Managed Agents」とデカデカと鎮座しています。

![](https://static.zenn.studio/user-upload/33dbc090b332-20260411.png)

なんかすごそう。

でも実際何ができるんだろう…

## Starting Point

昨日参加した勉強会で、コマンドを使うと簡単に開発が開始できるというのを聞いて、試してみました。

<https://x.com/kumamo_tone/status/2042566804778946760>

```
/claude-api managed-agent-onboard
```

```
❯  /claude-api managed-agent-onboard

⏺ Skill(claude-api)
  ⎿  Successfully loaded skill · 4 tools allowed

⏺ Managed Agents オンボーディング

  Claude Managed Agents は、Anthropic がホストするエージェントです。Anthropic
  のオーケストレーション層でエージェントループを実行し、セッションごとにサンドボックス化されたコンテナをプロビ
  ジョニングします。ツール（bash、ファイル操作、コード実行など）はそのコンテナ内で実行されます。

  あなたが用意するもの：
  - エージェント設定 — ツール、スキル、モデル、システムプロンプト。再利用可能でバージョン管理されます。
  - 環境設定 — ツールが実行されるサンドボックス（ネットワーク、パッケージ）。エージェント間で再利用可能。

  各エージェントの実行はセッションです。

  ---
  まず最初の質問です：

  ▎ 作りたいエージェントが既に決まっていますか？それとも、よくあるパターンをいくつか見てから決めたいですか？

  参考までに、よくあるパターンはこちらです：

  ┌──────────────────────────┬──────────┬──────────────────────────────────────────────────────────────────┐
  │         パターン         │ トリガー │                                例                                │
  ├──────────────────────────┼──────────┼──────────────────────────────────────────────────────────────────┤
  │ Fire-and-forget PR       │ 人間     │ Slackコマンド → エージェント（GitHub tool）→ CI通過するPR        │
  ├──────────────────────────┼──────────┼──────────────────────────────────────────────────────────────────┤
  │ リサーチ +               │ 人間     │ トピック → エージェント（web search + skill）→                   │
  │ ダッシュボード           │          │ HTMLダッシュボード                                               │
  └──────────────────────────┴──────────┴──────────────────────────────────────────────────────────────────┘

  どちらのアプローチで進めますか？
```

おお

よくわからん…

```
❯ よくあるパターンをいくつか見てから決めたい

⏺ 4つの代表的なパターンを紹介します。すべて同じランタイムコードパス（sessions.create() → sessions.events.send()
   → stream）で動きます。違いはトリガーと出力先だけです。

  ┌───────────────────────┬────────────┬───────────────────────────────────────────────────────────────────┐
  │       パターン        │  トリガー  │                              具体例                               │
  ├───────────────────────┼────────────┼───────────────────────────────────────────────────────────────────┤
  │ イベント駆動          │ Webhook    │ GitHub PR push → エージェント（GitHub tool）→ Slack通知           │
  ├───────────────────────┼────────────┼───────────────────────────────────────────────────────────────────┤
  │ スケジュール実行      │ Cron       │ 毎日のブリーフ: ブラウザ + GitHub + Jira → エージェント →         │
  │                       │            │ Slackレポート                                                     │
  ├───────────────────────┼────────────┼───────────────────────────────────────────────────────────────────┤
  │ Fire-and-forget PR    │ 人間の操作 │ Slackスラッシュコマンド → エージェント（GitHub tool）→            │
  │                       │            │ CI通過するPR作成                                                  │
  ├───────────────────────┼────────────┼───────────────────────────────────────────────────────────────────┤
  │ リサーチ +            │ 人間の操作 │ トピックを投げる → エージェント（web search + frontend-design     │
  │ ダッシュボード        │            │ skill）→ HTMLダッシュボード生成                                   │
  └───────────────────────┴────────────┴───────────────────────────────────────────────────────────────────┘
```

実例を教えてくれて、ちょっと雰囲気が見えてきました。Webhookや定期実行、人間がSlackコマンドなどを打ったタイミングで、Claudeの知性を使って、複雑な操作をClaudeのクラウド上で効率よく動かしたいときに使えそうな感じがします。

わざわざClaudeの知性を使う必要はなさそうですが、試しによく自分が作ったOSSのリポジトリにIssueとか立ったのを気づかず放置してしまうことが多いので、PR立ったら、Discordに要約して通知してくれる仕組みを作ることにしました。

## 作ったもの

GitHub Webhook → Cloudflare Workers → Discord という構成です。最終的にはこうなりました。

```
  GitHub (PR/Issue/コメント)
    → Webhook
      → Cloudflare Worker（振り分け）
        ├── PR → Managed Agents でコードレビュー
        │     リポジトリをコンテナにマウント
        │     git diff → コード読解 → テスト実行 → レビュー
        │     → Discord に投稿
        └── Issue/コメント → Claude API で要約通知
              内容を要約 → Discord に投稿
```

2つの処理を使い分けています。

* Issue/コメント通知: 普通の Claude API を呼ぶだけ。Managed Agents は使わない（コスト削減のため）
* PRレビュー: Managed Agents でリポジトリをマウントして、実際にコードを読んでテストを走らせてレビュー

### エージェントとセッションの関係

Managed Agents には「エージェント」と「セッション」という概念があります。

* エージェント:  
  設定（モデル、システムプロンプト、使えるツール）を定義した永続的なオブジェクト。一度作ったら使い回す
* セッション: エージェントの実行インスタンス。PRが来るたびに新しいセッションを作る

  つまり「こういうエージェントを作っておいて」→「このエージェントで新しいセッション開始して」→「このタスクやって」という流れになりそうです。

#### 1. エージェントを作る（一度だけ）

```
  const agentRes = await fetch("https://api.anthropic.com/v1/agents", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": API_KEY,
      "anthropic-version": "2023-06-01",
      "anthropic-beta": "managed-agents-2026-04-01",
    },
    body: JSON.stringify({
      name: "PR Code Reviewer",
      model: "claude-sonnet-4-6",
      system: "あなたはシニアソフトウェアエンジニアとして...",
      tools: [
        { type: "agent_toolset_20260401", default_config: { enabled: true } },
      ],
    }),
  });
```

agent\_toolset\_20260401 を有効にすると、bash / read / write / edit / glob / grep / web\_fetch / web\_search がまとめて使えるようになるそうです。これにより、エージェントが自分で判断してこれらのツールを使い分けてくれます。

ちなみに TypeScript SDK（v0.52.0 時点）にはまだ Managed Agents のバインディングがなかったので、fetch で直接 API を叩いています。Cloudflare Workers ではむしろこちらのほうがシンプルで依存も少ないので、結果的にちょうどよかったです。

#### 2. PRが来たらセッションを作る

セッション作成時に リポジトリをマウント できます。

```
  const res = await fetch("https://api.anthropic.com/v1/sessions", {
    method: "POST",
    headers: ANTHROPIC_HEADERS,
    body: JSON.stringify({
      agent: {
        type: "agent",
        id: env.REVIEWER_AGENT_ID,
        version: env.REVIEWER_AGENT_VERSION,
      },
      environment_id: env.ENVIRONMENT_ID,
      resources: [
        {
          type: "github_repository",
          url: repoUrl,
          authorization_token: env.GITHUB_PAT,
          mount_path: "/workspace/repo",
          checkout: { type: "branch", name: pr.head.ref },
        },
      ],
    }),
  });
```

これでエージェントのコンテナ内に /workspace/repoとしてリポジトリがクローンされます。あとはメッセージを送るだけで、エージェントが勝手に git diff したり grep したりテストを走らせたりしてくれます。

普通の Claude API だと「PRの差分テキストを渡して感想をもらう」くらいしかできませんが、Managed Agents なら「リポジトリ丸ごと渡すから好きに調べてレビューして」ができるということになります。ただし、ここらへんは今までもGitHub Actions経由でできていたことなので、cron実行とかのほうがわざわざ作る甲斐があるかな？と感じました。

## 動かしてみた

![](https://static.zenn.studio/user-upload/31a951785e82-20260411.png)

DiscordにPRを要約した内容を通知してくれました。

## ハマったこと

Worker のログ（`wrangler tail`）では「セッション作成OK、メッセージ送信OK」と出ているのに、Discordに何も来ません。

結局、セッションのイベントを API で直接叩いて確認する必要がありました。

```
curl -s "https://api.anthropic.com/v1/sessions/${SESSION_ID}/events" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: managed-agents-2026-04-01" | python3 -m json.tool
```

出てきたのは…

```
{
  "error": {
    "message": "Your credit balance is too low to access the Anthropic API.",
    "type": "billing_error"
  },
  "type": "session.error"
}
```

クレジット残高不足でした。ここらへんのトラブルシューティングもClaude Codeと対話的に行えるので、長時間ハマることはありませんでした。新しい開発者体験だ…

## コンソール

今回自作した Claude Managed Agents に関する情報は、Console の Managed Agents > Agents から確認することができます。グラフィカルに見やすく表示してくれるのはありがたいですね。

![](https://static.zenn.studio/user-upload/792ec5d35f89-20260411.png)

また、どのようにセッションがうごいたかについては、 Console の Managed Agents > Sessions で見ることができました。今回はシンプルすぎる例だったのであまり真価が発揮できていない感じがしますが、実際にAgentがどのように働いたかみることができるため、デバッグに使用することができそうです。

![](https://static.zenn.studio/user-upload/49ad8f41e07e-20260411.png)

## 似た機能

Claude Managed Agents はエージェントを登録して行うことをプログラマブルに設定でき、それがクラウド上で実行されるという特徴から、かなり柔軟で、かつ長時間掛かるようなタスクでも耐えうる、チーム開発で輝きそうな機能だと感じました。

一方で、クラウド上で簡単に実行するという観点で言うと、もっと簡単な機能がありそうです。

### ウェブスケジュールタスク

<https://code.claude.com/docs/en/web-scheduled-tasks>

スケジュールタスクを作成するのは簡単で、以下のページから作れます。

<https://claude.ai/code/scheduled>

新しいスケジュールタスクボタンをクリックすると、クラウド上で定時にClaudeでのタスクを行ってくれそうです。毎日ニュースを収集するとかのタスクは、これで事足りるかも知れません。

![](https://static.zenn.studio/user-upload/241acb21ce95-20260411.png)

実行されるのはローカルマシンになりますが、 Claude Desktop アプリからもスケジュールタスクは実行することができるようです。

## 感想

### 試すのが簡単

最初見たときなんだか難しそ〜〜と思ってしまいましたが、実際にはコマンドを打って対話的にやりたいことをClaudeに伝え続けるだけで完成したので、思ったより敷居が低いデザインになっていて感動しました。

### 金がかかる

APIキーを使った従量課金なので、庶民感覚だとお金がどんどん減っていくな…という感覚になります。個人で使うには上に挙げたスケジュールタスクや、Dispatch、/loop などで代用できないか検討したほうが良さそうです。

### ユースケースが難しい

便利なユースケースについてはちょっとまだ解像度が低いなと感じていて、専用の環境を用意しないとできないようなことがあまり身の回りに思いつかないですが、組織でSlackコマンドでなんか便利なことを効率的にしたいみたいな場合に結構効いてくるのかなと想像しました。

とはいえ、今までより柔軟に色々なことができるようになったことは間違いないので、みなさんも一度体験するために作ってみてはいかがでしょうか。

---

4/15 追記

<https://code.claude.com/docs/en/routines>

「PR来たら通知」みたいなユースケースは、新しくリサーチプレビューになったRoutinesでかなりカバーできそうです。Routinesは、プロンプト・リポジトリ・コネクタを一度設定しておいて、スケジュール・APIコール・GitHubイベントに応じて実行できる自動化機能で、Anthropicがホストするクラウドインフラ上で動くため、ラップトップを閉じていても動作します。

サブスクだとProユーザーは1日5回、Maxユーザーは15回、Team/Enterpriseは25回までという制限があるというものの、APIキーを使うとタスクによっては1回数ドルとか掛かったりするので、助かる人は多いのではないでしょうか。
