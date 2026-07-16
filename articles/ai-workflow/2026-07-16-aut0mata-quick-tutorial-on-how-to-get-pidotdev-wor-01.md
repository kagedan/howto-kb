---
id: "2026-07-16-aut0mata-quick-tutorial-on-how-to-get-pidotdev-wor-01"
title: "@aut0mata: Quick tutorial on how to get @pidotdev working with @UnrealE"
url: "https://x.com/aut0mata/status/2077734073896759611"
source: "x"
category: "ai-workflow"
tags: ["MCP", "AI-agent", "x"]
date_published: "2026-07-16"
date_collected: "2026-07-17"
summary_by: "auto-x"
query: ""Model Context Protocol" tutorial OR "Claude MCP" integration"
---

Quick tutorial on how to get @pidotdev working with @UnrealEngine:

1. Go to plugins and install Unreal MCP (and also All Toolsets). The Terminal plugin is also interesting so you can run Pi inside the UE editor.

2. Enable Auto Start Server option in Edit > Editor Preferences > Model Context Protocol and restart UE

3. Add this .mcp.json to the root path of your Unreal project:

{
  "mcpServers": {
    "unreal-mcp": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}

4. Install the MCP adapter: with pi install npm:pi-mcp-adapter

5. Restart UE, open the terminal and go to the root path of your Unreal project and run pi

6. Inside pi, run /mcp and select the unreal-mcp, enable all tools and reconnect

That's it, you should be able to ask Pi to help you creating scenes, etc

It should work with other AI agents, just run Codex or CC inside the terminal.

For more information about Unreal MCP: https://t.co/4nE0GKb8T4
