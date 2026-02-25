# Polyclaw -- Autonomous AI Copilot

Study notes and reference material for [Polyclaw](https://github.com/aymenfurter/polyclaw), an open-source autonomous AI agent built on the GitHub Copilot SDK. Created by Aymen Furter (Microsoft Solution Engineer).

## What Polyclaw Is

Polyclaw turns GitHub Copilot from a reactive coding assistant into a fully autonomous agent that can:

- Run scheduled tasks unattended (cron-based scheduler)
- Make and receive voice calls (Azure Communication Services + OpenAI Realtime API)
- Send proactive messages to Telegram and Microsoft Teams
- Maintain persistent memory across sessions (Second Brain pattern)
- Self-extend by writing and installing new skills at runtime
- Deploy to Azure Container Apps with managed identity and RBAC

Every AI interaction routes through the Copilot SDK, meaning the same model access, tool infrastructure, and billing you already have with a GitHub Copilot subscription.

## Why This Matters for Data Scientists

| Concept | Relevance |
|---------|-----------|
| Autonomous agents | Production agent patterns beyond chat-based interaction |
| Scheduled tasks | Automated data pipelines, report generation, monitoring |
| Memory system | Persistent context across sessions -- pattern for long-running workflows |
| Guardrails | Defense-in-depth safety for production AI (allow/deny/HITL/AITL) |
| Copilot SDK harness | How to build on top of GitHub Copilot programmatically |
| Admin/runtime separation | Container isolation patterns for secure agent deployment |
| Voice + messaging | Multi-channel agent interfaces beyond web UIs |

## Architecture Overview

### Two-Container Design

```
+------------------------------+      +-------------------------------+
|         ADMIN PLANE          |      |        AGENT RUNTIME          |
|  (admin container)           |      |  (runtime container)          |
|                              |      |                               |
|  - React + Vite dashboard    |      |  - Copilot SDK agent core     |
|  - TypeScript TUI            |      |  - aiohttp web server         |
|  - Azure CLI session         |      |  - Bot Framework integration  |
|  - GitHub CLI / token        |      |  - Scheduler engine           |
|  - Setup wizard              |      |  - Memory formation           |
|  - Deployment orchestration  |      |  - Voice call handler         |
|                              |      |  - Sandbox executor (ACA)     |
|  HAS: GH token, admin secret|      |  HAS: service principal only  |
|  NEVER: agent execution      |      |  NEVER: GH token, admin secret|
+------------------------------+      +-------------------------------+
              |                                     |
              +------------ shared volume -----------+
                   .env, SOUL.md, memory/, skills/
```

### Core Agent Flow

```
User message --> Bot Framework / Telegram / CLI
    |
    v
Agent.send(prompt)
    |
    v
CopilotClient (GitHub Copilot SDK)
    |-- build_system_prompt() loads SOUL.md + memory context
    |-- get_all_tools() registers custom tools
    |-- SandboxToolInterceptor wraps file/terminal operations
    |-- HitlInterceptor checks guardrails before tool execution
    |-- EventHandler streams response tokens
    |
    v
Response --> Channel --> MemoryFormation (idle timer triggers consolidation)
```

### Persistent Workspace (~/.polyclaw/)

```
~/.polyclaw/
|-- SOUL.md               # Agent personality and instructions
|-- profile.json           # User preferences, emotional state
|-- mcp_servers.json       # MCP server configurations
|-- scheduler.json         # Scheduled task definitions (cron)
|-- suggestions.txt        # Proactive message suggestions
|
|-- memory/
|   |-- daily/             # YYYY-MM-DD.md daily conversation logs
|   +-- topics/            # topic-name.md consolidated knowledge
|
|-- sessions/              # Session transcripts
|-- skills/                # User-created skills (self-extending)
|-- media/
|   |-- incoming/          # Received media files
|   +-- outgoing/          # Sent media (pending/sent/error)
+-- plugins/               # MCP plugin configurations
```

### Key Subsystems

| Subsystem | Module | Description |
|-----------|--------|-------------|
| Agent Core | `app/runtime/agent/agent.py` | CopilotClient wrapper, session lifecycle |
| Memory | `app/runtime/state/memory.py` | Idle-triggered consolidation using lighter model |
| Scheduler | `app/runtime/scheduler/engine.py` | Cron-based task execution with HITL support |
| Guardrails | `app/runtime/state/guardrails/` | Allow/deny/HITL/AITL/content filtering per tool |
| Voice | `app/runtime/realtime/` | Azure Communication Services + OpenAI Realtime API |
| Messaging | `app/runtime/messaging/` | Bot Framework, Telegram, slash commands |
| Sandbox | `app/runtime/sandbox/executor.py` | ACA Dynamic Sessions for isolated execution |
| Identity | `app/runtime/server/routes/identity_routes.py` | Managed identity, RBAC inspection and auto-fix |
| Skills | `app/runtime/registries/` | Self-extending skill system, plugin management |
| Settings | `app/runtime/config/settings.py` | Environment-driven configuration, data dirs |

### Custom Agent Tools

Defined with `@define_tool` from the Copilot SDK:

| Tool | Purpose |
|------|---------|
| `schedule_task` | Create cron or one-shot scheduled tasks |
| `cancel_task` | Remove a scheduled task by ID |
| `list_scheduled_tasks` | Enumerate all scheduled tasks |
| `make_voice_call` | Initiate outbound phone call via ACS |
| `search_memories_tool` | Search consolidated memories (Foundry IQ) |
| `send_adaptive_card` | Rich adaptive card to channel |
| `send_hero_card` | Hero card with image and buttons |
| `send_thumbnail_card` | Thumbnail card |
| `send_card_carousel` | Carousel of multiple cards |

## Repository Structure (Cloned)

The cloned `polyclaw-repo/` contains:

```
polyclaw-repo/
|-- Dockerfile             # Multi-stage build (Python + Node.js)
|-- docker-compose.yml     # Admin + runtime container orchestration
|-- pyproject.toml          # Python dependencies and entry points
|-- entrypoint.sh           # Container startup script
|-- AGENTS.md               # Agent onboarding instructions
|-- conftest.py             # Root pytest configuration
|
|-- app/
|   |-- cli/               # polyclaw-run CLI entry point
|   |-- frontend/          # React + Vite admin dashboard (TypeScript)
|   |-- runtime/           # Python backend
|   |   |-- agent/         # Copilot SDK agent core, tools, prompts
|   |   |-- config/        # Settings, environment configuration
|   |   |-- messaging/     # Bot Framework, Telegram, slash commands
|   |   |-- realtime/      # Voice call handling (ACS + OpenAI)
|   |   |-- registries/    # Plugin and skill registries
|   |   |-- scheduler/     # Cron-based task engine
|   |   |-- sandbox/       # ACA Dynamic Sessions executor
|   |   |-- server/        # aiohttp web server, routes, middleware
|   |   |-- services/      # Tunnel, deployer, Key Vault, cloud CLIs
|   |   |-- state/         # JSON-file-backed state stores
|   |   |-- templates/     # Prompt templates (memory, scheduler, etc.)
|   |   +-- tests/         # Comprehensive test suite
|   +-- tui/               # Terminal UI (TypeScript, Bun, OpenTUI)
|
|-- docs/                  # Hugo documentation site
|-- plugins/               # Built-in MCP plugins
|-- presentations/         # Slide decks
|-- scripts/               # run-tui.sh and helper scripts
+-- skills/                # Built-in skill definitions
```

## Security Model

Polyclaw implements defense-in-depth:

- **Container isolation**: Admin and runtime never share credentials
- **ADMIN_SECRET**: JWT-validated API authentication
- **Telegram whitelist**: Only approved user IDs can interact
- **Sandbox execution**: Agent commands run in ACA Dynamic Sessions
- **Key Vault integration**: Secrets referenced via `@kv:` prefix
- **LOCKDOWN_MODE**: Disables all external tool execution
- **HITL (Human-in-the-Loop)**: Interactive approval before tool calls
- **AITL (AI-in-the-Loop)**: Separate AI reviewer evaluates tool calls
- **Content filtering**: Azure Content Safety prompt shields
- **Managed identity + RBAC**: Least-privilege Azure access

## Prerequisites

- Docker Desktop
- GitHub Copilot subscription (Individual, Business, or Enterprise)
- Azure subscription (for ACS, Container Apps, Content Safety)
- Azure CLI (`az`)

## Key Learning Objectives

1. Understand how to build autonomous agents on top of the Copilot SDK
2. Study the memory formation pattern (idle-triggered, lighter model consolidation)
3. Learn cron-based scheduled task execution with guardrail support
4. Explore multi-channel messaging (Telegram, Teams, voice calls)
5. Analyze the admin/runtime container separation for credential isolation
6. Review guardrail strategies (allow, deny, HITL, AITL, content filtering)
7. Study the self-extending skill system (agent writes its own tools)
8. Understand Azure-native deployment (ACA, managed identity, Key Vault)

## Links

- Source: [aymenfurter/polyclaw](https://github.com/aymenfurter/polyclaw)
- Author: [Aymen Furter](https://www.linkedin.com/in/aymenfurter/) (Microsoft Solution Engineer)
- License: MIT
- Languages: Python 58.5%, TypeScript 32.8%, CSS 7.0%
