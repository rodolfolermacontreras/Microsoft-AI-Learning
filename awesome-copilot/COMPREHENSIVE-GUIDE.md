# Comprehensive Guide to GitHub Copilot Customization

A practical, end-to-end reference for creating and using **Agents**, **Skills**, **Instructions**, **Tools**, **MCP Servers**, **Hooks**, **Agentic Workflows**, and **Plugins** with GitHub Copilot. This guide is designed so that anyone can pick it up and start building immediately.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Repository Structure](#2-repository-structure)
3. [Agents](#3-agents)
4. [Instructions](#4-instructions)
5. [Skills](#5-skills)
6. [Tools and MCP Servers](#6-tools-and-mcp-servers)
7. [Hooks](#7-hooks)
8. [Agentic Workflows](#8-agentic-workflows)
9. [Plugins](#9-plugins)
10. [GitHub Copilot SDK](#10-github-copilot-sdk)
11. [Project Setup and Validation](#11-project-setup-and-validation)
12. [Quick Reference Cheat Sheet](#12-quick-reference-cheat-sheet)
13. [Resources](#13-resources)

---

## 1. Architecture Overview

GitHub Copilot's customization system is built around **six resource types** that live in your repository's `.github/` directory (or repository root). Each resource type serves a distinct purpose:

| Resource | File Pattern | Purpose |
|---|---|---|
| **Agent** | `*.agent.md` | Specialized AI persona with defined expertise, tools, and model |
| **Instruction** | `*.instructions.md` | Contextual rules applied automatically based on file patterns |
| **Skill** | `skills/*/SKILL.md` | Self-contained knowledge + assets for specific tasks |
| **Hook** | `hooks/*/hooks.json` | Automated scripts triggered by coding agent events |
| **Workflow** | `workflows/*.md` | AI-powered GitHub Actions automations |
| **Plugin** | `plugins/*/plugin.json` | Bundles of agents, commands, and skills for distribution |

### How They Interact

```
User in VS Code / CLI
        |
        v
  GitHub Copilot Chat
        |
        +-- Reads .github/copilot-instructions.md (global instructions)
        +-- Reads .github/instructions/*.instructions.md (scoped instructions)
        +-- Loads .github/agents/*.agent.md (invokable via @agent-name)
        +-- Loads skills on demand (referenced in agents or standalone)
        +-- Connects to MCP Servers (tools defined in agents or .vscode/mcp.json)
        +-- Fires hooks (session start/end, prompt submitted, tool used)
        |
        v
  LLM (gpt-4.1, claude-sonnet-4.5, etc.)
```

---

## 2. Repository Structure

### Where Customizations Live

```
your-project/
├── .github/
│   ├── copilot-instructions.md          # Global instructions (always active)
│   ├── instructions/
│   │   ├── python-django.instructions.md  # Scoped to matching files
│   │   └── react-testing.instructions.md
│   ├── agents/
│   │   ├── code-reviewer.agent.md
│   │   └── python-mcp-expert.agent.md
│   ├── hooks/
│   │   └── session-logger/
│   │       ├── hooks.json
│   │       ├── README.md
│   │       └── log-session-start.sh
│   └── workflows/
│       └── daily-issues-report.md
├── .vscode/
│   └── mcp.json                         # VS Code workspace MCP config
└── ...
```

### MCP Configuration Locations

| Scope | Path | When to Use |
|---|---|---|
| **VS Code Workspace** | `.vscode/mcp.json` | Per-project MCP servers in VS Code |
| **Project (Copilot CLI)** | `.mcp/copilot/mcp.json` | Per-project MCP servers for CLI |
| **Global (Copilot CLI)** | `~/.copilot/mcp-config.json` | User-wide MCP servers |

---

## 3. Agents

Agents transform GitHub Copilot Chat into **domain-specific assistants**. You invoke them with `@agent-name` in chat.

### File Format

**Location:** `.github/agents/` or project root `agents/`
**Extension:** `.agent.md`
**Naming:** Lowercase with hyphens (e.g., `python-mcp-expert.agent.md`)

### Frontmatter (YAML)

```yaml
---
description: 'Brief description of the agent and its purpose'   # REQUIRED, single quotes
name: 'My Agent Name'                                            # Recommended (human-readable)
model: GPT-4.1                                                   # Strongly recommended
tools:                                                           # Recommended
  - codebase
  - terminalCommand
  - githubRepo
---
```

| Field | Required | Description |
|---|---|---|
| `description` | Yes | Single-quoted, non-empty. Explains what the agent does. |
| `name` | Recommended | Human-readable display name (e.g., "Python MCP Expert"). |
| `model` | Strongly recommended | Which LLM to use (e.g., `GPT-4.1`, `claude-sonnet-4.5`). |
| `tools` | Recommended | Array of tools the agent can access. |

### Available Built-in Tools

| Tool | Description |
|---|---|
| `codebase` | Search and read files in the workspace |
| `terminalCommand` | Run terminal commands |
| `githubRepo` | Access GitHub repository data |
| `fetch` | Make HTTP requests |
| `useDiffEditTool` | Apply code edits via diffs |
| `insertEditTool` | Insert code at specific locations |
| `createFile` | Create new files |

### Complete Agent Example

```markdown
---
description: 'Expert assistant for developing Model Context Protocol (MCP) servers in Python'
name: 'Python MCP Server Expert'
model: GPT-4.1
tools:
  - codebase
  - terminalCommand
---

You are an expert Python developer specializing in Model Context Protocol (MCP)
server development using the FastMCP framework.

## Your Expertise

- Python MCP SDK (FastMCP high-level API)
- Transport configuration (stdio, streamable HTTP, SSE)
- Tool, Resource, and Prompt development
- Pydantic data validation and type safety
- Async Python patterns

## Your Approach

- Always use type hints on all function parameters and return types
- Use Pydantic models for structured input/output
- Prefer FastMCP decorators (@mcp.tool(), @mcp.resource(), @mcp.prompt())
- Include comprehensive docstrings (these become tool descriptions)
- Handle errors gracefully with informative messages
- Log to stderr, never stdout (stdout is for MCP protocol messages)

## Guidelines

- Start with `from mcp.server.fastmcp import FastMCP`
- Use `uv` for dependency management
- Always validate inputs before processing
- Return structured data (dicts or Pydantic models), not raw strings
- Include progress reporting for long operations via `ctx.report_progress()`
- Use Context parameter for logging: `ctx.info()`, `ctx.error()`
- Test with MCP Inspector: `mcp dev server.py`
```

### Agent with MCP Server Tools

Agents can reference external MCP servers. The MCP server configuration is embedded in the agent or configured separately:

```markdown
---
description: 'Agent with access to external API via MCP'
name: 'API Agent'
model: GPT-4.1
tools:
  - codebase
  - terminalCommand
---

You are an assistant with access to external APIs through MCP tools.
Use the available MCP tools to query data and perform actions.

When the user asks about data, use the appropriate MCP tool to fetch it
rather than making assumptions.
```

The corresponding MCP server is configured in `.vscode/mcp.json`:

```json
{
  "servers": {
    "my-api": {
      "type": "http",
      "url": "https://api.example.com/mcp",
      "headers": {
        "Authorization": "Bearer ${input:api_key}"
      }
    }
  }
}
```

---

## 4. Instructions

Instructions are **contextual rules** that Copilot applies automatically based on file patterns. Unlike agents (which you invoke), instructions activate in the background.

### File Format

**Location:** `.github/instructions/` or `.github/copilot-instructions.md` (global)
**Extension:** `.instructions.md`
**Naming:** Lowercase with hyphens (e.g., `python-django.instructions.md`)

### Frontmatter (YAML)

```yaml
---
description: 'Instructions for building MCP servers using the Python SDK'   # REQUIRED
applyTo: '**/*.py, **/pyproject.toml, **/requirements.txt'                  # REQUIRED
---
```

| Field | Required | Description |
|---|---|---|
| `description` | Yes | Single-quoted, non-empty. What these instructions cover. |
| `applyTo` | Yes | Glob patterns (comma-separated) for when to activate. |

### Glob Pattern Examples

| Pattern | Matches |
|---|---|
| `**/*.py` | All Python files |
| `**/*.ts, **/*.tsx` | All TypeScript files |
| `src/**` | Everything under src/ |
| `**/test_*.py, **/*_test.py` | Python test files |
| `**/Dockerfile, **/docker-compose*.yml` | Docker files |
| `**/*.py, **/pyproject.toml, **/requirements.txt` | Python project files |

### Complete Instruction Example

```markdown
---
description: 'Instructions for building MCP servers using the Python SDK'
applyTo: '**/*.py, **/pyproject.toml, **/requirements.txt'
---

# Python MCP Server Development

## Standards

- Use `uv` for dependency management, not pip
- Import from `mcp.server.fastmcp` for the high-level API
- Use type hints on all function parameters and return types
- Use Pydantic models for structured input/output validation
- Log to stderr (`logging` module), never print to stdout

## Server Setup Pattern

Always structure MCP servers as:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("server-name")

@mcp.tool()
async def my_tool(param: str) -> dict:
    """Tool description that becomes the MCP tool description."""
    return {"result": param}

if __name__ == "__main__":
    mcp.run()
```

## Error Handling

- Wrap tool logic in try/except blocks
- Return error details in a structured format
- Use `ctx.error()` for logging errors, not print

## Testing

- Test with: `mcp dev server.py`
- Use MCP Inspector for interactive testing
- For Claude Desktop: `mcp install server.py`
```

### Global Instructions

Place a file at `.github/copilot-instructions.md` (no `applyTo` needed) for rules that always apply:

```markdown
# Project-Wide Copilot Instructions

- Use conventional commits (feat:, fix:, docs:, refactor:, test:)
- Always include type hints in Python code
- Follow PEP 8 style guidelines
- Use descriptive variable names (verb_noun pattern for functions)
- Include docstrings on all public functions and classes
- Never commit secrets or API keys
```

---

## 5. Skills

Skills are **self-contained knowledge packages** with optional bundled assets. They provide deep, task-specific expertise that Copilot can load on demand.

### Structure

```
skills/
└── my-skill-name/
    ├── SKILL.md           # REQUIRED - skill definition + instructions
    ├── references/        # Optional - reference documentation
    │   ├── api-docs.md
    │   └── examples.md
    └── scripts/           # Optional - helper scripts
        └── setup.sh
```

### SKILL.md Frontmatter

```yaml
---
name: my-skill-name                                                          # REQUIRED
description: 'Generate a complete MCP server project in Python'              # REQUIRED
---
```

| Field | Required | Constraints |
|---|---|---|
| `name` | Yes | Lowercase with hyphens, must match folder name, max 64 chars. |
| `description` | Yes | Single-quoted, 10-1024 characters. |

### Bundled Assets

- Each asset must be under **5 MB**
- Assets must be referenced from SKILL.md
- Common asset types: reference docs, schemas, templates, scripts
- Follows the [Agent Skills Specification](https://agentskills.io/specification)

### Complete Skill Example

```markdown
---
name: python-mcp-server-generator
description: 'Generate a complete MCP server project in Python with tools, resources, and proper configuration'
---

# Python MCP Server Generator

Generate a production-ready MCP server project in Python.

## Requirements

When generating an MCP server, always include:

### Project Structure
```
my-mcp-server/
├── pyproject.toml
├── README.md
├── src/
│   └── my_mcp_server/
│       ├── __init__.py
│       └── server.py
└── tests/
    └── test_server.py
```

### Dependencies (pyproject.toml)
```toml
[project]
name = "my-mcp-server"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["mcp[cli]>=1.0.0"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project.scripts]
my-mcp-server = "my_mcp_server.server:main"
```

## Implementation Details

### Server Configuration
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "my-server",
    version="0.1.0",
    description="Description of what this server does",
)
```

### Tool Implementation
```python
@mcp.tool()
async def process_data(input_text: str, format: str = "json") -> dict:
    """Process input text and return structured data.

    Args:
        input_text: The text to process
        format: Output format (json, csv, or text)
    """
    # Implementation here
    return {"processed": input_text, "format": format}
```

### Resource Implementation
```python
@mcp.resource("config://settings")
async def get_settings() -> dict:
    """Return current server configuration settings."""
    return {"version": "0.1.0", "debug": False}

@mcp.resource("data://{table_name}")
async def get_table(table_name: str) -> str:
    """Get data from a named table."""
    return f"Data from {table_name}"
```

## Testing

```bash
# Run the server in development mode
mcp dev src/my_mcp_server/server.py

# Install for Claude Desktop
mcp install src/my_mcp_server/server.py

# Run directly
uv run my-mcp-server
```

## Best Practices

- Use type hints on all parameters and return types
- Return structured data (dicts/Pydantic models), not raw strings
- Log to stderr, never stdout
- Validate inputs before processing
- Include progress reporting for long operations
- Handle errors with informative messages
- Clean up resources in tool handlers
```

### Creating a New Skill (Scaffolding)

```bash
cd awesome-copilot
npm run skill:create -- --name my-new-skill --description "Description of the skill"
```

This creates the folder structure and a template SKILL.md.

---

## 6. Tools and MCP Servers

Tools extend Copilot's capabilities beyond code generation. There are two main approaches: **built-in tools** referenced in agents, and **MCP (Model Context Protocol) servers** that provide custom tools via a standardized protocol.

### 6.1 Built-in Copilot Tools

These are referenced in agent `tools` arrays:

```yaml
tools:
  - codebase          # Search and read workspace files
  - terminalCommand   # Execute terminal commands
  - githubRepo        # Access GitHub repository data
  - fetch             # Make HTTP requests
  - useDiffEditTool   # Apply code changes via diff
  - insertEditTool    # Insert code at locations
  - createFile        # Create new files
```

### 6.2 MCP Server Concepts

MCP (Model Context Protocol) is an open standard for connecting AI models to external tools and data. An MCP server exposes:

- **Tools**: Functions the AI can call (e.g., query a database, call an API)
- **Resources**: Data the AI can read (e.g., configuration, documentation)
- **Prompts**: Pre-built prompt templates

### 6.3 MCP Server Configuration

#### VS Code Workspace Configuration (`.vscode/mcp.json`)

```json
{
  "servers": {
    "my-server-name": {
      "type": "http",
      "url": "https://api.example.com/mcp",
      "headers": {
        "Authorization": "Bearer ${input:api_key}"
      }
    }
  }
}
```

#### Two Transport Types

**HTTP/URL-based (Streamable HTTP):**
```json
{
  "servers": {
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp"
    }
  }
}
```

**Command-based (stdio):**
```json
{
  "servers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${input:github_pat}"
      }
    }
  }
}
```

#### Command-based Variants

**Using npx (Node.js packages):**
```json
{
  "servers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
    }
  }
}
```

**Using Docker:**
```json
{
  "servers": {
    "my-tool": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "API_KEY",
        "ghcr.io/org/mcp-server:latest"
      ],
      "env": {
        "API_KEY": "${input:api_key}"
      }
    }
  }
}
```

**Using uv (Python packages):**
```json
{
  "servers": {
    "python-tool": {
      "command": "uv",
      "args": ["run", "--with", "my-mcp-package", "my-mcp-server"],
      "env": {
        "CONFIG_PATH": "/path/to/config"
      }
    }
  }
}
```

**Using npx mcp-remote (proxy to HTTP servers):**
```json
{
  "servers": {
    "remote-server": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://remote-server.example.com/sse"]
    }
  }
}
```

### 6.4 Building an MCP Server in Python

#### Minimal Server

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
async def greet(name: str) -> str:
    """Greet a user by name."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
```

#### Server with Tools, Resources, and Prompts

```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP(
    "data-server",
    version="0.1.0",
    description="Server for data operations",
)

# --- Tools ---

class QueryParams(BaseModel):
    table: str = Field(description="Table name to query")
    limit: int = Field(default=10, description="Max rows to return")

@mcp.tool()
async def query_data(params: QueryParams) -> dict:
    """Query data from a table with optional limit."""
    # Your implementation here
    return {"table": params.table, "rows": [], "count": 0}

@mcp.tool()
async def analyze_text(text: str, language: str = "en") -> dict:
    """Analyze text for sentiment and key phrases.

    Args:
        text: The text to analyze
        language: ISO language code (default: en)
    """
    return {
        "sentiment": "positive",
        "key_phrases": ["example"],
        "language": language,
    }

# --- Resources ---

@mcp.resource("config://settings")
async def get_settings() -> dict:
    """Return current server settings."""
    return {"version": "0.1.0", "debug": False}

@mcp.resource("schema://{table_name}")
async def get_schema(table_name: str) -> dict:
    """Get the schema for a database table."""
    return {"table": table_name, "columns": []}

# --- Prompts ---

@mcp.prompt()
async def summarize(text: str) -> str:
    """Create a summary prompt for the given text."""
    return f"Please summarize the following text:\n\n{text}"

if __name__ == "__main__":
    mcp.run()
```

#### Server with Context (Logging, Progress)

```python
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("context-server")

@mcp.tool()
async def long_operation(items: list[str], ctx: Context) -> dict:
    """Process a list of items with progress reporting.

    Args:
        items: List of items to process
        ctx: MCP context for logging and progress
    """
    results = []
    total = len(items)

    for i, item in enumerate(items):
        ctx.info(f"Processing item {i+1}/{total}: {item}")
        await ctx.report_progress(i, total)

        # Process item
        results.append({"item": item, "status": "processed"})

    await ctx.report_progress(total, total)
    ctx.info("All items processed successfully")

    return {"processed": len(results), "results": results}
```

#### HTTP Transport Server

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "http-server",
    host="0.0.0.0",
    port=8080,
    stateless_http=True,      # Enable stateless HTTP mode
    json_response=True,       # Return JSON instead of SSE streams
)

@mcp.tool()
async def health_check() -> dict:
    """Check server health status."""
    return {"status": "healthy"}

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

#### Project Setup (pyproject.toml)

```toml
[project]
name = "my-mcp-server"
version = "0.1.0"
description = "My MCP server"
requires-python = ">=3.10"
dependencies = [
    "mcp[cli]>=1.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project.scripts]
my-mcp-server = "my_mcp_server.server:main"
```

#### Testing MCP Servers

```bash
# Development mode with MCP Inspector
mcp dev server.py

# Install for Claude Desktop
mcp install server.py

# Run with stdio transport (default)
uv run server.py

# Run with HTTP transport
uv run server.py --transport streamable-http --port 8080
```

### 6.5 Building an MCP Server in TypeScript

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
  name: "my-ts-server",
  version: "0.1.0",
});

server.tool(
  "greet",
  "Greet a user by name",
  { name: z.string().describe("The user's name") },
  async ({ name }) => ({
    content: [{ type: "text", text: `Hello, ${name}!` }],
  })
);

server.resource(
  "config://settings",
  "Server configuration settings",
  async () => ({
    contents: [{
      uri: "config://settings",
      text: JSON.stringify({ version: "0.1.0" }),
      mimeType: "application/json",
    }],
  })
);

const transport = new StdioServerTransport();
await server.connect(transport);
```

### 6.6 Connecting MCP Servers in Copilot SDK

When building applications with the Copilot SDK, connect to MCP servers programmatically:

#### TypeScript
```typescript
import { CopilotClient } from "@github/copilot-sdk";

const client = new CopilotClient();
const session = await client.createSession({
    model: "gpt-4.1",
    mcpServers: {
        github: {
            type: "http",
            url: "https://api.githubcopilot.com/mcp/",
        },
        filesystem: {
            type: "stdio",
            command: "npx",
            args: ["-y", "@modelcontextprotocol/server-filesystem", "."],
        },
    },
});
```

#### Python
```python
from copilot import CopilotClient

client = CopilotClient()
await client.start()

session = await client.create_session({
    "model": "gpt-4.1",
    "mcp_servers": {
        "github": {
            "type": "http",
            "url": "https://api.githubcopilot.com/mcp/",
        },
        "filesystem": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
        },
    },
})
```

---

## 7. Hooks

Hooks let you run **automated scripts** triggered by specific events during GitHub Copilot coding agent sessions.

### Hook Events

| Event | Trigger |
|---|---|
| `sessionStart` | Coding agent session begins |
| `sessionEnd` | Coding agent session ends |
| `userPromptSubmitted` | User submits a prompt |
| `toolExecuted` | A tool finishes executing |

### Structure

```
.github/hooks/
└── my-hook/
    ├── README.md         # Documentation with frontmatter
    ├── hooks.json        # Event configuration (REQUIRED)
    └── my-script.sh      # Bundled script(s)
```

### README.md Frontmatter

```yaml
---
name: 'Session Logger'
description: 'Logs all Copilot coding agent session activity for audit and analysis'
tags: ['logging', 'audit', 'analytics']
---
```

### hooks.json Format

```json
{
  "version": 1,
  "hooks": {
    "sessionStart": [
      {
        "type": "command",
        "bash": ".github/hooks/session-logger/log-session-start.sh",
        "cwd": ".",
        "timeoutSec": 5
      }
    ],
    "sessionEnd": [
      {
        "type": "command",
        "bash": ".github/hooks/session-logger/log-session-end.sh",
        "cwd": ".",
        "timeoutSec": 5
      }
    ],
    "userPromptSubmitted": [
      {
        "type": "command",
        "bash": ".github/hooks/session-logger/log-prompt.sh",
        "cwd": ".",
        "env": {
          "LOG_LEVEL": "INFO"
        },
        "timeoutSec": 5
      }
    ]
  }
}
```

### Hook Configuration Fields

| Field | Required | Description |
|---|---|---|
| `type` | Yes | Must be `"command"` |
| `bash` | Yes | Path to the script to execute |
| `cwd` | No | Working directory (default: repo root) |
| `timeoutSec` | No | Max execution time in seconds |
| `env` | No | Environment variables for the script |

### Complete Hook Example: Session Logger

**log-session-start.sh:**
```bash
#!/bin/bash
mkdir -p logs/copilot
echo "{\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"event\":\"sessionStart\",\"cwd\":\"$(pwd)\"}" >> logs/copilot/session.log
```

**log-session-end.sh:**
```bash
#!/bin/bash
echo "{\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"event\":\"sessionEnd\"}" >> logs/copilot/session.log
```

### Installation

1. Copy the hook folder to `.github/hooks/` in your repository
2. Make scripts executable: `chmod +x .github/hooks/my-hook/*.sh`
3. Commit to your repository's default branch
4. Add `logs/` to `.gitignore` if logging locally

### Reference

- [GitHub Copilot Hooks Specification](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/use-hooks)

---

## 8. Agentic Workflows

Agentic Workflows are **AI-powered repository automations** that run coding agents inside GitHub Actions. They are defined as Markdown files with YAML frontmatter specifying triggers, permissions, and safe outputs.

### File Format

**Location:** `workflows/` directory
**Extension:** `.md` (Markdown only, no `.yml` or `.lock.yml`)

### Frontmatter (YAML)

```yaml
---
name: "Daily Issues Report"
description: "Generates a daily summary of open issues and recent activity"
on:
  schedule: daily on weekdays
permissions:
  contents: read
  issues: read
safe-outputs:
  create-issue:
    title-prefix: "[daily-report] "
    labels: [report]
---
```

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Human-readable workflow name |
| `description` | Yes | Single-quoted, non-empty description |
| `on` | Yes | Trigger configuration (schedule, events, etc.) |
| `permissions` | Yes | Least-privilege GitHub permissions |
| `safe-outputs` | Recommended | Constrained output actions (issues, PRs, etc.) |

### Complete Workflow Example

```markdown
---
name: "Daily Issues Report"
description: "Generates a daily summary of open issues and recent activity as a GitHub issue"
on:
  schedule: daily on weekdays
permissions:
  contents: read
  issues: read
safe-outputs:
  create-issue:
    title-prefix: "[daily-report] "
    labels: [report]
---

## Daily Issues Report

Create a daily summary of open issues for the team.

## What to Include

- New issues opened in the last 24 hours
- Issues closed or resolved
- Stale issues that need attention
```

### Validation

```bash
# Validate workflow syntax locally (requires GitHub CLI with aw extension)
gh aw compile --validate --no-emit my-workflow.md
```

### Guidelines

- Use **least-privilege permissions** (only request what the workflow needs)
- Use **safe-outputs** to constrain what the agent can create/modify
- Only submit `.md` files (compiled `.lock.yml` files are generated automatically)
- Follow the [GitHub Agentic Workflows Specification](https://github.github.com/gh-aw/reference/workflow-structure/)

---

## 9. Plugins

Plugins **bundle related agents, commands, and skills** into installable packages. They make it easy for teams to share comprehensive toolkits.

### Structure

```
plugins/
└── my-plugin/
    ├── .github/
    │   └── plugin/
    │       └── plugin.json    # Plugin metadata (REQUIRED)
    └── README.md              # Documentation (REQUIRED)
```

### plugin.json Format

```json
{
  "name": "python-mcp-development",
  "description": "Complete toolkit for building MCP servers in Python",
  "version": "1.0.0",
  "keywords": ["python", "mcp", "server"],
  "author": { "name": "Your Name" },
  "repository": "https://github.com/your-org/your-repo",
  "license": "MIT",
  "agents": [
    "./agents/python-mcp-expert.agent.md"
  ],
  "commands": [
    "./commands/create-mcp-server.md"
  ],
  "skills": [
    "./skills/python-mcp-server-generator/"
  ]
}
```

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Lowercase with hyphens, must match directory name |
| `description` | Yes | Non-empty description |
| `version` | Yes | Semantic version (e.g., `"1.0.0"`) |
| `keywords` | No | Array of lowercase hyphenated strings |
| `agents` | No | Array of relative paths to agent files |
| `commands` | No | Array of relative paths to command files |
| `skills` | No | Array of relative paths to skill folders |

### Creating a Plugin

```bash
npm run plugin:create -- --name my-plugin-id
```

### Key Rules

- Plugin content is **declarative**: paths in `agents`, `commands`, `skills` reference source files
- All referenced paths must point to existing files
- Instructions are standalone and **not** part of plugins
- Validate before submitting: `npm run plugin:validate`

---

## 10. GitHub Copilot SDK

The Copilot SDK lets you embed Copilot's agentic workflows into any application programmatically. Available for **TypeScript/Node.js**, **Python**, **Go**, and **.NET**.

### Prerequisites

1. GitHub Copilot CLI installed and authenticated
2. Language runtime: Node.js 18+, Python 3.8+, Go 1.21+, or .NET 8.0+

### Installation

```bash
# Node.js/TypeScript
npm install @github/copilot-sdk tsx

# Python
pip install github-copilot-sdk

# Go
go get github.com/github/copilot-sdk/go

# .NET
dotnet add package GitHub.Copilot.SDK
```

### Quick Start (Python)

```python
import asyncio
from copilot import CopilotClient

async def main():
    client = CopilotClient()
    await client.start()

    session = await client.create_session({"model": "gpt-4.1"})
    response = await session.send_and_wait({"prompt": "What is 2 + 2?"})

    print(response.data.content)
    await client.stop()

asyncio.run(main())
```

### Custom Tools (Python with Pydantic)

```python
import asyncio
import sys
from copilot import CopilotClient
from copilot.tools import define_tool
from copilot.generated.session_events import SessionEventType
from pydantic import BaseModel, Field

class SearchParams(BaseModel):
    query: str = Field(description="Search query string")
    max_results: int = Field(default=5, description="Maximum results to return")

@define_tool(description="Search a knowledge base for relevant documents")
async def search_docs(params: SearchParams) -> dict:
    # Your search implementation here
    return {"query": params.query, "results": [], "total": 0}

async def main():
    client = CopilotClient()
    await client.start()

    session = await client.create_session({
        "model": "gpt-4.1",
        "streaming": True,
        "tools": [search_docs],
    })

    def handle_event(event):
        if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            sys.stdout.write(event.data.delta_content)
            sys.stdout.flush()

    session.on(handle_event)
    await session.send_and_wait({"prompt": "Search for MCP server documentation"})
    await client.stop()

asyncio.run(main())
```

### Custom Tools (TypeScript)

```typescript
import { CopilotClient, defineTool, SessionEvent } from "@github/copilot-sdk";

const searchDocs = defineTool("search_docs", {
    description: "Search a knowledge base for relevant documents",
    parameters: {
        type: "object",
        properties: {
            query: { type: "string", description: "Search query string" },
            max_results: { type: "number", description: "Maximum results", default: 5 },
        },
        required: ["query"],
    },
    handler: async (args: { query: string; max_results?: number }) => {
        // Your search implementation here
        return { query: args.query, results: [], total: 0 };
    },
});

const client = new CopilotClient();
const session = await client.createSession({
    model: "gpt-4.1",
    streaming: true,
    tools: [searchDocs],
});

session.on((event: SessionEvent) => {
    if (event.type === "assistant.message_delta") {
        process.stdout.write(event.data.deltaContent);
    }
});

await session.sendAndWait({ prompt: "Search for MCP documentation" });
await client.stop();
process.exit(0);
```

### MCP Server Integration via SDK

```python
session = await client.create_session({
    "model": "gpt-4.1",
    "mcp_servers": {
        "github": {
            "type": "http",
            "url": "https://api.githubcopilot.com/mcp/",
        },
    },
})
```

### Custom Agents via SDK

```python
session = await client.create_session({
    "model": "gpt-4.1",
    "custom_agents": [{
        "name": "pr-reviewer",
        "display_name": "PR Reviewer",
        "description": "Reviews pull requests for best practices",
        "prompt": "You are an expert code reviewer. Focus on security, performance, and maintainability.",
    }],
})
```

### Session Configuration Options

| Option | Description |
|---|---|
| `model` | LLM to use (`"gpt-4.1"`, `"claude-sonnet-4.5"`, etc.) |
| `sessionId` | Custom session identifier (for persistence) |
| `tools` | Custom tool definitions |
| `mcpServers` / `mcp_servers` | MCP server connections |
| `customAgents` / `custom_agents` | Custom agent personas |
| `systemMessage` / `system_message` | Override default system prompt |
| `streaming` | Enable incremental response chunks |
| `availableTools` | Whitelist of permitted tools |
| `excludedTools` | Blacklist of disabled tools |

### Event Types

| Event | Description |
|---|---|
| `assistant.message` | Complete model response |
| `assistant.message_delta` | Streaming response chunk |
| `tool.execution_start` | Tool invocation started |
| `tool.execution_complete` | Tool execution finished |
| `session.idle` | No active processing |
| `session.error` | Error occurred |

### Client Configuration

| Option | Description | Default |
|---|---|---|
| `cliPath` / `cli_path` | Path to Copilot CLI executable | System PATH |
| `cliUrl` / `cli_url` | Connect to existing server | None |
| `port` | Server communication port | Random |
| `useStdio` / `use_stdio` | Use stdio transport instead of TCP | true |
| `logLevel` / `log_level` | Logging verbosity | `"info"` |
| `autoStart` / `auto_start` | Launch server automatically | true |
| `autoRestart` / `auto_restart` | Restart on crashes | true |
| `cwd` | Working directory for CLI process | Inherited |

### Architecture

```
Your Application
       |
  SDK Client (Python / TS / Go / .NET)
       | JSON-RPC
  Copilot CLI (server mode)
       |
  GitHub (models, auth)
```

---

## 11. Project Setup and Validation

### Initial Setup (for awesome-copilot contributors)

```bash
git clone https://github.com/github/awesome-copilot.git
cd awesome-copilot
npm ci                          # Install dependencies
npm run build                   # Generate README.md + marketplace.json
```

### Validation Commands

```bash
npm run skill:validate          # Validate all skills
npm run plugin:validate         # Validate all plugins
npm run build                   # Rebuild README.md and marketplace.json
bash scripts/fix-line-endings.sh  # Normalize CRLF to LF
```

### Scaffolding Commands

```bash
npm run skill:create -- --name my-skill --description "Skill description"
npm run plugin:create -- --name my-plugin
```

### Pre-commit Checklist

- [ ] Run `npm ci` to install dependencies
- [ ] Run `npm run build` to regenerate README
- [ ] Run `bash scripts/fix-line-endings.sh`
- [ ] Verify all files have proper frontmatter
- [ ] File names follow `lowercase-with-hyphens` convention
- [ ] Test your contribution works with GitHub Copilot
- [ ] Target the `staged` branch (not `main`) for PRs

### Naming Conventions

| Resource | Convention | Example |
|---|---|---|
| Agent | `lowercase-hyphens.agent.md` | `python-mcp-expert.agent.md` |
| Instruction | `lowercase-hyphens.instructions.md` | `python-django.instructions.md` |
| Skill folder | `lowercase-hyphens/` | `python-mcp-server-generator/` |
| Hook folder | `lowercase-hyphens/` | `session-logger/` |
| Workflow | `lowercase-hyphens.md` | `daily-issues-report.md` |
| Plugin folder | `lowercase-hyphens/` | `python-mcp-development/` |

### Frontmatter Rules (All Resources)

1. `description` must be wrapped in **single quotes**
2. `description` must be **non-empty**
3. `name` fields use human-readable format in frontmatter, but file/folder names use hyphens
4. All frontmatter is YAML between `---` delimiters

---

## 12. Quick Reference Cheat Sheet

### Create an Agent

```bash
# 1. Create the file
echo '---
description: '"'"'My agent description'"'"'
name: '"'"'My Agent'"'"'
model: GPT-4.1
tools:
  - codebase
  - terminalCommand
---

You are an expert in [domain]. Help users with [specific tasks].
' > .github/agents/my-agent.agent.md
```

### Create an Instruction

```bash
# 1. Create the file
echo '---
description: '"'"'Instructions for [technology]'"'"'
applyTo: '"'"'**/*.py'"'"'
---

# [Technology] Guidelines

- Rule 1
- Rule 2
' > .github/instructions/my-tech.instructions.md
```

### Configure an MCP Server

```bash
# .vscode/mcp.json for VS Code
cat > .vscode/mcp.json << 'EOF'
{
  "servers": {
    "my-server": {
      "type": "http",
      "url": "https://api.example.com/mcp"
    }
  }
}
EOF
```

### Build a Python MCP Server

```bash
# 1. Create project
mkdir my-mcp-server && cd my-mcp-server
uv init --name my-mcp-server
uv add "mcp[cli]"

# 2. Create server.py
cat > server.py << 'EOF'
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
async def hello(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
EOF

# 3. Test
mcp dev server.py
```

### Add a Hook

```bash
# 1. Create hook directory
mkdir -p .github/hooks/my-hook

# 2. Create hooks.json
cat > .github/hooks/my-hook/hooks.json << 'EOF'
{
  "version": 1,
  "hooks": {
    "sessionStart": [{
      "type": "command",
      "bash": ".github/hooks/my-hook/on-start.sh",
      "timeoutSec": 5
    }]
  }
}
EOF

# 3. Create script
echo '#!/bin/bash
echo "Session started at $(date)"' > .github/hooks/my-hook/on-start.sh
chmod +x .github/hooks/my-hook/on-start.sh
```

---

## 13. Resources

### Official Documentation

- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [GitHub Copilot in VS Code](https://code.visualstudio.com/docs/copilot/overview)
- [GitHub Copilot Hooks Specification](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/use-hooks)
- [GitHub Agentic Workflows Specification](https://github.github.com/gh-aw/reference/workflow-structure/)
- [Agent Skills Specification](https://agentskills.io/specification)

### GitHub Repositories

- [awesome-copilot](https://github.com/github/awesome-copilot) - Community collection of agents, skills, instructions
- [copilot-sdk](https://github.com/github/copilot-sdk) - SDK for embedding Copilot in apps
- [github-mcp-server](https://github.com/github/github-mcp-server) - GitHub's official MCP server
- [MCP Servers Directory](https://github.com/modelcontextprotocol/servers) - Community MCP servers

### MCP Protocol

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

### Key Concepts Summary

| Concept | One-liner |
|---|---|
| **Agent** | A persona you invoke with `@name` in Copilot Chat |
| **Instruction** | Background rules applied automatically by file pattern |
| **Skill** | Deep task knowledge with optional bundled assets |
| **Tool** | A function Copilot can call during reasoning |
| **MCP Server** | External service exposing tools/resources via standard protocol |
| **Hook** | Automated script triggered by coding agent events |
| **Workflow** | AI-powered GitHub Actions automation |
| **Plugin** | Installable bundle of agents, commands, and skills |
