---
id: "2026-06-13-topicstxtを書くだけarxivの最新論文をpdfで届けるツール作った-01"
title: "topics.txtを書くだけ。arXivの最新論文をPDFで届けるツール作った"
url: "https://zenn.dev/schhrcat/articles/1d15251a3b4311"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "Python", "zenn"]
date_published: "2026-06-13"
date_collected: "2026-06-14"
summary_by: "auto-rss"
query: ""
---

arXivを定期巡回して、興味のあるトピックの最新論文をサマリPDFにまとめ、論文本体も自動ダウンロードするツールを作りました。Claude（チャット + Claude Code）とのペアプログラミングで開発した記録です。  
![](https://static.zenn.studio/user-upload/7728425aaee4-20260612.png)

## なにを作ったか

`topics.txt` にキーワードを書いておくと、arXivから各トピックの最新論文を取得して、サマリPDF＋論文PDFを日付フォルダに保存するPythonツールです。

topics.txt

```
# 1行1トピック、#始まりはコメント
Kondo effect
Green function condensed matter
dynamical mean field theory DMFT
```

実行は1コマンド。

```
python fetch_papers.py --num 5
```

出力はこうなります。

```
output/
  20260316/
    condensed_matter_survey_20260316.pdf  # サマリPDF
    2603.13047.pdf                        # 論文PDF
    2603.12844.pdf
    ...
```

私は物性物理（近藤効果・DMFT・グリーン関数）で使っていますが、`topics.txt` を書き換えれば機械学習でも量子情報でも、arXivにある分野なら何でも追えます。

## arXiv APIの罠：sortBy=submittedDate が機能しない

本題です。当初はarXiv公式APIで実装しました。Pythonには公式推奨の `arxiv` パッケージがあり、ドキュメント通りに書けば動きます。

```
import arxiv

search = arxiv.Search(
    query="cat:cond-mat AND Kondo",
    max_results=5,
    sort_by=arxiv.SortCriterion.SubmittedDate,  # 新しい順…のはず
)
```

ところが返ってきたのは **2003〜2004年の論文** でした。「投稿日の新しい順」を指定しているのに、20年以上前の論文が「最新」として返ってくる。

### 試行錯誤の全記録

| 試した方法 | 結果 |
| --- | --- |
| `arxiv` パッケージ + `SortCriterion.SubmittedDate` | 2003年の論文が返る |
| クエリに `submittedDate:[202401010000 TO *]` フィルタ | HTTP 500 |
| `sortBy=lastUpdatedDate` に変更 | やはり古い論文が混在 |
| API取得後にPython側で日付フィルタ | 全件弾かれて0件 |
| Semantic Scholar APIに乗り換え | HTTP 429（レート制限） |
| **arXiv検索ページのスクレイピング** | **成功** ✅ |

`sortBy=submittedDate` は内部IDベースのソートが混在しているらしく、実質的に機能していませんでした。日付範囲フィルタはサーバーが500を返すので回避不能。

### 解決策：人間が見ているページをそのまま取る

ブラウザで <https://arxiv.org/search/> を開くと、新着順の論文が**正しく**表示されます。APIが信用できないなら、人間が見ているのと同じページを取りに行けばいい。

```
ARXIV_SEARCH = "https://arxiv.org/search/"

params = {
    "searchtype": "all",
    "query": query,
    "start": 0,
    "order": "-announced_date_first",  # 新着順
}
resp = requests.get(ARXIV_SEARCH, params=params, headers=HEADERS, timeout=30)
```

`requests` + `BeautifulSoup` に切り替えた瞬間、2026年3月の論文がずらりと並びました。

```
soup = BeautifulSoup(resp.text, "html.parser")
results = soup.find_all("li", class_="arxiv-result")

for item in results[:num]:
    title_tag = item.find("p", class_="title")
    title = title_tag.get_text(strip=True) if title_tag else "No title"
    # authors, arxiv_id, submitted, abstract も同様に抽出
```

## PDF生成：weasyprint で詰まり pdfkit へ

HTML→PDF変換は最初 `weasyprint` を選びましたが、WindowsではGTK/Pangoランタイムが別途必要で導入が複雑でした。

```
OSError: cannot load library 'libgobject-2.0-0': error 0x7e.
```

`pdfkit` + `wkhtmltopdf` に切り替えたらあっさり動きました。wkhtmltopdf 0.12.6（with patched qt）はWindows向けインストーラがあり、導入は実質ダブルクリックだけです。

```
config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)
pdfkit.from_string(html_content, output_pdf, configuration=config, options=options)
```

## コード構成

```
fetch_papers.py
├── FetchError / PdfError   # カスタム例外
├── load_topics()           # topics.txt 読み込み
├── fetch_papers()          # 検索ページをスクレイピング
├── _parse_entry()          # <li>要素 → 論文メタデータ
├── download_paper_pdfs()   # 論文PDFのダウンロード
├── build_html()            # サマリHTML生成
└── main()                  # CLIエントリポイント
```

例外処理はエラー種別ごとに原因が伝わるメッセージを出すようにしています。

```
try:
    resp = requests.get(ARXIV_SEARCH, params=params, headers=HEADERS, timeout=30)
    resp.raise_for_status()
except requests.exceptions.ConnectionError as exc:
    raise FetchError(f"arXivへの接続に失敗しました（ネットワーク確認を）: {exc}") from exc
except requests.exceptions.Timeout as exc:
    raise FetchError(f"arXivへのリクエストがタイムアウトしました: {exc}") from exc
except requests.exceptions.HTTPError as exc:
    raise FetchError(
        f"arXivがHTTPエラーを返しました (status={exc.response.status_code}): {exc}"
    ) from exc
```

この堅牢化とコメント付与はClaude Codeに依頼しました（後述）。

## 運用：タスクスケジューラで月次自動実行

Windowsのタスクスケジューラにバッチを登録して月1回自動実行しています。

run\_fetch.bat

```
@echo off
cd /d C:\00_main\program\python\get_paper
call .venv\Scripts\activate.bat
python fetch_papers.py --num 5
```

月初にPDFが溜まっていくので、トレンドの変化を後から追えます。

## Claude Chat と Claude Code の役割分担

今回の開発で見えた分業の形です。

| 作業 | 担当 |
| --- | --- |
| 設計・仕様決め | Claude Chat |
| APIの罠の調査・デバッグ | Claude Chat |
| 方針転換の判断（API→スクレイピング） | Claude Chat（+ 人間） |
| 堅牢化・例外処理の整備 | Claude Code |
| 日本語コメント・docstring追加 | Claude Code |
| 機能追加（仕様が明確なもの） | Claude Code |

「2003年の論文が返ってくる」という症状から原因を切り分ける作業は、対話で試行錯誤するしかありませんでした。一方、動くコードができてからの仕上げはClaude Codeに仕様を明確に渡せば差分形式で綺麗に上げてきます。

実感として、**AIがコードを書く速度が上がるほど、人間側の「なぜ動かないかを理解する力」の重要性が上がります**。実装は任せられても、設計と検証は手放せません。

## プレプリントとの付き合い方

arXivは査読なしで投稿できるため玉石混交です。取得した論文を頭から信じるのではなく「釣り堀」として使うのが現実的だと思っています。

1. サマリPDFを流し読みして気になるタイトルを拾う
2. 著者グループを確認する
3. 面白そうなら全文を読む
4. 査読済み版がジャーナルに載ったら本腰を入れる

なお、arXivは2026年3月にコーネル大学からの独立を発表しました。AI関連論文の急増で投稿数が2022年比50%増、運営は赤字とのこと。プレプリントの洪水はこれからさらに加速します。自分の興味に合わせた自動サーベイツールを一本持っておくのは、その備えとして悪くないはずです。

## まとめ

* arXiv APIの `sortBy=submittedDate` は壊れている（2026年3月時点）
* 検索ページのスクレイピング + `order=-announced_date_first` が確実
* WindowsのPDF生成は `pdfkit` + `wkhtmltopdf` が楽
* AI開発の分業：試行錯誤はチャット、仕上げはClaude Code

コードは全部リポジトリにあります。`topics.txt` を書き換えて、あなたの分野でも使ってみてください。

## リポジトリ：arxiv-paper-fetcher

<https://github.com/fox-research-lab/arxiv-paper-fetcher>
