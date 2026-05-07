---
id: "2026-05-06-claudeのcomputer-useでmacのサードパーティアプリが認識されない問題と解決方法-01"
title: "Claudeのcomputer-useでMacのサードパーティアプリが認識されない問題と解決方法"
url: "https://zenn.dev/kent0011/articles/9cbc87949a58e4"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "cowork", "zenn"]
date_published: "2026-05-06"
date_collected: "2026-05-07"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude CodeやClaude Cowork等でComputer Use機能を利用している際、Macにインストールされているはずのサードパーティ製アプリ（VS Code、Zed、Google Chrome、Slackなど）が認識されず、操作に失敗する問題が発生することがあります。

ログを確認すると、Apple純正のアプリしかインデックスされていない状態になっているのが特徴です。GitHubのIssue等でも類似の報告がいくつか上がっています。  
<https://github.com/anthropics/claude-code/issues/43760>

## 原因

結論から言うと、これはClaude系ツールのバグではなく、macOS側のSpotlightインデックスの破損（または欠落） が根本原因である可能性が高いです。

Claudeのcomputer-useがMac内のアプリケーション一覧を取得する際、内部的に `mdfind`（macOSのSpotlight検索を利用するコマンド）などのOSの検索機能を利用しているようです。そのため、Spotlightのインデックスが壊れていると、Claudeもアプリを見つけることができません。

自分がこの問題に該当するかは、ターミナルで以下のコマンドを実行することで確認できます。

```
mdfind {任意のサードパーティ製アプリケーション名} -name

# ↓例
mdfind Slack -name
```

ここで `/Applications/{アプリ名}.app` がヒットしない場合は、インデックスが壊れています。

### なぜインデックスが壊れるのか？

環境によって異なりますが、以下のような要因が考えられると思います。

* 誤削除  
  ターミナルやDaisyDiskなどのストレージ管理アプリ経由で、誤ってインデックス関連のファイルを消去してしまった。
* サードパーティ製ランチャーの影響  
  AlfredやRaycastなどを利用している環境で、何らかの理由でシステムのインデックスと競合・不整合が起きた。
* ストレージ容量の逼迫  
  Macの空き容量が限界に近づくと、OSがキャッシュやインデックスを自動破棄したり、更新を停止したりすることがあるかも？

## 解決方法

Spotlightのインデックスを再構築することで解決します。以下のいずれかの方法を実行してください。

### 方法1: mdutil コマンドを使用する

ターミナルから以下のコマンドを実行し、インデックスを強制的に消去・再構築させます。

参考↓  
<https://qiita.com/P-man_Brown/items/aacde772fe78171f10fe>

### 方法2: システム環境設定からやる

<https://support.apple.com/ja-jp/102321>

## まとめ

AIエージェントツールで「アプリが見つからない」「ファイルが見つからない」という挙動に遭遇した場合、ついツール側のIssueやプロンプトを疑いがちですが、OSの検索機能（mdfind / Spotlight）が正常に機能しているかを疑うことで解決の糸口が見えることがあります。同じ問題でハマっている方の参考になれば幸いです。
