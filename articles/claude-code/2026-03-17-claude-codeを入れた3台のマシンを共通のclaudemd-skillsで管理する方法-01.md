---
id: "2026-03-17-claude-codeを入れた3台のマシンを共通のclaudemd-skillsで管理する方法-01"
title: "Claude Codeを入れた3台のマシンを共通のCLAUDE.md, skillsで管理する方法"
url: "https://qiita.com/shunxneuro/items/8ed58f11c4e0e334bbba"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "cowork", "qiita"]
date_published: "2026-03-17"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

## Claude Codeを入れた3台のマシンを共通のCLAUDE.md, skillsで管理する方法 (私の活用事例)

こんにちは。Yamamotoです。初投稿です。

私はAIの研究に従事していてAIエージェントを最近よく触っています。

私の研究ではlaptop PC, GPU work station, Linux serverの三つのマシンを使いスマホもTailnet上で共有して、スマホからもターミナルを覗けるようにしています。

| マシン | OS | GPU | 主な用途 |
| --- | --- | --- | --- |
| PC1 Laptop | Windows + WSL | laptop RTX 4000 | 論文収集・解析・ **Claude Cowork** |
| PC2 Workstation | Windows + WSL | Ada 6000 (48GB) | GPUバウンドな処理・AI学習 |
| PC3 Server | Linux | RTX 4000 | デプロイ・Docker・Web |
| iPhone | iOS | - | Tailscale 経由で SSH 接続して監視 |

しかし、Claude codeをそれぞれのマシンで起動してやっているとCLAUDE.mdなどどのマシンでどう書いたか分からなくなりカオスになります。

そこで共通のコード「claude-config」で管理する方法を考えました。

## claude-config は、この問題を解決するための「設定の司令塔」

1つの Git リポジトリに全マシンの設定をまとめ、どのマシンでも setup.sh を1回叩くだけで環境が整うようにしています。

もう1つ大切にしている考え方があります。今は Claude Code をメインで使っていますが、将来的にCodex、Antigravity など別のツールに乗り換えたり、併用したりすることも十分あり得ます。そのため、特定のツールに依存しない設計にしています。

いわば「引越ししやすい家」を建てているようなものです。

## この記事を読むとわかること

## 1.ファイルから全マシン共通のCLAUDE.mdを生成する仕組み。

小文字の shared/claude.md（原本）からマシン固有の情報を結合して大文字の CLAUDE.md（完成品）を自動生成します。共通ルールの変更は1箇所で済み、git push → setup.sh だけで全マシンに反映されます（§1.2, §3）

## 2. コンテキストウィンドウを守るための分離設計と、エージェントの「記憶」を3層に分けるアーキテクチャ。

活動サマリー（summary.md）やマシンメモリ（memory.md）をあえて CLAUDE.md に含めず、システムプロンプトの肥大化を防いでいます。さらに、エージェントの知識を rules（起動時に必ず読むトリガー）、マシンメモリ（Git 共有される恒久知識）、プロジェクトメモリ（ローカル専用の作業ログ）の3層に分け、知識の寿命と共有範囲に応じた管理を実現しています（§3.1, §5）

## 3. 共通スキルとマシン固有スキルを管理する方法。

全マシンで使うスキルは shared/skills/ に、特定マシンだけで使うスキルは machines//skills/ に置きます。どちらも Git 管理されるため、他マシンから「PC2 にはこんなスキルがある」と把握できます（§5.2）

### 1.1 リポジトリ内の各ファイルが果たす役割

リポジトリにはいくつかのファイルがありますが、それぞれに明確な役割があります。

| ファイル | 場所 | 役割 | 読者 |
| --- | --- | --- | --- |
| `DESIGN.md` | リポジトリ | 設計の「なぜ」を記録する備忘録 | 人間 |
| `shared/claude.md` | リポジトリ | 全マシン共通の指示書。CLAUDE.md の原本 | AI |
| `machines/`<n>`/profile.md` | リポジトリ | マシン固有の環境情報 | AI |
| `machines/`<n>`/memory.md` | リポジトリ | マシン固有の知識の蓄積 | AI |
| `machines/`<n>`/summary.md` | リポジトリ | 活動サマリー。別マシンへの申し送り | 人間 / AI |
| `machines/`<n>`/desktop-instructions.md` | リポジトリ | Cowork / Chat 用の指示（手動コピペ） | 人間 |
| `~/.claude/CLAUDE.md` | ローカル | setup.sh が生成する完成版指示書 | AI |
| `~/.claude/rules/machine-memory.md` | ローカル | memory.md への参照指示 | AI |
| `~/.claude/projects/`<path>`/MEMORY.md` | ローカル | プロジェクト固有の作業ログ | AI |

### 1.2 claude.md → CLAUDE.md ── 全マシン共通の指示を1ファイルで管理する仕組み

小文字の shared/claude.md から大文字の ~/.claude/CLAUDE.md を自動生成する仕組みです。

shared/claude.md はリポジトリに1つだけ存在する「全マシン共通の指示書の原本」です。エージェントに守ってほしいルール、作業の進め方、通知のポリシーなど、マシンを問わず共通の指示はすべてここに書きます。

setup.sh を実行すると、この shared/claude.md にマシン固有の環境情報（machines//profile.md）を結合して、最終的な ~/.claude/CLAUDE.md を生成します。

つまり CLAUDE.md の中身は「共通指示 + マシン固有情報」の組み合わせです。

```
shared/claude.md（共通指示の原本、Git で全マシン共有）
        +
machines/<n>/profile.md（マシン固有の環境情報）
        ↓  setup.sh が結合
~/.claude/CLAUDE.md（完成品、各マシンのローカルに生成）
```

### この設計のメリットは2つあります。

* **共通ルールの変更が1箇所で済む。**  
  shared/claude.md を編集して git push → 各マシンで git pull & setup.sh を実行するだけで、全マシンのエージェントに同じルールが適用されます。マシンごとに設定を書き換える必要がありません。
* **マシン固有の差分だけを分離できる。**  
  「PC2 には強力なGPU がある」「PC3 は Docker ホストである」といった情報は profile.md に書きます。共通指示は触らなくて済みます

## 2. アーキテクチャ ── 全体の仕組み

##### リポジトリ構造（原本）

Git リポジトリの中身はこうなっています。全マシン共通の部分とマシン固有の部分がきれいに分かれている点がポイントです。

~/claude-config/ (Git repo)  
├── shared/  
│ ├── claude.md 全マシン共通の指示（CLAUDE.md の原本）  
│ └── skills/ 共通スキルの原本  
│  
├── machines/  
│ ├── pc1/  
│ │ ├── profile.md マシン環境情報（CLAUDE.md に結合される）  
│ │ ├── desktop-instructions.md Claude Cowork / Chat 用の指示  
│ │ ├── memory.md マシン固有のナレッジ（§3.1 参照）  
│ │ ├── summary.md 活動サマリー  
│ │ └── skills/ マシン固有スキル  
│ ├── pc2/ ...  
│ └── pc3/ ...  
│  
├── DESIGN.md  
└── setup.sh

##### デプロイ後の構造（setup.sh が生成するもの）

setup.sh を実行すると、リポジトリの中身が各ツールが読める場所に配置されます。  
~/.claude/  
├── CLAUDE.md ← shared/claude.md + machines//profile.md を結合した完成品  
├── rules/  
│ └── machine-memory.md ← §3.1 参照（setup.sh 管理外、手動配置）  
└── skills/ ← Claude Code がスキルを探す場所

~/.codex/  
├── AGENTS.md ← 同上（AGENTS.md 形式）  
└── skills/ ← --multi-tool 時のみ接続

### 3. メモリの3層構造 ── エージェントの「記憶」はどこにあるか

Claude Code が持つ知識は3つの層に分かれています。これらは役割がまったく異なるので、混同しないことが重要です。

| 層 | ファイル | ロード方法 | 中身 | Git |
| --- | --- | --- | --- | --- |
| rules | `~/.claude/rules/machine-memory.md` | 自動（起動時に必ず） | memory.md への参照指示 | なし |
| マシンメモリ | `~/claude-config/machines/`<machine>`/memory.md` | rules 経由で Read | マシン固有の恒久知識 | あり |
| プロジェクトメモリ | `~/.claude/projects/`<path>`/memory/MEMORY.md` | 自動（起動ディレクトリ依存） | プロジェクト固有の作業ログ | なし |

なぜこの3層になっているかというと、それぞれの知識の「寿命」と「共有範囲」が違うからです。

##### rules/ は Claude Code がどのディレクトリで起動しても必ず読む特別な場所です。ここに memory.md への参照を置いておけば、マシンメモリが確実に読み込まれます

マシンメモリは Git 管理されているため、PC1 から「PC3 にはどんなサービスが動いているか」を把握できます  
プロジェクトメモリは Claude Code の自動メモリ機能にお任せです。そのプロジェクト固有の作業文脈だけを記録します

##### なお、shared/claude.md にも同じ参照ルールをフォールバックとして書いてあります。rules/ をまだ設定していないマシンでもメモリが読めるようにするための保険です。

machine-memory.md という名前には「マシンのメモリを読みに行くルール」という意味を込めています。rules/ 内に他のルールファイルが増えても、役割がひと目で分かるようにするためです。

## 運用フロー ── 日常のよくある操作

#### スキル内容の編集

リポジトリ内で編集して git push するだけです。symlink 経由で全ツールに即座に反映されるため、setup.sh の再実行は不要です。

#### スキルの新規追加

shared/skills/ または machines//skills/ にスキルを作成 → git push → 各マシンで setup.sh を実行。新しいスキルの symlink を張るために setup.sh が必要です。

#### スキルの削除

リポジトリからスキルを削除 → git push → 各マシンで setup.sh を実行。--multi-tool を使っている場合、壊れた symlink は自動で掃除されます。

#### 指示の変更

shared/claude.md または machines//profile.md を編集 → git push → 各マシンで setup.sh を実行。CLAUDE.md が再生成されます。

#### 活動サマリーの更新

Claude Code のセッション終了時にエージェントが machines//summary.md を自動更新 → git push。別マシンで git pull → ./setup.sh --status でサマリーを確認できます。

#### Claude Cowork への反映

./setup.sh pc1 --desktop を実行すると desktop-zips/ に .zip ファイルが生成されます。Claude Cowork の Customize > Skills からアップロードしてください。カスタム指示は desktop-instructions.md の中身をコピペします。

#### マシン切り替え時のフロー

別のマシンで作業を始めるときの手順です。

cd ~/claude-config && git pull で最新の設定を取得  
./setup.sh を実行（shared/claude.md や profile.md に変更があった場合のみ）  
./setup.sh --status で他マシンのサマリーを確認  
作業開始

summary.md や memory.md だけの変更なら、setup.sh の再実行は不要です。
