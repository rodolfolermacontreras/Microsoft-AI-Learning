# GitHub Copilot SDK - Complete Summary & Guide

> **Date Explored:** January 23, 2026  
> **Repository:** https://github.com/rodolfolermacontreras/copilot-sdk (forked from github/copilot-sdk)  
> **Status:** Technical Preview (released January 2026)

---

## 🎯 Executive Summary

### What Is It?
The **GitHub Copilot SDK** is a programmable interface that lets you embed Copilot's AI-powered agentic workflows directly into your applications. Instead of building your own AI orchestration, you get access to the **same production-tested agent runtime** that powers the Copilot CLI.

### Key Value Proposition
| Traditional Approach | With Copilot SDK |
|---------------------|------------------|
| Build your own LLM orchestration | Copilot handles planning & orchestration |
| Manage tool calling manually | SDK manages tool invocation automatically |
| Build file editing capabilities | Built-in file operations |
| Create custom agent runtime | Production-tested runtime included |

### Who Should Use It?
- **Developers building AI-powered tools** - CLI assistants, code generators, automation
- **Teams integrating AI into existing apps** - Add AI capabilities without building from scratch
- **Enterprises with custom workflows** - BYOK (Bring Your Own Key) support available

---

## 📦 Available SDKs (4 Languages)

| Language | Package | Installation |
|----------|---------|--------------|
| **Python** | `github-copilot-sdk` | `pip install github-copilot-sdk` |
| **Node.js/TypeScript** | `@github/copilot-sdk` | `npm install @github/copilot-sdk` |
| **Go** | `github.com/github/copilot-sdk/go` | `go get github.com/github/copilot-sdk/go` |
| **.NET** | `GitHub.Copilot.SDK` | `dotnet add package GitHub.Copilot.SDK` |

---

## 🏗️ Architecture

```
┌─────────────────────────┐
│   Your Application      │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│      SDK Client         │  ← Python/TypeScript/Go/.NET
│  (CopilotClient)        │
└──────────┬──────────────┘
           │ JSON-RPC
           ▼
┌─────────────────────────┐
│   Copilot CLI           │  ← Server Mode
│  (Agent Runtime)        │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│   LLM Models            │
│  (GPT-4.1, Claude, etc) │
└─────────────────────────┘
```

### How It Works
1. **SDK Client** manages the CLI process lifecycle automatically
2. Communication happens via **JSON-RPC** protocol
3. Supports both **stdio** (default) and **TCP** transports
4. Can connect to an **external CLI server** for debugging/resource sharing

---

## 🚀 Quick Start (Python)

### Prerequisites
1. **GitHub Copilot CLI** installed and authenticated
2. **Python 3.9+**
3. **Copilot subscription** (free tier has limited usage)

### Basic Example

```python
import asyncio
from copilot import CopilotClient

async def main():
    # Create and start client
    client = CopilotClient()
    await client.start()

    # Create a session
    session = await client.create_session({"model": "gpt-4.1"})
    
    # Send a message and wait for response
    response = await session.send_and_wait({"prompt": "What is 2 + 2?"})
    print(response.data.content)

    # Clean up
    await client.stop()

asyncio.run(main())
```

### With Streaming

```python
import asyncio
import sys
from copilot import CopilotClient
from copilot.generated.session_events import SessionEventType

async def main():
    client = CopilotClient()
    await client.start()

    session = await client.create_session({
        "model": "gpt-4.1",
        "streaming": True,  # Enable streaming
    })

    # Handle streaming events
    def handle_event(event):
        if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            sys.stdout.write(event.data.delta_content)
            sys.stdout.flush()
        if event.type == SessionEventType.SESSION_IDLE:
            print()  # New line when done

    session.on(handle_event)

    await session.send_and_wait({"prompt": "Tell me a short joke"})
    await client.stop()

asyncio.run(main())
```

---

## 🛠️ Core Features

### 1. Custom Tools
Define tools that Copilot can invoke during conversations:

```python
from pydantic import BaseModel, Field
from copilot import CopilotClient
from copilot.tools import define_tool

class GetWeatherParams(BaseModel):
    city: str = Field(description="The name of the city")

@define_tool(description="Get the current weather for a city")
async def get_weather(params: GetWeatherParams) -> dict:
    # Your implementation here
    return {"city": params.city, "temperature": "72°F", "condition": "sunny"}

# Use the tool in a session
session = await client.create_session({
    "model": "gpt-4.1",
    "tools": [get_weather],
})
```

### 2. MCP Server Integration
Connect to Model Context Protocol servers for pre-built tools:

```python
session = await client.create_session({
    "mcp_servers": {
        "github": {
            "type": "http",
            "url": "https://api.githubcopilot.com/mcp/",
        },
    },
})
```

### 3. Custom Agents
Define specialized AI personas:

```python
session = await client.create_session({
    "custom_agents": [{
        "name": "pr-reviewer",
        "display_name": "PR Reviewer",
        "description": "Reviews pull requests for best practices",
        "prompt": "You are an expert code reviewer. Focus on security, performance, and maintainability.",
    }],
})
```

### 4. Session Persistence
Save and resume conversations:

```python
# Create with custom ID
session = await client.create_session({
    "session_id": "user-123-conversation",
    "model": "gpt-4.1",
})

# Resume later
resumed = await client.resume_session("user-123-conversation")

# List all sessions
sessions = await client.list_sessions()

# Delete session
await client.delete_session("user-123-conversation")
```

### 5. Multiple Sessions
Run parallel conversations:

```python
session1 = await client.create_session({"model": "gpt-4.1"})
session2 = await client.create_session({"model": "claude-sonnet-4.5"})

# Each maintains independent context
await session1.send({"prompt": "You are helping with Python"})
await session2.send({"prompt": "You are helping with Go"})
```

### 6. BYOK (Bring Your Own Key)
Use your own API keys with custom providers:

```python
session = await client.create_session({
    "provider": {
        "type": "openai",  # or "azure", "anthropic"
        "base_url": "https://your-endpoint.com",
        "api_key": "your-api-key",
    }
})
```

### 7. System Message Customization

```python
# Append mode (default) - adds to CLI foundation
session = await client.create_session({
    "system_message": {
        "mode": "append",
        "content": "You are a helpful assistant for our engineering team.",
    }
})

# Replace mode - full control (removes SDK guardrails)
session = await client.create_session({
    "system_message": {
        "mode": "replace",
        "content": "Your complete custom system message here.",
    }
})
```

---

## 📊 Session Event Types

The SDK provides rich event streaming. All events are available via `SessionEventType`:

| Event Type | Description |
|------------|-------------|
| `ASSISTANT_MESSAGE` | Complete assistant response |
| `ASSISTANT_MESSAGE_DELTA` | Streaming response chunk |
| `ASSISTANT_REASONING` | Model's reasoning process |
| `ASSISTANT_REASONING_DELTA` | Streaming reasoning chunk |
| `ASSISTANT_INTENT` | Detected user intent |
| `ASSISTANT_USAGE` | Token usage information |
| `TOOL_EXECUTION_START` | Tool execution beginning |
| `TOOL_EXECUTION_COMPLETE` | Tool execution finished |
| `TOOL_EXECUTION_PROGRESS` | Tool progress updates |
| `SESSION_IDLE` | Session ready for next input |
| `SESSION_ERROR` | Error occurred |
| `SESSION_START` | Session initialized |
| `SESSION_RESUME` | Session resumed |
| `SUBAGENT_STARTED` | Sub-agent activated |
| `SUBAGENT_COMPLETED` | Sub-agent finished |
| `USER_MESSAGE` | User message processed |

---

## 📂 Repository Structure

```
copilot-sdk/
├── python/                    # Python SDK
│   ├── copilot/              # Main package
│   │   ├── client.py         # CopilotClient class
│   │   ├── session.py        # CopilotSession class
│   │   ├── tools.py          # @define_tool decorator
│   │   ├── types.py          # Type definitions
│   │   └── generated/        # Auto-generated event types
│   └── pyproject.toml        # Package config
├── nodejs/                    # TypeScript/Node.js SDK
│   └── src/
│       ├── client.ts
│       ├── session.ts
│       └── types.ts
├── go/                        # Go SDK
│   ├── client.go
│   ├── session.go
│   └── definetool.go
├── dotnet/                    # .NET SDK
│   └── src/
│       ├── Client.cs
│       └── Session.cs
├── cookbook/                  # Practical recipes
│   ├── python/
│   │   ├── error-handling.md
│   │   ├── multiple-sessions.md
│   │   ├── managing-local-files.md
│   │   ├── pr-visualization.md
│   │   └── persisting-sessions.md
│   ├── nodejs/
│   ├── go/
│   └── dotnet/
├── docs/
│   └── getting-started.md    # Complete tutorial
├── samples/                   # Video tutorials
└── test/                      # Test infrastructure
```

---

## 💰 Billing & Requirements

| Requirement | Details |
|-------------|---------|
| **Subscription** | GitHub Copilot subscription required |
| **Billing Model** | Same as Copilot CLI - counts toward premium request quota |
| **Free Tier** | Limited usage available |
| **BYOK** | Supported for custom API keys |

---

## 🎮 Supported Models

All models available via Copilot CLI are supported:
- `gpt-4.1`
- `gpt-5`
- `claude-sonnet-4`
- `claude-sonnet-4.5`
- `claude-haiku-4.5`

Use `client.get_models()` to get available models at runtime.

---

## 🔧 Client Configuration Options

```python
client = CopilotClient({
    "cli_path": "copilot",      # Path to CLI executable
    "cli_url": "localhost:8080", # Connect to existing server
    "cwd": "/path/to/workdir",   # Working directory
    "log_level": "info",         # Log level: none, error, warning, info, debug, all
    "auto_start": True,          # Auto-start CLI server
    "auto_restart": True,        # Auto-restart on crash
    "use_stdio": True,           # Use stdio transport (default)
    "port": 0,                   # TCP port (0 = random)
    "env": {"KEY": "value"},     # Environment variables
})
```

---

## 📚 Cookbook Recipes Available

1. **Error Handling** - Connection failures, timeouts, cleanup
2. **Multiple Sessions** - Parallel independent conversations
3. **Managing Local Files** - AI-powered file organization
4. **PR Visualization** - Generate PR age charts with GitHub MCP
5. **Persisting Sessions** - Save/resume across restarts

---

## 🔌 External CLI Server Mode

For debugging or resource sharing, run CLI separately:

```bash
# Start CLI in server mode
copilot --server --port 4321
```

```python
# Connect SDK to external server
client = CopilotClient({
    "cli_url": "localhost:4321"
})
```

---

## ⚡ Default Tool Availability

By default, SDK operates with `--allow-all` equivalent:
- File system operations ✅
- Git operations ✅
- Web requests ✅
- All first-party tools enabled ✅

Customize with `available_tools` or `excluded_tools` in session config.

---

## 🎯 Practical Use Cases

| Use Case | Implementation |
|----------|----------------|
| **CLI Assistant** | Interactive terminal with custom tools |
| **Code Generator** | Generate code based on specifications |
| **PR Reviewer** | Custom agent for code review |
| **File Organizer** | AI-powered file management |
| **Data Analyzer** | Process and visualize data |
| **Documentation Bot** | Generate docs from codebase |
| **Multi-User Chat** | One session per user |
| **A/B Testing** | Compare different models |

---

## 🚦 Status & Limitations

| Aspect | Status |
|--------|--------|
| **Stability** | Technical Preview - may have breaking changes |
| **Production Ready** | Not yet recommended for production |
| **Documentation** | Good coverage, improving |
| **Support** | GitHub Issues for bugs/features |

---

## 📖 Quick Reference Links

- **Getting Started Guide:** `docs/getting-started.md`
- **Python SDK README:** `python/README.md`
- **Cookbook Recipes:** `cookbook/python/`
- **Contributing:** `CONTRIBUTING.md`
- **Video Samples:** [AI Powered YouTube Content Generator](https://youtu.be/6GcupNzH678)

---

## 🏁 Next Steps for You

1. **Install the Copilot CLI** - Follow [installation guide](https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli)
2. **Verify CLI works:** `copilot --version`
3. **Install Python SDK in your venv:**
   ```bash
   pip install github-copilot-sdk
   ```
4. **Try the basic example** from this guide
5. **Explore cookbook recipes** for advanced patterns
6. **Build something amazing!** 🚀

---

*Generated from exploration of the copilot-sdk repository on January 23, 2026*
