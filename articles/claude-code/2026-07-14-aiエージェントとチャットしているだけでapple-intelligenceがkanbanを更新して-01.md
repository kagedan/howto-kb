---
id: "2026-07-14-aiエージェントとチャットしているだけでapple-intelligenceがkanbanを更新して-01"
title: "AIエージェントとチャットしているだけでApple IntelligenceがKanbanを更新してくれるmacOSアプリを作った"
url: "https://zenn.dev/iloli/articles/apple-intelligence-kanban-reconciler"
source: "zenn"
category: "claude-code"
tags: ["CLAUDE-md", "AI-agent", "LLM", "zenn"]
date_published: "2026-07-14"
date_collected: "2026-07-15"
summary_by: "auto-rss"
query: ""
---

自分はタスク管理が全然できません。

やることを思いついていないわけではありません。むしろ逆で、AIと話しているうちに「あれも直したい」「ここまで調べよう」と作業が始まり、そのまま集中してしまいます。

問題は、その前にKanbanを開いてカードを作る工程が挟まるのが辛いんです。

```
AIと相談する
    ↓
作業が始まる
    ↓
集中する
    ↓
カードを作るのを忘れる
```

作業を止めてタスク管理へ戻るのではなく、AIと作業を始めた時点で勝手にカードが作られてほしい。すでに同じカードがあるなら、新規作成せず会話をそこへ紐付けてほしい。  
怠惰すぎると言われるかもしれないですが、仕事でもなく自分個人のためのタスク管理は極限までストレスや摩擦を減らしたい、みんなもそうっすよね？

AIと話し始めたらそのまま会話を止めずにKanbanの方が追いかけてくる体験を目指したい。

そこで、個人開発しているmacOSアプリに、AIとの会話とKanbanを自動で照合するBoard Reconcilerを実装しました。

![会話からKanbanへ反映するBoard Reconciler](https://static.zenn.studio/user-upload/deployed-images/06d1e1b1921b442c923e6d83.png?sha=a4a052b7e7c1a1a65358037d67296b8e0a5a5c6a)

*右側の会話から作業を検出し、左側のカード作成と会話への紐付けを行います。*

Appleの[Foundation Models framework](https://developer.apple.com/documentation/FoundationModels)を使い、会話が一区切りするたびに次のどれかを判定します。

```
何もしない
新しいタスクを作る
既存のタスクへ会話を紐付ける
```

Foundation ModelsはApple Intelligenceの中核にあるオンデバイスモデルへSwiftからアクセスでき、`@Generable`と`@Guide`を使った構造化出力を利用できます。

ただし、モデルへKanbanの更新権限をそのまま渡したわけではありません。

この記事では、実機で遭遇した二つの誤判定と、モデルに曖昧な意味判断だけを任せるために設けた境界について書きます。

## Board Reconcilerが動くタイミング

対象は、まだタスクへ紐付いていないAI会話です。

ACPセッションのturnが正常終了したとき、次の条件を確認します。

* Board Reconcilerが設定で有効
* セッションが既存タスクへ未割り当て
* 前回の照合以降に新しい発言がある
* ユーザーとAgentの両方の発言がある
* Foundation Modelsが利用可能

入力するのは、前回照合以降の差分会話と、現在のKanbanにある未完了カードです。

```
前回までの会話
──────────────
lastBoardReconcileMessageID
──────────────
今回のユーザー発言
今回のAgent発言      ← モデルへ渡す
```

会話履歴全体を毎回渡さないのは、オンデバイスモデルのコンテキストを節約し、過去の別話題に引っ張られにくくするためです。

カードも未完了のものだけを、最大30件の番号付きリストにします。

```
1. [BACKLOG] オンボーディングを改善する
2. [DOING] 設定画面のテーマ切り替えを実装する
3. [REVIEW] CSVエクスポートを確認する
```

## モデルの出力を三種類に限定する

モデルから受け取る構造は、概略として次の形です。

```
@Generable
struct GeneratedBoardReconcileDecision {
    @Guide(description: "ユーザーが作業を依頼した場合だけtrue")
    var userRequestedWork: Bool

    @Guide(
        description: "実行する操作",
        .anyOf(["none", "create", "attach"])
    )
    var operation: String

    @Guide(description: "createの場合だけ使うタイトル")
    var title: String

    @Guide(description: "createの場合だけ使う説明")
    var taskDescription: String

    @Guide(description: "attach先のカード番号")
    var existingTaskNumber: Int

    @Guide(description: "実作業が始まっている場合だけtrue")
    var workHasStarted: Bool
}
```

操作は`none`、`create`、`attach`の三種類だけです。

### none

質問、雑談、説明、すでにKanbanへ反映済みで変更が不要な会話なら何もしません。

### create

具体的な作業依頼があり、既存カードのどれにも該当しない場合は、新しいカードを作ります。

### attach

会話が既存カード一件の作業だと明確な場合は、そのカードへセッションを紐付けます。

さらに、ファイル編集やコマンド実行など、実作業を始めた証拠があれば`workHasStarted`を`true`にできます。

計画や「これから対応します」という約束だけでは開始扱いにしません。

## 実機では、空のKanbanにもattachしようとした

構造化出力にすれば、それだけで意味まで正しくなるわけではありません。

実機で試すと、空のKanbanなのに次のような出力を返し続けることがありました。

```
{
  "operation": "attach",
  "existingTaskNumber": 0
}
```

カードが一件もないので、`attach`できるはずがありません。

対策は二重にしました。

まず、空のKanbanでは`attach`を選べないことをプロンプトへ明記します。

```
The board is empty, so attach is not available.
Choose create or none.
```

それでもモデル出力は信用せず、Converterで番号の範囲を検証します。

```
guard existingTaskNumber >= 1,
      existingTaskNumber <= cards.count else {
    return nil
}
```

0や範囲外を返した場合、操作は何も起こりません。

## 雑談から架空タスクを作ろうとした

もう一つ実機で起きたのが、作業依頼ではない会話から架空のタスクを`create`する偽陽性です。

プロンプトで「雑談や質問はnone」と書くだけでは十分ではありませんでした。

そこで、`operation`より前に`userRequestedWork`を生成させています。

```
@Guide(description: "ユーザーが変更、修正、実装、調査を依頼した場合だけtrue")
var userRequestedWork: Bool
```

そして、モデルが`operation = create`を返しても、Converter側で再度止めます。

```
guard userRequestedWork else {
    return nil
}
```

```
userRequestedWork == false
        +
operation == create
        =
何もしない
```

モデルへ一度考えさせたから安全、とはしません。同じ意味の境界を通常のコードでも適用します。

## LLMにUUIDを選ばせない

既存カードへ会話を紐付けるとき、モデルにUUIDを返させる設計にはしませんでした。

```
{
  "operation": "attach",
  "taskID": "E51D0B5A-..."
}
```

UUIDはアプリ内では便利ですが、小型モデルにとって意味のある文字列ではありません。

一文字間違える、存在しないIDを生成する、別のIDを返すといった失敗を考慮する必要があります。

そこで、モデルには番号だけを返させます。

```
{
  "operation": "attach",
  "existingTaskNumber": 2,
  "workHasStarted": true
}
```

番号を入力配列の範囲内で検証し、アプリ側でUUIDへ変換します。

```
let taskID = cards[existingTaskNumber - 1].id
```

モデルは「どのカードに意味が近いか」を判断します。

識別子の解決は、入力したデータを持っているアプリが行います。

## 生成開始時にマーカーを進める

Board Reconcilerは非同期で動くため、モデルの応答を待っている間に同じturnをもう一度処理しないようにする必要があります。

モデル生成を始める前に、対象の最終メッセージIDを記録します。

```
session.lastBoardReconcileMessageID = lastMessageID
```

生成完了後ではなく、開始前に進めるのがポイントです。

これにより、同じ会話に対するReconcileが並行して複数起動することを防ぎます。

生成に失敗した場合、そのturnは自動再処理しません。Board Reconcilerは重要データを確定する処理ではなく、ベストエフォートの補助機能だからです。

モデルが利用できない、コンテキストが長すぎる、出力を変換できないといった場合も、UI上は何も起こりません。手動でカードを作る通常操作はそのまま使えます。

## 人間の操作を優先する

モデルが生成している間に、ユーザーが手動で会話をカードへ紐付ける可能性があります。

生成開始時には未割り当てでも、適用時には状況が変わっているかもしれません。

そのため、判定を適用する直前にもう一度確認します。

```
guard session.assignedTaskID == nil else {
    return
}
```

人間が先に操作していれば、モデルの判定を破棄します。

カードをDOINGへ移動するときも、生成開始時の情報を無条件に適用せず、更新日時を使った楽観ロックで競合を検出します。

生成AIの非同期処理では、「入力時の状態が、出力適用時にも正しい」とは限りません。

## AIにDONEを触らせない

Board Reconcilerが実行できるのは、次の操作までです。

```
新規カードをBACKLOGへ作る
既存カードへ会話を紐付ける
作業開始の証拠があればDOINGへ移す
```

タスクをDONEへ移すことはできません。

会話の中でAgentが「完了しました」と言っても、それは完了の証拠にはならないためです。

```
モデルに任せる
    会話は作業依頼か
    どの既存カードに近いか
    実作業が始まったか
    新規カードの短い文言

通常のコードで決める
    UUIDの解決
    保存先Project
    レーン
    重複防止
    競合解決
    DONE禁止
    モデル利用可否
```

曖昧な意味判断と、権限を伴う状態変更の境界を分けています。

## まとめ

当初の目的であったAIとの会話を止めずにKanbanの方が追いかけてくる体験と、AI  
セッションとタスクの紐付けは上手くいっておりかなり満足です。

そもそもCLAUDE.mdなどでタスク管理をワークフローに組み込むという手段もあると思うのですが、今回このような手段を選んだのは、あくまで人間のためのタスク管理・ビジュアル化に無駄なトークンを使いたくなかったからです。  
また、Apple Intelligenceのオンデバイスモデルを活用してみたかったという理由もありました。

面白いと思って下さった方は是非この記事を参考にして、管理のために手を止めない作業体験を確立してみてください。
