# Migration Comparison: Semantic Kernel → AutoGen → Agent Framework

> **📌 Follow**: [../../AGENT_DEVELOPMENT_GUIDE.md](../../AGENT_DEVELOPMENT_GUIDE.md)

---

## At a Glance

```
SEMANTIC KERNEL (2023-2025)           AUTOGEN (2023-2025)
├── .NET, Python, Java                ├── Python only
├── Kernel-centric design             ├── Config-driven agents
├── Plugin system for tools           ├── GroupChat focused
├── ChatCompletionAgent               ├── ConversableAgent
├── OpenAIAssistantAgent              ├── AssistantAgent
├── AzureAIAgent                      └── UserProxyAgent
│
└──────────────── MERGED INTO ────────────────┐
                                              ▼
                          AGENT FRAMEWORK (2026)
                          ├── .NET and Python
                          ├── One AIAgent type
                          ├── Direct function tools
                          ├── Workflow engine (seq, concurrent, handoff, group)
                          ├── Agent-managed sessions
                          └── Multi-provider support
```

---

## 1. Agent Creation

### Semantic Kernel
```python
# SK: Required Kernel → Builder → Agent
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent

kernel = Kernel()
kernel.add_service(AzureChatCompletion(...))

agent = ChatCompletionAgent(
    kernel=kernel,
    instructions="You are helpful.",
    name="MyAgent"
)
```

### AutoGen
```python
# AutoGen: Config-driven
from autogen import ConversableAgent

agent = ConversableAgent(
    name="MyAgent",
    system_message="You are helpful.",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": "..."}]}
)
```

### Agent Framework ✅
```python
# AF: Simplest approach
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential

agent = AzureOpenAIResponsesClient(
    credential=AzureCliCredential(),
).as_agent(
    name="MyAgent",
    instructions="You are helpful.",
)
```

**Winner**: Agent Framework — fewest lines, no boilerplate, no intermediate objects.

---

## 2. Tool Registration

### Semantic Kernel
```python
# SK: Decorator → Plugin → Kernel → Agent (4 steps)
from semantic_kernel.functions import kernel_function

class WeatherPlugin:
    @kernel_function(description="Get weather")
    def get_weather(self, city: str) -> str:
        return f"Sunny in {city}"

kernel.add_plugin(WeatherPlugin())
agent = ChatCompletionAgent(kernel=kernel, ...)
```

### AutoGen
```python
# AutoGen: Register function
@agent.register_for_llm(description="Get weather")
def get_weather(city: str) -> str:
    return f"Sunny in {city}"
```

### Agent Framework ✅
```python
# AF: Direct function reference (1 step)
def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"Sunny in {city}"

agent = client.as_agent(
    tools=[get_weather],  # That's it
    ...
)
```

**Winner**: Agent Framework — no decorators, no plugins, no registration.

---

## 3. Conversation Management

### Semantic Kernel
```python
# SK: Manual typed thread creation
from semantic_kernel.agents import OpenAIAssistantAgentThread

thread = OpenAIAssistantAgentThread(assistant_client)  # Must know the type
async for response in agent.invoke(thread=thread, ...):
    print(response.message)
```

### AutoGen
```python
# AutoGen: Implicit chat management
result = agent.initiate_chat(other_agent, message="Hello")
```

### Agent Framework ✅
```python
# AF: Agent-managed sessions
session = await agent.create_session()
response = await agent.run("Hello", session=session)
response = await agent.run("Follow up", session=session)
```

**Winner**: Agent Framework — one universal pattern regardless of provider.

---

## 4. Multi-Agent Orchestration

### Semantic Kernel
```python
# SK: Limited built-in multi-agent (AgentGroupChat)
from semantic_kernel.agents import AgentGroupChat

chat = AgentGroupChat(agents=[agent1, agent2])
async for message in chat.invoke():
    print(message)
```

### AutoGen
```python
# AutoGen: GroupChat focus
from autogen import GroupChat, GroupChatManager

groupchat = GroupChat(agents=[agent1, agent2], messages=[])
manager = GroupChatManager(groupchat=groupchat)
agent1.initiate_chat(manager, message="Start")
```

### Agent Framework ✅
```python
# AF: Full workflow engine with multiple patterns
from agent_framework.orchestrations import SequentialBuilder

# Sequential
workflow = SequentialBuilder(participants=[writer, reviewer]).build()

# All patterns available:
# SequentialBuilder  — pipeline
# ConcurrentBuilder  — parallel execution
# HandoffBuilder     — delegation
# GroupChatBuilder   — discussion
```

**Winner**: Agent Framework — purpose-built workflow engine with streaming.

---

## 5. Streaming

### Semantic Kernel
```python
# SK: Different API per agent type
async for chunk in agent.invoke_streaming(thread=thread, ...):
    print(chunk.content)
```

### AutoGen
```python
# AutoGen: Limited streaming support
# No built-in streaming for multi-agent scenarios
```

### Agent Framework ✅
```python
# AF: Unified streaming everywhere
async for update in agent.run_streaming("Hello"):
    print(update.text, end="")

# Even workflows stream
async for event in workflow.run("Task", stream=True):
    print(event)
```

**Winner**: Agent Framework — streaming works consistently across single and multi-agent.

---

## 6. Provider Support

| Provider | Semantic Kernel | AutoGen | Agent Framework |
|----------|:---:|:---:|:---:|
| Azure OpenAI | ✅ | ✅ | ✅ |
| Azure AI Foundry | ✅ | ❌ | ✅ |
| OpenAI | ✅ | ✅ | ✅ |
| GitHub Copilot | ❌ | ❌ | ✅ |
| Anthropic Claude | ❌ | ❌ | ✅ |
| AWS Bedrock | ❌ | ❌ | ✅ |
| Ollama | ✅ | ✅ | ✅ |

---

## 7. Namespace Changes (.NET)

| Semantic Kernel | Agent Framework |
|----------------|-----------------|
| `Microsoft.SemanticKernel` | `Microsoft.Agents.AI` |
| `Microsoft.SemanticKernel.Agents` | `Microsoft.Agents.AI` |
| `ChatMessageContent` | `ChatMessage` (from `Microsoft.Extensions.AI`) |
| `KernelFunction` | `AIFunction` (from `Microsoft.Extensions.AI`) |
| `Kernel` | Not needed |

---

## 8. Key Terminology Changes

| Old Concept | New Concept |
|-------------|-------------|
| Kernel | Not needed (agents stand alone) |
| Plugin | Tools (direct functions) |
| KernelFunction | AIFunction |
| AgentThread | AgentSession |
| InvokeAsync | RunAsync |
| InvokeStreamingAsync | RunStreamingAsync |
| AgentGroupChat | Workflow (Sequential/Concurrent/Handoff/GroupChat) |

---

## Migration Decision Tree

```
Are you using Semantic Kernel agents?
├── Yes → Follow SK migration guide
│         Key changes: Remove Kernel, use .as_agent(), direct tools
│
Are you using AutoGen?
├── Yes → Follow AutoGen migration guide
│         Key changes: Replace ConversableAgent, use workflow engine
│
Starting fresh?
├── Yes → Start with Agent Framework directly
│         Go to examples/01-hello-agent/
```

---

## Sources

- [SK to Agent Framework Migration Guide](https://learn.microsoft.com/en-us/semantic-kernel/agent-framework/migration-guide)
- [AutoGen to Agent Framework Migration Guide](https://learn.microsoft.com/en-us/semantic-kernel/agent-framework/autogen-migration)
- [Agent Framework Release Candidate Announcement](https://devblogs.microsoft.com/semantic-kernel/microsoft-agent-framework-reaches-release-candidate/)
