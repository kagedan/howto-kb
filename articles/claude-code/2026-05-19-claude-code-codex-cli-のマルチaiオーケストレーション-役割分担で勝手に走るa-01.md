---
id: "2026-05-19-claude-code-codex-cli-のマルチaiオーケストレーション-役割分担で勝手に走るa-01"
title: "Claude Code × Codex CLI のマルチAIオーケストレーション — 役割分担で勝手に走るAIを制御する"
url: "https://zenn.dev/kobarutosato/articles/claude-codex-orchestration"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "AI-agent", "LLM", "OpenAI"]
date_published: "2026-05-19"
date_collected: "2026-05-20"
summary_by: "auto-rss"
query: ""
---

## はじめに：なぜ2つのAIを組み合わせるのか

Claude Code も Codex CLI も、単体で「コードを書かせる」ことはできます。ではなぜわざわざ2つを組み合わせるのか？

結論から言うと、**「仕様判断」と「実装」と「レビュー」を別のAIに分けると、それぞれの居心地のいい場所で働かせられる**からです。

* Claude Code は **対話と判断**に最適化されている — 仕様を聞き返してくれるし、トレードオフを言語化してくれる(Plan モードという「コードを書く前に方針だけ詰める」専用モードが用意されていることに、その思想が端的に表れています)
* Codex CLI は **コード生成と差分編集**に最適化されている — とにかく動くコードを出してくる
* 「書いた本人がレビューする」と盲点に気づきにくい (同一履歴・同一重みで見落としが再生産される) → **別コンテキスト/別モデルの第三者AI**にレビューさせる

本記事では、Claude Code をオーケストレータ、Codex CLI を実装ワーカー、別コンテキストの Claude を独立レビュアーとして組み合わせる構成を、NestJS プロジェクトでの実証つきで紹介します。

---

## 1. 全体像：3層構造で役割を分担する

| 役割 | 担当 | 実体 |
| --- | --- | --- |
| 仕様分解・判断・対話 | Claude (メイン) | 人間と直接話すセッション |
| 実装・テスト・verify | Codex CLI | `codex-worker` サブエージェント経由 |
| 独立レビュー | Claude (別コンテキスト) | `claude-reviewer` サブエージェント |

ポイントは、**人間が話す相手は Claude オーケストレータだけ**ということです。Codex は表に出てこない実装屋として黙々と働き、レビュアーは別人格として独立判定を出す。人間は「やってほしいこと」と「最終結果」だけを見る構造になります。

---

## 用語整理：「verify」「`verify.sh`」「Codex の自己修正挙動」の違い

以降「verify」という単語が複数の文脈で出てきます。最初に切り分けておきます。

| 用語 | 何を指すか |
| --- | --- |
| **`verify.sh`** | このプロジェクトで用意した**シェルスクリプト本体**。`npm test` (Jest unit) → `npm run build` → `npm run test:e2e` を順に走らせ、全段グリーンなら exit 0、どこかで失敗したら exit 非0で止まる |
| **verify** (動詞) | 「`verify.sh` を実行して、変更が壊れていないか確認する」という操作 |
| **(観測された) Codex の自己修正挙動** | Codex CLI が、自分の出した変更に対してテスト/ビルド系コマンドを自発的に走らせ、失敗したら修正して再実行する**ことがある**、という観測された傾向。本リポジトリの構成・スキル定義・ラッパースクリプトのどこにも「緑になるまでループせよ」とは書かれていません(`.codex/skills/run-verify/SKILL.md` はむしろ「1回叩いて pass/fail を報告。修正は caller の仕事」と明記)。Codex CLI 公式仕様としての裏取りは本記事時点で**未取得** |

つまり関係としては：

* `verify.sh` = **テスト/ビルド一括実行スクリプト** (=ハーネス。中身)
* verify = `verify.sh` を**1回叩く操作**
* 「Codex の自己修正挙動」= 上記の verify を Codex が**自分の判断で**再実行することがある、という観測。明示的に組み込まれたループ機構ではない

本記事の例 (§6) では、Codex が一度 `TS1272` でビルド失敗 → 自分で `import type` に書き換え → `verify.sh` 再実行 → グリーン、という流れが**1事例として**観測されました。あくまで「実装ワーカーに据えてみたら自己修正がそこそこ働いた」という現場観測に留めます。

---

## 2. 設計思想：なぜこの役割分担が効くのか

ベンチマーク上、Claude と Codex (GPT-5系) の**生コード生成能力はほぼ拮抗**しています。それでも役割を分けると効くのは、両者の差が **能力の高低ではなく、出力スタイルと最適化対象 (= RLHF の厚みの方向)** にあるからです。

* Claude は「**判断を言語化する**」方向に学習が厚い → 仕様の聞き返し・トレードオフの提示が自然に出る
* Codex は「**緑のコードを出す**」方向に学習が厚い → 確認より先に手が動く・失敗時に自分で叩き直す傾向が観測される (機構として保証されたものではない)

同じ作業をやらせれば似たコードを書きますが、**振る舞いの初期値が違う**。だから「居心地のいい役割」に置いた方が、それぞれ無理なく力を出します。

### 2.1 得意領域マップ

象限の読み方は次のとおり：

* **左下=Claude メイン (オーケストレータ)** — 仕様分解・設計判断・人間対話
* **左上=Claude reviewer (別コンテキスト)** — 厳密にレビューを言語化
* **右上=Codex (実装ワーカー)** — 差分実装・テスト追加・失敗時の自己修正(観測)

「能力差」ではなく「**それぞれが居心地のいい象限が違う**」ことが本質です。

### 2.2 モデル特性の対比

| 観点 | Claude (Sonnet/Opus 4.x) | Codex CLI (GPT-5系) |
| --- | --- | --- |
| **最適化対象** | 判断・要件分解・トレードオフ提示 | コード生成・差分編集・テスト合格 |
| **得意な出力** | 仕様書、設計判断、レビュー指摘、人間向け解説 | 実装/テストコード、差分パッチ、リファクタ |
| **苦手 / リスク** | コードを書かせると饒舌・抽象的になりがち | 仕様が曖昧だと**勝手に補完して走る** |
| **トークン密度** | 中(説明文混じり) | 高(差分集中) |
| **長時間ループ耐性** | コンテキスト一貫性が強い | `reasoning_effort` を調整して速度/品質を制御 |
| **自己レビューバイアス** | 比較的厳しめだが、自分の出力を「自然な続き」として評価しがち | 甘くなりがち。同一プロンプト履歴で見落とすパターンが残る → **別モデルでレビューする価値が大きい** |

### 2.3 「Codex がコード得意」の実体

* OpenAI が Codex CLI を **コード編集に特化したプロダクト**として出しており、ファイル編集ツールなどコードを書くワークフローに最適化する挙動も見られる
* 出力傾向として「**コードを直接書く**」ことに集中する。Claude が「まずこの設計で?」と確認に入りがちなのに対し、Codex は「とりあえず動くコードを出す」
* ただし**能力の絶対値では Claude 4.x と Codex (GPT-5系) はベンチマーク上ほぼ拮抗**。差は**出力スタイル**にある

### 2.4 「Claude が仕様/判断が得意」の実体

* Anthropic は **判断を言語化させると強い** 設計を意図しており、Agentic Tool Use と意思決定の RLHF が分厚い
* 人間との対話で要件を引き出す・トレードオフを並べる・**「なぜそれを選んだか」を残す**用途で Claude を中心に置くと、後から読み返したときの情報密度が高い
* Claude Code は **Plan モード**(コードを一切書かず、調査と方針合意だけを進める専用モード)を持っており、「設計→合意→実装」を明確に分離する思想がプロダクト機能として組み込まれている。ワーカー側が手を動かす前に**オーケストレータ側で仕様を固める**という本構成の役割分担に、そのまま乗る
* Task tool / Skill / メモリも含めて、Claude Code は **オーケストレータとして人間と並走する設計**になっており、これを実装ワーカーに使うのは過剰

---

## 3. キー設計判断：なぜそうしたのか

### 3.1 なぜ Codex を Claude のサブエージェント経由で呼ぶか

Claude Code の Task tool が提供する「**並列起動・コンテキスト分離・結果集約**」をタダで使うためです。

直接 Bash で Codex を呼ぶと、Codex の冗長な出力 (diff、ログ、思考プロセス) がすべてメインの Claude のコンテキストに流れ込んで汚染します。`codex-worker` というサブエージェントを挟むと、そこが別コンテキストで吸収してくれて、**要約だけがメインに返ってくる**。

### 3.2 なぜ独立レビュアーを分けるか

「**実装した本人がレビューすると盲点に気づかない**」という多AI協調の核心原則です。これは LLM の擬人的な「愛着」ではなく、もっと機構的な話です。

* **同一プロンプト履歴の前提を引き継いでしまう**: 実装時に置いた前提(型の解釈、命名、設計判断)が、続けてレビューさせると暗黙の「与件」となり、そこ自体の妥当性は問われにくくなる
* **自己一致バイアス**: LLM は直前の自分の出力と整合する続きを生成しやすいため、評価も「これで OK」の方向に分布が寄る
* **同一の重み**: 同じモデルの同じ訓練分布では、書いたときに見落としたパターンはレビューでも同じく見落とす

そこで **別コンテキスト**(履歴を引き継がない)で、理想的には **別モデル** に判定させると、上記いずれもリセットされ、規約違反や論理ミスを拾いやすくなります。本構成では Claude reviewer を採用していますが、Codex を実装ワーカーに据えている時点で**実装と評価が別モデルになっている**点が肝です。

### 3.3 なぜラッパースクリプト (`codex-run.sh`) を必須にするか

**安全・コスト既定値の一元化**のためです。`reasoning_effort=medium`、`--sandbox`、`--skip-git-repo-check` などのオプションを毎回書かなくて済む。escalate したいときだけ `--high` を渡す、という運用にできます。

#### `reasoning_effort` の選び方

Codex CLI の `reasoning_effort` は `low` / `medium` / `high` の3段階です。デフォルトを **`medium`** に置くのを推奨します。

| レベル | 速度・コスト | 品質 | 推奨用途 |
| --- | --- | --- | --- |
| `low` | 最速・最安 | 浅い (テンプレ的) | 定型タスク (boilerplate生成、リネーム、フォーマット適用) |
| **`medium`** (既定) | 中 | 実用十分 | **通常の機能追加、DTO/Service/Controller の典型追加、テスト追加** |
| `high` | 遅い・高コスト | 深い推論 | 後述の escalate 条件に該当する場合のみ |

**`high` に escalate すべきタイミング**:

1. **同じ仕様で `medium` が2回失敗した**とき — Codex がループしているサインなので推論を厚くする
2. **クロスモジュールで影響範囲が広い変更**(例: 認証フロー全面改修、ドメインモデル再設計) — `medium` だと文脈を取りこぼしやすい
3. **アルゴリズム的・数値的に正しさが要る変更**(例: 並行制御、トランザクション境界、計算精度) — 浅い推論だと微妙なバグが残る
4. **既存コードのリファクタで「壊さないこと」が最重要**なとき — 影響範囲の解析に推論コストを払う価値がある
5. **`reviewer` が REQUEST\_CHANGES を返した後の再委譲** — 失敗を学習し直してほしい局面

逆に **`low` に下げてよい**のは、雛形生成・リネーム・依存追加だけのような、考えるより手を動かす方が早いタスク。本記事の `POST /items` 程度なら `medium` で十分通ります(§6 参照)。

運用上は、`./scripts/codex-run.sh "<spec>"` を既定 `medium` で回し、必要なときだけ `./scripts/codex-run.sh --high "<spec>"` でエスカレート、というスイッチ運用がシンプルです。

### 3.4 なぜ `AGENTS.md` を正本にするか

**クロスエージェント互換規格**だからです。

* `CLAUDE.md` は Claude 固有
* `.codex/config.toml` は Codex 固有
* `AGENTS.md` は **両方が読む**

そこで `CLAUDE.md` は `@AGENTS.md` 1行に簡素化し、**規約の真実源を `AGENTS.md` に一本化**します。両AIが同じ規約を読むので、片方だけが知らないルール、ということが起きません。

---

## 4. 構成ファイル

| パス | 役割 |
| --- | --- |
| `AGENTS.md` | 全エージェント共通契約 (規約 + 連携フロー)。**正本** |
| `CLAUDE.md` | `@AGENTS.md` 1行のみ |
| `.codex/config.toml` | model / reasoning\_effort をプロジェクト固定 |
| `.codex/skills/run-verify/SKILL.md` | `verify.sh` 標準呼出手順 |
| `.claude/agents/codex-worker.md` | Codex 委譲ワーカー (Bash でラッパー起動) |
| `.claude/agents/claude-reviewer.md` | 独立レビュアー (別コンテキスト) |
| `scripts/codex-run.sh` | reasoning/sandbox 既定値ラッパー |
| `scripts/verify.sh` | test + build + e2e ハーネス |

---

## 5. 実行フロー：1タスクが完了するまで

人間が「`POST /items` を validation つきで追加して」と頼んでから完了報告までのシーケンスです。

注目ポイント：

* **オーケストレータは仕様を 6 節 (Context/Task/Files/Contract/Constraints/Verify) に分解する**。曖昧な依頼を曖昧なまま Codex に投げると勝手に補完して暴走するため、ここで構造化する
* **codex-worker は Codex の自己申告を Read で再検証する**。「直しました」を信じず、ファイルを実際に読む
* **APPROVE が出るまで commit しない**。レビュアーが REQUEST\_CHANGES を返したら、仕様を more specific にして再委譲

---

## 6. 例：NestJS 11 で `POST /items` API を作ってみる

### 6.1 題材

* **題材**: NestJS 11 (Express) の新規プロジェクトに `POST /items` API を追加 (DTO validation 付き)
* **結果**: codex-worker → claude-reviewer → verify のフルパスを 1サイクル完走

### 6.2 `verify.sh` の最終結果

```
=== 1/3  npm test (Jest unit) ===
Test Suites: 2 passed, 2 total
Tests:       4 passed, 4 total

=== 2/3  npm run build (nest build) ===
(no errors)

=== 3/3  npm run test:e2e (Jest E2E) ===
Test Suites: 2 passed, 2 total
Tests:       6 passed, 6 total

All checks passed.
```

### 6.3 `codex-worker` レポート (抜粋)

* **Files changed**: 10 (`src/items/*` 6新規 + `src/app.module.ts`, `src/main.ts`, `package.json`, `package-lock.json`)
* **Reasoning used**: medium (`--high` なし)
* **途中エラー**: 一度 `TS1272` (isolatedModules + value import) でビルド失敗 → **Codex 自身が `import type { Item }` に修正して再 verify → pass**
* **Verdict**: SUCCESS

### 6.4 `claude-reviewer` レポート (抜粋)

* **Files reviewed**: 10
* **CRITICAL**: 0 / **HIGH**: 0 / **MEDIUM**: 0 / **LOW**: 3
  1. E2E で `ValidationPipe` を再宣言しており `main.ts` と重複 (NestJS 慣例だが drift リスク注意)
  2. `Item` 型を `type` で export (`interface` がやや慣習)
  3. `import type { Item }` は適切 (確認メモ)
* **Verdict**: APPROVE

人間がやったのは「仕様を書く」と「APPROVE を確認する」だけです。

---

## 7. 他プロジェクトへの横展開手順

新しい NestJS リポジトリで本構成を立ち上げる手順を、そのまま手順書化したもの：

1. `nest new <name> --package-manager npm --skip-git`
2. **`.gitignore` を手動作成** (NestJS テンプレ + `.serena/` + `AGENTS.override.md`)
3. `git init -b main` → 初回 commit (例: `chore: initial NestJS scaffold`)
4. 以下をコピペで配置 (中身は `AGENTS.md` と `verify.sh` のみフレームワーク依存):
   * `AGENTS.md`, `CLAUDE.md` (`@AGENTS.md` 1行)
   * `.codex/config.toml`, `.codex/skills/run-verify/SKILL.md` + `agents/openai.yaml`
   * `.claude/agents/codex-worker.md`, `claude-reviewer.md`
   * `scripts/codex-run.sh` (+x), `scripts/verify.sh` (+x)
5. `./scripts/verify.sh` でグリーン確認 → commit (`chore: add orchestration scaffolding`)
6. 実タスクの仕様を **Context / Task / Files / Contract / Constraints / Verify** の6節で書く
7. Task tool → codex-worker 役で Codex 実装
8. Task tool → claude-reviewer 役で独立レビュー
9. APPROVE なら commit、REQUEST\_CHANGES なら仕様を more specific にして再委譲

---

## 8. 再利用できる部品

他プロジェクトに持っていって効く順：

| 部品 | 効果 |
| --- | --- |
| `scripts/codex-run.sh` (ラッパー必須化) | **大** — 安全/コスト既定値の一元化 |
| `.claude/agents/codex-worker.md` | **大** — 並列起動 + コンテキスト分離が無料 |
| `.claude/agents/claude-reviewer.md` | **大** — 同一履歴/同一重みで生まれる見落としをリセットできる |
| `.codex/skills/<name>/SKILL.md` | 中 — 頻出操作のスキル化 |
| `AGENTS.md` ベース運用 | 中 — Codex/Claude 共通契約 |

特に効いた設計判断：

* `CLAUDE.md` を `@AGENTS.md` 一行化
* Codex 側で動かない役割は Claude 側に逃がす柔軟性

---

## 9. まとめ：何が嬉しいのか

この構成を回してみて、本質的に効いていたのは次の3点でした。

**① コンテキスト汚染を防げる**  
Codex の冗長な出力は `codex-worker` が吸収する。メインの Claude は「仕様」と「結果サマリ」だけを見て判断できる。長時間セッションでも頭がクリア。

**② 自己レビューバイアスを除去できる**  
LLM は直前の自分の出力と整合する続きを返しやすく、同じモデル・同じ履歴では「書いたときに見落としたパターン」をレビューでも見落としやすい。別コンテキスト・別モデルで評価することで、この自己一致バイアスをリセットできる。

**③ 仕様の構造化が強制される**  
Codex に投げる前に Context/Task/Files/Contract/Constraints/Verify の6節で書き直す必要があるため、**人間自身の思考が整理される**。AIに任せた結果、人間の仕事の質が上がるという逆説。

「AIにコードを書かせる」のではなく、「**AIたちに役割を持たせて協調させる**」。マルチAI協調は能力差ではなく**最適化対象の差**を活かす設計です。ぜひ手元のプロジェクトで試してみてください。
