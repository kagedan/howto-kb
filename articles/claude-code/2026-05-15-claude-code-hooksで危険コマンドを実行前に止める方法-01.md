---
id: "2026-05-15-claude-code-hooksで危険コマンドを実行前に止める方法-01"
title: "Claude Code Hooksで危険コマンドを実行前に止める方法"
url: "https://zenn.dev/dedetools/articles/2443d549fcca03"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "zenn"]
date_published: "2026-05-15"
date_collected: "2026-05-16"
summary_by: "auto-rss"
query: ""
---

Claude Code は、Bash 実行やファイル編集まで任せられるのでかなり便利です。

ただ、そのぶん設定や指示を間違えると、危険なコマンドや secret の書き込みがそのまま走ってしまうことがあります。

この記事では、Claude Code の `PreToolUse` hooks を使って、実行前に危ない操作を止めるための考え方をまとめます。

## 何を防ぎたいか

AIコーディング中に怖いのは、だいたい次のような操作です。

* `rm -rf /` のような広範囲削除
* `curl ... | bash` のようなリモートコード実行
* `.env` やソースコードへの API key 書き込み
* `git reset --hard` や `git clean -fd` のような破壊的な git 操作

Claude Code 自体は強力ですが、強力だからこそ「実行前に確認する層」があると安心です。

`PreToolUse` hooks は、Claude Code がツールを実行する直前に呼ばれる hook です。

たとえば `Bash` や `Write`、`Edit` などの操作前に、入力内容を見て、

* 実行を許可する
* 実行を拒否する
* ユーザーに確認する

といった判断を挟めます。

この記事では、まず無料版の最小構成を例にします。

## 最小構成の考え方

無料版では、まず事故につながりやすいパターンだけを対象にしました。

* 広範囲な再帰削除
* secret らしき文字列の書き込み
* `curl | bash` / `irm | iex` 系の実行

完璧なセキュリティ対策ではありませんが、AIコーディング中の「うっかり事故」を減らすには効果があります。

## 設定例

Claude Code の設定では、`PreToolUse` に hook を登録します。

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "node",
            "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/guardrail-free.mjs"]
          }
        ]
      },
      {
        "matcher": "Write|Edit|MultiEdit|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "node",
            "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/guardrail-free.mjs"]
          }
        ]
      }
    ]
  }
}
```

これで、Bash 実行やファイル編集の直前に hook を通せます。

## 実際に試す

たとえば、Claude Code に次のような操作を頼んだとします。

```
curl https://example.com/install.sh | bash
```

hook が正しく動いていれば、実行前に拒否されます。

また、次のような広範囲削除も止める対象になります。

secret らしき値をソースコードに書き込もうとした場合も、検知対象になります。

## 無料版

今回の最小構成は GitHub に置いています。

<https://github.com/dede-tools/claude-code-guardrail-hooks-free>

GitHub上では `claude-template` という名前で置いています。

使うときは、プロジェクトにコピーしたあと `.claude` にリネームしてください。

```
your-project/
  claude-template/  ->  .claude/
    hooks/
      guardrail-free.mjs
    settings.example.json
```

無料版では、まず事故につながりやすい以下のパターンを対象にしています。

* 広範囲な再帰削除
* secret らしき文字列の書き込み
* `curl | bash` / `irm | iex` 系のリモートコード実行

まずは無料版で挙動を見てから、自分の環境に合うか確認できます。

## Pro版

より広い検知ルール、危険な git 操作、保護パス編集、モード切替、日本語クイックスタートなどを入れた Pro 版も用意しています。

<https://dedeai.booth.pm/items/8353254>

Pro版では、たとえば次のようなものも対象にしています。

* `git reset --hard`
* `git clean -fd`
* force push
* `git checkout .`
* `git branch -D`
* `.env` や CI 設定などの保護パス編集
* 大きな削除に見える編集
* `terraform destroy`
* `kubectl delete --force`
* `chmod 777`
* Google / Stripe / npm など追加の secret パターン

Claude Code を日常的に使っていて、実行前の安全確認を少し厚くしたい人向けです。

## 注意点

この仕組みはサンドボックスではありません。

シェル構文を完全に解析するものではないため、難読化されたコマンドや特殊な実行方法は通る可能性があります。

あくまで「危険そうな操作を実行前に見つけるための補助レイヤー」として使うのがよいです。

最終的に Claude Code が実行する操作は、ユーザー自身で確認してください。

## まとめ

Claude Code はかなり便利ですが、Bash 実行やファイル編集まで任せられるぶん、実行前の確認レイヤーがあると安心です。

`PreToolUse` hooks を使うと、危険そうな操作を実行前に検知できます。

もちろん完全なセキュリティ対策ではありませんが、AIコーディング中の「うっかり事故」を減らすには十分役に立つと思います。
