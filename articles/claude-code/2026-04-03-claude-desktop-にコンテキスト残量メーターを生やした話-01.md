---
id: "2026-04-03-claude-desktop-にコンテキスト残量メーターを生やした話-01"
title: "Claude Desktop にコンテキスト残量メーターを生やした話"
url: "https://zenn.dev/saqoosha/articles/ccdex-claude-desktop-context-indicator"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-03"
date_collected: "2026-04-04"
summary_by: "auto-rss"
---

# なにを作ったか

Claude Desktop の Code タブのフッターバーに、リアルタイムのコンテキスト使用量とレートリミット状況を表示するインジケーターを注入する拡張 **CCDEX** (Claude Code Desktop Context Extension) を作った。

![CCDEX screenshot](https://static.zenn.studio/user-upload/deployed-images/5da9e823c9307bf2b93098b0.png?sha=7aa3bd1330d349664a69f7f913ffb9ebaf022256)

<https://github.com/Saqoosha/CCDEX?tab=>

表示されるのは 3 つ：

* **コンテキスト使用量** — プログレスバー + トークン数（`46.7k / 200.0k` とか `171.2k / 1.0M` とか）
* **5 時間レートリミット** — 使用率 + リセットまでのカウントダウン（`5h 4% 4h30m`）
* **週間レートリミット** — 同上（`Wk 6% 6d`）

色分けは 50% 未満で緑、50〜80% で黄色、80% 超で赤。

# 動機

基本的には Claude Code CLI がメインツールなこの頃。でもターミナルで使いたくないんですよ。[専用ターミナルまで作ってみても](https://zenn.dev/saqoosha/articles/sessylph-libghostty-claude-code-terminal)やっぱりターミナルはターミナルなんで TUI なので好きくない。

で、[Visual Studio 用の Claude Code Extension を WebView で動かすやつ](https://github.com/Saqoosha/Canopy)を作ってみたりしたものの（また今度別記事書く）、それなら Claude Desktop でいいんちゃう？と思いましたが、ただ一つ、致命的に足りないものがありまして。**コンテキスト残量がわからない**。

CLI ならステータスバーをカスタマイズすればすんなり出せるんだが Desktop にはそういう仕組みがない。`/context` で一応出るんだがすげえ長大な情報が出てくるし何よりコマンド打つのがダルい。

常時表示されるメーターがあれば「そろそろ新しいセッション始めるか」とか「リミット近いから少し待つか」みたいな判断がサクッとできるよね、ってことで作った。

# しくみ

## Claude Desktop = Electron アプリ

Claude Desktop は Electron アプリなので解析しやすい。ということで Claude Code に頑張って色々調べてもらったところ、Code タブは `https://claude.ai/claude-code-desktop/...` を Electron の WebContentsView でレンダリングしている。つまり中身はウェブページ。

ということはあとは適当に JavaScript を注入できれば何とでもなりそうってことで、開発進めてもらったけどこれが一筋縄ではいかなかった。Claude Desktop は Electron の [Fuse](https://www.electronjs.org/docs/latest/tutorial/fuses) でセキュリティがガチガチに固められていて、`--inspect`、`NODE_OPTIONS`、ASAR リパックなど一般的な手法は全滅（6 回失敗した）。最終的には `EnableEmbeddedAsarIntegrityValidation` Fuse をバイナリレベルで無効化した上で、`app.asar` 内の preload スクリプト（`mainView.js`）末尾にスクリプトを直接バイナリパッチで追記する、という力技で解決した。[試行錯誤の全記録はこちら。](https://github.com/Saqoosha/CCDEX/blob/main/RESEARCH.md)

## データの取得方法

### コンテキスト使用量（Electron IPC から）

Claude Code がアシスタントの応答を受け取るたびに、内部的に IPC イベントが発火する。このイベントには `usage` オブジェクトが含まれていて、`input_tokens`、`output_tokens`、`cache_creation_input_tokens`、`cache_read_input_tokens` がわかる。これを拾い上げてセッションごとに集計している。

モデルのコンテキストウィンドウサイズ（200k とか 1M とか）も IPC 経由で取得できる。ターンが完了すると `result` イベントに `modelUsage.contextWindow` が入ってくるので、ハードコーディングは不要。モデルが変わっても自動で追従する。

### 5 時間制限、週間制限

5 時間制限、週間制限は [Settings -> Usage ページ](https://claude.ai/settings/usage)で使われてる API をそのまま叩いている。  
ここがちょっと面白いところで、Code タブが `https://claude.ai` から読み込まれているおかげで、`fetch('/api/...')` がそのまま **same-origin リクエスト** になる。ブラウザが自動的にセッション Cookie を付けてくれるので、認証の設定は一切不要。

```
GET /api/organizations/{orgId}/usage
```

このエンドポイントを叩くと 5 時間窓と 7 日窓それぞれの使用率（0〜100）とリセット時刻が返ってくる。org ID は `lastActiveOrg` Cookie から抽出。

# インストール方法

Claude Code に [README.md](https://github.com/Saqoosha/CCDEX) 読ませてやってーっていうのが早い。  
途中 `sudo` 必要だからターミナルで自分でやってーって言われるかも。

# おまけ機能：サイドバーナビゲーション

インジケーターのついでにキーボードショートカットも追加した：

* `Ctrl+1` 〜 `Ctrl+9` — サイドバーのセッションに番号でジャンプ
* `Cmd+Opt+↓` / `Cmd+Opt+↑` — 次/前のセッションに移動

地味に便利。

# セキュリティについて

正直に書いておくと、Electron アプリの ASAR 整合性チェックを無効化するということは、他の悪意を持ったソフトウェアが `app.asar` を改ざんしても検出できなくなるということ。信頼できるマシンでのみ使うこと。

# 最後に

そのうち Claude Code に標準でつくと思う。っていうかつけてくれ。なんでついてないんだ。

<https://github.com/Saqoosha/CCDEX?tab=>
