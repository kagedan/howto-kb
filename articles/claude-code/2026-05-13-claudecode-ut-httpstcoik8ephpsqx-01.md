---
id: "2026-05-13-claudecode-ut-httpstcoik8ephpsqx-01"
title: "@ClaudeCode_UT: https://t.co/Ik8ePHpsqx"
url: "https://x.com/ClaudeCode_UT/status/2054691480728674326"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "x"]
date_published: "2026-05-13"
date_collected: "2026-06-08"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/Ik8ePHpsqx


--- Article ---
「なんかClaude Code前よりバカになってない💢」

「あれ、最近Claude Codeいうこと聞かなくなってきたな」

あなたのCLAUDE.mdはいま何行で書かれていますか？30行？100行？それ以上？

以前の私は700行くらいまで膨れ上がっていました。

私自身が書いたのではなく、Claude Codeに私が色々指示している間に勝手に追加した結果こうなっていました。

Claude Codeの性能をあげようと良かれと思ってCLAUDE.mdに情報をモリモリに書き込んでいませんか？その結果知らず知らずのうちにClaude Code自身が数百行に渡っていたのです。

みなさんのAIももしかしたらこのような状態になって、それが原因で性能が意図せず落ちてしまっているのかもしれません。

今回はそのような性能低下を回避して上手にClaude Codeを使いこなすための設計やTipsを紹介します。

最近注目されていた海外の記事 "You've been using Claude wrong this whole time. CLAUDE.md fixes everything" の本体を、日本のビジネス現場向けに噛み砕いて再構成しました。

元ポストはこちら：
[https://x.com/TheAIWorld22/status/2053023798170198453](https://x.com/TheAIWorld22/status/2053023798170198453)

この記事をブクマ、AIを使っているお知り合いに紹介して読み続けてください。

## CLAUDE.md は自己プロフィールではなく Claude の挙動を変える契約だ

![](https://pbs.twimg.com/media/HIMUPfUaEAAz2gJ.jpg)

最初に多くの方が誤解している前提を 1 つだけ整理させてください。

CLAUDE.md と聞くと、こんなイメージを持っていませんか。

「自分の役割や好みを書いて、AI に自己紹介する場所」

実はこの理解だと、CLAUDE.md は本来の半分も使えていません。

自己紹介で書ける内容は「私は誰か」「何を作っているか」「どう書くか」のような情報です。Claude はそれを読んで、出力の内容を合わせてきます。

でも本当の使い方は、Claude の挙動そのものを変えることにあります。

毎回 "Great question!" で始まる癖を消したい。確証のない数字を断定で書かないようにさせたい。頼んでないところまで触らせたくない。これらは「自分の情報」ではなく「Claude の振る舞いに対する宣言」です。

ここでひとつ言葉を入れさせてください。CLAUDE.md は **永続契約** を書く場所です。

会話のたびに「これしないでね」と何度も言う代わりに、契約として 1 回だけ書いておく。すると、その癖はそのプロジェクトの中で二度と現れなくなります。

自己プロフィールと永続契約を別物として扱う。これが本記事のすべての出発点になります。

## 会話の癖を直す 4 つの指示

![](https://pbs.twimg.com/media/HIO26yRboAASoQx.jpg)

最初の領域は会話の癖です。元の英語記事では Part 1 にあたる箇所で、Claude が毎セッションで繰り返してしまう「おもてなし芸」を消す 4 つの指示です。

**指示 1：フィラー禁止**

冒頭の "Great question!" "Of course!" "Certainly!" を完全に消します。日本語でもケバトリ的な効果があります。

```markdown
Never open responses with filler phrases like 'Great question!', 'Of course!', 'Certainly!', or similar warmups. Start every response with the actual answer.

```

これを書くだけで、Claude の返答が即「答え」から始まるようになります。1 日 5 セッション × 3 秒の節約は些細に見えますが、CLAUDE.md に 1 行書くだけで永久に解決します。

**指示 2：選択肢を提示させる**

Claude は何も言わないと、勝手に 1 つの方針で書き始めます。

「文体を直して」と頼んだら、こちらの意図と違う方向に直されることがあります。

```markdown
Bef
