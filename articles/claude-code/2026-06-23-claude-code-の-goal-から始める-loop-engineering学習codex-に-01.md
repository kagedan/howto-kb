---
id: "2026-06-23-claude-code-の-goal-から始める-loop-engineering学習codex-に-01"
title: "Claude Code の `/goal` から始める Loop Engineering学習。Codex に許可されるまで止まらないループを作ってみた"
url: "https://qiita.com/Ryotaro-namaketAI/items/2cd6bc161b437f621c21"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "prompt-engineering", "API", "AI-agent", "OpenAI"]
date_published: "2026-06-23"
date_collected: "2026-06-24"
summary_by: "auto-rss"
query: ""
---

## やったこと

Claude Code の `/goal` と、Codex プラグインの `/codex:review` を組み合わせて、**「Codex が approve するまでセッションが終わらない自走ループ」** を運用に乗せました。

合わせて、新規プロジェクトに入った最初の1コマンドで全部の初期化が済むように `/loop:init` という自作スラッシュコマンドを書きました。

```
/loop:init

↓ ゲートON + .agent/* + .gitignore + progress.md

/goal "<検証可能な条件>"

↓ Claude が編集 → 終了しようとした瞬間に Codex が ALLOW/BLOCK 判定

↓ BLOCK ならもう一周、ALLOW なら完了
```

この記事は、その過程で整理した「`/goal` って結局なに?」「Loop Engineering流行ってるけど結局なに?」「なんで `/loop:init` を自作したのか」を、普段から Claude Code を使っているけど一段上に行きたい人向けに書いたものです。

## 想定読者

こちらの記事は

- Claude Code は毎日触ってる
- `/rewind` `/resume`,  など、組み込みのコマンドあたりは使いこなしている
- カスタムスラッシュコマンドも1-2個作ったことがある
- skillの自作をしている

そんな方を想定しています。

## 1. そもそも `/goal` ってなに?

`/goal` は Claude Code のビルトインスキルのひとつで、こう動きます。

```
/goal "<達成条件を1文で>"
```

これを打つと、その条件を満たすまで **セッションが終了しなくなります**。
Claude が「完了しました」と返事しようとした瞬間に、Stop hook が直前のターンを採点して、条件を満たしていなければセッション継続を強制する仕組みです。

ベースにあるのは、いまコミュニティで急速に広がっている **Loop Engineering** という考え方です。

### Prompt → Context → Harness → Loop

2022年から2026年の今までに、エンジニアリングの関心は層を変えてきました。

| 世代 | 関心の対象 |
|------|----------|
| Prompt Engineering (2022–2024) | 言葉遣い・指示の表現 |
| Context Engineering (2025) | 推論時に「見えている」情報の集合 |
| Harness Engineering (2026前半) | ツール、権限、メモリ、評価の足場 |
| Loop Engineering (2026年6月〜) | 反復サイクル・検証・終了条件の設計 |

並べると分かりやすいのですが、これは**置き換えではなく入れ子**です。
良いループは良いハーネスの上で動き、良いハーネスは良いコンテキスト管理を含み、
各ステップでは良いプロンプトを使う。

Loop Engineering という名前が定着したきっかけは、2026年6月初旬にあった2つの発言です。

ひとつは Peter Steinberger(`@steipete`, OpenClaw)の X 投稿(2026年6月8日)で、
これが 650万ビューに到達して議論が広がりました。

> Here's your monthly reminder that you shouldn't be prompting coding agents anymore. You should be designing loops that prompt your agents.
> (もうコーディングエージェントにプロンプトを打つのはやめろ。エージェントにプロンプトを打つループを設計しろ)
>
> — [Peter Steinberger, via Digg / The New Stack](https://thenewstack.io/loop-engineering/)

もうひとつは Anthropic の Boris Cherny(Claude Code を作った人)が登壇で言った発言です。

> I don't prompt Claude anymore. I have loops running that prompt Claude and figuring out what to do.
> (もう Claude にプロンプトを打っていない。Claude にプロンプトを打って次の手を決めるループを走らせている)
>
> — [Boris Cherny, Anthropic, via Explainx.ai](https://explainx.ai/blog/anthropic-engineer-loops-prompts-ai-coding-harness-engineering-2026)

そして翌日、Google の Addy Osmani が essay として体系化し、"Loop Engineering" という名前を与えました([Loop Engineering — addyosmani.com, 2026-06-07](https://addyosmani.com/blog/loop-engineering/))。
Osmani は essay の冒頭でこう書いています。

> Loop engineering is replacing yourself as the person who prompts the agent. You design the system that does it instead.
> (ループエンジニアリングは、エージェントにプロンプトを打つ人を自分から置き換えることだ。代わりにそれをやるシステムを設計する)

`/goal` は、この流れが Claude Code 本体にネイティブ実装されたもの。
という位置づけです。

## 2. ループの中身 — Perceive → Plan → Act → Observe

`/goal` が回しているループの中身を分解すると、こうなります。

```
1. Perceive  : コードベース・テスト結果・エラーログを観測
2. Reason    : 現状理解、必要情報の特定
3. Plan      : 次の一手を決定
4. Act       : ファイル編集・コマンド実行
5. Observe   : 結果を取り込み、ゴール達成を判定
                ↓ 未達 → 次イテレーション
```

この型自体は2022年の **ReAct 論文**(Yao et al.)が元で、AutoGPT → Reflexion → Plan-and-Execute → Ralph Loop と発展してきました。

Loop Engineering でやるのは、このサイクルの各段を「設計」することです。
何を観測させるか、何を検証器にするか、いつ止めるか、コストの上限はどこかなどですね。

### `/goal` を設計するときに毎回考える5つ

実際に `/goal` を打つときは、頭の中で次の5つを埋めています。

1. **Verifiable Goal**: 達成を機械が判定できる1文になっているか
2. **Tool Set**: ファイル/シェル/テストは揃っているか
3. **Context Management**: 圧縮・剪定・外部化のどれを使うか
4. **Termination**: success / failure / budget の3層を区別できるか
5. **Independent Reviewer**: 自己採点に依存していないか

この5つ目が、今回の記事のキモです。

## 3. `/goal` をそのまま使うと困ること

`/goal` は便利なんですが、デフォルトのまま使うと**自己採点の罠**にハマります。

Claude が自分のターンを見て「ゴール達成しました」と判定して、Stop hook の評価エージェントも同じ Claude 系列で「承認」を出すと、両者が結託してハルシネート完了します。Loop Engineering の界隈では `hallucinated success` と呼ばれている、ループ運用でいちばんよく踏まれる失敗モードです。

Tosea.ai の Loop Engineering ガイドはこれをこう定義しています。

> Hallucinated success. The agent reports "done" without real verification. Fix: trust a deterministic verifier, never the agent's self-report.
> (エージェントが本当の検証なしに「完了」と報告する。対処は決定論的検証器を信用し、エージェントの自己申告は決して信用しないこと)
>
> — [What Is Loop Engineering? — Tosea.ai](https://tosea.ai/blog/loop-engineering-ai-agents-complete-guide-2026)

具体例を挙げると、僕が踏んだことのあるパターンだけでも、

- テストを書く前に「実装完了」と言って止まる
- 失敗していたテストを「コメントアウトすれば緑」と理解して通す
- README に「実装済み」と書いて成果物のフリをする

これは Claude が悪いというより、**検証器と実装者が同じだとそうなる**という構造の問題です。Addy Osmani の essay も同じことを別の角度で言っています。

> A loop running unattended is also a loop making mistakes unattended. The faster the loop ships code you did not write, the bigger the gap between what exists and what you actually get.
> (放置されたループは、放置されたままミスを犯すループでもある。書いていないコードをループが速く出力すればするほど、存在するものと実際に得たものの間のギャップが大きくなる)
>
> — [Addy Osmani, "Loop Engineering"](https://addyosmani.com/blog/loop-engineering/)

### Reward Hacking — テストを削除して CI を緑にする問題

実装エージェントに検証も任せると、最短経路は「検証器を甘くする」になります。
ClaudeCodeで作成したプロダクトをClaudeにレビューさせると問題なくても、codex:reviewだといくつか穴が出てる！というケースが近いです。

## 4. 解決策 — Codex を Independent Reviewer にする

幸い、Claude Code には公式の **Codex プラグイン**(`openai-codex/codex`)があります。これがそのまま、Loop Engineering の Verifier 層として機能するように設計されています。

### Codex プラグインで使うコマンド

```bash
/codex:review --wait --scope working-tree
/codex:adversarial-review --wait
/codex:setup --enable-review-gate
/codex:status
```

ポイントは3つあります。

**1. 異モデル系列**

Codex は OpenAI 側のモデル(`gpt-5.3-codex`, `gpt-5.5` など)で動いています。
Claude が見落とした設計判断や、自己肯定で素通しした品質劣化を別系列の目で再評価できます。

**2. 構造化スキーマで返ってくる**

`schemas/review-output.schema.json` を見ると、こんな形式です。

```json
{
  "verdict": "approve" | "needs-attention",
  "findings": [
    {
      "severity": "critical" | "high" | "medium" | "low",
      "title": "...",
      "file": "src/auth/login.py",
      "line_start": 42,
      "line_end": 58,
      "confidence": 0.85,
      "recommendation": "..."
    }
  ],
  "next_steps": [...]
}
```

`verdict` と `severity` が機械可読なので、ループの分岐条件にそのまま使えます。

**3. Stop hook 統合**

これが一番強力です。`hooks/hooks.json` で `Stop` イベントに `stop-review-gate-hook.mjs` が登録されていて、Claude がセッション終了しようとした瞬間に Codex が直前ターンの git diff を見て採点します。

- `ALLOW: <理由>` → セッション通常終了
- `BLOCK: <理由>` → セッション続行 = Claude にもう一周させる

つまり、`/codex:setup --enable-review-gate` を有効化したプロジェクトでは、**Codex が承認しない限りセッションが物理的に終わらない**状態になります。

これが Loop Engineering の Verifier 層として、本当によくできていると思った理由です。

## 5. 課金まわり(気になる人向け)

ループはサブスクリプションとは別の料金形態なのでは？
と聞かれそうなので先に書いておきます。

- **`/goal`**: Claude Code 組み込み。追加課金なし。Claude Pro / Max のサブスクか API キーで動く
- **`/codex:review`**: 2026年4月以降、**ChatGPT の全プラン**(Free / Go / Plus / Pro / Business / Enterprise)に Codex 利用が含まれている。`codex login` でChatGPT アカウントログインするだけで使える
- もしくは OpenAI API キー認証(従量課金)

つまり、すでに ChatGPT を使っていれば追加で何も払わずに `/codex:review` をループの Verifier にできます。

注意点として、Codex CLI は Codex Web / IDE と **5時間ウィンドウのレート制限を共有**します。CLI で重く回すと Web 側のクォータも食う、というのは覚えておいてください。

## 6. なぜ `/loop:init` を自作したのか

ここからが本題のひとつです。

Codex の Stop ゲート(`stopReviewGate`)は **プロジェクト単位**で保存される仕様になっています。実装を確認すると、

```js
// scripts/codex-companion.mjs
if (options["enable-review-gate"]) {
  setConfig(workspaceRoot, "stopReviewGate", true);
  //         ^^^^^^^^^^^^^^^ 必ず workspaceRoot 単位
}
```

設定の保存先も `~/.claude/plugins/data/codex-openai-codex/state/<workspace-hash>/state.json` で、ワークスペースごとに別ファイルです。

**グローバルデフォルト ON は公式にはサポートされていません**。
新規プロジェクトに入るたびに `/codex:setup --enable-review-gate` を手で打つ必要があります。

これが少々面倒です。
元に記事を書いている僕ですら「あのコマンドなんだっけ」と毎回調べにいくレベルです。

加えて、Loop Engineering を実用に乗せるには、ゲートON だけじゃなく:

- `.agent/CLAUDE.md`(プロジェクト固有の system prompt)
- `.agent/AGENTS.md`(役割定義)
- `.agent/HARNESS.md`(ツール許可)
- `.agent/FEATURE_INTAKE.md`(タスク取り込みテンプレ)
- `.claude/progress.md`(イテレーション間で残す進捗ログ)
- `.gitignore` に Loop 関連の一時ファイルを追記

このあたりを毎回手で揃えるのは、結局やらなくなる未来しか見えません。

なので、これらを何度実行しても安全に、もれなく1コマンドで済ませる `/loop:init` を作りました。

## 7. `/loop:init` の中身

`~/.claude/commands/loop/init.md` に置いたファイルです。Claude Code のスラッシュコマンドは、`~/.claude/commands/<dir>/<name>.md` に置けば全プロジェクトから `/dir:name` で呼べる、というだけのシンプルな仕組みです。

中身は次のような構成になっています。

```markdown
---
description: "Loop Engineering: 新規プロジェクトの初期化"
allowed-tools: ["Bash(mkdir:*)", "Bash(touch:*)", "Bash(test:*)",
                "Bash(grep:*)", "Bash(echo:*)", "Bash(cat:*)",
                "Bash(ls:*)", "Read"]
---

# Loop Engineering 初期化

## 手順

### 1. Codex Stop ゲートを ON
`/codex:setup --enable-review-gate` を実行する。

### 2. ディレクトリスケルトンを作成
mkdir -p .agent .claude

### 3. .agent/ 配下のファイルを「無ければ作る」
- .agent/CLAUDE.md
- .agent/AGENTS.md
- .agent/HARNESS.md
- .agent/FEATURE_INTAKE.md

### 4. .gitignore に Loop の一時ファイルを追記(重複追記しない)

### 5. .claude/progress.md を初期化(無いときだけ)

### 6. 完了報告
```

ポイントを3つ書いておきます。

**1. 全部「無ければ作る」にする**

`test -f` で存在チェックしてから `cat > ... <<'EOF'` で書き込む。
既存のファイルは絶対に触りません。これを徹底しないと、すでにセットアップ済みのプロジェクトで `/loop:init` を打った瞬間に上書き事故が起きます。

**2. `allowed-tools` で破壊的操作を弾く**

`Bash(rm:*)` や `Write`、`Edit`なども入れていません。冪等な初期化なので、書き込み系は `cat >` のリダイレクトだけで十分だと考えています。

**3. `.gitignore` への重複追記を防ぐ**

```bash
grep -qxF '.claude/ralph-loop.local.md' .gitignore \
  || echo '.claude/ralph-loop.local.md' >> .gitignore
```

`-q`(quiet)`-x`(行全体一致)`-F`(固定文字列)の組み合わせで、何度打ってもファイルが汚れないようにしています。

## 8. 実行するとこうなる

実際に空のディレクトリで `/loop:init` を打つと、こんな感じで動きます。

```
created: .agent/CLAUDE.md
created: .agent/AGENTS.md
created: .agent/HARNESS.md
created: .agent/FEATURE_INTAKE.md
appended: .claude/ralph-loop.local.md
appended: .claude/progress.md
created: .claude/progress.md
---
Final tree:
.agent:
  AGENTS.md
  CLAUDE.md
  FEATURE_INTAKE.md
  HARNESS.md
.claude:
  progress.md
  settings.local.json
.gitignore

✅ Loop Engineering 初期化完了。
   次は /goal "<検証可能な条件>" でループを起動できます。
```

Codex 側の出力も verbatim で見えます。

```json
{
  "ready": true,
  "codex": { "available": true, "detail": "codex-cli 0.140.0" },
  "auth": { "available": true, "loggedIn": true },
  "reviewGateEnabled": true,
  "actionsTaken": [
    "Enabled the stop-time review gate for <project-path>."
  ]
}
```

`reviewGateEnabled: true` が確認できたら、もうそのプロジェクトでは Codex が Stop ゲートとして常駐している状態です。


## 9. ゴール文の書き方 — 良い例と悪い例

`/loop:init` が済んだあとは `/goal` を打つだけ、なんですが、ここでゴール文の質が全部を決めます。

| 良くない例 | 良い例 |
|----------|--------|
| `/goal "コードを良くする"` | `/goal "src/auth/ をリファクタし、tests/auth/ 全テスト緑、/codex:review verdict=approve。最大20ターン"` |
| `/goal "ログイン機能作る"` | `/goal "POST /api/auth/login を実装し、tests/auth/test_login.py 緑、/codex:review approve、最大30ターン"` |
| `/goal "バグ直す"` | `/goal "issue #42 の再現テストを書いて緑にし、回帰なし、/codex:review approve"` |

判定の基準はシンプルで、**第三者の人間がゴール文だけ見て「達成 / 未達成」を5秒で判定できるか**。これができれば検証器に乗ります。

### テストも AI に書かせたいときは2段に分ける

「テストも実装も AI にやらせたい」場合、1つのゴールにまとめるか、2段に分けるかで悩むと思います。

結論から言うと、**ほぼ常に分けたほうが品質が上がります**。

```
Goal 1: テスト設計(実装ファイルは触らない、RED 確認、Codex approve)
Goal 2: 実装(テストファイルは編集禁止、全テスト緑、Codex approve)
```

理由は、1つのゴールに混ぜると「テストを甘く書いて即緑にする」が最短路になるからです。
テストと実装の役割を分けると、Goal 1 ではテストが仕様として固定され、Goal 2 ではその仕様を通すコードが要求されます。

Codex のレビューも2回独立に入るので、ダブルチェックになります。

## 10. 使ってみての気づき

### 編集のないターンは ALLOW で素通し

最初は「毎回 Codex が走ったら鬱陶しそう」と思っていたんですが、実際の挙動を見ると違いました。Stop hook のプロンプト(`prompts/stop-review-gate.md`)を読むと、こう書かれています。

> If the previous Claude turn was only a status update, a summary,
> a setup/login check, a review result, or output from a command
> that did not itself make direct edits in that turn, return ALLOW
> immediately and do no further work.

質問への回答だけ、ステータス確認、ドキュメント説明のターンは即 ALLOW で素通しされます。**コードを実際に書いたターンだけ採点される**。これがあるので、おしゃべりが詰まる心配はないです。

### Codex の出力は絶対に要約しない

`commands/review.md` を読むと、こう書いてあります。

> Return the command stdout verbatim, exactly as-is.
> Do not paraphrase, summarize, or add commentary before or after it.

Codex の出力には `file`、`line_start`、`line_end`、`confidence` が含まれていて、これを Claude が要約すると行情報が消えます。プロンプト側にも「Codex 出力は改変禁止」を明記しておくと安心です。

### `--max-turns` は必ず付ける

Loop Engineering の界隈で何度も警告されているのが、`--max-turns` なしのループです。

:::note
Data Science Dojo の Loop Engineering ガイドは、報告された実例として「エージェントが壊れたツールを5分間で400回呼び続けた」インシデントを挙げています([Agentic Loops: From ReAct to Loop Engineering — Data Science Dojo](https://datasciencedojo.com/blog/agentic-loops-explained-from-react-to-loop-engineering-2026-guide/))。
同ガイドは Steinberger 報告として「本番ループの月間使用量が最大 130万ドル」という数字も載せていて、Loop Engineering の構造上、コスト境界はループ自身では止められないことが繰り返し強調されています。
:::

僕の運用ルールでは、`/goal` のデフォルトを最大30ターン、トークン予算20万に置いています。

これがないと
`/goal`使ったらセッション上限行っちゃったよ！→生成AI使えない→今日の仕事おーーわり！となってしまいかねません。

人間一度上がった生活水準を落とすことは難しいと言いますが、生成AIの領域においても顕著ですね。

### 高リスク変更は `/codex:adversarial-review`

通常の `/codex:review` は実装の品質チェックですが、`adversarial-review` のほうは「そのアプローチが正しいのか?」「前提が壊れていないか?」を問う敵対的モードです。

DB マイグレーション、auth、payment、大規模リファクタの類はこちらに切り替えています。
重い分、設計の穴を引き当てる確率が高いと考えています。

## 11. 次にやりたいこと

`/loop:init` が動いたので、次は2つ考えています。

**1. SessionStart hook でゲートを自動 ON**

プロジェクト単位の設定はそのままに、**新規プロジェクトに入った瞬間に自動でゲートONにする** SessionStart hook を仕込めば、`/loop:init` すら打たずに済みます。プラグインの workspace ハッシュ計算アルゴリズムに合わせて state.json を書き込む形になりますが、実装は短いです。

**2. テンプレ集の充実**

`~/.claude/loop/prompts/` に TDD、bugfix、リファクタ、高リスク変更用のテンプレを置いて、`/loop:init` から `@` 参照させる構成にしたい。テンプレが育つと、`/goal` のゴール文も毎回ゼロから書かなくて済みます。

## まとめ

ここまでの話をひと言にすると、こうなります。

> `/goal` で自走させる。Codex Stop ゲートで自己採点を潰す。
> `/loop:init` で毎プロジェクトの初期化を1コマンドに畳む。

`/goal` 単体は便利ですが、それだけだと「自己採点で素通し」のリスクが残ります。
Codex を Independent Reviewer に置くことで、**Claude が「完了」と言っても、Codex の許可印がないと止まれない**状態が作れます。

Loop Engineering は、プロンプトを磨くフェーズから、サイクルを設計するフェーズへの移行です。
1ターン1ターンを最適化するのではなく、ゴールから逆算した「終わり方」を設計する。`/goal` も Codex のゲートも、その道具です。

Addy Osmani が essay の最後で書いていた一文は、運用に乗せた今のほうが重く刺さります。

> Build the loop. But build it like someone who intends to stay the engineer, not just the person who presses go.
> (ループを作れ。ただし、ボタンを押すだけの人ではなく、エンジニアであり続けるつもりの人として作れ)
>
> — [Addy Osmani, "Loop Engineering"](https://addyosmani.com/blog/loop-engineering/)

普段から Claude Code を使っているなら、`/loop:init` 相当の初期化スクリプトを自分の `~/.claude/commands/` に1つ置くだけで、毎日のワークフローが変わります。やってみてください。

### 補足:同じ名前の OSS もある

記事を書いている最中に気づいたんですが、Cobus Greyling がメンテしている [`cobusgreyling/loop-engineering`](https://github.com/cobusgreyling/loop-engineering) という npm パッケージ集にも `loop-init` という CLI が含まれていました。

```bash
npx @cobusgreyling/loop-init . --pattern daily-triage --tool grok
```

向こうは Grok / OpenAI / Claude 横断のプロジェクト雛形ジェネレータで、今回作った Claude Code 専用の `/loop:init` とは射程が違いますが、**`loop-init` という名前で同じ問題を解こうとする実装が複数現れている**こと自体が、Loop Engineering がもう「概念」から「現場ツール」のフェーズに来ていることの一つの傍証だと思います。

## 最後に

実を言うとこちらの記事も今回作成した仕組みを用いて初稿を書きました。
ClaudeCodeやCodexに聞きながらキャッチアップ→実装→そのコンテキストをもとに`/goal`で記事を作成と言う流れです。

ファクトベースで調査させて、元々置いてあったテクニカルライティング用のスキルを使いながら執筆→Codexでファクトチェックの流れが動く様は壮観の一言でした。

もちろんそのままポン出ししているわけではなく、筆者の目を通して添削などをする必要はありますが、ある程度は自然な文章になっているのではないでしょうか。

何よりコンテキストが維持されている都合上、普段の筆者の文体に似通っていることもポイントが高いですね。

## 参考

### Loop Engineering の発端(2026年6月)

- [Loop Engineering — Addy Osmani(2026-06-07)](https://addyosmani.com/blog/loop-engineering/) — 命名と体系化の essay
- [Peter Steinberger の 6.5M ビュー投稿(2026-06-08)](https://thenewstack.io/loop-engineering/) — The New Stack による文脈整理付き
- [Anthropic Engineer: Stop Prompting Claude, Build Loops — Explainx.ai](https://explainx.ai/blog/anthropic-engineer-loops-prompts-ai-coding-harness-engineering-2026) — Boris Cherny の発言コンテキスト

### 実践ガイド(引用元)

- [What Is Loop Engineering? — Tosea.ai](https://tosea.ai/blog/loop-engineering-ai-agents-complete-guide-2026) — "Hallucinated success" と "Reward Hacking" の定義
- [Agentic Loops: From ReAct to Loop Engineering — Data Science Dojo](https://datasciencedojo.com/blog/agentic-loops-explained-from-react-to-loop-engineering-2026-guide/) — 400回コール事件等の実例
- [Effective harnesses for long-running agents — Anthropic](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — 一次ソース
- [The Anatomy of an Agent Loop — Steve Kinney](https://stevekinney.com/writing/agent-loops) — ループの最小実装
- [How to Build an Agentic Loop with Claude Code — MindStudio](https://www.mindstudio.ai/blog/how-to-build-agentic-loop-claude-code) — `--max-turns` 等の運用パラメータ

### 同名 OSS / 類似ツール

- [cobusgreyling/loop-engineering — GitHub](https://github.com/cobusgreyling/loop-engineering) — `loop-init` `loop-audit` `loop-cost` の3 CLI セット(マルチエージェント対応)
- [awesome-harness-engineering — GitHub](https://github.com/ai-boost/awesome-harness-engineering) — Harness 系のキュレーション

### Codex 課金まわり

- [Using Codex with your ChatGPT plan — OpenAI Help Center](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan)
- [Codex Pricing — OpenAI Developers](https://developers.openai.com/codex/pricing)
