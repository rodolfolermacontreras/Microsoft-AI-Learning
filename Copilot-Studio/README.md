# Copilot Studio — Knowledge Hub

> **Everything you need to learn, build, and master Microsoft Copilot Studio for AI agent development.**

Microsoft Copilot Studio is Microsoft's low-code platform for building, extending, and governing AI agents that work across Microsoft 365, Teams, websites, and external systems. This folder is your one-stop repository for learning materials, hands-on projects, quick-reference sheets, and session notes.

---

## Quick Navigation

| Section | What's Inside | Start Here |
|---|---|---|
| [01-fundamentals](01-fundamentals/) | Core concepts, architecture, platform overview | [What is Copilot Studio?](01-fundamentals/what-is-copilot-studio.md) |
| [02-agents](02-agents/) | Building agents: topics, knowledge, tools, patterns | [Agent Design Patterns](02-agents/agent-design-patterns.md) |
| [03-integrations](03-integrations/) | MCP, Fabric, Power Platform, M365, SDK bridge | [MCP and Fabric](03-integrations/mcp-and-fabric.md) |
| [04-projects](04-projects/) | Hands-on project walkthroughs | [Project Index](04-projects/README.md) |
| [05-sessions](05-sessions/) | Q&A sessions and learning logs | [Session Index](05-sessions/README.md) |
| [06-tipsheets](06-tipsheets/) | Cheat sheets and quick-reference cards | [Cheatsheet](06-tipsheets/copilot-studio-cheatsheet.md) |
| [07-limitations-and-gotchas](07-limitations-and-gotchas/) | Platform limits, known issues, workarounds | [Platform Limits](07-limitations-and-gotchas/platform-limits.md) |
| [resources](resources/) | Official links, training paths, community resources | [Official Links](resources/official-links.md) |

---

## What is Copilot Studio? (30-Second Version)

Copilot Studio is Microsoft's **low-code conversational AI builder** where you design agents through a web studio using topics, flows, and natural language. It evolved from Power Virtual Agents and now adds:

- **GPT-powered orchestration** over language models, plugins, and workflows
- **1,100+ prebuilt connectors** to enterprise systems (Dataverse, SharePoint, Dynamics, custom APIs)
- **Multi-channel publishing** to Teams, websites, mobile apps
- **MCP integration** for connecting to external AI tools and Fabric Data Agents
- **Enterprise governance** riding on M365 security, compliance, and identity

**Access it at:** [https://copilotstudio.microsoft.com](https://copilotstudio.microsoft.com)

---

## Prerequisites

- A **Microsoft work or school account** (Microsoft Entra ID) with Copilot Studio access
- Access to [copilotstudio.microsoft.com](https://copilotstudio.microsoft.com) for hands-on work
- Familiarity with this workspace's conventions: see [RULES.md](../RULES.md)

No local setup is required to use this knowledge base. For hands-on projects in `04-projects/`, prerequisites are documented per project.

---

## How This Folder is Organized

```
Copilot-Studio/
├── README.md                            ← You are here
├── 01-fundamentals/                     # Learn the platform from the ground up
│   ├── what-is-copilot-studio.md
│   ├── architecture-and-concepts.md
│   ├── copilot-studio-vs-copilot-sdk.md
│   └── getting-started-checklist.md
├── 02-agents/                           # Deep-dive into building agents
│   ├── agent-design-patterns.md
│   ├── topics-and-conversations.md
│   ├── knowledge-sources.md
│   └── tools-and-actions.md
├── 03-integrations/                     # Ecosystem connections
│   ├── mcp-and-fabric.md
│   ├── power-platform.md
│   ├── microsoft-365.md
│   └── copilot-sdk-bridge.md
├── 04-projects/                         # Hands-on builds (added over time)
│   └── README.md
├── 05-sessions/                         # Q&A and learning logs (added per session)
│   └── README.md
├── 06-tipsheets/                        # Quick reference
│   ├── copilot-studio-cheatsheet.md
│   ├── knowledge-source-matrix.md
│   └── tool-selection-guide.md
├── 07-limitations-and-gotchas/          # What to watch out for
│   ├── platform-limits.md
│   └── known-issues.md
└── resources/                           # Links and community
    ├── official-links.md
    └── community-resources.md
```

---

## Learning Path (Suggested Order)

If you're new to Copilot Studio, follow this sequence:

1. **[What is Copilot Studio?](01-fundamentals/what-is-copilot-studio.md)** — Platform overview and positioning
2. **[Architecture and Concepts](01-fundamentals/architecture-and-concepts.md)** — Mental model for how everything fits together
3. **[Getting Started Checklist](01-fundamentals/getting-started-checklist.md)** — Sign up and build your first agent
4. **[Agent Design Patterns](02-agents/agent-design-patterns.md)** — Common patterns for real-world agents
5. **[Knowledge Sources](02-agents/knowledge-sources.md)** — Connect your agent to enterprise data
6. **[Tools and Actions](02-agents/tools-and-actions.md)** — Extend your agent with connectors, flows, MCP, and APIs
7. **[Copilot Studio Cheatsheet](06-tipsheets/copilot-studio-cheatsheet.md)** — Keep this open while building
8. **[Platform Limits](07-limitations-and-gotchas/platform-limits.md)** — Know the boundaries before you hit them

---

## Key Concepts at a Glance

| Concept | What It Is |
|---|---|
| **Agent** | An AI companion that handles conversations and tasks using instructions, knowledge, tools, and triggers |
| **Topic** | A portion of a conversation defining a specific flow (trigger → nodes → response) |
| **Agent Flow** | An automation (like Power Automate) that an agent can trigger as a tool |
| **Knowledge Source** | Enterprise data (SharePoint, Dataverse, websites, documents) the agent uses for grounding |
| **Tool** | An action the agent can perform: connector calls, API requests, MCP server calls, prompts |
| **Generative Orchestration** | AI-driven mode where the agent dynamically selects the best topic, tool, or knowledge to respond |
| **Classic Orchestration** | Rule-based mode where topics are matched via trigger phrases |
| **MCP (Model Context Protocol)** | Open standard for connecting AI to external tools/data; Copilot Studio supports MCP server connections |
| **Connector** | Pre-built or custom integration with an external service (1,100+ available) |

---

## Related Folders in This Workspace

| Folder | Relationship |
|---|---|
| `copilot-sdk/` | GitHub Copilot SDK — code-first programmatic approach (compare with Studio's low-code approach) |
| `copilot-sdk-exploration/` | Hands-on SDK experiments and reference |
| `awesome-copilot/` | GitHub Copilot customization: agents, skills, instructions, plugins |
| `microsoft-agent-framework/` | Microsoft Agent Framework patterns and comparisons |

---

*Last updated: March 2026*
