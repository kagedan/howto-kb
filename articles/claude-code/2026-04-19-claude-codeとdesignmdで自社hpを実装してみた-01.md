---
id: "2026-04-19-claude-codeとdesignmdで自社hpを実装してみた-01"
title: "Claude CodeとDESIGN.mdで自社HPを実装してみた"
url: "https://qiita.com/Kawashima_RPA/items/e2c7da94bfa59bd3859e"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-19"
date_collected: "2026-04-19"
summary_by: "auto-rss"
query: ""
---

## WordPressで自社HPを構築していたが、再検討してみた

以前はXサーバーでWordPressを使って自社HPを運営していました。ドラッグ&ドロップでページを組めて便利だったのですが、使い続けるうちに「本当にWordPressが必要か？」と思うようになりました。

* ブログ記事はQiitaに移行していた
* WordPressの管理画面の重さ、プラグインの更新管理が負担になってきた
* デザインの細かい調整が意外とやりにくい

そこで、**「Claude Codeでホームページを作り直してみよう」** と再検討することにしました。どこまで作れるか試してみたくなったのです。

---

## できあがったもの

[![HP実装デモ](https://qiita-user-contents.imgix.net/https%3A%2F%2Fraw.githubusercontent.com%2FAutoFor%2Flife-public%2Fmain%2Fqiita%2Fassets%2Fhp-demo.gif?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=f953240451c34be75d35505e81ac8e83)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fraw.githubusercontent.com%2FAutoFor%2Flife-public%2Fmain%2Fqiita%2Fassets%2Fhp-demo.gif?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=f953240451c34be75d35505e81ac8e83)

**実際のHP：<https://autofor.co.jp/>**

実装したページ：

* `index.html` — トップページ
* `about.html` — 会社概要
* `rpa_consulting.html` — RPAコンサルティング
* `rpa_engineer.html` — RPA技術者育成
* `ai_backoffice.html` — AIバックオフィス
* `news.html` — お知らせ
* `contact.html` — お問い合わせ

ヒーローセクション、カードグリッド、AIタイムライン風のビジュアル、レスポンシブ対応まで全部入っています。

---

## アプローチ：DESIGN.mdというアイデア

今回やってみた手法が **DESIGN.md** です。

作りたいサイトのデザインを、テキストで徹底的に記述したMarkdownファイルです。今回は **[getdesign.md](https://getdesign.md/)** というサービスを使って、Cursorのウェブサイトのデザインシステムを抽出しました。

実際に生成されたDESIGN.mdの冒頭はこんな感じです（全体で約330行）：

```
# Design System Inspired by Cursor

## 1. Visual Theme & Atmosphere

Cursor's website is a study in warm minimalism meets code-editor elegance. The entire experience
is built on a warm off-white canvas (`#f2f1ed`) with dark warm-brown text (`#26251e`) -- not pure
black, not neutral gray, but a deeply warm near-black with a yellowish undertone that evokes old
paper, ink, and craft.

**Key Characteristics:**
- CursorGothic with aggressive negative letter-spacing (-2.16px at 72px) for compressed display headings
- berkeleyMono for code and technical labels
- Warm off-white background (`#f2f1ed`) instead of pure white
- Primary text color `#26251e` (warm near-black with yellow undertone)
- Accent orange `#f54e00` for brand highlight and links
- oklab-space borders at various alpha levels for perceptually uniform edge treatment

## 2. Color Palette & Roles

### Primary
- **Cursor Dark** (`#26251e`): Primary text, headings
- **Cursor Cream** (`#f2f1ed`): Page background
- **Cursor Light** (`#e6e5e0`): Secondary surface, button backgrounds

### Border Colors
- **Border Primary** (`oklab(0.263084 -0.00230259 0.0124794 / 0.1)`): Standard border
- **Border Medium** (`oklab(0.263084 -0.00230259 0.0124794 / 0.2)`): Emphasized border
...（以下続く）
```

Cursorのサイトは「ウォームミニマリズム」とでも呼ぶべきデザインで、特徴的なのは：

* **ウォームオフホワイト**（`#f2f1ed`）を背景に使う。純白ではなく、温かみのあるクリーム色
* **テキストカラー**も純黒ではなく、黄みがかったウォームブラック（`#26251e`）
* **oklab色空間**のボーダー色。RGBAでなくperceptually uniformな色管理
* **3つのフォント体系**：ゴシック（見出し）、明朝（本文）、モノスペース（コード）

これを日本語サイト向けにアダプトして、フォントはNoto Sans JP / Noto Serif JPに置き換えました。

[getdesign.md](https://getdesign.md/) はURLを入力するだけで、そのサイトのデザインシステム（色、フォント、余白、コンポーネントの設計）をMarkdown形式で書き出してくれるサービスです。これをそのままClaude Codeへの指示書として使えます。

### DESIGN.mdをClaude Codeのルールにする

`CLAUDE.md`（Claude Codeが自動で読む設定ファイル）に「DESIGN.mdとCONTENT.mdが正典。HTMLはそこから派生する生成物」というルールを書きました。

```
## 🚨 絶対ルール（Single Source of Truth）
- HTML / CSS / JS を書くときは、まず CONTENT.md または DESIGN.md を確認
- DESIGN.md に定義されていない色・フォントサイズ・余白をCSSに直接書いてはいけない
```

これにより、**Claude Codeが毎回DESIGN.mdを参照しながらHTMLを生成・修正**するようになります。デザインの一貫性が保たれ、「なぜかこのページだけフォントが違う」という事故が防げます。

### 実際に使った3つのMDファイル

今回のHP制作で用意したMarkdownは以下の3つだけです。これが**唯一の入力**です。

```
autofor-hp/
├── DESIGN.md    # デザインシステム定義（色・フォント・余白・コンポーネント）
├── CONTENT.md   # サイト内全テキスト・構造・ナビ定義
└── CLAUDE.md    # Claude Codeへの作業ルール（Single Source of Truthの宣言）
```

**CONTENT.md** にはサイトに載せるテキストを全部書きます（抜粋）：

```
# AutoFor株式会社 HP コンテンツ一覧

## ナビゲーション
- ホーム
- 事業紹介
  - RPA業務改善コンサルティング
  - RPAエンジニア事業
  - AIによるバックオフィス自動化
- 私たちについて
- よくあるご質問
- お知らせ
- お問い合わせ

## トップページ（index.html）

### メインビジュアル

**キャッチコピー**
> RPAとAIエージェントで業務を自動化する

**サブコピー**
> すべての業務を人が抱える時代は、もう終わりにしませんか？
> 人が働くことをもっと価値あるものにするために、"手放す"選択肢を届けます。

### 事業紹介（PROJECT）

**PROJECT #1　RPA業務改善コンサルティング**
> 業務フローの分析から自動化設計・導入・運用支援まで一貫サポート。

...（以下ページごとにテキストが続く）
```

**CLAUDE.md** にはClaude Codeへの絶対ルールを書きます（これが全文）：

```
# Autofor HP — Claude 作業ルール

## 🚨 絶対ルール（Single Source of Truth）

このリポジトリの **設計と内容の正典は `DESIGN.md` と `CONTENT.md`** です。
`*.html` / `*.css` / `*.js` は **上記2つから派生する生成物**として扱います。

### ルール 1：正典 → 生成物 の一方向原則

- HTML / CSS / JS を書くときは、まず `CONTENT.md` または `DESIGN.md` を確認
- `CONTENT.md` / `DESIGN.md` に記載がない内容をHTMLに追加してはいけない
- `DESIGN.md` に定義されていない色・フォントサイズ・余白をCSSに直接書いてはいけない

### ルール 2：編集の同期は必須

| 変更対象 | 同時に更新すべきファイル |
|---------|------------------------|
| テキスト・構造・ページ追加削除 | `CONTENT.md` |
| 色・タイポ・余白・コンポーネント | `DESIGN.md` |

### ルール 3：作業フロー

1. 要件を聞いたら、まず `CONTENT.md` / `DESIGN.md` を読む
2. 変更内容を先に `CONTENT.md` / `DESIGN.md` に反映する
3. その定義に従って `*.html` / `*.css` / `*.js` を更新する
4. コミット前に「MDと実装がずれていないか」を自己確認する

## 禁止事項

- ❌ `DESIGN.md` に無い色・サイズをCSSに直書き
- ❌ `CONTENT.md` に無いテキストをHTMLに追加
- ❌ MDを更新せずにHTML/CSS/JSだけを変更する
```

この3ファイルを用意したら、あとはClaude Codeに「これをもとにHTMLを作って」と指示するだけ。細々とした微調整なしに、**一気にサイトを作り上げました。**

---

## 実装の流れ

### 1. Playwright MCPで動作確認しながら修正

JavaScript周りの動作（ハンバーガーメニュー、スムーススクロール、フォームバリデーションなど）は、実際にブラウザで動かさないと確認できません。

ここでPlaywright MCPが活躍しました。

* Claude Codeがコードを実装する
* Playwright MCPでブラウザを起動し、実際にクリック・操作する
* エラーや挙動の問題をそのままClaude Codeにフィードバックする
* 自動修復

この「実装→ブラウザ確認→フィードバック→修正」のサイクルをClaude Code単体でぐるぐる回せるのが最高でした。人間がブラウザで確認してバグ報告する必要がほとんどありません。

### 2. HTMLがズレたらHTMLを直さずDESIGN.mdを直す

実装中に「思ったデザインと違う」と感じることが何度かありました。このとき、**HTMLやCSSを直接いじらない**というルールを徹底しました。

代わりにやること：

1. 「なぜ自分の意図と違うのか」をDESIGN.mdレベルで考える
2. DESIGN.mdの定義を修正・追記する
3. Claude Codeに「DESIGN.mdを参照してHTMLに反映して」と指示する

たとえばカードのボーダーが薄すぎると感じたら、DESIGN.mdの`Border Primary`の定義を見直す。フォントが重すぎる場合はDESIGN.mdのタイポグラフィテーブルを調整する。

この運用にすることで、**DESIGN.md = 完成形の設計図**という状態が常に保たれます。「HTMLは触ったけどDESIGN.mdは古いまま」という状態にならないのがメリットです。

```
【修正フロー】
意図と違う → DESIGN.mdを更新 → Claude Codeが反映 → HTML/CSSは自動生成
（HTMLを直接触るのはNG）
```

### 3. 日本語フォントの調整だけは手作業

唯一、手修正が必要だったのが**日本語フォント周り**です。

Cursorのデザインは英語フォント（CursorGothic）前提で設計されています。

```
/* Cursorオリジナル */
letter-spacing: -2.16px; /* 72pxのとき */
```

これをそのまま日本語に適用すると、文字が詰まりすぎて読みにくくなります。日本語グリフは欧文より字面が大きく、ネガティブトラッキングの許容範囲が狭い。

DESIGN.mdの段階で日本語向けに調整した値を定義しました：

```
/* 日本語向けアダプト */
--font-sans: "Noto Sans JP", sans-serif;
letter-spacing: -0.02em; /* 見出しでも控えめに */
line-height: 1.75;       /* 本文は広め */
```

ここだけは「Cursorのピクセル値をそのまま使う」ではなく、自分の目で見て調整する必要がありました。

---

## やってみてわかったこと

### DESIGN.mdアプローチの強み：「AI感」がなくなる

Claude Codeだけでホームページを作ると、**パッと見でAIが作ったとわかる**ことがあります。なんとなくレイアウトがバラバラ、フォントサイズが統一されていない、色使いが微妙に一貫していない。

DESIGN.mdがあると、この「AI感」が一切なくなりました。

理由はシンプルで、Claude Codeが毎回同じデザイントークンを参照するからです。「Cursorっぽく」という曖昧な指示ではなく、「`#f2f1ed`のウォームクリーム背景、`#26251e`のウォームブラックテキスト、`oklab()`ボーダー」という具体的な定義があるので、ページをまたいでもデザインが揺れません。

### 2つのMDファイルだけで管理できる

このプロジェクトで維持管理するファイルは実質2つです：

* **`DESIGN.md`** — 見た目の定義（色・フォント・余白・コンポーネント）
* **`CONTENT.md`** — 内容の定義（テキスト・構造・ナビゲーション）

HTMLを修正したいときも、まずこの2つのMDを更新してからClaude Codeに「MDの内容をHTMLに反映して」と指示します。HTMLを直接いじる必要がほぼありません。

一度作ったDESIGN.mdは他のプロジェクトでも再利用できます。デザインのコピーライトに注意は必要ですが、\*\*「このデザインシステムでページを追加して」\*\*と言えば新しいページが生えてくる体験はかなり気持ちいいです。

### WordPressに戻る理由がなくなった

管理画面のメンテナンス、プラグイン更新、セキュリティパッチ、レンタルサーバー費用。

静的HTMLなら：

* AzureでホスティングのためXサーバーのランニングコストが不要に
* セキュリティ更新不要（サーバーサイドロジックがない）
* Claude Codeで好きなように修正できる

コンテンツ更新の頻度が低く、ブログはQiitaに任せているという状況なら、静的HTMLのほうが圧倒的にシンプルです。

### Playwright MCPは「AI×ブラウザ」の組み合わせ

Claude CodeとPlaywright MCPの組み合わせは、フロントエンド開発で特に強力だと感じました。「ボタンを押したら何も起きない」「モバイルでレイアウトが崩れる」という問題を人間がバグ報告する必要がなく、AIが自分で確認して直してくれます。

---

## まとめ

| 項目 | 以前（WordPress） | 今回（静的HTML） |
| --- | --- | --- |
| デザイン変更 | テーマ設定・CSS上書き | DESIGN.md → Claude Code |
| 動作確認 | 手動でブラウザ確認 | Playwright MCPで自動 |
| ホスティング | Xサーバー（有料） | Azure |
| 更新コスト | プラグイン管理・バックアップ | git push |

WordPressが悪いわけではなく、**用途に合った選択**の話です。ブログを別サービスに移行済みで、コンテンツ更新頻度が低いなら、静的HTMLのほうがずっと身軽です。

Claude CodeとDESIGN.mdの組み合わせで、「デザインの意図をコードに落とし込む」作業がかなり楽になりました。ホームページ作成に興味がある方はぜひ試してみてください。
