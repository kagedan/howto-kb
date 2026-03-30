---
id: "2026-03-29-officeドキュメントやpdfをaiに読ませるためのmcpサーバdoctools-mcpを作ってみ-01"
title: "OfficeドキュメントやPDFをAIに読ませるためのMCPサーバ「DocTools MCP」を作ってみた"
url: "https://zenn.dev/snaga/articles/2026-03-29-doctools-mcp-agentic-rag"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "AI-agent", "zenn"]
date_published: "2026-03-29"
date_collected: "2026-03-30"
summary_by: "auto-rss"
---

tl;dr


AIエージェントに「目」と「手」を与える: ExcelやPowerPointなどのOfficeファイルやPDFをOn-the-flyでMarkdown変換・画像化し、エージェントが自律的に読み取れるようにするMCPサーバを開発。

「Agentic RAG」をローカルで実現: 複雑なベクトルDBは不要。エージェントが自ら検索ツールを駆使し、数千件のドキュメントから必要な情報を秒速で深掘り。

圧倒的な解像度向上: PPTの構成図をPNG化してマルチモーダルで理解するなど、コピペでは不可能な情報の活用を可能に。

結論、力技は正義: 精度よりも「手間ゼロ」を優先し、必要...
