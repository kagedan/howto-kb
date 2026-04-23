---
id: "2026-04-05-claude-code-の-settingsjson-が丸ごと無視されていた話と対処法-01"
title: "Claude Code の settings.json が丸ごと無視されていた話と対処法"
url: "https://qiita.com/gumiyuya/items/645484ec42b221b719ef"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-05"
date_collected: "2026-04-06"
summary_by: "auto-rss"
---

## はじめに

気づいたきっかけは、Claude Codeの `settings.json` にsandboxのデフォルト有効設定を書いたことでした。  
`~/.claude/settings.json` に以下の設定を追加して起動し `/sandbox` で確認するも反映されず、  
よく見ると `"model": "claude-opus-4-6"` すら効いておらず Sonnet 4.5 で起動していました。

```
{
  // 元々書いてた
  "model": "claude-opus-4-6",

  // ~略~

  // 追記
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true
  }
}
```

[![](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3718885%2F12040ea0-3adb-4428-b263-a0a0f468f8ef.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2ec23bcc26fb7517d218df008b4d1e89)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3718885%2F12040ea0-3adb-4428-b263-a0a0f468f8ef.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2ec23bcc26fb7517d218df008b4d1e89)

確信はありませんでしたが、どうやら `settings.json` 自体が丸ごと読み込まれていないようでした。  
原因特定まで結構な時間を使ったので、同じ現象でハマる人向けに共有します。

## 症状

* settings.json に `"model": "claude-opus-4-6"` を書いているのに Sonnet 4.5 で起動する
* sandbox を `"enabled": true` にしても `/sandbox` では `No Sandbox (current)` のまま
* `settings.local.json` の設定だけは正常に反映される

実を言うと、`settings.local.json` にはsandbox設定を書いていました。  
そのため、正確には以下の状況でした。

1. `settings.local.json` でsandboxを有効にしてセッションを開始すると、`Sandbox BashTool, with auto-allow (current)` で起動
2. `settings.json` にsandbox有効設定を追記してセッションを開始すると、`No Sandbox (current)` で起動
3. 2の後に `settings.local.json` からsandbox設定を消してセッションを開始すると、`No Sandbox (current)` で起動

## 原因

色々格闘した後、`claude doctor` を実行したところ、以下の結果が返ってきました。

```
~ $ claude doctor

 Diagnostics
 └ Currently running: npm-global (2.0.37)
 └ Path: /opt/homebrew/Cellar/node/25.1.0_1/bin/node
 └ Invoked: /opt/homebrew/bin/claude
 └ Config install method: unknown
 └ Auto-updates: default (true)
 └ Update permissions: Yes
 └ Search: OK (vendor)

 Invalid Settings
 ~/.claude/settings.json
  └ permissions
    └ deny
      ├ "Bash(docker compose exec * ruby -e:*)": Use ":*" for prefix matching, not just "*". Change to "Bash(docker compose exec :* ruby -e::*)" for prefix matching. Examples: Bash(npm run:*), Bash(git:*)
      └ "Bash(docker compose exec * rails runner:*)": Use ":*" for prefix matching, not just "*". Change to "Bash(docker compose exec :* rails runner::*)" for prefix matching. Examples: Bash(npm run:*), Bash(git:*)
```

`settings.json` の deny ルールの中にワイルドカードの書き方が間違っているものが2つあっただけなのですが、これが原因で `settings.json` 全体がスキップされていました。

## 修正

```
- "Bash(docker compose exec * ruby -e:*)"
+ "Bash(docker compose exec :* ruby -e:*)"
- "Bash(docker compose exec * rails runner:*)"
+ "Bash(docker compose exec :* rails runner:*)"
```

Claude Codeの権限ルールでは、プレフィックスマッチングに `*` ではなく `:*` を使う必要があったのです。

修正後、`settings.json` の全設定（モデル、sandbox、hooks 等）が正常に読み込まれるようになりました。

[![](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3718885%2F0f9c0574-c824-45fa-8348-ee4b378bebac.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d075384c17f6fc9a350048fde7461fb5)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3718885%2F0f9c0574-c824-45fa-8348-ee4b378bebac.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d075384c17f6fc9a350048fde7461fb5)

## 実はアップデートだけでも直る

ここまでの修正で解決はしたのですが、気になることがありました。別のPCでClaude Code（当時 v2.1.88）を起動した時は同じ `settings.json` で問題なく動いていたのです。  
調べてみると、v2.1.0 の changelog に以下の記載がありました。

> Added wildcard pattern matching for Bash tool permissions using `*` at any position in rules (e.g., `Bash(npm *)`, `Bash(* install)`, `Bash(git * main)`)

v2.0.x では deny ルールの途中に置いた `*` は不正な構文として扱われていましたが、v2.1.0 で任意の位置の `*` がワイルドカードとして正式サポートされました。

実際に v2.0.37 → v2.1.0 にアップデートし、上記の修正を行わずに deny ルールをそのまま（`*` のまま）にした状態で起動したところ、`settings.json` が正常に読み込まれ、モデルもsandboxも反映されました。

[![](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3718885%2F3462a293-5f10-42cf-a915-4b6dde204beb.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e7d9960d119e866649ee275e1107f218)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3718885%2F3462a293-5f10-42cf-a915-4b6dde204beb.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e7d9960d119e866649ee275e1107f218)

つまり、deny ルールの `:*` への修正をしなくても、v2.1.0 以降にアップデートするだけで解決します。

## 厄介なポイント

この問題が厄介なのは、バリデーションエラーが起動時に一切表示されないことです。

`settings.json` にバリデーションエラーがあると、Claude Codeはエラーを出さずにファイル全体を黙ってスキップします。部分的に読んでくれるわけでもありません。deny ルール1つの記法ミスで、モデル設定もsandboxもhooksも全部無視されます。

起動画面にも何も出ないので、設定が効いていないことに気づくのに時間がかかります。

## 設定が反映されないときは

これを最初に実行してください。何か不具合があれば報告してくれます。

## 参照
