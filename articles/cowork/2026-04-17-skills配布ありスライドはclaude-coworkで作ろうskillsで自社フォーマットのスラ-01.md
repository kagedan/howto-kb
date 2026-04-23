---
id: "2026-04-17-skills配布ありスライドはclaude-coworkで作ろうskillsで自社フォーマットのスラ-01"
title: "【Skills配布あり】スライドはClaude Coworkで作ろう。Skillsで自社フォーマットのスライドを自動生成する。"
url: "https://zenn.dev/and_dot/articles/6f9c0b71acca52c1"
source: "zenn"
category: "cowork"
tags: ["cowork", "zenn"]
date_published: "2026-04-17"
date_collected: "2026-04-18"
summary_by: "auto-rss"
query: ""
---

## はじめに

こんにちは、アンドドットCTOの高根沢です。

「プレゼン資料を作成して」の一言で、自社ブランドに沿ったスライドが出てくる環境を作りました。  
これを実現しているのが、Claude Coworkの「Skills」機能です。

「Skills」という機能では、繰り返し行う作業をMarkdownで定義して再利用でき、ここに自社のデザインルール（ブランドカラー、ロゴ配置、フォントサイズ、レイアウト）を組み込むことで、誰がスライドを作っても同じフォーマットで出力されるようになります。

![Claude Coworkでスライド生成](https://static.zenn.studio/user-upload/deployed-images/17dd1a9a3db757e91e866f0c.png?sha=c7e22680d30e2b40a27c0b81bf3995405b3ecfa7)  
*Claude Coworkのチャットで構成を指示 → 自社ブランドのスライドが出力される*

実際に、弊社ではこの仕組みで作った資料を使って、外部イベントでの登壇も行っています。  
この記事では、具体的なSkillの作り方から、ロゴ画像の配置ルールまで、具体的なやり方について解説していきたいと思います。

## サンプルSkillを配布しています

本記事で解説するスライド生成Skillのサンプル版を配布しています。アンドドット固有のロゴ・背景画像をプレースホルダーに差し替え、社名を汎用化したものです。

<https://github.com/p0x0q/claude-cowork-hands-on>

`.skill` ファイルをダウンロードして Claude Desktop の「カスタマイズ → スキル」からインポートすれば、すぐに試せます。自社ロゴ・カラーへのカスタマイズ方法は記事の後半で解説しています。

### Sample Skillを実際にインポートして試した例

`.skill` ファイルをClaude Desktopにインポートすると、内容のプレビューが表示されます。

![Sample Skillのインポート確認](https://static.zenn.studio/user-upload/deployed-images/83d5aea5677984b82fd54cb1.png?sha=3ed1528bcedb95c4f86a4688a13bed24a0997bbb)  
*「sample-pptx-skill をライブラリに追加しますか？」の確認画面。ロゴ運用ルールやチェックリストがプレビューされる*

インポート後、「AIニュースのスライドを作って」と指示した結果がこちらです。

![Sample Skillで生成したスライド](https://static.zenn.studio/user-upload/deployed-images/7a693662ce8f0bd3ef567694.png?sha=476a34d6741ec61e1d9c52c71d1a56d2a0b06df9)  
*プレースホルダーの背景枠・カラーパレットが適用されたスライド。ロゴ部分を自社のものに差し替えればそのまま使える*

## Claude CoworkのSkillsとは

Skillsは、Claude Desktop / Cowork上で「毎回同じ手順でやっている」作業を自動化・テンプレート化して再利用できる機能です。  
SKILL.mdというMarkdownファイルに手順・ルール・テンプレートを記述し、Claude Desktopに登録します。「スキルを作って」「スケジュールして」などとClaude上で指示すると登録が可能です。

現在、アンドドットでは主に以下のSkillsを運用し、業務フローに組み込んでいます。

| スキル名 | 用途 | 備考 |
| --- | --- | --- |
| **anddot-pptx-v3** | 自社テンプレートでスライド生成 | **本記事で解説** |
| **anddot-docx-v3** | 自社テンプレートでWord文書生成 |  |
| **anddot-search-v2** | 社内横断検索 |  |
| **anddot-scheduling-v2** | 日程調整の自動化 |  |

![組織スキル一覧](https://static.zenn.studio/user-upload/deployed-images/9439dde908395e156df1655c.png?sha=6c6c7d8cf8f30e8ca7a643b18168f8b9c9ae2850)  
*Claude Desktopの組織スキル画面。anddot-pptx-v3、anddot-docx-v3、anddot-search-v2、anddot-scheduling-v2が並ぶ*

## スライド生成Skillの作り方

### 1. 自社のデザインルールを言語化して整理する

Skillに組み込む前に、スライドのブランドルールを言語化します。アンドドットの場合は以下のように規定しました。

* **ブランドカラー**: ダークブルー `#1B5E8A` 基調
* **背景**: グラデーション枠の背景画像を使用
* **ロゴ配置**: 表紙と最終ページのみに配置。アイソレーションエリア（ロゴ周辺の余白）を30%確保
* **フォント**: 見出しはボールド、本文はレギュラー
* **レイアウト**: タイトル、コンテンツ、2カラム、4象限など用途別に定義

ここで重要なポイントは、**Skillのパッケージ内に会社ロゴなどの画像ファイルを「アセット」として内包できる**点です。  
これにより、ユーザー側で毎回ロゴ画像をプロンプトに添付しなくても、Claudeが自律的に正しいロゴを引き当ててスライドに埋め込んでくれるようになります。

![Skillのassets構成](https://static.zenn.studio/user-upload/deployed-images/4f22847e60ad317e8698bee0.png?sha=26385b8468d9ee34d0369948f3bf9240eb4b769d)  
*anddot-docx-v3の実際の構成。SKILL.md、assets/logos/（黒・白のロゴバリエーション）、references/style-guide.mdで構成される*

### 2. SKILL.mdを書く

Skillの中身はMarkdownファイルです。anddot-pptx-v3はゼロからすべてを作るのではなく、 **ラッパースキル** として設計しています。  
PPTX生成ロジック自体はClaude標準の `pptx` スキルに委譲し、デザイン（カラー・フォント・ロゴ）だけ自社仕様で上書きする構成です。これにより、標準スキルがアップデートされた際も保守の手間がかかりません。

SKILL.mdの主要セクションは以下です（全文は400行超あるため抜粋）。

```
---
name: anddot-pptx-v3
description: >
  自社の共通スタイルでプレゼン資料（.pptx）を作成するスキル（v3: ロゴ運用の厳格化）。
  「プレゼン作って」「営業資料を作成」「スライド作成」などのリクエストで起動する。
metadata:
  version: "3.2.0"
---

# 自社共通スタイル プレゼン資料作成（v3 — ロゴ運用厳格化）

このスキルはブランドスタイルを定義する **ラッパースキル** である。
PPTXの生成ロジックは標準 `pptx` スキルに委譲し、
デザインだけ自社仕様で上書きする。

## 🔴 ロゴ運用ルール（v3 最重要）
- ロゴは表紙と最終スライドの最大2箇所のみ
- アイソレーションエリア: ロゴサイズの30%以上

## 🔴 テキストカラーの鉄則
- 白フォント（#FFFFFF）は原則禁止（白背景のため）
- タイトル: #1B5E8A、本文: #333333

## 必須手順
1. 標準 pptx スキルを読み込む
2. 自社スタイルとアセットを適用する
3. QAを実施する（ロゴ配置チェック含む）
```

ポイントは **標準pptxスキルとの分離** です。生成ロジックを自前で書く必要がなく、デザインルールとアセットだけを定義すれば良いため、標準スキルがアップデートされてもデザインルールはそのまま使うことができます。

### 3. ロゴ画像をassetsに配置する

Skillにはassetsディレクトリを持たせることができます。  
ここにロゴ画像（PNG）や背景画像を配置しておくと、スライド生成時にClaudeが参照して配置します。

```
anddot-pptx-v3/
├── SKILL.md
├── assets/
│   ├── background.jpg          ← 背景画像（1920x1080, 16:9）
│   └── logos/
│       ├── _black/
│       │   ├── icon_black_Primera.png
│       │   ├── icon-black_Segunda.png
│       │   └── logo_black_Primera.png
│       └── _white/
│           ├── icon_white_Primera.png
│           ├── logo_white_Primera.png
│           └── logo_white_Segunda.png
└── references/
    └── style-guide.md           ← カラーパレット・フォント等の詳細
```

黒背景用・白背景用のロゴバリエーションをそれぞれ用意しています。SKILL.md内で「表紙にはlogo\_black\_Primera.pngを使用」のように具体的に指定します。

### 4. Claude Desktopに登録する

Claude Desktopの「カスタマイズ → スキル」から登録します。SKILL.mdの内容が読み込まれ、以後「プレゼン作って」「スライドを作成して」といった指示で自動的にこのSkillが呼び出されます。

![Skillのインポート確認](https://static.zenn.studio/user-upload/deployed-images/40ba2aad07cbdc2764478eec.png?sha=9cf953e3415d9f98df8add47f2ce430ba965916a)  
*Skillファイルをライブラリに追加する確認画面。SKILL.mdの内容がプレビューされる*

Claude TeamまたはEnterpriseプランで、組織設定からスキルをインポートすれば、全員がこのフォーマットに従ったスライド生成を行うことができます。（社内ではこの方法を採用しています）

![スキルアップロード画面](https://static.zenn.studio/user-upload/deployed-images/e12c86fc3f11be674e536273.png?sha=8c7936edc2b282f5a04e9635354ba9f493cfe8f8)  
*組織スキルのアップロード画面。.mdファイルまたは.zip/.skillファイルをドラッグ&ドロップで登録できる*

### 5. Coworkと壁打ちしながらSkillを作る

実は、SKILL.mdを最初から自分で書く必要はありません。Claude Coworkのチャット上で壁打ちしながら作れます。

やり方はシンプルで、Coworkに「スライド生成用のSkillを作りたい。うちのブランドカラーは#1B5E8Aで、ロゴは表紙と最終ページだけに入れたい」と伝えるだけです。Coworkが SKILL.md のドラフトを生成してくれるので、それをベースに「ロゴのアイソレーションをもっと厳しくして」「テーブルのカラーリングルールも追加して」と対話で詰めていけます。

アンドドットのanddot-pptx-v3も、最初はCoworkとの壁打ちで骨格を作り、実際にスライドを生成しては「ここが違う」「このルールが守られてない」とフィードバックを繰り返してv3まで育てました。SKILL.mdを一発で完璧に書こうとするより、Coworkと対話しながら育てる方が圧倒的に速いです。

![Coworkとの壁打ちでSkillを作成](https://static.zenn.studio/user-upload/deployed-images/8f1e8cc1b59c9ddc795149d1.png?sha=6a30fca9043cc163bc986a28caad293230f02c22)  
*「エンジニア向けのスライドスキルを作りたい」と伝えると、既存スキルの構造を確認した上で方向性を質問してくれる。対話で要件を詰めながらSKILL.mdが出来上がる*

## 実際に使ってみた

### 「プレゼン作って」だけで自社ブランドのスライドが完成

テーマと構成を伝えるだけで、ブランドカラー・背景枠・ロゴ配置が反映されたスライドが出力されます。

![生成されたスライド](https://static.zenn.studio/user-upload/deployed-images/f4320d90228e56a52293127f.png?sha=7fbda8e619dcff808cd7617e007c5ddeea0ddb47)  
*Claude Cowork上でスライドを編集している様子。左にスライド一覧、右にプレビューが表示される*

実際にこのSkillで作ったスライドで登壇もしています。登壇資料38枚を、Claude Coworkのチャットで構成を指示しながら生成しました。

### ロゴ配置で工夫した点

最初のバージョン（v1）では全ページにロゴを入れていましたが、コンテンツページではロゴが邪魔になるケースが多発しました。v3では以下の方針に変更しています。

* **表紙と最終ページのみにロゴを配置**
* コンテンツページはグラデーション枠の背景画像でブランドを維持
* ロゴ周辺には **アイソレーションエリア30%** を確保（ロゴが他の要素と近づきすぎない）

この変更で、コンテンツエリアが広く使えるようになり、情報量の多いスライドも見やすくなりました。

### v1→v3で改善したこと

| バージョン | 課題 | 改善 |
| --- | --- | --- |
| v1 | ロゴが全ページに入りコンテンツが窮屈 | 表紙・最終ページ限定に変更 |
| v2 | テーブルのカラーリングが不統一 | ヘッダー行のみカラー適用ルール追加 |
| v3 | セクション区切りが単調 | Part番号＋帯デザインのテンプレート追加 |

Skillは一度作って終わりではなく、実際に使いながらチームのフィードバックを取り入れて改善していくことが成功の鍵です。

## Skillを作るときのコツ

**ルールは具体的に書く**。

「ブランドカラーを使う」ではなく「#1B5E8Aを見出し背景に使用」と書かないと、Claudeの解釈にブレが生じます。

**referencesに参考例を入れる**。

「こういうスライドを作って」の完成イメージを入れておくと、出力の品質が安定します。

**assetsの画像は用途を明記する**。

「logo.png → 表紙と最終ページの中央下部に配置」のように、どこにどう使うかをSKILL.md内で具体的に指示します。Claudeは画像の用途を推測しないので、明示が必要です。

## まとめ

Claude CoworkのSkillsを使えば、チーム全体の資料作成にかかるリードタイムを大幅に削減しつつ、アウトプットの品質とブランディングを統一できます。

構築のステップは非常にシンプルです。  
「業務を観察する」→「SKILL.mdにルールを書く」→「使って改善する」

「毎回同じ手順で体裁を整えている」業務があるのであれば、まずはMarkdown一つから始められるSkill化をぜひ検討してみてください！

## 一緒に"爆速文化"をつくる仲間を募集しています

アンドドットでは、生成AIとともにプロダクトを創り上げ、少数精鋭で大きな成果を出す組織を目指しています。AI活用を前提とした新しい開発スタイルに興味のある方、ぜひ一度カジュアルにお話しましょう。

<https://calendar.google.com/calendar/appointments/schedules/AcZssZ2betA1myxHjAccbO6w6EEDYG6SGfdlymYyx2MJBIwHamQtmzI66cm7Da7aLiC4sYSbXv-CP846>
