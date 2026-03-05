# Cross-Terminal Agent Communication in Claude Code

> "Can you talk to my Claude agent in another terminal?"
> Short answer: yes -- using `claude remote-control`, shared files, agent teams, or an MCP bridge.
> This document explains each approach and when to use it.

---

## The Problem

By default, each `claude` terminal session is isolated: its own context window, its own
conversation history, its own working state. Two sessions running simultaneously have no
awareness of each other.

But there are four practical ways to make them communicate.

---

## Quick Setup

Before any cross-terminal work, activate your project virtual environment in each terminal:

```powershell
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# macOS / Linux (bash/zsh)
source .venv/bin/activate
```

Confirm your environment and start Claude:

```bash
python --version      # should show 3.12+
claude --version      # should show installed version
```

---

## Pattern 1: Remote Control (Direct Message Passing)

Since v2.1.51, `claude remote-control` lets one Claude session send messages to another
that is running in a different terminal.

### Setup

```bash
# Terminal A: start the worker session, expose a control socket
claude --expose-control-socket /tmp/my-agent.sock

# Now work in Terminal A as normal -- this session is the "worker"
```

```bash
# Terminal B: become the controller -- send Terminal A a task
claude remote-control --socket /tmp/my-agent.sock \
  --message "Implement the login endpoint per docs/auth-spec.md"

# Read the streamed response from Terminal A
```

### When to Use

- Real-time coordination: controller directs worker with specific tasks
- Automated pipelines: a script in Terminal B drives Terminal A programmatically
- Monitoring: Terminal B polls Terminal A for status updates

---

## Pattern 2: Shared Files (Filesystem-Based)

The simplest approach. Agents communicate by writing and reading files on a shared
filesystem. No real-time connection needed.

### Convention

Use `.claude/agent-memory/` as the shared communication directory (already tracked by
Claude Code's memory system):

```
.claude/agent-memory/
    task-status.md       # Agent A writes current status
    findings.md          # Agent A writes analysis results
    instructions.md      # Agent B writes tasks for Agent A
```

### Workflow

**Agent A** (Terminal A) -- writes results:
```
Write your findings to .claude/agent-memory/auth-analysis.md
Include: current status, key decisions, blockers, and next steps.
```

**Agent B** (Terminal B) -- reads and continues:
```
Read .claude/agent-memory/auth-analysis.md and continue the implementation
based on Agent A's findings.
```

### When to Use

- Agents work at different times (no simultaneous requirement)
- Passing large amounts of structured data (reports, plans, code reviews)
- Audit trail needed (files persist after sessions end)

---

## Pattern 3: Agent Teams (Experimental Coordinated Sessions)

Since v2.1.32, agent teams allow a lead Claude session to spawn and coordinate
multiple teammate sessions, each with its own worktree.

### Enable

```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

### How It Works

```
Lead Agent (Terminal A, main directory)
    |
    |-- Teammate 1 (auto-spawned, worktree: feature-auth/)
    |       Working on: authentication module
    |
    |-- Teammate 2 (auto-spawned, worktree: feature-db/)
    |       Working on: database layer
    |
    v
Lead Agent reviews, coordinates, merges
```

The lead agent uses `TeammateIdle` and `TaskCompleted` hook events to know when
teammates finish and to dispatch new tasks.

### When to Use

- Parallel development on independent modules
- Lead + worker pattern where one agent actively manages others
- Large tasks that benefit from worktree isolation (no file conflicts)

Note: Agent teams are token-intensive (each teammate is a full session). Reserve for
tasks that genuinely benefit from true parallelism.

---

## Pattern 4: MCP Server as Communication Bridge

Use a local MCP server as a message bus between two Claude sessions. Each session
connects to the same MCP server and exchanges structured messages through it.

### Bridge Server Concept

```python
# bridge_server.py (minimal MCP server)
# Exposes two tools:
#   post_message(sender, content) -> writes to shared queue
#   read_messages(since_id)       -> returns messages after a given ID
```

### MCP Configuration (`.vscode/mcp.json` or `.claude/settings.json`)

```json
{
  "mcpServers": {
    "agent-bridge": {
      "command": "python",
      "args": ["bridge_server.py"],
      "transport": "stdio"
    }
  }
}
```

Both Terminal A and Terminal B connect to the same server. Agent A calls
`post_message`, Agent B calls `read_messages`, and vice versa.

### When to Use

- Typed, structured message exchange (not just raw text)
- Multiple agents need a shared message queue
- Building a custom multi-agent framework on top of Claude Code

---

## Pattern 5: Resume an Existing Session

To continue a previous session from a new terminal (not truly cross-terminal, but
commonly mistaken for it):

```bash
# List recent sessions
claude --list-sessions

# Resume a specific session by ID
claude --resume <session-id>

# Resume the most recent session
claude --resume
```

This reconnects to the conversation history of a previous session. The session's
context, memory, and state are restored.

---

## Decision Guide

| What You Need | Best Pattern |
|---------------|-------------|
| Real-time: Terminal B sends commands to Terminal A | Remote Control |
| Async: Agents share results without running simultaneously | Shared Files |
| Parallel: Lead agent coordinates multiple workers | Agent Teams |
| Structured API between agents | MCP Bridge |
| Continue a session from a different terminal | `claude --resume` |

---

## Common Setup Checklist

Before working across terminals:

```
[ ] Virtual environment activated in each terminal (.\.venv\Scripts\Activate.ps1)
[ ] Claude Code installed and authenticated (claude --version)
[ ] If using Agent Teams: CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 set
[ ] If using Remote Control: --expose-control-socket path agreed between terminals
[ ] .claude/agent-memory/ directory exists for shared file patterns
```

---

## See Also

- [OVERVIEW.md](OVERVIEW.md) -- Full Claude Code reference (Section 6: Agent Teams, Section 14: SDK and Remote Control)
- [RULES.md](../RULES.md) -- Section 10: Claude Agent Architecture
- [Microsoft-VS-Code/03-subagents/](../Microsoft-VS-Code/03-subagents/) -- VS Code subagent patterns
