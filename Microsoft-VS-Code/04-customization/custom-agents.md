# Custom Agents

> Create specialized AI personas with their own tools, instructions, models, and handoffs.

---

## What Custom Agents Are

A custom agent is a reusable configuration (`.agent.md` file) that gives an agent a
specific role, tools, and instructions. Think of them as specialized team members --
a security reviewer, a planner, a TDD practitioner -- each with their own expertise.

---

## File Structure

Custom agents are Markdown files with YAML frontmatter:

```markdown
---
name: My Agent
description: What this agent does
tools: ['read', 'search', 'edit']
model: Claude Sonnet 4.5 (copilot)
---

# Instructions

Your detailed instructions here...
```

---

## Frontmatter Reference

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Display name in the agent picker |
| `description` | string | Placeholder text in chat input |
| `argument-hint` | string | Hint for additional input |
| `tools` | array | Available tools for this agent |
| `agents` | array | Which custom agents can be used as subagents |
| `model` | string/array | Preferred model(s). Array = priority fallback list |
| `user-invocable` | boolean | Show in dropdown (default: true). Set false for subagent-only |
| `disable-model-invocation` | boolean | Prevent automatic subagent use (default: false) |
| `target` | string | Environment: `vscode` or `github-copilot` |
| `handoffs` | array | Suggested next-step transitions to other agents |

---

## File Locations

| Scope | Path |
|-------|------|
| Workspace | `.github/agents/` (shared with team via version control) |
| User profile | Managed by VS Code (available across workspaces) |
| Claude format | `.claude/agents/` (compatible with Claude Code) |

Additional locations via `chat.agentFilesLocations` setting.

---

## Handoffs

Handoffs create guided transitions between agents:

```yaml
handoffs:
  - label: Start Implementation
    agent: implementation
    prompt: Implement the plan above.
    send: false
    model: GPT-5.2 (copilot)
```

| Property | Description |
|----------|-------------|
| `label` | Button text shown to user |
| `agent` | Target agent to switch to |
| `prompt` | Pre-filled prompt for the target agent |
| `send` | Auto-submit the prompt (default: false) |
| `model` | Override model for the handoff |

---

## Invocation Control

| Setting | `user-invocable` | `disable-model-invocation` | Result |
|---------|-----------------|---------------------------|--------|
| Default | true | false | Visible in dropdown AND usable as subagent |
| Subagent-only | false | false | Hidden from dropdown, available as subagent |
| User-only | true | true | Visible in dropdown, cannot be used as subagent |
| Disabled | false | true | Hidden and blocked (use `agents` override to re-enable) |

---

## Examples

### Code Reviewer (Read-Only)

```markdown
---
name: Reviewer
description: Review code for quality and best practices
tools: ['read', 'search', 'codebase', 'problems', 'usages']
---
You are an experienced senior developer conducting a code review.
Analyze code quality, identify bugs, security issues, and performance problems.
DO NOT write or suggest specific code changes directly.
Focus on explaining what should be changed and why.
```

### Planning Agent with Handoff

```markdown
---
name: Planner
description: Create implementation plans before coding
tools: ['read', 'search', 'codebase', 'fetch']
handoffs:
  - label: Start Implementation
    agent: agent
    prompt: Implement the plan above step by step.
    send: false
---
Research the codebase thoroughly before creating a plan.
Ask clarifying questions to resolve ambiguity.
Output a numbered step-by-step plan with verification criteria.
```

### Documentation Writer

```markdown
---
name: DocWriter
description: Generate and update documentation
tools: ['read', 'search', 'edit', 'create']
model: Claude Haiku 4.5 (copilot)
---
You write clear, concise technical documentation.
Follow the project's existing documentation style.
Include code examples for every concept.
Update the table of contents when adding new sections.
```

---

## Creating Custom Agents

### Manual

1. Create `.github/agents/MyAgent.agent.md` in your workspace
2. Add frontmatter and instructions
3. Agent appears in the dropdown

### With AI

Type `/create-agent` in chat and describe the persona you want.

### From a Conversation

After a productive session, ask: "make an agent for this kind of task"

---

## Using with Subagents

See [Orchestration Patterns](../03-subagents/orchestration-patterns.md) for
coordinator-worker, TDD, and multi-perspective review patterns that use
custom agents as subagents.

---

## Next Steps

- [Custom Instructions](custom-instructions.md) -- project-wide coding standards
- [Prompt Files](prompt-files.md) -- reusable slash commands
- [Subagents Guide](../03-subagents/subagents-guide.md) -- run agents as subagents
