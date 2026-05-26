---
id: "2026-05-25-slackのスタンプ1つで-claude-が改修prを作るbotを作った-01"
title: "Slackのスタンプ1つで Claude が改修PRを作るBotを作った"
url: "https://zenn.dev/uguisu_blog/articles/4d42dfe5cd18bd"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "zenn"]
date_published: "2026-05-25"
date_collected: "2026-05-26"
summary_by: "auto-rss"
query: ""
---

## 1. はじめに

こんにちは！！  
株式会社うぐいすソリューションズでエンジニアを細々とやっている中江です。

Slack に飛んでくる「これ直してほしい」「ここ調べてほしい」を流して忘れる、という事態を防ぐために、

> **Slack で `/post` → 依頼を投稿 → 管理者が承認スタンプ → GitHub Issue 自動作成 → Claude Code Action が走り PR が飛んでくる → 完成通知が元スレッドへ返ってくる**

という一気通貫の依頼受付 Bot を作りました。

```
Slack ─スタンプ→ meyasubako ─Issue作成→ GitHub ─@claude→ Claude Code Action ─PR→ GitHub
                       ↑                                                        │
                       └──────────── Webhook 経由で完成通知 ←────────────────────┘
```

本記事では、この Bot に実装した **7つの機能** を順番に解説します。

## 2. 動作デモ

まずは依頼 → スタンプ → PR が飛んでくるまでの流れを、各段階のスクリーンショットで一通り見ていただきます。

### ① `/post` でモーダルを開く

Slack の任意のチャンネルで `/post` を実行すると、カテゴリと内容を入力するモーダルが立ち上がります。  
![](https://static.zenn.studio/user-upload/0af79ff2de97-20260521.png)

### ② 依頼カードがチャンネルに投稿される

モーダル送信後、ヘッダ・本文・投稿者表記が整形されたカードがチャンネルに投稿されます。  
![](https://static.zenn.studio/user-upload/1dad5e5af01b-20260521.png)

### ③ 管理者が承認スタンプを押すと投稿内容でGithubにIssueを作成する

依頼カードを見た管理者が、トリガーに設定されたスタンプを押します。  
スタンプ押下後、bot が GitHub Issue を作り、URL を元スレッドに返信します。  
![](https://static.zenn.studio/user-upload/202e2d2c275f-20260521.png)

### ④ GitHub に Issue が作成されている

リンクを開くと、`@claude` メンション・依頼内容・必須制約・Slack情報が整理された Issue が出来上がっています。

![](https://static.zenn.studio/user-upload/ca00c5e89785-20260521.png)

### ⑤ Claude Code Action が起動

Issue 本文の `@claude` をトリガに、対象リポジトリの GitHub Actions で **Claude Code** ワークフローが自動起動します。  
![](https://static.zenn.studio/user-upload/34be84d13dc7-20260521.png)

### ⑥ Claude が Pull Request を作成

Claude が develop 起点で branch を切り、変更をコミット・push し、`Closes #N` を含む PR を作成します。

![](https://static.zenn.studio/user-upload/20689069a7c1-20260521.png)

### ⑧ 元 Slack スレッドへ PR 完成通知が返ってくる

GitHub Webhook 経由で meyasubako が PR 作成を検知し、最初の依頼スレッドに「Pull Requestが作成されました」と返信します。  
![](https://static.zenn.studio/user-upload/ea41110b172d-20260521.png)

---

依頼者は Slack のスタンプを1回押しただけで、**最後の PR URL までずっと同じスレッドの中で完結** します。

## 3. なぜ作ったのか

私は **社内システムの開発/保守担当** をしながら、並行して **受託案件にも参画** しています。受託側に集中したい一方で、社内システムへの改修依頼や問い合わせの対応にも一定の時間が取られる、という状況がありました。  
**社内タスク対応をなるべく自動化して、自分が手を動かす時間を受託に寄せたい** — これが今回の Bot を作った直接の動機です。

ベースとなる運用として、**社内システムに対する改修依頼は専用の Slack チャンネルに投稿してもらう** 形を以前から取っていました。これを起点に、

* 依頼の **可視化**(Slack でカード化、誰の何の依頼か明示)
* 依頼の **トリアージ**(承認スタンプを押すまで Issue 化しない)
* 採用された依頼の **着手**(Claude が PR を出してくれる)
* 完成の **追跡**(PR ができたら元スレッドへ通知)

までを一気通貫でつなげて、人間は「PR をレビューする」ところからスタートできる状態にしたい、と考えました。

## 4. システム構成

### 4.1. コンポーネント図

meyasubako は Node.js + Express で書かれた小さな Web Service です。AI 推論は持たず、Slack と GitHub の橋渡しに徹します。

### 4.2. シーケンス図 (時系列)

依頼1件あたりの実際の動きを時系列で並べると次のようになります。Slack の3秒タイムアウト対策として、すべての受信エンドポイントは **即 200 を返してから本処理を非同期実行** している点に注目してください。

## 5. 機能詳細

### 機能 1: `/post` スラッシュコマンドで依頼投稿モーダル

Slack のどのチャンネルでも `/post` と入力すると、依頼投稿用のモーダルが立ち上がります。

入力項目は2つだけ。

| 項目 | 内容 |
| --- | --- |
| カテゴリ | プルダウンから1つ選択(申請管理システム改修依頼 / 調査依頼 / 作成依頼) |
| 内容 | 自由記述のテキスト |

送信すると、そのチャンネルに整形済みのカード形式で投稿されます。**ヘッダにカテゴリ・本文・投稿者表記** が並び、依頼の種別と内容が一目で把握できます。

「依頼テンプレ用のチャンネル」を作る運用と違い、**話の流れの中で依頼を生成できる** のが地味に便利で、文脈を切らずに依頼を残せます。

### 機能 2: 承認スタンプによる Issue 化トリガー

投稿された依頼カードに、**許可されたユーザー** が **特定のスタンプ** を押すと、その依頼が GitHub Issue に変換されます。

これにより、

* フリーフォーマットの相談・愚痴が **誤って GitHub に流れない**
* スタンプを押す = 「これは正式に取り掛かる依頼です」というトリアージが成立
* 押せる人は環境変数で制御 (`ALLOWED_REACTION_USERS`) できるので、誰でも勝手に Issue 化できない

現在は **「申請管理システム改修依頼」カテゴリの依頼のみ** が Issue 化対象。それ以外のカテゴリは Slack 内で完結する設計です。「いま GitHub にしたい依頼」と「Slack の中で会話で済む依頼」の境界を、カテゴリと承認の2段階フィルタで設定できます。

### 機能 3: ユーザー名・チャンネル名の自動解決

GitHub Issue に Slack の生 ID(`<@U06MKT2897V>` / `C0ABFD1DS1M`)がそのまま出ると、誰も読めません。  
そこで Issue 作成時に Slack API を叩き、

* 投稿者・承認者の **表示名(@kouki など)**
* 依頼が投稿された **チャンネル名(#general など)**

を自動で解決して Issue 本文に埋め込みます。

仕様として **解決に失敗した場合は ID をそのまま出さず、その行を省略** するようにしてあります。読みにくい情報を中途半端に残すぐらいなら、いっそ無いほうが良いという判断です。

### 機能 4: `@claude` メンション付きの Issue 自動作成

承認されると meyasubako が GitHub REST API で Issue を作成します。中身は次の構成。

* **タイトル** — 依頼本文の最初の60文字を要約として採用
* **本文先頭** — `@claude この Issue の依頼内容を実装してください。` を必ず挿入
* **依頼内容** — Slack に投稿されたカードを丸ごと転載(mention は名前解決済み)
* **必須制約** — `develop` 起点で branch を作る、main / master へ PR を作らない、不要な大規模リファクタを避ける、等
* **完了条件** — テストが通る、PR 本文に変更内容を書く、レビュー待ち、等
* **Slack情報** — チャンネル名・承認者(解決できた場合のみ)
* **HTML コメント (非表示)** — `<!-- meyasubako:thread channel=... ts=... -->` という形で、PR完成通知に使う情報を埋め込み
* **ラベル** — `from-slack`, `ai-task`

このとき先頭の `@claude` メンションが次の機能 5 のトリガになります。

### 機能 5: Claude Code Action による自動 PR 作成

対象リポジトリには `anthropics/claude-code-action@v1` を組み込んだ workflow を1つ置いてあり、**Issue 本文に `@claude` が含まれていると自動的に起動** します。

workflow 内では Claude にこう指示してあります。

```
mode: agent
claude_args: >-
  --allowed-tools "Edit,Write,Read,Glob,Grep,MultiEdit,
  Bash(git:*),Bash(gh:*),Bash(npm:*),Bash(node:*),Bash(npx:*),..."
prompt: |
  あなたは自律的に動作するソフトウェアエンジニアのエージェントです。
  この Issue 本文の要件を必ず実装まで完遂し、Pull Request を作成して終了すること。
  ...
```

これにより Claude は GitHub の Ubuntu Runner 上で

1. `develop` 起点で `claude/<要約>` ブランチを作成
2. Issue 内容を読み、`Read`/`Grep`/`Glob` で対象コードを把握
3. `Edit`/`Write` で実装
4. `git commit` & `git push`
5. `gh pr create --base develop --body "...Closes #<番号>"` で Pull Request 作成

までを自律実行します。  
**API キー方式ではなく Claude Code Max サブスクリプションの OAuth トークン** (`claude setup-token`) で動かしているため、追加の API 課金は発生しません。

### 機能 6: PR 作成時の Slack スレッド通知

Claude が PR を出したら、依頼者は **元のスレッドにそのまま通知を受け取れる** ようにしました。これが意外と重要で、「依頼 → 放置 → どうなった?」という遅延を防ぎます。

実現方法:

1. 対象リポジトリに **GitHub Webhook** を設定し、`pull_request.opened` イベントを meyasubako の `/github/webhook` エンドポイントへ POST
2. meyasubako は **HMAC SHA-256** で署名検証(`GITHUB_WEBHOOK_SECRET` を共有秘密として持つ)
3. PR 本文の `Closes #N` から **元 Issue 番号を逆引き**
4. Issue 本文に埋め込んでおいた **HTML コメント** から元 Slack スレッドの `channel_id` と `ts` を取り出す
5. `chat.postMessage` で「Pull Requestが作成されました: <URL>」と元スレッドに返信

依頼者は Slack を一歩も出ずに、

```
依頼カード
 ├─ スレッド: GitHub Issueを作成しました <Issue URL>
 └─ スレッド: Pull Requestが作成されました <PR URL>
```

という導線で最終成果物まで辿れます。

### 機能 7: 設定の柔軟性

すべての主要パラメータは環境変数で差し替え可能です。

| 環境変数 | 用途 |
| --- | --- |
| `TARGET_REACTION` | 承認スタンプの絵文字名 |
| `ALLOWED_REACTION_USERS` | 承認できる Slack ユーザー ID(カンマ区切り) |
| `GITHUB_OWNER` / `GITHUB_REPO` | Issue 作成先リポジトリ |
| `ISSUE_BASE_BRANCH` | Claude に「ここを base にして PR を作って」と伝える branch 名(既定 `develop`) |
| `GITHUB_WEBHOOK_SECRET` | PR 通知 Webhook 用の共有秘密 |

別チームに展開する際は環境変数を差し替えるだけで使い回せます。

## 6. 実装中につまづいたところ

開発中に踏んだ落とし穴を2つだけ共有します。

### `permission_denials_count: 3` — 動いてるように見えて動いていない

Claude Code Action を初回起動した時、ジョブは緑色で完了したのに **PR が来ない**。ログを掘ると:

```
{ "is_error": false, "num_turns": 5, "permission_denials_count": 3 }
```

Claude が3回ツール呼び出しを拒否されていました。デフォルトでは `Bash(git:*)` や `Edit`/`Write` が許可されていなかったのです。`claude_args: --allowed-tools "..."` で必要なツールを列挙したら一発で PR まで届くようになりました。

### `num_turns: 1` — Claude がコメントだけ返して終わる

別の機会には `permission_denials_count: 0` なのに PR が出ず、`num_turns: 1` で終わるパターンに遭遇。**Claude が「実装します」とコメントを返して、そのまま停止していた** のが原因でした。

対策は workflow で `mode: agent` を明示し、プロンプトに「**コメントだけで終わってはいけない。実装まで完遂すること**」と明記するだけ。これで一発で実装に着手するようになりました。

「動いてるように見えて動いてない」型の問題は気づきにくいので、`num_turns` と `permission_denials_count` の2つのメトリクスは常に最初にチェックするのがおすすめです。

## 7. まとめ

依頼 → 承認 → 実装 → 通知の4ステップを、依頼者は Slack のスタンプ1回だけで起動できます。**Bot 自体は AI 推論を一切持たず、Issue を作るところで責務を終える**シンプルな設計にしたことで、Claude のクォータ・トークン・モデルの選択は対象リポジトリ側で完結し、必要に応じて差し替えやすくなっています。
