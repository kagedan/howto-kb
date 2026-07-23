---
id: "2026-07-23-claude-code-21217でsubagentのネストがデフォルト無効になっていた-01"
title: "Claude Code 2.1.217でSubAgentのネストがデフォルト無効になっていた"
url: "https://zenn.dev/arakawaaa/articles/2fec700785443a"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-07-23"
date_collected: "2026-07-24"
summary_by: "auto-rss"
query: ""
---

#### Claude Codeを2.1.217に上げたら、SubAgentの中からSubAgentを呼べなくなってました。せっかく6月にSubAgentのネストが解禁されたのにどうしちまったんだ、とCHANGELOGを見に行ったら、仕様が変更されていたようなのでまとめました。

## しれっとデフォルトで無効になってる

2.1.217の[CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)にこう書かれています。

> Changed subagents to no longer spawn nested subagents by default; set `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` to allow deeper nesting

ネスト自体は2.1.172で解禁され、5段までという深さ制限つきで使えていました。それが2.1.217からデフォルト無効に変わり、環境変数でのオプトイン制になっています。英語版の[環境変数リファレンス](https://code.claude.com/docs/en/env-vars)と[サブエージェントのドキュメント](https://code.claude.com/docs/en/sub-agents#let-subagents-spawn-their-own-subagents)にも反映されてます。(日本語版はまだ)

## 実際に何が起きるか

デフォルトの状態でSubAgentの中でAgentツールを呼ぼうとすると、こういうエラーになります。

```
Error: No such tool available: Agent.
Agent exists but is not enabled in this context.
```

SubAgentのネストが封じられてますね。  
もちろん、メインから直接SubAgentを呼ぶ分には今まで通り動きます。禁止されたのは2段目以降だけです。

ひとつ補足すると、`context: fork` のスキルはこのゲートの影響を受けません。SubAgentの中からforkスキルを呼ぶのも、forkスキルの中からforkスキルを呼ぶのも、変わらず動きます。ネスト制限がかかるのはAgentツール経由のスポーンだけです。

## 環境変数を設定する

プロジェクトの `.claude/settings.json` に書くのが定石ですかね。

```
{
  "env": {
    "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "3"
  }
}
```

値は「メインの下に重ねられるSubAgentの数」で、デフォルトは1です。1はメイン→Subのみでネスト不可、2で初めてメイン→Sub→Subというネストが通ります。SubAgentを3段重ねたければ3、という数え方です。この値は上げることしかできず、0にしてSubAgent自体を無効化するような使い方はできません。

## 所感

SubAgentのネストが解禁された一方で、200体のスポーン上限(2.1.212)、今回のデフォルト無効化と、制限を加えるアップデートが続いています(上限を設けること自体は自然ですが、なんか慌てて塞いでる感が)。Anthropicもまだ挙動を制御しきれていないようですね。

個人的にはSubAgentのネストを使った開発ワークフローを組んだりしていたので、この先どうなっていくのか気になるところです。以前claude -pの従量課金化が話題になって以降(撤回されましたが)、claude -p以外に柔軟にコンテキスト分離できる方法を探していたのですが、SubAgentのネストでうまいことできそうじゃん！となっていた矢先の出来事でした。

SubAgentのネストによる挙動は、バグなのか仕様なのか分からないものを色々観測しているので、時間が取れれば改めて記事にまとめたいですね。
