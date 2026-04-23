---
id: "2026-04-11-issuereleaseを自動化したら逆に人間が重要になった話-claude-code-plugin-01"
title: "Issue→Releaseを自動化したら、逆に人間が重要になった話 ― Claude Code Plugin gh-issue-driven を作って学んだ HITL Gate 設計"
url: "https://qiita.com/kiyotaman/items/302c8b7dc2cbcec555ff"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

## はじめに

> **AI の出力そのものではなく、AI の出力を見た人間の中に起きる反応こそが価値である。**

この記事は「**AIで開発しているけど、なんか質が上がらない**」と感じている方向けです。

## TL;DR

* AI は品質を上げます。でも、価値は生みません
* 価値は「**立ち止まった時**」にだけ生まれます
* **Gate** はそのための装置です ― 承認ではなく、気づきを引き出す構造
* **gh-issue-driven** はその Gate を **3フェーズの横矢印** に仕込んだ Claude Code Plugin です

---

## 1. はじめに ― Issue を AI にレビューさせたら、Issue が間違っていた

ある日、Claude Code に Issue の設計レビューを頼みました。返ってきたのは「この実装方針は妥当です、続行して良さそうです」という、よくある通過判定でした。

なのに、読み終わった瞬間に手が止まったのです。

> いや、この Issue の切り方、そもそもおかしい。1個のスコープに3つの関心事が混ざっている。これは切り直した方がいい。

AI はそれを指摘していません。指摘したのは、AI のレビューを **読んでいる最中の自分** でした。

この瞬間、AI 支援開発に対する考え方が180度変わりました。それまでは「AI に精度の高いレビューをさせて、通ったらそのままマージ」を理想だと思っていました。でもその日から、**AI の出力そのものよりも、その出力を読んだ人間の中で起きる反応の方がずっと価値がある** という確信に変わりました。

この確信から生まれたのが、Claude Code プラグイン [gh-issue-driven](https://github.com/JFK/gh-issue-driven) です。この記事では、その全体設計と、設計の底に流れる **HITL Gate(Human-in-the-Loop Gate)** の思想を解説します。

Claude Code、GitHub Copilot、各種 AI agent の登場で開発速度は劇的に向上しました。しかし、**Full Automation(完全自動化)のアウトプットの価値は限定的**です。自動化が生む成果物は「既知の問題の効率的な解」であり、新しい価値の創造には人間の突発的な思いつきや衝動が必要になります。そしてその「思いつき」は、冒頭のエピソードのように **AI のレビューを読んでいる最中にこそ想起** します。

---

## 2. 全体像 ― 1本の横矢印

gh-issue-driven がやっていることは、一枚の図で説明できます。

左端は **人間の衝動**(Issue起票)、右端は **Release**。その間を `start` → 実装 → `ship` → `tag` と流れていきます。矢印の上に浮いている橙色の丸が **HITL Gate** ― プラグインが人間を立ち止まらせるポイントです。

この図の上を、以下のセクションで **左から右に歩いて** いきます。

関連プラグイン:

---

## 3. Phase 1: `/gh-issue-driven:start` ― 設計の不安を Gate1 で解く

`/gh-issue-driven:start <issue-number>` が行うこと:

1. GitHub から Issue 本文を取得
2. **Kagura Memory** から過去の関連記憶を `recall`(session-start)
3. **Gate 1: 設計レビュー** を `/ask` → `/ceo` cascade で実行
4. Verdict を解析し、`green` なら feature branch を作成して実装待機状態へ

ここでの主役は Gate 1 です。内部動作に興味がある方は下の詳細フロー図を展開してください。そうでない方は §3.4 の実体験まで読み飛ばしても大丈夫です。

📊 Phase 1 の詳細フロー図(クリックで展開)

左から右へ、`/ask` のスコアリング → decline 判定 → `/ceo` エスカレーション → Verdict 解析 → 分岐、という順序で進みます。黄色の丸が HITL(yellow verdict 時の立ち止まり)、緑が成功出口、赤が中止出口です。

### 3.1 `/ask` の自動ルーティング

Gate1 の最初のレビュアーは `/claude-c-suite:ask` です。これは **単一レンズ自動ルーター** として設計されています。

内部動作:

1. 12 の CxO ロール(CTO, CSO, CIO, COO, CFO, CAIO, CDO, CMO, CLO, PM, QA Lead, DX Lead)それぞれに対して **3軸スコアリング** を実行します
   * **domain fit**(0–3): 質問がそのロールの専門領域にどれだけ合致するか
   * **evidence locatability**(0–2): コードベースから根拠を見つけられるか
   * **single-lens sufficiency**(0–2): 単一の視点で十分に答えられるか
2. 最高スコアのロールを選び、そのロール視点でレビューします
3. 特定の条件下で **decline** を発行します
   * 最高スコア < 4(どのロールにも十分な適合がない)
   * 上位2ロールのスコア差が1点以内 **かつ** 質問がトレードオフを要求している

**decline は失敗ではなく、設計された機能**です。「この質問は単一の視点では答えられない」と正直に認めることで、精度の低い回答を防ぎます。

### 3.2 `/ceo` cascade ― 3レンズ統合

`/ask` が decline を発行すると `/claude-c-suite:ceo` にエスカレーションされます。

1. 11ロールのクロスリファレンスグラフから、質問に最も関連する **3つの視点** を選定します
2. 各視点で分析を実行します
3. 3つの分析を統合し、**convergence / tension / conflict** を識別します
   * **convergence**(3視点が一致): 高確信度
   * **tension**(2対1): 中確信度、トレードオフを明示
   * **conflict**(対立): CEO 判断で決着

### 3.3 Verdict 解析コントラクト

全ての Gate レビュアーは共通の Verdict 構文を使います。

* **構造化行**: `## Verdict: <token>` を正規表現 `^\s*##\s*Verdict:\s*(green|yellow|red|decline)\b` でマッチします
* **last-wins 方式**: レスポンス内に複数の Verdict 行がある場合、**最後の行が優先** されます。レビュアーが途中で考えを変えても問題ありません
* **Gate1 トークン**: `green` / `yellow` / `red` / `decline`(decline は Gate1 のみ)

Verdict 別の挙動:

| Verdict | 動作 |
| --- | --- |
| `green` | 続行。ブランチ作成へ |
| `yellow` | **人間に判断を返す**。AskUserQuestion で「続行するか?」を確認 |
| `red` | 中止。`force` フラグで強制続行は可能 |
| `decline` | `/ceo` にエスカレーション |

#### yellow が最重要 ― ここで「気づきの装置」が起動する

green / red は判断が自明です。yellow だけが、**人間が立ち止まって考える必要がある** 状態を意味します。

* `green` → AIが「問題ない」と言っているだけ。人間の脳は働きません
* `red` → AIが「止めろ」と言っているだけ。人間の脳は同意するか force するかだけ
* `yellow` → 「判断できない、あなたが決めて」という AI からの委譲 ― **ここで人間の脳が初めて起動します**

冒頭で紹介した Issue の切り直しエピソードは、まさに Gate1 が yellow を返した時に起きました。もしそこが自動 green 通過だったら、Issue は歪なままマージされていたはずです。**Gate 設計で最も守るべきものは、この yellow 経路です**。

### 3.4 実体験 ― Gate1 で Issue の切り方を変えたくなった

Gate1 でレビューを読んでいるうちに、「このIssueの切り方がそもそもおかしいのでは」と気づくことが何度かありました。AI レビュアーの指摘そのものよりも、その指摘を **読んだ自分の中に起きた反応** ―「いや、このスコープではなくて、もっとこう分けるべきだ」― の方が価値がありました。

これは自動化では起きません。レビュー結果を自動でパスさせていたら、Issue の切り直しという選択肢は生まれなかったはずです。

---

## 4. 実装 ― Claude Code プラグインエコシステムを味方につける

Gate1 を通ったら実装に入ります。gh-issue-driven は実装そのものには介入しません ― ここは人間と Claude Code の対話の場です。

ただし「人間と Claude Code の対話」と言っても、今の Claude Code は素の LLM 一体ではなく、**プラグインとサブエージェントが豊富にぶら下がった統合環境** です。gh-issue-driven はそれを前提に設計されています。

### 4.1 `/feature-dev:feature-dev` を主軸に据える

実装フェーズで最もよく呼び出すのが `/feature-dev:feature-dev` です。これは Claude Code 公式の [feature-dev](https://github.com/anthropics/claude-code) プラグインが提供するスキルで、次のことを一手に引き受けてくれます。

* **既存コードベースの理解**: 該当機能の周辺を自動探索し、規約・パターン・依存関係をマッピング
* **アーキテクチャ提案**: 新規コードの置き場所・既存モジュールとの整合・命名規則を含む実装ブループリント
* **ビルド順序の提示**: どのファイルから手を付けるべきかを順序立てて返す

gh-issue-driven の start フェーズで Gate1 が抽象レベルの設計判断を返した後、`/feature-dev:feature-dev` がそれを **具体レベルの実装計画に翻訳する** 役割を担います。Gate1 が「この方向で作ろう」と決め、feature-dev が「この順でファイルを作ろう」と決める、というレイヤー分担です。

さらに feature-dev プラグインは `code-architect` / `code-explorer` / `code-reviewer` のサブエージェント群を内包しており、必要に応じてそれらが動きます。Claude Code の **Explore** エージェントなどの汎用サブエージェントも、大規模な調査が必要なときに走ります。実装中に「知らないコードベースの広範囲調査が必要だな」と感じたら、Claude Code 自身がサブエージェントを呼び出してくれるので、明示的に指示する必要はほとんどありません。

### 4.2 `/simplify` ― Gate 1.5

実装の仕上げに近づいたところで、もう一つのチェックポイントが自然と定着しました。

```
Gate1(設計レビュー)
    ↓
実装 (+ /feature-dev:feature-dev)
    ↓
/simplify(Gate 1.5 ← ここ)
    ↓
Gate2(Pre-PR レビュー)
```

`/simplify` は Claude Code 組み込みのスキルで、変更コードの **reuse(再利用可能性)・ quality(品質)・ efficiency(効率)** をレビューして、問題があれば自動修正してくれます。

Gate2 に進む前に `/simplify` でコードレベルの問題を潰しておくと、Gate2 ではアーキテクチャの議論に集中できます。ここで **レイヤーの分離** が発生します。

### 4.3 プラグイン同士を組み合わせる設計思想

gh-issue-driven が直接提供する機能は、実は思ったより少ないです。

* Gate1/Gate2 の **オーケストレーション**
* Verdict 解析コントラクト
* Copilot ループの制御
* Release ceremony の自動化

実際のレビューや実装作業は、すべて他のプラグイン(`claude-c-suite`, `feature-dev`, 組み込みの `/simplify`)が担っています。gh-issue-driven は **糊(glue)** として設計されており、個々のプラグインの仕事を奪わずに順序と繋ぎ方だけを提供します。この設計のおかげで、Claude Code エコシステムに新しいプラグインが追加されても、gh-issue-driven 側の変更はほぼ不要です。

---

## 5. Phase 2: `/gh-issue-driven:ship` ― 実装を Gate2 + Copilot で出し切る

`/gh-issue-driven:ship` が行うこと:

1. **Gate 2: Pre-PR レビュー** を CSO + QA Lead + CTO の並列実行
2. Verdict 集約 → 人間の承認を経て PR 作成
3. **Copilot review loop**(最大5回)
4. session-summary で Kagura Memory に学びを保存

このフェーズの特徴は、**HITL が 2 箇所ある** ことです(Gate2 yellow 時と、Copilot 依頼の入口)。内部動作に興味がある方は下を展開してください。

📊 Phase 2 の詳細フロー図(クリックで展開)

CSO / QA Lead / CTO が並列で走り、集約 Verdict → HITL① → PR 作成 → HITL② → Copilot ループ → exit\_reason で終了、という構造です。

### 5.1 Gate2 ― 並列アドバイザー

Gate2 では 3 人の AI アドバイザーを **Skill tool の単一バッチで並列実行** します。

```
Skill tool batch invocation:
  ├─ /claude-c-suite:cso     → CSO_OUT
  ├─ /claude-c-suite:qa-lead → QA_OUT
  └─ /claude-c-suite:cto     → CTO_OUT
```

各アドバイザーのレンズ:

* **CSO** (Chief Security Officer): OWASP Top 10 準拠の脆弱性評価、認証パターン、secrets 管理、依存関係リスク。原則は *defense in depth, least privilege, secrets are toxic, fail secure, assume breach*
* **QA Lead**: テストカバレッジマップ(unit / integration / E2E)、フレーキーテスト検出、CI/CD ゲート評価、戦略ギャップ。原則は *test the contract not the implementation, every bug is a missing test*
* **CTO**: テックデット評価(debt-to-feature 比率 > 30% で警告)、アーキテクチャリスク分析、ドキュメント鮮度。原則は *debt compounds, breaking changes need coordination, docs are part of product*

集約ルール:

```
any red    → GATE2_VERDICT = red
any yellow → GATE2_VERDICT = yellow
all green  → GATE2_VERDICT = green
```

Gate2 は `decline` をサポートしません ― decline は Gate1 のルーティング概念であり、Gate2 のアドバイザーは自分の専門領域で必ず判断を返します。

デフォルトでは binary gate は無効(advisor-only モード)ですが、`gate2.binary_gate` に`/claude-c-suite:audit` 等を設定すると、追加の hard gate として並列実行できます。binary gate の `fail` は `force` フラグでも上書きできない hard block として機能します。

### 5.2 Copilot レビューループ ― 品質担保の自動化

Gate2 を通った後、PR 作成 → GitHub Copilot にレビュー依頼という流れに入ります。ここは **気づきの装置ではなく、品質の守護者**。役割が Gate と明確に違います。

#### Copilot レビューの特徴 ― diff ベース・ライン単位

Copilot の PR レビューには、CxO 系アドバイザーとは異なる決定的な特徴があります。

* **diff ベース**: PR の変更行だけをスコープに見ます。未変更の周辺コードは基本的にレビュー対象外です
* **ライン単位**: 「この行のこの引数が間違っている」レベルの指摘を返します。抽象度が低く、具体的です
* **cross-document consistency**: 同じ PR 内の複数ファイル間の矛盾(関数名の表記ゆれ、コマンドのステップ番号ズレ、ドキュメントとコードの乖離)を検出します
* **文章とコードの整合性**: コメントや docstring の記述がコードと食い違っているパターンに強いです

**これは Gate2 アドバイザーの弱点を埋めます**。CSO/QA Lead/CTO はアーキテクチャや戦略レベルの問題を見ますが、「この行のこの変数」という粒度には降りてきません。逆に Copilot はライン単位の正しさを見ますが、「そもそもこの機能が必要か」という抽象度には上がりません。

だから **同じレイヤーのレビューを重ねても価値は増えない** のです。Gate2 と Copilot は **補完関係** にあります。

#### ループ設計

```
for i in 1..max_loops(5):
    14.a  Wait for Copilot activity(polling)
    14.b  Parse: REVIEW_DECISION, NEW_COMMENTS
    14.c  Exit conditions check
    14.d  Address actionable comments(Edit/Bash)
    14.e  Commit and push
    14.f  Reply and re-request review
    14.g  Update state file
```

**Exit conditions**(構造化された終了条件):

| exit\_reason | 条件 |
| --- | --- |
| `approved` | Copilot が APPROVED を返した |
| `no_actionable_feedback` | 新しいコメントなし、または全て generic |
| `max_loops` | 上限回数(デフォルト5)に到達 |
| `tests_failed` | ループ中のテストが失敗。壊れたコードはコミットしない |
| `silent_no_op` | Copilot レビュアーがそもそも検出されなかった |

**「青天井にしない」設計が重要** です。5回で解決しなければ人間に返します。AI に際限なくリトライさせるのは、品質向上ではなくリソースの浪費です。

Copilot 検出は 2 信号方式を採用しています。gh CLI のバージョンやリポジトリ設定によって Copilot の検出方法が異なるため、`reviewRequests`(明示的に追加)と `latestReviews`(Automatic Copilot code review で自動起動)の両方を並行で確認します。

### 5.3 HITL Gate ― Copilot 依頼の前で立ち止まる

Copilot ループに入る **直前** に、もう一つの立ち止まりが挟まっています。

> 「Copilot レビューを依頼しますか? (y/n)」

これは一見無駄な確認に見えますが、実は重要です。Copilot レビューは:

* **通知コスト**: レビュアーへの通知を発生させます(取り消し不可)
* **API コスト**: ループ中に Copilot の API リクエストを消費します
* **社会的コスト**: PR の履歴にレビュー依頼が残ります

つまり **取り消しがきかず、外部に影響が及ぶ** 行動です。こういう行動はデフォルトで自動化すべきではない ― これが HITL Gate の核心原則の一つです。Copilot ループの「内側の自動化」(5回の反復処理)は維持しつつ、その「入口」には人間のゲートを置きます。

### 5.4 実体験 ― アドバイザーが見逃した矛盾を Copilot が発見

初回の e2e ドッグフーディングで、Gate2 アドバイザー (CSO, QA Lead, CTO) はアーキテクチャレベルの問題を正しく検出しました。しかし、**コマンドファイル間のステップ参照の矛盾** は Copilot のラインレビューが発見しました。

CSO は「認証設計が正しいか」を見ます。QA Lead は「テスト戦略が十分か」を見ます。CTO は「アーキテクチャが健全か」を見ます。しかし「doctor.md の Step 10 が shipping.md で参照されているが実際は Step 11 になっている」というミスは、どの CxO の抽象度にも載らないのです。そこに降りられるのは diff ベース・ライン単位の Copilot だけでした。

CxO アドバイザーを増やしても、同じ抽象度のレンズが増えるだけです。**レイヤーの異なるレビュー**(アーキテクチャ vs. ライン単位)を組み合わせることが重要だという教訓を得ました。

---

## 6. Phase 3: `/gh-issue-driven:tag` ― Release まで一気通貫

PR を main にマージしたあとの **リリース儀式** を自動化するフェーズです。

`/gh-issue-driven:tag <version>` が行うこと:

1. **Pre-flight checks**: default branch か? 作業ツリーはクリーンか? remote と同期しているか?
2. **Milestone readiness**: 指定バージョンに対応する milestone を探し、open issues が残っていないか確認します(残っていれば `force` なしでは abort)
3. **Lint**: `check-frontmatter.py` とテストを実行します(ファイル変更の前に)
4. **Release notes 生成**: milestone の closed issues を **label でグルーピング** します:

   ```
   ## What's Changed

   ### Bug Fixes
   - <issue title> (#123) — @author

   ### Enhancements
   - <issue title> (#124) — @author

   **Full Changelog**: https://github.com/<owner>/<repo>/compare/v0.2.0...v0.3.0
   ```
5. **Manifest bump**: `.claude-plugin/plugin.json` と `marketplace.json` の version を更新します(jq で値を読み、Edit tool で書き換えます ― sed は使いません)
6. **CHANGELOG.md 更新**: 先頭に `## [v0.3.0](https://github.com/.../releases/tag/v0.3.0) — 2026-04-11` を追加します
7. **Commit**: `chore: release v0.3.0`
8. **Annotated tag**: `git tag -a v0.3.0 -m "v0.3.0"`(`-a` は必須 ― lightweight tag は `--follow-tags` に載りません)
9. **Push**: `git push --follow-tags origin main`(commit と tag を一緒に push して partial-failure window を閉じます)
10. **GitHub Release**: `gh release create v0.3.0 --notes-file /tmp/gh-issue-driven-release-notes.md`

このフェーズの設計原則は「**チェックは前に寄せる、変更は後ろに寄せる**」です。下の詳細フロー図では、pre-flight の 3 ノードが黄色で示されています ― ここで失敗すると作業ツリーに傷がつかずに abort します。dry-run が意味を持つのも、この配置のおかげです。

📊 Phase 3 の詳細フロー図(クリックで展開)

黄色の 3 ノードがファイル変更前のチェック群。7 ステップ目(Manifest bump)以降だけが destructive な操作です。

### 6.1 なぜ tag コマンドが必要だったか

手動でやっていた頃の release ceremony は、以下の失敗パターンを何度も生みました:

* **manifest 片側だけ bump** ― `plugin.json` は更新したが `marketplace.json` を忘れた
* **annotated tag 忘れ** ― `git tag v0.3.0` だけで `-a` を付けず、`--follow-tags` でも送られなかった
* **milestone open issues 残存** ― release ノートを書いたあとに open issue を見つけて、次のバージョンに押し出すべきか悩む
* **CHANGELOG 忘れ** ― Release は作ったが repo 側の履歴が空のまま

`/tag` はこれらを **pre-flight checks で防ぎ、アトミックな ceremony として完結させる** ための設計です。

### 6.2 dry-run ― 取り返しのつかない行動の前に

```
/gh-issue-driven:tag 0.3.0 dry-run
```

`dry-run` フラグを付けると、**ファイルも git も GitHub も一切触らず**、何が起きるはずだったかだけを表示します:

* 生成される release notes(完全版)
* manifest bump の before/after diff
* CHANGELOG に追加される行
* 実行されるはずの git コマンド列

release は push と tag を伴うため、Phase 1/2 と違って **取り返しが部分的にしか効きません**。dry-run は「もう一回立ち止まるためのオプション」として意図的に用意されています。

### 6.3 branch protection との衝突時のリカバリ設計

直接 push が branch protection で拒否されるリポジトリの場合、`/tag` は諦めず、**recover workflow** を案内します:

1. 現在のローカル HEAD(release commit)から short-lived branch を作ります
2. その branch を push して PR を開きます
3. PR をマージします
4. ローカルの default branch をマージ後の commit に追随させます
5. ローカル tag を merge commit に付け直します(non-fast-forward マージの場合のみ)
6. tag を push します
7. GitHub Release 作成(step 12)だけ実行します

重要なのは、**「最初から `/tag` をやり直さない」** ことを明示的に指示している点です。steps 7–10(manifest bump, CHANGELOG, commit, local tag)は既に完了しているので、そこからの再実行は二重コミットや version 衝突を生みます。ここも「取り返しのつかない行動に対する丁寧な扱い」の一例です。

---

## 7. Kagura Memory ― 学びの持ち越し

```
/gh-issue-driven:start
  └─ session-start(過去の学びを想起)
  └─ recall(Issue 内容 + 過去の関連記憶)

   ... 実装 ...

/gh-issue-driven:ship
  └─ session-summary(今回の学びを保存)
```

各 Issue の設計判断・バグ修正・パターンが記憶として蓄積され、次の Issue 開始時に recall で想起されます。

Kagura Memory Cloud は **60% セマンティック + 40% BM25** のハイブリッド検索に Neural Memory(ヘブ学習)の boosting を加えた検索を提供します。Issue 内容の文脈的な類似性と、キーワードの完全一致の両方を活用できます。

**記憶がなければ毎回ゼロからスタートになり、Gate の判断精度も下がります**。「**人間とAIとの対話記録から学ぶ**」プロセスを、AI との協働に組み込む設計です。

---

## 8. HITL Gate の哲学 ― なぜ3フェーズ全てに立ち止まりがあるのか

> **Gate は承認ではありません。気づきの装置です。**  
> **立ち止まることは、遅れることではありません。気づくことです。**

ここまでで 3 フェーズを駆け抜けました。最後に、この設計の **底に流れている思想** を明示しておきたいと思います。

### 8.1 Gate は承認ではなく気づきの装置

HITL Gate は単なる承認フローではありません。**「立ち止まる装置」** として設計しています。

AI が返すレビュー結果を人間が読むことで初めて浮かび上がる気づき ―「これじゃない」「もっとこうできる」― それがプロダクトの価値を生みます。この反応の源泉は人間の経験・文脈・欲求であり、自動化できません。

```
Input(AI 出力) → 人間の脳 → 「気づき」(Output)
                      ↑
              経験・文脈・欲求
```

**AI の出力そのものではなく、AI の出力を見た人間の中に起きる反応こそが価値の源泉**。これが gh-issue-driven の設計原則のゼロ番目にあります。

### 8.2 品質担保と価値創造を分離する

gh-issue-driven には 2 種類の「レビュー」が混ざっています。両者は役割が違います。

| レイヤー | 担当 | 目的 | 自動化の上限 |
| --- | --- | --- | --- |
| `/simplify` (Gate 1.5) | Claude Code 組み込み | コード品質(reuse / quality / efficiency) | 無制限(品質担保) |
| Gate2 advisors | CSO, QA Lead, CTO | アーキテクチャ・セキュリティ・テスト戦略 | 人間の承認が要る(気づき) |
| Copilot review loop | GitHub Copilot | diff ベース・ライン単位のロジックバグ、cross-document consistency | 5 回上限(品質担保) |

**これらは補完的であり、冗長ではありません**。ある PR では `/simplify` を2パス走らせてコードレベルの問題を先に潰し、Gate2 ではアーキテクチャの議論に集中できました。別の PR では `/simplify` 1 パスで済み、すぐに Gate2 に進めました。

### 8.3 Gate 設計の原則

| 原則 | 説明 |
| --- | --- |
| **Gate は承認ではなく気づきの装置** | AI の出力を見た人間の反応を引き出すことが目的 |
| **2段階 Gate 構成** | 「やるべきか」(Gate1) と「出せるか」(Gate2) で異なる気づきが生まれる |
| **yellow が最重要** | green / red は自明。yellow こそ人間の判断が問われる |
| **自動化には上限を設ける** | Copilot ループ 5 回上限、exit\_reason で終了条件を構造化 |
| **品質担保と創造的判断を分離する** | Copilot ループ(品質)と Gate(気づき)は異なるレイヤー |
| **decline は失敗ではなく誠実さ** | /ask が複数レンズ必要と判断したら正直に辞退し /ceo にエスカレーション |
| **レイヤーの異なるレビューを組み合わせる** | /simplify + Gate2 advisors + Copilot の 3 層が補完関係 |
| **取り返しのつかない行動は自動化しない** | Copilot 依頼・tag push・Release 作成はすべて明示的な人間の合図を要求 |
| **学びを持ち越す** | Kagura Memory でセッション間の知識を蓄積 |

### 8.4 なぜ Gate 設計が差別化要因になるのか

AI で開発速度が上がれば上がるほど、**「何を作るか」の判断の重みが相対的に大きくなっていきます**。実装スピードはどのチームでも似たような値に収束するからです。

すると、差がつくのは以下の2点です。

1. **Issue に落とす前の着想の質** ― これは Gate の外側、人間の日常観察の領域
2. **Issue から PR に向かう途中で起きる "気づき" の量** ― これがまさに HITL Gate の守備範囲

2 番はよく見落とされます。多くのチームは「AI に投げて返ってきた結果をそのまま受け取るか/拒否するか」の二択にしがちです。でも本当に価値があるのは、返ってきた結果を **読んでいる最中に自分の中で起きる反応** です。「あ、これ違う」「そういう切り方もあるか」「これは別 Issue だな」― この反応は自動化できません。それを **引き出すための構造** が Gate です。

```
            │ 品質担保        │ 価値創造
────────────┼────────────────┼──────────────────
自動化可能   │ Copilot ループ  │ ×(自動化できない)
            │ CI/CD          │
            │ /simplify      │
            │ /tag ceremony  │
────────────┼────────────────┼──────────────────
人間が必要   │ テスト戦略判断  │ Gate1: Issue 再解釈
            │                │ Gate2: 思いつきの発生
            │                │ HITL Gate: Copilot 依頼の合図
```

右上の象限 ―「価値創造 × 自動化可能」― は永遠に空欄です。新しい価値の創造は自動化できません。ただし、その創造を **構造的に引き出す装置** は設計できます。それが HITL Gate であり、この装置をワークフローに組み込めているかどうかが、AI 時代の開発プロセスの差になっていきます。

---

## 9. ドッグフーディング ― プラグインが自分のバグを捕まえた

gh-issue-driven の最初の e2e ドッグフーディングで、印象的な自己検証が起きました。

Verdict parser にバグがありました。旧実装は単純な substring match で、レビュー文中に「decline」という単語が含まれているだけで誤エスカレーションしていました。この修正 PR を gh-issue-driven 自身で処理したところ、Gate1 のレビュアーがレビュー文の中で「decline」という単語を自然に 4 回以上使用しました ― **まさに substring matcher なら誤動作するパターン**です。

修正後の構造化パーサー(`## Verdict:` 行の last-wins 方式)はこれを正しく処理し、レビュー本文中の自然言語としての「decline」を無視して、最後の構造化 Verdict 行だけを解析しました。

**プラグインが、自分自身を修正する PR の中で、まさにそのバグを踏んで自己検証した** のです。設計妥当性の最も強い実証であり、構造化 Verdict 行というコントラクト設計の正しさを証明しました。

これ以降、gh-issue-driven の全ての新機能は **自分自身で開発する** というルールにしています。HITL Gate も `/tag` コマンドも、全て gh-issue-driven を使って開発・リリースされました。記事で紹介している横矢印の流れは、その全てのリリースで実地に回ってきた設計です。

---

## 10. 導入方法と実際の利用イメージ

### 10.1 インストール

Claude Code 環境で以下を実行するとインストールできます。

```
/plugin marketplace add JFK/gh-issue-driven
/plugin install gh-issue-driven@JFK
```

初回実行前に環境チェック:

必要な依存(`gh` CLI、git 認証、関連プラグイン)を一括で確認してくれます。

### 10.2 Issue 1本を流してみる

最初の Issue を処理するときの典型的な流れです。

```
$ /gh-issue-driven:start 123

Fetching issue #123 … ✓
Recalling related memories from Kagura (3 hits) … ✓

─── Gate 1: Design Review ─────────────────────────
/claude-c-suite:ask  (scoring 12 roles)
  CTO          domain_fit=3  evidence=2  single_lens=2  total=7
  QA Lead      domain_fit=2  evidence=2  single_lens=1  total=5
  ...
  → routing to CTO
  
## Verdict: yellow
(CTO 所見本文 …)

⚠ yellow verdict — do you want to continue? [y/n/abort]
```

ここで一度立ち止まります。続行すると branch が切られ、実装フェーズに入ります。

```
$ /feature-dev:feature-dev "Issue #123 を実装して"
(code-explorer → code-architect → 実装 …)

$ /simplify
Reviewing changed files for reuse / quality / efficiency …
  commands/start.md:  no issues
  commands/ship.md:   1 suggestion (consolidate duplicated jq filter)
Apply fixes? [y/n] y

$ /gh-issue-driven:ship

─── Gate 2: Pre-PR Review ─────────────────────────
Skill batch invocation:
  /claude-c-suite:cso      → ## Verdict: green
  /claude-c-suite:qa-lead  → ## Verdict: yellow
  /claude-c-suite:cto      → ## Verdict: green
Aggregated: yellow

⚠ Proceed to PR creation? [y/n] y
✓ PR #124 created: https://github.com/JFK/gh-issue-driven/pull/124

Request Copilot review? [y/n] y          ← HITL Gate
Polling Copilot … (loop 1/5)
Copilot posted 2 actionable comments. Addressing …
(loop 2/5) Copilot: APPROVED
exit_reason=approved

Saving session summary to Kagura Memory … ✓
```

main にマージされたあとのリリース:

```
$ /gh-issue-driven:tag 0.4.0 dry-run
[DRY RUN]
Version v0.4.0
Manifests
  plugin.json:      0.3.0 → 0.4.0
  marketplace.json: 0.3.0 → 0.4.0
CHANGELOG.md updated
Release Notes Preview:
  ## What's Changed
  ### Enhancements
  - /propose command (#17) — @JFK
  ### Bug Fixes
  - doctor: skill origin URL (#9) — @JFK
Next steps: run without dry-run to execute

$ /gh-issue-driven:tag 0.4.0
(実行 …)
Release https://github.com/JFK/gh-issue-driven/releases/tag/v0.4.0
```

この一連の流れが、冒頭の横矢印そのものです。左端の Issue 起票から右端の Release まで、**3フェーズ × 3つの立ち止まり** で繋がっています。

### 10.3 config のカスタマイズ

で `~/.claude/gh-issue-driven-config.json` のテンプレートが生成されます(既存があれば上書きしない設計です)。

---

## 11. まとめ

* 完成形は最初からありません。正解はやりながら探します
* AI 全自動化ではこの「探索」は起きません
* HITL Gate = AI の出力を見た人間の中に起きる反応を引き出す装置です
* gh-issue-driven はその装置を **3フェーズの横矢印** の上に仕込んだ Claude Code Plugin です
* Gate の設計こそが、AI 時代の開発における差別化要因になっていきます
* **立ち止まることは、遅れることではありません。気づくことです**

---

## 参考リンク
