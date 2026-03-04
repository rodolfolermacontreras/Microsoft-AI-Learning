# Migration Guide: Python Agent Project → GitHub Copilot Customization Framework

A complete, agent-executable guide for migrating an existing Python-based AI agent project (with tools, data extraction, utilities) into the GitHub Copilot customization framework for VS Code. This document contains every rule, template, and step needed to perform the migration without external references.

---

## Table of Contents

1. [Concept Mapping: Old World → New World](#1-concept-mapping)
2. [Target Directory Structure](#2-target-directory-structure)
3. [Migration Strategy Overview](#3-migration-strategy-overview)
4. [Step 1: Create the Agent File (.agent.md)](#step-1-create-the-agent-file)
5. [Step 2: Convert Python Tools to an MCP Server](#step-2-convert-python-tools-to-an-mcp-server)
6. [Step 3: Register the MCP Server in VS Code](#step-3-register-the-mcp-server-in-vs-code)
7. [Step 4: Create Instructions Files](#step-4-create-instructions-files)
8. [Step 5: Create Skills for Complex Workflows](#step-5-create-skills-for-complex-workflows)
9. [Step 6: Create a Plugin Bundle](#step-6-create-a-plugin-bundle)
10. [Step 7: Add Hooks (Optional)](#step-7-add-hooks)
11. [Step 8: Add Agentic Workflows (Optional)](#step-8-add-agentic-workflows)
12. [Step 9: Create Global Project Instructions](#step-9-create-global-project-instructions)
13. [Step 10: Validation and Testing](#step-10-validation-and-testing)
14. [Complete Migration Example: End-to-End](#complete-migration-example)
15. [Frontmatter Rules Reference](#frontmatter-rules-reference)
16. [MCP Server Patterns Reference](#mcp-server-patterns-reference)
17. [Troubleshooting](#troubleshooting)
18. [Quick Reference Cheat Sheet](#quick-reference-cheat-sheet)

---

## 1. Concept Mapping

This table maps what you have today to what you will produce in the Copilot framework.

| What You Have (Old) | What It Becomes (New) | Framework Resource Type |
|---|---|---|
| **Main agent script** (e.g., `agent.py`, `main.py`) — the orchestrator with system prompt and LLM calls | **Agent file** (`.agent.md`) — a Markdown file with YAML frontmatter defining the persona, model, and tools | **Agent** |
| **Python tool functions** (e.g., `tools/search.py`, `tools/extract_data.py`) — callables the agent invokes | **MCP Server** — a Python FastMCP server that wraps each tool function with `@mcp.tool()` decorators | **MCP Server (Tools)** |
| **System prompt / personality definition** (hardcoded string or file) | **Agent body** — the Markdown content after the frontmatter in the `.agent.md` file | **Agent** |
| **Coding standards / style rules** (README, comments, linter config) | **Instruction files** (`.instructions.md`) — scoped rules applied automatically by file glob | **Instruction** |
| **Reference docs, templates, schemas** bundled with your agent | **Skill** (`SKILL.md` + `references/` folder) — self-contained knowledge packages with bundled assets | **Skill** |
| **Utility scripts** (setup, data loading, environment prep) | **Skill scripts** (`skills/my-skill/scripts/`) or **Hook scripts** (`.github/hooks/`) | **Skill** or **Hook** |
| **The whole project** as a distributable package | **Plugin** (`plugin.json` + README) — a bundle of agents, skills, and commands for distribution | **Plugin** |
| **Config files** (`.env`, `config.yaml`, API keys) | **MCP server env vars** — passed via `.vscode/mcp.json` using `${input:var}` or `${env:VAR}` syntax | **MCP Config** |
| **Scheduled tasks / cron jobs** | **Agentic Workflows** — Markdown files compiled to GitHub Actions with AI agent capabilities | **Workflow** |
| **Session logging / telemetry** | **Hooks** — bash scripts triggered by Copilot coding agent events (session start/end, prompts) | **Hook** |

### Key Paradigm Shifts

1. **Agents are NOT Python code anymore.** They are Markdown files with YAML frontmatter. The LLM, persona, and tool access are declared, not coded.
2. **Tools become MCP servers.** Your Python tool functions get wrapped in a FastMCP server that speaks the Model Context Protocol. Copilot calls them via this protocol.
3. **Instructions replace hardcoded rules.** Instead of embedding coding standards in a system prompt string, you write `.instructions.md` files that Copilot applies automatically based on file patterns.
4. **Skills replace bundled documentation.** Reference docs, templates, and schemas live in a `SKILL.md` + assets folder structure.
5. **Everything is file-based.** No databases, no deployment pipelines — just files in your repository that VS Code reads.

---

## 2. Target Directory Structure

After migration, your project should look like this:

```
your-project/
├── .github/
│   ├── copilot-instructions.md              # Global instructions (always active)
│   ├── instructions/
│   │   ├── python-standards.instructions.md  # Python coding rules
│   │   └── data-extraction.instructions.md   # Data extraction patterns
│   ├── agents/
│   │   └── my-agent.agent.md                 # Your migrated agent
│   ├── hooks/                                # Optional
│   │   └── session-logger/
│   │       ├── hooks.json
│   │       └── log-session-start.sh
│   └── workflows/                            # Optional
│       └── daily-report.md
├── .vscode/
│   └── mcp.json                              # MCP server registration
├── skills/
│   └── my-domain-knowledge/
│       ├── SKILL.md                          # Skill definition
│       └── references/
│           ├── api-docs.md
│           └── schema.md
├── mcp-server/                               # Your migrated Python tools
│   ├── pyproject.toml
│   ├── server.py                             # FastMCP server wrapping your tools
│   └── tools/                                # Your existing Python tool modules
│       ├── __init__.py
│       ├── search.py
│       ├── extract_data.py
│       └── transform.py
├── plugins/                                  # Optional: for distribution
│   └── my-plugin/
│       ├── .github/
│       │   └── plugin/
│       │       └── plugin.json
│       └── README.md
└── ...your existing project files...
```

---

## 3. Migration Strategy Overview

Execute these steps in order. Each step is independent enough to test before proceeding.

```
Step 1: Create agent file (.agent.md)
  ↓
Step 2: Wrap Python tools in MCP server
  ↓
Step 3: Register MCP server in .vscode/mcp.json
  ↓
Step 4: Create instruction files (.instructions.md)
  ↓
Step 5: Create skills for reference docs/templates
  ↓
Step 6: Bundle into a plugin (optional, for sharing)
  ↓
Step 7: Add hooks (optional, for audit/logging)
  ↓
Step 8: Add workflows (optional, for automation)
  ↓
Step 9: Create global project instructions
  ↓
Step 10: Validate and test everything
```

---

## Step 1: Create the Agent File

### What This Replaces

Your main agent script — the system prompt, the personality, the orchestration logic. In the new framework, all of this is a single Markdown file.

### File Location and Naming

- **Path:** `.github/agents/my-agent-name.agent.md`
- **Naming rule:** Lowercase with hyphens. No spaces, no underscores, no uppercase.
- **Examples:** `data-analyst.agent.md`, `python-mcp-expert.agent.md`, `code-reviewer.agent.md`

### Frontmatter Specification

Every agent file MUST start with YAML frontmatter between `---` delimiters:

```yaml
---
description: 'One-line description of what this agent does'
name: 'Human-Readable Agent Name'
model: GPT-4.1
tools:
  - codebase
  - terminalCommand
  - fetch
---
```

**Frontmatter field rules:**

| Field | Required | Type | Rules |
|---|---|---|---|
| `description` | **YES** | string | MUST be wrapped in single quotes. MUST be non-empty. Should be 10-200 characters. |
| `name` | Recommended | string | Human-readable display name. Single quotes recommended. |
| `model` | Strongly recommended | string | LLM to use. Values: `GPT-4.1`, `claude-sonnet-4.5`, `Claude Sonnet 4`, `o4-mini`, etc. |
| `tools` | Recommended | array | List of built-in tools the agent can access. |

**Available built-in tools (use these exact strings):**

| Tool String | What It Does |
|---|---|
| `codebase` | Search and read files in the workspace |
| `terminalCommand` | Run terminal/shell commands |
| `githubRepo` | Access GitHub repository data (issues, PRs, etc.) |
| `fetch` | Make HTTP requests to external URLs |
| `useDiffEditTool` | Apply code edits via unified diff format |
| `insertEditTool` | Insert code at specific file locations |
| `createFile` | Create new files in the workspace |

### Agent Body (After Frontmatter)

After the closing `---`, write the agent's personality and instructions in Markdown. This is your migrated system prompt.

**Structure your agent body with these sections:**

```markdown
You are [role description]. [One sentence about primary purpose].

## Your Expertise
- Bullet list of knowledge domains
- Technologies you know
- Patterns you follow

## Your Approach
- How you work step by step
- What you always do
- What you never do

## Guidelines
- Specific rules for output
- Error handling behavior
- Tool usage patterns

## Available MCP Tools
- Description of custom tools available via MCP server
- When to use each tool
- Expected inputs and outputs for each tool
```

### Migration Action: Extracting the System Prompt

1. **Find your current system prompt.** It may be:
   - A string variable in your main script (e.g., `SYSTEM_PROMPT = "..."`)
   - A separate file (e.g., `prompts/system.txt`)
   - A template rendered at runtime
   
2. **Extract the core persona.** Remove any framework-specific boilerplate (LangChain/CrewAI/AutoGen agent class definitions, tool binding code, memory setup). Keep only the natural language instructions.

3. **Restructure into the section format** above (Expertise, Approach, Guidelines).

4. **Add a section describing your MCP tools** — the agent needs to know what custom tools are available from your MCP server (Step 2) and when/how to use them.

### Complete Agent File Template

```markdown
---
description: 'Expert data extraction and analysis assistant with Python tools for querying, transforming, and reporting on datasets'
name: 'Data Extraction Agent'
model: GPT-4.1
tools:
  - codebase
  - terminalCommand
  - fetch
---

You are an expert data extraction and analysis assistant. You help users
query data sources, transform datasets, and generate reports using
specialized Python tools available via MCP.

## Your Expertise

- Data extraction from APIs, databases, and files
- Data transformation and cleaning with Python/Pandas
- Report generation and visualization
- SQL query construction and optimization
- File format handling (CSV, JSON, Parquet, Excel)

## Your Approach

1. Understand the user's data need before taking action
2. Use the available MCP tools for data operations — do NOT write raw scripts when a tool exists
3. Validate data quality after extraction
4. Present results in structured, readable format
5. Suggest follow-up analyses when appropriate

## Guidelines

- Always use type-safe parameters when calling tools
- Handle errors gracefully — if a tool fails, explain what went wrong and suggest alternatives
- For large datasets, always ask about row limits before extracting
- Never expose credentials or connection strings in output
- Log progress for long-running operations

## Available MCP Tools

The following tools are provided by the project's MCP server:

- **search_data** — Search across configured data sources by keyword or query
- **extract_table** — Extract a full table or filtered subset from a data source
- **transform_data** — Apply transformations (filter, aggregate, join) to extracted data
- **generate_report** — Create a formatted report from processed data

Use these tools instead of writing ad-hoc scripts. They handle authentication,
connection pooling, and error handling internally.
```

### How to Invoke This Agent in VS Code

Once the file is at `.github/agents/data-extraction.agent.md`, open VS Code Copilot Chat and type:

```
@data-extraction Help me extract user signups from the last 30 days
```

The `@` prefix followed by the filename (minus `.agent.md`) invokes the agent.

---

## Step 2: Convert Python Tools to an MCP Server

### What This Replaces

Your `tools/` folder full of Python functions. In the new framework, these become an **MCP (Model Context Protocol) server** — a small Python program that exposes your functions as tools that Copilot can call.

### What Is MCP

MCP (Model Context Protocol) is an open standard (like HTTP for AI tools). An MCP server exposes:
- **Tools** — functions the AI can call (this is where your Python tools go)
- **Resources** — data the AI can read (configs, schemas, docs)
- **Prompts** — pre-built prompt templates

### Prerequisites

- Python 3.10+
- `uv` package manager (recommended) or `pip`

Install `uv` if you don't have it:
```bash
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 2a: Create the MCP Server Project

Create a directory for your MCP server (can be inside your project or standalone):

```
mcp-server/
├── pyproject.toml
├── server.py
└── tools/              ← Your existing Python tool modules go here
    ├── __init__.py
    ├── search.py
    ├── extract_data.py
    └── transform.py
```

**pyproject.toml:**

```toml
[project]
name = "my-agent-mcp-server"
version = "0.1.0"
description = "MCP server exposing data extraction and analysis tools"
requires-python = ">=3.10"
dependencies = [
    "mcp[cli]>=1.0.0",
    # Add your existing tool dependencies here:
    # "pandas>=2.0",
    # "requests>=2.28",
    # "sqlalchemy>=2.0",
    # etc.
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project.scripts]
my-agent-mcp-server = "server:main"
```

### Step 2b: Wrap Each Tool Function

For EVERY Python tool function in your `tools/` folder, create a corresponding `@mcp.tool()` function in `server.py`.

**The conversion pattern:**

BEFORE (your existing tool):
```python
# tools/search.py
def search_data(query: str, source: str = "default", limit: int = 100) -> list:
    """Search data sources for matching records."""
    # ... your existing implementation ...
    results = do_search(query, source, limit)
    return results
```

AFTER (MCP-wrapped tool):
```python
# server.py
from mcp.server.fastmcp import FastMCP
from tools.search import search_data as _search_data  # import your existing function

mcp = FastMCP("my-agent-server")

@mcp.tool()
async def search_data(query: str, source: str = "default", limit: int = 100) -> dict:
    """Search data sources for matching records.

    Args:
        query: Search query string or keywords
        source: Data source identifier (default: "default")
        limit: Maximum number of results to return (default: 100)
    """
    try:
        results = _search_data(query, source, limit)
        return {"status": "success", "count": len(results), "results": results}
    except Exception as e:
        return {"status": "error", "message": str(e), "results": []}
```

### Conversion Rules

1. **Add `@mcp.tool()` decorator** to every function you want Copilot to be able to call.

2. **Make functions `async`**. If your existing function is synchronous, either:
   - Make the wrapper async and call the sync function directly (Python will handle it)
   - Or use `asyncio.to_thread()` for truly blocking operations:
     ```python
     import asyncio
     
     @mcp.tool()
     async def heavy_extraction(source: str) -> dict:
         """Extract data from a heavy source (runs in thread pool)."""
         result = await asyncio.to_thread(_heavy_sync_function, source)
         return {"data": result}
     ```

3. **Add type hints to ALL parameters and return types.** MCP requires this.
   - Use basic types: `str`, `int`, `float`, `bool`, `list`, `dict`
   - For complex inputs, use Pydantic models:
     ```python
     from pydantic import BaseModel, Field
     
     class ExtractionParams(BaseModel):
         source: str = Field(description="Data source to extract from")
         table: str = Field(description="Table or collection name")
         filters: dict = Field(default={}, description="Key-value filter conditions")
         limit: int = Field(default=1000, description="Max rows to extract")
     
     @mcp.tool()
     async def extract_table(params: ExtractionParams) -> dict:
         """Extract data from a specific table with optional filters."""
         ...
     ```

4. **Write comprehensive docstrings.** The docstring becomes the tool description that the LLM sees. It MUST clearly explain:
   - What the tool does
   - What each parameter means
   - What the tool returns
   - When to use this tool vs. alternatives

5. **Return dicts or Pydantic models, not raw strings.** Always structure your return data:
   ```python
   # GOOD
   return {"status": "success", "count": 42, "data": [...]}
   
   # BAD
   return "Found 42 results"
   ```

6. **Handle errors gracefully.** Wrap tool logic in try/except and return error info:
   ```python
   @mcp.tool()
   async def risky_operation(input: str) -> dict:
       """Perform a risky operation."""
       try:
           result = do_something(input)
           return {"status": "success", "result": result}
       except ConnectionError as e:
           return {"status": "error", "error_type": "connection", "message": str(e)}
       except ValueError as e:
           return {"status": "error", "error_type": "validation", "message": str(e)}
   ```

7. **Log to stderr, NEVER stdout.** stdout is reserved for MCP protocol messages.
   ```python
   import logging
   import sys
   
   logging.basicConfig(level=logging.INFO, stream=sys.stderr)
   logger = logging.getLogger(__name__)
   
   @mcp.tool()
   async def my_tool(data: str) -> dict:
       logger.info(f"Processing data: {data[:50]}...")  # Goes to stderr ✓
       # print("Debug info")  ← NEVER DO THIS — breaks MCP protocol
   ```

8. **Use the Context parameter** for MCP-aware logging and progress reporting:
   ```python
   from mcp.server.fastmcp import FastMCP, Context
   
   @mcp.tool()
   async def batch_process(items: list[str], ctx: Context) -> dict:
       """Process a batch of items with progress reporting."""
       total = len(items)
       results = []
       for i, item in enumerate(items):
           ctx.info(f"Processing {i+1}/{total}: {item}")
           await ctx.report_progress(i, total)
           results.append(process_one(item))
       await ctx.report_progress(total, total)
       return {"processed": len(results), "results": results}
   ```

### Step 2c: Add Resources (Optional)

If your agent has reference data (schemas, configs) that the LLM should be able to read:

```python
@mcp.resource("config://settings")
async def get_settings() -> dict:
    """Return current server configuration."""
    return {
        "version": "0.1.0",
        "sources": ["database", "api", "filesystem"],
        "default_limit": 1000,
    }

@mcp.resource("schema://{source_name}")
async def get_source_schema(source_name: str) -> dict:
    """Get the schema for a specific data source."""
    schemas = load_schemas()  # your existing schema loading logic
    return schemas.get(source_name, {"error": "Unknown source"})
```

### Step 2d: Complete server.py Template

```python
#!/usr/bin/env python3
"""MCP Server — Exposes data extraction and analysis tools to GitHub Copilot."""

import asyncio
import logging
import sys
from mcp.server.fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

# ─── Logging (MUST go to stderr) ───
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

# ─── Import your existing tool implementations ───
# Adjust these imports to match your project structure:
# from tools.search import search_data as _search_data
# from tools.extract_data import extract_table as _extract_table
# from tools.transform import transform_data as _transform_data

# ─── Create the MCP server ───
mcp = FastMCP(
    "my-agent-server",
    version="0.1.0",
    description="Data extraction and analysis tools for the data agent",
)

# ─── Pydantic models for complex inputs ───

class SearchParams(BaseModel):
    query: str = Field(description="Search query string")
    source: str = Field(default="default", description="Data source identifier")
    limit: int = Field(default=100, description="Maximum results to return")

class ExtractionParams(BaseModel):
    source: str = Field(description="Data source to extract from")
    table: str = Field(description="Table or collection name")
    filters: dict = Field(default={}, description="Key-value filter conditions")
    limit: int = Field(default=1000, description="Max rows to extract")

class TransformParams(BaseModel):
    operation: str = Field(description="Transform operation: filter, aggregate, join, pivot")
    data_ref: str = Field(description="Reference to previously extracted data")
    params: dict = Field(default={}, description="Operation-specific parameters")

# ─── Tool definitions ───

@mcp.tool()
async def search_data(params: SearchParams) -> dict:
    """Search across configured data sources by keyword or query.

    Use this tool when the user wants to find specific records, look up
    information, or explore what data is available. Returns matching
    records with metadata.

    Args:
        params: Search parameters including query, source, and limit
    """
    try:
        # Replace with your actual implementation:
        # results = _search_data(params.query, params.source, params.limit)
        results = []  # placeholder
        return {"status": "success", "count": len(results), "results": results}
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def extract_table(params: ExtractionParams, ctx: Context) -> dict:
    """Extract a full table or filtered subset from a data source.

    Use this tool when the user needs to pull data from a specific table
    or collection. Supports filtering and row limits. For large extractions,
    progress will be reported.

    Args:
        params: Extraction parameters including source, table, filters, limit
        ctx: MCP context for progress reporting
    """
    try:
        ctx.info(f"Extracting from {params.source}/{params.table} (limit: {params.limit})")
        # Replace with your actual implementation:
        # data = await asyncio.to_thread(_extract_table, params.source, params.table, params.filters, params.limit)
        data = []  # placeholder
        await ctx.report_progress(1, 1)
        return {"status": "success", "row_count": len(data), "data": data}
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def transform_data(params: TransformParams) -> dict:
    """Apply transformations to previously extracted data.

    Use this tool after extract_table to filter, aggregate, join, or pivot
    the data. Supports chaining multiple transforms.

    Args:
        params: Transform operation, data reference, and operation params
    """
    try:
        # Replace with your actual implementation:
        # result = _transform_data(params.operation, params.data_ref, params.params)
        result = {}  # placeholder
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Transform failed: {e}")
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def generate_report(title: str, data_ref: str, format: str = "markdown") -> dict:
    """Generate a formatted report from processed data.

    Use this tool to create a human-readable report after data extraction
    and transformation. Supports markdown, CSV, and JSON output formats.

    Args:
        title: Report title
        data_ref: Reference to the data to include in the report
        format: Output format — markdown, csv, or json (default: markdown)
    """
    try:
        # Replace with your actual implementation
        report = f"# {title}\n\nReport generated successfully."
        return {"status": "success", "format": format, "content": report}
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return {"status": "error", "message": str(e)}

# ─── Resources (optional — for reference data the LLM can read) ───

@mcp.resource("config://server-info")
async def get_server_info() -> dict:
    """Return server configuration and available data sources."""
    return {
        "version": "0.1.0",
        "available_sources": ["database", "api", "csv-files"],
        "supported_transforms": ["filter", "aggregate", "join", "pivot"],
        "report_formats": ["markdown", "csv", "json"],
    }

# ─── Entry point ───

def main():
    mcp.run()

if __name__ == "__main__":
    main()
```

### Step 2e: Install and Test

```bash
cd mcp-server/

# Install dependencies
uv sync
# OR with pip:
pip install -e ".[dev]"

# Test with MCP Inspector (interactive browser UI)
mcp dev server.py

# Test with stdio transport (what VS Code uses)
uv run server.py
```

The MCP Inspector opens a browser UI where you can call each tool interactively and see the responses. Verify all your tools work before proceeding.

---

## Step 3: Register the MCP Server in VS Code

### What This Does

Tells VS Code where your MCP server is so Copilot can connect to it and use the tools.

### Create `.vscode/mcp.json`

In your project root, create `.vscode/mcp.json`:

**Option A: Local Python server via stdio (most common for development):**

```json
{
  "servers": {
    "my-agent-tools": {
      "command": "uv",
      "args": ["run", "--directory", "${workspaceFolder}/mcp-server", "server.py"],
      "env": {
        "DATABASE_URL": "${input:database_url}",
        "API_KEY": "${input:api_key}"
      }
    }
  }
}
```

**Option B: Using Python directly (if not using uv):**

```json
{
  "servers": {
    "my-agent-tools": {
      "command": "python",
      "args": ["${workspaceFolder}/mcp-server/server.py"],
      "env": {
        "DATABASE_URL": "${input:database_url}"
      }
    }
  }
}
```

**Option C: Using a virtual environment Python:**

```json
{
  "servers": {
    "my-agent-tools": {
      "command": "${workspaceFolder}/.venv/Scripts/python.exe",
      "args": ["${workspaceFolder}/mcp-server/server.py"],
      "env": {}
    }
  }
}
```

**Option D: Docker-based (for production/sharing):**

```json
{
  "servers": {
    "my-agent-tools": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "DATABASE_URL",
        "-v", "${workspaceFolder}:/workspace",
        "my-agent-mcp-server:latest"
      ],
      "env": {
        "DATABASE_URL": "${input:database_url}"
      }
    }
  }
}
```

**Option E: HTTP transport (for remote/shared servers):**

```json
{
  "servers": {
    "my-agent-tools": {
      "type": "http",
      "url": "http://localhost:8080/mcp",
      "headers": {
        "Authorization": "Bearer ${input:api_token}"
      }
    }
  }
}
```

### Variable Syntax in mcp.json

| Syntax | What It Does | When to Use |
|---|---|---|
| `${input:variable_name}` | Prompts the user for input when the server starts | API keys, credentials, one-time config |
| `${env:VARIABLE_NAME}` | Reads from OS environment variables | Pre-configured environments |
| `${workspaceFolder}` | Resolves to the VS Code workspace root | File paths relative to project |

### Verification

After creating `.vscode/mcp.json`:

1. Open VS Code
2. Open the Command Palette (`Ctrl+Shift+P`)
3. Run: `MCP: List Servers`
4. Your server should appear. Click to start it.
5. Open Copilot Chat, the tools should be available.

---

## Step 4: Create Instructions Files

### What This Replaces

Any hardcoded coding standards, style guides, or project-specific rules that were part of your agent's system prompt or README.

### File Location and Naming

- **Path:** `.github/instructions/`
- **Extension:** `.instructions.md`
- **Naming:** Lowercase with hyphens (e.g., `python-standards.instructions.md`)

### Frontmatter Specification

```yaml
---
description: 'Description of what these instructions cover'
applyTo: '**/*.py'
---
```

| Field | Required | Rules |
|---|---|---|
| `description` | **YES** | Single-quoted. Non-empty. 10-200 characters. |
| `applyTo` | **YES** | Glob patterns (comma-separated) for when these instructions activate. |

### Common Glob Patterns

| Pattern | Matches |
|---|---|
| `**/*.py` | All Python files anywhere in the project |
| `**/*.py, **/pyproject.toml, **/requirements.txt` | Python files + config files |
| `tools/**` | Everything under the tools/ directory |
| `**/*.sql` | All SQL files |
| `**/test_*.py, **/*_test.py` | Python test files |
| `**` | ALL files (universal instruction) |
| `**/*.md` | All Markdown files |
| `**/*.json, **/*.yaml, **/*.yml` | All config files |

### Instructions File Template

```markdown
---
description: 'Python coding standards for data extraction tools'
applyTo: '**/*.py'
---

# Python Standards for This Project

## Code Style
- Follow PEP 8
- Use type hints on ALL function parameters and return types
- Maximum line length: 100 characters
- Use f-strings for string formatting

## Naming
- Functions: `snake_case` with verb_noun pattern (e.g., `extract_records`, `validate_input`)
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: prefix with underscore `_`

## Documentation
- All public functions MUST have docstrings
- Use Google-style docstrings:
  ```python
  def func(param: str) -> dict:
      """Brief description.

      Args:
          param: Description of param

      Returns:
          Description of return value

      Raises:
          ValueError: When param is invalid
      """
  ```

## Error Handling
- Always use specific exception types, not bare `except:`
- Log errors before re-raising
- Return structured error responses from tool functions

## Imports
- Standard library first, then third-party, then local
- Use absolute imports
- No wildcard imports (`from module import *`)

## Data Handling
- Always validate input data before processing
- Use Pydantic models for structured data
- Handle None/empty values explicitly
- Set sensible defaults for optional parameters
```

### Create Multiple Instruction Files for Different Concerns

**`.github/instructions/data-extraction.instructions.md`:**
```markdown
---
description: 'Best practices for data extraction tool development'
applyTo: 'tools/**, mcp-server/**'
---

# Data Extraction Standards

- Always include a `limit` parameter with a sensible default (e.g., 1000)
- Validate connection parameters before attempting extraction
- Use connection pooling for database sources
- Log extraction start/end times for performance tracking
- Return row counts alongside data
- Handle pagination for large datasets
- Close connections/cursors in finally blocks
```

**`.github/instructions/testing.instructions.md`:**
```markdown
---
description: 'Testing standards for the project'
applyTo: '**/test_*.py, **/*_test.py, **/conftest.py'
---

# Testing Standards

- Use pytest as the test framework
- Each tool function must have at least one happy-path and one error-path test
- Use fixtures for shared setup (database connections, test data)
- Mock external dependencies (APIs, databases) in unit tests
- Name tests descriptively: `test_search_data_returns_matching_records`
```

---

## Step 5: Create Skills for Complex Workflows

### What This Replaces

Reference documentation, templates, schemas, example code, and any bundled assets that your agent needs for specialized tasks.

### When to Use Skills vs. Instructions

| Use **Instructions** when... | Use **Skills** when... |
|---|---|
| You have coding rules/standards | You have deep reference documentation |
| Rules apply based on file type | Knowledge is loaded on-demand for specific tasks |
| Content is short (< 100 lines) | Content is long or requires bundled assets |
| Rules are universal or per-language | Knowledge is task-specific |

### Skill Structure

```
skills/
└── my-skill-name/
    ├── SKILL.md              # REQUIRED — skill definition
    ├── references/           # Optional — reference docs
    │   ├── api-reference.md
    │   └── schema-guide.md
    └── scripts/              # Optional — helper scripts
        └── setup.sh
```

### SKILL.md Frontmatter

```yaml
---
name: my-skill-name
description: 'Detailed description of what this skill provides (10-1024 chars)'
---
```

| Field | Required | Rules |
|---|---|---|
| `name` | **YES** | Lowercase with hyphens. MUST match the folder name. Max 64 characters. |
| `description` | **YES** | Single-quoted. 10-1024 characters. |

### SKILL.md Body

After the frontmatter, write the skill content in Markdown. Reference any bundled assets using relative paths.

### Skill Template

```markdown
---
name: data-source-schemas
description: 'Reference documentation for all configured data sources, their schemas, and query patterns'
---

# Data Source Schemas

This skill provides schema documentation and query patterns for all data sources
available to the data extraction agent.

## When to Use This Skill

Load this skill when:
- User asks about available data sources or their structure
- Building queries for a specific data source
- Troubleshooting extraction errors related to schema mismatches

## Available Data Sources

### PostgreSQL — Main Database
- **Connection:** Configured via `DATABASE_URL` environment variable
- **Tables:** See [schema reference](references/postgres-schema.md)
- **Query patterns:** Standard SQL with parameterized queries

### REST API — External Service
- **Base URL:** Configured via `API_BASE_URL`
- **Auth:** Bearer token via `API_KEY`
- **Endpoints:** See [API reference](references/api-reference.md)

## Query Patterns

### Basic extraction
```sql
SELECT * FROM {table} WHERE {conditions} LIMIT {limit}
```

### Filtered extraction with date range
```sql
SELECT * FROM {table}
WHERE created_at BETWEEN '{start_date}' AND '{end_date}'
ORDER BY created_at DESC
LIMIT {limit}
```

## Error Handling

| Error | Cause | Resolution |
|---|---|---|
| ConnectionRefused | Database not reachable | Check DATABASE_URL and network |
| AuthenticationFailed | Invalid credentials | Verify API_KEY is set correctly |
| TableNotFound | Wrong table name | Check schema reference docs |
```

### Bundled Assets Rules

- Each asset file must be under **5 MB**
- Assets must be referenced from SKILL.md (unreferenced assets are ignored)
- Supported asset types: `.md`, `.txt`, `.json`, `.yaml`, `.py`, `.sh`, `.sql`, `.csv`
- Place assets in `references/` or `scripts/` subdirectories

---

## Step 6: Create a Plugin Bundle

### What This Does

Packages your agent, skills, and commands into an installable unit that others can use with `copilot plugin install`.

### When to Create a Plugin

- You want to share your agent with others
- You want a one-command install experience
- You have multiple related agents/skills that belong together

### Plugin Structure

```
plugins/
└── my-data-agent/
    ├── .github/
    │   └── plugin/
    │       └── plugin.json
    └── README.md
```

### plugin.json

```json
{
  "name": "my-data-agent",
  "description": "Data extraction and analysis agent with Python MCP tools",
  "version": "1.0.0",
  "keywords": ["data", "extraction", "python", "analysis", "mcp"],
  "author": { "name": "Your Name" },
  "repository": "https://github.com/your-org/your-repo",
  "license": "MIT",
  "agents": [
    "./agents/data-extraction.agent.md"
  ],
  "skills": [
    "./skills/data-source-schemas/"
  ]
}
```

**plugin.json field rules:**

| Field | Required | Rules |
|---|---|---|
| `name` | **YES** | Lowercase with hyphens. MUST match the plugin directory name. |
| `description` | **YES** | Non-empty string. |
| `version` | **YES** | Semantic version: `"MAJOR.MINOR.PATCH"` |
| `keywords` | No | Array of lowercase hyphenated strings. |
| `agents` | No | Array of relative paths to `.agent.md` files. |
| `commands` | No | Array of relative paths to command `.md` files. |
| `skills` | No | Array of relative paths to skill folders (must end with `/`). |

**Key rules:**
- All referenced paths MUST point to existing files/folders
- Instructions are **NOT** part of plugins (they are standalone)
- Plugin name MUST match directory name

### README.md

```markdown
# My Data Agent Plugin

Data extraction and analysis agent with Python MCP tools.

## What's Included

- **Agent:** Data Extraction Agent — expert at querying, transforming, and reporting on data
- **Skill:** Data Source Schemas — reference docs for all available data sources

## Installation

```bash
copilot plugin install my-data-agent@your-org/your-repo
```

## Requirements

- Python 3.10+
- MCP server running (see mcp-server/ directory)

## Setup

1. Install the plugin
2. Configure `.vscode/mcp.json` with your MCP server
3. Use `@data-extraction` in Copilot Chat
```

---

## Step 7: Add Hooks

### What This Does

Runs automated scripts when specific events happen during Copilot coding agent sessions (session start/end, user prompts, tool execution).

### When to Add Hooks

- You want session logging/audit trails
- You want to auto-commit changes after a coding session
- You want to validate prompts before they're processed
- You want to integrate with external systems on events

### Hook Structure

```
.github/hooks/
└── my-hook-name/
    ├── hooks.json          # REQUIRED — event configuration
    ├── README.md           # Documentation
    └── my-script.sh        # Script(s) to execute
```

### hooks.json Specification

```json
{
  "version": 1,
  "hooks": {
    "EVENT_NAME": [
      {
        "type": "command",
        "bash": ".github/hooks/my-hook/script.sh",
        "cwd": ".",
        "timeoutSec": 10,
        "env": {
          "MY_VAR": "value"
        }
      }
    ]
  }
}
```

**Available events:**

| Event | When It Fires |
|---|---|
| `sessionStart` | Copilot coding agent session begins |
| `sessionEnd` | Copilot coding agent session ends |
| `userPromptSubmitted` | User sends a prompt to the coding agent |
| `preToolUse` | Before a tool is executed |
| `postToolUse` | After a tool finishes executing |
| `errorOccurred` | When an error occurs |

**Hook command fields:**

| Field | Required | Description |
|---|---|---|
| `type` | YES | Must be `"command"` |
| `bash` | YES | Path to the script to execute (relative to repo root) |
| `cwd` | No | Working directory (default: repo root) |
| `timeoutSec` | No | Max execution time in seconds |
| `env` | No | Environment variables to pass to the script |

### Session Logger Hook Example

**`.github/hooks/session-logger/hooks.json`:**
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
        "timeoutSec": 5
      }
    ]
  }
}
```

**`.github/hooks/session-logger/log-session-start.sh`:**
```bash
#!/bin/bash
mkdir -p logs/copilot
echo "{\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"event\":\"sessionStart\",\"cwd\":\"$(pwd)\"}" >> logs/copilot/session.log
```

### Installation

1. Copy the hook folder to `.github/hooks/`
2. Make scripts executable: `chmod +x .github/hooks/my-hook/*.sh`
3. Commit to the repository's default branch
4. Add `logs/` to `.gitignore`

---

## Step 8: Add Agentic Workflows

### What This Does

Creates AI-powered automations that run in GitHub Actions — scheduled reports, automated triage, documentation maintenance.

### Workflow File Format

**Location:** `.github/workflows/` 
**Extension:** `.md`

```markdown
---
name: "Daily Data Quality Report"
description: "Generates a daily data quality summary as a GitHub issue"
on:
  schedule: daily on weekdays
permissions:
  contents: read
  issues: write
safe-outputs:
  create-issue:
    title-prefix: "[data-quality] "
    labels: [report, data-quality]
---

## Daily Data Quality Report

Generate a summary of data quality metrics for all configured sources.

## What to Include

- Record counts per source (compared to yesterday)
- Missing value percentages for key fields
- Extraction errors from logs
- Recommendations for attention
```

### Workflow Setup

1. Install GitHub CLI agentic workflows extension: `gh extension install github/gh-aw`
2. Place `.md` file in `.github/workflows/`
3. Compile: `gh aw compile`
4. Commit both the `.md` and generated `.lock.yml`

---

## Step 9: Create Global Project Instructions

### What This Does

Creates a single file with rules that ALWAYS apply to every Copilot interaction in the project, regardless of file type.

### File Location

**Path:** `.github/copilot-instructions.md` (exactly this name, no frontmatter needed)

### Template

```markdown
# Project-Wide Copilot Instructions

## Language and Style
- Primary language: Python 3.10+
- Use type hints on all function parameters and return types
- Follow PEP 8 style guidelines
- Use f-strings for string formatting
- Maximum line length: 100 characters

## Architecture
- MCP tools are in `mcp-server/tools/` — do not duplicate tool logic elsewhere
- Agent definitions are in `.github/agents/` — do not hardcode prompts in Python
- Reference docs are in `skills/` — link to them, don't inline large docs

## Git Practices
- Use conventional commits: feat:, fix:, docs:, refactor:, test:, chore:
- Never commit secrets, API keys, or connection strings
- All new tool functions need corresponding tests

## Error Handling
- Always use specific exception types
- Log errors to stderr before re-raising
- Return structured error responses from tools

## Data Handling
- Always validate input data before processing
- Include row limits on all extraction functions
- Handle None/empty values explicitly
- Use Pydantic models for complex data structures
```

---

## Step 10: Validation and Testing

### Test the Agent

1. Open your project in VS Code
2. Ensure the MCP server is configured in `.vscode/mcp.json`
3. Open Copilot Chat (`Ctrl+Shift+I`)
4. Type `@your-agent-name` followed by a test prompt
5. Verify:
   - The agent responds with the correct persona
   - MCP tools are available and callable
   - Tool results are correctly formatted
   - Instructions are being followed (check code style, etc.)

### Test MCP Tools Independently

```bash
cd mcp-server/

# Interactive testing with MCP Inspector
mcp dev server.py

# This opens a browser UI where you can:
# - See all registered tools
# - Call each tool with test parameters
# - Inspect responses
# - Check for errors
```

### Validate Plugin Structure (if applicable)

If you're contributing to awesome-copilot or using the validation scripts:

```bash
cd awesome-copilot
npm ci
npm run plugin:validate    # Validates all plugin.json files
npm run skill:validate     # Validates all SKILL.md files
npm run build              # Regenerates README.md + marketplace.json
```

### Checklist

- [ ] Agent file has valid YAML frontmatter with `description` in single quotes
- [ ] Agent file is named lowercase-with-hyphens.agent.md
- [ ] MCP server starts without errors
- [ ] All tools have type hints on parameters and return types
- [ ] All tools have comprehensive docstrings
- [ ] All tools return dicts/structured data (not raw strings)
- [ ] All tools handle errors with try/except
- [ ] `.vscode/mcp.json` correctly points to the MCP server
- [ ] Instruction files have `description` (single-quoted) and `applyTo` in frontmatter
- [ ] Skill folders have a `SKILL.md` with `name` and `description` frontmatter
- [ ] Skill `name` matches folder name exactly
- [ ] No logging to stdout in MCP server code
- [ ] Plugin `name` matches directory name (if creating a plugin)
- [ ] All file/folder names use lowercase-with-hyphens convention

---

## Complete Migration Example

### Source: A Python Agent with Tools

**Before (old structure):**
```
my-old-agent/
├── agent.py                 # Main agent with LLM calls
├── config.py                # Configuration
├── prompts/
│   └── system.txt           # System prompt
├── tools/
│   ├── __init__.py
│   ├── search.py            # search_records(query, source)
│   ├── extract.py           # extract_table(source, table, filters)
│   └── report.py            # generate_report(data, format)
├── data/
│   └── schema.json          # Data source schemas
├── requirements.txt
└── README.md
```

### Target: Copilot Framework Structure

**After (new structure):**
```
my-project/
├── .github/
│   ├── copilot-instructions.md
│   ├── instructions/
│   │   ├── python-standards.instructions.md
│   │   └── data-extraction.instructions.md
│   └── agents/
│       └── data-agent.agent.md
├── .vscode/
│   └── mcp.json
├── skills/
│   └── data-source-schemas/
│       ├── SKILL.md
│       └── references/
│           └── schema-guide.md
├── mcp-server/
│   ├── pyproject.toml
│   ├── server.py
│   └── tools/                ← COPIED from old project
│       ├── __init__.py
│       ├── search.py
│       ├── extract.py
│       └── report.py
└── ... (rest of your project)
```

### Migration Steps Applied

**1. Copy `tools/` into `mcp-server/tools/`** — your existing Python code stays intact.

**2. Create `mcp-server/server.py`** — wraps each function from `tools/` with `@mcp.tool()`.

**3. Create `mcp-server/pyproject.toml`** — lists `mcp[cli]` plus your existing `requirements.txt` dependencies.

**4. Extract system prompt from `prompts/system.txt` → `.github/agents/data-agent.agent.md`** — restructured into Expertise/Approach/Guidelines sections.

**5. Extract coding rules → `.github/instructions/python-standards.instructions.md`**.

**6. Move schema docs → `skills/data-source-schemas/references/schema-guide.md`**.

**7. Create `.vscode/mcp.json`** — points to `mcp-server/server.py`.

**8. Create `.github/copilot-instructions.md`** — global project rules.

---

## Frontmatter Rules Reference

These rules apply to ALL resource types. Violations will cause validation failures.

| Rule | Details |
|---|---|
| **Delimiter** | Frontmatter is YAML between two `---` lines at the top of the file |
| **description — required** | MUST be present. MUST be non-empty. MUST be wrapped in single quotes. |
| **description — quotes** | Use single quotes: `description: 'My description here'` |
| **description — escaping** | If description contains a single quote, escape as `''`: `description: 'It''s great'` |
| **name — convention** | File/folder names: lowercase-with-hyphens. Frontmatter name: human-readable. |
| **applyTo (instructions)** | Glob patterns, comma-separated. Required for instruction files. |
| **name (skills)** | MUST match the folder name exactly. Max 64 characters. |

### Frontmatter Examples by Resource Type

**Agent:**
```yaml
---
description: 'Expert Python data extraction assistant'
name: 'Data Agent'
model: GPT-4.1
tools:
  - codebase
  - terminalCommand
---
```

**Instruction:**
```yaml
---
description: 'Python coding standards for the project'
applyTo: '**/*.py'
---
```

**Skill:**
```yaml
---
name: my-skill-name
description: 'Deep reference documentation for data sources'
---
```

**Hook (README.md only):**
```yaml
---
name: 'Session Logger'
description: 'Logs Copilot session activity for auditing'
tags: ['logging', 'audit']
---
```

**Workflow:**
```yaml
---
name: "Daily Report"
description: "Generates daily data quality report"
on:
  schedule: daily on weekdays
permissions:
  contents: read
  issues: write
safe-outputs:
  create-issue:
    title-prefix: "[report] "
    labels: [report]
---
```

---

## MCP Server Patterns Reference

### Pattern 1: Simple Tool (No Dependencies)

```python
@mcp.tool()
async def hello(name: str) -> str:
    """Greet a user by name."""
    return f"Hello, {name}!"
```

### Pattern 2: Tool with Pydantic Model Input

```python
from pydantic import BaseModel, Field

class QueryParams(BaseModel):
    query: str = Field(description="Search query")
    limit: int = Field(default=10, description="Max results")

@mcp.tool()
async def search(params: QueryParams) -> dict:
    """Search for records matching the query."""
    results = do_search(params.query, params.limit)
    return {"count": len(results), "results": results}
```

### Pattern 3: Tool with Context (Progress Reporting)

```python
from mcp.server.fastmcp import Context

@mcp.tool()
async def batch_process(items: list[str], ctx: Context) -> dict:
    """Process items with progress reporting."""
    results = []
    for i, item in enumerate(items):
        ctx.info(f"Processing {i+1}/{len(items)}")
        await ctx.report_progress(i, len(items))
        results.append(process(item))
    return {"processed": len(results)}
```

### Pattern 4: Tool Wrapping Sync Code

```python
import asyncio

@mcp.tool()
async def heavy_operation(data: str) -> dict:
    """Run a CPU/IO-heavy operation in a thread."""
    result = await asyncio.to_thread(sync_heavy_function, data)
    return {"result": result}
```

### Pattern 5: Resource (Read-Only Data)

```python
@mcp.resource("config://settings")
async def get_settings() -> dict:
    """Server configuration."""
    return {"version": "0.1.0", "debug": False}

@mcp.resource("schema://{table_name}")
async def get_schema(table_name: str) -> dict:
    """Schema for a specific table."""
    return load_schema(table_name)
```

### Pattern 6: HTTP Transport (Remote Server)

```python
mcp = FastMCP(
    "my-server",
    host="0.0.0.0",
    port=8080,
    stateless_http=True,
    json_response=True,
)

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

---

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Agent not showing in Copilot Chat | File not in `.github/agents/` or root `agents/` | Move file to correct location |
| Agent has no tools | `tools:` array missing from frontmatter | Add `tools:` list to YAML frontmatter |
| MCP server won't start | Missing dependencies | Run `uv sync` or `pip install -e .` in mcp-server/ |
| MCP tools not visible in Copilot | `.vscode/mcp.json` misconfigured | Verify path in `command`/`args` matches your server |
| Tools work in Inspector but not Copilot | Server using stdout for logging | Change all `print()` to `logging.info()` with stderr |
| Frontmatter validation fails | Description not in single quotes | Wrap in single quotes: `description: 'text'` |
| Skill not loading | `name` in SKILL.md doesn't match folder name | Make them match exactly |
| Plugin validation fails | Referenced files don't exist | Check all paths in plugin.json point to real files |
| "Input required" dialog keeps appearing | `${input:var}` in mcp.json | Enter the value or switch to `${env:VAR}` |
| Agent ignores instructions | Instruction `applyTo` doesn't match current file | Check glob pattern matches the files you're editing |

---

## Quick Reference Cheat Sheet

### File Naming Convention (ALL resources)
```
lowercase-with-hyphens
```
- Agent: `my-agent.agent.md`
- Instruction: `my-rules.instructions.md`
- Skill folder: `my-skill/SKILL.md`
- Hook folder: `my-hook/hooks.json`
- Workflow: `my-workflow.md`
- Plugin folder: `my-plugin/plugin.json`

### Minimal Agent (copy-paste starter)
```markdown
---
description: 'Brief description of the agent'
name: 'Agent Name'
model: GPT-4.1
tools:
  - codebase
  - terminalCommand
---

You are an expert in [domain]. You help users with [tasks].

## Your Approach
- Step 1
- Step 2

## Guidelines
- Rule 1
- Rule 2
```

### Minimal MCP Server (copy-paste starter)
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
async def my_tool(param: str) -> dict:
    """Describe what this tool does."""
    return {"result": param}

if __name__ == "__main__":
    mcp.run()
```

### Minimal mcp.json (copy-paste starter)
```json
{
  "servers": {
    "my-tools": {
      "command": "uv",
      "args": ["run", "--directory", "${workspaceFolder}/mcp-server", "server.py"]
    }
  }
}
```

### Minimal Instruction (copy-paste starter)
```markdown
---
description: 'Brief description of these rules'
applyTo: '**/*.py'
---

- Rule 1
- Rule 2
```

### Minimal Skill (copy-paste starter)
```markdown
---
name: my-skill-name
description: 'What this skill provides'
---

# Skill Title

Content here. Reference assets like [this](references/doc.md).
```

### Minimal Plugin (copy-paste starter)
```json
{
  "name": "my-plugin",
  "description": "What this plugin provides",
  "version": "1.0.0",
  "agents": ["./agents/my-agent.agent.md"],
  "skills": ["./skills/my-skill/"]
}
```

### Invoke Agent in VS Code Chat
```
@agent-name your prompt here
```

### Test MCP Server
```bash
cd mcp-server && mcp dev server.py
```
