---
id: "2026-06-11-claude-codeのflibbertigibbetingって何謎の待機ワード187個訳してみた-01"
title: "Claude Codeの「Flibbertigibbeting...」って何？謎の待機ワード187個訳してみた"
url: "https://zenn.dev/mukuil_blog/articles/d529551f2c373a"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-06-11"
date_collected: "2026-06-12"
summary_by: "auto-rss"
query: ""
---

こんにちは！[株式会社ムクイル](https://www.mukuil.com/)のあるけみです。

![](https://static.zenn.studio/user-upload/1937922ba7bf-20260611.png)

こんなのは見たことありますか？

普段Claude Codeを使ってると、処理中に「Combobulating...」みたいな見慣れない単語がチラッと出ること、ありますよね。

せっかくなので、Claude Codeが考え中に出す謎単語、全部訳してみました！(暇人か)

# Claude Code 待機ワード一覧

CLI版と拡張機能版とちょっと違うっぽいですが、個人的なよく見るものを集めてみました。

## よく見るやつ

```
Accomplishing   ：達成中
Actualizing     ：実現中
Baking          ：焼き上げ中
Booping         ：ツンと突き中
Brewing         ：醸造中
Cerebrating     ：思考中
Channeling      ：力を通し中
Churning        ：かき混ぜ中
Clauding        ：クロード稼働中（造語）
Cogitating      ：熟考中
Combobulating   ：整理整頓中（こんがらがりの逆）
Computing       ：計算中
Concocting      ：調合（でっち上げ）中
Considering     ：検討中
Cooking         ：調理中
Determining     ：決定中
Discombobulating：頭こんがらがり中
Doing           ：作業中
Effecting       ：実行中
Enchanting      ：魔法をかけ中
Envisioning     ：思い描き中
Forging         ：鍛え中
Frolicking      ：はしゃぎ回り中
Herding         ：まとめ上げ中
Imagining       ：想像中
Incubating      ：温め（孵化）中
Manifesting     ：具現化中（引き寄せ中）
Moseying        ：ぶらぶら歩き中
Mulling         ：あれこれ思案中
Musing          ：物思いにふけり中
Percolating     ：じわじわ醸成中
Processing      ：処理中
Puttering       ：のんびり手を動かし中
Puzzling        ：頭をひねり中
Ruminating      ：反芻中
Scheming        ：企み中
Schlepping      ：えっちらおっちら運び中
Shimmying       ：くねくね動き中
Simmering       ：じっくり煮込み中
Smoothing       ：滑らかに整え中
Spelunking      ：洞窟探検中
Synthesizing    ：合成中
Transmuting     ：変換（錬成）中
Vibing          ：ノリノリ中（まったり中）
Wandering       ：さまよい中
Whirring        ：頭フル回転中（ブーン）
Working         ：作業中
Wrangling       ：格闘中
```

## 他にもこんなのもある

Claude Codeのソースに含まれているスピナー表示用の単語リストには、上記以外にもこんな単語が眠っているらしいです。

```
Actioning         ：実行に移し中
Architecting      ：設計中
Beaming           ：ビーム発射中
Beboppin'         ：ビバップで踊り中
Befuddling        ：頭を混乱させ中
Billowing         ：もくもく立ちのぼり中
Blanching         ：下茹で中
Bloviating        ：長々と演説中
Boogieing         ：ノリノリで踊り中
Boondoggling      ：無駄な作業中
Bootstrapping     ：自力で立ち上げ中
Bunning           ：お団子ヘアにまとめ中
Burrowing         ：穴を掘って潜り中
Calculating       ：計算中
Canoodling        ：イチャイチャ中
Caramelizing      ：キャラメリゼ中
Cascading         ：滝のように連鎖中
Catapulting       ：カタパルト発射中
Channelling       ：チャネリング中（英綴り）
Choreographing    ：振り付け中
Coalescing        ：融合中
Composing         ：構成・作曲中
Contemplating     ：考え込み中
Crafting          ：丹念に作り込み中
Creating          ：創造中
Crunching         ：数値をガリガリ処理中
Crystallizing     ：結晶化中
Cultivating       ：育成中
Deciphering       ：解読中
Deliberating      ：審議中
Dilly-dallying    ：ぐずぐず中
Doodling          ：落書き中
Drizzling         ：たらしかけ中
Ebbing            ：引き潮中
Elucidating       ：解明中
Embellishing      ：飾り付け中
Evaporating       ：蒸発中
Fermenting        ：発酵中
Fiddle-faddling   ：だらだら中
Finagling         ：うまくやりくり中
Flambéing         ：フランベ中
Flibbertigibbeting：そわそわ落ち着かず中
Flowing           ：流れ中
Flummoxing        ：困惑させ中
Fluttering        ：ひらひら中
Forming           ：形成中
Frosting          ：糖衣がけ中
Gallivanting      ：遊び歩き中
Galloping         ：駆け足中
Garnishing        ：盛り付け中
Generating        ：生成中
Germinating       ：発芽中
Gesticulating     ：身振り手振り中
Gitifying         ：Git化中（プログラマー的内輪ネタ）
Grooving          ：ノリノリ中
Gusting           ：突風中
Harmonizing       ：調和中
Hashing           ：ハッシュ化中
Hatching          ：孵化（企み）中
Honking           ：クラクション中
Hullaballooing    ：大騒ぎ中
Hyperspacing      ：ワープ中
Ideating          ：アイデア出し中
Improvising       ：即興中
Inferring         ：推論中
Infusing          ：風味を移し中
Ionizing          ：イオン化中
Jitterbugging     ：ジルバ踊り中
Julienning        ：千切り中
Kneading          ：こね中
Leavening         ：発酵・膨らまし中
Levitating        ：浮遊中
Lollygagging      ：だらだら中
Marinating        ：漬け込み中
Meandering        ：寄り道・蛇行中
Metamorphosing    ：変態（生物的変化）中
Misting           ：霧吹き中
Moonwalking       ：ムーンウォーク中
Mustering         ：かき集め中
Nebulizing        ：霧状化中
Nesting           ：巣作り中
Newspapering      ：新聞作り中
Noodling          ：思案・即興中
Nucleating        ：核形成中
Orbiting          ：軌道周回中
Orchestrating     ：編成・指揮中
Osmosing          ：浸透中
Perambulating     ：散策中
Perusing          ：熟読中
Philosophising    ：哲学的に思索中
Photosynthesizing ：光合成中
Pollinating       ：受粉中
Pondering         ：思案中
Pontificating     ：偉そうに語り中
Pouncing          ：飛びかかり中
Precipitating     ：沈殿（降水）中
Prestidigitating  ：手品中
Proofing          ：発酵（生地）中
Propagating       ：繁殖・伝播中
Quantumizing      ：量子化中
Razzle-dazzling   ：派手にきらめかせ中
Razzmatazzing     ：派手に演出中
Recombobulating   ：再びまとめ直し中
Reticulating      ：網目状に構成中
Roosting          ：止まり木で休み中
Sautéing          ：ソテー中
Scampering        ：ちょこまか走り中
Scurrying         ：慌てて走り中
Seasoning         ：味付け中
Shenaniganing     ：いたずら中
Skedaddling       ：急いで逃げ中
Sketching         ：スケッチ中
Slithering        ：にょろにょろ中
Smooshing         ：ぐちゃっと潰し中
Sock-hopping      ：ソックホップ中
Spinning          ：くるくる回転中
Sprouting         ：芽吹き中
Stewing           ：煮込み中
Sublimating       ：昇華中
Swirling          ：渦巻き中
Swooping          ：急降下中
Symbioting        ：共生中
Tempering         ：テンパリング中
Thinking          ：考え中
Thundering        ：雷鳴轟き中
Tinkering         ：いじり中
Tomfoolering      ：ふざけ中
Topsy-turvying    ：上を下への大騒ぎ中
Transfiguring     ：変容中
Twisting          ：ひねり中
Undulating        ：うねり中
Unfurling         ：広げ中
Unravelling       ：解きほぐし中
Waddling          ：よちよち歩き中
Warping           ：歪曲・ワープ中
Whatchamacalliting：「えーっと、あれ」状態中
Whirlpooling      ：渦潮中
Whisking          ：泡立て中
Wibbling          ：ぐらぐら中
Zesting           ：皮すりおろし中
Zigzagging        ：ジグザグ中
```

## 考察中...

187個の単語を眺めていると、いくつか面白い傾向が見えてきます。

まず圧倒的に多いのが料理・調理にまつわる単語。次に目立つのが「考える」の同義語の量です。

個人的に一番の見どころは、Combobulating／Discombobulating／Recombobulatingという三段活用の単語ファミリーが仕込まれている点です。

「こんがらがる」の逆である「整える」、さらにその逆をいく「再び整え直す」まで律儀に揃えているあたり、単なる単語リストというより小さな言葉遊びのコレクションとして設計されている印象を受けます。

さらにはネイティブでも初見では読めないような古い俗語（Flibbertigibbeting、Whatchamacalliting、Tomfoolering等）まで幅広く採用されており、「待たされている」という体験を、無機質な進捗表示ではなく、どこかコージーでユーモラスなものに変換しようとする意図が感じられます。

さて、皆さんはいくつ単語の意味が分かりましたか？  
最後にクイズです。次の3つ、意味を予想してみてください。

* Combobulating...
* Whatchamacalliting...
* Photosynthesizing...

答え

Combobulating ：整理整頓中（Discombobulatingの逆）  
Whatchamacalliting：「えーっと、あれ」状態中  
Photosynthesizing：光合成中

ありがとうございました！
