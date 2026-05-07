---
id: "2026-05-06-codens-vs-devin-vs-cursor-composer-vs-sweep-を点解決と-01"
title: "Codens vs Devin vs Cursor Composer vs Sweep を、点解決と workflow harness の軸"
url: "https://zenn.dev/zoetaka38/articles/b5d2a1b0b115f9"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "AI-agent", "zenn"]
date_published: "2026-05-06"
date_collected: "2026-05-07"
summary_by: "auto-rss"
query: ""
---

## はじめに

「AI coding agent、結局どれを入れればいいの？」という問いを最近よく投げられる。Devin、Cursor Composer、Sweep、それと自分が作っている Codens。比較記事は世にいくつもあるが、機能チェックリストの x / o を並べただけのものが多くて、評価フェーズの実務にはあまり噛み合わないと感じていた。とくに、各製品が「そもそも何を解こうとしているのか」が揃っていないまま機能比較されると、用途と合わない側が不当に低く見える。

評価フェーズで欲しいのは「どれが最強か」ではなく、「自分のチームがいま解きたい問題は何で、その問題に対してこの 4 つはそれぞれどの粒度で答えているのか」だと思う。粒度がずれている product を比べると、当然に片方が不当に低く見える。評価する側に必要なのは、性能の絶対値より、設計思想の解像度。

先に結論を一行で言うと、Devin / Cursor / Sweep は**点解決**で、Codens は**workflow harness**だと自分は捉えている。同じ x 軸に置いて比較表を書ける製品もあれば、別カテゴリとして並べたほうがフェアな製品もある。以下、それぞれが何を解いているかを揃えてから、ユースケース別にどれを選ぶかを書く。biased な書き手ではあるので、Codens 以外の 3 つについては可能な限り公開情報の範囲で書いた、機能の数値や最新スペックは各社の公式ページが正解で、この記事は設計思想の比較に振っている。

## 各プロダクトが解こうとしている問題

### Devin: タスクを丸ごと AI に任せたい(autonomous task completion)

Cognition AI の Devin は「自律的な AI software engineer」を標榜していて、ブラウザ上から task を投げて、自分のサンドボックス環境で計画を立て、コードを書き、テストを回し、PR を出すところまでを単一の agent が引き受ける形をとる。エンジニアは途中で覗くこともできるが、基本は「数十分から数時間、放置して結果だけ見る」ワークフローを想定している。

強みはやはり end-to-end の自動化で、IDE を開かず、ローカルの dev 環境を整えず、issue ベースのタスクをそのまま投げ込める。Slack 経由などで起票して、結果だけ受け取るスタイルが回せる。立ち上がりまでの摩擦が極端に小さい設計で、「とりあえず投げる」がしやすい。サンドボックスの中で browser を立ち上げて Web を見に行く動きまで、Devin の側で揃えてあるのは強い。

トレードオフとして、自分が触った範囲では「途中経過が opaque になりがち」「金額が嵩みやすい」「単一 agent なので role specialization の上限がプロンプト工夫の上限と一致する」という三点を感じた。これは設計思想の選択なので Devin の欠陥という話ではない、autonomous を最大化した結果として生まれる性質と捉えるのが正確だと思う。たとえば「途中で人間が割り込みたい」「プロセスの一段だけ別の専用 agent に渡したい」という要望は、autonomous を売りにしている product にとってはむしろ要件と矛盾する。

### Cursor Composer: IDE の中で AI が手元の編集を加速(inner-loop dev)

Cursor は VS Code のフォークをベースにした「AI-first IDE」で、Composer は IDE の中から複数ファイルにまたがる編集を依頼できる agent 機能。エンジニアがエディタを開いている前提で、目の前のコードに対して「この変更を書いて」「このリファクタを 5 ファイル横断でやって」と指示する。VS Code の拡張資産がそのまま使えるので、移行コストもほぼゼロに近い。

強みは inner loop の速さで、コード補完、リファクタ、ファイル横断の小さな修正、そして `@file` で context を渡す UX のキビキビ感は他の追随を許さないと感じる。エンジニア個人の「手元のコードを書く速度」を底上げするフェーズでは、現時点で最有力に近い選択肢だと思う。最近は agent 寄りのモード(自動でファイルを調べに行って、複数ステップの編集を一気に走らせる動作)も IDE 内に統合されてきていて、「IDE の中で半 autonomous な動きまでやる」という方向に進化している。

トレードオフは、エンジニアが editor に座っていることが前提な点。非エンジニアが触れる入口はないし、ticket からの async ワークフローも本質的には Cursor の領域ではない。チーム共有の credit pool のような org 単位の budget 設計もないので、per-seat の subscription が中心になる。これも Cursor の欠陥ではなく、「個人のエディタ体験を最高にする」という product のコア価値とまっすぐ一貫した選択だと思う。

### Sweep: GitHub issue から自動で PR が立つ(async issue-to-PR)

Sweep は GitHub issue にラベルを付けると agent が起動して、cloud 側で実装し、PR を返してくる。GitHub-native のトリガーで動くのが特徴で、エンジニアが editor を開いていなくても、issue が起票された段階で workflow が始まる。「人間が issue を書く担当、AI が実装担当」という分業モデルがハマっている組織だと、運用に自然に組み込みやすい。

強みは GitHub への密着で、issue → PR の async loop に綺麗に乗る。インフラもエンジニアが用意する範囲が小さい。GitHub Actions と密に連携する形なので、既存の review プロセスに混ぜ込みやすいのも実務としては助かる。

トレードオフは、エントリーが GitHub issue に集約されている点。Notion やビジネス側のドキュメントから直接トリガーする workflow とは噛み合わない、PM が GitHub に直接 issue を書ける文化がある組織でないと、この入口は機能しにくい。また機能スコープは「issue を PR に変える」が中心で、QA agent やエンジニアリング活動の集計のような他の SDLC 工程には踏み込んでいない。これも product の覚悟の問題で、狭く深い設計を選んでいる結果として横展開のスコープが narrower になっている、という話。

### Codens: 非エンジニアの要望から、テスト済 PR まで全工程を harness で繋ぐ

Codens は 5 つの specialized agent(PRD writer の Green、orchestrator の Purple、E2E テスト生成の Blue、エラー自動修正の Red、エンジニアリング活動 ledger の Yellow)を、組織共通の credit pool 上で動かす harness として設計している。

エントリーは Notion ticket。PM が要望を Notion に書くと Green が PRD を構造化し、Purple が PRD を task graph に分解して develop step を回し、Blue が実装 diff を context として E2E テストを生成し、本番で Sentry が出した error を Red が拾って修正 PR を出す。Yellow はその全部の活動を集計して、どの工程に時間と credit が溶けたのかを後から見られる ledger にしている。

強みは、SDLC の複数ロールが一つの harness で繋がっていること、非エンジニアの入口が用意されていること、そして credit が組織横断で pool されていることの三点。一つ目について補足すると、Purple→Blue 間で実装 diff を context として渡す handoff のように、ロール間の境界面を product 側で握っているのが harness の本懐で、ここは単一 agent では設計できない。

トレードオフは正直に書くと、(1) opinionated な workflow を持っているので「うちはこの 1 工程だけ AI 化したい」というチームには harness 全体は明らかに重い、(2) 顧客リファレンスは Devin / Cursor と比べて少ない、(3) JP-first のローカライズが手厚い分、グローバル integrations は競合より薄い、の三点。これらは product の年齢と市場フォーカスから来ている素直な弱みで、隠す気はない。

## 比較表(at-a-glance)

軸を「実務の評価で問われやすいもの」に絞った。x / o ではなく、性質を文字で書く形式にしている。チェックリストにすると、設計思想の違いが「機能不足」に見えてしまうので。

| 軸 | Devin | Cursor Composer | Sweep | Codens |
| --- | --- | --- | --- | --- |
| 主なエントリー | Web UI / Slack / API | IDE 内 | GitHub issue | Notion ticket / GitHub / 内部 API |
| Agent 構成 | 単一 autonomous agent | IDE 内 agent | 単一 issue→PR agent | 5 つの specialized agent |
| 想定実行環境 | クラウドの sandbox | ローカル IDE | クラウド | クラウドの remote worker |
| 非エンジニアが触れるか | 可(Web UI で起票) | 不可(IDE 前提) | 限定的(GitHub 操作が必要) | 可(Notion から起票) |
| 主要対象工程 | 任意の dev タスク | 編集・リファクタ | issue → PR | PRD → 実装 → テスト → 修正 PR → 集計 |
| 課金モデル | subscription + usage | per-seat | per-PR / per-issue 系 | tier subscription + 共有 credit pool |
| Org 横断の budget 共有 | 弱め | per-seat 単位 | usage 単位 | tier ごとに pool 共有 |
| 進捗の可視化 | 実行ログ閲覧 | IDE 上で即時 | PR コメント | Notion / GitHub / 内部ダッシュボード |
| カスタム workflow の柔軟さ | 高(prompt 設計) | 中(IDE 中心) | 中(issue 駆動) | 中〜高(harness の wiring 次第) |
| 強み | 任意タスクを丸投げできる | inner loop が圧倒的に速い | GitHub-native の async | SDLC を一つの harness で繋ぐ |
| 弱み | 中身が opaque、価格 | 編集者必須、async 弱め | GitHub 中心、scope 狭め | opinionated、reference 少なめ |

弱みの欄は意図的にどれも書いた。「自分の product だけ弱みなしで、競合は全部 x」という比較表は、評価する側からすれば一番信用できないやつなので。あと、エントリー方式と agent 構成の二軸が、4 製品で本質的に一番離れているところだとも思う。ここが揃わないと、他の機能比較は全部「何を解いているかが違う製品同士」の比較になる。

## ユースケース別: どれを選ぶか

### 個人エンジニアが手元のコードを高速に書きたい → Cursor

editor に座って書くのが好きな個人エンジニア、あるいは「AI に手元を加速してほしいが、最終的な意思決定は全部自分でやりたい」というロールの人にとって、Cursor の inner loop の速さは現時点でほぼ独走に近い。Composer の multi-file edit、ファイル context の渡し方、補完の応答速度、そして VS Code 拡張資産の継承。仕事の中心が「自分でコードを書く」フェーズなら、まずこれ。

### タスクを丸投げして数時間放置でいい → Devin

「ticket を投げて、結果を待って、必要なら微調整する」という働き方ができるロールには、Devin の autonomous な作りはハマる。とくに、エンジニアが他のことをしている間に重めの実装を並列で進めたい、というシナリオは Devin の得意分野。コストは嵩むが、エンジニア工数の機会費用と比べたらペイする使い方は十分にある。

### issue 起票から PR まで一気通貫の async が欲しい → Sweep

GitHub に閉じた workflow を持っていて、「issue を立てる人とコードを書く人を分けたい、書く部分は AI で」という要件には Sweep が綺麗に当てはまる。Notion などビジネス側からのトリガーが要らない、GitHub-only で完結している組織なら整合性は良い。

### 非エンジニアの要望から、テスト・修正まで複数ロールで処理 → Codens

PM が Notion に書いた要望から、PRD 構造化、実装、テスト生成、本番エラーの修正 PR、活動 ledger までを「複数ロールが繋がった一つの workflow」として欲しい組織には、Codens は素直にハマるはず。とくに、エンジニアが少人数で SDLC のあちこちに引っ張られている、という典型的な小規模〜中規模の開発組織だと、handoff を harness 側で握れる効きが大きい。

逆に「うちはコード生成の 1 工程だけ自動化したい、他は要らない」というチームには、harness 全体は明らかに過剰になる。そういうチームには素直に上の 3 つのどれかをお勧めしている。営業の場面でも、harness が要らないチームには Codens を売らないほうが long term の関係性として健全だと思っているので、ここはわりと真面目に最初の打ち合わせで聞くようにしている。

## なぜ単一 agent ではなく複数 agent harness を選んだか

Codens を作る前、自分も「巨大な単一 agent に全部やらせる」案は当然検討していて、最初の prototype はそれだった。やめた理由は二つある。

一つは specialization の上限。単一 agent に PRD 構造化と実装と E2E テスト生成と error 修正の全部を持たせようとすると、prompt と tool 一覧が膨らみ続けて、ある臨界点を超えると挙動が壊れる。一つの role が増えるたびに他の role の精度が下がる、というやつ。これは Anthropic の SDK 周りで agent を書いている人なら共有できる感覚だと思う。具体的には、tool の数が 10 を超えたあたりから、どの tool を選ぶかの判断が雑になってくる傾向があって、PRD 用の tool と error 修正用の tool が同じ namespace にあると、agent が「今は何のロールをやっているか」を忘れる事故が起こりやすい。

もう一つは budget の摩擦。ロールごとに別 SaaS を契約すると、PRD は X、実装は Y、テストは Z、と budget が分かれて、どこが詰まっているか可視化しづらいし、安く済むはずの工程に高い tier の料金を払うことになりがち。組織共通の credit pool を一段噛ませたほうが、ロール間で credit を融通できて、結果として総額が下がる。これは zenn-008 や別記事で書いた話なのでここでは詳述しない。

特殊化された 5 agent + 共通 credit pool の構成は、汎用の単一 agent よりも「狭く深い役割を、横の handoff と budget だけ揃えて並べる」発想に近い。Purple→Blue 間で実装 diff を context として渡す設計(zenn-014 で書いた)も、handoff の解像度を上げる方向の延長線上にある。Purple は何を変えたか知っていて、Blue は何をテストすべきかを知っているが、両者の context をパイプで繋ぐ責任は harness 側が持つ、という分担。

ここは正直、評価フェーズで誤解されやすいポイントでもある。「単一 agent で全部やれるなら、わざわざ複数 agent を入れたほうが complexity が上がるだけでは」という指摘はもっともで、自分も最初はそう思っていた。実装してみると逆で、specialization を切り分けたほうが、各 agent の prompt と tool 一覧がシンプルに保てるので、結果として全体の挙動が安定する。複雑性は agent 間の境界面に集中させて、agent 自体は薄く保つ、というのが harness の設計思想になっている。

## 価格モデルの違い

ここは生っぽい数字を書くと変動した時に陳腐化するので、課金モデルの設計だけ書く。最新の正確な値は各社の公式ページを見てほしい。

| 製品 | 課金の主軸 | 組織横断 budget |
| --- | --- | --- |
| Devin | subscription + usage(高め) | usage 単位、組織での pool 設計は導入時の交渉次第 |
| Cursor | per-seat | seat 単位、共有 pool は弱め |
| Sweep | per-PR / per-issue 系 | usage 単位 |
| Codens | tier subscription + 共有 credit pool(Hobby ¥3,000 〜) | tier 内の pool を組織で共有 |

Codens の価格設計は、credit を「engineer の work hour」に近い概念として扱いたいという意図がある。誰が使ったかではなく、組織として何ロールぶん回したか、で課金されるのが筋がいいと考えていて、tier subscription + pool に落としている。詳細は note の price 関連記事に書いた。

per-seat も per-usage も、それぞれ正しいケースがある。per-seat は「seat を持つ人が日常的に使う」ツール(IDE、エディタ、エンジニアの inner loop)に綺麗にハマる、Cursor がここを取りにいっているのは整合性が高い。per-usage は「使う頻度がロールや時期で大きく振れる」ワークフロー(Devin の autonomous task、Sweep の issue 起票駆動)にフィットする。Codens の credit pool は、その中間層、「複数ロールが組織で workflow を回す」シナリオの料金モデルとして設計している。どれが正しい、ではなく product のコア価値に料金体系が一致しているか、という見方をすると、4 製品の課金設計はそれぞれ自己整合的になっている。

## どれが「正解」というよりは、何を組織で繋げたいか

ここまで書いてきて、自分の中での評価軸はわりとシンプルに収束した。

* **1 ロールを速くしたいだけ**なら、点解決の Devin / Cursor / Sweep のどれかを、ロールの形に合わせて選べばよい
* **チーム全体の handoff を速くしたい**なら、harness のような上位レイヤーが要る、その時の選択肢の一つが Codens

両者は競合というより層が違う、と言ってしまっても間違いじゃない。実際、Codens を入れている組織でも、エンジニア個人は Cursor を編集環境として使っているケースは普通にある。Codens は workflow harness なので、editor の中で何を使うかには干渉しない。Devin と組み合わせるパターンも理屈の上では成立する、autonomous な単一 task は Devin に投げて、組織の workflow としての handoff は Codens で握る、という構成。

逆に、「Cursor を入れたから Codens は要らない」「Devin があるから Codens は要らない」という質問をたまに受けるが、これは axis が違う。「IDE を入れたから CI/CD は要らない」と言っているのに近い。エンジニア個人の inner loop と、チームの outer loop は別の問題で、別のレイヤーの道具で解くのが筋が良いと自分は思っている。

評価のフレームとしては、まず「自分の組織で詰まっている工程はどこか」を一つ書き出すのが先で、その工程が単一ロール(個人エンジニアの編集速度、ticket からの実装、issue からの PR)で説明できるなら点解決、ロール間の handoff(PRD と実装、実装とテスト、本番エラーと修正)が詰まっているなら harness、と切り分けると製品選びがブレない。

## まとめ

自分は Codens を作っている人間なので biased なのは前提として、それでもこの 3 つの競合は本当によくできていると思っている。Cursor の inner loop UX は研究対象で、Devin の autonomous な振る舞いは「ここまで丸投げできるのか」と何度も唸らされたし、Sweep の GitHub-native の割り切りは設計として綺麗。比較記事を書く時に、競合をあえて低く見せる書き方は long term で自分の信用を削ると思っているので、誇張なしで書いた。

組織の評価フェーズで「点解決と harness のどっちが要るんだっけ」を最初に決めると、その後の選択は驚くほど単純になる。1 ロールを高速化したいだけなら点解決を、SDLC を横で繋ぎたいなら harness を、と切り分ければ、4 製品のどれが自分の組織に向いているかは自然に絞れる。両方が要るなら両方入れればいい、layer が違うので干渉しない。

Codens 自体に興味を持ってもらえた場合は、LP(<https://www.codens.ai/>)から覗いてみてほしい。Hobby tier から触れる構成になっている。
