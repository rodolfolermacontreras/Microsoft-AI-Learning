# Microsoft Agent Framework — Core Concepts & Architecture

> **📌 Follow**: [../../AGENT_DEVELOPMENT_GUIDE.md](../../AGENT_DEVELOPMENT_GUIDE.md)

---

## Evolution

```
Semantic Kernel (2023-2025)     AutoGen (2023-2025)
         │                              │
         └──────────┬───────────────────┘
                    ▼
    Microsoft Agent Framework (2026)
    ├── Unified API across .NET & Python
    ├── Simpler agent creation
    ├── Built-in workflow orchestration
    └── Multi-provider support
```

---

## Core Abstractions

### 1. AIAgent — The Universal Agent Type

In Agent Framework, **one type handles all providers**:

```python
# Python — All providers use the same pattern
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential

agent = AzureOpenAIResponsesClient(
    credential=AzureCliCredential(),
).as_agent(
    name="MyAgent",
    instructions="You are a helpful assistant.",
)

# Run (non-streaming)
response = await agent.run("Hello!")

# Run (streaming)
async for update in agent.run_streaming("Hello!"):
    print(update.text, end="")
```

**Contrast with Semantic Kernel** — SK needed different agent classes per provider:
| SK Agent Type | AF Equivalent |
|--------------|---------------|
| `ChatCompletionAgent` | `client.as_agent()` |
| `OpenAIAssistantAgent` | `assistant_client.create_ai_agent()` |
| `AzureAIAgent` | `persistent_agents_client.create_ai_agent()` |

In AF, it's **always** `.as_agent()` or `.create_ai_agent()`.

---

### 2. Function Tools — Direct Registration

No more `[KernelFunction]` attributes, plugins, or kernel instances:

```python
# Python
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"Weather in {city}: 72°F, sunny"

agent = client.as_agent(
    name="WeatherBot",
    instructions="Help users with weather info.",
    tools=[get_weather],  # Direct function reference
)
```

```csharp
// .NET
AIAgent agent = chatClient.AsAIAgent(
    tools: [AIFunctionFactory.Create(GetWeather)]
);
```

**SK required**: KernelFunction attribute → Plugin class → Kernel → Agent  
**AF requires**: Function → Agent. Done.

---

### 3. Sessions — Agent-Managed Conversations

```python
# Python — agent creates its own session
session = await agent.create_session()
response = await agent.run("Hello!", session=session)
response = await agent.run("Follow up question", session=session)
```

```csharp
// .NET
AgentSession session = await agent.CreateSessionAsync();
AgentResponse response = await agent.RunAsync("Hello!", session);
```

**SK required**: Caller manually created typed threads (`OpenAIAssistantAgentThread`, `AzureAIAgentThread`).  
**AF**: Agent handles it — `agent.create_session()`.

---

### 4. Workflow Engine — Multi-Agent Orchestration

The real power — composing multiple agents into patterns:

#### Sequential (Pipeline)
```python
from agent_framework.orchestrations import SequentialBuilder

workflow = SequentialBuilder(participants=[writer, reviewer]).build()

async for event in workflow.run("Write a tagline for an eBike.", stream=True):
    if event.type == "output":
        for msg in event.data:
            print(f"[{msg.author_name}]: {msg.text}")
```

#### Concurrent (Parallel)
Multiple agents work on the same input simultaneously.

#### Handoff
Agent A delegates to Agent B when it hits its boundary.

#### Group Chat
Multiple agents discuss and collaborate on a problem.

---

### 5. Multi-Provider Support

| Provider | How to Connect |
|----------|---------------|
| **Azure OpenAI** | `AzureOpenAIResponsesClient(credential=...)` |
| **Azure AI Foundry** | `AzureAIAgentsClient(credential=...)` |
| **OpenAI** | `OpenAIResponsesClient(api_key=...)` |
| **GitHub Copilot** | Via Copilot SDK integration |
| **Anthropic Claude** | Via compatible client |
| **AWS Bedrock** | Via compatible client |
| **Ollama** | Via compatible client |

---

### 6. Interoperability Standards

| Standard | Purpose |
|----------|---------|
| **A2A** (Agent-to-Agent) | Communication between agents across systems |
| **AG-UI** | Agent-to-UI protocol for frontend integration |
| **MCP** (Model Context Protocol) | Connect agents to external tools & data |

---

## Response Types

### Non-Streaming
```python
response = await agent.run("Question")
print(response.text)               # Final text
print(response.messages)           # All messages (tool calls, reasoning, result)
```

### Streaming
```python
async for update in agent.run_streaming("Question"):
    print(update.text, end="")     # Incremental text updates
```

---

## Quick Comparison Table

| Feature | Semantic Kernel | AutoGen | Agent Framework |
|---------|----------------|---------|-----------------|
| Agent creation | Complex (Kernel required) | Complex (config-heavy) | Simple (`.as_agent()`) |
| Tool registration | Attributes + Plugins + Kernel | Decorators + registration | Direct function reference |
| Thread management | Manual typed threads | Automatic | Agent-managed sessions |
| Multi-agent | Limited | GroupChat focused | Full workflow engine |
| Streaming | Varies by provider | Limited | Built-in everywhere |
| Providers | Azure-centric | OpenAI-centric | Multi-provider |
| Languages | .NET, Python, Java | Python | .NET, Python |
| Type consolidation | Many agent types | Many agent types | One `AIAgent` type |

---

## Key Design Principles

1. **Simplicity** — Fewer lines of code to get started
2. **Consistency** — Same patterns across .NET and Python
3. **Composability** — Agents compose into workflows naturally
4. **Provider-agnostic** — Switch providers without rewriting agents
5. **Standards-based** — A2A, AG-UI, MCP from day one
