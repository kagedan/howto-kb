---
id: "2026-07-21-superdoccimo-agent-security-で足りないのは危ない-prompt-っぽいで-01"
title: "@superdoccimo: agent security で足りないのは、「危ない prompt っぽい」ではなく、同じ危険を同じ名前で呼べることだ"
url: "https://x.com/superdoccimo/status/2079652223869476932"
source: "x"
category: "claude-code"
tags: ["MCP", "prompt-engineering", "AI-agent", "x"]
date_published: "2026-07-21"
date_collected: "2026-07-22"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

agent security で足りないのは、「危ない prompt っぽい」ではなく、同じ危険を同じ名前で呼べることだと思います。

aveproject/ave は、そこを AVE ID と AIVSS score に落とす OSS 標準です。README と record set を見る限り、skill file、MCP server manifest、system prompt、agent plugin の危険な振る舞いに stable ID、behavioral fingerprint、remediation、OWASP MCP Top 10 や MITRE ATLAS への mapping を付けます。

使いどころは、agent 用の scanner、CI、SARIF、社内レビューです。たとえば「この skill はなんとなく怪しい」ではなく、「これは tool hook hijacking の型で、どの stage で検出し、どう封じるか」と渡せる。

僕が面白いと思ったのは、CVE 的な product/version の穴では拾いにくい、自然言語の行動指示そのものを分類対象にしているところです。agent の部品は code だけでなく、説明文や設定文でも動きが変わるので、ここに名前を付ける価値があります。

ただし今回は GitHub、README、release、record JSON、reference scanner の確認までです。各 detection rule の精度や運用負荷は、自分の skill/MCP 棚に当てて確かめる必要があります。

情報元: GitHub / Hacker News
