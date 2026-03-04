# Power Platform Integration

> **TL;DR:** Copilot Studio is a native Power Platform citizen. Agents live in Power Platform environments, use Power Platform connectors for data access, and leverage Power Automate for complex workflows. Understanding these integration points unlocks the full potential of your agents.

---

## Copilot Studio ↔ Power Platform

```
┌──────────────────────────────────────────────────┐
│                Power Platform                     │
│                                                   │
│  ┌──────────────┐  ┌──────────────┐              │
│  │Copilot Studio│  │Power Automate│              │
│  │  (Agents)    │◄─┤  (Flows)     │              │
│  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                       │
│  ┌──────▼─────────────────▼──────┐               │
│  │         Connectors            │               │
│  │  (1,100+ Microsoft & 3rd party) │             │
│  └──────┬────────────────────────┘               │
│         │                                        │
│  ┌──────▼───────┐  ┌──────────────┐             │
│  │  Dataverse    │  │ Power Apps   │             │
│  │  (Data Store) │  │ (UI Layer)   │             │
│  └──────────────┘  └──────────────┘             │
└──────────────────────────────────────────────────┘
```

---

## Key Integration Points

### 1. Environments

Copilot Studio agents live in Power Platform environments. An environment is a container for:
- Agents and their configurations
- Dataverse tables and data
- Connections and authentication credentials
- Solution packages for ALM

**Strategy:**
- **Dev environment** — build and test agents
- **Staging environment** — QA and UAT testing
- **Production environment** — live agents serving users

### 2. Connectors

Connectors are the primary mechanism for agents to interact with external systems.

**Categories:**

| Category | Examples | Auth Pattern |
|---|---|---|
| **Standard** | SharePoint, Outlook, Teams, Excel | End-user or maker credentials |
| **Premium** | SQL Server, HTTP, Azure services | Typically maker or service account |
| **Custom** | Your internal APIs | You define the auth |

**Using connectors as tools in agents:**
1. Add connector action as a tool in your agent
2. Write a clear description for generative orchestration
3. Map conversation variables to connector inputs
4. Define completion behavior (summarize, message, redirect)

### 3. Power Automate Flows

Copilot Studio agents can trigger Power Automate flows for complex multi-step logic.

**Two ways to use flows:**

| Method | Description | Best For |
|---|---|---|
| **Agent flows** | Created natively in Copilot Studio | Simple to moderate automation, stays within Studio |
| **Cloud flows** | Created in Power Automate, called from Studio | Complex logic, existing flows, advanced connectors |

**Agent flow example — HR Leave Request:**
```
Input: employee_email, leave_type, start_date, end_date
  │
  ├── Get employee details from Dataverse
  │
  ├── Check leave balance
  │
  ├── If sufficient balance:
  │   ├── Create leave request record
  │   ├── Send approval email to manager
  │   └── Return: request_id, status = "Pending Approval"
  │
  └── If insufficient balance:
      └── Return: status = "Insufficient Balance", remaining_days
```

### 4. Dataverse

Dataverse is the default data store for Power Platform. Copilot Studio uses it for:
- **Agent configuration storage** — topics, settings, analytics
- **Knowledge source** — search Dataverse tables for answers
- **Data operations** — CRUD via connector or flow
- **File storage** — uploaded knowledge documents

**Best practices:**
- Enable Dataverse search for knowledge source tables
- Use security roles to control data access
- Index columns you expect the agent to search

### 5. Power Apps

Combine Copilot Studio with Power Apps for richer UX:

| Pattern | Description |
|---|---|
| **Embed agent in Power App** | Add a chat widget to your Power App |
| **Agent opens Power App** | Agent sends a link to a Power App form for complex data entry |
| **Shared Dataverse** | Both the app and agent read/write the same Dataverse tables |

---

## Solution Management (ALM)

Copilot Studio agents support Power Platform solution management for Application Lifecycle Management:

| Operation | How |
|---|---|
| **Export agent** | Export as a managed or unmanaged solution |
| **Import agent** | Import solution into another environment |
| **Version control** | Solutions can be committed to source control |
| **CI/CD** | Power Platform Build Tools for Azure DevOps / GitHub Actions |
| **Environment variables** | Configure environment-specific settings (URLs, credentials) |

**Recommended flow:**
```
Dev Environment → Export Solution → Source Control → CI/CD Pipeline → Staging → Production
```

---

## Common Integration Scenarios

### Scenario 1: Teams + SharePoint + Dataverse

```
User in Teams → Agent → SharePoint (knowledge) + Dataverse (records) + Teams (notifications)
```

The most common enterprise setup. Agent answers questions from SharePoint docs, creates/updates Dataverse records, and sends Teams notifications.

### Scenario 2: CRM Workflow Automation

```
User → Agent → Dynamics 365 (via connector) + Power Automate (complex logic)
```

Agent collects information, validates against CRM data, triggers a flow for the multi-step business process.

### Scenario 3: External System Integration

```
User → Agent → Custom connector (internal API) + HTTP connector (external API)
```

Agent connects to systems beyond the Microsoft ecosystem via custom connectors or direct HTTP calls.

---

## Licensing Considerations

| Component | License Required |
|---|---|
| **Copilot Studio** | Copilot Studio license (per user or per tenant) |
| **Standard connectors** | Included with Copilot Studio |
| **Premium connectors** | May require Power Automate Premium or separate licensing |
| **Dataverse** | Included with Copilot Studio environment |
| **Power Automate flows (cloud)** | May require Power Automate license depending on usage |
| **Agent flows (native)** | Included with Copilot Studio |

> **Tip:** Agent flows (built natively in Studio) avoid separate Power Automate licensing in many scenarios. Use them when the flow complexity allows.

---

## Next Steps

- **[Microsoft 365 Integration](microsoft-365.md)** — Teams, Outlook, and M365 Copilot extensions
- **[Tools and Actions](../02-agents/tools-and-actions.md)** — Complete connector and tool reference
- **[MCP and Fabric](mcp-and-fabric.md)** — Data agent integration

---

*Sources: [Microsoft Learn — Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/), [Power Platform Documentation](https://learn.microsoft.com/en-us/power-platform/)*
