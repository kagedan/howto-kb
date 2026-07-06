---
id: "2026-07-06-claude-codeで美容院向け前金予約saasをゼロから作りきった全記録-iosアプリバックエン-01"
title: "Claude Codeで美容院向け前金予約SaaSをゼロから作りきった全記録 — iOSアプリ×バックエンド×Stripe Connect×App Store提出まで"
url: "https://qiita.com/sorabcjanne1/items/5ea48f30bcf08c2fc33f"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "JavaScript", "qiita"]
date_published: "2026-07-06"
date_collected: "2026-07-07"
summary_by: "auto-rss"
query: ""
---

## はじめに

「予約されたのに無断でキャンセルされた」「前金を取りたいがシステムが高すぎる」——個人サロン経営者のそういった声を起点に、**前金付き予約管理 iOS アプリ「前金予約」** を Claude Code で構築しました。

このセッションは単なるコード生成に留まらず、

- SwiftUI/SwiftData の 6 フェーズ実装（約 60 ファイル）
- Node.js バックエンドの設計・ConoHa VPS へのデプロイ
- Stripe Connect を使った店舗ごとの直接入金
- App Store Connect への審査提出（ブラウザ自動操作＋API）

まで、**設計書を読み込んだ AI が全工程を自律的に推進する**という体験になりました。本記事ではその全容と、途中でハマったポイントを共有します。

---

## やったこと

### Phase 1〜2：iOS アプリの基盤とビジネスロジック

xcodegen でプロジェクトを生成し、4 タブ構成・Keychain・SwiftData モデル・BookingEngine を実装しました。

特に BookingEngine は「**重複判定の等号境界**」「**前金の 10 円切り捨て**」「**ステータス遷移の強制**」という 3 つの核をユニットテストで固めてから UI に進みました。

```swift
// 席数を考慮した最大同時予約数チェック
func fitsCapacity(_ slot: DateInterval, capacity: Int, excluding: Reservation.ID?) -> Bool {
    let count = reservations
        .filter { $0.id != excluding }
        .filter { DateInterval($0.startDate, $0.endDate).intersects(slot) }
        .count
    return count < capacity
}
```

### Phase 3〜6：画面 14 枚・Stripe・StoreKit・通知

カレンダー、予約 CRUD、Stripe 決済リンク発行、APNs 通知スケジューラ、StoreKit 2 によるサブスク管理、フリー枠制限と Paywall まで実装。最終的にユニットテスト 36 本が全緑になりました。

```swift
// StoreKit 2 の購入フロー
func purchase(_ product: Product) async throws -> Bool {
    let result = try await product.purchase()
    switch result {
    case .success(let verification):
        let transaction = try verification.payloadValue
        isPremium = true
        await transaction.finish()
        return true
    default:
        return false
    }
}
```

### バックエンド：Node.js + Hono + PostgreSQL

v2 のキモは「**お客様が店の URL にアクセスして自分で予約・前金決済する**」セルフ予約フローです。ConoHa VPS（既存の本番システムと完全分離・ポート 3210）に Hono + ローカル PostgreSQL で構築しました。

二重予約防止は **Postgres の `SELECT ... FOR UPDATE` 行ロック + 10 分の仮押さえ（hold）** で実現しています。

```javascript
// 同時アクセスでも安全な hold 処理
await client.query('BEGIN');
const store = await client.query(
  'SELECT id FROM stores WHERE slug = $1 FOR UPDATE',
  [slug]
);
const concurrentCount = await client.query(
  `SELECT COUNT(*) FROM reservations
   WHERE store_id = $1
   AND status IN ('held','confirmed')
   AND NOT (end_time <= $2 OR start_time >= $3)`,
  [storeId, startTime, endTime]
);
if (parseInt(concurrentCount.rows[0].count) >= store.rows[0].capacity) {
  await client.query('ROLLBACK');
  return c.json({ error: 'slot_full' }, 409);
}
// hold を INSERT
await client.query('COMMIT');
```

### Stripe Connect：店ごとに直接入金

application_fee_amount を設定することで、**各店舗の Stripe アカウントに直接入金しながら 1% をプラットフォームが受け取る**構成にしました。

```javascript
const session = await stripe.checkout.sessions.create(
  {
    mode: 'payment',
    line_items: [{ price: price.id, quantity: 1 }],
    success_url: `${BASE_URL}/done?session_id={CHECKOUT_SESSION_ID}`,
    payment_intent_data: {
      application_fee_amount: Math.floor(depositAmount * PLATFORM_FEE_BPS / 10000),
    },
  },
  { stripeAccount: store.stripe_account_id }  // 直接課金
);
```

実決済で `application_fee_amount: 42`（¥4,200 の 1%）が確認できました。

### Stripe Connect の自動確定（reconcile 方式）

ダイレクトチャージの Webhook は接続アカウント側に飛ぶため、プラットフォーム側のハンドラでは受け取れません。Webhook 追加設定をユーザーに求める代わりに、**店アプリが同期するたびにサーバーが Stripe へ照合して未確定決済を自動確定する** reconcile 方式で解決しました。

```javascript
async function reconcileStorePayments(store) {
  const pending = await db.query(
    `SELECT * FROM reservations
     WHERE store_id = $1 AND status = 'held'
     AND created_at > NOW() - INTERVAL '7 days'`,
    [store.id]
  );
  for (const r of pending.rows) {
    const sessions = await stripe.checkout.sessions.list(
      { payment_intent: r.stripe_payment_intent_id },
      store.stripe_account_id ? { stripeAccount: store.stripe_account_id } : {}
    );
    if (sessions.data[0]?.payment_status === 'paid') {
      await db.query(
        `UPDATE reservations SET status='confirmed', deposit_status='secured' WHERE id=$1`,
        [r.id]
      );
    }
  }
}
```

### App Store Connect の全自動操作

App Store Connect の API キー（`~/.appstoreconnect/private_keys/` に既存）を発見し、**メタデータ投入を全 API 化**。ブラウザが必要な操作（サブスク商品作成・App Privacy 公開・審査提出）は Playwright MCP で自動化しました。

アプリアイコンも CoreGraphics でコード生成しています。

```swift
// カレンダー + ¥コインをコードで描画
let context = CGContext(data: nil, width: 1024, height: 1024, ...)!
// グラデーション背景
let gradient = CGGradient(...)
context.drawLinearGradient(gradient, start: ..., end: ...)
// カレンダー枠
context.addRoundedRect(...)
context.setFillColor(UIColor.white.withAlphaComponent(0.15).cgColor)
context.fillPath()
// ¥ マーク
// ...
```

---

## ハマったポイント

### 1. Stripe の `rk_test_` キーはデフォルト権限ゼロ

制限付きテストキー（`rk_test_`）は作成直後は全権限が `None` です。エンドポイント別に 403 を拾うプローブで必要権限を特定しました。

```bash
# プローブ例
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $KEY" \
  https://api.stripe.com/v1/payment_links
# → 403: payment_links_read が必要
```

最終的に必要だった権限（仕様書に記載がなかったものを含む）：

| エンドポイント | 必要な権限 |
|---|---|
| GET /v1/payment_links | Payment Links: Read |
| GET /v1/checkout/sessions | Checkout Sessions: Read |
| POST /v1/prices | Prices: Write |
| POST /v1/payment_links | Payment Links: Write |
| POST /v1/payment_links/{id} | Payment Links: Write |
| POST /v1/refunds | Refunds: Write |

### 2. SMTP パスワードの SSH 越しシェル展開

`giF%j+a$B/J^` のようなパスワードを SSH コマンド引数で渡すと `$B` が展開されて文字化けします。ヒアドキュメントで回避しました。

```bash
# NG（$B が展開される）
ssh deploy@server "echo SMTP_PASS=giF%j+a\$B/J^ >> .env"

# OK（ヒアドキュメント内はシングルクォートで展開抑制）
ssh deploy@server bash <<'SCRIPT'
PASS='giF%j+a$B/J^'
echo "SMTP_PASS=${PASS}" >> /var/www/maekin-yoyaku/.env
SCRIPT
```

### 3. SwiftData の in-memory fetch が XCTest 内でクラッシュ（Xcode 26 / iOS 26）

`context.fetch(FetchDescriptor<T>())` を XCTest のテストプロセス内で呼ぶと `EXC_BREAKPOINT` でクラッシュします。**アプリ本体では正常動作**しており、ヘッドレステスト環境のバグです。

対処：SwiftData コンテナに依存するテストを削除し、`URLProtocol` スタブで実 JSON を流す形に置き換えました。

```swift
// URLProtocol スタブで実サーバーのレスポンスを再現
class StubURLProtocol: URLProtocol {
    static var stubData: Data?
    override func startLoading() {
        let response = HTTPURLResponse(url: request.url!, statusCode: 200, ...)!
        client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
        client?.urlProtocol(self, didLoad: StubURLProtocol.stubData ?? Data())
        client?.urlProtocolDidFinishLoading(self)
    }
}
```

### 4. ASC API でアプリ作成は不可

App Store Connect API は `apps` リソースの CREATE を許可していません。

```
POST /v1/apps
→ 409: The resource 'apps' does not allow 'CREATE'
```

アプリの器だけはブラウザで手動作成し、その後のメタデータ（説明文・KW・サブタイトル等）は API で投入する二段構えが必要です。

### 5. ASC の説明文に使えない文字がある

`━`（罫線文字）は ASC が弾きます（`Invalid value`）。`─` に変えても同様。`■` や `◆` は通りました。

```
# NG
━━━━━━━━━━━━━━━

# OK（区切りを除去して ■ 見出しに統一）
■ セルフ予約ページで 24 時間受付
```

### 6. サブスク商品の What's New は初回バージョンで設定不可

バージョン 1.0 は `What's New` フィールドが編集不可（409）。2 回目以降のアップデートから有効になります。

### 7. サブスクが READY_TO_SUBMIT にならない原因

サブスクグループ自体のローカリゼーション（`displayName`）が未設定だと、商品側が READY にならず MISSING_METADATA のままになります。商品の表示名とは別にグループの表示名も必要です。

---

## 学び

### 「任せる！」で全工程が進む体験

このセッションで一番印象的だったのは、ユーザーが「任せる！」と言うだけでフェーズ間の判断・デプロイ・権限調査・ブラウザ操作・ASO 原稿まで AI が推進した点です（個人の感想として）。

ただし **AI が自律できない境界** は明確でした：

- Apple ID / Stripe の 2FA 認証
- SMTP アカウントのパスワード
- DNS の A レコード操作
- Stripe Identify の本人確認（クロスオリジン iframe）

これらは金融・認証情報の性質上、人間が担う必要があります。逆に言えば、**「境界だけ人間が担当し、それ以外は AI に委ねる」** という分業が SaaS 開発の新しいスタイルになりつつあると感じます。

### Stripe Connect の設計指針

- **Direct Charge**（店が MoR）は法的リスクが小さく多店舗に向いている
- `application_fee_amount` でプラットフォーム手数料を自動回収できる
- Connect Webhook の「接続アカウント側にイベントが飛ぶ」問題は reconcile-on-sync で回避できる（Webhook 設定をユーザーに求めずに済む）

### 実 API との付き合い方

仕様書の「必要権限一覧」はしばしば不完全です。エンドポイントを 1 本ずつ叩いて 403 のエラーメッセージを読む「プローブ診断」が、Stripe に限らず権限系の問題解決に有効でした。

---

## まとめ

Claude Code を使い、設計書から App Store 審査提出まで **ほぼ 1 セッションで**完走できました。途中で「店が予約リンクを送る」→「お客様がセルフ予約する」という方針転換も AI が飲み込んでコードに反映してくれます。

ハマりどころの多くは Apple/Stripe の仕様の細かな罠でしたが、エラーメッセージをちゃんと読んで原因を特定する行動は AI も人間も変わりません。**「エラーを読む」「小さく実証する」「境界を正直に伝える」** の 3 点を守れば、思ったよりずっと遠くまで進めます。
