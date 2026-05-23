---
id: "2026-05-23-claude-code-v21148-リリース毎日changelog解説-01"
title: "Claude Code v2.1.148 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/82124e21108d4a2a3535"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-05-23"
date_collected: "2026-05-23"
summary_by: "auto-rss"
query: ""
---

2.1.147 で混入した Bash ツールのデグレを潰す緊急修正リリース。

## 今回の注目ポイント

1. **Bash ツールが常に exit 127 を返すデグレを修正**: 2.1.147 にアップしてからコマンドが何も通らなくなっていた人向け

---

## Bash ツールが exit 127 を吐き続ける問題を解消

対象読者: 2.1.147 へ上げた直後から、Claude Code が動かしたコマンドが片っ端から失敗していた人。

Unix 系で exit code 127 は「command not found」を意味します。シェルが PATH を探してもバイナリを見つけられなかったときの戻り値。

```
$ nonexistent-command
zsh: command not found: nonexistent-command
$ echo $?
127
```

2.1.147 では一部ユーザーの環境で、Bash ツール経由のコマンドがすべてこの 127 を返していました。Claude Code から見ると、`ls` も `git status` も `pwd` も「そんなコマンドありません」状態。読み込みでも書き込みでも Bash を介する操作が全部詰む形です。

2.1.148 で戻り値の取り扱いが直り、実コマンドの終了ステータスが Claude Code 側に正しく届きます。

該当バージョン: 2.1.148(2026-05-22 リリース)。2.1.147 を入れていて Bash が死んでいるなら、2.1.148 に上げれば直ります。

## まとめ

2.1.148 は 2.1.147 由来のデグレ 1 件のみを潰す緊急パッチ。2.1.147 を踏んでいるなら今すぐ上げる、それだけ。
