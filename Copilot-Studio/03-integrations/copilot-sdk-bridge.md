# Copilot SDK Bridge

> **TL;DR:** Copilot Studio and the GitHub Copilot SDK serve different audiences but can share infrastructure — particularly MCP servers. This document covers patterns for bridging the two, when hybrid approaches make sense, and how to build shared AI tooling.

---

## Why Bridge Studio and SDK?

Most organizations have two classes of AI agent users:

| Audience | Tool | How They Work |
|---|---|---|
| **Business users** | Copilot Studio | Visual builder, Teams channel, low-code |
| **Developers** | Copilot SDK | Code-first, custom apps, terminal/IDE |

The bridge patterns below let both audiences benefit from the **same backend capabilities** without duplicating work.

---

## Pattern 1: Shared MCP Servers

Build your AI tools once as MCP servers. Connect from both platforms.

```
                    ┌──────────────────┐
                    │   MCP Server     │
                    │  (Custom Tools)  │
                    └────┬────────┬────┘
                         │        │
              ┌──────────▼─┐  ┌──▼──────────┐
              │ Copilot     │  │ Copilot SDK  │
              │ Studio      │  │ (Python/TS)  │
              │ Agent       │  │ Application  │
              └─────────────┘  └─────────────┘
              Business Users     Developers
```

**How it works:**
- Build an MCP server that exposes your domain tools (data queries, actions, lookups)
- In Copilot Studio: add as MCP tool
- In Copilot SDK: add to `mcp_servers` session config
- Same server, same tools, same auth — two client experiences

**Example: Customer health MCP server**
```python
# Shared MCP server — serves both Studio and SDK clients
@server.tool()
async def get_customer_health(customer_id: str) -> list[TextContent]:
    """Get health score, churn risk, and recent interactions for a customer."""
    data = await crm_api.customer_health(customer_id)
    return [TextContent(type="text", text=json.dumps(data))]

@server.tool()
async def list_open_tickets(customer_id: str) -> list[TextContent]:
    """List all open support tickets for a customer with status and age."""
    tickets = await support_api.open_tickets(customer_id)
    return [TextContent(type="text", text=json.dumps(tickets))]
```

**Studio agent** uses these tools in conversational support workflows.
**SDK application** uses the same tools in a developer CLI for quick customer lookups.

---

## Pattern 2: Fabric Data Layer Sharing

Both platforms connect to the same Fabric Data Agent for analytics.

```
                    ┌──────────────────┐
                    │ Fabric Data Agent│
                    │   (MCP Server)   │
                    └────┬────────┬────┘
                         │        │
              ┌──────────▼─┐  ┌──▼──────────┐
              │ Studio Agent│  │ SDK Script   │
              │ (Teams Q&A) │  │ (CLI Reports)│
              └─────────────┘  └─────────────┘
                 "What were       generate_report(
                  sales?"          "monthly_sales")
```

**Studio agent** handles ad-hoc natural language questions from business users in Teams.
**SDK script** generates automated reports and analyses for the data team.

---

## Pattern 3: Studio Front-End, SDK Back-End

Use Studio for conversation management and the SDK for heavy-lifting tasks.

```
User ──▶ Copilot Studio Agent ──▶ REST API / Azure Function
                                        │
                                  SDK-powered backend
                                  (custom tools, multi-model,
                                   complex reasoning)
```

**When to use:** Studio handles the UX (Teams publishing, conversation flow, analytics) but the task requires capabilities only available in code — multi-model routing, complex file processing, custom agent logic.

**Implementation:**
1. Build your complex logic as an Azure Function or API using the Copilot SDK
2. Expose it as a REST API
3. In Studio, add it as a REST API tool
4. Studio handles conversation; SDK handles processing

---

## Pattern 4: Complementary Agents

Separate agents for separate audiences — no shared infrastructure needed.

| Agent | Platform | Audience | Purpose |
|---|---|---|---|
| HR Assistant | Copilot Studio | All employees (Teams) | Policy Q&A, leave requests |
| Code Review Helper | Copilot SDK | Dev team (CLI/IDE) | PR review, code analysis |
| Sales Copilot | Copilot Studio | Sales team (Teams) | CRM lookups, meeting prep |
| Data Pipeline Monitor | Copilot SDK | Data engineers (CLI) | Pipeline health, debugging |

This is the simplest pattern — no bridging needed, just the right tool for the right audience.

---

## Decision Framework

```
Do business users AND developers need the same capabilities?
├── YES → Pattern 1 (Shared MCP) or Pattern 2 (Shared Fabric)
│         Build tools once, connect from both platforms
└── NO → Do business users need capabilities only code can provide?
         ├── YES → Pattern 3 (Studio front-end, SDK back-end)
         └── NO → Pattern 4 (Complementary — separate agents)
```

---

## Implementation Tips

### For Shared MCP Servers

| Tip | Why |
|---|---|
| Use SSE transport (HTTP-based) | Works with both Studio (web) and SDK (local/remote) |
| Design tool descriptions carefully | Studio's generative orchestration AND SDK agents read them |
| Keep tool inputs simple | Both platforms need to map conversation to tool inputs |
| Add comprehensive error responses | Studio can show them in chat; SDK can handle programmatically |
| Version your MCP server | Breaking changes affect both platforms simultaneously |

### For REST API Bridges

| Tip | Why |
|---|---|
| Use OpenAPI specs | Studio can import them; SDK apps can auto-generate clients |
| Implement proper auth (OAuth2) | Both platforms support OAuth; SSO via Entra ID for both |
| Return structured JSON | Studio can extract fields; SDK can parse programmatically |
| Add health checks | Monitor the shared endpoint separately |

---

## Workspace References

For SDK details, see:
- `../../copilot-sdk/README.md` — SDK overview and setup
- `../../copilot-sdk/docs/getting-started.md` — Detailed tutorial
- `../../copilot-sdk-exploration/COPILOT_SDK_SUMMARY.md` — Complete reference
- `../../copilot-sdk/cookbook/` — Practical recipes

---

## Next Steps

- **[MCP and Fabric](mcp-and-fabric.md)** — Detailed MCP integration guide
- **[Copilot Studio vs Copilot SDK](../01-fundamentals/copilot-studio-vs-copilot-sdk.md)** — Full comparison
- **[Tool Selection Guide](../06-tipsheets/tool-selection-guide.md)** — Choosing the right approach

---

*Based on analysis of Copilot Studio documentation and Copilot SDK (Technical Preview) — patterns and APIs may evolve.*
