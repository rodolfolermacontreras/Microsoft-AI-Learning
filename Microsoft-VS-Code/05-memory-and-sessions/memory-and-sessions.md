# Memory and Session Management

> How agents persist context across conversations and how to manage sessions effectively.

---

## Memory Scopes

VS Code agents use three memory scopes to retain context:

| Scope | Path | Persists Across Sessions | Persists Across Workspaces | Use For |
|-------|------|-------------------------|---------------------------|---------|
| **User** | `/memories/` | Yes | Yes | Preferences, patterns, frequently used commands |
| **Repository** | `/memories/repo/` | Yes | No | Codebase conventions, project structure, build commands |
| **Session** | `/memories/session/` | No | No | Task-specific context, in-progress plans |

### User Memory

Persists across all workspaces and conversations. First 200 lines auto-loaded
at session start.

```
"Remember that I prefer tabs over spaces and always use single quotes in JavaScript"
```

### Repository Memory

Scoped to the current workspace. Persists across conversations in that workspace.

```
"Remember that this project uses the repository pattern for data access"
```

### Session Memory

Scoped to current conversation. Cleared when the conversation ends.
The Plan agent saves its implementation plans here (`plan.md`).

---

## Storing and Retrieving Memories

### Store

```
"Remember that our team uses conventional commits for all commit messages"
```

The agent determines the appropriate scope automatically.

### Retrieve

```
"What are our commit message conventions?"
```

### Manage

| Command | Action |
|---------|--------|
| Chat: Show Memory Files | View all memory files across scopes |
| Chat: Clear All Memory Files | Remove all memories |

---

## Copilot Memory (GitHub-Hosted)

A separate system from local memory. Repository-scoped insights shared across
GitHub Copilot surfaces (coding agent, code review, CLI).

| Aspect | Local Memory Tool | Copilot Memory |
|--------|-------------------|----------------|
| Storage | Local on your machine | GitHub-hosted |
| Scopes | User, repo, session | Repository only |
| Cross-surface | VS Code only | Coding agent, code review, CLI |
| Created by | You or agent in chat | Copilot agents automatically |
| Expiration | Manual | Auto (28 days) |

Enable: `github.copilot.chat.copilotMemory.enabled`

---

## Session Management

### Creating Sessions

Each session is independent with its own context window. Multiple sessions can
run in parallel across different agent types.

```
New Session (+)  ->  Choose agent type  ->  Choose model  ->  Enter prompt
```

### Sessions View

The Chat view sessions list shows:
- Status (running, completed, error)
- Agent type (local, background, cloud)
- Diff statistics for changed files
- Time grouping (Today, Last Week)

### View Modes

- **Compact**: Sessions embedded in Chat view
- **Side-by-side**: Sessions panel beside Chat view (auto when wider)

### Session Actions

- Archive: Hide from active list (can unarchive later)
- Delete: Permanently remove (irreversible)
- Hand off: Transfer to another agent type
- Open as Editor: View in editor tab

---

## Context Window Management

### Compaction

When the context window fills:
- VS Code automatically summarizes older conversation parts
- Important details may be compressed
- Manual trigger: `/compact` with optional focus instructions

### Best Practices

| Practice | Why |
|----------|-----|
| New session per task | Prevents context pollution |
| Remove irrelevant history | Keeps context focused |
| Use subagents for research | Isolates exploration from main context |
| Use custom instructions for persistent rules | Survive compaction |
| Choose the right session type | Local for interactive, background for autonomous |
| Run parallel sessions for independent tasks | Separate contexts |

---

## Checkpoints

Agent sessions create checkpoints as work progresses:

1. Review changes at each checkpoint
2. Rewind to a previous checkpoint if the agent goes off track
3. Try a different approach from that point

---

## Next Steps

- [Subagents Guide](../03-subagents/subagents-guide.md) -- context isolation via delegation
- [Custom Instructions](../04-customization/custom-instructions.md) -- persistent rules
- [Cheatsheet](../07-reference/cheatsheet.md) -- quick reference
