---
id: "2026-06-18-aiスキル設計の6つの罠-matt-pocock-skills-v100-が体系化した予測可能なai-01"
title: "AIスキル設計の6つの罠 — Matt Pocock Skills v1.0.0 が体系化した「予測可能なAIマニュアル」の書き方"
url: "https://zenn.dev/417/articles/masakazu-matt-pocock-skills-design-20260618"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "GPT", "TypeScript", "zenn"]
date_published: "2026-06-18"
date_collected: "2026-06-19"
summary_by: "auto-rss"
query: ""
---

## tldr

Matt Pocock氏（Total TypeScript著者）がClaude Code用のスキルセットを**v1.0.0として正式リリース**した。GitHub 133kスター。注目すべきはスキルの中身より、**スキルの書き方を体系化したメタスキル**「writing-great-skills」の存在。AIに渡す指示書（スキル）の設計には6つの失敗パターンがあり、すべて「予測可能性（Predictability）」という1つの原則に集約される。本記事ではリポジトリを実際にcloneして読み解いた結果をまとめる。

<https://github.com/mattpocock/skills>

## 「スキル」とは何か

スキルとは、**AIに渡す永続的な仕事のマニュアル**のこと。プロンプトが「今日これやって」という1回きりの指示だとすれば、スキルは「この現場で働く限り、ずっとこのルールで動いてくれ」という手順書にあたる。Claude Codeではスラッシュコマンド（`/skill-name`）で呼び出せる。

Matt Pocock氏のリポジトリには約30個のスキルが含まれており、6つのカテゴリに整理されている。

* `engineering/` — コードワーク（TDD、バグ診断、PRD生成など）
* `productivity/` — 非コードワークフロー（壁打ち、ハンドオフなど）
* `misc/` — たまに使うもの
* `personal/` — 個人環境向け（非公開扱い）
* `in-progress/` — 開発中
* `deprecated/` — 廃止済み

しかし本記事の主題は個々のスキルではなく、それらを支える**設計論**だ。

## 6つの核心概念

### 1. User-invoked と Model-invoked — 2種類のスキル

Matt Pocock氏はすべてのスキルを「誰が呼べるか」という1軸で分類する。

**Model-invoked**は、AIが自律的に発火できるスキル。`description`フィールド（説明文）を持ち、AIはこの説明文を常にコンテキストウィンドウに載せている。AIが作業中に「あ、今このスキルが必要だな」と判断して自動的に呼び出せる。

例えるなら、キッチンの調理台に常に開いて置いてあるレシピカードだ。いつでも参照できるが、台のスペースを占拠する。

**User-invoked**は、人間が明示的に呼ぶスキル。`disable-model-invocation: true`を設定してdescriptionをAIから隠す。AIは存在すら知らないので、人間がスラッシュコマンドで指定した時だけ発火する。

棚にしまったレシピ本のようなもの。調理台を圧迫しないが、人間が「あの本あったな」と覚えていないと使えない。

この設計の背景には**2つのコスト**がある。

* **Context Load** — Model-invokedスキルのdescriptionがコンテキストウィンドウを常時消費するコスト。スキルが増えるほどAIの「調理台」が狭くなり、注意力が薄まる
* **Cognitive Load** — User-invokedスキルの存在を人間が記憶するコスト。スキルが増えるほど人間の「どのスキルをいつ使うか」の判断負荷が上がる

どちらかのコストは必ず発生する。無料のスキルは存在しない。

**判断基準**: 「AIが自分の判断で使う必要があるか？」がYesならModel-invoked、NoならUser-invoked。壁打ちのようにアイデア段階で人間が意図的に始めるものはUser-invoked。バグ診断のようにコーディング中にAIが自律的に判断すべきものはModel-invoked。

User-invokedスキルが増えすぎてCognitive Loadが問題になった場合、Matt Pocock氏は\*\*Router Skill（ルータースキル）\*\*で解決している。`ask-matt`という1つのUser-invokedスキルが、他のすべてのUser-invokedスキルを案内する受付窓口になる。覚えるスキルが1つで済む。

### 2. Leading Word — 1語で挙動を規定する

Leading Wordとは、**AIの事前学習にすでに存在する1語を「合言葉」として使い、スキル内の複数の指示を圧縮する**技法。

例えば、Matt Pocock氏のgrilling（壁打ちインタビュー）スキルには"relentlessly"と書いてある。たった1語だが、この単語があるだけでAIのインタビューの深さが変わる。AIは事前学習で「relentless」が使われた膨大な文脈を知っていて、そのすべてが「手を抜くな、最後まで追え」というニュアンスを持つからだ。

Leading Wordには2つの効果がある。

**実行時の効果**: スキル本文でLeading Wordを繰り返すことで、AIの挙動の方向性が安定する。「1語の周りに分散した定義が蓄積する」とMatt Pocock氏は表現している。

**発火時の効果**: スキルのdescriptionにLeading Wordを入れておくと、ユーザーが普段の会話やコードで同じ言葉を使った時に、AIがそのスキルを自動的に結びつけて発火しやすくなる。共通言語が接着剤になる。

重要なのは、**既存の言葉を使う**こと。造語も使えるが、AIの事前学習にない言葉は定義文のトークンコストがかかる。事前学習済みの言葉なら、そのコストがゼロになる。

### 3. No-op Test — 言わなくてもやることは書くな

No-op（No Operation）とは、**書いても書かなくてもAIの挙動が変わらない指示**のこと。

典型例は「丁寧に対応してください」「ユーザーの意図を理解してください」のような指示。ClaudeもGPTも、何も言わなくてもそうする。デフォルトの挙動と同じことを書いているだけなので、トークンを消費して何も生み出していない。

Matt Pocock氏の判断基準はシンプルだ。

> その行を削除してスキルを動かした時、出力が変わるか？ 変わらないなら、その行はNo-opだ。

注意点が2つある。

**人間の直感で判断しない**: 「丁寧にやれ」が効くかどうかは、人間の感覚ではわからない。実際にスキルから削除して、出力を比較する実験だけが真実。

**モデル依存**: ClaudeではNo-opでもGPTでは効く指示があり得る。同じClaudeでもバージョンが変わればNo-opでなくなることもある。モデル更新のたびに再検証が必要。

No-opを見つけたら、ただ削除するのではなく**Leading Wordに置き換える**のが上級テクニック。「be thorough」（No-op）を「relentless」（強いLeading Word）に変える。弱い合言葉を強い合言葉に交換するイメージだ。

### 4. Premature Completion — 次の工程が見えると手を抜く

Premature Completion（早すぎる完了）は、**AIが次のステップを意識するあまり、今のステップを十分にやらずに切り上げる現象**。

スキル内にStep 1〜Step 5が全部書いてあると、Step 1の調査中にStep 5のレポート作成を意識して、調査が浅くなる。

Matt Pocock氏は2段階の防御を定義している。**使う順番が重要**。

**第1の防御: Completion Criterion（完了基準）を明確にする**

「調査する」ではなく「全てのAPIエンドポイントのレスポンス形式を確認し、undocumentedなフィールドが存在しないことを検証する」のように、AIが機械的に「完了/未完了」を判定できるレベルまで具体化する。曖昧なゴールは「まあこのくらいで」を許す。この修正は安くて局所的。

**第2の防御: 後の工程を隠す（スキル分割）**

Step 1のスキルにはStep 1のことだけ書き、Step 2以降は別のスキルに分離する。AIの視界から後の工程を消す。ただしスキルが増えるとContext LoadかCognitive Loadが増えるため、第1の防御で解決しない場合にのみ使う。

Matt Pocock氏のgrill-with-docsスキルはこの原則の実践例で、中身はたった2行だ。

```
Run a `/grilling` session, using the `/domain-modeling` skill.
```

2行のUser-invokedスキルが、2つのModel-invokedスキルを組み合わせるだけ。後の工程は完全に見えない。

### 5. Deep Module — 小さい窓口、大きい裏方

Deep Module（深いモジュール）は、John Ousterhout氏の "A Philosophy of Software Design" に由来する概念で、Matt Pocock氏はこれをスキル設計全体に適用している。

**Deep Module**: 小さいインターフェース（窓口）の裏に、大量の処理（裏方）が隠れている。コンビニで「おにぎりください」と言えば出てくる。裏では仕入れ・製造・配送・検品・陳列・在庫管理が回っている。

**Shallow Module**: インターフェースと実装が同じくらい複雑。各窓口がスタンプを押すだけの多段たらい回しになっているような構造。

Matt Pocock氏はスキルの構造自体をDeep Moduleにしている。

* `codebase-design`（Model-invoked）— Deep Module語彙体系の共通定義
* `domain-modeling`（Model-invoked）— ドメインモデルの構築・更新
* `grilling`（Model-invoked）— インタビューループの共通エンジン

これらのModel-invokedスキルが「共有部品」として、複数のUser-invokedスキルから呼び出される。`grill-with-docs`は`grilling` + `domain-modeling`、`improve-codebase-architecture`は`grilling` + `domain-modeling` + `codebase-design`を組み合わせる。窓口は2行、裏方は数百行。

**削除テスト**: モジュールを消したらどうなるか想像する。消しても複雑さが消えず隣に引っ越すだけなら、そのモジュールはShallow。消した時に複雑さが本当に消えるなら、Deep Moduleとして価値がある。

### 6. Information Hierarchy — どこまで見せて、どこから隠すか

Information Hierarchy（情報階層）は、スキル内の情報を「AIがいつ必要とするか」で3段階に分ける設計手法。

1. **In-skill step** — SKILL.md内の手順。最優先で常に見える
2. **In-skill reference** — SKILL.md内の参考情報。手順の次に見える
3. **External reference** — 別ファイルに分離した詳細。必要な時だけ読み込む

図書館の設計と同じだ。案内板には棚の場所だけ、棚には著者名の索引、本を開いて初めて本文が出てくる。全情報を案内板に書いたら案内板が機能しなくなる。

情報を下の階層に移す操作をMatt Pocock氏は\*\*Progressive Disclosure（段階的開示）\*\*と呼んでいる。SKILL.mdには手順だけ残し、詳細なルールや例外パターンは別ファイル（例: `GLOSSARY.md`）に押し出す。

ここで重要なのが\*\*Context Pointer（コンテキストポインター）\*\*の書き方だ。

```
<!-- NG: ポインターの宛先だけ -->
詳細はGLOSSARY.mdを参照。

<!-- OK: いつ読むかの条件を明示 -->
**太字の用語**はすべてGLOSSARY.mdに定義がある。意味が曖昧な時は必ず参照しろ。
```

**ポインターの宛先ではなく、ポインターの文言がAIの行動を決める**。宛先がどんなに良い文書でも、文言が雑だとAIは読みに行かない。

## すべては「予測可能性」に帰結する

Matt Pocock氏はスキル設計の最上位原則を\*\*Predictability（予測可能性）\*\*と定義している。

> 予測可能性とは「毎回同じ出力を出す」ことではなく、「毎回同じプロセスで動く」こと。ブレインストーミングなら出力は毎回違って当然。でも「10個出す → 3つに絞る → 深掘りする」というプロセスは毎回同じであってほしい。

6つの概念はすべてこの予測可能性を高めるために存在する。

* **User-invoked / Model-invoked** → スキルが「いつ発火するか」を予測可能に
* **Leading Word** → AIの「挙動の方向性」を予測可能に
* **No-op Test** → 「効いてない指示」を排除し、残った指示の効果を予測可能に
* **Premature Completion対策** → 「各ステップの深さ」を予測可能に
* **Deep Module** → 「何を呼べば何が起きるか」を予測可能に
* **Information Hierarchy** → 「何をいつ読むか」を予測可能に

## 6つの失敗パターン

Matt Pocock氏がGLOSSARY.mdで定義している失敗パターンをまとめる。

**Premature Completion（早すぎる完了）** — 次の工程が見えてしまい、今の工程を端折る。AIの出力が浅い時に疑う。完了基準の明確化 → スキル分割の順で対処。

**Duplication（重複）** — 同じ意味を2箇所に書いている。1箇所を変更してもう1箇所を忘れるとAIが混乱する。Single Source of Truth（1つの意味は1箇所だけ）で対処。

**Sediment（堆積）** — 古い指示が削除されず蓄積する。追加は気楽だが削除は勇気がいるため、古い地層と新しい地層が混在して有効な指示がわからなくなる。定期的なプルーニング（剪定）で対処。

**Sprawl（膨張）** — 全行が生きているのに単純に長すぎる。AIの注意力が全体に薄く広がり、どの指示も中途半端に効く。Progressive Disclosure（詳細を別ファイルに押し出す）で対処。

**No-op（空振り）** — 書いてもAIの挙動が変わらない指示。トークンを消費して何も生まない。削除またはより強いLeading Wordへの置換で対処。

**全部Model-invoked問題**（筆者追記） — 「AIが自動で使ってくれたほうが便利」と思って全スキルにdescriptionを付けると、Context Loadが膨張して全体精度が落ちる。「AIが自律的に判断する必要があるか？」を毎回問う。

## リポジトリの導入方法

```
npx skills@latest add mattpocock/skills
```

対話形式でスキルを選択し、どのコーディングエージェントにインストールするか指定する。初回は`/setup-matt-pocock-skills`を実行して、Issue tracker（GitHub Issues / Linear / ローカルファイル）、triageラベル、ドキュメント配置を設定する。

## おわりに

Matt Pocock氏のスキル設計論の根底にあるのは**引き算の美学**だ。

* この1行を消してもAIの挙動が変わらないなら消す（No-op Test）
* この情報を今見せる必要がないなら隠す（Progressive Disclosure）
* このスキルをAIに常時見せる必要がないなら見せない（User-invoked）

足し算より引き算のほうが難しいし勇気がいる。しかし、AIに仕事を任せるなら、マニュアルの書き方こそが成果を決める。Claude Codeに限った話ではなく、システムプロンプトの設計、GPTsの構築、社内AIのルール策定、すべてに適用できる原則だ。

## 参考資料
