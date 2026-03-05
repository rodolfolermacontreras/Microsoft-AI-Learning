# MCP Servers

> Extend agents with external tools and data sources via Model Context Protocol.

---

## What MCP Is

Model Context Protocol (MCP) is an open standard for connecting AI models to external
tools and services. MCP servers provide tools for tasks like database queries, API
calls, browser automation, and file operations.

When you add an MCP server, VS Code makes its tools, prompts, and resources available
in chat.

---

## Adding MCP Servers

### From Gallery

```
Extensions view (Ctrl+Shift+X)  ->  Search "@mcp"  ->  Install
```

### Manual Configuration

Create or edit `.vscode/mcp.json`:

```json
{
  "servers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp"
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@microsoft/mcp-server-playwright"]
    },
    "database": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db", "path/to/db.sqlite"]
    }
  }
}
```

### Locations

| Scope | File |
|-------|------|
| Workspace | `.vscode/mcp.json` (share via version control) |
| User profile | MCP: Open User Configuration |

---

## MCP Capabilities

| Capability | What It Provides | How to Access |
|------------|-----------------|---------------|
| **Tools** | Functions agents can call | Automatic via tools picker |
| **Resources** | Data context (files, tables) | Add Context > MCP Resources |
| **Prompts** | Preconfigured templates | `/<server>.<prompt>` |
| **MCP Apps** | Interactive UI components | Inline in chat |

---

## Sandboxing (macOS/Linux)

Restrict MCP server access:

```json
{
  "servers": {
    "myServer": {
      "command": "npx",
      "args": ["-y", "@example/mcp-server"],
      "sandboxEnabled": true,
      "sandbox": {
        "filesystem": {
          "allowWrite": ["${workspaceFolder}"]
        },
        "network": {
          "allowedDomains": ["api.example.com"]
        }
      }
    }
  }
}
```

Sandboxed servers auto-approve tool calls since they run in a controlled environment.

---

## Managing Servers

| Method | Action |
|--------|--------|
| Extensions view | Right-click in MCP SERVERS section |
| mcp.json editor | Use inline code lenses |
| Command Palette | MCP: List Servers > select > action |
| Settings | `chat.mcp.autoStart` for auto-restart on config change |

---

## Security

- Only add servers from trusted sources
- Avoid hardcoding API keys (use input variables or `.env` files)
- Review server configuration before starting
- Trust confirmation is required for new servers

---

## Next Steps

- [Agent Plugins](agent-plugins.md) -- prepackaged MCP + agents + skills bundles
- [Custom Agents](custom-agents.md) -- give agents access to MCP tools
