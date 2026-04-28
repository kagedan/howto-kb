---
id: "2026-04-27-ai開発にはaiテストそれとも個人開発80ツールのe2eでclaude-in-chromeを諦めた話-02"
title: "AI開発にはAIテスト？それとも…個人開発80ツールのE2EでClaude in Chromeを諦めた話"
url: "https://qiita.com/sakutto-panda/items/418a597cda25af3cb950"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "LLM", "TypeScript", "qiita"]
date_published: "2026-04-27"
date_collected: "2026-04-28"
summary_by: "auto-rss"
query: ""
---

[ぱんだツールズ](https://sakutto-panda.com) のツール数が 80 を超えた。AI と一緒に開発するようになってから、ツールを作る速度が自分で動作確認できる速度を完全に追い越した。共通コンポーネントを 1 行触ると 80 ツールが影響範囲に入るので、リファクタが怖くて手が止まる。

自動回帰テストを入れるしかなくなった。問題は **どう自動化するか** だった。AI で開発しているんだから、テストも AI に任せるのが筋なんじゃないか。ちょうど Anthropic から [Claude in Chrome](https://www.anthropic.com/news/claude-for-chrome) がリリースされたタイミングで、最初はこれを本命に検討した。

が、結論から言うと、Claude in Chrome は E2E 用途では諦めて Playwright に倒した。AI 開発時代だからこそ「AI にテストさせる」より「AI が書いたテストコードで自動化する」方が圧倒的にコスパが良かった、という話。

この記事では、Claude in Chrome を諦めた 4 つの理由と、最終的に Playwright でどう実装したかをまとめる。

https://sakutto-panda.com

## なぜ自動回帰テストが必要になったか

ぱんだツールズは PDF・CSV・画像・テキスト処理など、ブラウザ完結型のツールを 80 個以上公開している。アーキテクチャ上、共通の UI コンポーネント（ファイルアップロード・ダウンロードボタン・プレビュー表示）が大量のツールから参照されている。

これがどういう状況を生むかというと、

- ファイルアップロードの実装を 1 行触ると、80 を超えるツール全部が影響範囲になる
- 「アップロードしてダウンロードできる」という基本動線が壊れていないかは、本来全ツールで確認したい
- でも手動で 80 を超えるツールを開いて操作するのは現実的じゃない

ツール数が 30 個くらいまでは「気合で全部触る」でなんとかなっていた。50 個を超えたあたりから怪しくなり、80 個を超えて完全に破綻した。

最初に Claude Code に「リファクタしたついでに全ツールが動くか確認して」と頼んだら、トークンを大量消費した上で 5 ツールくらいランダムに開いて「動いてました」と返してきた。これじゃダメだ。

## Claude in Chrome に期待していたこと

Claude in Chrome は Chrome 拡張で、Claude にブラウザ操作を自然言語で任せられる。「このサイトでログインして XX してきて」みたいな指示が通る。

これを E2E テストに使えたら最強では、と思った。

期待していたこと:

- 自然言語で「全ツールのファイルアップロード機能が動くか確認して」と頼める
- スクリプトを書く時間がゼロ
- UI が変わってもセレクタの修正が要らない（人間が見る感覚で判定するから）
- 探索的に「壊れてそうなところない？」を任せられる

「個人開発でテスト書く時間がない」問題を一発で解決してくれるんじゃないかと期待した。

## 検討した結果、E2E 用途には合わないと判断した

結論から言うと、**回帰テストの番人としては合わない**と判断した。理由は 4 つ。

### 1. CI で毎 PR 回せない（ここが致命傷）

回帰テストの本質は「PR ごとに自動で回って、壊れたら止める」ことにある。GitHub Actions で毎 PR 自動実行できないと、そもそも「回帰テスト」として機能しない。

Claude in Chrome は現状、Chrome 拡張として個人のブラウザ上で動く。これを CI ランナー上で動かして、結果を PR にコメントさせる仕組みはない（少なくとも 2026 年 4 月時点では公式に整備されていない）。

「人間がローカルで思い立ったときに走らせるテスト」は、回帰テストとは呼ばない。それは賢い手動 QA だ。

### 2. 実行コストが現実的じゃない

仮に CI 連携できたとして、80 を超えるツール × 各数十秒の LLM 推論時間がかかる。Playwright なら全件で 1〜2 分で終わるところを、Claude in Chrome だと推論待ちで分単位かかる。

しかも全部 LLM 課金が乗る。1 PR ごとにこれを回す経済合理性はない。個人開発の月額予算は限られている。

### 3. 決定性が足りない

回帰テストで一番困るのは false negative（壊れてるのに通る）と false positive（壊れてないのに落ちる）の両方が起きること。LLM ベースのテストはどうしてもここが揺れる。

「ボタンが表示されてるはず → 表示されてないけど Claude は『動いてます』と返す」「軽微なレイアウトずれを Claude が『壊れてる』と判定する」みたいな揺れが入ると、テストへの信頼が崩れる。

回帰テストは「グリーンなら本当に壊れてない」と信じられてはじめて意味がある。グレーゾーンが多いテストは、結局誰も見なくなる。

### 4. そもそも用途がズレている

Claude in Chrome は「賢い手動 QA」「探索的テスト支援」としては強い。でも回帰テストは違う。回帰テストは退屈で機械的で決定的な作業を、PR ごとに何度も自動で回すためのものだ。

LLM の強みは「曖昧な状況での判断」だが、回帰テストに求めているのは「曖昧さの排除」だ。役割が真逆だった。

## Playwright に倒した実装

というわけで、Playwright で素直に書くことにした。Next.js + TypeScript の構成なので相性も良い。

### 構成

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e/tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html', { open: 'never' }]],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'npm run dev -- --port 3000',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
  globalSetup: './e2e/global-setup.ts',
})
```

ポイントは 3 つ。

- **chromium 単体**: マルチブラウザは個人開発ではオーバーキル。Chrome ベース 1 つで十分
- **webServer の自動起動**: `npm run test:e2e` だけで dev server 起動から後片付けまで完結
- **CI で retry 2**: ネットワーク揺れで落ちる軽微な fail を吸収

### スモークテストで全ツールを 40 行でカバー

スモークは「ページが開いて、JS エラーが出てない」だけを確認する。これが一番費用対効果が高い。

```typescript
// e2e/tests/smoke.spec.ts
import { test, expect } from '@playwright/test'

const ALL_TOOL_SLUGS = [
  'ai-bg-remove', 'ai-cli-commands', 'barcode-reader', 'base64',
  // ... 残りは実コード参照
]

for (const slug of ALL_TOOL_SLUGS) {
  test(`ページロード: /tools/${slug}`, async ({ page }) => {
    const errors: string[] = []
    page.on('pageerror', (err) => errors.push(err.message))

    await page.goto(`/tools/${slug}`)
    await page.waitForLoadState('networkidle')

    await expect(page).not.toHaveTitle(/404|Not Found/)

    const fatalErrors = errors.filter(
      (e) => !e.includes('gtag') && !e.includes('analytics')
    )
    expect(fatalErrors, `JSエラー: ${fatalErrors.join(', ')}`).toHaveLength(0)
  })
}
```

`gtag` と `analytics` のエラーは除外している。Cookie ブロッカーや広告ブロッカー由来のノイズで、本質的な fail じゃないから。これを入れないと PR が通らなくなる。

40 行で 80 を超えるツール全部のスモークが回る。リファクタ後にこれが全件通れば「少なくとも 404 にはなってない」が保証される。

### 機能テストはカテゴリ別に書く

ファイル処理系のツールは、「アップロードしてダウンロードボタンが出る」までを確認したい。これはカテゴリ別に分けて書いた。

```typescript
// e2e/tests/csv-tools.spec.ts
test.describe('CSV文字コード変換', () => {
  test('CSVをアップロードして変換できる', async ({ page }) => {
    await page.goto('/tools/csv-encoding')
    await uploadFile(page, FIXTURES.csvUtf8)
    await expect(page.locator('text=sample-utf8.csv')).toBeVisible()
    await expect(page.locator('button:has-text("ダウンロード")'))
      .toBeVisible({ timeout: 15000 })
  })
})
```

fixtures は `e2e/global-setup.ts` で毎回プログラム的に生成する。リポジトリにバイナリを置きたくなかったので、PDF は `pdf-lib` で 1 ページの空 PDF を、PNG/JPG は base64 デコードした 1x1 画像を起動時に書き出している。

```typescript
// e2e/global-setup.ts（抜粋）
const pdfDoc = await PDFDocument.create()
pdfDoc.addPage([595, 842])
const pdfBytes = await pdfDoc.save()
writeFileSync(join(FIXTURES_DIR, 'sample.pdf'), pdfBytes)

const csvUtf8 = '名前,年齢,メール\n田中太郎,25,...\n'
writeFileSync(join(FIXTURES_DIR, 'sample-utf8.csv'), csvUtf8, 'utf8')
```

最終的に 8 ファイル・約 790 行で、80 を超えるツールのスモーク + カテゴリ別機能テスト（CSV / PDF / 画像 / テキスト / 開発者ツール / 検索系 / その他）が揃った。

### Claude Code に書かせる前提なら E2E は量産できる

ここが今回一番の発見だった。

「E2E は書くのが面倒」というのが昔の常識だったが、Claude Code に書かせるならパターンが揃った Playwright のテストは恐ろしく量産が効く。実際、未テストだった 41 ツール分のテストを 1 コミットで追加できた。

```
c48014b feat: Playwright E2Eテスト環境を構築
e75cc94 test: 未テストツール41件のPlaywright E2Eテストを追加
```

最初の環境構築 1 コミットでテンプレが固まれば、あとは「このパターンで残り全部書いて」と Claude Code に頼むだけ。LLM の強みは「曖昧な状況での判断」じゃなく、ここでは「揃ったパターンの量産」のほうで使う。

これが Claude in Chrome を見送った決定打でもある。**「Claude にやらせる」より「Claude が書いたコードで自動化する」のほうが、回帰テストの用途では圧倒的にコスパが良かった。**

## じゃあ Claude in Chrome はどこで使うのか

E2E から見送ったとはいえ、Claude in Chrome 自体は便利だ。住み分けはこう考えている。

| 用途 | ツール |
|---|---|
| 回帰テスト（PR ごとに毎回） | Playwright |
| 新機能リリース直後の探索的検証 | Claude in Chrome |
| 「ユーザーが詰まる導線ない？」のふわっとしたチェック | Claude in Chrome |
| 複雑な手動 QA の代替 | Claude in Chrome |

Claude in Chrome は「賢いインターン」として手動 QA を巻き取ってくれる存在。Playwright は「決定的な番人」として PR を止める存在。求めている性質が違うので、両方使えばいい。

## 学び・まとめ

- 回帰テストには「決定性・CI 連携・実行コスト」の 3 点が必須で、LLM ベースのブラウザエージェントは現状ここが弱い
- 「Claude にやらせる」と「Claude が書いたコードで自動化する」は別物。回帰テストでは後者のほうが圧倒的に強い
- 個人開発でも 80 ツールを超えたら自動回帰は必須。Claude Code に書かせる前提なら Playwright の初期コストはかなり下がっている
- Claude in Chrome は探索的テスト・手動 QA 代替として使う。E2E と二者択一じゃなく両輪で使うのが正解だった

ぱんだツールズはこれで「リファクタが怖くない」状態になった。次に共通コンポーネントを触るときも、PR で全ツールのスモークが緑なら安心して merge できる。

:::note
**ぱんだツールズ** では PDF・画像・CSV・テキスト処理など、開発者向けの無料ツールを 80 個以上公開中。全部ブラウザ完結・登録不要・サーバー送信なし。よかったら覗いてみてください。
https://sakutto-panda.com
:::

---

> この記事は [Zenn](https://zenn.dev/sktt_panda/articles/e2e-playwright-vs-claude-in-chrome) にも同じ内容を投稿しています。
