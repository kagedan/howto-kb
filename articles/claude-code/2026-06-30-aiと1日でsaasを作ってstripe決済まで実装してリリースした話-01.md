---
id: "2026-06-30-aiと1日でsaasを作ってstripe決済まで実装してリリースした話-01"
title: "AIと1日でSaaSを作って、Stripe決済まで実装してリリースした話"
url: "https://zenn.dev/flowly/articles/6527fd8f90dde0"
source: "zenn"
category: "claude-code"
tags: ["API", "zenn"]
date_published: "2026-06-30"
date_collected: "2026-07-01"
summary_by: "auto-rss"
query: ""
---

## はじめに

海外クライアントから報酬をもらっているフリーランサーなら、こんな悩みありませんか。

* 為替レートをいちいち調べて手計算している
* 確定申告のときに年間収入をまとめるのが大変
* 英語の請求書を作るのが面倒
* 未払いの催促メールを英語で書けない

既存のツール（Toggl・Harvest・Clockify）を試しましたが、どれもチーム向けで日本の確定申告には対応していませんでした。

「ないなら作ろう」と思い立ち、Claude（AI）と一緒に1日でSaaSを作りました。この記事では何を使って、どう作ったかをまとめます。

## 作ったもの

**Flowly** — 海外案件をやる日本人フリーランサー向けの時間管理・請求書・確定申告ツールです。

<https://flowly-iota-ten.vercel.app>

### 主な機能

* ワンクリックタイマー
* 英語PDF請求書の自動生成
* 為替レート自動換算（USD/EUR/GBP→JPY）
* AI督促メール自動生成
* 確定申告用年間収入レポート（PDF出力）
* 送金手数料を考慮した実収入表示
* ポモドーロタイマー・収益目標トラッカー

## 技術スタック

| 領域 | 採用技術 |
| --- | --- |
| フロントエンド | Next.js 16 (App Router) |
| データベース・認証 | Supabase |
| 決済 | Stripe |
| ホスティング | Vercel |
| AI | Claude API (Anthropic) |

## なぜ1日で作れたのか

正直に言うと、コードを書く時間よりも「何を作るべきか」を固める時間の方が長かったです。

Claudeと対話しながら要件を決め、その場で実装する。このサイクルを繰り返すことで、通常なら数週間かかる開発が1日で形になりました。

具体的には以下のような流れでした。

1. ランディングページ・認証・基本機能の実装
2. Vercel + Supabaseで公開
3. Stripeで月額課金を実装
4. フリープランの制限設計
5. 為替API連携・確定申告レポート機能の追加
6. UIのブラッシュアップ（ミニマルデザインへ）

## つまずいたポイント

### 1. Next.js のミドルウェア名変更

Next.js 16から`middleware.ts`が`proxy.ts`に変わっており、関数名も`middleware`から`proxy`に変更が必要でした。

```
// Before (古いバージョン)
export async function middleware(request: NextRequest) { ... }

// After (Next.js 16)
export async function proxy(request: NextRequest) { ... }
```

### 2. Supabase RLSによるWebhookの権限エラー

StripeのWebhookからSupabaseのprofilesテーブルを更新しようとして、Row Level Securityに弾かれました。Service Role Keyを使うことで解決しました。

```
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY! // anon keyではなくservice role keyを使う
)
```

### 3. React Hooksの呼び出し順序エラー

`if (!user) return null`の後に`useState`を呼んでいて、Reactのhooksルール違反でエラーになりました。早期returnの前に全てのhooksを呼ぶよう修正しました。

## 収益化の設計

フリープランの設計は最初緩すぎました。

| 機能 | 最初の設定 | 修正後 |
| --- | --- | --- |
| クライアント数 | 5件 | 2件 |
| 請求書 | 10件/月 | 3件/月 |
| AI督促 | 5回/月 | 2回/月 |
| 確定申告レポート | 無料 | Pro限定 |
| 為替換算 | 無料 | Pro限定 |

「使ってみたいけど制限にぶつかる」絶妙なラインを意識しました。

## 今後の展望

現在はProduct Hunt・Reddit・X・noteで公開し、フィードバックを集めている段階です。

確定申告レポート機能は競合がほぼないため、日本人海外フリーランサー向けにニッチを取れると考えています。

## さいごに

AIを使った開発は「アイデアを形にするまでの距離」を劇的に縮めてくれると実感しました。

興味のある方はぜひ触ってみてください。フィードバックお待ちしています。

<https://flowly-iota-ten.vercel.app>
