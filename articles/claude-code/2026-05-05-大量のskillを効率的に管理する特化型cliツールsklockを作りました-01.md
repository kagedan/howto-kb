---
id: "2026-05-05-大量のskillを効率的に管理する特化型cliツールsklockを作りました-01"
title: "大量のSkillを効率的に管理する特化型CLIツール「sklock」を作りました"
url: "https://qiita.com/artie/items/980b1b48f943e096b46c"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "qiita"]
date_published: "2026-05-05"
date_collected: "2026-05-06"
summary_by: "auto-rss"
---

## はじめに

AI Agentのハーネスまわりの管理には、すでにいろいろな方向性や構造がありますが、  

実際に運用してみると、

- いちばん数が増えやすくて
- いちばん再利用されやすく
- いちばん管理が面倒

になりやすいのは**Skill** で、

数が増えるつれて、単体で完結するよりも、他の Skill を参照しながら組み合わさっていくほうがより効率的になっていきます。

![](https://static.zenn.studio/user-upload/a04aa1130540-20260502.png)

そうなると欲しくなるのは、
**Skill だけに特化した lockfile / graph / workspace 管理**です。

そこで作ったのが **sklock** です。  

https://github.com/artieax/sklock
https://deepwiki.com/artieax/sklock
https://deepwiki.com/search/-1-2-oss-3-1_ae5cfc1a-aaf5-467a-8d58-affb6b2643c2?mode=fast

sklockを使うと自動的に`SKILL.md` ベースの Skill workspace をスキャンして、依存関係を解決し、`skill.lock` を生成し、`tree` や `graph` で構造を見える化できます。 

しかも、GitHub のリンクからそのまま導入できるので、

AI に雑に以下のようにurlを渡すだけで即導入して効率化できます。

```
https://github.com/artieax/sklock を導入して、skillを管理したいです
```

プロジェクト内に増えるファイルとしては
- 各種skillのfront matter
- skill.lockファイル

だけなので、入れようと思ったらすぐに入れられるし、外そうと思ったらすぐに外せます。

なので、リスクなく始めることができます。

## なぜ今、Skill管理だけに特化したライブラリを作ったのか

理由は単純で、Skill は書きやすく、配りやすく、再利用しやすいからです。  

個人的にもこの1ヶ月でも200〜300個のSkillを作成していて、依存関係の管理に非常に危機感を覚えていた節があります。

これからのSkillは1個作ると終わりではなく
- この Skill の中の処理を切り出したい
- この前作った Skill を別の Skill から呼びたい

という形で、どんどん派生していきます。

この段階に入ると、必要なのはSkill を1個作る方法ではなく、

**増えていく Skill を壊さず育てる方法**です。  

sklock は、そのための基盤として作りました。

## 他のツールと比べたときの sklock の立ち位置

sklock の立ち位置を一言でいうと、**配布やレジストリ中心のツールではなく、再帰的な skill workspace の内部管理に強いツール**です。

特に強いのは、`SKILL.md` をベースにした **tree 型の skill 構造** をそのまま扱えることです。  
大きな Skill の中に sub-skill をネストし、その構造を `tree` で見て、依存関係を `graph` で確認し、`skill.lock` で workspace 全体の状態を固定できます。

| ツール | 主に強い領域 | sklock より強いところ | sklock が強いところ |
|---|---|---|---|
| **sklock** | 再帰 skill workspace の管理 | - | `SKILL.md` ベースの nested skill tree、`skill.lock`、`tree` / `graph` / `why` / `explain`、workspace drift 検知 |
| **skillpack** | deterministic lockfile / bundle / sign | bundle、ed25519 署名、deterministic tarball、CI verify | bundle / 署名よりも、**tree 型 skill workspace の可視化と内部把握**にフォーカスしている |
| **PSPM** | npm 的な install / registry / deployment | private registry、central store、symlink 配置、publish / search | registry-first ではなく、**workspace-first で nested skill 構造を扱える** |
| **skillfile** | manifest 駆動の declarative 管理と cross-tool deploy | `Skillfile` / `Skillfile.lock`、exact commit pin、patch 運用、複数 platform deploy | deploy よりも、**ローカルの skill tree を解析して管理する体験**が強い |
| **APM** | skills を含む agent package 全体の統合管理 | prompts / hooks / plugins / MCP servers まで一元管理、transitive dependency、policy、pack/distribute | 守備範囲を絞っているぶん、**skill-only の軽さ**と**tree 型 workspace への集中**がある |
| **vercel-labs/skills** | open skills の install / update CLI | GitHub 由来の skills を入れる体験、skills-lock.json による追跡 | `tree` / `graph` / `why` のような **workspace 内部構造の把握**に強く、nested skill 設計を前提にしやすい |


この比較で伝えたいのは、sklock が**全部入りで**はないということです。  

むしろ逆で、**Skill にだけ絞っているからこそ、階層構造を持つ tree 型の Skill workspace をちゃんと扱える**のが強みです。

配布、署名、レジストリ、クロスツール deploy を主役にするツールはすでにある。 

その中で sklock は、**増えすぎた Skill を workspace 内でどう壊さず育てるか**に集中しています。

## APMのような総合管理があっても、なぜSkillだけにフォーカスするのか

総合的な AI package 管理の方向性はすでにあります。 

ただ、hook,command,rule, MCP serverと合わせてSkillも扱おうとすると、
どうしても管理としてはやや複雑になりがちで、シンプルにSkillだけで管理したいという需要は根強くあると思います。

Skillだけは今エンジニア、非エンジニア問わず圧倒的に人気で

そのためSkillをなんとなく扱っていると

- どの Skill がどの Skill を参照しているのか分からない
- nested な Skill をどう整理するべきか分からない
- lockfile がなく、workspace の状態を固定できない
- CI で drift を検知できない
- 適当に作ってくれているけど、無駄にtokenを消費している気がする
- 同じ機能は参照させたりした方が効率的だと感じる

となりがちです。

だからまず今最も世の中的に需要があるのは全部入りの大きな仕組みより、
**Skill だけに深く小さく効く仕組み**です。  

sklock はそこにフォーカスしています。

## なぜSkillの需要が特に大きいのか

![](https://static.zenn.studio/user-upload/148526dc5417-20260502.png)

Skillは、今最も世界で利用され始めている再利用単位の1つです。

prompt単体よりもより進化した機能を持たせやすく、plugin や MCP よりも導入コストが低い。  

referencesやscriptsといった構造でpromptとプログラムの境界を溶かせて融合しているので、
**非エンジニア、エンジニア問わずいかなる人**でも使いやすい。

さらにハーネスエンジニアリングにおいて

- feedforward(前学)
- feedback (後鞭)

※ 前学(ぜんがく)、後鞭(こうべん)は筆者が最近気に入ってるオリジナルの和訳です

のどちらのフェーズでも、モデルの性能に対して壊れにくく活躍できる。


だから Skill は人気が出やすいし、数も増えやすい。  

そして、数が増えるなら、当然管理の問題が発生します。

sklock は、この人気があるからこそ管理が必要になるという、

かなり素直な問題に対するアンサーです。

## Skillは単体ではなく、他のSkillを参照して使うのが自然

たとえば、レポート作成 Skill の中で、

- 情報収集
- 要約
- 引用整形
- 出力フォーマット調整

のような処理を全部1枚の巨大な Skill に押し込むより、それぞれを別 Skill に分けて参照したほうが再利用しやすいです。

こうなると Skill は、ただのメモではなく、**依存関係を持つ構成要素**になります。

そして依存関係を持つなら、解決、可視化、固定、検証の仕組みが必要になります。 

sklock はそこを CLI と lockfile で扱えるようにします。

## sklockを使うと何がうれしいのか

sklock の価値は、単に Skill を並べて読むことではありません。  
**増えた Skill workspace を、構造ごと扱えるようになること**です。

具体的には、次のようなうれしさがあります。

- `SKILL.md` をスキャンして依存関係を解決できる
- `skill.lock` で workspace の状態を固定できる
- `tree` で階層構造を見られる
- `graph --mermaid` で依存グラフを可視化できる
- `why` や `explain` で影響範囲を追える
- `check --frozen` で CI から drift を検知できる

つまり sklock は、Skill を「書く」ためのツールというより、**Skill を継続運用するためのツール**です。

## sklockは階層構造を持つtree型のSkill workspaceを作れる

ここが sklock の一番大きい特徴です。

sklock は、Skill を flat に並べるだけでなく、
**Skill の中にさらに Skill を持てる tree 型の workspace** を前提にしています。  

つまり、大きな Skill の内部に `skills/` ディレクトリを置き、その下に sub-skill をネストしていけます。

これはかなり重要です。  
なぜなら、現実のタスクは最初から flat ではないからです。

- 大きな仕事がある
- その中に小さな手順がある
- 小さな手順の中にさらに共通処理がある

この構造をそのまま Skill に写像できるなら、Skill 設計はかなり自然になります。 

sklock はその tree を前提に、発見、依存解決、可視化、lock を行えます。

## 親Skillの中にsub-skillを持てると、何がうれしいのか

親 Skill の中に sub-skill を持てると、大きな Skill をきれいに分割できます。

たとえば「research-report」という親 Skill があったとき、その内部に

- summarize
- fetch-content
- format-output

のような sub-skill を持たせられます。

こうしておくと、

- 親 Skill は大きな目的を表す
- sub-skill は内部工程を表す
- さらに深い sub-skill は補助処理を表す

というように、責務の分割がしやすくなります。

しかも、単にファイルを分けるだけではなく、**tree として見える**のが大きいです。 

あとで見返したときに、
- これはこの親 Skill の内部構造なのか
- workspace 全体で再利用される独立 Skill なのか

が判断しやすくなります。

## flatなSkill管理ではなく、treeで管理できると設計がきれいになる

Skill を flat に並べるだけだと、数が増えたときにすぐ苦しくなります。

- 名前空間が散らばる
- 何が内部実装で、何が外部向け Skill なのか曖昧になる
- 大きい Skill の責務分割が見えない
- 再利用と局所化の境界がぼやける

一方で tree 型にできると、設計に階層が生まれます。

- workspace 全体で使う共通 Skill
- ある親 Skill の内部だけで使う sub-skill
- さらにその下にある補助的な処理

このように、**構造そのものが設計情報になる**わけです。  

sklock の価値は、依存解決だけでなく、この構造をきちんと扱えることにもあります。

## `skill.lock` があると、大量のSkill管理はどう変わるのか

Skill が少ないうちは、**人間の記憶と雰囲気**でなんとかなります。 

でも、増えてくると難易度が上がります。

sklock は `skill.lock` を生成することで、workspace の状態を再現可能な形で固定できます。  

しかも hash も1種類ではなく、

- `contentHash`
- `closureHash`
- `workspaceHash`

という複数の粒度で状態を見られます。

これがうれしいのは、

- その Skill 自体が変わったのか
- 子孫 sub-skill を含む部分木が変わったのか
- workspace 全体が変わったのか

を分けて判断できるからです。

lockfile があると、Skill 管理は

**今どうなってるっけ？ ⇨ この状態です**

ときちんと言える世界に変わります。  

これは大量の Skill を扱うなら、かなり大きな差です。

## `tree` / `graph` / `why` / `explain` があると、リファクタが勘ではなくなる

Skill 管理がつらいのは、増えること自体より、**変更の影響範囲が見えないこと**です。

- この Skill を消して大丈夫か
- どの親 Skill の下に移すべきか
- これを共通化すると何が壊れるか
- 今の依存は妥当か

こういう問いに対して、flat なファイル群だけでは答えにくいです。

sklock は、`tree`、`graph`、`why`、`explain` という形で、構造と依存を追えるようにしています。  

これにより、Skill リファクタリングをなんとなくではなく、
**確認しながら進められる作業**になります。

これは地味ですが、長期運用では**かなり大きい**です。

## sklockはpackage managerというより、Skill workspace managerである

sklock を package manager と呼ぶことはできます。  

ただ、感覚としてはもう少し違います。

sklock が強いのは、レジストリ公開や配布や署名というより
**ローカルの recursive skill workspace を理解して管理すること**です。  

その意味では、package manager というより **Skill workspace manager** と言ったほうが近いと思っています。

- `SKILL.md` を発見する
- nested な Skill tree を解釈する
- dependency graph を解決する
- `skill.lock` を生成する
- workspace の drift を検証する

これらはすべて、**大量の Skill を継続的に育てる**ための機能です。  

sklock は、Skill を配るためだけでなく、**Skill を壊さず増やすための土台**を目指しています。

## まとめ

sklock は、Skill を1個作るためのツールではありません。  

**増え続ける Skill を、tree 構造ごと管理し、lockfile で固定し、graph で把握し、CI で検証できるようにするためのツール**です。

特に大きいのは次の3点です。

- Skill 特化だから、現場で今発生している問題にまっすぐ効く
- OSSのGitHub のリンクをそのまま渡して導入できるので、AI にも人間にも配りやすい
- flat ではなく tree 型の Skill workspace を作れるので、大きな Skill をきれいに分解して育てられる


## 最後に

現在ハーネスエンジニアリングが流行っていますが、

その中で、今まさに本格的な管理が必要になってきているのは、Skill です。

そして、**AIに任せるままに適当に作成している人**も多い状況です。

だから総合管理より先に、Skill だけに深く効くものとして sklock を作りました。

冒頭でも書きましたが、以下をClaude CodeなどのAIエージェントに渡すだけですぐに使い始めることができます。

```
https://github.com/artieax/sklock を導入してskillを管理したいです
```

繰り返しになりますが、プロジェクト内に増えるファイルとしては
- 各種skillのfront matter
- skill.lockファイル

だけなので、入れようと思ったらすぐに入れられるし、
外そうと思ったらすぐに外せますので、すぐにリスクなく使い始めることができます。

ぜひ大量のスキルをなんとなく作ったけど、管理に不安を覚えている方や軽快にもっと効率的にできる方法を探していたという方がいらっしゃったら、導入してみてください。

https://github.com/artieax/sklock
