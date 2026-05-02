---
id: "2026-05-01-claudeで作ったスキルをcodexでも使えるようにした話-スキルの二重管理をやめる-01"
title: "Claudeで作ったスキルをCodexでも使えるようにした話 — スキルの二重管理をやめる"
url: "https://qiita.com/t-tonton/items/c6edc83224329b2aaab9"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "AI-agent", "Gemini", "qiita"]
date_published: "2026-05-01"
date_collected: "2026-05-02"
summary_by: "auto-rss"
query: ""
---

## はじめに

僕は普段、Claude Code と Codex CLI を併用しています。
それぞれ得意なことが微妙に違うので目的に合わせて使い分けたり、片方のトークン上限で詰まったときに切り替えたりしています。

ただ、両方を行き来しているうちに気になり始めたのが、**「片方で作ったスキルを、もう片方でも同じように使いたい」** ということでした。

Claude Code で書いて重宝しているスキルを、Codex に切り替えたときもそのまま呼び出したい。逆に Codex 側で書いたものを Claude Code に戻して使いたい。どちらで作ったスキルでも、どちらからでも同じように使えるとうれしい。

…なんですが、いざやろうとすると、各ツールの規約が違うせいで、同じ内容を 2 回書く必要が出てきます。これが今回の話の出発点です。

## 困っていたこと

具体例で書くと、たとえば「ブランチを安全に main に揃える」みたいなワークフローを Claude Code のプラグインとして `SKILL.md` で書いたとします。Claude Code 上では `/git-sync:update-main` で呼び出せて、これがなかなか便利。

これを Codex CLI でもそのまま使いたい。…のですが、Codex は `~/.agents/skills/` という別の場所を見にいく仕組みで、Claude Code のプラグイン (`~/.claude/plugins/cache/`) とは全然違う規約。

仕方ないので、同じ内容を Codex 用にもう一度書きました。やってみると地味にしんどくて、しかもスキルを増やすたびに発生する。「あれ、これ毎回やるの…?」と気づいたところで、なんとかしたくなりました。

同じパターンはリポジトリ root の指示書にもあります。Claude Code は `CLAUDE.md`、Codex CLI は `AGENTS.md`、Gemini は `GEMINI.md` を、それぞれ自分の規約名で読みに行く。同じ内容を 2 つ 3 つ用意していると drift するし、書いた瞬間からメンテの負債が積もります。

ということで、これをどう解決したかを書いてみます。

## 結論から

結論からいうと、こうしました。

```
[ skills/ ]   ← 本体 (1ソース)
    ↑    ↑
 Claude  Codex
```

スキルの本体は `skills/` に1つだけ置いて、Claude Code 用と Codex 用にはそれぞれ symlink で見せる。これだけで、どっちのエージェントからも同じプロンプトが使えます。

実際のディレクトリ構成はこんな感じです。

```
リポジトリroot/
├── skills/                              # 本体 (agent-neutral, 1ソース)
│   └── git-sync-update-main/SKILL.md
├── plugins/                             # Claude Code 向け wrapper
│   └── git-sync/skills/update-main → ../../../skills/git-sync-update-main
└── codex/                               # Codex 向け wrapper
    └── skills/git-sync-update-main → ../../skills/git-sync-update-main
```

新しいスキルを足したいときも、`skills/` に1個書いて、両側に symlink を貼るだけ。本体は1つしかないので、二重管理は発生しません。

完成したリポジトリはこちら: <https://github.com/t-tonton/tonton-ai-skills>

## 核心: SKILL.md のフォーマットがほぼ互換だった

これに気づいた瞬間、「これいけるな」となりました。Claude Code と Codex の SKILL.md をスペック比較するとこうなります。

| 項目 | Claude Code | Codex CLI |
|---|---|---|
| ファイル名 | `SKILL.md` | `SKILL.md` |
| 配置 | `<plugin>/skills/<name>/SKILL.md` | `<name>/SKILL.md` |
| 必須 frontmatter | `description` | `name` + `description` |
| 自動呼び出し | `description` のマッチで起動 | 同じ |
| 明示呼び出し | `/<plugin>:<name>` | `$<name>` |
| ユーザー設置先 | `~/.claude/plugins/cache/` | `~/.agents/skills/` |

結局のところ、違うのはディレクトリの規約と、frontmatter に `name:` が要るかどうかくらい。プロンプトの本文 (`SKILL.md` の中身) は同じファイルで両方に通用します。

frontmatter は両方の要件をまとめて満たす形で書けばOK。

```yaml
---
name: git-sync-update-main          # Codex 必須、Claude Code は冗長フィールドとして無害
description: 現在のリポジトリを安全に最新の main ブランチへ同期する。...
---

あなたは安全な Git 操作を行うエンジニアです。
...
```

これで1ファイルがどっちのエージェントでも動きます。

## 全体構造

実際のリポジトリの中身はこうなっています。

```
.
├── skills/                                # ← single source of truth
│   ├── git-sync-update-main/SKILL.md
│   └── session-handoff-{save,list,load}/SKILL.md
├── .claude-plugin/
│   └── marketplace.json                   # Claude Code marketplace catalog
├── plugins/                               # Claude Code adapter (中身は全部 symlink)
│   ├── git-sync/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/
│   │       └── update-main → ../../../skills/git-sync-update-main
│   └── session-handoff/
│       ├── .claude-plugin/plugin.json
│       └── skills/{save,list,load} → ../../../skills/session-handoff-{...}
└── codex/                                 # Codex adapter (中身は全部 dir-symlink)
    ├── skills/
    │   ├── git-sync-update-main → ../../skills/git-sync-update-main
    │   └── session-handoff-{save,list,load} → ../../skills/session-handoff-{...}
    └── install.sh                         # ~/.agents/skills/ 配下に symlink を配置
```

整理すると、`skills/` には agent-neutral な本体だけが入っていて、特定のエージェントの規約には縛られていません。`plugins/` も `codex/` も中身は全部 symlink で、各エージェントが期待するディレクトリ名 (`<plugin>/skills/<skill>` と `<skill>` の違い) を満たすためだけのラッパーに過ぎない、というのがこの構造のポイントです。

新しいエージェントが出てきたら `<adapter-name>/` ディレクトリを1つ足すだけで済みます。`skills/` 本体には触りません。

### 新スキル追加の手順

新しい skill `foo-bar` を足したいなら、こんな手順になります。

```bash
# 1. 本体を1つ書く
mkdir -p skills/foo-bar
$EDITOR skills/foo-bar/SKILL.md
# ↑ frontmatter に `name: foo-bar` と `description: ...` を書く

# 2. Claude Code 側 wrapper symlink
mkdir -p plugins/foo/skills
ln -s ../../../skills/foo-bar plugins/foo/skills/bar

# 3. Codex 側 wrapper symlink
ln -s ../../skills/foo-bar codex/skills/foo-bar
```

これだけで Claude Code からは `/foo:bar`、Codex からは `$foo-bar` で同じスキルが呼べます。

## おまけ: AGENTS.md / CLAUDE.md / GEMINI.md も同じ手で1ソース化

似た話で、リポジトリ root のドキュメントも symlink で 1 ソースにできます。Codex CLI は `AGENTS.md`、Claude Code は `CLAUDE.md`、Gemini は `GEMINI.md` を、それぞれ自分の規約名で読みに行きます。

同じ内容を3つ用意すると drift するので、本体を1つだけ置いて、他はそこへの symlink にしておけば済みます。

```bash
# CLAUDE.md は実体 (このリポジトリのコントリビューターガイド)
$EDITOR CLAUDE.md

# Codex 用は symlink を貼るだけ
ln -s CLAUDE.md AGENTS.md

# 将来 Gemini 対応するなら、これだけ
ln -s CLAUDE.md GEMINI.md
```

これで全エージェントが同じドキュメントを読むので、本体を直せば全部に反映されます。

## 動かしてみた

### Codex 側

リポジトリ root で `bash codex/install.sh` を実行すると `~/.agents/skills/` に symlink が貼られます。Codex CLI を起動して `$` で skill picker を開くと、追加した skill たちがちゃんと見えます。

<!-- ここに Codex の skill picker のスクショを貼る -->

`description:` ベースなので自然言語起動も効きます。「main に揃えて」と言うだけで `git-sync-update-main` が発動するし、`$git-sync-update-main` と打てば明示的にも呼べます。

### Claude Code 側

```
/plugin marketplace add t-tonton/tonton-ai-skills
/plugin install git-sync@tonton-plugins
/reload-plugins
/git-sync:update-main
```

外部 symlink を含む plugin でも、Claude Code はキャッシュにコピーするときに symlink を解決して中身を持っていってくれるので、ちゃんと動きました。

## 何が嬉しいか

やってみて一番効いたのは、ツールを切り替えた瞬間に頭が一瞬止まる、みたいな小さなストレスが消えることでした。普段 Claude Code で `/git-sync:update-main` と打ってるのが、Codex に切り替えても `$git-sync-update-main` でそのまま動く、というのは思った以上に快適です。

書いた `SKILL.md` が片方のエージェント専用にならないのも、地味に効きます。せっかく時間かけて書いた知見が、ツール側の都合で塩漬けにならないのは安心感がある。

将来 Cursor や Aider みたいな別のエージェントを混ぜたくなっても、adapter を1つ足すだけで済むはずなので、構造として伸ばしやすいかなと思っています。

## 注意点

`plugin.json` 固有の機能 (hooks や MCP server バンドル) は Codex には持っていけません。Codex の skill レイヤーに対応する概念がないので、ここは Claude Code adapter 側に閉じ込めるしかないです。

Symlink を使うので、Windows で同じことをやりたい人は別途検証が必要です。自分は macOS で組んだだけで未確認。

チームで運用する場合は、CI や配布形式、レビュー体制で別の制約が出てくるはずなので、そのまま当てはめるかは状況によります。

## まとめ

スキルの「中身」と「エージェントごとの入口」を分離する。やったのはそれだけです。

書いたスキルが再利用できて、ツール間の違和感も消えて、開発体験がかなり安定しました。やる前は「そこまで効くかな」と思ってましたが、やってみたら想像以上に効きました。

リポジトリ: <https://github.com/t-tonton/tonton-ai-skills>
