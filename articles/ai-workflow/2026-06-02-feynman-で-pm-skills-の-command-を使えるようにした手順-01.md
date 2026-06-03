---
id: "2026-06-02-feynman-で-pm-skills-の-command-を使えるようにした手順-01"
title: "Feynman で PM Skills の command を使えるようにした手順"
url: "https://zenn.dev/53able/articles/3bcc8957d86372"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "AI-agent", "zenn"]
date_published: "2026-06-02"
date_collected: "2026-06-03"
summary_by: "auto-rss"
query: ""
---

## この記事のゴール

Claude plugin として入っている PM Skills の command を、Feynman からも `/write-prd` や `/discover` のように呼び出せるようにした手順をまとめます。

最終的にやったことはシンプルです。Claude plugin 側にある `commands/*.md` を、Feynman/Pi が prompt template として読む `~/.feynman/agent/prompts/` へシンボリックリンクしました。

## 一次情報

この手順は、手元の実装と各リポジトリを見て確認しました。最初に参照元を置いておきます。

| 対象 | 一次情報 | この記事で使った情報 |
| --- | --- | --- |
| Feynman | [companion-inc/feynman](https://github.com/companion-inc/feynman) | `package.json` の description が "Research-first CLI agent built on Pi and alphaXiv"。README では "The open source AI research agent." と説明されています。 |
| Pi | [earendil-works/pi](https://github.com/earendil-works/pi) | `@earendil-works/pi-coding-agent` は coding agent CLI で、現在のリポジトリ名は `pi` です。古い `pi-mono` URL は GitHub 上で `earendil-works/pi` にリダイレクトされます。prompt template の読み込み処理もこの系統の実装にあります。 |
| PM Skills | [phuryn/pm-skills](https://github.com/phuryn/pm-skills) | README に "65 PM skills and 36 chained workflows across 8 plugins" とあり、`pm-*/commands/*.md` と `pm-*/skills/*/SKILL.md` が実体として置かれています。 |

## なぜこの作業が必要だったのか

PM Skills は Claude plugin としてはインストール済みでした。しかし、Claude が command を探す場所と、Feynman/Pi が `/xxx` 形式の入力を探す場所は同じではありません。

Claude plugin では、`/write-prd` のような command は plugin 内の `commands/` にあります。一方、Feynman/Pi では、ユーザーが入力する `/write-prd ...` のような文字列は `prompts/` にある Markdown ファイル、つまり prompt template として展開されます。

つまり、Claude 側に PM Skills が入っているだけでは、Feynman から command を呼べません。Feynman が読む場所に、command の Markdown を置く必要があります。

この関係を図にすると、次のようになります。

この図で大事なのは、PM Skills のファイルを作り変えていない点です。Feynman 側にコピーしたのではなく、Feynman が読む `prompts/` から Claude plugin cache 内の command Markdown を参照できるようにしました。

## 背景 1: Feynman と Pi の関係

ここで出てくる Feynman と Pi は、同じものではありません。

Feynman は、研究・調査・執筆向けに使っている AI エージェント環境です。ユーザーから見ると、会話しながらファイルを読んだり、Markdown を書いたり、調査結果をまとめたりする作業場です。リポジトリは [companion-inc/feynman](https://github.com/companion-inc/feynman) です。

<https://github.com/companion-inc/feynman>

Pi は、その下で動いているエージェント実行基盤です。ローカルファイルの読み書き、スキルの読み込み、prompt template の展開、slash command の処理など、Feynman の操作を支える仕組みを持っています。この記事で確認した Pi 側のパッケージは [earendil-works/pi](https://github.com/earendil-works/pi) の `packages/coding-agent` に対応します。

<https://github.com/earendil-works/pi>

この記事で重要なのは、Feynman の画面で `/write-prd ...` と入力していても、その入力をどう解釈するかは Pi 側の仕組みに依存している、という点です。Pi は Markdown で書かれた prompt template を `/名前` の形で呼び出せます。

たとえば、次のファイルがあるとします。

```
~/.feynman/agent/prompts/write-prd.md
```

この場合、Feynman の入力欄で次のように入力すると、`write-prd.md` の内容が prompt template として展開されます。

```
/write-prd SSO support for enterprise customers
```

この仕組みに合わせて、PM Skills の command Markdown を Feynman 側の `prompts/` に見せるのが今回の作業です。

この図では、Feynman を「ユーザーが触る作業環境」、Pi を「入力を解釈して prompt template を扱う実行基盤」として分けています。今回の設定変更は、主に Pi が参照する `prompts/` 側に関するものです。

## 背景 2: PM Skills の構造

PM Skills は、プロダクトマネジメントの作業を支援する Skill、Command、Plugin をまとめたセットです。PRD 作成、ディスカバリー、戦略整理、ローンチ計画、ユーザー調査、分析 SQL 作成などのワークフローが含まれています。リポジトリは [phuryn/pm-skills](https://github.com/phuryn/pm-skills) です。

公式ドキュメントでは、PM Skills の構造が Skill、Command、Plugin の 3 層として説明されています。

<https://github.com/phuryn/pm-skills>

| 種類 | 役割 | 実体 |
| --- | --- | --- |
| Skill | 作業手順やフレームワークを定義する最小単位 | `skills/<name>/SKILL.md` |
| Command | `/write-prd` のように起動するワークフロー | `commands/<name>.md` |
| Plugin | PM 領域ごとに Skill と Command をまとめた配布単位 | `.claude-plugin/plugin.json` など |

たとえば `/write-prd` は Command です。PRD を書くための流れをまとめた Markdown ファイルで、内部では PRD 作成用の Skill を使う想定になっています。

PM Skills 内の関係も、図で見ると分かりやすくなります。

今回 Feynman から使いたかったのは、Skill 単体ではなく `/write-prd`、`/discover`、`/strategy` のような Command です。そのため、作業対象は `skills/` ではなく `commands/` でした。

## 方針: commands を prompts として読ませる

Feynman/Pi 側の実装を確認すると、古い `commands/` ディレクトリは `prompts/` へ移行する扱いになっていました。

確認したファイル:

```
~/.feynman/npm-global/lib/node_modules/@earendil-works/pi-coding-agent/dist/migrations.js
```

該当する説明:

```
Migrate commands/ to prompts/ if needed.
```

prompt template の読み込み処理は、次のファイルで確認しました。

```
~/.feynman/npm-global/lib/node_modules/@earendil-works/pi-coding-agent/dist/core/prompt-templates.js
```

Pi は主に次の場所から prompt template を読みます。

1. グローバル: `~/.feynman/agent/prompts/`
2. プロジェクト単位: `<cwd>/.pi/prompts/`
3. CLI で `--prompt-template` に渡したパス

今回は、どのプロジェクトでも PM Skills の command を使えるようにしたかったため、グローバルの `~/.feynman/agent/prompts/` を使いました。

## 手順 1: PM Skills の command がある場所を確認する

まず、PM Skills がローカルのどこにあるかを探しました。

```
find ~/.claude ~/.feynman ~/.agents ~/git -maxdepth 6 \
  \( -path '*/pm-*' -o -path '*/pm-skills*' \) -type d 2>/dev/null | head -100
```

このコマンドでは、Claude、Feynman、agents、手元の git ディレクトリの中から、`pm-*` や `pm-skills*` に一致するディレクトリを探しています。

主な配置先として、次のディレクトリが見つかりました。

```
~/.claude/plugins/cache/pm-skills/pm-product-strategy/1.0.1/commands
~/.claude/plugins/cache/pm-skills/pm-product-discovery/1.0.1/commands
~/.claude/plugins/cache/pm-skills/pm-execution/1.0.1/commands
...
```

ここにある `commands/*.md` が、Feynman から呼び出したい command の本体です。

## 手順 2: Feynman の prompts ディレクトリを作る

Feynman が読むグローバルの prompt template ディレクトリを作成しました。

```
mkdir -p ~/.feynman/agent/prompts
```

`mkdir` はディレクトリを作るコマンドです。`-p` を付けると、親ディレクトリが足りない場合はまとめて作成し、すでに存在している場合もエラーにしません。

## 手順 3: command Markdown をシンボリックリンクする

Claude plugin キャッシュ内の `commands/*.md` を探し、それぞれを `~/.feynman/agent/prompts/` へシンボリックリンクしました。

```
PROMPTS="$HOME/.feynman/agent/prompts"
SRC="$HOME/.claude/plugins/cache/pm-skills"
mkdir -p "$PROMPTS"

while IFS= read -r f; do
  name="$(basename "$f")"
  target="$PROMPTS/$name"

  if [ -e "$target" ] || [ -L "$target" ]; then
    if [ "$(readlink "$target" 2>/dev/null || true)" != "$f" ]; then
      mv "$target" "$target.bak.$(date +%Y%m%d%H%M%S)"
      ln -s "$f" "$target"
    fi
  else
    ln -s "$f" "$target"
  fi
done < <(find "$SRC" -path '*/commands/*.md' -type f | sort)
```

この処理でしていることは、次の通りです。

* `SRC` に、Claude plugin cache 内の PM Skills ディレクトリを指定します。
* `PROMPTS` に、Feynman が読む prompt template ディレクトリを指定します。
* `find "$SRC" -path '*/commands/*.md' -type f` で、PM Skills 内の command Markdown をすべて探します。
* 各 Markdown ファイルに対して、同じファイル名のリンクを `~/.feynman/agent/prompts/` に作ります。
* すでに同名ファイルがある場合は、上書きせず `*.bak.<timestamp>` へ退避します。

コピーではなくシンボリックリンクにした理由は、元ファイルを重複管理したくなかったためです。リンクにしておけば、Feynman 側は Claude plugin キャッシュ内の実体を参照します。

## 結果: 36 個の command が使える状態になった

Feynman の prompt template ディレクトリに、PM Skills の command が 36 個リンクされました。

確認コマンド:

```
find ~/.feynman/agent/prompts -maxdepth 1 -type l -name '*.md' -print | wc -l
```

結果:

主な command は次の通りです。

```
/discover
/write-prd
/strategy
/sprint
/north-star
/plan-launch
/market-product
/research-users
/write-query
/analyze-test
```

リンクされた command Markdown 一覧

```
analyze-cohorts.md
analyze-feedback.md
analyze-test.md
battlecard.md
brainstorm.md
business-model.md
competitive-analysis.md
discover.md
draft-nda.md
generate-data.md
growth-strategy.md
interview.md
market-product.md
market-scan.md
meeting-notes.md
north-star.md
plan-launch.md
plan-okrs.md
pre-mortem.md
pricing.md
privacy-policy.md
proofread.md
research-users.md
review-resume.md
setup-metrics.md
sprint.md
stakeholder-map.md
strategy.md
tailor-resume.md
test-scenarios.md
transform-roadmap.md
triage-requests.md
value-proposition.md
write-prd.md
write-query.md
write-stories.md
```

## 動作確認

最後に、Pi の prompt template ローダーを直接呼び出して、主要な command が読み込まれることを確認しました。

```
node --input-type=module <<'NODE'
import { loadPromptTemplates } from '/Users/oreore/.feynman/npm-global/lib/node_modules/@earendil-works/pi-coding-agent/dist/core/prompt-templates.js';

const templates = loadPromptTemplates({
  cwd: process.cwd(),
  agentDir: process.env.HOME + '/.feynman/agent',
  promptPaths: [],
  includeDefaults: true
});

const names = templates.map(t => t.name).sort();
for (const name of ['discover', 'write-prd', 'strategy', 'sprint', 'north-star']) {
  console.log(name, names.includes(name) ? 'OK' : 'MISSING');
}
console.log('total_templates', names.length);
NODE
```

結果:

```
discover OK
write-prd OK
strategy OK
sprint OK
north-star OK
total_templates 36
```

`discover OK` のように出ているため、`/discover` という入力が prompt template として解決できる状態になっています。`total_templates 36` は、今回リンクした 36 個の command が読み込み対象になっていることを示しています。

## 使い方

Feynman をすでに開いている場合は、まず次を実行します。

`/reload` は、Feynman にリソースを読み直させるための操作です。今回追加した `prompts/` の内容を、起動中のセッションへ反映するために使います。

その後、次のように command を入力できます。

```
/write-prd SSO support for enterprise customers
/discover AI-powered meeting summarizer for remote teams
/strategy B2B project management tool for agencies
/north-star 二面 marketplace の成長指標を決める
```

## 注意点

この対応は、Claude plugin の Command を Feynman の prompt template として使うための橋渡しです。Claude plugin の仕組みそのものを Feynman に移植したわけではありません。

PM Skills の Skill が別経路でインストール済みでも、`/discover` のような Command は `prompts/` に置かないと Feynman の `/` 補完や展開対象になりません。Skill と Command は別物です。

シンボリックリンク先は Claude plugin cache です。PM Skills を再インストールしたり、バージョンが変わってキャッシュのパスが変わったりした場合は、リンクを張り直す必要があります。
