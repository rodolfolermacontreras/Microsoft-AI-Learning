"""
Basic Agent Example - Microsoft Agent Framework
=================================================
Creates a simple conversational agent using Azure Foundry / OpenAI.

Prerequisites:
    pip install agent-framework --pre

Environment Variables:
    AZURE_AI_AGENT_PROJECT_CONNECTION_STRING  (for Azure Foundry)
    -- or --
    OPENAI_API_KEY  (for OpenAI)
    -- or --
    GITHUB_TOKEN  (for GitHub Models)
"""

import asyncio
from agent_framework import AIAgent, AgentSession
from agent_framework.openai import OpenAIChatClient

# ── Option 1: OpenAI ──────────────────────────────────────────────
async def basic_openai_agent():
    """Simple agent using OpenAI as the provider."""
    agent = AIAgent(
        name="Assistant",
        instructions="You are a helpful assistant. Be concise and clear.",
        client=OpenAIChatClient(model="gpt-4o"),
    )

    session = AgentSession()
    response = await agent.invoke(session, "What is the Microsoft Agent Framework?")
    print(f"Agent: {response}")

# ── Option 2: Azure Foundry ───────────────────────────────────────
async def basic_foundry_agent():
    """Simple agent using Azure AI Foundry as the provider."""
    from agent_framework.azure import AzureAIChatClient

    agent = AIAgent(
        name="FoundryAssistant",
        instructions="You are a helpful assistant powered by Azure AI Foundry.",
        client=AzureAIChatClient(model="gpt-4o"),
    )

    session = AgentSession()
    response = await agent.invoke(session, "Explain the Agent Framework in one paragraph.")
    print(f"Agent: {response}")

# ── Option 3: GitHub Models ───────────────────────────────────────
async def basic_github_agent():
    """Simple agent using GitHub-hosted models."""
    agent = AIAgent(
        name="GitHubAssistant",
        instructions="You are a helpful assistant using GitHub Models.",
        client=OpenAIChatClient(
            model="gpt-4o",
            # GitHub Models uses the OpenAI-compatible endpoint
            # Set GITHUB_TOKEN env var
        ),
    )

    session = AgentSession()
    response = await agent.invoke(session, "What providers does Agent Framework support?")
    print(f"Agent: {response}")

# ── Streaming Response ────────────────────────────────────────────
async def streaming_agent():
    """Agent with streaming output - token by token."""
    agent = AIAgent(
        name="StreamAssistant",
        instructions="You are a helpful assistant. Explain things step by step.",
        client=OpenAIChatClient(model="gpt-4o"),
    )

    session = AgentSession()
    print("Agent: ", end="")
    async for chunk in agent.invoke_stream(session, "List 3 benefits of the Agent Framework."):
        print(chunk, end="", flush=True)
    print()  # newline

# ── Main ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("Microsoft Agent Framework - Basic Agent Example")
    print("=" * 60)

    # Uncomment the example you want to run:
    asyncio.run(basic_openai_agent())
    # asyncio.run(basic_foundry_agent())
    # asyncio.run(basic_github_agent())
    # asyncio.run(streaming_agent())
