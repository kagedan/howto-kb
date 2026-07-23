---
id: "2026-07-23-mastra-youtube-解説-agents-hour今週のaiニュースまとめ2026年7月22-01"
title: "[Mastra YouTube 解説] Agents Hour：今週のAIニュースまとめ（2026年7月22日）"
url: "https://zenn.dev/shiromizuj/articles/e563d0feeaace7"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "LLM", "OpenAI", "Gemini"]
date_published: "2026-07-23"
date_collected: "2026-07-24"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の[公式YouTubeチャンネル](https://www.youtube.com/@mastra-ai)にアップされた動画を速報ベースでお伝えします。ただの文字起こしではなく、扱われているトピックの抽出と、トピックごとの要約をしています。速報性重視でAIの力を多分に使っているので、私自身の考察は少なめです。

[Mastra YouTube動画 速報解説一覧](https://zenn.dev/shiromizuj/articles/8d6e4fd86631e9)

---

## 動画情報

<https://www.youtube.com/live/lZoo4EcSjmA>

* **URL**: <https://www.youtube.com/live/lZoo4EcSjmA>
* **原題**: Agents Hour - Live from London (Part 2)
* **公開日**: 2026年7月22日
* **言語**: 英語
* **備考**: Mastra が TypeScript AI Conference（7月23日・ロンドン）のためロンドンにいるため、通常の月曜から変更して火曜開催。本記事はニュースセクションのみを対象とします。

---

## 概要

今回の Agents Hour はロンドンのオフサイトから生配信。Shane Thomas（CPO）と Abhi Aiyer（CTO）が、Kimi K3 の登場を筆頭に盛り沢山なニュースを駆け足でお届けしました。

主なトピックは以下のとおりです。

* **Kimi K3** の衝撃登場とフロンティアモデルへの肉薄
* **Claude Fable** の永続化と **Opus 5** リークの噂
* **蒸留攻撃（Distillation Attack）論争** と Anthropic の著作権和解（$15億）
* **Grok Build** のオープンソース化
* **Thinking Machines / Inkling** のオープンウェイト公開
* **Gemini** 新モデルへの率直な評価
* **Ramp Router** と "Ramp は AI 企業にピボットする" というホットテイク
* **Door Dash CLI** と Uber Eats CLI テクニック
* **ファクトリーエンジニア** という概念の台頭

---

## 要点

1. Kimi K3（2.8兆パラメーター）がフロントエンドコードアリーナで Fable 5 を超えて1位を獲得。Sonnet 価格帯で提供。
2. Kimi K3 は需要が急増し新規サブスクを一時停止。Ali Cloud 経由での利用が有力代替。
3. Anthropic は Claude Fable を Max・Team プランへ永続的に含めると発表。コミュニティの離反を防ぐための事実上のコードレッド対応。
4. Opus 5 のリーク情報が浮上。Fable 並みの性能かつ Opus 価格帯になれば Sonnet 5 の失敗を挽回できる可能性。
5. 蒸留攻撃批判に対し、ホストたちは「自分たちのモデルもオープンインターネットデータで無断学習したのでは」と反論。
6. Anthropic が書籍の著作権侵害で $15 億ドルの和解金を支払い（米国史上最大規模と思われる）。
7. Grok Build が Git リポジトリを含めてオープンソース化。
8. Thinking Machines の Inkling モデルがオープンウェイト公開予定。Tinker と組み合わせてファインチューニングが容易に。
9. Gemini 新3モデルはフロンティア以下で、開発者からの評価は芳しくない。
10. Ramp が LLM ルーター "Ramp Router" を一般公開。Shane は "Ramp は半年以内に AI 企業にピボットする" と予測。

---

## 詳細

### Kimi K3 — フロントエンドで Fable 5 を超えたモデル

![](https://static.zenn.studio/user-upload/ee31eb2cfe78-20260722.png)

**7月16日、Moonshot AI（Kimi.ai）が Kimi K3 を発表しました。**

主なスペックは以下のとおりです。

* **パラメーター数**: 2.8兆
* **コンテキストウィンドウ**: 100万トークン
* **マルチモーダル**: ネイティブ対応
* **価格帯**: Sonnet 相当

ナレッジワークとエージェント型ブラウジングのベンチマークでは Fable 5 に並ぶ水準を示しています。  
![](https://static.zenn.studio/user-upload/fedc0e604bd5-20260722.png)

人工分析インデックスでは 57 点（Opus 4.8 や 5.5 相当）を記録。ただし Fable や GPT-5.6 には及びません。

![](https://static.zenn.studio/user-upload/b9b049062853-20260722.png)

注目はフロントエンド領域です。**フロントエンドコードアリーナで 1,679 ポイントで1位**となり、Fable 5、Sonic 5、Opus 4.8 をすべて上回りました。

![](https://static.zenn.studio/user-upload/aec83901310a-20260722.png)

デザインアリーナでも同様に1位を獲得しています。Shane は「フロントエンドのワンショット生成の精度がこれまでのモデルより明らかに高かった」と述べています。

![](https://static.zenn.studio/user-upload/7b1fd82f732b-20260722.png)

また、法律タスクでは Fable の2倍の性能というデータも公開されており、法務エージェントの開発者にとって選択肢の一つになりうるとホストたちは見ています。

![](https://static.zenn.studio/user-upload/bb955cdb02d5-20260722.png)

価格設定については、これまでの中国製モデルが圧倒的な安さを売りにしてきたのとは異なり、Sonnet 相当という "比較的高め" の価格設定を採用している点が特徴的です。それでも OpenAI より安く、性能を考えると競争力があるとホストたちは評価しています。

**需要爆発で新規サブスクを一時停止**

発表から48時間で GPU キャパシティの限界に近づき、既存ユーザー保護のため新規サブスクを一時停止する事態に。Kimi.ai がこれほどの需要を計画していなかったことが伺えます。Shane は「Alibaba Cloud に今すぐ声をかけるべき」とコメントしています。

![](https://static.zenn.studio/user-upload/787c9951ef5b-20260722.png)

なお、**近日中にオープンウェイトを公開予定**とのアナウンスも出ており、実現すれば最強のオープンソースモデルとなります。

![](https://static.zenn.studio/user-upload/b0888e5e1477-20260722.png)

**Ali Cloud について**

Ali Cloud（阿里クラウド）はプロバイダーで、サブスクまたはトークンプランを購入するとオープンモデルが利用できます。Deepseek V4、Kimi 2.7、GLM 5.2 などに対応しており、推論速度が速いのが特徴です。Kimi K3 はまだ対応していませんが、将来的に追加される見込みとのことです。

---

### Claude Fable の永続化と Opus 5 リーク

**7月17日、Anthropic が Claude Fable の扱いを変更しました。**

* 7月20日以降、Claude Fable を **Max・Team プレミアムプランに上限50%で含める**（追加料金不要）
* Pro・Team Standard ユーザーには使用量クレジット経由で引き続きアクセス可能
* 対象ユーザーに\*\*$100のワンタイムクレジット\*\*を付与

![](https://static.zenn.studio/user-upload/fada0f051f65-20260722.png)

ホストたちは「これは事実上のコードレッド対応だった」と見ています。Kimi K3 や Grok 4.5 など競合モデルが十分な品質に達しつつあり、Fable を消費クレジット課金のみにすれば大量の解約が起きていた可能性があります。「Fable を消されたら辞める」という視聴者コメントを引用しながら、Anthropic はそのリスクを取れなかったとコメントしています。

さらに、**Opus 5 のリーク情報**も浮上しました。Sonnet 5 が不評だったため、Opus 5 で Fable 相当かそれに近い性能を Opus 価格帯で提供することが Anthropic の次の一手になりうるとホストたちは予測しています。実現すれば、サブスク内で高使用量を提供できるプランとしての魅力が増すとのことです。

![](https://static.zenn.studio/user-upload/b1da831d6bdf-20260722.png)

また Abhi は「複数の AI プランを持つことを強く推奨する」とも述べており、特定モデル一択ではなく、Anthropic・OpenAI・Ali Cloud など複数を組み合わせて使うスタイルを実践していることを紹介しました。

---

### 蒸留攻撃論争と Anthropic の著作権和解

**蒸留攻撃（Distillation Attack）とは**

中国のモデル企業が大量の API アカウントを作成し、プロンプトとその回答データを自社の学習データとして収集する行為を指します。Anthropic の CEO Dario Amodei はこれを批判してきましたが、ホストたちはその主張に懐疑的です。

![](https://static.zenn.studio/user-upload/976e0969bb57-20260722.png)

「自分たちのモデルも、過去20年分のオープンインターネットデータをほぼ無断で使って学習させてきたのではないか。しかも現在も、ユーザーが料金を払って使ったアウトプットを将来の学習に活用している。ユーザーが生成させたコードは自分のものではないのか」というのがホストたちの見解です。Shane は「API を通じて生成させたコードを自分のプログラムで使うのは当然の権利であり、そこからモデルを学習させても、払ったからには文句を言われる筋合いはない」とコメントしています。

一方、**無料クレジットを悪用したゲートウェイファーム**（犯罪者が無料枠を横取りしてルーターとして使う行為）は別問題であり、これはプロバイダーが無料プランを廃止すれば対処できると述べています。

**Anthropic の著作権和解（$15億ドル）**

書籍の著作権侵害に関する訴訟で、Anthropic が **15億ドルの和解金**を支払ったと報道されました。OpenAI も同様の訴訟でヒットされています（規模は小さい）。ホストたちは「無料ではなかったが、全部払っていたら学習自体が成り立たなかった。そのうえで蒸留に文句を言う資格はない」という立場です。

![](https://static.zenn.studio/user-upload/dccfc41953b3-20260722.png)

---

### Grok Build がオープンソース化

xAI（SpaceX）が **Grok Build をオープンソース化**しました。CLI の Git リポジトリも含めて公開されており、信頼性・堅牢性のあるハーネス構築を誰でも行えます。

![](https://static.zenn.studio/user-upload/161c002d4c5d-20260722.png)

ホストたちは「良い動き」と評価。以前に git の commit 履歴を誤って Google Cloud に送信してしまうブランダーがあったことが背景にあるかもしれないとコメントしました（笑）。OpenAI の Codex も（ある意味）オープンソース化されており、Claude Code はソースアベイラブルだった時期こそあれ現在はオープンソースではありません。エージェント型コーディングツール領域でオープンソース化の流れが進んでいます。

---

### Thinking Machines — Inkling モデル発表

Thinking Machines が **Inkling** を発表しました。テキスト・画像・音声のモダリティを横断して推論できるモデルで、**完全なウェイトを公開予定**です。

![](https://static.zenn.studio/user-upload/c20b63b4bf17-20260722.png)

Tinker プロダクトと組み合わせることで、自前データでファインチューニングしてそのまま Thinking Machines のインフラ上で動かすことができます。フロンティアには届かないものの、「ファインチューニングして自分専用モデルにできる」という選択肢を提供することで差別化を図る戦略です。

ホストたちは「ファインチューニングと強化学習の時代はまだこれからだが、こうしたツールが普及することで、将来的に安価な自分専用モデルを持てる時代が来る」と見ています。

---

### Gemini 新モデル — フロンティアへの道のり

Gemini 3.6 Flash、3.5 Flash Light、3.5 Flash Cyber の3モデルが発表されました。3.6 Flash は 3.1 Pro を超えましたが、ほぼ全てのベンチマークでフロンティア以下です。

![](https://static.zenn.studio/user-upload/d5c22152f5c7-20260722.png)

ホストたちの評価は率直で、「誰も Gemini をコーディングには使っていない。Google 検索に組み込まれた AI 機能は便利だが、モデルリリースとして発表するとベンチマークで評価されてしまい傷が見える」とコメントしています。コンシューマー向け製品での強みを持つ Google が、同時にモデル競争に参加しようとしているが、どちらも中途半端に見えるというのがホストたちの見解です。

---

### Ramp Router — 「Ramp は AI 企業にピボットする」

**7月20日、Ramp が LLM ルーター "Ramp Router" を一般公開しました。**

3年前に内部で開発した LLM ルーターをオープンソースとして公開。1つの OpenAI 互換エンドポイントから最適なモデルを自動選択し、アプリを書き換えることなくコスト削減できます。

![](https://static.zenn.studio/user-upload/5876e66d8cec-20260722.png)

ホストたちは Ramp のエンジニアリングチームを高く評価しつつ、「ルーターそのものは珍しくはない」とも述べています。重要なのは、**内部で有用だったものをコミュニティに開放するスタイル**。Inspect（ソフトウェアファクトリー）を最初に公開してブームを作ったときと同じアプローチです。

**Shane のホットテイク：「Ramp は半年以内に AI 企業にピボットする」**

「内側の知見を外に出しながら、ポジショニングを積み上げてきた Ramp は、最終的に Inspect を軸として Devon と競合する製品を出す。6ヶ月後には、財務サービス部門を持つ AI 企業になっていると思う」というのが Shane の予測です。Amazon が AWS で事業の重心を移したように、Ramp も AI が中心になっていく可能性があるとのこと。「間違えるかもしれないが、思い切り振らないとね」とも添えています。

---

### Door Dash CLI と Uber Eats CLI テクニック

**Door Dash CLI が米・カナダの macOS 開発者向けに限定ベータ公開されました。**

エージェントから直接 DoorDash で注文できる CLI です。ホストたちは「面白いが誰が使うの？」と言いつつも、「ライブ配信中に注文して、配信が終わるまでに届くかテストしたい」と楽しみにしていました。

![](https://static.zenn.studio/user-upload/aeca538fbb88-20260722.png)

合わせて紹介されたのが、**Dax が Jay Longster から教わった Uber Eats CLI の作り方**です。

![](https://static.zenn.studio/user-upload/b72e9750d060-20260722.png)

手順は以下のとおりです。

1. エージェントにブラウザを操作させながらネットワークリクエストを記録させる
2. そのリクエストパターンから CLI を生成する

Web UI はマークアップが変わりうるが、API リクエストの構造はそうそう変わらないため、自動化の土台として堅牢です。認証（Cookie や JWT の取得）が最大の課題ですが、セッションを取得してヘッダーに付ければ動作します。「任意のウェブサービスで自分専用の CLI を作れる、汎用的なテクニック」とホストたちは評価しています。

---

### ラピッドファイア: その他ニュース

* **Open Ship**: 自分のインフラにアプリをデプロイ・運用・スケールするためのオープンソースプラットフォーム。

![](https://static.zenn.studio/user-upload/c45190b3b6b7-20260722.png)

* **AI SDK for Python**: Vercel の AI SDK が TypeScript だけでなく Python でも使えるようになった（Europython で発表）。

---

### ファクトリーエンジニアという概念

Mastra チームメンバーの Alex が共有した動画がきっかけで取り上げられたトピックです。Kent Dodds も「What the devil is a factory engineer?」というタイトルの動画を公開しており、この概念への関心が高まっています。

![](https://static.zenn.studio/user-upload/86b9150f345d-20260722.png)

**ファクトリーエンジニアとは**、ソフトウェアを直接書くエンジニアではなく、**ソフトウェアを作るファクトリー（システム）を構築するエンジニア**のことを指します。長時間動き続け、野心的なタスク（例: Bun を Rust に書き直す、など）をこなすエージェントシステムを設計・運用します。

ホストたちは「今日のゲスト（観測メモリ、ビデオプロダクション）はすべてこの "ファクトリー" に繋がる話だった」と振り返り、耐久性・決定論的構造・メモリの重要性を強調しました。2日後の TypeScript AI Conference（ロンドン、7月23日）でも Mastra から関連する発表があるとのことです。

コーディングファクトリーだけでなく、コンテンツ・マーケ・セールス・ビデオ制作など多くの領域でファクトリー化が進むとホストたちは予測しています。

---

### GitHub スターパーティ: Yard Arm（Mastra Code の Electron アプリ）

元 Gatsby 同僚の Jeremiah が、Mastra Code の Electron アプリ **Yard Arm** を独自に開発・公開しました。Mastra Code はオープンソースのため、コミュニティが独自のクライアントやラッパーを作っているとのこと。Mastra チームも公式にいくつかの動きがあるとのことです（詳細は近日発表）。

---

## 関連リンク
