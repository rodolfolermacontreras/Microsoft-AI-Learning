# Prompt Files (Slash Commands)

> Reusable task templates you invoke with `/command-name` in chat.

---

## What Prompt Files Are

Prompt files are Markdown files with `.prompt.md` extension. They encode common tasks
as reusable templates that you invoke with `/` in chat. Unlike custom instructions
(which apply automatically), prompt files are invoked manually.

---

## File Format

```markdown
---
name: create-component
description: Scaffold a new React component
argument-hint: ComponentName
agent: agent
model: Claude Sonnet 4.5 (copilot)
tools: ['edit', 'create', 'read', 'search']
---

Create a new React component with the following structure:
- Component file: src/components/${input:name}/index.tsx
- Styles: src/components/${input:name}/styles.module.css
- Tests: src/components/${input:name}/${input:name}.test.tsx
- Storybook: src/components/${input:name}/${input:name}.stories.tsx

Follow the patterns in [coding standards](../copilot-instructions.md).
```

---

## Frontmatter Reference

| Field | Description |
|-------|-------------|
| `name` | Command name shown after `/` |
| `description` | Short description |
| `argument-hint` | Hint text in chat input |
| `agent` | Agent to use: `agent`, `plan`, `ask`, or custom agent name |
| `model` | Preferred language model |
| `tools` | Available tools for this prompt |

---

## Variables

| Variable | Value |
|----------|-------|
| `${workspaceFolder}` | Workspace root path |
| `${file}` | Current file path |
| `${fileBasename}` | Current file name |
| `${selection}` | Current editor selection |
| `${input:varName}` | User input from chat |
| `${input:varName:placeholder}` | User input with placeholder hint |

---

## File Locations

| Scope | Path |
|-------|------|
| Workspace | `.github/prompts/` |
| User profile | VS Code profile prompts folder |

Additional locations via `chat.promptFilesLocations` setting.

---

## Using Prompt Files

```
/create-component MyButton
/security-review
/create-api for listing customers
```

Or: Command Palette > Chat: Run Prompt > Select prompt.

---

## Generating Prompt Files

| Command | What It Does |
|---------|-------------|
| `/create-prompt` | AI generates a prompt file from your description |
| `/prompts` | Opens Configure Prompt Files menu |

You can also extract prompts from conversations: "turn this into a reusable prompt."

---

## Example: Security Review Prompt

```markdown
---
name: security-review
description: Review code for security vulnerabilities
tools: ['read', 'search', 'codebase', 'problems']
agent: ask
---

Perform a security review of ${file}. Check for:
1. SQL injection and command injection
2. Cross-site scripting (XSS)
3. Hardcoded credentials or API keys
4. Path traversal vulnerabilities
5. Insecure deserialization
6. Missing input validation
7. Overly permissive CORS or file permissions

Provide findings ranked by severity (critical, high, medium, low).
```

---

## Next Steps

- [Agent Skills](agent-skills.md) -- portable capabilities across tools
- [Custom Agents](custom-agents.md) -- agent personas
