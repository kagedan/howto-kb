---
id: "2026-05-24-claudecode-love-httpstcoeztelwu0xy-01"
title: "@ClaudeCode_love: https://t.co/ezTelwu0XY"
url: "https://x.com/ClaudeCode_love/status/2058496124047249708"
source: "x"
category: "claude-code"
tags: ["claude-code", "x"]
date_published: "2026-05-24"
date_collected: "2026-05-30"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/ezTelwu0XY


--- Article ---
Claude Code、進化が早すぎて正直ついていけてますか？
毎週のように新しいコマンドが増えて、設定がいつのまにか変わって、気づけば「昨日まで普通に使えてた手順」がもう通用しない。Xを開けば解説は山ほど流れてくるけど、どれが本当でどこまで自分に関係あるのかも分からないし、追いかけるだけで一日終わっちゃいますよね。

でも、大丈夫です。毎週ぜんぶ追いかける必要はありません。この記事を最後まで読めば、今週Claude Codeに入った変化は"これ1本"でまるっとキャッチアップできます🔥

しかも全部公式の1次情報から取ってきてます！！

ところで皆さん、こんなこと、心当たりありませんか？

![](https://pbs.twimg.com/media/HJE8DeUbkAAAOrS.jpg)

・アップデートが毎週来すぎて、もう何が変わったのか追いきれない

・`/`コマンドが増えたり名前が変わったりして、いつもの手順が急に通らなくなる

・「なんか便利になったらしい」とは聞くけど、自分の使い方で何が変わるのか分からない

・最近トークンの減りが早い気がするけど、何が原因なのか見えない

・Xの解説が盛ってるのか公式の話なのか、判断できなくてモヤモヤする

ひとつでも「あ、それ自分だ」と思った方は、ぜひこのまま読み進めてみてください。

というのも今週（2026年5月17日〜24日）だけで、Claude Codeには v2.1.145 から v2.1.150 まで、立て続けにアップデートが入りました。正直、ぜんぶ自力で追うのはしんどい量です。

なのでこの記事は、Xでバズってる解説の寄せ集めではありません。Anthropic公式の CHANGELOG・公式ドキュメントのリリースノート・公式アカウントの発信という"一次情報だけ"を読み込んで、今週ぶんを「あなたの手元で何が変わるか」の順に並べ直しました。バージョン番号も日付もコマンド名も、ぜんぶ公式の表記そのまま。盛ってもいないし、削ってもいません。だから安心して保存して、あとでゆっくり見返してもらってOKです👀

![](https://pbs.twimg.com/media/HJE8OPFboAAZgxh.jpg)

出典：公式CHANGELOG（github.com/anthropics/claude-code）／公式changelog（code.claude.com/docs/en/changelog）／Anthropic公式アカウント（@ClaudeDevs／@bcherny ほか）

それでは、今週の要点をできるだけやさしく噛み砕いていきましょう👇

■ 𝟭. `/simplify` が `/code-review` に進化した（v2.1.147・5/21）

![](https://pbs.twimg.com/media/HJE8IcYbYAAaEtG.jpg)

まず最初がこれ。普段づかいのコマンドがまるっと別物になったので、知らずに使うと一番「あれ？」となるやつです。

これまであった `/simplify` コマンドが、今週から名前も中身もガラッと変わって `/code-review` になりました。

![](https://pbs.twimg.com/media/HJE8UtTaoAA_WN0.jpg)

旧 `/simplify` は「コードを片付けて直す（cleanup-and-fix）」挙動でしたが、この古い挙動は完全に削除されています。新しい `/code-review` は、コードを勝手にいじるのではなく、正しさ（correctness）のバグを指摘するレビュー役に振り切りました。

しかも、レビューの深さを自分で選べます。

```

/code-review high

```

のように effort レベルを指定すると、その強度でレビューしてくれます。軽く見てほしいときは低く、本気で粗探ししてほしいときは高く、と使い分けられるわけです。

さらに強力なのが `--comment` オプション。

```

/code-review --comment

```

これを付けると、見つけた指摘をGitHub の PR に inline コメントとして直接投稿できます。つまり「Claude にレビューさせて、その結果をそのままチームのプルリクに貼る」という流れが、コマンド一発で完結します。

𝗕𝗲𝗳𝗼𝗿𝗲：`/simplify` で何となくコードを整えてもらう（けど勝手に直される）

𝗔𝗳𝘁𝗲𝗿：`/code-review high --comment` で
