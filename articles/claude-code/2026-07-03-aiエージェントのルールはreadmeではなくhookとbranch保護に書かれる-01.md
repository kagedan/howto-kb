---
id: "2026-07-03-aiエージェントのルールはreadmeではなくhookとbranch保護に書かれる-01"
title: "AIエージェントのルールは、READMEではなくhookとbranch保護に書かれる"
url: "https://zenn.dev/heftykoo/articles/f8da0aef2f2e38"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "zenn"]
date_published: "2026-07-03"
date_collected: "2026-07-04"
summary_by: "auto-rss"
query: ""
---

AIエージェントに「慎重に作業してください」と書くのは、たぶん一番弱い制御である。

人間には読める。雰囲気も伝わる。チームとしての姿勢も分かる。

でも repository は、それだけでは止まらない。

agent は tool を呼ぶ。file を読む。command を実行する。branch を作る。CI を走らせる。PR を出す。場合によっては、人間が画面を見ていない間に、かなりのところまで進む。

そこで効くルールは、README の心得ではない。実行前に止められる場所、触ってよい branch、必須の check、reviewer が読む PR description、session log。つまり repo の実行面に置かれたルールである。

AI利用ガイドラインを書くな、という話ではない。入口としては必要だ。ただ、チーム開発で本当に危ないのは、ガイドラインを読まなかった瞬間ではなく、読んでもなお実行できてしまう瞬間である。

## hook は便利機能ではなく、policy surface である

GitHub Copilot の hooks を見ると、agent の制御点がかなり具体的になっている。

sessionStart、userPromptSubmitted、preToolUse、postToolUse、agentStop、subagentStop、errorOccurred。どれも「AIに何を言うか」ではなく、「AIが動いている途中のどこに介入するか」を表している。

とくに重要なのは preToolUse だと思う。

tool を呼ぶ前に、その操作を許可するか、拒否するか、承認を要求するかを決められる。危険な command を止める。sensitive file への access を止める。秘密情報が混ざっていないかを見る。ログを残す。

これは自動化の飾りではない。

チームの AI ルールを、初めて実行境界に変換する場所である。

「production credential は触らない」と README に書くより、`secrets/` や `.env.production` への access を hook で止めるほうが強い。「勝手に migration を走らせない」と言うより、該当 command を denylist に入れるほうが現実に効く。

もちろん hook も万能ではない。同期的に走るなら latency も増える。雑に shell script を増やせば、agent より hook のほうが読みにくくなる。だが、それでも README よりは repo に近い。少なくとも、危険な操作の直前に立てる。

ここを「便利な自動処理」とだけ見ると、設計を間違える。

hook は、agent に何を許すかを repository が判断するための面である。

## branch protection は、agent を疑うためではない

cloud agent のような仕組みでは、agent は repository を調べ、branch 上で変更し、push し、PR へ進む。そうなると、branch protection や required checks は一気に古くない話になる。

むしろ、AIエージェント時代に一番地味で効く部品になる。

agent 専用の branch だけ push できるようにする。main へ直接触れない。CodeQL、dependency advisory check、secret scanning、test を required にする。workflow 実行には承認を挟む。session log を残す。merge は人間が見る。

これは agent を信用しないための儀式ではない。

agent が安全な道だけを通るための線路である。

人間の開発者にも同じことをしてきた。main に直接 push しない。CI が落ちたら merge しない。review を通す。secret が出たら止める。AIだから特別に厳しくするというより、AIにも同じ repo の重力を受けさせる。

ここを曖昧にすると、AI導入は個人の手元だけで進む。便利な人はどんどん使う。怖い人は使わない。チームとしては、「慎重に使いましょう」と言いながら、実際には各自のローカル判断に丸投げする。

それは、けっこう危ない。

エージェントは人間より速く失敗することがある。悪意があるからではなく、実行の拍が速いからだ。だからこそ、branch と check は説教ではなく機械的な制限として置く必要がある。

## 失敗する PR は、コード生成の失敗だけではない

agentic PR の失敗を見ていると、問題は model の賢さだけでは片付かない。

大きすぎる変更。触る file が多すぎる差分。CI failure。重複 PR。望まれていない feature 実装。reviewer が反応しにくい説明。こういう失敗は、生成能力の問題というより、PR という単位への落とし込みに失敗している。

AI が悪いコードを書いた、で終わらせると見落とす。

そもそも渡した仕事が大きすぎたのかもしれない。reviewer に読める粒度ではなかったのかもしれない。PR description が、何を変えたのか、なぜ変えたのか、どこを見てほしいのかを説明していなかったのかもしれない。

人間の PR でも同じだが、AI はその失敗を量産しやすい。

だから rule は code style だけでは足りない。PR の形もルールに入る。

たとえば、agent が PR を出すなら、最低限このくらいは要求したい。

* 変更した目的
* 触った範囲
* 触っていない範囲
* 実行した check
* 落ちた check と未解決の理由
* reviewer に見てほしい箇所
* 人間判断が必要な箇所

これは文章作法の話ではない。review queue を守る話である。

読めない PR は、正しくても詰まる。説明が足りない PR は、差分が小さくても怖い。AI が作った PR ならなおさら、説明面を repo policy に含めたほうがいい。

## "human in the loop" では粗すぎる

AIエージェントの安全性を語るとき、よく "human in the loop" と言う。

便利な言葉だが、実務では粗い。

どの loop なのか。

prompt を投げる前か。tool 実行の前か。sensitive file を読む前か。CI を走らせる前か。PR を ready にする前か。merge の前か。

全部を人間に戻すと、agent を使う意味が薄れる。全部を自動にすると、ただの自走する変更生成器になる。必要なのは、人間が入る場所をひとつの美談にしないことだ。

作業の開始権限、実行権限、branch への push 権限、workflow 実行権限、review 依頼権限、merge 権限。これらは分けて考えたほうがいい。

たとえば、agent に調査と patch 作成までは任せる。push は agent branch のみ許す。workflow は low-risk な check だけ自動実行する。security check と merge は人間が見る。PR description が template を満たしていなければ ready にしない。

このくらい分けると、ようやく「人間が最後に見るから安心」という雑な設計から抜けられる。

最後に人間が見ることは大事だ。

ただし、最後だけ人間が見るのは、制御としては遅いことがある。

## 最小構成は、そんなに大げさでなくていい

最初から巨大な AI governance を作る必要はない。

むしろ、最初に重すぎるものを作ると、誰も使わない。実際に効く最小構成から始めたほうがいい。

自分なら、まずこのくらいにする。

* dangerous command denylist
* sensitive file approval
* agent 専用 branch
* main への direct push 禁止
* required CI と security checks
* PR description template
* review owner
* session/audit log

これだけでも、README に「安全に使う」と書くだけの状態とはかなり違う。

dangerous command denylist は、`rm -rf` のような分かりやすいものだけではない。migration、deployment、credential 操作、広範囲 format、package lock の大規模更新など、repo ごとに危ない操作がある。

sensitive file approval も、単純な secret file だけではない。billing、auth、permissions、infrastructure、legal text。AI が触ると怖い場所は、チームごとに違う。

PR description template は、地味だが効く。agent が作った差分は、生成過程を人間が全部追えているとは限らない。だからこそ、何をしたかだけでなく、何をしていないかを書かせる。

review owner も必要だ。AI PR は誰かが読むだろう、では流れる。owner を決めておかないと、review queue に薄い不安だけが積もる。

session log は、責任追及のためというより、後から原因を読めるようにするためにある。なぜこの file を触ったのか。どの command を試したのか。どこで失敗したのか。そこが見えないと、AI の出力はただの不思議な差分になる。

## AIルールは、文章から実行面へ移る

チームで AIエージェントを使うとき、最初に決めるべきことは「どのモデルが一番賢いか」ではない。

どの操作を止めるか。

どの branch だけを通すか。

どの check が通らなければ review しないか。

どの説明がなければ PR として扱わないか。

どこで人間が入るか。

ここを決めないまま agent を入れると、チームルールは雰囲気になる。README は整っている。利用方針もある。だが repo は止めてくれない。CI も review queue も、あとから結果を受け取るだけになる。

AIエージェントをチームに入れるとは、AIに良い子でいてもらうことではない。

良い子でなくても壊れにくい道を、repo 側に作ることだ。

文章のルールは入口でいい。最後に効くのは、hook、branch protection、required checks、PR description、review handoff である。

AI時代の開発ルールは、読まれるためではなく、実行されるために書く。

## Source notes

* GitHub Docs: Copilot hooks の lifecycle event、preToolUse による tool 実行制御、secret scanning、audit logging、同期実行の注意点を確認。
* GitHub Docs: Copilot cloud agent の branch 制限、CodeQL、dependency advisory checks、secret scanning、session log、human review before merge などの mitigation を確認。
* "Where Do AI Coding Agents Fail?": agent-authored PR の失敗要因を、変更サイズ、CI failure、duplicate PR、不要な feature、reviewer engagement の観点から確認。
* "How AI Coding Agents Communicate": PR description と reviewer response / merge outcome の関係を、review handoff の論点として使用。
* "Collaborator or Assistant?": operational agency と merge governance を分ける視点を、"human in the loop" の分解に使用。
* Zenn topic pages: Claude Code、Codex、AIエージェント周辺の日本語読者面確認に使用。
