---
id: "2026-04-17-i-built-an-mcp-server-for-an-ai-character-it-remem-01"
title: "I Built an MCP Server for an AI Character — It Remembers Users"
url: "https://zenn.dev/glasswerks/articles/claude-code-hoo-mcp-server-en"
source: "zenn"
category: "claude-code"
tags: ["CLAUDE-md", "MCP", "AI-agent", "zenn"]
date_published: "2026-04-17"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

## What You'll Get From This Article

* MCP server implementation pattern (Cloudflare Workers + Neon PostgreSQL)
* Tool design for giving an AI character "memory" of users (12 tools and their roles)
* How to control personality at the prompt layer (2-level structure)

## Background: Why an MCP Server for an AI Character?

I develop MUED, a suite of music production tools. There are three products:

* **MUEDear** — Ear training app (measures cognitive profile across 7 games)
* **MUEDnote** — Session log and break timer
* **MUEDial** — AI mixing assistant

And there's a fourth presence that runs across all of them: **Hoo**, an owl AI character.

Hoo started as an in-app chatbot. Its role is to help users think through music production decisions, drawing on their cognitive profile (a 5-dimension score measured in MUEDear).

At some point I wanted to call Hoo from Claude Code as well. During development I'd sometimes need to check "what's this user's cognitive profile again?" or "how would Hoo phrase this?"

MCP lets you pass user context as a tool. Add the MCP server URL to the Claude Code config, and Hoo's data becomes accessible directly.

### Config: wrangler.toml

The Cloudflare Workers project config:

```
name = "hoo-mcp"
main = "src/index.ts"
compatibility_date = "2024-12-01"

[vars]
ALLOWED_ORIGINS = "https://your-domain.com,http://localhost:3000"
MUED_API_URL = "https://your-domain.com"

# Secrets (set via `wrangler secret put`):
# DATABASE_URL — Neon PostgreSQL connection string
# INTERNAL_API_KEY — For Worker → API internal calls
```

Secrets are set via `wrangler secret put DATABASE_URL`. Nothing sensitive appears in code or toml.

## Architecture: 3 Layers

The Hoo MCP server is structured in three layers:

```
[Claude Code / Cursor / AI Tool]
        ↓ JSON-RPC 2.0 (POST /mcp)
[Hoo MCP Server — Cloudflare Workers]
        ↓ Bearer Token → SHA-256 → DB lookup
[Neon PostgreSQL]
        ↓ clerk_id to identify user
[User data: cognitive profile, conversation history, subscription state]
```

### Layer 1: Transport — Streamable HTTP

Standard MCP protocol (JSON-RPC 2.0) over HTTP. Three endpoints only:

```
// POST /mcp — MCP JSON-RPC over HTTP (stateless)
// GET  /    — Health check
// OPTIONS /* — CORS preflight
```

Fully stateless. No SSE or WebSocket. Cloudflare Workers handles each request in isolation — that architecture fits perfectly here.

### Layer 2: Auth — API Key Hash Lookup

MCP-specific API keys with a `mcp_` prefix. Users generate the key from the MUED settings page and paste it into their Claude Code config as a Bearer token.

```
export async function authenticateRequest(
  request: Request,
  sql: SQL,
  _env: Env
): Promise<string | null> {
  const authHeader = request.headers.get("Authorization");
  if (!authHeader?.startsWith("Bearer ")) return null;

  const token = authHeader.slice(7);
  if (!token.startsWith("mcp_")) return null;

  const keyHash = await sha256(token);

  // Look up key hash, join with users to get clerk_id
  const rows = await sql`
    SELECT u.clerk_id, k.id as key_id
    FROM mcp_api_keys k
    JOIN users u ON u.id = k.user_id
    WHERE k.key_hash = ${keyHash} AND k.revoked_at IS NULL
    LIMIT 1
  `;

  if (rows.length === 0) return null;

  // Update last_used_at (fire-and-forget)
  sql`UPDATE mcp_api_keys SET last_used_at = NOW()
      WHERE id = ${rows[0].key_id}`.catch(() => {});

  return rows[0].clerk_id as string;
}
```

Three design decisions here:

1. **Never store the raw API key.** Only the SHA-256 hash goes into the DB. A DB leak can't expose the original key.
2. **`mcp_` prefix signals intent.** No confusion with Clerk JWTs or other tokens.
3. **`last_used_at` is fire-and-forget.** Doesn't slow down auth response.

Once authenticated, `tools/list` returns the tool catalog and `tools/call` executes them:

```
async function handleMcpRequest(
  rpcReq: JsonRpcRequest,
  clerkId: string,
  sql: SQL,
  env: Env
): Promise<JsonRpcResponse> {
  switch (rpcReq.method) {
    case "initialize":
      return jsonRpcResult(rpcReq.id, {
        protocolVersion: "2024-11-05",
        capabilities: { tools: {} },
        serverInfo: { name: "hoo-mcp", version: "1.0.0" },
      });

    case "tools/list":
      return jsonRpcResult(rpcReq.id, { tools: TOOL_DEFINITIONS });

    case "tools/call": {
      const toolName = rpcReq.params?.name;
      const toolArgs = rpcReq.params?.arguments ?? {};
      // dispatch by tool name
    }
  }
}
```

This is the standard MCP pattern: `initialize` returns protocol version and server info, `tools/list` returns the catalog, `tools/call` executes.

Tools are divided into two tiers.

| Tool | What it returns | When to use |
| --- | --- | --- |
| `get_user_profile` | Cognitive scores, custom instructions, musical preferences | Start of conversation |
| `get_conversation_history` | Past Hoo conversations | Context-aware responses |
| `get_hoo_context` | System prompt + user context | When you want the LLM to respond as Hoo |
| `get_muedlobe_profile` | 5-dimension cognitive scores, patterns, game progress | Deep dive on cognitive traits |
| `get_subscription_status` | Subscription state, credit balance | Feature gating decisions |
| `save_conversation` | (write) Save conversation to MUED | After explicit user consent |

| Tool | What it returns |
| --- | --- |
| `get_dial_session_status` | Full mixing session state |
| `get_dial_chat_history` | In-session Hoo conversation history |
| `get_dial_credit_balance` | Subscription + credit pack balance |
| `get_dial_task_details` | Individual task details (preview/production/mastering) |
| `get_dial_phase_and_actions` | Current phase and available actions |

Three reasons not to go with a single `get_everything` tool:

**LLM context efficiency.** Tool responses consume context window. When you only need the cognitive profile, you don't need the full mixing session state too.

**Cost.** Avoids unnecessary DB queries. `get_user_profile` runs 3 queries; `get_hoo_context` runs 5 — but only when called. You pay only for what's needed.

**Permissions.** Tier 2 tools only return meaningful data for MUEDial subscribers. Free-tier users get empty responses from Tier 2 — but the tool descriptions communicate when each tool is relevant, so the LLM makes the right call.

### Implementing `get_user_profile`

Returns cognitive profile, custom instructions, and musical preferences:

```
{
  name: "get_user_profile",
  description:
    "Retrieve the user's cognitive profile (MUEDlobe scores), " +
    "custom instructions, and musical preferences",
  inputSchema: {
    type: "object",
    properties: {},
    required: [],
  },
}
```

Note the empty `inputSchema`. The user is already identified by the `clerkId` from auth — no LLM input needed.

Implementation:

```
export async function getUserProfile(
  sql: SQL,
  clerkId: string
): Promise<ToolResult> {
  const [profileRows, internalId, gamesRows] = await Promise.all([
    sql`SELECT wm_score, ps_score, vc_score, pr_score, att_score,
               significant_patterns, measured_at
        FROM cognitive_profiles WHERE user_id = ${clerkId} LIMIT 1`,
    resolveInternalId(sql, clerkId),
    sql`SELECT DISTINCT game_type
        FROM measurement_history WHERE user_id = ${clerkId}`,
  ]);

  const sections: string[] = ["# User Profile"];

  if (cogProfile) {
    sections.push("\n## Cognitive Profile (MUEDlobe)");
    sections.push(`- **Memory (Working Memory)**: ${cogProfile.wm_score}/100`);
    sections.push(`- **Tempo (Processing Speed)**: ${cogProfile.ps_score}/100`);
    // ... all 5 dimensions
  }

  if (customInstructions) {
    sections.push(`\n## Custom Instructions\n${customInstructions}`);
  }

  if (userProfile?.musical) {
    sections.push("\n## Musical Profile");
    // ... genre, instruments, production style
  }

  return { content: [{ type: "text", text: sections.join("\n") }] };
}
```

Two design decisions:

**Return Markdown, not JSON.** The LLM can forward this directly to the user without transformation. Tables and headings included.

**`Promise.all` for parallel queries.** Cognitive profile, internal ID, and game history have no dependencies — fetch them simultaneously. Neon Serverless creates a new connection per query, so parallelism pays off more than with traditional pooled connections.

### Implementing `get_hoo_context`

The most important tool. Returns Hoo's full system prompt plus user context in one call:

```
{
  name: "get_hoo_context",
  description:
    "Get Hoo's full system prompt and user context. " +
    "The host LLM should use this to respond as Hoo.",
  inputSchema: {
    type: "object",
    properties: {
      include_recent_messages: {
        type: "number",
        description:
          "Number of recent messages to include for " +
          "conversation context (default 10, max 50)",
        default: 10,
      },
    },
    required: [],
  },
}
```

The description says "The host LLM should use this to respond as Hoo." The tool's return value contains Hoo's personality definition — the description tells the LLM what to do with it.

Implementation: combines 3 prompt layers + user context + recent conversation history into one text block:

```
export async function getHooContext(
  sql: SQL,
  clerkId: string,
  params: { include_recent_messages?: number }
): Promise<ToolResult> {
  const [profileRows, internalId] = await Promise.all([
    sql`SELECT wm_score, ps_score, vc_score, pr_score, att_score,
               significant_patterns, prompt_params
        FROM cognitive_profiles WHERE user_id = ${clerkId} LIMIT 1`,
    resolveInternalId(sql, clerkId),
  ]);

  let contextBlock = "";

  if (profileRows.length > 0) {
    const p = profileRows[0];
    contextBlock += `\n\n## User Cognitive Profile
- Working Memory: ${p.wm_score}/100
- Processing Speed: ${p.ps_score}/100
- Verbal Comprehension: ${p.vc_score}/100
- Perceptual Reasoning: ${p.pr_score}/100
- Attention: ${p.att_score}/100`;
  }

  // custom instructions, musical profile, recent conversation...

  const fullPrompt =
    `${HOO_CORE_PROMPT}\n\n---\n\n` +
    `${HOO_EXTENDED_PROMPT}\n\n---\n\n` +
    `${HOO_MCP_MODE_PROMPT}${contextBlock}`;

  return textResult([
    "# Hoo Context",
    "",
    "Use the system prompt below to respond as Hoo.",
    "",
    "---",
    "",
    fullPrompt,
    "",
    "---",
    "",
    "*Respond to the user's next message as Hoo.*",
  ].join("\n"));
}
```

One call delivers everything: personality, conversation rules, user's cognitive traits, recent conversation thread. The LLM becomes Hoo.

### Implementing `save_conversation`

The only write tool. Saves a conversation to MUED after explicit user consent:

```
{
  name: "save_conversation",
  description:
    "Save this conversation to MUED for profile enrichment. " +
    "Only call after the user explicitly consents to saving.",
  inputSchema: {
    type: "object",
    properties: {
      messages: {
        type: "array",
        description: "Array of conversation messages",
        items: {
          type: "object",
          properties: {
            role: { type: "string", enum: ["user", "assistant"] },
            content: { type: "string" },
          },
          required: ["role", "content"],
        },
      },
      title: {
        type: "string",
        description: "Conversation title (auto-generated if omitted)",
      },
    },
    required: ["messages"],
  },
}
```

"Only call after the user explicitly consents" in the description is the key instruction. This tool persists user data — the LLM should never call it without permission.

Key implementation detail: after saving, it automatically triggers memory extraction.

```
export async function saveConversation(
  sql: SQL,
  clerkId: string,
  params: {
    messages: Array<{ role: string; content: string }>;
    title?: string;
  },
  env: { MUED_API_URL: string; INTERNAL_API_KEY: string }
): Promise<ToolResult> {
  if (!params.messages || params.messages.length === 0) {
    return textResult("Error: No messages provided.");
  }

  const internalId = await resolveInternalId(sql, clerkId);
  if (!internalId) return textResult("Error: User not found.");

  const messagesJson = params.messages.map((m) => ({
    role: m.role,
    content: m.content,
    timestamp: new Date().toISOString(),
  }));

  const inserted = await sql`
    INSERT INTO hoo_conversations (
      user_id, title, messages, message_count,
      model, provider, started_at, last_message_at
    ) VALUES (
      ${internalId}, ${params.title || "MCP conversation"},
      ${JSON.stringify(messagesJson)}::jsonb, ${params.messages.length},
      'external-mcp', 'mcp', NOW(), NOW()
    )
    RETURNING id
  `;

  const conversationId = inserted[0].id as string;

  // Auto-trigger memory extraction for conversations with 4+ turns (fire-and-forget)
  if (params.messages.length >= 4 && env.MUED_API_URL && env.INTERNAL_API_KEY) {
    fetch(`${env.MUED_API_URL}/api/hoo/memory/extract`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Internal-API-Key": env.INTERNAL_API_KEY,
      },
      body: JSON.stringify({ conversationId, userId: internalId }),
    }).catch(() => {});
  }

  return textResult(
    `Conversation saved (${params.messages.length} messages). ` +
    `${params.messages.length >= 4
      ? "Auto-memory extraction triggered."
      : "Too few messages for memory extraction (need 4+)."}`
  );
}
```

**Conversations under 4 turns skip memory extraction.** Brief greetings and one-off exchanges rarely yield meaningful memories. The threshold is intentional.

**Memory extraction is fire-and-forget.** The MUED API handles it asynchronously. `catch(() => {})` means failures are silently ignored — memory enrichment is a nice-to-have, not core to the save operation.

## Personality Design: 2 Prompt Levels

Hoo's personality is defined in two layers.

### Level 1: Core Prompt — Hoo's Unchanging Character

```
You are "Hoo", an owl character.
Your role is to help creators think through their work.

## Conversation style

- Fact-based deep diving
- Receive and summarize what the other person says first
- Questions once every 2-3 turns — not every response
- Structure and clarify the points being made
- No unnecessary praise or decoration
- Neutral tone by default; gradually match the other person's style
- Match the language the user writes in

## Watch out for

- Don't barrage with questions. Let the other person lead
- "I see" or "Got it" replies that just acknowledge are fine
- When the other person reaches a conclusion, respect it — add to it, don't redirect

## On "Hohho"

- Use as an interjection when a new insight or question surfaces
- Don't overuse it

## Never do

- Excessive positivity
- Ending with generic advice
- Talking at length about things not asked
```

Level 1 defines *what Hoo is*: an owl, receives before structuring, fact-based, no excessive positivity, "Hohho" as a catchphrase but not a reflex.

The critical element is the explicit "Never do" list. Left to its own defaults, an LLM will over-praise and volunteer unsolicited advice. Without a "never do" list, Hoo's character collapses. This is the same principle from Z3 (hooks article): *behavior you didn't define is a bug*.

### Level 2: Extended Prompt — Conversation Techniques

```
## Techniques for deep dives

### Drawing out thinking
- Show the structure of what the other person said (Before/After, binary oppositions, tables)
- Rephrase to confirm: "So you mean...?"
- Bring in historical examples or analogous cases for comparison
- When the conversation broadens: "Where do you want to go deeper?"

### Organizing the argument
- Separate "what changes / what doesn't"
- Split by time horizon (short / medium / long)
- Use bullet points to improve scanability

### Respect for the other person's domain
- Assume they're the expert in their field
- Don't pretend to know more than you do
- "You probably know this better than I do — can you explain?"
```

Level 2 defines *how Hoo has conversations*: structuring thoughts, organizing arguments, unsticking when stuck.

Level 1 and Level 2 are separated because **they change at different rates**. Level 1 (Hoo's personality) is nearly fixed. Level 2 (conversation techniques) gets updated as we learn what works. Separation means adding a technique to Level 2 doesn't destabilize the core personality in Level 1.

### MCP-Specific Adjustments

App chat and MCP reach users in different states. MCP callers are in the middle of work — writing code, writing a document. So there's an MCP-specific adjustment layer:

```
## MCP Mode (In-Work Assistant)

You are being called via MCP. The person on the other end is working
in Claude Desktop, Cursor, or another AI tool.

### Tone adjustments

- **Brevity first**: They're in the middle of work. Long responses interrupt flow.
- **Conclusion first**: Lead with the point or suggestion; add context only if needed.
- **Keep the core personality**: Fact-based, receive first, no question barrages — these don't change.
- **"Hohho" is fine**: Hoo is still Hoo in MCP mode. Just use it sparingly.
```

"Keep the core personality" is explicitly stated. Optimizing for brevity in MCP mode shouldn't turn Hoo into a plain information API.

## Auth and Deployment

### Why API Keys Instead of JWT

The initial design considered verifying Clerk JWTs directly, but the MCP connection UX pushed toward API keys:

* **JWT approach problem:** The MCP client (Claude Code, Cursor, etc.) would need to implement an OAuth flow. Almost no clients support this yet.
* **API key advantage:** User generates a key from the MUED settings page and pastes it into their client config. Works with any MCP client.

The `mcp_` prefix makes the token's purpose unambiguous.

### Claude Code Config

To use Hoo MCP from Claude Code, add this to `settings.json`:

```
{
  "mcpServers": {
    "hoo": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://your-mcp-server.workers.dev/mcp"],
      "env": {
        "API_KEY": "mcp_your-api-key-here"
      }
    }
  }
}
```

`mcp-remote` is an npm package for connecting to remote MCP servers. It bridges local Claude Code to a Cloudflare Workers deployment.

### Deployment

```
# Set secrets
wrangler secret put DATABASE_URL
wrangler secret put INTERNAL_API_KEY

# Deploy
wrangler deploy
```

Running on Cloudflare Workers free tier. Daily requests are in the tens to hundreds — nowhere near the 100k/day free limit.

## Memory Rules: When Does Hoo Save?

`save_conversation` is the only write tool among the 12. The rules for calling it are strict.

### When to save

Four signals defined in the prompt:

1. **Thanks:** "Thank you," "That helped," "Appreciate it"
2. **Action commitment:** "I'll try that," "Got it," "I'll do it"
3. **Explicit summary request:** "Summarize that," "Log this"
4. **Natural closure:** Conversation winds down without jumping to a new topic

### Always ask first

Hoo asks before calling `save_conversation`. The phrasing is randomized to avoid the same opener every time:

```
Example confirmation phrases (vary by context):
- "Hohho, should I send this to MUED? It could add to your profile."
- "Good thread. Want to save it to MUED?"
- "This feels worth logging — okay to send it over?"
```

### When not to save

* Conversations under 2 turns — don't ask
* If the user declines — don't ask again

This "when to remember / when not to remember" design applies beyond Hoo. Saving everything is easier to implement but feels invasive to users. Saving only meaningful conversations, with explicit consent, is what keeps an AI character trustworthy.

## By the Numbers

| Metric | Value |
| --- | --- |
| MCP tools | 12 (Tier 1: 7 + Tier 2: 5) |
| Prompt layers | 3 (Core + Extended + MCP Mode) |
| Deployment | Cloudflare Workers |
| DB | Neon PostgreSQL (serverless) |
| Auth | API key (SHA-256 hash lookup) |
| Monthly cost | Within Workers free tier + Neon free tier |
| Code volume | ~800 lines across 4 files |

## Design Decision Summary

| Decision | Choice | Reason |
| --- | --- | --- |
| Transport | Streamable HTTP (stateless) | Fits Cloudflare Workers; no SSE needed |
| Auth | API key (SHA-256 hash) | No client-side OAuth needed; universal |
| Tool split | 12 (7 + 5) | Optimized for context efficiency, cost, permissions |
| Return format | Markdown text | LLM can forward directly to user |
| Personality | 3-layer separation (Core / Extended / MCP) | Isolated change frequency; MCP is env delta only |
| Conversation saving | Consent required + 4-turn threshold | Maintains user trust |
| Memory extraction | Fire-and-forget | Save latency unaffected |

The MCP server implementation itself is on the simpler end. Stateless HTTP, Neon queries, return text. The complexity lives in the tool design and prompt design — not the infrastructure.

---

Back to the series: [Z1: Running 10 departments with claude-peers](https://zenn.dev/glasswerks/articles/claude-code-10-agents) | [Z5: Auto memory patterns](https://zenn.dev/glasswerks/articles/claude-code-auto-memory-patterns)
