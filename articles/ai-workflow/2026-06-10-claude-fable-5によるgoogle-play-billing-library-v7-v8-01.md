---
id: "2026-06-10-claude-fable-5によるgoogle-play-billing-library-v7-v8-01"
title: "Claude Fable 5による、Google Play Billing Library v7 → v8.3.0 移行・テスト内容の作成"
url: "https://zenn.dev/biwacoder/articles/16e7640cbf237f"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-06-10"
date_collected: "2026-06-11"
summary_by: "auto-rss"
query: ""
---

# Google Play Billing Library v7 → v8.3.0 移行・テストドキュメント

## 0. 前提・スケジュール

* PBL v7 のサポート期限は **2026年8月31日**(Play Console から延長申請をすれば 11月1日まで猶予あり)。期限後は v7 のままだと新規リリースが警告/ブロック対象になる。
* 2026年5月19日に **PBL 9.0.0 がリリース済み**。今回 8.3.0 に上げておけば v8 系のサポートは 2027年8月31日まで。

---

## 1. v7 → v8 の破壊的変更(必須対応)

### 1-1. SkuDetails 系 API の完全削除

v5 以降 deprecated だったものが v8 で**クラスごと削除**。コンパイルが通らなくなるため漏れは機械的に検出可能。

| 削除された API | 置き換え先 |
| --- | --- |
| `SkuDetails` | `ProductDetails` |
| `SkuDetailsParams` | `QueryProductDetailsParams` |
| `querySkuDetailsAsync()` | `queryProductDetailsAsync()` |
| `SkuDetailsResponseListener` | `ProductDetailsResponseListener` |
| `BillingFlowParams.Builder.setSkuDetails()` | `setProductDetailsParamsList()` |
| `Purchase.getSkus()` | `Purchase.getProducts()` |

JNI 側の注意点:

* `GetMethodID` で文字列指定しているシグネチャは**コンパイルエラーにならず実行時に NoSuchMethodError で落ちる**。`querySkuDetailsAsync` / `getSkus` / `getSku` 等を grep で全件洗い出すこと。
* 価格取得は `SkuDetails.getPrice()` の1メソッドではなく、`ProductDetails.getOneTimePurchaseOfferDetails().getFormattedPrice()`(消費型)/ `getSubscriptionOfferDetails()`(サブスク)に分岐する。本プロジェクトは消費型中心なので `oneTimePurchaseOfferDetails` が null のケース(商品設定ミス)もガードする。

### 1-2. queryProductDetailsAsync の戻り値変更

コールバックが `List<ProductDetails>` ではなく **`QueryProductDetailsResult`** を返すようになった。

* `getProductDetailsList()`: 取得できた商品
* `getUnfetchedProductList()`: 取得に失敗した商品(無効なオファー等)が**理由付きで**返る

→ 「ストアに商品が出ない」系の問い合わせ調査が楽になるので、`unfetchedProductList` が空でない場合は productId と statusCode を**必ずログ(Crashlytics の non-fatal でも可)に出す**実装を入れること。

### 1-3. queryPurchaseHistoryAsync / PurchaseHistoryRecord の削除

* 過去の消費済み・期限切れ購入を SDK から取得する手段が**完全になくなった**。
* 現在有効な購入は従来通り `queryPurchasesAsync()` で取得。
* 購入履歴が必要な用途はサーバー側の台帳(レシート検証時に保存しているレコード)で代替。返金・チャージバックは Voided Purchases API で補完可能だが完全な代替ではない。
* 既存の復元処理・未消費リカバリ処理が `queryPurchasesAsync` のみで完結しているか要確認。`queryPurchaseHistoryAsync` をリカバリ系デバッグメニューで使っていた場合はその機能ごと見直し。

### 1-4. 自動再接続(任意だが推奨)

`BillingClient.Builder.enableAutoServiceReconnection()` が追加。`SERVICE_DISCONNECTED` 時の自前リトライ処理を SDK に任せられる。

* 採用する場合: 自前の再接続ループと**二重に走らない**ことを確認(無限リトライ・コールバック多重発火のリスク)。
* 採用しない場合: 既存の再接続実装をそのまま維持で OK。今回の移行スコープを小さくするなら**採用見送りが安全**。

### 1-5. 8.1〜8.3 で追加された API(対応不要・把握のみ)

8.1〜8.3 の差分は外部オファー / 外部コンテンツリンク / **外部決済(External Payments)** 向けの新 API(`enableBillingProgram`, `isBillingProgramAvailableAsync`, `DeveloperProvidedBillingDetails` 等)。日本は外部リンク決済の対象地域なので将来の事業判断次第で関係してくるが、**呼ばなければ挙動に影響なし**。8.0 ではなく 8.3.0 を選ぶ理由は単純に最新のバグフィックス(8.2.1 で billing program 系の修正あり)を取り込むため。

---

## 2. ビルド・環境まわりのチェック

ここが今回の移行で一番事故りやすい。コード修正より先に**ビルドが通るかを最初に検証**する。

---

## 3. テスト計画

### 3-1. テスト環境の準備

### 3-2. 機能テスト(正常系)

| # | 項目 | 確認内容 |
| --- | --- | --- |
| 1 | 商品情報取得 | 全 productId の名称・価格・通貨が Play Console の設定と一致。`unfetchedProductList` が空 |
| 2 | 消費型購入(通常) | 購入 → サーバー検証 → 付与 → `consumeAsync` まで完走。ジェム残高が正しく増える |
| 3 | 連続購入 | 同一商品を連続で2回購入(consume 完了前の2回目が `ITEM_ALREADY_OWNED` にならないこと/なる場合のリカバリ動作) |
| 4 | 複数商品 | 価格帯の異なる商品を一通り購入(最安・最高額・初回限定系) |
| 5 | 初回購入特典 | 初回限定商品の購入可否判定がサーバー側と整合 |
| 6 | 通貨・ロケール | 端末言語/Play アカウント地域を変えて価格表示確認(最低 JPY ともう1通貨) |

### 3-3. 異常系・中断系(バグが出るのはここ)

| # | 項目 | 手順 | 期待動作 |
| --- | --- | --- | --- |
| 1 | 購入キャンセル | 決済シートで戻る | `USER_CANCELED` を正しくハンドリングし、UI がロック状態に残らない |
| 2 | 決済拒否 | 「常に拒否」テストカード | エラー表示 → 再購入可能 |
| 3 | 保留購入 | 「しばらくしてから承認」カード | `PENDING` 状態を付与せず保持 → 承認後の `onPurchasesUpdated` or 復帰時 `queryPurchasesAsync` で付与 |
| 4 | 購入直後プロセス kill | 決済完了 → consume 前にアプリ強制終了 | 再起動時に未消費購入を検出し、付与とconsume が走る(**二重付与しない**) |
| 5 | 通信断(購入後) | 決済完了 → サーバー検証前に機内モード | リトライ or 次回起動時リカバリで付与。purchaseToken がロストしない |
| 6 | 通信断(商品取得) | 機内モードで購入画面へ | エラー表示、復帰後に再取得可能 |
| 7 | サービス切断 | billing overrides で `SERVICE_DISCONNECTED` | 再接続して処理続行(自前リトライと自動再接続の二重発火がないこと) |
| 8 | acknowledge 漏れ | 付与後3日放置(またはログで確認) | 消費型は consume が acknowledge を兼ねる。consume されないパスがないことをログで確認(漏れると**3日後に自動返金**) |
| 9 | 別端末復元 | 端末Aで購入 → 未消費のまま端末Bでログイン | アカウント設計上の期待動作通り(obfuscatedAccountId の突合) |
| 10 | 多重起動・連打 | 購入ボタン連打 | `launchBillingFlow` が多重に走らない |
| 11 | 返金 | Play Console からテスト購入を返金 | サーバー側(Voided Purchases / RTDN)で検知し残高処理が仕様通り |

### 3-4. 回帰観点(v8 固有)

### 3-5. リリース後の監視

---

## 4. 作業順序の推奨

1. ブランチを切って AAR を 8.3.0 に差し替え → **まずビルドを通す**(セクション2)
2. コンパイルエラー箇所を ProductDetails 系に置換(セクション1-1)
3. JNI シグネチャの grep 全件確認
4. `QueryProductDetailsResult` 対応 + unfetched ログ追加(1-2)
5. `queryPurchaseHistoryAsync` 依存箇所の棚卸しと削除(1-3)
6. 内部テストトラックで 3-2 → 3-3 → 3-4 を消化(チェックリストをテスト管理表に転記)
7. アップデートまたぎテスト(v7ビルド→v8ビルド)
8. 段階的公開 + 監視(3-5)
