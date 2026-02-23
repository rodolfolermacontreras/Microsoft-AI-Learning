# Microsoft Agent Framework — Learning & Examples

> **Status**: Release Candidate (.NET and Python)  
> **Predecessor**: Semantic Kernel + AutoGen → unified into Agent Framework  
> **Docs**: [Agent Framework Announcement](https://devblogs.microsoft.com/semantic-kernel/microsoft-agent-framework-reaches-release-candidate/)  
> **📌 Follow**: [../AGENT_DEVELOPMENT_GUIDE.md](../AGENT_DEVELOPMENT_GUIDE.md) for all development practices.

---

## What is Microsoft Agent Framework?

Microsoft Agent Framework is a comprehensive, open-source framework for building, orchestrating, and deploying AI agents. It's the **successor to Semantic Kernel and AutoGen**, providing a unified programming model across .NET and Python.

### Key Capabilities
| Capability | Description |
|-----------|-------------|
| **Simple Agent Creation** | Zero to working agent in a few lines of code |
| **Function Tools** | Type-safe tool definitions that call your code |
| **Graph-based Workflows** | Sequential, concurrent, handoff, and group chat patterns |
| **Multi-provider Support** | Foundry, Azure OpenAI, OpenAI, GitHub Copilot, Claude, Bedrock, Ollama |
| **Streaming** | Built-in streaming support for all patterns |
| **Checkpointing** | Save/restore workflow state |
| **Human-in-the-loop** | Gate agent actions with human approval |
| **Interoperability** | A2A, AG-UI, and MCP standards |

### Installation
```bash
# Python
pip install agent-framework --pre
pip install agent-framework-orchestrations --pre

# .NET
dotnet add package Microsoft.Agents.AI.OpenAI --prerelease
dotnet add package Microsoft.Agents.AI.Workflows --prerelease
dotnet add package Azure.Identity
```

---

## Project Structure

```
microsoft-agent-framework/
├── README.md                    ← You are here
├── notes/
│   ├── framework-overview.md    ← Core concepts & architecture
│   └── migration-comparison.md  ← SK vs AutoGen vs Agent Framework
├── examples/
│   ├── 01-hello-agent/          ← Simplest possible agent
│   ├── 02-function-tools/       ← Adding tools to agents
│   ├── 03-sequential-workflow/  ← Multi-agent sequential pipeline
│   ├── 04-concurrent-workflow/  ← Parallel agent execution
│   ├── 05-handoff-workflow/     ← Agent-to-agent handoff
│   └── 06-group-chat/           ← Group chat pattern
└── comparisons/
    ├── semantic-kernel/         ← Side-by-side SK vs AF examples
    └── autogen/                 ← Side-by-side AutoGen vs AF examples
```

---

## Learning Path

```
1. Read notes/framework-overview.md          → Understand the concepts
2. Read notes/migration-comparison.md        → See what changed from SK/AutoGen
3. Run examples/01-hello-agent/              → Build your first agent
4. Run examples/02-function-tools/           → Add tools
5. Run examples/03-sequential-workflow/      → Multi-agent orchestration
6. Explore comparisons/                      → Compare with previous frameworks
```
