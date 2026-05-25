---
id: "2026-05-24-claude-desktop-cursor-からボーカル抽出カラオケ生成まで叩くstemsplit-01"
title: "Claude Desktop / Cursor からボーカル抽出・カラオケ生成まで叩く：StemSplit 公式 MCP サーバー stemsplit-mcp の使い方【2026年版】"
url: "https://qiita.com/stemsplit/items/b9d0fbc9fee4b7b3a756"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "prompt-engineering", "API", "LLM", "qiita"]
date_published: "2026-05-24"
date_collected: "2026-05-25"
summary_by: "auto-rss"
query: ""
---

歌ってみたミックス前のオフボーカル作り、VTuber 歌枠のセトリ準備、耳コピ用の6ステム分離——「ファイルを投げて、ボーカルとオフボーカルのパスが返ってくれば十分」というケースは、AI アシスタントから直接実行できると一番速いです。

そういう用途のために、StemSplit 公式の **Model Context Protocol サーバー** [`stemsplit-mcp`](https://www.npmjs.com/package/stemsplit-mcp) を npm に公開しました。Claude Desktop、Cursor、Cline、Windsurf、Zed あたりに 1 ファイル設定を入れるだけで、**チャット欄からボーカル除去・カラオケ作成・4ステム / 6ステム分離が走ります**。本記事はその使い方とハマりどころをまとめたものです。

:::note info
本記事は MCP クライアント側（Claude Desktop / Cursor 等）の設定にフォーカスします。 StemSplit 全体の使い方や 2026 年版の MCP サービス紹介は [StemSplit MCP サーバーの公式記事](https://stemsplit.io/ja/blog/stemsplit-mcp-server-claude-cursor) をご覧ください。
:::

---

## この記事でわかること

- ✅ `stemsplit-mcp` を Claude Desktop / Cursor に組み込む手順
- ✅ `STEMSPLIT_API_KEY` の設定方法（`sk_live_...`）
- ✅ チャット欄から実行できる 8 つの MCP ツールの中身（`separate_stems` / `separate_youtube` / `get_balance` ほか）
- ✅ ローカルファイル・YouTube URL 双方の扱い方の違い
- ✅ 「相対パスを投げて固まる」あるあるの回避策
- ✅ 自動リトライ・指数バックオフが内部で何をしているか

---

## 想定するユースケース

stemsplit-mcp を入れて一番おいしいのは、**「ファイルパスや YouTube URL を AI に伝えて、ステムだけ返してもらいたい」場面**です。

| シーン | 入力 | 欲しい出力 | 推奨ツール |
|---|---|---|---|
| 歌ってみた用オフボーカル生成 | 原曲の MP3/WAV | `instrumental.mp3` | `separate_stems` / `BOTH` |
| VTuber 歌枠のセトリ準備 | 原曲 URL のリスト | `instrumental.mp3` × N | `separate_stems` を順に依頼 |
| ミックス師向けの素材分離 | クライアントから届いた WAV | vocals / drums / bass / other | `separate_stems` / `FOUR_STEMS` |
| 耳コピ・楽曲解析 | 原曲ファイル | 6 ステム全部 | `separate_stems` / `SIX_STEMS` + `quality=BEST` |
| YouTube 動画から acapella | 公開動画の URL | `vocals.mp3` | `separate_youtube` |
| 残り分のチェック | — | 残クレジット（分） | `get_balance` |

普通の curl + ポーリングと違って、**MCP サーバー側がアップロード / ポーリング / ダウンロード / リトライを全部隠してくれる** のがポイントです。LLM 側は「ファイルパスをツールに渡すだけ」で済みます。

---

## 前提

| 項目 | 内容 |
|---|---|
| Node.js | 20 以上（`node --version` で確認） |
| アカウント | StemSplit の API キー（[stemsplit.io/app/settings/api](https://stemsplit.io/app/settings/api) で発行、`sk_live_...` 形式） |
| クライアント | Claude Desktop / Cursor / Cline / Windsurf / Zed のいずれか |

`stemsplit-mcp` 本体は npm から `npx -y` 経由で自動取得されるので、手動で `npm install` する必要はありません。グローバルに入れたい人だけ `npm install -g stemsplit-mcp` で OK です。

---

## 1. API キーを発行する

1. [StemSplit のダッシュボード](https://stemsplit.io/app/settings/api)にログイン
2. 「API Keys」セクションを開き「Create New Key」
3. キー名を `mcp-client` などにしてコピー（`sk_live_...` 形式）

このキーは MCP サーバー起動時に `STEMSPLIT_API_KEY` 環境変数として渡します。チャットの中に貼らないでください。MCP の `env` ブロックに入れるのが正解です。

---

## 2. Claude Desktop に設定する

macOS の場合、`~/Library/Application Support/Claude/claude_desktop_config.json` を編集します（Windows は `%APPDATA%\Claude\claude_desktop_config.json`）。

```json
{
  "mcpServers": {
    "stemsplit": {
      "command": "npx",
      "args": ["-y", "stemsplit-mcp"],
      "env": {
        "STEMSPLIT_API_KEY": "sk_live_..."
      }
    }
  }
}
```

ファイル保存後 Claude Desktop を再起動すると、ウィンドウ下部に「stemsplit」とアイコンが出てきます。緑のドットが点いていれば稼働中です。

---

## 3. Cursor に設定する

`~/.cursor/mcp.json` に同じ形で書きます（Settings → MCP からでも可）。

```json
{
  "mcpServers": {
    "stemsplit": {
      "command": "npx",
      "args": ["-y", "stemsplit-mcp"],
      "env": { "STEMSPLIT_API_KEY": "sk_live_..." }
    }
  }
}
```

Cursor を再起動するか、設定画面で MCP セクションを再読み込みすれば認識されます。Cline / Windsurf / Zed もほぼ同じ構造（`command` / `args` / `env`）です。詳しくは [公式ガイド](https://stemsplit.io/ja/developers/guides/mcp) を参照してください。

---

## 4. 動作確認：チャットから叩く

設定が済んだら、AI アシスタントにこう投げます。

```text
/Users/me/Music/track.mp3 を boy ステム分離して、ボーカルとオフボーカルを返して。
```

LLM が `separate_stems` ツールを `outputType=BOTH`、`quality=BALANCED` あたりで呼び、サーバー側がアップロード → ポーリング → ダウンロードまで進めてから、`~/Downloads/stemsplit/<job-id>/` にローカルパスを返してきます。

YouTube から直接やる場合はこんな感じ。

```text
https://youtu.be/dQw4w9WgXcQ のオフボーカルが欲しい。
```

`separate_youtube` が呼ばれ、サーバー側で動画を取得して分離を回します。**ローカルに `yt-dlp` を入れる必要はありません**。レート制限を心配する役は StemSplit 側が引き受けます。

残クレジットを確認したいときは：

```text
StemSplit のクレジット、あと何分残ってる？
```

`get_balance` が叩かれて秒数 / 分数で返ります。長尺ジョブの前に確認するのに便利です。

---

## ツール一覧

`stemsplit-mcp` が公開しているツールは現在 8 つです。

| ツール | 用途 |
|---|---|
| `separate_stems` | ローカルファイル or 直リンクの音声 URL を分離。`BOTH` / `VOCALS_ONLY` / `INSTRUMENTAL_ONLY` / `FOUR_STEMS` / `SIX_STEMS` |
| `separate_youtube` | YouTube URL を渡して `vocals` + `instrumental` を取得 |
| `get_job` / `list_jobs` | 通常ジョブの状態と履歴 |
| `get_youtube_job` / `list_youtube_jobs` | YouTube ジョブの状態と履歴 |
| `get_balance` | 残クレジットを秒・分で取得 |
| `download_stems` | 完了済みジョブの presigned URL を取り直してローカル保存 |

加えて 4 つの resource（残高 / 直近のジョブ / ジョブ詳細 / YouTube ジョブ詳細）と 4 つの prompt（カラオケメーカー / ボーカル分離 / 6ステムサンプラー / YouTube オフボーカル）が定義されています。詳しい仕様は [GitHub の README](https://github.com/StemSplit/stemsplit-mcp#readme) を見てください。

---

## ハマりどころ：相対パスは弾かれる

これは MCP サーバーを真面目に作る上で重要な話なので、最初に押さえておく価値があります。

`./song.mp3` のような **相対パスは即拒否します**。理由は、MCP サーバーの CWD が AI クライアント側からは見えないからです。Claude Desktop や Cursor から起動すると、サーバープロセスは多くの場合システムルート（`/` など）から立ち上がります。そこに対する相対パスを解釈しても、ユーザーの意図とはまずずれます。

そのため `stemsplit-mcp` は次のような明確なエラーを返します。

```
Relative paths are not supported (got "./song.mp3").
Pass an absolute path like "/Users/you/Music/song.mp3" or a home-anchored path like "~/Music/song.mp3".
If you do not know the absolute path, ask the user for it before retrying.
```

このメッセージのおかげで LLM は「絶対パスを聞き直す」「`~` で代用する」といった次のアクションを取りやすくなります。ローカルファイルを渡したい場合は **絶対パスまたは `~/...` の形** で渡すのが鉄則です。

---

## 中で何をしているか

シンプルに見えますが、地味に効く処理がいくつか入っています。

### 自動リトライ（指数バックオフ + ジッター）

- `GET /jobs/:id` のような **読み取り系**：最大 4 回までリトライ。`Retry-After` も尊重します。
- `POST /jobs` のような **書き込み系**：保守的に最大 3 回、ただし「サーバーが request を見ていないことが分かる」ネットワークエラーのみ。二重課金は起きません。
- R2 へのアップロード：最大 3 回。`ReadableStream` は巻き戻せないので、毎回ファイルを開き直して新しいストリームを作ります。
- R2 からのダウンロード：5xx はリトライ、403 はリトライしない。403 は presigned URL が失効した合図なので、`get_job` で新しい URL を取り直す方が正しいからです。

リトライは stderr にログを出します。Claude Desktop のログを `tail` していると流れているのが見えるはず。

### 進捗ノーティフィケーション

ポーリング進捗は MCP の `notifications/progress` として AI クライアントに転送されるので、長尺の YouTube ジョブは Claude Desktop の進捗 UI に「10% → 35% → 70% → 100%」と表示されます。固まっているように見えない、というのは UX 上わりと重要です。

### 構造化エラー

`INSUFFICIENT_CREDITS` / `RATE_LIMIT_EXCEEDED` / `FILE_TOO_LARGE` / `UNSUPPORTED_FORMAT` 等の `code` を返すので、LLM は英語の自然文をパースする必要がありません。

---

## 既存の選択肢との位置づけ

StemSplit を呼ぶ方法は今こうなっています。

| 方法 | こんなときに |
|---|---|
| **`stemsplit-mcp`**（本記事） | Claude / Cursor 等のチャットから個別に呼びたい |
| **`n8n-nodes-stemsplit`** | n8n でバッチ・スケジュール・Webhook 起点で回したい |
| **生の REST API** | 自社サーバーや GitHub Actions から server-to-server で叩きたい |
| **`demucs-onnx`**（PyPI） | アプリに 316 MB の ONNX モデルを同梱してオフラインで分離したい |

ユーザーが人間で、AI アシスタント越しの操作なら MCP サーバーが圧倒的に楽。ユーザーがソフトウェアなら API か n8n ノードのほうが向きます。実運用では「MCP サーバー（試行錯誤）＋ n8n ノードか API（量産）」の併用がおすすめです。

---

## まとめ

- `stemsplit-mcp` は [npm に MIT ライセンスで公開](https://www.npmjs.com/package/stemsplit-mcp)
- Node.js 20+ と StemSplit の API キーがあれば 2 分でセットアップ完了
- Claude Desktop / Cursor / Cline / Windsurf / Zed のチャットから、ボーカル除去・カラオケ生成・4 / 6 ステム分離・YouTube 分離まで自然言語で叩ける
- リトライ・進捗通知・構造化エラー・絶対パス検証など、地味に必要な機能は最初から入っている

公式 npm パッケージ → [npmjs.com/package/stemsplit-mcp](https://www.npmjs.com/package/stemsplit-mcp)
GitHub → [github.com/StemSplit/stemsplit-mcp](https://github.com/StemSplit/stemsplit-mcp)
日本語の解説記事 → [StemSplit MCP サーバー紹介ブログ](https://stemsplit.io/ja/blog/stemsplit-mcp-server-claude-cursor)

何か作ったら GitHub Discussions か X で見せてください。バグや改善案は Issue でも歓迎です。
