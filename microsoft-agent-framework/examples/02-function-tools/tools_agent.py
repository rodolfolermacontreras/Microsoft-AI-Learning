"""
Function Tools Example - Microsoft Agent Framework
====================================================
Demonstrates registering Python functions as tools that the agent can call.

The Agent Framework uses `@function_tool` decorator to expose Python
functions to the LLM. The framework handles:
- Schema generation from type hints
- Argument parsing and validation
- Tool call routing and response handling

Prerequisites:
    pip install agent-framework --pre
"""

import asyncio
from datetime import datetime
from agent_framework import AIAgent, AgentSession, function_tool
from agent_framework.openai import OpenAIChatClient


# ── Define Tools ──────────────────────────────────────────────────

@function_tool
def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@function_tool
def calculate(expression: str) -> str:
    """
    Evaluate a mathematical expression.
    
    Args:
        expression: A mathematical expression to evaluate (e.g., '2 + 3 * 4')
    """
    try:
        # Safety: only allow math operations
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Only basic math operations are allowed."
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error evaluating expression: {e}"


@function_tool
def lookup_employee(name: str) -> str:
    """
    Look up employee information by name.
    
    Args:
        name: The employee's name to look up.
    """
    # Simulated employee database
    employees = {
        "alice": {"title": "Senior Engineer", "department": "Platform", "location": "Redmond"},
        "bob": {"title": "PM Lead", "department": "AI Tools", "location": "Remote"},
        "carol": {"title": "Data Scientist", "department": "Analytics", "location": "NYC"},
    }
    
    info = employees.get(name.lower())
    if info:
        return f"{name.title()}: {info['title']} in {info['department']} ({info['location']})"
    return f"No employee found with name '{name}'"


@function_tool
def search_documents(query: str, max_results: int = 3) -> str:
    """
    Search internal documents for relevant information.
    
    Args:
        query: The search query.
        max_results: Maximum number of results to return (default: 3).
    """
    # Simulated document search
    docs = [
        {"title": "Agent Framework Overview", "snippet": "The Microsoft Agent Framework unifies SK and AutoGen..."},
        {"title": "Migration Guide", "snippet": "To migrate from Semantic Kernel, replace KernelFunction with function_tool..."},
        {"title": "Multi-Agent Patterns", "snippet": "Sequential workflows chain agents: writer → reviewer → publisher..."},
        {"title": "Tool Registration", "snippet": "Use @function_tool decorator to register Python functions..."},
        {"title": "Provider Support", "snippet": "Supports OpenAI, Azure Foundry, Anthropic, Bedrock, Ollama..."},
    ]
    
    # Simple keyword matching
    results = [d for d in docs if query.lower() in d["title"].lower() or query.lower() in d["snippet"].lower()]
    results = results[:max_results]
    
    if not results:
        return f"No documents found for query: '{query}'"
    
    return "\n".join(f"📄 {d['title']}: {d['snippet']}" for d in results)


# ── Create Agent with Tools ──────────────────────────────────────

async def agent_with_tools():
    """Agent that can use multiple tools to answer questions."""
    
    agent = AIAgent(
        name="ToolsAssistant",
        instructions="""You are a helpful workplace assistant with access to tools.
        Use the available tools to answer questions accurately.
        Always use tools when the question requires real-time data or lookups.
        Be concise in your responses.""",
        client=OpenAIChatClient(model="gpt-4o"),
        tools=[get_current_time, calculate, lookup_employee, search_documents],
    )

    session = AgentSession()

    # Multi-turn conversation with tool usage
    queries = [
        "What time is it right now?",
        "What's 15% of 2450?",
        "Look up Alice's information",
        "Search for documents about migration",
    ]

    for query in queries:
        print(f"\nUser: {query}")
        response = await agent.invoke(session, query)
        print(f"Agent: {response}")


# ── Streaming with Tools ─────────────────────────────────────────

async def streaming_with_tools():
    """Demonstrates streaming responses when tools are involved."""
    
    agent = AIAgent(
        name="StreamTools",
        instructions="You are helpful. Use tools when needed. Explain your findings.",
        client=OpenAIChatClient(model="gpt-4o"),
        tools=[get_current_time, calculate, lookup_employee],
    )

    session = AgentSession()
    
    print("\nUser: What time is it and what's 42 * 37?")
    print("Agent: ", end="")
    async for chunk in agent.invoke_stream(session, "What time is it and what's 42 * 37?"):
        print(chunk, end="", flush=True)
    print()


# ── Main ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Microsoft Agent Framework - Function Tools Example")
    print("=" * 60)

    asyncio.run(agent_with_tools())
    # asyncio.run(streaming_with_tools())
