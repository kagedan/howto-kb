---
id: "2026-06-26-jetbrains-ai-chat-に-ui-からコンテキストを追加してみた-01"
title: "JetBrains AI Chat に UI からコンテキストを追加してみた"
url: "https://zenn.dev/nattogohan/articles/203144f648e63e"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-06-26"
date_collected: "2026-06-27"
summary_by: "auto-rss"
query: ""
---

## はじめに

Junie がベータ版を終了し、正式版になりました。

Junie は JetBrains が提供する AI コーディングエージェント。JetBrains IDE や CLI から使えます。  
公式発表の中でJunie 一般提供開始に伴って行われた変更のなかで、Junie CLI の Debug mode に焦点をあてます。

<https://blog.jetbrains.com/junie/2026/06/junie-coding-agent-out-of-beta/>

この記事では、Junie CLI の Debug modeを使ってみて **「たまに落ちるテスト」の調査がどう改善したか** を書きます。

## Junie の Debug mode

このリポジトリにある `spring-demo-project` です。Spring Boot の注文処理アプリで、`OrderService`、`OrderRepository`、`OrderServiceTest` などがあります。注文を作る処理です。

```
public Order createOrder(Long userId, BigDecimal amount) {
    long id = System.currentTimeMillis();
    Order order = new Order(id, userId, amount);
    Order saved = orderRepository.save(order);
    System.out.println("[order created] id=" + saved.getId() + ", userId=" + userId);
    return saved;
}
```

注文 ID に `System.currentTimeMillis()` を使っています。これは現在時刻をミリ秒で返す Java のメソッドです。

保存先は `OrderRepository` です。

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

この組み合わせだと、短い時間に2つの注文を作ったとき、同じミリ秒になって同じ ID が作られる可能性があります。`Map` は同じキーが来ると後から来た値で上書きするので、テストがたまに落ちる原因になりそうです。

ただし、コードを読んだだけでは「本当に同じミリ秒になっている」とは言い切れません。実行中の `id` の値や、保存先の状態を見ないと判断できません。

flaky なテストでは、

* ログを足しても同じ状態が再現するとは限らない
* 再実行すると通ってしまうことがある
* 調査用のログをあとで消す必要がある
* どこにログを足すべきかを先に自分で決めないといけない

> **flaky テストとは**  
> 同じコードに対して、実行するたびに成功したり失敗したりと、結果が安定しないテストのこと。コードのバグだけでなく、時刻・実行順序・並行処理・外部サービスなど「実行時の状況」に左右されて起きることが多い。失敗が毎回は再現しないため、原因の特定が難しいのが特徴です。今回のように `System.currentTimeMillis()` で ID を採番していると、たまたま同じミリ秒になったときだけ衝突して落ちる、という flaky な挙動になります。

## 実際に使ってみた

こちらからは、次のように、対象と「何を確認してほしいか」を伝えました。

```
OrderService#createOrder の注文 ID が System.currentTimeMillis() のせいで衝突しうるのかを、
デバッガで突き止めてください。
OrderServiceTest を実行し、createOrder の id と OrderRepository の store の状態を見て、
同じ id が上書きされうるかを、実際の値を根拠に説明してください。
```

どこにブレークポイントを置くか、どうステップ実行するか、どの式をどう評価するかは Junie に任せました。

## 手順

1. IntelliJ IDEA で `spring-demo-project` を開く
2. `src/test/java/com/example/order/OrderServiceTest.java` を開く
3. Junie CLI を 起動
4. Junie CLI で Debug mode に切り替える

５. Junie に、調査したいことを伝える

```
OrderService#createOrder の注文 ID が System.currentTimeMillis() のせいで衝突しうるのかを、
デバッガで突き止めてください。
OrderServiceTest を実行し、createOrder の id と OrderRepository の store の状態を見て、
同じ id が上書きされうるかを、実際の値を根拠に説明してください。
```

今回はこの1回の依頼だけで、Junie がブレークポイントの設定からデバッグ実行、値の確認までを通しでやってくれました。  
![ezgif-855c798963288dbf.gif](https://res.cloudinary.com/zenn/image/fetch/s--1VADxFBS--/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3978583/f6d47df0-2e91-40e0-81d7-0f4fd0e982b7.gif?_a=BACMTiAE)

## 実際に確認できたこと

Junie は自分でブレークポイントを置き、`OrderServiceTest` をデバッグ実行して、次のことを実行中の値で示してくれました。  
![image.png](https://res.cloudinary.com/zenn/image/fetch/s--b6Ya67EZ--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3978583/26a972cb-a22e-4cf8-873b-2803e4af19f9.png?_a=BACMTiAE)

* 注文 ID `1782278540214` で作られた注文（`Order@2287`）を保存する直前に、同じ ID のダミー注文（`Order@2496`）をあらかじめ保存させた
* ステップ実行で `store` の中身を確認すると、サイズは `1` のままで、値が `Order@2496` から `Order@2287` へ上書きされた
* さらに停止中のフレームで `System.currentTimeMillis()` を100回連続で評価したところ、戻り値はすべて同じ値（distinct count = 1）だった

「同じミリ秒で同じ ID が作られ、`Map` の同じキーが上書きされる」という、コードを読んだだけでは断定できなかったことが、実行中の値として確認できました。

特に、`println` では難しい次のような操作を、止まっている状態のまま進められたのがよかったです。

* 100回連続で現在時刻を評価して、衝突しやすさを数値で確かめる
* 保存される直前に同じ ID の注文を差し込んで、上書きが起きる瞬間を再現する

## 停止中の状態から追加で確認できるようになった

flaky テストでは、同じ失敗状態が何度も再現するとは限りません。

だから、実行が止まったタイミングで、追加で確認できるのがよかったです。

たとえば、Junie に次のように聞けます。

```
今の注文 ID と、保存先に同じ ID の注文があるかを確認してください。
```

```
この処理がどのテストから呼ばれたかも確認してください。
```

ログを追加する方法だと、こういう確認をするたびにコードを変えて再実行する必要があります。Debug mode では、止まっている状態を使ってそのまま次の確認に進めます。

## 調査と修正を分けやすくなった

Debug mode では、まず実行中の状態を見て原因を確認します。今回なら、見るべきポイントは次のようなものです。

* `id` にどんな値が入っているか
* 同じ ID が保存先に存在するか
* どのテストから `createOrder` が呼ばれているか
* 保存時に上書きが起きそうか

原因が見えたあとで、通常モードに戻して修正を依頼します。

## 改善したこと

Junie CLI Debug mode で特に改善したのは、

* **ログを増やす前に実行中の値を見られる**  
  `println` を足して再現待ちする前に、止まっている状態の変数や保存先を確認できます。
* **細かいデバッグ操作を自分で決めなくてよい**  
  評価する式や確認する値を最初から全部決めなくても、Junie に目的から調査を組み立ててもらえます。
* **調査と修正を分けやすい**  
  まず Debug mode で原因を確認し、原因が見えてから通常モードで修正に進めます。

## まとめ

`spring-demo-project` の `OrderService` を題材に、Junie CLI Debug mode で flaky テスト調査の流れがどう変わったかを書きました。

対象と確認してほしい値を伝えるだけで、Junie が停止位置や式を自分で組み立てて、実行中の状態を見ながら調査を進めてくれます。

Debug mode で「まず実行中の値を見てもらう」という使い方は、かなり実用的だと感じました。

## ナットウシステムからのお知らせ

弊社は JetBrains 製品に関するご質問、ご相談等を受け付けております。弊社の[X](https://x.com/nattosystem?s=20)または[メール](mailto:sales@nattosystem.com)でご連絡ください。

## 参考

<https://blog.jetbrains.com/junie/2026/06/junie-coding-agent-out-of-beta/>

<https://junie.jetbrains.com/docs/junie-cli-debug-mode.html>
