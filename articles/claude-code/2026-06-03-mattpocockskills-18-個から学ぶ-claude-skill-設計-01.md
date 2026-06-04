---
id: "2026-06-03-mattpocockskills-18-個から学ぶ-claude-skill-設計-01"
title: "mattpocock/skills 18 個から学ぶ Claude Skill 設計"
url: "https://qiita.com/ryoji9702/items/fdd5e0ac1ce6718fb680"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "AI-agent", "LLM", "cowork", "TypeScript", "qiita"]
date_published: "2026-06-03"
date_collected: "2026-06-04"
summary_by: "auto-rss"
query: ""
---

## はじめに

`mattpocock/skills` は、Total TypeScript で知られる Matt Pocock 氏が「自分の `.claude/` ディレクトリそのものを公開した」リポジトリです。公開から短期間で **GitHub Stars 10 万超**、Fork 9.6k に達しています（2026-06-01 時点）。

「Skill を書こうとしているけど、SKILL.md に何を詰めれば良いか分からない」「他人の運用中スキルを覗いてみたい」という人にとって**今いちばん刺さる教材**です。実際に 18 個全部読みながら、設計の癖と効くテクニックを整理したのが本稿です。

### 対象読者

- Claude Code / Cowork でスキルを書こうとしているが、書き出しが固まらない人
- 自分のスキル運用が「コマンド化」に寄っていて、もっと役割化したい人
- 「Vibe Coding じゃない、地に足の付いた AI 開発」のテンプレを探している人

### この記事でわかること

- mattpocock/skills 18 個の全体像と分類
- 「AI コーディングエージェントの 4 つの失敗モード」とその処方箋
- 明日から効く 4 スキル（grill-me / grill-with-docs / caveman / handoff）の使いどころ
- SKILL.md を書くときに参考になる 3 つの共通パターン

### 前提知識・環境

- Claude Code または Cowork を触ったことがある（スキル機構の概念を知っている）
- `.claude/skills/` ディレクトリと `SKILL.md` の役割を雑にでも把握している

## 1. リポジトリ全体像

- **Repo**: [mattpocock/skills](https://github.com/mattpocock/skills)
- **License**: MIT
- **Stars / Forks**: 108k / 9.6k
- **構成**: 18 個の Skill を `engineering / productivity / misc` の 3 カテゴリに分割
- **インストール**: `npx skills@latest add mattpocock/skills`（[skills.sh](https://skills.sh/mattpocock/skills) 経由）

README の冒頭で本人がはっきり書いている設計思想がとても刺さります。

> Developing real applications is hard. Approaches like GSD, BMAD, and Spec-Kit try to help by owning the process. But while doing so, they take away your control. These skills are designed to be small, easy to adapt, and composable.

**プロセスを丸ごと奪う系のフレームワーク（GSD / BMAD / Spec-Kit）への明示的なアンチテーゼ**として、「小さく・差し替えやすく・組み合わせ可能」な単位に分解されています。この姿勢は SKILL.md 本文の書き味にも一貫していて、どれも 1 ファイルが短いです。

## 2. 18 スキルの全体マップ

カテゴリ別に並べると次の通りです。

### Engineering（10 個）

| Skill | 役割 |
| --- | --- |
| **grill-with-docs** | 計画を既存ドメインモデルに照らして詰問しつつ、`CONTEXT.md` / ADR を同時更新 |
| **diagnose** | 再現 → 最小化 → 仮説 → 計測 → 修正 → 回帰テスト、の規律あるバグ調査ループ |
| **tdd** | red-green-refactor を強制し、垂直スライス単位で機能追加 / バグ修正 |
| **triage** | Issue を triage 用ステートマシンで分類 |
| **improve-codebase-architecture** | `CONTEXT.md` と ADR を踏まえて、コードを「深いモジュール」に寄せる改善箇所を抽出 |
| **setup-matt-pocock-skills** | repo 単位の設定（issue tracker / triage ラベル / ドキュメント配置）を一回だけスキャフォールド |
| **to-issues** | PRD や仕様を「単独で着手可能な GitHub Issue」に分解 |
| **to-prd** | 会話のコンテキストから PRD を組み立て、Issue 化 |
| **zoom-out** | 知らないコードに対して「全体の中での位置づけ」を語らせる |
| **prototype** | 使い捨てプロトタイプ（CLI / UI バリアント）を作って設計判断を駆動 |

### Productivity（4 個）

| Skill | 役割 |
| --- | --- |
| **grill-me** | 計画 / 設計を全部の枝葉まで詰問されるインタビュー |
| **caveman** | フィラーを削ってトークン消費を **〜75% 圧縮**する超圧縮モード |
| **handoff** | 会話を引き継ぎドキュメントに圧縮し、別エージェントに渡せる形にする |
| **write-a-skill** | 適切な構造・progressive disclosure で新規スキルを書く |

### Misc（4 個）

| Skill | 役割 |
| --- | --- |
| **git-guardrails** | Claude Code hooks で `push / reset --hard / clean` 等の危険コマンドをブロック |
| **migrate-to-shoehorn** | テストファイルの `as` 型アサーションを `@total-typescript/shoehorn` に置換 |
| **scaffold-exercises** | 練習問題の sections / problems / solutions / explainers をスキャフォールド |
| **setup-pre-commit** | Husky + lint-staged + Prettier + 型チェック + テストの pre-commit を構築 |

## 3. 設計思想 — Matt が「真に解こうとしている 4 つの失敗モード」

README は単なる Skill 一覧ではなく、**「AI コーディングエージェントの 4 つの失敗モードと、それぞれへの処方箋」** という構造になっています。これが本リポジトリの本質的な価値です。

### #1: The Agent Didn't Do What I Want（指示と実装のミスアライメント）

「あなたが何を求めているか、開発者は本当に分かっているか？」というアジャイル本にもよくある問いを、AI エージェントに当てはめた話です。**処方箋は「grilling session」**。エージェントの側から計画について質問を浴びせさせます。

- `grill-me` — 非コード作業全般向け
- `grill-with-docs` — `grill-me` にドメインドキュメント連携を追加した強化版

> The most common failure mode in software development is misalignment.

開発者なら誰でも刺さるフレーズ。**ペアプロでも品質を担保する一番の方法は「質問」** だという、極めて Pragmatic Programmer 的な姿勢。

### #2: The Agent Is Way Too Verbose（共有言語の不在）

Eric Evans の DDD を引いて、**「共有言語（Ubiquitous Language）が無いとエージェントは 1 単語で済む話を 20 単語で書く」** と問題提起。処方箋は `CONTEXT.md` というドメイン用語集を repo に置くこと。

具体例も載っている：

- **BEFORE**: "There's a problem when a lesson inside a section of a course is made 'real'"
- **AFTER**: "There's a problem with the materialization cascade"

**共有言語のメリットは、トークン削減だけではない**：

1. 変数 / 関数 / ファイル名が一貫した語彙で命名される
2. コードベースがエージェントにとって読みやすくなる
3. 「思考の語彙」が短くなり、トークンを推論に回せる

この発想を担うのが `grill-with-docs` で、grilling と同時に `CONTEXT.md` や ADR を更新します。**「会話の副産物としてドキュメントが育つ」設計**が秀逸です。

### #3: The Code Doesn't Work（フィードバックループ不足）

Pragmatic Programmer の "Always take small, deliberate steps" を引いて、**フィードバックループの遅さがコード品質を決める** と主張。処方箋は静的型 + ブラウザ + 自動テストの 3 点セット。

- `tdd` — red-green-refactor を強制
- `diagnose` — デバッグのベストプラクティスを単純なループに包む

### #4: We Built A Ball Of Mud（設計の腐敗）

Kent Beck と Ousterhout を引いて、**エージェントは「コード書く速度」を上げると同時に「腐敗する速度」も上げる** と警告。処方箋は **「設計について毎日考える」** を Skill に組み込むこと。

- `to-prd` — PRD を書く前にどのモジュールに触るかをクイズ
- `zoom-out` — システム全体の中での位置づけを説明させる
- `improve-codebase-architecture` — 数日に 1 回走らせて「深いモジュール」化のチャンスを探す

## 4. 実際に効くと感じた 4 つのスキル

18 個全部良いですが、**「明日から効く」4 個** に絞るとこうなります。

### 4.1 grill-me — 計画を全方位から詰問させる

「実装に入る前にこの設計をレビューして」と投げると、**意思決定ツリーの各分岐を順番に潰すように質問を浴びせて**くれます。曖昧な要件・暗黙の前提・未決事項を、エージェントの側から拾い上げてくれます。

`grill-with-docs` のような `CONTEXT.md` 連携は無いですが、**ドメインドキュメントがまだ整っていない初期フェーズ・個人プロジェクト・非コード作業** ではこちらが使いやすいです。「Claude に勝手に進められる前に、まず自分の頭の中を整理する」用途に効きます。書き出し前に 5 分これを回すだけで、後段の手戻りが目に見えて減ります。

### 4.2 grill-with-docs — ドメイン整合性を詰める

`grill-me` にドメインドキュメント連携を足した強化版です。「やりたいことを 1 文で書いた issue」を投げると、**ドメインモデルとの整合性、用語のブレ、抜けてる意思決定** を片っ端から詰問してくれます。`CONTEXT.md` を repo に置いておくと、用語が会話の途中で **共有語彙にリプレース**されていくので非常に便利です。

さらに、質問は1問ずつ選択肢付きで投げてくれるので、答えながら頭の中が整理されていく感覚があります。

![スクリーンショット 2026-06-03 232542.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4437970/718673aa-24d6-4b56-9014-960e7a518f7b.png)

これを 1 回挟むかどうかで、後段の `tdd` / `to-prd` の出力品質が全く変わります。**書き出し前のチェックポイント**として組み込みたいです。

### 4.3 caveman — トークン削減モード

`/caveman` で発動するだけで、Claude の出力が **超圧縮モード**になります。技術的精度を保ったままフィラーを削るので、長時間セッションでのトークン消費が体感で 1/4 になります。**Opus を使うときに特に効きます**。

Productivity 系の中では一番すぐに価値が出ます。デフォルトを caveman にしてもいいくらいです。

### 4.4 handoff — セッションをまたぐ

長いセッションをやっていて context window が逼迫してきたとき、`/handoff` で **「次のエージェントに渡せる引き継ぎ docs」** を生成します。新しいセッションを開いて handoff docs を最初に投げると、コンテキストロスがほぼゼロで再開できます。

**Cowork や Claude Code を「数日にまたがるプロジェクト」で使う人** は、これを知っているだけでワークフローが変わります。

## 5. SKILL.md の書き味 — 18 個読んで気づいた共通パターン

ソースコードを読むと、**18 個に強く貫通している規約**が 3 つあります。

### 5.1 description は短く、具体的に、命令形

```yaml
name: grill-with-docs
description: Grilling session that challenges your plan against the existing
  domain model, sharpens terminology, and updates CONTEXT.md and ADRs inline.
```

抽象語（"intelligent" や "comprehensive"）を使わず、**「何をするか」だけを 1 文**で書きます。Anthropic 公式の Skill ガイドラインに忠実な書き方です。

### 5.2 本文は「ステップ番号付き」で、長くしない

各 SKILL.md は驚くほど短いです。「やる手順を 5〜10 ステップで列挙する」だけで、長い説明文を書きません。**プロンプト本文は "プロンプトのプロンプト" であり、長さは精度を下げる**という割り切りです。

### 5.3 進行状況を「人間に問う」設計

`grill-me` 系も `triage` 系も、**判断分岐は必ず人間に投げ返します**。「Claude に勝手に進めさせない」が貫かれているのが、「なんでも自動で進める」系のスキルとの大きな違いです。

## 6. 試すならどう入れるか

3 つの導入パスがあります。

### パス A: 公式インストーラ（最速）

```bash
npx skills@latest add mattpocock/skills
```

スキルを選んで、対象エージェント（Claude Code / Codex / Cursor）を選べば終わりです。`/setup-matt-pocock-skills` を必ず選択し、初回起動時に repo の設定（issue tracker / triage ラベル / docs パス）を済ませます。

### パス B: 部分採用（手動 clone）

`skills/engineering/grill-with-docs/` だけを `.claude/skills/` 配下にコピーします。**全部入れるより、まず `grill-with-docs` と `tdd` の 2 個から**始めるのが、フィット確認には向いています。

### パス C: Cowork プラグイン化（自前ビルド）

Cowork で使うなら 18 スキルを `.plugin` ファイルにまとめて、自分のマーケットにアップロードする手もあります。**ただしこれは結構な罠が待ち構えていた**ので、別記事に書きました。

## 7. 個人的に効いた発見 — 「Skill は OOP の `class`」 説

18 個を眺めて気づいたのは、**Skill の単位が "オブジェクト指向の class" にすごく似ている** こと。

- `description` = class doc
- `SKILL.md` 本文 = `__init__` + メソッド群
- 同梱 `scripts/` = privateメソッド / utility
- スキル間連携（`/grill-with-docs` → `/tdd` の流れ）= メソッドチェーン

**「カスタムスラッシュコマンドが関数だとすると、Skill はクラス」** という感覚は、運用 1 ヶ月後に確信に変わりました。Matt のリポジトリは、その class 設計の "良いお手本集" として読めます。

## まとめ

- `mattpocock/skills` は **「Vibe Coding じゃない、地に足の付いた AI 開発」** をテーマにした 18 スキル集
- 4 つの失敗モード（misalignment / verbosity / broken code / ball of mud）への処方箋として体系化されている
- **明日から効くのは `grill-me` / `grill-with-docs` / `caveman` / `handoff`** の 4 個
- SKILL.md の書き味（短い description / 短い本文 / 人間に問う設計）は、自分の Skill を書くときの規範になる
- Skill は「LLM 時代の class」だと思って読むと、設計の意図が掴みやすい

Anthropic 公式の Skill ガイドラインを読んでも実例が足りなくてピンと来ない人は、まずこのリポジトリを 1 周読むのが早いです。**コード以前に「設計思想」が学べる**のが、このリポジトリの本当の価値です。

## 参考

- [mattpocock/skills — GitHub](https://github.com/mattpocock/skills)
- [Skills 公式インストーラ — skills.sh](https://skills.sh/mattpocock/skills)
- [Total TypeScript — Matt Pocock 本人](https://www.totaltypescript.com/)
- [Claude Skills 公式ドキュメント — Anthropic](https://docs.claude.com/en/docs/build-with-claude/skills)
- [The Pragmatic Programmer — David Thomas & Andrew Hunt](https://www.amazon.co.uk/Pragmatic-Programmer-Anniversary-Journey-Mastery/dp/B0833F1T3V)
- [Domain-Driven Design — Eric Evans](https://www.amazon.co.uk/Domain-Driven-Design-Tackling-Complexity-Software/dp/0321125215)
- [A Philosophy of Software Design — John Ousterhout](https://www.amazon.co.uk/Philosophy-Software-Design-2nd/dp/173210221X)
