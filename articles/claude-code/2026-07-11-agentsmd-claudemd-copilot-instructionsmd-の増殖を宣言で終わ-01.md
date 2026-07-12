---
id: "2026-07-11-agentsmd-claudemd-copilot-instructionsmd-の増殖を宣言で終わ-01"
title: "AGENTS.md / CLAUDE.md / copilot-instructions.md の増殖を、宣言で終わらせる"
url: "https://zenn.dev/takashi_m_jp/articles/d138b040d02172"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "AI-agent", "zenn"]
date_published: "2026-07-11"
date_collected: "2026-07-13"
summary_by: "auto-rss"
query: ""
---

> 🔗 この記事は <https://blog.tak3.jp/ja/blog/declarative-agent-instructions/> からの転載です（一次情報源）。

リポジトリを開くと、ほとんど同じことが書かれたエージェント向け指示ファイルが、もう何個も並んでいる — `CLAUDE.md`、`AGENTS.md`、`.github/copilot-instructions.md`。本稿は、この増殖を手で同期し続けるのではなく、宣言と検証で終わらせる方法を書く。前回は [basou というハーネスそのもの](https://blog.tak3.jp/ja/blog/introducing-basou/)を紹介した。今回はその手前にある、もっと地味で、もっと多くの人が踏んでいる問題の話だ。

## 「また指示ファイルが増えた」

ここ1〜2年で、AI コーディングツールはそれぞれ独自の「エージェント向け指示ファイル」を持ち込んだ。プロジェクトのルール、コーディング規約、やってはいけないこと。人間向けの README とは別に、エージェントに読ませる前提のファイルだ。

問題は、ツールごとにファイル名が違うことだ。Claude Code は `CLAUDE.md`、Codex は `AGENTS.md`、GitHub Copilot は `.github/copilot-instructions.md`。同じチームが複数のツールを併用すれば、リポジトリの中に**同じ内容のファイルが3つ**並ぶ。

そして、これらは静かに腐る。片方だけ直して、もう片方が古いまま残る。エージェントに「規約はこうだ」と教えたつもりが、別のツールでは1世代前の規約を読ませている。しかも、どれが最新でどれが腐っているかは、目視では分からない。

この記事のスコープは、個人〜小規模チームの単一リポジトリ運用だ。全社ポリシーの配布のような大掛かりな話ではなく、「手元の repo で指示ファイルが増えていく」問題を、現実的な手数で片付けることを狙う。

## なぜ1つにまとめられないのか

素朴には「AGENTS.md 1つに統一すればいい」と思う。実際、AGENTS.md は事実上の共通フォーマットになりつつある。エージェント向けの「README」として設計されたオープン仕様で、2026年なかば時点で [Agentic AI Foundation](https://agents.md/)（Linux Foundation 傘下）がスチュワードとなり、20を超えるツールが読み、6万を超える OSS リポジトリが採用する。Codex CLI、Cursor、Windsurf、Aider、Zed……主要どころはほぼ AGENTS.md に寄せ、GitHub Copilot も coding agent では AGENTS.md を読むようになった。Google の新しい面々（Jules など）も同様だ。

寄せなかったのが Claude Code だ。Claude Code が読むのは `CLAUDE.md` であって、`AGENTS.md` ではない。フォールバックとして読むわけでもない（「無ければ AGENTS.md を読む」という説は誤り）。試しに AGENTS.md しかないリポジトリで Claude Code を起動しても、エラーは出ない。プロジェクト指示が0件のまま、何事もなく動く。統一したつもりのチームで、いちばん静かに壊れるのがここだ。「AGENTS.md をサポートしてほしい」という要望は [anthropics/claude-code の issue #6235](https://github.com/anthropics/claude-code/issues/6235) に数千のリアクションを集めているが、2026年7月時点の公式ドキュメントでもロードマップの気配はない。

整理すると、対応表はこうなる（2026年7月時点）。

| ツール | 読む指示ファイル |
| --- | --- |
| Claude Code | `CLAUDE.md`（`AGENTS.md` は読まない） |
| Codex CLI | `AGENTS.md` |
| GitHub Copilot | `.github/copilot-instructions.md`（coding agent は `AGENTS.md` も読む） |
| Cursor | `AGENTS.md`（`.cursor/rules` は現役の別機構。旧 `.cursorrules` は非推奨） |

Claude Code を使う限り `CLAUDE.md` は消せない。AGENTS.md に統一しても、Claude Code のためだけに二重管理が残る。この1点の非対称が、「1ファイルに寄せれば終わり」を成立させない。

## 素朴な解決策と、その限界

### 全部にコピペする

いちばん素朴なのは、同じ本文を各ファイルにコピペすることだ。初回はこれで動く。破綻するのは2回目以降で、規約を1行直すたびに N 個のファイルを直す義務が生まれる。人間は必ずどこかを忘れる。そして前述のとおり、どれが腐ったかは見えない。同期のコストと、腐敗を検知できないこと。この2つがコピペの本質的な限界だ。

### 1ファイルに集約して import で参照する

Claude Code には `@path` の import 構文がある。`CLAUDE.md` の先頭に `@AGENTS.md` と1行書けば、起動時に AGENTS.md の中身がそのまま展開されて読まれる。

```
<!-- CLAUDE.md -->
@AGENTS.md
```

これは筋がいい。本文の実体は AGENTS.md に一本化され、CLAUDE.md は1行のスタブで済む。共通本文に**ツール固有の指示を足せる**のも import ならではだ — Claude Code にだけ効かせたい規約があるなら、スタブの2行目以降に書けばいい。ただし限界もある。import 構文はツール横断で共通ではない（Copilot の `.github/copilot-instructions.md` に同じ手は効かない）。そして両ファイルとも本文を持ちうる形なので、「スタブは1行のまま」という規律が崩れれば、乖離はまた再発する。

なお Claude Code の `/init` を AGENTS.md のあるリポジトリで実行すると、既存の AGENTS.md を読んで関連部分を生成される CLAUDE.md に取り込んでくれる — が、これは参照ではなく**コピー**だ。一本化が目的なら、import の1行を手で書くほうが筋がいい。

### symlink で1実体に束ねる

もっと直接的なのは、ファイルシステムのレベルで「実体は1つ」にしてしまうことだ。`CLAUDE.md` を `AGENTS.md` への symlink にすれば、Claude Code が `CLAUDE.md` を開いたとき、OS が透過的に AGENTS.md の中身を返す。ツール側は symlink を意識しない。「symlink を追ってくれないのでは」という心配は、少なくとも**読み取り**については無用だ。開くのはツールでも、辿るのは OS だからだ。実際、Claude Code の公式ドキュメント自身が `ln -s AGENTS.md CLAUDE.md` を選択肢として挙げている。

単一リポジトリなら、これが最も手堅い。以下で実際の手順を示す。

## 実践 — symlink で正本1つに束ねる

### トポロジ

`AGENTS.md` を正本（hub）とし、他のファイルはそこへ向く spoke にする。

```
myrepo/AGENTS.md                          # 正本（実体ファイル・ここだけを編集する）
myrepo/CLAUDE.md                          -> AGENTS.md
myrepo/.github/copilot-instructions.md    -> ../AGENTS.md
```

正本を AGENTS.md にするのは、いちばん多くのツールが素で読むフォーマットだからだ。将来 Claude Code が AGENTS.md をサポートすれば、spoke を1本減らせばいいだけになる。

### コマンド

```
# 既に CLAUDE.md に本文がある場合は、まず実体を AGENTS.md へ移す
git mv CLAUDE.md AGENTS.md

# CLAUDE.md を AGENTS.md への symlink にする
ln -s AGENTS.md CLAUDE.md

# Copilot 用（.github/ の中から見た相対パスに注意）
mkdir -p .github
ln -s ../AGENTS.md .github/copilot-instructions.md
```

相対パスにしておくのがコツだ。リポジトリをどこにクローンしても、リンクは repo 内で完結して壊れない。

### Git での扱い

git は symlink を「モード `120000` の blob（中身はリンク先パス）」として素直に記録する。だから symlink はそのまま commit でき、クローン先でも復元される。

```
$ git ls-files -s AGENTS.md CLAUDE.md .github/copilot-instructions.md
120000 …  .github/copilot-instructions.md  # symlink
100644 …  AGENTS.md                        # 実体
120000 …  CLAUDE.md                        # symlink
```

注意点は Windows だ。symlink を正しくチェックアウトするには `core.symlinks=true` と、開発者モードや権限が要る。それが無い環境では、symlink がリンク先パスを中身に持つただのテキストファイルとして展開されてしまう。Windows を混ぜるチームは、この点だけ事前に確認しておくとよい（一般論として。筆者は macOS 運用だ）。

### この方式で足りなくなる場面

symlink は単一リポジトリでは十分だが、範囲が広がると3つの問題が顔を出す。

1. **公開リポジトリと非公開の中身。** 指示ファイルが非公開の計画情報を含む場合、実体を公開 repo の履歴に入れれば中身がそのまま公開される。symlink にしておけば中身までは漏れないが、それでもリンク先のパス — 非公開側のディレクトリ構成 — は履歴に残る。
2. **複数リポジトリで同じ正本を使いたい。** repo が増えるほど、手でリンクを張る運用は破綻する。
3. **配線が静かに腐る。** リンクが欠ける・壊れる・別の場所を指す、といった状態を目視で追えない。指示ファイルの腐敗を、今度は symlink のレイヤーで再発させることになる。

要するに、symlink は「1実体に束ねる」は解くが、「宣言」と「検証」は解かない。手で張って、手で確かめ続けるしかない。

## 一歩進める — 正本を宣言し、配線を検証する

ここまでは、1つのリポジトリの中で完結する話だった。ここからは §1 で切ったスコープの外縁 — リポジトリが増え、公開と非公開が混ざり始めたときの話になる。発想はこうだ。

> **正本を1つ宣言し、各ツールへの配線は生成し、その配線を検証する。**

この3拍子に、専用ツールは要らない。正本の場所を1回だけ書き（宣言）、リンクは数行のスクリプトで張り（生成）、CI に `git ls-files -s` の期待値を diff する数行を置けば形は守れる（検証）。手で symlink を張る運用との違いは、「あるべき配線」が文書ではなくコードとして存在し、崩れたら機械が教えてくれることだ。

筆者が実際に使っているのは、これを [basou](https://basou.dev) に載せた形だ。basou は AI コーディングエージェントを操縦するためのハーネスで、その一機能として、エージェント指示ファイルの配線（wiring）を宣言的に扱う。以下の記述は v0.32.0 時点のものだ。

### 宣言する

リポジトリとその属性（visibility＝公開/非公開、language など）を manifest に宣言する。正本の本文は、非公開の「アンカー」— 正本を集約する側のリポジトリ — に1か所だけ置く（`agents/<repo>/AGENTS.md`）。各 repo の指示ファイルは、そこへ向く配線として扱われる。

トポロジは §4 と同じ hub-and-spoke だが、hub がアンカーの正本を指す点が違う。

```
<repo>/AGENTS.md                          -> <anchor>/agents/<repo>/AGENTS.md   # hub -> 正本
<repo>/CLAUDE.md                          -> AGENTS.md                          # spoke -> hub
<repo>/.github/copilot-instructions.md    -> ../AGENTS.md                       # spoke -> hub
```

正本はアンカー側の1ファイル。各 repo の AGENTS.md はそれを指す **gitignore された symlink** になる。だから正本（非公開の計画情報を含みうる）は一度だけ編集され、どのツールも symlink 越しに読み、公開 repo の履歴には決して入らない。

### 生成する

配線は手で張らず、生成させる。

```
basou project derive    # 宣言から配線一式を生成（dry-run 既定・--apply で書き込み）
```

`derive` は manifest から、各 repo の symlink・正本の定型ブロック・公開 repo の `.gitignore`・複数 repo を束ねるワークスペースビューを依存順に作る（個別に回す `symlinks` / `preset` / `gitignore` / `workspace` もある）。いずれも**非破壊**だ。欠けているものだけを作り（`preset` は自分の生成ブロックだけを更新し、手書きの本文には触れない）、既存ファイルの上書きや、別の場所を指す symlink の張り替えはせず、衝突は「衝突」として報告して人間に委ねる。既存の手書き AGENTS.md をこのトポロジへ取り込む `retrofit` もある。

### 検証する

そして、配線を検証する。ここが symlink の手運用に無かったピースだ。

```
$ basou project check     # 宣言 vs 実配線の drift を洗い出す（read-only）
✅ Every present repo's and the view's instruction files (AGENTS.md + spokes) are wired as declared.

$ basou project wiring    # 配線とプライバシーリスクの点検（read-only）
✅ No instruction file is tracked by git in a public-facing repo (no privacy risk).
```

`check` は「正本が欠けている」「spoke が足りない」「衝突している」といった drift を報告する。`wiring` はさらに踏み込んで、**プライバシーリスク** — 公開 repo が指示ファイルを git 追跡してしまい、非公開の正本の中身を公開履歴に晒しかねない状態 — を洗い出す。目視では追えなかったものが、コマンド一発で判定として出る。

上の出力は作例ではない。この記事を書いているブログのリポジトリで、いま実行した実物（抜粋）だ。そしてこのブログの symlink は、basou の配線機能を通さず、§4 の手順どおり**手で張った**ものだ。あとから manifest に宣言を足して `check` を回しても、直すものは何も出てこない — 手で張った配線が、宣言との突き合わせをそのまま通る。§4 と §5 は置き換えの関係ではなく、同じ形への収束だ。手で始めても、何も無駄にならない。

### 例外 — 自己完結した非公開リポジトリ

いつも hub-and-spoke でアンカーに寄せるわけではない。いま例に出したこのブログのリポジトリは非公開で、`AGENTS.md` を**実体ファイルとして持ち、symlink ごと git に commit している** — §4 で見せた `git ls-files` の出力は、実はこのリポジトリそのものだ。manifest の宣言も、実物は次の3行しかない。

```
repos:
  - path: .
    visibility: private
    language: ja
```

非公開ゆえに漏洩リスクがないので、正本を外のアンカーに集約するより、指示文書の編集も diff もリポジトリ内で完結させるほうが素直だ — 自分自身がアンカーを兼ねる、単一リポジトリの形だ。basou では、こうして「指示ファイルを設計どおり commit する」リポジトリを `instructions: self` として宣言できる。宣言された repo は、指示ファイルを追跡していてもプライバシーリスクとは判定されない。self が本領を発揮するのは、OSS が contributor に読ませるために AGENTS.md をあえて commit する**公開**リポジトリのほうで、非公開 repo なら宣言がなくとも visibility だけで判定は通る（上の `wiring` の出力がそれだ）。公開 repo は正本を隠して配線する、自己完結でよい repo は正本ごと commit する — この使い分けまで宣言で書けるのが、手運用との差だ。

### 正直な位置づけ

先に出口を書いておく。単一リポジトリで、ツール別の差分も要らないなら、**§4 の symlink で終わっていい**。このブログ自身、いまもその形のままだ。逆にエージェント別に固有の指示を足したくなったら、それは §3 の import の領分で、symlink 完全統一（も basou の配線も）は答えを持たない。

そして念のため書いておくと、basou は筆者自身のハーネスで、まだ単著者のドッグフード段階だ。ここで薦めたいのは製品ではなく、**発想の転換**のほうだ。「N 個のファイルを手で同期する」から「正本を1つ宣言して、配線は生成・検証させる」へ。symlink を手で張るだけでも半分は今日から手に入るし、検証も CI の数行から始められる。basou は、その3拍子を manifest 1枚に載せた一例にすぎない。basou 自体が何者かは[前回の記事](https://blog.tak3.jp/ja/blog/introducing-basou/)に譲る。

## まとめ

* AI コーディングツールごとに指示ファイル名が違う（`CLAUDE.md` / `AGENTS.md` / `copilot-instructions.md`）。AGENTS.md が事実上の標準に寄る一方、**Claude Code は `CLAUDE.md` しか読まない**ため、1ファイルには寄せきれない。
* 手を動かす第一歩は **symlink**。`AGENTS.md` を正本にし、`CLAUDE.md` などをそこへの symlink にすれば、実体は1つになり、ツールは透過的に読む。git も `120000` blob として素直に運ぶ（Windows だけ要注意）。
* symlink は「1実体に束ねる」は解くが、公開/非公開の混在・複数 repo・配線の腐敗までは解かない。そこからは **宣言（正本1つ）・生成（配線）・検証（drift とプライバシーリスク）** の3拍子に載せ替える — 専用ツールがなくても、CI の数行から始められる。
* 指示ファイルの管理そのものを、手の同期から、人間の宣言とツールの生成・検証へ。指示ファイルの配線もまた、人間が握るべき手綱の一本だ。希少なのは、やはり制御だ。
