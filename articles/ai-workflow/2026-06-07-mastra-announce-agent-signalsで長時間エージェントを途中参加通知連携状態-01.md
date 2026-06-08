---
id: "2026-06-07-mastra-announce-agent-signalsで長時間エージェントを途中参加通知連携状態-01"
title: "[Mastra Announce] Agent Signalsで長時間エージェントを途中参加・通知連携・状態更新できるように"
url: "https://zenn.dev/shiromizuj/articles/e91394dd201039"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "AI-agent", "OpenAI", "zenn"]
date_published: "2026-06-07"
date_collected: "2026-06-08"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の [公式Blog](https://mastra.ai/blog) で発表された [Announcements](https://mastra.ai/blog/category/announcements) を、周辺知識も補いながら解説します。今回は単なる新 API の追加ではなく、**長時間動くエージェントをどう観察し、どう途中で導き、どう外部イベントとつなぐか** という、エージェント実装の根っこに関わる発表です。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

## 今回の発表をひとことで言うと

今回 Mastra が発表した Agent Signals は、**エージェントを「ひとりの人間がリクエスト・レスポンスする相手」ではなく、「チームみんなの仲間」として扱うための仕組み**です。

従来のエージェント実装は、多くの場合 `agent.stream()` のような request/response 的な入口が中心でした。1 人が 1 回の依頼を投げて結果を受け取る用途にはこれで何も問題はありませんでした。ですが、エージェントが数分から数時間動き続け、複数の UI や複数の人間が途中参加し、外部イベントにも反応し、しかも内部状態を抱えながら進むようになると、この形ではかなり苦しくなります。

Agent Signals はそこを変えます。メッセージ送信、途中割り込み、次ターンへのキュー、processor からの文脈注入、状態の差分更新、GitHub や Slack などの外部通知取り込みを、**同じ thread 上で順序付きに扱える**ようにします。

しかも重要なのは、これが単なるイベント配送機能ではなく、**コンテキストエンジニアリングの新しい基本部品**として設計されていることです。Mastra は Signals を「動いているエージェントへ、必要な文脈を必要な瞬間に届けるための primitive」と位置づけています。

---

## 背景: なぜ従来の request/response では足りなくなったのか

2026 年のエージェントは、2024 年の chatbot とはかなり違うものになっています。いま実務で増えているのは、たとえば次のようなタイプです。

* 何十分もコードベースを調べ続けるコーディングエージェント
* 会議や Slack 監視を継続しながら、必要なときだけ反応する業務エージェント
* バックグラウンドでタスクを進め、途中で人間が方針を差し替えるアシスタント
* 複数 UI から同じ会話スレッドを監視・操作するサポートエージェント

この手のシステムでは、最初にプロンプトを投げた人だけがストリームを持つ、という前提がすぐ破綻します。Web のダッシュボードで進捗を見ていた人と、Slack からフォローアップを送った人と、CLI でログを見ている開発者が、同じエージェントループを共有したいからです。

しかも、途中で誰かがメッセージを送ったからといって、毎回エージェントを最初から再起動していては困ります。今ちょうどツールを呼び、情報を集め、作業を進めている loop の途中へ、新しい文脈を秩序立てて差し込みたい。そのためには「会話を持つストリーム」と「会話へ文脈を送る経路」を分ける必要があります。

Mastra の今回の発表は、まさにこの問題を正面から扱っています。

確かに、エージェントを「自分たちのチームの一員」として考えると、その方が自然ですよね。例えばチームメンバーの A さん。今朝リーダーから頼まれたタスクに取り組んでいますが、お昼にその件でサブリーダーから軌道修正を指示されるとか、普通ですよね。または夕方に同僚から割り込みのお願いをされたりとか。エージェントが「ひとりのユーザーのアシスタント」から「チームみんなの同僚」になると、「タスクの実行中にそれを割り当てたユーザとは別のメンバーと会話する」ことが当たり前にもとめられるのだ、と改めて気づかされます。

---

## Agent Signals とは何か

Signals は、thread を単位としてエージェントとやり取りする仕組みです。基本的な考え方は次の 3 段に分けると理解しやすいです。

1. `subscribeToThread()` で、ある thread の現在のストリームを購読する
2. `sendMessage()` や `queueMessage()` で、その thread に新しい入力を送る
3. `sendSignal()` や `sendNotificationSignal()` で、ユーザー入力ではない文脈や外部イベントを送る

このとき thread には `resourceId` と `threadId` があり、Mastra Memory がそのスレッド順序とアクティブ実行を管理します。エージェントがいま動いているなら、メッセージはその loop に取り込まれます。アイドルなら、新しい実行としてスレッドが起動します。

最小構成はかなり単純です。

```
const subscription = await agent.subscribeToThread({
  resourceId: "user_123",
  threadId: "thread_456",
});

await agent.sendMessage("Compare that with the previous option.", {
  resourceId: "user_123",
  threadId: "thread_456",
});

for await (const chunk of subscription.stream) {
  console.log(chunk);
}
```

ですが、面白いのはここから先です。Signals は単に「チャットを続ける API」ではなく、同じ thread に対して複数の種類の文脈を秩序立てて入れられるようにしています。

---

## 1. Messages: 実行中ループへ途中参加できる

最も分かりやすいのが `sendMessage()` と `queueMessage()` です。

### `sendMessage()` は「いま見てほしい」入力

```
await agent.sendMessage(
  {
    contents: "Use the latest customer note too.",
    attributes: { name: "Jane", sentFrom: "slack" },
  },
  { resourceId, threadId },
);
```

エージェントが動作中なら、そのメッセージは現在の loop へ入ります。止まっているなら、そのメッセージで thread が起動します。つまり「誰がストリームを最初に開いたか」とは無関係に、あとから会話へ入れるわけです。

### `queueMessage()` は「今のターンが終わってから見てほしい」入力

```
await agent.queueMessage("Also check whether the tests need updates.", {
  resourceId,
  threadId,
});
```

こちらは、現在のモデル呼び出しを邪魔せず、次ターンで確実に処理させたいときに使います。人間が 2 回連続で補足を送りたいときや、Active Run の途中で割り込むと逆に文脈を壊しそうなときに向いています。

### 何がうれしいのか

この差は地味に見えますが、実務ではかなり効きます。たとえばコーディングエージェントがテスト実行中に、Slack から PM が「今回は Postgres 版を優先してください」と言ったとします。そのとき、

* 即時に見せたいなら `sendMessage()`
* いまのテスト結果を受け取ってから扱わせたいなら `queueMessage()`

という制御ができます。これがないと、ユーザー入力のたびに run を abort してやり直す、という雑な実装になりがちです。

---

## 2. Multiplayer: 複数 UI と複数人間を前提にした thread 設計

Signals のもう 1 つの本質は multiplayer です。これは「1 つの thread を複数人が共有できる」という意味ですが、単なる閲覧共有ではありません。**誰がどこから何を送ったかをモデルに見せたまま、複数経路から介入できる** のがポイントです。

属性付きメッセージはモデル側では XML として見えます。

```
<user name="Jane" sentFrom="slack">Can you prioritize the Postgres version?</user>
```

これにより、モデルは「同じ thread に来た複数の入力」をただのテキスト列ではなく、送信者や送信経路付きのコンテキストとして解釈できます。

### 典型ユースケース

1. Web UI でオペレーターが進捗を見ている
2. Slack で現場担当が追加情報を投げる
3. モバイルでマネージャーが承認や優先順位変更を送る
4. CLI では開発者が内部ログを監視する

これらが同じ loop に接続されていても、モデルには「誰の発言か」が残ります。これは長時間エージェントでは特に重要です。複数人の入力が混ざると、発話内容だけでは責任や権限を判断できないからです。

### system prompt との相性

記事でも示唆されているとおり、実運用では system prompt 側に「`sentFrom=slack` は顧客対応チャネル」「`role=manager` の指示は優先度を上げる」など、属性の意味を補っておくとかなり安定します。Signals は属性を運ぶ器であり、どう解釈させるかは prompt design の仕事です。

---

## 3. Reactive Signals: 実行中のエージェントへ、その場で必要な指示を入れる

Reactive Signals は、processor がエージェントの挙動を見て、条件に応じて文脈を差し込む仕組みです。これはかなり重要です。なぜなら、エージェント開発の多くの失敗は「最初に全部説明しておけば大丈夫」という発想から起こるからです。

実際には、必要な指示は場面依存です。

* あるディレクトリに入ったときだけ `AGENTS.md` を読ませたい
* 危険なツールを呼ぶ直前だけ安全ポリシーを再通知したい
* 残り `maxSteps` が少なくなった瞬間だけ最終回答を促したい
* 2 つのツールを組み合わせるときだけ使い方の注意を入れたい

こういう指示を全部 system prompt に最初から詰め込むと、長くなり、ノイズになり、しかも必要な瞬間に薄まります。Reactive Signals は、それを「必要になった瞬間に送る」形へ変えます。

### 代表例: `AGENTS.md` の自動読込

Mastra が出している例は分かりやすく、エージェントがファイル操作をした結果から `AGENTS.md` の存在を検知し、その内容を system-reminder 的な形で差し込むものです。これにより、リポジトリごとのルールやサブディレクトリ固有の作法を、必要な場所に入ったタイミングでだけ読ませられます。

これはコーディングエージェントだけでなく、たとえば営業支援エージェントでも応用できます。商談相手の業界が判明した瞬間に業界別ガイドラインを入れる、金融商品が話題に出た瞬間にコンプラ指示を差し込む、といった設計が可能です。

Reactive Signals は「動的な注意喚起」を thread の正規コンテキストにする機能だと言えます。

---

## 4. State Signals: 頻繁に変わる状態を、prompt cache を壊さず持ち続ける

今回の発表で、個人的にいちばん重要なのはここです。

長時間エージェントでは、頻繁に変わる状態をモデルへ見せたい場面が多くあります。

* working memory
* ブラウザで今どのページを見ているか
* エディタでどのファイルを開いているか
* バックグラウンドジョブの進捗
* 現在のサブタスクの状態

従来はこの種の情報を dynamic system prompt へ毎回再構築して入れがちでした。しかしそれをやると、system prompt 更新のたびに prompt cache が invalidation され、長い run ほどコストとレイテンシが悪化します。

State Signals はこの問題を避けます。状態を thread 履歴の中の append-only な lane として扱い、

* 現在の完全状態は `snapshot`
* 変更分だけは `delta`

として入れていくからです。

### なぜこれが効くのか

State Signals の発想は、ソースコード管理に近いです。毎回全文を送り直さず、現在値と差分を管理することで、モデルへ見せる状態を保ちつつ重複送信を減らせます。Mastra は同じ `cacheKey` と `mode` の state signal を重複としてスキップするので、変更がないのに毎ターン同じ状態を流し込む必要もありません。

### working memory との接続

今回の発表に合わせて、Mastra は working memory を state signal として配信する experimental 機能も出しています。

```
const memory = new Memory({
  options: {
    workingMemory: {
      enabled: true,
      useStateSignals: true,
    },
  },
});
```

これが嬉しいのは、working memory が「system prompt の大きな塊」ではなく「履歴の中で更新される状態」として扱える点です。長い thread での prompt caching と相性がよく、途中の状態変化も audit trail 的に追いやすくなります。

### どういう場面で効くか

1. ブラウザエージェントがタブ状態や現在 URL を持ち回る
2. IDE エージェントがファイル編集中の局所状態を共有する
3. 業務エージェントが「今どこまで終わったか」を progress lane として持つ
4. 人間の設定や好みが run 中に変わっても、system prompt 全体を組み立て直さず追従する

これは単なる最適化ではなく、**長時間エージェントにおける状態管理の設計パターン**です。

---

## 5. Notification Signals: 外部イベントを inbox 化してエージェントへ届ける

Notification Signals は、GitHub、Slack、メール、CI、インシデント、会議録など、外の世界で起きた出来事をエージェントの thread に接続する仕組みです。

これが面白いのは、単純に「イベントが来たら全部エージェントへ渡す」作りではないことです。外部イベントはノイズが多いので、Mastra は通知をまず record として保存し、その後 delivery policy に従って、

* すぐ全文配信する
* 要約だけ先に渡す
* アイドル時まで遅延させる
* inbox に溜める
* 破棄する

といった判断をします。

### priority-aware な配送

Signals docs では、優先度ごとの既定動作も整理されています。たとえば `high` は要約をすぐ出しつつ、thread が idle になったら全文通知を届ける、`low` はすぐ起こさず後で要約だけ出す、といった具合です。これはかなり実務的です。

長時間動くエージェントにとって問題なのは「通知を受け取れないこと」ではなく、「どうでもいい通知で main loop が汚染されること」だからです。Notification Signals は、通知を文脈へ変換する前に、運用上の優先度と配送ポリシーを差し込む層を持っています。

### Mastra Code の GitHub Signals

Mastra Code では、Experimental GitHub Signals をオンにし、`/github subscribe` すると、チェックアウト中 PR に関するレビュー、承認、CI 状態、新規コメントなどを受け取れます。これは Notification Signals の分かりやすい実例です。

さらに、PR 関連コマンドを実行したときに「この PR は購読できる」と教える reactive signal も組み合わせています。つまり、

* 外部イベントを溜める Notification Signals
* その購読行動を発見可能にする Reactive Signals

が一緒に動いているわけです。ここが設計としてきれいです。

---

## Signals が効く代表的なユースケース

### 1. コーディングエージェントのマルチクライアント運用

IDE でコードを書かせつつ、Slack から PM が追加条件を送り、ブラウザ UI でレビュー担当が進捗を見る。従来ならストリーム配線や割り込み制御を自前で実装しがちでしたが、Signals なら thread ベースで統一できます。

### 2. サポート・運用エージェント

Web 管理画面、Slack、メールイベント、監視アラートが全部同じ案件 thread に紐づくケースです。urgent な通知だけ即時介入し、medium/low は inbox にまとめる、といった運用がしやすくなります。

### 3. 長時間のリサーチエージェント

数十分調査し続けるエージェントに対し、人間が途中で「この論点も調べて」「このソースは信用しないで」と差し込むケースです。`sendMessage()` と `queueMessage()` の使い分けで、run を壊さず進行を調整できます。

### 4. browser / editor / workflow state を持つ UI エージェント

今の URL、開いているタブ、選択中のファイル、バックグラウンドタスク進捗などを state signal として持てば、system prompt を毎回巨大化させずに現在状態を共有できます。

---

## 具体的な利用方法

### 最低限の始め方

必要条件は次のとおりです。

* `@mastra/core@1.39.0` 以降
* Mastra Memory を使うこと
* 単一サーバーならそのまま利用可
* 複数プロセスなら Pub/Sub を設定

まずは thread を subscribe し、そこへ message を送る構成から始めるのが最も分かりやすいです。

```
const subscription = await agent.subscribeToThread({ resourceId, threadId });

await agent.sendMessage("Continue with the next step.", {
  resourceId,
  threadId,
  ifIdle: {
    behavior: "wake",
    streamOptions: { maxSteps: 3 },
  },
});

await subscription.processDataStream({
  onChunk: chunk => console.log(chunk),
  reconnect: true,
});
```

Web クライアントを自作して SSE を張るなら、heartbeat を送って接続を維持するのも重要です。Signals docs でも、長寿命 subscription では keep-alive と reconnect を前提にしています。

### processor で reactive signal を送る

リポジトリルール、業務ルール、危険操作の注意など、「必要になった瞬間だけ見せたい文脈」は processor に寄せるのが自然です。

```
export const policyProcessor: Processor = {
  id: "policy-reminder",
  async processInputStep({ messageList, sendSignal }) {
    if (!shouldWarnAboutRisk(messageList)) return messageList;

    await sendSignal?.({
      type: "reactive",
      contents: "You are about to perform a high-risk action. Summarize the impact first.",
      attributes: { policy: "high-risk-write" },
    });

    return messageList;
  },
};
```

### state signal で頻繁に変わる状態を扱う

working memory 以外でも、browser state や editor state のように頻繁に変わる情報は state signal に向いています。ポイントは、

* snapshot をいつ出すか
* delta をどう表現するか
* `cacheKey` を何で安定化させるか

を producer 側で明示的に設計することです。ここは雑にやると重複送信や snapshot 再注入の乱発につながるので、導入時に一番設計力が問われます。

### notification inbox を与える

通知を読み、既読にし、検索し、整理させたいなら `createNotificationInboxTool()` を agent に持たせる構成が自然です。これにより、通知をただ受けるだけでなく、agent 自身が inbox を確認しに行けるようになります。サポートや運用エージェントではかなり相性が良いはずです。

---

## 導入時に気をつけたい点

### 1. これは「全部を streaming にする」話ではない

Signals はストリームを増やす機能ではありますが、本質は thread を単位としたコンテキスト秩序の管理です。単にイベント数を増やすだけでは、逆にノイズが増えます。どの入力を即時配信し、どれを queue し、どれを persist に逃がすかを決める必要があります。

### 2. 属性設計は雑にしない

`name` や `sentFrom` は分かりやすいですが、実運用では `role`、`channel`、`priority`、`delivery`、`source` などの意味論をかなり丁寧に設計した方がいいです。Attributes は自由度が高いぶん、曖昧な名前にするとモデル側の解釈もぶれます。

### 3. Notification は保存基盤も前提になる

通知 inbox を本格運用するなら、docs にあるとおり storage adapter 側の対応も見ておく必要があります。少なくとも notification workflows は、単なるその場の stream echo ではなく、保存・遅延・要約・再配送の設計が前提です。

### 4. API は alpha 扱い

Signals docs では、この機能は alpha とされています。大きな破壊的変更は major version を伴わず入る可能性があるので、いきなり核機能へベタ書きせず、アプリ側に薄いラッパーを置いておく方が安全です。

---

## 既存の Mastra 機能との位置づけ

今回の発表は単独機能に見えて、実際にはここ数か月の Mastra の流れとかなり綺麗につながっています。

* Memory: thread と resource を軸に、長い会話の状態を管理する
* Working Memory: 常に効く状態を持ち回る
* Background Tasks: 主ループとは別の遅い処理を扱う
* Browser / Workspace / Code 系機能: エージェントが長時間実作業する前提を強める

Signals は、その上に「実行中の loop へどう介入するか」を乗せたピースです。言い換えると、Mastra のエージェントが本格的に **stateful で、multiplayer で、外部イベントに反応する runtime** へ寄ってきた、ということでもあります。

とくに State Signals は、今後の context engineering を考えるうえで重要です。静的 prompt を最初に積んで終わり、ではなく、**必要な状態を必要な粒度で差分配信し続ける** 方向へ一歩進んだと見てよいでしょう。

---

## 他のフレームワークと比べると何が違うのか

ここで気になるのは、「こういう仕組みは Mastra だけなのか」という点です。結論から言うと、**近い能力を持つフレームワークはありますが、Mastra Signals ほど一つの抽象にまとまっている例はまだ少ない**です。

たとえば OpenAI Agents SDK には、streaming、tool approval、human-in-the-loop、RunState の保存と再開があります。つまり、実行中の agent run を一時停止し、人間の承認を挟み、同じ状態から再開することはできます。ただしこれは主に **run 単位の interruption と resume** の仕組みで、Mastra Signals のように thread を共有しながら複数クライアントが途中参加したり、reactive / state / notification を同じ系で扱ったりする設計とは少し違います。

LangGraph 系もかなり近い思想を持っています。durable execution、stateful graph、interrupt、human approval などは非常に強く、長時間エージェントの設計では有力です。ただし重心は thread runtime というより **workflow graph と state machine** にあります。Mastra が「会話スレッドへ途中で何を差し込むか」に寄っているのに対し、LangGraph は「どのノードで止まり、どの状態で再開するか」に寄っています。

Vercel AI SDK も、message persistence や resumable streams を備えていて、長時間の生成結果を複数クライアントで再接続しながら扱うことはできます。ただ、こちらは主に UI ストリーミング基盤と chat persistence が中心です。Mastra Signals のように、system-generated context の注入、state lane の snapshot / delta、notification inbox と delivery policy までをフレームワークの一級概念として束ねているわけではありません。

要するに、他のフレームワークにも「似た部品」はあります。ですが Mastra Signals の面白さは、それらをバラバラの機能としてではなく、**thread を中心にした agent runtime の基本操作**としてまとめた点にあります。とくに Reactive Signals、State Signals、Notification Signals まで同じ文脈で設計されているのは、かなり Mastra らしいところです。

---

## まとめ

Agent Signals は、表面的には `subscribeToThread()` や `sendMessage()` などの API 追加に見えます。ですが本質は、**長時間エージェントを「会話して終わり」の存在ではなく、共有され、途中で導かれ、外部世界へ反応し、状態を抱えながら動く runtime」に変えること**です。

今回の発表から読み取れるポイントは次のとおりです。

1. 長時間エージェントには、request/response より thread runtime が必要になっている
2. 文脈は最初に全部渡すのではなく、途中で差し込むべきものが多い
3. 頻繁に変わる状態は dynamic system prompt ではなく state lane として扱う方がよい
4. 外部イベントは単純に投げ込むのではなく、優先度・要約・inbox を伴う notification workflow にすべき

Mastra を使っていて「エージェントが長く動き始めると設計が急に難しくなる」と感じていた人には、今回の Agent Signals はかなり本質的なアップデートです。単なる新機能というより、これからの agent UX と agent runtime の基礎部品として見ておく価値があります。

---

## 関連リンク
