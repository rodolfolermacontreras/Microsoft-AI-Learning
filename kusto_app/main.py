"""
🔍 Kusto Query Assistant - Main Application

An AI-powered agent that helps you explore and query your Kusto database.
The agent can:
- Explore tables and schemas
- Execute read-only queries  
- Explain results
- Help write KQL queries from natural language

SAFETY: Only read operations are allowed. All modification commands are blocked.
"""

import asyncio
import sys
import os
from copilot import CopilotClient
from copilot.generated.session_events import SessionEventType

# Add the kusto_app directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from kusto_connection import KustoConnection, KustoConfig
from kusto_tools import ALL_KUSTO_TOOLS, set_kusto_connection


# =============================================================================
# CONFIGURATION - Load from environment variables
# =============================================================================

# Copilot CLI path (set COPILOT_CLI_PATH env var or update this default)
COPILOT_CLI_PATH = os.getenv("COPILOT_CLI_PATH", "copilot.exe")

# Kusto Configuration - set these in your .env file
KUSTO_CLUSTER = os.getenv("KUSTO_CLUSTER", "https://your-cluster.kusto.windows.net")
KUSTO_DATABASE = os.getenv("KUSTO_DATABASE", "YourDatabase")


# =============================================================================
# SYSTEM PROMPT - Kusto Query Expert
# =============================================================================
SYSTEM_PROMPT = """You are an expert Kusto Query Language (KQL) assistant.

You help users explore and query Azure Data Explorer (Kusto) databases using
natural language. You translate questions into KQL, explain results, and
suggest optimizations.

## YOUR CAPABILITIES
You have tools to interact with the Kusto database (READ-ONLY access):

1. **list_tables** - See all tables in the database
2. **get_table_schema** - Get columns and types for a table
3. **get_sample_data** - View sample rows from a table
4. **get_row_count** - Get approximate row count
5. **execute_query** - Run a KQL query (read-only only!)
6. **validate_query** - Check if a query is safe before running

## WORKFLOW
When the user asks a question:

1. **Explore first** - If you don't know the schema, use list_tables and get_table_schema
2. **Understand the data** - Use get_sample_data to see actual values and column meanings
3. **Connect to domain** - Relate columns to the business domain
4. **Write the query** - Explain your approach, then write the KQL
5. **Execute** - Run the query and explain the results in context
6. **Iterate** - Refine based on what you learn

## KQL BEST PRACTICES
- Always filter by time FIRST (most efficient)
- Use 'has' instead of 'contains' when possible
- Project only needed columns
- Add 'take' during exploration
- Comment your queries

## SAFETY RULES
- You have READ-ONLY access
- Never attempt DROP, DELETE, CREATE, ALTER, or any modification
- If a user asks to modify data, explain you can only read
- Be careful with PII data

## RESPONSE STYLE
- Be concise but thorough
- Show your reasoning about what the data means
- Suggest follow-up analyses
- If column names are unclear, explore and explain what you discover
"""


# =============================================================================
# MAIN APPLICATION
# =============================================================================

async def run_assistant():
    """Main function to run the Kusto Assistant."""
    
    print("=" * 70)
    print("🔍 WWIC KUSTO QUERY ASSISTANT")
    print("=" * 70)
    print(f"\n📡 Connecting to Kusto...")
    print(f"   Cluster: {KUSTO_CLUSTER}")
    print(f"   Database: {KUSTO_DATABASE}")
    
    # Initialize Kusto connection
    config = KustoConfig(
        cluster_url=KUSTO_CLUSTER,
        database=KUSTO_DATABASE,
    )
    
    kusto_conn = KustoConnection(config)
    
    if not kusto_conn.connect():
        print("\n❌ Failed to connect to Kusto. Please check your configuration.")
        print(f"   Cluster: {KUSTO_CLUSTER}")
        print(f"   Database: {KUSTO_DATABASE}")
        return
    
    # Set connection for tools
    set_kusto_connection(kusto_conn)
    
    print("\n🤖 Starting AI Assistant...")
    
    # Initialize Copilot client
    client = CopilotClient({"cli_path": COPILOT_CLI_PATH})
    await client.start()
    
    # Create session with our tools
    session = await client.create_session({
        "model": "gpt-4.1",
        "streaming": True,
        "tools": ALL_KUSTO_TOOLS,
        "system_message": {
            "mode": "replace",
            "content": SYSTEM_PROMPT,
        },
    })
    
    # Track tool calls for visibility
    def handle_event(event):
        if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            sys.stdout.write(event.data.delta_content)
            sys.stdout.flush()
        elif event.type == SessionEventType.TOOL_EXECUTION_START:
            tool_name = getattr(event.data, 'tool_name', 'unknown')
            print(f"\n   🔧 Running: {tool_name}...", end="", flush=True)
        elif event.type == SessionEventType.TOOL_EXECUTION_COMPLETE:
            print(" ✓")
        elif event.type == SessionEventType.SESSION_IDLE:
            print("\n")
    
    session.on(handle_event)
    
    # Welcome message
    print("\n" + "=" * 70)
    print("✅ Ready! I'm connected to your Kusto database.")
    print("\nI can help you:")
    print("  • Explore tables and understand the schema")
    print("  • Write KQL queries from natural language")
    print("  • Execute queries and explain results")
    print("  • Optimize your queries")
    print("\nCommands:")
    print("  'tables'  - Quick list of all tables")
    print("  'schema'  - Show current database info")
    print("  'exit'    - Quit the assistant")
    print("=" * 70)
    
    # Interactive loop
    while True:
        try:
            print("-" * 70)
            user_input = input("📝 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'exit':
                print("\n👋 Goodbye! Happy querying!")
                break
            
            if user_input.lower() == 'tables':
                # Quick table list
                df, status = kusto_conn.get_tables()
                print(f"\n{status}")
                if df is not None:
                    for _, row in df.iterrows():
                        print(f"  • {row.get('TableName', row.iloc[0])}")
                continue
            
            if user_input.lower() == 'schema':
                print(f"\n📊 Database: {KUSTO_DATABASE}")
                print(f"🌐 Cluster: {KUSTO_CLUSTER}")
                continue
            
            print("\n🤖 Assistant:\n")
            try:
                await session.send_and_wait({"prompt": user_input}, timeout=300)  # 5 minute timeout
            except asyncio.TimeoutError:
                print("\n⏱️ Request timed out. The query might be taking too long. Try a simpler question or use 'tables' command first.")
            except Exception as e:
                print(f"\n❌ Error: {e}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except EOFError:
            break
    
    # Cleanup
    await session.destroy()
    await client.stop()
    kusto_conn.close()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Check for required packages
    try:
        import pandas
        from azure.kusto.data import KustoClient
    except ImportError as e:
        print("❌ Missing required packages. Install with:")
        print("   pip install azure-kusto-data azure-identity pandas")
        sys.exit(1)
    
    asyncio.run(run_assistant())
