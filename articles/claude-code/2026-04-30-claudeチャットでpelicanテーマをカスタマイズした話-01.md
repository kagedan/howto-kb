---
id: "2026-04-30-claudeチャットでpelicanテーマをカスタマイズした話-01"
title: "ClaudeチャットでPelicanテーマをカスタマイズした話"
url: "https://qiita.com/y_catch/items/70fd9324a4e3eeb254d5"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-30"
date_collected: "2026-05-01"
summary_by: "auto-rss"
---

Claudeで何かを作る練習として、自分が管理・運営しているブログのデザインテンプレートを作ってみました。

- [Heppocode Garage](https://www.catch.jp/heppocode-garage2/)

このブログは、Python製の静的サイトジェネレータ「Pelican」で運営しています。2024年ごろに、Wordpressから移行しました。

- [WordpressからPelicanに移行した手順のメモ #Python - Qiita](https://qiita.com/y_catch/items/c16c738a720178b3e1e8)

ただ、移行した時に気に入ったデザインテンプレートがなくて、あり合わせのデザインで放置していました。

今回、このデザインを改善するため、Claudeで作ってみることにしました。

Claude Codeではなくチャットベース(Sonnet 4.6)を使って、必要なファイルを作成させています。ClaudeとClaude Codeを使い始めたばかりで慣れていないので、まずはチャットで練習しながら、実力を確認しようという目論見です。


## 1.見本になるWordpressテーマの特長を調べる

> PelicanのThemeを入れ替える。次のWordpressテーマをベースにする
> - AAAAAAA
> 
> このWordpressテーマのデザイン上の特長をリストアップして

そのままのデザインを採用する訳ではないけれど、どう言語化すればいいのか調べてみました。その結果、取り入れたいデザインはPinterest風のスタイルで「マソンリーグリッド」と呼ぶらしい（一般的には、「メイソンリー masonry」なのかな）


## 2.ベースになるPelicanのテーマを選定する

> 既存のPelican Themeをカスタマイズして実現する。
> まず、ベースになるPelicanのテーマを選定して。

候補を絞り込みます。マソンリーグリッドに適した構造を持つテーマを詳しく調べます。主要なテーマの構造と特徴が把握できました。比較表を整理します。調査結果をまとめて、比較表とおすすめを提示します。

---

### おすすめ: Flex テーマ

マソンリーグリッドを実現するベースとして、**Flex** が最適です。理由は次のとおりです。

**Flexを選ぶ理由：**

Flexは `base.html` → `index.html` のシンプルなJinja継承構造を持ち、改造ポイントが明確です。デフォルトで左サイドバー（サイト名・カテゴリ一覧）を持つ点が一致しており、サイドバー部分はほぼそのまま使えます。外部CSSフレームワークに依存していないため、マソンリーグリッド用のCSSをまっさらに書けます。`index.html` の記事ループ部分をグリッドに差し替えるだけで済みます。

**改造する具体的なファイルは2つのみ：**
- `templates/index.html` — マソンリーグリッドのHTML構造を書く
- `static/css/style.css` — CSS column-count または Masonry.js でグリッドを実現

---

このまま **Flexをベースに改造手順・コードを作成** に進みますか？

## 3.修正手順を確認する

> Flexテーマをベースにして、マソンリーグリッドに改造する。
> Flexのコードを直接変更しない。
> Pelican Themeのカスタマイズ方法を確認して。

公式ドキュメントと実装の詳細が確認できました。整理します。

---

Pelicanには**3つの公式カスタマイズ手段**があります。Flexを一切触らずにマソンリーグリッドを実現するには、これらを組み合わせます。

---

### 方法 1 — `THEME_TEMPLATES_OVERRIDES`（推奨）

Jinja2がテーマの `templates/` を検索する前に先に探すパスを指定できる設定。テーマをフォークせずに個別テンプレートを上書きできる。

```python
# pelicanconf.py

THEME = 'path/to/Flex'          # Flexはそのまま

THEME_TEMPLATES_OVERRIDES = [
    'overrides/templates',       # ← ここに置いたファイルが優先される
]
```

`overrides/templates/index.html` だけ置けば、Flexの `index.html` だけが差し替わり、他のテンプレート（`article.html`, `base.html` など）はFlexのものをそのまま使う。

---

### 方法 2 — Jinja継承で `{% extends %}` を使う

`{% extends "!simple/index.html" %}` のように `!` プレフィックスでsimpleテーマのテンプレートを継承できる。通常の `{% extends "index.html" %}` で同テーマ内の継承も可能。

ただし この `!テーマ名` 記法は `simple` テーマに対してのみ機能し、Flexのような任意テーマを `!Flex/base.html` のように継承することはできない。

→ **Flexに対しては方法1が現実的な選択肢。**

---

### 方法 3 — `STATIC_PATHS` でCSSを追加注入

FlexはCSS上書き変数 `CUSTOM_CSS` に対応しているため、CSSだけで見た目を変えるアプローチ：

```python
# pelicanconf.py
CUSTOM_CSS = 'static/css/masonry.css'   # Flex固有の設定変数
STATIC_PATHS = ['images', 'static']     # 自前のstatic/を追加コピー
```

---

### 今回の構成（方法1 + 方法3の組み合わせ）

```
mysite/
├── pelicanconf.py
├── content/
│   └── (記事ファイル)
├── overrides/
│   └── templates/
│       └── index.html        ← Flexのindex.htmlだけ上書き
└── static/
    └── css/
        └── masonry.css       ← マソンリーグリッドのCSS追加
```

```python
# pelicanconf.py
THEME = 'path/to/Flex'

THEME_TEMPLATES_OVERRIDES = ['overrides/templates']

STATIC_PATHS = ['images', 'static']
CUSTOM_CSS = 'static/css/masonry.css'
```

---

**この方針でよければ、次のステップ（`overrides/templates/index.html` と `masonry.css` の実装）に進みますか？**

## 4.テーマの差分を実装してもらう

> overrides/templates/index.html と masonry.css の実装を実装して

テンプレートファイルを直接取得します。ユーザーが指定したURLから直接取得します。GitHub のレート制限がかかっています。Flexのライブデモサイトから実際のHTMLを確認します。ライブデモのHTMLソースを確認して実際のDOM構造を把握します。ライブデモとFlexのWikiで設定変数を確認します。必要な情報が揃いました。Flexのライブデモから実際のHTML構造（`#wrapper > #sidebar + main > article`）、`CUSTOM_CSS`、`THEME_TEMPLATES_OVERRIDES`の使い方がわかりました。実装します。

---

### `overrides/templates/index.html`の実装

Flexの `index.html` を `{% extends "index.html" %}` で継承し、`{% block content %}` だけを差し替えています。各記事を `.masonry-card` としてレンダリングし、`article.cover` メタデータがある記事はサムネイル付き、ない記事はテキストカード（黒いルーラー付き）として表示します。

### `content/static/css/masonry.css`の実装

CSS `column-count` でマソンリーグリッドを実現しています。Playfair Display（見出し）と Lato（本文）でタイポグラフィを再現しています。Flexの既存レイアウトを `!important` で最小限上書きし、レスポンシブ対応（デフォルト2列、1280px以上で3列、700px以下で1列）を含みます。

### `pelicanconf.py`の実装

3行の追加だけでFlexを完全に無変更のまま動作させます。

```python
THEME_TEMPLATES_OVERRIDES = ["overrides/templates"]  # index.html だけ差し替え
CUSTOM_CSS = "static/css/masonry.css"                # CSS を追加注入
STATIC_PATHS = ["images", "static"]                  # CSS ファイルを output へコピー
```


## 5. 適用方法を調べる

> 既存のPelicanサイトに、Flexテンプレートをそのまま導入する手順は

情報が揃いました。インストール方法は2つあり、実際の手順を整理します。

---

Flexテーマを既存Pelicanサイトにインストール方法は**2択**あります。

---

### 方法A — プロジェクト内にクローン（推奨・シンプル）

```bash
# サイトルートで実行
cd /your-pelican-site

# themes/ ディレクトリにクローン
git clone https://github.com/alexandrevicenzi/Flex themes/Flex
```

```python
# pelicanconf.py
THEME = "themes/Flex"   # ← 相対パスで直接指定
```

メリット：仮想環境に依存しない、git で Flex のバージョン管理できる。

---

### 方法B — `pelican-themes` コマンドでシステムインストール

```bash
# pelican-themes のリポジトリをクローン（全テーマ入り、大きいので注意）
git clone --recursive https://github.com/getpelican/pelican-themes ~/pelican-themes

# Flex だけをインストール
pelican-themes --install ~/pelican-themes/Flex

# インストール確認
pelican-themes --list
```

```python
# pelicanconf.py
THEME = "Flex"   # ← テーマ名だけでOK（パス不要）
```

または、Flexは pelican-themes リポジトリ内のものが最新でないことがあるので、Flex公式リポジトリから直接インストールする方が確実。

```bash
git clone https://github.com/alexandrevicenzi/Flex ~/Flex
pelican-themes --install ~/Flex
```

---

### 最小限の `pelicanconf.py` 設定

Flexを動かすのに**必須なのは `THEME` だけ**ですが、Flexのwikiに掲載されている設定例を参考に、最低限これを追加します：

```python
# テーマ指定
THEME = "themes/Flex"          # 方法Aの場合
# THEME = "Flex"               # 方法Bの場合

# Flex 固有の変数（省略するとデフォルト値が使われる）
SITETITLE   = "サイト名"
SITESUBTITLE = "サブタイトル"

# 既存サイトで使っていた STATIC_PATHS はそのまま残す
STATIC_PATHS = ["images"]
```

---

### ビルドして確認

```bash
pelican content
pelican --listen      # http://localhost:8000 で確認
```

---

### 注意点

**既存記事のメタデータはそのまま使える**ので、コンテンツ側の変更は不要です。ただし、以前のテーマで使っていた `THEME` 固有の変数（例：`CSS_FILE` など）は Flex では使われないので、`pelicanconf.py` から外しておくと警告が出なくなります。

テーマ導入が確認できたら、前のステップで作成した `overrides/templates/index.html` と `masonry.css` を追加してマソンリーグリッド化に進めます。


## 6. デバッグ

> pelican content 
> [17:12:10] CRITICAL RecursionError: maximum recursion depth exceeded

テンプレートの継承でループが起きています。問題のある `index.html` を確認します。

原因が明確です。`THEME_TEMPLATES_OVERRIDES` に置いた `index.html` が `{% extends "index.html" %}` で自分自身を参照して無限ループになっています。

`THEME_TEMPLATES_OVERRIDES` の探索順は「overrides → テーマ」なので、Jinja2が `"index.html"` を解決する際にまた自分自身を見つけてしまいます。

**修正方法：** Flexの `base.html` を継承する形に変えます。

**原因と修正の説明：** `THEME_TEMPLATES_OVERRIDES` はJinja2の検索パスの**先頭**に追加されます。そのため `{% extends "index.html" %}` と書くと、Jinja2は `"index.html"` を探す際に再び `overrides/templates/` を先に見て——自分自身を発見し、無限ループになっていました。

**修正：** `{% extends "base.html" %}` に変更しました。`base.html` はoveridesフォルダに存在しないので、Jinja2は正しくFlexの `base.html` を参照します。Flexの `index.html` が持っていたブロック構造と同じ `{% block content %}` をそのまま使えるので動作は変わりません。

> 記事が、正常に表示されない。（画面ショットを添付）

原因が確定しました。

```css
/* style.min.css より */
aside {
  width: 25vw;
  position: fixed;   ← ここ
  top: 0;
  left: 0;
}
```

`aside` が `position: fixed` なので、`main` はページ左端（x=0）から始まっています。`main` に `margin-left: 25vw` を追加すれば直ります。`masonry.css` を更新しました。追加した内容は2点です。

```css
main {
  margin-left: 25vw !important;   /* aside の固定幅と揃える */
  padding: 32px 36px 60px !important;
}

@media screen and (max-width: 768px) {
  main { margin-left: 0 !important; }  /* モバイルは解除 */
}
```

**なぜこれで直るか：** `aside` が `position: fixed` のためドキュメントフローから外れており、`main` はページ左端から描画されます。`aside` の幅 `25vw` と同じ値を `main` の `margin-left` に設定することで、`main` のコンテンツが `aside` の右側から始まるようになります。


## 完成したサイト

最終的に、こんな感じのデザインになりました。作業時間は、4-6時間くらいです。

![Heppocode_Garage_top.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/86880/aee414e3-e5d8-499b-a872-93dd50759df5.png)

- [Heppocode Garage](https://www.catch.jp/heppocode-garage2/)

元にしたPelicanテンプレートは、こちら。

- [Flex](https://flex.alxd.me/)

マソンリーグリッド以外にも、細かくデザインを調整しています。

この場所がおかしい、ここを変更したいと指摘すれば、的確に修正してくれます。画面ショットを添付すれば、そこから情報を読み取ってくれるので、何でもテキストプロンプトで書かなくてもいいし、こちらが気付いていない箇所も読み取ってくれます。例えば、ブラウザの開発ツールの画面ショットを添付すると、そこからHTMLやCSSの状態を読み取って、ちゃんと修正してくれるという具合です。

普段、プログラミングやWebデザインをやっている訳ではない素人なので、ここまで手伝ってもらえたのはスゴく助かりました。

Claude Codeを使えば、ファイルコピーをしなくて済むので手間は減りそうですが、その分、勝手に書き換えられないよう、いろいろガードレール的な準備が必要になりそう。たまにいじる程度なら、チャットでやるのが楽かも。

他にも、いろいろ試してみようと思います(お気持ち表明)。
