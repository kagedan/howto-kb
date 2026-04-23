---
id: "2026-03-24-フリーランスエンジニアの確定申告をゲーム化した話-claude-code-nextjsで作るタックス-01"
title: "フリーランスエンジニアの確定申告をゲーム化した話 ── Claude Code × Next.jsで作るタックスシミュレーター「TAX QUEST」開発記"
url: "https://qiita.com/claude-code-news/items/2d227ce2a6f8856d0eae"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-24"
date_collected: "2026-03-25"
summary_by: "auto-rss"
---

[![TAX QUEST 開発記](https://qiita-user-contents.imgix.net/https%3A%2F%2Fraw.githubusercontent.com%2FClaudeCodeNews%2Fzenn-content%2Fmain%2Fimages%2Ftax-quest-portfolio%2Fbanner-v2.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2e781bfe73eff29c6e9f78f1e23fed09)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fraw.githubusercontent.com%2FClaudeCodeNews%2Fzenn-content%2Fmain%2Fimages%2Ftax-quest-portfolio%2Fbanner-v2.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2e781bfe73eff29c6e9f78f1e23fed09)

フリーランスエンジニアにとって、毎年の確定申告は避けて通れない"ラスボス"です。複雑な税制、山のような書類、e-Taxの入力地獄……。「これ、もっとシンプルにできないか？」という自分自身の課題感から、確定申告の全工程をブラウザだけで完結させるWebアプリ「TAX QUEST」を開発しました。開発にはAIコーディングツール「Claude Code」をフル活用し、設計・実装・テストまでAIとの協働で進めています。

この記事では、なぜこのアプリを作ったのか、技術的にどう設計したのか、Claude Codeをどう活用したのか、そして実際に自分の確定申告で使ってみた結果まで、開発の全貌を詳しく紹介します。

## アプリの概要 ── TAX QUESTとは

[![TAX QUEST ダッシュボード](https://qiita-user-contents.imgix.net/https%3A%2F%2Fraw.githubusercontent.com%2FClaudeCodeNews%2Fzenn-content%2Fmain%2Fimages%2Ftax-quest-portfolio%2Fscreenshot-dashboard.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=314557f9891f0ecafdcfba8b4c6c3a69)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fraw.githubusercontent.com%2FClaudeCodeNews%2Fzenn-content%2Fmain%2Fimages%2Ftax-quest-portfolio%2Fscreenshot-dashboard.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=314557f9891f0ecafdcfba8b4c6c3a69)

TAX QUESTは、フリーランスエンジニア向けの確定申告シミュレーションWebアプリです。

「4つのステージをクリアして申告完了」というゲーム的なUIで、確定申告のハードルを下げることをコンセプトにしています。

主な特徴は以下の通りです。

* Stage 1（収入記録）: 給与所得・事業所得・雑所得を登録
* Stage 2（経費計上）: 12カテゴリの経費入力、減価償却計算、家事按分、CSVインポート
* Stage 3（控除申請）: 11種類の所得控除に対応、ふるさと納税シミュレーター内蔵
* Stage 4（結果確認）: 所得税・住民税・事業税・消費税の一括計算、e-Tax入力ガイド、自動アドバイス
* 追加機能: 申告チェックリスト（20項目）、消費税・インボイス対応、前年度比較、JSON/CSVインポート

サーバー不要・ブラウザ完結で、データはLocalStorageに保存されます。個人の税務データをサーバーに送らないので、セキュリティの観点からもシンプルです。

## 技術スタック

* フレームワーク: Next.js 16（App Router）
* 言語: TypeScript
* UI: React 19 + Tailwind CSS 4
* チャート: Recharts 3
* ストレージ: LocalStorage（サーバーレス）
* 開発ツール: ESLint 9
* AI開発支援: Claude Code（Anthropic）

特にNext.js 16のApp Routerを採用し、全ページを`'use client'`のクライアントコンポーネントとして実装しています。税額計算はすべてブラウザ上でリアルタイムに行うため、サーバーサイドレンダリングは不要という判断です。

## アーキテクチャ設計

[![アーキテクチャ概要](https://qiita-user-contents.imgix.net/https%3A%2F%2Fraw.githubusercontent.com%2FClaudeCodeNews%2Fzenn-content%2Fmain%2Fimages%2Ftax-quest-portfolio%2Fsection1-architecture.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d0fea2d7c0707e49157fc3b66e7e6427)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fraw.githubusercontent.com%2FClaudeCodeNews%2Fzenn-content%2Fmain%2Fimages%2Ftax-quest-portfolio%2Fsection1-architecture.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d0fea2d7c0707e49157fc3b66e7e6427)

### ディレクトリ構成

```
src/
├── app/                    # Next.js App Router（6ページ）
│   ├── page.tsx           # ダッシュボード
│   ├── income/page.tsx     # Stage 1: 収入入力
│   ├── expenses/page.tsx   # Stage 2: 経費入力
│   ├── deductions/page.tsx # Stage 3: 控除申請
│   ├── summary/page.tsx    # Stage 4: 結果確認
│   ├── checklist/page.tsx  # 申告チェックリスト
│   └── consumption-tax/    # 消費税・インボイス
├── components/
│   └── Navigation.tsx      # レスポンシブナビゲーション
├── context/
│   └── TaxContext.tsx      # グローバル状態管理
├── lib/
│   ├── tax-calculator.ts   # 税額計算エンジン（コア）
│   ├── storage.ts          # LocalStorage + CSV解析
│   └── utils.ts            # ユーティリティ
└── types/
    └── index.ts            # 全型定義
```

「計算ロジック」「データ永続化」「UI」の3層を明確に分離しています。特に`tax-calculator.ts`は純粋関数のみで構成されており、UIから完全に独立しています。

### 状態管理 ── React Context + LocalStorage

状態管理にはReact ContextAPIを採用しました。外部ライブラリ（Redux、Zustand等）は使っていません。

```
interface TaxContextType {
  data: TaxReturnData;
  addIncome: (income: IncomeEntry) => void;
  removeIncome: (id: string) => void;
  addExpense: (expense: ExpenseEntry) => void;
  removeExpense: (id: string) => void;
  updateDeductions: (deductions: Deductions) => void;
  updateFilingType: (filingType: FilingType) => void;
  addDepreciationAsset: (asset: DepreciationAsset) => void;
  removeDepreciationAsset: (id: string) => void;
  updateHomeOfficeRatios: (ratios: HomeOfficeRatios) => void;
  updateConsumptionTax: (settings: ConsumptionTaxSettings) => void;
  updateChecklist: (checklist: Record<string, boolean>) => void;
  importData: (data: TaxReturnData) => void;
  resetData: () => void;
}
```

すべての操作関数を`useCallback`でメモ化し、`setData`の中でLocalStorageへの保存も同時に行っています。これにより「画面上の状態」と「永続化されたデータ」が常に一致する設計です。

ContextAPIを選んだ理由は、このアプリの状態更新パターンが比較的シンプル（CRUDが中心）で、コンポーネントのネストも深くないためです。過度に複雑な状態管理ライブラリを導入する必要はないと判断しました。

### 型定義 ── TypeScriptによる堅牢なデータモデル

確定申告のデータ構造を丁寧にTypeScriptの型として定義しました。

```
interface TaxReturnData {
  year: number;                          // 対象年度
  filingType: 'blue65' | 'blue10' | 'white';  // 申告種類
  incomes: IncomeEntry[];                // 収入リスト
  expenses: ExpenseEntry[];              // 経費リスト
  deductions: Deductions;                // 各種控除
  depreciationAssets: DepreciationAsset[];  // 減価償却資産
  homeOfficeRatios: HomeOfficeRatios;    // 家事按分比率
  consumptionTax: ConsumptionTaxSettings; // 消費税設定
  checklist: Record<string, boolean>;    // チェックリスト
}
```

経費カテゴリは12種類をユニオン型で厳密に定義しています。

```
type ExpenseCategory =
  | 'rent'           // 地代家賃
  | 'utilities'      // 水道光熱費
  | 'communication'  // 通信費
  | 'transportation' // 旅費交通費
  | 'advertising'    // 広告宣伝費
  | 'entertainment'  // 接待交際費
  | 'supplies'       // 消耗品費
  | 'outsourcing'    // 外注工賃
  | 'depreciation'   // 減価償却費
  | 'insurance'      // 損害保険料
  | 'tax_and_dues'   // 租税公課
  | 'other';         // その他
```

このように税務の概念をそのまま型に落とし込むことで、計算ロジックのバグを型レベルで防いでいます。

## 税額計算エンジンの実装

[![税額計算エンジン](https://qiita-user-contents.imgix.net/https%3A%2F%2Fraw.githubusercontent.com%2FClaudeCodeNews%2Fzenn-content%2Fmain%2Fimages%2Ftax-quest-portfolio%2Fsection2-tax-engine-v3.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=cc8a5a427b1a4509f5addd2ff8c19d92)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fraw.githubusercontent.com%2FClaudeCodeNews%2Fzenn-content%2Fmain%2Fimages%2Ftax-quest-portfolio%2Fsection2-tax-engine-v3.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=cc8a5a427b1a4509f5addd2ff8c19d92)

ここがこのアプリの一番の技術的な肝です。`tax-calculator.ts`に約400行の計算ロジックを実装しています。

### 所得税の累進課税（7段階）

令和7年分の所得税率テーブルをそのまま実装しました。

```
function calcIncomeTax(taxableIncome: number): number {
  if (taxableIncome <= 0) return 0;
  if (taxableIncome <= 1_950_000) return taxableIncome * 0.05;
  if (taxableIncome <= 3_300_000) return taxableIncome * 0.1 - 97_500;
  if (taxableIncome <= 6_950_000) return taxableIncome * 0.2 - 427_500;
  if (taxableIncome <= 9_000_000) return taxableIncome * 0.23 - 636_000;
  if (taxableIncome <= 18_000_000) return taxableIncome * 0.33 - 1_536_000;
  if (taxableIncome <= 40_000_000) return taxableIncome * 0.4 - 2_796_000;
  return taxableIncome * 0.45 - 4_796_000;
}
```

ポイントは「速算表」の形式を採用している点です。各段階で`税率 × 課税所得 - 控除額`という1行の計算式にしているので、段階ごとの差額計算が不要になり、コードの見通しが良くなっています。

### 減価償却計算 ── 定額法・定率法・月割り対応

フリーランスエンジニアがMacBookやモニターを買ったときの減価償却も自動計算します。

```
function calcDepreciationForAsset(asset: DepreciationAsset, year: number): number {
  // 取得年は月割り計算（取得月から12月まで）
  let monthsUsed = 12;
  if (acqYear === year) {
    monthsUsed = 13 - acqMonth; // 取得月を含む
  }

  if (asset.method === 'straight-line') {
    // 定額法: 取得価額 ÷ 耐用年数
    const annualDepreciation = Math.floor(cost / life);
    return Math.floor(annualDepreciation * monthsUsed / 12);
  } else {
    // 200%定率法: (期首帳簿価額) × (2 / 耐用年数)
    const rate = 2 / life;
    // ... 帳簿価額を年ごとに追跡して計算
  }
}
```

定率法では200%定率法を採用し、帳簿価額が保証額（取得価額の5%）を下回った時点で均等償却に切り替える処理も実装しています。取得年の月割り計算も対応しているので、「4月に買ったMacBookの今年の償却費はいくら？」にも正確に答えられます。

### 家事按分 ── 自宅兼事務所の経費配分

フリーランスが自宅で仕事をする場合、家賃や光熱費の一部を経費にできます。この「家事按分」機能も実装しました。

```
function calcExpensesWithHomeOffice(
  expenses: { category: string; amount: number }[],
  ratios: HomeOfficeRatios
): { total: number; adjustedByCategory: Record<string, number> } {
  const ratioMap = {
    rent: ratios.rent,           // 家賃の按分率
    utilities: ratios.utilities,  // 光熱費の按分率
    communication: ratios.communication, // 通信費の按分率
    insurance: ratios.insurance,  // 保険料の按分率
  };
  // 対象カテゴリのみ按分率を適用、それ以外は全額計上
}
```

### ふるさと納税シミュレーター

課税所得に基づいて、ふるさと納税の上限目安額をリアルタイムで計算します。

```
function calcFurusatoNozeiLimit(taxableIncome: number): number {
  const residentTaxIncome = Math.floor(taxableIncome * 0.1);
  const incomeTaxRate = getIncomeTaxRate(taxableIncome);
  // 上限額 = 住民税所得割額 × 20% ÷ (90% - 所得税率 × 1.021) + 2,000
  const limit = Math.floor(residentTaxIncome * 0.2 / (0.9 - incomeTaxRate * 1.021)) + 2_000;
  return Math.max(limit, 0);
}
```

この計算式は総務省の算出方法に基づいています。収入や経費を入力するたびにリアルタイムで更新されるので、「あとどれくらいふるさと納税できるか」が一目でわかります。

### 消費税 ── 3つの課税方式

インボイス制度対応として、消費税の計算も3パターン実装しています。

* 免税事業者: 前々年の売上が1,000万円以下の場合、消費税0円
* 簡易課税: 事業区分ごとのみなし仕入率で計算（IT・サービス業は第5種・50%）
* 本則課税: 売上消費税 - 仕入消費税の実額計算

## 自動アドバイス機能 ── AIっぽいけどルールベース

サマリー画面には「Tax Advisor's Tips」という自動アドバイス機能を実装しました。

```
function generateAdvice(data, result): Advice[] {
  const tips = [];
  // 白色→青色申告の切替提案
  if (data.filingType === 'white' && result.businessIncome > 0) {
    tips.push('青色申告に切り替えると最大65万円の控除。年間で約13〜20万円の節税効果！');
  }
  // 経費率チェック
  if (expenseRatio < 0.2) {
    tips.push(`経費率が${ratio}%と低め。計上漏れがないか確認を。`);
  }
  // 社会保険料の入力忘れ検出
  if (data.deductions.socialInsurance === 0) {
    tips.push('社会保険料控除が0円。国保・年金の支払額を入力しましたか？');
  }
  // iDeCo活用の提案、ふるさと納税上限超過警告 etc.
}
```

入力データのパターンから「よくあるミス」や「節税チャンス」を自動検出する仕組みです。AIではなくルールベースですが、実際に使ってみると「あ、iDeCo忘れてた」など、かなり実用的でした。

## e-Tax入力ガイド ── 申告書との対応表

実際にe-Taxで電子申告する際に迷わないよう、確定申告書第一表・第二表の項目番号と計算結果を対応させた一覧表を実装しました。

各数値にはCOPYボタンを付けており、ワンクリックでクリップボードにコピーしてe-Taxの入力欄に貼り付けられます。

確定申告書の「欄ア」「欄①」「欄㉖」といった項目番号を自動でマッピングしているので、e-Taxの画面とTAX QUESTを並べて見比べながら入力できます。

[![経費入力画面（Stage 2）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fraw.githubusercontent.com%2FClaudeCodeNews%2Fzenn-content%2Fmain%2Fimages%2Ftax-quest-portfolio%2Fscreenshot-expenses.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d766bb12987e60891d429e46e2f97683)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fraw.githubusercontent.com%2FClaudeCodeNews%2Fzenn-content%2Fmain%2Fimages%2Ftax-quest-portfolio%2Fscreenshot-expenses.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d766bb12987e60891d429e46e2f97683)

## データ永続化とインポート/エクスポート

### LocalStorageによる自動保存

```
function saveTaxData(data: TaxReturnData): void {
  localStorage.setItem('tax-return-2025', JSON.stringify(data));
}
```

操作するたびに自動保存されるので、ブラウザを閉じてもデータは残ります。また、データマイグレーション機能も実装しており、アプリのアップデートで新しいフィールドが追加されても古いデータが壊れません。

### CSVインポート ── 銀行明細を一括取り込み

銀行やfreeeからダウンロードしたCSVファイルを読み込んで、経費を一括登録できます。

```
function parseCSVToExpenses(csvText: string) {
  const header = lines[0].split(',');
  // 「日付」「摘要」「金額」「カテゴリ」などのヘッダーを自動検出
  const dateIdx = header.findIndex(h => /日付|date|取引日/i.test(h));
  const amountIdx = header.findIndex(h => /金額|amount|支出/i.test(h));
  // ヘッダー名の表記ゆれにも対応
}
```

ヘッダーの自動検出に正規表現を使い、「日付」「date」「取引日」といった表記ゆれにも対応しています。

### JSONエクスポート/インポート

全データをJSONファイルとしてエクスポートでき、来年の確定申告時にインポートして前年比較に使えます。

## UI/UXのこだわり

[![ゲーミフィケーションUI](https://qiita-user-contents.imgix.net/https%3A%2F%2Fraw.githubusercontent.com%2FClaudeCodeNews%2Fzenn-content%2Fmain%2Fimages%2Ftax-quest-portfolio%2Fsection3-ux.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d417114d776c489675b7a13a3a86083b)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fraw.githubusercontent.com%2FClaudeCodeNews%2Fzenn-content%2Fmain%2Fimages%2Ftax-quest-portfolio%2Fsection3-ux.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d417114d776c489675b7a13a3a86083b)

### ゲーミフィケーション

「確定申告」という堅いテーマを、4つのステージをクリアしていくゲーム風のUIにしました。

* Stage 1（収入）: 青
* Stage 2（経費）: 緑
* Stage 3（控除）: 紫
* Stage 4（結果）: オレンジ

各ステージの進捗状況（「3件入力済み」など）がカード上に表示され、どこまで終わったかが一目でわかります。

### リアルタイム計算

ダッシュボードには「現在の還付見込み」または「現在の納付見込み」が常に表示されます。数字を1つ入力するたびに金額が変わるので、「この経費を入れたら税額がこれだけ減った」がすぐに体感できます。

### レスポンシブ対応

スマホでもPCでも使えるよう、ハンバーガーメニュー付きのレスポンシブナビゲーションを実装しています。確定申告の書類を見ながらスマホで入力……というユースケースにも対応しています。

[![サマリー画面（Stage 4）](https://qiita-user-contents.imgix.net/https%3A%2F%2Fraw.githubusercontent.com%2FClaudeCodeNews%2Fzenn-content%2Fmain%2Fimages%2Ftax-quest-portfolio%2Fscreenshot-summary.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=b4f5ae59f5350962751f3c1a712b9deb)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fraw.githubusercontent.com%2FClaudeCodeNews%2Fzenn-content%2Fmain%2Fimages%2Ftax-quest-portfolio%2Fscreenshot-summary.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=b4f5ae59f5350962751f3c1a712b9deb)

## 実際に使ってみた結果

自分自身の令和7年分の確定申告で実際に使いました。

* 事業所得: 約1,000万円（SES案件）
* 給与所得: 約97万円（前職の端数分）
* 経費: 約110万円（外注費、技術書、通信費など）
* 申告種類: 白色申告

TAX QUESTで計算した結果をe-Taxに入力し、無事に申告完了。自動アドバイス機能で「来年は青色申告にした方がいい」「iDeCoを始めると年間16万円以上の節税になる」といった提案も受け、来年度の税務戦略の参考にもなりました。

## Claude Codeで開発して感じたこと

今回のTAX QUESTは、企画・設計・実装・テストの全工程でAnthropicのAIコーディングツール「Claude Code」を活用しました。

具体的には、以下のような使い方をしています。

* 設計フェーズ: 確定申告の税制ルール（累進課税の7段階、減価償却の定額法・定率法など）をClaudeに伝え、TypeScriptの型定義と計算ロジックの設計を壁打ち
* 実装フェーズ: 「所得税の速算表を純粋関数で実装して」「家事按分のロジックを追加して」といった指示で、コード生成→レビュー→修正のサイクルを高速で回す
* デバッグ: 「定率法の償却計算で保証額を下回った時の切り替えが正しくない」といった税務ドメイン特有のバグも、計算式の根拠を共有しながら修正

印象的だったのは、税務という専門ドメインのルールを正確にコードに落とし込む作業でClaude Codeが大きな力を発揮した点です。国税庁の税率表や計算方法を伝えれば、それをTypeScriptの関数として正確に実装してくれます。人間が手で書くと間違えやすい7段階の累進課税計算も、AIに任せることでミスなく実装できました。

一方で、最終的な税額の正確性は国税庁の公式ツールと突き合わせて自分で検証しています。AIを「万能な開発者」ではなく「優秀なペアプログラミングの相手」として使うのが、現時点での正しい付き合い方だと感じました。

## 今後の改善予定

* 青色申告決算書の自動生成（PDF出力）
* freee/マネーフォワードとのAPI連携
* 複数年度のデータ管理・推移グラフ
* PWA化（オフライン対応）
* 税制改正への自動追従（年度ごとのパラメータ外部化）

## まとめ

「自分が困っている課題を、自分の技術で解決する」というのが、エンジニアの一番の強みだと思います。

TAX QUESTは、Next.js + TypeScript + Tailwind CSSという比較的シンプルな技術スタックで、確定申告という複雑なドメインロジックをブラウザ完結で実装した事例です。税額計算、減価償却、家事按分、消費税、ふるさと納税シミュレーションまで、フリーランスエンジニアが確定申告で必要とする計算をほぼすべてカバーしています。

同じようにフリーランスで確定申告に苦しんでいるエンジニアの方、ぜひTAX QUESTを参考にしてみてください。あるいは、自分だけの確定申告ツールを作ってみるのも面白いかもしれません。「自分のための開発」が一番モチベーション続きますよ。

皆さんは確定申告、どうやって乗り切っていますか？ freee？ マネーフォワード？ それとも手書き？ ぜひコメントで教えてください。

---

参考リンク
