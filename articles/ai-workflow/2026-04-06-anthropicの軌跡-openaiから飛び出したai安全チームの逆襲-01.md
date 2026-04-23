---
id: "2026-04-06-anthropicの軌跡-openaiから飛び出したai安全チームの逆襲-01"
title: "Anthropicの軌跡 — OpenAIから飛び出したAI安全チームの逆襲"
url: "https://qiita.com/kinamocchi_tech/items/c2e689bcd163d1e06d13"
source: "qiita"
category: "ai-workflow"
tags: ["OpenAI", "qiita"]
date_published: "2026-04-06"
date_collected: "2026-04-06"
summary_by: "auto-rss"
---

## はじめに

🐹 もっちー「ねえきなこ、飼い主がまた新しいAIサービスに課金してるんだけど。」

🦜 きなこ「また？今度は何に課金したの？」

🐹 もっちー「Claudeっていうやつ。Anthropicって会社が作ってるらしいんだけど。」

🦜 きなこ「Anthropicね。実はこの会社、ものすごいドラマがあるの。」

🐹 もっちー「ドラマ？なになに、気になる！」

[![動画タイトルカード：「Anthropicの軌跡 — OpenAIから飛び出したAI安全チームの逆襲」](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F006_title_card.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=36cd4b575ba94051e3339bfb821d7111)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F006_title_card.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=36cd4b575ba94051e3339bfb821d7111)

🦜 きなこ「OpenAIの安全チームが「これじゃダメだ」って飛び出して作った会社なのよ。」

🐹 もっちー「なんでやねん！OpenAIから飛び出すとか、めっちゃ気になるやん！」

🦜 きなこ「今日はそのAnthropicの誕生から現在までを、たっぷり深掘りしていくね。」

## OpenAIを飛び出した7人

[![Dario Amodeiのプロフィール概要（Princeton物理学PhD、Hertz Fellow、計算神経科学）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F011_dario_profile.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=fdabb2c9871e9199c471db35e3806d66)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F011_dario_profile.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=fdabb2c9871e9199c471db35e3806d66)

🦜 きなこ「さて、Anthropicの話をするなら、まずは創業者のDario Amodeiから紹介しないとね。」

🐹 もっちー「ダリオさんね。どんな人なの？」

🦜 きなこ「Princetonで物理学と生物物理学のPhDを取った人で、計算神経科学が専門だったの。」

[![Darioの経歴タイムライン（Baidu AI 2014年→Google Brain 2015年→OpenAI 2016年）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F014_dario_timeline.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e3d4641fa7bb11b0cfcb50c6b7b8fa8c)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F014_dario_timeline.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e3d4641fa7bb11b0cfcb50c6b7b8fa8c)

🦜 きなこ「そこからBaiduのAI部門でAndrew Ngと一緒にDeep Speech 2を開発して、Google Brainを経て、OpenAIに入ったの。」

🐹 もっちー「Baidu、Google、OpenAIって、AIのオールスターチームを渡り歩いてるじゃん。」

[![OpenAIでの実績（VP of Research、GPT-2/3開発リード、RLHF共同発明）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F016_openai_achievements.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=226a1293e848fa983e3d8817f949d57a)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F016_openai_achievements.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=226a1293e848fa983e3d8817f949d57a)

🦜 きなこ「OpenAIではVP of Research、つまり研究担当副社長として、GPT-2とGPT-3の開発をリードしたの。」

🦜 きなこ「しかもRLHF、人間のフィードバックからの強化学習の共同発明者でもあるのよ。」

🐹 もっちー「RLHFってChatGPTが賢く答えてくれる仕組みのことだよね？それを作った人ってことか！」

🦜 きなこ「そうそう、よく分かってるね。AIに人間の好みを学ばせる技術の生みの親の一人なの。」

[![Daniela Amodeiのプロフィール（UCサンタクルーズ英文学卒、OpenAI VP of People→Anthropic社長）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F020_daniela_profile.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4506ae61904d45091f7ac052d2456a5d)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F020_daniela_profile.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4506ae61904d45091f7ac052d2456a5d)

🦜 きなこ「そして妹のDaniela AmodeiもOpenAIでVP of Peopleとして組織運営を担っていたの。」

🐹 もっちー「兄妹で起業したんだ。技術の兄と組織の妹、いいコンビだね。」

[![7人の共同創業者一覧（Dario、Daniela、Tom Brown、Jack Clark、Jared Kaplan、Sam McCandlish、Chris Olah）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F022_cofounders.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=84d934b475db3ec7bebc28810d275a19)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F022_cofounders.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=84d934b475db3ec7bebc28810d275a19)

🦜 きなこ「この2人を含む7人がOpenAIを離れたんだけど、理由はOpenAIの商業化路線への疑問だったの。」

🐹 もっちー「つまりさ、ラーメン屋で修行してた職人が「この店、味より金儲け優先になってきたな」って独立したようなもんだよね。」

🦜 きなこ「まあ、ラーメンかどうかはともかく、方向性は合ってるわね。」

🐹 もっちー「で、独立したのはいいけど、ちゃんと儲かる仕組みにしたの？」

[![Public Benefit Corporation（公益目的会社）の仕組み図](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F026_pbc_structure.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d59f20179f66d2d69a8b52dbce0f761e)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F026_pbc_structure.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d59f20179f66d2d69a8b52dbce0f761e)

🦜 きなこ「AnthropicはPublic Benefit Corporation、つまり公益目的会社として設立されたの。利益だけじゃなく社会的使命も追求する法人形態ね。」

[![LTBTの仕組み図（5人の信託者が取締役の選任・解任権を持つ）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F027_ltbt_structure.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=3751a96d78491c427b949f92032e2c9a)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F027_ltbt_structure.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=3751a96d78491c427b949f92032e2c9a)

🦜 きなこ「さらに2023年にはLong-Term Benefit Trust、長期利益信託を設立して、5人の信託者が公益ミッションを監視する体制を作ったの。」

🐹 もっちー「えっと、つまり会社が暴走しないように外から見張る仕組みってこと？」

🦜 きなこ「その通り。OpenAIで起きた2023年のお家騒動を構造的に防ぐ設計なの。」

[![2026年1月：創業者7人が個人資産の80%（推定210億ドル以上）を寄付すると誓約](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F030_donation_pledge.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=86dda93f0b49d019674d80ca271a7155)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F030_donation_pledge.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=86dda93f0b49d019674d80ca271a7155)

🐹 もっちー「ほんまかいな！しかも2026年1月には創業者7人全員が資産の80%を寄付するって宣言してるんだって！」

## AIに「憲法」を教える

🦜 きなこ「さて、ここからAnthropicの技術的な革新について話すね。」

[![RLHFの仕組みを図解（人間の評価者がモデル出力を比較・ランク付けするフロー）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F032_rlhf_diagram.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=97a1a51b2e6ad7514180b0acee7ef12b)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F032_rlhf_diagram.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=97a1a51b2e6ad7514180b0acee7ef12b)

🦜 きなこ「当時のAIの安全性訓練はRLHFっていう手法が主流だったの。」

🐹 もっちー「RLHF？なんか呪文みたいだけど、どういう意味？」

🦜 きなこ「人間のフィードバックによる強化学習、略してRLHFね。」

🦜 きなこ「AIが2つの回答を出して、人間が「こっちのほうがいいね」って選ぶ。それを繰り返して学習させるの。」

🐹 もっちー「なるほど、人間が先生になってAIを教育するわけか。」

[![RLHFの課題リスト（スケーラビリティの限界、人間のバイアス、コスト、一貫性欠如）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F037_rlhf_challenges.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=aa27d7c63cfee9998ad269eb4b3ef966)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F037_rlhf_challenges.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=aa27d7c63cfee9998ad269eb4b3ef966)

🦜 きなこ「そう。でもこの方法には大きな問題があったの。」

🦜 きなこ「評価する人間を大量に雇う必要があるし、人によって判断がブレる。しかも有害なコンテンツを人間が読み続けないといけない。」

🐹 もっちー「それって学校の先生が一人で何万人の生徒のテスト採点するみたいな話だよね。しかも問題文が全部ヤバい内容っていう。」

[![Constitutional AI（CAI）の概要図（2022年12月発表）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F040_cai_overview.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a362a89b439ddb66ffc6e1a03290fa2c)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F040_cai_overview.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a362a89b439ddb66ffc6e1a03290fa2c)

🦜 きなこ「いい例えね。そこでAnthropicが2022年12月に発表したのがConstitutional AI、通称CAIよ。」

🐹 もっちー「憲法のAI？AIに憲法を守らせるってこと？」

[![CAIの2段階プロセス図](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F042_cai_process.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=92cedf8991c0842d3d65dea725983e36)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F042_cai_process.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=92cedf8991c0842d3d65dea725983e36)

🦜 きなこ「近いわね。AIに「憲法」、つまり守るべき原則のセットを与えて、AI自身がその原則に基づいて自分の回答を批評・修正するの。」

🐹 もっちー「めっちゃええやん！人間の代わりにAI自身が先生になるってことか！」

[![「憲法」の内容例リスト（世界人権宣言、Appleの利用規約、DeepMindのSparrow Rules等）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F044_constitution_examples.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=631b5ecb6602ef4f08668ab21dd861c2)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F044_constitution_examples.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=631b5ecb6602ef4f08668ab21dd861c2)

🦜 きなこ「しかもこの「憲法」の中身がユニークなの。世界人権宣言やAppleの利用規約まで含まれてるのよ。」

🐹 もっちー「Appleの利用規約まで入ってるの？なんか面白い組み合わせだね。」

🦜 きなこ「大事なのは、この原則が全部公開されていること。どんなルールでAIが訓練されたか、誰でも確認できるの。」

[![バグバウンティの結果（参加者183名、テスト3,000時間以上、普遍的ジェイルブレイク未発見）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F047_bug_bounty.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2ef3748721e2e3ff190493b485b7a905)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F047_bug_bounty.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2ef3748721e2e3ff190493b485b7a905)

🦜 きなこ「さらに2025年にはConstitutional Classifiersのバグバウンティも実施したわ。」

🦜 きなこ「183名が3,000時間以上テストしたけど、普遍的なジェイルブレイクは見つからなかったの。」

🐹 もっちー「183人がかかっても突破できなかったってこと？それはかなり頑丈だね！」

## AIの脳を覗く研究者たち

🦜 きなこ「さて、ここからはAnthropicの研究の中でも特に注目すべき分野を紹介するね。」

[![「機械的解釈可能性」のタイトルと概念図](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F050_interpretability.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=09c00eaaaab8a2857a6d12ea8b51f017)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F050_interpretability.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=09c00eaaaab8a2857a6d12ea8b51f017)

🦜 きなこ「機械的解釈可能性、英語ではMechanistic Interpretabilityって呼ばれる研究分野なの。」

🐹 もっちー「メカニスティック…なんか難しそうな名前だね。何をする研究なの？」

🦜 きなこ「簡単に言うと、AIの脳の中で何が起きてるかを解明する研究だよ。」

🐹 もっちー「つまり、AIの頭をカパッと開けて、中の配線を調べるみたいなこと？」

🦜 きなこ「まさにそんなイメージ。Dario Amodeiも「自分たちが作ったAIがどう動くか分からない」って認めてるの。」

[![Chris Olahと「Superposition（重ね合わせ）」の概念図](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F055_superposition.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=bf58ed38793c492520e8f095915baea2)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F055_superposition.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=bf58ed38793c492520e8f095915baea2)

🦜 きなこ「この研究を率いるのがChris Olahというエンジニアで、彼は2022年にSuperpositionという核心問題を解明したの。」

🐹 もっちー「スーパーポジション？重ね合わせ？」

🐹 もっちー「あ、わかった。ハムスターの頬袋みたいなもんだ。1つの袋にヒマワリの種もペレットも全部詰め込んじゃう感じ？」

🦜 きなこ「意外といい例えかも。1つのニューロンが複数の概念を混ぜて記憶してるから、何を考えてるか解読しにくいの。」

[![「Scaling Monosemanticity」の成果概要（Claude 3 Sonnetから数百万の特徴を抽出）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F059_scaling_mono.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=966863879bbadfe32b0c84d29bde0424)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F059_scaling_mono.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=966863879bbadfe32b0c84d29bde0424)

🦜 きなこ「そして2024年5月、ついにClaude 3 Sonnetの「心」を覗くことに成功したの。数百万もの特徴を抽出したのよ。」

🐹 もっちー「ほんまかいな！AIの頭の中が見えるようになったってこと？」

[![Golden Gate Claude実験の概要](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F061_golden_gate.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=3379e7fd83e526cfb397bca829451b25)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F061_golden_gate.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=3379e7fd83e526cfb397bca829451b25)

🦜 きなこ「しかもここからが面白くて。Golden Gate Bridgeに対応する特徴を見つけて、それを10倍に増幅したの。」

🐹 もっちー「増幅したらどうなったの？」

🦜 きなこ「Claudeが「私はGolden Gate Bridgeです」って主張し始めたの。何を聞いても橋の話に持っていくようになったのよ。」

🐹 もっちー「なんでやねん！AIが橋になるとか意味わからん！」

🦜 きなこ「実はこれ、すごく重要な実験なの。特徴が「たまたま反応してる」んじゃなくて「原因として効いてる」って証明したのよ。」

[![Circuit Tracing（2025年3月）の主要発見リスト](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F066_circuit_tracing.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=f486249d0fa3f59b2769f36c7cdb2840)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F066_circuit_tracing.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=f486249d0fa3f59b2769f36c7cdb2840)

🦜 きなこ「そして2025年のCircuit Tracingでは、Claudeが言語を超えた「普遍的な思考言語」を持つことが発見されたの。」

🐹 もっちー「めっちゃすごいやん！AIの脳を覗く技術がここまで進んでるんだ。」

[![MIT Technology Review「2026年のブレークスルー技術」選出バッジ](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F068_mit_tech_review.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2c8a338ed3c8316eb57a0f7a02824d45)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F068_mit_tech_review.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2c8a338ed3c8316eb57a0f7a02824d45)

🦜 きなこ「この研究はMIT Technology Reviewの「2026年のブレークスルー技術」にも選ばれたの。AIの安全性を語る上で欠かせない分野よ。」

## 爆速成長の記録

[![Anthropic資金調達タイムライン（Series A〜G、2021年〜2026年の棒グラフ）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F069_funding_timeline.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=b12a9eed533ab1ed0295903c1dcf87f9)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F069_funding_timeline.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=b12a9eed533ab1ed0295903c1dcf87f9)

🦜 きなこ「ここからはAnthropicの資金調達の歴史を見ていくね。」

🐹 もっちー「お金の話きた。ここからはワイの出番やな。」

🦜 きなこ「2021年5月のSeries Aでは1億2400万ドルを調達したの。」

🦜 きなこ「リードはSkype共同創業者のヤーン・タリンさん。AI安全性に共感した投資家が集まったの。」

🐹 もっちー「1億ドルでもすごいけど、ここからが本当にヤバいんだよね？」

[![FTX Series B投資の概要（$580M、Sam Bankman-Fried、2022年4月）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F074_ftx_series_b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0fa0d70f7e424ebbc08526f967207715)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F074_ftx_series_b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0fa0d70f7e424ebbc08526f967207715)

🦜 きなこ「そう。2022年のSeries Bでは5億8000万ドル。リードはFTXのサム・バンクマン・フリードだったの。」

🐹 もっちー「FTXって、あの崩壊した仮想通貨取引所の？」

🦜 きなこ「そう。FTXは2022年11月に破綻して、Anthropic株は破産手続きで売却されたの。」

🐹 もっちー「嵐を乗り越えたってことか。投資家ガチャでハズレ引いても生き残ったのがすごい。」

[![ビッグテック戦略的投資まとめ（Amazon $8B、Google $2-3B、Microsoft&Nvidia $15B）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F078_bigtech_investment.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=36f3367b2a09259ccecf70dae3305028)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F078_bigtech_investment.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=36f3367b2a09259ccecf70dae3305028)

🦜 きなこ「そこからビッグテックが一気に動いたの。Amazonが累計80億ドル、Googleが20〜30億ドルを投資。」

🐹 もっちー「80億ドル!? ほんまかいな！ワイのひまわりの種何粒分やねん！」

🦜 きなこ「さらに2025年11月にはMicrosoftとNvidiaが合計150億ドルの戦略提携を発表したの。」

🦜 きなこ「これでClaudeはAWS、Google Cloud、Azureの3大クラウド全てで使える唯一のフロンティアモデルになったの。」

🐹 もっちー「全部のクラウドで使えるって、つまりどのお店にも置いてある人気商品ってことだよね。」

[![Series G詳細（$30B調達、バリュエーション$380B）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F083_series_g.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=31bb91d2836b774659fa4c674a81b439)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F083_series_g.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=31bb91d2836b774659fa4c674a81b439)

🦜 きなこ「そして2026年2月のSeries Gで300億ドルを調達。バリュエーションは3800億ドルに到達したの。」

🐹 もっちー「3800億ドルって日本円で50兆円超えやん！めっちゃええやん！」

[![ARR成長グラフ（$87M→$1B→$5B→$14B→$19B）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F085_arr_growth.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4c3ba4c3fe873e3c718256c52c559171)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F085_arr_growth.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4c3ba4c3fe873e3c718256c52c559171)

🦜 きなこ「売上の伸びも異次元なの。2024年1月のARR8700万ドルから、2026年3月には190億ドル。26ヶ月で218倍よ。」

🐹 もっちー「ARRっていうのは、今月の売上を12倍して年間に換算した数字のことね。直近の勢いが分かる指標だよ。」

[![Claude Code ARR推移（$500M→$1B→$2.5B）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F087_claude_code_arr.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6f70d12deb88645352345e9821d8562e)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F087_claude_code_arr.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6f70d12deb88645352345e9821d8562e)

🦜 きなこ「特にClaude Codeは単体でARR25億ドル。史上最速で成長したプロダクトと言われているの。」

🐹 もっちー「Fortune 10の8社が使ってるって、もうトップ企業の定番ツールやん。ワイも投資したいわ！」

## 安全チーム崩壊の裏側

🦜 きなこ「ここからは、OpenAIの内部で何が起きていたかを見ていくね。」

[![Superalignmentチーム設立の概要（2023年7月、Ilya SutskeverとJan Leike共同リーダー、計算資源20%の約束）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F090_superalignment.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=1e28602930cc3b52b8feff3927837b07)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F090_superalignment.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=1e28602930cc3b52b8feff3927837b07)

🦜 きなこ「2023年7月、OpenAIは「Superalignment」チームを設立したの。」

🐹 もっちー「スーパーアライメント？なんかカッコいい名前だけど、何するチームなの？」

🦜 きなこ「超知能、つまり人間を超えたAIが暴走しないように制御する技術を研究するチームだよ。」

🐹 もっちー「人間超えちゃうの？それ怖くない？」

🦜 きなこ「だからこそ必要なの。リーダーは共同創業者のIlya Sutskeverとアライメント責任者のJan Leike。」

🦜 きなこ「しかも「計算資源の20%をこのチームに充てる」と公式に約束したの。」

🐹 もっちー「20%！めっちゃ本気やん！」

[![「20%計算資源」の約束と現実の対比](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F096_20pct_promise.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=1cbee9879f70b120cdbd46f94e861ef2)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F096_20pct_promise.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=1cbee9879f70b120cdbd46f94e861ef2)

🦜 きなこ「でもね、この約束は結局ほとんど守られなかったの。」

🦜 きなこ「チーム関係者の証言では、ごく一部の計算資源を要求しても拒否されることが多かったと。」

🐹 もっちー「なんでやねん！約束したんちゃうんかい！」

🐹 もっちー「これ、ハムスターに「毎日ひまわりの種10粒あげるよ」って言って2粒しかくれないのと同じだよね。」

[![タイムライン: 2024年の大量離職（5月 Ilya辞任→SSI設立、5月 Jan Leike→Anthropic、8月 Schulman→Anthropic、9月 Murati退職）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F100_exodus_timeline.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=387466b907dc008d7364ec00d0d46a35)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F100_exodus_timeline.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=387466b907dc008d7364ec00d0d46a35)

🦜 きなこ「そうね。そして2024年5月、ついにIlyaが辞任してSafe Superintelligence Inc.を設立。」

🦜 きなこ「翌日にはJan Leikeも辞任。声明で「安全文化は華やかな製品に後回しにされた」と告発したの。」

🐹 もっちー「安全より製品を優先したってことか。それはキツいなぁ。」

🦜 きなこ「Jan Leikeはその後Anthropicに移籍して、今はアライメントサイエンスチームを率いてるわ。」

[![Daniel Kokotajloの非誹謗契約拒否（約$1.7M=約2.5億円の株式リスク）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F104_kokotajlo.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e44c2fe39529875d0db4711280ab8dcf)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F104_kokotajlo.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e44c2fe39529875d0db4711280ab8dcf)

🦜 きなこ「さらに衝撃的なのが、元研究者Daniel Kokotajloの件。」

🦜 きなこ「OpenAIの非誹謗契約に署名しないと、約2.5億円分の株式が取り消される条件だったの。」

🐹 もっちー「2.5億円を捨てる覚悟で会社を批判したってこと？それはすごい勇気だよ。」

🦜 きなこ「その後もCTOのMira MuratiやJohn Schulmanなど、幹部が次々と離職していったの。」

[![構造図: OpenAIの安全チーム崩壊（Superalignment設立→計算資源未配分→幹部離職→Anthropic/SSI設立の流れ）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F108_safety_collapse.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6632aa035085fa1c3891d96ca0549678)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F108_safety_collapse.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6632aa035085fa1c3891d96ca0549678)

🦜 きなこ「安全か商業化か。この衝突がOpenAIの内部崩壊を引き起こし、Anthropic誕生の伏線になったわけ。」

## Dario Amodeiの哲学

🦜 きなこ「ここからはDario Amodeiの思想に踏み込んでみましょう。」

[![「Machines of Loving Grace」エッセイ概要（2024年10月、約15,000語）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F110_loving_grace.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=099ed12c2dad4fd06028da771e35734e)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F110_loving_grace.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=099ed12c2dad4fd06028da771e35734e)

🦜 きなこ「2024年10月、彼は「Machines of Loving Grace」という約1万5千語のエッセイを公開したの。」

🐹 もっちー「1万5千語って、本1冊分くらいの量じゃない？」

🦜 きなこ「そうね、50ページくらい。そこで彼は「AGI」という言葉を意図的に避けて、「強力なAI」と呼んだの。」

[![5つの楽観的変革領域（①生物学 ②神経科学 ③経済発展 ④平和 ⑤仕事・意味）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F113_loving_grace_domains.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5255fa2e1e3426eea0cfb9ca31cd54db)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F113_loving_grace_domains.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5255fa2e1e3426eea0cfb9ca31cd54db)

🦜 きなこ「「データセンター内の天才たちの国」がAIの未来だと。生物学、経済、平和など5つの領域で世界を変えると書いてる。」

🐹 もっちー「つまり「AIがあれば全部うまくいく！」って話？ちょっと楽観的すぎない？」

🦜 きなこ「実はね、Darioの面白いところはそこなの。楽観的なビジョンを語りながら、ちゃんとリスクも直視してる。」

[![「The Adolescence of Technology」（2026年1月、約20,000語、5つのAIリスク）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F116_adolescence.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e11f783c88b7f51e0c27e0da8ecd6468)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F116_adolescence.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e11f783c88b7f51e0c27e0da8ecd6468)

🦜 きなこ「2026年1月、対となるエッセイ「The Adolescence of Technology」を発表。こっちは2万語でリスクを徹底的に論じてる。」

🐹 もっちー「楽観と悲観、両方書くってすごいな。で、どんなリスクがあるの？」

[![5つのAIリスク（①自律性 ②破壊的悪用 ③権力掌握 ④経済的混乱 ⑤社会不安定化）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F118_five_risks.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=45f73d591007e7f02aa2dd2391766a1b)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F118_five_risks.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=45f73d591007e7f02aa2dd2391766a1b)

🦜 きなこ「AIの自律性リスク、生物兵器などの破壊的悪用、権威主義政府による悪用、経済的混乱、そして社会の不安定化。5つよ。」

🐹 もっちー「ほんまかいな！自分で作っといて「危ないかも」って言うんかい！」

[![Darioの発言引用:「1〜5年以内にホワイトカラー職の50%を混乱させる」](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F120_dario_quote_jobs.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=493ea3e8124f9681dd88567add92d047)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F120_dario_quote_jobs.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=493ea3e8124f9681dd88567add92d047)

🦜 きなこ「しかも「AIは1〜5年以内にエントリーレベルのホワイトカラー職の50%を混乱させる」とまで明言してるの。」

🐹 もっちー「50%って半分だよ！？新入社員の仕事の半分がAIに取られるってこと？」

[![25%壊滅的リスク見積もり](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F122_catastrophic_risk.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=8c745665315ea0395af69af54c2dd473)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F122_catastrophic_risk.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=8c745665315ea0395af69af54c2dd473)

🦜 きなこ「そしてもう一つ。彼は壊滅的なリスクの確率を25%と見積もっているの。4回に1回は大惨事になるかもしれないと。」

🐹 もっちー「だからこそ安全性にこだわってるわけか。口だけじゃなくて、行動でも示してるの？」

[![ペンタゴンとの対立（2026年2月）：Claude利用要求を拒否→サプライチェーンリスクに指定](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F124_pentagon.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=eb0d1fd1cd3ef6c42e0850755500936f)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F124_pentagon.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=eb0d1fd1cd3ef6c42e0850755500936f)

🦜 きなこ「2026年2月、ペンタゴンが大規模監視や自律兵器にClaudeを使わせろと要求したの。Darioは拒否した。」

🐹 もっちー「めっちゃええやん！国にケンカ売るとか度胸あるなぁ！」

🦜 きなこ「でも代償は大きくて、Anthropicは「サプライチェーンリスク」に指定されて、連邦機関での使用が禁止されたの。」

[![流出メモ：OpenAIの取引を「safety theater」と批判](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F127_safety_theater.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=210aff91ac04b83db73af4b48d6b429f)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F127_safety_theater.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=210aff91ac04b83db73af4b48d6b429f)

🦜 きなこ「さらに内部メモが流出して、OpenAIの政府取引を「safety theater」と批判してたことも明るみに出た。」

🐹 もっちー「理想を貫くけど、裏では競合をバッサリか。なんか人間くさくて逆に信用できるかもね。」

## Claudeの進化とスーパーボウル

🦜 きなこ「さて、ここからはAnthropicのプロダクト面を見ていくね。」

[![Claudeモデル進化タイムライン（Claude 1→2→3→4→4.6）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F130_claude_timeline.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2301abdde0a9ccdb71ec613ee6041bc3)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F130_claude_timeline.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2301abdde0a9ccdb71ec613ee6041bc3)

🦜 きなこ「Claudeは2023年の初代から急速に進化してきたの。」

🦜 きなこ「2024年にClaude 3ファミリーが登場して、Haiku・Sonnet・Opusの3段構成に。」

🐹 もっちー「で、2026年2月に出た最新のOpus 4.6がすごいんでしょ？」

[![Opus 4.6スペック（1Mトークン、14.5時間タスクホライズン）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F133_opus_specs.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a2119518626155c85c5169c8ff9716ec)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F133_opus_specs.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a2119518626155c85c5169c8ff9716ec)

🦜 きなこ「そう。コンテキストウィンドウが100万トークン。14.5時間の自律タスクをこなせるの。」

🐹 もっちー「100万トークンって、本一冊まるごと読ませて質問できるみたいなもんだよね。」

[![Claude Code成長グラフ（研究プレビュー→GA→ARR $2.5B）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F135_claude_code_growth.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=cd4ff4586984fa315c4398864ccbea4a)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F135_claude_code_growth.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=cd4ff4586984fa315c4398864ccbea4a)

🦜 きなこ「そしてプロダクト面で特に注目なのがClaude Codeね。」

🦜 きなこ「2025年2月に研究プレビューで出て、5月にGA。そこから3ヶ月でARR5億ドル突破。」

🐹 もっちー「めっちゃええやん！で、2026年2月にはARR25億ドルやろ？エグいて！」

🦜 きなこ「JavaScriptランタイムのBunも買収して、インフラ強化に動いてるの。」

[![Claude Cowork概要（非技術系向けAIエージェント）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F139_cowork.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d338f28842f48560c2e571d768705972)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F139_cowork.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d338f28842f48560c2e571d768705972)

🦜 きなこ「もう一つ、Claude Coworkっていう非エンジニア向けのエージェントも出たの。」

🐹 もっちー「プログラマーじゃない人でもAIエージェントが使えるってこと？」

🐹 もっちー「回し車みたいなもんやな。前はハムスター専用だったのが、インコでも乗れるようになったみたいな。」

🦜 きなこ「インコは回し車に乗らないけど、まあ言いたいことは伝わるわ。」

🦜 きなこ「そう。影響は大きくて、エンタープライズソフトウェア株に1兆ドル規模の売りが出たの。」

🐹 もっちー「1兆ドル！？飼い主の持ち株も下がってへんか心配やわ。また課金も増えてるし。」

[![スーパーボウルLX広告「A Time and a Place」（2026年2月8日）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F143_superbowl.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=871f75a3a2de28319e6c61a48ce667dd)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F143_superbowl.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=871f75a3a2de28319e6c61a48ce667dd)

🦜 きなこ「そしてAnthropicのマーケティングで一番話題になったのが、スーパーボウルの広告。」

🦜 きなこ「「AIに広告は来る。でもClaudeには来ない」っていう宣言をしたの。」

🐹 もっちー「OpenAIがChatGPTに広告入れるって言った直後にこれやるの、ケンカ売ってるよね。」

[![Sam Altmanの反応（「clearly dishonest」「authoritarian」）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F146_altman_reaction.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=b9fd287f84c2565b34828d569046da9b)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F146_altman_reaction.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=b9fd287f84c2565b34828d569046da9b)

🦜 きなこ「Sam Altmanも反応して「明らかに不正直だ」「権威主義的だ」と強く批判したの。」

[![スーパーボウル広告の効果（App Store 41位→7位、DAU 11%増）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F147_superbowl_impact.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=20fe7d690bde9880d9cf1cecbb01bc90)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F147_superbowl_impact.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=20fe7d690bde9880d9cf1cecbb01bc90)

🐹 もっちー「でも結果はApp Storeで41位から7位に急上昇、DAUも11%増やろ？大勝利やん！」

🦜 きなこ「IPOの準備も進めてるという報道もあって、Anthropicの勢いは止まらないわね。」

## まとめ

[![まとめスライド：Anthropicの軌跡 3つのポイント](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F149_summary.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=53c3a0f0a7d47cce54dcd1ed322a9d20)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F149_summary.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=53c3a0f0a7d47cce54dcd1ed322a9d20)

🐹 もっちー「さて、今日のAnthropicの話をまとめていこうか。」

🦜 きなこ「まず、OpenAIの安全チームから飛び出して、安全性を企業の柱に据えたこと。」

🐹 もっちー「「安全じゃないなら作らない」って姿勢を創業から貫いてるのがすごいよね。」

🦜 きなこ「次に、Constitutional AIや解釈可能性研究といった技術的イノベーション。」

🐹 もっちー「AIの中身をちゃんと理解しようって研究、地味だけどめちゃくちゃ大事だよ。」

🦜 きなこ「そして3つ目、ARR190億ドル、評価額3800億ドルという爆速成長ね。」

🐹 もっちー「安全性と成長を両立させてるの、ほんまにすごいわ！」

🦜 きなこ「理想と現実を両方追いかける姿勢、見習いたいわね。」

🐹 もっちー「ところでさ、うちの飼い主、Claude Proに毎月課金してるんだよね。」

🦜 きなこ「その分、私たちのおやつ代に回してほしいんですけど。」

🐹 もっちー「でもこの動画もClaudeに手伝ってもらってるから、感謝しないとね！」

🦜 きなこ「まあ、それは確かにそうね。ありがたく使わせてもらいましょう。」

[![コメント誘導：「Anthropicの安全性へのこだわり、どう思う？」](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F161_comment_cta.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=26fff0b1448cb49ec275c75e71012ffe)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fpub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev%2Fimages%2FV002%2F161_comment_cta.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=26fff0b1448cb49ec275c75e71012ffe)

🐹 もっちー「さて、みんなに聞きたいんだけど。」

🐹 もっちー「Anthropicの安全性へのこだわり、みんなはどう思う？コメントで教えてね。」

🦜 きなこ「「安全性は必要だけど開発スピードも大事」とか、いろんな意見を聞きたいです。」

🐹 もっちー「あと、OpenAIの話も別の動画で深掘りしたいよね。」

🦜 きなこ「Anthropicとの違いを比較するのも面白そうね。興味があったらぜひコメントで教えてね。」

---

**きなこもっちーのテック深掘り** では、AI/LLM を中心としたテック全般をハムスター（🐹 もっちー）とセキセイインコ（🦜 きなこ）の掛け合いで楽しく解説しています。

チャンネル登録・高評価よろしくお願いします！ → <https://www.youtube.com/watch?v=YfrMEwlpAG0>
