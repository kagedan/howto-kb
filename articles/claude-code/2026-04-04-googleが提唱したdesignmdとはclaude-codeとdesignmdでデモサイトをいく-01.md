---
id: "2026-04-04-googleが提唱したdesignmdとはclaude-codeとdesignmdでデモサイトをいく-01"
title: "Googleが提唱したDESIGN.mdとは？Claude CodeとDESIGN.mdでデモサイトをいくつか作ってみた"
url: "https://qiita.com/miruky/items/a6312c14e6352376ec00"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-04"
date_collected: "2026-04-05"
summary_by: "auto-rss"
---

## はじめに

[![スクリーンショット 2026-04-04 19.54.10.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2F6067acaf-2a15-4f50-9736-d618d8070e86.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c625ca79654f0794e2d0c61752fceb86)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2F6067acaf-2a15-4f50-9736-d618d8070e86.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c625ca79654f0794e2d0c61752fceb86)

こんばんは、mirukyです。  
**個人的にAIにデザインを指定するのって、意外と難しいと思っています。**

皆さん、**DESIGN.md**をご存知でしょうか。GoogleがStitchプロジェクトの一部として策定した、マークダウンベースのデザインシステム仕様です。「AIコーディングエージェントにデザインの文脈を与える」という、シンプルながら強力なアプローチで、いま海外のAI開発者コミュニティで注目を集めています。

私はこのDESIGN.mdの仕様を読んで「これ、実際に使うとどのくらいのクオリティが出るんだろう？」と気になりました。

そこで今回、**DESIGN.mdを5つ書き、それぞれClaude Codeに渡してデモサイトを作ってもらいました**。ジャンルはSaaS、カフェ、ポートフォリオ、ヘルスケア、クリエイティブエージェンシーとバラバラにしています。結果は正直、かなり驚きました。

この記事では、DESIGN.mdの概要から実際の活用方法、そして完成したデモサイトの紹介までを一気にお届けします。

## 目次

1. DESIGN.mdとは何か
2. DESIGN.mdの書き方
3. 実際にデモサイトを作ってみた
4. 完成した5つのデモサイト
5. 使ってみて感じたこと

## 1. DESIGN.mdとは何か

### 1-1. Googleが策定した「AIのためのデザインシステム」

[![スクリーンショット 2026-04-04 19.57.32.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2F5f0e7bd3-989c-48a6-9e29-65d172281ed9.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=af068d5fbec55ed2462ae24811f8f0d8)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2F5f0e7bd3-989c-48a6-9e29-65d172281ed9.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=af068d5fbec55ed2462ae24811f8f0d8)

DESIGN.mdは、**GoogleがStitchプロジェクトの一部として策定したオープンなマークダウン仕様**です。一言でいうと、「デザインシステムを1つのマークダウンファイルにまとめて、AIコーディングエージェントに読ませるためのフォーマット」です。

> DESIGN.md is a markdown file that captures everything an AI coding tool needs to build consistent UIs: colors, typography, spacing, component patterns, and more — all in plain text.  
> （DESIGN.mdは、AIコーディングツールが一貫したUIを構築するために必要なすべてを捉えるマークダウンファイルです。色、タイポグラフィ、スペーシング、コンポーネントパターンなど、すべてをプレーンテキストで記述します。）
>
> designmd.ai

従来、デザインシステムといえばFigmaファイルやJSON形式のデザイントークンが主流でした。しかしこれらはLLMが直接読み取るには不向きです。DESIGN.mdは**人間にもAIにも読める**という点で、まさにAI時代のデザインシステムと言えます。

### 1-2. なぜDESIGN.mdが必要なのか

AIコーディングエージェント（Claude Code、Cursor、GitHub Copilotなど）に「かっこいいLPを作って」と頼むと、毎回微妙に異なるデザインが生成されます。色もフォントもバラバラ。これは**AIにデザインの文脈が渡されていない**からです。

DESIGN.mdをプロジェクトルートに置くだけで、AIエージェントは自動的にこのファイルを読み込み、**指定されたカラーパレット、タイポグラフィ、コンポーネント仕様に従ったUI**を生成するようになります。

DESIGN.mdの特徴を整理すると、以下の通りです。

| 特徴 | 内容 |
| --- | --- |
| フォーマット | プレーンなマークダウン |
| 策定元 | Google（Stitchプロジェクト） |
| 対応ツール | Claude Code、Cursor、Copilot、Gemini CLIなど |
| バージョン管理 | Git管理可能（テキストファイルのため差分も見やすい） |
| ベンダーロックイン | なし（どのAIツールでも利用可能） |

## 2. DESIGN.mdの書き方

### 2-1. 基本構成

DESIGN.mdに決まった「スキーマ」はありませんが、一般的に以下のセクションで構成します。

```
# プロジェクト名 — デザインシステム

## Colors
（カラーパレット: 名前、HEXコード、用途）

## Typography
（フォントファミリー、サイズ、ウェイト、行間）

## Spacing
（ベースユニット、スケール値）

## Components
（ボタン、カード、ナビゲーションなどの具体的仕様）

## Elevation
（シャドウ、深度の定義）

## Guidelines
（デザイン原則、Do's / Don'ts）
```

### 2-2. 実際に書いたDESIGN.mdの例

今回のデモ用に書いたDESIGN.mdの一部を紹介します。これはSaaS LP用のものです。

```
# NovaPulse — AI Analytics SaaS Design System

## Colors
- **Primary** (#7C3AED): Violet — CTAs, links, active states
- **Primary Light** (#A78BFA): Hover states, secondary accents
- **Secondary** (#06B6D4): Cyan — metrics highlights, badges
- **Background** (#0B0F1A): Deep navy — page background
- **Surface** (#141929): Cards, modals, elevated containers
- **Text Primary** (#F1F5F9): Headings and body
- **Text Secondary** (#94A3B8): Muted labels, captions

## Typography
- **Font Family**: "Inter", system-ui, -apple-system, sans-serif
- **Display**: 72px / 1.05, weight 800, letter-spacing -0.03em
- **H1**: 48px / 1.15, weight 700, letter-spacing -0.02em
- **Body**: 16px / 1.6, weight 400

## Components
- **Buttons (Primary)**: bg gradient (#7C3AED → #6D28D9), white text,
  12px radius, 16px 32px padding, font-weight 600,
  hover: brightness(1.1), shadow 0 4px 14px rgba(124,58,237,0.4)
- **Cards**: bg #141929, 16px radius, 1px solid #2A3158 border,
  32px padding, hover: translateY(-4px) + shadow
```

ポイントは、**色の用途（どこに使うか）やホバー時の挙動まで記述する**ことです。AIは具体的な指示ほど正確に再現します。

[![スクリーンショット 2026-04-04 19.58.16.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2Fdd13909f-cf36-4843-9f79-577461f471de.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=907650d7d85d9bf20d18aeb174f439d1)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2Fdd13909f-cf36-4843-9f79-577461f471de.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=907650d7d85d9bf20d18aeb174f439d1)  
出典：[What is DESIGN.md?](https://stitch.withgoogle.com/docs/design-md/overview)

公式サイトにも書き方例が載っています。

## 3. 実際にデモサイトを作ってみた

### 3-1. 手順

実際に行った手順は非常にシンプルです。

1. テーマを決める（SaaS、カフェ、ポートフォリオなど）
2. そのテーマに合ったDESIGN.mdを書く  
   （これすらClaude Codeにお願いしても大丈夫です）
3. DESIGN.mdをプロジェクトルートに配置
4. Claude Codeに「このDESIGN.mdに従ってLPを作って」と指示

これだけです。各サイトのDESIGN.mdは50〜80行程度で、私は書くのに10〜15分ほどかかりました。サイトを作る前段として、Claude Codeに具体的な指示をしてDESIGN.mdを作るのもアリです（二度手間感ありますが）。

### 3-2. 工夫したポイント

5つのサイトで**意図的にデザインの方向性を変えました**。同じフォーマットでどこまで振り幅が出るかを検証するためです。

| サイト | テーマ | デザインの方向性 |
| --- | --- | --- |
| NovaPulse | SaaS LP | ダーク、グラデーション、モダン |
| Maison Lumière | カフェ | ウォーム、セリフ体、エレガント |
| Kei Tanaka | ポートフォリオ | ミニマル、モノクロ、余白重視 |
| VitaWell | ヘルスケアアプリ | グリーン、丸角、親しみやすさ |
| PRISM | クリエイティブエージェンシー | ダーク、ビビッド、大胆 |

## 4. 完成した5つのデモサイト

リポジトリはこちらです。

**GitHub**:

**GitHub Pages**:

### 4-1. NovaPulse（SaaS LP）

ダークテーマにバイオレットとシアンのグラデーションを使ったSaaS LP。ダッシュボードのプレビューUIや料金テーブルも含む、フルページ構成です。

[![スクリーンショット 2026-04-04 20.00.33.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2F2321894d-8121-494a-bfdd-45e28fc6dce4.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7b8cdc5e023898473fe4d693d42948c0)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2F2321894d-8121-494a-bfdd-45e28fc6dce4.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7b8cdc5e023898473fe4d693d42948c0)

[![スクリーンショット 2026-04-04 20.16.42.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2F0951728a-0eb4-459d-bddd-cc071a59f37e.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=197e29ae89cf03051af7500abbfde38b)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2F0951728a-0eb4-459d-bddd-cc071a59f37e.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=197e29ae89cf03051af7500abbfde38b)

DESIGN.mdでグラデーションの方向（135deg）やカードのホバーアニメーション（translateY + shadow）まで指定したため、**インタラクション込みで期待通りのデザイン**が生成されました。  
海外企業っぽいと思いますが、洗練された格好良いデザインになりましたね。

### 4-2. Maison Lumière（カフェ）

クリーム色の背景にウォームブラウンのアクセント。Playfair Displayのセリフ体をヘッディングに使い、Latoのサンセリフ体を本文に使った**クラシカルで上品なデザイン**です。

[![スクリーンショット 2026-04-04 20.02.50.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2F415e9d1e-7e69-42f6-9622-b97cec3ec99d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0c49965c2e37ac650cc0a9385e200a28)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2F415e9d1e-7e69-42f6-9622-b97cec3ec99d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0c49965c2e37ac650cc0a9385e200a28)

[![スクリーンショット 2026-04-04 20.03.37.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2F05492c06-8e04-4c2d-b9a5-272f9fdcd500.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=158eed0605e8ffdac24817600602f641)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2F05492c06-8e04-4c2d-b9a5-272f9fdcd500.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=158eed0605e8ffdac24817600602f641)

メニューカード、レビュー、営業時間といったカフェサイトに必要なセクションがすべて揃っています。DESIGN.mdで「装飾的な区切り線（divider）」のスタイルまで定義したことで、**細部の雰囲気まで統一**されました。

メニューの部分は特に素晴らしいですね。喫茶店のウェブページが、数分で作成できる時代になりました。

### 4-3. Kei Tanaka（ポートフォリオ）

白と黒、そしてワンポイントの赤（#FF3B30）だけで構成した**究極のミニマルデザイン**。角丸ゼロ、シャドウなし。タイポグラフィの大小と余白だけで階層を表現しています。

[![スクリーンショット 2026-04-04 20.04.47.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2F7a6f3d10-c813-4ac9-88a3-ce4c8b2769a8.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=64bb331ff8d30c2aabcc43aa4306ddb9)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2F7a6f3d10-c813-4ac9-88a3-ce4c8b2769a8.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=64bb331ff8d30c2aabcc43aa4306ddb9)

[![スクリーンショット 2026-04-04 20.05.12.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2Fa98b7a36-4cbe-446e-ab94-1b54d36d6a12.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=23b43d8308172d14ed5de154bf123bdc)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2Fa98b7a36-4cbe-446e-ab94-1b54d36d6a12.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=23b43d8308172d14ed5de154bf123bdc)

DESIGN.mdの「Guidelines」セクションで「No rounded corners (0px radius)」「This design system does not use shadows」と明記したことが効いています。**「使わない」ことを指定する**のもDESIGN.mdの重要なテクニックです。

ミニマリストの方が好みそうなデザインになりました。

### 4-4. VitaWell（ヘルスケアアプリ）

エメラルドグリーン（#059669）を基調にした、**信頼感と親しみやすさを両立するデザイン**。角丸の大きいカード、ソフトなシャドウ、グリーンティンテッドの背景色が特徴です。  
[![スクリーンショット 2026-04-04 20.06.59.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2F82bb5857-4d16-44c5-9910-40ee4777746c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=cc6ead12750266ace89d7efb9a8987ae)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2F82bb5857-4d16-44c5-9910-40ee4777746c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=cc6ead12750266ace89d7efb9a8987ae)

[![スクリーンショット 2026-04-04 20.07.31.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2F969284f2-2a8e-48da-8753-36759cf80ef0.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0c17c1b2f4147e38f33cedc0de413d84)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2F969284f2-2a8e-48da-8753-36759cf80ef0.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0c17c1b2f4147e38f33cedc0de413d84)

スマートフォンのモックアップをCSSだけで作り込んでいる点も見どころです。DESIGN.mdでプログレスバーやバッジのスタイルを詳細に定義したことで、**アプリUIの雰囲気がそのままWebに反映**されました。

### 4-5. PRISM（クリエイティブエージェンシー）

ブルーとマゼンタのグラデーション、96pxの超大型タイポグラフィ、横スクロールのマーキーテキスト。**「ルールを壊す」ことがルール**というクリエイティブエージェンシーらしいデザインです。

[![スクリーンショット 2026-04-04 20.08.05.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2F1f9b1fb4-6aeb-4278-b8dd-bc586dd6266d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=80d464192170cc41be4ddfc6bcab3edb)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2F1f9b1fb4-6aeb-4278-b8dd-bc586dd6266d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=80d464192170cc41be4ddfc6bcab3edb)

[![スクリーンショット 2026-04-04 20.17.12.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2Fb33cf6a7-053a-43fe-a5f0-d34014d7c5da.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=fe4a14ffce923733df10389ea8e61a3e)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637204%2Fb33cf6a7-053a-43fe-a5f0-d34014d7c5da.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=fe4a14ffce923733df10389ea8e61a3e)

DESIGN.mdのGuidelinesに「Bold, expressive, rule-breaking」「No safe, corporate feel — push boundaries」と書いたことで、AIが**積極的に大胆なレイアウトを採用**しました。ホバーで画像にオーバーレイが出るプロジェクトカードのインタラクションも含め、エージェンシーサイトとしての完成度は高いです。

個人的に一番好きなデザインです。下の動く帯の部分に名だたる企業が乗っているパターンのウェブサイトを数え切れないくらいみたことがあります。

## 5. 使ってみて感じたこと

### 5-1. DESIGN.mdの「効き」は想像以上

正直なところ、「マークダウンで書いただけでそんなに変わるのか？」と半信半疑でした。しかし実際に5サイトを作ってみて、**DESIGN.mdの有無でAIの出力品質は劇的に変わる**と思いました。

DESIGN.mdがない場合、AIは「それっぽい」汎用的なデザインを出してきます。色選びはまあまあだけど、タイポグラフィは無個性、余白は均一、インタラクションはほぼなし。DESIGN.mdがある場合、**カラーパレット、フォントの使い分け、ホバーエフェクト、影の強さまで仕様通り**です。

### 5-2. 「使わないもの」を指定する重要性

ポートフォリオサイトのDESIGN.mdで学んだのは、**「何を使うか」だけでなく「何を使わないか」を書くことの効果**です。「シャドウは使わない」「角丸はゼロ」「グラデーションは不要」と明記すると、AIはそれらを一切使わず、代わりに余白とタイポグラフィで階層を作ります。

### 5-3. コンポーネントの具体性がカギ

色とフォントだけ定義して終わりにすると、コンポーネントのデザインはAI任せになります。**ボタンのhover時の挙動、カードのborder-radiusとpadding、ナビゲーションのbackdrop-filter**まで書くことで、統一感が格段に上がりました。

## おわりに

ここまでお読みいただきありがとうございます。

DESIGN.mdは「AIにデザインの文脈を渡す」というシンプルなアプローチですが、その効果は絶大です。50〜80行程度のマークダウンを書くだけで、AIが生成するUIの品質が目に見えて変わります。

Figmaでデザインを作り込む前の「方向性を決めるフェーズ」や、プロトタイプの素早い作成に特に向いていると感じました。今後、AIコーディングがさらに普及していく中で、DESIGN.mdは**デザイナーとAIの共通言語**になっていくのではないでしょうか。

ではまた、お会いしましょう。

## 参考リンク

### Google Stitch / DESIGN.md

### ツール

### 本記事のデモ
