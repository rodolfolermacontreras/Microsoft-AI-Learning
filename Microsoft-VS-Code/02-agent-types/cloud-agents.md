# Cloud Agents

> Agents that run on remote infrastructure and integrate with GitHub for team collaboration.

---

## What Cloud Agents Are

Cloud agents (Copilot coding agent) run on GitHub's infrastructure, not your machine.
They create branches, implement changes, and open pull requests for team review.

Use cloud agents for:
- Tasks that benefit from team collaboration
- Long-running implementations that should produce a PR
- Tasks where you want teammate review before merging
- Assigning GitHub issues directly to an AI agent

---

## How Cloud Agents Work

```
User assigns task
    |
    v
Cloud agent runs on GitHub infrastructure
    |
    v
Creates branch and implements changes
    |
    v
Opens pull request
    |
    v
Team reviews and merges
```

Cloud agents are asynchronous -- you do not need to stay connected. The agent
works independently and notifies you when the PR is ready.

---

## Starting a Cloud Agent Session

### From Chat View

```
Chat view  ->  New Session (+)  ->  Select "Cloud"  ->  Select provider  ->  Enter prompt
```

### From Plan Agent

```
Plan Agent generates plan  ->  Start Implementation  ->  Continue in Cloud
```

### From Background Agent

```
Background session  ->  /delegate  ->  Cloud
```

### From GitHub

- Assign an issue to `copilot` on GitHub.com
- Mention `@copilot` in an issue comment or PR

---

## Supported Cloud Agent Providers

| Provider | What It Does |
|----------|-------------|
| **Copilot coding agent** | Built-in. Creates branches, PRs. Full GitHub integration. |
| **Claude** | Third-party. Anthropic's Claude as a cloud agent. |
| **Codex** | Third-party. OpenAI's Codex as a cloud agent. |

Third-party cloud agents must be enabled in your Copilot account settings.

---

## Managing Cloud Sessions

### Sessions View

Cloud sessions appear in the Chat view sessions list. Each shows:
- Status (running, waiting for review, completed)
- PR link
- Changed files and diff statistics

### Reviewing Changes

1. Select the cloud session from the list
2. Review the PR diff
3. Right-click for options: **Checkout**, **Apply**, or **View PR**
4. Use the GitHub Pull Requests extension for full PR workflow

---

## Requirements

- Project must be published to a GitHub repository
- GitHub repository must be added as a remote
- For third-party agents: enable in Copilot account settings
- Install the GitHub Pull Requests extension for best experience

---

## Compared to Background Agents

| Aspect | Background Agent | Cloud Agent |
|--------|-----------------|-------------|
| Runs on | Your machine | GitHub infrastructure |
| Isolation | Git worktree (local) | Remote branch |
| Output | Local diff to apply | Pull request |
| Collaboration | Solo | Team via PR review |
| MCP access | Local servers only | Cloud-configured servers |
| Persistence | Tied to VS Code session | Independent of your machine |

---

## Practical Example: Feature via PR

```
1. Open Chat  ->  Select "Cloud"
2. Enter: "Refactor authentication to use OAuth2 with JWT. Add tests."
3. Cloud agent creates branch, implements changes, opens PR
4. Team reviews the PR on GitHub
5. Address feedback or merge
```

---

## Next Steps

- [Third-Party Agents](third-party-agents.md) -- Claude, Codex, external providers
- [Custom Agents](../04-customization/custom-agents.md) -- define specialized cloud personas
