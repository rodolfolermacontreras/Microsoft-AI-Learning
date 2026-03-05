# How Agents Work in VS Code

> Core architecture: the agent loop, tools, validation, and how agents differ from chat.

---

## Agent vs Chat vs Inline Suggestions

VS Code offers AI across a spectrum of interaction surfaces:

| Surface | What It Does | Autonomy Level |
|---------|-------------|----------------|
| **Inline suggestions** | Ghost-text completions as you type | Passive -- accepts/rejects |
| **Inline chat** | Ctrl+I in the editor for focused edits | Reactive -- one-shot changes |
| **Ask mode** | Questions about your codebase, read-only | Read-only -- no file edits |
| **Agent mode** | Autonomous multi-step task execution | Full autonomy -- plans, edits, runs, validates |

Agents are the highest-autonomy surface. They do not just suggest code -- they **plan**, **execute
tools**, **validate results**, and **iterate** until the task is complete.

---

## The Agent Loop

Every agent follows a three-stage loop:

```
User Prompt
    |
    v
+---------------------------+
|  1. UNDERSTAND            |
|  - Read files             |
|  - Search codebase        |
|  - Look up documentation  |
+---------------------------+
    |
    v
+---------------------------+
|  2. ACT                   |
|  - Edit code              |
|  - Run terminal commands  |
|  - Install dependencies   |
|  - Call MCP tools          |
+---------------------------+
    |
    v
+---------------------------+
|  3. VALIDATE              |
|  - Run tests              |
|  - Check compiler errors  |
|  - Review own changes     |
|  - If errors: loop back   |
+---------------------------+
    |
    v
Result (or loop back to UNDERSTAND)
```

The agent chains actions together as needed. A simple question might involve a few file reads.
A feature implementation loops through editing, running tests, diagnosing failures, and editing
again until the tests pass.

---

## Tools: How Agents Interact with the Environment

Without tools, the model can only generate text. Tools give agents the ability to
**act** on your development environment.

### Built-in Tools

| Tool | Purpose | Category |
|------|---------|----------|
| `read` | Read file contents | Read |
| `search` | Search codebase | Read |
| `codebase` | Semantic codebase search | Read |
| `problems` | Get compiler/lint errors | Read |
| `usages` | Find code references | Read |
| `changes` | View git changes | Read |
| `edit` | Edit files | Write |
| `create` | Create new files | Write |
| `runInTerminal` | Run terminal commands | Execute |
| `terminalLastCommand` | Get last terminal output | Read |
| `fetch` | Fetch web content | External |
| `githubRepo` | Access GitHub repos | External |
| `runSubagent` | Spawn a subagent | Orchestration |

### Tool Categories

```
Read-only tools          Write tools             Execute tools
(no side effects)       (modify files)          (run commands)
    |                       |                       |
    v                       v                       v
  search                  edit                  runInTerminal
  read                    create                fetch
  codebase                                      githubRepo
  problems                                      runSubagent
  usages
  changes
```

### Tool Approval

Every tool invocation goes through an approval check:

| Level | Behavior |
|-------|----------|
| Auto-approve | Tool runs without prompting (safe read-only tools) |
| Ask | User must confirm before execution (terminal commands, file edits) |
| Deny | Tool is blocked entirely |

You control approval via settings, and organizations can enforce policies with device
management.

---

## How Context Flows to the Model

When you send a message, VS Code assembles a prompt from multiple sources:

```
+-------------------------------------------+
|  CONTEXT WINDOW (sent to the model)       |
|                                           |
|  1. System instructions (built-in)        |
|  2. Custom instructions / AGENTS.md       |
|  3. Custom agent definition               |
|  4. User message (your prompt)            |
|  5. Conversation history                  |
|  6. Implicit context (current file, git)  |
|  7. Explicit references (#file, #web)     |
|  8. Tool outputs (file reads, searches)   |
+-------------------------------------------+
            |
            v
    Language Model (LLM)
            |
            v
    Response (text, edit, or tool request)
```

Everything outside this window is invisible to the model. This is why referencing specific
files with `#file` produces better results than asking about code the model has not seen.

---

## How Agents Self-Correct

Agents do not just execute once -- they iterate. A typical flow:

```
1. Agent reads the failing test output
2. Agent traces the error to a specific file
3. Agent edits the file to fix the issue
4. Agent re-runs the test
5. If test still fails: agent reads the new error, goes back to step 2
6. If test passes: agent reports success
```

This self-correction loop is what makes agents fundamentally different from
chat-based suggestions. The agent keeps iterating until the task succeeds or
it determines it cannot proceed.

---

## Built-in Agent Modes

VS Code provides three built-in agent configurations:

### Agent Mode

The default. Full autonomy for complex coding tasks. Has access to all tools.
Reads files, edits code, runs commands, installs dependencies, self-corrects.

### Plan Mode

Read-only analysis and planning. Cannot edit files. Creates structured
implementation plans with step-by-step breakdowns. Use it to research and
design before committing to implementation.

```
User: "Add authentication to this app"
    |
    v
Plan Agent researches codebase (read-only)
    |
    v
Plan Agent asks clarifying questions
    |
    v
Plan Agent outputs structured plan:
  1. Create auth middleware
  2. Add JWT token validation
  3. Update API routes
  4. Add login/logout endpoints
  5. Write tests
    |
    v
User reviews and approves
    |
    v
Hand off to Agent Mode for implementation
```

### Ask Mode

Read-only question answering. Searches your codebase and provides explanations
without making any changes. Best for understanding code.

---

## Everything is Nondeterministic

The same prompt can produce different results each time. This is by design --
LLMs sample from probability distributions. Strategies to handle this:

1. **Be specific** -- include expected outputs, test cases, file names
2. **Use checkpoints** -- revert if the agent goes off track
3. **Start fresh** -- new session for new tasks (avoids context pollution)
4. **Iterate** -- refine with follow-up prompts instead of restarting
5. **Choose models carefully** -- different models have different strengths

---

## Next Steps

- [Context and Models](context-and-models.md) -- choosing models, managing context windows
- [Local Agents](../02-agent-types/local-agents.md) -- interactive agent sessions
- [Subagents Guide](../03-subagents/subagents-guide.md) -- delegation and orchestration
