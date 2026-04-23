---
id: "2026-04-20-claude-managed-agents-で自作ai開発オーケストレーターを組み直した-01"
title: "Claude Managed Agents で自作AI開発オーケストレーターを組み直した"
url: "https://zenn.dev/atsumell_blog/articles/0fdd4b1e07dd15"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-04-20"
date_collected: "2026-04-21"
summary_by: "auto-rss"
query: ""
---

# Claude Managed Agents で自作AI開発オーケストレーターを組み直した ー 何が消えて、何が残ったか

こんにちは。株式会社Atsumellのまつしたです。

弊社では、簡単な実装タスクを素早く処理するため、GitHub の Issue にラベルをつけると、Claudeが起動してPRを作成し、CodeRabbitのレビューに対して修正するような、GitHub Issue 駆動のシンプルな開発オーケストレーターを自前で実装していました。(ClaudeのGitHub Appも便利ですが、もう少し複雑なワークフローを組みたくて自前実装をしています。)

すぐエラーで詰まったりするのを都度対処しながら業務の合間を縫って作っていたのですが、ちょうどClaude Managed Agents のベータ版が公開されたので、早速これを利用した構成に変更してみました。

この記事では、その組み直しによって「何が便利になって、何が残ったか」を整理します。

## 何を作っていたか

GitHub Issue に付いたラベルを起点に、AI が開発フローを順番に進めるオーケストレーターです。

* triage ラベル → Issue の整理と初期判断
* plan ラベル → 実装方針を固める
* implement ラベル → コードを書いてコミットする
* review-fix ラベル → PR レビューへの対応を行う

Issueについたラベルを、「AI の実行トリガー」として扱う構成です。やりたいこと自体はわかりやすいものですが、難しかったのは「AI を止まらせず、長時間動かす足場」の部分でした。

## Before: 自前構成で持っていた責務

Managed Agents に寄せる前の構成は次のようなものでした。

```
GitHub Webhook
  ↓
Express API
  ↓
WorkflowService（ラベルと状態を管理）
  ↓
JobDispatcher（フェーズに対応するジョブを選んで起動）
  ↓
各 Job
  ├── LocalJobRunner（Claude CLI をサブプロセスとして起動）
  ├── WorkspaceManager（Issue ごとに独立した作業フォルダ = worktree を生成）
  └── ArtifactStore（フェーズの成果物を保存して次に渡す）
```

構成としては動きます。しかし運用していくと、コードの主役が「プロダクトのロジック」ではなく、「実行基盤の維持」になりやすいものでした。

具体的には、次の責務をすべて自前で持つことになります。

* サブプロセスの起動・監視・終了(issueのラベルをSoTに)
* フェーズごとの作業フォルダの生成と後片付け
* 「plan フェーズで作った設計書を implement に渡す」といった成果物の受け渡し（artifact handoff）
* ラベルイベントと内部状態の整合
* 途中失敗時のリトライ・停止・復旧

**「AI に何をやらせるか」よりも、「AI を動かすランタイムの保守」に時間を取られていました。** 中心的な責務だけでも 5 種類あり、どれも削れませんでした。

## After: Managed Agents に寄せた後の構成

![](https://static.zenn.studio/user-upload/97455233efd2-20260417.png)

Managed Agents に寄せた後は、構成がかなり薄くなりました。

```
GitHub Webhook
  ↓
Express API
  ↓
SessionRouter（Issue と Session の対応付けを管理）
  ↓
Managed Agents API
```

アプリ側に残る中心的な責務は、大きく 3 つです。

1. Webhook を受け取る
2. どの Issue をどの Session に紐づけるかを管理する
3. ラベルやフェーズに応じて「次に何をさせるか」をメッセージとして組み立てる

主役が JobDispatcher や WorkspaceManager から SessionRouter に変わりました。設計の中心が「実行基盤を維持すること」から、「この Issue に対して次に何をさせるべきかを決めること」へ移った変化です。

### 何が変わったか

| 観点 | Before: 自前構成 | After: Managed Agents |
| --- | --- | --- |
| 実行単位 | Job / CLI サブプロセス | Session |
| 文脈の保持 | 成果物を保存して次フェーズに受け渡す | 同一 Session の会話履歴を使う |
| 作業フォルダ | Issue ごとに自前で生成・管理する | managed 環境に任せる |
| フェーズ移行 | ジョブ切り替え + 成果物受け渡しが必要 | 同じ Session に追加メッセージを送るだけ |
| GitHub 連携 | custom tool / 自前 RPC 中心 | 可能な範囲で MCP に寄せる |
| 失敗時の心配 | サブプロセス停止・フォルダ破損・成果物欠損 | タイムアウトなどによるSession中断・接続切れ・再開制御 |

持つ責務の種類が本質的なものに変わったと捉えるのが正確だと思います。

## 1 Issue = 1 Session が特に効いた

![](https://static.zenn.studio/user-upload/15fb21bd1a65-20260417.png)

今回いちばん大きかったのは、1 つの Issue に対して 1 つの Session を対応させられるようになったことです。

自前構成では triage → plan → implement を別ジョブで扱うため、フェーズをまたぐたびに「前段の成果物をどう次段に渡すか」が問題になっていました。Managed Agents では、同一 Session に追加メッセージを送るだけで続きとして処理が進みます。

ただ、「同一 Session なら文脈が保持される」ことと、「長期記憶が永続化される」ことは別の話です。Session が終了・破損した場合に備えて、復元情報は外部に持っておく必要があります。たとえば、Issue コメントにplan.mdの内容を残しておくといった方法をとっています。

## まとめ

Managed Agentsを利用していちばん変わったのは、めんどくさいセッション管理をManaged環境に任せられることでした。

ローカルの自前実装では、プロセス管理・作業フォルダ管理まで自分で管理する必要がありましたが、Claude Managed Agentsを利用することで、「次に何をさせるか」「どこで人間を挟むか」「失敗時に retry するか人間に戻すか」といった本質的な実装に集中できます。

「組織としてどうワークフローを設計するか」はどうしても人間が作る必要な領域だと思います。実行基盤の保守に時間を吸われるよりも、その判断に時間を使えるのであれば、採用する意味はかなり大きいと感じました。

※Claude Managed AgentsはClaudeのサブスクリプションに含まれずAPI料金が必要になるので、どれぐらいお金がかかるのかこれからウォッチしていきます...！
