---
id: "2026-06-19-aiエージェント時代こそ守りたい規律-agentsmdと-docs実装ログでトレーサビリティを取る-01"
title: "AIエージェント時代こそ守りたい規律 — AGENTS.mdと_docs実装ログでトレーサビリティを取る"
url: "https://zenn.dev/zapabob/articles/agents-md-docs-traceability-milspec"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "API", "AI-agent"]
date_published: "2026-06-19"
date_collected: "2026-06-20"
summary_by: "auto-rss"
query: ""
---

エージェントにコードを書かせると、速い。速いからこそ、あとから「なぜこうなったか」が消える。

人間が書いていた時代は、PR 説明とコミットメッセージだけでなんとか追えた。今は、同じタスクを Cursor、Codex、Claude Code が分担し、チャットは消え、コンテキストは切り替わる。**規律をファイルに固定しないと、品質も履歴も一緒に流れていく。**

この記事では、軍用規格（MILSPEC）から **転用できる考え方** と、ソフトウェア工学の定番、そして自分が実際に使っている **`AGENTS.md`（`CLAUDE.md`）+ `_docs/` 実装ログ** の三層について書く。目的は一つ、**手戻りを減らすトレーサビリティ** だ。

前回の [AGENTS.md に SOP を symlink する話](https://zenn.dev/zapabob/articles/agents-md-sop-design-symlink) が「どこに何を書くか」なら、今回は「エージェント時代に何を崩さないか」と「実装のあとをどう残すか」に寄せる。

## エージェント時代に緩むもの

現場でよく見る退化パターンがある。

* **曖昧な完了条件** — 「いい感じに直して」で merge される
* **検証の省略** — エージェントが「動くはず」と言っただけで test を走らせない
* **スコープの膨張** — 依頼は1行なのに、無関係なリファクタが混ざる
* **秘密の混入** — `.env` や個人パスが diff に紛れ込む
* **判断の根拠が消える** — なぜ A 案でなく B 案か、チャット外に残らない

どれも「人間がサボった」というより、**ツールが速すぎて、記録の習慣が追いついていない** ことが多い。だから規律は、人間への説教ではなく **リポジトリの仕組み** に落とす方が効く。

## MILSPEC をそのまま持ち込まない

まず誤解を避けたい。MILSPEC（米軍仕様）をアプリ開発に丸ごと適用する必要はない。書類地獄になり、エージェントの速度メリットを殺す。

取り込むのは **要求・検証・追跡** の骨格だけだ。

| MILSPEC 由来の考え | エージェント向けの言い換え | 置き場所 |
| --- | --- | --- |
| 要求の明示 | 曖昧語禁止、Done はコマンドで閉じる | `AGENTS.md` の Rules / Done |
| 検証 | test / lint / typecheck を必須化 | `AGENTS.md` の Commands |
| 追跡可能性 | 誰が・いつ・何を・なぜ | `_docs/` 実装ログ + git |
| 変更管理 | 小さな PR、レビュー可能な diff | SOP + CI |
| インタフェース分離 | UI と API の規約を分離 | `DESIGN.md` / SOP |

ISO/IEC 12207 や Definition of Done と同じ家族だ。MILSPEC は **比喩としての背骨** であり、認証取得の目的ではない。

## ソフトウェア工学 — エージェントに任せても崩さない線

エージェントは実装は得意だが、**境界と検証** は人間が設計する部分が残る。ここだけは短く列挙する。詳細は各言語の SOP に逃がす。

**変更容易性**

* 1変更1理由。依頼外の「ついで」を禁止する（`AGENTS.md` の Rules）
* 既存の命名・ディレクトリ規約に合わせる。エージェント独自の抽象化を増やさない

**検証可能性**

* Done は「完了した気がする」ではなく **コマンドが通る** 状態で書く
* CI があれば、ローカル Commands と CI を一致させる

**セキュリティ**

* secrets は repo に入れない。エージェント向けに「コミットしてはいけないパス」を列挙する
* 破壊的操作（本番 deploy、force push）は AGENTS.md で明示的に禁止

**可観測性**

* 実装ログに仮説と結果を残す（後述）。「試してダメだった」も資産になる

**トレーサビリティ**

* 要求 → 実装 → 検証 → ログ、が一本の線で辿れること

エージェントに「ベストプラクティスに従え」とだけ言っても散漫になる。**Commands / Rules / Done に分解して書く** のが、AGENTS.md の存在理由だ。

## 二層の憲法 — AGENTS.md と CLAUDE.md

[Codex](https://developers.openai.com/codex) はリポジトリルートの `AGENTS.md` を読む。[Claude Code](https://docs.anthropic.com/en/docs/claude-code) は `CLAUDE.md`（または `AGENTS.md`）を読む。Cursor も同系のプロジェクトルールを持つ。

役割分担はこう整理している。

| 層 | 典型パス | 内容 | コミット |
| --- | --- | --- | --- |
| 個人憲法 | `~/.codex/AGENTS.md` | 文体、MCP 方針、工学規律の上位原則 | しない |
| プロジェクト憲法 | `./AGENTS.md` / `./CLAUDE.md` | Commands, Rules, Done, CI 要点 | する |
| 詳細手順 | `docs/sop/*.md` | PR、言語別規約、レビュー | する |
| UI 規約 | `docs/design/DESIGN.md` | コンポーネント、トークン | する |

**AGENTS.md は短く。** 32 KiB 上限や毎ターン読み込みを意識し、詳細は SOP へリンクする。エージェントが毎回読むのは要約、人間が深掘りするのは SOP、という分業だ。

グローバル側の先頭1行例:

```
AGENTS.md / CLAUDE.md は SOP、MILSPEC 由来の規律、ソフトウェア工学のベストプラクティスに従うこと。
```

リポジトリ側では、実装ログのルールも明示する（[本 repo の AGENTS.md](https://github.com/zapabob/codex-zenn-starter/blob/main/AGENTS.md) より）:

```
## Rules
- Implementation logs go to `_docs/`; not part of published reader content.
- After substantive agent work, add `_docs/yyyy-mm-dd_{summary}{agent-or-branch}.md`.
```

`{agent-or-branch}` には `main`、`codex`、`cursor`、`claude` など、**誰（何）が実装したか** を入れる。ブランチ名でもよい。後から「この変更、どのセッション由来か」を grep できる。

## 独自の第三層 — `_docs/` 実装ログ

ここが本記事の提案の芯だ。

**`_docs/` は、エージェント作業の飛行記録（flight recorder）** だ。読者向け記事（`articles/`）でも製品 README でもない。チーム内のトレーサビリティと手戻り防止用。

### ファイル名規約

```
_docs/yyyy-mm-dd_{実装内容の短い要約}{実装AIまたはブランチ}.md
```

例（実際にこの repo で使っているもの）:

```
_docs/2026-06-17_Codex-CI-ChatGPT認証{main}.md
_docs/2026-06-18_Hermes比較記事{main}.md
_docs/2026-06-17_システムプロンプト解剖記事{main}.md
```

| 部分 | 意味 |
| --- | --- |
| `yyyy-mm-dd` | 作業完了日（UTC かローカルかはチームで統一） |
| `{実装内容}` | 日本語可。grep しやすい短い名詞句 |
| `{実装AI}` | `main` / `codex` / `cursor` / `claude` / feature ブランチ名 |

波括弧 `{}` は **識別子の区切り** として使っている。ファイルシステム上はそのまま `{}` を含めてよい（Windows も可）。「どこまでが内容でどこからが実装者か」が一目で分かる。

### 中身のテンプレート

長文不要。次の見出しだけで十分回る。

```
# yyyy-mm-dd {タイトル} {agent}

**完了:** ISO-8601 またはローカル時刻
**ブランチ / PR:** （あれば）

## ユーザー要望
（1段落）

## 仮説 → 検証
| # | 仮説 | 結果 |
|---|------|------|
| 1 | ... | ✅ / ❌ / 🔄 |

## 実装内容
- 変更ファイルと要点（箇条書き）

## 検証
- 実行したコマンドと結果

## 手戻りメモ / 次
- 次のセッションが読むべき注意
```

**仮説 → 検証** の表が効く。エージェントは試行錯誤が速いので、「ダメだった道」がチャットに埋もれがちだ。表に残すと、同じ失敗を別モデルが繰り返しにくい。

### AGENTS.md との関係

```
AGENTS.md     … これからどう動くか（規範）
_docs/*.md    … さっき何をしたか（記録）
git log       … 公式な変更履歴
```

三者は競合しない。AGENTS.md に過去の長い経緯を書かない。`_docs` に書いて、AGENTS.md からは「実装後は `_docs` に log を残せ」と一行参照するだけでよい。

起動時（新しいエージェントセッション）に `_docs` を読ませるかは任意だが、**同じ repo の続き作業** では `_docs` の最新数件を読むルールをグローバル AGENTS.md に入れておくと、手戻りが減る。

## なぜ git だけでは足りないか

コミットメッセージは公式履歴として必要だが、足りないことがある。

* **試行錯誤の過程** — revert 前の仮説は commit に残らない
* **CI の run ID や secret 名** — 本文に書きにくい
* **ユーザー要望の原文** — チケットが無い個人 repo では消える
* **モデル差** — 同じ diff でも Codex と Claude で前提が違う

`_docs` は **コミットと1対1でなくてよい**。1作業1ファイル、完了時に追加、でよい。後から `git blame` と `_docs` を突き合わせれば、変更理由の解像度が上がる。

## 手戻りが減る具体例

**ケース1: CI 認証の切り替え**

ChatGPT 認証（`CODEX_AUTH_JSON`）への移行では、`GITHUB_OUTPUT` の NUL 問題、sandbox の network 設定、`--base` と prompt の競合など、複数の仮説があった。ログ [`2026-06-17_Codex-CI-ChatGPT認証{main}.md`](https://github.com/zapabob/codex-zenn-starter/blob/main/_docs/2026-06-17_Codex-CI-ChatGPT%E8%AA%8D%E8%A8%BC%7Bmain%7D.md) に表形式で残している。三ヶ月後に workflow を触るとき、チャットはもう無いが log はある。

**ケース2: 執筆・記事**

Zenn 本の章執筆も `_docs/2026-06-17_章2-5執筆{main}.md` のように区切った。どの章をどの順で仕上げたか、次のセッションが迷わない。

**ケース3: fork 比較**

Hermes 本家と fork の差分調査は、README と compare API の数字を log に残した。記事本文は読者向けに磨き、**調査メモは `_docs` に隔離** した。

## エージェントへの指示例（コピー可）

リポジトリ `AGENTS.md` に足す一行:

```
- Substantive agent sessions: append `_docs/yyyy-mm-dd_{topic}{codex|cursor|claude|branch}.md` with 要望 / 仮説検証 / 変更 / 検証コマンド / 次アクション.
```

グローバル `~/.codex/AGENTS.md` に足す一行:

```
- On session start for continuing work, read latest 3 files in `_docs/` if present.
- MILSPEC-style: explicit requirements, verifiable Done, no secrets in repo, minimal diff scope.
```

## チーム展開するとき

個人 repo からチームへ広げる場合の現実的ライン:

| 項目 | 推奨 |
| --- | --- |
| `_docs/` | コミットする（private repo ならそのまま） |
| 個人パス・secret | log にも書かない |
| 公開 OSS | `_docs` は開発者向けと明記。必要なら `.gitignore` ではなく README で説明 |
| レビュー | PR に `_docs` 追加を含めてよい。差分は通常小さい |

`_docs` を「第二の README にしない」こと。テンプレに沿った短い log の方が、長期的に検索可能だ。

## Codex 本・他記事との位置づけ

エージェントコーディングは、**速度と規律の両立** が勝負だ。速度だけ取ると、のちの自分が必ず払う。規律は AGENTS.md に、記録は `_docs` に、検証は Commands に分ければ、エージェントは速いままでも、プロジェクトは荒れにくい。

## おわりに

MILSPEC を崇拝する必要はない。ただ、**明示・検証・追跡** という三つは、チャットが消える時代ほど価値が上がる。

`AGENTS.md` / `CLAUDE.md` で「これからどう動くか」を固定し、`_docs/yyyy-mm-dd_{内容}{AI}.md` で「何をしたか」を残す。シンプルだが、これだけで **実装の手戻り** は目に見えて減る。

次にエージェントに大きなタスクを渡す前に、Done の一行と、log ファイル名の一行だけ、先に決めてみてほしい。あとの会話が、驚くほど短くなる。
