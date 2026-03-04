# Tools and Actions

> **TL;DR:** Tools let your Copilot Studio agent DO things — not just talk. There are six tool types: prebuilt connectors, custom connectors, agent flows, prompts, REST APIs, and MCP servers. Plus computer use for GUI automation. Choose based on what you're connecting to and who manages it.

---

## Tool Types at a Glance

| Tool Type | What It Is | Best For |
|---|---|---|
| **Prebuilt connector** | Microsoft-managed connector from the 1,100+ library | SharePoint, Outlook, Teams, ServiceNow, Salesforce, etc. |
| **Custom connector** | Your own API wrapped as a Power Platform connector | Internal APIs already exposed via custom connectors |
| **Agent flow** | Power Automate-style workflow built natively in Studio | Multi-step automations, logic-heavy tasks, loops |
| **Prompt** | Single-turn AI prompt with model + knowledge access | Summarization, classification, extraction, rewriting |
| **REST API** | Direct HTTP call to any REST endpoint | External APIs without a Power Platform connector |
| **MCP server** | Model Context Protocol server connection | Fabric Data Agents, custom AI tools, external AI services |
| **Computer use** | GUI automation (click, type, navigate) | Legacy apps without APIs, screen-based workflows |

---

## Tool Type Deep Dives

### 1. Prebuilt Connectors

Connect to 1,100+ Microsoft and third-party services.

**Setup:**
1. Tools → Add a tool → Search connector library
2. Select the connector (e.g., "Microsoft Teams")
3. Choose the action (e.g., "Post message in a chat or channel")
4. Configure authentication
5. Map inputs from conversation variables

**Common connectors:**

| Connector | Popular Actions |
|---|---|
| **Microsoft Teams** | Post message, create channel, add member |
| **Outlook** | Send email, create event, get messages |
| **SharePoint** | Get items, create item, get file content |
| **Dataverse** | List rows, add row, update row |
| **ServiceNow** | Create incident, get record, update record |
| **Salesforce** | Get record, create record, run query |
| **HTTP** | Make any HTTP request |

**Authentication options:**
- **End-user credentials** — action runs as the user
- **Maker-provided credentials** — action runs as a service account you configure

### 2. Custom Connectors

Your own APIs wrapped in the Power Platform connector format.

**When to use:** You already have internal APIs and want reusability across Power Platform (not just Copilot Studio).

**Setup:**
1. Create a custom connector in Power Platform (via OpenAPI spec, from blank, or from Azure)
2. In Copilot Studio → Tools → Add a tool → select your custom connector
3. Choose the action and configure as with prebuilt connectors

### 3. Agent Flows

Power Automate-style workflows created directly within Copilot Studio.

**When to use:** 
- Multi-step logic (loops, conditions, approvals)
- Need to transform or combine data from multiple sources
- Complex business rules that go beyond a single API call

**Setup:**
1. Tools → Add a tool → Agent flow → New
2. Build the flow visually (triggers, actions, conditions, loops)
3. Define inputs (what the agent passes in) and outputs (what comes back)
4. The flow is stored as a tool and invoked by the agent

**Example flow:**
```
Input: ticket_description, urgency
  │
  ▼ Parse urgency level
  │
  ▼ If urgency = "critical"
  │   └─ Create P1 incident in ServiceNow
  │   └─ Send Teams alert to on-call channel
  │   └─ Return: incident_id, status
  │
  ▼ Else
      └─ Create standard ticket in ServiceNow
      └─ Return: ticket_id, status
```

### 4. Prompts

Single-turn AI model interactions, useful for processing text.

**When to use:**
- Summarize a document or conversation
- Classify user intent
- Extract structured data from unstructured text
- Rewrite content in a different tone

**Setup:**
1. Tools → Add a tool → Prompt → New
2. Write the prompt template with optional placeholders
3. Optionally attach knowledge sources for grounding
4. Configure the model parameters

### 5. REST APIs

Direct HTTP connections to any REST endpoint.

**When to use:**
- External API without a Power Platform connector
- Internal API you don't want to wrap as a custom connector
- Quick prototyping without connector overhead

**Setup:**
1. Tools → Add a tool → REST API
2. Enter the endpoint URL, method, headers, and body
3. Configure authentication (OAuth2, API key, etc.)
4. Map request parameters from conversation variables
5. Map response fields to output variables

### 6. MCP Servers

Connect to Model Context Protocol servers for tools and resources.

**When to use:**
- Fabric Data Agents (query Lakehouses, Warehouses, Semantic Models)
- Custom MCP servers exposing domain-specific tools
- Standardized AI tool integration across multiple platforms

**Setup:**
1. Tools → Add a tool → MCP → New
2. Enter the MCP server URL
3. Studio discovers available tools from the server
4. Select which tools to expose to the agent
5. Configure authentication

**Key details:**
- MCP is an open standard — same server works with Claude, Copilot, and other MCP clients
- Fabric Data Agents automatically expose MCP endpoints
- See [MCP and Fabric Integration](../03-integrations/mcp-and-fabric.md) for detailed setup

### 7. Computer Use

GUI automation — the agent clicks buttons, fills forms, and navigates screens.

**When to use:**
- Legacy applications with no API
- Screen-based workflows that can't be automated otherwise
- Last resort when no other integration method is available

**Caution:** More fragile than API-based tools; sensitive to UI changes.

---

## Tool Configuration

Every tool in Copilot Studio has three configuration sections:

### 1. Details

- **Name:** How the agent references the tool
- **Description:** What the tool does (critical for generative orchestration — the AI reads this to decide when to use the tool)

### 2. Inputs

- Map conversation variables or literals to the tool's parameters
- Define which inputs are required vs optional
- Set default values

### 3. Completion (After Running)

| Option | Behavior |
|---|---|
| **Summarize results in chat** | AI generates a natural language summary of the tool's output |
| **Send a message** | Display a custom message with optional variable interpolation |
| **Ask a question** | Follow up with the user based on results |
| **Go to another topic** | Route to a specific topic after tool execution |

---

## Tool Limits

| Limit | Value |
|---|---|
| **Max tools per agent** | 128 |
| **Recommended tools** | 25-30 (for best AI routing accuracy) |
| **Tool description max length** | Varies (keep concise — a few sentences) |
| **Max tool inputs** | Varies by tool type |

> **Pro tip:** If you approach the 128 limit, use the multi-agent pattern — split tools across specialist agents.

---

## Authentication Patterns

| Pattern | How It Works | Use When |
|---|---|---|
| **End-user auth** | Tool runs with the user's OAuth credentials | User-specific data (their emails, their tickets) |
| **Maker-provided auth** | Tool runs with a service account you configure | Shared data (knowledge bases, common APIs) |
| **API key** | Static key passed in headers | Simple external APIs |
| **No auth** | Public endpoints | Public APIs with no auth required |

**Security guidance:**
- Prefer end-user auth for user-specific data (respects permissions)
- Use maker-provided for shared resources
- Never expose credentials in tool descriptions or messages
- Rotate API keys on a regular schedule

---

## Tool Selection: How the Agent Chooses

In **generative orchestration**, the AI decides which tool to call based on:

1. **User's message** — what they're asking for
2. **Tool descriptions** — what each tool can do
3. **Tool input schemas** — what parameters are needed
4. **Conversation context** — what's been discussed so far

**This makes tool descriptions the single most important factor in tool routing.**

### Writing Good Tool Descriptions

**Good:**
> "Resets a user's password for the email system. Requires the user's email address and a verification code. Returns a temporary password and instructions for setting a new one."

**Bad:**
> "Password reset"

**Good:**
> "Creates a new support ticket in ServiceNow with the specified title, description, urgency level, and category. Returns the ticket ID and URL."

**Bad:**
> "ServiceNow ticket"

---

## Choosing the Right Tool Type

```
Need to connect to...
├── A Microsoft or popular SaaS service?
│   └── Prebuilt connector  <-- use this
├── Your own API already in Power Platform?
│   └── Custom connector  <-- use this
├── An external REST API?
│   └── REST API tool  <-- use this (or custom connector for reuse)
├── A Fabric Data Agent or MCP-compatible service?
│   └── MCP server  <-- use this
├── Multi-step logic with conditions and loops?
│   └── Agent flow  <-- use this
├── AI text processing (summarize, classify, extract)?
│   └── Prompt  <-- use this
└── A legacy GUI application with no API?
    └── Computer use  <-- use this (last resort)
```

---

## Next Steps

- **[MCP and Fabric](../03-integrations/mcp-and-fabric.md)** — Detailed MCP and Fabric Data Agent integration guide
- **[Tool Selection Guide](../06-tipsheets/tool-selection-guide.md)** — Quick-reference decision matrix
- **[Power Platform Integration](../03-integrations/power-platform.md)** — Deeper look at connector and flow patterns

---

*Sources: [Microsoft Learn — Add Tools](https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-tools-custom-agent), [Microsoft Learn — Extend Capabilities](https://learn.microsoft.com/en-us/microsoft-copilot-studio/copilot-plugins-overview)*
