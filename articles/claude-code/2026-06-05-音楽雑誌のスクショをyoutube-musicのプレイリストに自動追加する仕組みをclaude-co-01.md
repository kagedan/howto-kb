---
id: "2026-06-05-音楽雑誌のスクショをyoutube-musicのプレイリストに自動追加する仕組みをclaude-co-01"
title: "音楽雑誌のスクショをYouTube Musicのプレイリストに自動追加する仕組みをClaude Codeで作った"
url: "https://zenn.dev/obataka123/articles/b30ff8261eb927"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "Python", "zenn"]
date_published: "2026-06-05"
date_collected: "2026-06-06"
summary_by: "auto-rss"
query: ""
---

音楽雑誌を読んでいると、気になるアルバムがどんどん出てくる。

雑誌のレビューページには、アーティストの紹介とともに代表作や新作が並んでいる。本当はすべて聴きたいところだが、CDを買ったりサブスクで追いかけたりすると、お金も時間もかかる。ただ最近はYouTubeに公式でアップされている音源も多い。「全部は無理でも、YouTubeにあるものだけでも聴いて音楽の勉強をしたい」というのが動機だった。

問題は、気になったアルバムを逐一YouTube Musicで検索してプレイリストに追加する作業が地味にめんどくさいこと。雑誌1冊でアルバムが10〜20枚出てくることもざらで、手作業でやっていると時間がかかりすぎる。

そこでスクショを1枚撮るだけで、あとは全部自動でYouTube Musicのプレイリストに追加してくれる仕組みをClaude Codeで作った。

## 作ったもの

雑誌のレビューページをスクショしてフォルダに入れると、以下の流れで自動的にプレイリストへ追加される。

```
スクショ (input/ に置く)
    ↓
Claude API（vision）でアーティスト名・アルバム名を抽出
    → output/playlist.csv に保存
    ↓
ytmusicapi でYouTube Musicを操作
    → アルバムを検索 → トラックをプレイリストに追加
    ↓
input/ を自動クリーンアップ
```

使い方はこれだけ。

```
python3 scripts/run.py "プレイリスト名"
```

## 使用技術

* **Claude API（claude-haiku-4-5）**：雑誌スクショからアーティスト・アルバム名を抽出
* **ytmusicapi**：YouTube Musicをプログラムから操作するPythonライブラリ
* **Python**：スクリプト本体

## 仕組みの解説

### ステップ1：Claude APIで画像からアルバム情報を抽出

`extract.py` が担当する部分。`input/` フォルダの画像をBase64エンコードしてClaude APIに送り、アーティスト名とアルバム名のペアを抽出させる。

プロンプトはシンプルにこう指示している。

```
この画像は音楽雑誌のレビューページです。
ページに掲載されているアーティスト名とアルバム名のペアをすべて抽出してください。

以下の形式で1行に1組ずつ出力してください（ヘッダー行は不要）：
アーティスト名,アルバム名
```

日本語・英語どちらの表記でも誌面に書かれているままの表記を使わせることで、精度が安定した。レビュー文や評点といった不要な情報が混入しないよう、明示的に除外指示も入れている。

抽出結果は `output/playlist.csv` に保存される。

```
artist,album
Radiohead,OK Computer
Portishead,Dummy
```

### ステップ2：ytmusicapiでYouTube Musicに追加

`create_playlist.py` が担当する部分。CSVを読み込み、アルバムをYouTube Musicで検索してプレイリストに追加する。

```
results = yt.search(f"{artist} {album}", filter="albums", limit=3)
browse_id = results[0].get("browseId")
album_info = yt.get_album(browse_id)
video_ids = [t["videoId"] for t in album_info["tracks"] if t.get("videoId")]
yt.add_playlist_items(playlist_id, video_ids)
```

アルバム単位で検索してトラックIDをまとめて取得し、一括でプレイリストに追加している。

## ハマったポイント

### 1. browser.jsonの取得方法

ytmusicapiはYouTube Music用の非公式Pythonライブラリで、Googleの公式APIキーは不要。代わりに、ブラウザのCookieを使って認証する。

認証ファイル（`browser.json`）の取得手順は以下の通り。

1. ブラウザでYouTube Musicを開き、ログインする
2. 開発者ツールを開く（F12）
3. 「ネットワーク」タブを開いた状態で、YouTube Music上で何か操作する（プレイリストを開くなど）
4. リクエスト一覧から `browse` などのリクエストを選択
5. リクエストヘッダーをコピー
6. ターミナルで以下を実行：

プロンプトが表示されるので、コピーしたヘッダーを貼り付けてEnterを2回押す。`browser.json` が生成される。

このファイルにはCookieが含まれているため、`.gitignore` に追加して絶対にコミットしないこと。

### 2. YouTube検索に存在しないアルバムを許容する設計

CSVにアルバム名があっても、YouTube Musicの検索結果にヒットしないことがある。マイナーなアーティストや、日本未配信のアルバムなどが該当する。

最初はエラーで止める実装を考えたが、それだと1件見つからないだけで全体が止まってしまう。そこで「見つからなければスキップして続行」という設計にした。

```
if not results:
    print(f"    アルバムが見つかりません: {artist} - {album}", file=sys.stderr)
    return []  # 空リストを返してスキップ
```

完了時には「何件中何件追加できたか」を表示して、スキップされたアルバムは標準エラー出力に出るようにした。

```
完了!
  アルバム数: 8 / 10
  追加トラック数: 94
  URL: https://music.youtube.com/playlist?list=xxxx
```

見つからなかった2件は手動で確認するという運用にすることで、自動化の恩恵を最大化しつつ、見落としも防げる。

## Claude Codeのスラッシュコマンドとして整備した

スクリプトを直接叩くだけでも動くが、「スクショからやりたい」「CSVだけ先に確認したい」「自分で書いたCSVを使いたい」など、状況によって使い分けたいケースがある。

そこで3つのスラッシュコマンドとして `.claude/commands/` に整備した。Claude Codeのプロジェクトディレクトリで `/` を入力すると候補として表示されるので、コマンド名を覚えていなくても使える。

### `/add-playlist-from-input [プレイリスト名]`

スクショからプレイリスト追加まで一気通貫で実行するコマンド。一番よく使うフルパイプライン。

```
input/ のスクショ → Claude API で抽出 → YouTube Music に追加
```

プレイリスト名を省略するとデフォルト名が使われる。

### `/create-playlist-csv`

スクショから `output/playlist.csv` を生成するだけのコマンド。プレイリストには追加しない。

```
input/ のスクショ → Claude API で抽出 → output/playlist.csv に保存
```

「まず何が抽出されるか確認してから追加したい」という場合に使う。抽出結果を見て不要なアルバムを手動で削除してから、次のコマンドでプレイリストに追加する、という使い方ができる。

### `/add-playlist-from-csv [プレイリスト名]`

既存の `output/playlist.csv` をYouTube Musicに追加するコマンド。

```
output/playlist.csv → YouTube Music に追加
```

自分でCSVを手書きしてプレイリストを作りたいときにも使える。フォーマットは `artist,album` の2列だけなので、Excelやメモ帳で簡単に作れる。

---

この3つの使い分けをまとめると以下のようになる。

| やりたいこと | 使うコマンド |
| --- | --- |
| スクショ → プレイリスト（一発完結） | `/add-playlist-from-input` |
| スクショ → CSVだけ作る（内容確認） | `/create-playlist-csv` |
| 手書きCSV → プレイリスト | `/add-playlist-from-csv` |
| CSV確認後 → プレイリスト追加 | `/add-playlist-from-csv` |

## コード全体の構成

```
spotify-playlist-automation/
├── input/              # スクショを置く（処理後に自動削除）
├── output/
│   └── playlist.csv   # 抽出結果
├── browser.json        # YouTube Music認証ファイル（gitignore）
└── scripts/
    ├── extract.py      # Claude APIで画像→CSV
    ├── create_playlist.py  # CSV→YouTube Musicプレイリスト
    └── run.py          # 上記2つのオーケストレーター
```

## 使い方まとめ

**初回セットアップ**

```
pip install anthropic ytmusicapi
ytmusicapi browser  # browser.jsonを生成
```

事前にYouTube Musicで追加先のプレイリストを作成しておく。

**毎回の使い方**

```
# input/ にスクショを置く
python3 scripts/run.py "From Guitar Magazine"
```

**オプション**

```
# 画像抽出だけ（CSVを確認したい場合）
python3 scripts/run.py --extract-only

# CSV→プレイリスト追加だけ（CSVが既にある場合）
python3 scripts/run.py --playlist-only "プレイリスト名"
```

## まとめ

Claude APIのビジョン機能でOCR代わりにアルバム情報を抽出し、ytmusicapiでYouTube Musicを操作することで、雑誌のスクショ → プレイリスト追加を完全自動化できた。

工夫したのは「見つからなくても止まらない」設計で、これのおかげで実用的なツールになった。精度も問題なく、スクショを撮ってコマンド1つ叩くだけで処理が完了する。

音楽雑誌を読む習慣がある人にはそのまま使えるし、Claude APIのビジョン機能の活用例としても参考になると思う。

---

**関連記事**
