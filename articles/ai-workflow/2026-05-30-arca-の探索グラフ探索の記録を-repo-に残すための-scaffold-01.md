---
id: "2026-05-30-arca-の探索グラフ探索の記録を-repo-に残すための-scaffold-01"
title: "Arca の探索グラフ：探索の記録を repo に残すための scaffold"
url: "https://zenn.dev/sisiodos/articles/c11580fb40978a"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "LLM", "zenn"]
date_published: "2026-05-30"
date_collected: "2026-05-31"
summary_by: "auto-rss"
query: ""
---

# Arca の探索グラフ：探索の記録を repo に残すための scaffold

Arca の開発を続ける中で、ある問題に気づいていました。

action log には「何をしたか」が残ります。PR には「何を変えたか」が残ります。しかし、「なぜその方向を選んだのか」「どの候補を検討して、なぜ採用しなかったのか」という探索の跡は、どこにも残らないままでした。

この記事では、探索グラフ（exploratory graph）という仕組みを考案し、それを scaffold に組み込んでいったプロセスを振り返ります。

## Stage 9 の問題意識

Stage 8 で、Arca は roadmap からタスクを生成する仕組みを得ました。agent が roadmap を読んで、次にやるべき作業を自分で見つけてくる、という流れです。

しかし、Stage 8 の完成によって、別の問題が浮き上がってきました。

Arca の roadmap は、やや遠い将来の目標を段階的に定めるものです。その「次の目標を何にするか」という問いに答えるために、私はチャットサービスや検索サービスを使いながら、候補を探したり、方向性を考えたりしていました。この探索は人間である私がやっていたわけですが、ある時こう思いました。

```
この探索プロセスそのものを、ある程度エージェントに委任できないだろうか
```

これは「agent に勝手に goal を決めさせる」という話ではありません。問題は、探索の結果を repo に残す仕組みがなかったことでした。

チャットで候補を考え、検索で情報を集め、比較して選択する。そのプロセスは人間の頭の中にあるか、消えたセッションの中にあるかのどちらかでした。

```
なぜその goal が選ばれたのか、記録がない
どの候補を検討して、なぜ却下したのか、残っていない
その判断に至るまでの観察や発見が、次の agent に伝わらない
```

設計ノートに書いた当時の言葉で言えば、「探索の跡が implicit すぎる」という状態でした。探索プロセスをエージェントに委ねていく前に、まず探索の記録を repo に残す形式が必要だ、という認識が Stage 9 の出発点になりました。

## 最初の設計：探索をグラフとして残す

Stage 9 の目標として定めたのは、「exploratory activity を repository-owned な証拠として可視化する」ことでした。

ただし、このとき強く意識したのは、グラフを workflow authority にしてはならない、という制約でした。

```
グラフがやるべきこと
  - goal がなぜ選ばれたかを説明する
  - 却下された候補とその理由を保存する
  - 発見を source に繋ぐ
  - risk と follow-up candidates を示す

グラフがやるべきでないこと
  - GOAL.md を置き換える
  - handoff を受け取る
  - review を承認する
  - PR を作成・マージする
  - role を dispatch する
```

この「やるべきでないことリスト」を先に定めたのは、当時の経験から来ていました。Arca の設計を通じて繰り返し学んだのは、新しい artifact を追加するとき、それが workflow を乗っ取るリスクを最初から制限しておかないと、後から境界を引き直すのが非常に難しくなる、ということでした。

ただし、これには別の側面があります。scaffold に書く設計原則は、エージェントへの指示として機能するために、意図的に強く書く必要があります。エージェントは曖昧な余地があれば、そこに踏み込む可能性がある。だから制約は明確に、強く書く。

しかし、それを書いた人間の側では、その制約自体がまだ仮説であることがあります。「graph を workflow authority にしてはならない」という原則も、エージェントに誤解を与えないように強く書いてはいますが、本当のところはまだ可能性を探っている段階でした。scaffold への記述の強さと、設計者の確信の強さは、必ずしも一致しない。これは agent と協調して設計を進めていく上での、一つの現実だったと思います。

## 二層分離の設計

探索グラフの具体的な設計として選んだのは、二層に分けることでした。

```
graph.yaml
  機械可読なグラフトポロジー
  ノード、ソース、エッジの構造
  LLM なしでも走査できる

nodes/*.md
  Markdown によるノード本文
  観察、発見、理由、open question
  人間と LLM 両方が読める
```

`graph.yaml` は topology の authority であり、node 本文の意味は Markdown ファイルにある、という分離です。

当時なぜこの設計を選んだかを振り返ると、理由はいくつかありました。

一つは、グラフ構造を LLM に依存せず検証できるようにしたかったこと。もう一つは、Markdown node 本文に self-contained な文脈を書けるようにしたかったこと。

そしてもう一つ、別の流れから来た理由がありました。Arca では `AGENTS.md` を目次的に使い、「全部読まなくても始められる」という方向に scaffold を整えてきていました。探索記録も同じ考え方で設計できる、と気づいたことです。

```
全部読む必要はない
探索ノードの関係が辿れさえすればよい
必要なノードだけを、必要なときに読む
```

`graph.yaml` があれば、topology を先に把握して、必要な node body だけを選んで読める。探索記録を全量読む必要をなくす、という分離が機械可読な manifest によって測れると考えました。

「graph」という名前については、探索は流れを持ち、分岐もあるので、tree として設計することもできました。しかし、より一般的な graph という名前にしておきました。いずれ本当の graph になるだろう、という予感があったからです。現在の運用実態は、一本道の path だったり、分岐のある tree 程度です。

後から外部の graph database や search index を使う可能性も残しつつ、それらは必ず「repository files から派生した derivative」として位置づけ、repository が truth のままであるようにしました。

## vocabulary を小さく保つ

最初のノードタイプは次の八種類でした。

```
question   - 探索が始まる問い
source     - 参照した情報源
finding    - 観察や発見
candidate  - 検討した選択肢
decision   - 採用した判断
risk       - 確認されたリスク
rejected   - 却下した候補
next       - 保留・後続に回した事項
```

エッジタイプも、`derived_from`、`supports`、`weakens`、`contradicts`、`led_to`、`answers`、`selects`、`defers`、`blocked_by` という最小セットから始めました。

「vocabulary を小さく保つ」という方針は、設計の中で何度も書きました。実際に使ってみるまで、どのノードやエッジが本当に必要かはわからない。先に細かく定めると、使われない vocabulary が増えて schema が重くなる。この教訓は、role 分離を一度細分化してから再統合した経験から来ていました。

## 最初のグラフ：Stage 9 goal selection

実装した最初のグラフが `EXP-001` でした。これは「Stage 9 は何を最適化すべきか」という問いを root に持つ探索グラフです。

```
N-001: question - Stage 9 は何を最適化すべきか
N-002: finding - Stage 8 で visible intake が実現した
N-003: risk - 探索の跡が implicit なまま
N-004: candidate - exploratory graph を導入する
N-005: rejected - 外部 index を authority にする
N-006: decision - Stage 9 で exploratory graph を実装する
N-007: next - 実装の具体的な作業
```

このグラフは、Stage 9 の goal を選んだ探索の証拠として残り、その後 `closed` に移行しました。Arca の設計が、グラフ自体をグラフで記録するという、ある種の自己参照的な状態になっていました。

## root node への情報集約

実装を進める中で、一つ設計上の問題に気づきました。最初は `graph.yaml` の top-level に `title` フィールドを持たせていましたが、これではグラフのタイトルや scope が topology manifest に混入してしまいます。

そこで schema version 2 から、`title` を top-level から削除して、代わりに `root` node id のみを top-level に残しました。グラフの意味は root node の Markdown 本文が持つ、という設計です。

```
graph.yaml
  schema_version: 2
  id: EXP-001
  root: N-001       ← ここだけが entrypoint
  created: ...
  status: active
  nodes: ...

nodes/N-001-question.md
  ← ここにグラフのタイトル・問い・scope を書く
```

機械可読な manifest は topology だけを持ち、意味は Markdown が持つ。この分離は、後から見ても良い判断だったと思います。

## catalog による発見

探索グラフが増えていくと、次の問題が出てきました。グラフの一覧が repo を見ても分からない、という問題です。

ここで、一つの設計上の考えがありました。複数の探索グラフを、一つの大きなグラフに統合する必要はない、という考えです。

それぞれの exploratory graph は、一つの question を中心として広がるものです。別のグラフとの関係は、最初のうちは見えないことの方が多い。グラフ同士を早期に繋ごうとすると、まだ見えていない関係を先取りして構造化することになり、それは探索の本来の性質と合いません。

そこで選んだのは、グラフ同士を統合するのではなく、それぞれを独立したまま列挙する、という設計でした。

そのために `arca/explorations/catalog.yaml` を追加しました。これはすべての exploratory graph を列挙する discovery index です。

```
catalog.yaml
  - id: EXP-001
    graph: EXP-001/graph.yaml
    status: closed
    root: N-001
    root_body: EXP-001/nodes/N-001-question.md
```

catalog はあくまで「どこを見ればよいか」を示す index であり、グラフの意味はここには書かない。グラフのタイトルや問いは root node に、topology は `graph.yaml` に、という原則を catalog まで一貫させました。

また、graph integrity checker として `run-exploration-check.sh` を作り、catalog の整合性、node body の存在確認、edge endpoint の validity などを自動で検証できるようにしました。

## context-reading skill の導入

グラフを作っても、agent がそれを「いつ読むか」「何を選ぶか」が明確でないと、グラフは書かれたまま参照されない artifact になってしまいます。

そこで `arca/skills/context-reading.md` という skill を追加しました。これは、agent が exploratory graph を読む手順を定めたものです。

```
1. catalog.yaml を読んで候補グラフを探す
2. status と root body path でグラフを選ぶ
3. root node body を読んでから graph.yaml を読む
4. edge を辿って必要な node body と source ref を読む
5. action log に実際に読んだ graph、node、source を記録する
```

ただし、この skill を追加した後でも、agent が実際にグラフを使うかどうかは安定しませんでした。後になってわかったのは、問題は skill の内容ではなく、「exploratory な作業をグラフで記録すべき」というシグナルが builder の bootstrap に入っていなかったことでした。

この問題を修正するために、builder の起動時の読み込み対象に exploratory graph の検討を明示的に組み込みました。グラフを使うかどうかは task intake の段階で判断する、という設計にしました。

```
旧: グラフは exploration reading のオプション
新: task intake 時に「グラフを使うか、既存グラフに追記するか、なぜ使わないか」を明示する
```

## explorations → contexts への改名

Stage 9 が落ち着いてきたころ、次の考えが浮かびました。

planning も、同じようにグラフにできるのではないか。

roadmap の次の目標を選ぶプロセスは、探索とは少し異なる性質を持ちます。候補を集めて比較するだけでなく、なぜその方向を選んだのか、なぜ他の候補を保留したのかという判断の根拠を残すことが、planning における記録の中心になります。

しかし、ここで問題がありました。当時の名前は `exploratory graph` であり、格納場所は `arca/explorations/` でした。planning の記録をここに置こうとすると、名前と責務が合わなくなります。

最初に考えたのは、`planning graph` と `exploratory graph` を別々に設ける、という案でした。しかし、考えるほど、両者の vocabulary はほぼ共通になることが見えてきました。

`candidate`、`rejected`、`decision` といったノードタイプは、planning のために新たに追加しようとしていたわけではありませんでした。これらはすでに Stage 9 の最初のグラフ `EXP-001` から使われていたものです。「Stage 9 の goal に何を選ぶか」という探索自体が、候補を並べ、却下し、決定する、という構造を持っていたからです。

```
EXP-001 の最初のグラフ（Stage 9 実装時）

  N-004: candidate - exploratory graph を導入する
  N-005: rejected  - 外部 index を authority にする
  N-006: decision  - Stage 9 で exploratory graph を実装する
```

つまり、goal 選択という探索は、最初から planning と同じ語彙を使っていた。planning graph を別に設けようとしたとき、追加すべき vocabulary がほとんどない、ということが分かったのです。

graph を二種類に分けても、node タイプもエッジタイプも変わらない。分けることで得られるものより、管理コストの方が大きくなる。

そこで、両方をまとめて扱える抽象的な名前に置き換えることにしました。`context graph` です。探索も planning も、どちらも「文脈の記録」として扱える。

格納場所を `arca/explorations/` から `arca/contexts/` に改名し、グラフ id も `EXP-*` から `CTX-*` に変えました。

```
当初: arca/explorations/EXP-001/
現在: arca/contexts/CTX-001/
```

この名前の変化は、理解の変化を表しています。「探索の記録」として始まったものが、「文脈の記録」という広い概念に育っていきました。

```
EXP (exploration) → CTX (context)

  探索の記録
  計画の根拠
  歴史的証拠の読み込み
  設計判断の traceability
```

## グラフは操作の記録であり、要約ではない

探索グラフを設計するにあたって、一つの使い方を防ごうとしていました。「探索が終わってから、その結果をグラフに整理する」という使い方です。

探索の結果だけをグラフに書くと、なぜその候補を却下したのか、どのリスクが未解決のまま残ったのか、何を後続に回したのか、という過程が抜け落ちます。グラフが結論だけを保持する要約になってしまうと、次の agent が同じ地点から探索をやり直す可能性が生まれます。

そこで、グラフを操作の記録として機能させるために、二つの設計を組み合わせました。

一つは、`rejected`、`risk`、`next` といったノードタイプを vocabulary に含めること。結論に至らなかったノードを first-class に扱うことで、過程が記録に残るようにしました。

```
グラフは操作の記録であり、操作の要約ではない

  探索しながら node を追加する
  候補が却下された瞬間に rejected node を作る
  リスクが見えた時点で risk node を追加する
  保留になった時点で next node を追加する
```

もう一つは、`context-reading.md` にその意図を明示すること。agent が graph work を始める前に読む skill に「グラフは探索しながら育てるものであり、後から整理するものではない」と書いておくことで、要約としての使い方を防ぐ設計にしました。

## まとめ

探索グラフの設計は、一つの動機から始まりました。

```
「なぜその判断に至ったか」が残らない問題を解くために、
探索の跡を repository に残す仕組みが必要だった
```

実装の過程では、いくつかの設計の変化がありました。

```
当初: explorations として、探索の記録を残す
経由: graph.yaml と Markdown の二層分離
経由: root node へのタイトル・scope の集約
経由: catalog による発見可能性の確保
経由: context-reading skill による読み方の標準化
経由: builder bootstrap への組み込みで使用を促進
現在: contexts として、文脈の記録全般を扱う
```

最終的に残ったのは、次のような仕組みです。

```
arca/contexts/catalog.yaml        - 発見のための index
arca/contexts/CTX-*/graph.yaml    - 機械可読な topology
arca/contexts/CTX-*/nodes/*.md    - 人間可読な node 本文
arca/skills/context-reading.md   - 読む手順
arca/scripts/run-context-check.sh - 整合性の検証
```

そして、設計を通じて繰り返し確認したことがあります。

グラフは evidence であり memory です。workflow authority ではない。

この境界を守ることが、グラフを scaffold の中で機能させ続けるための核心でした。

## 現在：可能性の探索

記事を締めるにあたって、現在の状況を補足しておきます。

task や handoff は、Arca の中で workflow authority として確立しています。一方、task は candidate や rejected のような分岐が少ない作業が多く、そこに exploratory graph を使う局面があるかどうかは、まだ定まっていません。

action log の distillation をグラフで扱えるかどうかも検討しています。これはまだ bootstrap path に乗っておらず、実験の段階です。

graph が workflow に関わりうるかどうか。task との境界がどこに引かれるか。scaffold に強く書いた原則の先で、何が可能かを、今もまだ試しているところです。
