---
id: "2026-06-26-unofficial-google-finance-mcp-open-source-01"
title: "Unofficial Google Finance MCP (Open-source)"
url: "https://qiita.com/zenixls2/items/b568182e2f40e442a730"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "qiita"]
date_published: "2026-06-26"
date_collected: "2026-06-27"
summary_by: "auto-rss"
query: ""
---

We all know that Google Finance discontinued its public API service years ago.

![Screenshot 2026-06-26 at 18.42.22.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/133489/d10bc6d0-89af-4500-aa7d-ce9ad5d79664.png)


In this article, I want to share a different way to access Google Finance data without scraping the page every few minutes.

![Screenshot 2026-06-26 at 18.41.04.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/133489/ea0a8bd6-8935-4f8c-be4e-47483232f0f9.png)
.

The API was never truly removed. Instead, it appears to have been converted into a different, more dynamic form that is harder to use directly. However, if you carefully inspect the network requests and responses, you may find some interesting JSON responses. From there, you can trace them back to several important objects in the HTML, such as:

`AF_initDataKeys` and `AF_dataServiceRequests`

You may also notice endpoints such as:

* https://www.google.com/finance/_/GoogleFinanceUi/data/batchexecute
* https://www.google.com/finance/beta/_/FinHubUi/data/batchexecute

I have documented the details on GitHub and built a local MCP service that allows AI agents to query the latest financial information provided by Google Finance. It is more powerful than the Google Sheets finance functions, and the project is fully open source.

Please check it out here:

https://github.com/woodstock-tokyo/google-finance-mcp/blob/master/README.md

Before using it further, please read the legal notice:

https://github.com/woodstock-tokyo/google-finance-mcp/blob/master/LEGAL.md

Have fun running it with Codex, Claude, Grok, Hermes, OpenCode, or your favorite AI agent workflow.
