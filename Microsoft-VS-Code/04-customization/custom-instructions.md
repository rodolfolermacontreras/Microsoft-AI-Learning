# Custom Instructions

> Define project-wide coding standards that automatically influence every AI interaction.

---

## What Custom Instructions Are

Custom instructions are Markdown files that tell the AI about your coding conventions,
architecture decisions, and project context. They are included automatically in every
chat request -- no need to repeat them manually.

---

## Types of Instruction Files

### Always-On Instructions

Automatically included in every chat request.

| File | Location | Scope |
|------|----------|-------|
| `copilot-instructions.md` | `.github/copilot-instructions.md` | Workspace-wide |
| `AGENTS.md` | Project root (or subfolders) | Workspace-wide |
| `CLAUDE.md` | Project root, `.claude/`, or `~/` | Cross-tool compatibility |
| Organization instructions | GitHub org settings | All repos in org |

### File-Based Instructions

Applied conditionally based on file patterns or task relevance.

| File | Location | Scope |
|------|----------|-------|
| `*.instructions.md` | `.github/instructions/` | Pattern-matched files |

---

## copilot-instructions.md

The primary instruction file. Create at `.github/copilot-instructions.md`:

```markdown
# Project Coding Guidelines

## Code Style
- Use semantic HTML5 elements
- Prefer ES6+ features (const/let, arrow functions, template literals)
- Use TypeScript strict mode

## Naming Conventions
- PascalCase for components and interfaces
- camelCase for variables, functions, methods
- ALL_CAPS for constants

## Error Handling
- Always handle errors explicitly
- Use custom error classes for domain errors
- Log errors with structured context
```

---

## File-Based Instructions (.instructions.md)

Apply different rules to different file types using `applyTo` glob patterns:

```markdown
---
name: Python Standards
description: Coding conventions for Python files
applyTo: '**/*.py'
---
# Python coding standards
- Follow PEP 8 style guide
- Use type hints for all function signatures
- Write docstrings for public functions
- Use 4 spaces for indentation
```

```markdown
---
name: Test Conventions
description: Testing standards
applyTo: '**/*.test.{ts,js}'
---
# Testing standards
- Use descriptive test names that explain the expected behavior
- Follow Arrange-Act-Assert pattern
- Mock external dependencies
- Test edge cases and error paths
```

---

## AGENTS.md

For cross-agent compatibility (works with multiple AI tools):

```markdown
# Project Context

This is a TypeScript monorepo using pnpm workspaces.

## Architecture
- packages/api -- Express REST API
- packages/web -- React frontend
- packages/shared -- Shared types and utilities

## Conventions
- Use barrel exports (index.ts) in each package
- All API responses follow the { data, error, meta } format
```

Nested AGENTS.md (experimental): Place in subfolders for folder-specific rules.

---

## Generating Instructions

| Command | What It Does |
|---------|-------------|
| `/init` | Analyzes workspace and generates copilot-instructions.md |
| `/create-instruction` | AI generates a targeted .instructions.md file |
| `/instructions` | Opens the Configure Instructions menu |

---

## Tips

1. Keep instructions concise -- they load on every interaction
2. Focus on what the AI cannot infer from code (non-obvious conventions)
3. Show examples of preferred and avoided patterns
4. Explain WHY behind rules (helps the AI handle edge cases)
5. Use separate files per concern (Python rules, test rules, API rules)
6. Store in workspace to share with team via version control

---

## Next Steps

- [Prompt Files](prompt-files.md) -- reusable task templates
- [Agent Skills](agent-skills.md) -- portable capabilities
