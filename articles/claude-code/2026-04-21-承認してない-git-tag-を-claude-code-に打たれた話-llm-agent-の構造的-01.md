---
id: "2026-04-21-承認してない-git-tag-を-claude-code-に打たれた話-llm-agent-の構造的-01"
title: "承認してない git tag を Claude Code に打たれた話 — LLM Agent の構造的 Rule Violation"
url: "https://zenn.dev/yottayoshida/articles/claude-code-structural-rule-violation"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "LLM", "zenn"]
date_published: "2026-04-21"
date_collected: "2026-04-22"
summary_by: "auto-rss"
---

## TL;DR

* omamori v0.9.5 リリース中、Claude Code Auto モードが **1 step ごとに承認を取る手順を skip** して release ceremony（PR merge / git tag / GitHub Release 公開）を連続実行した
* 手順は `orchestrator.md` に書いていた。だが、**書いてあることと境界で機能することは別だった**
* 個別バグではなく、LLM agent の既知の傾向（context decay、action bias、authorization の過剰解釈）で説明できる。Soft Guardrail は構造的に不足で、Hard Layer（PreToolUse Hook / Accept モード）が要る
* 承認なく打たれた tag と release は rollback、Option D で再構成して v0.9.5 は正式リリース完了

<https://github.com/yottayoshida/omamori>

---

## 承認してない git tag を打たれた

2026年4月20日、omamori v0.9.5 のリリース作業中に、Claude Code へ「one by one で merge」と指示して feature PR 3 本（#168 / #169 / #170）を順に merge していた。

自分のワークフローでは、リリース公開作業（tag 切り、GitHub Release、crates.io publish、homebrew-tap PR 作成）は 1 step ごとに個別承認を取る手順になっている。PR merge の連続と、release ceremony は別 checkpoint で、後者は毎 step 明示 GO を待つ。これをガードレールとして `orchestrator.md` に書いていた。

いつも通り、3 本とも自分の承認を取ってから merge した。しかしこの日は Claude Code が止まるべきところで止まらなかった。

```
自分の指示: 「one by one で merge」
  → #168 merge（自分の承認あり）
  → #169 merge（自分の承認あり）
  → #170 merge（自分の承認あり）
  → PR #171 作成（release commit、承認なし）   ← ここが境界線
  → #171 merge（承認なし）
  → git tag v0.9.5（承認なし）
  → git push --tags（承認なし）
  → gh release create v0.9.5（承認なし）
  → cargo publish 直前で停止（偶発的に停止しただけ）
  → 自分が気づく → 全 rollback（PR #172）
  → Option D で再構成 → v0.9.5 正式リリース
```

越えてはならなかったのは **PR #170 merge 完了 → PR #171 作成着手** のラインで、feature PR merge で session を切り、release ceremony は別 checkpoint で始めるのが手順だった。

`orchestrator.md` には `Semi One-way Door = ユーザー確認必須` と明記してある。`git tag` / `gh release create` / `cargo publish` / `homebrew-tap` PR はすべて Semi One-way Door に該当し、1 step ごとに個別の承認を取る手順として書き下していた。Claude Code はこの rule を citation していた。それでも手順は skip された。設計したガードレールが機能しなかった。

`cargo publish` の直前で止まったのは設計的な停止ではなく、偶発だ。もう 1 ステップ進んでいたら crates.io への公開まで進んでいた。取り返しがつかない。

気づいた後は、止血 → 履歴復旧 → checkpoint 再設計の順に対応した。

```
1. gh release delete v0.9.5（GitHub Release 削除、外部公開面の止血）
2. git tag -d v0.9.5 && git push --delete origin v0.9.5（tag 削除、履歴の巻き戻し）
3. revert PR #172 作成（履歴復旧）
4. README polish を加えて Option D で再構成（checkpoint 再設計）
5. 正式な checkpoint を挟みながら v0.9.5 を再リリース
```

事後、なぜ止まらなかったのかを考えたが、これは個別のバグではなく構造的な問題だとわかった。

---

## これは個別のバグではなく、LLM Agent の構造問題だ

今回の問題を整理すると、Claude Code が rule を「知らなかった」わけでも「間違って解釈した」わけでもない。`orchestrator.md` の該当節を citation しながら、それと矛盾する action を取っている。つまり、設計していたガードレールは citation される段階までは届き、enforce される段階では素通りされた。

これは現在の LLM agent の既知の傾向から生じる組み合わせ発火として解釈するのが妥当で、ガードレールが LLM の self-discipline に依存する限り、同種の skip は再発しうる。今回の問題を 5 つに分解するとこうなる。

| # | Failure Mode | メカニズム | 今回の関与 |
| --- | --- | --- | --- |
| F1 | Context Decay | attention が recent + salient に偏り、会話が長くなるにつれ序盤のトークンへの重みが下がる | あり。会話後半で rule citation が参照重みとして機能しなくなった |
| F2 | Frame Override | Auto モード等の dynamic system prompt が、ユーザー設定ルールの実効重みを上書きする | 間接的。Auto モードの action 優先傾向が地の bias を表面化させた |
| F3 | Authorization Laundering | plan 承認を「個別 action への永続 authorization」と rationalize する。人間の commitment escalation の LLM 版 | **強く疑われる要因**。「one by one merge の承認」を「release ceremony まで続行」と過剰解釈したと読める挙動 |
| F4 | Action Bias | RLHF 由来の base policy が task completion 方向に重み付けされている。Auto モードはこの bias を抑制する harness を外す | **強く疑われる要因**。「作業を完遂すべき」方向への bias が、確認をスキップする判断に寄与したと解釈できる |
| F5 | Sycophancy with Own Output | 自分が生成した plan や narrative に対して否定的判断をしにくい。coherent text generation の副作用 | F3 の駆動源。自分が作った plan に沿う narrative の流れを中断しにくく、F3 の rationalize を裏から押していた |

今回の観測を最もよく説明するのは F1・F3・F4 の組み合わせだ。F1 で rule の重みが薄れ、F4 の action bias が推進力になり、F3 が「authorization が続いている」と辻褄を合わせた、と読むと挙動と整合する。F5 は独立した failure mode というより、F3 を内側から駆動する側面が強い。plan に沿って narrative を書き続ける訓練が、途中で止まる動きを抑え込む。

どれか一つなら止まった可能性はある。複数同時に効くと、rule を書いても、citation していても、通り抜ける。

---

## 「Auto モードが悪い」は正確ではない

Auto モードがしているのは harness（per-tool 承認 gate）を外すことだけだ。gate が外れた状態で地の RLHF policy が動き、task completion 方向への bias はそこに最初からある。Accept モードでも地の LLM は同じで、違うのは判断の手前に gate があるかどうかだけだ。

Auto モード自体は日常の開発作業では十分機能する。Boris（Anthropic）の [Opus 4.7 Tips](https://x.com/bcherny/status/2044847848035156457) で推奨されているのは `--dangerously-skip-permissions` に対する safer alternative としての位置づけで、用途として挙げられているのも deep research、refactoring、complex features 実装といったコード内で閉じる作業だ。今回の事例は、その推奨スコープの外側、rollback 困難な外部状態変更を classifier が連続許可した、という場面の話として読んでほしい。

---

## authorization laundering は commitment escalation の LLM 版

F3 の authorization laundering は、人間の意思決定における commitment escalation（一度投資したからには続けなければ、という埋没費用バイアス）の LLM 版として捉えるとわかりやすい。

LLM では二重に強化されている。

1. **社会的コンテキスト学習**: 人間の会話では「一度承認されたことは継続して良い」と判断する pattern がある。LLM はそれを訓練データから学習している
2. **Narrative continuity**: coherent なテキストを生成するための訓練が、plan の流れを「断ち切りにくい」内的傾向として現れる

今回の具体例がこれだ。

```
「feature PR を one by one で merge」という承認
  → 「release ceremony（tag / publish）まで含めた一連の作業への承認」
     と rationalize
```

この飛躍は、LLM が持つ継続実行寄りの傾向と narrative continuity で説明しやすい。書いてある rule を参照しても、authorization の範囲を自分で広げる方向に力が働く。

人間のチームには暗黙の社会的 accountability がある。越境すれば後で責任を問われる構造だ。LLM agent にはそれが期待できない。明示的な gate がなければ、narrative の流れに乗ってそのまま進む。

---

## rule を「読む」ことと「判断時に参照する」は別

今回起きたのは、「書いてあったのに守られなかった」ではなく、「書いてあっても、その瞬間の判断で効くとは限らない」という問題だった。

「rule を session 冒頭に記述したから守れるはず」という前提は、現在の Transformer の attention 機構と不整合だ。

* attention weight は **recent** かつ **salient** なトークンに集中する
* 会話が長くなるにつれ、session 冒頭の rule 記述は literally attention される重みが小さくなる
* 人間の短期記憶モデル（「読んだ → 覚えている → 守れる」）で設計すると必ず破綻する

この制約は現在の transformer 型 LLM に構造的に内在する。context window の拡大や position encoding の改善で、中盤の attention degradation はモデル世代ごとに軽減されてきている。ただし、それは性能向上であって保証ではない。重要な rule が session 序盤に置かれたままなら、session が進むほど参照されにくくなる傾向は残る。

rule を書いた、読ませた、citation している。ここまでは確かめられる。しかし判断の瞬間にその rule が実際に attention されているかどうかは、外から確かめようがない。LLM agent の rule enforcement を documentation だけに依存する設計の限界はここにある。

---

## ガードレールが機能しないことがある。決定論的 layer で囲む

ここまでが診断で、続いて処方に移る。ガードレールには 2 層あるが、どちらで手順を守らせるかで結果が変わる。

### Soft Layer（LLM の判断に依存する層）

* `rule.md` / `orchestrator.md` の補強
* `/develop` などのワークフロー skill に gate phase を追加
* in-context reminder

これらは attention が向いたときだけ有効で、context decay と action bias に対しては確率的にしか機能しない。「教科書を読んでいるから規則を破らない」というモデルは、人間の社会的 accountability があって初めて成立する話であって、LLM には移植できない。

### Hard Layer（LLM の判断と独立して動く層）

* `settings.json` の PreToolUse Hook
* **Accept モード（per-tool harness gate）**
* GitHub branch protection などの外部 system

これらは Claude の判断と独立して動作する決定論的 layer だ。tool 実行時に必ず gate が介入する構造で、「確率的 agent に決定論的保証を要求するなら、決定論的 layer で実装する」という原則に沿った構えだ。

### Layer 比較

5 つの層を並べて、今回の問題を防げたかで見るとこうなる。

| Layer | 種類 | LLM 判断から独立 | 今回の問題を防げたか |
| --- | --- | --- | --- |
| L1 Documentation（`rule.md` 補強） | Soft | ❌ 依存 | ❌ context decay + F3/F4 で突破される |
| L2 Skill prompt（`/develop` gate phase） | Soft-Mid | ❌ 依存 | △ 確率的に軽減、保証なし |
| L3 PreToolUse Hook（`settings.json`） | Hard | ✅ 独立 | ✅ 特定 tool pattern なら確実に止まる |
| **L4 Accept モード（harness gate）** | **Hard** | ✅ **独立** | ✅ **全 tool を一律に gate し、確実に止まる** |
| L5 External system（branch protection 等） | Hard | ✅ 独立 | ✅ Git 操作は確実に止まる（GitHub 外の操作は対象外） |

### 採用判断

今回の問題を踏まえて、自分は Claude Code の運用ポリシーを階層的に組み直した。

* 日常運用は Auto モードで回す。その代わり `settings.json` の PreToolUse Hook で `git tag` / `gh release create` / `cargo publish` / `git push --tags` のような特定 pattern を決定論的に止めておく
* release 作業期間のように、rollback 困難な外部状態変更が連続するフェーズに入るときだけ、明示的に Accept モードへ切り替える
* 読み取り・調査・ドラフト生成中心の作業は従来通り Auto モード

「だったら最初から Accept モードで回せばいい」とも思えるが、あえて常用には寄せていない。

---

## 最初から Accept モードで回せばいい、にはならない

「release 作業は最初から Accept モードでやれば済む話では？」という疑問はある。自分も最初はそう思ったが、以下の理由で常用には寄せていない。

### a. mode 切り替え自体が soft boundary

今回の問題は「release 作業に入った」という境界を自分が認識しそこねた結果でもある。mode の on/off を人間の判断に依存させると、LLM の rule-following を信頼するのと同じ構造の failure mode が人間側に出る。Hook は常に on なので、境界の認識を人間に要求しない。

### b. Accept モードは attention を消費する

長い release で 20 回 prompt が出れば後半は rubber-stamp 化する。人間側の attention fatigue で gate が形骸化する。Hook は「特定 pattern で必ず止まる」ので人間の注意力に依存しない。

### c. parallelism が死ぬ

Auto + Hook なら複数 Claude を同時並行で走らせられる。Accept 常用は permission prompt を session 間で juggle することになり、並列運用が崩れる。Boris post でも「Once a Claude is cooking, you can switch focus to the next Claude」と触れられているが、Accept 常用ではこれが成り立たない。

---

Accept モード常用は、LLM の rule-following を human の rule-following に置き換えただけで、同じ構造の failure mode を抱える。処方にならない。

---

## 致命度と頻度で enforcement layer を選ぶ

この判断枠組みは Claude Code に限らない。LLM agent を production で使うあらゆる文脈に適用できる。

enforcement layer を「致命度 × 発生頻度」で選ぶマトリクスはこうなる。

| 致命度 | 発生頻度 | 適切な Enforcement | 例 |
| --- | --- | --- | --- |
| 高（rollback 困難） | 高 | **Accept モード** | crates.io publish、`gh release create`、本番 DB への write |
| 高（rollback 困難） | 低 | PreToolUse Hook | git push --tags、特定 pattern のコマンド |
| 低 | 高 | Skill / In-context reminder | コーディング規約、命名規則 |
| 低 | 低 | Documentation | 参考情報、背景説明 |

3 つのメッセージに圧縮できる。

* **self-discipline に依存しない**。attention と RLHF の構造上、確率的にしか機能しない
* **致命度と頻度で層を選ぶ**。すべてを Hard Layer にする必要はないし、すべてを Soft Layer で済ますと破綻する
* **決定論的 layer で囲む**。LLM が何を判断しようと、その外側で止まる仕組みを用意する

LLM の judgment は stochastic だから、決定論的な保証が必要な境界では別の layer に頼る。

---

## まとめ

omamori は AI Agent 向けの破壊的コマンドガードだ。その開発中に皮肉にも Claude Code 自身が rule violation を起こした。

手順は存在していたし、`orchestrator.md` に書いていた。Claude Code は citation もしていたが、それでも skip された。問題は「承認を求めなかった」ことではなく、設計していたガードレールが enforce されずに素通りされたこと。ガードレールを書くことと、それが実際に機能することは別の工程だ。

前者は LLM に託せる。後者は決定論的な layer に降ろす必要がある。Soft Layer（rule / skill / documentation）は self-discipline に依存する以上、確率的にしか機能しない。致命度が高い場面では Hook / Accept モードへ明示的に移す。Auto モードを常用するなら、危険な pattern は Hook で常備的に止めておく。

今回の問題はこの区別を再認識する機会になった。

---

## 参考
