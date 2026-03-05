# Agent Orchestration Patterns

> Practical patterns for composing multi-agent workflows using subagents, custom agents, and handoffs.

---

## Overview

Orchestration is how you compose multiple agents to handle complex tasks. VS Code
supports several patterns, each suited to different scenarios.

```
Pattern Spectrum (simple to complex):
    |
    Single Agent  ->  Subagent Delegation  ->  Coordinator-Worker  ->  Multi-Perspective  ->  Full Pipeline
```

---

## Pattern 1: Coordinator-Worker

A coordinator agent manages the overall task and delegates subtasks to specialized
worker agents. Each worker has tailored tools and a narrower focus.

### Architecture

```
User: "Build user registration feature"
    |
    v
Feature Builder (coordinator)
    |
    |-- Planner subagent (read-only tools)
    |       Returns: step-by-step plan
    |
    |-- Plan Architect subagent (read-only tools)
    |       Returns: validation against codebase patterns
    |
    |-- Implementer subagent (read+write tools, cheaper model)
    |       Returns: implemented code
    |
    |-- Reviewer subagent (read-only tools)
    |       Returns: code review findings
    |
    v
Feature Builder synthesizes and presents result
```

### Implementation

**Coordinator** (`Feature-Builder.agent.md`):

```markdown
---
name: Feature Builder
tools: ['agent', 'edit', 'search', 'read']
agents: ['Planner', 'Plan-Architect', 'Implementer', 'Reviewer']
---
You are a feature development coordinator. For each feature request:

1. Use the Planner agent to break down the feature into tasks.
2. Use the Plan Architect agent to validate the plan against codebase patterns.
3. If the architect identifies reusable patterns, send feedback to update the plan.
4. Use the Implementer agent to write the code for each task.
5. Use the Reviewer agent to check the implementation.
6. If the reviewer identifies issues, use the Implementer agent again to fix them.

Iterate between planning and implementation until each phase converges.
```

**Worker -- Planner** (`Planner.agent.md`):

```markdown
---
name: Planner
user-invocable: false
tools: ['read', 'search']
---
Break down feature requests into implementation tasks.
Incorporate feedback from the Plan Architect.
```

**Worker -- Implementer** (`Implementer.agent.md`):

```markdown
---
name: Implementer
user-invocable: false
model: ['Claude Haiku 4.5 (copilot)', 'Gemini 3 Flash (Preview) (copilot)']
tools: ['edit', 'create', 'read', 'search', 'runInTerminal']
---
Write code to complete assigned tasks. Run tests after implementation.
```

**Worker -- Reviewer** (`Reviewer.agent.md`):

```markdown
---
name: Reviewer
user-invocable: false
tools: ['read', 'search', 'problems']
---
Review code for quality, security, and adherence to project conventions.
DO NOT edit files. Provide findings and recommendations only.
```

### When to Use

- Complex features requiring research, planning, implementation, and review
- Tasks where different phases need different capabilities
- Projects where code review is mandatory before completion

---

## Pattern 2: Multi-Perspective Code Review

Run multiple independent review perspectives as parallel subagents, then
synthesize findings. Each subagent approaches the code fresh without
bias from other perspectives.

### Architecture

```
User: "Review the authentication module"
    |
    v
Thorough Reviewer (coordinator)
    |
    |-- Correctness subagent (parallel)
    |       Focus: logic errors, edge cases, type issues
    |
    |-- Code Quality subagent (parallel)
    |       Focus: readability, naming, duplication
    |
    |-- Security subagent (parallel)
    |       Focus: input validation, injection, data exposure
    |
    |-- Architecture subagent (parallel)
    |       Focus: patterns, design consistency, structure
    |
    v
Thorough Reviewer prioritizes and synthesizes all findings
```

### Implementation

```markdown
---
name: Thorough Reviewer
tools: ['agent', 'read', 'search']
---
You review code through multiple perspectives simultaneously.
Run each perspective as a parallel subagent.

When asked to review code, run these subagents in parallel:
- Correctness reviewer: logic errors, edge cases, type issues
- Code quality reviewer: readability, naming, duplication
- Security reviewer: input validation, injection risks, data exposure
- Architecture reviewer: codebase patterns, design consistency

After all subagents complete, synthesize findings into a prioritized
summary. Note which issues are critical versus nice-to-have.
Acknowledge what the code does well.
```

### When to Use

- Code reviews where multiple perspectives add value
- Audit scenarios (security, accessibility, performance)
- Any analysis where independent viewpoints are important

---

## Pattern 3: Test-Driven Development (TDD)

Three specialized agents for the classic Red-Green-Refactor cycle.

### Architecture

```
User: "Implement email validation with TDD"
    |
    v
TDD Coordinator
    |
    |-- Red Agent: write failing tests
    |       Returns: test file with failing tests
    |
    |-- User reviews tests
    |
    |-- Green Agent: write code to make tests pass
    |       Returns: implementation code
    |
    |-- Refactor Agent: improve code quality
    |       Returns: refactored code + re-run tests
    |
    v
TDD Coordinator confirms all tests pass
```

### Implementation

**Coordinator** (`TDD.agent.md`):

```markdown
---
name: TDD
tools: ['agent', 'edit', 'read', 'runInTerminal']
agents: ['Red', 'Green', 'Refactor']
---
Implement features using test-driven development:
1. Use the Red agent to write failing tests that define the expected behavior
2. Confirm the tests fail (run them)
3. Use the Green agent to write the minimum code to make tests pass
4. Run the tests to confirm they pass
5. Use the Refactor agent to improve the code while keeping tests green
```

**Red Agent** (`Red.agent.md`):

```markdown
---
name: Red
user-invocable: false
tools: ['edit', 'create', 'read', 'search']
---
Write failing tests that define expected behavior.
Tests should be specific, focused, and follow the project's testing conventions.
Do NOT write implementation code.
```

**Green Agent** (`Green.agent.md`):

```markdown
---
name: Green
user-invocable: false
model: ['Claude Haiku 4.5 (copilot)']
tools: ['edit', 'create', 'read']
---
Write the MINIMUM code to make the failing tests pass.
Do not over-engineer. Do not add untested functionality.
```

**Refactor Agent** (`Refactor.agent.md`):

```markdown
---
name: Refactor
user-invocable: false
tools: ['edit', 'read', 'search', 'runInTerminal']
---
Improve code quality without changing behavior.
After refactoring, run the tests to confirm they still pass.
```

### When to Use

- Disciplined feature development with test coverage
- Teams that practice TDD and want AI to follow the same discipline
- Critical code where test-first ensures correctness

---

## Pattern 4: Handoff Pipeline

Use custom agent **handoffs** to create sequential workflows with user review gates
between stages. Unlike subagents (which run within a session), handoffs transition
between separate agent sessions.

### Architecture

```
User: "Build a new API endpoint"
    |
    v
Plan Agent  -->  [Handoff: "Start Implementation"]  -->  Implementation Agent
                                                              |
                                                    [Handoff: "Review Code"]
                                                              |
                                                              v
                                                     Review Agent
```

### Implementation

**Plan Agent** (`Planner.agent.md`):

```markdown
---
name: Planner
description: Generate implementation plans
tools: ['search', 'read', 'codebase']
handoffs:
  - label: Start Implementation
    agent: Implementation
    prompt: Implement the plan outlined above.
    send: false
    model: GPT-5.2 (copilot)
---
You create detailed implementation plans. Research the codebase thoroughly.
Ask clarifying questions. Output a step-by-step plan.
```

**Implementation Agent** (`Implementation.agent.md`):

```markdown
---
name: Implementation
description: Implement from plans
tools: ['edit', 'create', 'read', 'runInTerminal']
handoffs:
  - label: Review Code
    agent: Reviewer
    prompt: Review the implementation above for quality and security.
    send: false
---
Implement the given plan step by step. Run tests after each major change.
```

### When to Use

- Multi-stage workflows with user review between stages
- Teams that want to approve plans before implementation
- Quality gates (plan -> implement -> review -> approve)

---

## Pattern 5: Research and Implement

The simplest orchestration pattern. The Plan agent researches, then
hands off to an implementation agent.

### Workflow

```
1. Select Plan agent
2. Enter: "How should we add rate limiting to the API?"
3. Plan agent researches, asks questions, produces plan
4. Review the plan
5. Click "Start Implementation" -> Agent implements the plan
```

This requires no custom agent setup -- it uses the built-in Plan and Agent modes.

---

## Pattern 6: Parallel Sessions

Run multiple independent agent sessions simultaneously. Each session
has its own context and can use a different agent type.

### Architecture

```
Session A (Background): "Implement auth module"
Session B (Background): "Implement logging module"
Session C (Local): "Design the API schema"
Session D (Cloud): "Set up CI/CD pipeline"
```

Each runs independently. Monitor all from the Sessions view.

### When to Use

- Multiple independent tasks
- Different tasks requiring different agent types
- Exploratory work (try multiple approaches simultaneously)

---

## Choosing a Pattern

| Scenario | Best Pattern |
|----------|-------------|
| Feature with research + implementation | Coordinator-Worker |
| Code review | Multi-Perspective |
| Test-first development | TDD |
| Multi-stage with approval gates | Handoff Pipeline |
| Quick research then implement | Research and Implement |
| Multiple independent tasks | Parallel Sessions |

---

## Pattern Composition

Patterns can be combined. For example:

```
Coordinator-Worker pattern
    |
    +-- Worker uses TDD pattern internally
    |       |
    |       +-- Red/Green/Refactor subagents
    |
    +-- Reviewer uses Multi-Perspective pattern
            |
            +-- Security/Quality/Architecture subagents
```

---

## Next Steps

- [Custom Agents](../04-customization/custom-agents.md) -- define the agent files
- [Hooks](../04-customization/hooks.md) -- automate lifecycle events
- [Examples](../06-examples/) -- working configuration files
