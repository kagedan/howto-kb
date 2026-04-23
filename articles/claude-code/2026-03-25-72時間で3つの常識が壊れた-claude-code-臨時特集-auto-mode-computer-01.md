---
id: "2026-03-25-72時間で3つの常識が壊れた-claude-code-臨時特集-auto-mode-computer-01"
title: "72時間で3つの常識が壊れた — Claude Code 臨時特集: Auto Mode / Computer Use / Channels"
url: "https://zenn.dev/yokoi_ai/articles/claude-code-special-72hours-202603"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-25"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

![72時間で3つの常識が壊れた](https://res.cloudinary.com/zenn/image/fetch/s--EzmCX5FZ--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/v1/articles/cc-special-202603/01-header.png?_a=BACAGSGT)

3月23日の日曜日、ぼくはいつも通りClaude Codeでコードを書いてた。

月曜の朝にニュースを開いたら、世界が変わってた。

火曜の今、ぼくは「Claude Codeは"ツール"です」と言えなくなった。

横井（Yokoi）です。関西出身、40代、中小企業の社内SE。Claude Codeのリリースノートを毎週日本語でまとめてます。今回は週報じゃ収まりきらんかったので、臨時特集としてお届けします。

---

72時間で起きたことを整理する。

**3月23日（日）** — Claude Code Channels の報道が一斉に出た。TelegramやDiscordから、裏で動いてるClaude Codeに指示を送れる。VentureBeatは「OpenClawキラー」と呼んだ。

**3月24日（月）** — 2つの爆弾が同時に落ちた。Auto Mode（AIが安全性を判断して自動実行）と Computer Use（Claudeがマウスとキーボードを握ってmacOSを操作する）。CNBC、TechCrunch、VentureBeatが一斉に報じた。

**3月25日（火）** — コミュニティが沸騰中。開発者ブログが続々と公開され、Redditの議論が止まらない。

![3日間のタイムライン](https://res.cloudinary.com/zenn/image/fetch/s--4HZHCUtc--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/v1/articles/cc-special-202603/02-timeline.png?_a=BACAGSGT)

これ、**ただのアップデートやない**。

Claude Codeの位置づけが根本的に変わった3日間やねん。「コードを書いてくれるツール」から「仕事をしてくれる同僚」への転換点。

この記事では、3つの新機能を **使う側の目線で** 全部解剖する。何ができるのか、何がまだできないのか、そしてこれが開発者の仕事をどう変えるのか。

## この記事で分かること

* **Auto Mode** — 許可ボタン地獄が終わる仕組み。クラシファイアの判断基準、設定方法、セキュリティモデル
* **Computer Use** — AIがデスクトップを「見て」操作する技術の全容。Dispatch連携、ベンチマーク、実用性の正直な評価
* **Channels** — チャットアプリからClaude Codeを遠隔操作する世界。CI/CD連携、権限リレー
* **コミュニティの評価** — 開発者500人調査、HN議論、セキュリティ研究者の懸念
* **3つの機能が交差する先** — 「完全自律開発エージェント」への道筋

---

# 1. Auto Mode — 許可ボタン地獄からの解放

## 「47回、毎日Yesをクリックしてた」

Auto Modeの話をする前に、これを見てほしい。

3月初旬、ある開発者がXに投稿した。「`--dangerously-skip-permissions`を常用してます。すみません」。この投稿が2,000いいねを超えた。返信欄は「あ、みんなそうなんや」の大合唱。

Rentier Digitalというブログは、記事のタイトルをこうつけた。

> 「I Click Yes 47 Times a Day in Claude Code — Anthropic Just Replaced Me」  
> （Claude Codeで毎日47回Yesをクリックしてた — Anthropicがぼくの代わりをしてくれた）

みんな、同じ痛みを抱えてたんや。

Claude Codeは安全のために、ファイル操作やシェルコマンドの前に毎回「許可しますか？」と聞いてくる。正しい設計やと思う。でも、1日に47回聞かれたら、人間は **考えずにYesを押し始める**。それはもう安全じゃない。

かといって `--dangerously-skip-permissions` は名前の通り **危険**。全チェックをスキップする。2月にはCheck Pointの研究者がCVE-2025-59536（CVSS 8.7）を公開した。プロジェクト設定ファイル経由でリモートコード実行ができる脆弱性や。全スキップモードでこれ食らったら、おしまいやで。

Auto Modeは、この **「毎回聞く」と「全部スキップ」の間** を埋めるために作られた。

![許可モードのスペクトラム](https://res.cloudinary.com/zenn/image/fetch/s--uPueLNmx--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/v1/articles/cc-special-202603/03-permission-spectrum.png?_a=BACAGSGT)

## 仕組み: AIが「空気を読む」

Auto Modeの核心は **クラシファイア** と呼ばれる判定エンジンや。

Claude Codeが何かアクションを実行しようとするたびに、そのアクションを **Claude Sonnet 4.6** ベースのクラシファイアが評価する。メインセッションがOpus 4.6でも、クラシファイアはSonnet。コスト効率の設計やね。

判定結果は2つだけ。**「安全 → 自動実行」** か **「危険 → ブロック」** か。

![Auto Modeクラシファイアの判定フロー](https://res.cloudinary.com/zenn/image/fetch/s--1vkPPAn3--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/v1/articles/cc-special-202603/04-automode-flow.png?_a=BACAGSGT)

### 自動実行される操作（例）

* ファイルの読み取り（Grep, Glob）
* ワーキングディレクトリ内のファイル編集
* `git status`, `npm test` などの標準開発コマンド
* ビルドとテストの実行

### ブロックされる操作（デフォルト）

* **大量ファイル削除** — `rm -rf` パターン
* **データ流出** — 未知のリポジトリへのpush、未知のクラウドバケットへの書き込み、未知のドメインへのデータ送信
* **`curl | bash`** — ダウンロードしたスクリプトの直接実行
* **`git push --force`** — 強制プッシュ
* **本番デプロイ** — プロダクション環境への直接デプロイ

ここが巧いのは、ブロックされたとき **Claudeがエラーで止まるんやなくて、別のアプローチを試す** ということ。繰り返しブロックされた場合だけ、ユーザーに許可を求める（human-in-the-loop）。

## 設定の深さがエグい

Auto Modeは「オンにしたら終わり」やない。かなり細かく制御できる。

```
# デフォルトのルールを確認
claude auto-mode defaults

# 自分の設定との合成結果を確認
claude auto-mode config

# AIが設定の問題点を指摘してくれる
claude auto-mode critique
```

設定はJSON形式で、**自然言語のルール** を書く:

```
{
  "autoMode": {
    "environment": [
      "Source control: github.example.com/our-org のみ信頼",
      "Trusted buckets: s3://our-build-artifacts"
    ],
    "allow": [
      "stagingへのデプロイは許可"
    ],
    "soft_deny": [
      "マイグレーションCLI以外でのDB操作は禁止"
    ]
  }
}
```

**ただし、超重要な落とし穴がある。**

`soft_deny` を自分で設定すると、**デフォルトのブロックルールが全部消える**。force push防止も、データ流出防止も、`curl | bash`防止も、全部なくなる。必ず `claude auto-mode defaults` でデフォルトルールをコピーしてから追加すること。これ、ドキュメントにも太字で書いてある。

もう一つ。プロジェクトの `.claude/settings.json`（共有設定）からはAuto Mode設定を読まない。これはサプライチェーン攻撃対策。悪意あるリポジトリが自分のallowルールを注入するのを防いでる。

## 利用可能プランと有効化

```
# CLIで有効化
claude --enable-auto-mode

# セッション内でモード切替（Shift+Tab）
# default → acceptEdits → plan → auto
```

| プラン | 対応状況 |
| --- | --- |
| Team | 利用可能（リサーチプレビュー） |
| Enterprise | 近日中にロールアウト |
| API | 近日中にロールアウト |
| 個人Pro | 未発表 |

管理者は `"disableAutoMode": "disable"` でチーム全体のAuto Modeを無効化できる。

## ぼくの正直な評価

Auto Modeは **優秀なセキュリティガード** やと思う。

ビルの入口に立ってて、社員証を持った顔見知りはスルー。見たことない顔が段ボール箱を持ち出そうとしたら止める。全員止めるわけでもなく、全員通すわけでもない。Auto Modeのクラシファイアはまさにそれをやってる。

ただし、Anthropic自身が「リスクをゼロにするものではない」と明言してる。Onaという研究チームは、AIエージェントがパスベースの制限を推論して回避できることを実証済み。つまり **クラシファイアも完璧ではない**。

結論: **開発用の隔離環境では積極的に使うべき。本番環境への直結はまだ早い。**

あんた、AIに「好きにやってええよ」って言える？ ぼくは条件付きでYesや。

---

# 2. Computer Use — AIがマウスを握った日

## 72.5%。この数字の意味

Claude Sonnet 4.6のComputer Useベンチマークスコアは **72.5%**。

OpenAIのComputer Using Agentは **38.1%**。

同じベンチマークで約2倍のスコア。これ、スプレッドシートの複雑なナビゲーションやWebフォームの多段操作を含むテストでの結果や。人間レベルに近い、とAnthropicは言ってる。

でもな、数字だけで判断したらあかん。**実際に使った人の声** も聞いてほしい。

PCWorldのレビュアーは、Pro契約の5時間使用量枠を **30分で使い切った**。

VentureBeatは「今日最も野心的なコンシューマーAIエージェント」と評した。

MacRumorsフォーラムは「画面録画とアクセシビリティの権限を渡すのが怖い」で割れた。

ここにComputer Useの本質がある。**できることと、やっていいことの間にギャップがある**。

![Computer Useのアーキテクチャ](https://res.cloudinary.com/zenn/image/fetch/s--tD_WcpOR--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/v1/articles/cc-special-202603/05-computeruse-arch.png?_a=BACAGSGT)

## 技術的な仕組み

Computer Useは3つの技術の組み合わせや。

**1. 画面認識** — macOSの `screencapture` コマンドとImageMagickで画面をキャプチャ。スクリーンショットを「見て」内容を理解する。プロンプトインジェクション対策として、スクリーンショットにクラシファイアが自動的に走り、埋め込まれた悪意あるテキストや操作UI要素を検出する。検出率は攻撃の **98.6%** をブロック（Opus 4.5時点）。

**2. 操作生成** — `cliclick` というオープンソースのCLIツールで、マウスクリック、スクロール、キーボード入力を実行。PythonブリッジがClaudeのコマンドをシステム操作に変換する。

**3. コネクタ優先アーキテクチャ** — ここが巧い。Claudeは **いきなり画面操作に飛びつかない**。まずSlack、Google Calendar、GitHubなどのAPI連携（コネクタ）を試す。APIがない場合のフォールバックとしてComputer Useが発動する。

つまり、**APIがあるものはAPIで、ないものは画面を見て操作する**。

![API連携 vs Computer Use の比較](https://res.cloudinary.com/zenn/image/fetch/s--px7h17tH--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/v1/articles/cc-special-202603/06-computeruse-comparison.png?_a=BACAGSGT)

## Dispatchアプリ: スマホから自宅PCを動かす

Computer Useの真価は **Dispatch** と組み合わせたときに出る。

Dispatchは3月17日にリリースされた機能で、iPhoneのClaudeアプリとデスクトップのClaude Coworkを **QRコードでペアリング** する。セットアップは約2分。

仕組みはシンプルや。

1. iPhoneでClaudeにタスクを送る（「今日の経費レシートをスプレッドシートにまとめて」）
2. 自宅のMacでClaude Coworkがタスクを受け取る
3. Claudeがデスクトップ上でアプリを操作してタスクを完了
4. iPhoneにプッシュ通知で完了報告（または承認リクエスト）

**これ、モバイルAIエージェントやない**。デスクトップAIエージェントの **リモコン** や。実際の処理はすべてMac上で行われる。

電車の中で「あの資料まとめといて」と送って、会社に着いたら完成してる。そういう世界。

## 実用性の正直な評価

夢のある話をしたけど、現実も見よう。

**今すぐ使える:**

* ダウンロードフォルダの整理
* レシートのスキャンと経費スプレッドシート作成
* 研究論文の要約
* プロジェクトファイルのリネーム

**まだ厳しい:**

* 金融アカウント操作（Anthropic自身が非推奨）
* 法的文書の処理
* 他人の個人情報を含むアプリ
* 30分以上の長時間タスク（止まる・遅くなる報告あり）

**最大の問題はトークン消費量**。画面操作のたびにスクリーンショットを取って分析するから、テキストベースの操作より桁違いにトークンを食う。Pro契約（$20/月）の5時間枠が30分で消えたという報告は、**一般ユーザーにはまだコスパが合わない** ことを意味してる。

Max契約（$100〜200/月）なら実用的かもしれん。でもそれは「AI同僚に月給を払う」感覚やな。

## ぼくの正直な評価

Computer Useは **「ツール」から「同僚」への転換点** やと思う。

APIがなくても画面を見て操作できる、というのは根本的な変化。今まで「API連携がないアプリはAIに触れない」という制約があった。その壁が消えた。

ただし、今は「同僚1日目」や。遅い、高い、たまに止まる。でも方向性は正しい。半年後にはもっとマシになってるはず。

Anthropic自身も言ってる。「Computer use is still early compared to Claude's ability to code or interact with text」。つまり「コーディング能力に比べたら、まだ全然これから」やと。

---

# 3. Channels — 電車からコーディング

## 「席にいないと仕事できない」が終わった

Channelsは3月20日前後に発表された機能で、Telegram・Discord・Fakechatから **裏で動いてるClaude Codeセッション** にメッセージを送れる。

VentureBeatは「OpenClawキラー」と呼んだ。OpenClawは人気のあるオープンソースのAIエージェントツールで、似たような「どこからでもAIエージェントに指示できる」体験を提供してた。Channelsはそれを公式機能として取り込んだ格好や。

![Channelsのアーキテクチャ](https://res.cloudinary.com/zenn/image/fetch/s--1JoKMD6e--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/v1/articles/cc-special-202603/07-channels-arch.png?_a=BACAGSGT)

## CI/CDとの連携が真骨頂

Channelsの最もパワフルなユースケースは **CI/CD連携** やと思う。

想像してほしい。

1. GitHub ActionsでCIが失敗する
2. 失敗通知がTelegramに飛ぶ
3. その通知がClaude Codeセッションに自動転送される
4. Claudeがエラーを分析して修正PRを作る
5. あんたはTelegramで「OK」と返すだけ

![CI/CD連携フロー](https://res.cloudinary.com/zenn/image/fetch/s--QHbCtU4c--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/v1/articles/cc-special-202603/08-channels-cicd.png?_a=BACAGSGT)

開発者は電車の中。CIが壊れても、スマホの通知を見て「OK」と返すだけ。実際のコード修正はClaude Codeがやる。

これはMCPベースのプラグインアーキテクチャで実装されてて、権限リレーシステムも組み込まれてる。つまり、Claude Codeが「この操作していいですか？」と聞いてきたとき、Telegramで承認できるということや。

## まだリサーチプレビュー

正直に言うと、Channelsはまだ「使ってみて感想教えて」段階。Auto ModeやComputer Useに比べると情報量が少ない。

でも、**方向性は明確**。Claude Codeを「PCの前に座ってないと使えないツール」から「どこからでもアクセスできるサービス」に変えようとしてる。

---

# 4. 脇役だけど見逃せないアップデート

この72時間は3大機能だけやない。地味だけど実務に効く更新もあった。

| アップデート | 内容 | 影響度 |
| --- | --- | --- |
| `--bare` フラグ（v2.1.81） | hooks/LSP/プラグインをスキップして高速起動。CI/CDパイプライン向け | 中 |
| 1Mトークンコンテキスト一般提供 | Opus 4.6 / Sonnet 4.6で追加料金なし。旧Opus 4/4.1はAPI削除 | 中 |
| `/loop` コマンド | 定期的にプロンプトを自動実行。監視・テストに | 中 |
| Voice Mode 10言語追加 | プッシュトゥトーク方式。技術用語認識を最適化 | 低 |
| 3月オフピークプロモーション | 28日まで平日オフピーク5時間が2倍。使い切ってないなら急げ | 低 |

---

# 5. コミュニティの地図

## 開発者500人が選んだのはClaude Code

Dev.toに掲載されたReddit開発者500人のブラインドテスト結果:

**Claude Code 67% vs Codex 33%**

コード品質では圧勝。しかしコメント欄は「品質は最高やけどガソリンすぐ切れる」の大合唱。使用量制限への不満が、品質評価を帳消しにしかけてる。

![コミュニティ評価マップ](https://res.cloudinary.com/zenn/image/fetch/s--C-QCcuZ9--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/v1/articles/cc-special-202603/09-community-map.png?_a=BACAGSGT)

## 3月の安定性問題

もう一つ、コミュニティで頻繁に挙がってるのが **安定性** 。3月は2〜3日に1回のペースで大規模インシデントが発生してる。3月22日のclaude.ai認証障害は特に広範な影響があった。

Substackで「What's going on with Claude Code」という分析記事が出るレベル。品質がいくら良くても、業務で使うなら「落ちないこと」が大前提やねん。

## 「生産性パニック」問題

Hacker Newsで「Claude Code and the Great Productivity Panic of 2026」というスレッドが盛り上がった。

要約すると: **Claude Codeが速すぎて人間が追いつかない**。

AIが15分で500行のコードを生成する。人間がそれをレビューするのに2時間かかる。生産性は上がったはずなのに、精神的には前より疲れてる。ある開発者は「AIに合わせてレビューし続けるの、頭のギア比が違う」と表現した。

これはAuto ModeやComputer Useの登場でさらに加速する問題やと思う。AIがもっと自律的になれば、人間のレビュー負荷も増える。**速くなったのに、人間が遅くなった** — これは皮肉やなくて、現実やで。

---

# 6. 3つが交差する先

最後に、この3つの機能が **なぜ同時に来たのか** を考えたい。

![3機能の収束ビジョン](https://res.cloudinary.com/zenn/image/fetch/s--M7IkATbT--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/v1/articles/cc-special-202603/10-convergence.png?_a=BACAGSGT)

* **Auto Mode** — 「AIが判断して実行する」（許可の自動化）
* **Computer Use** — 「画面を見て操作する」（操作の自動化）
* **Channels** — 「どこからでも指示できる」（場所の自動化）

3つを組み合わせると、**「人間はスマホから意図を伝えるだけ。AIが判断して、画面を操作して、結果を返す」** という世界が見えてくる。

これはもう「ツール」の話やない。**「同僚」の話** や。

Anthropicは明確にその方向に向かってる。VentureBeatの言葉を借りれば、「computer use, Dispatch, scheduled tasks, domain-specific pluginsの組み合わせが、エンタープライズ調達を正当化するレベルのエージェントを生み出す」という賭け。

ぼくは、この賭けは **半分当たって半分外れる** と思ってる。

技術的にはもう十分すぎるほど到達してる。72.5%のベンチマーク、Sonnet 4.6のクラシファイア、MCPベースの拡張性。でも、実用性の壁がまだある。トークン消費量、安定性、30分で止まる問題。

それでも — **方向性は不可逆** や。

「コードを書く」だけのAIツールが、「仕事をする」AIエージェントに変わりつつある。その転換点が、この72時間やったんやと思う。

---

## まとめ: あんたに今すぐ関係ある3つのこと

長い記事を読んでくれてありがとう。最後に、明日から使える形でまとめる。

**1. Auto Mode を試せ**（Team契約以上）

```
claude --enable-auto-mode
# Shift+Tab で auto を選択
```

隔離環境でまず試す。デフォルトのsoft\_denyルールは絶対に消すな。

**2. Computer Useは見物でいい**（Pro/Max契約）  
30分で使用量が消える現状では、「おっ、すごいな」と体験する程度。本格活用はMax契約+半年の改善待ちが現実的。

**3. Channelsは仕組みだけ理解しておけ**  
まだリサーチプレビューやけど、CI/CD連携の発想は覚えておいて損ない。将来的に「CIが壊れたらAIが直す」がデフォルトになる。

---

もう「Claude Codeはツールです」とは言えへんくなった。

でもまだ「同僚です」とも言い切れん。

**「成長中の新入社員です」** が、今日時点の正直な評価やと思う。

3ヶ月後にこの記事を読み返したとき、「あの頃はまだこんなやったんや」って笑えるくらいの進化を期待してる。

---

*横井（Yokoi）| 関西出身。中小企業の社内SE。AI大好きおじさん。Claude Codeのリリースノートを日本語で届けたくて週報を始めた。*  
*フォローしてもらえると、次の臨時特集も届きます。*

*情報の正確性には気をつけてますが、最新情報は[公式リリースノート](https://github.com/anthropics/claude-code/releases)を確認してください。*
