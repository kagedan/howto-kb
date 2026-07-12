---
id: "2026-07-12-ai-エージェントによる-skill-利用を把握する-skilltrace-でどの-skill-が-01"
title: "AI エージェントによる Skill 利用を把握する ─ SkillTrace で「どの Skill が どう使われたのか」を追跡！"
url: "https://zenn.dev/h1deya/articles/skilltrace-introduction"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "AI-agent", "LLM", "Gemini"]
date_published: "2026-07-12"
date_collected: "2026-07-13"
summary_by: "auto-rss"
query: ""
---

# SkillTrace とは？

**[SkillTrace](https://www.npmjs.com/package/skilltrace) は AI agent による skill の利用状況を把握するための、無料の observability tool です。** 以下ではその使い方をサンプルを使って具体的に説明します。

![SkillTrace ダイアグラム](https://static.zenn.studio/user-upload/deployed-images/60dd5037f29d31f55341f953.webp?sha=7a672e4a233fa397b6574404ccbbb5c2bb44103e)

# なぜ Skill のデバグは難しいのか？

最近、AI coding agent が、再利用可能な “skills” を活用するようになってきました。

ここでいう skill とは、特定の種類の作業を行うための小さな手順パッケージのようなものです。たとえば、

* pull request をレビューする
* TypeScript のエラーを修正する
* database migration を確認する
* project 固有の debugging checklist に従う

といった作業について、agent に「この作業ではこう進めてください」と伝えるための instructions や references、場合によっては scripts をまとめたものです。

これはかなり強力です。  
一方で、そのデバグに関して、新たな問題も認識され始めています。

> agent が複数の skills から選べるとき、どの skill を実際にどう使ったのか、どうやって知ればよいのか？

* agent は skill file を読んだのか？
* その skill の指示に従ったのか？
* その一部だけを使ったのか？
* skill から参照されている reference file を読んだのか？
* 最後に agent は、その skill が作業にどう影響したと認識しているのか？

こうしたことは、意外と分かりにくいです。

たとえば、Tool call は明確な境界を越えるため、比較的観測しやすいです。LLM はその外部にある tool を呼び出し、arguments を渡し、result を受け取る。周辺システムは、そのやり取りをログとして記録できます。

しかし skill は少し違います。

自然言語で記述された skill は file として読み込まれ、LLM 内部の context に取り込まれ、その後の判断や出力に影響します。

このとき、外側から見ているだけでは、

> この skill がここで使われた

という明確なイベントが発生するとは限りません。

# SkillTrace とは？

**[SkillTrace](https://www.npmjs.com/package/skilltrace)** は、この問題を解決するための小さな observability tool です。

SkillTrace は、スキルを使った処理（run）において、次の3つの evidence stream を取得し、それらを比較します。

* Skill ファイルのアクセスの監視
* 専用 MCP 呼び出しによる skill 利用の宣言的な記録
* run の最後 agent による skill 利用状況の振り返り

これらの情報を組み合わせることにより、

> skill をデバグできるようにすること

を目指しています。

この記事では、まず小さな toy demo を動かし、その後、自分の repository に適用する流れを紹介します。

[![SkillTrace 実行の様子](https://static.zenn.studio/user-upload/deployed-images/68163ecc7ae6ecd0fbc0b55a.webp?sha=e605d346b641f402a7757f4b5668b5e21855ac34)  
*SkillTrace による toy demo 実行の様子*](https://github.com/user-attachments/assets/a486b3cd-a0e5-4167-bbe5-885705ea4328)

# SkillTrace が記録するもの

SkillTrace は、大きく3種類の evidence を比較します。

### 1. Passive Traces

Passive trace は、file access を観測したものです。たとえば、

* `SKILL.md` が読まれた
* Skill が参照する reference file が読まれた

といった事実を記録します。  
これは、agent とは無関係に観測できるという点で有用です。

ただし、重要な制限があります。  
File が読まれたからといって、その skill が本当に使われたとは限りません。  
Skill は読まれたが、使われなかったかもしれない。一部だけしか使われなかったかもしれない。  
もしくは、別の instruction に上書きされたかもしれません。

### 2. Semantic traces

Semantic trace は、agent が専用の MCP tool を通じて明示的に記録するイベントです。  
SkillTrace はイベント記録用の local MCP server を提供します。  
Semantic traces を有効にすると、agent に対し、次のようなイベントを報告するよう追加で指示します。

* Skill start
* Reference read
* Skill finish

たとえば、  
「この skill を使い始めました」  
「この reference file を読みました」  
といった宣言です。

ただし、これは agent による自己申告です。  
model は申告を忘れるかもしれません。  
誤った 関連付けをするかもしれません。  
報告の指示に従わないこともありえます。

### 3. Reflection

Run の最後に、SkillTrace は agent に作業を振り返らせます。  
Reflection によって、たとえば次のような情報を取得します。

* どの skills を使ったと思っているか
* どの skill files を読んだか
* どの reference files が作業に影響したか
* どの手順に従ったか
* どんな不確実性が残ったか
* Skill に改善すべき点があるか

Reflection も確実な情報ではありません。  
それでも価値があるのは、相互の情報比較に利用できるためです。

Passive probing では reference file が読まれているのに、reflection では触れられていない。  
Semantic trace では skill を使ったと宣言しているのに、passive trace では対応する file access が見えない。  
すべてがきれいに揃っている。

どれも、debugging に役立つ情報です。  
SkillTrace は、この比較作業を可能とすることを念頭に設計されています。

![SkillTrace 実行の様子](https://static.zenn.studio/user-upload/deployed-images/f1da1ad4d802b222e128851d.webp?sha=324567f540e6864a1a3db5143bfc535f24e561ec)

# Requirements

SkillTrace は、現時点ではコマンドラインベースの（CLI の） agent workflow を対象にしています。インストールと実行に必要なものは次の通りです。

* Node.js 22+
* npm
* Codex CLI、Claude Code、Gemini CLI のいずれか
* macOS または Linux

なお、

* macOS では passive file-access probing に `fs_usage` を使うため、admin password を求められることがあります。
* Linux では `inotifywait` を使うため、`inotify-tools` のインストールが必要になることがあります。

SkillTraceは、対象とする skill ファイルは、`AGENTS.md` ＋ `.agents/skills/`、または `CLAUDE.md` ＋ `.claude/skills/` の構成であることを想定しています。

SkillTrace は pre-alpha の開発者向けツールです。不安定な挙動、OSによる挙動の差異、トレースの取得の失敗などは、大いにありえます。特に、小さなモデルを使うと、自己申告をし忘れる傾向にあります。

# SkillTrace をインストールする

global package として install します。

```
npm install -g skilltrace
```

バージョンを確認します。

local daemon を起動します。

macOS では、passive skill-file access probing のために `fs_usage` を使うので、admin password を求められることがあります。

次に UI を開きます。

Linux container や VM から host machine の browser で UI を開きたい場合は、all interfaces に bind します。

```
HOST=0.0.0.0 skilltrace daemon start
```

ただし、これは trusted local network や isolated development environment でのみ使うべきです。

# 専用 MCP server を登録する

SkillTrace は、semantic skill-usage events を記録するために MCP tools を使います。  
もっとも簡単な setup は次です。

これは、PATH 上で見つかった supported agent CLI すべてに SkillTrace を登録します。  
registration を確認します。

特定の client だけを対象にすることもできます。

```
skilltrace mcp install --agent codex
skilltrace mcp install --agent claude
skilltrace mcp install --agent gemini
```

setup 後に diagnostics を実行します。

何か問題がありそうな場合は verbose mode を使います。

```
skilltrace diagnostics --verbose
```

# まず toy skill で試す

自分の repository を trace する前に、小さな demo project で試すのがおすすめです。このプロジェクトのリポジトリ内で提供しています。

Toy demo では、期待される skill usage が分かりやすいので、UI の見方を掴みやすくなります。以下はその手順です。

```
git clone https://github.com/hideya/skill-trace.git
cd skill-trace
mkdir -p tmp
cp -RP examples/type-fix-demo tmp/type-fix-demo
cd tmp/type-fix-demo
npm install

# daemon がまだ動いていない場合:
skilltrace daemon start
skilltrace mcp install
skilltrace diagnostics

skilltrace start --note "demo type-fix run"
codex "Fix the TypeScript error using the available skill"
# claude "Fix the TypeScript error using the available skill"
# gemini "Fix the TypeScript error using the available skill"
skilltrace stop
```

実行中、AI エージェントが「skilltrace MCP server tool の呼び出しを許可（allow）するか？」といったことを聞いてきたら、「Allow」を選択してください。

小さめの LLM を使うと、時おり、MCPツールの呼び出しがスキップされることがあります。この問題が発生した場合は、より大きなモデルを試してみてください。

その後、ブラウザで

を開きます。

SkillTrace UI に新しい run が表示されるはずです。

Toy demo を clean copy からやり直したい場合は、次のようにします。

```
cd ../..
rm -rf tmp/type-fix-demo
cp -RP examples/type-fix-demo tmp/type-fix-demo
cd tmp/type-fix-demo
npm install
```

この demo の目的は、TypeScript error fix そのものではありません。  
目的は、agent が skill を読んだのか、skill usage を宣言したのか、reference file を使ったのか、作業後にどう reflection したのかを見ることです。

# UI での確認

ブラウザで `http://localhost:7555` を開くと、以下のような main page が見えると思います。  
もしまだ１つしか run していない場合は、項目が１つだけ表示されます。

このページでは、trace runs、status、trace mode、result、model/client context、mode comparison などが確認できます。

![run リストページ](https://static.zenn.studio/user-upload/deployed-images/daf6ffe33d4d9016439935b0.webp?sha=5f12922aa1cae585254401ac4e2238151ab7e51d)

項目の１つを選択すると、その run detail page が表示されます。

![run 詳細ページ](https://static.zenn.studio/user-upload/deployed-images/f42ec2c2a0002684c626fc67.webp?sha=b54c1da95a4c315f09ada6e030625fa0f77fd92e)

run detail page では、次のような情報を見ることができます。

* Captured events の timeline
* Run context
* Git snapshot information
* Captured instruction contents
* Consistency table
* Reflection

特に重要なのは consistency table です。  
ここでは、passive、semantic、reflection の evidence を比較し、skill usage に関する evidence が揃っているかを確認します。

![run 詳細ページ](https://static.zenn.studio/user-upload/deployed-images/f1da1ad4d802b222e128851d.webp?sha=324567f540e6864a1a3db5143bfc535f24e561ec)

たとえば、

* Passive trace は SKILL.md の access を察知したか？
* Agent は MCP を通じて skill usage を宣言したか？
* Final reflection は、その skill が run に影響したと述べているか？
* Reference files は evidence streams 間で一致しているか？

といったことを確認できます。

Passive\_only mode の run は **Pass** ではなく **Captured** と表示されます。  
File access だけでは、skill 利用の証明にはならないためです。  
SkillTrace は file アクセスを確固とした証拠として扱うのではなく、ひとつの evidence stream として扱います。

![run タイムライン](https://static.zenn.studio/user-upload/deployed-images/027ecd6f97a921c91a8afd74.webp?sha=f10c22e6ca7cca62c0d3ed53995f9a25597dac13)

# Trace mode を変えてみる

instrumentation は agent の挙動に影響する可能性があります。  
agent に skill usage を明示的に考えさせ、MCP tool calls で報告させると、agent がより慎重になったり、verbose になったり、通常時とは少し違う挙動をするかもしれません。

そのため、SkillTrace には3つの trace modes があります。

```
skilltrace start --mode full
skilltrace start --mode passive_reflection
skilltrace start --mode passive_only
```

### full

次を記録します。

* passive file access
* live semantic MCP declarations
* final reflection

もっとも情報量が多い mode ですが、agent の挙動にもっとも影響を与えます。skill を開発・debug していて、最大限の visibility がほしいときに使います。

### passive\_reflection

次を記録します。

* passive file access
* final reflection

Skill の実行中には agent に何も要求しません。  
Task flow の実行に対する干渉を減らしたい場合に使います。

### passive\_only

次だけを記録します。

Instruction injection は行いません。  
よって、agent への干渉は最小限になるはずですが、プラットフォーム依存のオーバーヘッドや想定外の影響はありえます。  
また、passive-only mode では file が access されたことは分かっても、それが実際に使われたかは分かりません。

# Mode 間で比較する

同じ target repo について、複数の trace mode で successful run がある場合、runs page から比較できます。  
典型的な流れは次の通りです。

1. full mode で、agent が期待通りの skill を読み、宣言するかを debug する
2. passive\_reflection で、live semantic reporting を減らす
3. passive\_only で、最小限の介入で file access を観測する

Compare Modes は、同じ skill files や reference files がそれぞれの run に現れているかを確認します。

![Compare Modes](https://static.zenn.studio/user-upload/deployed-images/4eef66afd67a6f864fa9843a.webp?sha=b101898f19f90cef54816a942ac5b2d40ed42f0e)

これは、次のような問いに答えるために役立ちます。  
tracing を弱めても、agent は同じ skill を使っているように見えるか？  
observability は、それ自体が agent の挙動を変える可能性があります。  
SkillTrace は、この問題を隠さず、比較できるようにしています。

# 自分の repository で使う

Toy demo がうまく成功したら、自分の repository でも同じ workflow が使えます。その場合、target repo に移動し、トレースをスタートします。

```
cd <repo>
skilltrace start
```

run list に目的を表示したい場合は run に対して note を付けることができます。

```
skilltrace start --note "trying to simplify AGENTS.md"
```

その後、agent task を通常通り実行します。

```
codex "..."
# or
claude "..."
# or
gemini "..."
```

task が終わったら、trace session を止めます。

実行途中に何らかの不具合が見つかり、記録を DB に残したくない場合は、終了時に discard できます。

```
skilltrace stop --discard
```

# Target repo requirements

SkillTrace は現在、2つの instruction profile（Skill ファイルのディレクトリフォーマット）をサポートしています。

### agents

Codex や Gemini CLI 利用者用の、次の構成の repository 向けです。

```
AGENTS.md
.agents/skills/
```

### claude\_code

Claude Code 利用者用の、次の構成の repository 向けです。

```
CLAUDE.md
.claude/skills/
```

そして「スキルごとに1つのディレクトリ」という共通のレイアウトに沿っていることを想定しています。

```
<repo>/.agents/skills
  └── <skill-name>
        ├── SKILL.md
        └── <reference-files>
```

通常、skilltrace start は supported profile を自動検出します。repo に複数の instruction surface がある場合や、明示的に指定したい場合は、次のようにします。

```
skilltrace start --instruction-profile agents
```

または、

```
skilltrace start --instruction-profile claude-code
```

skilltrace start は、選択された instruction file に一時的な tracing-policy instruction を挿入し、.skilltrace/instrumentation.mdを書き、必要に応じて .skilltrace.json を作成します。

skilltrace stop を実行すると、変更されていない場合、それらの一時的な instruction と generated files を削除します。

同時に active にできる trace session は1つだけです。

# 利用した skill の変更状況の確認

Skill ファイルを変更して挙動の確認を繰り返している場合などに、run で実際に使用した skill ファイルの状態を知りたい場合があります。

それを実現するために、target repo が Git worktree 内にある場合には、SkillTrace は run start 時点で skill files の軽量な snapshot を記録します。

記録するものは次の通りです。

* HEAD commit and branch
* Repo 全体のファイルの変更状況
* Skill 関連ファイルの実行時点での diffs
* 変更があるSkill 関連ファイルの実行時点での内容

これは、successful run と failed run を、実行時の skill / instruction state と照らし合わせる際にとても役立ちます。

特に、`AGENTS.md`、`CLAUDE.md`、`.agents/skills/`、`.claude/skills/` を編集しながら試しているときに便利です。ある run が前回と違う挙動をしたとき、その run で使われた skill や instruction surface は、前回と何が違っていたのか？といった疑問に、明確に答えることができるようになります。

Run detail page では、changed instruction files が Run snapshot panel で highlight されます。  
File をクリックすると、その run で capture された plain-text contents を確認することができます（未コミットの変更のある行がハイライトされます）。

![Skillファイルのスナップショット](https://static.zenn.studio/user-upload/deployed-images/61b6271ff45de1123c7548b5.webp?sha=8abc86314ad631f0b17b20f4187238cfb9df29cc)  
![Skillファイルの変更箇所](https://static.zenn.studio/user-upload/deployed-images/1f4a1890f6032fb4b74ca0cf.webp?sha=bc82fc90a20d70d08d206e994a70a7789f7d15d8)

# 内部では何をしているのか

SkillTrace の基本的な考え方は明快で、それは「1つの signal に依存せず、複数の不完全な signals を比較する」です。

内部的には、ざっくり次のような構成です。

![SkillTrace ダイアグラム](https://static.zenn.studio/user-upload/deployed-images/60dd5037f29d31f55341f953.webp?sha=7a672e4a233fa397b6574404ccbbb5c2bb44103e)

### Local daemon

Daemon は local server と web UI を提供します。  
Active trace session の管理や captured events の受信も行います。

### Passive file-access probe

macOS では `fs_usage` を使います。  
Linux では `inotifywait` を使います。  
この probe が、run 中の skill files や reference files への access を監視します。

### MCP semantic logger

SkillTrace は専用のローカルな MCP server を提供します。  
Agent が injected tracing instructions を読むと、SkillTrace MCP tools を呼び出して、skill start、reference read、skill finish などの semantic events を通知するようになります。

### Temporary instruction injection

skilltrace start 実行時に、SkillTrace は対象となるリポジトリのメインとなる instruction file に一時的な tracing policy を挿入します。  
これにより、agent に skill usage reporting の方法を伝えます。  
skilltrace stop 実行時に、その temporary instruction を削除します。

### Post-run reflection

Run の最後に、SkillTrace は agent に対し、作業の振り返りを要求します。  
どの skills、references、files、steps、uncertainties が関係したかをまとめさせます。ただし、これは自己申告ですので、間違えがあるかもしれません。

### Trace store and UI

SkillTrace は run data を local に保存し、UI で表示します。  
run detail page では、passive traces、semantic declarations、reflection が比較できます。  
UI の主な目的は、トレースイベント間の不一致をわかりやすくすることです。

# SkillTrace が目指さないこと

SkillTrace は、汎用の agent observability platform の置き換えは目指しません。一般的な observability tools では、たとえば次のようなものを trace します。

* model calls
* tool calls
* spans
* latency
* cost
* production behavior

SkillTrace が焦点を当てているのは、もっと限定された、しかし独特な「問い」です。それは、「ある agent run において、skill ファイルがいつアクセスされ、どのように利用され、実行にどのような影響があったを、どうのようにして知るか？」です。

SkillTrace は、skill usage 自体を debug するための、complementary local probe です。また現時点では、SkillTrace は postmortem generator でも automatic skill-improvement system でもありません。その手前の段階、つまり skill の利用を debug できるように観測可能にすることに注力しています。

# Known limitations

SkillTrace は pre-alpha です。以下のような制限があります。

* Codex CLI、Claude Code、Gemini CLI が最初のサポートされている command-line workflows です。
* Codex App support はまだありません。
* Passive file-access probing はプラットフォーム依存です。
* macOS passive probing では admin privileges が必要になることがあります。
* Linux passive probing は inotifywait に依存します。
* Semantic traces と reflections は agent による協力に依存しています。
* Reflection の内容は確実ではありません。取りこぼし、取り違い、過剰な報告をする可能性があります。
* instrumentation は model の挙動に影響することがあります。特に full mode ではその可能性が高いです。
* passive\_only mode では file access はわかりますが、それが実際に agent によって使われたかはわかりません。
* SkillTrace は現時点では、observability に注力しており、自動 postmortem generation や skill improvement はサポートしていません。

これらの制約は、単なる実装不足というより、この問題領域そのものの難しさでもあります。Skill の利用状況は、しばしば LLM context に溶け込むため、観測が簡単ではありません。SkillTrace は、その過程を少しでも調査可能にするための実験です。

# Privacy and data

SkillTrace 自体はローカルで実行され、リモートアクセスは必要ありません（UI は Google Fonts を読み込みますi）。ただし、センシティブな開発情報を保存する可能性があります。  
Trace mode や repository の状態によって、取得されるデーターには次のようなものが含まれます。

* skill files and reference files
* injected instrumentation instructions
* Git metadata
* changed-file status
* instruction-relevant files の bounded diffs
* changed instruction-relevant files の bounded plain-text contents
* agent-declared summaries, uncertainties, and file attribution
* MCP semantic logging events
* OS platform、CPU architecture、Node.js version、probe backend などの local runtime metadata

機密性の高い repositories で使う場合は、何が記録されるかを理解した上でご利用ください。Logs、screenshots、exports を共有する前に、取得された runs 情報を確認することをおすすめします。  
local SkillTrace data は次に保存されます：`~/.skilltrace`

# なぜこれが重要なのか

SkillTrace の背後にある長期的なアイデアは、次のようなものです。

> [人類の知識蓄積の単位は「文章」から「実行可能な作業単位」へ移行しつつあるのではないか。](https://note.com/h1deya/n/n20e7b4066fe6)

Skills は、単に共有されただけで「信頼できる再利用可能な知識」になるわけではありません。信頼できる実行可能な集合知の単位になるには、skills には evidence が必要です。

* どのようにして活性化されたのか？
* どのように利用されたのか？
* どこで失敗したのか？
* その失敗がどう改善に反映されたのか？

SkillTrace は、その大きな問題に対する小さな第一歩です。

# おわりに

AI agent skills は、まだ始まったばかりです。

しかし、agents に procedural knowledge を渡すための重要な形式になっていく可能性があります。

agent が複数の skills から選べるようになるなら、私たちは、その skills がどのように activated され、declared され、reflected され、ときには misused されるのかを理解する必要があります。

SkillTrace は、その問題を調べるための小さな local tool です。

Passive file-access traces、MCP semantic declarations、structured post-run reflection を比較し、agent run の中で何が起きたのかを inspect できるようにします。

まずは toy demo で試してみてください。  
そのあと、自分の skill workflow に適用してみてください。

このツールが何かのお役に立てることを願っています！
