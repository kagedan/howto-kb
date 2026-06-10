---
id: "2026-06-09-running-sysdig-headless-cloud-security-with-claude-01"
title: "Running Sysdig Headless Cloud Security with Claude's ant CLI and Managed Agents"
url: "https://qiita.com/takao-shimizu/items/97652151b2068d9e5b19"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "Python"]
date_published: "2026-06-09"
date_collected: "2026-06-10"
summary_by: "auto-rss"
query: ""
---

> `ant` is the official CLI for calling the Claude API from your terminal; **Managed Agents** runs Claude as an autonomous agent on Anthropic-managed infrastructure. Combine the two and you can run Sysdig's cloud-security workflows *without keeping Claude Code open on your laptop*. This article walks through the whole thing end to end — the big picture, the design, the steps, and the gotchas.

## Introduction — beyond "it works on my machine"

Sysdig publishes its cloud-security expertise as **AI-agent skills** in the [`sysdig/skills`](https://github.com/sysdig/skills) repository: ranking vulnerable images, remediating CVEs, investigating runtime threats — workflows you drive by giving Claude natural-language instructions.

But that repo is designed as a **plugin for Claude Code** (your local CLI / IDE). The default shape is "you open a terminal and work interactively."

Which raises an obvious question:

> **"I want to run vulnerability scans as a nightly batch." "I want investigation tasks to run unattended for tens of minutes to hours." "I want this as a standing team platform." — how do I get that long-running, asynchronous, server-resident usage?**

The answer is **Claude Managed Agents**, and the tool to drive it declaratively is the **`ant` CLI**. This article carefully assembles the "blueprint" and the "runbook" for running Sysdig's skills with this combination, so you never get lost.

By the end you'll have three things:

1. The **precise division of roles** between `ant`, Managed Agents, and Sysdig skills
2. The **mapping mindset** for porting a Claude Code plugin to Managed Agents
3. **Copy-and-run, step-by-step build instructions** (and the honest gotchas)

## Chapter 1 — Meet the three actors

A complex-looking topic gets a lot clearer once you sort out the cast. There are three leads here.

### Actor 1: the `ant` CLI — "the `gh` command for the Claude API"

`ant` is **Anthropic's official CLI for driving the Claude API straight from your terminal**. Every API resource becomes a subcommand: `ant <resource> <action>`.

```bash
brew install anthropics/tap/ant   # macOS
ant --version
```

Unlike hand-writing JSON for `curl`, `ant` gives you:

- **Typed flags or YAML/JSON** to build requests (no hand-written JSON)
- `@path` to inline a file's contents into the body (PDFs auto-base64-encoded)
- `--transform` (GJSON) to extract just the fields you want from a response (no `jq`)
- **Automatic pagination** on list endpoints

Think of it as the "Claude API edition" of the `gh` command for GitHub. You can explore interactively, and drop it straight into shell scripts or CI. Crucially, **Claude Code itself knows how to use `ant`** — ask it to "summarize which of my recent sessions errored out" and it will call `ant` under the hood to find out.

### Actor 2: Managed Agents — "an agent platform you don't have to build"

Normally, building an agent means assembling your own agent loop, tool-execution layer, and secure sandbox. **Managed Agents provides that whole stack as a managed service from Anthropic.** It's built for long-running, asynchronous tasks.

Managed Agents is made of just **four concepts**. Lock these in:

| Concept | What it is | Analogy |
|---|---|---|
| **Agent** | The "definition": model, system prompt, tools, MCP servers, skills | Recipe |
| **Environment** | Where a session runs (cloud, or your own sandbox) | Kitchen |
| **Session** | A "run instance" of an Agent on an Environment | One cooking session |
| **Events** | Messages between your app and the agent (utterances, tool results, state) | Talk in the kitchen |

Inside the sandbox, Claude can autonomously use **bash, file ops, web search/fetch, and MCP connections**. It's a "stateful" design — conversation history and sandbox state persist server-side, and you can pause and resume.

> 📌 **Beta note**: Managed Agents is currently beta (every request needs the `managed-agents-2026-04-01` header; `ant`'s `beta:` prefix adds it automatically). Because it's stateful, it is currently **outside the scope of ZDR / HIPAA BAA**.

### Actor 3: Sysdig Headless Cloud Security — "a cloud-security expertise pack"

[`sysdig/skills`](https://github.com/sysdig/skills) packages Sysdig's runtime-derived security expertise as **skills**. There are seven:

| Skill | Role |
|---|---|
| **sysdig-investigate** | Rank vulnerable images by a risk metric and build a remediation plan |
| **sysdig-onboarding** | Guide AWS account / Kubernetes cluster connection |
| **sysdig-posture** | Author Rego-based custom controls/policies, emit Terraform |
| **sysdig-remediate** | Fix a specific CVE in a container image and open a PR |
| **sysdig-runtime-investigate** | Analyze Falco-detected threats with a confidence score |
| **sysdig-runtime-remediate** | Execute approved runtime response actions |
| **sysdig-sysql** | SysQL query-language reference and debugging |

The repo is, in substance, a **Claude Code plugin**.

```text
skills/
├── .claude-plugin/marketplace.json
├── plugins/headless-cloud-security/
│   ├── .claude-plugin/plugin.json
│   └── skills/<skill-name>/
└── skills/<skill-name>/   ← spec-compliant mirror (the SKILL.md set)
```

And there are **two ways** these skills reach the API — which matters later:

- Via the **hosted Sysdig MCP server** (`https://<region>.app.sysdig.com/mcp/secure`, OAuth auth)
- Via **bundled Python scripts** hitting the Sysdig REST API directly (using env vars `SYSDIG_SECURE_URL` / `SYSDIG_SECURE_API_TOKEN`)

## Chapter 2 — The crux: why you can't "just install it"

This is the single most important realization in the article.

Sysdig's repo is built for Claude Code, to be installed via `/plugin marketplace add` → `/plugin install`. But **Managed Agents reads neither plugins nor marketplaces.**

What Managed Agents understands is exactly these three "parts":

1. **custom skills** (individual skills you upload to your workspace)
2. **MCP servers** (declared in the agent definition, authenticated at session time)
3. **agent_toolset** (bash / files / web — required to run the Python inside a skill)

So the job is: **"take the plugin apart, translate the parts into the Managed Agents vocabulary, and reassemble."** This translation table is the starting point for the whole design.

### 🔁 Translation table: Claude Code plugin → Managed Agents

| Sysdig-side building block | How Claude Code handles it | Managed Agents equivalent |
|---|---|---|
| 7 skills (`skills/<name>/SKILL.md`) | Bulk-installed via `/plugin install` | Uploaded **individually** via `ant beta:skills create`, then attached to the agent under `skills:` |
| Sysdig MCP (`/mcp/secure`) | `claude mcp add ... secure-mcp-server` | Declared in the agent's `mcp_servers` + enabled via `mcp_toolset`. Auth lives in a **vault** |
| `SYSDIG_SECURE_API_TOKEN` (env) | A shell env var | Must be injected into the sandbox (see the verification point below) |
| bash / file ops | Provided by your local environment | Add `agent_toolset_20260401` to tools |

> 💡 **A MECE way to see it**: what a Sysdig skill does decomposes into three things — "① knowledge (the runbook), ② API access, ③ a script-execution environment." Map them one-to-one — ①→skills, ②→MCP (+vault), ③→agent_toolset + environment — and you get no gaps and no overlaps.

## Chapter 3 — The blueprint: the whole picture in one diagram

Once you understand the parts, hold the assembled shape in your head. The whole thing is easier to grasp as **four layers** — "① caller," "② Managed Agents (definitions and the vault)," "③ sandbox execution," and "④ external Sysdig."

<!-- IMAGE ⓪: drag & drop img/architecture-phase1-en.drawio.png right below this line in the Qiita editor -->
*▼ Architecture overview (4 layers: ① Caller / ② Managed Agents / ③ Sandbox execution / ④ External Sysdig)*
![architecture-phase1-en.drawio.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2802819/3aa9c875-a68e-49cd-8ed7-48f1149c596c.png)

#### How to read the diagram (legend)

| Symbol | Meaning |
|---|---|
| solid line | control / invocation flow (who drives whom) |
| thick solid line | the result stream (events / SSE) |
| dashed line | reference / injection (a Session binding its resources, a Vault handing over the key, etc.) |
| 🔐 | secret material (auth). **Separated from the agent definition** |
| 🤖 | the reusable definition (agent). Holds no token |

And the **①②③ correspondence** (same numbers as the Chapter 2 translation table):

| # | Agent component | Role | Phase-1 value |
|---|---|---|---|
| ① | `skills` | Domain knowledge (what it knows) | `sysdig-sysql` (SKILL.md + references/) |
| ② | `mcp_servers` + `vault` | API connection target (②) and its key (②'s key) | `secure-mcp-server` / `static_bearer` token |
| ③ | `tools` | Execution capability (what it can do) | `agent_toolset` + `mcp_toolset(always_allow)` |

The heart of the design is that **"secret material (auth)" is separated from "the reusable definition (agent)"** (the 🔐 and 🤖 in the diagram). The agent definition carries no auth token; the token goes into a **vault** (a per-session-referenced safe). That lets you reuse the same agent **with different auth per user and per environment**, keep the definition under code management (GitOps), and keep secrets in the vault — a clean split of responsibilities.

> 💡 **The data path**: a natural-language instruction makes Claude fire the skill in ③, which calls the Sysdig MCP in ④ via `mcp_toolset`. That traffic is allowed outbound by the **Environment's `allowed_hosts`** and authenticated by the **Vault's Bearer token**. In other words, it's a layered structure where data is reachable only when all three line up: "execution capability (③)," "the route (Environment)," and "the key (Vault)."

## Chapter 4 — Hands-on: build it in six steps

Now the hands-on part. You won't get lost if you keep track of "which row of the translation table" each step implements.

### Step 0: Prepare

```bash
# Authenticate (browser OAuth; for API-key usage, export ANTHROPIC_API_KEY=... works too)
ant auth login
ant auth status        # check which credential / workspace is active

# Get the Sysdig skills
git clone https://github.com/sysdig/skills.git
```

### Step 1: Upload the skills (= row ① of the table)

Upload each SKILL.md directory under `skills/skills/<name>/` as a custom skill. Keep the returned `skill_id`.

All files must live in a single top-level directory, with `SKILL.md` at its root. Upload subdirectories like `references/` too.

> ⚠️ **Per-file `--file` does NOT work (verified on real hardware, 2026-06)**: `ant 1.10.0`'s `--file <path>` truncates the multipart `filename` to its basename, so a skill with subdirectories fails with `400 "SKILL.md file must be exactly in the top-level folder"`. The fix is to **zip the whole folder and pass it as one file** (details in Chapter 5 ②).

```bash
# Zip the skill folder (sysdig-investigate/) as the top-level dir and pass it as one file
cd skills/skills
zip -r /tmp/sysdig-investigate.zip sysdig-investigate

SKILL_INVESTIGATE=$(ant beta:skills create --file /tmp/sysdig-investigate.zip \
  --display-title "Sysdig Investigate" \
  --transform id --raw-output)
rm -f /tmp/sysdig-investigate.zip

# Same idea for sysql / remediate / runtime-investigate, etc.
```

> 📋 **The skill name comes from SKILL.md**: `ant beta:skills create` has no `--name` flag. The name is taken from the SKILL.md frontmatter `name:` field (`--display-title` is a human-facing label and is not included in the prompt).
>
> 📋 **Naming rules**: `name` is lowercase letters, digits, and hyphens only; the reserved words `claude` / `anthropic` are not allowed. Sysdig's names (`sysdig-*`) comply.
>
> 📋 **Cap**: a session allows **20 skills** total. Attach only what you need.

### Step 2: Define the Agent (= binds rows ①②③)

Bring skill attachment, the Sysdig MCP declaration, and the toolset together in one YAML.

```bash
AGENT_ID=$(ant beta:agents create --transform id --raw-output <<YAML
name: Sysdig Cloud Security
model: claude-opus-4-8
system: |
  You are a Sysdig cloud security operator. Use the attached Sysdig skills
  to investigate, prioritize, and remediate cloud risk. Always keep a human
  in the loop before any write or remediation action.
mcp_servers:
  - type: url
    name: sysdig-secure
    url: https://us2.app.sysdig.com/mcp/secure   # ← change to your region
tools:
  - type: agent_toolset_20260401                  # ③ bash etc. Required to run skill Python
  - type: mcp_toolset                              # ② enable the Sysdig MCP
    mcp_server_name: sysdig-secure                 #    must match the name in mcp_servers
skills:                                            # ① knowledge
  - { type: custom, skill_id: $SKILL_INVESTIGATE, version: latest }
  - { type: custom, skill_id: $SKILL_SYSQL,       version: latest }
YAML
)
```

> ⚠️ **Consistency rule**: a server declared in `mcp_servers` must be referenced by an `mcp_toolset` in `tools` (and vice versa). An unreferenced server, or a dangling toolset, makes the API **reject** the agent definition.

### Step 3: Create the Environment (= the foundation for row ③)

There are two environment types; choose based on how the Sysdig skill accesses the API (the why is detailed in Chapter 5 ①).

**(A) `cloud` (Anthropic-managed) — when everything goes through MCP**

A `cloud` environment's `config` consists of just `networking` and `packages` (confirmed in the `ant 1.10.0` API reference). **There is no field for injecting env vars or secrets.** Because this is a security tool, prefer `limited` (scoped to Sysdig's endpoints) over wide-open `unrestricted`.

```bash
ENV_ID=$(ant beta:environments create --transform id --raw-output <<YAML
name: sysdig-env
config:
  type: cloud
  networking:
    type: limited
    allow_mcp_servers: true             # allow traffic to MCP servers declared on the agent
    allowed_hosts:
      - us2.app.sysdig.com              # change to your region
  packages:
    pip: []                             # list any deps the skill's Python needs
YAML
)
```

**(B) `self_hosted` (your own infra) — when Python hits REST directly**

A skill that wants `SYSDIG_SECURE_API_TOKEN` via env cannot do that on `cloud`. In that case create a `self_hosted` environment and run `ant beta:worker` **on your own machine/container**. You fully control the worker's env vars, so you can set the token as an ordinary env var.

```bash
ENV_ID=$(ant beta:environments create --transform id --raw-output <<YAML
name: sysdig-selfhosted
config:
  type: self_hosted
YAML
)

# In another terminal, put the token in env and start the worker
export SYSDIG_SECURE_URL="https://us2.app.sysdig.com"
export SYSDIG_SECURE_API_TOKEN="..."
ant beta:worker --environment-id "$ENV_ID" --environment-key "$ENV_KEY"
```

### Step 4: Prepare the auth vault (= the key for row ②)

Register the Sysdig MCP credentials in a vault. If the server accepts a fixed API token as a Bearer, `static_bearer` is the simplest.

```bash
VAULT_ID=$(ant beta:vaults create \
  --display-name "sysdig-secure" \
  --transform id --raw-output)

ant beta:vaults:credentials create --vault-id "$VAULT_ID" <<YAML
display_name: Sysdig Secure token
auth:
  type: static_bearer
  mcp_server_url: https://us2.app.sysdig.com/mcp/secure   # must exactly match the agent's url
  token: $SYSDIG_SECURE_API_TOKEN
YAML
```

> 🔑 **Exact URL match is everything**: credentials are injected only when `mcp_server_url` and the agent's `url` match **as exact strings** — trailing slash included. If they don't match, the connection is attempted "unauthenticated," and if the server requires auth you'll get a runtime error.
>
> 🔑 **If OAuth is required**: use the `mcp_oauth` type instead of `static_bearer`, registering `access_token` + refresh details (`token_endpoint` / `client_id` / `refresh_token`, etc.). Anthropic auto-refreshes the token on expiry.
>
> 🔒 **Handling secrets**: secret fields like `token` / `access_token` are write-only and never reappear in API responses. The vault is workspace-scoped, so anyone holding an API key in the same workspace can reference it — archive/delete it when no longer needed.

### Step 5: Start a Session and instruct it (= run)

```bash
SESSION_ID=$(ant beta:sessions create \
  --agent "$AGENT_ID" \
  --environment-id "$ENV_ID" \
  --vault-id "$VAULT_ID" \
  --title "Sysdig investigation" \
  --transform id --raw-output)

# Send a user message
ant beta:sessions:events send --session-id "$SESSION_ID" \
  --event '{type: user.message, content: [{type: text, text:
    "Show me the top vulnerable images by actually-exploitable findings and build a remediation plan."}]}'
```

### Step 6: Observe execution (= read the Events)

```bash
# Follow in real time (SSE)
ant beta:sessions:events stream --session-id "$SESSION_ID"

# Read history afterward; extract just the text
ant beta:sessions:events list --session-id "$SESSION_ID" \
  --transform 'content.0.text' --format auto --raw-output
```

Sessions can run for a long time, be interrupted, and resumed. Send another `user.message` to steer mid-flight, or a `user.interrupt` event to stop it.

#### What it looks like in practice (verified on a US East tenant)

Here is the Console while actually running the `sysdig-sysql` skill on `cloud` + a vault (`static_bearer`). From `user.message`, through skill firing (reading SKILL.md) → running the MCP tool `run_sysql` → a table answer with real data, the whole thing flows headlessly.

<!-- IMAGE ①: drag & drop img/t07-1-transcript-overview.png right below this line -->
*▼ Screenshot 1: the full session transcript*
![t07-1-transcript-overview.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2802819/db71ac74-ecfc-4327-a81c-8d15ab83a369.png)

In the end, a natural-language question ("five Kubernetes workloads") is translated into SysQL, and **real environment data** fetched via the Sysdig MCP comes back as a table.

<!-- IMAGE ②: drag & drop img/t07-7-final-answer-table.png right below this line -->
*▼ Screenshot 2: the final answer (a table of real workloads)*
![t07-7-final-answer-table.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2802819/9b08e9c9-dc4a-4aac-8b87-109a5e198125.png)

## Chapter 5 — Gotchas (four of them, honestly)

This is the "no glossing over it" chapter. Here are four points, MECE, that you'll actually hit when you run this.

### ① How to get the Python-script token into the sandbox (verified; conclusion reached)

This was the biggest issue. Checking the `cloud` environment's `config` schema in the `ant 1.10.0` API reference, **the only subfields are `networking` and `packages` — there is no way to inject env vars or secrets.** So the "Python reads `SYSDIG_SECURE_API_TOKEN` from env" pattern is confirmed **impossible** on Anthropic-managed cloud.

The fix is to use the right environment type (see Step 3).

| Skill's API access method | Environment | How to pass the token |
|---|---|---|
| Via Sysdig MCP (investigate / sysql, etc.) | `cloud` is fine | **vault** (`static_bearer` / `mcp_oauth`). No env needed ✅ |
| Python hits REST directly (env required) | **`self_hosted`** | Run `ant beta:worker` yourself; set it in the **worker's env vars** ✅ |

→ **Recommendation**: push anything that can go through MCP onto `cloud` + vault, and split off only the skills that truly need an env token onto a `self_hosted` worker. The practical answer is to keep both environment types in one workspace and route by skill characteristics.

### ② Skill upload format (verified)

`ant beta:skills create` takes files via `--file` (repeatable); there is no `--directory` or `--name` flag, and the skill name comes from the SKILL.md frontmatter. The SKILL.md rules (`name` ≤64 chars, lowercase + symbols only, reserved words `claude`/`anthropic` forbidden; `description` ≤1024 chars) match the official spec.

But there was **one gotcha on real hardware** (verified 2026-06). `ant 1.10.0`'s `--file <path>` **truncates the multipart `filename`
