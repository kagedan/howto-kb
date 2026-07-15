---
id: "2026-07-15-claude-codeでapi-error-response-stalled-mid-stream-01"
title: "Claude CodeでAPI Error: Response stalled mid-stream. The response above may be incomplete.が出る"
url: "https://qiita.com/ou-mori/items/cd7b2cf089496215acbc"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-07-15"
date_collected: "2026-07-15"
summary_by: "auto-rss"
query: ""
---

# はじめに

Claude Codeで開発していると、たまに以下のエラーが発生しました。

`Version: 2.1.205`

```
API Error: Response stalled mid-stream. The response above may be incomplete.
```

このエラーが発生すると、`continue`しても`/rewind`しても、同じエラーが返ってきます。

# 暫定対処

毎回、5分5秒くらいで発生していたので、一旦タイムアウト時間を伸ばしてみています。  
`~/.claude/settings.json`に以下の設定を追加して、Claude Codeを再度立ち上げます。

~/.claude/settings.json

```
{
  "env": {
    "API_TIMEOUT_MS": "1200000",
    "CLAUDE_STREAM_IDLE_TIMEOUT_MS": "600000"
  }
}
```

# まとめ

おそらくサーバーからのレスポンスが返ってくる前に、タイムアウトになったのかなと推察しますが、  
`/resume`と`continue`で再開するとエラーは一旦なくなったので、様子見しています。
