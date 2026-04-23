---
id: "2026-03-17-aiがspaを読めない問題chrome-devtools-mcpで解決した-01"
title: "AIがSPAを読めない問題、Chrome DevTools MCPで解決した"
url: "https://zenn.dev/canaria_john/articles/91ad50759abbbb"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "GPT", "JavaScript", "zenn"]
date_published: "2026-03-17"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

## はじめに

AIに「このページの内容教えて」とURLを渡す場面は、最近かなり増えた。

Claude CodeやChatGPTを使っていると、調べたいドキュメントやダッシュボードのURLを渡して情報を取得してもらうことがよくある。

ところが、SPAで実装されているサイトだと、これがうまくいかない。

たとえば、Google Mapsのような動的なサイトにURLを渡しても、AIが返してくるのは「ページタイトルとJavaScriptのコードだけです」といった内容になる。

実際にブラウザで開けば地図もUIも見えているのに、AIには何も見えていない。

これが、SPA特有の問題だ。

この記事では、次のことを書く。

* なぜAIはSPAのコンテンツを取得できないのか
* Chrome DevTools MCPでどう解決するのか
* 実際にGoogle Mapsで試した結果
* どう使うか、どんな場面で効くか

---

## 何が起きるのか：SPAの本質

通常のWebページは、HTMLの中に本文が書かれている。

たとえば、技術ブログやドキュメントサイトの多くは、サーバーが最初から完全なHTMLを返してくれる。  
だから、AIがそのHTMLを取得すれば、記事の内容を読むことができる。

一方、SPA（Single Page Application）は、最初に返されるHTMLがほぼ空だ。

実際のコンテンツは、JavaScriptがブラウザ上で動的にレンダリングする。

つまり、AIがWebページを取得する方法は、だいたい次の2種類に分かれる。

| 取得方法 | 見えるもの | SPAでの挙動 |
| --- | --- | --- |
| HTMLをそのまま取得 | サーバーが返したHTMLの中身 | ほぼ空。`<div id="root"></div>` だけとか |
| ブラウザでレンダリング後に取得 | JavaScriptが描画した後の状態 | 実際に表示されている内容が見える |

多くのAIツールは、前者の「HTMLをそのまま取得」する方法を使っている。

だから、SPAだとコンテンツが取れない。

---

## 実例：Google Mapsで試してみる

実際にどうなるのか、Google Mapsで試してみた。

### WebFetchでの取得結果

まず、通常のWebページ取得方法で Google Maps（`https://www.google.com/maps`）を取得してみる。

Claude Codeには `WebFetch` というツールがあり、URLを渡すとHTMLを取得して内容を解析してくれる。

これでGoogle Mapsを取得すると、返ってくるのはこんな内容だった。

```
ページタイトル: Google マップ
bodyタグ内の初期要素は極めてシンプルです：
- ページタイトル
- スクリプトタグ: 大量のインライン JavaScript コード
- 設定オブジェクト: window.APP_OPTIONS という大規模な JSON 構造

実際のマップUIやコンテンツは、JavaScriptの実行後に挿入されます。
レンダリング前は、表示可能なコンテンツがほぼ存在しません。
```

つまり、AIが取得できたのは「タイトルとJavaScriptのコード」だけで、マップの内容や検索結果、UI要素などは何も見えていない。

次に、Chrome DevTools MCPを使ってみる。

Chrome DevTools MCPは、実際にブラウザを起動してページを開き、JavaScriptが実行された後の状態を見ることができる。

同じGoogle Mapsを、今度はブラウザで開いて取得すると、こうなる。

* 地図のUI全体が見える
* 検索ボックスやメニューの内容が取得できる
* 地図上に表示されている地名や施設名も読み取れる
* ページ内のボタンやリンクも認識できる

つまり、**人間がブラウザで見ている状態と同じものを、AIも見ることができる**。

これがSPA問題の解決策になる。

---

Chrome DevTools MCPは、Model Context Protocol（MCP）という仕組みを使って、AIがブラウザを操作できるようにするツールだ。

### MCPとは

MCPは、AIが外部のツールやサービスと接続するための標準規格のようなもので、Anthropicが提唱している。

たとえば、

* ファイルシステムにアクセスする
* データベースに接続する
* Webブラウザを操作する

といった機能を、統一されたインターフェースでAIに提供できる。

Chrome DevTools MCPは、その中でもブラウザ操作に特化したMCPサーバーだ。

### 何ができるのか

Chrome DevTools MCPを導入すると、AIは次のようなことができるようになる。

* ブラウザでページを開く
* スクリーンショットを撮る
* ページ内の要素をクリックする
* フォームに入力する
* JavaScriptを実行する
* レンダリング後のDOMを取得する

つまり、**人間がブラウザでやることを、AIに代行させられる**。

SPA問題の文脈では、「レンダリング後のDOMを取得する」という部分が特に重要になる。

---

## 導入手順

Chrome DevTools MCPの導入は、だいたい次の流れになる。

### 1. MCPサーバーの追加

ターミナルで以下のコマンドを実行するだけでよい。

```
claude mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest
```

これで、Claude CodeにChrome DevTools MCPが登録される。

### 2. 動作確認

Claude Codeで次のように指示すると、ブラウザが起動してページを開くことができる。

```
Google Mapsを開いて、東京駅周辺の様子を教えて
```

これで、AIがブラウザを操作して情報を取得してくれる。

---

## どう使うか

導入したあと、実際にどう使うかを整理しておく。

### 基本の使い方

AIに対して、こんな指示を出すだけでよい。

```
ブラウザで https://example.com を開いて、ページの内容を教えて
```

ただし、Claude Codeは標準では `WebFetch` を使おうとすることがあるため、SPAのページで確実にChrome DevTools MCPを使わせたい場合は、ツール名を明示するのが確実。

```
chrome-devtoolsを使って https://example.com を開いて、ページの内容を教えて
```

### SPAサイトでの使い方

SPAのサイトでは、次のように指示するとうまくいく。

```
https://example.com/dashboard をブラウザで開いて、
ダッシュボードに表示されている数値を教えて
```

レンダリングが完了するまで少し待つ必要がある場合は、こう指示することもできる。

### スクリーンショットを撮る

視覚的な情報を取得したい場合は、スクリーンショットを撮らせることもできる。

```
Google Mapsで「東京タワー」を検索して、結果のスクリーンショットを撮って
```

これで、AIが検索操作をして、結果を画像で返してくれる。

こうした使い方は、通常のWebFetchではできない。

---

## まとめ

AIにURLを渡して内容を取得してもらう場面は増えているが、

SPAで実装されているサイトでは、通常の方法ではコンテンツを取得できない。

Chrome DevTools MCPを導入すると、AIがブラウザを操作して、JavaScriptでレンダリングされた後の状態を取得できるようになる。

これにより、「Google MapsのようなSPAサイトの内容が読める」ようになった。

導入自体は簡単で、コマンド一発で追加できるので、試してみる価値はある。

---
