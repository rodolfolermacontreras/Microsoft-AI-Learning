# Copilot Studio vs GitHub Copilot SDK

> **TL;DR:** Copilot Studio is a low-code web platform for building conversational agents over Microsoft 365 data. The GitHub Copilot SDK is a code-first library for embedding Copilot's agent runtime into custom applications. They serve different audiences and scenarios but can complement each other.

---

## Side-by-Side Comparison

| Dimension | Copilot Studio | GitHub Copilot SDK |
|---|---|---|
| **Approach** | Low-code / no-code web builder | Code-first programmatic API |
| **Primary audience** | Business users, citizen developers, IT pros | Software developers building applications |
| **Where agents run** | Microsoft cloud (Power Platform) | Your application (via Copilot CLI process) |
| **Agent authoring** | Visual canvas + natural language | Python / TypeScript / Go / .NET code |
| **Models** | Azure OpenAI GPT (platform-managed) | GPT-4.1, Claude Sonnet 4.5, Claude Haiku, etc. (selectable) |
| **Data access** | 1,100+ Power Platform connectors, SharePoint, Dataverse | Custom tools, MCP servers, file system, GitHub |
| **Channels** | Teams, web, mobile, Facebook, Azure Bot Service | Any application you build (CLI, web app, API) |
| **MCP support** | Yes (connect to MCP servers as tools) | Yes (connect to MCP servers via session config) |
| **Governance** | Built-in M365 security, admin center, environment management | Application-level (you manage auth and access) |
| **Billing** | Copilot Studio license / Power Platform meters | GitHub Copilot subscription (premium request quota) |
| **Status** | Generally Available | Technical Preview (Jan 2026) |

---

## When to Use Each

### Use Copilot Studio When...

- You need agents that **serve business users** (not developers) through Teams, web, or mobile
- Your data lives in **Microsoft 365, SharePoint, Dataverse, or Dynamics**
- You want **citizen developers** (non-coders) to build and maintain agents
- You need **enterprise governance** out of the box (SSO, compliance, admin controls)
- The use case is **conversational** — Q&A, task routing, workflow triggering
- You need to **extend Microsoft 365 Copilot** with custom capabilities
- You want **rapid prototyping** without writing code

### Use Copilot SDK When...

- You're building a **custom application** (CLI tool, web app, internal tool)
- You need **full control** over the agent runtime, tool execution, and UX
- You want to **choose the LLM** (GPT-4.1, Claude, etc.) per session
- You need **custom tools defined in code** with complex logic
- Your use case is **developer-centric** (code generation, PR review, file management)
- You want to **embed AI capabilities** into an existing product
- You need **session persistence** and **multi-session management** in your app

### Use Both Together When...

- Copilot Studio handles **business-facing agents** (Teams helpdesk, HR assistant)
- Copilot SDK powers **developer-facing features** in your internal tools
- Both connect to the **same MCP servers** for shared backend capabilities
- Studio agents trigger **external systems** that your SDK-based tools also consume

---

## Architecture Comparison

### Copilot Studio Architecture

```
Business User (Teams / Web / Mobile)
        │
        ▼
  Copilot Studio Agent
  ┌─────────────────────────┐
  │ Topics + Gen. Orch.     │
  │ Knowledge Sources       │
  │ Tools (Connectors,      │
  │        Flows, MCP)      │
  └────────┬────────────────┘
           │
  ┌────────▼────────┐
  │ Power Platform   │
  │ (Dataverse,      │
  │  Automate,       │
  │  Connectors)     │
  └──────────────────┘
```

### Copilot SDK Architecture

```
Your Application (CLI / Web / Custom)
        │
        ▼
  SDK Client (Python / TS / Go / .NET)
  ┌─────────────────────────┐
  │ Custom Tools (@define)  │
  │ MCP Server connections  │
  │ Custom Agents           │
  │ Session Management      │
  └────────┬────────────────┘
           │ JSON-RPC
  ┌────────▼────────┐
  │ Copilot CLI      │
  │ (Agent Runtime)  │
  └────────┬────────┘
           │
  ┌────────▼────────┐
  │ GitHub / Models  │
  │ (Auth, LLMs)     │
  └──────────────────┘
```

---

## Feature-Level Comparison

### Agent Capabilities

| Feature | Copilot Studio | Copilot SDK |
|---|---|---|
| Natural language understanding | Built-in (generative + classic NLU) | Via LLM prompts |
| Topic/flow authoring | Visual canvas | Code |
| Multi-turn conversation | Built-in with context tracking | Manual with session state |
| Channel publishing | Multi-channel (Teams, web, etc.) | Custom (you build the UI) |
| Handoff to human | Built-in escalation system | You implement |
| Analytics | Built-in dashboard | You implement |

### Data and Tools

| Feature | Copilot Studio | Copilot SDK |
|---|---|---|
| SharePoint grounding | Native knowledge source | Via MCP or custom tool |
| Dataverse access | Native knowledge source | Via MCP or custom tool |
| Power Automate flows | Native tool type | Not available |
| Connectors | 1,100+ prebuilt | Via MCP servers |
| Custom code tools | Limited (via flows/connectors) | Full (any code) |
| File system access | Via connectors | Built-in (default tools) |
| Git operations | Not available | Built-in |

### Developer Experience

| Feature | Copilot Studio | Copilot SDK |
|---|---|---|
| Learning curve | Low (visual builder) | Medium (requires coding) |
| Version control | Solution export/import | Standard code repos |
| CI/CD | Power Platform pipelines | Standard dev pipelines |
| Testing | Built-in test chat | Programmatic + manual |
| Debugging | Trace in Studio | CLI logs + code debugging |
| Extensibility | Connectors, flows, MCP | Unlimited (it's your code) |

---

## Quick Decision Framework

```
Do you need an agent for business users in M365/Teams?
├── YES → Copilot Studio
│         └── Need code-level customization too?
│             └── YES → Studio for agent UX + SDK for backend tools
└── NO → Are you building a custom application?
         ├── YES → Copilot SDK
         └── NO → What are you building?
                  ├── GitHub automation → Copilot agents (awesome-copilot)
                  └── Azure services → Azure AI Foundry
```

---

## Key SDK Quick Reference (for Comparison)

Since you have the Copilot SDK in this workspace, here's the essential API pattern:

```python
# Copilot SDK — Python
import asyncio
from copilot import CopilotClient

async def main():
    client = CopilotClient()
    await client.start()
    session = await client.create_session({
        "model": "gpt-4.1",
        "tools": [my_custom_tool],      # Your code-defined tools
        "mcp_servers": { ... },          # External MCP connections
        "custom_agents": [{ ... }],      # Custom personas
        "streaming": True,               # Token-by-token output
    })
    response = await session.send_and_wait({"prompt": "Do something"})
    await client.stop()

asyncio.run(main())
```

Compare this with Copilot Studio where the same agent would be built visually — no code, but also less flexibility.

---

## Next Steps

- **[What is Copilot Studio?](what-is-copilot-studio.md)** — Deep dive into the Studio platform
- **[Copilot SDK Bridge](../03-integrations/copilot-sdk-bridge.md)** — How Studio and SDK can work together
- **SDK reference:** See `../copilot-sdk-exploration/COPILOT_SDK_SUMMARY.md`

---

*Sources: [Copilot SDK repo](https://github.com/github/copilot-sdk), [Microsoft Learn — Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/fundamentals-what-is-copilot-studio)*
