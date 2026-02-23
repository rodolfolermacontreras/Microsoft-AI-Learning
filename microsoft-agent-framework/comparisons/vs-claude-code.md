# Microsoft Agent Framework vs Claude Code Agent Patterns

## Overview

Microsoft Agent Framework and Claude Code approach AI agent development from fundamentally different angles. Agent Framework is an **SDK for building production agents**; Claude Code is an **AI coding assistant with agent capabilities built in**.

## Architecture Comparison

| Aspect | Microsoft Agent Framework | Claude Code |
|--------|--------------------------|-------------|
| **Type** | SDK / Library | AI Coding Assistant |
| **Purpose** | Build custom AI agents | Be an AI agent for coding |
| **Languages** | Python, .NET, Java | Works with any language |
| **Agent Definition** | Code (`AIAgent` class) | YAML frontmatter in `.claude/agents/` |
| **Skill Definition** | `@function_tool` decorator | Markdown files in `.claude/skills/` |
| **Orchestration** | Sequential, Concurrent, Handoff, Group Chat | Sub-agent invocation, headless mode |
| **State Management** | `AgentSession` object | Conversation context + CLAUDE.md |
| **Configuration** | Code + env vars | `.claude/` directory + settings.json |
| **Deployment** | Azure, containers, any cloud | Local CLI, GitHub Actions |
| **Interoperability** | A2A, AG-UI, MCP | MCP (client + server) |

## Conceptual Mapping

### Agent Definition

**Agent Framework** — agents are Python/C# objects:
```python
agent = AIAgent(
    name="CodeReviewer",
    instructions="Review code for bugs and style issues.",
    client=OpenAIChatClient(model="gpt-4o"),
    tools=[analyze_code, suggest_fix],
)
```

**Claude Code** — agents are YAML + markdown files:
```yaml
# .claude/agents/code-reviewer.md
---
name: Code Reviewer
description: Reviews code for bugs and style issues
model: claude-sonnet-4
tools:
  - Read
  - Grep
  - Bash
---
You are a code reviewer. Analyze code for bugs, style issues...
```

### Tools / Skills

**Agent Framework** — Python functions with decorators:
```python
@function_tool
def analyze_code(file_path: str) -> str:
    """Analyze a code file for issues."""
    # ... implementation
```

**Claude Code** — Markdown skill files with instructions:
```markdown
<!-- .claude/skills/code-analysis.md -->
# Code Analysis
When analyzing code:
1. Check for common bug patterns
2. Verify error handling
3. Review naming conventions
```

### Workflows

**Agent Framework** — code-defined orchestration:
```python
workflow = SequentialWorkflow(agents=[writer, reviewer, publisher])
result = await workflow.invoke(session, "Write a blog post")
```

**Claude Code** — agent invocation chains:
```bash
# From one agent, invoke another
claude --agent code-reviewer.md --print "Review src/app.py"
# Or in GitHub Actions
claude --agent deploy-agent.md --headless
```

### Memory & State

**Agent Framework**:
- `AgentSession` — per-conversation state
- Explicit session management in code
- No persistent cross-session memory (you build it)

**Claude Code**:
- `CLAUDE.md` — project-level memory (auto-read)
- User memory (`~/.claude/CLAUDE.md`) — personal preferences
- Local memory (`.claude/CLAUDE.local.md`) — gitignored secrets
- Conversation context — per-session

## When to Use What

### Use Microsoft Agent Framework When:
- ✅ Building a **production application** with AI agents
- ✅ Need **multi-agent orchestration** (pipelines, handoffs, group chat)
- ✅ Deploying to **Azure or cloud infrastructure**
- ✅ Building **APIs / services** with agentic capabilities
- ✅ Need **provider flexibility** (OpenAI, Anthropic, Ollama, etc.)
- ✅ Want **.NET / Java** support
- ✅ Building **enterprise solutions** with full control

### Use Claude Code Agent Patterns When:
- ✅ **Coding tasks** — writing, reviewing, refactoring code
- ✅ **CI/CD automation** — GitHub Actions with `--headless` mode
- ✅ **Development workflow** — skills, commands, hooks for your team
- ✅ **Quick prototyping** — YAML frontmatter vs full SDK setup
- ✅ **Knowledge encoding** — CLAUDE.md as persistent project context
- ✅ **Monorepo management** — subproject CLAUDE.md hierarchy

### They Can Complement Each Other:
- Use **Claude Code** to *develop* an Agent Framework application
- Use **Claude Code skills** to encode patterns *about* Agent Framework code
- Use **Agent Framework** agents in MCP servers that Claude Code connects to
- Use **AGENT_DEVELOPMENT_GUIDE.md** patterns when building with either

## Interoperability: MCP

Both support Model Context Protocol, but from different sides:

| | Agent Framework | Claude Code |
|--|----------------|-------------|
| MCP Client | ✅ Agents can call MCP servers | ✅ Built-in MCP client |
| MCP Server | ✅ Agents can be exposed as MCP | ✅ Can connect to MCP servers |
| A2A Protocol | ✅ Agent-to-Agent standard | ❌ Not supported |
| AG-UI Protocol | ✅ Agent-GUI standard | ❌ Not supported |

## Summary

Think of it this way:
- **Agent Framework** = *building blocks* to construct AI agent systems
- **Claude Code** = *an AI agent* that helps you code, with customizable behavior

They solve different problems and work great together — use Claude Code for development workflow, and Agent Framework for the production agents you're building.
