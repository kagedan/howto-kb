---
id: "2026-07-21-claude-が生成した資料にスクショを追加しnotion-に貼る方法-01"
title: "Claude が生成した資料にスクショを追加しNotion に貼る方法"
url: "https://qiita.com/rikuto125/items/64d39d506dab8420d1fc"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "AI-agent", "LLM", "Python", "qiita"]
date_published: "2026-07-21"
date_collected: "2026-07-22"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code や Claude Artifacts で社内向けの資料（検討資料・ADR・議事録）を作ると、テキストは綺麗に出る。
ところが**スクショや図を1枚入れた瞬間に破綻する**。
Notion の HTML埋め込みブロックに貼ると、画像だけリンク切れになるのだ。

この記事では、その原因と、`data:` URI（Base64埋め込み）＋プレースホルダー注入という回避策を扱う。

最後に、この手順を自動でやってくれる Claude Code スキルも紹介する。

### 生成される資料イメージ(画像挿入式)
![スクリーンショット 2026-07-21 22.21.10.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2601888/d09451f8-4351-47dc-9e98-dcbca208f7de.png)


---

## なぜ画像がリンク切れするのか

Claude Artifacts、そして Notion の HTML埋め込みを含む多くのサンドボックス環境は、
**外部ホストの画像URLを踏めない**。

- CSP（Content Security Policy）で外部画像・CDN へのリクエストが遮断される
- 仮に踏めても、社内の画像置き場URLはいずれ**リンクが腐る（rot）**

つまり `<img src="https://...">` は最初から選択肢にならない。
残る唯一の手段は、画像そのものをファイルに埋め込む `data:` URI（Base64）だ。

```html
<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUg...(数十万文字)..." alt="ログイン画面">
```

これで外部依存はゼロになり、単一HTMLファイルとして完全に自己完結する。

---

## 素直に Base64 を直書きすると、今度は編集できなくなる

ところが Base64 を最初から `<img>` に直書きすると、別の問題が出る。

画像1枚で数十万文字。数枚入れれば HTML は**数百KB〜1MB近く**に膨れる。この状態では、

- エディタの文字列置換（Claude の Edit ツール等）は、巨大なBase64を含む行のマッチが不安定になる
- ファイル全体を読み込む操作はトークンを大量に食い、事実上できない

つまり「画像を入れた瞬間、以降の文章・レイアウト編集が地獄になる」。

---

## 解法：プレースホルダー方式（構造を先に、実データは最後に1回）

ポイントは、**編集の重さと画像の重さを切り離す**こと。
手順はこうなる。

**1. HTML本体にはプレースホルダーだけ書く**

`src` に Base64 を直書きせず、一意な文字列を置く。

```html
<img src="data:image/png;base64,{img_01_login}" alt="ログイン画面">
```

こうすれば HTML は数十KBの見通しの良いサイズのまま、構造・レイアウト・文章を先に完成できる。

**2. 各画像を Base64 テキスト化しておく**

```bash
base64 -i shots/01-login.png -o shots/01-login.png.b64
```

**3. 最後に1回だけ、機械置換で実データを注入する**

```python
from pathlib import Path

html_path = Path("doc.html")
html = html_path.read_text()

mapping = {
    "{img_01_login}":  "shots/01-login.png.b64",
    "{img_02_detail}": "shots/02-detail.jpg.b64",
}
for placeholder, b64_path in mapping.items():
    b64 = Path(b64_path).read_text().replace("\n", "")
    html = html.replace(placeholder, b64)

html_path.write_text(html)
```

テキスト編集はすべて「軽いプレースホルダー版」に対して行い、
実データ注入は最後の Python 置換1回で終わる。これが肝。

**4. 注入後はタグバランスを機械チェック**

置換後のHTMLは目視確認が困難なので、開閉タグ数の一致だけ機械的に見ておく。

```python
import re
html = open("doc.html").read()
for tag in ("div", "section", "table"):
    op = len(re.findall(rf"<{tag}[\s>]", html))
    cl = len(re.findall(rf"</{tag}>", html))
    print(f"{tag}: open={op} close={cl} {'OK' if op == cl else 'MISMATCH'}")
```
---

## ついでに：資料そのもののデザインも揃える

画像問題を解決しても、資料の見た目がバラバラだと結局読まれない。
情報が多い資料ほど読み手は全部読まないので、**色を絞るのが効く**。

- 黒文字 × 白背景をベースに、**黄色マーカーは1色だけ**
- マーカーを引くのは「結論・数字・期限」に限定（1段落1箇所まで）
- 表が長ければ 表⇔カード切替、行クリックで詳細展開、などの拾い読み用インタラクション

こうすると、拾い読みだけで意思決定に必要な情報が拾える資料になる。

---

## 手順を自動化する Claude Code スキルにした

上の「デザインシステム＋Base64注入」を毎回手でやるのは面倒なので、
Claude Code の Agent Skill として公開した（MIT / OSS）。

https://github.com/rikuto125/team-doc-design 

Claude Code にこう頼むだけ：

- 「このツール導入の検討資料を作って」
- 「この決定をADRにまとめて」
- 「議事録をきれいにまとめて」

検討資料・コード解説・ADR・議事録の4テンプレートと、上記のBase64注入手順が入っている。

```bash
# 日本語版・英語版の両方
npx skills add rikuto125/team-doc-design

# 日本語版だけ
npx skills add rikuto125/team-doc-design --skill team-doc-design-ja
```

Claude Code の公式プラグインとしても入る。

```
/plugin marketplace add rikuto125/team-doc-design
/plugin install team-doc-design@team-doc-design
```

---

## おわりに

`data:` URI 自体は枯れた技術だが、「プレースホルダーで構造を先に作り、実データは最後に注入する」という分離を挟むと、Claude/LLM との相性が一気に良くなる、というのが個人的な発見だった。

同じ「Notion 画像リンク切れ」で消耗している人の役に立てば。
Star / Issue / 改善 PR 歓迎です 🙏

<!--
  投稿前チェック:
  - [ ] hero-screenshot.jpg / showcase-detail.jpg を実ファイルとして同じディレクトリに置く
        (リポジトリ内の docs/hero-screenshot.jpg, docs/showcase-detail.jpg をコピー)
  - [ ] Qiita のタグを設定: Claude, ClaudeCode, Notion, HTML, OSS など
-->
