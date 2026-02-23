# 02 - Function Tools

## What This Covers

- Registering Python functions as tools with `@function_tool`
- Type hints → automatic JSON schema generation
- Multi-tool agents
- Tool calls during streaming

## Key Concepts

### @function_tool Decorator

The `@function_tool` decorator converts a regular Python function into a tool the agent can call. The framework:

1. **Reads the docstring** → becomes the tool description for the LLM
2. **Reads type hints** → generates the JSON schema for parameters
3. **Handles invocation** → parses LLM tool calls, runs the function, returns results

```python
@function_tool
def get_weather(city: str, units: str = "celsius") -> str:
    """
    Get current weather for a city.
    
    Args:
        city: The city name to get weather for.
        units: Temperature units - 'celsius' or 'fahrenheit'.
    """
    return f"Weather in {city}: 22°{units[0].upper()}, sunny"
```

### Registering Tools with an Agent

Pass tools as a list when creating the agent:

```python
agent = AIAgent(
    name="Assistant",
    instructions="Use tools when needed.",
    client=OpenAIChatClient(model="gpt-4o"),
    tools=[get_weather, calculate, search_docs],  # ← list of tools
)
```

### Migration from Semantic Kernel

| Semantic Kernel | Agent Framework |
|----------------|-----------------|
| `@kernel_function` | `@function_tool` |
| `kernel.add_plugin(plugin)` | `tools=[fn1, fn2]` on AIAgent |
| Plugin classes | Plain functions with decorator |
| `KernelArguments` | Standard Python args + type hints |

## .NET Equivalent

```csharp
using Microsoft.Agents.AI;

// Define tool via method attribute
[AgentFunction("get_weather", "Get weather for a city")]
public string GetWeather(string city, string units = "celsius")
{
    return $"Weather in {city}: 22°{units[0]}, sunny";
}

// Register with agent
var agent = new AIAgent()
{
    Name = "Assistant",
    Tools = { GetWeather },
    Client = new OpenAIChatClient("gpt-4o")
};
```

## Running

```bash
pip install agent-framework --pre
$env:OPENAI_API_KEY = "sk-..."
python tools_agent.py
```
