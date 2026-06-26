---
id: "2026-06-25-kgsi-httpstcoxpnhyi0cup-01"
title: "@kgsi: https://t.co/XPnHyi0cUp"
url: "https://x.com/kgsi/status/2070116538796196255"
source: "x"
category: "cowork"
tags: ["LLM", "x"]
date_published: "2026-06-25"
date_collected: "2026-06-26"
summary_by: "auto-x"
query: "Cowork スケジュール OR Cowork スキル作成 OR Cowork 自動化"
---

https://t.co/XPnHyi0cUp


--- Article ---
6/24〜6/25に開催中のConfig San Francisco 2026で、**Anthropicの[Chelsea Larsson](https://www.chelsealarsson.me/about)が「[Writing for** humans in an AI world](https://config.figma.com/san-francisco/session/47d280de-e85a-4e10-b6e6-b97734490e9f/)」というセッションに登壇しました。
Chelseaの肩書きはContent Design Lead。内容として面白かったので、登壇内容をもとに自分なりに整理したレポートを書いてみました。

![](https://pbs.twimg.com/media/HLqA71kaUAAZD0l.jpg)

# 「私たち、もう終わった？」

Chelseaは**自分のことを"human text generator"と呼んでいます。**UIコピーなど、言葉を作る仕事を続けてきた人間です。

LLMが出てきて、それが誰でも高速にできるようになりました。「Are we cooked?（私たち、もう終わった？）」と本気で思ったそうです。皮肉なことに、その後Chelsea自身がAI企業であるAnthropicに入ってContent Designをリードする立場になっています。
結論は悲観ではありませんでした。**「終わっていない。ただし仕事は変わった」と。**

AIで"書く仕事"が消えたのではなく、仕事の重心が移っています。個別の文言を手で磨くだけでなく、チームがClaudeを使ってよい文章を書ける仕組みを作ること、Claude自身がどう書くかを設計すること。それがContent Designの仕事になっています。

Chelseaはこの変化を"ego death（自我の死）"とも表現していました。専門性だと信じていた作業の一部が、AIのワークフローでは前ほど必要とされなくなる。その喪失を受け入れたうえで、自分のクラフトをどこに移すか。問われているのはそこだ、と。

# 言葉が体験を決める

Chelseaは、言葉を後から載せる仕上げではなく、**体験そのものを形づくる素材だと位置づけていました。**LLMは言葉で指示され、言葉で振る舞いが変わります。だからAIプロダクトでは言語が主要なデザインマテリアルになる、と。

具体例がいくつか挙げられました。
文言変更のPRは、以前はPM、エンジニア、ローカライゼーション、複数回のレビューを挟んで2週間かかることもあったそうです。いまはClaudeに意図を伝え、リポジトリ上の文言を更新してもらい、PRを確認して出すだけなら早ければ20分で終わります。仕事が消えたのではなく、手を動かす場所が変わった、と述べています。

メモリ移行を促すプロンプトの話もありました。最初は「It is my right」「It is imperative」のような要求口調で書いたところ、モデルに"操作的だ"と判断されて失敗したそうです。そこで「data portability」やアカウント移行という正当で馴染みのある文脈に言い換えたら、引き出せる情報が増えました。さらにエンジニアがプロンプトをチェックリスト形式にしたことで結果がもう一段改善し、多くのユーザーに届く機能になったとのことです。

この話を聞いて気づかされたのは、**Chelseaが「人間に直接読ませる文章」だけを書いているわけではない、という点でした。**「人間を助けるためにAIに読ませる文章」も書いている。言い回しひとつでモデルの反応が変わり、その結果としてユーザー体験も変わります。プロンプトやツール説明もUIコピーと同じく、体験設計の一部になっています。

# Claudeの"人格"は言葉でできている

体験はユーザーが触る前の層でも作られます。システムプロンプト、ツール記述、eval、モデルのトレーニング方針まで含めて、言語がプロダクトの振る舞いを決めています。
AnthropicではAmanda Askell @AmandaAskell がClaudeのキャラクターや価値観に関わるチームを率いているとのこと。

Claudeの方針として印象に残ったのが、**「dishonestly diplomatic（不誠実に外交的）」ではなく「diplomatically honest（敬意を持って正直に）」であるべき、という設計思想です。**反対するときにもただ迎合せず、相手への敬意を保ちながら正直に返す。この感じは偶然では
