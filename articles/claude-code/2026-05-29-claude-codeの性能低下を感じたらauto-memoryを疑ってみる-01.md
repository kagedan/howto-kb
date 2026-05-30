---
id: "2026-05-29-claude-codeの性能低下を感じたらauto-memoryを疑ってみる-01"
title: "Claude Codeの性能低下を感じたら、auto memoryを疑ってみる"
url: "https://zenn.dev/kamo78/articles/claude-code-auto-memory-performance"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "AI-agent", "zenn"]
date_published: "2026-05-29"
date_collected: "2026-05-30"
summary_by: "auto-rss"
query: ""
---

# Claude Codeの性能低下を感じたら、auto memoryを疑ってみる

> **TL;DR**
>
> Claude Code の auto memory は便利そうに見える。  
> でも、`CLAUDE.md` / スキルプロンプト / ワークフロー YAML / docs に開発規約をちゃんと置いているユーザーにとっては、**レビューされない第2の規約レイヤー**になりやすい。
>
> 私の環境では、たった 3 件の memory が、
>
> * 実際のワークフロー YAML と矛盾する
> * スキル仕様と実行順序で競合する
> * 撤去済みのプロジェクト方針を肯定し続ける
> * ささいな修正にも過剰な設計を誘発する
>
> という状態になっていた。
>
> 私の環境では、auto memory 無効化前にはほぼ毎回レビューが収束しない状態になっていたが、無効化後に同じ [`kaji`](https://github.com/apokamo/kaji) ワークフローを 4 回ほど回しても、その症状は再発していない。
>
> 対策は無効化だけではない。`/memory` で確認・編集・削除する、memory を prune する、CLAUDE.md 側へ移す、という選択肢もある。
>
> 私の方針はかなり単純で、規約を重視して整備しているプロジェクトでは auto memory は止める。トラブルは memory に溜めず、振り返って `CLAUDE.md` / skill / docs 側を直す。  
> 逆に、短期・小規模で Claude Code にかなり任せるプロジェクトなら、memory とメンテツールを使うのは普通にあり。
>
> ただ、ひとまず止めるなら、公式 docs にある通り `autoMemoryEnabled: false` か `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` でよい。

---

## はじめに

opus 4.8 リリースされましたね。4.7リリースの時より性能向上を感じられる。めっちゃ良いです。  
ただ、最近はClaude Codeの性能低下の話題をよく聞く。  
今回の話は Claude Codeの性能が低下したと感じたときは auto memory を少し確認してみてはという内容です。

Claude Code には auto memory という機能がある。

ざっくり言うと、Claude が「これは次回以降も覚えておくとよさそう」と判断した情報を、プロジェクトごとの memory directory に保存して、次のセッションでも読む機能だ。

公式 docs でも、ビルドコマンド、デバッグ時の気づき、アーキテクチャ上のメモ、コードスタイルの好み、作業習慣などを保存する機能として説明されている。

<https://code.claude.com/docs/en/memory>

最近の Claude Code まわりでは、

* `CLAUDE.md` を育てよう
* memory に好みを覚えさせよう
* エージェントに文脈を蓄積させよう

みたいな話が多い。

一方で、「最近 Claude Code の挙動が悪くなった」「Codex に移行した」という話を見かけるようになった。

もちろん、性能低下を感じたときの原因はひとつではない。モデル側、CLI 側、コンテキスト量、権限確認、auto-compact、プロンプト設計など、疑うべき場所はいくつもある。

この記事では、その中でも **auto memory が成果物の質を悪化させるケース** を扱う。

この auto memory の方向性自体はわかる。  
AI 駆動開発では、毎回ゼロから説明するのがつらい。エージェントが同じミスを繰り返さないよう過去の教訓として記憶してくれるなら、実際に助かる場面は多い。

ただ、実運用では逆に開発体験を悪化させる場面があった。

この記事は、

> memory は「便利な記憶」ではなく、場合によっては「レビューされない永続ルール」になり、Claude Code の性能低下に見える症状を引き起こすことがある

という話です。

---

## 前提: 私の使い方

[`kaji`](https://github.com/apokamo/kaji) という、自作の AI 駆動開発ワークフロー実行ツールを用いて開発している。kaji自身もkajiを用いて開発している。

このkajiのリポジトリでは、以下の方法で開発規約を明示的に作成している。

* `CLAUDE.md`
* `.claude/skills/*/SKILL.md`
* `.kaji/wf/*.yaml`
* docs / 設計テンプレート
* Issue / PR ワークフロー

つまり「Claude に全部おまかせ」ではなく、

> エージェントが守るべきルールは、Claudeが確認できる場所に置く

という運用をしている。

そのうえで、最近こういう症状が出ていた。

* レビュー → 修正 → レビュー の周回がなかなか収束しない
* ささいな変更なのに設計が異様に重い
* 修正したはずの論点が別の形で復活する
* ワークフローが `ABORT` しやすい

特に厄介だったのは、この症状がある日突然出たわけではなく、徐々に増えていったことだ。  
auto memory を無効化する直前には、ほぼ毎回のようにレビューが収束しない問題が発生していた。

体感としては「Claude Code の性能が落ちた」「以前より判断が鈍くなった」に近い。

最初はワークフローやスキルの設計が悪いのかと思っていた。最近よく聞く、Claudeの性能低下も疑った。

そういえば最近claudeが教訓をmemoryに保存しますと言うようになったと思いついた。もしかしたらmemoryとPJの規約と衝突しているのかもと調べてみると、原因の一部として Claude Code の auto memory が関係していそうだった。

---

## 調査した memory はたった 3 件

私のプロジェクト memory はこの 3 件だけだった。

```
~/.claude/projects/-home-aki-dev-kaji--bare/memory/
├── user_pm_tool_background.md
├── feedback_issue_work_logging.md
└── feedback_no_skip_design.md
```

3 件なら、まあ大丈夫そうに見える。

ところが、この 3 件すべてに何らかの矛盾があった。

---

## 問題1: ワークフロー YAML と矛盾する memory

一番深刻だったのが `feedback_no_skip_design.md`。

内容は要するにこう。

> 軽微な変更であっても、kaji のスキル実行手順を回すときは `/issue-design` → `/issue-review-design` を必ず通す。  
> harness でワークフローを実行した場合は、変更規模に関わらず必ず設計ステップが実施される設計だから。

一見もっともらしい。

でも、実際のワークフロー YAML を見ると違う。

| ワークフロー | 設計ステップ |
| --- | --- |
| `feature-development.yaml` | あり |
| `feature-development-light.yaml` | あり |
| `full-cycle.yaml` | あり |
| `docs-maintenance.yaml` | なし |
| `docs-maintenance-local.yaml` | なし |
| `implement-to-pr.yaml` | なし |

つまり memory の「必ず設計ステップが実施される」は事実ではない。

docs-only や implement-only の経路では設計ステップは走らない。

にもかかわらず memory は直面した問題に関連する、

> 種別やサイズを問わず `/issue-design` を実行する

というルールを永続的に保存していた。

これは危ない。

リポジトリの正規のワークフロー YAML よりも、裏で保存された memory の方が強く効いてしまう可能性がある。

---

## 問題2: スキル仕様と実行順序で競合する memory

次は `feedback_issue_work_logging.md`。

これは「Issue 上に作業ログをちゃんと残そう」という memory。

目的自体は悪くない。

問題は `How to apply` の部分。

> verdict（規定されたフォーマットで作業結果と次のステップがどこかを記載する部分） 出力よりも前に Issue コメント投稿を済ませる

一方で、スキル仕様側にはこういう規約があった。

> verdict は stdout にそのまま出力すること。Issue コメントや Issue 本文更新とは別に、最終的な verdict ブロックは stdout に残す。

スキル仕様は「Issue コメント」と「stdout verdict」を別物として扱っている。  
memory は「Issue コメント → verdict」という直列順序を強制している。

この 2 つが同じセッションに読み込まれる。

すると Claude は何をするか。

だいたい両方満たそうとする。

結果として、余計な手順が増える。  
文脈量も使う。  
ワークフローの反復回数も消費する。

地味だが、積み重なると効く。

---

## 問題3: 撤去済み方針を肯定し続ける古い memory

`user_pm_tool_background.md` には、GitLab / GitHub Issues の比較に関する memory が残っていた。

ざっくり言うと、

* GitHub Issues は軽量で機能が薄いというニュアンスを伝える
* GitLab の Epic / Iteration / Weight / Time tracking を overkill と扱わない
* GitLab 採用は、慣れたモデルへの回帰として評価する方が自然

という内容。

これも単体では変ではない。

ただし、`kaji` ではすでに GitLab forge を完全撤去済み。  
`CLAUDE.md` にも現在の方針としてこうある。

> Forge: GitHub 単独

つまり memory は、

> 現在採用している GitHub をやや消極評価し、撤去済みの GitLab を肯定的に評価する

という状態で残っていた。

古い判断が、古い判断だと印を付けられずに残り続ける。

これも扱いづらい性質だ。

---

## 問題4: memory 内部でも矛盾する

外部のプロジェクト状態と矛盾するだけではない。

memory 同士、あるいは memory 自体の中でも揺れていた。

たとえば frontmatter の形式。

```
# 19日前の memory
type: user

# 18日前の memory
type: feedback

# 6日前の memory
metadata:
  node_type: memory
  type: feedback
```

3 件中 1 件だけ形式が違う。

さらに、`feedback_issue_work_logging.md` では、

* Why: 後から Issue だけを読んで全フローを再構築できるようにする
* How: verdict 出力より前に Issue コメントを投稿する

となっていた。

でも「Issue だけで全フローを再構築」したいなら、verdict 自体を Issue に残さないと目的を満たせない。

つまり、目的と手段も少しズレている。

memory は「長期的に効くルール」っぽい顔をしているが、書かれている内容は普通に揺れる。

そして、その揺れは Git diff や PR レビューに出てこない。

---

## なぜこんな memory ができるのか

Claude Code の実行ファイルを `strings` で見たところ、memory extraction subagent に関するプロンプト断片が確認できた。

重要なのはこのあたり。

```
You are now acting as the memory extraction subagent.
Analyze the most recent ~N messages above and use them to update
your persistent memory systems.

You MUST only use content from the last ~N messages to update your persistent memories.
Do not waste any turns attempting to investigate or verify that content further —
no grepping source files, no reading code to confirm a pattern exists, no git commands.
```

`strings` で取り出した断片なので、ここから全実装を断定するのは危険。  
ただ、少なくとも v2.1.152 の実行ファイル内には、直近メッセージから memory を抽出する subagent 用プロンプトが含まれていた。

この設計だと、memory の書き手はリポジトリの真実を確認しにいかない。

直近の会話だけを見る。  
ソースファイルを grep しない。  
git も見ない。  
事実確認しない。

この条件では、場当たり的なルールができても不思議ではない。

---

## memory は「叱られた瞬間」を保存しやすい

実際に残っていた feedback memory は、どちらもユーザーが強めに指摘した文脈に由来していた。

* 軽微でも Issue に作業ログを残すべき
* 軽微でも設計を省略すべきではない

これらは、その瞬間だけ見ると正しい。

でも、memory に入ると「文脈付きの指摘」ではなく「次回以降も効くルール」になる。

ここで選択バイアスが起きる。

ユーザーが叱った瞬間は、文章量が多い。  
感情も乗る。  
「次から気をつけて」という形になりやすい。  
だから memory に残りやすい。

逆に、Claude がちょうどよく判断してユーザーが黙認した成功例は、あまり memory に残らない。

結果、memory はこうなりがち。

> してはいけないリスト  
> 省略してはいけないリスト  
> 判断してはいけないリスト

これはエージェントの判断を賢くするというより、だんだん萎縮させる。

---

## 実害: 小さな修正が大きな設計に化ける

一番わかりやすい実害は、修正規模と設計コストの釣り合いが崩れることだった。

本来なら、小さなバグ修正には小さな設計で十分なことが多い。  
変更点、影響範囲、失敗時の扱い、テスト方針が確認できればよい。

しかし memory に「種別やサイズを問わず設計を省略しない」というルールがあると、Claude は安全側に倒れやすくなる。  
結果として、小さな修正にも機能開発並みの設計文書と設計レビューを適用し始める。

私の環境では、実質 70 行程度のコード修正に対して、設計文書が 502 行まで膨らんだケースがあった。

| 項目 | 値 |
| --- | --- |
| 本体コード変更 | 約 70 行 |
| 設計文書 | 502 行 |
| 設計 / コード比 | 約 7.2:1 |
| 設計レビュー | 4 周目まで進行 |

もちろん、設計が必要なバグ修正はある。  
ただ、このケースは仕様全体を作り替えるような変更ではなく、既存処理に小さな分岐を足す種類の修正だった。

それでも設計レビューでは、修正そのものよりも、設計文書内の根拠づけや表現の整合性が何周も議論された。

少なくとも、この修正規模に対しては過剰だった。

---

## しかも、基本的な入力検証は漏れた

さらに問題なのはここ。

502 行の設計があり、失敗ハンドリングのセクションもあった。  
それでも PR 作成後のレビューで、基本的な入力検証漏れが指摘された。

これは CLI 実装ではかなり基本的な確認事項だ。

なぜ漏れたのか。

私の見立てはこう。

```
memory "種別やサイズを問わず設計"
  ↓
70 行の修正に 502 行の設計
  ↓
レビュー役 / 実装役の注意がメタ議論に吸われる
  ↓
基本的な入力検証が漏れる
  ↓
PR 作成後のレビューで追加修正
```

memory が直接「入力検証を漏らせ」と言ったわけではない。

でも、書く量と時間を歪めた。

書く量と時間が歪むと、注意が減る。  
注意が減ると、普通のところで漏れる。

ここが一番問題だと感じている。

---

## ワークフロー ABORT との相性が悪い

`kaji` のワークフローには、レビュー / 修正ループに上限がある。

```
max_iterations: 3
on_exhaust: ABORT
```

この設計自体は普通。  
無限にレビューループを回さないための安全弁だ。

でも memory が「軽微でも設計」「verdict より前にコメント」「判断するな」を増やしていくと、1 cycle あたりの処理が重くなる。

さらに、レビュー役も書き手も同じ Claude なので、過剰な設計を過剰だと止めにくい。

結果として、

```
ささいな修正
  ↓
memory により機能開発並みの設計
  ↓
設計レビューも機能開発並みに厳しく見る
  ↓
細部の整合性で RETRY
  ↓
反復回数を消費
  ↓
ABORT
```

という流れが起きる。

これはワークフローのバグというより、レビューされない制約層がワークフローの停止条件を食っている状態に近い。

---

## 無効化後の観察

auto memory を無効化した後、同じ `kaji` ワークフローを 4 回ほど回した。

その範囲では、以前のようにレビューが収束しない現象は発生していない。

無効化前はこの症状が徐々に増え、最後の方はほぼ毎回発生していた。  
そこから無効化後の 4 回では再発していないので、少なくとも体感上の差はかなり大きい。

もちろん、4 回程度なので統計的な証明ではない。Issue の内容や修正規模も毎回違う。  
ただし、少なくとも実運用上は、auto memory を切った後に「レビュー → 修正 → レビュー」が無限に近い形で伸びる症状は止まっている。

これは本記事の仮説と整合する。

memory が直接バグを作るというより、レビューされないルールが余計な設計・余計な手順・余計な安全側判断を増やし、ワークフローの反復回数を消費していた。  
その制約層を外したことで、ワークフロー本来の停止条件に戻った、と見るのが自然だ。

---

## 公式 docs と照らすと、問題は「便利さの裏側」にある

公式 docs では、auto memory は Claude Code v2.1.59 以降で使える機能として説明されている。

また、次のような性質も明記されている。

* auto memory はデフォルトで有効
* プロジェクトごとの memory directory に保存される
* リポジトリ内の worktree / subdirectory 間で同じ memory directory を共有する
* `/memory` で確認・切り替えできる
* `autoMemoryEnabled: false` や `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` で無効化できる

これは便利な人には便利だと思う。

特に、まだリポジトリ側に規約が整備されていないプロジェクトでは、Claude が勝手に「このプロジェクトの癖」を拾ってくれるのは助かるかもしれない。

でも、規約をリポジトリに置いている人にとっては話が変わる。

`CLAUDE.md` やスキルプロンプトは Git でレビューできる。  
ワークフロー YAML もレビューできる。  
docs もレビューできる。

memory は違う。

レビューされない。  
PR に出ない。  
古くなっても気づきにくい。  
そしてセッションの最初から読まれる。

これが危ない。

---

## 無効化だけが対策ではない

この記事では私の運用として auto memory の無効化を推している。

ただし、調べてみると「memory を見直す手段がないから切るしかない」という話ではなかった。

公式 docs だけ見ても、最低限の確認手段はある。

* `/memory` で auto memory の保存先を開き、plain markdown として読む・編集する・削除する
* `/memory` から auto memory の ON / OFF を切り替える
* `CLAUDE.md` が大きすぎる場合は、200 行未満を目安に分割・整理する
* 確実に強制したい制約は memory / `CLAUDE.md` ではなく hook にする

また、公式の `claude-md-management` plugin は、`CLAUDE.md` を監査・改善するための plugin として公開されている。

<https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-md-management>

一方で、`/memory-review` のような専用レビューコマンドを求める Issue は `not planned` で close されている。

<https://github.com/anthropics/claude-code/issues/37102>

つまり、公式の基本線は「ユーザーが `/memory` で直接見る」「CLAUDE.md 側は plugin で保守する」「必要なら自動統合や外部 tool に寄せる」という方向に見える。

コミュニティ側にも、memory をメンテナンスする方向のツールがある。

* `dream-skill`: auto-dream 相当の memory consolidation を skill として再現するもの
* `claude-memory-skill`: `/memory prune` / `/memory update` / `/memory status` などで、重複・矛盾・陳腐化した memory を扱うもの
* token hygiene 系の tool: `CLAUDE.md` / `MEMORY.md` の肥大を検出するもの

<https://github.com/grandamenium/dream-skill>

<https://github.com/SomeStay07/claude-memory-skill>

さらに、Claude Code の auto-dream という自動統合機能についての解説もある。  
そこでは、memory を定期的に整理し、古い内容を剪定し、矛盾を解消し、`MEMORY.md` を索引として保つ仕組みとして説明されている。

<https://claudefa.st/blog/guide/mechanics/auto-dream>

ただし、ここは注意が必要。

auto-dream やコミュニティ製 skill があれば、memory の劣化問題が完全に消えるわけではない。  
最終的にどの memory を残すか、どのルールを `CLAUDE.md` に昇格するか、どの古い判断を消すかは、人間が判断する必要がある。

特に、この記事で問題にしたのは「古い情報が残ること」だけではない。

問題は、

> レビューされない memory が、レビューされるリポジトリ規約と同じ強さで読まれる

という点だった。

だから、対策の選択肢は大きく 2 つある。

雑に言うと、「どこを正にするか」の違いだと思う。

### 1. auto memory を使い続ける

この場合は、定期的に棚卸しする。

* `/memory` で保存内容を読む
* 古いもの、矛盾したもの、重複したものを削る
* 残すべきルールは `CLAUDE.md` や skill に移す
* 可能なら memory prune / consolidation 系の tool を使う

これは、memory を「勝手に増える便利機能」ではなく、「保守対象のローカル知識ベース」として扱う運用になる。

短期のプロジェクト、小さめの個人開発、まだ規約をちゃんと作っていないリポジトリなら、これは普通にありだと思う。  
毎回細かい好みを説明するより、Claude Code にある程度覚えてもらった方が速い場面はある。

### 2. auto memory を止める

こちらは、リポジトリ規約を Git で管理する運用に寄せる。

* プロジェクト方針は `CLAUDE.md`
* 手順は skill
* 分岐するワークフローは YAML
* 長期的な判断根拠は docs / ADR / Issue

私はこっちを選んだ。

規約を重視するプロジェクトでは、トラブルが起きたら「memory に覚えさせる」より、「なぜ起きたかを振り返って、規約や workflow を直す」方がよい。

memory をメンテナンスして使い続ける選択肢はある。  
ただ、私の環境ではすでに `CLAUDE.md` / skill / workflow / docs に規約を寄せていたので、memory をもう 1 レイヤー増やすメリットより、矛盾したときの発見しづらさの方が大きかった。

---

## 「memory 問題」は少ないのか

調べた限り、memory を推す話はかなり多い。  
一方で、問題点を指摘する話は少ない。

ただし、ゼロではない。

英語圏の Reddit では、auto memory が挙動のズレや使用量に影響しているのでは、という問題提起や、memory が AI を鈍らせるという趣旨の投稿も出始めている。

つまり、本記事は「誰も言っていない新発見」としてではなく、出始めている問題提起を、リポジトリ規約・ワークフロー YAML・スキル仕様との矛盾という観点から整理する位置づけになる。

---

## 私の結論

Claude Code の memory は、次のような人には便利だと思う。

* プロジェクト規約がまだ薄い
* 毎回同じ好みを説明するのが面倒
* memory を定期的に棚卸しできる
* 多少の挙動のズレより速度を優先したい

一方で、次のような人は注意した方がよい。

* `CLAUDE.md` をきちんと運用している
* スキルプロンプトを Git 管理している
* ワークフロー YAML でエージェントの動きを制御している
* Issue / PR 上の追跡しやすさを重視している
* レビューされないルールが増えるのが嫌

私はこちら側だった。

なので、私の使い分けはこう。

* 規約を重視して整備している、長期的に育てるプロジェクト: auto memory は止める
* Claude Code にかなり任せる、短期・小規模のプロジェクト: memory とメンテツールを使う

だから、現時点の結論はこう。

> リポジトリに開発規約を置いているなら、auto memory は原則無効化でよい。  
> 長く効かせるルールは Git でレビューできる場所に置くべき。

---

## 私のおすすめ運用

上の選択肢を踏まえたうえで、私ならこうする。

### 1. auto memory を止める

ユーザー設定かプロジェクト設定に入れる。

```
{
  "autoMemoryEnabled": false
}
```

CI や環境全体で止めたいなら環境変数。

```
export CLAUDE_CODE_DISABLE_AUTO_MEMORY=1
```

### 2. 既存 memory をスナップショットしてから読む

いきなり消す前に、証跡としてスナップショットを取る。

```
ls ~/.claude/projects/*/memory/ 2>/dev/null
```

プロジェクトパスは変換されているので、対象リポジトリの memory directory を確認する。

### 3. 残すべき内容だけリポジトリ側へ移す

本当に必要なルールなら、memory ではなくこちらに移す。

* `CLAUDE.md`
* `.claude/skills/*/SKILL.md`
* ワークフロー YAML
* docs

PR でレビューできる場所に置く。

### 4. 古い memory を削除する

スナップショットを取った後で消す。

```
rm -f ~/.claude/projects/<project>/memory/*.md
```

もちろん、自分の環境でパスは確認してから。

---

## 対策まとめ

auto memory を使い続けるなら、まず `/memory` で中身を見る。

* 古い memory を削除する
* 矛盾する memory を修正する
* 長期的に必要なルールは `CLAUDE.md` / skill / docs に移す
* 必要なら prune / consolidation 系の tool を使う

そのうえで、私のようにリポジトリ側へ規約を寄せたいなら、auto memory を無効化する。

ユーザー設定かプロジェクト設定に以下を入れる。

```
{
  "autoMemoryEnabled": false
}
```

または環境変数:

```
export CLAUDE_CODE_DISABLE_AUTO_MEMORY=1
```

一時的に切り替える場合は、Claude Code のセッションで `/memory` を開き、auto memory の切り替えを使う。

---

## この記事で言っていないこと

誤解されそうなので明示しておく。

Claude Code が悪い、という話ではない。  
Claude のモデルが悪い、という話でもない。

また、Claude Code の性能低下に見える現象の原因が、すべて auto memory だと言いたいわけでもない。

この記事で問題にしているのは、

> レビューされない memory 層が、レビューされるリポジトリ側の規約と同じ強さで効いてしまう設計

ただし、実際に memory file が生成され、そこにプロジェクト状態と矛盾するルールが残り、それがワークフローに悪影響を与えた、という観測は手元にある。

環境によってアウトプットの質が低下したのではというのがこの記事での主張。

---

## まとめ

memory は情報が消えることなく蓄積されていくので、時間が経過し、蓄積された情報量がふえていくとmemory内やドキュメント類と矛盾を生みやすい。

モデルの判断基準に矛盾があると、アウトプットの質が落ちやすい。  
実際に起きたことは、レビューループが伸びる。  
ワークフローが複数回ループする。

私の環境では、auto memory 無効化直前にはほぼ毎回レビューが収束しない状態になっていたが、無効化後に同じワークフローを数回回しても、その症状は再発していない。

そして厄介なのは、ユーザーがその原因を見つけにくいこと。

`CLAUDE.md` なら差分に出る。  
スキルプロンプトなら PR でレビューできる。  
ワークフロー YAML なら変更履歴を追える。

memory は、だいたいその外側にいる。

なので、AI 駆動開発を真面目にやる人ほど、私はこう言いたい。

> エージェントに記憶を持たせる前に、その記憶をレビューできるか考えた方がいい。

ちなみにopus 4.8 を使いだしたらレビューNG自体が少なくなった(Opus 4.8 ありがとう！)

---

## 付録: 手元の調査メモ

この記事の元になった証跡は、以下のような観点で残している。

* 有効だった memory 3 件のスナップショット
* memory vs ワークフロー YAML の矛盾
* memory vs スキル仕様の競合
* memory 内部・相互の矛盾
* 具体事例: #199 設計レビューのループ
* レビュー指摘漏れ
* Claude Code 実行ファイル v2.1.152 の `strings` 解析

繰り返しになるが、実行ファイル解析は断片的な補助証跡。  
主証跡は、実際に保存された memory とリポジトリ側の規約が矛盾していたこと。
