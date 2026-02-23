"""
Copilot SDK - Streaming Example
Watch the response appear word by word!
"""
import asyncio
import os
import sys
from copilot import CopilotClient
from copilot.generated.session_events import SessionEventType

# Full path to Copilot CLI (set COPILOT_CLI_PATH env var or update this default)
COPILOT_CLI_PATH = os.getenv("COPILOT_CLI_PATH", "copilot.exe")

async def main():
    print("🚀 Copilot SDK Streaming Demo\n")
    print("=" * 50)
    
    client = CopilotClient({"cli_path": COPILOT_CLI_PATH})
    await client.start()
    
    session = await client.create_session({
        "model": "gpt-4.1",
        "streaming": True,  # Enable streaming
    })
    
    # Track events for display
    def handle_event(event):
        if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            # Print each chunk as it arrives
            sys.stdout.write(event.data.delta_content)
            sys.stdout.flush()
        elif event.type == SessionEventType.SESSION_IDLE:
            print("\n" + "=" * 50)
    
    session.on(handle_event)
    
    print("\n📤 Asking: 'Explain what the Copilot SDK is in 3 sentences'\n")
    print("📥 Response (streaming):\n")
    
    await session.send_and_wait({
        "prompt": "Explain what the GitHub Copilot SDK is in 3 sentences. Be concise."
    })
    
    await session.destroy()
    await client.stop()
    print("\n✅ Done!")

if __name__ == "__main__":
    asyncio.run(main())
