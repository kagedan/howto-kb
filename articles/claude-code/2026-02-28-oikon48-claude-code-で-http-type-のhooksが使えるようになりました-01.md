---
id: "2026-02-28-oikon48-claude-code-で-http-type-のhooksが使えるようになりました-01"
title: "@oikon48: Claude Code で \"http type\" のHooksが使えるようになりました。
 
今までは command"
url: "https://x.com/oikon48/status/2027658781895889312"
source: "x"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "x"]
date_published: "2026-02-28"
date_collected: "2026-03-19"
summary_by: "auto-x"
---

Claude Code で "http type" のHooksが使えるようになりました。
 
今までは command, prompt, agent の3 typeでしたが、新たに http が追加されています。http Hook は既存のHooks システムに新しいトランスポート層を追加したもの。
 
HTTP hook fields:
 
- url: URL to send the POST request to
- headers: Additional HTTP headers as key-value pairs.                   
- allowedEnvVars: List of environment variable names that may be interpolated
 
大きな違いは、command Hook では `exit 2` で明示的にブロックできますが、http Hook ではネットワーク障害とブロック意図の区別ができないため、「エラー = 続行」という安全側に倒しています。ブロックしたい場合は必ず 2xx を返す必要があ
