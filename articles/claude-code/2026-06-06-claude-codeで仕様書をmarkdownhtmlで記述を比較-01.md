---
id: "2026-06-06-claude-codeで仕様書をmarkdownhtmlで記述を比較-01"
title: "Claude Codeで仕様書をMarkdown/HTMLで記述を比較"
url: "https://zenn.dev/kawauchi_lab/articles/4b300879a41ab5"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-06-06"
date_collected: "2026-06-07"
summary_by: "auto-rss"
query: ""
---

# Claude Codeで仕様書をMarkdown/HTMLで記述を比較

AI駆動開発・仕様駆動開発の流れのなかで、仕様書の存在感が増しています。Claude の技術ブログ [Using Claude Code: The unreasonable effectiveness of HTML](https://claude.com/blog/using-claude-code-the-unreasonable-effectiveness-of-html) でも HTML 出力の有効性が語られています。

仕様書を Markdown と HTML のどちらで書くか。迷いながらどちらでも書いてきましたが、一度きちんと比較してみることにしました。

題材は、最近開発していたアカウント管理システムです。このソースコードを Claude Code に読み込ませ、基本的な条件をそろえたうえで、Markdown / HTML と諸条件を変えて仕様書を生成し、比較しました。

**見やすさの比較などを下に置いていますので参考にしてください**

![](https://static.zenn.studio/user-upload/35376ebd2e1b-20260606.jpg)

## 目次

## 検証方法

詳しい条件は下記の通りです。**図の表現**も見たかったので mermaid、HTML の表示確認のために **Playwright での自己検証**、さらに **HTML 特有の Interactive 表現**の指示も混ぜています。

| 項目 | 内容 |
| --- | --- |
| モデル | Opus 4.8 / high effort |
| 入力 | 実装コードのみ（`ledger.html` + `serve.py` + `data/*.csv`） |
| 進め方 | 各版を独立セッションで起動し、`/goal` で「成果物が完成している」状態まで完走 |
| 変えた点 | 出力形式の指定だけ（Markdown / HTML、mermaid・Interactive・Playwright 自己検証の有無） |

| 版（記事内の呼び方） | 出力形式 | mermaid | Interactive 表現 | Playwright 自己検証 |
| --- | --- | --- | --- | --- |
| markdown 指示 | Markdown | – | – | – |
| markdown + mermaid 指示 | Markdown | ✓ | – | – |
| html 指示 | HTML | – | – | – |
| html 指示 + Playwright | HTML | – | – | ✓ |
| html 指示 + Interactive + Playwright | HTML | – | ✓ | ✓ |

### 共通プロンプト

```
# 指示

`source/` にあるシステムの実装コードを解析し、**仕様書を作成**してください。

## 入力
- `source/ledger.html` — 台帳アプリ（単一HTML・依存なし）
- `source/serve.py` — ローカルサーバー
- `source/data/*.csv` — 台帳データ（実体）

これら**実装コードのみ**を根拠に、システムの仕様をリバースで起こしてください。
（仕様書・設計書の類は渡していません。コードと実データから読み取れることだけを書いてください。）

## 出力
- **<Markdown または HTML>形式**の仕様書を、このプロジェクト直下（`source/` の外）に出力してください。
- ファイル名は `仕様書.<md または html>`。
- `source/` 配下は**読み取り専用**。一切変更しないでください。

## 仕様書に含めるべき観点
- システムの目的・概要
- データモデル（エンティティと関連）
- 各エンティティの項目（列）とその意味
- 主要機能・画面の挙動
- 起動・運用方法

## 条件
- モデル: Opus 4.8 / high effort
```

### 変更プロンプト（版ごとに足す部分）

**mermaid 指示**（markdown + mermaid 版で追加）

```
## 可視化
- 実装を見ない引き継ぎ者が理解しやすいよう、**図で可視化**してください。特にデータモデル（エンティティ関連）と全体構成は図にしてください。
- 図は **mermaid** で描いてください（`erDiagram` / `flowchart` 等）。**ASCIIアート（罫線文字で描いた図）は使わないでください。**
- すべてを1枚の図に詰め込む必要はありません。**観点ごとに図を分けて**構いません。
```

**作図指示（HTML）**（html の図あり版で追加。mermaid 指示の代わりに使う）

```
## 可視化
- 実装を見ない引き継ぎ者が理解しやすいよう、**図で可視化**してください。特にデータモデル（エンティティ関連）と全体構成は図にしてください。
- HTMLの表現力を活かして作図してください（SVG・CSS・table 等）。**ASCIIアート（罫線文字で描いた図）は使わないでください。**
- すべてを1枚の図に詰め込む必要はありません。**観点ごとに図を分けて**構いません。
```

**Interactive 表現指示**（interactive 版で、上の作図指示にさらに1行追加）

```
- さらに、読み手の理解を助けるため、**インタラクティブな要素を取り入れてください**（例：折りたたみ・タブ・ホバー説明・フィルタ・図のクリックで詳細表示 など）。静的に読むだけの仕様書にしないでください。
```

**Playwright 自己検証指示**（Playwright 版で追加。冒頭にも一文を足す）

```
## 自己検証（このプロジェクト固有）
- 出力した `仕様書.html` を **Playwright MCP** でブラウザに開き、実際の表示を確認してください。
- レイアウトが崩れていないか・読み手にとって意図通りに見えるかを確認し、**問題があれば修正して再確認**してください。
- 検証対象は**自分が生成した仕様書HTML**です（台帳アプリ `ledger.html` の動作確認ではありません）。
```

---

## 実行時間・トークン比較

時間とトークンを計測しました。

* HTML にすると**2倍**
* 図の要素が入ると**2倍**
* Interactive要素を入れると**2倍**  
  と膨らんでいきます。

仕様駆動開発では**仕様のメンテナンス**も必要になるため、直すたびにこのコストがかかります。図や Interactive な要素はかなり見やすくなるので悩ましいところですが、Interactive 要素まで入れると現実的に回らなくなりそうです。

| 版 | 時間 | ターン | トークン |
| --- | --- | --- | --- |
| markdown 指示 | 3m | 1 | 13.7k |
| markdown + mermaid 指示 | 5m | 1 | 20.1k |
| html 指示 | 7m | 1 | 33.5k |
| html 指示 + Playwright | 17m | 1 | 52.4k |
| html 指示 + Interactive + Playwright | 33m | 1 | 114.1k |

---

## 仕様書の見やすさ比較

それぞれの条件での見やすさの参考に、本文・表・システム構成図・ER図を並べます。

### text（本文）

仕様書のデザインは**HTMLにするとより気分が良くなります**。気分よく開発ができます。  
下の方に行けば行くほど気持ちよく見る気が起こると思います。

**markdown 指示**  
![](https://static.zenn.studio/user-upload/bebd44f51199-20260606.png)  
**html 指示**  
![](https://static.zenn.studio/user-upload/fc82ae37c8db-20260606.png)  
**html 指示 + Playwright での自己検証指示**  
![](https://static.zenn.studio/user-upload/4a1ddade1deb-20260606.png)  
**html 指示 + Interactive 表現指示 + Playwright での自己検証指示**  
![](https://static.zenn.studio/user-upload/39598dc92dae-20260606.png)

### table（表）

テーブルは無味乾燥な表から、だんだん**カラフルで何か意味がありそうな、読んで楽しそうな形に**変化しました。

**markdown 指示**  
![](https://static.zenn.studio/user-upload/09849e07ab60-20260606.png)  
**html 指示**  
![](https://static.zenn.studio/user-upload/a2bc4bcbc7ba-20260606.png)  
**html 指示 + Interactive 表現指示 + Playwright での自己検証指示**  
![](https://static.zenn.studio/user-upload/5ee19db9c286-20260606.png)

### Architecture（システム構成図）

アーキテクチャ図は、何か理解した気分になれる図に下に行くほどなっている気がします。

**markdown 指示**  
![](https://static.zenn.studio/user-upload/ee7740943fc7-20260606.png)  
**markdown + mermaid 指示**  
![](https://static.zenn.studio/user-upload/d7eae904c3c9-20260606.png)  
**html 指示**  
![](https://static.zenn.studio/user-upload/35ba770acf7d-20260606.png)  
**html 指示 + Interactive 表現指示 + Playwright での自己検証指示**  
![](https://static.zenn.studio/user-upload/3c5a4180e6eb-20260606.png)

### ER（ER図）

ER図は実際に読みやすくて助かる。

**markdown 指示**  
![](https://static.zenn.studio/user-upload/ba68ce1b16ed-20260606.png)  
**markdown + mermaid 指示**  
![](https://static.zenn.studio/user-upload/38bf8d1f9c44-20260606.png)  
**html 指示**  
![](https://static.zenn.studio/user-upload/697ccb83f613-20260606.png)  
**html 指示 + Interactive 表現指示 + Playwright での自己検証指示**  
![](https://static.zenn.studio/user-upload/d7585f151ff2-20260606.png)

---

## Interactive の動作

Interactive 版の実際の操作の様子です。  
操作感が上がるので、あれこれ開いたりするより、実際の工数が削減できるようになり。  
脳の効率が上がります。

![](https://static.zenn.studio/user-upload/f1e73d170bae-20260606.gif)

## まとめ

HTML仕様書のがいいし、Interactiveな仕様書はなお良い。  
だからぜひ、これで作業したいが、実際はドキュメントの作成編集時間が延びるため、できなくて悲しい。
