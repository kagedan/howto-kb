---
id: "2026-04-10-sigma-の公式ドキュメント情報にアクセス出来るsigma-document-mcp-server-01"
title: "Sigma の公式ドキュメント情報にアクセス出来る『Sigma Document MCP Server』連携をClaudeから試す"
url: "https://zenn.dev/truestar/articles/a01e4d4d4eca13"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-04-10"
date_collected: "2026-04-11"
summary_by: "auto-rss"
---

![Sigma&Claudeのロゴ画像](https://static.zenn.studio/user-upload/af41a167e009-20260410.png)

Sigma ComputingがMCP serverを使って公式ドキュメントをAIエージェントに提供する機能をBetaリリースしました。(※参考：[What's new in Sigma January 31st, 2026](https://help.sigmacomputing.com/changelog/2026-01-30))

Claude CodeやCursorなどのAIツールと組み合わせることで、Sigma操作に関する質問への回答精度が大きく向上します。

当エントリでは、この機能に関するMCP連携について、Claude Code及びClaude Desktopからの利用を試みてみた記録をお届けします。

## Sigma Document MCP Serverについて

<https://help.sigmacomputing.com/docs/use-documentation-mcp-server>

"Sigma documentation MCP server"は、Sigma Computingの公式ドキュメントをMCP（Model Context Protocol）経由でAIエージェントから参照できるようにするサーバーです。エンドポイントは <https://help.sigmacomputing.com/mcp> で、Claude Code・Cursor・Gemini CLIなど、MCPに対応したAIツールであればすぐに接続できます。

## Claude Code経由での利用

まずはClaude Codeからの利用手順について。最低限、Claude Codeを対象OS内で利用出来るような環境を整えておいてください。

```
% claude --version
2.1.100 (Claude Code)
```

`claude mcp add`コマンドで導入。

```
## グローバルで利用したかったので`--scope user`オプションを付与しています.
## また、上述ドキュメントにおいて『Sigmaのドキュメントサーバーは認証を必要としません。
## 接続タイプを選択する必要がある場合は、HTTPを選択してください』との記載があるので
## 『--transport http』でその旨指定しています.
% claude mcp add --scope user --transport http sigma-docs https://help.sigmacomputing.com/mcp

Added HTTP MCP server sigma-docs with URL: https://help.sigmacomputing.com/mcp to user config
File modified: /Users/xxxxxxxxxx/.claude.json

## 導入内容の確認.
% claude mcp list
Checking MCP server health...
:
sigma-docs: https://help.sigmacomputing.com/mcp (HTTP) - ✓ Connected
```

Claude Codeログイン後、`/mcp`コマンドでも導入内容を確認してみます。  
![Claude Codeログイン後の導入確認 by /mcpコマンド](https://static.zenn.studio/user-upload/90bcb3ff45ec-20260410.png)

いずれも問題無さそうです。現状、このMCPサーバーでは5つのツールが使える模様。  
![Claude Codeログイン後の導入確認 by /mcpコマンド 続き](https://static.zenn.studio/user-upload/0a3eb02bf538-20260410.png)

実際どんなことを聞いてどんな回答が返ってくるのか、確認してみます。

> Ask Sigmaについて詳しく知りたいです。参考資料があればそれらのリンクも付記する形で詳細解説をお願いします。

結果はこんな感じで返ってきました。元々英語表記のドキュメント類ですが、こういう形で日本語で要約された形で返ってくるだけでもありがたいです。  
![Claude CodeにてAsk SigmaのことをMCP経由で尋ねる #1](https://static.zenn.studio/user-upload/0d01887834f3-20260410.png)

![Claude CodeにてAsk SigmaのことをMCP経由で尋ねる #2](https://static.zenn.studio/user-upload/a8362d01114a-20260410.png)

![Claude CodeにてAsk SigmaのことをMCP経由で尋ねる #3](https://static.zenn.studio/user-upload/166a2ecadd5d-20260410.png)

![Claude CodeにてAsk SigmaのことをMCP経由で尋ねる #4](https://static.zenn.studio/user-upload/44360a87a357-20260410.png)

## Claude.ai(Web)経由での利用

続いて、Claude.ai(Web)経由でのMCP連携設定が出来るか試してみます。

結論としては行けました。利用可能です。

[設定]→[コネクタ]から[カスタムコネクタを追加]を選択。認証URLに`https://help.sigmacomputing.com/mcp`を入力し、設定として保存すればOKです。

![](https://static.zenn.studio/user-upload/b08c6e28077a-20260423.png)

接続すると、以下のSigma Computingの5ツールがClaude.aiの会話内で使えるようになります。

* search(ドキュメント検索)
* fetch(ページ詳細取得)
* search-endpoints(API検索)
* list-endpoints(API一覧)
* get-endpoint(APIエンドポイント詳細)

![](https://static.zenn.studio/user-upload/324d9e2429a1-20260423.png)  
*都度認証が面倒という場合は設定側で「全て許可」にしてしまってもいいかも*

WebUI上でSigma Document MCPに質問してみます。先日アップデートがあったAsk Sigma、直近でSigma Assistantに名称変更したのですがその点もちゃんと反映された情報が返ってきました。

![](https://static.zenn.studio/user-upload/c9007b6874d5-20260423.png)

## Claude Desktop経由での利用(現状NGな模様)

更に、Claude DesktopでのMCP連携設定が出来るか試してみます。

一応進め方の手順を残しておきます。メニューの[設定]→[開発者]から設定ファイルを呼び出し、任意のツールで編集を試みます。  
![Claude Desktop経由でのSigma Document MCPサーバー設定#1](https://static.zenn.studio/user-upload/38fbbe33c5a4-20260410.png)

本来であればここでjsonファイルに対してこのような設定を追加後、(※ただし現状Claude Desktopはこの形式に非対応のためエラーとなりますのであくまでイメージ)

```
{
  "mcpServers": {
    : 
    "sigma-docs": {
      "url": "https://help.sigmacomputing.com/mcp",
      "transport": "http"
    }
    :
  }
}
```

Claude Desktopを再起動→問題なければここでClaude Desktopも起動し、先に進めるはずだったのですがエラーとなってしまいます。  
![Claude Desktop経由でのSigma Document MCPサーバー設定#2](https://static.zenn.studio/user-upload/900b059622f8-20260410.png)

ここで『あれ...何でだろう？』となり、原因究明へ。せっかくClaude Code経由でSigmaのドキュメント情報にアクセス出来るようになったのでそのままこの件を『なんで？』と聞いてみました。結果は以下の通り。現状Claude DesktopではSigma Document MCPサーバーに対応していないようです。  
![Claude Desktop経由でのSigma Document MCPサーバー設定#3](https://static.zenn.studio/user-upload/7b7a4142a613-20260410.png)

ドキュメントにもその旨ちゃんと記載がありました(というのを教えてくれました)。  
![Claude Desktop経由でのSigma Document MCPサーバー設定#4](https://static.zenn.studio/user-upload/d3fe49a18c1b-20260410.png)

## まとめ

という訳で、Sigma(Sigma Computing)で展開されている『Sigma Document MCPサーバー』に対してClaude Code/Claude Desktopから連携を試みてみた記録の紹介でした。

Sigmaに関する情報をこのような形でスムーズに利活用出来るのは、日本語リソースがまだ少ない環境において、日本語話者としては非常に助かります。上記で案内したように現状ClaudeにおいてはClaude Codeでの利用のみ可能となる形ですが、最大限活用してSigmaの利活用に活かしていきましょう！
