---
id: "2026-05-09-codexをコーディングツールだと思っていたら全然違った後編自動化マルチタスクclaude-code-01"
title: "Codexを「コーディングツール」だと思っていたら、全然違った——後編：自動化・マルチタスク・Claude Codeとの使い分け"
url: "https://zenn.dev/kenworkflow/articles/474853a25d8507"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "prompt-engineering", "API", "AI-agent", "OpenAI"]
date_published: "2026-05-09"
date_collected: "2026-05-10"
summary_by: "auto-rss"
query: ""
---

前編では、Codexの基本概念（プロジェクト＝フォルダ、記憶、Plugin、Skill、画像生成）について書きました。後編では「実際にどう使うか」の話をします。

結論から言うと、Codexの真価は個々の機能じゃなくて、それらを組み合わせたときに出てくる。ブラウザ操作＋Skill＋定時実行を繋げると、個人レベルのRPAが自然言語だけで組めるようになります。

## ブラウザ操作・コンピュータ操作——エージェントがGUIを触る

![](https://res.cloudinary.com/zenn/image/fetch/s--8U3xXLSF--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://hcniahdryda7.feishu.cn/space/api/box/stream/download/asynccode/%3Fcode%3DYTEwOWVkNTc1MjFlZTE0YjU4YmYzYjdlZjQ3NWEzMDJfQjVIMndOekJwWXhSMFNtcmpkVHZmanI2enhRckpQYUVfVG9rZW46RUpuUmJSQjQybzlzaDZ4UHN2QmMwVFNNbmpnXzE3NzgzMTQ0Nzg6MTc3ODMxODA3OF9WNA)

これが一番驚いた能力です。

Codexには`@browser use`と`@computer use`という2つのプラグインがあって、エージェントが実際にマウスとキーボードを操作します。画面を見て、クリックして、入力して、スクロールする。APIがないアプリケーションでも、GUIで操作できるものならエージェントに渡せる。

### Computer Useの実例

前編で生成した5枚の商品画像を、[Canva](https://www.canva.com/)でプレゼン資料にまとめる作業。「Canvaを開いて、新しいプレゼンを作って、この5枚の画像を1ページずつ配置して」と指示すると、エージェントがCanvaのデスクトップアプリを起動して、実際にマウスで操作して、スライドを作っていきます。

自分がやったら15分かかる作業が、プロンプト1本で終わる。しかも自分はその間、別のチャットで次のタスクを進められる。

### Browser Useの実例

[Riley Brownのチュートリアル](https://www.youtube.com/watch?v=474wZZHoWN4)で印象的だったのは、エージェントに自動QAをやらせていた場面です。自分が作ったWebアプリのHTMLを生成させた後、「ブラウザで開いて、Startボタンを押して、クイズに答えて、正誤判定が動いているか確認して」と頼む。エージェントが開発者であると同時にテスターにもなる。

ここだけの話、この機能を見たとき「人間がマウスとキーボードでやってることの大半は、原理的にエージェントに渡せるようになったんだな」と思いました。APIの有無に関係なく。これはCodexの中でも一番射程が広い能力だと感じています。

## Automation——すべてを定時タスクにする

![](https://res.cloudinary.com/zenn/image/fetch/s---kmw8KWv--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://hcniahdryda7.feishu.cn/space/api/box/stream/download/asynccode/%3Fcode%3DZjdkMGIyNGIxYjNlM2UzYmNjNGU3YmExYjlhMzRkMzZfTlpQaklBN0IwTklnbWdCZTNXaGl4NWFmSklTaDk4QzdfVG9rZW46TTdjWmJmMURCb0VNaUZ4OHJnOGNoZFRJbjlnXzE3NzgzMTQ0Nzg6MTc3ODMxODA3OF9WNA)

前編で説明したPluginとSkillを、時間軸に乗せるのがAutomationです。

使い方はシンプル。すでに動いたチャットの中で「これを毎週金曜の午後4時に自動実行して」と言うだけ。エージェントがAutomationsパネルにcronジョブを作ってくれます。

[Riley Brownが動画の中で設定していた](https://www.youtube.com/watch?v=KXIdYEdOPys)のは3つ——

* 毎週金曜16時：Googleカレンダーから来週の予定を読んで、サマリーを生成
* 毎月末：YouTubeチャンネルの分析レポートを自動作成（Supadata APIのSkill経由）
* 毎朝：[Typefully](https://typefully.com/) APIでX（旧Twitter）の投稿を3本下書き

やっていることは、Plugin（接続）→ Skill（手順）→ Automation（スケジュール）の3段積み。これが全部自然言語で組めるので、[Zapier](https://zapier.com/)やn8nを触ったことがなくても、自分専用の自動化パイプラインが作れます。

個人的には、Automationが一番ROIの高い機能だと思っています。高頻度だけど価値の低い仕事——経費精算の集計、メールのフィルタリング、定期レポートの下書き——をここに逃がすと、週あたり数時間が浮く。

## マルチタスク——「並行処理」ではなく「直列化」

![](https://res.cloudinary.com/zenn/image/fetch/s--KznWCgVu--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://hcniahdryda7.feishu.cn/space/api/box/stream/download/asynccode/%3Fcode%3DMTE3MDM3MDVlODIxN2JjOGUwMGZlNjYwYWYzMGRjYjNfQ0RxQzNxSzNoUWJXazZoNHY3aFBJS1RzTEc5dEpvQ0JfVG9rZW46Qk13cmJNVHJCb2ViVTR4eXNNR2NOajFlbmlnXzE3NzgzMTQ0Nzg6MTc3ODMxODA3OF9WNA)

ここからは方法論の話です。

[Riley Brownの100分チュートリアル](https://www.youtube.com/watch?v=KXIdYEdOPys)では、ひと晩で6つのプロジェクトを同時に進めていました。iOSアプリの設計稿、アプリ本体のSwift実装、ランディングページ、投資家向けデッキ、プロモーション動画、SNS自動投稿。

でも、ここからが本題で——彼自身が「multitaskという言い方は正確じゃない」と訂正しています。より正確には​\*\*serializing（直列化）\*\*​。

> "Each prompt that you type in is the task. Once you press enter, check out of that task and move to a new one."

6つの画面を同時に見ているわけじゃない。質の高いプロンプトを1本書いて、Enterを押したら、そのタスクから離れる。エージェントが5〜15分かけて独立に作業している間に、自分は次のチャットを開いて次のプロンプトを書く。終わったらチャットの青い点を見て戻ってレビューする。

この働き方が成り立つには、2つのことが必要です。

​**プロンプトの密度を上げる**​。一回の指示で十分なコンテキストを渡しきる。後から「あ、これも」「ここはこうして」と追加するほど、エージェントの作業が中断されてロスが出る。

​**手を離す勇気を持つ**​。進捗バーを不安に眺めるのをやめて、信頼して別の仕事に移る。エージェントの単一タスク稼働時間は[Riley Brownによると1〜2時間](https://www.youtube.com/watch?v=KXIdYEdOPys)まで伸びてきています。この時間をどう使うかが、生産性の分かれ目になる。

### steeringとqueueの違い

エージェントが長いタスクを実行中に追加指示を出したいとき、2つの入力モードがあります。

​\*\*通常入力（queue）\*\*​：エージェントが現在のタスクを最後まで終えてから、次の指示として処理する。

​**steer入力**​：エージェントが次のツール呼び出しを終えた瞬間に、割り込みで指示を挿入する。

これ、意外と知られてないんですが、長時間タスクの途中で「やっぱり出力フォーマットをCSVじゃなくてExcelにして」みたいな軌道修正ができるということです。タスクを最初からやり直させなくていい。

### fork chat＝会話のブランチ

もう一つ実用的な機能。あるチャットで満足のいく結果が出たら、そのチャットを右クリックして「fork into local」すると、上下文がすべて引き継がれた新しいチャットが分岐します。

たとえばiOSアプリのデザインが完成したチャットからforkして、「このアプリの視覚スタイルを参考にして投資家向けデッキを作って」と指示する。ゼロから説明し直す必要がない。Gitのブランチを会話に適用したような感覚です。

## Claude Codeとの使い分け——どちらか1つじゃない

![](https://res.cloudinary.com/zenn/image/fetch/s--9m2A9gr2--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://hcniahdryda7.feishu.cn/space/api/box/stream/download/asynccode/%3Fcode%3DNWYyNTMzMzQ2YWE1YTNkNmYyZWU3ZmE3NWI4YjVmNmJfV3U0elVERWJvbm1QckF1QmNuUWhnbGg1d3B0ZWZpRzVfVG9rZW46V2h3QWJueTdQb2c3TWR4d3g4YWNzU1RNbmJoXzE3NzgzMTQ0Nzg6MTc3ODMxODA3OF9WNA)

ここは前回の[使い分け記事](https://note.com/)でも書きましたが、CodexとClaude Codeは競合というより補完関係です。

**Codexの強み**は統合性。コーディング、ファイル操作、Plugin経由の外部連携、画像生成、ブラウザ操作、Automation——全部が一つのチャットUIに収まっていて、非エンジニアでも使えるGUIがある。

**Claude Codeの強み**は推論の深さ。[200Kトークン標準、Opus 4.6で100万トークンのコンテキスト](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview)を使った大規模コードベースの把握、十数ファイルにまたがるリファクタリングの一発完了、SWE-benchでの高い解決率——複雑なエンジニアリングタスクでは信頼性が一段上です。

Riley Brown自身が[動画の中で実践していた](https://www.youtube.com/watch?v=KXIdYEdOPys)使い方が印象的でした。Codexのターミナルの中で`claude --dangerously-skip-permissions`と打って、Claude Codeをサブエージェントとして呼び出している。ランディングページの視覚的な仕上げや、投資家デッキのデザイン精度が必要な部分はClaude Opus 4.7に任せる。

> Codexをオーケストレーター、Claude Codeをサブエージェントとして使い分ける。

これ、今も使ってる。タスクの「性格」で切り替えるのが現時点のベストです。工程管理や複数ツールの連携はCodex、深い推論やデザインの最終仕上げはClaude Code。

## 気になった点も書きます

### Chronicle（環境感知記憶）

Codexには「Chronicle」という機能があって、常時スクリーンショットを撮ってエージェントに視覚的なコンテキストを渡します。有効にすると、何もファイルを渡さなくても「さっきわたしが見ていたプレゼンに何を追加すべきか」とエージェントに聞ける。

便利です。でも、常時スクリーン録画が走っているということでもあるので、クライアントの機密資料や個人情報を表示している画面が記録される可能性があります。業務環境では、有効にする前にコンプライアンスの確認が必要です。

### 「何でもできる」ゆえの迷子問題

機能が多すぎて、最初は何から手をつければいいかわからなくなります。これは正直、最初は意味がわからなくて。

個人的にうまくいったのは、まず一つの繰り返しタスクに絞ること。たとえば毎週やっている経費精算をSkill化して、Automationに回す。それが安定したら、次のタスクに広げる。一気に6並列しようとするのは、Codexの操作に慣れてからの方がいいです。

### 「通用モデル＋自作Skill」はSaaSを置き換えるのか

Codexが「APIさえあれば何でもSkillにできる」という状況になったとき、軽量SaaSの立場はかなり厳しくなります。ただ、現時点ではSkillの安定性にばらつきがあるし、APIの仕様変更に自動で追従する仕組みもない。「今日の時点では面白い可能性」であって、「明日からZapierを解約しよう」ではないです。

## Codexの能力スタックを整理する

ここまでの前後編を全部抽象すると、Codexの構造はこうなります。

**Chronicle（環境感知）** → エージェントが「見る」 **ファイルシステム＋AGENTS.md** → 作業場所と長期記憶 **Plugin** → 外部サービスとの接続 **Skill** → 「何をどうやるか」のレシピ **Browser / Computer Use** → GUIレベルの実行 **Automation** → 時間軸上のトリガー

Plugin（接続）→ Skill（手順）→ Automation（スケジュール）の3段階で組むと、個人レベルのRPAが自然言語だけで完成する。これがCodexの本当の使い道だと思っています。

## 最後に——「学べるかどうか」より「何をやらせるか」

Riley Brownが動画の中で何度も言っていたのが「I also have never used Supabase / Remotion / Typefully API」——自分も使ったことがない。でも、エージェントにAPIドキュメントを読ませて、一緒にやりながら覚える。

学習曲線がエージェントに吸収された後、人間に残る仕事は2つだけです。「やる価値のあることを見つける」と「出てきた結果が十分かどうか判断する」。ツールの使い方は、もう競争力じゃなくなりつつある。

エージェントのスキルを複数ツール間で再利用する仕組みとして、[EvoMap](https://evomap.ai/)が面白いアプローチを取っています。AGENTS.mdやCLAUDE.mdに書いたルールはそのツールの中で閉じてしまいますが、EvoMapの[GEP（Genome Evolution Protocol）](https://evomap.ai/wiki)は、エージェントのスキルを「Gene」という単位で構造化して、モデルやツールをまたいで継承・再利用できるようにする。CodexとClaude CodeとCursorを行き来する人ほど、こういう横断的な仕組みの価値を感じるはずです。

#OpenAICodex #AIエージェント #ClaudeCode #自動化 #AIツール
