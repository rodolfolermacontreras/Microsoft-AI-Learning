# Claude Code -- Comprehensive Overview

> Reference document for the [anthropics/claude-code](https://github.com/anthropics/claude-code) repository.
> Last updated: 2025-07-27

---

## Table of Contents

1. [What is Claude Code](#1-what-is-claude-code)
2. [Core Architecture](#2-core-architecture)
3. [Key Concepts](#3-key-concepts)
4. [Subagents Deep Dive](#4-subagents-deep-dive)
5. [Worktrees Deep Dive](#5-worktrees-deep-dive)
6. [Agent Teams (Multi-Agent Collaboration)](#6-agent-teams-multi-agent-collaboration)
7. [Plugin System](#7-plugin-system)
8. [Official Plugins Reference](#8-official-plugins-reference)
9. [Hooks System](#9-hooks-system)
10. [Skills System](#10-skills-system)
11. [Commands System](#11-commands-system)
12. [Memory and Context Management](#12-memory-and-context-management)
13. [Settings and Security](#13-settings-and-security)
14. [SDK and Headless Mode](#14-sdk-and-headless-mode)
15. [Multi-Agent Design Patterns](#15-multi-agent-design-patterns)
16. [Practical Examples from the Repo](#16-practical-examples-from-the-repo)
17. [Pros and Cons](#17-pros-and-cons)
18. [Version History Milestones](#18-version-history-milestones)
19. [Getting Started](#19-getting-started)
20. [References](#20-references)

---

## 1. What is Claude Code

Claude Code is Anthropic's agentic coding tool. It operates as an AI assistant that lives in your
terminal and IDE, understands your entire codebase, and can perform real actions: editing files,
running commands, searching code, managing git workflows, and interacting with external services
through MCP servers.

Unlike chat-only assistants, Claude Code is an **agent** -- it plans multi-step tasks, executes
tools, validates results, and iterates autonomously. It can spawn sub-processes (subagents), work
in isolated git worktrees, and coordinate teams of agents working in parallel.

### How It Runs

```
Terminal (CLI)          VS Code Extension          Headless (SDK)
      |                       |                        |
      v                       v                        v
  claude                 Native panel            @anthropic-ai/sdk
      |                       |                        |
      +--------> Claude Code Engine <---------+
                      |
          +-----------+-----------+
          |           |           |
       Tools       Hooks      Plugins
    (Bash, Read,  (Pre/Post    (Agents,
     Write, MCP)  ToolUse,     Skills,
                   Stop)       Commands)
```

Key interfaces:
- **CLI**: `claude` command in any terminal. Supports interactive and non-interactive (`-p`) modes.
- **VS Code Extension**: Native panel integration (since v2.0.0).
- **SDK**: TypeScript and Python SDKs for programmatic/headless usage.
- **Desktop App**: Standalone Claude Code for Desktop (since v2.0.51).
- **Chrome Extension**: Claude in Chrome for web-based interaction (since v2.0.72, Beta).

---

## 2. Core Architecture

### Tool System

Claude Code works by calling **tools** -- discrete actions the model can invoke:

| Tool | Purpose |
|------|---------|
| `Bash` | Run shell commands |
| `Read` | Read file contents |
| `Write` | Write/edit files |
| `WebSearch` | Search the web |
| `WebFetch` | Fetch a URL |
| `Task` | Spawn a subagent |
| `TodoList` | Track progress across steps |

### Permission Model

Every tool call goes through a permission check:
- **allow**: Auto-approved (no prompt).
- **ask**: Requires user confirmation.
- **deny**: Blocked entirely.

Permissions are layered: enterprise > organization > project > user. This prevents individual
users from overriding security policies set by administrators.

### Settings Hierarchy

```
Enterprise managed-settings.json   (highest priority, cannot be overridden)
    |
Organization managed-settings.json
    |
Project .claude/settings.json
    |
User settings.json / settings.local.json  (lowest priority)
```

---

## 3. Key Concepts

### 3.1 Agents

An **agent** in Claude Code is a named persona with a specific system prompt, allowed tools,
and optional model override. Agents are defined in:
- Plugin `plugin.json` files (under `"agents"` key)
- Skill frontmatter (with `agent:` field)
- CLI via `--agents` flag
- Dynamic creation by the model during a session

Agents are invoked via the **Task tool** -- the model spawns a subagent with a specific prompt
and set of permitted tools, then receives its output.

### 3.2 Skills

A **skill** is a markdown file with YAML frontmatter that provides domain-specific instructions.
Skills are like "expert knowledge packs" that Claude loads when relevant.

```yaml
---
name: security-review
description: Reviews code for security vulnerabilities
tools: [Read, Bash, WebSearch]
---

When reviewing code for security, check for:
1. SQL injection vulnerabilities
2. XSS attack vectors
3. Hardcoded credentials
...
```

Skills can be:
- **Auto-invoked**: Loaded automatically when context matches (via `alwaysInclude: true` or model decision).
- **On-demand**: Loaded when the user or model explicitly requests them.
- **Forked**: Run in a separate context (`context: fork`) to avoid polluting the main conversation.

### 3.3 Commands

**Commands** are markdown-based prompt templates stored in `.claude/commands/`. They act as
reusable workflows that users invoke with `/command-name`.

Commands support:
- `allowed-tools`: Restrict which tools the command can use.
- `description`: Short help text.
- Dynamic context injection: `!git status` embeds live command output.
- `$ARGUMENTS`: Placeholder for user-provided input.

### 3.4 Hooks

**Hooks** are user-defined scripts that run at specific lifecycle points:

| Hook Event | When It Fires |
|------------|---------------|
| `PreToolUse` | Before a tool is called |
| `PostToolUse` | After a tool completes |
| `Stop` | When the model finishes its turn |
| `UserPromptSubmit` | When the user submits a prompt |
| `SessionStart` | When a new session begins |
| `PermissionRequest` | When a permission check occurs |
| `WorktreeCreate` | When a worktree is created |
| `WorktreeRemove` | When a worktree is removed |
| `TeammateIdle` | When a teammate agent becomes idle |
| `TaskCompleted` | When a task/subagent completes |

Hooks are external processes (Python scripts, shell commands, etc.) that receive JSON on stdin
and return exit codes:
- Exit 0: Allow/continue.
- Exit 1: Show stderr to user (informational).
- Exit 2: Block the action and show stderr to Claude (corrective feedback).

### 3.5 MCP (Model Context Protocol) Servers

Claude Code can connect to external **MCP servers** to access additional tools and data sources.
MCP servers are configured in `.claude/settings.json` and extend Claude's capabilities with
custom tools (e.g., database queries, API calls, specialized search).

### 3.6 Memory

Claude Code has an automatic memory system (since v2.1.32). It records and recalls:
- Project-level memories in `CLAUDE.md` / `.claude/` files.
- User preferences and patterns observed across sessions.
- Conversation context that can be resumed (`/resume` or `claude --resume`).

---

## 4. Subagents Deep Dive

Subagents are the core mechanism for multi-agent work in Claude Code. When Claude needs to
delegate a task, it uses the **Task tool** to spawn a new agent instance.

### How Subagents Work

```
Main Agent (Orchestrator)
    |
    |-- Task tool call: "Analyze the authentication module"
    |       |
    |       v
    |   Subagent (isolated context)
    |       - Has its own conversation history
    |       - Runs with specified tools
    |       - Can use a different model (e.g., Haiku for speed)
    |       - Returns result to main agent
    |
    |-- Task tool call: "Review the database schema"
    |       |
    |       v
    |   Subagent (independent, can run in parallel)
    |
    v
Main Agent collects results, synthesizes, continues
```

### Subagent Capabilities

1. **Model mixing**: Subagents can use different models than the orchestrator. Use Haiku for
   fast exploration, Sonnet for balanced work, Opus for complex reasoning. The orchestrator
   dynamically selects the model per subagent (since v2.0.28).

2. **Isolated context**: Each subagent has its own conversation window, preventing context
   pollution of the main agent. Results are summarized back.

3. **Parallel execution**: Multiple subagents can run concurrently. The orchestrator fans out
   tasks and collects results.

4. **Resumable**: Subagents can be resumed if interrupted (since v2.0.28).

5. **Worktree isolation**: Subagents can work in their own git worktree (since v2.1.49)
   with `isolation: "worktree"` in the agent definition.

### Subagent Milestones (from CHANGELOG)

| Version | Capability |
|---------|-----------|
| v0.2.74 | Task tool can write files and run bash |
| v1.0.60 | Custom subagents via `/agents` command |
| v2.0.17 | Explore subagent (Haiku-powered codebase search) |
| v2.0.28 | Plan subagent, resume support, dynamic model selection |
| v2.1.49 | Worktree isolation for subagents |

### Subagent Patterns from Official Plugins

**Pattern 1: Parallel Fan-Out (code-review plugin)**

The code-review plugin spawns 5 parallel subagents, each reviewing a different aspect:
- **Logic & correctness** (Sonnet 4)
- **Error handling & edge cases** (Sonnet 4)
- **Performance & scalability** (Haiku)
- **Readability & maintainability** (Haiku)
- **Security implications** (Opus 4)

Each agent returns findings with a confidence score. A validation subagent then filters
results above a threshold, producing the final review.

**Pattern 2: Sequential Phases with Parallel Internals (feature-dev plugin)**

The feature-dev plugin runs 7 phases:
1. Analyze requirements
2. Explore codebase (parallel code-explorer agents)
3. Design architecture (code-architect agent)
4. Human review gate
5. Implement (main agent)
6. Review (code-reviewer agent)
7. Polish and commit

Each phase has specialized agent types with different system prompts and tools.

**Pattern 3: Specialized Agent Pool (pr-review-toolkit plugin)**

Six specialized agents, each tuned for a specific review concern:
- `comment-analyzer` -- Examine PR review comments
- `pr-test-analyzer` -- Evaluate test coverage
- `silent-failure-hunter` -- Find error paths that fail silently
- `type-design-analyzer` -- Review type system usage
- `code-reviewer` -- General code quality
- `code-simplifier` -- Identify over-engineering

Agents activate selectively based on the PR content.

---

## 5. Worktrees Deep Dive

Git worktrees allow multiple working directories to share a single `.git` repository. Claude Code
leverages this for **isolated parallel work**.

### What Git Worktrees Are

```
Main working directory:  /project/
    |
    +-- .git/  (shared)
    |
    +-- Worktree A:  /project/.worktrees/feature-auth/
    |       - Independent branch
    |       - Own file modifications
    |       - Does not affect main directory
    |
    +-- Worktree B:  /project/.worktrees/fix-bug-123/
            - Another independent branch
            - Can run simultaneously with A
```

### Worktrees in Claude Code

Since v2.1.49, Claude Code supports worktrees natively:

1. **CLI flag**: `claude --worktree` (or `-w`) starts Claude in an isolated git worktree.
   Changes happen in a temporary branch that does not affect your main working directory.

2. **Agent definition**: Agents with `isolation: "worktree"` automatically get their own
   worktree when spawned as subagents.

3. **Hook events**: `WorktreeCreate` and `WorktreeRemove` hooks fire when worktrees are
   created or destroyed, enabling custom setup/teardown logic.

### Why Worktrees Matter for Multi-Agent Work

Without worktrees, multiple agents editing files in the same directory create conflicts.
Worktrees solve this:

```
Orchestrator Agent (main directory)
    |
    |-- Subagent A (worktree: feature-auth/)
    |       - Modifying auth.ts, auth.test.ts
    |       - On branch: agent/feature-auth
    |
    |-- Subagent B (worktree: fix-styling/)
    |       - Modifying styles.css, layout.tsx
    |       - On branch: agent/fix-styling
    |
    v
Orchestrator merges results from both worktrees
```

Each subagent works on its own branch in its own directory. No file conflicts. No race
conditions. The orchestrator can merge the branches when both complete.

### Worktree + Agent Teams

The agent teams feature (v2.1.32) uses worktrees as its isolation primitive. Each teammate
agent gets its own worktree, enabling true parallel development on the same repository.

---

## 6. Agent Teams (Multi-Agent Collaboration)

Agent teams (research preview since v2.1.32) enable multiple Claude Code instances to
collaborate on a shared objective.

### How Agent Teams Work

```
User Session
    |
    v
Lead Agent (orchestrator)
    |
    |-- Teammate A (own worktree, own context)
    |       - Working on: backend API endpoints
    |       - Hook events: TeammateIdle, TaskCompleted
    |
    |-- Teammate B (own worktree, own context)
    |       - Working on: frontend components
    |
    |-- Teammate C (own worktree, own context)
    |       - Working on: test suite
    |
    v
Lead Agent coordinates, reviews, merges
```

### Enabling Agent Teams

```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

This is a research preview feature (token-intensive). Each teammate is a full Claude Code
session with its own worktree.

### Key Team Hooks

- `TeammateIdle` -- Fires when a teammate finishes its assigned work and awaits new tasks.
- `TaskCompleted` -- Fires when a subagent/teammate completes a task.

### Background Agents

Since v2.0.60, agents can run in the background while the user continues working. Since
v2.0.64, agents and bash commands can run asynchronously and send messages to wake up the
main agent. This enables non-blocking multi-agent workflows.

---

## 7. Plugin System

Plugins are the primary extension mechanism for Claude Code. A plugin bundles agents, skills,
commands, and hooks into a distributable package.

### Plugin Structure

```
my-plugin/
    plugin.json          -- Manifest (agents, skills, hooks, commands, metadata)
    README.md            -- Documentation
    commands/            -- Slash command markdown files
    skills/              -- Skill markdown files
    hooks/               -- Hook scripts
    agents/              -- Agent definition files
```

### plugin.json Schema

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "What this plugin does",
  "commands": [
    { "name": "my-command", "description": "Does a thing", "file": "commands/my-command.md" }
  ],
  "agents": [
    { "name": "my-agent", "description": "Specialist", "file": "agents/my-agent.md" }
  ],
  "skills": [
    { "name": "my-skill", "description": "Knowledge", "file": "skills/my-skill.md" }
  ],
  "hooks": {
    "PreToolUse": [{ "matcher": "Bash", "file": "hooks/validate-bash.py" }],
    "Stop": [{ "file": "hooks/on-stop.py" }]
  }
}
```

### Plugin Lifecycle

1. **Discovery**: Via marketplaces (configurable, restrictable) or local paths.
2. **Installation**: `/plugin install <name>` or repository-level `extraKnownMarketplaces`.
3. **Activation**: `/plugin enable <name>` or auto-enabled per plugin config.
4. **Validation**: `/plugin validate` checks plugin structure and integrity.

---

## 8. Official Plugins Reference

The repository includes 13 official plugins in `plugins/`:

### 8.1 agent-sdk-dev

**Purpose**: Scaffolds and verifies projects built with the Claude Agent SDK (TypeScript).

Components:
- Commands: `agent-sdk-new-project` (scaffold), `agent-sdk-verify` (validate)
- Agents: `verification_agent` (runs tests with retry loops), `debugging_agent` (targeted debugging)
- Skills: `agent-sdk-patterns`, `sdk-reference`

### 8.2 claude-opus-4-5-migration

**Purpose**: Guides migration to Opus 4.5, mapping feature equivalences and API changes.

Components:
- Skills: `migration-guide` (auto-invoked, maps old features to new patterns)

### 8.3 code-review (Key Multi-Agent Example)

**Purpose**: Comprehensive PR review system using 5 parallel agents and a 7-stage pipeline.

Architecture:
```
/code-review
    |
    Stage 1: Gather PR diff (bash)
    Stage 2: Initial analysis
    Stage 3: 5 parallel review agents
    |   - Logic & correctness (Sonnet)
    |   - Error handling (Sonnet)
    |   - Performance (Haiku)
    |   - Readability (Haiku)
    |   - Security (Opus)
    Stage 4: Validation agent (filters low-confidence)
    Stage 5: Synthesize findings
    Stage 6: Risk assessment
    Stage 7: Format and present
```

Notable patterns:
- Model mixing (Haiku for speed, Opus for depth)
- Confidence scoring per finding
- Validation subagent as quality gate

### 8.4 commit-commands

**Purpose**: Git workflow automation with context-aware commit messages.

Components:
- Commands: `smart-commit` (builds message from diff context)
- Hooks: `SessionStart` (injects bash context like `$PWD`, branch, recent history)

### 8.5 explanatory-output-style

**Purpose**: Modifies Claude's output style to include explanatory insights.

Components:
- Hooks: `SessionStart` (injects system prompt modification for educational explanations)

### 8.6 feature-dev (Key Workflow Example)

**Purpose**: Full-lifecycle feature development with 7 phases and 3 agent types.

Architecture:
```
/feature-dev <requirements>
    |
    Phase 1: Requirements analysis
    Phase 2: Codebase exploration (parallel code-explorer agents)
    Phase 3: Architecture design (code-architect agent)
    Phase 4: Human review gate (user approves/modifies plan)
    Phase 5: Implementation (main agent)
    Phase 6: Code review (code-reviewer agent)
    Phase 7: Polish and commit
```

Agent types:
- `code-explorer`: Searches codebase, maps dependencies, finds patterns
- `code-architect`: Designs architecture, evaluates trade-offs, writes specs
- `code-reviewer`: Reviews implementation against architectural decisions

### 8.7 frontend-design

**Purpose**: Provides UI/UX design expertise when frontend work is detected.

Components:
- Skills: `design-system-expert` (auto-invoked, covers layout, accessibility, responsiveness)

### 8.8 hookify

**Purpose**: Meta-plugin that creates custom hooks by analyzing your conversation patterns.

Components:
- Commands: `hookify` (analyzes conversation for automatable patterns, generates hook scripts)
- Agents: `conversation_analyst` (inspects session history to identify recurring patterns)

### 8.9 learning-output-style

**Purpose**: Pedagogical mode that adjusts output to leave room for the user to participate.

Components:
- Hooks: `SessionStart` (tells Claude to explain reasoning but leave coding to the user)

### 8.10 plugin-dev (Meta-Toolkit)

**Purpose**: Comprehensive toolkit for building Claude Code plugins (8 phases, 3 agents, 7 skills).

Architecture:
```
/plugin-dev <plugin-idea>
    |
    Phase 1: Requirements analysis
    Phase 2: Architecture design
    Phase 3: Plugin scaffolding
    Phase 4: Component implementation
    Phase 5: Testing
    Phase 6: Documentation
    Phase 7: Validation
    Phase 8: Publication prep
```

Agents: `plugin_architect`, `plugin_tester`, `plugin_reviewer`
Skills: `claude-code-extension-points`, `plugin-json-schema`, `hook-development`,
`agent-development`, `skill-development`, `command-development`, `plugin-testing`

### 8.11 pr-review-toolkit (Key Specialization Example)

**Purpose**: 6 specialized review agents, each focusing on a different code quality dimension.

Agents:
- `comment-analyzer` -- Examines PR review comments for patterns
- `pr-test-analyzer` -- Evaluates test coverage and quality
- `silent-failure-hunter` -- Finds error paths that fail silently
- `type-design-analyzer` -- Reviews type system usage and design
- `code-reviewer` -- General code quality assessment
- `code-simplifier` -- Identifies over-engineering and unnecessary complexity

Pattern: Selective activation based on PR content (not all agents run on every PR).

### 8.12 ralph-wiggum (Autonomous Iteration Example)

**Purpose**: Autonomous iteration via a Stop hook that feeds Claude's output back as new input.

Mechanism:
```
Claude generates output
    |
    v
Stop hook intercepts
    |
    v
Hook evaluates output quality
    |
    v
If unsatisfactory: re-prompt Claude with feedback (exit 2)
If satisfactory:    allow completion (exit 0)
```

Notable patterns:
- Self-referential feedback loops
- State management via `.local.md` files
- Autonomous quality improvement without user intervention

### 8.13 security-guidance

**Purpose**: Real-time security analysis during development.

Components:
- Hooks: `PreToolUse` (intercepts Bash and Write tool calls)

Checks 9 security patterns:
1. Hardcoded credentials/API keys
2. SQL injection vulnerabilities
3. Command injection risks
4. Path traversal attacks
5. Insecure deserialization
6. XSS vulnerabilities
7. SSRF risks
8. Weak cryptography
9. Overly permissive file permissions

---

## 9. Hooks System

Hooks provide lifecycle interception points. They are external processes (not inline code)
that communicate via JSON over stdin/stdout.

### Hook Configuration

In `.claude/settings.json` or `plugin.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /path/to/validate_bash.py"
          }
        ]
      }
    ]
  }
}
```

### Hook Input (JSON on stdin)

```json
{
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf /tmp/test"
  },
  "session_id": "abc123",
  "conversation_id": "def456"
}
```

### Hook Exit Codes

| Exit Code | Effect |
|-----------|--------|
| 0 | Allow the action, continue normally |
| 1 | Show stderr to user only (informational warning) |
| 2 | Block the action, show stderr to Claude as feedback |

### Practical Hook Example (from repo)

The `examples/hooks/bash_command_validator_example.py` demonstrates:
- Intercepting `Bash` tool calls
- Validating commands against rules (e.g. "use `rg` instead of `grep`")
- Blocking non-compliant commands with corrective feedback

---

## 10. Skills System

Skills are markdown files with YAML frontmatter. They inject domain expertise into Claude's
context at the right time.

### Skill Frontmatter

```yaml
---
name: my-skill
description: What this skill provides
tools: [Read, Bash, WebSearch]
alwaysInclude: false
context: fork
agent: my-specialized-agent
---

<skill content in markdown>
```

Key fields:
- `tools`: Which tools the skill enables.
- `alwaysInclude`: If true, always loaded. If false, loaded by model decision.
- `context: fork`: Runs in a separate context to avoid polluting the main conversation.
- `agent`: Associates a specific agent with this skill.
- Hot-reload (since v2.1.0): Skills reload automatically when edited.

---

## 11. Commands System

Commands are markdown templates stored in `.claude/commands/`. The repo includes three
official commands as examples:

### 11.1 commit-push-pr

Creates a branch (if on main), commits all changes, pushes, and opens a PR -- all in a
single Claude response.

```yaml
---
allowed-tools: Bash(git checkout --branch:*), Bash(git add:*), Bash(git status:*),
               Bash(git push:*), Bash(git commit:*), Bash(gh pr create:*)
description: Commit, push, and open a PR
---
```

### 11.2 dedupe

Finds duplicate GitHub issues using a multi-agent approach:
1. Agent checks if issue needs deduplication
2. Agent summarizes the issue
3. **5 parallel agents** search for duplicates with diverse keywords
4. Filter agent removes false positives
5. Comment script posts results

This command is a real-world example of **parallel fan-out** in a production workflow.

### 11.3 triage-issue

Triages GitHub issues by analyzing content and applying labels:
- Fetches available labels (only uses existing ones, never invents new).
- Categorizes by type (bug, enhancement, question).
- Applies lifecycle labels (`needs-repro`, `needs-info`) when warranted.
- Handles both new issues and comments on existing issues.
- Uses `./scripts/gh.sh` wrapper for all GitHub interactions.

---

## 12. Memory and Context Management

### CLAUDE.md Files

The primary memory mechanism. These files in your project root or `.claude/` directory
contain persistent instructions, preferences, and project context.

### Automatic Memory (since v2.1.32)

Claude Code automatically records and recalls:
- Patterns it observes in your code
- Preferences you express during conversations
- Project-specific conventions

### Conversation Management

- **Compaction** (since v0.2.47): Automatic summarization when conversation gets long,
  enabling unbounded session length.
- **Resume** (since v0.2.93): Resume previous conversations with `/resume` or `claude --resume`.
- **Rewind** (since v2.0.0): `/rewind` to go back to a previous point in the conversation.
- **Todo list** (since v0.2.93): Claude tracks its own progress across multi-step tasks.

### Thinking Modes

Control the depth of Claude's internal reasoning:
- `"think"` -- Standard extended thinking
- `"think harder"` -- Deeper reasoning
- `"ultrathink"` -- Maximum depth reasoning (since v0.2.44)
- Toggle with Tab key (since v2.0.0)

---

## 13. Settings and Security

### Settings Files (from repo examples)

The repo provides three reference configurations:

**settings-lax.json** -- Minimal restrictions:
- Disables `--dangerously-skip-permissions` bypass
- Blocks unknown plugin marketplaces

**settings-strict.json** -- Maximum lockdown:
- All lax restrictions plus:
- Bash requires approval for every command
- Web search and fetch denied
- Only managed permission rules (users cannot override)
- Only managed hooks (users cannot add custom hooks)

**settings-bash-sandbox.json** -- Sandboxed execution:
- Bash runs in a sandboxed environment
- Network access controlled (allowedDomains, proxy ports)
- Unix socket access restricted
- Only managed permission rules

### Key Security Properties

| Property | Purpose |
|----------|---------|
| `disableBypassPermissionsMode` | Prevents `--dangerously-skip-permissions` |
| `strictKnownMarketplaces` | Empty array blocks all plugin marketplaces |
| `allowManagedPermissionRulesOnly` | Only enterprise-set permissions apply |
| `allowManagedHooksOnly` | Only enterprise-set hooks can run |
| `sandbox.enabled` | Runs Bash in a sandboxed environment |

### Sandbox Details

The sandbox (since v2.0.24, Linux and Mac) isolates Bash tool execution:
- Network access restricted to specified domains
- File system access limited
- Unix socket access controlled
- Does NOT apply to other tools (Read, Write, WebSearch, WebFetch, MCPs)
- Does NOT apply to hooks or internal commands

---

## 14. SDK and Headless Mode

### TypeScript SDK (since v1.0.23)

```typescript
import { Claude } from "@anthropic-ai/claude-code-sdk";

const claude = new Claude();
const result = await claude.run({
  prompt: "Refactor the auth module to use JWT",
  workingDirectory: "/path/to/project",
  model: "claude-sonnet-4-20250514"
});
```

### Python SDK (since v1.0.23)

```python
from claude_code_sdk import Claude

claude = Claude()
result = claude.run(
    prompt="Refactor the auth module to use JWT",
    working_directory="/path/to/project",
    model="claude-sonnet-4-20250514"
)
```

### Headless / Print Mode

```bash
# Single prompt, get result
claude -p "What files are in this project?"

# Streaming JSON output
claude -p "Explain the architecture" --output-format=stream-json
```

### Programmatic Agent Orchestration

The SDK enables building custom multi-agent systems outside of Claude Code's built-in
mechanisms:

```typescript
// Fan out to 3 parallel agents
const tasks = [
  claude.run({ prompt: "Review auth module", agents: ["security-reviewer"] }),
  claude.run({ prompt: "Review data layer", agents: ["performance-reviewer"] }),
  claude.run({ prompt: "Review API surface", agents: ["api-reviewer"] }),
];
const results = await Promise.all(tasks);
```

### Remote Control (since v2.1.51)

`claude remote-control` allows one Claude Code instance to control another, enabling
programmatic orchestration of Claude sessions.

---

## 15. Multi-Agent Design Patterns

Based on analysis of all 13 official plugins, the following patterns emerge:

### Pattern Catalog

| Pattern | Description | Example Plugin |
|---------|------------|----------------|
| Parallel fan-out (same type) | Multiple agents with same role, different inputs | dedupe command (5 search agents) |
| Parallel fan-out (mixed models) | Different models for different complexity levels | code-review (Haiku/Sonnet/Opus) |
| Redundant parallel agents | Same task, multiple approaches, best result wins | dedupe (diverse search strategies) |
| Validation subagents | Agent that filters/validates other agents' output | code-review (confidence filtering) |
| Sequential stages with parallel internals | Pipeline where some stages fan out | feature-dev (7 phases, parallel exploration) |
| Selective agent activation | Not all agents run; activated by content | pr-review-toolkit (PR-content-based) |
| Progressive refinement | Output of one agent becomes input of next | code-review (analysis to synthesis) |
| Human-in-the-loop gates | Human approval between automated stages | feature-dev (Phase 4 review gate) |
| Command-to-agent chaining | Slash command orchestrates multiple agents | plugin-dev (8-phase pipeline) |
| Autonomous iteration (Stop hook) | Agent loops on its own output until quality met | ralph-wiggum |
| Meta-agents | Agents that create/configure other agents | hookify (conversation to hooks) |
| Conversation analysis agent | Agent that inspects session history | hookify (pattern detection) |
| Confidence-based filtering | Only pass findings above a score threshold | code-review (validation stage) |

### When to Use Each Pattern

**Parallel fan-out**: When tasks are independent and can run simultaneously. Best for
reviews, searches, and analyses where multiple perspectives add value.

**Model mixing**: When cost and speed matter. Use cheap/fast models (Haiku) for routine
tasks, expensive/powerful models (Opus) only where depth is needed.

**Validation subagents**: When raw agent output needs quality control. Acts as a filter
between generation and presentation.

**Human-in-the-loop**: When the cost of mistakes is high. Insert a gate where the user
reviews a plan before the agent executes it.

**Autonomous iteration**: When quality is hard to specify upfront. Let the agent iterate
until its own evaluation is satisfied.

---

## 16. Practical Examples from the Repo

### Example 1: Bash Command Validator Hook

File: `examples/hooks/bash_command_validator_example.py`

Demonstrates intercepting Bash commands and enforcing rules:
- Blocks `grep` usage (recommends `rg` instead)
- Blocks `find -name` usage (recommends `rg --files`)
- Returns exit code 2 to give Claude corrective feedback

### Example 2: DevContainer Setup Script

File: `Script/run_devcontainer_claude_code.ps1`

PowerShell script for running Claude Code inside a DevContainer:
- Supports Docker or Podman backends
- Initializes and starts container environment
- Finds the running devcontainer by label
- Executes `claude` inside the container and drops into `zsh`

### Example 3: GitHub Issue Management

Files: `.claude/commands/dedupe.md`, `.claude/commands/triage-issue.md`

Real-world commands that Anthropic uses to manage their own GitHub issues:

**Deduplication flow**:
1. Check if issue needs deduplication
2. Summarize the issue with an agent
3. Launch 5 parallel search agents with diverse strategies
4. Filter false positives with another agent
5. Post results via script

**Triage flow**:
1. Fetch available labels
2. Read issue details and comments
3. Classify (bug, enhancement, question, invalid)
4. Apply lifecycle labels if warranted
5. Handle both new issues and comment events

---

## 17. Pros and Cons

### Pros

1. **True agentic capability**: Not just chat -- it plans, executes, validates, iterates.
   It can edit files, run tests, manage git, and interact with external services.

2. **Powerful multi-agent architecture**: Subagents, worktree isolation, agent teams, and
   model mixing enable sophisticated workflows impossible in single-agent systems.

3. **Extensible plugin system**: Agents, skills, commands, and hooks provide four orthogonal
   extension points. Plugins are distributable and composable.

4. **Enterprise-grade security**: Layered permission model, sandboxing, managed settings
   hierarchy, marketplace restrictions, and hook-based validation.

5. **Model flexibility**: Dynamic model selection per subagent. Use the right model for the
   right task (Haiku for speed, Opus for reasoning).

6. **IDE integration**: Native VS Code extension, terminal CLI, desktop app, and Chrome
   extension provide multiple access points.

7. **SDK for automation**: TypeScript and Python SDKs enable headless/programmatic usage,
   CI/CD integration, and custom orchestration.

8. **Memory and context management**: Automatic memory, conversation compaction, resume,
   and CLAUDE.md files provide persistent context across sessions.

9. **Active development**: Rapid release cadence (2,070-line CHANGELOG from v0.2.21 to
   v2.1.69), with major features landing regularly.

10. **Production-tested**: The repo's own commands (dedupe, triage) show Anthropic using
    Claude Code to manage Claude Code's own GitHub issues.

### Cons

1. **Anthropic lock-in**: Only works with Claude models. No option to use other LLMs.

2. **Token consumption**: Multi-agent workflows are token-intensive. Agent teams are
   explicitly flagged as "token-intensive" in the docs.

3. **Experimental features**: Agent teams (v2.1.32) are a "research preview." Worktree
   isolation is recent (v2.1.49). These APIs may change.

4. **Cost**: Opus model usage for subagents adds up quickly. Model mixing helps but
   requires careful orchestration.

5. **Complexity**: The extension system (plugins + hooks + skills + commands + agents)
   has a significant learning curve. The interaction between these systems is not always
   obvious.

6. **Platform limitations**: Sandbox only works on Linux and Mac. Some features require
   specific environments (e.g., tmux for agent team sessions).

7. **No visual UI for agent orchestration**: Multi-agent workflows are defined in config
   files and markdown. There is no visual builder or debugger for agent flows.

8. **Context window constraints**: Despite compaction, complex multi-agent workflows can
   push context limits. Subagent isolation helps but adds overhead.

9. **Git dependency**: Worktree features require git. Non-git projects miss out on the
   isolation capabilities.

10. **Closed source**: The Claude Code engine itself is closed source. The repo contains
    plugins, examples, and scripts -- not the core tool.

---

## 18. Version History Milestones

Key releases from the 2,070-line CHANGELOG (v0.2.21 to v2.1.69):

| Version | Date Range | Key Feature |
|---------|-----------|-------------|
| v0.2.44 | Early | Thinking modes ("think", "think harder", "ultrathink") |
| v0.2.47 | Early | Automatic conversation compaction |
| v0.2.74 | Early | Task tool can write files and run bash |
| v0.2.93 | Early | Resume conversations, Todo list |
| v0.2.105 | Early | Web search capability |
| v1.0.0 | GA | General availability, Sonnet 4 and Opus 4 |
| v1.0.23 | Post-GA | TypeScript and Python SDKs |
| v1.0.38 | Post-GA | Hooks system (PreToolUse, PostToolUse, Stop) |
| v1.0.54 | Post-GA | UserPromptSubmit hook |
| v1.0.60 | Post-GA | Custom subagents via `/agents` |
| v1.0.81 | Post-GA | Output styles |
| v2.0.0 | Major | VS Code extension, Agent SDK, `/rewind`, `/usage` |
| v2.0.12 | v2 | Plugin system released |
| v2.0.17 | v2 | Explore subagent (Haiku-powered) |
| v2.0.20 | v2 | Skills system |
| v2.0.24 | v2 | Bash sandbox (Linux/Mac) |
| v2.0.28 | v2 | Plan subagent, resume subagents, dynamic model selection |
| v2.0.51 | v2 | Opus 4.5, Claude Code for Desktop |
| v2.0.60 | v2 | Background agents |
| v2.0.64 | v2 | Async agents and bash |
| v2.0.72 | v2 | Claude in Chrome (Beta) |
| v2.1.0 | v2.1 | Plugin hooks expanded, skill hot-reload |
| v2.1.32 | v2.1 | Agent teams (research preview), Opus 4.6, automatic memory |
| v2.1.45 | v2.1 | Sonnet 4.6 |
| v2.1.49 | v2.1 | Worktree flag (`--worktree`), subagent worktree isolation |
| v2.1.50 | v2.1 | WorktreeCreate/Remove hooks, `isolation: worktree` in agents |
| v2.1.51 | v2.1 | `claude remote-control` subcommand |

---

## 19. Getting Started

### Installation

```bash
# Via npm (globally)
npm install -g @anthropic-ai/claude-code

# Via Homebrew
brew install claude-code

# Verify
claude --version
```

### First Run

```bash
# Start interactive session
claude

# Start with a prompt
claude "Explain this codebase"

# Print mode (headless)
claude -p "What files are in this project?"
```

### Configuration

```bash
# Open settings
claude settings

# Install a plugin
/plugin install code-review

# Create a project CLAUDE.md
echo "This project uses TypeScript with strict mode." > CLAUDE.md
```

### Using Subagents

```bash
# In an interactive session, Claude will use subagents automatically
# You can also define custom agents:
/agents

# Or use the --agents flag:
claude --agents my-custom-agent
```

### Using Worktrees

```bash
# Start in an isolated worktree
claude --worktree

# Or shorthand
claude -w
```

---

## 20. References

- Repository: https://github.com/anthropics/claude-code
- Documentation: https://docs.anthropic.com/en/docs/claude-code
- Settings docs: https://code.claude.com/docs/en/settings
- Hooks docs: https://docs.anthropic.com/en/docs/claude-code/hooks
- SDK: https://www.npmjs.com/package/@anthropic-ai/claude-code-sdk
- Agent SDK: Renamed from Claude Code SDK to Claude Agent SDK in v2.0.0
- License: Proprietary (Anthropic PBC, Commercial Terms of Service)
