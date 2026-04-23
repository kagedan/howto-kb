---
id: "2026-04-22-claude-code-のスキルを中央集権しないで配るchezmoi-dotfiles-スターターキ-01"
title: "Claude Code のスキルを「中央集権しない」で配る、chezmoi dotfiles スターターキット"
url: "https://qiita.com/kamo-shika/items/6c4e74972eeb0d1a6fb2"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-22"
date_collected: "2026-04-23"
summary_by: "auto-rss"
---

# はじめに

Claude Code をはじめとする AI コーディングエージェントで、「スキル（Skills）」が運用の中核になってきています。プロンプトやワークフロー、禁則事項を `SKILL.md` にまとめておくと、エージェントが必要なタイミングで自動的に読み出して振る舞いを切り替えてくれる仕組みです。

ここで実運用の悩みとして出てくるのが、スキルをチームでどう配るかという話です。便利なスキルほど同僚にも使ってほしくなる一方で、全員に全スキルを押し付けるのは筋が良くありません。自分のワークフロー依存のスキルまで巻き込んでしまいますし、他人の環境に合わないものまで配られかねません。

この記事では、自分が運用している dotfiles スターターキットを題材に、中央集権に頼らずスキルを配布する設計を紹介します。スキル運用の参考として読んでもらえればと思います。

# 「チーム共通 skills リポジトリ」だと困ること

最初に検討しがちな方式として、「チームで共通の skills リポジトリを作って、全員そこから pull する」案があります。一見すっきり見えますが、実際に回すと3つの問題が出てきます。

1. 不要なスキルまで全員に配られてしまう
2. メンテナ負荷が中央に集中する
3. 気軽に試行錯誤しにくくなる

スキルの育て方は人それぞれで良いと思っています。むしろ一旦は人それぞれに任せたほうが多様なスキルが生まれて、チーム全体のアジリティ向上につながると考えています。

# 各自が持ち寄る dotfiles 型の配布

代わりに今回採用したのが、各自が自分の dotfiles リポジトリでスキルを持ち、必要な人が必要な分だけ pull するという P2P 型の構成です。

* 自作スキルは自分の dotfiles に置き、そこを source-of-truth にする
* 他人のスキルを借りたければ、その人の dotfiles から install するだけでよい
* 強制も中央管理もせず、「欲しければ使える」状態を作るだけにとどめる

この形を運用しやすくするために作ったのが、[chezmoi](https://www.chezmoi.io/) ベースのスターターキットです。

# スターターキットの構成

リポジトリは [github.com/kamo-shika/chezmoi-dotfiles-starter](https://github.com/kamo-shika/chezmoi-dotfiles-starter) に置いてあります。中身はこれだけです。

```
.
├── .chezmoiignore         # chezmoi が無視するファイル
├── .gitignore
├── README.md
└── dot_claude/            # → ~/.claude/ に配布される
    ├── CLAUDE.md          # グローバルのユーザー指示
    ├── settings.json      # Claude Code の設定
    └── skills/            # ユーザースキル置き場
        ├── example-skill/
        │   └── SKILL.md
        └── skill-management/
            └── SKILL.md   # スキル管理の運用ルール（chezmoi / skills CLI 使い分け）
```

chezmoi の命名規則では `dot_foo` が `~/.foo` に展開されます。つまり `dot_claude/skills/` がそのまま `~/.claude/skills/` に配布され、Claude Code が読める状態になります。

使い方も `chezmoi init` して `chezmoi apply` するだけです。新しいマシンに移っても数コマンドでスキルが復元します。

```
brew install chezmoi
chezmoi init https://github.com/<your-username>/dotfiles.git
chezmoi apply
```

ここまでは普通の dotfiles 管理と変わりません。スキルを3種類に分類して棲み分けさせるのが、このスターターキットのポイントです。

# スキルを「出自」で3分類する

Claude Code の環境で扱うスキルは、出自によって次の3種類に分けられます。

| 分類 | 例 | 管理ツール |
| --- | --- | --- |
| 1. 自作スキル | 自分が書いた `skill-management` や独自ワークフロー | chezmoi |
| 2. 他人のスキル | vercel-labs の [skills.sh](https://skills.sh/) から入れるもの | skills CLI |
| 3. 案件スキル | 特定プロジェクトの規約・ワークフロー | プロジェクト repo |

ここで重要なのが、**出自を混ぜない**という原則です。同じスキルが chezmoi と skills CLI の両方で管理されると、`skills update` で引いた最新版を次の `chezmoi apply` が古い内容で巻き戻す、といった事故につながります。

## 1. 自作スキルは chezmoi で管理し公開する

自分で書くスキルは `~/dotfiles/dot_claude/skills/<name>/SKILL.md` に置きます。編集はこの source 側で行い、`chezmoi apply` で `~/.claude/skills/` に反映します。

配布したければ、dotfiles リポジトリを push するだけで、使いたいメンバーが pull できる状態になります。社内 GHE に push しておけば社内限定で共有できますし、public な GitHub に置けば社外にも共有できます。

## 2. 他人のスキルは skills CLI に任せる

Vercel Labs が公開している `skills CLI`（[skills.sh](https://skills.sh/) 経由）を使うと、他人の公開スキルを一発で install できます。

```
skills add <owner>/<repo> -g         # グローバル install
skills update -g                     # 全部更新
skills find <query>                  # skills.sh で検索
```

install 後の実体は `~/.claude/skills/<name>/` に置かれますが、これを **chezmoi 管理下に入れない**ようにしましょう。理由は前述のとおりで、`skills update` と `chezmoi apply` の両方が同じファイルに手を出すと事故につながるためです。

## 3. 案件スキルはプロジェクトに直置きする

特定の案件でしか使わないスキル（その案件のデプロイ手順や固有のチケット運用など）は、**プロジェクト repo の `.claude/skills/` に直接コミット**します。Claude Code は `.claude/skills/` をプロジェクトスコープとして読む仕様なので、他メンバーが repo を clone すれば自動的に使える状態になります。

個人の dotfiles や skills CLI に入れてしまうと、そのプロジェクトを離れた後も不要なスキルがグローバルに残って邪魔になります。案件固有のものは案件と一緒に消える場所に置く、という原則です。

# 運用ルールを「スキルにして」配る

スターターキットには、運用ルール自体を codify したスキル `skill-management` を同梱しています。

`skill-management/SKILL.md` の description には、スキル関連のあらゆる話題で確実に発火するよう、大量のトリガーワードを並べてあります。雰囲気が伝わるよう一部を抜粋するとこんな感じです。

> Claude Code スキルの作成・追加・更新・削除・配置に関する運用ルールを提供する。……「スキル作って」「スキル追加して」「skills add」「chezmoi でスキル」などの発言、および `~/.claude/skills/` / `~/.agents/.skill-lock.json` / `dot_claude/skills/` への言及があれば必ずトリガーする。

つまりユーザーが「スキル追加したい」と言った瞬間に Claude Code がこのスキルを読み込み、3分類の判定フローに従って「自作か／他人のか／案件か」を確認したうえで、正しいツールで作業してくれます。運用ルールを Wiki に書くのではなく、エージェントに直接読ませる形に寄せているのがポイントです。

この構成によって、次のような副次的な効果が得られます。

* 新しく入った人がルールを知らなくても、同じ運用に自動的に乗れる
* ルールが変わったら dotfiles を push し直すだけで、pull したメンバー全員に伝播する

# 社内 GHE で配るときのハマりどころ

社内で使う場合、dotfiles を社内 GitHub Enterprise（以下 GHE）に置いて、そこから他のメンバーが install する運用になります。このときに skills CLI 側で一つ罠があるので共有しておきます。

`skills add` はホスト名で分岐しており、`github.com` 以外（GHE を含む）は `sourceType: "git"` で登録されます。このケースでは folder hash が空のままになり、その後の `skills update -g` が**エラーも出さずに silently skip**します。原因は CLI 内部で `api.github.com` がハードコードされていて、GHE の API エンドポイントに問い合わせる手段がないためです。

回避策はシンプルで、同じ URL で `skills add` を再実行すると上書き install されます。これが現時点では GHE install の唯一の更新手段です。

```
# 他のメンバーの GHE スキル更新手順
export GH_TOKEN=$(gh auth token -h <your-ghe-host>)
skills add https://<your-ghe-host>/<your-ghe-user>/<your-ghe-user>-dotfiles -s <name> -g -y
```

`GH_TOKEN` 環境変数での明示渡しをおすすめします。`gh auth token` のホスト指定が skills CLI 側で効かないケースを観測しているためです。

このノウハウも `skill-management` スキルの本文に埋め込んであるので、使っているメンバーが「GHE でスキル更新したい」と言えば Claude Code が自然に正しい手順を返してくれます。

# まとめ

スキル配布を中央集権型にすると、柔軟性とメンテ性を両取りするのは意外と難しいものです。一方で、

* 自作スキルは chezmoi で自分の dotfiles に置く
* 他人のスキルは skills CLI に任せる
* 案件スキルはプロジェクト repo に直置きする

という3分類で棲み分ければ、中央集権を避けつつチーム全体で相互利用できる状態が作れます。

さらに運用ルール自体をスキル化してエージェントに読ませておけば、チームがスケールしても規律が維持できます。Wiki を読むコストがゼロになり、人間が覚えておくべきことも減らせます。

この運用自体まだ始めたばかりで、今後どう育っていくかは正直わかりません。発展や新しい気づきがあれば、改めてブログに書こうと思います。

# 参考
