# Microsoft AI Learning

A structured learning repository for a Data Scientist transitioning into AI Engineering. Covers Microsoft AI frameworks, agent development patterns, SDK exploration, and practical project work -- all organized for progressive learning.

## Who This Is For

- Data Scientists moving into AI Engineering
- Engineers learning Microsoft's AI tooling ecosystem
- Anyone building with agents, LLMs, and orchestration frameworks

## Repository Structure

```
Microsoft-AI-Learning/
|
|-- .env.template              # Required environment variables (copy to .env)
|-- .gitignore                 # Git ignore rules
|-- RULES.md                   # Development rules and best practices (READ FIRST)
|-- README.md                  # This file
|
|-- copilot-sdk-exploration/   # GitHub Copilot SDK hands-on work
|   |-- README.md              # SDK overview, setup, key concepts
|   |-- COPILOT_SDK_SUMMARY.md # Detailed SDK reference
|   +-- examples/              # Test scripts (basic, streaming)
|
|-- microsoft-agent-framework/ # Microsoft Agent Framework (RC) learning
|   |-- README.md              # Framework overview, getting started
|   |-- notes/                 # Architecture docs, migration guides
|   |-- examples/              # Basic agent, tools, multi-agent workflows
|   +-- comparisons/           # vs Claude Code, vs Copilot SDK
|
|-- kusto_app/                 # Kusto Query Assistant (Azure Data Explorer)
|   |-- README.md              # Setup, features, usage
|   |-- main.py                # Application entry point
|   |-- kusto_connection.py    # Database connection handling
|   |-- kusto_tools.py         # Query tools for the agent
|   |-- kusto_assistant.py     # AI assistant with schema awareness
|   +-- KUSTO_SCHEMA_GUIDE.md  # Schema configuration guide
|
+-- workplace_docs/            # Workplace Documentation Tool
    |-- README.md              # Quick start, setup, features
    |-- app.py                 # Unified web application
    |-- START.bat              # One-click launcher
    +-- requirements.txt       # Dependencies
```

### Reference Repos (cloned, gitignored)

These are cloned reference repositories. They are excluded from this repo's git tracking and should be cloned separately if needed:

| Folder | Source | Purpose |
|--------|--------|---------|
| `copilot-sdk/` | [github/copilot-sdk](https://github.com/github/copilot-sdk) | Official SDK source code |
| `claude-code-best-practice/` | [anthropics/claude-code-best-practice](https://github.com/anthropics/claude-code-best-practice) | Claude agent patterns reference |

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
| Copilot SDK | `copilot-sdk-exploration/` | Explored -- summary and examples complete |
| Microsoft Agent Framework | `microsoft-agent-framework/` | In progress -- notes, examples, comparisons |
| Kusto Query Assistant | `kusto_app/` | Built -- blocked by Azure auth |
| Workplace Documentation | `workplace_docs/` | Built -- async event loop issue on AI features |

## Learning Path

```
1. Copilot SDK           -- Understand how GitHub Copilot works under the hood
2. Agent Framework       -- Learn Microsoft's unified agent platform (SK + AutoGen successor)
3. Kusto App             -- Apply agents to real data work (Azure Data Explorer)
4. Workplace Docs        -- Full-stack app with AI analysis, knowledge graphs
```

## Technology Stack

| Category | Technology |
|----------|-----------|
| Language | Python 3.12 |
| AI SDK | GitHub Copilot SDK, Microsoft Agent Framework (RC) |
| Cloud | Azure AI Foundry, Azure Data Explorer |
| Providers | OpenAI, GitHub Models, Anthropic Claude |
| Environment | Windows 11, VS Code, PowerShell |
| Agent Tools | Claude Code, GitHub Copilot |

## Environment Variables

Copy `.env.template` to `.env` and fill in your keys. Required variables depend on which projects you run:

| Variable | Used By |
|----------|---------|
| `OPENAI_API_KEY` | Agent Framework examples |
| `GITHUB_TOKEN` | Copilot SDK, GitHub Models |
| `AZURE_AI_AGENT_PROJECT_CONNECTION_STRING` | Azure Foundry agents |
| `KUSTO_CLUSTER`, `KUSTO_DATABASE` | Kusto app |

## Contributing

This is a personal learning repo, but follows professional standards. See [RULES.md](RULES.md) for all conventions.
