---
id: "2026-03-28-nextjs-16-anthropic-claude-apiでトレード日記ai分析ツールを個人開発し-01"
title: "Next.js 16 + Anthropic Claude APIでトレード日記AI分析ツールを個人開発した話【5言語対応・PWA】"
url: "https://qiita.com/tradejournal/items/6ce1b9b3959c8f722075"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

# Next.js 16 + Anthropic Claude APIでトレード日記AI分析ツールを個人開発した話

## はじめに

個人トレーダーとして数年間FXと株を続ける中で、ずっと感じていた課題がありました。「なぜ同じ失敗を繰り返すのか」という問いへの答えが、スプレッドシートや手書き日記では得られなかったのです。

その課題を解決するために作ったのが **[TradeJournal](https://tradejournal.company)** です。トレード記録を蓄積し、週次でAIがプロのコーチのような分析レポートを自動生成するWebアプリです。

> **デモページを公開しています。** アカウント登録不要でUIと機能を確認できます。  
> <https://tradejournal.company/demo>

本記事では技術選定の意図から実装の詳細まで、エンジニア視点で解説します。

### 主な特徴

| 機能 | 概要 |
| --- | --- |
| AI週次レビュー | Claude APIが数値根拠付きのコーチングを自動生成 |
| ルール違反検知 | 自分で設定したルールへの違反を自動チェック |
| 多言語対応 | 日本語・英語・韓国語・繁体字中国語・簡体字中国語の5言語 |
| PWA対応 | スマホのホーム画面に追加してネイティブアプリ感覚で利用可能 |
| フリープラン | 月30件のトレード記録 + 月1回のAIレビューが無料 |

---

## 1. なぜ作ったか

トレードにおける最大の敵は「感情」と「自分のルール違反」です。勝てるトレーダーの多くは、厳密なルールと記録管理によってこれを克服しています。しかし一般的なトレーダーのジャーナル管理は以下のような問題を抱えています。

* Excelで記録しても「分析」は自分でやらなければならない
* 手書き日記は書くのが面倒で続かない
* 勝率・損益の集計はできても「パターンの発見」には繋がらない
* 「ルール違反」を記録していても、その損益インパクトを計算していない

特に最後の点が重要です。「ルール違反をしたらどれだけ損をしているか」を数値で把握していないトレーダーがほとんどです。この数値を可視化し、さらにAIが毎週フィードバックをくれる仕組みがあれば、トレードは劇的に改善できると考えました。

---

## 2. 技術スタック全体像

```
フロントエンド:  Next.js 16 (App Router) + React 19 + TypeScript + Tailwind CSS
バックエンド:    Next.js Route Handlers + Supabase (Auth / DB / RLS)
AI:             Anthropic Claude API (claude-haiku-4-5)
決済:           Paddle (グローバル対応のMoR型決済)
メール:          Resend
i18n:           next-intl（5言語対応）
PWA:            next-pwa
```

### Next.js 16 (App Router) + React 19

React 19のServer Components（RSC）によってデータフェッチのアーキテクチャが大きく変わりました。トレードジャーナルのようなデータ集計が多いアプリでは、サーバー側でSupabaseクエリを実行してHTMLとして返せるRSCは非常に相性が良いです。

また、Route HandlersによるAPIエンドポイント管理が簡潔になり、Edge Runtimeへの対応も容易です。

### Supabase

* **認証（Auth）**: JWTベースの認証をゼロ実装で導入可能
* **RLS（Row Level Security）**: ユーザーデータの分離をDBレイヤーで保証
* **リアルタイム**: 将来的なライブ機能拡張に対応
* **コスト**: フリープランで十分なMVP検証が可能

特にRLSはマルチテナントSaaSを個人で構築する際に非常に強力です。アプリ層でのフィルタリングミスによる情報漏洩リスクをDBレイヤーで根本的に排除できます。

### Anthropic Claude API

GPT-4と比較検討しましたが、以下の理由でClaudeを選択しました。

* **長いコンテキスト**: 数十件のトレードデータ＋統計数値をまとめてプロンプトに注入しても処理できる
* **日本語品質**: 日本語ユーザー向けの自然な文章生成品質が高い
* **コスト**: claude-haiku-4-5 は推論速度と価格のバランスが優秀

### next-intl による5言語対応

`next-intl`を使い、日本語（JA）・英語（EN）・韓国語（KO）・繁体字中国語（ZH-TW）・簡体字中国語（ZH-CN）の5言語をサポートしています。App Routerの`[locale]`動的セグメントとミドルウェアによるロケール検出を組み合わせることで、URLベースの言語切替を実現しました。

### Paddle による決済

グローバル展開を見据え、Merchant of Record（MoR）型のPaddleを採用しました。消費税・VAT処理をPaddle側に委任でき、個人開発者でも各国の税務対応を気にせず課金機能を導入できます。

---

## 3. 実装のポイント

### 3-1. App Router でのサーバーコンポーネント活用

ダッシュボードページは完全なServer Componentとして実装し、Supabaseからのデータ取得をサーバー側で完結させています。

```
// src/app/dashboard/page.tsx
import { createClient } from '@/lib/supabase/server'
import { DashboardStats } from '@/components/dashboard/DashboardStats'
import { EquityCurve } from '@/components/dashboard/EquityCurve'
import { computeWeeklyStats } from '@/lib/analytics/weekly-stats'

export default async function DashboardPage() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  const { data: trades } = await supabase
    .from('trades')
    .select('*')
    .eq('user_id', user!.id)
    .order('trade_date', { ascending: false })
    .limit(200)

  const stats = computeWeeklyStats(trades ?? [])

  return (
    <main className="container mx-auto py-8">
      <DashboardStats stats={stats} />
      <EquityCurve trades={trades ?? []} />
    </main>
  )
}
```

クライアントコンポーネントはインタラクションが必要な部分のみ（チャートの操作、フォーム送信など）に限定し、初期表示は全てSSRで完結させています。

---

### 3-2. Supabase Auth + RLS によるマルチテナント設計

RLSポリシーをテーブル単位で設定し、アプリ層を一切通さずにデータアクセスを制御しています。

```
-- supabase/schema.sql

ALTER TABLE trades ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only access their own trades"
  ON trades
  FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

ALTER TABLE rules ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only access their own rules"
  ON rules
  FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);
```

サーバーサイドのSupabaseクライアントは、リクエストのCookieからセッションを復元して動作します。Next.js 16では`cookies()`がPromiseを返す非同期APIに変更されているため注意が必要です。

```
// src/lib/supabase/server.ts
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export async function createClient() {
  const cookieStore = await cookies() // Next.js 16では await が必要

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll()
        },
        setAll(cookiesToSet: { name: string; value: string; options: object }[]) {
          cookiesToSet.forEach(({ name, value, options }) => {
            cookieStore.set(name, value, options)
          })
        },
      },
    }
  )
}
```

---

### 3-3. Claude APIプロンプトエンジニアリング

週次AIレビューの品質は、プロンプトにどれだけ具体的な数値を注入できるかで決まります。単純に「トレード記録を分析してください」と渡すだけでは汎用的な回答しか返ってきません。

プロフィットファクター・期待値・チルト検知などの指標を事前に計算し、構造化して注入することで、AIが具体的な数値根拠を持ったコーチングができるようになります。

```
// src/lib/ai/generate-review.ts
const prompt = `
あなたはプロのトレードコーチです。以下の週次データを分析し、
具体的な数値根拠を持ったフィードバックを日本語で提供してください。

## 今週の基本統計
- 総トレード数: ${stats.totalTrades}件
- 勝率: ${(stats.winRate * 100).toFixed(1)}%
- プロフィットファクター: ${stats.profitFactor.toFixed(2)}
- 期待値: ${stats.expectancy.toFixed(0)}円/トレード

## ルール違反分析
- 違反トレード数: ${violationTrades.length}件
- 違反時の平均損益: ${violationAvgPnl.toFixed(0)}円
- 遵守時の平均損益: ${normalAvgPnl.toFixed(0)}円
- 違反による推定損失: ${estimatedViolationCost.toFixed(0)}円

## チルト指標
- 連勝後翌日勝率: ${(postStreakWinRate * 100).toFixed(1)}%（通常比 ${diff}%）
`
```

---

### 3-4. ルール違反自動検知エンジン

トレーダーが「損切りは-2%以上」「エントリーは9時〜15時のみ」のようなルールを設定すると、記録時に自動で違反チェックが走ります。

```
// src/lib/rule-engine/check-violations.ts
type Operator = 'gt' | 'gte' | 'lt' | 'lte' | 'eq' | 'neq'

const OPERATORS: Record<Operator, (a: number, b: number) => boolean> = {
  gt:  (a, b) => a > b,
  gte: (a, b) => a >= b,
  lt:  (a, b) => a < b,
  lte: (a, b) => a <= b,
  eq:  (a, b) => a === b,
  neq: (a, b) => a !== b,
}

export function checkViolations(trade: Partial<Trade>, rules: Rule[]): Rule[] {
  return rules.filter(rule => {
    const tradeValue = getTradeField(trade, rule.field)
    if (tradeValue === undefined || tradeValue === null) return false
    const op = OPERATORS[rule.operator as Operator]
    // ルールの「こうあるべき」条件を満たさない = 違反
    return !op(Number(tradeValue), Number(rule.threshold))
  })
}
```

5フィールド（損益率・RR・ポジションサイズ・エントリー時間・保有時間）×6演算子で、ほとんどのトレードルールを表現できます。

---

## 4. 詰まったポイントと解決法

### Next.js 16 の破壊的変更

`cookies()`が非同期APIになったため、`await cookies()`が必要。また`setAll`の型に明示的なアノテーションが必要になりました。

```
// NG: Next.js 15以前
const cookieStore = cookies()

// OK: Next.js 16
const cookieStore = await cookies()
```

### Claude APIのレスポンス型エラー

`message.content[0]`は`TextBlock | ImageBlock`のユニオン型のため、`.text`に直接アクセスするとTypeScriptエラーになります。

```
// NG
const text = message.content[0].text

// OK
const block = message.content[0]
const text = block.type === 'text' ? block.text : ''
```

---

## 5. PWA対応

TradeJournalはPWA（Progressive Web App）に対応しており、スマホのホーム画面に追加するとネイティブアプリに近い操作感で使えます。トレード直後にサッと記録を残したいという需要に応えるため、モバイル体験の最適化は必須でした。

`next-pwa`を導入し、Service Workerによるキャッシュ戦略とオフラインフォールバックを設定しています。

---

## 6. 今後の展望

* MT4/MT5からのトレード自動インポート
* 仮想通貨取引所APIとの連携
* AIバックテスト機能
* チーム・コミュニティ機能
* 対応言語の追加

---

## まとめ

Next.js 16 (React 19) + Supabase + Claude APIの組み合わせは個人開発SaaSに非常に適したスタックです。Paddleによるグローバル決済、next-intlによる多言語対応、PWAによるモバイル体験まで含めて、個人でもプロダクション品質のSaaSを構築できる良い時代になりました。

**[TradeJournal](https://tradejournal.company)** は公開中です。フリープランで月30件のトレード記録と月1回のAIレビューを無料で試せます。

まずは **[デモページ](https://tradejournal.company/demo)** でUIと機能をご覧ください。フィードバックお待ちしています。
