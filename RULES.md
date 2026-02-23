# Rules and Best Practices

> **REQUIRED READING** -- Every contributor and every AI agent working on this repo must follow these rules.
> This file is the single source of truth for development standards.
> Last updated: 2026-02-23

---

## Table of Contents

1. [Code Quality](#1-code-quality)
2. [Version Control](#2-version-control)
3. [Documentation](#3-documentation)
4. [Script Management](#4-script-management)
5. [Data Science Practices](#5-data-science-practices)
6. [Testing](#6-testing)
7. [Security](#7-security)
8. [Project Planning](#8-project-planning)
9. [AI Agent Rules](#9-ai-agent-rules)
10. [Claude Agent Architecture](#10-claude-agent-architecture)
11. [Development Workflow](#11-development-workflow)
12. [Quick Reference](#12-quick-reference)

---

## 1. Code Quality

### Absolute Rules

- **No emojis** in code, comments, commit messages, or documentation. They cause encoding issues and look unprofessional in production code.
- **Use the project virtual environment** (`.venv`). Never install to the global Python environment.
- **Type hints** on all Python function signatures.
- **Docstrings** on all modules, functions, and classes.

### Naming Conventions

| Type | Convention | Good | Bad |
|------|------------|------|-----|
| Functions | `verb_noun` | `calculate_weighted_average()` | `calc()` |
| Variables | descriptive | `user_count` | `x` |
| Classes | PascalCase | `DataProcessor` | `data_processor` |
| Constants | UPPER_SNAKE | `MAX_RETRIES` | `maxRetries` |
| Files | snake_case | `kusto_connection.py` | `KustoConnection.py` |
| Branches | type/description | `feat/add-auth` | `new-stuff` |

### Code Organization (within a file)

```
1. Module docstring
2. Imports (stdlib, then third-party, then local)
3. Constants
4. Type definitions
5. Helper functions (private)
6. Main classes / public functions
7. Entry point (if __name__ == "__main__")
```

### Error Handling

```python
# CORRECT: Specific exceptions with context
try:
    result = api.fetch_data(endpoint)
except ConnectionError as e:
    logger.error(f"Failed to connect to {endpoint}: {e}")
    raise DataFetchError(f"Could not retrieve data from {endpoint}") from e

# WRONG: Bare except, silent failure
try:
    result = api.fetch_data(endpoint)
except:
    pass
```

### Style Guidelines

- Follow PEP 8 for Python, ESLint conventions for JavaScript, consistent SQL capitalization.
- Explain WHY in comments, not WHAT.
- Prefer `with` statements for resource management (files, connections, sessions).
- Use f-strings for string formatting, not `.format()` or `%`.

---

## 2. Version Control

### Branch Rules

- **Never commit directly to main.** All changes go through feature branches.
- **One branch = one logical unit of work.** Do not bundle unrelated changes.
- **Delete branches after merge.**

### Branch Naming

```
<type>/<short-description>

Types:
  feat/      New feature
  fix/       Bug fix
  docs/      Documentation only
  refactor/  Code restructuring (no behavior change)
  test/      Adding or updating tests
  chore/     Maintenance, config, dependencies
```

### Commit Messages

Use conventional commits format: `<type>: <description>`

```
GOOD:
  feat: add user authentication with JWT
  fix: resolve null pointer in data aggregation
  docs: update kusto_app README with schema guide
  refactor: extract validation into separate module

BAD:
  updated stuff
  fix bug
  WIP
  asdf
```

### Branch Workflow

```
1. git pull origin main
2. git checkout -b <type>/<description>
3. Make changes, commit incrementally
4. git push origin <branch-name>
5. Create Pull Request
6. After merge: delete branch locally and remotely
```

### Branch Tracking

Maintain a `BRANCH_HISTORY.md` if the project grows beyond simple feature work:
- Active Branches: name, goal, status, date created
- Archived Branches: name, goal, final status (merged/abandoned), date closed

---

## 3. Documentation

### Project Structure

Every project folder must have a `README.md` that covers:
- What the project does (one paragraph)
- Directory structure
- Prerequisites and setup
- How to run it
- Key concepts

### Core Documentation Files

Adapt to project needs -- not every project needs all of these:

| File | Purpose |
|------|---------|
| `README.md` | Overview, setup, usage |
| `RULES.md` | This file (repo-wide standards) |
| `PROJECT_STATUS_REVIEW.md` | Chronological change log |
| `SYSTEM_ARCHITECTURE.md` | Technical design and data flows |
| `METHODOLOGY.md` | Statistical/analytical approaches |

### Documentation Discipline

- Update docs **as you code**, not later. Same commit.
- Before creating a new doc file, check if existing files can accommodate the content.
- Track significant changes with date, what changed, why, and results.
- Clear notebook outputs before committing: `jupyter nbconvert --clear-output --inplace notebook.ipynb`

---

## 4. Script Management

### No Orphan Scripts

Every script must live inside a project folder with a README that explains it. No scripts floating at the repo root.

Before deleting a scaffolding script, verify:
- Functionality is integrated into the main system
- Tests pass without it
- No other code depends on it
- Documentation is updated

### Production Script Standards

Any script that is not a quick throwaway must have:
- Module-level docstring
- Function docstrings
- Error handling (not bare `print` for errors)
- Logging (use `logging` module)
- Argument parsing (for CLI scripts)
- Usage examples in docstring or README

---

## 5. Data Science Practices

### Reproducibility

- Set random seeds: `random.seed(42)`, `np.random.seed(42)`
- Version data (track file versions, checksums, timestamps)
- Document all transformations applied to data
- Save intermediate results for long pipelines

### Data Validation

- Validate inputs before processing (nulls, ranges, types)
- Log data quality metrics (row counts, null percentages, outlier counts)
- Validate joins (expected row counts, no unintended duplicates)
- Compare to baseline when rerunning (flag >5% deviations)

### Methodology Documentation

- Write out statistical formulas (use LaTeX: $\bar{x} = \frac{1}{n}\sum_{i=1}^{n}x_i$)
- State assumptions and limitations explicitly
- Document validation approach (backtesting, cross-validation splits)
- Track metrics (accuracy, MAPE, $R^2$, etc.) with dates

### Notebook Discipline

- Clear all outputs before committing
- Use markdown cells with headers (H1, H2) for structure
- Number sections (1.1, 1.2, 2.1)
- Include executive summary at the top
- **Production code goes in `.py` files, not notebooks.** Notebooks are for exploration only.

---

## 6. Testing

### When to Test

- After implementing new functionality
- After fixing a bug
- After refactoring
- Before declaring any task complete

### Test Structure

```python
# tests/test_feature.py
def test_happy_path():
    """Normal input produces expected output."""
    ...

def test_edge_case():
    """Boundary inputs are handled correctly."""
    ...

def test_error_case():
    """Invalid input raises appropriate error."""
    ...
```

### Pre-Merge Checklist

```
[ ] All tests pass
[ ] Code follows style guide
[ ] Documentation updated
[ ] No hardcoded credentials or paths
[ ] No debug print statements left
[ ] No orphan scripts introduced
```

---

## 7. Security

### Secrets

- **Never commit** API keys, passwords, or connection strings.
- Use environment variables: `api_key = os.getenv("API_KEY")`
- Use `.env` files (listed in `.gitignore`).
- Document required secrets in `.env.template` without exposing values.
- Never log passwords or tokens, even at DEBUG level.

### Input Validation

```python
# CORRECT: Validate and sanitize
def process_input(data: str) -> str:
    if not data or len(data) > MAX_LENGTH:
        raise ValueError("Invalid input length")
    return sanitize(data)

# WRONG: Trust user input blindly
def process_input(data):
    return eval(data)  # DANGEROUS
```

### Sensitive Data in Output

- Mask secrets in error messages and logs.
- Never print full API keys -- show only last 4 characters if needed.
- Review all output before sharing screenshots or logs.

---

## 8. Project Planning

### Big Picture Plan

At the end of every significant status update, include:

```
CURRENT PHASE: [what we are working on now]
IMMEDIATE PRIORITIES (This Week): [1-3 items]
NEXT PHASE (Next 2 Weeks): [planned work]
LONG-TERM GOALS (Next Month+): [strategic direction]
```

This prevents tunnel vision on a single task while losing sight of overall goals.

### Task Tracking

For multi-step work, maintain a checklist:

```
[ ] Task 1: Description -- NOT STARTED
[ ] Task 2: Description -- IN PROGRESS
[x] Task 3: Description -- COMPLETE
```

---

## 9. AI Agent Rules

### What Agents Must Always Do

- **Explain reasoning before implementing.** State the approach, then execute.
- **Show diffs for file changes.** Use proper edit tools, not codeblocks.
- **Ask for confirmation on destructive operations** (deleting files, dropping data, force-pushing).
- **Validate assumptions.** If the requirement is ambiguous, ask before guessing.
- **Provide rollback instructions** when making significant changes.

### What Agents Must Never Do

- Make breaking changes without explicit approval.
- Delete files or data without confirmation.
- Commit directly to main branch.
- Add dependencies without discussion.
- Assume requirements -- ask when uncertain.
- Use emojis in code, commits, or docs.
- Hardcode credentials, paths, or machine-specific values.

### Agent Workflow

```
1. RESEARCH  -- Understand the request. Read existing code and context.
2. PLAN      -- Break into discrete subtasks. State the plan.
3. IMPLEMENT -- Execute one subtask at a time. Commit working increments.
4. VALIDATE  -- Test and verify before moving to the next subtask.
```

### Context Management (for Claude agents)

| Rule | Reason |
|------|--------|
| Manual compact at 50% context | Proactive is better than auto-compact |
| Each subtask should complete before context fills | Avoid partial work from truncation |
| Keep CLAUDE.md under 150 lines | Shorter context files get more reliable adherence |
| Commit often | Checkpoints let you reset if context degrades |

---

## 10. Claude Agent Architecture

This section documents how to structure agents, skills, and commands when working with Claude Code on any project in this repo.

### Component Hierarchy

```
USER invokes COMMAND
  -- COMMAND triggers AGENT
       -- AGENT uses SKILLS
             -- SKILLS provide domain knowledge
```

### Component Definitions

| Component | Purpose | Location |
|-----------|---------|----------|
| Skill | Reusable knowledge package | `.claude/skills/<name>/SKILL.md` |
| Agent | Specialized worker with tools and memory | `.claude/agents/<name>.md` |
| Command | User entry point (slash command) | `.claude/commands/<name>.md` |
| Hook | Lifecycle event handler (deterministic) | `.claude/hooks/` |
| Memory | Persistent context across sessions | `.claude/agent-memory/` |

### Skill Definition (YAML Frontmatter)

```yaml
---
name: my-skill
description: When to invoke this skill (Claude uses for auto-discovery)
argument-hint: [optional-arg]
allowed-tools: Read, Write, Bash(npm test *)
user-invocable: true
disable-model-invocation: false
context: fork
---

# Skill Instructions
Detailed instructions for what this skill does...
```

### Agent Definition (YAML Frontmatter)

```yaml
---
name: code-reviewer
description: Use PROACTIVELY when reviewing code changes
tools: Read, Write, Edit, Bash, Grep
model: sonnet
permissionMode: acceptEdits
maxTurns: 25
skills:
  - code-conventions
  - security-checklist
memory: project
---

You are a senior code reviewer. Focus on security and clarity.
```

### Memory Scopes

| Scope | Location | Shared via Git | Best For |
|-------|----------|----------------|----------|
| `user` | `~/.claude/agent-memory/` | No | Cross-project knowledge |
| `project` | `.claude/agent-memory/` | Yes | Team-shared knowledge |
| `local` | `.claude/agent-memory-local/` | No | Personal project knowledge |

### Loading Behavior

| Type | When Loaded |
|------|-------------|
| Ancestor CLAUDE.md (parent dirs) | Always at startup |
| Descendant CLAUDE.md (child dirs) | Lazy-loaded when touching files there |
| Sibling CLAUDE.md | Never loaded |
| Agent's `skills:` field | Preloaded at agent startup |

### Invoking Agents

```
# CORRECT -- use the Task tool
Task(
  subagent_type="agent-name",
  description="What this task accomplishes",
  prompt="Detailed instructions..."
)

# WRONG -- never invoke agents via bash
bash("claude --agent=reviewer ...")
```

### Project Layout for Claude

```
project/
+-- .claude/
|   +-- settings.json          # Team settings (committed)
|   +-- settings.local.json    # Personal settings (gitignored)
|   +-- agents/*.md            # Custom agents
|   +-- skills/<name>/SKILL.md # Reusable skills
|   +-- commands/*.md          # User-invocable commands
|   +-- rules/*.md             # Modular rules by topic
|   +-- hooks/scripts/         # Hook handlers
+-- CLAUDE.md                  # Project context (< 150 lines)
+-- src/
```

---

## 11. Development Workflow

### Starting New Work

```
1. [ ] git pull origin main
2. [ ] git checkout -b <type>/<description>
3. [ ] Activate virtual environment: .\.venv\Scripts\Activate.ps1
4. [ ] Read RULES.md if you haven't recently
5. [ ] Understand the existing code before changing anything
```

### During Development

```
1. [ ] Commit incrementally with conventional commit messages
2. [ ] Update documentation as you go (same commit)
3. [ ] Track scaffolding scripts -- delete when integrated
4. [ ] Run tests frequently
5. [ ] No emojis in code or commits
```

### Before Merging

```
1. [ ] All tests pass
2. [ ] Documentation updated
3. [ ] Scaffolding scripts deleted or justified
4. [ ] Code reviewed
5. [ ] No hardcoded credentials or paths
6. [ ] No debug print statements
7. [ ] Big picture plan reviewed
```

### After Merging

```
1. [ ] Delete feature branch (local and remote)
2. [ ] Update branch tracking if maintained
```

---

## 12. Quick Reference

### Red Flags (Rule Violations)

- Multiple undocumented scripts appear at repo root
- Main branch has direct commits
- Documentation outdated by more than one week
- Tests failing on main branch
- Emojis in commit messages or code
- Hardcoded secrets anywhere in the codebase
- Orphan scripts without README coverage

### File Change Checklist

```
[ ] Understood the existing code before changing it
[ ] Made minimal, targeted changes
[ ] Followed project conventions
[ ] Handled errors appropriately
[ ] Tested the changes
[ ] No regressions introduced
[ ] Documentation updated
```

### Debugging Process

```
1. READ the error message carefully
2. IDENTIFY the file and line number
3. UNDERSTAND what the code was trying to do
4. CHECK the inputs and state at that point
5. FIX the root cause, not just the symptom
```

### Common Python Issues

| Symptom | Likely Cause | Check |
|---------|-------------|-------|
| ImportError | Missing dependency | requirements.txt, venv activation |
| TypeError | Wrong argument type | Function signature, type hints |
| KeyError | Missing dict key | Data structure, API response shape |
| AttributeError | Wrong object type | Variable assignment chain |
| Event loop closed | Async lifecycle issue | Session and loop management |

---

*This document governs all work in this repository. When in doubt, follow these rules. When the rules conflict with project-specific needs, document the exception in that project's README.*
