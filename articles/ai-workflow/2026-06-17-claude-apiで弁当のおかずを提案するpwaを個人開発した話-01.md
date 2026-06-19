---
id: "2026-06-17-claude-apiで弁当のおかずを提案するpwaを個人開発した話-01"
title: "Claude APIで弁当のおかずを提案するPWAを個人開発した話"
url: "https://zenn.dev/sarashina1178/articles/5dfaaec8f8e256"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "zenn"]
date_published: "2026-06-17"
date_collected: "2026-06-19"
summary_by: "auto-rss"
query: ""
---

## 作ったもの

弁当のおかずをAIが提案するPWA「**おかずAI**」を作りました。

冷蔵庫にある食材やジャンルを選ぶだけで、AIが今週末に作るおかずを提案してくれます。ログイン不要でも試せます。

<https://okazu-sage.vercel.app/>

この記事では、個人開発で **Claude API を安全に組み込む構成** を中心に、実際のコードを交えて知見を共有します。

## 技術スタック

| 分類 | 技術 |
| --- | --- |
| フロントエンド | React 18 + Vite 6 / React Router 7 |
| スタイリング | Tailwind CSS 3 |
| PWA | vite-plugin-pwa（Workbox） |
| API | Vercel Functions |
| AI | Claude API（claude-haiku-4-5） |
| 認証 | Firebase Authentication（Googleログイン） |
| DB | Cloud Firestore |
| Bot対策 | Firebase App Check（reCAPTCHA v3） |
| 分析 / SEO | GA4 / sitemap.xml・robots.txt |

モデルに `claude-haiku-4-5` を選んだのは、おかず提案のように軽量な生成タスクでは速度とコストが効くからです。レシピ程度の出力なら十分な品質が出ます。

## 工夫した点①：APIキーを隠す構成

AI系の個人開発で一番やってはいけないのが、**APIキーをフロントに置くこと**です。ビルド成果物から普通に抜けるので、キーが流出して請求が青天井になります。

そこでClaude APIの呼び出しは必ずサーバー側（Vercel Functions）で行い、フロントは自前の `/api/generate` を叩くだけにしました。キーはVercelの環境変数に置きます。

```
// api/generate.js（抜粋）
const Anthropic = require('@anthropic-ai/sdk')

const apiKey = process.env.ANTHROPIC_API_KEY // サーバー側の環境変数
const client = new Anthropic({ apiKey })

const message = await client.messages.create({
  model: 'claude-haiku-4-5-20251001',
  max_tokens: 4000,
  messages: [{ role: 'user', content: prompt }],
})
```

AIには「JSON配列のみを出力」と指示し、レスポンスから正規表現で配列部分だけ抜き出してパースしています。説明文やコードブロックが混ざっても拾えるようにするための保険です。

```
const text = message.content[0].text
const jsonMatch = text.match(/\[[\s\S]*\]/)
if (!jsonMatch) throw new Error('AIの応答からJSONを取り出せませんでした')
const suggestions = JSON.parse(jsonMatch[0])
```

## 工夫した点②：多層の不正利用対策

APIキーを隠しても、生成APIが誰でも叩ける状態だと、結局そこを乱用されてClaudeの利用料が跳ね上がります。そこでログイン後の生成APIは多層で守っています。

1. **Firebase Auth** … ID Tokenを検証して本人確認
2. **App Check（reCAPTCHA v3）** … 自動化されたBotをブロック
3. **Firestoreトランザクション** … ユーザーごとに月次のレート制限

### ID Token検証 → 月次レート制限

レート制限は、単純に「読んで→+1して書く」だと、同時リクエストで上限を超えてしまう競合（race condition）が起きます。これを防ぐためにFirestoreの**トランザクション**で原子的に処理しています。

```
// api/generate.js（抜粋）
// ① Firebase ID Token を検証
const decoded = await admin.auth().verifyIdToken(authHeader.slice(7))
const userId = decoded.uid

// ② 月次レート制限（"2026-06" のようなキーで月ごとに集計）
const yearMonth = new Date().toISOString().slice(0, 7)
const usageRef = db.doc(`users/${userId}/usage/${yearMonth}`)

const limitExceeded = await db.runTransaction(async (tx) => {
  const snap = await tx.get(usageRef)
  const count = snap.exists ? (snap.data().count ?? 0) : 0
  if (count >= MONTHLY_LIMIT) return true
  tx.set(usageRef, { count: count + 1 }, { merge: true })
  return false
})

if (limitExceeded) {
  return res.status(429).json({ error: `今月の利用上限（${MONTHLY_LIMIT}回）に達しました。` })
}
```

月のキーを `YYYY-MM` のドキュメントIDにしているので、月が変われば自然に新しいカウンタが始まり、リセット処理が不要なのが地味に便利です。

### App Check の dev/prod 切り替え

App Checkは開発時にハマりやすいポイントです。本番ではreCAPTCHA v3のサイトキーが必須ですが、開発中はデバッグトークンで通す必要があります。環境で分岐させました。

```
// src/lib/firebase.js（抜粋）
if (import.meta.env.DEV) {
  // 開発：デバッグトークンを使う
  self.FIREBASE_APPCHECK_DEBUG_TOKEN = import.meta.env.VITE_APPCHECK_DEBUG_TOKEN ?? true
  initializeAppCheck(app, {
    provider: new ReCaptchaV3Provider(import.meta.env.VITE_RECAPTCHA_SITE_KEY ?? 'dev-placeholder'),
    isTokenAutoRefreshEnabled: true,
  })
} else if (import.meta.env.VITE_RECAPTCHA_SITE_KEY) {
  // 本番：サイトキーが設定されているときだけ有効化
  initializeAppCheck(app, {
    provider: new ReCaptchaV3Provider(import.meta.env.VITE_RECAPTCHA_SITE_KEY),
    isTokenAutoRefreshEnabled: true,
  })
}
```

## 工夫した点③：ログイン不要のゲスト体験

「使ってもらうにはまずログイン」だと離脱が大きいので、ログイン不要でも数回だけAI提案を試せる入口を用意しました。定番の食材セットがあらかじめ入っていて、ボタンを押すだけで提案が返ってきます。食材を編集して試すこともできます。

「まず触ってもらう → 気に入ったらログインして保存・履歴・カスタマイズ」という導線にすることで、入口のハードルを下げています。

## ハマったところ：ローカルでVercel Functionsを動かす

Vercel Functions（`/api/*`）は、`vite dev` の開発サーバーではそのままでは動きません。毎回Vercelにデプロイして確認するのは現実的ではないので、**Viteのカスタムミドルウェア**で `/api/*` を自前でハンドリングしました。

ポイントは、リクエストボディをパースしてVercel風の `req`/`res` を組み立てて関数に渡すところ。さらに `require.cache` を毎回削除することで、APIコードを編集したらホットリロードされるようにしています。

```
// vite.config.js（抜粋）
server.middlewares.use('/api/generate', (req, res) => {
  let body = ''
  req.on('data', chunk => (body += chunk))
  req.on('end', async () => {
    req.body = JSON.parse(body || '{}')
    const wrappedRes = {
      status(code) { res.statusCode = code; return this },
      json(data) {
        res.setHeader('Content-Type', 'application/json')
        res.end(JSON.stringify(data))
      },
    }
    const require = createRequire(import.meta.url)
    delete require.cache[require.resolve('./api/generate.js')] // ホットリロード
    const handler = require('./api/generate.js')
    await handler(req, wrappedRes)
  })
})
```

これで「ローカルでも本番と同じAPIコードが動く」状態になり、開発がかなり快適になりました。

## 個人開発の所感

* Claude APIは `haiku` を選べば、こういう軽量な生成用途ではコストも速度も実用的でした。
* AI機能で一番大事なのは品質より**お金の防御**。キー秘匿 + 認証 + レート制限はセットで考えるのがおすすめです。
* PWA化（vite-plugin-pwa）でホーム画面に追加でき、ネイティブアプリ風の体験になりました。

よければ触ってみてください。

<https://okazu-sage.vercel.app/>
