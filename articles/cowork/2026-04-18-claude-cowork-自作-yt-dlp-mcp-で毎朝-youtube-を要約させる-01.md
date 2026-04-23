---
id: "2026-04-18-claude-cowork-自作-yt-dlp-mcp-で毎朝-youtube-を要約させる-01"
title: "Claude Cowork × 自作 yt-dlp MCP で毎朝 YouTube を要約させる"
url: "https://zenn.dev/hanafsky/articles/claude-cowork-youtube-summarizer-mcp"
source: "zenn"
category: "cowork"
tags: ["MCP", "cowork", "zenn"]
date_published: "2026-04-18"
date_collected: "2026-04-19"
summary_by: "auto-rss"
query: ""
---

## はじめに

最近、YouTube で AI 関連の動画を追いかけているのですが、一日に流れてくる本数が多すぎて、自分で全部をチェックするのはなかなか難しいと感じるようになりました。かといって観るのをやめてしまうと、本当に参考になりそうなチュートリアルや発表を見落としてしまいそうで、どうにも落ち着かないのです。

そこで、次のような運用に落ち着きました。

* Claude Cowork の毎朝のスケジュールタスクで、おすすめ動画を 10 本ほど自動要約
* 各動画に ★1〜5 の「観るべき度」を添えて [Inkdrop](https://www.inkdrop.app/) に保存
* 通勤電車や筋トレの合間にスマホで Inkdrop を開き、★4 以上のものだけを実際に観る

この記事では、その仕組みをなるべく再現しやすい形で書き残しておきたいと思います。途中で自作の MCP サーバーを書く話が出てきますが、全体で 100 行ちょっとの Python で済む程度の、ごく小さなものです。

## 最初の試み: Claude in Chrome にブラウザを任せる

はじめのうちは、Chrome 拡張の [Claude in Chrome](https://www.anthropic.com/news/claude-for-chrome) にブラウザを操縦してもらい、YouTube のおすすめ欄から動画リストを拾ってきて、別タブで字幕ツールを開いて要約させる、という構成にしていました。

この方法でも一応は動いていたのですが、しばらく運用してみると、いくつか気になる点が出てきました。

* Chrome 拡張の再ログイン問題: ある朝 Inkdrop を開いたら要約が一本も増えていない、ということがときどきありました。Chrome 側で Claude がログアウト状態になっていて、手動で入り直さないとタスクが進まない、というのが原因のようです。通勤電車で気がついて少しがっかりします
* 長尺動画の扱い: 親切な判断として「長すぎる動画はスキップします」と勝手に切られることがあり、本当に参考になりそうなチュートリアル動画まで対象外になってしまうのが悩みどころでした
* 評価基準のズレ: 個人的に楽しみにしている「ムーザルのプログラミング絶望ラジオ」が、だいたい ★3 あたりに落ち着くことが多くて、チャンネルの文脈までは拾いきれていないのかもしれないと感じています

後ろの 2 つはプロンプトでの調整の余地がありそうですが、接続の不安定さは利用者側ではどうにもなりにくいので、これがいちばん気になっていました。

## 方針転換: yt-dlp を MCP サーバーでくるむ

Claude Cowork の実行環境は VM（サンドボックス）になっており、プロキシ越しに YouTube へアクセスしようとすると 403 で弾かれてしまうようです。そのため、Cowork の中から直接 `yt-dlp` を叩いても、動画情報は取ってこられません。

そこで、Mac 側で `yt-dlp` を動かす MCP サーバーを立てておき、Cowork からはそのサーバーを呼ぶだけ、という構成にしてみることにしました。絵にするとこのような形になります。

```
Cowork (VM, YouTube 到達不可)
    │  MCP (stdio)
    ▼
youtube_mcp/server.py   ← Mac 上で動く
    │  yt-dlp --cookies-from-browser chrome
    ▼
YouTube
```

MCP サーバーが公開しているツールは、次の 3 つです。

| ツール | 役割 | 主な引数 |
| --- | --- | --- |
| `list_recommendations` | フィードから動画一覧を取得 | `source` (`subscriptions` / `home` / `trending` / `search:<kw>` / URL), `limit`, `max_duration_sec`, `min_duration_sec` |
| `get_video_metadata` | タイトル・チャンネル・長さ・概要欄を取得 | `url` |
| `get_transcript` | 字幕を plain text で取得 | `url`, `languages` (default `["ja","en"]`), `prefer_manual` |

実装自体は `yt-dlp` を `subprocess` で叩くだけの、ごく単純なラッパーになっています。たとえば `get_video_metadata` の中身は、次のような形です。

```
proc = _run_yt_dlp(
    ["--dump-json", "--no-download", "--no-warnings", canonical],
    timeout=60,
)
```

`get_transcript` はもう少しだけ手を入れていて、手動字幕 → 自動字幕 → 英語字幕という優先順位で 2 段階に試し、SRT から plain text に畳み込んでから返すようにしています。

Chrome 自体は起動している必要がなく、`--cookies-from-browser chrome` で cookie ストアを読むだけで済むのも、個人的にはありがたいところでした。一度ログインしてあれば、以降 Chrome を立ち上げっぱなしにしなくてよいので、気兼ねなく使えます。

## セットアップの手順

### 1. 依存のインストール

```
cd ~/Documents/projects/youtube-summarizer
uv sync
```

`yt-dlp` と `mcp[cli]` は `pyproject.toml` に書いてあるので、これだけで必要なものが揃います。

### 2. Claude Desktop に MCP を登録

`~/Library/Application Support/Claude/claude_desktop_config.json` に、以下を追記します。

```
{
  "mcpServers": {
    "youtube-summarizer": {
      "command": "uv",
      "args": [
        "--directory", "/Users/hanafusakei/Documents/projects/youtube-summarizer",
        "run", "youtube-summarizer-mcp"
      ]
    }
  }
}
```

Claude Desktop を再起動すると、Cowork 側から `youtube-summarizer` のツール群が見えるようになります。

### 3. 動作確認

字幕まで取得できれば、ひとまずは動作確認としては十分かと思います。

```
uv run python -c "
from youtube_mcp.server import get_transcript
r = get_transcript('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
print(r['success'], r['language'], r['length'])
"
```

## Cowork のスケジュールタスクに組み込む

Cowork のスケジュールタスクは、作業フォルダ（このリポジトリ）と cron 式、それにプロンプトを渡すだけで登録できます。私の場合は `0 5 * * *`（毎朝 5 時）で回しています。

プロンプトの要点だけ抜き出すと、おおよそ次のような流れになります。

> 1. ワークスペースの `CLAUDE.md` を読む
> 2. `list_recommendations(source="subscriptions", limit=25)` で候補を取得
> 3. AI / LLM / プログラミング / 開発ツール / 技術チュートリアルに該当する動画だけ、最大 10 本残す
> 4. Inkdrop MCP の `search-notes` で video\_id が重複していないかをチェック
> 5. 各動画を 1 本ずつ順番に処理する（並列は禁止）
>    * `get_video_metadata` → `get_transcript` → 要約生成
>    * 429 エラーが返ったら、同じ URL に対して 1 回だけリトライする。それでもダメなら、概要欄ベースの要約にフォールバック
> 6. Inkdrop の `YouTube` ノートブックに保存

要約のフォーマットは `CLAUDE.md` にテンプレートとして書いてあるので、Cowork 側の Claude はそれに沿って書いてくれるだけです。結果としては、一行要約・200-400 字の要約・キーポイント 3〜7 個・技術トピック・★1-5 の閲覧価値、が並んだノートが出来上がります。

実際に生成されたノートは、次のような見た目になります。

![Inkdrop に保存された要約ノートの例](https://static.zenn.studio/user-upload/deployed-images/4d072eb3dedae45f4277b40f.png?sha=a375e33c650cd3cd3a7454030e9fbb38d740b866)

メタデータ表で動画の基本情報が一望でき、★2 の判定理由まで添えられています。通勤電車でこのノート一覧をスクロールしながら、どれをゆっくり観るかを仕分けする、というのが狙いです。

## 運用していて気になったポイント

### 429 Too Many Requests で止まることがある

最初の実装では、字幕取得を並列で走らせて高速化しよう、と考えていました。ただ、これは思っていたよりうまくいかなかったのです。YouTube 側が 429 エラーを返してきて、その日の残りの処理がそこで止まってしまう、ということが起きてしまいました。

対策としては、結局のところ「並列はやめて、1 本ずつ順に呼ぶ」という形に落ち着きました。MCP サーバー側でスロットルを入れるのではなく、プロンプト側でルールとして明示しておく形にしています。

> `get_transcript` は必ず 1 本ずつ順番に呼ぶ。複数 URL への同時並列呼び出しは禁止（429 の原因になるため）

失敗時のフォールバックも決めておきました。

> 429 エラーが返ったら、同じ URL に対して `get_transcript` を 1 回だけリトライする。リトライも 429 の場合は description を要約の材料にし、ノートに「※字幕なし - 概要欄ベース（レートリミット）」と明記する

これで少なくとも「その日の要約がゼロ本」という状況は避けやすくなったかなと思います。

### 評価基準のブレ

好きなチャンネルの評価が思ったより低めに出てしまう、という問題については、判定軸を言葉にして明示しておくことで、ある程度は落ち着いてきたように感じます。

> 判定軸: ユーザーが実際に真似する価値があるかどうか。ChatGPT / Claude / Local LLM の新機能やエージェント系ツールを使いこなすべきか、という目線で評価する

こうしておくと、コーディングの時事ネタを気楽に聞くタイプの動画も、情報量ベースで ★3〜★4 あたりに収まってくれることが増えました。完璧とは言えないのですが、自分で読んだときに違和感の少ない評価になってきたのではないかと思います。

### 長尺動画のスキップ

`list_recommendations` の `max_duration_sec` は 1 時間に設定してあり、それより長い動画は自動収集から外す形にしています。何時間もある分割チュートリアル（Code With Antonio さんの前後編 12 時間シリーズなど）は、自分で観ると決めたタイミングで改めて取得することにして、毎朝の自動収集の対象にはしていません。

## 運用してみてどうなったか

毎朝 5 時にタスクが走り、起きる頃には Inkdrop の `YouTube` ノートブックに 5〜10 本の要約が並んでいる、という状態になりました。通勤電車でスマホの Inkdrop を開き、★4 以上のものをピックアップして「これは今夜観る」「これはタイトルだけ把握しておけば十分」と仕分けていくのが、朝のちょっとした楽しみになっています。Chrome 拡張を使っていた頃と比べると、だいぶ安定して回ってくれているように感じます。

今となっては、Claude Cowork ではなく Claude Code + cron でも似たことができそうな気もするのですが、とりあえず現状の構成でしばらく問題なく動いているので、当面はこのまま使っていこうかなと思っています。

## おわりに

関連する Claude × 自作 MCP の別事例として、CAE 分野の FEM を解かせた実験も書いています。ご興味があれば併せてご覧ください。

同じような発想で、自分の趣味や仕事のまわりに「AI エージェントの手足」を少しずつ生やしていくと、日々がほんの少し楽になるのではないかと思っています。`yt-dlp` 自体は YouTube 以外のサイトにも幅広く対応しているようなので、ポッドキャストの書き起こしや要約などにも応用ができるかもしれません。
