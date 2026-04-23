---
id: "2026-04-16-wsl2にインストールしたplaywright-mcpをclaudedesktopから使えるようにす-01"
title: "WSL2にインストールしたPlaywright-mcpをClaudeDesktopから使えるようにする"
url: "https://qiita.com/snow_cornice_man/items/605cd3fa576681c7b269"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "qiita"]
date_published: "2026-04-16"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

# はじめに

最近Claudeが流行っているので色々試している中で、Playwright-mcpをClaudeDesktopから使えるよう設定するのに色々苦労したので同じように困っている人のためにメモとして残したいと思います。

# 環境

* Windows 11
* WSL v2.6.3.0 (Debian 13.4)
* Claude Desktop for Windows v1.2773.0
* WSL側でNode.js, Playwright（本体、MCPサーバ、ブラウザ）はインストール済とする

# どんな問題が起きたか？

基本的にClaudeDesktopでPlaywright-mcpを使うためにやることは、各ツールのインストールと`claude_desktop_config.json`の設定です。  
たったそれだけのはずが3つの問題に遭遇し、思いのほか時間がかかってしまいました。。

1. [公式](https://github.com/microsoft/playwright-mcp?tab=readme-ov-file#getting-started)通りに`claude_desktop_config.json`を設定しても動かない
2. WSLにツールをインストールした場合の実行方法が分かったが、nodeが見つからないエラー
3. MCP自体はうまく動いたが、Claudeにスクショを撮ってもらうと権限エラーになる

# 最終的な結論

最終的にこちらの設定でうまく動作した。

claude\_desktop\_config.json

```
{
  "mcpServers": {
    "playwright": {
      "command": "wsl",
      "args": [
        "-d", "Debian",
        "--",
        "/usr/bin/env",
        "-C", "{任意のディレクトリパス（playwrightのスクショの保存先）}",
        "PATH={nodeのフルパス}:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
        "npx",
        "-y",
        "@playwright/mcp@latest"
      ]
    }
  }
}
```

# 問題への対処

どの問題もすべて`claude_desktop_config.json`の記載方法で解決できました。

## 1. 公式通りにclaude\_desktop\_config.jsonを設定しても動かない

こちらはシンプルで、npxコマンドはWindows側にないため起きていたエラーでした。  
`npx`の前に`wsl`コマンドを打ってあげることで解決

修正Ver.1

```
{
  "mcpServers": {
    "playwright": {
      "command": "wsl",
      "args": [
        "npx",
        "@playwright/mcp@latest"
      ]
    }
  }
}
```

## 2. WSLにツールをインストールした場合の実行方法が分かったが、nodeが見つからないエラー

ここが今回一番詰まったところでした。  
エラーログを見ると`env: ‘node’: No such file or directory`というエラーでしたが、WSL上で`node`や`npx`が使えることは確認済。  
フルパスを指定しなきゃいけないという記事を見つけ、`npx`のフルパスを入れてみましたがそれでもダメでした。（`npx`のパスは`where npx`コマンドで取得）  
そこでClaudeにエラー原因を聞いてみると「おそらく`npx`が内部の`node`を参照するときにエラーが出ており、WSL起動時の`PATH`に`node`がないのが根本原因」と返答がありました。  
`wsl --`でコマンドを打った場合、Windows側の環境変数しか見れないようです。  
そのため、コマンドで`PATH`を渡してやることでMCPとのサーバとの接続ができました。

修正Ver.2

```
{
  "mcpServers": {
    "playwright": {
      "command": "wsl",
      "args": [
        "bash",
        "-c",
      　"PATH={nodeのフルパス}:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin {npxのフルパス} @playwright/mcp@latest"
      ]
    }
  }
}
```

## 3. MCP自体はうまく動いたが、Claudeにスクショを撮ってもらうと権限エラーになる

MCPも接続できたので`example.com`のスクショを依頼したところ「playwright-mcpがWindows側のパス（/mnt/c/Windows/System32/）にディレクトリを作ろうとして失敗しています」という返事。  
詳細を見ると権限エラーとなっていた。  
これは`playwright-mcp`がスクショの保存などを行うディレクトを作業ディレクトリ上に作成する仕様によるものと判明。  
`cd`コマンド等を追加して、動作するディレクトリを管理者権限の不要な任意の場所に変えることで解決。

# 参考
