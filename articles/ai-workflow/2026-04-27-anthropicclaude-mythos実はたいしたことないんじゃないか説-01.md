---
id: "2026-04-27-anthropicclaude-mythos実はたいしたことないんじゃないか説-01"
title: "【Anthropic】Claude Mythos、実はたいしたことないんじゃないか説"
url: "https://qiita.com/rana_kualu/items/cd4b0c04f16caa8366cd"
source: "qiita"
category: "ai-workflow"
tags: ["API", "LLM", "qiita"]
date_published: "2026-04-27"
date_collected: "2026-04-28"
summary_by: "auto-rss"
query: ""
---

[Mozillaもべた褒め](https://japan.zdnet.com/article/35246770/)で前評判が絶頂の[Claude Mythos](https://www.anthropic.com/glasswing)ですが、言うほどのものではないんじゃないかという説も浮上しています。

実際問題として、世界最強のAIをいくらでも使い放題で世界一安全なはずのAnthropic自体が、最近[やらかしを](https://cloud.watch.impress.co.jp/docs/column/techwatch/2101100.html)[連発して](https://qiita.com/rana_kualu/items/1d019f33fd59fcbf1494)[います](https://pc.watch.impress.co.jp/docs/news/2104320.html)からね。
Mythos自体も公開直後にさっそく[不正アクセスを食らった](https://techcrunch.com/2026/04/21/unauthorized-group-has-gained-access-to-anthropics-exclusive-cyber-tool-mythos-report-claims/)のですが、その方法は『既存のエンドポイントURLからMythosのURLを推測した』だそうです。
Mythosは自分自身の問題点を見つけられなかったので？という感想にもなりますわな。

ということで以下は[Anthropic's super-scary bug hunting model Mythos is shaping up to be a nothingburger](https://www.theregister.com/2026/04/22/anthropic_mythos_hype_nothingburger/)の紹介です。

# Anthropic's super-scary bug hunting model Mythos is shaping up to be a nothingburger

Claude Mythosは脆弱性の発見力があまりにも高いゆえに、Anthropicは犯罪者による悪用を恐れて一般公開を控えている、と言われています。
しかし初期分析の結果、Mythosは一部の人が主張しているほど危険ではないのではないかという見方があがっています。

Anthropicは、犯罪者がこのゼロデイ攻略モデルを手に入れる前に脆弱性を発見修正できるように、一部の組織に対して[プレビュー版](https://www.theregister.com/2026/04/07/anthropic_all_your_zerodays_are_belong_to_us/)をProject Glasswingという名で提供し始めています。

しかし、この計画は必ずしも予定通りには行っていません。
先日Anthropicは、Glasswingに参加していない企業がこのモデルにアクセスしたことを認めました。
「サードパーティ環境のひとつを通じて、Claude Mythosプレビュー版への不正アクセスがあったという報告を受け、現在調査中です。」

## Intruder alert

対象はAnthropicがモデル開発で協力している企業であると認めたものの、名前の公表は拒否しました。
関係者によると、不正アクセスがサードパーティ環境を越えて広がった証拠はなく、Anthropicのシステム自体には影響ありませんでした。

[不正アクセスを最初に報道した](https://www.bloomberg.com/news/articles/2026-04-21/anthropic-s-mythos-model-is-being-accessed-by-unauthorized-users)Bloombergによると、Anthropicの過去のモデルに基いてモデルの位置を推定することでMythosにアクセスした、ということです。
この詳細は、[Mercorのデータ漏洩](https://www.theregister.com/2026/04/02/mercor_supply_chain_attack)によって明らかになりました。

Mercorは、Anthropicをはじめとした[AI研究機関](https://www.mercor.com/research/)に専門家を派遣するAI人材派遣スタートアップです。
4月はじめ、MercorはLiteLLMサプライチェーン攻撃を受けた[数千社の企業のひとつ](https://www.theregister.com/2026/04/02/mercor_supply_chain_attack)だと発表しました。

この不正ユーザグループはDiscordの非公開グループに集まっており、そしてAnthropicがProject Glasswingを発表したその日にMythosへのアクセス権を取得したということです。
Bloombergによると、彼らはその後Mythosで遊んでいるだけで、悪用する気配は全くないと報じています。

もっとも、彼らが何を狙っているのかはともかく、この不正アクセスはいくつかの事実を表しています。

まず第一に、コードを秘密に保つのは非常に難しいということです。
これは[歴史的経緯](https://www.theregister.com/2026/04/06/anthropic_code_leak_kettle_podcast)からも明らかでしょう。
特に新しいモデルを試そうとしているのがサイバーセキュリティやエンジニアリングの専門家である場合はなおさらです。
そもそも彼らはネットワークやデータベースに侵入する必要がありませんでした。
内部犯やサプライチェーン攻撃こそが真の脅威なのです。


デセプション技術企業AcalvioのCEOであるRam Varadarajanは語ります。
「Mythosへの侵入には高度な攻撃は必要ありませんでした。URLパターンとちょっとした推測だけでした。すなわち、放出制御モデルは、モデル自体の機能が問題になる前に、最初から失敗したということです。」

サプライチェーンセキュリティ企業Black Duckの責任者Tim Mackeyも語ります。
「AnthropicによるMythosのマーケティングは、実質的に挑戦状であり、不正アクセスできるものならしてみろという[キャプチャー・ザ・フラッグ演習](https://ja.wikipedia.org/wiki/%E3%82%AD%E3%83%A3%E3%83%97%E3%83%81%E3%83%A3%E3%83%BC%E3%83%BB%E3%82%B6%E3%83%BB%E3%83%95%E3%83%A9%E3%83%83%E3%82%B0)でした。」


## Cutting through the hype

そしてそのマーケティングは現実を上回っているかもしれません。
[AWS](https://aws.amazon.com/blogs/security/building-ai-defenses-at-scale-before-the-threats-emerge/)やMozillaといったプレビューユーザからの初期報告では、このモデルは脆弱性の発見に非常に優れていて、高速で、人間のセキュリティエンジニアの負荷を減らす歓迎すべき時間短縮ツールとなるいっぽう、人間のセキュリティエンジニアを凌駕するところまでは至っていません。

MozillaのCTOであるBobby Holleyが[認めています](https://www.theregister.com/2026/04/22/mozilla_firefox_mythos_future_defenders/)。
「これまでのところ、人間が発見できる脆弱性のうち、このモデルが発見できないものは見つかっていません。」
「そして、人間の研究者でも発見できなかったバグも見つかっていません。」
言い換えれば、これはセキュリティエンジニアをひとりチームに迎えるということであり、世界にとって危険すぎるゼロデイ攻撃マシンではない。

Anthropicはこのモデルを発表した際、「Mythosによって数千件もの新たなクリティカルな脆弱性が発見された」と主張しました。
しかしVulnCheckの研究者Patrick Garrityによると、[脆弱性の数はせいぜい40程度](https://www.theregister.com/2026/04/15/project_glasswing_cves/)、あるいは全くない可能性もあると言っています。

さらに別の研究者DevanshはMythos関連のCVE、Anthropicのエクスプロイトコード、244ページのシステムカード、Glasswingの契約書などを徹底的に調査しました。
最終的に彼は、Mythosの実態を[誤情報と誇大宣伝に満ちたものである](https://www.artificialintelligencemadesimple.com/p/anthropics-claude-mythos-launch-is)と結論付けました。
たとえばAnthropicが発見したと主張する181件のFirefox脆弱性はサンドボックスモードを無効にした状態で実行されており、[FreeBSDの脆弱性](https://www.freebsd.org/security/advisories/FreeBSD-SA-26:08.rpcsec_gss.asc)には人の手が相当加えられていることが示唆されています。

さらに別の研究者Davi Ottenheimerによると、244ページのドキュメントには[脆弱性のことが全く記載されていない](https://www.flyingpenguin.com/the-boy-that-cried-mythos-verification-is-collapsing-trust-in-anthropic/)と指摘しました。
CVEも、CVSSも、深刻度も、情報公開のタイムラインも、誤検知率も一切ありません。
「別のモデルが既に発見して修正された脆弱性を、ブラウザのサンドボックスを無効化したテスト環境で見つけただけという、残念な結果だ。」

攻撃型AIハッキング企業[Horizon3.ai](http://horizon3.ai/)のCEOであるSnehal Antaniは主張しました。
「攻撃者は、脆弱性研究を加速するためにMythosを使う必要はない。4.6やOSSのモデルが既に加速させている。」
Mythosへの不正アクセスを懸念すべきかという問いにもいいえと答えました。
「正直なところ、たいした問題ではありません。あなたをハッキングするために、Mythosは特に必要ありません。」


# コメント欄

・誇大宣伝、はAIムーブメントそれ自体のまとめだ。価値がないとは言わないが、盛り過ぎである。

・AIは増幅するので、何かひとつでも問題があればまともな結果は得られない。

・『AIは増幅する』つまり、AIはアルコールを飲むようなものか？

・↑いいえ、そんなことはありません。アルコールを飲むのはいいことです。

・Mythosに宣伝通りの性能があるというのなら、ソースコード流出や不正使用の問題は起きないように設計されているべきでは？

・Mythosは、人間の脆弱性を検出するようにはできていません。

・人間を越えていると騒ぎ立てる連中の言うことに、未だに耳を傾ける連中がいるのだろうか？もう何年もこんな進歩しない話が続いている。

・現在はそうだし、近い将来そうなる可能性も低い。しかし今後そうなった場合のためにどうすべきか検討を始めるのは決して不合理ではない。

・そうだな、豚が空を飛び始めたときにどうすべきかについても検討を始めるべきだな。

・ついに私の対豚ドローンシステムが役に立つ時がきたか。



# 感想

まあ最終的には実際に使ってみないとわからないし、そして私のような一般人がMythosに触れるのは何年も後のことだろうから、噂が本当かどうかなんてわからないんですけどね。
それに『そこまですごいというほどでもない』がもし本当だったとしても、『私よりずっとすごい』のは間違いないので、うっかり流出してしまえば私の作った諸々が危険になることは結局変わらないのであんまり慰めにもなりませんね。

Mythosの、というかAIの特徴は、人間と同じようなことを人間より低コストで超高速に実行できるという部分にあると思っているので、元記事の`nothingburger`には正直あんまり同意できません。
中小企業や個人レベルで危険な脆弱性のあるソースコードなんて世界中にいくらでも存在するわけだけど、これまではわざわざコストを割いてそんな小さなところを攻撃するメリットがなかったわけです。
だから必然的に攻撃対象は大企業や政府機関といった金・権力のあるところに集中していました。
しかし今後はAIによって超低コストで、さらに休む必要もなく攻撃が続けられるわけで、危険性の裾野が広がっていくことはほぼ間違いないでしょう。

そして同時に、『世界が変わる』みたいにMythosを神格化する諸々の記事にもあんまり同意できませんけどね。
最後のSnehal Antaniの発言が全てでしょう。

すなわち、Mythosがなくても既に世界は危ない。
