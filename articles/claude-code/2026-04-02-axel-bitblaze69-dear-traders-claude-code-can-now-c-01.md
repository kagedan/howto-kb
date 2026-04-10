---
id: "2026-04-02-axel-bitblaze69-dear-traders-claude-code-can-now-c-01"
title: "@Axel_bitblaze69: Dear Traders, Claude code can now connect directly to your"
url: "https://x.com/Axel_bitblaze69/status/2039712499503964298"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "x"]
date_published: "2026-04-02"
date_collected: "2026-04-10"
summary_by: "auto-x"
query: "RT @kagedan_k"
---

Dear Traders,

Claude code can now connect directly to your TradingView charts

It reads your charts, indicators, writes Pine Script for your trading strategies, compiles it and fixes errors.. all automatically

Not a browser extension.. A direct connection to your live charting platform

▫️Here's how it works and how to set this up:

> How it works:

TradingView Desktop runs on Electron (Chromium). Chromium has a built in debug interface called Chrome DevTools Protocol. It's off by default. One flag turns it on.

That's the door. Claude Code connects through it via an MCP server running locally on your machine.

Nothing touches TradingView's servers. No data leaves your machine. Everything runs on localhost.

Here's the setup, give Claude code this prompt and it does everything:

"Install the TradingView MCP server. Clone and explore https://t.co/4NApHd4Lyx, run npm install, add to my MCP config at ~/.claude/.mcp.json, and launch TradingView with the debug port."

Once it's done, verify:

"Use tv_health_check to confirm TradingView is connected."

Then just try:

"What's on my chart right now?"

That's the whole setup. Claude installs it. Claude runs it. You just describe what you want.

▫️What Claude can actually see

What Claude can read from your charts:

> Current symbol and timeframe
> Real-time OHLC and volume
> Up to 500 price bars
> All indicator names, IDs, and values
> Pine Script drawings — lines, labels, tables, boxes
> Data window values
> Order book depth
> Strategy tester results and trade list
> Screenshots of any chart region

The most useful part is it reads protected indicators too. 

Pass a filter with the indicator name and you get back every price level, every text annotation, full table contents, every drawn zone.

"What levels is my NY Sessions indicator showing?" 

it reads them.

"What does the session stats table say?" 

it reads that too.All of this data is already on your screen. This tool just makes it readable to an AI.

▫️ The Pine S
