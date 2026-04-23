---
id: "2026-03-31-electronアプリの中にchrome組み込んでmcpサーバーにしたらclaude-codeが自分-01"
title: "Electronアプリの中にChrome組み込んでMCPサーバーにしたら、Claude Codeが自分でブラウザ操作できるようになった"
url: "https://qiita.com/patapim/items/d36a759b4d4a2fe766dc"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "qiita"]
date_published: "2026-03-31"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

タイトルの通りなんだけど、もう少し詳しく書く。

自分が作ってるターミナルIDE（[PATAPIM](https://patapim.ai)）に、Chromeブラウザを丸ごと組み込んで、それをMCPサーバーとして公開した。Claude CodeがこのMCPツールを使って、Webページを開いたり、要素をクリックしたり、フォームに入力したり、スクリーンショットを撮ったりできる。

これがどういうことかというと、Claude Codeに「このWebアプリのログインフォームをテストして」って頼むと、本当にブラウザを操作してテストしてくれる。ヘッドレスじゃなくて、画面にブラウザが見えてて、リアルタイムでClaude Codeが操作してるのが分かる。

## なぜ作ったか

Claude CodeのMCPには`mcp__puppeteer`とか外部のブラウザ操作ツールがあるけど、いくつか不満があった。

ヘッドレスだと何やってるか見えない。「あれ、今なにしてんの？」ってなる。別ウィンドウで立ち上がると、ターミナルとブラウザを行き来するのがめんどい。あとPlaywrightとかPuppeteerだと、セットアップがそこそこ大変。node\_modulesにChromiumのバイナリ落としてきたりとか。

「ターミナルの隣にブラウザが常に見えてて、Claude Codeがそのまま使えたら最高じゃない？」って思った。

## 構成

```
┌─────────────────────────────────────────────┐
│ PATAPIM (Electron)                          │
│                                             │
│  ┌──────────────┐  ┌────────────────────┐   │
│  │ Terminal     │  │ BrowserView        │   │
│  │ (xterm.js)  │  │ (Chrome)           │   │
│  │             │  │                    │   │
│  │ Claude Code │  │  ← MCP経由で操作   │   │
│  │  ↓ MCP呼出  │  │                    │   │
│  └──────┬───────┘  └────────┬───────────┘   │
│         │                   │               │
│         │    stdio JSON-RPC │               │
│         │         ↓         │               │
│  ┌──────┴───────────────────┴───────────┐   │
│  │ patapim-browser-server.js            │   │
│  │ (MCP Server - subprocess)            │   │
│  │                                      │   │
│  │  HTTP bridge → BrowserView制御       │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

やってることはシンプルで、3つのレイヤーがある。

1. **patapim-browser-server.js** — MCPサーバー。Claude Codeからstdio JSON-RPCで呼ばれる。`browser_navigate`, `browser_click`, `browser_screenshot`みたいなツールを提供する
2. **HTTP bridge** — MCPサーバーからElectronのメインプロセスへHTTPリクエストを投げる。localhost:31415で待ち受けてる
3. **BrowserView** — Electronの`BrowserView` API。本物のChromiumインスタンス。メインプロセスがCDP（Chrome DevTools Protocol）経由でページを操作する

なんでHTTPブリッジが必要かというと、MCPサーバーはsubprocessとして走るから、Electronのメインプロセスに直接アクセスできない。プロセス間通信の手段としてHTTPを使ってる。もっとエレガントなやり方あるかもしれないけど、動いてる。

## MCPツール一覧

Claude Codeから使えるツールはこんな感じ：

| ツール | やること |
| --- | --- |
| `browser_navigate` | URLに遷移 |
| `browser_click` | CSSセレクタかテキストで要素クリック |
| `browser_fill` | inputやtextareaに入力（React対応） |
| `browser_type` | 1文字ずつキー入力（contenteditable用） |
| `browser_content` | ページのHTML or テキスト取得 |
| `browser_screenshot` | スクリーンショット撮影 |
| `browser_evaluate` | 任意のJavaScript実行 |
| `browser_scroll` | スクロール |
| `browser_press_key` | キー送信（Enter, Tab等） |

`browser_click`は地味に工夫してて、CSSセレクタだけじゃなくてテキストマッチでも要素を見つけられる。Claude Codeは「ログインボタンをクリック」みたいに指示するから、テキストで探せるほうが相性がいい。セレクタ指定もできるけど、Claude Codeにセレクタ調べさせるより「ログインというテキストのボタンを押して」のほうが自然。

## ハマったところ

### BrowserViewのセキュリティサンドボックス

ElectronのBrowserViewって、`webPreferences`のセキュリティ設定がかなり厳しい。`nodeIntegration: false`にしないとセキュリティ警告が出るし、`contextIsolation: true`にすると直接DOMにアクセスできない。

結局、ページ操作は全部CDP（Chrome DevTools Protocol）経由にした。`webContents.debugger.attach()`してCDPのコマンドを叩く。`Runtime.evaluate`でJS実行、`Input.dispatchMouseEvent`でクリック、`Page.captureScreenshot`でスクショ。

これはこれで罠があって、CDPのマウスイベントって座標指定なんだけど、要素の座標を取得するのにまずJSを実行して`getBoundingClientRect()`して、その結果をCDPに渡す、みたいな二段構えになる。

### contenteditable地獄

Facebookとか、Slackとか、最近のWebアプリはinputじゃなくてcontenteditable divを使ってる。`browser_fill`でnative value setterを使っても効かない。

対策として、contenteditable要素に対しては`document.execCommand('insertText')`を使うようにした。これでReact/Draft.js/Lexical系のエディタでもだいたい動く。Facebookは特殊で、Lexicalエディタのインスタンスに直接`setEditorState`する必要があったけど、そこまでやるかどうかはケースバイケース。

### CORSとCSP

外部サイトでJSを実行しようとすると、CSP（Content Security Policy）でブロックされることがある。その場合はCDPの`Runtime.evaluate`を使えばCSPを無視できる（DevToolsのコンテキストで実行されるから）。これに気づくまで半日かかった。

## 実際の使い方

自分が日常的にやってるのはこのあたり：

**Webアプリのテスト。** 自分のアプリのログイン→ダッシュボード→設定変更→ログアウト、みたいなフローをClaude Codeに操作させる。手動テストの代わり。E2Eテスト書くほどでもない、でも毎回手で確認するのはだるい、みたいなやつ。

**ドキュメント調査。** コーディング中に「この APIのレート制限いくつだっけ」ってなった時、Claude Codeが勝手にドキュメントサイト開いて調べてくれる。自分のブラウザのタブが増えない。

**デバッグ。** エラーメッセージをそのままClaude Codeに渡して、「このエラーについて調べて」って言うと、ブラウザでStack Overflowとか見てくれる。まあ、Claude Code自体の知識で解決することのほうが多いけど。

一回面白かったのは、Claudeに「近所のスーパーを探して」って頼んだらGoogleマップを開いて検索結果をまとめてきたこと。開発と全然関係ない。でも「ブラウザ操作ができる」っていうのはこういうことなんだなって思った。

## ソースコードの話

PATAPIMはクローズドソースなんだけど、MCPブラウザサーバー部分は将来的に切り出してOSSにするか検討中。需要あるのかな。あったら教えてほしい。

MCPサーバーの作り方自体に興味ある人は、Anthropicの[MCP仕様](https://modelcontextprotocol.io/)が一次ソース。stdioトランスポートで動くサーバーなら、Node.jsで100行くらいで最低限のやつは作れる。

## 最後に

ブラウザ操作系のMCPは可能性がでかいと思う。今はWebアプリのテストとドキュメント調査くらいにしか使ってないけど、スクレイピング、フォーム自動入力、CI/CDの管理画面操作とか、いろいろ応用が考えられる。

ただ、セキュリティには気をつけないとヤバい。Claude Codeにブラウザ操作させるってことは、自分のログインセッション丸見え状態でAIに操作させてるってこと。信頼できる環境でだけ使ったほうがいい。

質問あったらコメントで。
