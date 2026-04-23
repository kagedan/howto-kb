---
id: "2026-04-15-claude-codeのrulesとskillsはいつ読まれる-ロード機構を理解して常時コストを41-01"
title: "Claude Codeのrulesとskillsはいつ読まれる？ — ロード機構を理解して常時コストを41%削減した話"
url: "https://zenn.dev/yottayoshida/articles/claude-code-context-cost-structure"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-04-15"
date_collected: "2026-04-16"
summary_by: "auto-rss"
query: ""
---

> この記事は2026年4月時点の [code.claude.com 公式ドキュメント](https://code.claude.com/docs/en/memory) に基づいています。

## この記事で伝えたいこと

Claude Codeの設定ファイルには**3つのロード層**がある。全部が毎回読まれているわけではない。

* **Always**: CLAUDE.md と `paths:`なしの rules → セッション開始時に読み込まれ、以降ずっとコンテキストに残る
* **Conditional**: `paths:`付きの rules/skills → マッチするファイルを触った時だけ
* **On-demand**: skills の本文 → 使う時だけ（通常はname と descriptionだけ常時。`disable-model-invocation: true` ならゼロ）

この仕組みを理解して自分のワークスペースを監査したら、**常時ロード量を1,358行から807行に（-41%）減らせた**。しかもその過程で「そもそも前提が間違っていた」ことに気づいた。

CLAUDE.mdの書き方や、rules/skillsが何なのかについては、すでに良い記事がたくさんある。

この記事ではそこは繰り返さず、**「いつ何がロードされるか」と「どうすればコストを減らせるか」だけ**を書く。

---

## きっかけ: Rate limitに早く到達するようになった

最近、セッション中にRate limitに達するのが明らかに早くなった。Claude Codeのバージョンの問題とか、Opus 4.6のtoken消費特性とか、原因は色々言われている。それはいったん置いておいて、自分でコントロールできる部分——設定ファイルのtoken効率——を見直そうと思った。

CLAUDE.mdが222行になっていた。公式の推奨は200行。「まずここを削るか」と思って全設定ファイルの行数を数えた。

```
  222  CLAUDE.md
2,165  .claude/rules/ （15ファイル合計）
9,833  .claude/skills/ （39ファイル合計）
```

**CLAUDE.mdは全体の2%にも満たなかった。** rulesだけで2,165行。skillsは9,833行。

ここで疑問が湧いた。この12,000行、毎回全部ロードされてるのか？ skillsがオンデマンドなのは知っていた。でも**rulesがどういうタイミングでロードされるか、正直わかっていなかった**。

自分の場合は「公式ドキュメント見てよしなに設定して」でrulesやskillsを増やしていた。出来上がった設定の有効性検証はしていたが、ロード機構の理解は曖昧だった。冒頭で紹介した記事のようなベストプラクティスはとても参考になるが、**他人の設定やリポジトリをそのまま突っ込む**人もいるだろう。skillsは `!` 記法で任意のshellコマンドを前処理として実行できるため、中身を確認せずに取り込むのは危険だ。原理をわからないまま使っているので、問題が起きても気づかないし修正できない。

Vibe codingならぬ**Vibe設定**。動いてるからヨシ、で積み上がった設定ファイルが何をしているか、自分でも把握していない。Vibe codingと同じ問題構造だ。

あらためて公式ドキュメントを読み直した。

---

## 3つのロード層: Always / Conditional / On-demand

公式ドキュメントを読み込んで整理した結果がこれだ。

### 1. Always（セッション開始時に読み込み、以降コンテキストに残り続ける）

**CLAUDE.md** と **`paths:`フロントマターのないrules**。

公式にはこう書いてある:

> "Rules without `paths` frontmatter are loaded at launch with the same priority as `.claude/CLAUDE.md`."

「毎回ファイルから再読込される」のではなく、**セッション開始時に一度読み込まれ、その後の各リクエストのコンテキストに載り続ける**という仕組みだ。結果として、セッション中はずっとトークンを消費し続ける。

つまりCLAUDE.mdを分割してrules/に置いても、`paths:`を付けなければ**コスト的には何も変わらない**。ファイルが分かれているだけで、全部コンテキストに載っている。

ここが最初の気づきだった。「rulesに分けたから整理できた」と思っていたが、トークンコスト的には1つの巨大CLAUDE.mdと同じだった。

### 2. Conditional（条件付き）

**`paths:`付きのrulesとskills**。マッチするファイルをClaudeが読んだ時だけロードされる。

```
---
paths:
  - "src/api/**/*.ts"
---
```

> "Path-scoped rules trigger when Claude reads files matching the pattern, not on every tool use."

TypeScriptのAPIファイルを触っている時だけAPIルールが注入される。Rustを書いている時は一切ロードされない。これは賢い。

**あまり知られていないが、skillsにも`paths:`が使える。** 公式のfrontmatter表にちゃんと載っている。ただし公式の表現は少し異なり、rulesが「マッチするファイルをreadした時にtrigger」なのに対し、skillsは「マッチするファイル群で**working**している時に自動ロード」となっている。意味は近いが、厳密には同じメカニズムとは言い切れない。

ただし落とし穴がある。`**/*.ts`のような広いパターンを書くと、TypeScriptファイルを1つでも開いた瞬間にトリガーされる。TypeScript中心のリポジトリでは、conditionalとは名ばかりで**実質alwaysに近づきやすい**。（これは公式の説明ではなく、自分の環境での観察に基づく推論だ。混在リポジトリならそうとは限らない。）

### 3. On-demand（使った時だけ）

**skills**。ここはなんとなく知っていたが、改めて読むと細かい仕組みがあった。

skillsは**2段階ロード**になっている:

* **常時**: skill の **name と description** がコンテキストに乗る。Claudeが「このスキル使えそうだな」と判断するためのインデックス。ただし `description + when_to_use` は1件あたり1,536文字で切り詰められ、skill数が多いと全体予算に合わせてさらに短縮されることがある
* **invoke時**: ユーザーが`/skill-name`で呼ぶか、Claudeが自動判断した時に初めて本文がロードされる

> "Description always in context, full skill loads when invoked."

つまり500行のskillを作っても、普段のコストはnameと短い説明文だけ。本文は必要になるまで眠っている。

### invocation制御でさらにコストが変わる

ここが既存記事であまり触れられていないポイントだ。

| 設定 | name + descriptionの扱い | 本文の扱い | 誰が起動？ |
| --- | --- | --- | --- |
| デフォルト | 常時コンテキストに乗る | invoke時 | Model と User |
| `user-invocable: false` | 常時コンテキストに乗る | invoke時 | Modelのみ（`/`メニュー非表示） |
| `disable-model-invocation: true` | **コンテキストに乗らない** | `/skill-name`時のみ | Userのみ |

**`disable-model-invocation: true` にすると、description すらゼロコストになる。** Claudeはそのskillの存在を知らない。ユーザーが明示的に呼んだ時だけ全文がロードされる。

`/deploy`や`/commit`のように「自分のタイミングで呼びたいワークフロー」には、これが最適だ。Claudeに勝手にデプロイを判断されても困る。

---

## 自分のワークスペースをあらためて監査した

ロード機構を理解した上で、自分の環境を見直してみた。

### Before: 思い込みの状態

最初は「rules 15ファイルが全部毎回ロードされている」と思っていた。

|  | ファイル数 | 行数 |
| --- | --- | --- |
| CLAUDE.md | 1 | 222行 |
| rules（paths:なし） | 9 | 1,136行 |
| rules（paths:あり） | 6 | 1,029行 |
| **常時ロード合計** |  | **1,358行** |

### 最初の発見: 前提が間違っていた

1ファイルずつfrontmatterを確認したら、**6ファイルには既に`paths:`が付いていた**。

* `agent-browser.md`（407行）→ ブラウザ自動化ファイルを触った時だけ
* `chrome-ext.md`（301行）→ Chrome拡張ファイルを触った時だけ
* `n8n.md`（121行）→ n8nワークフローを触った時だけ

これらは最初から条件ロードだった。「全部常時」という前提で立てた最適化計画の半分が不要だった。

**教訓: 最適化する前に、現状を正確に把握する。** 当たり前のことだが、思い込みで飛ばしてしまいがちだ。

### やったこと

残りの常時ロード9ファイル（1,136行）を精査した。

`git.md`、`security.md`、`orchestrator.md`、`memory.md`の4ファイル（633行）は毎セッション必要な正当な常時ロード。問題は**残り5ファイル（503行）**。これらは「並列実行の判断基準」「Agent/Skill連携マップ」「リファクタ手順書」といった、特定の作業でしか参照しない手順書・リファレンスだった。

**intervention 1: 手順書5ファイルをskillsに降格（-503行）**

| 旧rules | → 新skills | 設定 |
| --- | --- | --- |
| `agent-team.md`（129行） | `agent-team-strategy` | `user-invocable: false` |
| `agent-skill-interaction-map.md`（153行）+ `validation-templates.md`（111行） | `agent-skill-routing`（統合） | `user-invocable: false` |
| `refactor-execution-plan.md`（56行）+ `operation-checklist.md`（54行） | `agent-skill-refactoring`（統合） | `user-invocable: false` |

`user-invocable: false`にしたので、Claudeは必要と判断した時に自動でロードできる。情報は失われていない。**「常時」から「必要時」にタイミングが変わっただけ**だ。

**intervention 2: CLAUDE.mdのスリム化（222→174行、-48行）**

`rules/orchestrator.md`と重複していた要約を削除し、クイックリファレンスとGotchasを追加した。

### After

|  | Before | After | 削減 |
| --- | --- | --- | --- |
| CLAUDE.md | 222行 | 174行 | -48 |
| rules（paths:なし） | 1,136行 | 633行 | -503 |
| **常時ロード合計** | **1,358行** | **807行** | **-551（-41%）** |

最大のインパクトは skills 降格の503行。CLAUDE.md のスリム化は全体の9%にすぎなかった。

---

## 設定の置き場所を決めるときの考え方

「この情報、どこに置くべき？」と迷ったときの判断基準をまとめた。

**毎セッション必要な事実・ルール** → CLAUDE.md か rules（paths:なし）

* 「テストは必ず実行する」「セキュリティルールに従う」のような常時適用ルール
* CLAUDE.md は200行以内が目安。超えるなら rules/ に分割

**特定ファイルを触る時だけ必要** → rules/skills に `paths:` を付ける

* 「TypeScript API を書く時のルール」「Chrome拡張の規約」
* パターンは具体的に。`**/*.ts` ではなく `src/api/**/*.ts`

**手順書・リファレンス** → skills

* Claudeに自動判断させたい → `user-invocable: false`（descriptionだけ常時）
* 自分で呼ぶタイミングを決めたい → `disable-model-invocation: true`（完全ゼロコスト）

**コスト構造の整理**: 一般的には、**常時全文**（CLAUDE.md / unscopedなrules）が最も重く、**常時メタ情報のみ**（デフォルトskills）、**条件付き**（`paths:`付きrules/skills）、**完全手動**（`disable-model-invocation: true`）の順に軽くなる。ただし `paths:` 付きは発火頻度とファイルサイズ次第で、デフォルトskillsより重くなることもある。

---

## 知っておくと得する小ネタ

**HTMLコメントはタダ。** CLAUDE.md 内の `<!-- コメント -->` はClaudeに送信される前にstripされる。人間向けのメモを書いてもトークンを消費しない。

**description予算はコンテキストの1%。** 公式によると、全skillのdescription合計の予算はコンテキストウィンドウの1%で、fallbackは8,000文字。1件あたりの `description + when_to_use` は1,536文字で切り詰められる。

**compaction後のskill復元には上限がある。** `/compact`後は直近invokeのskillから順に復元されるが、1件5,000トークン上限・合計25,000トークンまで。重いskillが続くと5件前後で古いものから落ちる。軽いskillならもっと残る。

**description予算は環境変数で上書きできる。** `SLASH_COMMAND_TOOL_CHAR_BUDGET=16000 claude` で起動すると予算が倍になる。ただし根本解決は「skillの数を減らす」か「descriptionを短くする」。

---

## まとめ: 3つの原則

1. **現状を正確に把握してから最適化する。** 「全部毎回ロードされてる」は思い込みかもしれない。`paths:`の有無を1ファイルずつ確認するところから始める。
2. **`paths:`パターンの広さに気をつける。** `**/*.ts` のような汎用パターンは、言語中心のリポジトリでは実質alwaysに近づく。プロジェクト固有のディレクトリやファイル名で絞る。
3. **rulesからskillsへの降格が最大のレバレッジ。** 「毎回必要なルール」と「たまに参照する手順書」を区別する。手順書をskillsに移すだけで常時コストは大きく減る。さらに `disable-model-invocation: true` にすればほぼゼロだ。

設定ファイルはClaudeへの指示書であると同時に、トークン予算の配分先でもある。「書いてあるから安心」ではなく「いつロードされるか」を意識するだけで、コスト効率と指示の遵守率の両方が変わる。

---

## 参考

**公式ドキュメント（この記事の根拠）:**
