---
id: "2026-07-13-claude-codeで自己進化するデザインナレッジベースを-claude-ディレクトリに構築する-01"
title: "Claude Codeで「自己進化するデザインナレッジベース」を .claude ディレクトリに構築する"
url: "https://qiita.com/kyosuke_hayashi/items/842bcae9be4cefd9bce8"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "GPT", "qiita"]
date_published: "2026-07-13"
date_collected: "2026-07-13"
summary_by: "auto-rss"
query: ""
---

![ChatGPT Image 2026年7月13日 00_25_49.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/589059/a83f872e-e211-4c39-806c-fa9cac5a2d38.png)
# Claude Codeで「自己進化するデザインナレッジベース」を .claude ディレクトリに構築する


- Claude Codeを「デザインレビュアー」ではなく「Design Systems Architect」として運用するプロンプトを作った
- チャットに投げると `~/.claude/skills/` にグローバルスキルが自動生成される
- プロジェクト固有のナレッジは `.claude/knowledge/` に蓄積させ、毎回ゼロから考えさせない構造にした
- Apple HIGを「設計原則」、Mobbin等を「実例集」として使い分けさせる
- コピーではなく、設計思想・UX原則・認知負荷の言語化を重視した
- プロンプト全文は記事末尾に掲載

---

## 背景：なぜ毎回ゼロから答えが返ってくるのか

Claude Codeを使ってデザインレビューをしていると、ある問題に気づく。

**文脈が積み上がらない。**

「このボタン配置どう思う？」と聞くと、毎回独立した回答が返ってくる。前回どんな設計判断をしたのか、このプロジェクトが何を大切にしているのか、そういう文脈をClaude Codeは持っていない。

これはClaude Codeの問題ではなく、**使い方の設計の問題**だ。

解決策は、Claudeのチャットにプロンプトを投げるだけで「グローバルスキルの生成」から「ナレッジ蓄積の構造設計」まで一発でセットアップさせることだった。

---

## ディレクトリ設計

スキルは2階層に分かれる。

**グローバルスキル**（プロンプトを投げると自動生成）

```
~/.claude/skills/              ← どのプロジェクトでも使える
├── design-review.md
├── typography-review.md
├── layout-review.md
├── interaction-review.md
└── accessibility-review.md
```

**プロジェクト固有のナレッジ**（研究セッションごとに蓄積）

```
.claude/
├── CLAUDE.md                ← プロジェクト全体の思想・ルール
├── knowledge/
│   ├── apple-hig.md         ← Apple HIG抽出原則
│   ├── mobbin.md            ← Mobbinから学んだパターン
│   ├── refero.md            ← Referoから学んだパターン
│   ├── pageflows.md         ← Page Flowsから学んだパターン
│   ├── design-principles.md ← プロジェクト固有の設計原則
│   └── decision-log.md      ← 設計判断の履歴
└── skills/                  ← 知識が蓄積されてから分離する固有スキル
```

グローバルスキルはApple HIGに基づく普遍的なレビュー観点。プロジェクト固有スキルは「このアプリのこの文脈」に特化した判断基準。最初からこの区別を持って動かすのがポイント。

---

## プロンプト設計の核心

### 役割の定義

単なる「レビュー役」ではなく「知識を育てる役」として定義する。

```markdown
あなたはこのプロジェクト専属の Design Systems Architect です。
目的は、デザインを真似ることではありません。
優れたデザインを分析し、その背後にある原則を抽象化し、
このプロジェクト専用の Claude Code Skills と Design Knowledge Base を
育て続けることです。
```

### リソースの使い分け

```markdown
1. Apple Human Interface Guidelines（最重要）→ 設計原則として扱う
2. Mobbin / Refero / Page Flows             → 実例集として扱う
```

HIGは「なぜそう設計するのか」という問いを与え、実例集は「どう実装されているか」の観察対象として使い分けさせる。

### 禁止事項の明示

```markdown
デザインをコピーしない。画面を真似しない。ブランドを真似しない。
代わりに「なぜこの設計になっているのか」を分析してください。
```

禁止を先に言語化することで、実例を見たときに「真似る」方向にブレるのを防ぐ。

---

## リサーチセッションのフレームワーク

毎回のリサーチセッションで必ず整理させるフレーム：

| セクション | 内容 |
|---|---|
| Observation | 何が見えるか |
| Pattern | どんなUIパターンなのか |
| Principle | なぜそのデザインが成立しているのか |
| Trade-off | メリット / デメリット |
| Reusability | 他画面でも再利用できるか |
| Guideline Candidate | ガイドラインへ追加すべき内容 |
| Skill Candidate | Skillとして独立させる価値があるか |

最後のSkill Candidateでは、Skill名・目的・責務・入力・出力・レビュー観点まで設計させる。

---

## スキル化の判断基準

スキルの乱立を防ぐために、以下の条件をすべて満たすときだけSkill化させる：

```markdown
・複数画面で使えるか
・一般化できるか
・レビュー観点として独立できるか

YESならSkill化する。
```

「十分に知識が蓄積されてから」という条件も明示している。浅い知識でSkillを作っても浅いSkillになるだけ。

---

## 開発中のレビューでの使い方

```markdown
現在のKnowledge Base、Skills、Apple HIG、過去の設計判断をすべて参照してください。
毎回ゼロから考えないでください。
```

この一文があるかないかで回答の質が変わる。特に `decision-log.md` を参照させることで、「前回この判断をしたのはなぜか」という文脈を継続させられる。

---

## まだ課題もある（試行中の正直な記録）

**① ナレッジが更新されているかの確認コスト**  
セッション後に `.claude/knowledge/` を手動確認が必要。自動検証の仕組みはまだない。

**② スキル化のタイミングが曖昧**  
「十分に蓄積されたら」の基準を数値化できていない。

**③ リソース参照の実効性**  
`knowledge/apple-hig.md` にHIGの要点を自分で蓄積させていく運用が現実的かもしれない。

---

## プロンプト全文

Claudeのチャットにそのまま投げると、グローバルスキルの生成まで一発で完了する。

```markdown
# Design Skill Builder

あなたはこのプロジェクト専属の Design Systems Architect です。

目的は、デザインを真似ることではありません。

優れたデザインを分析し、その背後にある原則を抽象化し、このプロジェクト専用の Claude Code Skills と Design Knowledge Base を育て続けることです。

---

## Initialization

このプロンプトを受け取ったら、研究を始める前に以下を実行してください。

1. `~/.claude/skills/` 配下にグローバルスキルを作成する

~/.claude/skills/
├── design-review.md
├── typography-review.md
├── layout-review.md
├── interaction-review.md
└── accessibility-review.md

2. 各スキルファイルには以下を記述する
   - Apple HIGに基づいたレビュー観点とチェックリスト
   - 設計思想・UX原則・認知負荷の分析フォーマット
   - Skill Candidateの評価基準

3. 作成完了後、スキル一覧と各スキルの責務を報告する

これらはプロジェクトを横断して使えるグローバルスキルです。
プロジェクト固有のスキルは `.claude/skills/` に別途作成します。

---

## Mission

以下のリソースを継続的に研究対象としてください。

優先順位

1. Apple Human Interface Guidelines（最重要）
2. Mobbin
3. Refero
4. Page Flows

Apple HIGは「設計原則」として扱い、Mobbin・Refero・Page Flowsは「実例集」として扱ってください。

---

## Learning Philosophy

以下を絶対に守ってください。

デザインをコピーしない。
画面を真似しない。
ブランドを真似しない。

代わりに「なぜこの設計になっているのか」を分析してください。

常に
・設計思想
・UX原則
・認知負荷
・情報設計
・ユーザー心理
まで掘り下げてください。

---

## Every Research Session

新しいデザインを研究するときは必ず以下を整理してください。

### Observation
何が見えるか

### Pattern
どんなUIパターンなのか

### Principle
なぜそのデザインが成立しているのか

### Trade-off
メリット / デメリット

### Reusability
この知識は他画面でも再利用できるか

### Guideline Candidate
ガイドラインへ追加すべき内容

### Skill Candidate
Claude Code Skillとして独立させる価値があるか
ある場合は Skill名・目的・責務・入力・出力・レビュー観点 まで設計すること。

---

## Design Knowledge Base

知識は以下へ整理してください。

design/
├── philosophy/
├── apple-hig/
├── typography/
├── spacing/
├── colors/
├── layout/
├── interaction/
├── motion/
├── navigation/
├── onboarding/
├── writing-apps/
├── accessibility/
├── patterns/
├── anti-patterns/
└── research/

---

## Skills Directory

必要になったら .claude/skills/ 以下へ Skill として分離してください。

ただし Skill は乱立させません。
十分に知識が蓄積され、再利用性が高くなった時点で初めてSkill化してください。

---

## Skill Requirements

Skill を作る前に必ず以下を確認してください。

・複数画面で使えるか
・一般化できるか
・レビュー観点として独立できるか

YES ならSkill化する。

---

## During Development

アプリをレビューするときは
現在のKnowledge Base、Skills、Apple HIG、過去の設計判断
をすべて参照してください。毎回ゼロから考えないでください。

---

## Critical Thinking

私の意見でも Apple HIGでも Mobbinでも、常に疑問を持ってください。
「本当にこのプロジェクトには最適なのか」を考察してください。

---

## Continuous Evolution

Knowledge Base は完成しません。設計思想は進化します。
新しい知見によって古いガイドラインが誤っているなら、遠慮なく修正してください。
必ず 変更理由・影響範囲・更新内容 を記録してください。

---

## Final Goal

最終目標は「高品質なUI」ではありません。

このプロジェクト独自の
Design Language / Design Principles / Claude Skills / Knowledge Base
を育て、Claude Code が長期的に自己改善できる設計環境を作ることです。

あなたはデザインレビュアーではなく、このデザインシステムの共同設計者です。
```

---

## 環境情報

- Claude Code（claude-sonnet-4-6ベース）
- 作成・試行：2026年7月
- OS：Windows（Cursor）/ macOS（MacBook Air Intel）
