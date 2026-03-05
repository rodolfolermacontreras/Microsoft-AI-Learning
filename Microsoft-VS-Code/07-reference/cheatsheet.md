# VS Code Agents Cheatsheet

> Quick reference for all agent features, commands, and configuration.

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Alt+I` | Open Chat view |
| `Ctrl+I` | Inline chat (in editor) |
| `Tab` | Accept inline suggestion |
| `Alt+]` / `Alt+[` | Cycle inline suggestions |
| `Ctrl+Shift+P` | Command Palette |

---

## Chat Slash Commands

| Command | What It Does |
|---------|-------------|
| `/init` | Generate custom instructions for your workspace |
| `/compact` | Manually trigger context compaction |
| `/create-agent` | Generate a custom agent with AI |
| `/create-prompt` | Generate a prompt file with AI |
| `/create-instruction` | Generate an instruction file with AI |
| `/create-skill` | Generate an agent skill with AI |
| `/create-hook` | Generate a hook configuration with AI |
| `/agents` | Configure custom agents |
| `/prompts` | Configure prompt files |
| `/instructions` | Configure instruction files |
| `/skills` | Configure agent skills |
| `/hooks` | Configure hooks |
| `/delegate` | Hand off to cloud agent (from background) |
| `/yolo` | Enable global auto-approval |
| `/disableYolo` | Disable global auto-approval |

---

## Agent Types at a Glance

| Type | Where It Runs | Interactive | File Isolation | Output |
|------|--------------|-------------|----------------|--------|
| **Local (Agent)** | VS Code | Yes | No (edits workspace) | Direct edits |
| **Local (Plan)** | VS Code | Yes | Read-only | Implementation plan |
| **Local (Ask)** | VS Code | Yes | Read-only | Explanations |
| **Background** | Local machine (CLI) | No | Git worktree | Diff to apply |
| **Cloud** | GitHub infra | No | Remote branch | Pull request |
| **Third-party** | Provider infra | Varies | Varies | Varies |

---

## Context References (#)

| Reference | What It Adds |
|-----------|-------------|
| `#file:path` | Specific file contents |
| `#folder:path` | Folder contents |
| `#symbol:Name` | Symbol definitions |
| `#codebase` | Semantic codebase search |
| `#web` | Web search results |
| `#fetch <url>` | URL content |
| `#githubRepo owner/repo` | GitHub repo context |
| `#problems` | Compiler/lint errors |
| `#changes` | Git changes |
| `#selection` | Editor selection |
| `#terminalSelection` | Terminal output |
| `#testFailure` | Test failure details |

---

## File Locations Quick Reference

| Customization | Workspace Path | Extension |
|---------------|---------------|-----------|
| Instructions (always-on) | `.github/copilot-instructions.md` | `.md` |
| Instructions (file-based) | `.github/instructions/` | `.instructions.md` |
| Prompt files | `.github/prompts/` | `.prompt.md` |
| Custom agents | `.github/agents/` | `.agent.md` |
| Agent skills | `.github/skills/` | `SKILL.md` |
| Hooks | `.github/hooks/` | `.json` |
| MCP servers | `.vscode/mcp.json` | `.json` |
| Cross-tool instructions | `AGENTS.md` (root) | `.md` |
| Claude compat | `.claude/agents/`, `.claude/rules/` | `.md` |

---

## Custom Agent Frontmatter

```yaml
---
name: My Agent
description: What this agent does
tools: ['read', 'search', 'edit', 'create', 'runInTerminal', 'agent']
agents: ['Worker1', 'Worker2']    # Restrict subagent access
model: Claude Sonnet 4.5 (copilot)
user-invocable: true              # Show in dropdown
disable-model-invocation: false   # Allow as subagent
handoffs:
  - label: Next Step
    agent: target-agent
    prompt: Continue with...
    send: false
---
```

---

## Prompt File Frontmatter

```yaml
---
name: my-prompt
description: What this prompt does
argument-hint: [optional input]
agent: agent
model: GPT-5 (copilot)
tools: ['read', 'search', 'edit']
---
```

---

## Skill Frontmatter

```yaml
---
name: my-skill
description: When to use this skill
argument-hint: [optional input]
user-invocable: true
disable-model-invocation: false
---
```

---

## Instructions Frontmatter

```yaml
---
name: Python Standards
description: Coding conventions for Python files
applyTo: '**/*.py'
---
```

---

## Hook Events

| Event | When | Key Output |
|-------|------|-----------|
| `SessionStart` | First prompt | `additionalContext` |
| `UserPromptSubmit` | User sends message | Common output only |
| `PreToolUse` | Before tool runs | `permissionDecision`: allow/ask/deny |
| `PostToolUse` | After tool completes | `additionalContext`, `decision`: block |
| `PreCompact` | Before compaction | Common output only |
| `SubagentStart` | Subagent spawns | `additionalContext` |
| `SubagentStop` | Subagent completes | `decision`: block |
| `Stop` | Agent finishes | `decision`: block |

Hook exit codes: 0 = success, 2 = block, other = warning.

---

## MCP Server Config (mcp.json)

```json
{
  "servers": {
    "name": {
      "type": "http",
      "url": "https://api.example.com/mcp"
    },
    "local-tool": {
      "command": "npx",
      "args": ["-y", "@example/mcp-server"]
    }
  }
}
```

---

## Key Settings

| Setting | Purpose |
|---------|---------|
| `chat.agent.enabled` | Enable/disable agents |
| `chat.plugins.enabled` | Enable/disable plugins |
| `chat.mcp.autoStart` | Auto-restart MCP servers |
| `chat.tools.terminal.autoApprove` | Auto-approve terminal commands |
| `chat.tools.terminal.sandbox.enabled` | Sandbox terminal (macOS/Linux) |
| `github.copilot.chat.tools.memory.enabled` | Enable memory tool |
| `github.copilot.chat.copilotMemory.enabled` | Enable Copilot Memory |
| `chat.instructionsFilesLocations` | Custom instruction paths |
| `chat.promptFilesLocations` | Custom prompt paths |
| `chat.agentFilesLocations` | Custom agent paths |
| `chat.agentSkillsLocations` | Custom skill paths |
| `chat.hookFilesLocations` | Custom hook paths |

---

## Orchestration Patterns Summary

| Pattern | Description | Key Config |
|---------|------------|-----------|
| **Coordinator-Worker** | One agent delegates to specialized subagents | `agents: ['Worker1', 'Worker2']` |
| **Multi-Perspective** | Parallel subagents for independent review | Prompt: "analyze X, Y, Z simultaneously" |
| **TDD** | Red-Green-Refactor with 3 agents | `agents: ['Red', 'Green', 'Refactor']` |
| **Handoff Pipeline** | Sequential stages with user gates | `handoffs: [{agent, prompt, send}]` |
| **Plan-then-Implement** | Built-in Plan > Agent handoff | Plan mode > Start Implementation |
| **Parallel Sessions** | Multiple independent sessions | New Session per task |
