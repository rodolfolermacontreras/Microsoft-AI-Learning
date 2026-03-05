# Local Agents

> Interactive agents that run in VS Code on your machine with full access to tools and models.

---

## What Local Agents Are

Local agents run directly within VS Code. You interact through the Chat view and see
every step in real time. They have full access to your workspace, files, tools, MCP
servers, and all available models.

Use local agents for:
- Interactive tasks requiring immediate feedback
- Tasks needing editor context (test failures, lint errors, debug output)
- Brainstorming, planning, and exploratory work
- Tasks requiring specific VS Code extension tools or MCP servers

---

## Built-in Local Agents

### Agent

The default mode. Full autonomy for complex coding tasks.

**What it can do**:
- Read and search your codebase
- Edit files across your project
- Run terminal commands
- Install dependencies
- Self-correct when encountering errors
- Spawn subagents for subtasks

**When to use**: Building features, refactoring, debugging, testing.

```
Ctrl+Alt+I  ->  Select "Agent"  ->  Enter prompt
```

### Plan

Read-only analysis and structured planning. Cannot modify files.

**What it can do**:
- Research your codebase comprehensively
- Ask clarifying questions to resolve ambiguity
- Use subagents for research
- Generate step-by-step implementation plans

**What it cannot do**: Edit files, run terminal commands.

**Workflow**: Discovery -> Alignment -> Design -> Refinement

```
Ctrl+Alt+I  ->  Select "Plan"  ->  Enter task description
```

After the plan is complete, hand off to Agent mode or background/cloud agents.

### Ask

Read-only question answering about your codebase.

**What it can do**:
- Search semantically across your project
- Read files and explain code
- Answer questions about architecture and patterns

**What it cannot do**: Edit files, run commands, spawn subagents.

```
Ctrl+Alt+I  ->  Select "Ask"  ->  Enter question
```

---

## Starting a Session

1. Open the Chat view (`Ctrl+Alt+I`)
2. Select an agent from the dropdown (Agent, Plan, Ask, or custom)
3. Optionally select a language model from the model picker
4. Enter a prompt and press Enter

### Sending Follow-Up Prompts While Working

While an agent is working, you can send additional messages:
- **Queue**: message is processed after the current step
- **Steer**: redirect the current request
- **Stop and send**: interrupt and send immediately

---

## Reviewing Changes

When the agent makes code changes:
1. Changes appear in a diff view
2. Review each change individually
3. Select **Keep** to accept or **Undo** to reject
4. Modified files are highlighted in the working set

### Checkpoints

Agent sessions create checkpoints as work progresses. If the agent takes a
wrong turn:
1. Return to a previous checkpoint
2. Try a different approach
3. No need to manually undo changes

---

## Handing Off to Other Agent Types

Local sessions can be delegated to other agent types:

| From | To | How |
|------|------|-----|
| Local Agent | Background | Select "Background" from session type dropdown |
| Plan | Background | Start Implementation > Continue in Background |
| Local Agent | Cloud | Select "Cloud" from session type dropdown |
| Plan | Cloud | Start Implementation > Continue in Cloud |

The full conversation history and context carries over to the new session.

---

## Protecting Sensitive Files

VS Code helps prevent accidental edits to sensitive files like:
- `.env` files
- Workspace settings
- Configuration files

---

## Next Steps

- [Background Agents](background-agents.md) -- autonomous work in isolation
- [Custom Agents](../04-customization/custom-agents.md) -- create specialized personas
- [Subagents Guide](../03-subagents/subagents-guide.md) -- delegate subtasks
