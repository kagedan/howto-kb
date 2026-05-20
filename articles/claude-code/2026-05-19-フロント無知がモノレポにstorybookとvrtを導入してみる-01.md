---
id: "2026-05-19-フロント無知がモノレポにstorybookとvrtを導入してみる-01"
title: "フロント無知がモノレポにStorybookとVRTを導入してみる"
url: "https://zenn.dev/choshosu/articles/085487374c89f8"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "TypeScript", "zenn"]
date_published: "2026-05-19"
date_collected: "2026-05-20"
summary_by: "auto-rss"
query: ""
---

## はじめに

Storybook は社内デザインシステムや複数サービスを抱えるフロントエンド組織で使うものという印象が強く、業務でも個人開発でもこれまで触る機会がありませんでした。

ただ、個人開発でも UI コンポーネントを統一的に管理できる点は長期運用に効きそうだと思い、一度学んでみることにしました。本記事では pnpm workspace への Storybook 導入と、VRT (Visual Regression Test、ビジュアル回帰テスト) で UI 差分を検知できる状態にするところまでを扱います。

## Storybook とは

Storybook が登場する以前は、UI コンポーネントの状態を確認するために次のような手間がかかっていたとされています。

* ボタンの「disabled 状態」を見るために、その状態を再現するページをわざわざ開発環境に作る
* エラー時の UI を見るために、バックエンドをエラーで返すよう細工したり DevTools でネットワークを切断したりする
* コンポーネントが「アプリの中でしか動かない」状態になり、再利用性の議論が成立しない

それに対して Storybook は、コンポーネントを「アプリのコンテキストから独立させて開発・確認できる場」を提供します。これによってコンポーネント駆動開発 (Component-Driven Development, CDD) という小さい部品から積み上げる開発スタイルが現実的になりました。

2016 年に React 専用ツールとして登場し、その後 Vue / Angular / Svelte / Web Components などに対応を広げ、現在は事実上のフロントエンド業界標準と呼べる位置にあります。GitHub スター数は 8 万を超え、Shopify Polaris / IBM Carbon Design System / GitHub Primer などの公開デザインシステムが Storybook で公開されています。

### どんなケースで使うのか

| ケース | 何が嬉しいか |
| --- | --- |
| デザインシステムのカタログ化 | `Button` / `Input` / `Modal` 等の共通 UI を一覧化し、エンジニア・デザイナーが同じ画面で確認できる |
| コンポーネントの単体開発 | アプリを起動せず Controls で props を切り替えながら、長文 / 空データ / エラー等のエッジを確認できる |
| ビジュアル回帰テストの基盤 | Chromatic / percy / reg-suit と連携し、CSS 変更で別コンポーネントが崩れる事故を防げる |

逆に、小規模で再利用性の薄いアプリでは Storybook の導入コストに見合わないことが多く、採用はプロジェクトの寿命と共通化したい UI の量で判断する必要がありそうです。

## 実際に使ってみる

本記事ではpnpm workspaceへのStorybook導入から、VRTによるUI差分検知のCI化までやってみます。

### 前提プロジェクト

本記事の対象は次の構成のモノレポです。

* パッケージマネージャ: pnpm 10.33 (workspace + catalog)
* ビルドオーケストレーション: Turborepo 2.9
* フロントエンド: Vite 8 + React 19 + Tailwind CSS 4 + shadcn/ui
* 共通 UI: `packages/ui` 配下に Button などをまとめ、`apps/web` から `workspace:*` で参照

導入後のディレクトリ構成 (Storybook 関連のみ抜粋):

```
apps/
  storybook/
    .storybook/
      main.ts          # Story の対象とアドオンを宣言
      preview.ts       # 全 Story 共通の preview 設定 (Tailwind import 等)
    package.json
    tsconfig.json
    regconfig.json     # VRT で使う reg-suit の設定 (後述)
packages/
  ui/
    src/
      button.tsx
      button.stories.tsx   # 今回追加する Story
```

### 1. Storybook の初期化

本記事では手動でファイルを作成します。

まず `apps/storybook/.storybook` を作ります。

```
mkdir -p apps/storybook/.storybook
```

`apps/storybook/package.json` を新規作成します。

完成版

apps/storybook/package.json

```
{
  "name": "@your-org/storybook",
  "version": "0.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "storybook": "storybook dev -p 6006",
    "build-storybook": "storybook build"
  },
  "dependencies": {
    "@your-org/ui": "workspace:*",
    "react": "catalog:",
    "react-dom": "catalog:"
  },
  "devDependencies": {
    "@your-org/tsconfig": "workspace:*",
    "@storybook/addon-a11y": "catalog:",
    "@storybook/addon-docs": "catalog:",
    "@storybook/react-vite": "catalog:",
    "@tailwindcss/typography": "catalog:",
    "@tailwindcss/vite": "catalog:",
    "@types/react": "catalog:",
    "@types/react-dom": "catalog:",
    "storybook": "catalog:",
    "tailwindcss": "catalog:",
    "tw-animate-css": "catalog:",
    "typescript": "catalog:",
    "vite": "catalog:"
  }
}
```

`apps/storybook/tsconfig.json` を作ります。`packages/tsconfig/base.json` を継承しつつ、`.storybook/**/*` だけを include 対象にします。

完成版

apps/storybook/tsconfig.json

```
{
  "extends": "@your-org/tsconfig/base.json",
  "compilerOptions": {
    "target": "ES2023",
    "lib": ["ES2023", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "composite": false,
    "declaration": false,
    "declarationMap": false,
    "sourceMap": false,
    "noEmit": true,
    "types": ["vite/client"]
  },
  "include": [".storybook/**/*"]
}
```

### 2. catalog に Storybook 系を追記

`pnpm-workspace.yaml` の `catalog:` セクションに次を追記します。

pnpm-workspace.yaml

```
# Storybook
storybook: ^10.4.0
"@storybook/react-vite": ^10.4.0
"@storybook/addon-docs": ^10.4.0
"@storybook/addon-a11y": ^10.4.0
```

### 3. Storybook 設定ファイル

`apps/storybook/.storybook/main.ts` で Story の対象とアドオンを宣言します。`stories` を `packages/ui/src/**/*.stories.@(ts|tsx|mdx)` に向け、共通 UI の Story を吸い上げます。

apps/storybook/.storybook/main.ts

```
import tailwindcss from "@tailwindcss/vite";
import type { StorybookConfig } from "@storybook/react-vite";
import { mergeConfig } from "vite";

const config: StorybookConfig = {
  stories: ["../../../packages/ui/src/**/*.stories.@(ts|tsx|mdx)"],
  addons: ["@storybook/addon-docs", "@storybook/addon-a11y"],
  framework: { name: "@storybook/react-vite", options: {} },
  viteFinal: async (viteConfig) =>
    mergeConfig(viteConfig, {
      plugins: [tailwindcss()],
      server: { fs: { allow: ["../..", "../../.."] } },
    }),
};

export default config;
```

`apps/storybook/.storybook/preview.ts` で `@your-org/ui/styles` を import し、デザイントークンと Tailwind を全 Story に適用します。

apps/storybook/.storybook/preview.ts

```
import type { Preview } from "@storybook/react-vite";
import "@your-org/ui/styles";

const preview: Preview = {
  parameters: {
    controls: {
      matchers: { color: /(background|color)$/i, date: /Date$/i },
    },
  },
};

export default preview;
```

### 4. turbo.json にタスクを追加

Turborepo のタスクとして `storybook` / `build-storybook` を登録し、ルートから `pnpm turbo storybook` でも叩けるようにします。

turbo.json

```
"storybook": {
  "cache": false,
  "persistent": true
},
"build-storybook": {
  "outputs": ["storybook-static/**"]
}
```

### 5. 起動確認

```
pnpm install
pnpm -F @your-org/storybook storybook
```

<http://localhost:6006/> が開けば導入の半分は完了です。

この時点では `packages/ui` 配下に `*.stories.tsx` がまだ無いため、サイドバーに Story が並ばず `EmptyIndexError` の表示が出ます。次のステップで Button のストーリーを 1 つ追加すると、サイドバーに `Primitives/Button` が現れ、Controls タブから variant / size / disabled を切り替えられるようになります。

### 6. Button のストーリーを作る

`packages/ui/src/button.stories.tsx` を新規作成します。`packages/ui/src/button.tsx` は shadcn/ui で生成済みの Button を前提とします。

完成版

packages/ui/src/button.stories.tsx

```
import type { Meta, StoryObj } from "@storybook/react-vite";

import { Button } from "./button";

const meta = {
  title: "Primitives/Button",
  component: Button,
  tags: ["autodocs"],
  argTypes: {
    variant: {
      control: "select",
      options: ["default", "outline", "secondary", "ghost", "destructive", "link"],
    },
    size: {
      control: "select",
      options: ["default", "xs", "sm", "lg", "icon", "icon-xs", "icon-sm", "icon-lg"],
    },
    disabled: { control: "boolean" },
    children: { control: "text" },
  },
  args: {
    children: "Button",
    variant: "default",
    size: "default",
    disabled: false,
  },
} satisfies Meta<typeof Button>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};
export const Outline: Story = { args: { variant: "outline", children: "Cancel" } };
export const Secondary: Story = { args: { variant: "secondary", children: "Secondary" } };
export const Ghost: Story = { args: { variant: "ghost", children: "Ghost" } };
export const Destructive: Story = { args: { variant: "destructive", children: "Delete" } };
export const Link: Story = { args: { variant: "link", children: "Learn more" } };
export const SizeXs: Story = { args: { size: "xs", children: "Extra small" } };
export const SizeSm: Story = { args: { size: "sm", children: "Small" } };
export const SizeLg: Story = { args: { size: "lg", children: "Large" } };
export const Disabled: Story = { args: { disabled: true, children: "Disabled" } };
```

Storybook を起動した状態でファイルを保存すると、サイドバーに `Primitives/Button` が出現します。次の点を確認できます。

* Control タブで `variant` をドロップダウンから切り替えると、プレビューのボタンの見た目がリアルタイムで変わる

![](https://static.zenn.studio/user-upload/1fba96768712-20260519.png)

* サイドバーに `Default` / `Outline` / `Secondary` / `Ghost` / `Destructive` / `Link` / `SizeXs` / `SizeSm` / `SizeLg` / `Disabled` の 10 個の Story が並んでいる

![](https://static.zenn.studio/user-upload/1fb61a4c94ac-20260519.png)

ここまでで Storybook 本体の導入は完了です。次は VRT を載せて、UI の意図しない変化を自動で検知できるようにします。

## VRT (Visual Regression Test) の導入

Storybook の Story を対象に、UI の見た目が変わっていないかを自動で検出する仕組みを入れます。次の 3 つの道具を組み合わせます。

* `storycap`: Story を puppeteer-core で開いてスクリーンショットを取得
* `reg-suit`: 親ブランチのスナップショットと差分を比較し、レポートを生成
* `reg-publish-gcs-plugin`: ベースラインを Google Cloud Storage に保管

> モノレポ上での Storybook + VRT の構成は次の記事を参考にしました (出典: [Turborepo × pnpm で実現するモノレポ開発基盤 - ぐるなびエンジニアブログ](https://developers.gnavi.co.jp/entry/turborepo-pnpm/#5-Storybook-%E3%81%A8-VRT-%E5%9F%BA%E7%9B%A4))。

VRT のベースライン保管に使う GCS バケットは、Cloud Storage MCP サーバを Claude Code に渡して用意・動作確認まで委ねました。

<https://zenn.dev/choshosu/articles/70798aebd6edaa>

### 1. VRT 依存パッケージを追加

```
pnpm add -F @your-org/storybook --save-catalog -D storycap reg-suit reg-keygen-git-hash-plugin reg-publish-gcs-plugin reg-notify-github-plugin
```

catalog に次の行が追記されます。

```
storycap: ^5.0.1
reg-suit: ^0.14.5
reg-keygen-git-hash-plugin: ^0.14.5
reg-publish-gcs-plugin: ^0.14.4
reg-notify-github-plugin: ^0.14.5
```

### 2. スクリプトを追加

`apps/storybook/package.json` の `scripts` に capture コマンドを追加します。`--include "Primitives/Button/*"` で対象 Story を絞り、暫定的に Button のみを撮ります。

apps/storybook/package.json

```
"vrt:capture": "storycap --serverCmd \"storybook dev -p 6006 --ci --quiet\" http://localhost:6006 --include \"Primitives/Button/*\" --outDir __screenshots__"
```

リポジトリルートの `package.json` の `scripts` には、ワークスペース越しに叩くためのエイリアスを追加します。

package.json

```
"vrt:capture": "pnpm -F @your-org/storybook vrt:capture",
"vrt:run": "pnpm -F @your-org/storybook exec reg-suit run"
```

### 3. regconfig.json を作成

`apps/storybook/regconfig.json` を新規作成します。`workingDir` と `actualDir` は CWD (`apps/storybook`) からの相対パスです。`reg-publish-gcs-plugin` でバケット名と `pathPrefix` を指定します。

apps/storybook/regconfig.json

```
{
  "core": {
    "workingDir": ".reg",
    "actualDir": "__screenshots__",
    "thresholdRate": 0.02,
    "addIgnore": true,
    "ximgdiff": { "invocationType": "client" }
  },
  "plugins": {
    "reg-keygen-git-hash-plugin": {},
    "reg-publish-gcs-plugin": {
      "bucketName": [バケット名],
      "pathPrefix": "your-monorepo"
    }
  }
}
```

### 4. .gitignore に VRT 成果物を追加

スクリーンショットと reg-suit の作業ディレクトリはローカル成果物として扱い、ベースラインは GCS に置きます。

`.gitignore` の末尾に追記します。

.gitignore

```
# VRT (storycap + reg-suit)
.reg/
apps/storybook/__screenshots__/
apps/storybook/storybook-static/
```

### 5. ローカル実行時の Chromium について

storycap は内部で `puppeteer-core@^9.0.0` を使うため、Chromium バイナリは別途用意する必要があります。ローカル Windows 環境では、storycap が `C:\Program Files\Google\Chrome\Application\chrome.exe` の Chrome を自動検出して動作するので、Chrome がインストール済みなら追加作業は不要です (storycap の実行ログにも自動検出した旨が出ます)。

CI 側で自動検出に頼ると Chrome のバージョンが固定できないため、`browser-actions/setup-chrome@v1` で Chrome stable を入れ、`PUPPETEER_EXECUTABLE_PATH` 環境変数で puppeteer-core にバイナリのパスを明示します (後述のサンプル workflow 参照)。

### 6. 初回ベースラインを取得

```
pnpm vrt:capture
pnpm vrt:run
```

実行結果の要点は次の通りです。

* storycap: `Found 10 stories. ... Screenshot was ended successfully in 16165 msec capturing 10 PNGs.`
* reg-suit: `Changed items: 0 / New items: 10 / Passed: 0`
* Snapshot key: `<commit-sha>` (= 現 HEAD のコミットハッシュ)
* GCS path: `gs://[バケット名]/your-monorepo/<commit-sha>/`

storycap が裏で `storybook dev` を起動 → Button stories 10 件を撮影 → `__screenshots__/Primitives/Button/*.png` に出力します。続けて `reg-suit run` を実行すると、`reg-keygen-git-hash-plugin` が「previous snapshot 無し」と判定し、全 10 件を新規扱いで GCS にアップロードします (PNG 10 + レポート 4 = 計 14 オブジェクト)。

### 7. 差分検出の動作確認

Button の色を意図的に変えて再度 `pnpm vrt:capture && pnpm vrt:run` を回すと、reg-suit のレポートに `Changed items` が出ます。レポート HTML を開くと、ベースラインと現状の差分が並べて表示されます。

### 8. CI 化

GitHub Actions で `pnpm vrt:capture` → `pnpm vrt:run` を回します。PR ごとに自動でベースライン取得と差分検出が走るようになり、UI 変更の影響を視覚的にレビューできます (`reg-notify-github-plugin` を入れているので、差分が出た PR には自動でコメントが投稿されます)。

サンプル

.github/workflows/ci\_storybook.yaml

```
name: ci_storybook

# Visual Regression Testing for Storybook.
# - storycap で apps/storybook の Story 群をスクリーンショット撮影
# - reg-suit で過去 baseline (GCS: [バケット名]) と差分比較
# - PR ブランチ: merge-base コミットの baseline と比較
# - main へ push: 新しい baseline を GCS に publish

on:
  pull_request:
    paths:
      - "packages/ui/**"
      - "apps/storybook/**"
      - "pnpm-lock.yaml"
      - "pnpm-workspace.yaml"
      - ".github/workflows/ci_storybook.yaml"
  push:
    branches: [main]
    paths:
      - "packages/ui/**"
      - "apps/storybook/**"
      - "pnpm-lock.yaml"
      - "pnpm-workspace.yaml"
      - ".github/workflows/ci_storybook.yaml"
  workflow_dispatch:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read
  id-token: write

jobs:
  vrt:
    name: Storybook VRT
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup pnpm
        uses: pnpm/action-setup@v4
        with:
          version: 10.33.2

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: pnpm

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      # storycap は puppeteer-core を使うので Chromium を別途用意する必要がある。
      # ubuntu-latest には google-chrome がプリインストールされているが、バージョン揺らぎを避けるため明示的にセットアップ。
      - name: Setup Chrome for storycap
        id: setup-chrome
        uses: browser-actions/setup-chrome@v1
        with:
          chrome-version: stable

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          service_account: ${{ secrets.GCP_IAM_SERVICE_ACCOUNT }}
          workload_identity_provider: ${{ secrets.GCP_IAM_WORKLOAD_IDENTITY_PROVIDER }}

      - name: Capture screenshots (storycap)
        env:
          # storycap は内部で puppeteer-core を使うため、Chromium バイナリのパスを明示
          PUPPETEER_EXECUTABLE_PATH: ${{ steps.setup-chrome.outputs.chrome-path }}
        run: pnpm vrt:capture

      - name: Run reg-suit (compare + publish)
        run: pnpm vrt:run

      - name: Upload reg-suit working dir
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: reg-suit-report-${{ github.run_id }}
          path: apps/storybook/.reg/
          retention-days: 14
          if-no-files-found: warn
```

※ GitHub Actions では CI 実行アカウントに VRT 用の Cloud Storage へのオブジェクト管理者権限が必要です。

## まとめ

Storybook の意義の整理から、モノレポへの導入と VRT のベースライン取得・CI 化までを通しました。所感は次の通りです。

* アプリのコンテキストから独立してコンポーネントを開発できる体験はGood。エラー時やローディング時など、頻繁には起きない状態の UI を Controls からすぐ再現できるのが特にありがたいです。
* VRT で UI の変更を PR レビュー時に視覚的に検知できる仕組みは、長期運用で効きそうです。CSS の小さな変更が別コンポーネントに波及していないかを毎回目視で確認する手間がなくなります。
* 一方で、短期的・小規模なプロジェクトでは導入コストに見合わないと感じる場面もあります。`apps/storybook` の追加に伴う catalog / tsconfig / turbo.json の調整など、初期コストがそれなりにかかるためです。
* このあたりはプロジェクトの寿命と共通化したい UI コンポーネントの量で採用を判断するのがよさそうです。

本記事がどなたかの参考になれば嬉しいです！
