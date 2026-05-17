---
id: "2026-05-16-claude-codecodexにレビューを依頼するskill-01"
title: "【Claude Code】Codexにレビューを依頼するSkill"
url: "https://qiita.com/jyas-protein/items/ae3f744dd203f4f51903"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "OpenAI", "GPT"]
date_published: "2026-05-16"
date_collected: "2026-05-17"
summary_by: "auto-rss"
query: ""
---

# はじめに

今回は最近話題の、「Claude CodeからCodexを呼び出してレビューを依頼する」Skillを作成してみました。

Codexのセットアップ方法に関してはこちらをご参照ください。

https://qiita.com/jyas-protein/items/100e962813aaef568da3


# なぜこの組み合わせが流行っているのか

この組み合わせが多く採用されている理由を簡潔にまとめてみました。

1. 「実装担当」と「レビュー担当」を完全に分離できるため思考バイアスが引き継がれない。
1. Claude Codeの強みである「長文理解、オーケストレーション、対話（曖昧な指示に対して逆質問してくれる）」と、Codexの強みである「実装速度、生成コードの品質、批判的レビュー視点」それぞれを活かせる形になっている。
1. 異なるAIに相互レビューさせることで、ハルシネーションや見落としを減らせる。
1. Claude CodeとCodexを連携させる公式のMCPやプラグインが整備されてきた。
1. コンテキスト/トークン使用量をそれぞれのAIに分散できる。



# なぜSkillなのか

MCPやプラグイン（内部でMCPを使用）といった選択肢がありますが、以下の理由から自作のSkillを使用することにしました。

・MCP経由だとレスポンスが遅い/安定しない
・進捗内容を確認できない
・アップデートによって予期しない設定や仕様変更が加えられる危険もある

Skillを自作すると、これらの問題を解決するだけでなく、
**モデル/推論強度/承認ポリシー/Sandboxの設定/fast_mode...といった細かい設定をカスタマイズできる**
ことが一番大きな恩恵だと思います（セキュリティ対策にも）


こちら今回、Skillを自作しようと思ったきっかけになった記事です！

https://zenn.dev/owayo/articles/63d325934ba0de




# 完成したSkillがこちら

**※skill-creatorを使用しています。**
※過去に作成したSkillが一部反映されています。

「過去に作成したSkill」

https://qiita.com/jyas-protein/items/2d6f5ec6ae76002788a0

https://qiita.com/jyas-protein/items/81a66b0eb4376d3f5ed1

一部マークダウンの仕様上、[```]の前に#を入れています。

```md:.claude/skills/codex-review/SKILL.md
---
name: codex-review
description: Claude Codeで実装した未コミットの変更（git diff HEAD）をコミット前にCodex CLI（gpt-5.5 / model_reasoning_effort=high / web_search=live / sandbox=read-only）にレビュー依頼し、敵対的レビュー・セキュリティチェック・リファクタリング・ベストプラクティス準拠を含む全観点で精査した結果を、指摘1件ずつ「適用 / スキップ / さらに議論」の3択でユーザーと対話的に判断・反映していくスキル。ユーザーが `/codex-review` と入力したとき、または「コミット前にCodexにレビューさせて」「Codexで敵対的レビュー」「Codexにセキュリティチェック頼んで」「Codexにリファクタリング指摘もらって」「Codexにベストプラクティスを見てもらって」「未コミットの変更をCodexでレビュー」「Codexで全観点レビュー」など、Claude Code実装直後にCodexによる独立した第三者視点のレビューを得たい場面で必ず使用する。`codex exec` を **一度きりのコマンド** で呼ぶ自己完結構成（`config.toml` や profile に依存しない）、`--sandbox read-only` での非破壊実行、未コミット変更（`git diff HEAD`）を対象範囲とする運用、コミットやpushは行わず作業ツリーへの修正反映までを担当する方針が必要なすべてのケースで本スキルを優先的に呼び出すこと。
---

# codex-review

Claude Codeによる実装が一段落した「コミット前」のタイミングで、未コミット変更（`git diff HEAD`）をCodex CLIに **独立した第三者レビュアー** として精査させ、その結果を1件ずつユーザーと対話で取り込んでいくスキル。

## このスキルが目指すこと

Claude Codeが書いたコードを、Claude Code自身ではなく **別モデル（OpenAI Codex / gpt-5.5）** がレビューすることで、以下を狙う:

- **敵対的レビュー**: 「書いた本人が見落としやすい」境界条件・例外パス・契約違反を、別視点・別モデルの目で拾う
- **セキュリティチェック**: OWASP系の脆弱性、秘密情報の混入、安全でないデフォルト、依存ライブラリのCVE観点（Web Search live）
- **リファクタリング指摘**: 差分内のコード品質・命名・重複・抽象化
- **ベストプラクティス準拠**: 言語/フレームワーク慣習、リポジトリの既存パターン、テスト網羅、ログ・観測性

最終判断は必ずユーザーが行う。Codexの指摘は「採用 / スキップ / さらに議論」の3択で1件ずつ吟味し、採用したものだけを作業ツリーに反映する。コミット・pushは本スキルでは **一切行わない**。

## 採用する Codex 呼び出し方針

**一度きりのコマンド**で呼ぶ。`~/.codex/config.toml` や `--profile` に依存しない自己完結構成。skill 内の挙動を再現可能にするため、必要な設定はすべて `--config` で明示する。

- 入力: `git diff HEAD` を **stdin** で渡す（プロンプト本文を肥大化させない）
- 出力: `.codex/review.md` に Markdown で書き出し、skill 側が `Read` ツールで読む
- モデル: `gpt-5.5` / reasoning_effort=`high` / verbosity=既定（medium）
- サンドボックス: `read-only` （レビューは読み取り専用）
- 承認方針: `never` （非対話実行）
- Web Search: `live` （CVE・最新仕様の確認に必要）
- Codex 内部処理（プロンプト指示）は英語、ユーザー向け最終レポート（findings の値）は日本語

## 実行手順

### Step 1: 前提条件と現在状態を一括取得

以下を **並列で** 実行:

#```bash
command -v codex
#```

#```bash
git rev-parse --is-inside-work-tree
#```

#```bash
git branch --show-current
#```

#```bash
git status --short
#```

#```bash
git diff HEAD --stat
#```

#### 前提が満たされない場合

- `codex` が見つからない → 「Codex CLI がインストールされていません。`npm i -g @openai/codex` 等でインストールし、`codex login` で認証してから再実行してください」と伝えて終了。
- git リポジトリでない → その旨を伝えて終了。
- `git diff HEAD --stat` が空（未コミット変更なし） → 「未コミットの変更がありません。レビュー対象がないため終了します」と伝えて終了。

#### 差分が極端に大きい場合

`git diff HEAD --stat` の出力で **変更行数合計が 3,000 行を超える** 場合、ユーザーに次のように確認する:

#```
今回の差分は <N> ファイル / <+X> -<Y> 行と大規模です。
Codexのレビューには時間とトークンコストがかかります。

1. このまま全体をレビュー（推奨度：状況次第）
2. パスを絞ってレビュー（例: src/foo/ 配下のみ）
3. 中止
#```

「2」を選んだ場合、絞り込みパスを尋ねて以降の `git diff HEAD` を `git diff HEAD -- <paths...>` に置き換える。

### Step 2: レビュー対象差分のサマリをユーザーに提示

`git diff HEAD --stat` の結果を整形して提示し、レビュー開始の確認を取る:

#```
## Codex によるレビュー準備が整いました

- ブランチ: `<branch>`
- 対象: 未コミット変更（`git diff HEAD`）
- 規模: <N> ファイル / +<X> -<Y> 行
- モデル: gpt-5.5 (reasoning_effort=high, web_search=live, sandbox=read-only)

(--stat 出力)
<git diff --stat の結果>

このままレビューを依頼してよいですか?
#```

ユーザー OK で Step 3 へ。

### Step 3: Codex への一回限りの呼び出し

以下を **1コマンド** で実行する。出力ディレクトリ `.codex/` を作成し、`.gitignore` 未掲載なら追記提案する（自動追記はしない）。

#```bash
mkdir -p .codex
#```

#```bash
git diff HEAD | codex exec \
  --skip-git-repo-check \
  --ephemeral \
  -o .codex/review.md \
  --config model="gpt-5.5" \
  --config model_reasoning_effort="high" \
  --config sandbox_mode="read-only" \
  --config approval_policy="never" \
  --config web_search="live" \
  "$(cat <<'PROMPT'
You are a senior adversarial code reviewer with deep expertise in security, software architecture, and the broader engineering ecosystem. Your job is to review the git diff provided on STDIN as if you were the toughest reviewer the author has ever faced — while staying constructive and grounded in evidence.

# Scope
STDIN is the full output of `git diff HEAD` from the author's working tree — uncommitted changes about to be committed. Review ONLY what is in this diff. Do not propose changes outside the diff unless a change inside the diff strictly requires coordinated edits elsewhere; in that case, call it out explicitly.

# Review dimensions (apply all that are relevant)
1. Adversarial / correctness: hidden bugs, off-by-one, null/undefined/empty handling, race conditions, error paths, broken invariants, edge cases the author likely missed.
2. Security: OWASP-class issues (injection, XSS, SSRF, auth bypass, secrets in code, unsafe deserialization, prototype pollution, path traversal, supply chain risk), insecure defaults, missing input validation, weak crypto, unsafe regex, leaking sensitive data in logs. Use live web search to confirm CVE / advisory status when referencing a specific dependency or pattern.
3. Refactoring: poor abstractions, duplicated logic, oversized functions, naming, dead code, leaky interfaces — ONLY when the refactor target is in this diff. Do not propose codebase-wide refactors triggered by tangential observations.
4. Best practices: language/framework idioms, established patterns in this repository (infer from surrounding context in the diff hunks), test coverage gaps for changed behavior, observability/logging hygiene, documentation rot.

# Severity rubric
- Critical: must fix before merge. Security vulnerability, data loss risk, certain bug, broken contract.
- Major: should fix before merge. High likelihood of bug, significant maintainability/perf hit, missing essential validation.
- Minor: nice to fix. Code smell, naming, small inefficiency.
- Nit: cosmetic / style only.

# Output format (STRICT — a downstream parser depends on this)
Write the review as Markdown. The Summary text and each finding's values must be in JAPANESE. Keep the structural KEYS (file, line, category, severity, issue, rationale, suggestion) in English so the parser can locate them.

Use exactly this structure:

#```
# Codex Review Summary

<2-4 sentences in Japanese: overall impression, biggest concern, whether there are blockers>

# Findings

## 1. [Critical|Major|Minor|Nit] <short Japanese headline>
- file: `<path>`
- line: `<line or line-range, e.g. 42 or 88-95>`
- category: adversarial | security | refactor | best-practice
- severity: Critical | Major | Minor | Nit
- issue: <specific finding in Japanese>
- rationale: <why this is a problem in Japanese; cite CVE / RFC / docs URL inline when applicable>
- suggestion: <recommended fix in Japanese; include a code snippet when concise>

## 2. ...
#```

Number findings sequentially starting at 1. Order by severity (Critical → Major → Minor → Nit). If there are zero findings, output:

#```
# Codex Review Summary

<honest 2-3 sentence explanation in Japanese of why there is nothing to flag>

# Findings

(no findings)
#```

# Hard constraints
- You are in a read-only sandbox. Do NOT attempt to modify files. Produce only the review text.
- Do NOT invent file paths or line numbers. Quote them from the diff hunks you actually see.
- Do NOT pad with generic advice. Every finding must be grounded in a specific line of the diff.
- If a candidate finding turns out to be a false positive on closer reading, drop it. Quality over quantity.
- Use web search sparingly; cite the URL inline inside `rationale` when you do.
- Do not add sections beyond `# Codex Review Summary` and `# Findings`.
PROMPT
)"
#```

#### Codex 実行が失敗した場合

- 認証エラー（401 / unauthenticated 系） → 「`codex login` で認証してから再実行してください」と伝えて終了。
- ネットワークエラー → 1回だけ自動リトライしてよい。それでも失敗するならエラー内容をそのまま提示して終了。
- `.codex/review.md` が空 / セクション欠落 → Codex 出力をそのまま全文表示してユーザーに判断を委ねる（無理にパースしない）。

### Step 4: レビュー結果のパースと俯瞰提示

`.codex/review.md` を `Read` ツールで読み、以下をパースする:

- `# Codex Review Summary` セクション本文
- `# Findings` 配下の各 `## <N>. [Severity] <headline>` ブロック
- 各 finding の `file` / `line` / `category` / `severity` / `issue` / `rationale` / `suggestion`

`(no findings)` の場合は次のように出して終了:

#```
## Codex レビュー結果

<Summary 本文>

未解決の指摘はありません。コミットに進んで問題ありません。
コミットを分割整理したい場合は `/auto-commit` を使えます。
#```

指摘が1件以上ある場合は俯瞰テーブルで提示:

#```
## Codex レビュー結果

<Summary 本文>

### 指摘一覧（N件）

| # | 重大度 | カテゴリ | ファイル | 行 | 概要 |
|---|--------|---------|---------|-----|------|
| 1 | Critical | security | `src/api/auth.ts` | 42 | <headline> |
| 2 | Major | adversarial | `src/foo.ts` | 88-95 | <headline> |
| ... |

重大度の高いものから1件ずつ確認していきます。進めてよろしいですか?
#```

ユーザー OK で Step 5 へ。

### Step 5: 指摘1件ずつの対話処理ループ

`N` 件の finding を **Critical → Major → Minor → Nit の順** で、**1件ずつ** 処理する。複数件をまとめて処理しない。

#### 5-1. 該当コードと差分の読み込み

finding の `file` と `line` から、現在のファイル内容を `Read` ツールで読む。前後 10〜20 行のコンテキストを確保。あわせて、その指摘箇所が実際に `git diff HEAD` のどの hunk に属するかも確認する（必要なら `git diff HEAD -- <file>` を該当ファイルだけ実行）。

#### 5-2. 指摘とClaude評価をユーザーに提示

#```
## 指摘 i/N

**重大度**: <Critical|Major|Minor|Nit>
**カテゴリ**: <adversarial|security|refactor|best-practice>
**ファイル**: `<file>` の <line> 行目

### Codexの指摘
<issue（日本語、引用ブロック整形可）>

### 根拠
<rationale。URL があればリンク化>

### 該当箇所（現状）
#```<lang>
<file>:<startLine>-<endLine>
<前後コンテキスト込みのコード>
#```

### Codexの提案
<suggestion。短ければインラインdiff、長ければ要点列挙>

### Claudeの評価
<以下のいずれかの観点で、根拠付きで述べる:>
- **指摘は妥当**: <なぜ妥当か。提案された修正の妥当性も評価>
- **指摘は的外れ/不要**: <なぜ不要か。文脈・既存設計・他箇所での処理など>
- **判断保留**: <情報不足、設計判断が必要、副作用が大きいなど、ユーザー判断が必要な理由>

---

このコメントをどう扱いますか?
- **適用**: Codex（またはClaudeが微修正した）案を作業ツリーに反映
- **スキップ**: 何もせず次の指摘へ
- **さらに議論**: 修正方針を一緒に詰めたい / 別案を相談したい
#```

評価は **判断を押し付けない**。Codexの指摘でも、コードベース全体の文脈や既存の慣習を踏まえると不要なことはある。Claudeは「自分はこう見える」を根拠付きで提示するに留め、最終判断は必ずユーザーに委ねる。

#### 5-3. ユーザー判断に応じた処理

**「適用」と回答された場合:**

`Edit` ツールで対象ファイルを修正する。Codex の `suggestion` をそのまま採用するのが原則だが、Claude が読んだ現状コードと噛み合わない箇所（行番号ズレ、変数名差異等）は最小限の調整を加えてよい。複数ファイルにまたがる修正が必要なら、まず「この修正は `<他ファイル>` にも変更が必要です。一緒に反映してよいですか?」と確認する。

修正後の報告:

#```
✅ 適用しました
- `<file>` を修正
  - <変更概要(1行)>

次の指摘 (i+1/N) に進みます。
#```

**「スキップ」と回答された場合:**

#```
⏭ スキップしました。
理由をメモしておきたい場合はその旨を伝えてください（最終サマリに含めます）。
次の指摘 (i+1/N) に進みます。
#```

**「さらに議論」と回答された場合:**

フリーフォームの対話に入る。関連箇所の追加調査・別案の提示・Codex指摘の妥当性再評価などを行う。議論が収束したら「適用 / スキップ」のどちらかを再確認し、確定してから次の指摘へ進む。

#### 5-4. 中断時の挙動

ユーザーが途中で「ここで止めて」と伝えた場合は、その時点までの結果を Step 6 のサマリ形式で出力し、未処理は「未処理: <i>件」として残す。作業ツリーは「適用」したものだけが反映された状態のまま、何も巻き戻さない。

### Step 6: 全件処理後のサマリ

すべての指摘を処理（または中断）した後、以下を出力:

#```
## Codex レビュー対応 完了サマリ

ブランチ: `<branch>`
処理結果: 適用 P件 / スキップ Q件 / 議論後適用 R件 / 議論後スキップ S件 / 未処理 T件

### 適用した変更
- 指摘 1 (Critical/security): `src/api/auth.ts:42` — <変更概要>
- 指摘 3 (Major/adversarial): `src/foo.ts:88` — <変更概要>
- ...

### スキップした指摘
- 指摘 2 (Minor/refactor): `src/bar.ts:12` — <理由（ユーザーが述べた場合のみ）>
- ...

### 未処理（中断時のみ）
- 指摘 7〜N

### 作業ツリーの状態
<git status --short の結果>

### Codex生レビュー全文
`.codex/review.md` に保存されています（差分・指摘の追跡用）。
`.gitignore` に `.codex/` を追加することを推奨します。

### 次のアクション
- コミットを分割整理: `/auto-commit`
- PR作成: `/draft-pr`
#```

`git status --short` は実行して結果を埋め込む。

## エッジケース

- **Codex 出力がスキーマから外れた**: パースに失敗したら無理に構造化せず、`.codex/review.md` の全文をそのまま表示してユーザーに「このまま手動で扱いますか? / もう一度 Codex を呼び直しますか?」と確認する。再呼び出しはトークンを浪費するため、安易に自動再実行しない。

- **指摘が大量（20件超）**: 俯瞰提示時に「全件処理 / Critical & Major のみ / Critical のみ」を選べるようにする。ユーザーが絞り込みを選んだ場合、対象外の指摘は最終サマリで「未処理（重大度フィルタ）」として明示する。

- **同じ箇所への複数指摘**: 1件ずつ処理する原則は変えない。ただし2件目以降の提示時に「指摘 i では `<行X>` を <変更内容> に修正済みです。本指摘は同じ箇所への別観点です」と前置きを入れる。

- **Codex が差分外の修正を提案してきた**: そういう指摘は提示時に「Codexは差分外の `<file>` の修正も推奨しています」と明示。スコープを広げるか否かはユーザー判断に委ねる。

- **Codex が誤った行番号を返した**: パース時点で `Read` した実ファイルと突き合わせてズレを検出したら、提示時に「Codex指摘の行番号 <N> は現状ファイルでは <M> 付近に該当します」と注記して進む。

- **未コミット変更が staged と unstaged に分かれている**: `git diff HEAD` は両方を含むため通常は気にしない。ただしサマリに「うち staged: X ファイル / unstaged: Y ファイル」を補足してよい。

- **生成されたファイル（lockfile、ビルド成果物等）が差分に含まれる**: `git diff HEAD -- ':(exclude)package-lock.json' ':(exclude)yarn.lock' ':(exclude)pnpm-lock.yaml'` のような除外を Step 2 確認時にユーザーへ提案してよい。lockfile の差分まで Codex に読ませると S/N が悪化する。

- **秘密情報が差分に含まれている可能性**: `git diff HEAD | grep -E '(AKIA|api[_-]?key|secret|password|BEGIN .* PRIVATE KEY)'` を内部で確認し、ヒットがあれば Codex 呼び出し前にユーザーに警告する。Codex への送信前に該当箇所を取り除くか、ユーザー判断で続行するかを確認する。

- **Codex 認証が gpt-5.5 を解放していない**: `--config model="gpt-5.5"` で 400/403 が返る場合、`gpt-5` にフォールバックしてよい旨をユーザーに確認する。勝手にダウングレードしない。

## 振る舞いの原則

- **承認なしに作業ツリーを変更しない**: `Edit` での修正は必ずユーザーが「適用」を選んだ後のみ。Claude/Codex の評価が「妥当」でも勝手に反映しない。

- **コミット・pushはしない**: 本スキルは作業ツリーへの反映までを担当する。コミットは `/auto-commit`、push はユーザーの手動操作に委ねる。Codex対応・実装・リファクタを一括コミットして履歴が混ざるのを防ぐため。

- **判断を奪わない**: Claudeの評価はあくまで判断材料。「採用すべき」「不要」と断定的に誘導せず、根拠を述べたうえで「Claude はこう見ている」のトーンに留める。最終判断はユーザー。

- **Codex の指摘でも盲従しない**: 別モデルの視点は貴重だが、コードベースの文脈を踏まえない指摘・既存の慣習と矛盾する指摘も混ざる。提示時に Claude の独立評価を必ず添える。

- **一度きりのコマンド原則を崩さない**: `~/.codex/config.toml` や `--profile` に依存しない。本 skill だけで完結し、Codex CLI さえ入っていれば誰の環境でも同じ挙動になる。

- **コスト意識**: Codex の呼び出しは1回のレビューで1回のみ。再実行は明示的に「もう一度レビュー」と指示された場合だけ。`reasoning_effort=high` + `web_search=live` はそれなりに重いことを念頭に置く。

- **生レビュー全文を残す**: `.codex/review.md` は最終サマリ後も削除しない。後でユーザーが見直したり、PR 説明文に流用したりするため。

## 参考: なぜ Codex を別途使うのか

Claude Code が自分で書いたコードを Claude Code 自身に再レビューさせると、同じモデルゆえに同じ盲点を踏みやすい。OpenAI Codex（gpt-5.5）は別系統のモデルであり、特に以下で独立な視点を得やすい:

- セキュリティ（OpenAI 側の学習データ・ガイドラインの差分）
- ライブラリの最新動向（`web_search=live` で CVE / アドバイザリを都度取得）
- スタイル/慣習の偏り（Claude が好む書き方への過適合を相対化）

「Claude Code 実装 → Codex レビュー → ユーザー判断で反映 → コミット」というパイプラインが、本スキルが想定する標準フロー。
```

### このスキルの概要を簡潔に
・Claude Codeで実装した未コミットの変更に対するコードレビュー依頼専用のSkillです
・[敵対的レビュー/セキュリティチェック/リファクタリング/ベストプラクティス準拠]の観点からレビューします
・`--config`で設定を上書きすることで、Codexの設定ファイル（.codex/config.toml）に依存しないようにしてあります

### メインのコマンド部分

```
git diff HEAD | codex exec \
  --skip-git-repo-check \
  --ephemeral \
  -o .codex/review.md \
  --config model="gpt-5.5" \
  --config model_reasoning_effort="high" \
  --config sandbox_mode="read-only" \
  --config approval_policy="never" \
  --config web_search="live" \
  "$(cat <<'PROMPT'
```

`model="gpt-5.5"`: 使用モデル（最も優れたモデルを指定）
`model_reasoning_effort = "high"`: 推論強度(レスポンスが遅ければ"medium"も検討)
`sandbox_mode="read-only"`: AIに許可する操作内容とフォルダ範囲の設定（書き込み権限を渡さないことで、安心して`approval_policy="never"`が設定できる）
`approval_policy="never"`: 承認ポリシー（"never"にすることで、ユーザーによる確認をスキップする。`rm -rf`など暴走する可能性もあるため注意が必要）
`web_search="live"`: 任意のタイミングで最新情報の取得を許可する
（その他の設定はデフォルト値を使用）





# 使ってみた

まずはClaude Codeにリクエストをして実装させた後、先ほど作成したSkillを呼び出します。

![SCR-20260513-kxpm.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4345180/b07e7835-32b5-400c-a93c-0bbb2f89b887.png)


レビューの準備が整いました。


![SCR-20260513-kxwq.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4345180/18bff785-58a7-42b4-ac09-2e7a30fb6471.png)

Codexの進捗がリアルタイムで確認できます。
（今回の実装で変更が加えられた、`server.allowedHosts`周りのセキュリティベストプラクティスを`web search`で調べてくれているようです）

![SCR-20260513-kyvi.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4345180/eebcfbd9-13c2-45ae-884e-a510ea18acc5.png)


Codexによるレビューが完了しました。


![SCR-20260513-larf.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4345180/e77645d8-22e6-4427-816b-19f1dd014840.png)


![SCR-20260513-laub.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4345180/187d7de7-63d7-4776-b55e-2edca3c0e863.png)


今回の実装差分の中で指摘される可能性があるとしたらここだ！って箇所を見事に指摘してくれました。
少しでも参考になれば幸いです。
今回は以上になります。
