---
id: "2026-03-20-codexに-everything-claude-codeが使えるか聞いてみた-01"
title: "Codexに 「everything-claude-code」が使えるか聞いてみた。"
url: "https://note.com/ego_station/n/n1bfca090288a"
source: "note"
category: "claude-code"
tags: ["note"]
date_published: "2026-03-20"
date_collected: "2026-03-20"
summary_by: "auto-rss"
---

![](https://assets.st-note.com/img/1773972214-LzNdfPGWMHTmFZxSVInc9QEh.png?width=1200)

結論だけ言うと、次の事がCodexでは実現できないので、無理矢理codexで使う事もないのかなと思いました。

> 作業を中断しても前回の記憶を自動で引き継いだりする機能も備わっています。

これは、どう言う事をやっているかというと AIって毎回その場で考えていて、前回の回答を活かすという事がありません。

ECCでは、その部分を補完するために、作業の終了と最後に、作業の要約をフックを使って保存するという事をしています。

それをやることで前回の作業を活かして作業が出来るようになります。毎回、新人ではなく、回を重ねるごとに熟練工になっていくイメージです。

それを回避するためにCodexは次の提案をしてくれました。

> 要するに、Claude の「イベント駆動の自動化」は落ちます。  
> Codex ではその代わりに「指示ファイル + skills + agents + git hooks」で再構成する感じです。

なんか、無理矢理やってる感も個人的にはあるから、この提案には現状は賛成できなかったので、 使うときはclaude-codeで使うかもという結論になっています。

お待たせしました。Codexとの会話を始めましょう。

## everything-claude-code をcodexで使う方法はある？

ある。ただし、everything-claude-code をそのまま無改造で動かす、というより「Codex向けに移植する」が正確です。

**Codex で持ってこられるもの:**

* [SKILL.md](http://SKILL.md) ベースのスキル
* ワークフロー文書
* プロンプト資産
* 一部の subagent 前提の設計

**そのままは厳しいもの:**

Codex ではだいたいこう置き換えます:

1. everything-claude-code の中身を確認する
2. 再利用できる [SKILL.md](http://SKILL.md) や docs を ~/.codex/skills/ 側へ移す
3. Claude 固有ツール名を Codex 相当に置換する
4. subagent を使うなら ~/.codex/config.toml に [features] multi\_agent = true を入れる
5. 動かない部分だけ手で薄く書き換える

**要するに:**

と一次回答してたけど、Codexがレポジトリーを確認した結果回答がこうなりました。

> • .agents/skills/ と .codex/ は Codex 向けに明示的に作られていました。ここは「採用候補」でほぼ確定なので、残りは Claude 専用機能との依存度を  
> 見ています。  
> ────────────────────────────────────────────

• 仕分け結果はこうです。

> 結論だけ先に言うと、この repo はもう「Claude 専用の寄せ集め」ではなく、Codex 用の面をかなり持っています。なので  
> everything-claude-code 全体を移植する必要はなく、Codex 面だけ抜けばいいです。

そのまま使える

* /tmp/everything-claude-code/.codex/config.toml
* /tmp/everything-claude-code/.codex/AGENTS.md
* /tmp/everything-claude-code/.codex/agents
* /tmp/everything-claude-code/.agents/skills
* /tmp/everything-claude-code/AGENTS.md: root 指示は Codex でも使えます。やや強めですが、土台としては有効です。
* /tmp/everything-claude-code/scripts/sync-ecc-to-codex.sh
* /tmp/everything-claude-code/scripts/codex-git-hooks/pre-commit, /tmp/everything-claude-code/scripts/codex-git-hooks/pre-push

条件付きで使える

* /tmp/everything-claude-code/commands
* /tmp/everything-claude-code/agents
* /tmp/everything-claude-code/rules
* /tmp/everything-claude-code/mcp-configs
* /tmp/everything-claude-code/skills
* /tmp/everything-claude-code/.claude-plugin: Claude plugin 専用。
* /tmp/everything-claude-code/hooks, /tmp/everything-claude-code/scripts/hooks: README にもある通り、Codex は Claude-style hooks の実行  
  parity がありません。
* /tmp/everything-claude-code/.claude: Claude ローカル設定面。Codex では不要。
* /tmp/everything-claude-code/.cursor, /tmp/everything-claude-code/.opencode: 他ハーネス用。Codex 目的なら基本不要です。
* /tmp/everything-claude-code/install.sh, /tmp/everything-claude-code/install.ps1: 主対象が Claude/Cursor 系。Codex 目的なら優先度は低いで  
  す。

実運用の最小セットはこれです。

* /tmp/everything-claude-code/.codex/config.toml
* /tmp/everything-claude-code/AGENTS.md
* /tmp/everything-claude-code/.codex/AGENTS.md
* /tmp/everything-claude-code/.codex/agents
* /tmp/everything-claude-code/.agents/skills
* 必要なら /tmp/everything-claude-code/scripts/codex-git-hooks

> 見た限り、Codex で使うなら「Claude 用 repo を無理に流用する」のではなく、「repo に最初からある Codex 面だけ採用する」のが正解です。

### 参照:

## 出来ないことは何？

• 主に3つです。

### １．Claude Code の hooks をそのまま再現できない

Codex には Claude-style の PreToolUse / PostToolUse / SessionStart / Stop などの実行 parity がありません。  
なので /tmp/everything-claude-code/hooks や /tmp/everything-claude-code/scripts/hooks の「ツール実行前後に自動で割り込む仕組み」は使えません。  
/tmp/everything-claude-code/commands は Claude Code 前提です。Codex では /plan や /tdd のようにそのままは呼べません。  
使うなら「prompt 化して読む」「AGENTS/skills に落とす」変換が必要です。

### ２． Claude 固有の plugin / settings 面は使えない

このへんは Codex では無効です。  
Claude の plugin 配布、marketplace、settings override 前提の仕組みは捨てる必要があります。

細かく言うと、次もそのままは無理です。

* Claude の Task ベース subagent 呼び出し
* Claude hooks での自動フォーマット、自動 typecheck、自動警告
* Claude のセッション lifecycle にぶら下がる自動メモリ保存
* Claude ルール適用の一部自動化

ただし代替はあります。

* hooks → Git hooks / [AGENTS.md](http://AGENTS.md) / 手動検証
* slash commands → prompt 化
* Task → Codex の spawn\_agent
* 自動ガード → pre-commit / pre-push

要するに、Codex で出来ないのは「Claude Code のイベント駆動の自動化」です。  
逆に、[AGENTS.md](http://AGENTS.md)、.codex/config.toml、.agents/skills、multi-agent、Git hooks はかなり流用できます。

## 必要なら次に「Codex では何で代替するか」を 1 対 1 で表にして出します。

## › お願い

• everything-claude-code の Claude 専用機能を Codex でどう置き換えるかは、だいたいこの対応です。

実務的には、Codex ではこう考えるのが正しいです。

Codex で強い代替

* 方針強制: [AGENTS.md](http://AGENTS.md)
* 再利用ワークフロー: .agents/skills/
* 並列/役割分担: .codex/agents/ + multi-agent
* 最低限の自動防御: pre-commit / pre-push
* 外部連携: .codex/config.toml の MCP

Codex で弱くなる部分

* ツール実行のたびに自動介入するガード
* セッション lifecycle 連動の自動保存
* slash command の操作性
* Claude plugin 的な配布モデル

要するに、Claude の「イベント駆動の自動化」は落ちます。  
Codex ではその代わりに「指示ファイル + skills + agents + git hooks」で再構成する感じです。

## Everything Claude Code（略称：ECC）とは

前回の記事でskilsに書きましたが、それを大規模にした感じです。

イメージとしてはその担当の専門家を集めてきて一つのプロジェクトを作る感じです。

専門家 一人が skillsに相当します。（イメージです）  
  
ECCは、そのためのルール集で現状のプロジェクトに合わせて沢山のルールを組み合わせる感じになります。

---

「Everything Claude Code（略称：ECC）」は、AIを使ってプログラムを作る際の「超優秀な専門家チームをまるごと雇えるセット」のようなものです。

普通にAIへ作業を頼むと、「毎回微妙に違う答えが出る」「前に教えたルールを忘れてしまう」といった不満が出がちです。ECCは、こうした問題をまとめて解決してくれます。

最大の特徴は、AIを1人の「なんでも屋」として使うのではなく、「計画を立てる人」「プログラムを書く人」「ミスをチェックする人」「セキュリティを検査する人」など、**複数の専門家からなるチーム**に変身させられる点です。

使い方もシンプルで、短い命令（コマンド）を入力するだけで、このAIチームが自動で連携し、計画から品質チェックまでを一気に進めてくれます。また、会社のマニュアルのように「常に守るべきルール」をAIに覚えさせたり、作業を中断しても前回の記憶を自動で引き継いだりする機能も備わっています。

つまりECCを導入すれば、一人で作業していても、まるで熟練のプロチームと一緒に仕事をしているような「高い品質」と「スピード」を手に入れられる画期的な仕組みです。
