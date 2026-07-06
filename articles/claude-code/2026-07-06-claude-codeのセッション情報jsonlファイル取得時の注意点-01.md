---
id: "2026-07-06-claude-codeのセッション情報jsonlファイル取得時の注意点-01"
title: "Claude Codeのセッション情報（JSONL）ファイル取得時の注意点"
url: "https://zenn.dev/eda_sann/articles/64d29ee57cba2c"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-07-06"
date_collected: "2026-07-07"
summary_by: "auto-rss"
query: ""
---

## 結論

Claude Codeのセッション情報（JSONLファイル）を外部ツールから取得しようとして、`~/.claude/projects` 配下を調べたものの目的のフォルダが見つからずにハマったことはないでしょうか。

結論から言うと、

Claude CodeのJSONL保存先ディレクトリ名は、プロジェクトの絶対パスをそのまま利用しているわけではありません。

**絶対パス中の英数字以外の文字は `-` に変換された形式で保存されています。**

そのため、単純にプロジェクトパスからJSONLファイルの保存先を組み立てると失敗する場合があります。

## Claude CodeのJSONLファイル保存場所

Claude Codeのセッションログは以下の形式で保存されます。

```
~/.claude/projects/<encoded-project-path>/<session-id>.jsonl
```

公式ドキュメントでは、以下の例が記載されています。

↓

つまり、パス区切り文字 `/` がそのまま残るのではなく、ディレクトリ名として利用できる形式へ変換されています。  
参考: <https://claude-dev.tools/docs/jsonl-format>

## 実際にハマる例

例えば次のプロジェクトを考えます。

```
/home/user/work/my-project
```

これに対応するClaude Codeのコンテキストディレクトリは次のようになります。

```
-home-user-work-my-project
```

一方で、さらに記号や日本語が含まれる場合には注意が必要です。

↓

英数字以外の文字を含む箇所は `-` に変換されるため、単純なパス変換では一致しない場合があります。

## まとめ

Claude Codeでは、`~/.claude/projects` 配下のディレクトリ名として、

へ変換した値が利用されます。JSONLを直接参照するツールを作る際は、この変換ルールを考慮して実装しましょう。
