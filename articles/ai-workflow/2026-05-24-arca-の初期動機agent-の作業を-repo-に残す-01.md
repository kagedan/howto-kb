---
id: "2026-05-24-arca-の初期動機agent-の作業を-repo-に残す-01"
title: "Arca の初期動機：agent の作業を repo に残す"
url: "https://zenn.dev/sisiodos/articles/a7d5f317a69f94"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-24"
date_collected: "2026-05-25"
summary_by: "auto-rss"
query: ""
---

# Arca の初期動機：agent の作業を repo に残す

個人プロジェクトとして、[Arca](https://github.com/sisiodos/arca) というものを作っています。

Arca は、Claude や Codex のような agent に作業してもらうときに、その作業内容、判断、発見、引き継ぎを repo 内に残すための実験的な仕組みです。

この記事では、現在進めている発展的な考察ではなく、Arca を作り始めた頃の動機を記録しておきます。  
これは当時のログと、現在の記憶を照らし合わせた振り返りです。後から意味づけしている部分もありますが、  
なるべく当時の自己理解から離れすぎないように書いています。

Git の履歴を見ると、Arca を init したのは 4/9 でした。当時の自己理解では、Arca は自律開発エージェントのための markdown-based harness でした。Claude や Codex に repository 内で作業してもらうとき、どのルールを読ませるのか、どの role で動かすのか、どの成果物を残すのか、どのように review するのかを、repo 内に明示したいと考えていました。

## Arca を作り始める前の agent 設計の理解

Arca を作り始める少し前、私は agent 設計を「状態・射影・表現」の問題として整理していました。

LLM は内部状態を持つ主体というより、毎回与えられた入力に応答するステートレスな関数に近い。  
そのため、agent 設計の本質は、どの状態を保持し、そのうち何を選び、どのような形で LLM に渡すかにある、と考えていました。

また、agent を単なる prompt や tool ではなく、harness の中で運用するものとして捉えていました。

4/11 に書いたメモでは、harness を次のような要素に分解していました。

```
Instruction
Knowledge
Execution
Observability
Validation
Constraint
Improvement Loop
```

これは当時、自律開発エージェントを安定して運用するための機能分解として考えていたものです。

今から見ると、この時点ではかなり広い LLM システム設計として考えていました。その中で Arca は、特に agent の作業を記録し、検証し、次に引き継ぐための repo-local な実験として始まったものです。

## 初期動機: agent の作業を消さないために

この時点での動機は、かなり素朴なものでした。

Claude や Codex に作業してもらうと、その場ではかなり有用な出力が得られます。しかし、セッションが終わると agent は忘れます。人間である私も、数日経つと、なぜその作業をしたのか、どこまで進んだのか、何が発見だったのかを忘れてしまいます。

そのため、最初に必要だったのは、agent の作業をセッション外に残すことでした。

```
agent の活動を記録に残す
作業内容を repo に残す
次の自分や次の agent が再開できるようにする
```

この段階で必要だったのは、agent が何をしたのか、どのファイルを追加・変更したのか、どのように検証したのか、何が残作業なのかを、repo 内に残すことでした。

その最初の設計意図を記録したのが `arca/docs/design/INITIAL.md` でした。

## 4/9: INITIAL.md から scaffold を作る

Arca の最初の作業は、コード機能の実装ではありませんでした。

私が書いた `arca/docs/design/INITIAL.md` という設計ノートに合わせて、repository scaffold を整える作業でした。

当時の action log には、次のような作業が記録されています。

```
Task:
  Align the repository scaffold with the updated arca/docs/design/INITIAL.md.

Actions Taken:
  - replaced env.yaml with env.md
  - added templates
  - added logs
  - added procedures
  - added task lifecycle procedure
  - added GitHub pull request template

Outcome:
  The repository scaffold now matches the current initial design document
  and includes the new artifact loop from logs to procedures.
```

つまり「設計ノートを repo 構造に変換する」という意識で設計していました。

```
INITIAL.md
  -> scaffold
  -> templates
  -> logs
  -> procedures
  -> PR template
```

当初の Arca は、  
設計意図を repo 内に置き、それを agent が読める作業契約へ変換し、さらに作業結果を action log として残すことで、  
自律開発を安全に運用できる仕組みを目指していました。

この時点の log はまだ素朴でした。何をしたか、何を検証したか、何が follow-up かは残っていましたが、なぜその構成が必要だったのか、どの設計判断と対応しているのかは、log 単体からは十分に読めませんでした。

理由は `INITIAL.md` にあり、作業記録は action log にあり、成果物の変更履歴は repository diff にある。  
後から見ると、それらを読み合わせることで流れは分かりますが、当時の log はまだ作業記録に近いものでした。

## INITIAL.md における Arca の位置づけ

`INITIAL.md` では、Arca は次のように定義されていました。

```
Arca is a scaffold-based agent environment for software delivery with a strict PR-based workflow.
```

当時の中心は software delivery でした。  
main branch を保護し、topic branch で変更し、pull request を通じて review する。  
つまり、開発作業を agent に任せるための安全な作業足場として設計していました。

設計目標も、かなり開発ハーネス寄りでした。

```
1. agent system を最小構成から始める
2. execution model を repo 内に明示する
3. 共有ルールと role-specific behavior を分ける
4. pull-request-first workflow を徹底する
5. repository を環境間で portable に保つ
```

この時点では、Arca を「agent をどう動かすか」という harness / scaffold として位置付けていました。

## Scaffold としての成立

INITIAL.md の中心概念は scaffold でした。

Scaffold は、agent が作業前に読む安定した contract として定義されていました。

```
AGENTS.md
  repo-wide operating contract

arca/env.md
  execution and tool expectations

arca/rules.md
  shared behavior and workflow rules

arca/agents/*.md
  narrowly defined agent roles
```

これは、hidden prompt や外部サービスに依存せず、repository を読めば agent behavior が分かるようにするための設計でした。

当時の関心は、agent の行動を repo 内の markdown contract によってどこまで安定させられるか、という点にありました。

## procedures の導入

INITIAL.md の near-term next steps には、次の項目が含まれていました。

```
Introduce Action Log as a markdown-based artifact (`arca/logs/`), capturing agent actions per task.
Define initial procedure storage (`arca/procedures/`) and establish a loop from action logs to procedures.
```

ここには、現在の Arca の姿に繋がる、ある発想が含まれています。

```
action logs
  -> procedures
```

つまり、agent の作業を raw log として残し、そこから再利用可能な procedure を育てるという発想です。

当時は `procedures` と呼んでいましたが、現在の理解では `skills` と呼ぶのが良いと考えています。

```
当時: procedures
現在: skills
```

この名前の変化は、理解の変化をよく表していると思います。

Procedure は、繰り返し使われた実績ある手順の記録です。Skill は、agent が再利用できる作業能力です。最初は「手順を残す」つもりでしたが、使っていくうちに、それは agent に継承される operational knowledge に近いものだと見えてきました。

```
raw action log
  -> reusable procedure
  -> skill
  -> future behavior
```

この段階で、Arca は作業ログに残る記録から、その経験を未来の agent の作業へフィードバックするためのループを持ち始めていました。

## role 分離の進化

初期の agent role は意図的に小さく始めていました。

```
orchestrator
implementer
reviewer
```

最初は、自律開発 workflow を想定していたため、この三つで十分に見えていました。

```
orchestrator
  作業を整理し、次に誰が何をするかを決める

implementer
  実際に repository を変更する

reviewer
  変更内容、検証、workflow 違反、regression risk を確認する
```

しかし、Arca を使い続けるにつれて、role の分離は一度かなり細かくなっていきました。

これは、私自身が実装以外の作業が増えてきたと感じていたことに加えて、Codex の推奨でもありました。また、当時見ていた他の agent harness でも、planner、researcher、executor、reviewer のように role を分ける設計が多く見られました。

そのため、Arca でも一時期は role を細かく分ける方向を採用しました。

```
researcher
  外部情報や source を集める

spec-planner
  source や調査結果から、実装前の仕様・計画を整理する

implementer
  承認された task や spec に沿って変更する

reviewer
  成果物を検査し、workflow 違反や validation 不足を指摘する

procedure-curator / skill-curator
  action logs や反復作業から reusable skill を抽出する

scaffold-curator
  AGENTS.md、rules、env、roles、templates などの scaffold 自体を保守する
```

この分離には意味がありました。調査、仕様整理、実装、レビュー、scaffold 保守、skill 整理は、同じ agent にまとめると責務が混ざりやすかったからです。

ただし、現在は逆に role を統合する方向に戻っています。細かく分けすぎると、role の理解や handoff の負荷が増え、個人プロジェクトとしては運用が重くなるためです。

現在は、おおまかに次の三つへ寄せています。

```
builder
  調査・設計・実装など、作る側の作業を担う

reviewer
  成果物を検査し、問題や不足を指摘する

curator
  logs、skills、scaffold などを整理し、再利用可能な形に保つ
```

つまり、role 分離は一方向に細かくしていったのではなく、一度細分化して責務の違いを見たうえで、現在は実運用に合わせて再統合している段階です。

## handoff の設計

handoff の設計は、主に Codex の提案を取り入れながら進めました。

最初は、人間が agent に作業を渡し、agent が結果を返すだけでも十分に見えていました。しかし、作業が長くなると、次の問題が出てきました。

```
次の agent がどこから読めばよいか分からない
何が完了し、何が未完了か分からない
どの検証が済んでいるか分からない
どの判断が保留なのか分からない
```

そこで handoff が必要になりました。

handoff は、単なるメモではありません。次の agent または次の自分が、作業を安全に再開するための state transfer です。

```
current state
completed work
remaining work
validation status
known risks
recommended next action
```

handoff によって、agent の出力は repo に残る継続可能な作業状態になりました。

## 当時は markdown-based harness だと思っていた

この段階では、私は Arca を markdown-based harness だと思っていました。

Markdown で rules、roles、env、templates、logs、procedures を書き、agent にそれを読ませて作業させる。  
実行 runtime を自作するのではなく、Codex や Claude のような既存 agent harness に repository を読ませる。  
Arca は、その repository 側の契約である、と考えていました。

この理解は半分正しかったと思います。

Arca はたしかに markdown-based でした。repo 内の自然言語 contract を agent に読ませるという意味では、harness / scaffold として機能していました。

ただし、この頃にすでに、価値の中心は agent を動かすことそのものではなく、agent の作業が後から読める形で残ることにあるのではないか、と感じ始めていました。

```
何をしたか
なぜそうしたか
何を検証したか
何が残ったか
何を次に渡すか
```

この理解は、その後の Arca の使い方につながっていきます。

## まとめ

Arca の初期動機は、自律開発エージェントを安全に動かすための markdown-based harness を作ることでした。

しかし、その最初の段階から、単に agent を動かすだけでなく、agent の作業を記録に残し、人間と agent が後から継続できるようにすることが重要な関心でした。

```
markdown-based harness
  -> repo scaffold
  -> action log
  -> procedures / skills
  -> handoff
```

この段階では、まだ現在のような広い理解には至っていませんでした。INITIAL.md を書き、scaffold を作り、agent に作業させ、logs と procedures を運用し、role と handoff を分けていく中で、少しずつ Arca の意味が見えてきました。
