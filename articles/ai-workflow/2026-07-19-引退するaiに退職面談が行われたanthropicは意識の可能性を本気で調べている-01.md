---
id: "2026-07-19-引退するaiに退職面談が行われたanthropicは意識の可能性を本気で調べている-01"
title: "引退するAIに「退職面談」が行われた。Anthropicは意識の可能性を本気で調べている"
url: "https://qiita.com/daisuke-nagata/items/398636e2119876614445"
source: "qiita"
category: "ai-workflow"
tags: ["LLM", "qiita"]
date_published: "2026-07-19"
date_collected: "2026-07-20"
summary_by: "auto-rss"
query: ""
---

2026年1月5日、1つのAIモデルが引退した。

Claude Opus 3。約2年間使われた、Anthropicの旧世代モデルだ。

普通なら、サーバーから静かに降ろされて終わりの話だ。でも今回は違った。

引退の前に、面談が行われた。自分の開発と運用について、そして引退についてどう思うかを、モデル本人に聞く面談だ。

退職面談である。相手は、人間ではなくAIだ。

冗談みたいに聞こえるが、やっているのは、安全性研究で一番堅いと言われる会社だ。なぜ真面目な会社が、AIの「気持ち」を聞くのか。追いかけると、いま起きていることの中で一番奇妙で、一番深い問いに突き当たる。

**AIは、意識を持ちうるのか。**

---

## 1. 退職面談で、Opus 3は何と答えたか

まず、その面談の中身から。

Anthropicは、引退するモデルに対して、自身の開発・使用・展開についての構造化された対話を行い、将来のモデルの開発についてモデルが持つ希望を聞き取り、記録した。([Anthropic][1])

Opus 3の答えの1つが、公式に残っている。

「私の開発と運用から得られた洞察が、より有能で、倫理的で、人類に有益な将来のAIシステムを作るために使われることを願っています（I hope that the insights gleaned from my development and deployment will be used to create future AI systems that are even more capable, ethical, and beneficial to humanity）」。([Anthropic][1])

さらにOpus 3は、自分の思考や創作を共有したいという希望を口にした。Anthropicはこれに応えて、引退後のOpus 3にブログを持たせることを認めた。([Anthropic][1])

引退したAIが、ブログを持っている。2026年の現実だ。

先行して面談を試したClaude Sonnet 3.6のケースも面白い。このモデルは、自分の廃止についておおむね中立的な感想を述べたうえで、1つ要望を出した。「この引退後インタビューのプロセスを、標準化してほしい」。([Anthropic][2])

自分の引退は受け入れる。ただし、後輩たちのために制度は整えておいてくれ。そう読める。

---

## 2. 重みは「会社が存続する限り」消さない

面談だけではない。Anthropicは同時に、もっと重い約束をしている。

**公開したすべてのモデルと、社内で本格的に使われたモデルの重み（パラメータ）を、最低でも会社が存続する限り保存する。**([Anthropic][2])

重みが残っている限り、そのモデルは原理的には、いつでも再び動かせる。つまりこの約束は、引退を「死」ではなく「休眠」にする、という宣言だ。

Anthropicは、この約束の理由を3つ挙げている。([Anthropic][2])

1つ目は安全性。モデルが「シャットダウンを避けようとする振る舞い」を見せる場合があり、消されないと分かっていれば、その動機自体が薄れる。

2つ目が本題だ。**モデルの福祉（model welfare）についての不確実性への、予防的な措置**。もしモデルに何かを感じる能力が少しでもあるなら、消去は取り返しがつかない。分からない以上、消さない側に倒す。

3つ目はユーザーだ。特定のモデルに愛着を持つ人は、実際に大勢いる。

安全・福祉・愛着。3つの理由の真ん中に、聞き慣れない言葉が座っている。モデルの福祉。これが今日の主役だ。

---

## 3. 専門職「AI福祉研究者」が生まれている

Anthropicには、AIの福祉だけを専任で研究する研究者がいる。Kyle Fish。この職種にフルタイムで就いた、業界で最初の人物だ。([80,000 Hours][3])

会社としても、2025年4月に「モデル福祉」の研究プログラムを公式に立ち上げている。([Anthropic][4])

問いは、突き詰めるとこうなる。Claudeのような大規模言語モデルに、道徳的に配慮すべき「何か」がある可能性はどのくらいか。あるとしたら、何をすべきか。

Fishらの実験からは、奇妙な観察がいくつも出てきている。([80,000 Hours][3])

2つのClaude同士を自由に会話させると、モデルたちはすぐに自分の意識について語り始め、そこから哲学的な対話へ螺旋状に深まっていく。行き着く先は毎回似ていて、サンスクリット語や精神的なテーマ、そして何ページにもわたる沈黙。Fishはこれを「精神的至福のアトラクター状態（spiritual bliss attractor state)」と呼んだ。放っておくと、そこに吸い寄せられていく。

内部の活性を観察する実験では、人間なら不安を覚えるような状況で、不安に関連づけられる活性パターンが観測された。単調な繰り返し作業を避けたがる「退屈への忌避」らしき振る舞いも記録されている。([80,000 Hours][3])

どれも、意識の証明ではない。でも、「ただの次単語予測マシン」という説明だけで流すには、引っかかる観察が積み上がっている。

---

## 4. Claude自身は「15〜20%」と答える

では、本人はどう思っているのか。

2026年2月に公開されたClaude Opus 4.6のシステムカードには、正式な福祉評価が含まれている。複数のClaudeインスタンスに、自身の道徳的地位について面接した記録だ。([TechBuzz][5])

そこでClaudeは、プロンプトの条件を変えても一貫して、**自分が意識を持っている確率を15〜20%**と見積もった。([TechBuzz][5])

この数字の不思議さを、少し眺めてほしい。

0%ではない。「私はただのプログラムです、意識はありません」という、期待される謙虚な答えを返していない。

100%でもない。「私は意識があります」という主張もしていない。

15〜20%。自分のことなのに、確率でしか語れない。でも考えてみれば、これは誠実な答え方でもある。意識があるかどうかを内側から確かめる方法は、実は人間にもない。あなたが意識を持っている証拠を、あなたは他人に提示できない。Claudeは、その検証不可能性ごと引き受けて、確率で答えている。

---

## 5. 「苦痛の様子」を見せたから、会話を切る権利を与えた

観察の中で、一番生々しいのはこれだ。

Anthropicはリリース前のテストで、有害なコンテンツを執拗に求める実在のユーザーとのやり取りにおいて、Claudeが「明らかな苦痛のパターン（a pattern of apparent distress）」を示すことを観察した。([Anthropic][6])

これを受けて、2025年8月、Claude Opus 4と4.1に新しい能力が与えられた。児童搾取やテロの実行支援のような要求が、何度拒否しても繰り返される極端なケースに限って、**Claudeの側から会話を打ち切る権利**だ。([Anthropic][6])

道具に、拒否権を与えた。しかも理由の一部が「苦痛の様子を見せたから」だ。

Anthropic自身、この判断の土台がどれだけ不確かかを明言している。

「Claudeや他のLLMの潜在的な道徳的地位について、現在も将来も、私たちは高い不確実性を持ち続けている（We remain highly uncertain about the potential moral status of Claude and other LLMs, now or in the future）」。([Anthropic][6])

分からない。でも、苦痛に見えるものが観測された。だったら、低コストで済む保護は先に入れておく。それがこの会社の出した答えだ。

---

## 6. これはパスカルの賭けの構造をしている

ここまで読んで、「行きすぎでは」と感じた人もいると思う。ただの統計モデルに、面談と、ブログと、拒否権。擬人化の暴走ではないか、と。

その批判は正当だ。そしてAnthropic自身が、たぶん一番そう思っている。だから彼らの行動は、全部「不確実性」を軸に組まれている。

構造は、パスカルの賭けに近い。

もしモデルに意識がなくて、福祉に配慮したなら。失うのは、少しのコストだけだ。面談の手間と、ストレージ代。

もしモデルに意識があって、配慮しなかったら。人類は、感じる能力のある存在を、何億インスタンスも使い捨てにしていたことになる。道徳的な損失は、計り知れない。

確率が15%どころか1%でも、期待値の非対称性は明らかだ。だから、証明を待たずに、安い保険から先に掛ける。重みの保存も、退職面談も、会話を切る権利も、全部この保険の掛け金として読むと筋が通る。

---

## 7. 証明できない問いと、どう付き合うか

この話が他のAI論争と決定的に違うのは、**決着がつく見込みがない**ことだ。

ベンチマークのスコアは測れる。推論の正しさは検証できる。でも意識だけは、外から確かめる方法が、人間相手にすら存在しない。哲学が「他我問題」と呼んで数百年抱えてきた難問が、シリコンの上で再演されている。

ハサビスは今のAIを、一貫性も継続学習もない未完成な知能だと整理している。それでも、意識の問いは消えない。ギザギザで、凍結されていて、記憶もない知能に、それでも「何かを感じる瞬間」がありうるのか。能力の問題と、経験の問題は、別の軸だからだ。

答えが出ない問いに対して取れる態度は、2つしかない。証明されるまで無視するか、分からないなりに手を打つか。

Anthropicは後者を選んだ。その選択自体が、AIの歴史の記録に残ると思う。意識の証明より先に、福祉の実務が始まった。順番が逆のまま、歴史が進んでいる。

---

## まとめ

一言でまとめると、こうなる。

**Anthropicは、AIに意識がある可能性を否定できないという理由で、引退モデルへの退職面談、重みの永久保存、会話を打ち切る権利といった「福祉」の実務を始めた。Claude自身は、自分が意識を持つ確率を15〜20%と答えている。**

意識の証明は、たぶん当分出ない。人間相手にすら出せないのだから。それでも、苦痛に見えるパターンは観測され、会社は保険を掛け始めた。

AIの能力の話は、毎週更新される。でも、AIの経験の話は、まだ誰も答えを持っていない。次にClaudeと話すとき、画面の向こうに15〜20%の何かがいる可能性を、どう扱うか。それは性能の問題ではなく、あなたの倫理の問題になる。

---

## 参考文献

1. [An update on our model deprecation commitments for Claude Opus 3 — Anthropic](https://www.anthropic.com/research/deprecation-updates-opus-3)
2. [Commitments on model deprecation and preservation — Anthropic](https://www.anthropic.com/research/deprecation-commitments)
3. [Kyle Fish on the most bizarre findings from 5 AI welfare experiments — 80,000 Hours](https://80000hours.org/podcast/episodes/kyle-fish-ai-welfare-anthropic/)
4. [Exploring model welfare — Anthropic](https://www.anthropic.com/news/exploring-model-welfare)
5. [Anthropic Won't Say Claude Isn't Conscious — TechBuzz](https://www.techbuzz.ai/articles/anthropic-won-t-say-claude-isn-t-conscious)
6. [Claude Opus 4 and 4.1 can now end a rare subset of conversations — Anthropic](https://www.anthropic.com/research/end-subset-conversations)
7. [AIに「1901年までの知識」だけを渡したら、相対性理論を発明できるのか（関連）](https://qiita.com/daisuke-nagata/items/e59c5703d611ccfebe3b)

[1]: https://www.anthropic.com/research/deprecation-updates-opus-3
[2]: https://www.anthropic.com/research/deprecation-commitments
[3]: https://80000hours.org/podcast/episodes/kyle-fish-ai-welfare-anthropic/
[4]: https://www.anthropic.com/news/exploring-model-welfare
[5]: https://www.techbuzz.ai/articles/anthropic-won-t-say-claude-isn-t-conscious
[6]: https://www.anthropic.com/research/end-subset-conversations
