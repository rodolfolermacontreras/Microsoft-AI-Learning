# Agent Skills

> Portable, on-demand capabilities that work across VS Code, Copilot CLI, and Copilot coding agent.

---

## What Agent Skills Are

Agent Skills are folders containing instructions, scripts, and resources that the AI
loads when relevant. Unlike instructions (always-on), skills are loaded **on-demand**
based on the task.

Agent Skills is an **open standard** (agentskills.io) that works across multiple
AI agents, not just VS Code.

---

## Skill vs Instructions vs Prompts

| Feature | Skills | Instructions | Prompt Files |
|---------|--------|-------------|-------------|
| Loading | On-demand | Always included | Manual invocation |
| Portability | VS Code, CLI, coding agent | VS Code only | VS Code only |
| Content | Instructions + scripts + resources | Instructions only | Task template |
| Standard | Open (agentskills.io) | VS Code-specific | VS Code-specific |

---

## Skill Structure

```
.github/skills/
    webapp-testing/
        SKILL.md              # Required -- skill definition
        test-template.js      # Optional -- bundled resources
        examples/             # Optional -- example files
```

### SKILL.md Format

```markdown
---
name: webapp-testing
description: Run and debug web application tests with Playwright and Jest
argument-hint: [test file] [options]
---

# Web Application Testing

When testing web applications:

1. Check for existing test configuration (jest.config, playwright.config)
2. Run existing tests first: `npm test`
3. If tests fail, analyze the error output
4. Fix the root cause, not the symptom
5. Re-run to confirm the fix

## Playwright Tests

Use the [test template](./test-template.js) as a starting point for new tests.

## Jest Tests

- Use descriptive test names
- Follow Arrange-Act-Assert pattern
- Mock external dependencies with `jest.mock()`
```

---

## SKILL.md Frontmatter

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier (lowercase, hyphens). Must match directory name. Max 64 chars. |
| `description` | Yes | When to use the skill. Max 1024 chars. |
| `argument-hint` | No | Hint text for slash command usage |
| `user-invocable` | No | Show as `/skill-name` command (default: true) |
| `disable-model-invocation` | No | Prevent automatic loading (default: false) |

---

## Skill Locations

| Scope | Paths |
|-------|-------|
| Project | `.github/skills/`, `.claude/skills/`, `.agents/skills/` |
| Personal | `~/.copilot/skills/`, `~/.claude/skills/`, `~/.agents/skills/` |

Additional locations via `chat.agentSkillsLocations` setting.

---

## How Skills Load (Progressive Disclosure)

```
Level 1: Discovery
    AI reads name + description from frontmatter (lightweight)
        |
        v
Level 2: Instructions Loading
    When task matches description, AI loads SKILL.md body
        |
        v
Level 3: Resource Access
    AI accesses additional files in skill directory as needed
```

This three-level system means you can install many skills without consuming context.
Only relevant content loads.

---

## Using Skills

- Type `/skill-name` in chat (as a slash command)
- Or let the AI auto-load when the task matches the description

---

## Generating Skills

| Command | What It Does |
|---------|-------------|
| `/create-skill` | AI generates a skill from your description |
| `/skills` | Opens Configure Skills menu |

Extract from conversations: "create a skill from how we just debugged that."

---

## Next Steps

- [Hooks](hooks.md) -- lifecycle automation
- [MCP Servers](mcp-servers.md) -- external tool integration
