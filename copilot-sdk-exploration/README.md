# Copilot SDK Exploration

Hands-on exploration of the [GitHub Copilot SDK](https://github.com/github/copilot-sdk) -- a programmable interface for embedding Copilot's AI-powered agentic workflows into applications.

## What This Covers

- Understanding the Copilot SDK architecture and capabilities
- Basic agent invocation (question/answer)
- Streaming response handling
- Integration patterns for Python applications

## Directory Structure

```
copilot-sdk-exploration/
├── README.md                 # This file
├── COPILOT_SDK_SUMMARY.md    # Detailed SDK reference (features, API, patterns)
└── examples/
    ├── test_sdk_basic.py     # Simple Q&A with Copilot
    └── test_sdk_streaming.py # Streaming token-by-token responses
```

## Prerequisites

- GitHub Copilot CLI installed via WinGet
- Python 3.12+ with the `copilot` package
- Active GitHub Copilot subscription

## Quick Start

```powershell
# From workspace root
.\.venv\Scripts\Activate.ps1

# Install the SDK
pip install github-copilot-sdk

# Run basic test
python copilot-sdk-exploration\examples\test_sdk_basic.py

# Run streaming test
python copilot-sdk-exploration\examples\test_sdk_streaming.py
```

## Key Concepts

| Concept | Description |
|---------|-------------|
| `CopilotClient` | Main entry point -- manages connection to Copilot CLI |
| `Session` | Conversation context with model selection |
| `send_and_wait` | Send prompt, receive full response |
| `Streaming` | Token-by-token output via event handlers |

## Related

- **Source SDK repo**: `../copilot-sdk/` (cloned reference)
- **Full summary**: [COPILOT_SDK_SUMMARY.md](COPILOT_SDK_SUMMARY.md)
- **Microsoft Agent Framework**: `../microsoft-agent-framework/` (successor patterns)
