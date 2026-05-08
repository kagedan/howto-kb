---
id: "2026-05-06-code-with-claude-2026-基調講演新モデルなし全製品一気に強化dreamingro-01"
title: "Code with Claude 2026 基調講演｜新モデルなし、全製品一気に強化（Dreaming・Routines他）"
url: "https://zenn.dev/ai_heatland/articles/f342838e3d5132"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "AI-agent", "zenn"]
date_published: "2026-05-06"
date_collected: "2026-05-08"
summary_by: "auto-rss"
---

## 「新モデルは発表しない」と宣言した珍しい基調講演

2026年5月6日、サンフランシスコでAnthropicの開発者カンファレンス **Code with Claude 2026** の基調講演が開催された。X（Twitter）の公式ブロードキャスト経由でも世界に同時配信され、5時間超のストリーミングが残されている。

開幕で登壇したのは Chief Product Officer の **Ami Vora**。彼女が冒頭の自己紹介と顧客事例を語り終えてから、最初に発した実務的なメッセージはこうだ。

> "Let me say up front, we don't have a new model to unveil. Today is about how we're making our products work better for you."

**訳：「先に言っておくと、今日は新モデルを発表しません。今日のテーマは、すでにあるプロダクトを皆さんにとってもっと使いやすくすることです」**

これは普通のAI企業の基調講演としてはかなり珍しい。新モデル発表を「目玉」に据えず、Claude Code・Claude API・Claude Managed Agents・Claude desktopという既存プロダクトを**横断的にアップデート**する構成で2時間弱を埋めた。それでも会場は大いに盛り上がったし、SNS上でも「Anthropicがついに製品会社に振り切った」という反応が目立った。

本記事では、X公式ブロードキャストと Simon Willison のライブブログを一次ソースとして、講演で発表されたすべての主要アップデートを発表順に解説する。文字起こしから抜き出した一次ソースの肉声と、デモのキャプチャを併載した。

!

**この章のポイント**

* 2026-05-06 サンフランシスコで開催。Tokyoは6月10日、Londonは5月19日
* 基調講演の最大のメッセージは「**新モデルなし**・既存製品の総力アップデート」
* API使用量は前年比 **17倍**、平均開発者は週 **20時間** Claudeを動かす

---

## 開幕：Ami Voraの「指数関数的進化と、線形にしか追従できない組織のギャップ」

Ami Voraは自身のキャリア、Appalachiaの山ふもとで育ち、大学のコンピュータラボに行列して入った最初のコーディング体験から話を始めた。「コンパイルを押して動いた瞬間の喜び・発見・少しの安堵」という感覚を全開発者と共有したあと、講演は急速に Anthropic の経営指標へ転換する。

### 顧客事例：Stripe・Binti・Mythosの3本立て

Ami Voraが冒頭で挙げた具体例は3本。

| 顧客 | 担当者 | 成果 |
| --- | --- | --- |
| **Stripe** | Scott McVicker（developer relations） | 5万行の Scala → Java 移行を見積もり10エンジニアリング週 → 実績**4日** |
| **Binti** | Felicia Krakuru（共同創業者・CEO） | 児童養護のフォスター家庭ライセンス手続きから**20日短縮**——「効率化指標ではなく、子どもが家族とつながるまでの日数」 |
| **Mythos**（社内研究プロジェクト） | — | OpenBSDソースツリー全体を読んで**27年前から残っていた脆弱性**を発見。「人間レビュアー、ファザー、静的解析ツール、すべてが見逃していた」 |

いずれも数字と物語を組み合わせた強力なプレゼンテーションで、「**指数関数的に賢くなるモデル vs 線形にしか追従できない組織**」というその後のテーマに直結している。

### 「指数関数」という言葉が何度も繰り返された

Ami Vora は2024年からの進化を時系列でこう要約した。

* **2年前**: 「まともなメールが書ける」が最先端だった
* **1年前**: Opus 4 がヘッドライン。「エージェントが**1時間**人間チェックなしで動く」が当時のストレッチゴール
* **6ヶ月前**: エージェントが**夜通し**動き、朝起きると仕事が終わっている
* **先月**: Mythos が OpenBSD ソース全体を読んで27年前のバグを発見

> "The jumps keep getting bigger, and the intervals keep getting shorter."（ジャンプ幅は大きくなり、間隔はどんどん短くなっている）

このスピードに対して、ほとんどの組織はAI採用を**線形ペース**でしか進められない。**この差を埋める人**＝「Closing the gap」が、本日の講演テーマであり、開発者の役割である——というのが Ami の前置きだった。

### 経営指標：API 17倍成長、平均開発者は週20時間Claude

経営指標として開示されたのは2つ。

* **Cloudプラットフォーム上のAPIボリュームは前年比 約17倍**
* **Claude Code の平均開発者は、週 20時間 Claude を動かしている**

「20時間/週」というのは、フルタイム業務時間の半分をエージェントに任せている計算になる。Anthropic 内部では「Claudeの稼働時間が業務時間の半分を超えた」という見方をしているということだ。

そして次の発表が、開発者からその場で大きな歓声が上がったポイントだった——

「rate limits をダブル」というアナウンスで、現場の開発者からは大きな拍手と歓声が起きた。Claude Code の使いすぎで5時間ごとのリミットに頻繁に当たっていた利用者にとって、これは単なる増量ではなく**運用ストレスの解消**を意味する。

---

続いて登壇したのが Head of Product, Research の **Dianne Na Penn**。彼女はAnthropic の「モデル層」を担当する責任者で、フロンティアモデルそのもののアップデートを語った。

最大の発表は **Claude Design**。これは Anthropic Labs（実験的プロダクトを段階的にロールアウトする社内ブランド）から提供される新ツールで、UIデザイン・ビジュアル生成に特化したClaude機能だ。同時にリリースされる **Opus 4.7** モデル自体が**ビジュアルデザイン能力を大幅に強化**しており、デモではUIモック・ロゴ・ビジュアル資料がClaudeから直接生成される様子が披露された。

ここに別系統で「Multi-agent coordination feature」（複数エージェントが協調してより大きなゴールに取り組む機能）の予告も入った。これは後述のMulti-Agent Orchestrationと連動する。

---

## Claude Platform：Managed Agentsに3つの新機能——Multi-Agent / Outcomes / Dreaming

舞台中央に登場したのは Claude Platform チームの **Katelyn Lesse** と **Angela Kiang**。彼女たちは Cloud Managed Agents（社内では「Claude Managed Agents」）に**3つの新機能**を一気に追加する発表を行った。

| 機能名 | 状態 | 何ができるか |
| --- | --- | --- |
| **Multi-Agent Orchestration** | Public Beta | 複数エージェントの艦隊を組成し、複雑タスクを分担解決 |
| **Outcomes** | Public Beta | Markdownで「成功条件」を定義 → Claude が条件を満たすまで自動反復 |
| **Dreaming** | Research Preview | 過去セッションを夜間に振り返り、学んだことをメモリに自動書き込み |

### 架空のスタートアップ「Lumara」を題材にしたライブデモ

二人はこの3機能を**実演**で紹介するため、ステージ上で「**Lumara**」という架空のスタートアップを設定した。

> 「最近 Anthropic は某宇宙企業（SpaceXのこと）と過ごす時間が増えている。それに触発されて、我々も自社スタートアップを作った——その名も Lumara。月にドローンを着陸させて鉱物を採掘するエージェント・ソフトウェアだ」

「我々は航空宇宙エンジニアではない、だから優秀なエージェントが必要」というユーモアで会場をなごませつつ、Lumara のシステムを Claude Managed Agents 上に構築するデモが始まる。

#### Multi-Agent Orchestration：Commander が Detector と Navigator を統括

Lumara のエージェント編成はこうだ。

* **Commander Agent**: ミッション全体の指揮
* **Detector Agent**: 採掘候補地（高品質鉱物が眠る着陸地点）の探索
* **Navigator Agent**: ドローンを安全に着陸地点へ誘導

Claude API CLI で `commander` を「他2エージェントのコーディネーター」として登録すると、Commander がセッションを起こし、Detector と Navigator は**それぞれ独立したスレッド・独立したコンテキストウィンドウ**で並列稼働する。最後に結果をマージする。

> 「これは意図的な設計です。各エージェントに独立したコンテキストを持たせて、最後にマージする方が**全体の性能が高くなる**ことがわかっています」（Angela Kiang）

これは Anthropic が Claude.ai でも採用している Subagent パターンの、API版マネージドサービスといえる。

#### Outcomes：Markdownで成功条件を書くだけ

次に Outcomes のデモ。仕組みはシンプルで、**1つの Markdown ファイル**にこう書くだけだ。

```
# Outcome: Successful drone landing

- The drone touches down softly
- The drone lands on clear ground
- Sufficient fuel reserves remain to safely return to Earth
```

このファイルをセッションにイベントとして送ると、Cloud は内部で**別の Grader Agent**（採点エージェント）を立ち上げ、各セッションの実行結果がこのルーブリックを満たすか継続評価する。

> 「もちろん one-shot で達成できる場合もあります。でも普通は数セッションかけて反復します。最大反復回数も指定できます」（Katelyn Lesse）

つまり、開発者は「**何が成功か**」だけ書けば、**「どうやってそこに到達するか」はClaude が自分で**A/Bしてくれる。エージェントの自動反復改善ループがManaged Agentsに正式な一級機能として組み込まれた。

#### Dreaming：エージェントが夜中に「夢を見て」自分を改良する

3つ目が **Dreaming**——今回の発表で最も強い驚きを呼んだ機能だ。

Lumara のシナリオ：6つの候補地のうち4つは正解、2つ（site 3 と site 4）が不正解。普通なら「ヒルクライム」（仮説検証→改善）に開発者のかなりの時間がかかるところ、Dreaming のボタンを押すだけで、夜間にエージェントが**過去の全シミュレーションセッションを読み返し**、学んだ教訓を**メモリストアに直接書き込む**。

朝起きてダッシュボードを見ると、Claude は「**降下プレイブック**（dissent playbook）」というドキュメントを自分で書いていた。これには過去ミッションから抽出したヒューリスティクスが詰まっており、以降の全セッションがこのプレイブックを参照する。

### Advisor Strategy：実行はSonnet/Hiku、相談だけOpus

このパートで Katelyn Lesse と Angela Kiang がもう1つ重要な技術を解説した。**Advisor Strategy**だ。

実装はびっくりするほど簡単で、**Messages API の `tools` 配列を更新するだけ**。エージェントアーキテクチャが「実行」と「相談」に分割される。

* **実行 (executor)**: 安価な **Claude Haiku 4.6** または **Sonnet** クラス
* **相談 (advisor)**: 高性能な **Claude Opus 4.7**

Sonnet を実行担当 + Opus を相談担当にすると、検証では「**Sonnet 単独より性能が上**」かつ「**Sonnet 単独より安い**」という結果になった——「Opus が小さなアドバイスを差し挟むことで、Sonnet がより的確な判断を下し、結果的に総トークン量も減る」というのが Anthropic の説明だ。

> 顧客の **Eave Legal**（法務AI企業）はこの Advisor Strategy で「**フロンティアモデル品質を5分の1のコスト**」で達成したと発表された。

ステージ上には**ターミナル分割ビュー**が映され、左に「Claude Haiku 4.6」のみ、右に「Claude Haiku 4.6 + Claude Opus 4.7 ADVISOR」が同じタスク（GitHub Copilot に対する初期化、Hello World を出力する難読化済み `solve.py` を書く）を並列実行する様子がライブ表示された。

![Advisor Strategy のターミナル分割ビュー](https://res.cloudinary.com/zenn/image/fetch/s--fpN0WHfn--/https://ai-heartland.com/generated_images/code-with-claude-2026-advisor-demo.gif?_a=BACAGSGT)

右側のセッションは右下に `[advise + consulting opus...]` と表示され、Hiku が Opus に相談している様子がわかる。これは Cloud Code の[Skills](https://ai-heartland.com/explain/claude-skills-explained/)の概念と近く、「専門知識のオンデマンド注入」の系譜にある設計だ。

---

## Claude Code：Cat Wu と Boris Cherny の連続デモ

会場のテンションがさらに上がったのが、Head of Product, Claude Code の **Cat Wu** と Claude Code の生みの親 **Boris Cherny** が連続登壇したパートだ。彼らは Claude Code 側の新機能を矢継ぎ早に発表した。

### Code Review：Anthropic 全社で常用される機能

最初の発表は **Code Review** 機能の正式公開。Cat Wu の言葉が印象的だった。

> 「Anthropic では今や**全チームがこの Code Review を使っている**。私たちの社内基準が、そのままお客様にお渡しできるレベルに達したということです」

これは PR を Claude が自律的にレビューし、コメント・指摘・改善案を出す機能で、CI に組み込んで**マージ前の必須レビュー**として運用できる。

### CI Auto-Fix と Security Reviews

続けて Cat Wu は2つを公開。

* **CI Auto-Fix**: PR が CI で落ちたら、Claude Code が自動で原因を特定し、修正コミットを送る。「flaky な C.I. テストを直す」「マージコンフリクト解決」「コードレビューコメント対応」など、開発者が PR を**ベビーシッター**するように使っていた時間を丸ごと自動化する
* **Security Reviews**: セキュリティレビューを自動実行する Claude 機能。社内で運用されてきたものを外部公開

### Remote Control：スマホから自分のラップトップ上のセッションを継続

この発表は会場が一番ざわついた瞬間だった。**Remote Control**（後述のRemote Agentsの基盤になる機能）はこう動く：

1. ローカルのターミナルで `remote control` と打つ
2. Cloud Code on the web の URL が払い出される
3. **モバイルブラウザ**（または Cloud Code モバイルアプリ）からその URL を開くと、**ターミナルの中身がそのまま表示**される
4. スマホから入力すれば**ターミナルに反映**、ターミナルからの入力もスマホに反映

つまり「**同じセッション・同じ dev 環境を、デバイス間でシームレスに引き継ぐ**」機能だ。Boris お気に入りのパターンは「**長時間のセッションを起動しておいて、移動中にスマホから sub-agent を起動して別タスクを実行**」。

CISO目線では当然議論の対象だが、Anthropicは「ローカル実行のセキュリティ境界はそのまま、トリガーだけリモートにする」設計だと説明した。

### Boris Cherny 登場：Routines が来た

ここで Boris Cherny がステージに上がる。Claude Code を作った張本人として、彼が紹介したのが **Routines**——非同期自動化の新プリミティブだ。

![Boris Cherny がステージで Routines を紹介](https://res.cloudinary.com/zenn/image/fetch/s--e_SYrWa8--/https://ai-heartland.com/generated_images/code-with-claude-2026-boris-routines.gif?_a=BACAGSGT)

Routines は「**Claude Code が自分自身に prompt を送る**」仕組みだ。Boris が挙げた例：

> 「CI が flaky にネットワークタイムアウトで落ちた。Routine が起き上がって、既知のインフラ問題と診断し、ジョブをリトライした。実際 Cloud Code のコードベースでは、これを多くの場面で使っている」

つまり、**Claude Code が寝ている間も自分でトリガーを発火**できる。これは GitHub Actions の cron や Webhook では届きにくい「条件分岐つきの非同期作業」を Claude セッションとして書ける、という意味で大きな転換だ。

### AcmePay デモ：決済システム全体を Claude が verifyしながら実装

Boris のデモは「**AcmePay**」という架空の決済インフラ会社に転職した想定で進む。Claude Desktop アプリを起動して、最初のタスクは「マーチャント・ダッシュボードに返金機能を追加する」。

Claude が一気に実装したのは、ペイメント業界らしい本格的な仕様だ：

* **Idempotency**（冪等性）：webhook が重複しても二重返金しない
* **Multi-currency handling**：AcmePay が稼働する全リージョンを横断
* **Audit logging**：コンプライアンス用の完全な監査ログ

実装後、Claude は**自分で実装した結果を自分で検証**する。マーチャント・ダッシュボードを開いて、返金をトリガーする——するとSuccess toast（成功通知）が表示されない。

> "That's a real edge case. Claude sees the failure. It traces it back to a race condition in the optimistic update. It fixes it. And it's going to verify that it actually works in a browser before it calls the task done."

エッジケースに当たった Claude は、楽観的更新（optimistic update）におけるレースコンディションを特定して修正、**ブラウザで再度動作確認してから**「タスク完了」と宣言する。これが Anthropic が連呼する「**Verification**」（検証）のコアコンセプトで、Claude が自分の出力を信用せず、自分で確認するからこそ async に走らせられる、という設計思想だ。

### 同期コーディングは「全体の一部」になる

Boris はこのあと、Claude Desktop のサイドバーに目を移す。AcmePay の返金実装セッションは**多くのセッションのうちの1つ**にすぎなかった。

> "Synchronous coding is now just a slice of what's happening at any given moment. And we think that going forward, a lot more code is gonna start to be written in an async way."

「同期コーディング（プロンプトを打って待つ）」は、もはや**Claudeが今やっていることの**ごく**一部**でしかない。今後はもっと async に書かれるようになる、という宣言だ。

そして Boris は自身の働き方をこう語った——

> "And for me personally, a lot of my code nowadays is written by routines. I'm not the one doing the prompting. I'm the one creating a routine that does the prompting."

**「最近の僕のコードのほとんどはRoutineが書いている。プロンプトを打つのは僕じゃない、プロンプトを打つRoutineを僕が作っている」**。エンジニア向けには「**Routine は higher-order prompt（高階プロンプト）だ**」という比喩で説明した。

### Routines の詳細仕様

Boris が示した Routines の起動条件は3種類：

1. **スケジュール起動**：cron的に定期実行
2. **Webhook起動**：外部イベントから発火
3. **任意の API コール起動**：プログラムから直接トリガー

実行環境は2択：

* **ローカル**：自分のマシンで実行
* **リモート Cloud Compute**：Anthropic のマネージドコンピュート上で実行

例として「GitHub Issue が立った瞬間に発火するRoutine」「PR をベビーシッターするRoutine」「**毎日 GitHub Issue をトリアージするRoutine**」が挙げられた。Boris のチームでは、AcmePay 返金機能のような実装も「**夜中に同僚が GitHub Issue を作った瞬間、リポジトリを監視している Routine が拾って Claude を起動した**」という流れで生まれた。

### CI Auto-Fix の中身：「flaky なら直す」ではなく「根本原因を直す」

Cat Wu が紹介した CI Auto-Fix を、Boris が改めて深掘りした。

> "It's gonna auto fix any comments from code review and security review. It's gonna auto fix CI and it's gonna auto rebase if there's merge conflicts."

PR を最後まで（マージまで）ベビーシットする Routine だ。コードレビューコメント・セキュリティレビュー指摘・CI 失敗・マージコンフリクトを**順次自動修復**する。

このデモで象徴的だったのが、CI が**ネットワークタイムアウトで flake** したシーンだ：

> "CI flaked on the network timeout. The routine woke up, it diagnosed it as a known infra issue. It retried the job and now it's green."
>
> "And actually in the Cloud Codebase, we have it not just retry. We have it fix the root cause every time."

Anthropicの Cloud Code リポジトリ自身では、Routineは単に「リトライする」だけではなく**毎回 root cause を直す**設定になっている、という。「PR の所有者である Shunir さんは、**もう赤い X を見ることがない**」——CI失敗を**人が見る前に**Routine が解決してしまう。

### Auto Mode：パーミッション・プロンプトを classifier で自動判定

開発者体験パートで Boris は **Auto Mode**（権限の自動判定）を発表した。

これまで Claude Code は破壊的操作の手前で「**1, 1, 1...**」とパーミッションプロンプトを連打させていた。Boris はこれを「会場でウェーブができそう」と笑いながら、Auto Mode の仕組みを解説した。

Auto Mode は **classifier**（分類器）が裏で2つを判定する：

1. **このアクションは破壊的か？**
2. **プロンプトインジェクションっぽくないか？**

両方クリアならClaude が自動で実行、引っかかればブロックしてエージェントは別の方法を考える。Anthropic 社内ではこれだけで「長時間ジョブを起動して帰宅して、戻ってきたらパーミッションプロンプトで止まっていた」というシナリオが激減したという。

### Work Trees：`-W` ショートカット + Claude が自分で起動・終了

「Cloudが互いを踏みつけずに複数機能を同時開発する」課題への解として、**Work Trees**（git worktree を Claude Code から第一級でサポート）が発表された。

ポイントは2つ：

1. **設定ファイル**で「worktree 間で**共有するファイル**」を宣言できる（例：`node_modules`）。ディスク容量と再インストールの手間を排除
2. **`claude -W`**（または `--worktree`）で新セッションを起動すると、自動で新 worktree が作られる
3. **Claude 自身に `enter_worktree` / `exit_worktree` ツールを与えた**——CLAUDE.md に「複数機能を並行で進めて」と書いておけば、Claude は**自律的に worktree を作って入って、終わったら出る**

デモでは Excalidraw に対して `claude -W` で2つの worktree を起動：色追加と border-radius スライダー追加を**完全並列**で進め、さらに「`create a worktree to add a star shape`」とプロンプトすると Claude が**自分で**worktree を作成する様子を見せた。

### Voice Mode と Full Screen TUI

開発者体験まわりではほかにも：

* **Voice Mode**：`/voice` で有効化、**スペースキーを押している間** Claude に話しかけられる。長文プロンプトを打つよりずっと速い、という主張
* **Flicker-Free Full Screen TUI**：従来のターミナルでは長時間セッションでフリッカー（ちらつき）が起きていた。**仮想スクロールバック**を導入することで完全フリッカーフリーに。さらに**ターミナル内の要素がクリック可能**になり、メモリ使用量も長時間でフラットに保たれる。`/tui fullscreen` で有効化（`tui` は terminal UI の略）

### Multi-Session：Claude Desktop の根本変更

そしてフィナーレが **Claude Desktop アプリのマルチセッション機能**。

実際のデモでは Excalidraw に「**新しい台形シェイプを追加する**」というタスクを投げ、Claude が

* 既存のシェイプ実装を `Explore` エージェントで読む
* プランを立案
* `constants.ts` を編集（`+1 -0`）
* `bounds.ts` を編集（`+22 -0`）
* `shapes.ts` で台形のレンダリングを追加

という一連の作業を**サイドバーから別セッションを切り替えながら**行う様子が披露された。サイドバーには「Add new trapezoid shape」「Create joke command with loop time」「Add border radius slider control」「Border radius plan backup」「Routine demo backup」「ultrareview/dicksonsa/claude-cod...」など、複数の Pin / Recents セッションが並んでいる。

![Claude Desktop のマルチセッション + Excalidraw 実コード編集デモ](https://res.cloudinary.com/zenn/image/fetch/s--QH10-oQE--/https://ai-heartland.com/generated_images/code-with-claude-2026-desktop-demo.gif?_a=BACAGSGT)

サイドバー上部には **Chat / Cowork / Code** の3タブ。**Cowork** タブは複数開発者が同じセッションに同時参加できる新機能で、画面下部には現在使用中のモデル「**Opus 4.7 - Medium**」が表示されている。

### Pin as Chapter：トランスクリプトに「目次」を作る実験機能

最後に Boris が「**実験的だがめちゃくちゃ便利**」と紹介したのが **Pin as Chapter**。

長くなった transcript の任意のアシスタントメッセージを hover すると "Pin as Chapter" ボタンが現れる。クリックするとそのメッセージに自動で章タイトルが付く（例：「Debug pointer down event」「Add missing distance to trapezoid element function」）。複数 Pin した章は**画面左上の目次**として表示され、トランスクリプト内をジャンプできる。

> "Just let Anthony Morris, our Cloud Code Desktop lead know on X. And he'll probably ship it for you tomorrow."

Boris は「Cloud Code Desktop 担当の Anthony Morris に X でメッセージを送れば、たぶん**翌日には機能を出してくれる**」と冗談めかして締めた。実際の機能ロードマップは X 上のフィードバックを反映する高速サイクルで動いている、というメッセージでもある。

---

## 顧客事例：Mercado Libre 23,000エンジニア全員 / Shopify / Eave Legal

Cat Wu のセッション中に、3つの顧客事例が紹介された。いずれもCloud Codeの組織横断での運用例として強烈なインパクトがある。

### Mercado Libre：23,000エンジニア全員が Cloud Code、PR 50万件・アプリ9,000本リファクタ

Cat Wu の口から出た数字が会場をどよめかせた。

* ラテンアメリカ最大のECプラットフォーム、月間バイヤー **1億人超**
* エンジニアリング組織 **23,000人**、**全員 Cloud Code を使用**
* これまでに **50万件以上の PR** を Claude が（人間レビュー併用で）レビュー
* **9,000本以上のアプリ**を近代化（モダナイズ）した
* 技術責任者 **Oscar Mullen** が掲げる目標：「**2026年第3四半期までに 90% の自律コーディング** + **完全エージェント駆動の PR ループ**」

> "Engineers are pointing agents at tech debt that people haven't touched in a long time and people don't have time for."（エンジニアたちは、長年誰も触らなかった、誰も時間がないと思っていた技術的負債にエージェントを向けている）

Cat Wu はさらに「私が一番好きなディテールはこの数字じゃない」と続けた——

> 「マネージャーや VP たちが、再びコードベースを触るようになっていることだ。**この10年ロードマップとレビューばかりやっていた人たちが、また自分でビルドしている**」

### Shopify：Andrew McNamara「speed is just crazy」

Shopify の Director of Applied AI, **Andrew McNamara** のコメントとして「Cloud Code が社内ツール構築の方法を完全に変えた」が紹介された。設計・プロダクト・データサイエンスといった非エンジニアリングチームにも Cloud Code が浸透している、というのが要点だ。

### Eave Legal：5x 安価でフロンティア性能

前述の Advisor Strategy 採用例。Sonnet+Opus 組み合わせで「**フロンティア品質を5倍安く**」を実現した法務AI企業。

!

**Mercado Libreの数字が業界に与える衝撃**

「23,000人全員が Cloud Code」「50万PR レビュー」「9,000アプリのモダナイズ」「Q3に90%自律」——AI採用の **規模面での先行例** として、これは Code with Claude 2026 を通じて最も強力なメッセージになった。

---

## SpaceX/Colossus 提携と、なぜ「データセンター」を借りるのか

講演途中、Ami Vora から **SpaceXの Colossus データセンター全容量** との提携が発表された。Colossus は xAI（Elon Musk の AI 企業）が稼働させている超大型 GPU クラスタで、Anthropicがそのキャパシティをすべて使えるようになる、というアナウンスだ。

これは推論コスト・キャパシティ問題への直接の手当てで、Cloud Code のレート上限ダブル化や API 17倍成長を支えるインフラ拡張のひとつ。Anthropic は単に「賢いモデルを作る」会社から、「**インフラ + プロダクト + モデル**」を3点セットで運営する大手クラウド事業者へ近づいてきている。

---

## 全アップデート総括：1枚のマップで見る講演の全体像

ここまでの発表を1枚のフローで整理すると、Code with Claude 2026 の構造はこうなる。

---

## 講演で印象的だったフレーズ集（一次ソース文字起こしから）

X公式ブロードキャストから抽出した、講演中の印象的な肉声を抜粋する。

> "I come to work with a plan, and then I have to tear it up by lunchtime because something new has happened. That sound familiar?"  
> （朝、計画を持って出社して、お昼までに新しい何かが起きて計画を破り捨てる。ピンときませんか？）— Ami Vora

> "We don't have a new model to unveil. Today is about how we're making our products work better for you."  
> （今日は新モデルの発表はありません。すでにあるプロダクトを皆さんにとってより使いやすくする日です）— Ami Vora

> "Without a human checking in felt like a stretch goal."  
> （人間がチェックインしないでエージェントが走るのは、当時はストレッチゴールだった）— Ami Vora（1年前を振り返って）

> "We've been hanging out with a particular space company for most recently."  
> （最近 SpaceX とよく一緒にいるんですよね）— Katelyn Lesse（Lumara デモの導入で）

> "We get better performance by doing this all together and then merging in all the results."  
> （全部独立に走らせて結果をマージする方が、最終性能は高くなります）— Angela Kiang（Multi-Agent 設計）

> "CI flaked on the network timeout. The routine woke up, diagnosed it as a known infra issue, retried the job, and outscreen."  
> （CI がネットワークタイムアウトで flake した。Routine が起き上がって既知のインフラ問題と診断し、ジョブをリトライした）— Boris Cherny（Routines のデモ）

---

## 「新モデルを発表しない基調講演」が意味するもの

ここで一歩引いて考えたい。なぜ Anthropic はこのタイミングで「**新モデルを発表しない**」基調講演を組んだのか。

仮説は3つある。

### 仮説1: 製品成熟度のメッセージ送信

Cloud Code・Claude API・Claude Managed Agents・Claude Desktop は、もはや**フロンティアモデルの薄いラッパーではない**。Code Review、Routines、Outcomes、Dreaming、Multi-Agent Orchestration といった機能は、**モデルの上に乗る独自の知財**だ。「新モデル発表しなくても1日埋められる」というのは、**プロダクト企業として成熟した**ことを開発者コミュニティに伝える強いメッセージである。

### 仮説2: API 17倍成長のサステナビリティ確保

API ボリュームが17倍になったということは、推論コストとキャパシティが**現状でも逼迫**している。新モデルを発表してさらに需要を煽るより、**既存ユーザーが自社製品で得られる価値を増やす**方が、収益と顧客満足度を同時に最大化できる。SpaceX Colossus 提携と Cloud Code レート上限ダブル化は、この「現有顧客の体験を底上げする」戦略と整合している。

### 仮説3: GPT-5 / Gemini 3 への準備期間

OpenAI と Google も2026年Q2-Q3にフロンティアモデルアップデートを予定している。Anthropicが今回新モデルを温存したのは、**競合のタイミングに合わせて反応する**準備として読める。フロンティア最先端の競争はモデル単体性能ではなく「**モデル + ハーネス + プロダクト**」の総合戦になっており、ハーネス側で十分に差別化された状態でモデルを刷新するほうが、ベンチマーク勝負以上のインパクトを出せる。

---

## 開発者として今日からできる実務対応

講演を見終えて、日本の開発者・チームリーダーが**今日から取れる**実務的な対応を整理する。

### 1. Claude Code レート上限ダブル化の活用

Pro/Max/Team/Enterprise いずれかのプランを使っているなら、5時間ごとの上限が2倍になっている。長時間ジョブの分割の必要性が緩和されたので、これまでチャンク分けしていたタスクをまとめ直せる。

### 2. Routines の試用準備

Claude Code 内で「自分自身に prompt を送る」設計は、cron や GitHub Actions の単純化ではなく、**条件分岐を含む自律ワークフロー**を Markdown で書けるという話だ。既存の `.claude/commands/` や `.claude/skills/` で作っている自動化のうち、**夜間バッチ・障害復旧・PR ベビーシッティング**に該当するものから移植検討するとよい。

### 3. Outcomes ファイルでテスト書き換え

Outcomes は「成功条件を Markdown で書くだけ」というシンプルさが武器。既存のリリース基準書・QA 観点表を Markdown 化して Outcomes として与えるだけで、エージェントが自動反復してくれる時代になった。

### 4. Advisor Strategy で API コスト最適化

Hiku を実行担当・Opus を相談担当にする Advisor Strategy は、**ほとんどのユースケースで5倍級のコスト削減**を実現できる。社内エージェント基盤を持つ会社は、Anthropic が公開しているサンプル設定（Claude API CLI で `--advisor opus` フラグを試せる）から検証を始めたい。

### 5. Code Review の社内導入

「Anthropic 全社で使っている」という信頼度は強い。Pull Request のテンプレートに Claude Code Review を組み込み、**人間レビューより前**に自動レビューが走る運用を試したい。

---

## 比較表：今回発表された主要機能の利用ステージ

| 機能 | 利用可能ステージ | 主な対象 | 想定ユースケース |
| --- | --- | --- | --- |
| **Claude Code レート上限2倍** | 即日（自動適用） | Pro/Max/Team/Enterprise | 長時間ジョブ |
| **Multi-Agent Orchestration** | Public Beta | Cloud Platform 顧客 | 複雑タスクの分担解決 |
| **Outcomes** | Public Beta | Cloud Platform 顧客 | 成功条件ベースの自動反復 |
| **Dreaming** | Research Preview | 招待制 | エージェントの自己改善 |
| **Advisor Strategy** | 一般提供（API CLI） | コスト感度の高い運用 | フロンティア性能を5xコスト削減 |
| **Code Review** | 一般提供 | Claude Code ユーザー | PR自動レビュー |
| **CI Auto-Fix** | 一般提供 | Claude Code + GitHub | flaky CI の自動修復 |
| **Security Reviews** | 一般提供 | Claude Code + 大規模リポジトリ | 自動セキュリティ監査 |
| **Remote Agents** | 段階展開 | Claude Code モバイル連携 | スマホからのトリガー |
| **Routines** | 一般提供 | Claude Code | 非同期自律ワークフロー |
| **Multi-Session Desktop** | 一般提供 | Claude Desktop | 並列セッション管理 |
| **Claude Design** | Anthropic Labs | UIデザイナー | UI/ビジュアル生成 |

---

## まとめ：プロダクト企業 Anthropic への完全シフト

!

**Code with Claude 2026 速報の結論**

2026-05-06 の基調講演は、Anthropic が「**研究ラボから本格プロダクト企業へのシフトを完了した**」と宣言する場だった。新モデル発表を温存し、Claude Code・Cloud Platform・Claude Desktop の3製品を一気にアップデート。Routines・Dreaming・Outcomes・Advisor Strategy・Multi-Session など、**モデル単体ではなくハーネス全体の差別化**に振り切った。日本の開発者にとっては、まずレート上限2倍と Routines の活用から手をつけたい。

最後にAnthropicは Tokyo（**6月10日**）と London（**5月19日**）の追加開催を告知し、講演を締めくくった。Tokyo 開催では今回SF発表の各機能のローカリゼーションと、日本市場固有の事例（既に発表されている [GMO・三菱UFJ・ZOZO等の Claude API 採用事例](https://claude.com/code-with-claude/tokyo)）の深掘りが見込まれる。

新モデルを発表しないことが「ニュース」になる——そんな段階に AI 業界は入ったことを、この基調講演ははっきり示した

## 参照ソース
