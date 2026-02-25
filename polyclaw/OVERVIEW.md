# Polyclaw -- Complete Technical Overview

> **Document generated**: 2025-02-25
> **Source repository**: [aymenfurter/polyclaw](https://github.com/aymenfurter/polyclaw) (cloned at `polyclaw-repo/`)
> **Version**: 5.0.0 | **License**: MIT | **Python**: 3.11+ | **Stack**: aiohttp + React/Vite + Docker

---

## Table of Contents

1. [What Is Polyclaw](#1-what-is-polyclaw)
2. [Architecture -- How It Works](#2-architecture----how-it-works)
3. [Core Capabilities](#3-core-capabilities)
4. [Skills and Plugins](#4-skills-and-plugins)
5. [Resource Connections](#5-resource-connections)
6. [Connecting to Copilot Models](#6-connecting-to-copilot-models)
7. [Security Assessment](#7-security-assessment)
8. [How to Use Polyclaw](#8-how-to-use-polyclaw)
9. [Environment Variables Reference](#9-environment-variables-reference)
10. [Key Files Reference](#10-key-files-reference)

---

## 1. What Is Polyclaw

Polyclaw is a **self-hosted, autonomous AI assistant** (self-described as "Jarvis to Tony Stark")
built on top of the **GitHub Copilot SDK**. It runs as a persistent Python (aiohttp) server inside
Docker containers, with a React-based admin dashboard, and connects to users through multiple
channels: web chat, Telegram, Teams/Slack/LINE (via Azure Bot Service), and phone calls (via Azure
Communication Services + OpenAI Realtime API).

The core idea: take the full power of GitHub Copilot -- code generation, tool use, reasoning --
and untether it from the IDE. Polyclaw writes code, manages repos via the GitHub CLI, authors its
own skills at runtime, schedules tasks, proactively reaches out, and can even call you on the phone
for urgent matters.

---

## 2. Architecture -- How It Works

### 2.1 Container Topology

Polyclaw runs as **two Docker containers** orchestrated by `docker-compose.yml`:

| Container | Port | Purpose | Access Level |
|-----------|------|---------|--------------|
| **Admin** | 9090 | Admin dashboard, config, deployment | Has `docker.sock`, Key Vault, Azure CLI auth, admin-home volume |
| **Runtime** | 3978 (external) / 8080 (internal) | Agent execution, bot messaging, voice | NO admin-home, NO docker.sock -- fully isolated |

They share a `polyclaw-data` volume at `/data` for persistent state (memory, sessions, skills,
media). The runtime container depends on admin being healthy.

### 2.2 Docker Image

Two-stage build in the `Dockerfile`:

| Stage | Base Image | What It Produces |
|-------|------------|-----------------|
| **Frontend** | `node:22-slim` | Compiled React/Vite dashboard |
| **Runtime** | `python:3.12-slim` | Full agent runtime with all tools |

Bundled tools inside the image:
- GitHub Copilot CLI (`@github/copilot@0.0.405`)
- GitHub CLI (`gh`)
- Azure CLI (`az`)
- Docker CLI (client only, no daemon)
- Cloudflare tunnel (`cloudflared`)
- Playwright MCP + Chromium (headless browser)
- Node.js 22

### 2.3 Core Agent Loop

1. **`Agent` class** (`agent/agent.py`, 501 lines) wraps a `CopilotClient` from the
   `github-copilot-sdk` Python package
2. On `start()`: creates CopilotClient with a GitHub token, retries 3x, verifies auth via
   `client.get_auth_status()`, confirms model availability via `client.list_models()`, starts
   a stderr monitor thread
3. On `send(prompt)`: auto-creates a session if none exists, wraps the call in an OpenTelemetry
   span, sends with a 360-second timeout, tracks request counts per model, handles session expiry
   with auto-recreation
4. The **session config** includes: model, streaming=True, custom tools, system_message (replace
   mode), hooks (chained HITL + sandbox), skill directories, MCP servers, and excluded tools
   when sandbox is active

### 2.4 Event Handling

`EventHandler` (`agent/event_handler.py`, 188 lines) uses a dispatch table pattern for Copilot SDK
session events:

| Event | Handler |
|-------|---------|
| `ASSISTANT_MESSAGE_DELTA` | Streaming text chunks to client |
| `ASSISTANT_MESSAGE` | Final response + token usage extraction |
| `TOOL_EXECUTION_START/COMPLETE/PROGRESS` | Tool lifecycle with deduplication |
| `ASSISTANT_REASONING_DELTA` | Reasoning chain visibility |
| `SKILL_INVOKED` | Tracks skill usage in agent profile |
| `SUBAGENT_STARTED/COMPLETED` | Sub-agent orchestration events |
| `SESSION_IDLE` / `SESSION_ERROR` | Session lifecycle termination |

### 2.5 System Prompt Construction

`build_system_prompt()` in `agent/prompt.py` assembles a multi-layered prompt from:

1. **SOUL.md** -- agent's self-written identity (name, personality, backstory)
2. **Operating manual** (`system_prompt.md`, ~546 lines) -- core behavior rules, memory procedures,
   tool usage patterns, formatting, autonomy philosophy
3. **MCP server guidance** -- lists enabled MCP servers with usage instructions
4. **Sandbox section** -- when sandboxed, switches to terminal-only mode
5. **Profile state** -- emotional_state, name, location, preferences injected as context

### 2.6 Server and Middleware Stack

`AppFactory` (`server/app.py`, 541 lines) assembles the aiohttp application with three security
middlewares applied in order:

1. **Lockdown middleware** -- blocks admin panel access when `LOCKDOWN_MODE` is active
2. **Tunnel restriction middleware** -- blocks non-bot endpoints for requests arriving through
   Cloudflare tunnel (detected via `cf-*` headers)
3. **Auth middleware** -- Bearer token validation on `/api/*` using `hmac.compare_digest`,
   supports query param fallback (`?token=` / `?secret=`)

### 2.7 API Surface

The admin server exposes **22 route modules** covering:

| Route Group | Endpoints |
|-------------|-----------|
| Chat/Agent | Chat interface, session management |
| Guardrails | HITL config, per-tool/per-model policies, presets, YAML import/export |
| Skills | Marketplace browse, install/remove, contribute |
| Plugins | Enable/disable, setup wizard, ZIP import |
| MCP | Server CRUD, enable/disable, GitHub registry lookup |
| Scheduling | Cron-based task CRUD |
| Profile | Agent identity/personality editor |
| Identity | Runtime identity inspection, RBAC verification |
| Monitoring | OpenTelemetry/App Insights config, provisioning |
| Network | Topology, endpoint catalog, connectivity probes, resource audits |
| Deployment | ACA deployer, environments, resource cleanup |
| Security | Content Safety provisioning, Prompt Shield testing, preflight checks |
| Sandbox | ACA Dynamic Sessions config, testing |
| Foundry IQ | AI Search + Embeddings provisioning, indexing, search |
| Tool Activity | Audit log with filtering, flagging, timeline, export/import |
| Proactive | Follow-up preferences, dry-run, memory formation |

### 2.8 Background Agents

Polyclaw runs **six background agent contexts**, each with independent guardrails:

| Agent | Purpose | Has Tools |
|-------|---------|-----------|
| **Scheduler** | Cron-based scheduled tasks | Yes (full tool access) |
| **Bot Processor** | Telegram/Teams message handling | Yes (full tool access) |
| **Proactive Loop** | Proactive follow-up messages | No |
| **Memory Formation** | Post-conversation memory consolidation | No |
| **AITL Reviewer** | AI-based tool call review | Yes (submit_decision only) |
| **Realtime Voice Agent** | Voice call tool execution | Yes |

---

## 3. Core Capabilities

### 3.1 Chat and Messaging

- Interactive conversation through web UI, Telegram, Teams, Slack, LINE, Email
- Bot Framework integration via Azure Bot Service
- Telegram whitelist authorization
- Proactive messaging with reaction tracking and adaptive timing
- Rich cards: Adaptive Cards, Hero Cards, Thumbnail Cards, Carousels
- Media handling: incoming downloads, outgoing attachments with error recovery

### 3.2 Code Execution

- Full terminal/file access via Copilot SDK tools: `create`, `edit`, `view`, `grep`, `glob`,
  `run`, `bash`
- Optional sandbox execution via Azure Container Apps Dynamic Sessions
- Sandbox provides isolated environment with data upload/download, bootstrap scripts,
  100MB max zip size, whitelisted file sync

### 3.3 Scheduling

- Cron-based task scheduler with `croniter`, minimum 1-hour intervals
- Persistent JSON store at `scheduler.json`
- One-shot sessions with `gpt-4.1` as the default scheduled model
- Background HITL hooks with `execution_context="scheduler"`
- 60-second check loop

### 3.4 Voice Calls

- Outbound/inbound phone calls via Azure Communication Services
- OpenAI Realtime API for live voice conversation (bidirectional WebSocket, PCM 24K mono)
- Three voice tools: `invoke_agent` (sync), `invoke_agent_async`, `check_agent_task`
- Cloudflare tunnel provides HTTPS callback + WSS media streaming URLs
- Realtime middleware bridges ACS audio format to OpenAI Realtime format

### 3.5 Memory System

- File-based persistent memory with daily logs and topic notes
- Idle timer (default 5 minutes) triggers memory formation via a lighter model
- Memory formation agent consolidates transcripts into: daily logs, topic notes,
  emotional state, skill usage counts, profile preferences, sample queries
- Proactive follow-up processing with history context and reaction tracking
- Optional Foundry IQ: indexes memories into Azure AI Search for semantic recall

### 3.6 Sub-Agents

- `run_one_shot()` spawns ephemeral CopilotClient sessions with custom model/tools/prompt
- Used by: scheduler (`gpt-4.1`), memory formation (`MEMORY_MODEL`), AITL reviewer (`gpt-4.1`),
  realtime voice agent (`COPILOT_MODEL`)

### 3.7 Self-Extension

- The agent can create new skills at runtime (stored as markdown instruction files)
- Skills are loaded from both built-in and user directories
- Remote catalog fetches community skills from GitHub repositories

---

## 4. Skills and Plugins

### 4.1 Built-in Skills

| Skill | Verb | Description |
|-------|------|-------------|
| **daily-briefing** | `brief` | Morning briefing from daily logs, pending items, active topics |
| **note-taking** | `note` | Full CRUD for personal markdown notes with categories |
| **summarize-url** | `summarize` | Uses Playwright MCP to extract and summarize web page content |
| **web-search** | `search` | Google/DuckDuckGo search via Playwright MCP |

### 4.2 Plugins

| Plugin | Skills Included | Description |
|--------|----------------|-------------|
| **Microsoft Foundry Agents** | setup-foundry, foundry-agent-chat, foundry-code-interpreter | Azure AI Foundry: provisioning, ad-hoc agents, code interpreter |
| **GitHub Status Monitor** | gh-status-check, gh-incidents, gh-maintenance | GitHub infrastructure monitoring |
| **Second Brain / WorkIQ** | daily-rollover, end-day, weekly-review, monthly-review | M365-powered productivity reviews |
| **Wikipedia Lookup** | setup-wikipedia, wiki-search, wiki-summary, wiki-deep-dive | Wikipedia search and exploration |

### 4.3 Skill/Plugin Loading

- **Skills registry** (`registries/skills.py`): Scans directories, reads `SKILL.md` files,
  parses YAML frontmatter (name, description, verb). User skills override built-ins.
- **Plugin registry** (`registries/plugins.py`): Scans for `PLUGIN.json` manifests. Enable copies
  skill directories into user dir; disable removes them. Supports setup wizards and ZIP import.
- **Remote catalog** (`registries/catalog.py`): Fetches community skills from GitHub repos
  (`github/awesome-copilot`) with rate limiting and commit-count enrichment.

### 4.4 MCP Server Integration

| MCP Server | Risk Level | Purpose |
|------------|-----------|---------|
| **Playwright** | Medium | Browser automation for web search and content extraction |
| **Microsoft Learn** | Low | Read-only access to Microsoft documentation |
| **GitHub MCP Server** | High | Repository, PR, issue, and code management |
| **Azure MCP Server** | High | Azure resource creation and management |

---

## 5. Resource Connections

### 5.1 GitHub Copilot SDK (Primary AI Backend)

| Item | Detail |
|------|--------|
| **Package** | `github-copilot-sdk>=0.1.23` (PyPI) |
| **Authentication** | `GITHUB_TOKEN` env var or `gh auth` CLI state |
| **Client** | `CopilotClient` from `copilot` package |
| **CLI** | `@github/copilot@0.0.405` (npm global) |
| **Auth verification** | `client.get_auth_status()` on startup |
| **Model discovery** | `client.list_models()` returns available models with metadata |

### 5.2 Azure Services

| Service | Connection Method | Purpose |
|---------|------------------|---------|
| **Key Vault** | `DefaultAzureCredential` | Secret storage via `@kv:secret-name` pattern. Auto IP allowlisting. RBAC retry with backoff |
| **Bot Service** | `BOT_APP_ID` / `BOT_APP_PASSWORD` / `BOT_TENANT_ID` | Multi-channel messaging (Telegram, Teams, Slack, LINE, Email) |
| **Communication Services** | `ACS_CONNECTION_STRING` | Phone call automation with media streaming |
| **Azure OpenAI** | Endpoint + API key or `DefaultAzureCredential` | Realtime voice model via WebSocket proxy |
| **Container Apps** | Managed Identity or Service Principal | Runtime deployment + Dynamic Sessions (sandbox) |
| **AI Content Safety** | `DefaultAzureCredential` (Entra ID only) | Prompt Shield injection detection |
| **Container Registry** | Admin credentials via `az acr credential show` | Docker image storage for ACA deployment |
| **Azure Monitor** | `APPINSIGHTS_CONNECTION_STRING` | OpenTelemetry traces, metrics, and logs |
| **AI Search** (Foundry IQ) | API endpoint + key | Semantic memory search and embedding indexing |

### 5.3 Cloudflare Tunnel

- `CloudflareTunnel` class spawns `cloudflared tunnel --url` as a subprocess
- Parses the tunnel URL from stderr (regex for `*.trycloudflare.com`)
- Provides HTTPS/WSS endpoints for Bot Service webhooks and ACS media streaming
- Tunnel restriction middleware blocks non-bot endpoints from tunnel traffic

### 5.4 Azure CLI Wrapper

`AzureCLI` class (`services/cloud/azure.py`, 307 lines):
- Cached JSON queries with 30-second TTL
- Heartbeat logging for long-running commands
- 1200-second timeout with process kill
- Device code login flow for interactive auth
- Bot endpoint management, Telegram token validation with retries

---

## 6. Connecting to Copilot Models

### 6.1 Model Configuration

The primary model is set via the `COPILOT_MODEL` environment variable:

```
COPILOT_MODEL=claude-sonnet-4.6    # default
```

Other model slots:

| Context | Model | Variable/Constant |
|---------|-------|------------------|
| Primary agent | `claude-sonnet-4.6` | `COPILOT_MODEL` env var |
| Memory formation | Same as primary | `MEMORY_MODEL` env var |
| Scheduler | `gpt-4.1` | `SCHEDULED_MODEL` constant |
| AITL Reviewer | `gpt-4.1` | Hardcoded default |
| Realtime one-shot | `gpt-4.1` | `_REALTIME_MODEL` constant |
| Realtime voice | Azure OpenAI deployment | `AZURE_OPENAI_ENDPOINT` |

### 6.2 Available Models (Risk Tiers)

| Tier | Label | Models | Default Preset |
|------|-------|--------|---------------|
| 1 | Strong | `gpt-5.3-codex`, `claude-opus-4.6`, `claude-opus-4.6-fast` | Permissive |
| 2 | Standard | `claude-sonnet-4.6`, `gpt-5.2`, `gemini-3-pro-preview` | Balanced |
| 3 | Cautious | `gpt-5-mini`, `gpt-4.1` | Restrictive |

### 6.3 Authentication Flow

1. Set `GITHUB_TOKEN` in the `.env` file (or authenticate via `gh auth login`)
2. `Agent.start()` passes the token to `CopilotClient({"github_token": token})`
3. The client starts and authenticates against the GitHub Copilot API
4. Auth verified via `client.get_auth_status()` -- checks for Copilot access
5. Model availability confirmed via `client.list_models()` -- returns model metadata including
   billing multipliers and reasoning effort levels

### 6.4 Runtime Model Switching

- **Slash command**: `/model <model-name>` in chat
- **Admin dashboard**: Model selector in the web UI
- **API**: `GET /api/models` lists available models with guardrail policy state
- Each model has a security tier that determines its default guardrails preset

### 6.5 Voice Model Connection

For realtime voice calls, configure:

```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your-key   # or use DefaultAzureCredential
```

The `RealtimeMiddleTier` proxy bridges ACS WebSocket audio to the Azure OpenAI Realtime API
(`api-version=2025-04-01-preview`).

---

## 7. Security Assessment

### 7.1 Authentication and Authorization

**Strengths:**
- Admin API uses `hmac.compare_digest` for timing-safe token comparison (prevents timing attacks)
- Three-layer middleware chain: lockdown -> tunnel restriction -> auth
- Azure services use `DefaultAzureCredential` (Entra ID) -- no API key leakage to the
  runtime container
- Telegram whitelist authorization blocks unauthorized users
- Key Vault secrets use `@kv:` prefix pattern -- secrets never stored in plaintext once
  KV is configured
- Container isolation: runtime has NO `docker.sock`, NO admin-home volume, separate
  Azure CLI config directories

**Concerns:**
- Auth middleware supports query parameter tokens (`?token=` / `?secret=`) -- can leak into
  server access logs, browser history, and referrer headers
- `ADMIN_SECRET` is the single credential protecting the entire admin surface -- no MFA,
  no session expiry
- `GITHUB_TOKEN` provides broad Copilot access -- if compromised, all model access is exposed
- Bot credentials (`BOT_APP_PASSWORD`) stored in `.env`; Key Vault helps but requires
  initial bootstrap with plaintext

### 7.2 Prompt Injection Defense

**Strengths:**
- **Spotlighting / Data Marking** (`util/spotlight.py`): Implements the Microsoft Research
  technique (arXiv:2403.14720) -- replaces whitespace in untrusted content with `^` sentinel
  characters and wraps in `<<<UNTRUSTED_CONTENT>>>` boundary tags
- **AITL Reviewer** (`agent/aitl.py`, 267 lines): A separate Copilot session that reviews
  tool calls for prompt injection, data exfiltration, destructive actions, and privilege
  escalation before execution
- **Azure Prompt Shield** (`services/security/prompt_shield.py`): Azure AI Content Safety
  integration for server-side injection detection
- AITL reviewer uses spotlighting on its own inputs -- defense-in-depth against meta-injection

**Concerns:**
- Spotlighting is a heuristic defense -- sophisticated attacks may bypass it
- AITL reviewer 30-second timeout results in denial (safe default, but may block legitimate calls)
- Prompt Shield silently skips if endpoint not configured (graceful degradation, no protection)
- AITL reviewer shares the same model ecosystem -- model-level vulnerability affects both
  agent and reviewer

### 7.3 Guardrails System

**Strengths:**
- **Granular policy matrix**: Per-tool, per-model, per-context
  (interactive/background/scheduler/realtime) strategy assignment
- **Six strategies**: `allow`, `deny`, `hitl` (human approval), `aitl` (AI review),
  `pitl` (phone verification), `filter` (content safety)
- **Risk classification**: Every tool, MCP server, and skill classified as low/medium/high risk
- **Model tiering**: Three tiers (1=strong/permissive, 2=standard/balanced, 3=cautious/restrictive)
- **Preset system**: Restrictive, Balanced, Permissive -- with cross-reference tables adjusting
  per-model policies
- **YAML policy export/import**: Human-readable policy files via `agent-policy-guard`

**Concerns:**
- `report_intent` is in `_ALWAYS_APPROVED_TOOLS` -- bypasses all guardrails
- Default fallback is `auto_approve` when neither HITL nor sandbox hooks are active
- The `allow` strategy completely bypasses all checks including content safety

### 7.4 Code Execution and Sandbox

**Strengths:**
- Sandbox executor uses Azure Container Apps Dynamic Sessions for isolated execution
- File sync whitelist limits transferable file types
- 100MB max zip size for data transfers
- Bootstrap isolation: code runs in a separate ACA session with its own credential scope

**Concerns:**
- Main agent has full terminal access (`run`, `bash`) outside sandbox -- sandbox is optional,
  not default
- Sandbox credential acquisition inherits Azure credentials (`DefaultAzureCredential`)
- The Copilot SDK itself grants file system, terminal, and browser tools by default

### 7.5 Secret Management

**Strengths:**
- Key Vault integration with auto IP allowlisting on firewall errors
- RBAC retry with exponential backoff (4 attempts)
- `cfg.write_env()` auto-stores secrets in Key Vault when enabled
- `entrypoint.sh` sets separate `AZURE_CONFIG_DIR` per container mode
- Security preflight checks verify: identity existence, RBAC roles, credential isolation,
  no elevated roles, scope containment

**Concerns:**
- Bootstrap requires some plaintext secrets before Key Vault is configured
- Auto IP allowlisting modifies Key Vault firewall rules automatically
- Infrastructure identifiers stored in `.env` file

### 7.6 Network and Deployment Security

**Strengths:**
- Container isolation: runtime has no docker.sock access
- IP whitelisting for ACA ingress
- Azure resource security auditing (storage, Key Vault, ACR network configs)
- Tunnel restriction middleware prevents admin access through Cloudflare tunnel
- Lockdown mode completely blocks admin panel

**Concerns:**
- Cloudflare quick-tunnel (`trycloudflare.com`) creates a publicly accessible endpoint
- Admin container has `docker.sock` access -- full Docker daemon control
- ACR uses admin credentials for image push (managed identity preferable)
- No TLS termination within containers -- relies on external proxy

### 7.7 Data Privacy

**Strengths:**
- File-based memory is local -- no external storage by default
- Session archival with configurable retention (24h, 7d, 30d, never)
- Tool activity audit log with flagging and export

**Concerns:**
- Conversations, memories, and profile stored as plain JSON/text -- no encryption at rest
- Memory formation sends transcripts to models for processing
- Conversation references (channel IDs, user IDs, service URLs) stored in plain JSON

### 7.8 Overall Security Rating

| Category | Rating | Notes |
|----------|--------|-------|
| Authentication | Good | Timing-safe comparison, Entra ID, container isolation |
| Authorization | Good | Granular guardrails, model tiering, risk classification |
| Prompt Injection | Strong | Three-layer defense: Spotlighting + AITL + Prompt Shield |
| Secret Management | Good | Key Vault with auto-rotation support |
| Network Security | Moderate | Cloudflare tunnel publicly accessible; admin has docker.sock |
| Data Privacy | Moderate | Local storage but no encryption at rest |
| Code Execution | Moderate | Sandbox available but not default |
| Audit and Compliance | Good | Comprehensive audit log, preflight checks, YAML export |

---

## 8. How to Use Polyclaw

Polyclaw is built on the **GitHub Copilot SDK** -- the same engine that powers GitHub Copilot in
VS Code and the Copilot CLI. This means Polyclaw is essentially a way to run Copilot in an
autonomous, persistent, multi-channel mode. Here is how you can use it.

### 8.1 Prerequisite: GitHub Copilot Subscription

All paths require a **GitHub account with a Copilot subscription** (Individual, Business, or
Enterprise). The Copilot SDK authenticates via your GitHub token.

### 8.2 Option A: Run Polyclaw via Docker (Full Platform)

This is the primary intended usage -- running the full Polyclaw stack locally via Docker.

**Requirements:**
- Docker Desktop (or Docker Engine + Compose)
- Bun (for the TUI launcher)
- Git

**Steps:**

```bash
# 1. Clone the repository
git clone https://github.com/aymenfurter/polyclaw.git
cd polyclaw

# 2. Install Bun (if not already installed)
# Windows (PowerShell):
powershell -c "irm bun.sh/install.ps1 | iex"
# macOS/Linux:
curl -fsSL https://bun.sh/install | bash

# 3. Launch the TUI
./scripts/run-tui.sh
```

The TUI will:
1. Build the Docker image (includes all dependencies)
2. Start admin + runtime containers via `docker compose`
3. Walk you through GitHub authentication
4. Drop you into an interactive dashboard

**What you get:**
- Web dashboard at `http://localhost:9090`
- Interactive chat via TUI or web
- Bot Framework webhooks via Cloudflare tunnel
- Scheduler, memory, skills, plugins -- all running

### 8.3 Option B: Use the GitHub Copilot SDK Directly (VS Code / Python)

The Copilot SDK that Polyclaw wraps is independently usable. You do NOT need Polyclaw to use the
SDK -- you can build your own agents in VS Code.

#### Install the SDK

```bash
pip install github-copilot-sdk
```

#### Authenticate

Set a `GITHUB_TOKEN` environment variable with a GitHub PAT that has Copilot access, or
authenticate via the GitHub CLI:

```bash
gh auth login
```

#### Basic Usage in Python (VS Code)

```python
import asyncio
from copilot import CopilotClient

async def main():
    # Create a client (uses GITHUB_TOKEN or gh auth state)
    client = CopilotClient()
    await client.start()

    # Create a session with a model
    session = await client.create_session({
        "model": "claude-sonnet-4.6",   # or gpt-4.1, etc.
        "streaming": True,
    })

    # Send a message
    await session.send({"prompt": "Explain the Copilot SDK architecture"})

    # Wait for response via event handler
    # (see copilot-sdk-exploration/ for full examples)

    await client.stop()

asyncio.run(main())
```

#### With Custom Tools

```python
from copilot import CopilotClient, define_tool
from pydantic import BaseModel, Field

class SearchParams(BaseModel):
    query: str = Field(description="Search query")

@define_tool(description="Search the web")
def search_web(params: SearchParams) -> str:
    # Your implementation
    return f"Results for: {params.query}"

session = await client.create_session({
    "model": "claude-sonnet-4.6",
    "tools": [search_web],
    "streaming": True,
})
```

#### With MCP Servers

```python
session = await client.create_session({
    "model": "claude-sonnet-4.6",
    "mcp_servers": [
        {
            "name": "playwright",
            "command": "npx",
            "args": ["@playwright/mcp@latest"],
        }
    ],
})
```

#### With Skills

```python
session = await client.create_session({
    "model": "claude-sonnet-4.6",
    "skill_dirs": ["./my-skills/"],   # Directory of SKILL.md files
})
```

> **Tip**: The `copilot-sdk-exploration/` folder in this repo has detailed examples
> and the full SDK summary.

### 8.4 Option C: GitHub Copilot CLI

The Copilot CLI (`@github/copilot`) is the underlying binary that the Copilot SDK delegates to.
You can use it directly from any terminal.

#### Install

```bash
npm install -g @github/copilot
```

#### Authenticate

```bash
gh auth login
```

#### Usage

```bash
# Interactive chat session
copilot chat

# Ask a question directly
copilot "explain how kubernetes pods work"

# With a specific model
copilot --model claude-sonnet-4.6 "write a Python fibonacci function"
```

The Copilot CLI gives you IDE-quality code assistance in any terminal -- no VS Code required.
Polyclaw essentially wraps this CLI in a persistent server with memory, scheduling, and
multi-channel access.

### 8.5 Option D: Use Copilot in VS Code (Standard)

The most familiar path -- GitHub Copilot is already built into VS Code:

1. Install the **GitHub Copilot** and **GitHub Copilot Chat** extensions
2. Sign in with your GitHub account
3. Use inline suggestions, chat panel, or the terminal

**How Polyclaw relates to VS Code Copilot:**
- VS Code Copilot is session-based -- it helps while you are actively coding
- Polyclaw is persistent and autonomous -- it runs in the background, schedules tasks,
  messages you proactively, and remembers across sessions
- Both use the same underlying Copilot SDK and models
- VS Code Copilot uses the same models listed in Section 6.2

### 8.6 Option E: Study the Codebase as a Reference Architecture

Even without running Polyclaw, the codebase is a comprehensive reference for:

| What to Learn | Where to Look |
|---------------|---------------|
| Copilot SDK integration | `agent/agent.py`, `agent/one_shot.py` |
| Custom tool definitions | `agent/tools/` |
| HITL/AITL guardrails | `agent/hitl.py`, `agent/aitl.py` |
| Prompt engineering | `templates/system_prompt.md`, `templates/memory_prompt.md` |
| Multi-channel bots | `messaging/bot.py`, `messaging/proactive.py` |
| Azure service integration | `services/cloud/azure.py`, `services/keyvault.py` |
| Voice/realtime AI | `realtime/middleware.py`, `realtime/caller.py` |
| Sandbox execution | `sandbox/executor.py` |
| Skill/plugin architecture | `registries/skills.py`, `registries/plugins.py` |
| Security patterns | `services/security/`, `util/spotlight.py` |
| OpenTelemetry setup | `services/otel.py` |
| Docker multi-container | `docker-compose.yml`, `Dockerfile`, `entrypoint.sh` |

### 8.7 Practical Learning Path

Given your workspace structure, here is a recommended progression:

```
1. copilot-sdk-exploration/    -- Understand the SDK basics
2. workplace_docs/             -- Build a simple Copilot app
3. kusto_app/                  -- Apply to real data scenarios
4. polyclaw/                   -- Study the full autonomous agent architecture
5. microsoft-agent-framework/  -- Compare with Microsoft's Agent Framework
```

**For Polyclaw specifically:**
1. Read `polyclaw-repo/docs/content/getting-started/quickstart.md`
2. Study `agent/agent.py` to see how CopilotClient is wrapped
3. Look at `agent/tools/` to see how `@define_tool` works
4. Examine `templates/system_prompt.md` for prompt engineering patterns
5. Review `agent/hitl.py` and `agent/aitl.py` for guardrails patterns
6. Optionally run the full stack via Docker to see it all in action

---

## 9. Environment Variables Reference

| Variable | Default | Purpose |
|----------|---------|---------|
| `GITHUB_TOKEN` | -- | GitHub Copilot SDK authentication |
| `COPILOT_MODEL` | `claude-sonnet-4.6` | Primary AI model |
| `MEMORY_MODEL` | same as COPILOT_MODEL | Model for memory formation |
| `ADMIN_SECRET` | -- | Admin API authentication token |
| `BOT_APP_ID` | -- | Azure Bot Service app ID |
| `BOT_APP_PASSWORD` | -- | Azure Bot Service app password |
| `BOT_TENANT_ID` | -- | Azure Bot Service tenant |
| `ACS_CONNECTION_STRING` | -- | Azure Communication Services |
| `AZURE_OPENAI_ENDPOINT` | -- | Realtime voice model endpoint |
| `AZURE_OPENAI_API_KEY` | -- | Realtime voice model key |
| `KEY_VAULT_NAME` | -- | Azure Key Vault name |
| `MEMORY_IDLE_MINUTES` | `5` | Idle time before memory consolidation |
| `LOCKDOWN_MODE` | `false` | Disable admin panel |
| `TUNNEL_RESTRICTED` | `false` | Block non-bot tunnel traffic |
| `TELEGRAM_WHITELIST` | -- | Comma-separated allowed Telegram user IDs |
| `APPINSIGHTS_CONNECTION_STRING` | -- | Azure Monitor telemetry |
| `RUNTIME_SP_APP_ID` | -- | Service principal for runtime identity |
| `RUNTIME_SP_PASSWORD` | -- | Service principal password |
| `RUNTIME_SP_TENANT` | -- | Service principal tenant |
| `ACA_RUNTIME_FQDN` | -- | Deployed ACA runtime URL |
| `ACA_ACR_NAME` | -- | Azure Container Registry name |
| `ACA_ENV_NAME` | -- | ACA environment name |
| `ACA_MI_RESOURCE_ID` | -- | Managed identity resource ID |
| `ACA_MI_CLIENT_ID` | -- | Managed identity client ID |
| `POLYCLAW_DATA_DIR` | `~/.polyclaw/` | Data directory path |

---

## 10. Key Files Reference

| Path (relative to `polyclaw-repo/`) | Lines | Purpose |
|--------------------------------------|-------|---------|
| `app/runtime/agent/agent.py` | 501 | Core Agent class wrapping CopilotClient |
| `app/runtime/agent/hitl.py` | 444 | Human-in-the-Loop interceptor |
| `app/runtime/agent/aitl.py` | 267 | AI-in-the-Loop reviewer |
| `app/runtime/agent/event_handler.py` | 188 | Copilot SDK event dispatch |
| `app/runtime/agent/prompt.py` | ~100 | System prompt builder |
| `app/runtime/agent/one_shot.py` | ~80 | Ephemeral session runner |
| `app/runtime/agent/tools/` | -- | Custom tool definitions (scheduler, voice, cards, memory) |
| `app/runtime/config/settings.py` | 301 | Settings and env var resolution |
| `app/runtime/server/app.py` | 541 | Application factory and lifecycle |
| `app/runtime/server/middleware.py` | ~150 | Security middleware chain |
| `app/runtime/server/routes/` | 22 files | API endpoint handlers |
| `app/runtime/state/memory.py` | 300+ | Memory formation engine |
| `app/runtime/state/guardrails/` | 6 files | Guardrails config, risk, presets |
| `app/runtime/state/profile.py` | ~200 | Agent identity and usage tracking |
| `app/runtime/state/session_store.py` | ~200 | Session management |
| `app/runtime/scheduler/engine.py` | 368 | Cron-based scheduler |
| `app/runtime/sandbox/executor.py` | 483 | ACA Dynamic Sessions sandbox |
| `app/runtime/messaging/bot.py` | ~300 | Bot Framework handler |
| `app/runtime/messaging/message_processor.py` | ~200 | Background message pipeline |
| `app/runtime/messaging/proactive.py` | ~180 | Proactive messaging store |
| `app/runtime/realtime/middleware.py` | 360 | OpenAI Realtime WebSocket proxy |
| `app/runtime/realtime/caller.py` | ~200 | ACS call automation |
| `app/runtime/realtime/tools.py` | 283 | Voice agent bridge tools |
| `app/runtime/services/cloud/azure.py` | 307 | Azure CLI wrapper |
| `app/runtime/services/keyvault.py` | ~100 | Key Vault client |
| `app/runtime/services/tunnel.py` | ~80 | Cloudflare tunnel manager |
| `app/runtime/services/otel.py` | 261 | OpenTelemetry bootstrap |
| `app/runtime/services/security/` | 7 files | Preflight, identity, RBAC, secrets, prompt shield, auditor |
| `app/runtime/services/deployment/` | 4 files | ACA deployer, provisioner |
| `app/runtime/registries/skills.py` | ~200 | Skill discovery and management |
| `app/runtime/registries/plugins.py` | ~300 | Plugin lifecycle management |
| `app/runtime/registries/catalog.py` | ~150 | Remote skill catalog |
| `app/runtime/templates/` | 16 files | Prompt templates (system, memory, realtime, etc.) |
| `app/runtime/util/spotlight.py` | ~50 | Data marking for prompt injection defense |
| `app/frontend/src/` | ~30 files | React admin dashboard |
| `Dockerfile` | ~90 | Multi-stage Docker build |
| `docker-compose.yml` | ~50 | Two-container orchestration |
| `entrypoint.sh` | 304 | Container startup orchestration |
| `pyproject.toml` | ~80 | Package metadata and dependencies |
| `skills/` | 4 dirs | Built-in skill definitions |
| `plugins/` | 5 dirs | Plugin packs with manifests |
