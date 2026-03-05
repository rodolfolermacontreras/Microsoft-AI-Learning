# Background Agents

> Autonomous agents that run on your machine using CLI and git worktrees for isolated work.

---

## What Background Agents Are

Background agents (Copilot CLI) run non-interactively on your local machine. They use
**git worktrees** to work in isolation from your main workspace, preventing conflicts
with your active editing.

Use background agents for:
- Well-defined tasks with clear scope
- Implementing a plan created by the Plan agent
- Exploring multiple variants or proof of concepts
- Long-running tasks while you continue other work
- Tasks that do not require immediate interaction

---

## How Worktrees Provide Isolation

When a background agent starts, VS Code creates a separate git worktree:

```
Your workspace (main branch)
    |
    +-- .git/ (shared)
    |
    +-- Background Agent A worktree
    |       - Own directory
    |       - Own branch
    |       - Changes isolated from main
    |
    +-- Background Agent B worktree
            - Completely independent
            - Can run simultaneously
```

This means:
- You keep editing your main workspace without conflicts
- Multiple background agents can run in parallel
- Each agent commits changes to its worktree
- You review and apply changes when ready

---

## Starting a Background Agent Session

### From Chat View

```
Chat view  ->  New Session (+)  ->  Select "Background"  ->  Enter prompt
```

### From Plan Agent

```
Plan Agent generates plan  ->  Start Implementation  ->  Continue in Background
```

### From Terminal (Copilot CLI)

```
# Open dedicated Copilot CLI terminal
Terminal dropdown  ->  GitHub Copilot CLI

# Or type in any integrated terminal:
copilot
```

### Handoff From Local Session

```
Local session  ->  Delegate Session dropdown  ->  Background
```

Full conversation history carries over.

---

## Managing Background Sessions

### Sessions View

Filter the sessions list to show only background agents. Each session shows:
- Status (running, completed, error)
- Diff statistics
- Changed files

### Reviewing Changes

When a background agent completes:

1. Select the session from the list
2. Select any changed file to see the diff
3. Or select **View All Changes** for a multi-file diff
4. Select **Apply** to merge changes into your workspace
5. VS Code handles merge conflicts if they occur

### Follow-Up Prompts

You can send follow-up prompts to a running background agent to:
- Make adjustments
- Add requirements
- Redirect the approach

---

## Delegating to Cloud

From a background session, enter `/delegate` to hand off to a cloud agent.
This creates a PR for team review.

---

## Limitations

- Cannot access VS Code built-in tools or runtime context (test failures, selections)
  unless explicitly added to the prompt
- No access to extension-provided tools
- Limited to models available via the CLI tool
- Can only access local MCP servers that do not require authentication
- Currently no custom agent support (experimental setting: `github.copilot.chat.cli.customAgents.enabled`)

---

## Multi-Repository Workspaces

When your workspace contains multiple git repositories, VS Code shows a
repository picker when starting a background session. Select which
repository the worktree should be created in.

---

## Practical Example: Plan Then Implement in Background

```
1. Open Chat  ->  Select "Plan"
2. Enter: "Add dark/light theme toggle with persisted preference"
3. Plan Agent researches, asks questions, produces plan
4. Review the plan
5. Select "Start Implementation" -> "Continue in Background"
6. Continue your own work while the background agent implements the plan
7. When complete, review the diff and apply changes
```

This workflow separates thinking (Plan) from doing (Background) and lets you
stay productive throughout.

---

## Next Steps

- [Cloud Agents](cloud-agents.md) -- team collaboration via PRs
- [Subagents Guide](../03-subagents/subagents-guide.md) -- delegation within a session
- [Hooks](../04-customization/hooks.md) -- automate background agent lifecycle events
