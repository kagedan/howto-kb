---
id: "2026-06-19-appleがgoogleに屈したwwdc-2026-siri-aiがgemini-12tに進化した本-01"
title: "AppleがGoogleに屈した？WWDC 2026 Siri AIがGemini 1.2Tに進化した本当の理由"
url: "https://qiita.com/kinamocchi_tech/items/cc0a149c32869ced21bd"
source: "qiita"
category: "construction"
tags: ["AI-agent", "LLM", "Gemini", "GPT", "construction", "qiita"]
date_published: "2026-06-19"
date_collected: "2026-06-20"
summary_by: "auto-rss"
query: ""
---

:::message
📺 この記事は YouTube チャンネル **きなこもっちーのテック深掘り** の動画解説記事です。
▶️ 動画はこちら → [AppleがGoogleに屈した？WWDC 2026 Siri AIがGemini 1.2Tに進化した本当の理由](https://www.youtube.com/watch?v=vBdyJp4gwak)
:::

## はじめに

🦜 きなこ「Apple が自前主義を捨てた。Siri AI の中核は、Google Gemini ベースのカスタムモデルなんだよ。」

🐹 もっちー「ええっ！？ Apple が Google にお金払って Siri を任せたん！？ あの自前主義の Apple が！？」

🦜 きなこ「そう。WWDC 2026 で発表された Siri AI——複数報道では Google Gemini ベースの 1.2 兆パラメータ・年間 10 億ドル契約とされてる。」

![Apple Newsroom 公式リリースのスクショ（Gemini 文字なし）と TechCrunch・TechTimes 報道スクショの対比](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/004.png)

🦜 きなこ「でもね、ここが大事。Apple Newsroom の公式リリースには「Gemini」って単語が一切出てこないの。」

🐹 もっちー「えっ、ほんとに？ じゃあ Apple は公式には何て言ってるの？」

🦜 きなこ「今日はその「公式と報道のギャップ」を含めて、全部一緒に解きほぐすね。」

![Tim Cook の WWDC キーノートステージ写真](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/007.png)

🦜 きなこ「歴史的なのは、これが Tim Cook 最後の WWDC キーノートだったこと。Apple は AI 戦略を根本から転換したんだよ。」

![本動画3つの注目ポイント箇条書き（3層アーキ / Multi-AI Extensions / EU・中国の不在）](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/008.png)

🦜 きなこ「この動画では3層アーキテクチャ、Multi-AI Extensions、EU・中国の不在まで——全部わかるようにするから最後まで見てね。」

🐹 もっちー「ぼくも知りたい！ Apple がなんで方針変えたのか、めっちゃ気になるよ！」

🦜 きなこ「まずは WWDC 2026 で何が発表されたか、ざっと見てから核心に入っていこう。」

## WWDC 2026 の核心 — Siri AI と6つの OS、同時刷新

![WWDC 2026 のロゴと開催日 2026年6月8日を表示](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/020.png)

🦜 きなこ「じゃあ、まず WWDC 2026 で何が発表されたか整理するね。」

![iOS 27 / iPadOS 27 / macOS 27 / watchOS 27 / tvOS 27 / visionOS 27 の6つのアイコンを横並びで表示](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/021.png)

🦜 きなこ「今回の WWDC は規模がすごくて、iOS 27・iPadOS 27・macOS 27・watchOS 27・tvOS 27・visionOS 27、6つの OS を一気に発表したんだよ。」

🐹 もっちー「6つ！？ 全部同時って凄ない！？ めっちゃ総力戦やん！」

🦜 きなこ「そうなの。これが Apple の本気のところで、全プラットフォームに一斉展開するのは珍しい動き方なんだよ。」

![Siri の新しい standalone アプリのアイコンイメージと「独立アプリ化」のテキストを表示](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/024.png)

🦜 きなこ「で、その中核にあるのが次世代 Siri——Siri AI の発表なんだ。今回の Siri は大きく変わって、専用の独立したアプリとして生まれ変わるの。」

🐹 もっちー「独立アプリ？ Siri ってずっとホームボタン長押しで出てくるやつじゃなかったっけ？」

🦜 きなこ「そのイメージで合ってるよ。今までは OS に組み込まれた機能だったけど、今回から Siri は専用アプリとして独立するんだ。ホーム画面に並ぶアプリとして起動できるようになるの。」

![iPhone と Mac の間で会話履歴が iCloud 経由で同期されるイメージ図](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/027.png)

🦜 きなこ「それだけじゃなくて、会話の履歴を iCloud で同期できるようになるんだよ。iPhone で途中まで話した内容を、Mac で引き継いで続けられる。」

🐹 もっちー「それ、チャット AI みたいだよね。ChatGPT の会話履歴と同じ感じじゃない？」

🦜 きなこ「まさにその方向なの。UX 自体が対話形式、つまり conversational に変わるんだよ。聞いたら終わりじゃなくて、会話を重ねて深掘りできる Siri になるってこと。」

🐹 もっちー「でも…それって Apple が自分でぜんぶ作ったの？ さっき Gemini って言ってたけど、その辺がよくわかってないんだよね…」

![リリーススケジュールのタイムライン図：開発者ベータ（2026-06-08）→ パブリックベータ（2026年7月）→ 一般公開（2026年秋）](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/031.png)

🦜 きなこ「そこが今日のポイントの核心なんだけど、その話は次のパートで詳しく掘るね。まずリリーススケジュールを押さえておこう。」

🦜 きなこ「開発者ベータは 6 月 8 日の発表と同日に提供開始。パブリックベータが 7 月、一般公開が 2026 年秋の予定なんだ。」

🐹 もっちー「秋か。iPhone の新モデルと一緒に来る感じかな？」

![Federighi の引用バッジ：「a profoundly more intelligent, knowledgeable, and capable Siri」](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/034.png)

🦜 きなこ「タイミング的にはそうなりそうだね。で、この発表に際して Craig Federighi が言った言葉がすごく印象的で。」

🦜 きなこ「「profoundly more intelligent」——格段に賢く、知識豊富で、できることが増えた Siri って言い切ったんだよ。」

🐹 もっちー「Federighi がそこまで言うなら、ほんまに別物になったんやろな！ ワイでも使いこなせるやつ出てきてほしいわ！」

🦜 きなこ「そのためにも、中身を知っておく必要があるんだよ。じゃあ次はこの新しい Siri の中身——「Gemini 1.2T」「3層ルーティング」っていう本当の中核を見ていこう。」

## 3層アーキテクチャと Gemini 1.2T — 巨大モデルとプライバシーをどう両立したか

![3層ルーティング図解（Tier 1: デバイス / Tier 2: Private Cloud Compute / Tier 3: Google Cloud）](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/038.png)

🐹 もっちー「ちょっと待って、3層ルーティングって何なの？ なんか難しそうだけど。」

🦜 きなこ「簡単に言うと、Siri へのリクエストを3段階で振り分ける仕組みなの。」

🦜 きなこ「一番軽い Tier 1 は、タイマー設定とか音楽再生みたいなシンプルな処理。これは完全にデバイス内で完結するよ。」

🦜 きなこ「Tier 2 は中程度の複雑さ。ここは Apple Silicon を積んだ専用サーバ、Private Cloud Compute が処理するの。」

🦜 きなこ「そして本当に重い推論が必要なときだけ、Tier 3——Google Cloud に行く構造なんだよ。」

🐹 もっちー「プライバシーって言うけど、結局 Google Cloud にデータ送るんやろ？ 大丈夫なん？」

![Apple 公式引用バッジ「Bold new architecture uniquely designed to protect users' privacy」](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/044.png)

🦜 きなこ「そこが肝心なとこなの。Apple は公式に「Bold new architecture uniquely designed to protect users' privacy」って言ってる。」

🦜 きなこ「Google Cloud に飛ぶのはごく一部の重い処理だけで、データはリクエスト実行にしか使われない、って設計なんだよね。」

🐹 もっちー「なるほど。じゃあ Google Cloud で動かすモデルって、具体的に何なの？」

![Apple Newsroom スクショ（Gemini 文字なし）vs 報道スクショ の対比](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/047.png)

🦜 きなこ「ここ重要なんだけど、Apple の公式リリースには「Gemini」って名前も、パラメータ数も一切書かれてないの。」

![「Gemini ベース・約 1.2T パラメータ MoE」表示（隣に小さく「press 報道」バッジ）](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/048.png)

🦜 きなこ「複数の報道では、Gemini ベースで約 1.2 兆パラメータ、MoE アーキテクチャのカスタムモデルとされてる。」

🐹 もっちー「1.2 兆！？ 従来の 8 倍やん！ でも「press 報道では」ってことは確定じゃないんやな。」

🦜 きなこ「そう。数字を見るときは必ず出典を確認してね。報道と公式はきっちり分けて話す必要があるの。」

![「NVIDIA Blackwell B200 GPU」表示（「複数報道」バッジ）](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/051.png)

🦜 きなこ「Tier 3 で動かす GPU についても、複数の報道では NVIDIA の Blackwell B200 とされてる——これも Apple 公式は未公表だよ。」

🐹 もっちー「お金的にはどれくらいかかってるの？ Google に払う金額とか。」

![年間 10 億ドル bar chart（「Bloomberg 報道」バッジ）](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/053.png)

🦜 きなこ「Bloomberg の Mark Gurman は、Apple が Google に年間 10 億ドル規模を支払う複数年契約と報じてる。」

🦜 きなこ「これも公式発表に金額の記載はないから、Bloomberg 報道として受け取ってほしいの。」

🐹 もっちー「Apple が公式で言ってないことと、報道ベースのことが混ざってたんだね。ちゃんと分けて見ないとだ。」

🦜 きなこ「そこが今回のポイント。公式は「プライバシーを守る新設計」と言って、数字の詳細は出さない。スマートな戦略だよね。」

![Extensions 選択画面モックアップ（Claude/ChatGPT/Gemini/Grok ロゴ）予告](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/057.png)

🦜 きなこ「じゃあ次は、もう一つ衝撃的な発表——Siri が Claude や ChatGPT に呼びかけられる、つまり Multi-AI Extensions の話だよ。」

## Multi-AI Extensions — iPhone が『誰の AI で動くか』を選ぶ時代へ

![Extensions 選択画面モックアップ（Claude / ChatGPT / Gemini / Grok のロゴ並列）](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/058.png)

🐹 もっちー「次は Extensions の話だね！ Claude も ChatGPT も Gemini も Grok も選べるって、ぼくもう興奮が止まらないよ！」

![『iOS 27 / iPadOS 27 / macOS 27』＋『Extensions フレームワーク導入』のテキスト](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/059.png)

🦜 きなこ「Apple は iOS 27 と iPadOS 27、macOS 27 に『Extensions』という新しいフレームワークを導入することを発表したんだよ。」

🦜 きなこ「Settings から Claude・ChatGPT・Gemini・Grok を Apple Intelligence の既定 AI に選べるの。」

🐹 もっちー「Claude も ChatGPT も Gemini も選べるって、めっちゃええやん！ でも正直、どれ選ぶのが正解なん？ 全部使いたいわー！」

![4社 AI の強み比較表（Claude / ChatGPT / Gemini / Grok）](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/062.png)

🦜 きなこ「正解は一つじゃないの。使い方によって向いてる AI が全然違うから、自分の使い方で選んでみてって感じ。整理してみるね。」

🦜 きなこ「Claude は agent 操作と computer-use が強み。複数アプリを跨いで自律的に作業を進めてもらいたい人、たとえばファイル整理や予約まで任せたい人向きなんだよ。」

🦜 きなこ「ChatGPT は会話の自然さと汎用性が高い。Gemini は Google 検索との連動で最新情報に強くて、Grok は X のリアルタイム情報と連動してる。」

🐹 もっちー「ブラウザで Safari か Chrome か Firefox か選ぶみたいな感じで、AI も自分に合ったものを使えばいい時代になった、ってこと？」

🦜 きなこ「まさにそのとおり。ブラウザや地図アプリのデフォルト選択の AI 版なんだよ。Apple はその選択権をユーザーに渡したんだよね。」

🐹 もっちー「でもさ、たとえば仕事は Claude で、暇つぶしの会話は ChatGPT でって、タスクごとに切り替えるのはできるの？」

![『1 デバイスにつき 1 Extension』注釈バッジ＋『タスク別切替：未対応』](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/068.png)

🦜 きなこ「そこは制約があって、今のリリースでは 1 デバイスにつき 1 Extension しか設定できないの。タスク別の切り替えは今回はまだ未対応。」

🐹 もっちー「えっ、タスク別の切り替えはまだできないんだ。Settings で一個だけ選んで、それがずっと使われる感じなんだね。」

🦜 きなこ「そう。バージョン 1 の仕様だから、今後のアップデートで柔軟になる可能性はあると思う。SDK は開発者に公開済みだし、これからに期待なんだよ。」

🦜 きなこ「でも、この Extensions で一番大事なのは仕様の話じゃなくて、Apple がこれを作った戦略的な意味なんだよ。」

🦜 きなこ「Apple は OS という土台だけを握って、AI 本体は外部プロバイダから供給させる。自分で AI を抱え込まずプラットフォーマーに徹するという判断なんだよ。」

🐹 もっちー「iPhone が『単一の AI のフロントエンド』から、『自分の AI を選ぶプラットフォーム』に変わったってこと？ なんか歴史が動いてる感じがするな。」

![『単一 AI → 複数 AI 共存』の構造転換図](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/074.png)

🦜 きなこ「その感覚は正しいよ。Apple Intelligence が単一 AI から複数 AI 共存の構造に変わったのは、間違いなく歴史的な転換点なの。」

![世界地図に Siri AI 提供範囲の色分け（緑：全機能 / 黄：一部 / 赤：非提供）](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/075.png)

🦜 きなこ「ただし——この Multi-AI iPhone を全員が使えるわけじゃない。EU と中国では Siri AI が大幅に制限される。なぜか？」

## EU・中国の不在 — 規制とプラットフォームの綱引きが鮮明に

![世界地図・色分け表示（緑: 全機能提供 / 黄: 一部提供 / 赤: 非提供）](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/076.png)

🐹 もっちー「ちょっと待って……さっき「EU と中国では Siri AI が大幅制限される」って言ってたけど、どういうこと？」

🦜 きなこ「Apple Newsroom 公式に明記されてるの。EU では iOS 27 と iPadOS 27 は当初提供しない。中国本土は全面非提供。」

🐹 もっちー「えっ、iPhone と iPad だけ使えないの？ macOS とか watchOS は使えるんやろ？ なんか中途半端やな……」

![EU 地域: macOS/watchOS/visionOS に緑チェック、iOS/iPadOS に赤バツ](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/079.png)

🦜 きなこ「そうなんだよ。EU でも macOS 27・watchOS 27・visionOS 27 なら対応言語を設定すれば Siri AI を使える。iOS と iPadOS だけが規制でひっかかってる。」

🐹 もっちー「なんで EU と中国だけ使えへんの！？ ワイ心配やけど、日本はちゃんと使えるんやんな？」

🦜 きなこ「日本は大丈夫だよ。iOS 27 でふつうに Siri AI を使える。EU と中国は理由が全然違うから、順番に話すね。」

![DMA ロゴ + 「ユーザーデバイスへのほぼ無制限アクセス + 自律アクション能力」テキスト](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/082.png)

🦜 きなこ「まず EU。原因は DMA、デジタル市場法という EU の法律なんだよ。この法律は AI に「ユーザーのデバイスにほぼ無制限にアクセスできること」と「自律的なアクション能力」を持たせるよう求めてる。」

🐹 もっちー「「ほぼ無制限にアクセス」って、具体的にどういうことなの？」

🦜 きなこ「メッセージの読み書き、購入処理、ファイルへのアクセス——全部 AI に開放しなさいって法律が求めてるってこと。」

🐹 もっちー「それって怖くない？ メッセージも買い物もファイルも全部 AI に見えちゃうってこと？」

![「Apple 提案: Trusted System Agent（18ヶ月ロードマップ）→ 欧州委員会: 全て拒否」タイムライン](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/086.png)

🦜 きなこ「Apple は「危険すぎる」と判断したの。代わりに Trusted System Agent を挟む 18 ヶ月ロードマップを提案した。」

🐹 もっちー「欧州委員会はその代替案を受け入れてくれたの？」

![Federighi 発言引用「currently have no timeline」](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/088.png)

🦜 きなこ「全部拒否されたの。Federighi は「欧州委員会が建設的な関与を拒んだため、EU 提供時期は未定」との声明を出したと MacRumors が報じてる。」

🐹 もっちー「じゃあ中国はどうなの？ 理由が違うって言ってたけど。」

![中国: 「生成 AI 規制 / AI モデル認証プロセス・対応中」テキスト](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/090.png)

🦜 きなこ「中国は生成 AI に独自の認証制度があって、当局の審査を通す必要があるんだよ。Apple はその対応中で全面非提供。」

🐹 もっちー「EU は「AI をもっと開放しろ」、中国は「AI をちゃんと審査しろ」ってことか。方向が真逆なのに、どっちも使えないって面白いね。」

![EU: 「ユーザー保護 vs プラットフォームの安全運用」 ／ 中国: 「データ主権 vs 海外 AI モデル」対比図](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/092.png)

🦜 きなこ「鋭い。EU は「保護のために開放せよ」、中国は「主権のために管理せよ」——両者は方向逆でも最先端 AI を止めてる。」

🦜 きなこ「世界中のプラットフォームが最先端 AI を展開するとき必ずぶつかる綱引き——その最前線がここに可視化された。」

## まとめ

![「WWDC 2026 — 5つの要点」タイトルカード](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/094.png)

🦜 きなこ「じゃあ最後に、今日の話を5つにまとめるね。WWDC 2026 は Apple が AI 戦略を根本から転換した歴史的瞬間だったの。」

![要点1: 「Apple AI 自前主義の撤回」アイコン](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/095.png)

🦜 きなこ「1つ目: Apple の AI 自前主義が事実上撤回されたこと。Siri AI の本体は外部の Google Gemini ベース。これは Apple の戦略転換そのもの。」

![要点2: 「3層ルーティング設計」3層図](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/096.png)

🦜 きなこ「2つ目: 3層ルーティング設計でデバイス・Private Cloud Compute・Google Cloud を使い分け、性能とプライバシーを両立。」

![要点3: 「Multi-AI Extensions」4ロゴ並列](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/097.png)

🦜 きなこ「3つ目: Multi-AI Extensions で Claude・ChatGPT・Gemini・Grok を選べる時代に。iPhone は AI 選択のプラットフォームへ。」

![要点4: 「EU・中国は制限、日本は OK」世界地図](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/098.png)

🦜 きなこ「4つ目: EU と中国では大幅制限。EU は DMA、中国は生成 AI 認証規制——最先端 AI とユーザー保護の綱引きが鮮明に。日本は問題なく使えるよ。」

![要点5: 「Tim Cook 最後の WWDC キーノート」イメージ](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/099.png)

🦜 きなこ「5つ目: Tim Cook 最後の WWDC キーノートだったこと。経営者交代を予告する節目でもあって、この発表は Apple の新章の幕開けでもあるんだよ。」

![もっちーが飼い主のタブレットを覗き込むカット](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/099b.png)

🐹 もっちー「なあ、飼い主のタブレットにも Siri AI 入るんやろ？ 飼い主ぜったい興奮するで、これ。」

🐹 もっちー「うーん、正直 Apple が自前にこだわらなくなったの、ちょっと寂しいけど、ユーザーが AI を選べるってのはええことやな。」

🦜 きなこ「「Apple は AI で遅れている」って長く言われてきたけど、本当は「AI を抱え込まないという別の戦略を選んだ」だけかもしれないんだよ。」

🦜 きなこ「OS という土台だけ握って、AI 本体は外部から供給させる——これは「AI 開発で遅れた」じゃなくて、プラットフォーマーとしての成熟な選択なのかもしれない。」

![コメント誘導カード「あなたなら Siri に何を選ぶ？ Claude / ChatGPT / Gemini / Grok」](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/103.png)

🐹 もっちー「ワイは Claude 派！ ファイル整理とか予約とかぜんぶやってほしいねん！ みんなはどの AI を Siri に選びたい？」

![チャンネル登録ボタン + ベルアイコンのアニメーション](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/V207/105.png)

🦜 きなこ「Apple ですら「一つの AI で全部」を諦めたこと、これは Multi-AI 時代の幕開けで、本当に歴史的な節目だよ。今日の話が役に立ったら、チャンネル登録と高評価をぜひお願いね。」

---

**きなこもっちーのテック深掘り** では、AI/LLM を中心としたテック全般をハムスター（🐹 もっちー）とセキセイインコ（🦜 きなこ）の掛け合いで楽しく解説しています。

▶️ **動画で観る** → [AppleがGoogleに屈した？WWDC 2026 Siri AIがGemini 1.2Tに進化した本当の理由](https://www.youtube.com/watch?v=vBdyJp4gwak)

👍 **この記事が役に立ったら LGTM・ストックしてもらえると励みになります！**

📺 **チャンネル登録はこちら** → [きなこもっちーのテック深掘り](https://www.youtube.com/@kinamocchi_tech?sub_confirmation=1)

🔗 **他の解説動画も見る** → [きなこもっちーのテック深掘り の動画一覧](https://www.youtube.com/@kinamocchi_tech/videos)
