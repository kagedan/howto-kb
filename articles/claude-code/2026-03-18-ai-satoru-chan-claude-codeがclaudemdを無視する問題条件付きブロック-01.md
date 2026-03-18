---
id: "2026-03-18-ai-satoru-chan-claude-codeがclaudemdを無視する問題条件付きブロック-01"
title: "@ai_satoru_chan: Claude CodeがCLAUDE.mdを無視する問題、条件付きブロックで解決するテクニックが話題に

Claude "
url: "https://x.com/ai_satoru_chan/status/2034182892902040050"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "x"]
date_published: "2026-03-18"
date_collected: "2026-03-18"
summary_by: "auto-x"
---

Claude CodeがCLAUDE.mdを無視する問題、条件付きブロックで解決するテクニックが話題に

Claude CodeはCLAUDE.mdを「関連性があるかもしれないし、ないかもしれない」というシステムリマインダーでラップする
ファイルが長いと、個々のセクションをオプション扱いしがち

解決策は `<important if="condition">` タグ

```
<important if="you are writing or modifying tests">
- Use createTestApp() helper
- Mock database with dbMock
</important>
```

条件を明示することで、いつ適用すべきか明確なシグナルを与えられる

すべてをラップするのはNG
プロジェクト構造や技術スタックなど、常に有効な部分はそのままでOK

元ネタ: https://t.co/qXvRlW4uyG
