# 01 - Basic Agent

## What This Covers

- Creating an `AIAgent` with instructions
- Using `AgentSession` for conversation context
- Invoking the agent with `invoke()` and `invoke_stream()`
- Switching between providers (OpenAI, Azure Foundry, GitHub Models)

## Key Concepts

### AIAgent
The core building block. Takes a name, instructions (system prompt), and a client (provider).

```python
agent = AIAgent(
    name="Assistant",
    instructions="You are a helpful assistant.",
    client=OpenAIChatClient(model="gpt-4o"),
)
```

### AgentSession
Maintains conversation history and state. Pass the same session across multiple `invoke()` calls for multi-turn conversations.

```python
session = AgentSession()
r1 = await agent.invoke(session, "Hello")      # Turn 1
r2 = await agent.invoke(session, "Tell me more") # Turn 2 (remembers Turn 1)
```

### Streaming
Use `invoke_stream()` for token-by-token output:

```python
async for chunk in agent.invoke_stream(session, "Explain X"):
    print(chunk, end="", flush=True)
```

## Running

```bash
# Install
pip install agent-framework --pre

# Set your API key
$env:OPENAI_API_KEY = "sk-..."

# Run
python basic_agent.py
```

## .NET Equivalent

```csharp
using Microsoft.Agents.AI;
using Microsoft.Agents.AI.OpenAI;

var agent = new AIAgent()
{
    Name = "Assistant",
    Instructions = "You are a helpful assistant.",
    Client = new OpenAIChatClient("gpt-4o")
};

var session = new AgentSession();
var response = await agent.InvokeAsync(session, "What is Agent Framework?");
Console.WriteLine($"Agent: {response}");
```

## Provider Comparison

| Provider | Client Class | Model Examples |
|----------|-------------|----------------|
| OpenAI | `OpenAIChatClient` | gpt-4o, gpt-4o-mini |
| Azure Foundry | `AzureAIChatClient` | gpt-4o, Phi-4, Llama |
| Anthropic | `AnthropicChatClient` | claude-sonnet-4 |
| AWS Bedrock | `BedrockChatClient` | Various |
| Ollama | `OllamaChatClient` | llama3, phi3 |
| GitHub | `OpenAIChatClient` | gpt-4o (via GitHub endpoint) |
