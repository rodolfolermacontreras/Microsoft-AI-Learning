"""
Basic Copilot SDK Test - Simple question and answer
"""
import asyncio
import os
from copilot import CopilotClient

# Full path to Copilot CLI (set COPILOT_CLI_PATH env var or update this default)
COPILOT_CLI_PATH = os.getenv("COPILOT_CLI_PATH", "copilot.exe")

async def main():
    print("🚀 Starting Copilot SDK test...\n")
    
    # Create and start client with explicit CLI path
    client = CopilotClient({"cli_path": COPILOT_CLI_PATH})
    await client.start()
    print("✅ Client started successfully!")
    
    # Create a session
    session = await client.create_session({"model": "gpt-4.1"})
    print(f"✅ Session created: {session.session_id}\n")
    
    # Send a simple question
    print("📤 Sending question: 'What is 2 + 2?'")
    response = await session.send_and_wait({"prompt": "What is 2 + 2?"})
    
    if response:
        print(f"\n📥 Response:\n{response.data.content}")
    
    # Clean up
    await session.destroy()
    await client.stop()
    print("\n✅ Test completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
