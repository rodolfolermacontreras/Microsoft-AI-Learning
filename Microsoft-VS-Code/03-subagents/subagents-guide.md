# Subagents in VS Code -- Deep Dive

> How to delegate subtasks to isolated subagents, run them in parallel, and compose multi-agent workflows.

---

## What Subagents Are

A **subagent** is an independent AI agent spawned within a session to handle a subtask
in its own isolated context window. The main agent delegates work, the subagent performs
it, and only the result summary flows back.

Subagents are the **core mechanism for multi-agent orchestration** in VS Code.

```
Main Agent (receives your prompt)
    |
    |-- runSubagent: "Research authentication patterns"
    |       |
    |       v
    |   Subagent A (own context window)
    |       - Reads files, searches codebase
    |       - Returns summary of findings
    |
    |-- runSubagent: "Analyze the database schema"
    |       |
    |       v
    |   Subagent B (running in parallel)
    |       - Independent context
    |       - Does not see Subagent A's work
    |
    v
Main Agent receives both results, synthesizes, continues
```

---

## Why Subagents Matter

### 1. Context Isolation

Every subagent starts with a **clean context window**. It does not inherit the main
agent's conversation history or instructions. Only the task prompt is passed in.

This prevents **context pollution** -- the main agent's context stays focused on
orchestrating the overall task instead of accumulating research details.

### 2. Parallel Execution

VS Code can spawn multiple subagents simultaneously. Request parallel analysis
and VS Code runs them concurrently, then waits for all results before continuing.

### 3. Reduced Token Consumption

Subagent intermediate work (file reads, searches, exploration) stays in the
subagent's context. Only the final result summary is returned to the main agent.
This significantly reduces overall token usage for complex tasks.

### 4. Specialized Behavior

By running a **custom agent** as a subagent, you apply specialized tools,
instructions, and models for specific subtasks.

### 5. Experimental Isolation

If a subagent's research leads to a dead end, only the summary affects
your main context -- not all the intermediate exploration.

---

## How Subagent Execution Works

```
User Prompt: "Implement auth with OAuth2"
    |
    v
Main Agent decides to research first
    |
    |-- Spawns Subagent (task: "Research OAuth2 libraries for Node.js")
    |       |
    |       v                              Subagent Context Window:
    |   Subagent reads files               - Sees only the task prompt
    |   Subagent searches codebase         - Has access to same tools
    |   Subagent fetches web docs          - Independent conversation
    |       |
    |       v
    |   Returns: "passport.js with passport-oauth2 is used in 3 places..."
    |
    v
Main Agent receives summary (only the summary enters main context)
Main Agent proceeds with implementation
```

Subagents are **synchronous** from the main agent's perspective: the main agent
waits for results before continuing. This is intentional -- subagent findings
typically inform the next step.

However, **multiple subagents run in parallel** when they are independent.

---

## Invoking Subagents

### Agent-Initiated (Automatic)

The main agent decides when context isolation helps. You do not need to type
"run a subagent" -- the agent recognizes when to delegate.

**To encourage subagent use**, phrase prompts that suggest isolated research:

```
"Research the best authentication approach for this project,
then implement it based on your findings."
```

The agent will likely spawn a subagent for the research phase.

### Hinting Parallel Analysis

```
"Analyze this codebase for security, performance, and accessibility
simultaneously and summarize the findings."
```

VS Code spawns three subagents in parallel.

### In Custom Agent Instructions

For consistent behavior, define subagent usage in your custom agent's instructions:

```markdown
---
name: Feature Builder
tools: ['agent', 'edit', 'search', 'read']
---
For each feature request:
1. Use a subagent to research the codebase for related patterns
2. Use a subagent to review documentation
3. Implement the feature based on research findings
```

### In Prompt Files

Include `runSubagent` or `agent` in the tools list:

```markdown
---
name: document-feature
tools: ['agent', 'read', 'search', 'edit']
---
Run a subagent to research the implementation details.
Then update the docs/ folder with documentation.
```

---

## Running Custom Agents as Subagents

By default, subagents inherit the main session's model and tools. With custom agents,
you override these for specialized behavior.

### Creating a Subagent-Only Custom Agent

Set `user-invocable: false` to hide the agent from the dropdown while keeping
it available as a subagent:

```markdown
---
name: internal-researcher
user-invocable: false
tools: ['read', 'search', 'codebase']
---
You are a codebase researcher. Analyze code structure, patterns, and
dependencies. Return concise findings only.
```

### Restricting Which Subagents Can Be Used

In a coordinator agent, use the `agents` property to allow only specific subagents:

```markdown
---
name: TDD
tools: ['agent', 'edit', 'read']
agents: ['Red', 'Green', 'Refactor']
---
Implement features using test-driven development:
1. Use the Red agent to write failing tests
2. Use the Green agent to make tests pass
3. Use the Refactor agent to improve code quality
```

| Value | Effect |
|-------|--------|
| `['Red', 'Green']` | Only these agents can be used as subagents |
| `*` | All available agents (default) |
| `[]` | No subagent use allowed |

### Preventing Unwanted Subagent Invocation

Set `disable-model-invocation: true` on an agent to prevent the model from
automatically choosing it as a subagent:

```markdown
---
name: Dangerous-Tool-User
disable-model-invocation: true
tools: ['edit', 'runInTerminal']
---
```

This agent can only be invoked explicitly by the user, never by another agent.

---

## What the User Sees

When a subagent runs, it appears as a **collapsible tool call** in the chat:

```
[Subagent: internal-researcher]  Reading file...   [v expand]
```

Expand to see:
- All tool calls the subagent made
- The prompt passed to the subagent
- The returned result

This keeps the main conversation clean while preserving full visibility.

---

## Subagents vs Other Concepts

| Concept | What It Is | Context |
|---------|-----------|---------|
| **Subagent** | Child agent within a session, own context | Isolated, reports back |
| **New session** | Entirely separate conversation | No connection to current task |
| **Background agent** | Autonomous agent in a worktree | Runs independently |
| **Handoff** | Transfer session from one agent type to another | Same conversation continues |

---

## Performance Optimization

### Do

- Clearly define the task and expected output for each subagent
- Use custom agents with restricted tools for subagent roles
- Request parallel analysis when tasks are independent
- Use faster/cheaper models for subagent tasks via custom agent `model` field

### Do Not

- Pass unnecessary context to subagents (they start clean)
- Use subagents for trivial single-step tasks (overhead not worth it)
- Chain subagents sequentially when they could run in parallel

---

## Next Steps

- [Orchestration Patterns](orchestration-patterns.md) -- coordinator-worker, multi-perspective, TDD
- [Custom Agents](../04-customization/custom-agents.md) -- define subagent personas
- [Memory and Sessions](../05-memory-and-sessions/memory-and-sessions.md) -- persistence across subagents
