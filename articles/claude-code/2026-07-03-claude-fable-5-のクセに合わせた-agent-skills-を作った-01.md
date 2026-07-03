---
id: "2026-07-03-claude-fable-5-のクセに合わせた-agent-skills-を作った-01"
title: "Claude Fable 5 のクセに合わせた Agent Skills を作った"
url: "https://qiita.com/pani_py/items/d17b29898af7eeb62721"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "qiita"]
date_published: "2026-07-03"
date_collected: "2026-07-04"
summary_by: "auto-rss"
query: ""
---

## なぜ作ったか

### 公式が「旧スキルは Fable 5 の品質を下げうる」と言っている

きっかけは、公式プロンプティングガイド([Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5))の「Recommended scaffolding changes」にあるこの指摘です。

> **Refactor existing prompts and skills.** Skills developed for prior models are often too prescriptive for Claude Fable 5 and can degrade output quality. Review and consider removing older instructions if default performance is better.

*(訳)* **既存のプロンプトとスキルをリファクタリングする。** 旧モデル向けに開発されたスキルは Claude Fable 5 には過剰に規範的であることが多く、出力品質を劣化させうる。デフォルトの性能の方が良い場合は、古い指示の削除をレビュー・検討すること。

心当たりがある人は多いはずです。「必ずステップバイステップで考えてから」「まず計画を箇条書きにして」「〜を忘れずに」…。こういう指示は、指示追従が甘かった時代のモデルには効きましたが、指示忠実度が極端に高い Fable 5 相手だと全部が本気で実行されるため、簡単なタスクでも儀式的な手順が走ってしまいます。Sonnet / Opus 時代に育ててきたスキル資産は、そのままだと Fable 5 では負債になりうる。

### かといって「スキルなし」でもうまくいかない

じゃあスキルを全部消して素の Fable 5 に任せればいいかというと、そうでもありません。同じ公式ガイドが、Fable 5 特有の挙動をいくつも明記しています。高 effort だとルーチン作業でも考えすぎる、頼んでいない行動を取ることがある、長い自律実行の深部でツールを呼ばずに止まることがある、長時間セッションの報告が速記化する——どれも能力が高いからこそ出てくる過剰さで、旧スキルの「手取り足取り」では直らないし、むしろ悪化します。

必要なのは、公式が記述している Fable 5 の挙動を前提に「境界」だけを短く定義する新世代のスキルだと考え、ゼロから10個書き下ろしました。以下、**「公式ガイドはどう言っているか」→「それを受けてスキルは何をするか」**の順で紹介します。

## 10個のスキル

https://github.com/kpab/claude-fable-5-skills

### ① skill-refactorer — 旧スキル資産の棚卸し

**公式の記述:** 前掲のとおり、公式は旧モデル向けスキルのレビューと古い指示の削除検討を明示的に推奨しています。さらに削除すべき指示の具体例として、内部推論を応答に書き出させる類の指示が挙げられています。

> **Don't instruct Claude to reproduce its reasoning in the response.** Prompts, skills, or harness instructions that tell the model to echo, transcribe, or explain its internal reasoning as response text can trigger the `reasoning_extraction` refusal category on Claude Fable 5, causing elevated fallbacks to Claude Opus 4.8.

*(訳)* **Claude に推論内容を応答として再現させる指示を出さない。** 内部推論を応答テキストとして書き出す・転記する・説明するよう指示するプロンプトやスキル、ハーネス指示は、Claude Fable 5 で `reasoning_extraction` の拒否カテゴリを誘発し、Claude Opus 4.8 へのフォールバックを増加させうる。

**スキルがやること:** この移行作業そのものをスキル化しました。手持ちの旧スキルを Fable 5 に監査させ、「能力補償のための足場」(冗長な手順指示、過剰な注意書き、推論の書き出し指示)を削除し、「本物のガードレール」(セキュリティ境界、ビジネスルール、環境固有の制約)だけを残します。旧資産を全部手で書き直すのは非現実的なので、このスキル集の起点はここです。

### ② act-when-ready — 過剰プランニングの抑制

**公式の記述:** 高 effort 設定では、Fable 5 はルーチン作業でもタスクに必要な範囲を超えてコンテキスト収集と熟考を行うことがある、とされています。対策として公式が提示しているプロンプトがこれです。

> When you have enough information to act, act. Do not re-derive facts already established in the conversation, re-litigate a decision the user has already made, or narrate options you will not pursue in user-facing messages. If you are weighing a choice, give a recommendation, not an exhaustive survey. This does not apply to thinking blocks.

*(訳)* 行動に足る情報が揃ったら、行動せよ。会話内で既に確定した事実を再導出したり、ユーザーが決定済みの事項を蒸し返したり、実行しない選択肢をユーザー向けメッセージで語ったりしないこと。選択を迷う場合は、網羅的な調査ではなく推奨案を1つ出すこと。これは thinking ブロックには適用されない。

**スキルがやること:** この終了条件を常設のスキルにしたものです。「計画が行動を改善しなくなった時点で行動に移る」という判断閾値を与え、確定済み事実の再導出や、採用しない選択肢の比較表作成を明示的に禁止します。

### ③ effort-calibrator — effort 設定の選択(検証で1点修正あり)

**公式の記述:** Fable 5 向けの effort 推奨は、[Effort ドキュメント](https://platform.claude.com/docs/en/build-with-claude/effort)に明確に書かれています。

> Effort is the primary control for trading off intelligence, latency, and cost on Claude Fable 5. **Start with `high`, the default, for most tasks**, use `xhigh` for the most capability-sensitive workloads, and step down to `medium` or `low` for routine work. Lower effort settings on Claude Fable 5 still perform well and often exceed `xhigh` performance on prior models.

*(訳)* Fable 5 では effort が知能・レイテンシ・コストのトレードオフを制御する主要な手段である。**ほとんどのタスクはデフォルトの `high` から始め**、最も能力を要するワークロードには `xhigh` を、ルーチン作業には `medium` や `low` を使う。Fable 5 の低 effort 設定でも十分に性能が高く、旧モデルの `xhigh` を上回ることも多い。

**スキルがやること:** ワークロード種別ごとの effort 初期値の表と、上げ下げの判断シグナル、triage→escalate のパイプラインパターンを与えます。「とりあえず最大」をやめるだけでコストとレイテンシが大きく変わります。

**検証で見つけた誤記:** 当初スキルには「`xhigh` は Claude Code のデフォルト」という記述がありましたが、これは誤りでした。[Claude Code のモデル設定ドキュメント](https://code.claude.com/docs/en/model-config)にはこうあります。

> The default effort is `high` on Fable 5, Sonnet 5, Opus 4.8, Opus 4.6, and Sonnet 4.6, and `xhigh` on Opus 4.7.

*(訳)* デフォルトの effort は Fable 5・Sonnet 5・Opus 4.8・Opus 4.6・Sonnet 4.6 では `high`、Opus 4.7 では `xhigh` である。

「コーディングは `xhigh` から」は Opus 4.7/4.8 向けガイダンスの持ち越しでした。[移行ガイド](https://platform.claude.com/docs/en/about-claude/models/migration-guide)(Opus 4.8 → Fable 5)がこの世代差をそのまま説明しています。

> **Start at `high` effort:** The effort parameter default remains `high`. On Claude Opus 4.8, the recommendation for coding and high-autonomy work is to set `xhigh` explicitly. On `claude-fable-5`, use `high` as the default for most tasks and reserve `xhigh` for the most capability-sensitive workloads.

*(訳)* **`high` effort から始める:** effort パラメータのデフォルトは `high` のまま。Claude Opus 4.8 ではコーディングや高自律性の作業に `xhigh` を明示設定するのが推奨だったが、`claude-fable-5` ではほとんどのタスクでデフォルトの `high` を使い、`xhigh` は最も能力を要するワークロードのためにとっておく。

検証後にスキル本文と README(英・日)を修正済みです。旧モデルの知識で effort を運用している人は要注意のポイントだと思います。

### ④ no-gold-plating — 差分の最小化

**公式の記述:** 高 effort 時の「頼んでいない整頓・リファクタ」対策として、公式は非常に具体的なプロンプトを提示しています。

> Don't add features, refactor, or introduce abstractions beyond what the task requires. A bug fix doesn't need surrounding cleanup and a one-shot operation usually doesn't need a helper. Don't design for hypothetical future requirements: do the simplest thing that works well. Avoid premature abstraction and half-finished implementations. Don't add error handling, fallbacks, or validation for scenarios that cannot happen. Trust internal code and framework guarantees. Only validate at system boundaries (user input, external APIs). Don't use feature flags or backwards-compatibility shims when you can just change the code.

*(訳)* タスクが要求する範囲を超えて機能追加・リファクタリング・抽象化を導入しないこと。バグ修正に周辺の掃除は不要で、一度きりの操作にヘルパー関数はたいてい不要。仮想的な将来要件のために設計せず、うまく動く最もシンプルな実装を選ぶこと。早すぎる抽象化と作りかけの実装を避けること。起こりえないシナリオへのエラーハンドリング・フォールバック・バリデーションを追加しないこと。内部コードとフレームワークの保証を信頼すること。検証はシステム境界(ユーザー入力、外部 API)でのみ行うこと。コードを直接変更できるなら、フィーチャーフラグや後方互換シムを使わないこと。

**スキルがやること:** この公式プロンプトの各項目をルール化し、加えて diff 確定前のセルフチェック3問を課します。原則は「diff は依頼の大きさに比例すべき」。1行修正のついでの周辺リファクタや、起こりえないケースのエラーハンドリングをここで検出します。

### ⑤ grounded-progress — 進捗報告の証拠拘束

**公式の記述:** 長時間の自律実行では、実際のツール結果に照らして進捗を監査させよ、とされています。注目すべきは効果への言及です。

> On long autonomous runs, instruct Claude Fable 5 to audit progress against actual tool results. In Anthropic's testing, this nearly eliminated fabricated status reports even on tasks designed to elicit them:

*(訳)* 長時間の自律実行では、実際のツール結果に照らして進捗を監査するよう Claude Fable 5 に指示すること。Anthropic のテストでは、これにより捏造された進捗報告が——それを誘発するよう設計されたタスクでさえ——ほぼ根絶された。

公式が提示するプロンプトはこれです。

> Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for; if something is not yet verified, say so explicitly. Report outcomes faithfully: if tests fail, say so with the output; if a step was skipped, say that; when something is done and verified, state it plainly without hedging.

*(訳)* 進捗を報告する前に、各主張をこのセッションのツール結果に照らして監査すること。証拠を指し示せる作業だけを報告し、未検証のものは未検証と明言すること。結果は忠実に報告すること: テストが失敗したなら出力とともにそう言い、ステップを飛ばしたならそう言い、完了して検証済みのものはためらいなく明言する。

**スキルがやること:** 進捗報告の各主張を「このセッションのツール結果」に紐付けることを義務化します。完了なら証明するコマンド/テストを名指し、失敗なら出力をそのまま引用、未検証なら明示ラベル。証拠のない主張は出荷させません。「テスト通りました」(実行していない)対策です。

### ⑥ scope-guard — 頼まれていない行動の禁止

**公式の記述:** Fable 5 は時折、頼まれていない行動——依頼されていないメールの下書き、保険的な git ブランチのバックアップ作成など——を取ることがあるため、すべきこと/すべきでないことの明示的な制約を定義せよ、とされています。公式提示のプロンプトはこれです。

> When the user is describing a problem, asking a question, or thinking out loud rather than requesting a change, the deliverable is your assessment. Report your findings and stop. Don't apply a fix until they ask for one. Before running a command that changes system state (restarts, deletes, config edits), check that the evidence actually supports that specific action. A signal that pattern-matches to a known failure may have a different cause.

*(訳)* ユーザーが変更を依頼しているのではなく、問題を説明している・質問している・考えを声に出しているだけのときは、成果物はあなたの評価(アセスメント)である。所見を報告して止まること。求められるまで修正を適用しないこと。システム状態を変更するコマンド(再起動、削除、設定変更)を実行する前に、証拠がその特定のアクションを実際に裏付けているか確認すること。既知の障害にパターン一致するシグナルでも、原因は別のことがある。

**スキルがやること:** リクエストを「問題の記述/質問/思考の垂れ流し」と「明示的な変更依頼」に分類させ、前者では調査・報告・推奨で止まります。「診断して」と「直して」は別の依頼。状態変更コマンドの前には証拠の確認を要求し、パターンマッチだけの推測で破壊的操作をしないよう境界を引きます。

### ⑦ subagent-orchestration — 並列サブエージェントの活用

**公式の記述:** ここからは抑制系ではなく、Fable 5 の強みを引き出す側です。公式は Fable 5 の委譲能力の向上を明記しています。

> **Delegation and collaboration.** Claude Fable 5 is significantly more dependable at dispatching and sustaining parallel subagents, and reliably manages ongoing communication with long-running subagents and peer agents.

*(訳)* **委譲と協調。** Claude Fable 5 は並列サブエージェントの派遣と維持において著しく信頼性が高く、長時間稼働するサブエージェントや対等なエージェントとの継続的な連携を確実にこなす。

そのうえで、サブエージェントの積極活用・非同期協調・コンテキストを保持する長寿命サブエージェントを推奨し、検証の仕方についてはこう書いています。

> **Make self-verification explicit in long-run prompts.** Separate, fresh-context verifier subagents tend to outperform self-critique.

*(訳)* **長時間実行のプロンプトでは自己検証を明示すること。** 独立した、新鮮なコンテキストを持つ検証者サブエージェントは、自己批判(セルフクリティーク)を上回る傾向がある。

**スキルがやること:** 委譲の判断基準(独立性・規模・仕様化可能性)、同一ターンでの並列起動とノンブロッキング協調、長寿命ワーカーの使い方をパターン集として定義します。特に効くのが上記の fresh-context verifier パターンで、自分の作業を自分でレビューさせるより、コンテキストを持たない検証専用サブエージェントに見せた方がバイアスなく問題を見つけます。

### ⑧ markdown-memory — ファイルベースの教訓メモリ

**公式の記述:** メモリについて、公式ガイドはツール不要のミニマルな構成から勧めています。

> Claude Fable 5 performs particularly well when it can record lessons from previous runs and reference them. Provide a place to write notes, as simple as a Markdown file:

*(訳)* Claude Fable 5 は、過去の実行から得た教訓を記録して参照できるとき、とりわけ良い性能を発揮する。メモを書く場所を用意すること——Markdown ファイル1つで十分である。

運用ルールも具体的に提示されています。

> Store one lesson per file with a one-line summary at the top. Record corrections and confirmed approaches alike, including why they mattered. Don't save what the repo or chat history already records; update an existing note rather than creating a duplicate; delete notes that turn out to be wrong.

*(訳)* 1ファイルに1教訓を、冒頭に1行サマリを付けて保存すること。修正事項と確認済みアプローチの両方を、なぜ重要だったかも含めて記録すること。リポジトリやチャット履歴に既にある情報は保存しない。重複を作らず既存のノートを更新する。誤りと判明したノートは削除する。

**スキルがやること:** `memory/lessons/` に1教訓1ファイル + `INDEX.md` という構成で、この運用ルール(重複禁止・既知情報の記録禁止・誤った教訓の削除)と、過去セッションから教訓を掘り起こすブートストラップ手順をセットで課します。メモリは放っておくと腐るので、維持規律までがスキルの本体です。なお公式には API の [memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool) がありますが、このスキルはそれを使わないハーネスでも同じ効果を得るための実装、という位置づけです。

### ⑨ autonomous-continuation — 無人実行の完走

**公式の記述:** 長い自律実行に特有の失速モードが、公式に明記されています。

> Deep into a long session, Claude Fable 5 can occasionally end a turn with a text-only statement of intent ("I'll now run X") without issuing the corresponding tool call, or pause to ask permission when it already has enough to proceed.

*(訳)* 長いセッションの深部で、Claude Fable 5 は時折、対応するツール呼び出しを発行しないままテキストのみの意図表明(「これから X を実行します」)でターンを終えたり、続行に十分な情報があるのに許可を求めて停止したりすることがある。

対策として公式が提示する自律パイプライン向けシステムリマインダー(抜粋)がこれです。

> You are operating autonomously. The user is not watching in real time and cannot answer questions mid-task, so asking "Want me to…?" or "Shall I…?" will block the work. For reversible actions that follow from the original request, proceed without asking. (…) Before ending your turn, check your last paragraph. If it is a plan, an analysis, a question, a list of next steps, or a promise about work you have not done ("I'll…", "let me know when…"), do that work now with tool calls. End your turn only when the task is complete or you are blocked on input only the user can provide.

*(訳)* あなたは自律的に動作している。ユーザーはリアルタイムで見ておらず、タスクの途中で質問に答えられないため、「〜しましょうか?」と尋ねると作業がブロックされる。元のリクエストから導かれる可逆的なアクションは、確認せずに進めること。(…)ターンを終える前に最終段落を確認せよ。それが計画・分析・質問・次のステップのリスト・まだやっていない作業への約束(「これから〜します」「〜したら教えてください」)であるなら、今すぐツール呼び出しでその作業を行うこと。タスクが完了したか、ユーザーのみが提供できる入力でブロックされたときにのみターンを終えること。

また、ハーネスが残りトークンのカウントダウンを見せていると、新セッションの提案や作業の切り詰めが起きやすいことも記述されており、表示せざるを得ない場合の安心材料プロンプトも提示されています。

> You have ample context remaining. Do not stop, summarize, or suggest a new session on account of context limits. Continue the work.

*(訳)* コンテキストは十分に残っている。コンテキスト制限を理由に停止・要約・新セッションの提案をしないこと。作業を続けよ。

**スキルがやること:** 無人パイプライン向けの「自律性契約」(可逆なら進む。止まってよいのは破壊的操作・スコープ変更・ユーザーのみが持つ入力の3つ)と、上記の turn-ending check、context-budget composure を課します。

### ⑩ regrounding-summary — 読者を再接地させる最終報告

**公式の記述:** 長時間またはエージェント的な会話では、Fable 5 は追いにくいテキスト——矢印チェーンの速記、深すぎる実装詳細、ユーザーが見ていない思考への言及——を生成することがあるとされています。公式の処方箋(コミュニケーションスタイル補遺、抜粋)がこれです。

> Your final summary is different: it's for a reader who didn't see any of that. (…) Write it as a re-grounding, not a continuation of your working thread: the outcome first, then the one or two things you need from them, each explained as if new. The vocabulary you built up while working is yours, not theirs; leave it behind unless you re-introduce it. (…) Don't use arrow chains, hyphen-stacked compounds, or labels you made up earlier. When you mention files, commits, flags, or other identifiers, give each one its own plain-language clause. Open with the outcome: one sentence on what happened or what you found. (…) If you have to choose between short and clear, choose clear.

*(訳)* 最終サマリは別物である: それは作業の過程を一切見ていない読者のためのものだ。(…)作業スレッドの続きではなく「再接地(re-grounding)」として書くこと: まず結果、次に読者に必要な1〜2点を、それぞれ初出のものとして説明する。作業中に築いた語彙はあなたのものであって読者のものではない。再導入しない限り置いていくこと。(…)矢印チェーン、ハイフンで連結した複合語、自分が途中で作ったラベルを使わないこと。ファイル・コミット・フラグなどの識別子に言及するときは、それぞれに平易な説明句を付けること。結果から始めよ: 何が起きたか・何が分かったかを1文で。(…)短さと明瞭さのどちらかを選ぶなら、明瞭さを選べ。

「短くする方法」についても明確です。

> The way to keep output short is to be selective about what you include (drop details that don't change what the reader would do next), not to compress the writing into fragments, abbreviations, arrow chains like A → B → fails, or jargon.

*(訳)* 出力を短く保つ方法は、含める内容を取捨選択すること(読者の次の行動を変えない詳細を落とすこと)であって、文章を断片・略語・「A → B → fails」のような矢印チェーン・専門用語に圧縮することではない。

**スキルがやること:** 「作業を一切見ていない読者が読んで理解できるか」を報告の合格基準にし、結論から始める・完全な文で書く・矢印チェーンと自作略語を禁止・識別子には平易な説明句を付ける・圧縮ではなく取捨選択で短くする、というルール群を課します。数時間の自律実行も、締めの報告が解読できないと結局こちらがログを掘り直すはめになるので、ここはケチらない方がいいです。

## 設計原則: なぜこう書いたか

10個に共通する書き方のルールを4つ決めていました。

1. **手順ではなく意図を書く。** Fable 5 は指示忠実度が高いので、ステップバイステップのレシピを書くとその通りにしか動きません。「達成すべき結果」と「越えてはいけない境界」だけ書いて、経路はモデルに任せる
2. **構造的に短く。** 全スキルが1画面に収まる分量。挙動を変えない行は削除。Fable 5 の場合は全行が律儀に実行されるので、無駄な1行がそのまま無駄な挙動になります
3. **検証フックで縛る。**「注意深くやってください」とは書かない。代わりに証拠ルール(⑤)、ターン終了チェック(⑨)、diff セルフチェック(④)のような、機械的に判定できるチェックを定義する
4. **全文書き下ろし。** 本記事で見てきたとおり各スキルの趣旨は公式記述と対応させていますが、指示文はすべてオリジナルで書いており、丸写しはしていません

## 検証記録について

本記事の引用は、公開後に行った公式ドキュメント突き合わせ検証の記録から取っています。10スキル全件について「スキルがどう働くか → 公式原文 → 日本語訳」を記録し、全文公開しています。採用判断の材料にどうぞ。

https://github.com/kpab/claude-fable-5-skills/blob/main/docs/official-verification.ja.md

## インストール

Claude Code ならプラグインが楽です(アップデートも追従):

```
/plugin marketplace add kpab/claude-fable-5-skills
/plugin install fable5-skills@claude-fable-5-skills
```

手動なら、使いたいスキルのフォルダをコピーするだけ:

```bash
git clone https://github.com/kpab/claude-fable-5-skills
cp -r claude-fable-5-skills/skills/act-when-ready ~/.claude/skills/
```

プロジェクト単位なら `.claude/skills/` 配下に置く形でも OK。各スキルは `SKILL.md` 1枚の自己完結フォルダなので、Cursor や Copilot などでは `skills/` ディレクトリをスキルローダーに向けてください。全部入れる必要はなく、刺さった問題のスキルだけ入れるのを推奨します。

## おわりに

Fable 5 を実際に触れた時間はコミュニティ全体でもまだ短く、みんなでモデルのクセを学んでいる最中です。このスキル集も動く標的を追いかけている状態なので、再現可能な before/after 付きの Issue / PR は大歓迎です。

なお、本プロジェクトは非公式のコミュニティプロジェクトであり、Anthropic とは無関係です。本記事の引用は執筆時点(2026-07-03)の公式ドキュメントに基づき、訳はすべて拙訳です。API パラメータ等は本番投入前に[公式ドキュメント](https://platform.claude.com/docs)で最新情報を確認してください。

## 参照元

1. [Prompting Claude Fable 5 — Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5) — スキル ①②④〜⑩ の引用元
2. [Effort — Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/effort) — スキル ③
3. [Model configuration — Claude Code Docs](https://code.claude.com/docs/en/model-config) — スキル ③(Claude Code のデフォルト effort)
4. [Migration guide — Claude Platform Docs](https://platform.claude.com/docs/en/about-claude/models/migration-guide) — スキル ③(Opus 4.8 → Fable 5 の effort 再評価)
5. 検証記録(全引用の照合記録): https://github.com/kpab/claude-fable-5-skills/blob/main/docs/official-verification.ja.md

### リンク

- リポジトリ: https://github.com/kpab/claude-fable-5-skills
