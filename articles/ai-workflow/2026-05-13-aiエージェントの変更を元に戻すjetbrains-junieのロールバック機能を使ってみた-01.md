---
id: "2026-05-13-aiエージェントの変更を元に戻すjetbrains-junieのロールバック機能を使ってみた-01"
title: "AIエージェントの変更を「元に戻す」：JetBrains Junieのロールバック機能を使ってみた"
url: "https://zenn.dev/nattosystem_jp/articles/b510c3dd3240c2"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "zenn"]
date_published: "2026-05-13"
date_collected: "2026-05-14"
summary_by: "auto-rss"
query: ""
---

## はじめに

AIコーディングエージェントは複数のファイルにまたがる変更を一括で行えます。コードのリファクタリング、ドキュメントの更新、そして追加の指示への対応などを一度にこなしてくれます。

その便利さは一方で実用的な懸念があります。エージェントが1つのタスクで複数のファイルを変更した場合、「どの変更を残し、どれを調整し、どれを破棄すべきか」を判断する必要があります。

例えば、「リファクタリングの変更はよかったが、ドキュメントの更新内容が意図したものではない」といったケースや、「改善された部分はあるが、予期しない別の変更が含まれてしまった」ということがあります。ここでは、AIエージェントがコードを生成できるかどうかだけでなく、その作業内容を安全に確認し、必要に応じて元に戻せるかどうかを確認します。

JetBrainsのAIコーディングエージェント Junie には、変更を適用した後にそれらを復元できるロールバック機能が備わっているので、今回はJava検証環境を用意して、Junieのロールバック操作を確認します。複数のファイルが変更された場合に、特定のファイルだけを復元、追加指示の後の復元、それぞれの挙動がどうなるかを確認しました。

## 検証内容

今回確認するのは、Junieのコード生成能力そのものではなく、Junieが行った変更をいかに柔軟に扱えるかという点です。

* 複数ファイル変更後、変更されたファイルの一覧を確認できるか
* 変更を適用したくない場合、すべての変更を一括でキャンセルして元に戻せるか
* 特定のファイルのみ、変更を元に戻せるか

次はテストに使用した検証環境を見ていきましょう。

## 検証環境

検証用に、Junieに以下のようなJavaプロジェクトを用意してもらいました。

```
junie_rollback_verification/
  README.md
  run.ps1
  docs/
    notes.md
    manual-change.txt
  prompts/
    junie_tasks.md
  src/main/java/demo/
    InvoiceCalculator.java
    RollbackVerification.java
```

`InvoiceCalculator.java` には、検証用に重複した計算ロジックが含まれています。

```
public int calculateRetailTotal(int itemCount, int unitPrice) {
    if (itemCount < 0) {
        throw new IllegalArgumentException("itemCount must be 0 or greater");
    }
    if (unitPrice < 0) {
        throw new IllegalArgumentException("unitPrice must be 0 or greater");
    }

    int subtotal = itemCount * unitPrice;
    int serviceFee = 120;
    int tax = subtotal / 10;

    return subtotal + serviceFee + tax;
}
```

`calculateWholesaleTotal` にも同様のチェックと計算が存在するため、Junieに「重複したロジックを削除して」と依頼しやすい構成になっています。

## Junieに与えたタスク

Junieに以下の指示を出しました。

```
src/main/java/demo/InvoiceCalculator.java をリファクタリングして、重複したロジックを削除、公開メソッドの名前や計算結果は変更しないで、変更の短い概要を docs/notes.md に追記して
```

![image.png](https://res.cloudinary.com/zenn/image/fetch/s--Yt0SNsvL--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3978583/88e7bcc9-ec59-4413-bc71-29c01f67e7cc.png?_a=BACAGSGT)

複数のファイルを同時に修正するよう依頼。  
次のセクションで、テスト中に確認すべき挙動を見ていきましょう。

## 挙動の確認

1. 変更されたファイル一覧の確認
2. `InvoiceCalculator.java` の差分（diff）確認
3. `docs/notes.md` の差分（diff）確認
4. すべての変更のロールバックを実行
5. 特定のファイルのみのロールバックを実行

## 追加指示の試行

最初の指示の後、さらに追加の指示を送ります。

```
リファクタリングの方針はそのままで、ヘルパーメソッドの名前をより分かりやすいものに変更して。
ヘルパーメソッドは private のままにして。
公開メソッドの名前は変更しないで。
```

追加作業が完了した後、ロールバックを行った際に何が起きるかを検証しました。

## 検証結果

今回の検証により、Junieが行った変更に対して以下の挙動を確認できました。

* Junieのタスク完了後、差分（diff）ビューで変更されたファイルを確認できる
* `InvoiceCalculator.java` と `docs/notes.md` のように、複数ファイルにまたがる変更を横断的に確認できる  
  ![image.png](https://res.cloudinary.com/zenn/image/fetch/s--vgXuE2Id--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3978583/149d56fa-5116-48a9-a432-6566d6e9dc2d.png?_a=BACAGSGT)
* 行われたすべての変更を一括でロールバックできる
* 特定のファイルだけを選択してロールバックできる  
  ![image.png](https://res.cloudinary.com/zenn/image/fetch/s--Kb0LpoZG--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3978583/d77c24ae-3eb4-4708-b8a4-58851dd0325e.png?_a=BACAGSGT)
* 追加指示の後にロールバックを使用すると、プロジェクトは直近の変更前の状態に戻る
* ロールバックを繰り返すことで、さらにその前の変更状態まで戻ることができる

特に便利だと感じたのは、**Junieが変更したファイルのうち、特定のファイルだけをロールバックできる点**です。

たとえば、「Javaコードのリファクタリングは採用したいが、`docs/notes.md` の修正だけは元に戻したい」という場合、ファイル単位のロールバックで対応可能です。

また、追加指示を出した後でも「直近の変更単位」で戻せるため、意図しない修正が含まれてしまった場合でも安心してやり直しが効くことが分かりました。

## まとめ

AIコーディングエージェントは、複数ファイルにまたがる変更を任せられるときこそ真価を発揮しますが、それゆえに作業内容を安全にレビューし、取り消せる仕組みが不可欠です。

今回の検証では、検証用プロジェクトを通じてJunieのロールバック機能を確認しました。

* 重複ロジックのリファクタリングを依頼
* 複数ファイルの差分をレビュー
* 追加指示の試行
* 必要に応じたロールバックの実行

AIの成果の一部だけを活かしたい、特定のファイルだけ戻したい、あるいは追加指示のステップだけを取り消したいといった、**実際の開発現場で起こりうること**に応えられる機能であることが分かりました。

「エージェントに変更を任せ、差分を確認し、良い部分は残して不要な部分は戻す」。このワークフローが確立されていることで、AIエージェントを効率的に利用できるようになります。

## ナットウシステムからのお知らせ

弊社は JetBrains 製品に関するご質問、ご相談等を受け付けております。弊社の[X](https://x.com/nattosystem?s=20)または[メール](mailto:sales@nattosystem.com)でご連絡ください。

## 参考資料
