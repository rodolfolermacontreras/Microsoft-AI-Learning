# VS Code Agents — Deep-Dive Cheatsheet

> In-depth reference for customization and multi-agent orchestration.
> Companion to `07-reference/cheatsheet.md` (quick reference) and
> the full guides in `03-subagents/` and `04-customization/`.

---

## Table of Contents

1. [The Agent Mental Model](#the-agent-mental-model)
2. [Customization Layer — Complete Guide](#customization-layer--complete-guide)
   - [Custom Instructions](#1-custom-instructions)
   - [File-Based Instructions](#2-file-based-instructions)
   - [Custom Agents (.agent.md)](#3-custom-agents-agentmd)
   - [Prompt Files (.prompt.md)](#4-prompt-files-promptmd)
   - [Agent Skills (SKILL.md)](#5-agent-skills-skillmd)
   - [Hooks (Lifecycle Automation)](#6-hooks-lifecycle-automation)
   - [MCP Servers (External Tools)](#7-mcp-servers-external-tools)
   - [Agent Plugins (Marketplace Bundles)](#8-agent-plugins-marketplace-bundles)
3. [Multi-Agent Orchestration — Complete Guide](#multi-agent-orchestration--complete-guide)
   - [Subagents Deep Dive](#subagents-deep-dive)
   - [Pattern 1: Coordinator-Worker](#pattern-1-coordinator-worker)
   - [Pattern 2: Multi-Perspective Review](#pattern-2-multi-perspective-review)
   - [Pattern 3: TDD (Red-Green-Refactor)](#pattern-3-tdd-red-green-refactor)
   - [Pattern 4: Handoff Pipeline](#pattern-4-handoff-pipeline)
   - [Pattern 5: Research-then-Implement](#pattern-5-research-then-implement)
   - [Pattern 6: Parallel Sessions](#pattern-6-parallel-sessions)
   - [Composing Patterns](#composing-patterns)
4. [Agent Invocation Control Matrix](#agent-invocation-control-matrix)
5. [Context Engineering](#context-engineering)
6. [Memory Scopes](#memory-scopes)
7. [Session Lifecycle](#session-lifecycle)
8. [File Locations — Complete Map](#file-locations--complete-map)
9. [Settings Reference](#settings-reference)
10. [Decision Trees](#decision-trees)

---

## The Agent Mental Model

```
┌─────────────────────────────────────────────────────────┐
│                    YOUR PROMPT                          │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  CONTEXT ASSEMBLY                                       │
│  ┌──────────────┐ ┌──────────────┐ ┌─────────────────┐ │
│  │ System prompt │ │ Instructions │ │ Agent definition│ │
│  └──────────────┘ └──────────────┘ └─────────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ ┌─────────────────┐ │
│  │ History      │ │ # references │ │ Tool outputs    │ │
│  └──────────────┘ └──────────────┘ └─────────────────┘ │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  AGENT LOOP                                             │
│                                                         │
│  UNDERSTAND ──► ACT ──► VALIDATE ──┐                    │
│      ▲                             │                    │
│      └──── (if errors) ◄──────────┘                    │
│                                                         │
│  Tools: read, search, edit, create, runInTerminal,      │
│         fetch, codebase, problems, usages, changes,     │
│         githubRepo, terminalLastCommand, runSubagent    │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
                   RESULT
```

**Key insight**: Everything above the AGENT LOOP box is what you control
through customization. The 7 customization mechanisms each inject into
different parts of that context assembly.

---

## Customization Layer — Complete Guide

The 7 mechanisms, ordered from simplest to most powerful:

```
Simplicity ◄──────────────────────────────────────────► Power

Instructions  →  File-Based  →  Prompts  →  Skills  →  Agents  →  Hooks  →  MCP
  (always on)   (conditional)  (manual)   (on-demand) (personas) (enforce) (extend)
```

---

### 1. Custom Instructions

**What**: Markdown rules auto-included in EVERY chat request.
**When**: Project conventions the AI cannot infer from code alone.

#### File: `.github/copilot-instructions.md`

```markdown
# Project Coding Guidelines

## Architecture
- This is a Python FastAPI monorepo with React frontend
- Backend: src/api/    Frontend: src/web/    Shared types: src/shared/

## Code Style
- Use type hints for ALL function signatures
- Prefer f-strings over .format()
- Error handling: always use specific exception types
- Logging: use structlog, never print()

## Testing
- pytest with fixtures in conftest.py
- Name tests: test_<function>_<scenario>_<expected>
- Mock external services, never hit real APIs in tests

## Git
- Conventional commits: feat:, fix:, docs:, refactor:, test:, chore:
- One logical change per commit
```

#### Cross-Tool Files (Also Always-On)

| File | Where | Works With |
|------|-------|-----------|
| `AGENTS.md` | Project root or subfolders | VS Code, Claude Code, Copilot CLI |
| `CLAUDE.md` | Project root, `.claude/`, or `~/` | Claude Code, VS Code |
| Org instructions | GitHub org Copilot settings | All repos in the org |

#### Rules of Thumb

- Keep under ~500 lines (loaded on every request = token cost)
- Focus on what the AI CANNOT see: architecture decisions, naming reasons, non-obvious conventions
- Show examples of preferred AND avoided patterns
- Explain WHY behind rules (helps the AI handle edge cases)

---

### 2. File-Based Instructions

**What**: Conditional rules applied only when working with matching files.
**When**: Language-specific or domain-specific conventions.

#### File: `.github/instructions/<name>.instructions.md`

```markdown
---
name: Python Standards
description: PEP 8 and project conventions for Python files
applyTo: '**/*.py'
---

# Python Standards

- Follow PEP 8
- Type hints on all function signatures
- Docstrings for all public functions (Google style)
- Import order: stdlib → third-party → local (use isort)
- Use `with` for resource management
- Never bare `except:` — always catch specific exceptions
```

```markdown
---
name: React Component Rules
description: Standards for React components
applyTo: 'src/web/components/**/*.tsx'
---

- Functional components only (no class components)
- Props interface named {ComponentName}Props
- Use CSS modules for styling
- Export component as default
- Co-locate tests: ComponentName.test.tsx
```

```markdown
---
name: API Route Rules
description: FastAPI endpoint conventions
applyTo: 'src/api/routes/**/*.py'
---

- Use dependency injection for database sessions
- All endpoints return Pydantic response models
- Use HTTPException for error responses with specific status codes
- Add OpenAPI description to every endpoint
```

#### Glob Pattern Examples

| Pattern | Matches |
|---------|---------|
| `**/*.py` | All Python files |
| `src/api/**` | Everything under src/api/ |
| `**/*.test.{ts,js}` | All JS/TS test files |
| `**/migrations/**` | All database migration files |
| `Dockerfile*` | All Dockerfiles |

---

### 3. Custom Agents (.agent.md)

**What**: Specialized AI personas with their own tools, models, instructions, and handoffs.
**When**: You want repeatable, role-based behavior — or multi-agent orchestration.

#### File: `.github/agents/<Name>.agent.md`

#### Complete Frontmatter Reference

```yaml
---
# Identity
name: Feature Builder              # Display name in picker
description: Build features end-to-end  # Placeholder text in chat input
argument-hint: feature description  # Hint for user input

# Capabilities
tools:                              # Available tools (array)
  - read                            # Read file contents
  - search                          # Text search across codebase
  - codebase                        # Semantic codebase search
  - edit                            # Edit existing files
  - create                          # Create new files
  - runInTerminal                   # Execute terminal commands
  - problems                        # Get compiler/lint errors
  - usages                          # Find code references
  - changes                         # View git changes
  - fetch                           # Fetch web content
  - githubRepo                      # Access GitHub repos
  - agent                           # Spawn subagents (REQUIRED for orchestration)
  - terminalLastCommand             # Get last terminal output

# Model
model: Claude Sonnet 4.5 (copilot)                  # Single model
model: ['Claude Sonnet 4.5 (copilot)', 'GPT-5 (copilot)']  # Fallback priority list

# Subagent Control
agents: ['Planner', 'Implementer', 'Reviewer']  # Restrict which subagents this agent can use
agents: '*'                                       # Allow all agents as subagents (default)
agents: []                                        # Disable subagent use entirely

# Invocation Control
user-invocable: true               # Show in agent picker dropdown (default: true)
disable-model-invocation: false    # Can be auto-invoked as subagent (default: false)

# Execution Target
target: vscode                     # Run in VS Code (default)
target: github-copilot             # Run on GitHub infrastructure

# Handoffs — guided transitions to other agents
handoffs:
  - label: Start Implementation    # Button text shown to user
    agent: Implementer             # Target agent name
    prompt: |                      # Pre-filled prompt
      Implement the plan above step by step.
      Run tests after each major change.
    send: false                    # false = user reviews before sending (default)
    model: GPT-5.2 (copilot)      # Override model for the target session
---

# Agent Instructions (Markdown body)

Your detailed instructions here. This is the system prompt
for this agent's sessions.
```

#### Agent Design Patterns

**Read-Only Analyst** (safe for subagent delegation):
```yaml
tools: ['read', 'search', 'codebase', 'problems', 'usages']
```

**Full Implementer** (needs all write tools):
```yaml
tools: ['read', 'search', 'edit', 'create', 'runInTerminal', 'problems']
```

**Orchestrator** (delegates everything, does little itself):
```yaml
tools: ['agent', 'read', 'search']
agents: ['Planner', 'Implementer', 'Reviewer']
```

**Subagent-Only Worker** (hidden from user, invoked by coordinator):
```yaml
user-invocable: false
disable-model-invocation: false
```

**User-Only Agent** (never auto-invoked as subagent):
```yaml
user-invocable: true
disable-model-invocation: true
```

**Cost-Optimized Worker** (cheaper model for routine subtasks):
```yaml
user-invocable: false
model: ['Claude Haiku 4.5 (copilot)', 'Gemini 3 Flash (Preview) (copilot)']
```

---

### 4. Prompt Files (.prompt.md)

**What**: Reusable task templates invoked with `/command-name`.
**When**: Repetitive workflows you run manually (scaffolding, audits, reports).

#### File: `.github/prompts/<name>.prompt.md`

```markdown
---
name: create-api-endpoint
description: Scaffold a new FastAPI endpoint with tests
argument-hint: endpoint name and HTTP method
agent: agent
model: Claude Sonnet 4.5 (copilot)
tools: ['edit', 'create', 'read', 'search', 'runInTerminal']
---

Create a new FastAPI endpoint based on this description: ${input:description}

## Files to Create/Modify

1. **Route**: `src/api/routes/${input:name}.py`
   - FastAPI router with the endpoint
   - Pydantic request/response models
   - Dependency injection for DB session

2. **Tests**: `tests/api/test_${input:name}.py`
   - Happy path test
   - Validation error test
   - Not found test

3. **Register**: Add the router to `src/api/main.py`

Follow patterns in existing routes. Reference #file:src/api/routes/users.py
```

#### Variables Available in Prompts

| Variable | Resolves To |
|----------|-------------|
| `${input:varName}` | User input (prompted at invocation) |
| `${input:varName:placeholder}` | User input with hint text |
| `${workspaceFolder}` | Workspace root path |
| `${file}` | Current file path |
| `${fileBasename}` | Current file name |
| `${selection}` | Current editor selection |

#### Prompt vs Agent vs Instruction

| Need | Use |
|------|-----|
| "Always follow these rules" | Instructions |
| "When I say `/deploy`, do this workflow" | Prompt file |
| "Act as a security reviewer with these tools" | Custom agent |

---

### 5. Agent Skills (SKILL.md)

**What**: Portable, on-demand capabilities that load only when relevant.
**When**: Reusable expertise you want across projects and tools (VS Code + CLI + coding agent).

#### File: `.github/skills/<skill-name>/SKILL.md`

```markdown
---
name: database-migrations
description: >
  Create and manage database migrations with Alembic.
  Use when adding/modifying database models, creating migrations,
  or troubleshooting migration failures.
argument-hint: migration description
---

# Database Migration Skill

## Pre-Flight Checks
1. Verify `alembic.ini` exists at project root
2. Check current migration head: `alembic current`
3. Confirm database connection string in environment

## Creating a New Migration
```bash
alembic revision --autogenerate -m "${input:description}"
```

## Applying Migrations
```bash
# Upgrade to latest
alembic upgrade head

# Upgrade one step
alembic upgrade +1

# Downgrade one step
alembic downgrade -1
```

## Troubleshooting
- If autogenerate misses changes: check `env.py` target_metadata
- If migration fails: check for data-dependent DDL
- Multiple heads: `alembic merge heads -m "merge"`

## Project-Specific Notes
- Models are in `src/models/`
- Always review autogenerated migrations before applying
- Add data migrations manually when needed
```

#### Progressive Disclosure (How Skills Load)

```
Level 1 — DISCOVERY (cheap: name + description only)
    AI reads frontmatter across all installed skills
    Token cost: ~50 tokens per skill

Level 2 — INSTRUCTIONS (medium: full SKILL.md body)
    AI loads the full markdown when the task matches description
    Token cost: varies by skill size

Level 3 — RESOURCES (on-demand: files in skill directory)
    AI reads templates, scripts, examples in the skill folder
    Token cost: only what is accessed
```

This means you can install dozens of skills with minimal context cost.

#### Skill vs Instruction vs Prompt

| Dimension | Skill | Instruction | Prompt |
|-----------|-------|-------------|--------|
| Loading | On-demand (AI decides) | Always included | Manual (`/command`) |
| Portability | VS Code, CLI, coding agent | VS Code only | VS Code only |
| Can include scripts/files | Yes (whole directory) | No (single .md) | No (single .md) |
| Standard | Open (agentskills.io) | VS Code-specific | VS Code-specific |

---

### 6. Hooks (Lifecycle Automation)

**What**: Shell commands that run at specific agent lifecycle events.
**When**: Enforce policies, automate formatting, inject context, block dangerous actions.

#### File: `.github/hooks/<name>.json`

#### Complete Hook Reference

```jsonc
{
  "hooks": {
    // Fires on the first prompt of a session
    "SessionStart": [
      {
        "type": "command",
        "command": "python3 ./scripts/inject-project-context.py",
        "windows": "python ./scripts/inject-project-context.py",
        "timeout": 10
      }
    ],

    // Fires when the user sends a message
    "UserPromptSubmit": [
      {
        "type": "command",
        "command": "python3 ./scripts/audit-prompt.py",
        "timeout": 5
      }
    ],

    // Fires BEFORE a tool runs — can block or modify
    "PreToolUse": [
      {
        "type": "command",
        "command": "python3 ./scripts/block-dangerous-commands.py",
        "timeout": 5
      }
    ],

    // Fires AFTER a tool completes — can format, log, or block continuation
    "PostToolUse": [
      {
        "type": "command",
        "command": "npx prettier --write \"$TOOL_INPUT_FILE_PATH\"",
        "windows": "npx prettier --write \"%TOOL_INPUT_FILE_PATH%\"",
        "timeout": 15
      }
    ],

    // Fires before context compaction
    "PreCompact": [
      {
        "type": "command",
        "command": "python3 ./scripts/export-state.py",
        "timeout": 10
      }
    ],

    // Fires when a subagent is spawned
    "SubagentStart": [
      {
        "type": "command",
        "command": "python3 ./scripts/track-subagent.py",
        "timeout": 5
      }
    ],

    // Fires when a subagent completes
    "SubagentStop": [
      {
        "type": "command",
        "command": "python3 ./scripts/aggregate-results.py",
        "timeout": 10
      }
    ],

    // Fires when the agent wants to stop — can force continuation
    "Stop": [
      {
        "type": "command",
        "command": "python3 ./scripts/ensure-tests-ran.py",
        "timeout": 30
      }
    ]
  }
}
```

#### Hook I/O Protocol

Hooks receive JSON on **stdin** and must return JSON on **stdout**.

**Exit codes**:
| Code | Meaning |
|------|---------|
| `0` | Success — parse stdout JSON |
| `2` | Block — stop processing, report error to model |
| Any other | Warning — show to user, continue |

**PreToolUse output** (control tool execution):
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "rm -rf blocked by policy",
    "updatedInput": {},
    "additionalContext": "Use a safer alternative"
  }
}
```

Permission decisions: `allow` > `ask` > `deny` (most restrictive wins when multiple hooks fire).

**Stop hook output** (prevent premature completion):
```json
{
  "hookSpecificOutput": {
    "hookEventName": "Stop",
    "decision": "block",
    "reason": "Tests have not been executed. Run: npm test"
  }
}
```

> **Warning**: In Stop hooks, always check `stop_hook_active` to prevent infinite loops.

#### Practical Hook Recipes

**Block `rm -rf`, `DROP TABLE`, force pushes**:
```python
# scripts/block-dangerous-commands.py
import json, sys, re

data = json.load(sys.stdin)
tool_name = data.get("toolName", "")
tool_input = json.dumps(data.get("toolInput", {}))

BLOCKED = [
    r"rm\s+-rf\s+/",
    r"DROP\s+TABLE",
    r"DROP\s+DATABASE",
    r"git\s+push\s+--force",
    r":(){ :|:& };:",
]

for pattern in BLOCKED:
    if re.search(pattern, tool_input, re.IGNORECASE):
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Blocked: matches dangerous pattern '{pattern}'"
            }
        }
        json.dump(result, sys.stdout)
        sys.exit(2)

sys.exit(0)
```

**Inject project context at session start**:
```python
# scripts/inject-project-context.py
import json, subprocess, sys

branch = subprocess.check_output(["git", "branch", "--show-current"]).decode().strip()
result = {
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": f"Current branch: {branch}. Run tests with: pytest -x"
    }
}
json.dump(result, sys.stdout)
```

---

### 7. MCP Servers (External Tools)

**What**: External tools/data sources connected via Model Context Protocol.
**When**: Database queries, browser automation, API calls, custom integrations.

#### File: `.vscode/mcp.json`

```jsonc
{
  "servers": {
    // HTTP-based MCP server (remote)
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp"
    },

    // Local process-based MCP server
    "playwright": {
      "command": "npx",
      "args": ["-y", "@microsoft/mcp-server-playwright"]
    },

    // Database access with sandboxing
    "database": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db", "./data/app.sqlite"],
      "sandboxEnabled": true,
      "sandbox": {
        "filesystem": {
          "allowWrite": ["${workspaceFolder}/data"]
        },
        "network": {
          "allowedDomains": []
        }
      }
    },

    // Custom Python MCP server
    "my-tools": {
      "command": "python3",
      "args": ["./mcp-servers/my-tools/server.py"],
      "env": {
        "API_KEY": "${input:apiKey}"
      }
    }
  }
}
```

#### MCP Capabilities

| Capability | What Agents See | How to Use |
|------------|----------------|-----------|
| **Tools** | Functions to call (e.g., `query_database`) | Automatic via tools picker |
| **Resources** | Data context (tables, files, schemas) | Add Context > MCP Resources |
| **Prompts** | Pre-built templates | `/<server>.<prompt>` in chat |
| **MCP Apps** | Interactive UI widgets | Rendered inline in chat |

#### Security Checklist for MCP

- [ ] Only add servers from trusted sources
- [ ] Never hardcode API keys — use `${input:varName}` or `.env` files
- [ ] Enable `sandboxEnabled` for servers that don't need full access
- [ ] Restrict `filesystem.allowWrite` to specific directories
- [ ] Restrict `network.allowedDomains` to required hosts
- [ ] Review server source code before first run
- [ ] Trust confirmation dialog appears for new servers

---

### 8. Agent Plugins (Marketplace Bundles)

**What**: Installable packages bundling agents + skills + hooks + MCP servers.
**When**: Prepackaged capabilities from the community or your organization.

```
Extensions view (Ctrl+Shift+X) → Search "@agentPlugins" → Install
```

Custom marketplaces:
```json
"chat.plugins.marketplaces": [
    "copilot-plugins",
    "awesome-copilot",
    "myorg/internal-plugins"
]
```

Local plugins:
```json
"chat.plugins.paths": {
    "/path/to/my-plugin": true,
    "/path/to/disabled-one": false
}
```

---

## Multi-Agent Orchestration — Complete Guide

### Subagents Deep Dive

A subagent is a child agent spawned within a session via `runSubagent`. It runs
in its **own isolated context window** and returns only a summary to the parent.

```
┌─────────────────────────────────────────────────────────┐
│  MAIN AGENT (your session)                              │
│                                                         │
│  Context: [system + instructions + history + your work] │
│                                                         │
│  → runSubagent("Research auth patterns")                │
│      ┌─────────────────────────────────────┐            │
│      │  SUBAGENT A (isolated context)      │            │
│      │  - Reads 15 files                   │            │
│      │  - Searches codebase 8 times        │            │
│      │  - Fetches 3 web pages              │            │
│      │  - Returns: 200-word summary        │            │
│      └─────────────────────────────────────┘            │
│                                                         │
│  ← Only the summary enters main context                 │
│    (not the 15 file reads or 8 searches)                │
│                                                         │
│  Main agent continues with focused context              │
└─────────────────────────────────────────────────────────┘
```

#### Why This Matters

| Benefit | Without Subagents | With Subagents |
|---------|-------------------|----------------|
| Context pollution | Research + implementation compete for space | Research stays isolated |
| Token cost | All intermediate steps in one context | Only summaries flow back |
| Parallel work | Sequential only | Multiple subagents run concurrently |
| Dead-end cost | Full exploration pollutes context | Only summary (or nothing) returns |
| Specialization | One model/toolset for everything | Different model per subtask |

#### How to Trigger Subagent Use

**Agent-initiated** (the AI decides):
```
"Research the best auth approach, then implement it."
```

**Hinting parallel execution**:
```
"Simultaneously analyze security, performance, and accessibility."
```

**Forced via custom agent instructions**:
```markdown
---
name: Feature Builder
tools: ['agent', 'edit', 'read', 'search']
---
For each feature:
1. Use a subagent to research existing patterns
2. Use a subagent to review documentation
3. Implement based on findings
```

#### Subagent vs Other Delegation

| Mechanism | Context | Scope | Use Case |
|-----------|---------|-------|----------|
| **Subagent** | Isolated child context | Within a session | Research, analysis, specialized subtasks |
| **Handoff** | Full conversation carries over | Between agent sessions | Plan → implement → review pipeline |
| **Background agent** | Separate worktree | Independent process | Autonomous long-running tasks |
| **Cloud agent** | Remote branch | GitHub infrastructure | PR-based team collaboration |
| **New session** | Completely fresh | No connection | Unrelated tasks |

---

### Pattern 1: Coordinator-Worker

One coordinator delegates to specialized workers. Each worker has narrower tools
and a cheaper model for cost efficiency.

#### Full Implementation

**File: `.github/agents/Feature-Builder.agent.md`**
```markdown
---
name: Feature Builder
description: Build features end-to-end with research, planning, implementation, and review
tools: ['agent', 'edit', 'search', 'read']
agents: ['Planner', 'Plan-Architect', 'Implementer', 'Reviewer']
---

You are a feature development coordinator. For each feature request:

1. **Research**: Use the Planner agent to break down the feature into tasks.
2. **Validate**: Use the Plan Architect agent to validate against codebase patterns.
3. **Iterate Plan**: If the architect identifies issues, send feedback to update the plan.
4. **Implement**: Use the Implementer agent for each task in the plan.
5. **Review**: Use the Reviewer agent to check the implementation.
6. **Fix**: If the reviewer finds issues, use the Implementer again.
7. **Report**: Summarize what was done, what was tested, and any remaining items.

Iterate between planning and implementation until each phase converges.
```

**File: `.github/agents/Planner.agent.md`**
```markdown
---
name: Planner
user-invocable: false
tools: ['read', 'search', 'codebase']
---
Break down feature requests into numbered implementation tasks.
Each task should specify: what to do, which files to modify, and how to verify.
Incorporate feedback from the Plan Architect.
```

**File: `.github/agents/Implementer.agent.md`**
```markdown
---
name: Implementer
user-invocable: false
model: ['Claude Haiku 4.5 (copilot)', 'Gemini 3 Flash (Preview) (copilot)']
tools: ['edit', 'create', 'read', 'search', 'runInTerminal']
---
Write code to complete assigned tasks. Run tests after implementation.
Follow existing codebase patterns. Ask for clarification if the task is ambiguous.
```

**File: `.github/agents/Reviewer.agent.md`**
```markdown
---
name: Reviewer
user-invocable: false
tools: ['read', 'search', 'codebase', 'problems', 'usages']
---
Review code for quality, security, and adherence to project conventions.
DO NOT edit files. Provide findings ranked by severity.
```

**File: `.github/agents/Plan-Architect.agent.md`**
```markdown
---
name: Plan-Architect
user-invocable: false
tools: ['read', 'search', 'codebase']
---
Validate implementation plans against codebase patterns. Check for:
- Reusable patterns the plan should follow
- Missing edge cases
- Dependencies that need updating
- Potential conflicts with existing code
```

---

### Pattern 2: Multi-Perspective Review

Parallel subagents analyze code from independent viewpoints. No subagent sees
another's findings, preventing groupthink.

**File: `.github/agents/Thorough-Reviewer.agent.md`**
```markdown
---
name: Thorough Reviewer
description: Multi-perspective code review with parallel analysis
tools: ['agent', 'read', 'search']
---

You review code through 4 independent perspectives running in parallel.

For each review request, spawn these subagents simultaneously:

1. **Correctness**: Logic errors, edge cases, type issues, race conditions
2. **Code Quality**: Readability, naming, duplication, complexity
3. **Security**: Input validation, injection, data exposure, auth gaps
4. **Architecture**: Pattern consistency, design violations, coupling

After all 4 complete, synthesize into a single report:
- Critical issues (must fix)
- Improvements (should fix)
- Suggestions (nice to have)
- Strengths (what the code does well)
```

**Example invocation**: Select "Thorough Reviewer" → "Review the auth module"

---

### Pattern 3: TDD (Red-Green-Refactor)

Three agents enforce test-driven discipline. The coordinator runs tests between
each phase to verify the cycle.

**File: `.github/agents/TDD.agent.md`**
```markdown
---
name: TDD
description: Test-driven development with Red-Green-Refactor cycle
tools: ['agent', 'edit', 'create', 'read', 'search', 'runInTerminal', 'problems']
agents: ['Red', 'Green', 'Refactor']
---

Implement features using strict TDD:

1. **Red**: Use the Red agent to write failing tests defining expected behavior
2. **Verify Red**: Run the tests — confirm they FAIL for the right reasons
3. **Green**: Use the Green agent to write MINIMUM code to pass
4. **Verify Green**: Run the tests — confirm they all PASS
5. **Refactor**: Use the Refactor agent to improve code quality
6. **Verify Refactor**: Run the tests — confirm they still PASS

If tests fail after refactoring, fix immediately before continuing.
Each cycle produces a testable, working increment.
NEVER skip the Red phase.
```

**File: `.github/agents/Red.agent.md`**
```markdown
---
name: Red
user-invocable: false
tools: ['edit', 'create', 'read', 'search']
---
Write failing tests that define expected behavior. Tests should be specific,
focused, and follow the project's testing conventions. Do NOT write
implementation code. Only tests.
```

**File: `.github/agents/Green.agent.md`**
```markdown
---
name: Green
user-invocable: false
model: ['Claude Haiku 4.5 (copilot)']
tools: ['edit', 'create', 'read']
---
Write the MINIMUM code to make the failing tests pass.
Do not over-engineer. Do not add untested functionality.
```

**File: `.github/agents/Refactor.agent.md`**
```markdown
---
name: Refactor
user-invocable: false
tools: ['edit', 'read', 'search', 'runInTerminal']
---
Improve code quality without changing behavior. Extract functions,
improve names, reduce duplication. After refactoring, run the tests
to confirm they still pass.
```

---

### Pattern 4: Handoff Pipeline

Sequential agent-to-agent transitions with user review gates between stages.
Unlike subagents (within a session), handoffs transfer between separate sessions.

**File: `.github/agents/Pipeline-Planner.agent.md`**
```markdown
---
name: Pipeline Planner
description: Plan features before implementation
tools: ['read', 'search', 'codebase', 'fetch', 'agent']
handoffs:
  - label: Start Implementation
    agent: Pipeline Implementer
    prompt: Implement the plan above step by step. Run tests after each change.
    send: false
---
Research thoroughly. Ask clarifying questions. Output a numbered plan with:
- Step name, what to do, which files, how to verify
- List of files to create/modify
- Risks and decisions made
```

**File: `.github/agents/Pipeline-Implementer.agent.md`**
```markdown
---
name: Pipeline Implementer
description: Implement from approved plans
tools: ['edit', 'create', 'read', 'search', 'runInTerminal']
handoffs:
  - label: Review Code
    agent: Pipeline Reviewer
    prompt: Review the implementation above for quality and security.
    send: false
---
Implement step by step. Run tests after each major change.
Commit at logical checkpoints.
```

**File: `.github/agents/Pipeline-Reviewer.agent.md`**
```markdown
---
name: Pipeline Reviewer
description: Final review gate
tools: ['read', 'search', 'codebase', 'problems', 'usages']
---
Review the implementation for quality, security, and test coverage.
Provide a pass/fail recommendation with specific findings.
```

**User experience**:
```
1. Select "Pipeline Planner" → describe feature
2. Review the plan → click [Start Implementation]
3. Review the code → click [Review Code]
4. Read the review → merge or iterate
```

---

### Pattern 5: Research-then-Implement

The simplest pattern. Uses built-in Plan and Agent modes with no custom setup.

```
1. Ctrl+Alt+I → Select "Plan"
2. "How should we add rate limiting to the API?"
3. Plan agent researches, asks questions, outputs plan
4. Review → click "Start Implementation"
5. Agent mode implements the plan
```

---

### Pattern 6: Parallel Sessions

Multiple independent sessions running simultaneously, each with its own context.

```
Session A (Background):  "Implement auth module"
Session B (Background):  "Implement logging module"
Session C (Local):       "Design the API schema"
Session D (Cloud):       "Set up CI/CD pipeline"
```

Monitor all from the Sessions view. No custom agents needed.

---

### Composing Patterns

Patterns are combinable. A coordinator can use TDD workers, and the reviewer
can be a multi-perspective agent:

```
Coordinator-Worker
├── Planner (Research-then-Implement internally)
├── Implementer (TDD pattern internally)
│   ├── Red agent
│   ├── Green agent
│   └── Refactor agent
└── Reviewer (Multi-Perspective internally)
    ├── Correctness subagent
    ├── Security subagent
    ├── Quality subagent
    └── Architecture subagent
```

---

## Agent Invocation Control Matrix

| `user-invocable` | `disable-model-invocation` | In Dropdown? | Used as Subagent? | Typical Role |
|:-:|:-:|:-:|:-:|:--|
| `true` | `false` | Yes | Yes | General-purpose agent |
| `false` | `false` | No | Yes | Internal worker (Planner, Red, Green) |
| `true` | `true` | Yes | No | Dangerous tool user (manual only) |
| `false` | `true` | No | No | Disabled — use `agents: [...]` on coordinator to re-enable |

---

## Context Engineering

### What Enters the Context Window (Priority Order)

```
1. System instructions (built-in, immutable)
2. Custom instructions (copilot-instructions.md, AGENTS.md)
3. File-based instructions (matching current file's applyTo)
4. Agent definition (.agent.md body)
5. Loaded skills (SKILL.md bodies, on-demand)
6. Your message
7. Conversation history
8. Implicit context (current file, git state, errors)
9. Explicit # references (#file, #web, #codebase)
10. Tool outputs (file reads, search results, terminal output)
```

### Context Budget Strategy

| Layer | Token Cost | Frequency | Strategy |
|-------|-----------|-----------|----------|
| Instructions | Fixed per request | Every request | Keep concise (<500 lines) |
| Agent definition | Fixed per session | Every request in session | One focused page |
| Skills | On-demand | When matched | Can install many; only loaded when used |
| Conversation history | Growing | Compacts when full | Start new sessions; use `/compact` |
| Tool outputs | Variable | Per tool call | Subagents isolate research from main context |

---

## Memory Scopes

| Scope | Persists Across Sessions | Persists Across Workspaces | How to Store |
|-------|:---:|:---:|---|
| **User** | Yes | Yes | `"Remember I prefer tabs and single quotes"` |
| **Repository** | Yes | No | `"Remember this project uses repository pattern"` |
| **Session** | No | No | Automatic (Plan agent saves plan.md here) |

| | Local Memory | Copilot Memory (GitHub) |
|---|---|---|
| Storage | Your machine | GitHub-hosted |
| Scopes | User, repo, session | Repository only |
| Surfaces | VS Code only | Coding agent, code review, CLI |
| Expiration | Manual | Auto (28 days) |

Settings:
```
github.copilot.chat.tools.memory.enabled     → local memory
github.copilot.chat.copilotMemory.enabled     → GitHub-hosted memory
```

---

## Session Lifecycle

```
Create Session → Choose Agent Type → Choose Model → Enter Prompt
      │
      ├── Local (Agent/Plan/Ask): interactive, real-time
      ├── Background (CLI): isolated worktree, async
      └── Cloud (Coding Agent): remote branch → PR
                │
                ├── Work in progress...
                │   ├── Checkpoints created at each step
                │   ├── Follow-up prompts can steer/queue
                │   └── Subagents spawn and return
                │
                ├── Handoff to another agent type
                │   └── Full history carries over
                │
                └── Complete
                    ├── Review diff / PR
                    ├── Apply or reject changes
                    └── Archive or delete session
```

**Handoff paths**:
```
Local ←→ Background ←→ Cloud
  ↑                       ↑
  └───────────────────────┘
```

---

## File Locations — Complete Map

```
project-root/
│
├── .github/
│   ├── copilot-instructions.md          # Always-on instructions
│   ├── instructions/
│   │   ├── python.instructions.md       # applyTo: '**/*.py'
│   │   ├── react.instructions.md        # applyTo: '**/*.tsx'
│   │   └── tests.instructions.md        # applyTo: '**/*.test.*'
│   ├── prompts/
│   │   ├── create-component.prompt.md   # /create-component
│   │   ├── security-review.prompt.md    # /security-review
│   │   └── deploy.prompt.md             # /deploy
│   ├── agents/
│   │   ├── Reviewer.agent.md            # Code review persona
│   │   ├── Planner.agent.md             # Planning persona
│   │   ├── TDD.agent.md                 # TDD coordinator
│   │   ├── Red.agent.md                 # TDD: write failing tests
│   │   ├── Green.agent.md              # TDD: make tests pass
│   │   └── Refactor.agent.md           # TDD: improve quality
│   ├── skills/
│   │   ├── webapp-testing/
│   │   │   └── SKILL.md                # Playwright + Jest skill
│   │   └── database-migrations/
│   │       └── SKILL.md                # Alembic skill
│   └── hooks/
│       └── security-hooks.json          # Lifecycle automation
│
├── .vscode/
│   └── mcp.json                         # MCP server configuration
│
├── AGENTS.md                            # Cross-tool instructions
├── CLAUDE.md                            # Claude Code compatibility
│
└── ~/                                   # Home directory (personal)
    ├── .copilot/skills/                 # Personal skills
    ├── .claude/settings.json            # Personal hooks
    └── (VS Code profile)               # Personal agents, prompts
```

---

## Settings Reference

### Agent System

| Setting | Default | Purpose |
|---------|---------|---------|
| `chat.agent.enabled` | `true` | Master switch for agents |
| `chat.plugins.enabled` | `true` | Enable plugin marketplace |
| `chat.mcp.autoStart` | `true` | Auto-restart MCP servers on config change |

### Tool Approval

| Setting | Default | Purpose |
|---------|---------|---------|
| `chat.tools.terminal.autoApprove` | `false` | Skip confirmation for terminal commands |
| `chat.tools.terminal.sandbox.enabled` | `false` | Sandbox terminal commands (macOS/Linux) |

### Memory

| Setting | Default | Purpose |
|---------|---------|---------|
| `github.copilot.chat.tools.memory.enabled` | `true` | Local memory tool |
| `github.copilot.chat.copilotMemory.enabled` | `false` | GitHub-hosted memory |

### Custom Paths (Override Defaults)

| Setting | Default Location | Purpose |
|---------|-----------------|---------|
| `chat.instructionsFilesLocations` | `.github/instructions/` | Instruction files |
| `chat.promptFilesLocations` | `.github/prompts/` | Prompt files |
| `chat.agentFilesLocations` | `.github/agents/` | Agent files |
| `chat.agentSkillsLocations` | `.github/skills/` | Skill folders |
| `chat.hookFilesLocations` | `.github/hooks/` | Hook configs |

### Plugins

| Setting | Purpose |
|---------|---------|
| `chat.plugins.marketplaces` | Array of `"owner/repo"` marketplace sources |
| `chat.plugins.paths` | Object of `{ "path": true/false }` local plugins |

---

## Decision Trees

### "Which customization mechanism should I use?"

```
Is it a rule that should ALWAYS apply?
├── Yes → Is it project-wide?
│   ├── Yes → copilot-instructions.md or AGENTS.md
│   └── No (file-specific) → .instructions.md with applyTo glob
│
└── No → Is it a repeatable task template?
    ├── Yes → .prompt.md (invoked with /command)
    │
    └── No → Is it reusable domain expertise?
        ├── Yes → SKILL.md (on-demand, portable)
        │
        └── No → Is it a specialized persona?
            ├── Yes → .agent.md (custom agent)
            │
            └── No → Is it a policy that must be enforced?
                ├── Yes → hooks/*.json (lifecycle automation)
                │
                └── No → Is it an external tool/data source?
                    └── Yes → mcp.json (MCP server)
```

### "Which orchestration pattern should I use?"

```
Is the task a single coherent piece of work?
├── Yes → Is it complex enough to benefit from research first?
│   ├── Yes → Research-then-Implement (Plan → Agent, built-in)
│   └── No → Single Agent session
│
└── No (multiple subtasks) → Are the subtasks independent?
    ├── Yes → Can they run in the same session?
    │   ├── Yes → Multi-Perspective Review (parallel subagents)
    │   └── No → Parallel Sessions (multiple independent sessions)
    │
    └── No (sequential dependency) → Do you need user review between stages?
        ├── Yes → Handoff Pipeline (agent → agent with review gates)
        └── No → Coordinator-Worker (one orchestrator, many subagents)
            │
            └── Does it involve tests? → TDD pattern (Red/Green/Refactor)
```

### "Which agent type should I use?"

```
Do you need real-time interaction?
├── Yes → Local (Agent, Plan, or Ask)
│
└── No → Should it produce a PR for team review?
    ├── Yes → Cloud (Copilot coding agent)
    │
    └── No → Is it a well-defined task you can describe upfront?
        ├── Yes → Background (CLI + worktree)
        └── No → Local (interactive, then hand off)
```
