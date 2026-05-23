---
id: "2026-05-22-claude-codeを本気で使うskillshooksサンドボックスサブエージェント-01"
title: "# Claude Codeを本気で使う：Skills、Hooks、サンドボックス、サブエージェント"
url: "https://qiita.com/spfpt/items/b7125cd6aa9618886651"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "API", "AI-agent"]
date_published: "2026-05-22"
date_collected: "2026-05-23"
summary_by: "auto-rss"
query: ""
---

![og.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/c0d21d8b-b09c-41f8-9b47-add89284639c.png)


> _If you prefer English, please refer to [this blog post](https://spfpt.github.io/claude-code-101/)._

ChatGPT には慣れていて、Claude Code も同じ感覚で使えるようにしたい人向けの実践ガイドです。そこからさらに三、四歩先まで進みます。

この記事は意図的に長くしています。Claude Codeが初めてなら、最初は上から下まで一度通して読むのがおすすめです。ブックマークしておいて、実際に必要になったら「[7. Skills: 探す、入れる、使う](#7-skills-探す入れる使う)」以降に戻ってきてください。

すでに Claude Code に慣れている場合は、最初の章を飛ばして CLAUDE.md から読んでも大丈夫です。あるいは、目次を開いて読みたい章へ移動してください。

> 対象は Claude Code v2.1.147、2026年5月時点です。バージョンの進みが速いので、最近入った機能については、挙動が違うと感じたときに [release notes](https://github.com/anthropics/claude-code/releases) と照らし合わせられるようにしておきます。

> もう 1 つ大事なこととして、[Claude アカウントがどう課金されているか](https://claude.ai/settings/usage)は先に確認してください。Pro / Max では主に利用枠や週次上限を意識しますが、Enterprise では、独自の spending cap があり、API 料金ベースで課金される場合があります。詳しくは [12章](#12-地味だけど本当に大事な基礎) で扱いますが、Opus のような高いモデルで何時間も作業する前に知っておくべき話です。

## 1. ChatGPTからClaude Codeへ

ChatGPT を使ったことがあれば、Claude Codeの仕組みの 80% はすでに理解できています。残りの 20% が、いい意味で危険な部分です。

Claude Code は単なるチャットではありません。コードの隣に住む CLI エージェントです。プロンプトを渡すと、返事をするだけでなく、許可を取ったうえで次のことができます。

- プロジェクト内のファイルを読む
- シェルコマンドを実行する
- ディスク上のコードを編集する

.. すべて許可ベースです。手を動かせるシニアのペアプログラマーだと思うと近いです。

### どこで動かせるか

主な選択肢は 4 つあります。自分がよく使う順に並べます。

1. **Terminal（推奨）**。任意のディレクトリで `claude` と打つだけです。これが標準体験です。機能はまずここに入り、キーボードだけのワークフローも 1 日ほどで違和感がなくなります。この記事の内容は、基本的にここにいる前提で書いています。
2. **VS Code / Cursor / JetBrains plugin（次点）**。同じエンジンですが、diff のプレビューが見やすく、エディタにいながら作業できます。IDE 中心で作業しているなら入れる価値があります。ただし、Terminal 版ほど成熟していない点は覚えておいたほうがいいです。
3. **Desktop app（Mac / Windows）**。UI は洗練されていて、コーディング以外のタスクや、ちゃんとしたテキストエディタで会話したいときに向いています。一部の高度なフラグや slash command は反映が遅れます。Desktop app にはいくつかバグがあり、Terminal 版ほど安定していないという話も聞きますが、自分ではまだ使い込んでいません。
4. **Web at [claude.ai/code](https://claude.ai/code)**。手元のマシンから離れているときの単発質問、"ultraplan" モード、Anthropic 側のインフラで動く [scheduled routines](#11-truly-agentic-the-advanced-features) を起動する用途に向いています。日常的に作業する場所としては、だいたいここではありません。

### インストール

インストール手順はよく変わるので、ここでは再掲しません。[official quickstart](https://docs.claude.com/en/docs/claude-code/quickstart) を参照してください。

Windows を使っている場合は、Windows Subsystem for Linux (WSL) を使い、WSL のターミナル内に Claude Code を入れることを強くおすすめします。そうすると Claude Code を開くたびに最新バージョンを使いやすくなります。Windows PowerShell や Command Prompt で普通に使うのも問題ありませんが、WinGet で入れた場合は自動更新されないため、ときどき手動更新が必要になるかもしれません。最終的には好みです。

macOS の場合は、curl で Claude Code を入れるのがおすすめです。これは Anthropic も推奨しているネイティブな方法です。個人的な経験として、Homebrew 経由はおすすめしていません。

`claude --version` が動くようになったら戻ってきてください。

### 最初の例を 2 つ

Terminal で、よく知っているプロジェクトに `cd` します。どんなプロジェクトでも大丈夫です。そこで次のコマンドを実行します。

```bash
claude
```
![welcome-banner.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/b64fddc1-08e1-40b3-a849-d73e71b26f31.png)

これが起動時の welcome banner です。

プロンプトが出ます。次を試します。

```claude
what does this repo do?
```

![what-does-this-repo-do.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/a5d20f96-d5e3-408e-b228-346b25416591.png)


Claude はリポジトリの README、トップレベルのファイル、場合によっては `package.json` や `pyproject.toml` などを必要なだけ読んで答えます。やったことは、プロジェクトディレクトリに `cd` して、`claude` を起動し、シンプルな質問を 1 つしただけです。ここが ChatGPT との違いです。

まだプロジェクトに README.md がない場合は、次のコマンドを貼って作成します。すでに README.md がある場合は、この手順は飛ばしてください。

```bash
cat > README.md <<'EOF'
# README.md

Learning LoRA and finetuning by doing my own experiment where I compare 
three versions of the same `Qwen3-8B` math run:

1. the untouched baseline
2. LoRA on the attention projections
3. LoRA on both attention and feed-forward projections.

This project came to mind when I was reading the "LoRA Without Regret" blog 
post by Thinking Machines; so many research ideas to explore! Well, I only 
knew LoRA conceptually before this, and I have never done any serious 
finetuning before except for a hackathon, so I think this challenge 
I have set for myself is pretty nice.
EOF
```

次にこれを試します。

```claude
@README.md what's missing from this README that a new contributor would want?
```

![whats-missing-from-this-readme.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/c1018416-a655-4463-9d75-b4886cb57a27.png)

`@` は fuzzy file picker を起動します。選んだファイルはコンテキストに読み込まれます。これが最初の少し本格的な能力です。**Claude Code は指定したものを見られます。**

### メンタルモデル

> Claude Code は、ファイルシステムを見られて、許可を取ったうえで何かを実行できる ChatGPT です。

この一文でほぼ 90% は説明できます。チャットにコードをコピペしたくなるたびに思い出してください。コピペする必要はありません。ファイルを指し示せばいいだけです。

---

## 2. CLAUDE.md はリポジトリでいちばん大事なファイル

この記事で 1 つだけ覚えるなら、**リポジトリに `CLAUDE.md` を置く**ことです。いちばんレバレッジの高い変更と言ってもいいくらいです。

`CLAUDE.md` は Markdown ファイルで、Claude Code はそのディレクトリでセッションを始めるたびに自動で読み込みます。コードからは推測できないこと、たとえば規約、コマンド、注意点、「pip ではなく uv を使う」などを Claude に伝えるための場所です。毎回同じ説明を繰り返さなくて済みます。

### 置き場所

Claude Code は `CLAUDE.md` を次の 3 か所で探します。この順番です。


| Path                        | Scope                                             |
| --------------------------- | ------------------------------------------------- |
| `~/.claude/CLAUDE.md`       | User-level。個人設定。すべてのプロジェクトに適用されます。                |
| `<repo>/CLAUDE.md`          | Project-level。git に入れ、チームで共有します。                  |
| `<repo>/<subdir>/CLAUDE.md` | Subdirectory-level。その subtree で作業しているときだけ読み込まれます。 |


加えて `CLAUDE.local.md` もあります。これは `<repo>/CLAUDE.md` と同じですが、慣例的に `.gitignore` します。コミットしたくない個人メモに使います。

個人的には、`CLAUDE.md` はプロジェクトルートに置き、user level には置かないほうが好みです。たとえばこうです。

```bash
project-name/
├── src/
│   ├── cute/
│   │   ├── blackwell_helpers.py
│   │   ├── flash_fwd.py
│   │   └── paged_kv.py
│   ├── layers/
│   ├── models/
├── examples/
│   ├── inference/
├── docs/
│   ├── architecture.md
│   └── testing-guidelines.md
├── CLAUDE.md      # <-- here
├── .gitignore
├── .env
├── Makefile
├── README.md
└── LICENSE
```

### `/init`

始める最短ルートは、リポジトリで新しい `claude` セッションを開き、次を打つことです。

```claude
/init
```

![claudeinit.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/a360fd1f-1cae-4a79-85ab-44f689863b27.png)


Claude がリポジトリを調べて `CLAUDE.md` を提案します。確認して、削って、受け入れます。そのまま受け入れるのは避けたほうがいいです。余計なことまで入りすぎる場合があります。

### 良い CLAUDE.md に入れるもの

Anthropic の [ベストプラクティスのdoc](https://code.claude.com/docs/ja/best-practices) には良い ✅/❌ の表があります。要点はこうです。

✅ 入れるもの:

- Claude が推測できない Bash コマンド（`npm run lint`, `make watch`, `pnpm test:integration`）
- linter 設定にはないコードスタイル規則（`prefer named exports`, `match the existing pattern in src/api/`）
- ワークフロー上の約束（`always update the changelog`, `branch from main`, `we squash on merge`）
- リポジトリ固有の癖（`the .env in services/auth is different from the others`, `don't touch generated/`）

❌ 入れないもの:

- Claude がデフォルトで十分できること。バグ修正を頼んだら普通にテストを書くなら、「バグ修正ではテストを書け」を CLAUDE.md に足す必要はありません。
- 長い理由説明。なぜそうするかは design doc に置きます。
- ファイルツリーの再掲。Claude は `ls` できます。
- 実際の判断に効かない曖昧な包括ルール（「気をつける」「良い判断をする」）。

Claude Code の作者である Boris Cherny は、[Claude Code patterns post](https://howborisusesclaudecode.com/) でかなりはっきり言っています。Claude がその instruction なしでもできているなら、その instruction は消す。`CLAUDE.md` は雰囲気を足す場所ではなく、摩擦を減らす場所です。

### 他のファイルを import する

`@` 構文を使うと、CLAUDE.md に他のファイルを取り込めます。

```markdown
# Conventions for this repo

We use uv, not pip. We use ruff, not black.

@./docs/architecture.md
@./docs/testing-guidelines.md
```

Imports はセッション開始時に解決されます。`architecture.md` が長ければ、最初のターンから context window に入ると思ってください。

### Auto memory

Claude Code には、セッションをまたいで Claude 自身が memory を積み上げる機能があります。役割、好み、プロジェクト状態などの小さなメモです。直接管理するものではなく、`~/.claude/projects/<project-hash>/memory/` の下に置かれます。特に何かする必要はありません。ただ、`CLAUDE.md` が唯一の永続化手段ではなくなっていることを知っておくのは役に立ちます。それでも、`CLAUDE.md` は自分で管理でき、新しいセッションが最初に信頼するものです。

---

## 3. Claude に実作業を頼む

CLAUDE.md はできました。では、実際に Claudeに何かを「やって」もらうにはどうすればいいのでしょうか。

### 4 つの入力プリミティブ


| You type                        | What happens                              |
| ------------------------------- | ----------------------------------------- |
| `@filename`                     | Fuzzy file picker。選んだファイルが context に入ります。 |
| `!command`                      | シェルコマンドを実行し、その出力を prompt に入れます。           |
| Drag/drop image                 | 画像が context に入ります。paste でも動きます。           |
| `cat err.log | claude -p "..."` | stdin を one-shot prompt に流し込みます。          |


いちばんよく使うのは最初の `@` です。`@` に慣れると、コピペはほぼしなくなります。

![file-picker.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/294c2305-8cfc-421d-b0ff-d229c13bf287.png)

### ライブデモ

プロジェクトディレクトリに下書きのブログ記事を作ってみます。次を打ちます。

```claude
make a draft at drafts/hello.md with a short intro to Claude Code,
suitable for someone who's used chatgpt
```

![drafts-hello.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/b3df80b8-4eea-4b86-a845-815c7857131e.png)

Claude はファイルを提案し、内容を見せ、許可を求めます。承認すると書き込みます。次に、Claude Code にこれを貼ります。

```claude
@drafts/hello.md add a 3-section TOC at the top: intro, examples,
gotchas, and stub each section with a one-line placeholder.
```

![diff-of-new-toc.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/ae91571e-6711-4a21-b8d2-112c707ab750.png)

Claude はファイルを読み、編集内容を計算し、diff を表示し、許可を求めました。ChatGPT では起きなかった 3 つのことが起きています。実ファイルを読み、ディスクに書き、承認または却下できる diff を出しました。

### 効く prompting

ChatGPT と同じように prompt しても、Claude はそれなりに動きます。少しだけ頼み方を変えると、かなりよく動きます。[best-practices doc](https://docs.claude.com/en/docs/claude-code/best-practices) の 4 つのコツを短くまとめるとこうです。

1. **タスクの範囲を切る。** 「バグを直して」ではなく、「`id` が数値でないときに `/users/:id` が 500 を返すバグを直す。まず再現し、その後修正し、テストを追加する」。
2. **情報源を指す。** 関係あると分かっているファイルは `@` で指定します。Claude に grep させる前に渡します。
3. **既存パターンを参照する。** 「この新機能を追加するときは `src/api/v2/handlers/` のパターンに合わせる」。具体例は one-shot / few-shot examples として効き、抽象ルールより強いです。
4. **仮説ではなく症状を説明する。** 「cache layer が壊れている」と言うと、そこだけ見に行きます。バグが upstream にあってもです。観測したことを伝え、診断は任せます。

裏返すと、ChatGPT 的に「X をする関数を書いて」と頼んでいるだけでは、価値の大半を使えていません。Claude Code の強みは context を読めることです。必要な材料をちゃんと渡しましょう。

---

## 4. 内側のループ: 権限とモード

最初に多くの人がぶつかる壁は、ほぼすべての action で許可を求められることです。10 分もすると laptop を投げたくなります。そこから抜ける階段があります。覚えておく価値があります。

### 権限の階段

信頼度が低い順に並べます。

#### 1. Default（書き込みと実行の前に毎回聞く）

初日に見る状態です。編集、シェルコマンド、すべてで permission prompt が出ます。

![permission-to-rm.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/515f35c8-7fce-4779-9c1b-abf2c0bb2376.png)

そのセッションをまだ信頼していないときや、タスクが sensitive なときに使います。

#### 2. Plan mode（Shift+Tab を 2 回、または `/plan`）

このモードでは Claude Code は読むことと探索だけできます。編集、書き込み、実行はできません。その代わり、レビューできる計画をファイルに出します。多くの場合 `~/.claude/plans/<slug>.md` です。

![plan-mode.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/de927af2-8583-4c9d-afe0-1096c61e0b54.png)

慣れていないコードベースに入るときや、そこそこ大きい変更を始める前に使います。本物のエンジニアがやるのと同じです。まず探索し、計画し、それから実行する。ただし、もう少し構造化されています。

plan modeはかなり好きです。単純ではなく、ある程度の reasoning や手順の整理が必要なタスクでは、いつも plan mode を使います。

#### 3. acceptEdits（Shift+Tab で切り替え）

ファイル編集と安全な filesystem 操作（安全な path への `mkdir`, `touch`, `mv`, `cp`）を自動承認します。任意のシェルコマンドは自動承認しません。

![acceptedits.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/38119d91-0181-4946-b758-ffda018fa5d5.png)

> acceptEdits modeでも、protected paths（`.git`, `.claude`, dotfiles, home directory 自体）は守られます。acceptEdits は「diff を信頼する」であって、「全部を信頼する」ではありません。

注意を払いながら diff を確認しているが、40 回 `Approve` を押したくないときに使います。

#### 4. Auto mode (`claude --permission-mode auto`)

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/a9b0ddcd-e8ee-4392-a47a-d98f2663547a.png)

比較的新しく、知っておく価値があります。小さな classifier model が Bash と MCP calls を gate しているようです。scope escalation、未知の infrastructure、敵対的に見える content をブロックし、routine に見えるものは通します。classifierが3回連続でブロックすると、permission prompt に戻ります。Sonnet 4.6 以降とMax/Team/Enterprise plan が必要です。

#### 5. bypassPermissions / `--dangerously-skip-permissions`

チェックなし。全速力。何も聞かれません。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/c132f61e-b48a-482e-814f-f03c3b759394.png)

> **まだ使わないでください。** [9章](#9-guardrails-hooks) で hooks に戻ってきます。それが入ってからなら、`--dangerously-skip-permissions` は意図的な選択になります。

### `/permissions` allowlists

特定のコマンドを always-allowed として固定できます。セッション内でこうします。

```claude
/permissions allow Bash(npm run lint)
/permissions allow Bash(pytest *)
```

これで、そのコマンドは default mode でも permission prompt なしに実行されます。prompt を意味のある場所に残すための方法です。破壊的なコマンドは gate したまま、安全なものだけ nagging を止めます。

`/permissions list` で現在 allow されているものを表示します。`/permissions deny <rule>` で削除します。

### どのモデルを使うべきか

普段はほとんどのタスクで最新の Opus を使い、計画づくりには Sonnet を使っていました。タスクがよく整理されていて手順に自信があるなら、最初から最後まで Sonnet でも大丈夫です。Opus のほうが明らかに強いですが、Sonnet も悪くありません。`/model` に行けば、使いたいモデルに切り替えられます。

ただし、モデル選びを単なる品質の話として扱う前に、課金のされ方は確認したほうがいいです。通常の Pro / Max subscription では、主に利用枠や週次上限を気にします。一方、usage-based Enterprise や API key での利用では、使った分が API 料金で課金されるため、モデル選びがそのまま費用に効きます。この場合、Opus を一日中つけっぱなしにすると、spend cap を想像以上に速く使い切ることがあります。Haiku は本格的なコーディングにはあまりおすすめしません。実用上は、考える部分だけ Opus で進め、作業がはっきりしたら Sonnet に戻す、くらいがだいたい良いです。

さらに、2026年5月22日時点では、model effort を low から max まで設定できます。effort が高いほど、モデルは詳しい reasoning と analysis に時間を使います。`max` effort は効果のわりに token を使いすぎると感じることが多く、`high` や `xhigh` で十分なことが多いです。

---

## 5. セッションを再開する

昨日の debugging session、数日にまたがる feature、途中の refactor。もう一度説明する必要はありません。Claude Code はセッションを自動で残してくれます。

### resume flags

```bash
claude --continue           # or `claude -c` --- この dir の最新 session を再開
claude --resume             # 全 session から interactive picker
claude --resume my-oauth    # 名前付き session に飛ぶ
```

![claude-resume.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/37e7ad50-7a76-4852-8a68-a18de10c5721.png)

### セッションに名前を付ける

セッション内でこうします。

```claude
/rename my-oauth-refactor
```

後で探すなら、"ff347a49-e961-444f-9dae-28553602ead5" より名前のほうがずっと楽です。戻ってくる可能性があるものには名前を付けます。

### Checkpoints と `/rewind`

Claude Code は各変更の前に checkpoint を自動で作ります。巻き戻すには:

- `Esc Esc`: rewind menu を開く。
- `/rewind`: slash command で同じ menu を開く。

![rewind1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/ff40b3c0-0875-45b2-82c2-de4bd3558885.png)

\+

![rewind2.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/c8d11b5a-fc6b-4ba8-ba1c-cb5bb6c9abe6.png)


巻き戻し方は選べます。

- **Conversation only**: file edits は残し、chat history だけ戻す。「今の聞き方をやり直したい」に便利
- **Code only**: 会話は続け、disk changes だけ戻す
- **Both**: その turn への完全な time-machine
- **"Summarize from here"** または **"summarize up to here"**: 部分的な compaction（詳しくは [6章](#6-コンテキスト-溜める圧縮する消す)）

> Checkpoints が追跡するのは Claude の編集であり、外部プロセスではありません。長時間の build がファイルを書いた場合、それは戻りません。`/rewind` を git の代わりとして扱わないでください。Git は本当に大事です。変更追跡には必ず使うことをおすすめします。

### Teleporting

Web app や desktop app で始めたセッションを terminal で終わらせたい場合、`claude --teleport` で移せます。スマホで始めて laptop で終えるような使い方に便利です。

---

## 6. コンテキスト: 溜める、圧縮する、消す

Claude が読んだファイル、実行したコマンド、見た出力はすべて context window に入ります。長いセッションは遅く、高く、だんだん変になります。モデルが 2 時間前に言ったことを忘れ始めます。

これを管理する道具は 4 つあります。正しいものを使います。

### `/compact` : その場で要約

```claude
/compact
```

Claude は現在のセッションをその場で要約し、要点を残して細部を落とします。会話はその summary から続きます。

![compact.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/1bbd9371-77c7-4ddd-92f1-386b9ecd8e62.png)

instruction も渡せます。

```claude
/compact preserve the test failures and the chosen API design
```

summaryは指定したものを残します。これは Claude Codeで最も使われていない command の 1 つです。長いタスクの大きな区切りでは実行してください。

### `/clear` : 同じ repo で新しく始める

```claude
/clear
```

会話を消します。CLAUDE.md は引き続き読み込まれます。1つのタスクを終えて、同じprojectで別のタスクを始めるときに使います。Boris Cherny の [advice](https://howborisusesclaudecode.com/) は、積極的に `/clear` することです。次のタスクがかなり軽く感じるはずです。

### `/rewind` "summarize from here" : 部分 compact

これは [5章](#5-セッションを再開する) で見ました。別の knob です。最近の turn はそのまま残し、古い部分だけ要約します。進捗が出た直後で、最後の細部は失いたくないが、初期探索は圧縮していいときに向いています。

### `/btw` : ついでの質問

```claude
/btw what's the difference between Sonnet and Opus?
```

`/btw` は dismissible overlay を開きます。質問と Claude の回答は conversation history に入りません。今知りたいけれど、あとで session を汚したくない話に使います。

![btw.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/3054d215-95b1-42bb-acb0-36b794fbbd0d.png)

### 終了して新しく始める

最後の手段です。Claude Code を終了し（`Ctrl+C` twice または `/exit`）、新しいセッションを始めます。前のセッションが stuck、confused、あるいは同じ点を 3 回直したときに使います。

### 目安

**1 session, 1 goal.** Bug fix と refactor と doc rewrite は 3 つの session であって、1 つではありません。Claude Code の creator である Boris は、逆のやり方を "kitchen sink session" と呼んでいます。全部が 1 つの会話に放り込まれ、context が膨れ、quality が落ちます。`/clear` は無料です。

CLAUDE.md で compact の仕方を伝えることもできます。

```markdown
## On compaction

When compacting, always preserve:
- the chosen API contract
- any test failures we've seen
- any decisions we explicitly made
```

context limit に近づくと auto-compaction が走りますが、先に `/compact` するほうが安く、結果もタスクに合いやすいです。

---

## 7. Skills: 探す、入れる、使う

Skill は `/skill-name` で呼び出せる、まとまった instruction set です。必要なら tool restrictions も付けられます。ざっくり言うと、「Claude に X をやってほしいときの自分流」を 1 つの slash command にしておく仕組みです。

### `/skills`

セッション内で次を打ちます。

```claude
/skills
```

![skills.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/0e7209d7-a7c0-411c-a2d1-4a35fbd4a6bd.png)

現在読み込まれているものが見えます。user-level（`~/.claude/skills/`）と project-level（`./.claude/skills/`）の両方です。

入れたばかりの状態では何もありません。いくつか入れてみます。

### `/plugin` と marketplace

```claude
/plugin
```

![plugins.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/e3ffbdbc-b0f4-4d6b-8b0b-1f27dea7bfa8.png)

plugin は 1 つ以上の skills（必要なら hooks や MCP servers も）を 1 つにまとめた installable unit です。まずは公式 Anthropic marketplace の `claude-plugins-official` から始めるのがいいです。

まだ入っていなければ:

1. `/plugin` → **Tab to "Marketplace"** → **Add marketplace**。
2. marketplace GitHub repository identifier として `anthropics/claude-plugins-official` を貼る。
3. Confirm。

![plugins-marketplaces.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/1dd044e6-e36c-4211-8936-e6524a010b28.png)

これで browse できます。便利な starter pack を入れます。plugin は user level か project level に install できます。どの project でも使えるように、だいたい user level に入れています。


| Skill             | What it does                                    |
| ----------------- | ----------------------------------------------- |
| `frontend-design` | 高品質な frontend interface を作る。                    |
| `skill-creator`   | 新しい skill を一緒に作る、または既存の skill を改善する。meta-skill。 |


これらが install されたかは、`/plugin` 内の **Installed** tab で確認できます。

![installed-plugins.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/12008aa5-5135-46db-b1ce-9a87ca5e27c0.png)

### Skills を呼び出す

呼び出し方は 2 つあり、どちらも動きます。

**Leading.** prompt の先頭に skill を置く:

```claude
/frontend-design look at @src/cute/blackwell_helpers.py and design a modern and clean HTML UI for me to visualize this code intuitively.
```

**Mid-prompt.** より大きな instruction の中に skill を埋め込む:

```claude
fix the failing test in @examples/inference/test_blackwell_helpers.py, then /code-simplifier the result.
```

Mid-prompt invocation が動くのは、skills が Claude の呼べる tools として mounted されているからです。別 command を実行しているのではなく、その tool を使うよう促しています。

### デモを 3 つ

**Demo 1: 複雑な codebase に `/frontend-design` を使う。**

[src/cute/flash_fwd.py](https://github.com/Dao-AILab/flash-attention/blob/main/flash_attn/cute/flash_fwd.py) の code を可視化したいとします。複雑になってきていて、追いづらいからです。

```claude
/frontend-design look at @src/cute/flash_fwd.py and design a modern and clean HTML UI for me to visualize this code intuitively.
```

![frontend-design-skill.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/a25f8f80-79bb-4f6b-9c44-319d1c472c97.png)

Opus 4.7 with xhigh effort と `frontend-design` skill で、たった 1 つの prompt から生成されたものがこれです。

![frontend-design-result.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/41881879-f6ff-4acf-877e-a987ba3f593b.png)

初回としては悪くないと思います。かなり interactive でもあり、ここから学べそうです。

**Demo 2: UI をさらに改善するために `/frontend-design` を使う。**

さらに UI を改善したいとします。もう一度 `frontend-design` skill で頼めます。

```claude
please help me improve this ui further for this file. pasting the screenshot here to show you how it looks: [Image #1]. this is genuinely good, but the text could be a bit more legible, perhaps? continue to use the /frontend-design skill
```

![frontend-design-2nd-prompt.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412192/be4757f9-2b2d-44eb-acf2-c394078e40a3.png)

結果はこうです。

![frontend-design-2nd-result.png](https://qiita-image-st
