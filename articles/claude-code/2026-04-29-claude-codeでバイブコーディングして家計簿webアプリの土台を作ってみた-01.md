---
id: "2026-04-29-claude-codeでバイブコーディングして家計簿webアプリの土台を作ってみた-01"
title: "Claude Codeでバイブコーディングして家計簿Webアプリの土台を作ってみた"
url: "https://qiita.com/Java_Kobayashi/items/7d1ee30fe24c49173ca9"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "qiita"]
date_published: "2026-04-29"
date_collected: "2026-05-01"
summary_by: "auto-rss"
---

# はじめに
Claude Codeが最近流行っているということで、そろそろ触ってみなければ。
ということで、簡単な家計簿Webアプリの土台を作成してみようと思います。
※土台 = ローカル環境で動くものを作るという意味。

なお、この記事ではWindows PCで作業します。

# Claude Codeインストール
まずはClaude Codeをインストールしましょう。
とはいってもインストール方法すら分からないので、ChatGPTに聞いてみます。
```
WindowsでClaude Codeによるバイブコーディングを始める方法について、手順を追って説明して
```

ざっくり以下のような答えが返ってきましたので、PowerShellを使用して言われた通りインストールを進めます。
```
## Claude Code インストール
irm https://claude.ai/install.ps1 | iex

## Claude Code インストール確認、バージョンが表示されればOK
claude --version
```

VS Codeを使用してバイブコーディングするため、下記の手順も実施しました。
```
## VS Codeを開き、拡張機能検索で「Claude Code」を検索してインストール
```


# 家計簿Webアプリ作成開始
## 作成準備
Claude Codeのインストールが完了しました。
続いて家計簿Webアプリを作成しましょう。
作成の進め方もChatGPTに聞いてみます。
```
windows / Claude Codeを使用して、家計簿管理のWebアプリケーションを作りたいです。 この時、Claude Codeの構成、プロンプトなど教えて
```

以下のような回答が返ってきました。
まずは使用する技術についてです。
```
家計簿アプリなら、最初はこの構成が扱いやすいです。

フロントエンド: Next.js + TypeScript
UI: Tailwind CSS
DB: SQLite
ORM: Prisma
入力検証: Zod
グラフ: Recharts
フォーム: React Hook Form
実行環境: Windows + PowerShell + Claude Code
```
今回はWebアプリの土台作成が目的なので、技術選定はこの構成に従って進めます。


次に以下の指示に従い、プロジェクトを作成します。
```
PowerShellで以下を実行します。

mkdir kakeibo-app
cd kakeibo-app

npx create-next-app@latest . --ts --tailwind --eslint --app --src-dir --import-alias "@/*"

npm install @prisma/client prisma zod react-hook-form @hookform/resolvers date-fns lucide-react recharts
npx prisma init --datasource-provider sqlite

git init
```

そしていよいよClaude Codeを起動します
```
その後、Claude Codeをプロジェクト直下で起動します。

claude
```
上記はVS Codeの統合ターミナルでも、通常のPowerShellでも実行できます。
なお、サインインが求められた場合はブラウザで認証を実施してください。
※2026年4月現在、無料プランではClaude Codeを利用できないため、個人利用ではProプラン以上を契約しておきましょう。

## 作成開始
ChatGPTが回答した以下プロンプトから、Claude Codeに守ってほしいルールをCLAUDE.mdに定義します。
```
プロジェクト直下に CLAUDE.md を作って、以下を貼ってください。

# 家計簿Webアプリ開発ルール

## プロジェクト概要
このプロジェクトは、個人利用向けの家計簿管理Webアプリです。
収入・支出・カテゴリ・月別予算・集計レポートを管理します。

## 技術スタック
- Framework: Next.js App Router
- Language: TypeScript
- Styling: Tailwind CSS
- Database: SQLite
- ORM: Prisma
- Validation: Zod
- Forms: React Hook Form
- Charts: Recharts
- Package manager: npm

## 開発コマンド
- `npm run dev`: 開発サーバー起動
- `npm run build`: 本番ビルド確認
- `npm run lint`: lint確認
- `npx prisma migrate dev`: DBマイグレーション
- `npx prisma studio`: DB確認

## 実装方針
- まずMVPを優先する。
- 過剰な抽象化を避ける。
- TypeScriptの型安全性を重視する。
- 金額は円単位の整数 `Int` で扱う。
- 日付処理は `date-fns` を使う。
- DBアクセスは `src/lib/db.ts` に集約する。
- 入力検証スキーマは `src/lib/validations.ts` に集約する。
- APIレスポンスは成功時と失敗時の形式を統一する。

## UI方針
- 日本語UIにする。
- スマホ幅でも使えるレスポンシブUIにする。
- 主要画面は以下:
  - ダッシュボード
  - 取引一覧
  - 取引登録・編集
  - カテゴリ管理
  - 月別予算
  - レポート

## セキュリティ・プライバシー
- `.env` や秘密情報を表示・変更しない。
- 個人の家計データを外部APIに送信しない。
- ローカルSQLiteを基本とする。
- CSV出力時はユーザー操作でのみ実行する。

## Claude Codeへの作業ルール
- 大きな変更の前に必ず実装計画を提示する。
- 1回の作業では1つの機能単位に集中する。
- 変更後は `npm run lint` と `npm run build` を実行する。
- エラーが出た場合は、原因、修正内容、再発防止を説明する。
- 既存機能を壊す可能性がある変更では、先に影響範囲を説明する。
```

次に、ChatGPTが回答した以下プロンプトを、起動したClaude Codeのチャット欄に貼り付けて実装開始です。
```
このプロジェクトは個人利用向けの家計簿Webアプリです。

まず実装せず、現在のファイル構成を確認したうえで、Next.js + TypeScript + Prisma + SQLiteで作るMVPの実装計画を出してください。

MVPに含める機能:
- 収入・支出の登録
- 取引一覧
- 取引の編集・削除
- カテゴリ管理
- 月別の収支サマリー

制約:
- 日本語UI
- 金額は整数の円で扱う
- DBはSQLite
- 過剰な設計は避ける
- まずはログイン不要 
```

Claude Codeが「実装を開始していいですか？」と聞いてくるので、「進めていいよ」と答えると自動で実装開始。
その後、ファイルの作成・編集やコマンド実行の許可を求められるので、内容を確認して承認します。

15分ほどしてClaude Codeから実装完了の返答があったので、
```
npm run dev
```
を実行して、ターミナルに表示されたURLにアクセスします。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/263050/e67dca0a-d050-4cc7-98bc-534f69f775ed.png)

おお！できてる！
非常にシンプルな作りですが、以下の通り家計簿管理に必要な最低限のことはできそうです。
- ダッシュボード...月ごとの収支サマリが参照可能
- 取引一覧...月ごとの各収支が参照可能
- 取引登録...収支の登録が可能
- カテゴリ...収支登録時のカテゴリを管理

# さいごに
はじめてClaude Codeを触ってみましたが、想像以上に簡単かつスピーディにWebアプリケーション（の土台）が作れました。
次はログイン機能など、Webサイト上に公開する上で必要な実装も進めていこうと思います。

おわり
