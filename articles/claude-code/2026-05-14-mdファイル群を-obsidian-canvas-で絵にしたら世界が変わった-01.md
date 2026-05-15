---
id: "2026-05-14-mdファイル群を-obsidian-canvas-で絵にしたら世界が変わった-01"
title: "mdファイル群を Obsidian Canvas で「絵」にしたら世界が変わった"
url: "https://zenn.dev/tempeso/articles/36e556a0d78d5a"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-05-14"
date_collected: "2026-05-15"
summary_by: "auto-rss"
query: ""
---

## 🤖 AI 時代、人間の仕事は「仕様書を整備すること」になった

> コードは AI が書く。だから人間は仕様書を整える。

最近、強くそう感じています。

Claude Code や Cursor、Copilot を使い倒していると、コードを書く時間より **「AI に何をどう伝えるか」を考える時間** のほうが長くなってきました。

* どのドキュメントを読ませるか
* どの順番でコンテキストを渡すか
* そもそも、その仕様書は AI（と未来の自分）にとって読みやすいか？

**AI に渡す仕様書や資料を正しく整備していくこと** が、人間にとって新しく重要な仕事になりつつあります。

そして、ここで詰むのが **`docs/` 配下に積み上がった長大な markdown** です。

この記事では、こうした「正しいけど読まれない仕様書」を、**Obsidian + Claude Code** で **絵として一目で分かる Wiki** に変えるアプローチを紹介します。

実装の細部（skill の中身・Canvas の JSON・運用ルール）は次の記事に分けて、今回は **「こう変わるよ」のビフォーアフター** に絞ります。

---

## 👀 ビフォー: `docs/` に積み上がった markdown たち

私が現在開発している営業支援アプリ「EIGYOU」のプロジェクトには、こんな仕様書が並んでいます。

> EIGYOU プロジェクトの全体像や開発スタイルについては、シリーズの初日記事 [**30日後にサービスをリリースして不労所得を得る開発者 (1日目) ― Claude Code 全活用で楽したい開発者の基盤構築**](https://zenn.dev/tempeso/articles/900ea8ade4c165) もよかったらどうぞ 🤖

```
EIGYOU/docs/
├── APP_OVERVIEW.md             プロダクト概要
├── ARCHITECTURE.md             4層アーキ・技術スタック（1,000行超）
├── DOMAIN_SKETCH.md            ドメイン用語・ER 関係
├── DB_DESIGN.md                DB 全体方針
├── DB_DESIGN_TABLES_FIRESTORE.md   Firestore 14 コレクション
├── DB_DESIGN_TABLES_DRIFT.md       Drift 16 テーブル
├── SCREENS.md                  画面一覧 32 画面
├── SCREENS_DETAIL.md           画面別最終仕様
└── mockups/<画面ID>/           HTML モックアップ
```

仕様書としては網羅的で「正しい」。でも、こうなりがちです 👇

* 久しぶりに開くと、**「あれ、この画面どこから遷移するんだっけ？」** をスクロールで探す羽目になる
* 新メンバーに渡すと **「全部読むの大変です…」** と返ってくる
* AI に渡すときも **どのファイルをどこまで読ませるか毎回考える**

文章として正しくても、**「全体像が頭に入らない」** という致命的な弱点を持っています。

---

## 🗺 アフター: Obsidian Canvas で「絵」になった仕様書

これを Obsidian に「リンクハブ + Canvas で視覚化」する設計に変えたら、こうなります。

### 画面遷移図（screen-flow.canvas）

32 画面を **機能系統ごとの列に整列** させた Canvas。各ノードはダブルクリックで該当画面の markdown に飛びます。

![](https://static.zenn.studio/user-upload/8c7e21799dd4-20260514.png)

「ホームから G-01 ナビ経由でカレンダー・顧客・設定に分岐する」 — 文章で読むと大変ですが、**Canvas なら 1 秒で頭に入ります**。

### Firestore ER 図（er-firestore.canvas）

サブコレクションの階層構造をグループで囲み、テーブル名・Path・フィールド表をノードに格納。

![](https://static.zenn.studio/user-upload/4ff3e3fbe6d1-20260514.png)  
「customers → events → memos → attachments」の関係も、矢印で見えるので **同期戦略の議論が早くなる**。

### アーキ図（architecture.canvas）

4 層 Clean Architecture を縦に重ねて、各層に主要モジュールを box で配置。

![](https://static.zenn.studio/user-upload/5983c83a33b9-20260514.png)

「依存方向は Presentation → Application → Domain ← Infrastructure」と文章で書かれても忘れますが、**絵で 1 回見ると忘れない**。

### そして全体の入口になる `index.md`

ここまで紹介した Canvas や各ハブページは、すべて **`index.md` という 1 枚のページ** から辿れるようにしてあります。

![](https://static.zenn.studio/user-upload/f8b9c1d86f03-20260514.png)

新メンバーには「**まず `index.md` を開いて**」と伝えるだけで、自分で必要な情報まで辿り着けるようになりました。

---

## 💡 アプローチ: docs/ を「複製せず」リンクで束ねる

ここがポイントです。

**Obsidian 側に docs/ の本文をコピーしません。**

```
EIGYOU/                              ← リポジトリルート（= Obsidian Vault）
├── docs/                            ← 真実の源（Markdown 原本）
│   ├── ARCHITECTURE.md              ← 1,000行の本文はここに置きっぱなし
│   ├── SCREENS.md                   ← 画面一覧（32画面）
│   └── DB_DESIGN_*.md               ← DB 仕様
│
└── eigyou_wiki/                     ← Obsidian Wiki
    ├── index.md                     ← 🚪 全ドキュメントの目次（入口）
    │
    └── wiki/projects/EIGYOU/
        ├── README.md                ← (A) リンクハブ: プロジェクト入口
        ├── db/README.md             ← (A) リンクハブ: DB 系まとめ
        ├── screens/
        │   ├── README.md            ← (A) リンクハブ: 画面一覧
        │   └── S-04-home.md など    ← (C) 各画面のスタブ（H1+説明1行）
        └── canvas/
            ├── architecture.canvas  ← (B) 派生視覚化: アーキ図
            ├── screen-flow.canvas   ← (B) 派生視覚化: 画面遷移
            ├── er-firestore.canvas  ← (B) 派生視覚化: Firestore ER
            └── er-drift.canvas      ← (B) 派生視覚化: Drift ER
```

ファイルを次のように分類しています。

* **🚪 入口 (`index.md`)**: **すべてのページの目次**。これさえ開けば全体構造が一目で分かる
* **(A) リンクハブ**: docs/ への相対リンク + Wiki 内 wikilink を束ねる玄関ページ。**本文ほぼゼロ**
* **(B) 派生視覚化**: Canvas / ER 図など、docs/ には存在しない図表。**Wiki 固有の価値**
* **(C) 1 行スタブ**: 画面ごとに「タイトル + 1 行説明 + 原本リンク」だけのページ。wikilink のターゲットになる

**docs/ が真実の源**。Wiki 側はリンクと派生情報だけを持つ。これで docs/ を更新しても Wiki は基本的に無変更で済みます。

---

## 🤖 スキル化: Claude Code に Wiki を作らせる

Obsidian で手作業で Canvas を組むのは骨が折れます。そこで Claude Code に **専用 skill** を仕込みました。

```
.claude/skills/eigyou-wiki/
├── SKILL.md                    ← 発動条件・全体フロー
└── references/
    ├── directory-structure.md  ← どこに何を置くか
    └── ingest-workflow.md      ← docs/ → wiki/ 変換の具体手順
```

これを仕込んでおくと、Claude Code でこう指示するだけで Wiki が組み上がります。

```
> /eigyou-wiki docs を全部 Wiki 化して
```

裏側で Claude が:

1. `docs/` の主要ファイルを読み込む
2. 画面一覧・テーブル定義・アーキ層をメタ抽出
3. リンクハブを生成、画面スタブを 32 枚量産
4. Canvas 4 枚を JSON で生成（画面遷移 / ER 図 ×2 / アーキ）
5. `index.md` を更新

…を順番に実行してくれます。

---

## ✨ 結果: 何が変わったか

### 人間にとって

* 新しいメンバーに「まず Canvas 開いて」と言えば、**5 分で全体像が伝わる**
* 「あの画面どこから遷移するんだっけ？」が **画面遷移 Canvas を 1 秒見るだけで解決**
* ER 図のノードをダブルクリックすると `docs/DB_DESIGN_TABLES_FIRESTORE.md` の該当節に飛ぶので、**「概要 → 詳細」の往復が早い**

### AI にとって

* Claude に渡すコンテキストが **「まず Wiki のハブを読んで、必要な docs/ だけ深掘り」** の二段構えに整理できる
* AI が docs/ を全部読み込まなくて済むので **トークン消費が減る**
* 仕様書の更新は docs/ だけに集中するので、**「どっちが正しい？」問題が起きない**

### 結局のところ

**AI に渡す仕様書を整備するのが、人間の重要な仕事**。

その整備作業の半分以上は、実は AI に任せられます。「docs/ から Wiki を生成する skill」を一度書いてしまえば、あとは仕様書が増えるたびに `/eigyou-wiki` を呼ぶだけ。

人間がやるのは:

* docs/ の真実を保つこと
* skill の運用ルール（どこに何を置くか）を設計すること

この 2 つだけになります。

---

## 📝 まとめ

* 長すぎる markdown は **「正しいけど読まれない」** という致命的な弱点を持つ
* Obsidian Vault に **リンクハブ + Canvas で視覚化** すると、docs/ を複製せず「絵で分かる仕様書」が手に入る
* **docs/ を真実の源にして Wiki 側は派生情報だけ持つ** ことで、メンテコストを増やさない
* Claude Code に **専用 skill** を仕込めば、Wiki の生成・更新が自動化できる
* AI 時代、**仕様書整備は人間の中心仕事**。だからこそ skill 化して効率化する価値がある

「mdファイル見にくくない？」というモヤモヤを抱えていた方の、何かのヒントになれば嬉しいです 🗺

---

## 🚀 次回予告

今回は **「こう変わるよ」のビフォーアフター** に絞りました。

次の記事では、**実装の中身** に踏み込みます。

* `eigyou-wiki` skill の SKILL.md の中身（発動条件・委譲ルール）
* Canvas（`.canvas`）の JSON 構造とノード配置のコツ
* Obsidian Bases で「全画面を Plan・優先度で絞り込み表示」する設定
* リンク参照型 Wiki の運用ルール（複製禁止・1 行スタブの作り方）
* Vault ルートの罠（`file` ノードのパス指定でハマった話）

「自分のプロジェクトでも同じ仕組みを組みたい」という方は、次の記事で全部の手の内を公開するので、お楽しみに 🤖

---

最後まで読んでいただきありがとうございました。  
「うちの docs/ もこうしたい」という方は、ぜひコメントや感想をいただけると嬉しいです。
