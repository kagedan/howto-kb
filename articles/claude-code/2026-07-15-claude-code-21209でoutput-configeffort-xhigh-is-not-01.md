---
id: "2026-07-15-claude-code-21209でoutput-configeffort-xhigh-is-not-01"
title: "Claude Code 2.1.209で「output_config.effort 'xhigh' is not supported」と表示されたときの対処法"
url: "https://qiita.com/Shion1305/items/00566448b2e69ff6cc1a"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-07-15"
date_collected: "2026-07-15"
summary_by: "auto-rss"
query: ""
---

Claude Codeを`2.1.201`から`2.1.209`へアップグレードしたところ、次のエラーが表示されました。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F136916%2F0e9d6d43-03e7-483a-98ff-b58db6944ef4.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=ee19427a2fbea097333ceb0eff23894c)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F136916%2F0e9d6d43-03e7-483a-98ff-b58db6944ef4.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=ee19427a2fbea097333ceb0eff23894c)

```
API Error: 400 output_config.effort 'xhigh' is not supported when thinking is disabled on this model.
Use effort 'high' or below, or enable thinking.
```

## 原因

`effort`に`xhigh`が設定されている一方で、Thinking Modeが無効になっていることが原因です。

## 解決方法

Claude Codeで次のコマンドを実行します。

設定画面が表示されたら、**Thinking Modeを`true`に変更**します。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F136916%2F3e4455fc-59b2-414d-893e-b3513298ce95.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=7f68823e7e7d3a2e1003eec81325f114)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F136916%2F3e4455fc-59b2-414d-893e-b3513298ce95.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=7f68823e7e7d3a2e1003eec81325f114)

設定後、再度Claude Codeを実行すると、エラーが解消されました。

## まとめ

Claude Codeのアップグレード後に以下のエラーが出た場合は、

```
output_config.effort 'xhigh' is not supported when thinking is disabled
```

`/config`を開き、Thinking Modeを有効化してください。
