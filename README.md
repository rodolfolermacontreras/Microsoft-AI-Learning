# Microsoft AI Learning

A structured learning repository for a Data Scientist transitioning into AI Engineering. Covers Microsoft AI frameworks, agent development, SDK exploration, Copilot customization, Docker for data science, home server infrastructure, and practical project work -- all organized for progressive learning.

## Who This Is For

- Data Scientists moving into AI Engineering
- Engineers learning Microsoft's AI tooling ecosystem
- Anyone building with agents, LLMs, and orchestration frameworks
- Data Scientists adopting Docker and containerized workflows

---

## Repository Structure

```
Microsoft-AI-Learning/
|
|-- .env.template                          # Required environment variables (copy to .env)
|-- .gitignore                             # Git ignore rules
|-- RULES.md                               # Development rules and best practices (READ FIRST)
|-- README.md                              # This file
|-- AGENTS.md                              # GitNexus auto-generated agent context
|-- MIGRATION-GUIDE-TO-COPILOT-FRAMEWORK.md  # 10-step Python agent migration guide
|-- .vscode/mcp.json                       # MCP server config (GitNexus)
|
|-- Copilot-Studio/                # Microsoft Copilot Studio knowledge hub
|   |-- README.md                  # Overview, learning path, navigation
|   |-- 01-fundamentals/           # Platform overview, architecture, Studio vs SDK
|   |-- 02-agents/                 # Design patterns, knowledge, tools, topics
|   |-- 03-integrations/           # MCP/Fabric, Power Platform, M365, SDK bridge
|   |-- 04-projects/               # Hands-on project walkthroughs (scaffold)
|   |-- 05-sessions/               # Q&A and learning logs (scaffold)
|   |-- 06-tipsheets/              # Cheatsheet, knowledge matrix, tool selection
|   |-- 07-limitations-and-gotchas/  # Platform limits, known issues, workarounds
|   +-- resources/                 # Official links, community resources
|
|-- Docker_for_DS/                 # Docker for Data Science -- hands-on curriculum
|   |-- README.md                  # Overview, prerequisites, learning path
|   |-- CHEATSHEET.md              # All essential Docker commands at a glance
|   |-- 01-basics/                 # Core concepts, 10 essential commands, hello-world
|   |-- 02-python-environment/     # Custom DS image, pinned deps, .dockerignore
|   |-- 03-jupyter/                # Jupyter Lab in Docker, Compose, volumes
|   |-- 04-ml-pipeline/            # Train + serve containers, Flask API, shared volumes
|   |-- 05-multi-container/        # Docker Compose: Jupyter + PostgreSQL + pgAdmin
|   +-- dashboard/                 # Interactive Streamlit dashboard with AI tutor
|
|-- copilot-sdk-exploration/       # GitHub Copilot SDK hands-on work
|   |-- README.md                  # SDK overview, setup, key concepts
|   |-- COPILOT_SDK_SUMMARY.md     # Detailed SDK reference
|   +-- examples/                  # Test scripts (basic, streaming)
|
|-- awesome-copilot/               # GitHub Copilot customization framework
|   |-- COMPREHENSIVE-GUIDE.md     # 1,500-line deep-dive: agents, skills, MCP, plugins
|   +-- awesome-copilot-repo/      # Cloned awesome-copilot source (gitignored)
|
|-- microsoft-agent-framework/     # Microsoft Agent Framework (RC) learning
|   |-- README.md                  # Framework overview, getting started
|   |-- notes/                     # Architecture docs, migration guides
|   |-- examples/                  # Basic agent, tools, multi-agent workflows
|   +-- comparisons/               # vs Claude Code, vs Copilot SDK
|
|-- Local_Server/                  # Home server build (HP Z440 + RTX 3080)
|   |-- README.md                  # Architecture with Mermaid diagrams
|   |-- OVERVIEW.md                # Project summary and goals
|   |-- SHOPPING_LIST.md           # $1,000 budget buying guide
|   |-- HARDWARE.md                # Hardware specs and compatibility
|   |-- SERVER_SETUP.md            # OS, Docker, GPU passthrough setup
|   |-- DEV_WORKFLOW.md            # Development workflow guide
|   |-- docker/README.md           # Docker and container orchestration
|   |-- network/README.md          # Networking and remote access
|   |-- research/                  # Hardware research and raw notes
|   +-- projects/                  # 8 project READMEs (photo, music, security, etc.)
|
|-- kusto_app/                     # Kusto Query Assistant (Azure Data Explorer)
|   |-- README.md                  # Setup, features, usage
|   |-- main.py                    # Application entry point
|   |-- kusto_connection.py        # Database connection handling
|   |-- kusto_tools.py             # Query tools for the agent
|   |-- kusto_assistant.py         # AI assistant with schema awareness
|   +-- KUSTO_SCHEMA_GUIDE.md      # Schema configuration guide
|
|-- workplace_docs/                # Workplace Documentation Tool
|   |-- README.md                  # Quick start, setup, features
|   |-- app.py                     # Unified web application
|   |-- START.bat                  # One-click launcher
|   +-- requirements.txt           # Dependencies
|
|-- communication_microsoft/       # Microsoft Comms Guidance and Frameworks
|   |-- README.md                  # Overview, structure, data scientist lens
|   |-- comms_principles.md        # EEO guiding principles and platform usage
|   |-- before_you_send_checklist.md  # Pre-send/publish/present checklist
|   |-- meeting_map_framework.md   # Meeting Map template (from PDF)
|   +-- EEO Meeting Map.pdf        # Original PDF artifact from EEO
|
+-- polyclaw/                      # Autonomous AI Copilot (Copilot SDK agent)
    |-- OVERVIEW.md                # 800-line deep analysis of the polyclaw architecture
    +-- polyclaw-repo/             # Cloned source (gitignored)
```

### Reference Repos (cloned, gitignored)

These are cloned reference repositories excluded from git tracking. Clone separately if needed:

| Folder | Source | Purpose |
|--------|--------|---------|
| `copilot-sdk/` | [github/copilot-sdk](https://github.com/github/copilot-sdk) | Official SDK source code |
| `claude-code-best-practice/` | [anthropics/claude-code-best-practice](https://github.com/anthropics/claude-code-best-practice) | Claude agent patterns reference |
| `polyclaw/polyclaw-repo/` | [aymenfurter/polyclaw](https://github.com/aymenfurter/polyclaw) | Autonomous AI Copilot built on Copilot SDK |
| `GitNexus/` | [nicobailon/gitnexus](https://github.com/nicobailon/gitnexus) | Codebase knowledge graph (KuzuDB + Tree-sitter) |
| `awesome-copilot/` | [nicobailon/awesome-copilot](https://github.com/nicobailon/awesome-copilot) | GitHub Copilot customization catalog |

### Tooling

| Tool | Purpose | Config |
|------|---------|--------|
| **GitNexus** | Codebase knowledge graph -- 9,300+ nodes, 23,000+ edges, blast radius analysis | `.vscode/mcp.json`, `.gitnexus/` |
| **MCP Server** | GitNexus exposed as MCP server for AI agent architectural awareness | `.vscode/mcp.json` |

---

## Getting Started

### 1. Clone and Set Up

```powershell
git clone https://github.com/rodolfolermacontreras/Microsoft-AI-Learning.git
cd Microsoft-AI-Learning

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Copy environment template and fill in your keys
Copy-Item .env.template .env
# Edit .env with your API keys
```

### 2. Read the Rules

Before doing any work, read [RULES.md](RULES.md). It contains the development standards, workflow practices, and agent-specific guidelines that govern all work in this repo.

### 3. Pick a Topic

| Topic | Folder | Status |
|-------|--------|--------|
| Copilot Studio | `Copilot-Studio/` | Complete -- 22 files, fundamentals through advanced integrations |
| Docker for Data Science | `Docker_for_DS/` | Complete -- 5-section curriculum + interactive dashboard |
| Copilot SDK | `copilot-sdk-exploration/` | Complete -- summary and examples |
| Copilot Customization | `awesome-copilot/` | Complete -- 1,500-line comprehensive guide |
| Migration Guide | `MIGRATION-GUIDE-TO-COPILOT-FRAMEWORK.md` | Complete -- 10-step Python agent migration |
| Microsoft Agent Framework | `microsoft-agent-framework/` | In progress -- notes, examples, comparisons |
| Local Server Build | `Local_Server/` | Complete -- hardware, setup, 8 projects, shopping list |
| Kusto Query Assistant | `kusto_app/` | Built -- blocked by Azure auth |
| Workplace Documentation | `workplace_docs/` | Built -- async event loop issue on AI features |
| Communication at Microsoft | `communication_microsoft/` | Foundation -- EEO comms guidance, meeting frameworks |
| Polyclaw (Autonomous Agent) | `polyclaw/` | Study -- 800-line architecture deep-dive |

---

## Learning Paths

### Path A: AI Agent Development

```
1. Copilot SDK             -- Understand how GitHub Copilot works under the hood
2. Copilot Studio          -- Low-code agent building with Microsoft's platform
3. Copilot Customization   -- Agents, skills, instructions, MCP, plugins
4. Migration Guide         -- Convert Python agents to the Copilot framework
5. Agent Framework         -- Microsoft's unified agent platform (SK + AutoGen)
6. Polyclaw                -- Autonomous agents, memory, scheduling, voice
```

### Path B: Infrastructure and Tooling

```
1. Docker for DS           -- Containerize DS workflows, Jupyter, ML pipelines
2. Local Server            -- Home server build with GPU, Docker, edge devices
3. GitNexus                -- Codebase knowledge graphs and MCP integration
```

### Path C: Applied Projects

```
1. Kusto App               -- AI agents for Azure Data Explorer queries
2. Workplace Docs          -- Full-stack app with AI analysis
3. Local Server Projects   -- Photo server, music server, security camera, etc.
```

---

## Technology Stack

| Category | Technology |
|----------|-----------|
| Language | Python 3.12, Node.js v24 |
| AI SDK | GitHub Copilot SDK, Microsoft Agent Framework (RC) |
| Platforms | Microsoft Copilot Studio, Power Platform |
| Cloud | Azure AI Foundry, Azure Data Explorer |
| Providers | OpenAI, GitHub Models, Anthropic Claude |
| Containers | Docker, Docker Compose |
| Knowledge Graph | GitNexus (KuzuDB, Tree-sitter, MCP) |
| Environment | Windows 11, VS Code, PowerShell |
| Agent Tools | Claude Code, GitHub Copilot |
| Infra (planned) | HP Z440 + RTX 3080, Raspberry Pi |

## Environment Variables

Copy `.env.template` to `.env` and fill in your keys. Required variables depend on which projects you run:

| Variable | Used By |
|----------|---------|
| `OPENAI_API_KEY` | Agent Framework examples, Docker dashboard AI tutor |
| `GITHUB_TOKEN` | Copilot SDK, GitHub Models |
| `AZURE_AI_AGENT_PROJECT_CONNECTION_STRING` | Azure Foundry agents |
| `KUSTO_CLUSTER`, `KUSTO_DATABASE` | Kusto app |

## Contributing

This is a personal learning repo, but follows professional standards. See [RULES.md](RULES.md) for all conventions.

---

*Last updated: March 2026*
