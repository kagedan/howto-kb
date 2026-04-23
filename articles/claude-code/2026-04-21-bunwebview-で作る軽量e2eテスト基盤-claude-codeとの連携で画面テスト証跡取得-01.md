---
id: "2026-04-21-bunwebview-で作る軽量e2eテスト基盤-claude-codeとの連携で画面テスト証跡取得-01"
title: "Bun.WebView で作る軽量E2Eテスト基盤 ― Claude Codeとの連携で画面テスト・証跡取得まで自動化"
url: "https://zenn.dev/omeroid/articles/df728f3a985b8e"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "zenn"]
date_published: "2026-04-21"
date_collected: "2026-04-22"
summary_by: "auto-rss"
---

## はじめに

Vue 3 + Element Plus で構築した業務システムのE2Eテストを、**Bun + Bun.WebView** というミニマルな構成で実現しました。Playwright や Cypress のような大型フレームワークではなく、Bun本体に組み込まれたブラウザ自動化APIだけで動く軽量アプローチです。

さらに **Claude Code** と組み合わせることで、テスト作成の自動化、スクリーンショットのAIレビュー、リリースごとの証跡管理まで一気通貫で回せる仕組みを紹介します。

## なぜ Bun なのか

### Anthropic が Bun を買収した

2025年12月、[Anthropic が Bun を買収しました](https://bun.com/blog/bun-joins-anthropic)。Claude Code は内部的に [Bun ランタイム上で動作する TypeScript モノリス](https://newsletter.pragmaticengineer.com/p/how-claude-code-is-built)として構築されており、Bun は Claude Code のインフラの中核を担っています。

> Claude Code ships as a Bun executable to millions of users  
> ― [Anthropic公式発表](https://www.anthropic.com/news/anthropic-acquires-bun-as-claude-code-reaches-usd1b-milestone)

この買収により、Bun は「高速なJSランタイム」から「AIコーディングツールのプラットフォーム」へと位置づけが変わりました。Claude Code のスキルやフックからBunのテストランナーやプロセス制御を直接使えるため、**AIエージェントとE2Eテストの統合が自然にできる**のがBunを選ぶ最大の理由です。

### Playwright との比較

[Playwright は2026年現在、E2Eテストのデファクトスタンダード](https://dev.to/jake_kim_bd3065a6816799db/playwright-vs-cypress-2026-which-e2e-testing-framework-should-you-use-1kmo)です。クロスブラウザ対応、強力なセレクタ、豊富なCI統合など、汎用E2Eフレームワークとしては間違いなく最強です。

しかし、社内業務システムのステージング検証には**オーバースペック**な面があります:

| 観点 | Playwright | Bun.WebView |
| --- | --- | --- |
| **セットアップ** | ブラウザバイナリDL（[CI上で3〜4分](https://github.com/microsoft/playwright/issues/23388)、[低速回線では40分以上](https://github.com/microsoft/playwright/issues/14434)） | Bun本体に組み込み済み。追加DL不要 |
| **ブラウザ** | Chromium/Firefox/WebKit（クロスブラウザ） | WKWebView（macOS）/ Chrome（クロスプラットフォーム） |
| **テストAPI** | 独自API（`page.locator()`, `expect(locator).toBeVisible()` 等）の学習が必要 | `view.click()`, `view.evaluate()` のシンプルなAPI |
| **ストアアクセス** | [`page.evaluate()`](https://playwright.dev/docs/evaluating) 経由で可能だが煩雑 | `view.evaluate()` で直接実行。Piniaストアを自然に操作 |
| **並列実行** | [ワーカー設定が必要](https://playwright.dev/docs/test-parallel) | 各テストプロセスが独自のWebViewインスタンスを持つ |
| **CI/CD** | [Dockerイメージ推奨](https://playwright.dev/docs/docker) | macOSランナーで直接実行 |
| **AIエージェント連携** | 想定されていない | Claude Code と同じBunランタイムで自然に統合 |

**要するに**: クロスブラウザ対応が不要で、社内ツールのステージング検証やリリース証跡の取得が目的なら、Playwrightの複雑さは不要です。Bun.WebView なら追加パッケージなしでE2Eテストを書き始められます。

## Bun.WebView とは

[Bun v1.3.12](https://bun.com/blog/bun-v1.3.12) で、ヘッドレスブラウザ自動化API **[`Bun.WebView`](https://bun.com/reference/bun/WebView)** がBun本体に追加されました。macOSではシステム標準のWKWebView、その他のプラットフォームではChrome DevTools Protocolを使い、**外部ブラウザのダウンロードなし**でブラウザ操作ができます。

```
const view = new Bun.WebView({ width: 1920, height: 1080 })
await view.navigate("https://example.com")
await view.click("input[name='email']")
await view.type("hello")
const title = await view.evaluate("document.title")
const png = await view.screenshot({ format: "png" })
await Bun.write("screenshot.png", png)
view.close()
```

**特徴:**

* **Bun本体に組み込み**: 追加パッケージなし。Playwright風の自動待機を備え、[OS-levelイベント（`isTrusted: true`）](https://bun.com/blog/bun-v1.3.12)として操作を送信
* **`evaluate()`** でページ内の任意のJavaScriptを実行 → Vue/React のストアに直接アクセス可能
* **軽量**: WKWebView はOS標準、Chromeは既存インストールを利用

## テストの構成

```
e2e/
├── .env.e2e           # 認証情報
├── helpers.ts         # 共通ヘルパー（Bun.WebView操作をラップ）
├── runner.ts          # 並列実行ランナー
├── GNUmakefile
├── stories/           # テストファイル
│   ├── screens-*.test.ts    # 画面表示テスト
│   ├── crud-*.test.ts       # CRUDテスト
│   └── flow-*.test.ts       # 業務フローテスト
├── screenshots/       # スクリーンショット出力
└── reports/           # テスト結果JSON
```

`helpers.ts` が `Bun.WebView` のAPIをE2Eテスト向けにラップします。テストファイルからは `startBrowser()`, `login()`, `clickMenuItem()` のような高レベル関数を呼ぶだけです。

## 画面表示テスト ― 全画面を宣言的にテスト

画面定義を配列で書くだけで、一覧→詳細→全タブ→スクロール→エラー検知を自動実行します。

```
const screens: ScreenDef[] = [
  {
    menuText: "メンバー",
    expectedUrl: "/admins/members/",
    prefix: "admin_member",
    detailPath: "/admins/members/{id}/detail",
    tabs: [
      { label: "詳細", ssName: "detail" },
      { label: "権限", ssName: "permissions" },
    ],
  },
  {
    menuText: "グループ",
    expectedUrl: "/admins/groups/",
    prefix: "admin_group",
    detailPath: "/admins/groups/{id}/detail",
    tabs: [
      { label: "詳細", ssName: "detail" },
      { label: "メンバー一覧", ssName: "members" },
    ],
  },
]

test("全画面を表示し、詳細ペインとタブを確認する", async () => {
  await startBrowser()
  await login()
  await testScreens(screens)
}, 120000)
```

`testScreens()` は内部で以下を自動実行します:

1. サイドメニューをクリック → URL検証 → スクリーンショット
2. Piniaストアから実在するレコードIDを動的取得 → 詳細ページ遷移
3. 全タブを順にクリック → 各タブのスクリーンショット
4. エラー通知（`.el-notification` のERROR）を検知 → テスト失敗

### ポイント: Piniaストアへの直接アクセス

詳細ページのIDを取得する際、DOM操作ではなく **Piniaストアに直接アクセス** しています:

```
const id = String(await view.evaluate(`(() => {
  const pinia = document.querySelector('#app')
    .__vue_app__.config.globalProperties.$pinia;
  const store = pinia._s.get('member');
  return store.list?.[0]?.id || '';
})()`))
```

これにより「テーブルの1行目をクリック」のような脆弱なセレクタに依存せず、確実にデータを取得できます。

## CRUDテスト ― Piniaストアを操作して登録→更新→削除

CRUDテストでは、ダイアログのフォームに値を入力する代わりに **Pinia `$patch` でストアのformDataを直接セット** します。

```
test("取引先の登録→確認→更新→確認→削除", async () => {
  await startBrowser()
  await login()
  await clickMenuItem("顧客管理")

  // 1. 登録ダイアログを開いてformDataをセット
  await clickRegisterButton()
  await patchFormData("customer", {
    name: "E2E_TEST_CUSTOMER",
    nameIndex: "e2e_test",
  })
  await clickDialogSubmit("登録")
  expect(await getNotification()).toContain("SUCCESS")

  // 2. フィルタ検索で登録確認
  await searchByFilter("customer", "fuzzyName", "E2E_TEST_CUSTOMER")
  expect(await tableContainsText("E2E_TEST_CUSTOMER")).toBe(true)

  // 3. 更新
  await storeAction("customer", "updateData", { name: "E2E_UPDATED" })
  expect(await getNotification()).toContain("SUCCESS")

  // 4. 削除
  await storeAction("customer", "deleteData")
  expect(await getNotification()).not.toContain("ERROR")
}, 60000)
```

### なぜストア直接操作なのか

Element Plus の `el-select` や `el-date-picker` は内部構造が複雑で、セレクタでの操作が不安定です。ストアの `$patch` を使えば:

* **カスタムコンポーネントの内部構造に依存しない**
* **テストが短く書ける**（click → type → click の連鎖が不要）
* **どのフィールドに何を入れたか明確**

ダイアログの「登録」ボタンクリックは実際のUI操作なので、バリデーションやAPI呼び出しは本物が走ります。ただし `$patch` は `input` イベントを発火しないため、フィールド単位のリアルタイムバリデーション（入力中のエラー表示等）はバイパスされます。テストの目的が「APIへの登録→結果確認」であれば問題ありませんが、入力バリデーション自体をテストしたい場合は `view.type()` でのUI入力が必要です。

## フローテスト ― 画面をまたぐ業務フローの検証

複数画面をまたぐ業務フロー（申請→承認→処理→完了）もテストできます。

```
test("申請→承認→処理→完了の一気通貫フロー", async () => {
  // Phase 1: 申請登録
  await navigate("/workflow/applications/")
  await clickRegisterButton()
  await patchFormData("application", { ... })
  await clickDialogSubmit("登録")
  expect(await getNotification()).toContain("SUCCESS")

  // Phase 2: 承認処理（申請詳細から）
  await navigate(`/workflow/applications/${id}/detail`)
  // Piniaストアのメソッドを直接呼び出し
  await view.evaluate(`(() => {
    const store = pinia._s.get('application');
    store.prepareFormData(store.detail);
    store.approve();
  })()`)

  // Phase 3: 処理登録（承認済みデータを使用）
  // ...

  // Phase 4: 完了処理（前ステップの結果を使用）
  // ...
}, 600000) // 4画面をまたぐフローのため10分に設定
```

タイムアウト600秒は長く見えますが、4つの画面遷移・データ登録・検証・クリーンアップを含むフローテストでは必要な値です。個別のCRUDテストは60秒、画面表示テストは120秒で十分です。

ストアのメソッド（`approve()`, `completeProcess()` 等）を `view.evaluate()` で直接呼び出すことで、複雑なUI操作をバイパスしつつ、実際のAPI呼び出しは本物が走ります。

## 並列実行

`runner.ts` がテストファイルを検出し、各ワーカーを独立した `bun test` プロセスとして並列実行します。各プロセスが自前の `Bun.WebView` インスタンスを持つため、セッション管理の仕組みは不要です。

```
📋 20 stories found (concurrency: 3)

▶ [ユーザー管理] メンバー CRUD
▶ [顧客] 顧客マスタ CRUD
▶ [マスタ] カテゴリ CRUD
✅ [ユーザー管理] メンバー CRUD (39.7s)
▶ [認証] ログイン→ダッシュボード
✅ [顧客] 顧客マスタ CRUD (34.2s)
▶ [ユーザー管理] 全画面表示
...
✅ 20 passed / 0 failed (total: 420.3s)
```

1件完了するたびに次のストーリーを即座に投入するストリーミング方式です。デフォルト3並列で、**20ストーリー・269枚のスクリーンショットを約7分**で実行します。Playwrightのブラウザ起動やDockerコンテナの立ち上げが不要なぶん、セットアップ込みでもトータルの実行時間が短いのが特徴です。

## レポートと差分検出

テスト結果をJSONで保存し、前回のリリースタグと比較してregression/fixedを自動検出します。

```
make e2e-report  # テスト実行 + スクリーンショットアップロード + GitHub Issue投稿
```

GitHub Issueに投稿されるレポート:

| # | カテゴリ | ストーリー | 前回 | 今回 | 変化 |
| --- | --- | --- | --- | --- | --- |
| 1 | ユーザー管理 | メンバー CRUD | ✅ | ✅ | - |
| 2 | ワークフロー | 申請→承認フロー | ✅ | ❌ | 🔴 regression |
| 3 | マスタ | 一覧画面表示 | ❌ | ✅ | 🟢 fixed |

スクリーンショットはGitHub Releaseアセットにアップロードされ、Issueから直接参照できます。

## Claude Code との連携

ここからがこの構成のユニークなポイントです。E2Eテスト基盤を **Claude Code のスキルとして統合** することで、テスト作成・実行・レビューのサイクルを自動化しています。

### 1. テストの自動生成（/e2e-story）

Chrome DevTools Recorderで操作を録画し、JSONエクスポートしたものをClaude Codeに渡すだけでテストファイルを生成します。

```
# 1. Chromeで操作を録画 → JSONエクスポート
# 2. Claude Codeで:
/e2e-story recordings/detail-view.json 詳細画面表示 ワークフロー
```

Recorderの操作ステップ（click, type, navigate）がBun.WebView APIの呼び出しに変換され、適切な待機時間やスクリーンショットが挿入されたテストファイルが生成されます。

### 2. スクリーンショットのAIレビュー（/e2e-review）

テスト実行後、前回と今回のスクリーンショットをClaudeが視覚的に比較して3段階評価します。

Claudeが各画面のスクリーンショットを見て:

* 🟢 **問題なし** ― データの差異のみ（日付、件数の変化）
* 🟡 **要確認** ― UIに変化あり（カラム追加、ボタン変更）
* 🔴 **異常** ― レイアウト崩壊、エラー表示、白画面

動的データ（日付、件数）の変化はUI変更とみなさず、意味のある変更のみを検出します。結果はGitHub Issueにコメントとして投稿されます。

### 3. PRの画面検証（/verify）

PRの変更内容を分析し、影響する画面を `Bun.WebView` で実際に開いてスクリーンショットを取得します。

これにより「PRの変更が画面にどう影響するか」の証跡を自動で取得できます。

### 4. テスト作成時のバグ発見

E2Eテストを作る過程で、Claude Code がプロダクションコードのバグや設計上の問題を発見することがあります。実際に今回のテスト作成で見つかった問題:

* **API出力型の不一致**: List型にあるIDフィールドがDetail型になく、フロントエンドで`undefined`になるケースがあった
* **SUCCESS通知の欠落**: ある処理画面だけSUCCESS通知が表示されない実装漏れ
* **デッドコード**: UIには存在しないタブの分岐がストアにあり、テストから到達できないコードパスがあった

テストを書くこと自体が、コードベースのレビューとして機能しています。

## リリース証跡としての活用

E2Eテストの結果はそのまま **リリース証跡** として使えます。

1. **GitHub Release** にタグごとのスクリーンショットを保存
2. **GitHub Issue** にテスト結果レポートを蓄積
3. **前回比較** でregressionを検出

「v1.2.3リリース時にこの画面はこう表示されていた」をスクリーンショットで証明でき、問題発生時に「いつから壊れたか」を特定できます。

## まとめ

| 観点 | Playwright/Cypress | Bun.WebView |
| --- | --- | --- |
| セットアップ | ブラウザバイナリDL | Bun本体に組み込み済み |
| 並列実行 | 設定が必要 | 各プロセスが独自インスタンス |
| フレームワーク依存 | 独自API学習 | Bun test + シンプルなAPI |
| ストアアクセス | `evaluate` 経由で煩雑 | `evaluate` で直接操作 |
| CI/CD | Docker必要 | macOSランナーのみ |
| AI連携 | なし | Claude Codeスキルで統合 |

**トレードオフ**: macOSではWKWebView、それ以外ではChrome必須。クロスブラウザテストは不可。社内ツールやステージング検証には十分で、Playwrightほどの汎用性は不要なケースに向いています。

Bunの高速な起動と `Bun.WebView` のゼロセットアップを活かし、20ストーリーを7分で実行。Claude Codeとの連携でテスト作成・レビュー・証跡管理まで自動化できる構成は、特に業務システムの品質管理に効果的です。

## 参考リンク
