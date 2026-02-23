# 03 - Multi-Agent Workflows

## What This Covers

- 4 orchestration patterns: Sequential, Concurrent, Handoff, Group Chat
- Manual implementation (no extra package needed)
- Orchestration-based implementation (`agent-framework-orchestrations`)
- Real-world patterns: content pipeline, fan-out analysis, task routing

## Workflow Patterns

### 🔗 Sequential (Pipeline)
Agents process in order, each building on the previous output.

```
User Input → Writer → Reviewer → Publisher → Final Output
```

**Use When**: Multi-step processing where each step refines the output.

### ⚡ Concurrent (Fan-Out / Fan-In)
Multiple agents work simultaneously, results are combined.

```
                ┌→ Researcher ─┐
User Input ─────┤              ├→ Combiner → Output
                └→ Analyst ────┘
```

**Use When**: Independent tasks that can be parallelized for speed.

### 🔀 Handoff (Delegation)
A router agent analyzes the request and delegates to a specialist.

```
                ┌→ Writer
User Input → Router ─┤→ Researcher
                └→ Analyst
```

**Use When**: Requests that need different expertise based on content.

### 💬 Group Chat
Agents collaborate in a shared conversation with turn-taking.

```
User Input → [Writer ↔ Reviewer ↔ Researcher] → Consensus Output
```

**Use When**: Complex tasks requiring multiple perspectives and iteration.

## Installation

```bash
# Core framework
pip install agent-framework --pre

# Orchestration patterns (Sequential, Concurrent, Handoff, Group Chat)
pip install agent-framework-orchestrations --pre
```

## Key Code Patterns

### Sequential (with orchestrations)
```python
from agent_framework.orchestrations import SequentialWorkflow

workflow = SequentialWorkflow(agents=[writer, reviewer, publisher])
result = await workflow.invoke(session, "Write about X")
```

### Sequential (manual)
```python
draft = await writer.invoke(session, "Write about X")
reviewed = await reviewer.invoke(AgentSession(), f"Review: {draft}")
final = await publisher.invoke(AgentSession(), f"Publish: {reviewed}")
```

### Concurrent (manual with asyncio)
```python
research, analysis = await asyncio.gather(
    researcher.invoke(AgentSession(), topic),
    analyst.invoke(AgentSession(), topic),
)
```

## Migration from AutoGen

| AutoGen | Agent Framework |
|---------|-----------------|
| `GroupChat(agents=[...])` | `GroupChat(agents=[...])` |
| `GroupChatManager` | Built into orchestration |
| Manual sequential loops | `SequentialWorkflow` |
| `ConversableAgent` | `AIAgent` |
| `register_function` | `@function_tool` + `tools=[...]` |

## Running

```bash
$env:OPENAI_API_KEY = "sk-..."
python multi_agent.py
```
