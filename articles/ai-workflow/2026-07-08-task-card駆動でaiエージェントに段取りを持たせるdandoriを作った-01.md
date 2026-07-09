---
id: "2026-07-08-task-card駆動でaiエージェントに段取りを持たせるdandoriを作った-01"
title: "Task Card駆動でAIエージェントに段取りを持たせるDandoriを作った"
url: "https://zenn.dev/yaona807/articles/d67650a82b1ffe"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-07-08"
date_collected: "2026-07-10"
summary_by: "auto-rss"
query: ""
---

## はじめに

DandoriというOSSを作りました。  
![DANDORI logo](https://static.zenn.studio/user-upload/3bd56eeec3c6-20260708.png)

リポジトリはこちらです。

Dandoriは、AIエージェントに「段取り」を持たせるためのオーケストレーターです。

もう少し具体的にいうと、GitHub Copilot Custom Agentsを使ったマルチエージェント構成において、作業前のスコープ整理、Workerへの委譲、結果確認を制御するための仕組みです。

ここでいうWorkerは、OrchestratorからTask Cardを受け取って作業するサブエージェントのことです。

AIエージェントを1対1で使うだけであれば、ユーザーがその場で会話を調整すればよいです。  
しかし、複数のエージェントを役割ごとに使い分ける場合は、それだけでは少し厳しくなります。

誰が作業を分解するのか。  
誰がスコープを決めるのか。  
誰がWorkerに何を渡すのか。  
誰が戻ってきた結果を確認するのか。

このあたりを明確にしないと、エージェントを増やしても運用が難しくなります。

そこで、AIエージェントに作業前の段取りを持たせるための仕組みとして、Dandoriを作りました。

## 背景

最近は、AIエージェントを使って実装、調査、レビュー、ドキュメント作成などを進めることが増えてきました。

GitHub Copilot Custom Agentsを使うと、用途に合わせたエージェントを定義できます。  
また、Agent Skillsを使うことで、特定タスクに必要なinstructions、scripts、resourcesを切り出すこともできます。

参考:

* GitHub Copilot Custom Agents
* GitHub Copilot Agent Skills

このような仕組みを使えば、たとえば次のように役割ごとのエージェントを用意できます。

* 調査を行うResearcher
* 実装や文章作成を行うWriter
* レビューを行うReviewer

役割ごとに分けること自体は便利です。

ただ、実際に複数のエージェントを使う前提で考えると、次の問題が出てきます。

* どのエージェントに何を任せるべきか分かりづらい
* 曖昧な依頼をそのまま渡してしまう
* エージェント側で勝手に作業範囲を広げてしまう
* 必要以上にリポジトリを探索してしまう
* どこまでが承認済みの作業だったのか分かりづらい
* 戻ってきた結果が、元の依頼の範囲内なのか判断しづらい

つまり、マルチエージェント構成では、Workerを増やすだけでは足りません。

Workerをどう制御するかが重要になります。

## Dandoriでやりたいこと

Dandoriでやりたいことは、AIエージェントをより自律的に動かすことではありません。

むしろ逆です。  
AIエージェントが勝手に動きすぎないようにすることを重視しています。

具体的には、次の状態を目指しています。

* Workerに曖昧な依頼を渡さない
* 作業前にスコープを明確にする
* ユーザーが承認した範囲だけをWorkerに渡す
* WorkerにはTask Cardの範囲内で作業することを求める
* OrchestratorがWorkerの結果を確認してから次に進む
* 既存のエージェントをWorkerとして使い回せるようにする

特に重要なのは、次のルールです。

```
Internal Task Card ⊆ approved Task Flow Review step
```

図にすると、以下のようなイメージです。

Workerに渡すTask Cardは、ユーザーが承認したTask Flow Reviewの範囲を超えてはいけない、という考え方です。

Dandoriは、OSレベルの権限制御やサンドボックスでWorkerの行動を強制的に止める仕組みではありません。  
あくまで、OrchestratorとWorkerの間に「承認済みの範囲だけをTask Cardとして渡す」という契約を置き、スコープが広がりにくい運用を作るためのものです。

## Dandoriの構成

Dandoriでは、エージェントを大きく2つに分けています。

| 種別 | 役割 |
| --- | --- |
| Orchestrator | 作業の分解、スコープ整理、承認確認、Workerへの委譲、結果確認を行う司令塔 |
| Worker | OrchestratorからTask Cardを受け取って作業するサブエージェント |

全体の流れは以下です。

少し大げさにいうと、OrchestratorがControl Planeを担当し、WorkerがExecution Planeを担当するイメージです。

つまり、考えることはOrchestratorに寄せます。  
実作業はWorkerに任せます。

この分離がかなり大事だと思っています。

Workerにマルチエージェントオーケストレーションの内部詳細を持たせると、責務が混ざってしまいます。  
Workerを追加したり差し替えたりするたびに、全体の設計を気にする必要も出てきます。

それは保守しづらいです。

Dandoriでは、WorkerはTask Cardを受け取り、その範囲内で作業し、結果をOrchestratorへ返す、という契約にします。

この形にしておくことで、既存のエージェントをWorkerとして使い回しやすくなります。

## Task Flow Review

Dandoriでは、いきなりWorkerに作業を渡しません。

まず、OrchestratorがTask Flow Reviewを作成します。

Task Flow Reviewは、ユーザーに提示する作業計画です。  
ここでは、次のような内容を明確にします。

* 何を行うか
* 何を行わないか
* どの順番で進めるか
* どこまで進めば完了か
* どの条件になったら止まるか

この段階で情報が不足している場合、OrchestratorはWorkerに委譲しません。  
先にユーザーへ確認し、作業範囲を明確にします。

たとえば「実装して」とだけ依頼された場合、実際にはいろいろなことが曖昧です。

* どのファイルを触ってよいのか
* テストまで行うのか
* 仕様変更を含めるのか
* 既存挙動を変えてよいのか
* まず調査だけなのか

この状態でWorkerに渡すと、Workerが良かれと思って作業範囲を広げてしまう可能性があります。

そのため、Dandoriでは作業前に段取りを整理します。

## Task Card

Task Cardは、Workerに渡す作業指示です。

ただし、単なる依頼文ではなく、実行契約に近いものとして扱います。

例としては、以下のような形です。

```
capability: repository-inspection
assigned_agent: Researcher
goal: Understand the repository structure and key entry points.
expected_output: A concise summary of the project layout, stack, and notable patterns.
non_goals: No code changes, no tests, no deployment work.
done_when: The top-level structure and key config files have been inspected.
stop_when: The repository cannot be accessed or contains no relevant files.
return_to: orchestrator
```

Task Cardでは、少なくとも次の内容を明確にします。

* どのWorkerに依頼するか
* 何を達成するか
* どのような出力を期待するか
* 何を行わないか
* いつ完了とするか
* どの条件で停止するか
* 結果をどこへ返すか

重要なのは、WorkerがTask Cardの範囲外に出ないようにすることです。

Workerには、Task Cardに書かれていない作業を勝手に追加しないことを求めます。  
関連しそうだから、便利そうだから、ベストプラクティスだから、という理由でスコープを広げるのではなく、範囲外の作業が必要そうな場合はOrchestratorへ返す、という契約にします。

この流れにすることで、作業の境界を明確にできます。

## 承認の扱い

Dandoriでは、Task Flow Reviewに対する承認を明確に扱います。

承認が必要な場合、Orchestratorは次のような承認行を求めます。

承認は、表示されたTask Flow Reviewに対してのみ適用されます。

そのため、追加条件や修正を含む返信は、承認ではなく変更要求として扱います。  
これにより、「承認したつもりではないのに作業が進む」ことを避けやすくしています。

このあたりは少し細かいですが、実際の運用では大事です。

AIエージェントに作業を任せる場合、「どの範囲を承認したのか」が曖昧だと、後から判断しづらくなります。  
そのため、承認も作業範囲の一部として明確に扱うようにしています。

## Dandoriに含まれるもの

Dandoriには、主に以下が含まれています。

* Orchestrator agent
* 参照Worker agents
  + Researcher
  + Pull Request Researcher
  + Writer
  + Reviewer
  + Browser QA
* code-review skill
* Dandoriのロゴなどのassets

ただし、これらのWorkerはDandoriの中核ではありません。  
あくまで参照実装です。

Dandoriの中核はOrchestratorです。

同梱されているWorkerをそのまま使ってもよいですし、自分がすでに使っているCustom AgentをWorkerとして使ってもよいです。

たとえば、実装用のエージェントをすでに持っている場合は、それをWorkerとして利用できます。  
レビュー用のエージェントを別で持っている場合も同じです。

重要なのは、WorkerがDandoriの内部詳細を知っていることではありません。

Orchestratorから渡されたTask Cardに従い、範囲内で作業し、結果を返せることです。

## なぜOrchestratorが必要なのか

最初は、各Workerを賢くすればよいのではないかとも考えていました。

しかし、Worker側に判断を寄せすぎると、責務が曖昧になります。

Workerが、作業範囲を判断し、必要な調査を判断し、他のWorkerに任せるか判断し、最終的な回答までまとめる状態になると、もはやWorkerなのかOrchestratorなのか分からなくなります。

この状態はかなり扱いづらいです。

Dandoriでは、この問題を避けるために、考えることをOrchestratorに集めています。

Orchestratorは作業を分解し、スコープを決め、Workerに渡すTask Cardを作ります。  
Workerは、そのTask Cardの範囲内で作業します。

この方が、責務が分かりやすいです。

## Orchestratorにはある程度強いモデルを使いたい

Dandoriでは、Orchestratorが作業分解、スコープ制御、委譲、結果確認、最終統合を担当します。

そのため、Orchestratorにはある程度強い推論モデルを使う方がよいと考えています。

Workerは、タスクに応じて軽量なモデルや専門的なモデルを選んでもよいと思います。  
しかし、司令塔であるOrchestratorが弱いと、Task Flow ReviewやTask Cardの品質が落ちやすくなります。

たとえば、次のような問題が起きやすくなります。

* 必要な確認を飛ばす
* 曖昧なTask Cardを作る
* Workerに広すぎる作業を渡す
* Workerの結果が範囲外でも見逃す
* 最終回答でスコープ外の内容を混ぜる

Workerを増やすことよりも、まず司令塔の品質を安定させることが重要だと思っています。

## トークン効率について

Dandoriを作るうえで、トークン効率も意識しました。

トークン効率というと、プロンプトを短くする話になりがちです。  
もちろん、それも大事です。

ただ、エージェント運用では、それ以上に「無駄な作業を発生させないこと」が重要だと思っています。

たとえば、次のような作業はすべてトークン消費につながります。

* 必要以上にファイルを読む
* 関係の薄いコードまで調査する
* 何度も同じ確認をする
* 承認されていない作業を進める
* Workerが推測で範囲を広げる

つまり、無駄な作業はそのまま無駄なトークン消費になります。

Dandoriでは、作業前にOrchestratorがスコープを整理し、Workerには境界付きのTask Cardだけを渡します。

これにより、トークンを「承認された作業」に使いやすくすることを目指しています。

また、すべてをagent定義に詰め込むのではなく、必要なレビュー観点などはskill側に切り出すようにしています。  
agent定義を重くしすぎないことも、運用上は大事だと考えています。

## 使い方

基本的には、Dandoriのagent定義とskillを、利用するGitHub Copilot環境で参照できる場所に配置して使います。

DandoriのREADMEでは、ユーザーレベルの配置例として以下を示しています。

```
mkdir -p ~/.copilot/agents ~/.copilot/skills
cp .copilot/agents/*.agent.md ~/.copilot/agents/
cp -R .copilot/skills/* ~/.copilot/skills/
```

ただし、GitHub CopilotのCustom AgentsやAgent Skillsは、利用する環境によって参照される配置場所が異なる可能性があります。

たとえば、GitHub DocsではCustom Agentsのrepository levelの配置先として `.github/agents/CUSTOM-AGENT-NAME.md` が案内されています。  
また、Agent Skillsについては、project skillsとして `.github/skills`、`.claude/skills`、`.agents/skills`、personal skillsとして `~/.copilot/skills`、`~/.agents/skills` が案内されています。

そのため、実際に配置する場合は、公式ドキュメントと自分の利用環境で有効な探索パスを確認してください。

利用時の流れは以下です。

1. Copilot ChatでOrchestratorを選択する
2. Orchestratorに作業を依頼する
3. OrchestratorがTask Flow Reviewを作成する
4. ユーザーが内容を確認する
5. 問題なければ承認する
6. OrchestratorがTask Cardを作成する
7. Workerへ委譲する
8. Workerの結果をOrchestratorが確認する
9. 最終結果をユーザーへ返す

このとき、承認はTask Flow Reviewに対して行います。

承認後に追加条件や修正が入った場合は、承認ではなく変更要求として扱います。

## まとめ

Dandoriは、AIエージェントに段取りを持たせるためのオーケストレーターです。

1対1でAIを使うだけであれば、ここまでの仕組みは不要かもしれません。  
しかし、複数のエージェントを役割ごとに使い分ける場合は、どこかで「誰が全体を制御するのか」という問題が出てきます。

Dandoriでは、Orchestratorが作業前にTask Flow Reviewを作成し、ユーザーが承認した範囲だけをTask CardとしてWorkerに渡します。

Workerは、そのTask Cardの範囲内で作業します。  
結果はOrchestratorへ返し、Orchestratorが確認して次に進みます。

AIエージェントを強くするだけでなく、どこまで任せるかを制御する。  
そのための仕組みとして、Dandoriを作りました。

リポジトリはこちらです。
