"""
Multi-Agent Workflow Example - Microsoft Agent Framework
=========================================================
Demonstrates orchestrating multiple agents in different patterns:
- Sequential: Agent A → Agent B → Agent C (pipeline)
- Concurrent: Agents run in parallel, results combined
- Handoff: Agent delegates to specialist based on context
- Group Chat: Agents collaborate in a shared conversation

Prerequisites:
    pip install agent-framework --pre
    pip install agent-framework-orchestrations --pre
"""

import asyncio
from agent_framework import AIAgent, AgentSession, function_tool
from agent_framework.openai import OpenAIChatClient

# Try importing orchestrations (may need separate install)
try:
    from agent_framework.orchestrations import (
        SequentialWorkflow,
        ConcurrentWorkflow,
        HandoffWorkflow,
        GroupChat,
    )
    HAS_ORCHESTRATIONS = True
except ImportError:
    HAS_ORCHESTRATIONS = False
    print("⚠️  Install orchestrations: pip install agent-framework-orchestrations --pre")


# ── Define Specialist Agents ─────────────────────────────────────

def create_writer():
    """Content writer agent."""
    return AIAgent(
        name="Writer",
        instructions="""You are a technical writer. 
        Write clear, concise content based on the given topic.
        Output only the written content, no meta-commentary.""",
        client=OpenAIChatClient(model="gpt-4o"),
    )

def create_reviewer():
    """Content reviewer/editor agent."""
    return AIAgent(
        name="Reviewer",
        instructions="""You are a strict technical editor.
        Review the given content for:
        - Clarity and conciseness
        - Technical accuracy
        - Grammar and style
        Provide specific feedback and a revised version.""",
        client=OpenAIChatClient(model="gpt-4o"),
    )

def create_publisher():
    """Content publisher/formatter agent."""
    return AIAgent(
        name="Publisher",
        instructions="""You are a content publisher.
        Take the reviewed content and format it for publication:
        - Add appropriate headers
        - Format as clean Markdown
        - Add a TL;DR summary at the top
        Output the final publishable version.""",
        client=OpenAIChatClient(model="gpt-4o"),
    )

def create_researcher():
    """Research agent with search tools."""
    @function_tool
    def search_web(query: str) -> str:
        """Search the web for information.
        
        Args:
            query: Search query string.
        """
        # Simulated search results
        return f"[Simulated results for '{query}']: The Microsoft Agent Framework unifies Semantic Kernel and AutoGen into a single platform for building AI agents."
    
    return AIAgent(
        name="Researcher",
        instructions="""You are a research assistant.
        Use search tools to find relevant information.
        Summarize findings clearly with sources.""",
        client=OpenAIChatClient(model="gpt-4o"),
        tools=[search_web],
    )

def create_analyst():
    """Data analyst agent."""
    @function_tool
    def analyze_data(dataset: str) -> str:
        """Analyze a dataset and return insights.
        
        Args:
            dataset: Name or description of the dataset to analyze.
        """
        return f"[Analysis of '{dataset}']: Key trends show 40% adoption increase, 3 main clusters identified."
    
    return AIAgent(
        name="Analyst",
        instructions="""You are a data analyst.
        Analyze data and provide clear, actionable insights.
        Use charts descriptions and specific numbers.""",
        client=OpenAIChatClient(model="gpt-4o"),
        tools=[analyze_data],
    )


# ══════════════════════════════════════════════════════════════════
# Pattern 1: SEQUENTIAL WORKFLOW (Pipeline)
# Agent A → Agent B → Agent C
# ══════════════════════════════════════════════════════════════════

async def sequential_example():
    """Writer → Reviewer → Publisher pipeline."""
    print("\n" + "=" * 60)
    print("🔗 SEQUENTIAL WORKFLOW: Writer → Reviewer → Publisher")
    print("=" * 60)

    if HAS_ORCHESTRATIONS:
        workflow = SequentialWorkflow(
            agents=[create_writer(), create_reviewer(), create_publisher()]
        )
        session = AgentSession()
        result = await workflow.invoke(
            session, 
            "Write a short article about the Microsoft Agent Framework"
        )
        print(f"\nFinal Output:\n{result}")
    else:
        # Manual sequential without orchestrations package
        writer = create_writer()
        reviewer = create_reviewer()
        publisher = create_publisher()

        session = AgentSession()

        print("\n📝 Step 1: Writer drafts content...")
        draft = await writer.invoke(
            session, 
            "Write a short article about the Microsoft Agent Framework"
        )
        print(f"Draft: {str(draft)[:200]}...")

        print("\n🔍 Step 2: Reviewer edits...")
        reviewed = await reviewer.invoke(
            AgentSession(),  # Fresh session for reviewer
            f"Review and improve this content:\n\n{draft}"
        )
        print(f"Reviewed: {str(reviewed)[:200]}...")

        print("\n📢 Step 3: Publisher formats...")
        final = await publisher.invoke(
            AgentSession(),  # Fresh session for publisher
            f"Format this for publication:\n\n{reviewed}"
        )
        print(f"\nFinal Output:\n{final}")


# ══════════════════════════════════════════════════════════════════
# Pattern 2: CONCURRENT WORKFLOW (Fan-out / Fan-in)
# Multiple agents work in parallel, results merged
# ══════════════════════════════════════════════════════════════════

async def concurrent_example():
    """Researcher + Analyst work in parallel, results combined."""
    print("\n" + "=" * 60)
    print("⚡ CONCURRENT WORKFLOW: Researcher ‖ Analyst → Combine")
    print("=" * 60)

    if HAS_ORCHESTRATIONS:
        workflow = ConcurrentWorkflow(
            agents=[create_researcher(), create_analyst()]
        )
        session = AgentSession()
        result = await workflow.invoke(
            session, 
            "Analyze the adoption of AI agent frameworks in enterprise"
        )
        print(f"\nCombined Output:\n{result}")
    else:
        # Manual concurrent using asyncio.gather
        researcher = create_researcher()
        analyst = create_analyst()

        topic = "Analyze the adoption of AI agent frameworks in enterprise"

        print(f"\n🔬 Running Researcher and Analyst in parallel...")
        research_result, analysis_result = await asyncio.gather(
            researcher.invoke(AgentSession(), topic),
            analyst.invoke(AgentSession(), topic),
        )

        print(f"\n📚 Research findings:\n{research_result}")
        print(f"\n📊 Analysis findings:\n{analysis_result}")

        # Optionally, use a combiner agent
        combiner = AIAgent(
            name="Combiner",
            instructions="Synthesize research and analysis into a unified executive summary.",
            client=OpenAIChatClient(model="gpt-4o"),
        )
        combined = await combiner.invoke(
            AgentSession(),
            f"Research:\n{research_result}\n\nAnalysis:\n{analysis_result}\n\nCreate an executive summary."
        )
        print(f"\n📋 Executive Summary:\n{combined}")


# ══════════════════════════════════════════════════════════════════
# Pattern 3: HANDOFF (Delegation)
# Router agent delegates to specialist
# ══════════════════════════════════════════════════════════════════

async def handoff_example():
    """Router agent delegates to the right specialist."""
    print("\n" + "=" * 60)
    print("🔀 HANDOFF WORKFLOW: Router → Specialist")
    print("=" * 60)

    if HAS_ORCHESTRATIONS:
        workflow = HandoffWorkflow(
            agents=[create_writer(), create_researcher(), create_analyst()],
            # The framework automatically routes based on the query
        )
        session = AgentSession()
        result = await workflow.invoke(
            session,
            "I need data analysis on Q4 sales trends"
        )
        print(f"\nResult:\n{result}")
    else:
        # Manual handoff using a router agent
        @function_tool
        def delegate_to_writer(task: str) -> str:
            """Delegate a writing task to the Writer agent.
            
            Args:
                task: The writing task description.
            """
            return f"[DELEGATE:Writer] {task}"

        @function_tool
        def delegate_to_researcher(task: str) -> str:
            """Delegate a research task to the Researcher agent.
            
            Args:
                task: The research task description.
            """
            return f"[DELEGATE:Researcher] {task}"

        @function_tool
        def delegate_to_analyst(task: str) -> str:
            """Delegate an analysis task to the Analyst agent.
            
            Args:
                task: The analysis task description.
            """
            return f"[DELEGATE:Analyst] {task}"

        router = AIAgent(
            name="Router",
            instructions="""You are a task router. Analyze the user's request and delegate to the appropriate specialist:
            - Writer: for content creation tasks
            - Researcher: for information gathering tasks  
            - Analyst: for data analysis tasks
            Always delegate, never answer directly.""",
            client=OpenAIChatClient(model="gpt-4o"),
            tools=[delegate_to_writer, delegate_to_researcher, delegate_to_analyst],
        )

        specialists = {
            "Writer": create_writer(),
            "Researcher": create_researcher(),
            "Analyst": create_analyst(),
        }

        query = "I need data analysis on Q4 sales trends"
        print(f"\nUser: {query}")
        
        routing = await router.invoke(AgentSession(), query)
        print(f"Router decision: {routing}")

        # In a real implementation, parse the routing and invoke the specialist


# ══════════════════════════════════════════════════════════════════
# Pattern 4: GROUP CHAT
# Multiple agents collaborate in shared conversation
# ══════════════════════════════════════════════════════════════════

async def group_chat_example():
    """Multiple agents discuss a topic together."""
    print("\n" + "=" * 60)
    print("💬 GROUP CHAT: Writer + Reviewer + Researcher collaborate")
    print("=" * 60)

    if HAS_ORCHESTRATIONS:
        chat = GroupChat(
            agents=[create_writer(), create_reviewer(), create_researcher()],
            max_rounds=4,
        )
        session = AgentSession()
        result = await chat.invoke(
            session,
            "Let's create a blog post about AI agent frameworks"
        )
        print(f"\nChat Result:\n{result}")
    else:
        print("\n⚠️  Group Chat requires: pip install agent-framework-orchestrations --pre")
        print("This pattern uses graph-based orchestration to manage turn-taking")
        print("between multiple agents in a shared conversation context.")


# ── Main ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Microsoft Agent Framework - Multi-Agent Workflows")
    print("=" * 60)

    # Uncomment the pattern you want to run:
    asyncio.run(sequential_example())
    # asyncio.run(concurrent_example())
    # asyncio.run(handoff_example())
    # asyncio.run(group_chat_example())
