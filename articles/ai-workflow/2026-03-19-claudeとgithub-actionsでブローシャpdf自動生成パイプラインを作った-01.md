---
id: "2026-03-19-claudeとgithub-actionsでブローシャpdf自動生成パイプラインを作った-01"
title: "ClaudeとGitHub ActionsでブローシャPDF自動生成パイプラインを作った"
url: "https://qiita.com/tokistorage/items/f0c32dbd04ce127dd7ce"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-03-19"
date_collected: "2026-03-19"
summary_by: "auto-rss"
---

## TL;DR

* HTMLでブローシャを作り、GitHub Actionsで自動的にA4横PDFを生成・コミットするパイプラインを構築した
* DockerイメージはChromeやNode.js込みの`ghcr.io/puppeteer/puppeteer`を使うことでインストール工程をほぼゼロにした
* 絵文字はDockerコンテナ内で文字化けするのでSVGアイコンに置き換えた
* Actions内でgit pushするときは`stash → pull rebase → pop → push`の順番が重要
* HTMLを更新してpushするだけでPDFが自動再生成・コミットされる

---

## やったこと・背景

行政向けのブローシャ（A4横・1ページ）をHTMLで作っていた。毎回ローカルでPDFを生成してコミットするのが面倒だったので、HTMLを更新してpushするだけでPDFが自動生成される仕組みを作った。

ブローシャのHTMLはClaudeと対話しながら設計・文言を磨いていった。「このコピーは担当者目線になっているか」「行政機関に補助金という言葉は正しいか」といった議論をしながら、HTMLを直接編集してpushする流れだ。

最終的な構成：

```
ブローシャHTML更新 → git push
  ↓
GitHub Actions起動
  ↓
Puppeteer（Docker）でA4横PDF生成
  ↓
asset/brochure.pdf をコミット・push
  ↓
WEBページのダウンロードボタンからDL可能に
```

---

## ワークフローの全体像

generate-brochure-pdf.yml

```
name: Generate Brochure PDF

on:
  push:
    paths:
      - 'brochure-government-dx.html'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  generate-pdf:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/puppeteer/puppeteer:latest
      options: --user root

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install puppeteer locally
        run: npm install puppeteer --prefix /tmp/pdf

      - name: Serve HTML locally
        run: |
          npx http-server . -p 8080 --silent &
          sleep 2

      - name: Generate PDF
        run: |
          node - << 'EOF'
          const puppeteer = require('/tmp/pdf/node_modules/puppeteer');
          const fs = require('fs');

          (async () => {
            const browser = await puppeteer.launch({
              headless: true,
              args: ['--no-sandbox', '--disable-setuid-sandbox']
            });
            const page = await browser.newPage();
            await page.goto('http://localhost:8080/brochure-government-dx.html', {
              waitUntil: 'networkidle0',
              timeout: 30000
            });
            const pdf = await page.pdf({
              landscape: true,
              width: '297mm',
              height: '210mm',
              printBackground: true,
              margin: { top: 0, bottom: 0, left: 0, right: 0 }
            });
            fs.mkdirSync('asset', { recursive: true });
            fs.writeFileSync('asset/brochure-government-dx.pdf', pdf);
            console.log('PDF generated:', fs.statSync('asset/brochure-government-dx.pdf').size, 'bytes');
            await browser.close();
          })();
          EOF

      - name: Commit and push PDF
        run: |
          git config --global --add safe.directory /__w/lp/lp
          git config user.email "your@email.com"
          git config user.name "GitHub Actions"
          git add asset/brochure-government-dx.pdf
          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            git stash
            git pull --rebase origin main
            git stash pop
            git add asset/brochure-government-dx.pdf
            git commit -m "Auto-generate brochure PDF [skip ci]"
            git push
          fi
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## ハマりポイントと解決策

### 1. Dockerコンテナ内でPuppeteerのモジュールが見つからない

`ghcr.io/puppeteer/puppeteer`イメージにはPuppeteerが含まれているが、コンテナ内のパスが通っておらず`Cannot find module 'puppeteer'`エラーが出た。

**解決策：** `/tmp/pdf`に明示的にインストールして絶対パスで`require`する。

```
const puppeteer = require('/tmp/pdf/node_modules/puppeteer');
```

### 2. 絵文字が文字化けする

📊📋⚖️ などの絵文字をHTMLに使っていたが、DockerコンテナのChromeには絵文字フォントがなく、PDFで文字化けした。

**解決策：** 絵文字をインラインSVGに置き換える。

```
<!-- Before -->
<span class="wall-icon">📊</span>

<!-- After -->
<svg class="wall-icon" viewBox="0 0 20 20" fill="none">
  <rect x="2" y="10" width="3" height="8" rx="1" fill="#2563EB"/>
  <rect x="8" y="6" width="3" height="12" rx="1" fill="#2563EB"/>
  <rect x="14" y="2" width="3" height="16" rx="1" fill="#1E3A5F"/>
</svg>
```

フォントに依存しないのでどの環境でも確実に表示される。

### 3. git pushがリジェクトされる

ActionsでPDFを生成している間に別のcommitが入ると、pushが`fetch first`エラーになる。

**解決策：** `stash → pull rebase → pop → commit → push`の順番にする。

```
git stash
git pull --rebase origin main
git stash pop
git add asset/brochure.pdf
git commit -m "Auto-generate PDF [skip ci]"
git push
```

`[skip ci]`をcommitメッセージに入れることで、PDF生成のcommitがActionsを再トリガーするループを防ぐ。

### 4. Dockerコンテナ内でgitが「not in a git directory」になる

`--user root`でコンテナを起動しているため、gitがリポジトリを別ユーザーのディレクトリと判断してブロックする。

**解決策：**

```
git config --global --add safe.directory /__w/lp/lp
```

パスはリポジトリ名によって変わる（`/__w/{repo}/{repo}`の形式）。

### 5. 日本語フォントがなく文字化けする（aptインストール方式の場合）

`ubuntu-latest`で`apt-get install fonts-noto-cjk`する方式だと毎回60MB以上のダウンロードが発生して遅い。

**解決策：** `ghcr.io/puppeteer/puppeteer`イメージに切り替える。このイメージにはNotoフォント含む日本語フォントが同梱されており、インストール不要。

---

## Dockerイメージ選定の比較

| 方式 | 所要時間 | 日本語対応 | 絵文字対応 |
| --- | --- | --- | --- |
| ubuntu-latest + apt install | 4〜5分（毎回） | ✅ apt installで可 | ❌ 別途フォント必要 |
| ghcr.io/puppeteer/puppeteer | 1〜2分 | ✅ 同梱 | ❌ 絵文字フォントなし |

絵文字問題はどちらの方式でも発生するため、SVGアイコンへの置き換えが根本的な解決策になる。

---

## HTML側のprint CSS設計

ブローシャをWEBページとPDF両方に対応させるため、`@media print`でレイアウトを切り替えている。

```
/* 通常表示 */
.body-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
}

/* 印刷時 */
@media print {
    body { font-size: 11px; line-height: 1.42; }
    .body-grid { gap: 0.55rem; }
    .br-nav, .pdf-download, .br-footer { display: none; }
}
```

**A4横1ページに収めるコツ：**

* ベースフォントは10〜11px（これ以上大きくすると2ページになりやすい）
* 行間は1.4〜1.5（1.6以上は危険）
* セクション間のmarginは2〜3mm
* 絵文字はSVGアイコン（幅・高さ固定）に置き換える

---

## WEBページからのダウンロードボタン

PDFが生成されたかどうかをfetchで確認して、存在する場合だけダウンロードボタンを表示する。

```
<a id="btn-dl" href="asset/brochure.pdf" download style="display:none;">
  ⬇ PDFダウンロード
</a>

<script>
fetch('asset/brochure.pdf', { method: 'HEAD' })
  .then(r => {
    if (r.ok) document.getElementById('btn-dl').style.display = 'inline-block';
  })
  .catch(() => {});
</script>
```

---

## まとめ

| やりたいこと | 解決策 |
| --- | --- |
| HTMLからA4横PDFを生成 | Puppeteer + `page.pdf({ landscape: true, width: '297mm' })` |
| 日本語フォント対応 | `ghcr.io/puppeteer/puppeteer`イメージを使う |
| 絵文字の文字化け | インラインSVGアイコンに置き換える |
| Actions内でgit push | `stash → pull rebase → pop → commit → push` |
| push競合ループ防止 | commitメッセージに`[skip ci]`を入れる |
| gitのsafe.directory | `git config --global --add safe.directory /__w/{repo}/{repo}` |

HTMLを更新してpushするだけでPDFが自動再生成される構成が完成した。ブローシャの文言を磨くたびに手動でPDFを生成する手間がなくなり、常に最新版がダウンロードできる状態を維持できる。

---

*この記事は [TokiStorage](https://tokistorage.github.io/lp/) の行政DXブローシャ開発の過程で得た知見をまとめたものです。ブローシャの設計思想については[こちらのエッセイ](https://tokistorage.github.io/lp/language-changes-who-receives.html)で詳しく書いています。*
