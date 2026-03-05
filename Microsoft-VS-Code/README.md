# VS Code Agents and Subagents -- Learning Hub

> Comprehensive reference for using GitHub Copilot agents, subagents, and multi-agent orchestration in Visual Studio Code.
> Last updated: 2026-03-05

---

## What This Folder Covers

This is a structured learning resource for understanding and using **VS Code's agent system** --
the most powerful AI coding capability in the IDE. It covers the full spectrum from basic
agent sessions to multi-agent orchestration with subagents, custom agents, worktrees,
and team workflows.

**Target audience**: Data Scientists and Engineers learning to orchestrate AI agents
for complex, multi-step coding projects.

---

## Folder Structure

```
Microsoft-VS-Code/
|
|-- README.md                              # This file -- overview and navigation
|
|-- 01-core-concepts/
|   |-- how-agents-work.md                 # Agent loop, tools, context, LLMs
|   +-- context-and-models.md              # Context window, model selection, auto mode
|
|-- 02-agent-types/
|   |-- local-agents.md                    # Interactive agents (Agent, Plan, Ask)
|   |-- background-agents.md               # Copilot CLI, worktrees, autonomous tasks
|   |-- cloud-agents.md                    # Copilot coding agent, PR workflows
|   +-- third-party-agents.md              # Claude, Codex, external providers
|
|-- 03-subagents/
|   |-- subagents-guide.md                 # Deep dive: delegation, parallel execution
|   +-- orchestration-patterns.md          # Coordinator-worker, multi-perspective, TDD
|
|-- 04-customization/
|   |-- custom-agents.md                   # .agent.md files, personas, handoffs
|   |-- custom-instructions.md             # copilot-instructions.md, AGENTS.md, scoped rules
|   |-- prompt-files.md                    # Slash commands, reusable workflows
|   |-- agent-skills.md                    # SKILL.md, portable capabilities
|   |-- hooks.md                           # Lifecycle automation, security enforcement
|   |-- mcp-servers.md                     # External tools via Model Context Protocol
|   +-- agent-plugins.md                   # Plugin marketplaces, prepackaged bundles
|
|-- 05-memory-and-sessions/
|   +-- memory-and-sessions.md             # Memory scopes, session management, compaction
|
|-- 06-examples/
|   |-- .github/
|   |   |-- copilot-instructions.md        # Example: project-wide coding standards
|   |   |-- instructions/
|   |   |   +-- python-standards.instructions.md  # Example: Python-specific rules
|   |   |-- prompts/
|   |   |   |-- create-component.prompt.md # Example: React component scaffolding
|   |   |   +-- security-review.prompt.md  # Example: security audit prompt
|   |   |-- agents/
|   |   |   |-- Reviewer.agent.md          # Example: code review agent
|   |   |   |-- Planner.agent.md           # Example: planning-only agent
|   |   |   +-- TDD.agent.md              # Example: test-driven development orchestrator
|   |   |-- skills/
|   |   |   +-- webapp-testing/
|   |   |       +-- SKILL.md               # Example: web app testing skill
|   |   +-- hooks/
|   |       +-- security-hooks.json        # Example: hook configuration
|   +-- .vscode/
|       +-- mcp.json                       # Example: MCP server configuration
|
+-- 07-reference/
    +-- cheatsheet.md                      # Quick reference for all agent features
```

---

## Learning Path

### Phase 1: Understand the Fundamentals

```
1. 01-core-concepts/how-agents-work.md      -- Agent loop, tools, validation cycle
2. 01-core-concepts/context-and-models.md    -- Context window, model choices, auto mode
```

### Phase 2: Master Agent Types

```
3. 02-agent-types/local-agents.md            -- Agent, Plan, Ask built-in modes
4. 02-agent-types/background-agents.md       -- Copilot CLI, worktrees, parallel work
5. 02-agent-types/cloud-agents.md            -- Coding agent, PR collaboration
6. 02-agent-types/third-party-agents.md      -- Claude, Codex, multi-provider
```

### Phase 3: Subagents and Orchestration (The Core Goal)

```
7. 03-subagents/subagents-guide.md           -- Delegation, isolation, parallel execution
8. 03-subagents/orchestration-patterns.md    -- Coordinator-worker, TDD, multi-perspective
```

### Phase 4: Customize Everything

```
9.  04-customization/custom-agents.md        -- .agent.md, tools, handoffs
10. 04-customization/custom-instructions.md  -- Standards, scoped rules
11. 04-customization/prompt-files.md         -- Reusable slash commands
12. 04-customization/agent-skills.md         -- Portable capabilities
13. 04-customization/hooks.md                -- Lifecycle automation
14. 04-customization/mcp-servers.md          -- External tool integration
15. 04-customization/agent-plugins.md        -- Plugin ecosystem
```

### Phase 5: Reference and Practice

```
16. 05-memory-and-sessions/memory-and-sessions.md  -- Memory, sessions, scaling
17. 06-examples/                                    -- Working config files
18. 07-reference/cheatsheet.md                      -- Quick-access reference
```

---

## How This Relates to Other Folders

| Folder | Relationship |
|--------|-------------|
| `awesome-copilot/` | Covers agent/skill/MCP file formats in depth. This folder builds on that with subagent orchestration, agent types, and session management. |
| `microsoft-agent-framework/` | Code-level orchestration (SequentialBuilder, HandoffBuilder). This folder covers VS Code's UI-level orchestration (background agents, worktrees, handoffs). |
| `Claude-Code/` | Anthropic's parallel approach: plugins, hooks, worktrees. This folder covers the VS Code-native equivalent. |
| `copilot-sdk-exploration/` | SDK-level Copilot integration. This folder covers the IDE-level agent experience. |

---

## Prerequisites

- VS Code (latest stable)
- GitHub account with Copilot access (Free plan works for basic features)
- Agents enabled in VS Code settings (`chat.agent.enabled`)
- For cloud agents: GitHub Pull Requests extension
- For background agents: Git installed (worktrees require git)

---

## Key Takeaways

1. **Agents are not chat** -- they plan, execute tools, edit files, run commands, and self-correct
2. **Subagents enable orchestration** -- delegate subtasks to isolated contexts, run in parallel
3. **Four agent types** exist: local (interactive), background (autonomous), cloud (PR-based), third-party (Claude/Codex)
4. **Custom agents define personas** -- each with specific tools, instructions, and model preferences
5. **Handoffs chain agents** -- transitions from Plan to Implementation to Review
6. **Worktrees isolate work** -- background agents and subagents use git worktrees to prevent conflicts
7. **Everything is extensible** -- instructions, skills, prompts, hooks, MCP servers, plugins

---

## References

- [VS Code Copilot Documentation](https://code.visualstudio.com/docs/copilot)
- [VS Code Agents Documentation](https://code.visualstudio.com/docs/copilot/chat/agents)
- [GitHub Copilot Trust Center](https://resources.github.com/copilot-trust-center/)
- [Agent Skills Standard](https://agentskills.io)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Awesome Copilot Repository](https://github.com/nicobailon/awesome-copilot)
