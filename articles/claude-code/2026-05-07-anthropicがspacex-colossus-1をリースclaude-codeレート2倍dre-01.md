---
id: "2026-05-07-anthropicがspacex-colossus-1をリースclaude-codeレート2倍dre-01"
title: "AnthropicがSpaceX Colossus 1をリース——Claude Codeレート2倍・Dreaming・CI自動修正が同時解禁"
url: "https://note.com/ai_masaki/n/na2a930e713f3"
source: "note"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "OpenAI", "Python"]
date_published: "2026-05-07"
date_collected: "2026-05-07"
summary_by: "auto-rss"
query: ""
---

こんにちは、まさきです。

5月6日、Anthropicがサンフランシスコで開いた「Code with Claude」のキーノートで、インフラ・エージェント運用・開発体験の三つを一気にアップデートする発表がありました。

メンフィスのSpaceX Colossus 1データセンターを全面リースし、その容量を原資にClaude Codeのレート上限を倍増、Opus APIのレート上限を桁違いに引き上げる。あわせてClaude Managed Agentsには5本の新機能が乗り、エージェントが夜のうちにメモリを再構成する「Dreaming」までリサーチプレビューに入りました。

今日はこの一連を、Pro/MaxユーザーやAPIを叩く開発者の体感が何分後に変わるのか、という地点から順番にほどいていきます。

## ■ 目次

1. SpaceX Colossus 1全面リース——Anthropicが手にした22万GPUとレート上限倍増
2. 5機能同時投入、Claude Managed Agentsが「宣言型API」へ舵を切る
3. Claudeは夜に夢を見るのか——Dreamingが起こすエージェント記憶の自己改善
4. PRが朝には直っている——Claude Code 5本立てが描く「無人開発」の現実味
5. OpenAI・Microsoft・Salesforceの包囲網にAnthropicはどう返したか
6. まとめ

---

## ■ SpaceX Colossus 1全面リース——Anthropicが手にした22万GPUとレート上限倍増

![](https://assets.st-note.com/img/1778099395-4hBbOWfZAxgaM5FLcoYmj1GI.png?width=1200)

最初に押さえておきたいのは、今回のレート上限引き上げが単発の値引きではなく、メンフィスのColossus 1データセンターを丸ごと借りるという裏付けの上に立っている点です。

**旧xAI、現SpaceX所有のColossus 1には300MW超の電力枠と22万基以上のNVIDIA GPU（H100、H200、次世代GB200）が並んでいて、Anthropicはこの容量を全面リース。1か月以内にオンライン化される予定です。**

これを原資に、Claude Code Pro/Max/Team/Enterpriseの5時間あたりレート上限が2倍に。

Pro/Maxアカウントで悪名高かったピーク時間帯の追加制限は撤廃されました。

Opus系APIについても、Tier 1の入力トークン/分が1500%、出力トークン/分が900%という大幅な引き上げ。値上げはなし。

3月以降、Pro/Maxユーザーから「枠の消費が早すぎる」「夕方になると使えなくなる」という不満が積み重なっていました。

あなたが日中に書きかけのコードをClaude Codeに任せて離席し、戻ってきたら止まっていた経験があるなら、その状態は今日から地続きで変わるはずです。

ライバル同士のxAIとAnthropicがインフラで手を組んだという事実は、それだけで業界の力学を一段ひっくり返す出来事。Muskが学習用負荷をすでにColossus 2に移していたから貸し出せたという背景もあり、AI業界が「モデル開発競争」から「電力・GPU争奪戦」に移行したことを象徴する取引。

![](https://assets.st-note.com/img/1778099433-L27z8Ewq9IfthkRpxaXu0Dv5.png?width=1200)

出典: [Anthropic公式（Higher limits, powered by SpaceX）](https://www.anthropic.com/news/higher-limits-spacex)

## ■ 5機能同時投入、Claude Managed Agentsが「宣言型API」へ舵を切る

![](https://assets.st-note.com/img/1778099400-ZAHkGwSdmWa4Bi2fjL5nNEcp.png?width=1200)

増えた計算資源は、当然ながら何かを動かすために確保されます。

その「動かす側」を一気に強化したのが、Claude Managed Agentsプラットフォームへの5機能同時投入でした。

中身を順に並べるとこうなります。

親エージェントが複数のサブエージェントを統括しながら独立コンテキストで並列実行する設計が、Multi-Agent Orchestrationです。

「成功条件」だけ宣言すればClaudeが自律反復してゴールを目指すのがOutcomes。

Webhooksを介してセッションとVaultのライフサイクルイベントを受け取れるようになり、mcp\_oauthクレデンシャルのVault自動更新、セッションやイベントへの絞り込みフィルタ追加も実装されています。

すべてパブリックベータでの提供です。

**ここで一番大きな転換は、命令型から宣言型へのAPIの移動だと僕は見ています。**

「こう動け」と一手ずつ指示するのではなく「こうなっていればいい」と渡せる形は、書く側の負担を下げる代わりに、エージェントの判断品質をプラットフォーム側が背負う構図に近づきます。

実装事例も並んでいて、Notion・Rakuten・Asana・Sentry・Vibecodeが「1週間で本番投入」したケースを公開、Harveyの法務AIではDreamingと組み合わせてタスク完了率が約6倍に伸びたとされています。

1週間という時間軸が現実味を持って語られはじめたのは、これまでのエージェント基盤と比べて明確な進歩。

一方でDes Raj C.の「難しいのはエージェント連結ではなく、エージェントが半分正しいときに何をするか」という指摘は、Outcomesの宣言型シフトに対する真っ当な留保。

ロールバックと監査の整備が追いつくほどに、宣言型は本物になっていくのだと思います。

出典: [Anthropic公式ブログ（New in Claude Managed Agents）](https://claude.com/blog/new-in-claude-managed-agents)

## ■ Claudeは夜に夢を見るのか——Dreamingが起こすエージェント記憶の自己改善

![](https://assets.st-note.com/img/1778099406-ILD7Kgxb3yeFSk6AVCzh9ZJf.png?width=1200)

Managed Agentsの中でも、見出しに使うほど象徴的だったのがDreamingです。リサーチプレビューでリクエスト制ですが、エージェントの「記憶の更新の仕方」を根本から変える試みでした。

仕組みはシンプルです。夜のうちに、エージェントは僕たちとの過去のやりとりや記憶の蓄積を自分で見直し、パターンを掴んでメモリを再編成する。

重なった情報はひとまとめになり、古い記述や矛盾した内容は新しい情報で上書きされ、これまで気づけなかった傾向が拾われる。

繰り返しているミス、だんだん定まってきた作業のやり方、チームに共通する好み——それらが翌朝のエージェントに引き継がれるイメージです。

自動で更新するか、変更を確認してから適用するかはユーザーが選べます。

**ここで率直に立ち止まりたいのは、エージェントが自分の記憶を書き換える権限を持つことの意味です。**

Harveyのケースでタスク完了率が6倍に伸びたという数字は鮮烈ですが、自己改変するエージェントの監査ログをどう取るのか？ Anthropicは承認制オプションを用意していますが、本番運用で毎晩の差分を人がさばけるのかという別の負担も生まれます。

人間の睡眠中の記憶整理になぞらえた発想は、絵としては美しい。

Simon Willisonは「Ralphループのよう」と技術的な系譜に位置付け、研究系の開発者からはcontinual learningの実装例として歓迎の声が並びました。

一方で「Research Previewでまだ触れない、ハイプが先行している」という冷ややかな留保も多数。熱狂と懐疑が同時に成立する、ここしばらくのAIプロダクトの中でも珍しい温度感の発表。

夜にAIが夢を見る、という比喩を機能名に据えるところまで踏み込めるか。

出典: [Anthropic公式ブログ（New in Claude Managed Agents）](https://claude.com/blog/new-in-claude-managed-agents)

## ■ PRが朝には直っている——Claude Code 5本立てが描く「無人開発」の現実味

![](https://assets.st-note.com/img/1778099411-9LbwnvagXz6Yj4NpEZrIHM3k.png?width=1200)

Managed Agentsで土台を整えたあと、Anthropicが開発体験の方に向かって投げてきたのがClaude Codeの5本立てでした。

Anthropic社内の全チームが実際に使ってきたコードレビューの仕組みを、外部に開放したのがCode Reviewです。

/ultrareviewとコマンドを打つと、クラウド上で複数のAIレビュアーがPRを並列で読み込み始めます。

「高次プロンプト」として位置付けられた非同期自動化がRoutinesで、一連のタスクを定義しておくとマージ可能なPRをClaudeが生成する仕組みです。

実行回数はPro 5/日、Max 15/日、Team・Enterprise 25/日。

**CIの失敗やレビューコメントを検知してから、自動修正・プッシュ・説明をClaudeがクラウド上でこなすのがCI Auto-Fixで、手元のマシンを閉じていてもPRが「常にgreen」に保たれます。**

Remote Agentsはスマホからラップトップを操作する遠隔エージェント、Security Reviewsは自動セキュリティスキャンです。

朝、コーヒーを淹れている間にPRが直っている、という体験を想像してみてください。

あなたが昨日書いて寝落ちしたコードに対してCIが赤くなっていたら、起きるまでにClaudeが原因を特定して修正コミットを当てて、説明文付きで「あとはマージするだけ」の状態に整えてくれる。

それがCI Auto-Fixの設計図。

ただ、Routinesにはすでに既知の落とし穴があります。

4月に先行リリースされた段階で、ルーチンが互いを呼び出して止まらない「context-eating loop」（コンテキストを食い潰す無限ループ）がエラーを出さずにトークンを焼く事例が報告されていました。

今回の拡張で実行回数の枠が明示されたのも、その学習を踏まえての制度設計に見えます。

Karpathyが言うところの「80% agent coding」がプラットフォーム側から具体的な道具立てとして提示されたという点で、Claude Codeはこの数か月で最も飛躍した自動開発スイート。

![](https://assets.st-note.com/img/1778099427-yFAvXZ41duSsgxWKOlU30nDj.png?width=1200)

出典: [Claude Code公式ドキュメント（Overview）](https://code.claude.com/docs/en/overview) / [Claude Code公式ドキュメント（Routines）](https://code.claude.com/docs/en/routines)

## ■ OpenAI・Microsoft・Salesforceの包囲網にAnthropicはどう返したか

![](https://assets.st-note.com/img/1778099417-JNyT1xlcRI7a4MGebmDhCwk0.png?width=1200)

ここまでの3トラックを「Anthropic単独の強気施策」と読むと、半分しか見えません。同じ週に並んだ競合の動きと重ねると、別の絵が浮かんできます。

5月6日にはOpenAIがAgents SDKのTypeScript版をGAリリース。サンドボックス型エージェントとオープンソースのharnessを同梱し、Pythonに偏っていたエージェントSDK市場のmindshareをNode/フロント側にも広げにきました。

Microsoftは5月1日にAgent 365をGAし、Salesforceは4月29日にAgentforce Operationsを一般提供開始。IBMもwatsonx Orchestrateを5月5日に発表しています。

エンタープライズ向けエージェント運用のフルスタック化は、ほぼ同時多発で進んでいるわけです。

**その中でAnthropicが選んだ差別化が、命令型APIに対する宣言型（Outcomes）でした。**

OpenAIがSDKのカバレッジで攻めるのに対し、Anthropicは「成功条件を渡せばそこまで行く」という宣言型の設計思想で別のレイヤーを取りに行く。MCPプロトコルを下敷きにエージェント市場の支配権を競う構図が、ここではっきり見えてきます。

ただし、宣言型の優位がすぐに勝負を決めるとは限りません。

VentureBeatは「企業向けワンストップショップ」と評価しつつ「ベンダーロックインのリスク」を指摘しています。SNS上では運用者の声として、Claude Managed Agentsの$0.08/runtime hour換算で月$58〜の固定費にトークン課金が積み上がるというコスト感への留保も並びました。

フルスタックで囲い込む各社の戦略は、エージェントを一度本番に乗せた企業ほど抜けにくくなる構造を生む。それが顧客にとって正しい選択肢なのか？

ここからしばらくは、機能の差ではなくロックインの厚みが評価軸になっていく時期に入りそうです。

## ■ モデル開発から電力争奪へ——Anthropicが2026年5月に置いた布石

![](https://assets.st-note.com/img/1778099422-LwAeFJIMfdS8H4iT57yqrtuE.png?width=1200)

最後に視点を引いておくと、Code with Claudeの一連で起きていたのは「モデル開発の話」というよりは「電力とGPUを誰が押さえるか」の話に近い、ということがわかってきます。

Colossus 1全面リースは、Google・AWSに続く第3のクラウド軸としてSpaceXを取り込み、特定クラウドへの依存を分散させる動き。

MuskにとってはライバルAnthropicへの売却益でColossus 2の建設費を回収する財務戦略で、6月のSpaceX IPO直前というタイミングも噛み合っています。

Bloombergが「MuskはすでにxAIの学習をColossus 2に移行済み、Colossus 1を遊休化させずに済んだ」と書いた通り、両社の損得が交差する点で握られた取引。

**機能の話に戻すと、Managed AgentsもDreamingもClaude Codeも、それぞれを成立させているのは「動かす計算資源があること」。**

22万GPUという数字は、エージェントを夜中に走らせ続け、PRを朝までに直し続け、複数のサブエージェントを並列で動かすという用途の「燃料」として読むのが筋がよさそうです。

あなたが明日Claude Codeを叩いたとき、5時間枠の余裕やピーク時間帯のストレス減を感じる場面があれば、それはメンフィスのデータセンターから流れてくる電力の話と地続きで起きている。

発表のスケールが大きすぎて遠い話に感じる種類のニュースですが、現場の体感までの距離は意外と短いのかもしれません。

「電力を押さえた者がエージェントの覇権を握る」という見立てが、この先どこまで強い説明力を持つか。

最後まで読んでいただき、ありがとうございます。

気になったニュースや「ここもう少し詳しく」など、何でも気軽にコメントください。フォロー・スキでの応援も、毎朝更新する励みになります。

それでは、今日も良きAIライフを！

---

**【Xツイート 親】**

5月6日、AnthropicがメンフィスにあるSpaceX所有のColossus 1データセンターを全面リースした。300MW超の電力枠と22万基以上のNVIDIA GPUを原資に、Opus APIのTier 1は入力トークン/分が1500%、出力トークン/分が900%引き上げられ、値上げはない。ライバル同士のxAIとAnthropicがインフラで握手したという事実は、AI業界が「モデル開発競争」から「電力争奪戦」に移行したことをそのまま示している。

MuskがColossus 2にすでに学習負荷を移し終えていたから成立した取引という背景を知ると、このディールの読み方が変わる。

**【Xツイート リプ】**

詳細はnoteで。
