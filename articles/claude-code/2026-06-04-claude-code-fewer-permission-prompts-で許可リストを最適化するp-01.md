---
id: "2026-06-04-claude-code-fewer-permission-prompts-で許可リストを最適化するp-01"
title: "Claude Code /fewer-permission-prompts で許可リストを最適化する【permission】"
url: "https://zenn.dev/michan74/articles/441b7540653cca"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "prompt-engineering", "Python", "zenn"]
date_published: "2026-06-04"
date_collected: "2026-06-05"
summary_by: "auto-rss"
query: ""
---

Claude Codeを普段利用しているのですが、AIに指示したあとに毎回実行してもいいですか？？？という確認が入るのが地味に面倒くさくなってきたので、適切に許可/拒否リストを設定することにしました。

１日に何回も見るこれ↓  
![](https://static.zenn.studio/user-upload/efed5115cde3-20260604.png)

## Skill: fewer-permission-prompts

いちいち確認してくるの多いな〜と感じていた、まさにそのタイミングでClaudeから、`/fewer-permission-prompts`を使ってみたら？という提案があったので、使ってみました。

Skill: `/fewer-permission-prompts` は、  
会話履歴を見て、許可リストに入れるものを提案してくれるスキルです。

### 実行してみる

スキルを呼び出すと、`トランスクリプトをスキャンして使用パターンを分析します。...`と分析が始まり、  
Claudeとの会話履歴(jsonl\_files)を探索し、コマンド実行している部分を見つけ、集計しているようでした。ディレクトリ問わず全ての会話履歴を横断して探索していました！

普段のコード修正と同じく、`settings.json`の修正を提案してくれるので、そのタイミングで、問題がないかを確認できます。  
そして、最後に以下のようなレポートを出してくれました。  
書き込み系や悪意のコード実行の可能性があるものはスキップしてくれていることが確認できます！  
![](https://static.zenn.studio/user-upload/9567dfa76f2e-20260604.png)

## さらなる改善

### python実行問題

今回スキップしたもので、python3の実行が大量にありました。ファイルの読込み時のjsonからの値取得などで使っているのですが、毎回何をしようとしているか確認して、実行許可を与えるのが面倒でした。しかし、pythonの実行を安易に許可するのはリスクがあります。  
そこで、以下の記載をClaude.mdに追加し、様子を見てみようと思います。

CLAUDE.md

```
- データの集計・フィルタリング・JSON処理は `python3` より `jq` + シェルコマンドを優先する
  - `jq` は自動許可済みのためプロンプトが出ない
  - どうしても Python が必要な処理はスクリプトファイルに切り出す
```

### 書き込み系の扱い

`mkdir`などの書き込み系のコマンドが、`fewer-permission-prompts`のスキルだと、書き込み系という理由だけで許可リストへの追加をスキップされていました。しかし、ディレクトリを限定すれば、許可無しで実行させてもよいかなと思っています。  
今後ディレクトリも含めて精査していこうと思います。

### 結局許可求められる問題

`find`や`cat`など読み込み系のコマンドについては、すでに許可済みでしたが、なぜか毎回許可を求められるという事態に陥っています。(未解決事件)  
`|`で別のコマンドを繋ぐと、たとえ許可リストにコマンドが載っていたとしても、許可スルーにはできないようです。この辺りのクセを理解していこうと思います。

## 次回予告
