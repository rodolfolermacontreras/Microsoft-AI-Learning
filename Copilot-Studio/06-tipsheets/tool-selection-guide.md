# Tool Selection Guide

> Match your integration need to the right tool type in 30 seconds.

---

## The Flowchart

```
What are you connecting to?
│
├── Microsoft or popular SaaS service? ──────────▶ PREBUILT CONNECTOR
│   (SharePoint, Teams, Outlook, ServiceNow,
│    Salesforce, Dynamics, SQL Server, etc.)
│
├── Your own API already in Power Platform? ─────▶ CUSTOM CONNECTOR
│
├── An external REST API (no connector)? ────────▶ REST API TOOL
│
├── Fabric Lakehouse / Warehouse / ──────────────▶ MCP SERVER
│   Semantic Model?                                (Fabric Data Agent)
│
├── Any MCP-compatible server? ──────────────────▶ MCP SERVER
│
├── Multi-step workflow with ────────────────────▶ AGENT FLOW
│   conditions, loops, approvals?
│
├── AI text processing ─────────────────────────▶ PROMPT
│   (summarize, classify, extract, rewrite)?
│
└── Legacy GUI app with no API? ────────────────▶ COMPUTER USE
                                                   (last resort)
```

---

## Comparison Table

| Dimension | Prebuilt Connector | Custom Connector | Agent Flow | Prompt | REST API | MCP Server | Computer Use |
|---|---|---|---|---|---|---|---|
| **Setup effort** | Low | Medium | Low-Medium | Low | Medium | Medium | High |
| **Maintenance** | Microsoft-managed | You maintain | You maintain | You maintain | You maintain | You maintain | Fragile |
| **Auth options** | User / Maker | You define | Inherits | None | You define | You define | System-level |
| **Multi-step logic** | Single action | Single action | Yes | Single call | Single call | Per-tool call | Sequence of UI actions |
| **Reusable in Power Platform** | Yes | Yes | Studio only | Studio only | Studio only | Studio + SDK | Studio only |
| **Best strength** | Breadth (1,100+) | Your APIs | Complex logic | AI processing | Flexibility | Standard protocol | No-API apps |

---

## When Each Tool Type Shines

### Prebuilt Connector — "The Default Choice"
- Already exists for your target service
- Microsoft manages updates and compatibility
- Standard auth patterns (OAuth, API key)
- **Pick this first** unless you have a reason not to

### Custom Connector — "Your API, Platform-Ready"
- Your internal API needs to be reusable across Power Platform
- You want Power Platform's connection management (test, share, govern)
- You have an OpenAPI spec to import

### Agent Flow — "Logic Goes Here"
- You need if/else branching, loops, or multi-step workflows
- Combining data from multiple sources before responding
- Business rules that are too complex for a single connector call
- **Bonus:** Avoids separate Power Automate licensing in some scenarios

### Prompt — "AI Does the Processing"
- Summarize a long document or conversation
- Classify user intent into categories
- Extract structured data from unstructured text
- Rewrite content in a different tone or language
- **Not for:** data retrieval or external actions

### REST API — "Direct HTTP Access"
- External API without a Power Platform connector
- Quick prototyping (no connector creation overhead)
- Simple GET/POST operations
- **Trade-off:** Less governance than connectors

### MCP Server — "Standard AI Tool Protocol"
- Fabric Data Agents (query Lakehouses, Warehouses, Semantic Models)
- Custom AI tools you want to serve Copilot Studio AND other AI clients (Copilot SDK, Claude, etc.)
- Multi-tool servers (one connection, many capabilities)
- **Sweet spot:** Shared AI infrastructure across platforms

### Computer Use — "No Other Option"
- Legacy application with no API, no connector, no integration surface
- Screen-based workflows (click, type, navigate)
- **Fragile:** UI changes break automation
- **Always prefer API-based tools when available**

---

## Common Scenarios → Recommended Tool Type

| Scenario | Tool Type | Why |
|---|---|---|
| Send email after completing a task | **Prebuilt connector** (Outlook) | Native, simple, maintained by Microsoft |
| Create ServiceNow ticket | **Prebuilt connector** (ServiceNow) | Direct integration available |
| Look up customer in internal CRM API | **Custom connector** or **REST API** | Your API, standard patterns |
| Check leave balance + create request + notify manager | **Agent flow** | Multi-step with conditions |
| Summarize a support conversation | **Prompt** | AI text processing |
| Query sales data in Fabric | **MCP server** (Fabric Data Agent) | Native MCP endpoint |
| Fill out a form in a legacy web app | **Computer use** | No API available |
| Call an internal microservice | **REST API** | Quick, no connector overhead |
| Share tools with Copilot SDK apps | **MCP server** | Same server, multiple AI clients |

---

## Limits Reminder

| Limit | Value |
|---|---|
| Max tools per agent | 128 |
| Recommended for best routing | 25-30 |
| If approaching limit | Use multi-agent pattern (split tools across specialist agents) |

---

## Tool Description Writing (Critical for Generative Orchestration)

The AI reads tool descriptions to decide when to invoke tools. **Quality of descriptions directly impacts routing accuracy.**

### Formula

```
[What the tool does] + [What inputs it needs] + [What it returns]
```

### Examples

| Quality | Description |
|---|---|
| **Bad** | "Email tool" |
| **Good** | "Sends an email via Outlook. Requires recipient email address, subject, and body text. Returns confirmation that the email was sent." |
| **Bad** | "ServiceNow" |
| **Good** | "Creates a new incident in ServiceNow. Requires a short description, urgency level (low/medium/high), and category. Returns the incident number and URL." |

---

*For full tool documentation, see [Tools and Actions](../02-agents/tools-and-actions.md)*
