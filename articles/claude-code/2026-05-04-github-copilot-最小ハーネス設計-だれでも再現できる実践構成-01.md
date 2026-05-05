---
id: "2026-05-04-github-copilot-最小ハーネス設計-だれでも再現できる実践構成-01"
title: "GitHub Copilot 最小ハーネス設計: だれでも再現できる実践構成"
url: "https://zenn.dev/sawa_shin/articles/github-copilot-minimal-harness-design"
source: "zenn"
category: "claude-code"
tags: ["MCP", "AI-agent", "zenn"]
date_published: "2026-05-04"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

連載最終回は、ここまで紹介してきた instructions・custom agents・Agent Skills を **1 つの実践構成に束ねる方法** を見ます。

この記事でいう「ハーネス」は GitHub Copilot の公式用語ではありません。**instructions・custom agents・Agent Skills・review ステップをどう並べて仕事を流すか** を設計する枠組みを指しています。この考え方は、AI エージェント領域で **harness engineering**（複数の AI エージェントセッションを構造化された再現可能なワークフローに組み立てる手法）として広まりつつある概念です。

この記事の前提

* 2026-04 時点の GitHub Docs と VS Code Docs を根拠にしています
* prompt files、hooks、MCP は扱いません（hooks については第 1 回でリンクを紹介しています）
* 「ハーネス」は公式用語ではなく、instructions + agents + skills + review step をまとめた構成設計を指す呼び方です（harness engineering として知られる概念に基づきます）

## この記事で得られること

1. この記事でいう**最小ハーネスの意味**
2. instructions → agents → skills を**どの順で組むとわかりやすいか**
3. **少ない指示で自律的に精度よく動く**ための設計の考え方
4. 実際のディレクトリ構成とファイルの中身（**再現できる実例**付き）

---

## そもそもハーネスってなに？

ハーネスは、**前提・役割・レビュー位置を先に決めておく設計** です。

AI エージェントの文脈では **harness engineering** として、複数のエージェントセッションやモデル呼び出しを構造化された再現可能なワークフローに組み立てる手法を指します。

> prompt engineering（一つの問いを磨く）→ context engineering（前提を整える）→ **harness engineering**（全体の流れを設計する）

Agent Mode のモデル自体を強くする話ではなく、**1 回の依頼で agent がどれだけ自律的に・精度よく動いてくれるか**を設計する枠組みと考えてください。

![前提、役割、道具、レビューを1つのハーネスとして支えるイメージ](https://static.zenn.studio/user-upload/deployed-images/a72cf7ae809d9ea6e624ace7.png?sha=9fee59113fd1eea4990fb6bb6e183d20ef59350a)

> 📖 GitHub Docs の公式カスタマイズ機能として並んでいるのは custom instructions、custom agents、Agent Skills などで、`harness` という機能名はありません。  
> [Copilot customization cheat sheet](https://docs.github.com/en/copilot/reference/customization-cheat-sheet)

---

## なぜハーネス設計が大事なの？

Agent Mode の精度がぶれる原因は、モデルの能力不足だけでなく、**ミッション・前提・役割を明示しないまま作業を始めること**にもあります。

**少ない指示で agent が自律的に・精度よく仕事を進めてくれる設計** を目指すのがハーネスエンジニアリングの目的です。

そのために必要なのが：

* 前提を **instructions** で先に渡す
* 役割を **custom agent** で分担する
* 専門手順を **skill** で武器として持たせる
* 最後に **review step** を固定する

こう並べると、agent が自律的に長く仕事を継続し、精度が維持されやすくなります。

---

## Step 1: 最初に置く土台 — ミッションと instructions

### ミッション 1 文

すべての判断の基準になるミッションを 1 文で定義します。

たとえば、開発プロジェクトであれば：

```
高品質なコードを継続的にデリバリーし、保守性と開発速度を最大化する。
```

### repo instructions で前提を固定

`.github/copilot-instructions.md` に、agent が常に踏まえるべきルールをまとめます。

> 📖 repo instructions と path instructions の使い分けは、第 2 回で詳しく扱っています。  
> [第2回: instructions で回答精度を上げる最小設定](https://zenn.dev/sawa_shin/articles/github-copilot-instructions-guide)

```
# プロジェクト共通ルール

## ミッション

> 高品質なコードを継続的にデリバリーし、保守性と開発速度を最大化する。

## 最重要原則

1. **品質ファースト** — テスト可能で保守しやすいコードを書く
2. **設計してから実装する** — いきなりコードを書かず、影響範囲と方針を先に整理する
3. **公式情報を優先する** — ライブラリやフレームワークの仕様は公式ドキュメントで確認する
4. **誠実に書く** — 事実、推測、意見を混同しない
```

実際の copilot-instructions.md にはこの他に「コーディング規約」「レビュー観点」「禁止事項」なども含まれます。ポイントは、**長くなりすぎず、かつ agent の自律動作の精度に直結する指針を書く** ことです。

### path instructions で特定ファイルのルールを追加

`.github/instructions/tests.instructions.md` のように、特定ファイル向けのルールを追加します。

```
---
applyTo: "tests/**/*.test.*,tests/**/*.spec.*"
---

# テストコード規約

- テストは AAA パターン（Arrange / Act / Assert）で書くこと
- テスト名は「何を」「どんな条件で」「どうなるか」を明記すること
- モックは最小限にし、実際の振る舞いに近いテストを優先すること
```

---

## Step 2: 役割を分ける — custom agents

`.github/agents/` に、役割ごとの agent を定義します。

> 📖 custom agent / subagent / Agent Skills の基本概念と YAML 設定は、第 3 回で整理しています。  
> [第3回: custom agents と Agent Skills で役割を分ける](https://zenn.dev/sawa_shin/articles/github-copilot-subagents-skills-guide)

最初は **3 つの役割** で十分です。

![PM、Critic、QA Gateの3役で作業を流すイメージ](https://static.zenn.studio/user-upload/deployed-images/18f53064a41560fab639e890.png?sha=7873766dbb2953cbf067748b4b2bc324407fb080)

| 役割 | agent ファイル | 何をするか |
| --- | --- | --- |
| **PM** | `pm.agent.md` | 要件ベースで計画を分解し、agent に振り分ける |
| **Critic** | `critic.agent.md` | 設計や実装に対して「本当にこれで要件を満たすか」を疑う |
| **QA Gate** | `qa-gate.agent.md` | 変更内容に応じて validate と専門レビューを選び、Go/No-Go を判定 |

### 例: critic.agent.md

```
---
name: critic
description: 計画・設計・実装判断に対して、要件充足・エッジケース・整合性の観点から反証する批判者。
tools: ["read", "search"]
---

# Critic

このエージェントは、「本当にこの設計で要件を満たせるか」を疑う役です。

- 設計方針と実装の整合性を批判する
- エッジケースや見落としがないかチェックする
- ファイルの編集は行わず、指摘のみを行う
```

ポイント：

* `tools: ["read", "search"]` で**読み取りと検索だけに制限**している
* main agent に全部乗せるより、**critic は読むだけ** にするとレビュー精度が上がる
* main agent が `@critic` を subagent として呼び出し、指摘をもらう流れ

---

## Step 3: 武器を持たせる — Agent Skills

`.github/skills/` に、agent が使える手順パッケージを配置します。

```
.github/skills/
├── coding-standards/
│   └── SKILL.md              ← コーディング規約チェック skill
└── official-docs-enforcer/
    └── SKILL.md              ← 公式ドキュメント参照 skill
```

custom agent + skill をセットで設計する例：

| agent | 装備する skill | 効果 |
| --- | --- | --- |
| **PM** (`pm.agent.md`) | `coding-standards` | コーディング規約に沿った設計手順を持つ |
| **Critic** (`critic.agent.md`) | `official-docs-enforcer` | 公式ドキュメントとの整合チェック手順を持つ |
| **QA Gate** (`qa-gate.agent.md`) | `coding-standards` | コード品質の最終チェック手順を持つ |

---

## Step 4: 全体のフローを review step まで通す

最小構成をまとめると、**5 つの要素** です。

| # | 要素 |
| --- | --- |
| 1 | ミッション **1 文** |
| 2 | repo instructions **1 枚** |
| 3 | path instructions（テスト向け）**1 枚** |
| 4 | custom agents **3 役**（PM / Critic / QA Gate） |
| 5 | review step **1 回** |

skill は、各 agent が必要なタイミングで自動的に読み込みます。

### 依頼から完了までの流れ

> 🔵 **青**: あなた（人間）のアクション　　⬛ **黒**: agent が自律的に実行するアクション

---

## 実際のディレクトリ構成

ここまでの内容を実際のディレクトリ構成にまとめると、こうなります。

```
your-project/
├── .github/
│   ├── copilot-instructions.md          ← repo instructions（ミッション + 共通ルール）
│   ├── instructions/
│   │   ├── tests.instructions.md        ← テストコード向けルール
│   │   └── github-config.instructions.md ← .github 配下の設定向けルール
│   ├── agents/
│   │   ├── pm.agent.md                  ← PM（計画・分解）
│   │   ├── critic.agent.md              ← Critic（批評）
│   │   ├── qa-gate.agent.md             ← QA Gate（品質判定）
│   │   └── ...                          ← 必要に応じて追加
│   └── skills/
│       ├── coding-standards/
│       │   └── SKILL.md                 ← コーディング規約チェック skill（必須ファイル）
│       ├── official-docs-enforcer/
│       │   └── SKILL.md                 ← 公式ドキュメント参照 skill（必須ファイル）
│       └── ...
├── src/                                 ← ソースコード
├── tests/                               ← テスト
└── docs/                                ← ドキュメント
```

この構成は、私が実際の開発プロジェクトで運用しているものをベースにしています。

---

## Copilot に作ってもらうプロンプト集

ここまでで構成図はできました。次は **空のディレクトリを置いて、中身を Copilot に作らせる** のが速いです。

ポイントは 2 つ：

1. **公式ドキュメントを必ず参照させる**（記憶で書かせない）
2. **生成後は人間が中身を確認する**（公開前のレビューは省略しない）

以下のプロンプトは VS Code の Agent Mode で、上のディレクトリに `.keep` などを置いた状態から実行する想定です。

### プロンプト 1: repo instructions の雛形を作る

```
.github/copilot-instructions.md を作成してください。

要件:
- 内容と書式は以下の公式ドキュメントを必ず確認してから作成してください。
  https://docs.github.com/en/copilot/reference/customization-cheat-sheet
  https://docs.github.com/en/copilot/concepts/prompting/response-customization
- このリポジトリのミッションを 1 文で書く
- 「最重要原則」「コーディング規約」「レビュー観点」「禁止事項」のセクションを置く
- 長くなりすぎないこと（200 行を超えそうなら要点に絞る）
- 推測ではなく、リポジトリ内の実態（README、package.json、既存コード）を読んでから書く
```

### プロンプト 2: path instructions を追加する

```
.github/instructions/tests.instructions.md を作成してください。

要件:
- frontmatter の applyTo 構文と仕様は以下の公式ドキュメントで確認してください。
  https://docs.github.com/en/copilot/reference/customization-cheat-sheet
- applyTo は tests 配下の test/spec ファイルだけに当たるパターンにする
- AAA パターン、テスト名の書き方、モックの方針を簡潔に書く
- copilot-instructions.md と重複しない、テスト固有のルールだけを書く
```

### プロンプト 3: 3 役の custom agent を作る

```
.github/agents/ 配下に pm.agent.md / critic.agent.md / qa-gate.agent.md の 3 ファイルを作成してください。

要件:
- frontmatter の項目（name, description, tools など）は以下の公式ドキュメントで確認してください。
  https://docs.github.com/en/copilot/reference/custom-agents-configuration
- pm: 要件ベースで計画を分解する。tools は read と search に絞る
- critic: 設計や成果物に反証する。編集はしない（read と search のみ）
- qa-gate: 変更内容に応じて検証を選び Go / No-Go を出す。編集はしない
- description は日本語で、いつ呼ばれるべき agent かが 1 文でわかること
```

### プロンプト 4: skill を 1 つ作って agent と紐づける

```
.github/skills/coding-standards/SKILL.md を作成してください。

要件:
- skill の構造と SKILL.md の書き方は以下の公式ドキュメントで確認してください。
  https://docs.github.com/en/copilot/concepts/agents/about-agent-skills
- SKILL.md には description（必須）と、コーディング規約チェックの手順を書く
- description は「どんな場面で呼ばれるべきか」を 1 文で書く
- 既存の copilot-instructions.md と矛盾しないこと
```

!

⚠️ **生成後は必ず人間が確認してください。**

* frontmatter のスペルミス、`applyTo` のパターン誤り、`tools` の指定ミスは agent の挙動を壊します
* description が曖昧だと subagent や skill が呼ばれません
* 生成された内部リンクや公式 URL が実在することを確認してください

### 動作確認

ファイルを置いたら、Agent Mode のチャットで次のように呼び出して、各 agent と skill が認識されているか確認します。

```
@pm 今このリポジトリで未対応の改善タスクを 3 つに分解してください。
@critic 直前の計画に対して、見落としや過剰設計を 3 点指摘してください。
@qa-gate 直前の変更が公開可能かを判定してください。
```

custom agent が picker に出てこない、subagent が呼ばれない、といった場合は **frontmatter の構文ミス**か **description の書き方** が原因のことが多いです。

---

## 少ない指示で精度よく動かすには？

ハーネス設計の目的は「少ない指示で agent が自律的に・精度よく動くこと」です。

ハーネスが整っていると：

![短い依頼でもハーネスによって前提、役割、道具、レビューが効くイメージ](https://static.zenn.studio/user-upload/deployed-images/36b6f73545ecdd9fdc89c305.png?sha=f07f028e8b48c0f0c8b79318db14fa3dc081dea5)

* 前提（instructions）が先に渡っているので、**毎回の指示が短くて済む**
* 役割（agents）が分かれているので、**1 つの指示の中で agent が自律的に長く仕事を続けられる**
* review step が固定されているので、**大きな仕事を任せても最後に人間が確認するポイントが明確**

---

## まとめ

最小ハーネス設計の要点は、**機能を足す順番より、仕事を流す順番を決めること**です。

### 最小ハーネスの 5 ステップ

1. ミッションを **1 文** で定義する
2. instructions で**前提を固定**する
3. custom agents で **役割を分ける**（PM / Critic / QA Gate の 3 役）
4. Agent Skills で**専門の武器を持たせる**
5. 最後に **review step** を通す

---

連載を振り返ると：

* 第 1 回で Agent Mode の**入り口**を作り
* 第 2 回で **instructions** で毎回の指示を減らし
* 第 3 回で **custom agents / Agent Skills** で役割と武器を分け
* 第 4 回でそれらを **1 つの最小構成** へ束ねた

この連載で紹介した最小構成は、そのまま自分のリポジトリで再現できます。まずは copilot-instructions.md を 1 枚置くところから始めて、使い込みながら agents と skills を足していく——この順番が、いちばん無理なく進められるはずです。
