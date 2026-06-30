---
id: "2026-06-30-junie-cli-plan-mode-で実装まえに変更計画書を作ってもらいました-01"
title: "Junie CLI Plan mode で実装まえに変更計画書を作ってもらいました"
url: "https://zenn.dev/nattosystem_jp/articles/3a2e91a9923ff9"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "AI-agent", "zenn"]
date_published: "2026-06-30"
date_collected: "2026-07-01"
summary_by: "auto-rss"
query: ""
---

## はじめに

Junie がベータ版を終了し、正式版（GA）になりました。

今回は前回に引き続き、公式発表の中であった、Advanced Plan mode についてです。

<https://blog.jetbrains.com/junie/2026/06/junie-coding-agent-out-of-beta/>

AI コーディングエージェントを使っていていきなり実装に入って困ったことはありませんか。

まだ確認していないのに、エージェントが自信満々にコードを書き始めてしまうと、あとから差分を見て「そこではない」と気づくことがあります。

公式記事によるとAdvanced Plan mode は、Junie は plan 計画書を作り、それを確認してから実装をすることができるそうです。  
Plan mode に入るには `Shift+Tab`、生成された plan を開くには `Ctrl+P`、実装に進むには `Confirm` を押す、という流れが紹介されています。

また、plan は単なるチャット上の返答ではなく、`.junie/plans` 配下に残るドキュメントとして扱われます。

今回の記事では、この Advanced Plan mode を `spring-demo-project` のバグ修正で試しました。

前回は、同じ `spring-demo-project` を題材に Junie CLI の Debug mode を試しました。

前回は原因を調べていただきましたが、 今回は、「原因がわかったあと、実装前に修正方針」を Plan mode で試します。

それではみていきましょう！

## 題材にした問題

題材は、注文を作成する `OrderService#createOrder` です。

元の実装では、注文 ID に `System.currentTimeMillis()` を使っていました。

```
public Order createOrder(Long userId, BigDecimal amount) {
    long id = System.currentTimeMillis();
    Order order = new Order(id, userId, amount);
    Order saved = orderRepository.save(order);
    System.out.println("[order created] id=" + saved.getId() + ", userId=" + userId);
    return saved;
}
```

保存先は、`Long` の ID をキーにした `Map` です。

```
@Repository
public class OrderRepository {

    private final Map<Long, Order> store = new HashMap<>();

    public Order save(Order order) {
        store.put(order.getId(), order);
        return order;
    }

    public Optional<Order> findById(Long id) {
        return Optional.ofNullable(store.get(id));
    }
}
```

この組み合わせだと、短時間に複数の注文を作ったとき、同じミリ秒になって同じ ID が作られる可能性があります。

`Map` は同じキーが来ると後から来た値で上書きするので、注文が消えたように見える原因になります。

## Plan mode に渡したプロンプト

今回は、Plan mode に入った状態で以下のプロンプトを渡しました。

```
spring-demo-project の OrderService#createOrder で使っている System.currentTimeMillis() ベースの注文 ID 採番を見直したいです。

短時間に複数注文を作ると ID が衝突し、OrderRepository の Map で既存注文が上書きされる可能性があります。

この問題を最小限の変更で安定した ID 採番に修正する計画を立ててください。
```

変更対象ファイルやテスト方針は、こちらから指定していません。

最小限の変更で安定した ID 採番にしたい、というゴールだけを伝えました。  
![ezgif-703cac91717526d8.gif](https://res.cloudinary.com/zenn/image/fetch/s--A3qZLTEy--/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3978583/4650836b-28a8-4c5a-bc26-cf476e2ed81c.gif?_a=BACMTiAE)

## 生成された plan

Junie は `.junie/plans/fix-order-id-generation.md` を作成しました。

生成された plan には、次のような構成がありました。

* `Requirements`
* `Technical Design`
* `Delivery Steps`  
  ![image.png](https://res.cloudinary.com/zenn/image/fetch/s--jCUAwhS2--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3978583/8d5d6b57-bb20-4f86-a516-655a0687bdb1.png?_a=BACMTiAE)

内容としては、現在の問題を次のように整理していました。

* `OrderService#createOrder` が `System.currentTimeMillis()` で ID を生成している
* 同じミリ秒に複数注文を作ると、同じ ID になる可能性がある
* `OrderRepository` は `HashMap<Long, Order>` で保存しているため、同じ ID の注文が上書きされる
* `Long` の ID 型は維持する
* UUID、DB、外部 ID 採番サービスは導入しない

修正方針としては、`AtomicLong` を使う案が選ばれていました。

```
**ID Generation Approach:** Use an `AtomicLong` initialized with `System.currentTimeMillis()`. Calling `incrementAndGet()` guarantees unique IDs even during concurrent requests, requiring no changes to the `Order` model or `Long` ID type.
```

また、`OrderRepository` についても、`HashMap` から `ConcurrentHashMap` に変更する方針が入っていました。

これは、こちらのプロンプトでは明示していません。

ID 衝突だけでなく、短時間・並行アクセスという文脈から、保存先のスレッドセーフ性まで含めて計画に入れてきたようです。

## Confirm and Implement してみた

そのまま Confirm and Implement しました。

実装後、Junie は次のように報告しました。

```
Summary
• Implemented thread-safe and collision-free order ID generation as requested in the plan.
• Upgraded the in-memory order store to handle concurrent accesses securely.

Changes
• Updated OrderService to use AtomicLong for generating strictly monotonically increasing IDs, preventing ID conflicts when orders are created within the same millisecond.
• Changed HashMap to ConcurrentHashMap in OrderRepository to prevent data loss or concurrent modification exceptions under heavy concurrent operations.

Verification
• Project compilation validated via JetBrains builder mcp_jetbrains_build_project.
• Did not run automated tests because mvn and mvnw were not found in the environment.
```

![image.png](https://res.cloudinary.com/zenn/image/fetch/s--dL2KIINY--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3978583/db20856f-cf51-4072-94d8-6af234696d02.png?_a=BACMTiAE)

変更されたファイルは次の3つです。

* `src/main/java/com/example/order/OrderService.java`
* `src/main/java/com/example/order/OrderRepository.java`
* `.junie/plans/fix-order-id-generation.md`

最後の plan ファイルは、実装後に Delivery Step が完了状態へ更新されていました。

```
### ✓ Step 1: Implement thread-safe ID generation in OrderService
...
### ✓ Step 2: Ensure thread safety in OrderRepository
...
```

plan が単なるチャット上の返答ではなく、実装後にも状態が更新されるドキュメントとして扱われているのが分かります。

## 実装された内容

`OrderService` は、`AtomicLong` を持つ形に変わりました。

```
private final AtomicLong idGenerator = new AtomicLong(System.currentTimeMillis());

public Order createOrder(Long userId, BigDecimal amount) {
    long id = idGenerator.incrementAndGet();
    Order order = new Order(id, userId, amount);
    Order saved = orderRepository.save(order);
    System.out.println("[order created] id=" + saved.getId() + ", userId=" + userId);
    return saved;
}
```

これにより、同じミリ秒に複数回 `createOrder` が呼ばれても、`incrementAndGet()` によって ID は単調増加します。

`OrderRepository` は、`ConcurrentHashMap` を使うように変更されました。

```
@Repository
public class OrderRepository {

    private final Map<Long, Order> store = new ConcurrentHashMap<>();

    public Order save(Order order) {
        store.put(order.getId(), order);
        return order;
    }

    public Optional<Order> findById(Long id) {
        return Optional.ofNullable(store.get(id));
    }
}
```

今回のデモプロジェクトでは、DB や外部 ID 採番サービスを入れるほどの規模ではありません。

そのため、`Long` ID を維持したまま、最小限の変更で衝突を避ける方針としては自然です。

## テストはどうなったか

Junie は実装後に JetBrains builder でコンパイル確認を行いました。

一方で、JUnit の自動テストは実行されませんでした。

理由は、Junie の実行環境で `mvn` と `mvnw` が見つからなかったためです。

このプロジェクトには `pom.xml` はありますが、Maven Wrapper の `mvnw` / `mvnw.cmd` はありませんでした。

つまり、Junie の報告は、

> Maven 用のテストコマンドを実行する手段が CLI 環境になかったので、`mvn test` は実行できなかった。

また、今回の plan には `Testing Strategy` の独立したセクションはありませんでした。

こちらのプロンプトでも、テスト追加やテスト実行は明示していません。

そのため、Junie は plan に書かれていた実装ステップを完了し、コンパイル確認まで行って完了にしました。

テスト追加や検証方針まで確実に含めたい場合は、最初の依頼か plan のレビュー時点で明示したほうがよさそうです。

## 試してわかったこと

今回、Plan mode で良かったのは、実装前に修正方針を確認できたことです。

通常のチャットでは、エージェントはそのまま実装に入るかもしれません。

Plan mode では、まず `.junie/plans/fix-order-id-generation.md` が作られました。

その中で、次の判断を実装前に確認できました。 この時点で違和感があれば、実装前に plan を編集できます。

## 改善したこと

Junie CLI Plan mode を使って改善したと感じたのは、

* **実装前に方針をレビューできる**  
  コードが変更される前に、設計判断や変更範囲を確認できます。
* **計画がファイルとして残る**  
  `.junie/plans` 配下に Markdown として残るため、あとから「何を合意して実装したか」を追えます。
* **Confirm 後の実装が plan に沿って進む**  
  今回は plan に書かれた `AtomicLong` と `ConcurrentHashMap` の変更が、そのまま実装されました。

## まとめ

`spring-demo-project` の `OrderService#createOrder` を題材に、Junie CLI の Plan mode を試しました。

今回の依頼はかなり短いものでしたが、それでも Junie は `.junie/plans` に計画を作成し、Implement 後に plan どおりの実装を行い、plan のステップも完了状態に更新しました。

Plan mode は、実装前の合意点をファイルとして見える化ができます。

少ないプロンプトでも、修正方針のたたき台は十分に出てきます。

そこにテスト方針や制約を加えてから Confirm できるのが、Plan mode の実用的な使いどころだと感じました。

## ナットウシステムからのお知らせ

弊社は JetBrains 製品に関するご質問、ご相談等を受け付けております。弊社の[X](https://x.com/nattosystem?s=20)または[メール](mailto:sales@nattosystem.com)でご連絡ください。

## 参考

<https://blog.jetbrains.com/junie/2026/06/junie-coding-agent-out-of-beta/>

<https://junie.jetbrains.com/docs/junie-cli-plan-mode.html>
