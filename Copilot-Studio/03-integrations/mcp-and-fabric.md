# MCP and Fabric Integration

> **TL;DR:** Fabric Data Agents expose MCP (Model Context Protocol) server endpoints that Copilot Studio can connect to as tools. This lets your agent query Lakehouses, Warehouses, and Semantic Models through natural language. MCP is the open standard glue — same protocol works across Copilot Studio, Claude, and other AI clients.

---

## What Is MCP?

**Model Context Protocol (MCP)** is an open standard for connecting AI models to external tools and data sources. Think of it as a universal plug for AI agents.

```
AI Client (Copilot Studio, Claude, etc.)
     │
     │  MCP Protocol (JSON-RPC over HTTP/SSE)
     │
     ▼
MCP Server (exposes tools, resources, prompts)
     │
     ▼
Backend (database, API, file system, etc.)
```

**Key concepts:**
- **MCP Server** — exposes capabilities (tools, resources, prompts) via a standard protocol
- **MCP Client** — connects to MCP servers and invokes their capabilities
- **Tools** — functions the server exposes (e.g., "run_sql_query", "get_customer_record")
- **Resources** — data the server can provide (e.g., schema information, reference data)

**Why MCP matters for Copilot Studio:**
- One MCP server can serve multiple AI platforms (Studio, Claude, custom apps)
- Fabric Data Agents automatically expose MCP endpoints — no custom server needed
- Standardized protocol means less custom integration code

---

## Fabric Data Agents + MCP

### What Are Fabric Data Agents?

Fabric Data Agents are AI-powered agents within Microsoft Fabric that can:
- Query **Lakehouses** (SQL endpoint)
- Query **Warehouses** (T-SQL)
- Query **Semantic Models** (DAX)
- Access **OneLake** files
- Execute queries through natural language → SQL/DAX translation

**Each Fabric Data Agent automatically publishes an MCP server endpoint.**

### Architecture

```
User ──▶ Copilot Studio Agent
              │
              │ (MCP connection)
              ▼
         Fabric Data Agent (MCP Server)
              │
              ├── Lakehouse (SQL endpoint)
              ├── Warehouse (T-SQL)
              ├── Semantic Model (DAX)
              └── OneLake files
```

### Setting Up the Connection

**Step 1: Create a Fabric Data Agent**
1. Open Microsoft Fabric → select your workspace
2. Create a new **Data Agent**
3. Configure:
   - **Instructions:** Plain language description of what data this agent covers
   - **Data sources:** Select Lakehouses, Warehouses, and/or Semantic Models
   - **Permissions:** Configure who can access
4. The Data Agent publishes an MCP endpoint URL automatically

**Step 2: Connect from Copilot Studio**
1. In your Copilot Studio agent → Tools → Add a tool → MCP
2. Enter the Fabric Data Agent's MCP server URL
3. Studio discovers the available tools from the MCP server
4. Select which tools to enable for your agent
5. Configure authentication (typically Entra ID / OAuth)

**Step 3: Test**
1. In the test chat, ask a data question: "What were total sales last quarter?"
2. The flow: User question → Studio agent → MCP call → Fabric Data Agent → SQL/DAX query → results → natural language response

### Fabric Data Agent Instructions

Write agent instructions that help the AI understand your data:

```
You are a data analyst for Contoso's sales team. You have access to:
- Sales Lakehouse: Contains orders, customers, products, and regions tables
- Finance Semantic Model: Contains revenue, costs, and profitability measures

When answering questions:
- Use the Sales Lakehouse for transactional queries (order details, customer lookups)
- Use the Finance Semantic Model for aggregate metrics (revenue, margins, YoY growth)
- Always specify date ranges when querying time-series data
- Format currency as USD with 2 decimal places
```

**Instruction limits:** Up to 15,000 characters (as of current documentation).

---

## MCP Beyond Fabric

### Custom MCP Servers

You can build your own MCP server and connect it to Copilot Studio:

| Language | MCP SDK |
|---|---|
| Python | `mcp` package |
| TypeScript | `@modelcontextprotocol/sdk` |
| .NET | Community implementations |

**Example: Python MCP server exposing a custom tool:**
```python
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("my-data-tools")

@server.tool()
async def get_customer_health(customer_id: str) -> list[TextContent]:
    """Get the health score and recent activity for a customer."""
    # Your custom logic here
    score = await calculate_health_score(customer_id)
    return [TextContent(type="text", text=f"Health score: {score}")]

# Run the server (SSE transport for web-based clients like Copilot Studio)
server.run(transport="sse", port=8080)
```

**Connect to Copilot Studio:**
1. Deploy your MCP server (Azure App Service, Container Apps, etc.)
2. In Studio → Tools → Add a tool → MCP → enter your server URL
3. Studio discovers your tools automatically

### MCP in the Copilot SDK

The Copilot SDK also supports MCP servers in session configuration:

```python
session = await client.create_session({
    "mcp_servers": {
        "fabric-data": {
            "url": "https://your-fabric-data-agent.fabric.microsoft.com/mcp",
            "auth": { ... }
        },
        "custom-tools": {
            "url": "https://your-custom-mcp.azurewebsites.net/mcp",
            "auth": { ... }
        }
    }
})
```

This means the **same MCP server** can serve both Copilot Studio agents and Copilot SDK applications.

---

## Practical Patterns

### Pattern 1: Data Q&A Agent

Copilot Studio handles conversation; Fabric Data Agent handles analytics.

```
User: "What were our top 5 products by revenue last quarter?"
  │
  ▼ Copilot Studio routes to MCP tool
  │
  ▼ Fabric Data Agent generates SQL:
     SELECT TOP 5 ProductName, SUM(Revenue) as TotalRevenue
     FROM Sales.Orders
     WHERE OrderDate >= '2025-04-01'
     GROUP BY ProductName
     ORDER BY TotalRevenue DESC
  │
  ▼ Results returned via MCP
  │
  ▼ Studio formats: "Here are the top 5 products by revenue..."
```

### Pattern 2: Multi-Source Agent

Agent routes to different MCP servers based on the question type.

```
User question
  │
  ▼ Copilot Studio (generative orchestration)
  │
  ├── Sales data → Fabric Data Agent (Lakehouse)
  ├── Financial KPIs → Fabric Data Agent (Semantic Model)
  ├── Customer info → Custom MCP Server (CRM API)
  └── General questions → Knowledge sources (SharePoint docs)
```

### Pattern 3: Fabric → Studio → Teams Pipeline

End-to-end data analytics through Teams.

```
Team member asks in Teams → Studio agent → Fabric Data Agent → Query results → Formatted in Teams
```

---

## Current Limitations and Considerations

| Limitation | Impact | Workaround |
|---|---|---|
| **MCP is relatively new in Studio** | Documentation and tooling may evolve | Follow Microsoft Learn updates; test in a trial environment first |
| **Fabric Data Agent instructions** | 15,000 char limit may not cover complex schemas | Focus instructions on common query patterns; supplement with examples |
| **Query complexity** | Very complex analytical queries may not translate well | Pre-create views or stored procedures for complex patterns |
| **Latency** | MCP calls add roundtrip time (Studio → MCP → Fabric → back) | Acceptable for conversational flows; not ideal for sub-second responses |
| **Authentication** | Entra ID pass-through required; some orgs have complex auth setups | Work with IT to ensure proper app registrations and permissions |
| **Context window** | Large query results may exceed context limits | Use LIMIT/TOP in queries; summarize in the MCP server if possible |

---

## When to Use MCP vs Other Tool Types

| Scenario | Use MCP | Use Connector/REST |
|---|---|---|
| Fabric Lakehouse/Warehouse queries | Yes -- native MCP endpoint | Possible via REST, but MCP is easier |
| Custom AI tool that serves multiple platforms | Yes -- write once, use everywhere | REST API if only Studio needs it |
| Simple CRUD operations on Dataverse | Connector is simpler | Yes |
| SharePoint file operations | Connector is simpler | Yes |
| Complex data analytics pipeline | Yes -- Fabric Data Agent handles query generation | Too complex for connector |

---

## Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [Microsoft Fabric Data Agents](https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agents)
- [Copilot Studio MCP Support](https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-tools-custom-agent)
- Workspace reference: `../copilot-sdk-exploration/COPILOT_SDK_SUMMARY.md` (MCP section)

---

## Next Steps

- **[Power Platform Integration](power-platform.md)** — Connectors and flows
- **[Copilot SDK Bridge](copilot-sdk-bridge.md)** — Using MCP to bridge Studio and SDK
- **[Tool Selection Guide](../06-tipsheets/tool-selection-guide.md)** — When to use which tool type

---

*Sources: [MCP Documentation](https://modelcontextprotocol.io/), [Microsoft Learn — Fabric Data Agents](https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agents), user research notes on Fabric/MCP integration*
