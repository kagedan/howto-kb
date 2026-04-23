---
id: "2026-03-16-onecli-aiエージェントのための1passwordを試した-01"
title: "OneCLI: AIエージェントのための1Passwordを試した"
url: "https://zenn.dev/numa08/articles/ccf33c30c11b76"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "zenn"]
date_published: "2026-03-16"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

AIエージェント向けの1Passwordは分かりやすく表現するために使って言い回しで、実際には結構違うツールです（挨拶）

## AIエージェントのための1Passwordとは？

AIエージェント、使っていますか？OpenClaw、Claude CodeなどローカルPCで動作して色々なファイルを読み書きしたりMCPで外部APIを呼び出して作業したり、仕事に無くてはならない存在となってきています。

一方、AIエージェントが読み書きできる場所に外部サービスの認証情報を保管するリスクもあります。もちろんリテラシーの高い人ならば適切にファイルのアクセス権限を設定したり、エージェントごとの設定ファイルで読み込みに制限をかけます。

しかし、AIエージェントがツール呼び出しのリクエストを組み立てる上で認証情報が必要だったりそもそもローカルファイルにある認証情報をプロンプトで規制してもエージェントが読み込んでしまう事象も知られています。

<https://genai.owasp.org/llmrisk/llm01-prompt-injection/>

そこで、そもそもAIエージェントに認証情報を教えないことで問題の解決ができないか？と考えられます。

OneCLIは1Passwordのように認証情報を管理、暗号化します。AIエージェントはOneCLI経由でAPIを呼び出すことで認証情報を知らなくても、APIを利用できます。

## やってみた

公式リポジトリをcloneして動かしてみます。動作環境は

* WSL2
* Docker v29.2.1, Docker Compose v5.1.0

`docker compose -f docker/docker-compose.yml up`で起動するようですが、ネットワークの問題でアプリサーバーからDBにアクセスできなかったのでちょっと修正。PR出しました。

<https://github.com/onecli/onecli/pull/49>

実行するとダッシュボードにアクセスできます。

![](https://static.zenn.studio/user-upload/e1d627e9c59c-20260316.png)

`Try it`をクリックしてモックリクエストを組み立てます。以下のコマンドをターミナルから実行することで何が起きているか分かります。

```
$ curl -k -x http://x:aoc_your_agent_key_here@localhost:10255 -H "Authorization: Bearer FAKE_TOKEN" https://httpbin.org/anything
{
  "args": {},
  "data": "",
  "files": {},
  "form": {},
  "headers": {
    "Accept": "*/*",
    "Authorization": "Bearer WELCOME-TO-ONECLI-SECRETS-ARE-WORKING",
    "Host": "httpbin.org",
    "User-Agent": "curl/8.5.0",
    "X-Amzn-Trace-Id": "Root=1-69b7c8d3-31c6d7e93fe326a234ab0e9e"
  },
  "json": null,
  "method": "GET",
  "origin": "121.104.133.75",
  "url": "https://httpbin.org/anything"
}
```

リクエストヘッダーの`Bearer FAKE_TOKEN`をOneCLIのゲートウェイが読み取ってこの場合の本物のトークンである`Bearer WELCOME-TO-ONECLI-SECRETS-ARE-WORKING`に書き換えています。AIエージェントから使うときは偽のトークン情報を保存しておいて`http://x:aoc_your_agent_key_here@localhost:10255`に対してプロキシするようにしておけば良いというわけですね。`-x`オプションでプロキシ呼び出しを、`http://x:`はダミーのユーザーによる認証で、`aoc_your_agent_key_here`がOneCLIから払い出されるトークン情報です。

## GitHub Api を呼び出してみる

ダッシュボードの`Secrets`から以下の設定をします。

* Name: GitHub Personal Access Token
* Value: ghp\_xxxxxxxxxxxx（実際のトークン）
* Host Pattern: api.github.com
* Path Pattern: \*
* Header name: Authorization
* Value Format: Bearer {value}

![](https://static.zenn.studio/user-upload/166d89cf6cc8-20260316.png)

この設定をして、ローカルのClaude codeからリクエストを出してもらいました。

```
❯ 全部で covelline 内の public リポジトリが何個あるか調べてください。。                                                                                                                                  

● Bash(curl -sk -x http://x:aoc_your_agent_key_here@localhost:10255 -H "Authorization: Bearer FAKE_TOKEN" "https://api.git…)
  ⎿  Public repos: 30
       - feather-PressKit
       - Atmosphere
     … +28 lines (ctrl+o to expand)

● covelline org の public リポジトリは 30個 です。
```

Claude Code にPersonal Access Tokenを渡すことなくGitHub Apiにアクセスができました。

## まとめ

AIエージェントに秘密情報を与えることなくAPIへのアクセスを許可させるOneCLIを試しました。エージェントの権限を強くすることでできることは増えますが、一方機密情報・認証情報と言った重要な情報の取り扱い方法もまた管理が大変です。OneCLIのようなツールによって、安全にAIによるデータアクセスを制御可能になるかもしれません。

なお、OneCLI はHTTPプロキシとして動作するため、AIエージェントが直接HTTPリクエストを投げるケースには強いですが、MCPサーバーの設定ファイルにAPIキーを書くタイプの連携（例えばSlackやNotionのMCPサーバーな  
ど）ではこの仕組みの恩恵を受けられません。MCPサーバー自体がHTTPで外部APIを叩く実装であればプロキシ設定で経由させることもできそうですが、現時点ではそこまで試せていません。このあたりは今後のエコシステムの発展に期待です。

合同会社コベリンではAIを導入した業務の改善や運用を実施しています。AI導入の相談やノウハウの共有にご興味がありましたら連絡いただけましたらお返事します。

<https://covelline.com/>
