---
id: "2026-05-27-ふたつの-claudecode-と-cowork-個人開発者の使い分けガイド2026年5月版-01"
title: "ふたつの Claude（Code と Cowork） — 個人開発者の使い分けガイド【2026年5月版】"
url: "https://qiita.com/ryoji9702/items/e0607178425da45656b4"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "AI-agent", "LLM"]
date_published: "2026-05-27"
date_collected: "2026-05-28"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code がリリースされてから 1 年以上が経過していますが、今年に入って Claude Cowork というものが出てきました。Claude Code と何が違うの？と疑問に思っていたので調査してみました。

2026 年時点、Anthropic の「Claude を使ってエージェント的に仕事を進める」入口は大きく分けて 2 つあります。

- **Claude Code** — 2024年11月リリースの、ターミナルで動くコーディング・エージェント CLI
- **Claude Cowork** — 2026年1月リリースの、同じエンジンを Desktop GUI に載せたナレッジワーカー向け製品

どちらとも裏側のアーキテクチャ（Claude Agent SDK / MCP / Skills / Subagent）がほぼ共通していて、Anthropic も「Cowork は Claude Code を非エンジニア向けに着替えさせたもの」と説明しています。インタビュー記事によれば Cowork は少人数チームが短期間で立ち上げた製品で、コードの大半が Claude Code によって書かれました（[The New Stack のインタビュー](https://thenewstack.io/anthropic-takes-claude-cowork-out-of-preview-and-straight-into-the-enterprise/)）。

「同じエンジン」と言われても、**実際に使うときは UI / 想定ユーザー / 機能アクセスがかなり違う**ので、両方使っている人ほど「結局どっちで何をやればいいんだ」が判断しづらくなりがちです（自分もそれに陥っていました）。本記事では、Pro プラン（$20/月）でも触れる範囲を中心に、両者を **並べて** 整理します（Pro プランの契約で両方使えます）。

### 対象読者

- Claude Code と Cowork の両方を触ったことがある／触ろうとしている人
- 個人開発で AI エージェントの棲み分けを整理したい人
- 「両方契約しているが、結局どっちで何をやればいいか」を一度言語化したい人

### この記事でわかること

- 両者のアーキテクチャ的な共通点と差分
- 価格・配布・運用での実務的なハマりどころ
- Cowork の "中身"（Linux VM サンドボックス）が運用に効いてくる場面
- 個人開発者目線での現実的な使い分けルール

## やりたいことで使い分ける

![2026-05-26_fig1_decision_tree.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4437970/20f89960-c86f-42df-8c7c-e3d70eba2556.png)


結論をざっくり言うと **「git の中やコード管理は Code、それ以外は Cowork」** で、やりたいことを基準に Claude Code と Claude Cowork に役割を持たせるのがいいです。理由は記事の後半で詳しく見ますが、第一の理由は両者を同時に同じファイルで作業させると **キャッシュ・undo・git の競合** が起きるため、1 つの作業は片方で完結させた方が事故は少なくなります。

## 1. 共通アーキテクチャ：実は中身はほぼ同じ

ここを押さえておくと混乱しないのが、**両者は同じ Agent SDK の派生製品**という点です。具体的には次の 6 つが共通基盤として両者に乗っています。

- Claude モデル（Opus / Sonnet / Haiku）
- Claude Agent SDK（旧 Claude Code SDK のリネーム）
- MCP（Model Context Protocol）
- Skills（`SKILL.md` ＋同梱リソースのパッケージ）
- Subagent / Task tool
- プラグイン（Skill＋MCP＋Subagent をまとめた配布単位）

片方で書いたスキルやプラグインは、共通基盤を通してもう片方でもほぼそのまま動きます。**「Skill を書く」「MCP サーバを足す」レベルの投資は二重にならない**ということは覚えておくといいです（[Anthropic 公式](https://www.anthropic.com/product/claude-cowork)）。

ただし、**UI レイヤと「外向きの API」が違う**ため、機能の生やし方や運用パターンは別物になります。

## 2. UI / 入力モデルの違い

ここが両者の体感差を決めるいちばん大きい部分です。

### Claude Code（CLI）

- `claude` コマンドで起動し、**ターミナル上で対話可能**
- VS Code や Cursor など IDE の拡張機能が充実
- 入力は **テキスト ＋ スラッシュコマンド**（`/model`, `/permissions`, `/clear` など）
- 状態やコンテキストは **作業ディレクトリの `CLAUDE.md` / `.claude/`** に持つ
- 決まったタイミングで差し込みたい処理の拡張は **`hooks`（settings.json で `SessionStart` / `PreToolUse` 等にシェル・LLM・HTTP を仕込める）**（[Claude Code Docs / Hooks reference](https://code.claude.com/docs/en/hooks)）を使える
- Git / Bash / Vim ユーザーには素直に馴染む

### Claude Cowork（Desktop GUI）

- macOS / Windows のネイティブアプリで動作（Windows は 2026-02-10 に Mac と機能パリティで一般提供）
- 入力は **チャット ＋ Apple/Windows ライクな GUI ウィジェット**（タスクリスト、Artifacts、AskUserQuestion の選択肢ボタン、`request_cowork_directory` のフォルダピッカー等）
- 状態は **マウントされたフォルダ ＋ Cowork 内の `Projects`** に保持される
- **プラグイン**（Skill＋MCP＋Subagent をまとめて 1 つ）＋ **Skills**（個別）＋ **scheduled tasks** による拡張
- 「ターミナル？ それなんですか？」というユーザーに渡してもセットアップが回る

ざっくり言えば、**Claude Code は "シェル＋ Markdown" 寄り、Cowork は "アプリ＋ボタン" 寄り**です。同じことが両方で出来るケースは多いですが、**慣れているメンタルモデルが違うユーザーに渡したときの初動が大きく変わります**。

## 3. 機能差マトリクス

両方を触っていると気づく細かい違いを、表でまとめました。

| 観点                   | Claude Code                            | Claude Cowork                          |
| -------------------- | -------------------------------------- | -------------------------------------- |
| 主インターフェース            | CLI                                    | Desktop GUI                            |
| OS                   | Mac / Linux / WSL                      | macOS / Windows ネイティブ                  |
| ファイルアクセス             | 起動した CWD と配下                           | `request_cowork_directory` でマウントしたフォルダ |
| 永続記憶                 | `CLAUDE.md` ＋ `.claude/memory/`        | Projects ＋ `MEMORY.md`（同形式）            |
| スラッシュコマンド            | フル対応（カスタム `.claude/commands/`）         | Skill 起動として実質統合                        |
| Hooks                | フル対応（SessionStart / Pre/PostToolUse 等） | 同等の概念は限定的（GUI 側ハンドラに寄せている）             |
| Subagent / Task tool | Code 側で広く活用                            | 同じく利用可（GUI からは Task ウィジェットで可視化）        |
| Artifacts            | なし（テキスト出力主体）                           | あり（再オープンで自動データ更新する HTML）               |
| 選択肢 UI               | なし                                     | `AskUserQuestion` で選択ボタン提示             |
| スケジューラ               | 外部 cron / GH Actions に委ねる              | `scheduled tasks` を OS 内蔵              |
| プラグイン市場              | 公式マーケット＋ローカル                           | 公式 11 プラグイン＋エンタープライズ向けプライベートマーケット      |
| 想定ユーザー               | エンジニア中心                                | 営業・マーケ・財務・法務など非エンジニア中心                 |

「Claude Code でしか手が届かない」のは **hooks の細粒度制御** と **直接 Bash を扱う系の作業**、「Cowork でしか手が届かない」のは **Artifacts**（後で開くと自動でコネクタからデータを取り直す HTML ビュー）と **GUI 選択肢／タスクウィジェット**、それから **scheduled tasks** あたりです。

## 4. 価格と利用条件（Pro 視点）

両者は **同じ Claude プランの上に乗っている** ため、契約は 1 本でほぼ完結します。Pro（$20/月、年払い $17）以上なら Claude Code も Cowork も両方使えるのが現時点（2026 年 5 月、[claude.com/pricing](https://claude.com/pricing) スナップショット）の建付けです。

「Claude Code を Pro から外す」テストが SNS で炎上 → 撤回されたことが最近ありました。今後の情勢を踏まえると、**Pro での Code 利用は将来的にトーンが変わる可能性**は十分にあります。気になる方は最新の建付けを [Claude 公式 Pricing ページ](https://claude.com/pricing) で確認してください。

## 5. 設定・データ・配布の差（実務でだいたいハマる箇所）

画面や機能からは見えにくい、**運用フェーズで実際に起こりうること**を 3 つだけ挙げます。

### シークレットと設定の置き場所が違う

- **Claude Code**：`~/.claude/settings.json` ＋ `.claude/` 配下のプロジェクトファイル。**plaintext で平置き**するので、リポジトリにコミットしない運用ルール（`.gitignore` / `direnv` / OS のキーチェーン）を自分で組む
- **Cowork**：Cowork 内部の設定ストアに保存され、GUI から登録する。誤って Git に乗ることは無いが、**バックアップ・移行のときに「どこに何があるか」が見えにくい**

同じ MCP サーバを両方で使うなら **2 か所に同じシークレットを書く**ことになります。これは現時点では割り切るしかない部分です。

### Skill / プラグインの配布動線が違う

- **Claude Code**：基本は Git 上で配布。Skill フォルダごと commit → push して他人に `clone` させます
- **Cowork**：プラグインマーケット（公式＋プライベートマーケット）からインストールできるので、Skill 作成に自信がない人でも Skill が使えます。共有は **`.plugin` ファイルでパッケージ化**してマーケット経由できます

開発中は Code で書いて Git で回し、安定したら Cowork のプラグイン化してチーム配布、という **2 段ロケット**にすると現実的です。

### ローカル / クラウドの境界

両者とも **Claude モデル本体は Anthropic API への送信**で動くので、その意味では「ローカル AI」ではありません。違いは **手元のファイルをどこまで読むか**：

- **Claude Code**：起動した CWD 配下のみ。**シェル権限と同じ範囲**で動くため、`.env` などの機微情報が読まれ得る前提で扱う
- **Cowork**：`request_cowork_directory` で **明示的にマウントしたフォルダだけ**読める。マウントしていないディスクは見えない

セキュリティの観点では、**Cowork のほうが「読まれる範囲」が物理的に絞れている**ぶん、コードベースを離れた業務作業に向いています。

## 6. Cowork の "中身" を覗く

ここまで「Cowork は Claude Code を非エンジニア向けに着替えさせたもの」と書きましたが、**「同じエンジン」が実装レベルでどう実現されているか**を押さえると、ハマりどころと棲み分けの線がより鮮明になります。公開情報と複数のリバースエンジニアリング報告から、現時点で見えている実像を整理します。

### 実体は「Claude Code CLI が Linux VM の中で動いている」

Anthropic 自身が **「Cowork は Claude Code エージェントハーネスを Linux VM 内で動かしているもので、Apple Virtualization Framework または Microsoft の Host Compute System を通している」** と説明しています。つまり Cowork は別モデルではなく、**Claude Code CLI を VM 内で走らせ、Claude Desktop がオーケストレーションしているだけ**。実行環境は **Ubuntu 22.04 LTS のフル VM**（Docker コンテナではなく独自カーネル付き）で、Apple Silicon Mac では ARM64 として動作することがリバースエンジニアリングで確認されています（Windows 版は Hyper-V 上の対応アーキテクチャで動作）。

公式 Help Center にもこう書かれています：

> シェルコマンドと Claude が書いたコードはすべて専用 Linux VM 内で実行され、ホスト OS とはプラットフォームのハイパーバイザ（macOS は `Apple Virtualization.framework`、Windows は Hyper-V）で分離される。VM は独自のネットワーク egress フィルタリング、syscall 制限、セッション単位のユーザー分離を行う。

階層構造を図にすると次のようなイメージです。

![2026-05-26_fig2_vm_layers.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4437970/3940157d-66c5-40a0-a98b-32c1b09f342b.png)


ホスト → ハイパーバイザ → Linux VM → Bubblewrap → Claude Code CLI、と 4 段の境界を越えて初めて Claude のコマンドが実行されるイメージです。Computer Use だけはこの階層の外側、ホスト OS の上で直接動きます。

### 「制限が厳しい」と感じる理由：多層防御（sandbox-within-a-sandbox）

単なる VM 分離ではなく、**ハードウェアレベルの VM 分離に加えて、ゲスト内のプロセスを Bubblewrap (bwrap) でさらに制約する** 二重サンドボックス構造になっています。実務でぶつかる制限は次の 4 つ。

1. **ファイル可視範囲が "mount したフォルダのみ"** — ホストフォルダは VirtioFS Bridge 経由で `/mnt/.virtiofs-root/` にマウントされ、選択したフォルダだけが必要なときにマウントされます。**Cowork に見せていないフォルダは VM からは存在しないことになっている**
2. **ネットワークは allowlist 方式** — 依存関係のインストールは許可しつつ、任意の web アクセスはブロック。`pip install` や `npm install` は通っても、見知らぬドメインへの egress は通らない
3. **VM 内でさらに seccomp / bubblewrap** — syscall レベルで `rm -rf /` 的な攻撃を VM 内で封じ込め
4. **セッションごとに VM 状態がクリーン** — 各 Cowork セッションはクリーンな VM 状態で開始され、永続的なマルウェアはセッション間で生き残れない。**逆に言うと「セッションをまたいだ環境構築」が効きづらい**

### 例外：Computer Use だけは VM の外で動く

興味深いのは、**Computer Use は VM ではなくホスト上で動く**点です。Anthropic 自身が：

> Computer use は Cowork が通常ファイル作業やコマンド実行に使う仮想マシンの外で動く。つまり Claude は隔離サンドボックスではなく実際のデスクトップとアプリを操作している。

と明示しています。ブラウザ操作やアプリクリックは VM 内では物理的に無理なので当然そうなるのですが、**ここはセキュリティモデルが切り替わる境界線**なので、業務に組み込む前に理解しておく価値があります。

### この実装が個人運用に効いてくる場面

VM サンドボックスを前提に、棲み分けはより具体的にできます。

- **Git 操作を伴う自動化ジョブ**（コード生成 → push、ニュース収集 → リポジトリ更新など） → Cowork ではなく Claude Code（ローカル WSL2）で走らせる方が合理的です。Cowork だと `git push` の egress が allowlist に依存し、`~/.ssh` をマウントしないと SSH 鍵が見えません。ホスト権限そのままで動く Claude Code のほうが自動化パイプラインを組みやすいです
- **Skill 開発** → Cowork 内 VM だと `/mnt/skills/user/` への書き込みがセッション越しに残らない可能性があるため、Claude Code でローカルに書く方が反復が速い
- **特定フォルダ配下の整理タスク** → フォルダだけマウントすれば完結するので、**Cowork の制限がむしろ安全装置として機能**する

### Office ドキュメント生成では何が変わるか（pptx / xlsx / docx / pdf）

`.docx` / `.pptx` / `.xlsx` / `.pdf` を Claude に生成させる場面では、VM 境界の効き方がもっとも体感しやすくなります。結論から言うと **「バイナリ品質は同じ、でも生成までの摩擦が全然違う」** です。

#### ライブラリ環境

- **Cowork (VM)**：約 1,200 の apt パッケージがプリインストール済み。`numpy` / `pandas` / `matplotlib` / `seaborn`、`Pillow` / `OpenCV`、`python-docx` / `python-pptx` / `openpyxl` / `reportlab`、`pikepdf` / `pypdf` / `pdfplumber`、`pytesseract` あたりが最初から使える。**ただし `apt` でのシステムパッケージ追加は不可**
- **Claude Code (WSL2)**：素のホスト環境なので `pip install python-pptx openpyxl` などを自分で入れる必要があります（一度入れれば永続するのは利点）

#### スキルの成熟度

Cowork には `.docx` / `.pptx` / `.xlsx` / `.pdf` 向けの **ビルトインドキュメントスキルが「最適化済み」で同梱**されており、real formatting レベルでアウトオブボックスで動きます。Claude Code でも生成できますが、**Cowork のほうが「そのまま使える完成度」が高い**のが事実。

ただし注意点は、Cowork の標準 pptx / xlsx スキルは「素朴に綺麗」までで止まる点です。`md-to-pptx` の 4 テンプレート切替や `marp-slide-creator` の Obsidian 連携のような **自作スキルの旨味は出ない** ので、カスタム要件があるほど Claude Code 寄りに振ったほうが結果的に速いです。

#### 個人ワークフロー的な使い分け早見表

| 状況                                                | 寄せ先         | 理由                  |
| ------------------------------------------------- | ----------- | ------------------- |
| 使い捨ての pptx / xlsx を chat ベースで作る                   | Cowork      | 環境準備ゼロ              |
| `md-to-pptx` / `marp-slide-creator` 等のカスタムスキルを活かす | Claude Code | スキル資産がローカルにある       |
| 日本語フォント・LibreOffice 等の OS レベル依存がある                | Claude Code | `apt` が使える          |
| 特定フォルダ配下に「実ファイルとして納品」して終わり                        | Cowork      | mount するだけで完結       |
| 生成後に git push / Obsidian リンク埋め込み / 後続スクリプト連携      | Claude Code | egress / SSH 鍵の壁がない |

すでに Skill エコシステムを構築している場合は、**Office ファイル生成のフロー全体としては Claude Code に寄せておくほうが一貫性が出ます**。Cowork は「自作 Skill を持ち込まない、その場限りの単発作業」に振るのがバランス良さそうです。

### おまけ：Linux 版 Cowork サポートのコミュニティ実装

フル VM ではなく **スタブ ＋ srt によるサンドボックス案** を含む、Linux 向けの Cowork 起動を試みるコミュニティ PR（@chukfinley）が議論されており、WSL2 環境からネイティブに Cowork を叩ける日が来る可能性もあります（公式採用かどうかは別問題）。

> **要点**：Cowork の「制限が多い」と感じる挙動は、ほとんどが **VM 境界 ＋ Bubblewrap ＋ allowlist** の 3 段防御で説明できます。逆に Claude Code のローカル直叩きが速いのは、**この防御層を素通りしている**から。セキュリティとスピードのトレードオフを理解した上で、作業ごとに使い分けるのがいちばん事故が少ないです。

## 7. ユースケース別おすすめ

「同じことが両方できる」とはいえ、**慣れているとどちらに寄せるかは決まってきます**。実体験ベースで分類します。

### Claude Code を選ぶべき場面

- 既存リポジトリのコード生成・修正
- `pytest` / `cargo test` などをループで回しながらのデバッグ
- Git の履歴・ブランチ操作を伴う作業
- CI に組み込む系の自動化（GitHub Actions と相性が良い）
- `hooks` で「コミット前に Lint 当てる」「ツール呼び出し前に許可を取る」を仕込みたい

### Cowork を選ぶべき場面

- 報告書・議事録・スライド・スプレッドシートの作成
- 検索 → 要約 → ファイル保存の "ワンストップ" 知的作業
- 非エンジニアのチームメンバーに渡すとき
- 「毎朝 6 時にニュースを集めて Markdown にして」のような定常ジョブ
- 結果を **後で何度も開いて最新状態を見たい**（Artifacts）

### どちらでも良い場面

- 単発の調べ物・壁打ち
- Skill / プラグインの試作
- MCP サーバの動作確認

ここは **慣れている方** でやるのが結局いちばん速いです。

## 8. ハマりどころ（両方契約して気づいた事故）

2 つを並走させると、地味だが効くトラブルがあります。

1. **同じファイルを両方で開くと undo 戦争になる**。Claude Code が書き、Cowork でも開いていると、片方の "最後の保存" でもう片方の編集が消える。**1 ファイル ＝ 1 ツールに固定**するのが安全
2. **Skill のテストは片方でしか出来ない場合がある**。`hooks` を前提にした Skill は Claude Code 側でしか正しく動かない。逆に `AskUserQuestion` や `Artifacts` を呼ぶ Skill は Cowork 側でしか動作確認できない
3. **MCP 接続情報のスコープが別**。Claude Code は `~/.claude/` 配下、Cowork は Cowork 内部の設定ストア。**同じ MCP サーバを両方で使うなら 2 か所に登録**する必要がある
4. **scheduled tasks は Cowork 側にしかない**。同等のことを Claude Code でやろうとすると、結局 OS の cron / Task Scheduler に逃がす必要がある
5. **Projects（Cowork）と CLAUDE.md（Code）は意外と二重管理になる**。同じプロジェクトを両 UI で触るなら、**Cowork の Project 内に CLAUDE.md を置いて両側から読ませる**のが現実解

## 9. 個人開発者の現実解（筆者の運用）

個人開発でふたつを並走させるなら、**開発フェーズ × 成果物の種類** で線を引くと迷いがなくなります。筆者の運用は次の表に収束しました。

| フェーズ / 作業 | 使うツール | 主な理由 |
| --- | --- | --- |
| 要件定義・アイデア整理 | Cowork | Web 調査・ドキュメント横断・MEMORY.md でブレストが回しやすい |
| 設計 → 実装 → テスト | Claude Code | コードに張り付いて Git / シェル / テストランナーを直接叩ける |
| 成果物レビュー | Cowork | Markdown / pptx / Excel を GUI で開きながら確認できる |
| 文書管理（md / pptx / xlsx） | Cowork | `request_cowork_directory` でフォルダ単位にマウントして整理しやすい |
| Git 管理（commit / push） | Claude Code | VM 境界を越えず、`~/.ssh` などホスト権限で直接動かせる |
| エージェントハーネス（Claude Code 実行構造）の調査・把握 | Cowork | 公開資料・GitHub・関連リポジトリを横断調査するのに向く |

![2026-05-26_fig3_dev_phases.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4437970/ab60d774-47fd-481a-bb13-d8358fa989ea.png)


ざっくり言えば、**「考える・読む・まとめる」は Cowork、「書く・回す」は Claude Code**。同じプロジェクトの中でも、**開発フェーズが変わったらツールを切り替える**のがいちばんスムーズです。

- **要件定義と成果物レビューは Cowork** に寄せる。`md / pptx / xlsx` がドメインの中心になるので、GUI でファイルを開きながらやり取りできる強みが効きます
- **設計〜テストは Claude Code** に寄せる。ファイル編集・テスト実行・Git 操作までホスト権限で完結し、`pytest` / `npm test` のループに乗りやすい
- **共有資産（Skill / MCP / CLAUDE.md）は片方に集約**し、もう片方からは `Read` できる位置に置いて参照だけする。二重管理は事故のもと

「どちらで開くか」を迷う時間がほぼゼロになったのが最大の効果でした。**統合しようとせず "棲み分け線" を物理的に引く**のがコツです。

## まとめ

- Claude Code と Cowork は **中身（Agent SDK / MCP / Skills）が同じ**で、**UI と想定ユーザーだけが違う双子製品**
- Pro 1 本でほぼ揃うので、**どちらを取るかではなく「どこで何をやるか」を線引きする**のが正解
- 並走時の事故（undo 戦争・MCP 二重登録・scheduled tasks の片寄り）だけ意識すれば、両刀運用は十分現実的

**Cowork はリリースから日が浅い**ので、Claude Code 側にしかない hooks のような細粒度制御はこれから順次降りてくると見て良いはずです。今のうちに棲み分け線を引いておけば、機能差が縮まったあとも運用は崩れません。

## 参考

- [Claude Cowork — Anthropic 公式プロダクトページ](https://www.anthropic.com/product/claude-cowork)
- [Cowork: Claude Code power for knowledge work — Claude by Anthropic](https://claude.com/product/cowork)
- [Use plugins in Claude Cowork — Claude Help Center](https://support.claude.com/en/articles/13837440-use-plugins-in-claude-cowork)
- [Get started with Claude Cowork — Claude Help Center](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork)
- [Plans & Pricing — Claude by Anthropic](https://claude.com/pricing)
- [Hooks reference — Claude Code Docs](https://code.claude.com/docs/en/hooks)
- [Anthropic takes Claude Cowork out of preview and straight into the enterprise — The New Stack](https://thenewstack.io/anthropic-takes-claude-cowork-out-of-preview-and-straight-into-the-enterprise/)
- [Anthropic Expands Claude's "Computer Agent" Tools Beyond Developers with Cowork Research Preview — ADTmag](https://adtmag.com/articles/2026/01/20/anthropic-expands-claude-computer-agent-with-cowork.aspx)
- [Anthropic Launches Projects Feature for Claude Cowork Desktop — Cyber Security News](https://cybersecuritynews.com/projects-feature-claude-cowork-desktop/)
- [Claude Code Cheat Sheet 2026 — blakecrosley.com](https://blakecrosley.com/guides/claude-code-cheatsheet)
