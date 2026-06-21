---
id: "2026-06-20-kamranmoazim-httpstcol3wchiplv7-01"
title: "@KamranMoazim: https://t.co/L3wChIplV7"
url: "https://x.com/KamranMoazim/status/2068309489867018471"
source: "x"
category: "claude-code"
tags: ["MCP", "AI-agent", "x"]
date_published: "2026-06-20"
date_collected: "2026-06-21"
summary_by: "auto-x"
query: ""Model Context Protocol" tutorial OR "Claude MCP" integration"
---

https://t.co/L3wChIplV7


--- Article ---
On AWS, a plain Lambda *is* the tool - Bedrock AgentCore Gateway speaks the MCP protocol for you. This tutorial walks through the smallest version of that pattern end to end: an MCP your AI agent can use to answer real questions about invoices, with nothing to run between the model and your data except managed AWS services.

## **A quick refresher on MCP**

> The Model Context Protocol is how an AI client (Claude.ai, an agent, an IDE) discovers and calls tools. The client asks an MCP server "what can you do?" (`tools/list`), gets back a list of named tools with JSON schemas, and then calls one (`**tools/call**`) with arguments. Normally ***y*ou** write and host that server. The whole point of this build is that you don't - AgentCore Gateway is the server, and it forwards each call to a Lambda.

## **What I built**

An MCP tool that answers questions like **"what did Acme (Customer) owe us in March?"** by calling a single Lambda backed by DynamoDB. No MCP server code anywhere. Any MCP client can connect to it - Claude.ai, MCP Inspector, an AgentCore agent or any standard MCP client.

## Why it matters

The usual way to give an agent a tool is to stand up an MCP server: a long-running process with its own host, its own auth, its own deployment. That's infrastructure you now own and operate, just to expose a few functions.

This pattern deletes that server. The Lambda is the tool. AgentCore Gateway sits in front and handles the entire MCP surface - the tools/list response, the tools/call routing, the protocol handshake, and the auth check. You write two things: the business logic (a Lambda) and the contract (a JSON schema). Everything else is managed.

The operational payoff is real. There's nothing running when no one's calling, so idle cost is zero. Lambda and DynamoDB on-demand both bill per request, so a low-traffic tool costs cents (with the AWS free tier, often zero). Auth is Cognito, so the same JWT-based access control
