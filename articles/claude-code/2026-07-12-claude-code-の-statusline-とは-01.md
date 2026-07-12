---
id: "2026-07-12-claude-code-の-statusline-とは-01"
title: "Claude Code の statusline とは"
url: "https://qiita.com/zumi0/items/52fc14ba2468ad5e995c"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "qiita"]
date_published: "2026-07-12"
date_collected: "2026-07-13"
summary_by: "auto-rss"
query: ""
---

## はじめに

以前は Mac のターミナルで Claude Code を使っていましたが、最近は Claude Desktop（デスクトップアプリ内の Claude Code）も試すようになりました。

ターミナル版を使っていた頃は、ccstatusline を入れて、画面下部にコンテキスト使用率や 5 時間制限・週次制限・リセットまでの時間を常時表示していました。

https://github.com/sirmalloc/ccstatusline

ところが Desktop でも使ってみたところ、この statusline は表示されませんでした。「hook を使えば同じ内容を出せるのでは？」と思って調べてみたところ、コンテキスト使用率は hook で出せそうだが、Session / Weekly は出せなさそう、とわかりました。そこで今回、そもそも statusline とは何かというところから整理してみます。

検証環境は macOS + Claude Code v2 系（2026年7月時点）です。

## statusline とは

一言で言うと、Claude Code（CLI 版）の画面下部に表示されるカスタマイズ可能なステータスバーです。`settings.json` に任意のシェルコマンドを設定すると、Claude Code がそのコマンドを実行し、stdin（標準入力）にセッション情報の JSON を渡してくれます。コマンドが stdout（標準出力）に出力した文字列がそのままバーに表示される、というシンプルな仕組みです。

公式ドキュメントはこちらです。

https://code.claude.com/docs/en/statusline

設定例は次のとおりです。

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh",
    "refreshInterval": 10
  }
}
```

## statusline が受け取れるデータ

ここが今回の本題です。statusline スクリプトが stdin で受け取る JSON には、個人的に注目したいフィールドがいくつかあります。とくに `rate_limits` や `cost` は、後述の hook からは取れませんでした。フィールドの一覧は公式ドキュメントにまとまっています。

https://code.claude.com/docs/en/statusline#available-data

個人的に気になったのは次のあたりです。

| フィールド | 内容 |
|---|---|
| `context_window.used_percentage` | コンテキストウィンドウ使用率（計算済み） |
| `cost.total_cost_usd` | セッションの推定コスト（USD） |
| `rate_limits.five_hour` | 5時間制限の使用率とリセット時刻（Unix 秒） |
| `rate_limits.seven_day` | 週次制限の使用率とリセット時刻 |

`rate_limits` は Pro / Max などのサブスクリプションプランで、セッション内の最初の API レスポンス以降に入ってきます。

5時間制限・週次制限の使用率はサーバー側の値で、公式ドキュメント上はこの statusline の JSON に載っています。hook の入力 JSON やローカルの transcript には、自分が確認した範囲では含まれていませんでした（hook の入力例は次のとおりです）。

https://code.claude.com/docs/en/hooks#userpromptsubmit-input

## 手軽に使うなら ccstatusline

CLI 版で statusline を使うだけなら、自分でスクリプトを書かなくても ccstatusline を設定するのが手軽です。

```json
{
  "statusLine": {
    "type": "command",
    "command": "npx -y ccstatusline@latest"
  }
}
```

モデル名・git ブランチ・コンテキスト使用率・使用量制限などをウィジェット形式で並べられます。

![スクリーンショット 2026-07-12 21.36.17.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/581736/9e7e7920-30bd-414d-80f7-1070dd7f529f.png)


## Claude Desktop では statusline が動かない

Claude Desktop には statusline を表示する場所がありません。それだけでなく、`statusLine.command` 自体が実行されません。

これはドキュメントに明記されていなかったので、自分で確認してみました。statusline コマンドを「stdin の JSON をログファイルに書き出すラッパースクリプト」に差し替え、CLI 版と Desktop 版で挙動を比較したところ、ターミナルで使っている間はログが増え続けるのに対して、Desktop ではログに追記されませんでした。

つまり Desktop では、`rate_limits` を含む statusline 用 JSON がそもそも生成されず、横取りする余地がありません。

## UserPromptSubmit hook も試してみた

statusline が使えないので、UserPromptSubmit hook で代用できないか試してみました。

https://code.claude.com/docs/en/hooks#userpromptsubmit

`settings.json` に hook を登録して、transcript からコンテキスト使用率を出してみたところ、ccstatusline の Ctx 表示に近いものはなんとか出せました。一方で、Session / Weekly の使用率やセッションコストなど、ccstatusline で常時見ていた情報は全部は再現できませんでした。

## さいごに

今回、Desktop でも使ってみて statusline 周りを調べてみました。CLI 版では当たり前に表示されていた使用量の情報が、Desktop ではそう簡単には出てこないな、というのが個人的な感想です。

statusline は仕組みとしてはシンプルなのに、レートリミットの使用率みたいな情報の出口になっているのが面白いところだなと思いました。Desktop でも statusline 相当の仕組みが使えるようになると嬉しいので、今後のアップデートに期待しています。
