# Microsoft 365 Integration

> **TL;DR:** Copilot Studio agents integrate deeply with M365 — publish to Teams, extend Microsoft 365 Copilot, access SharePoint and Outlook data, and leverage Microsoft Graph for tenant-wide context. The primary channel for most enterprise agents is Teams.

---

## Integration Surface Areas

| M365 Service | Integration Type | What It Enables |
|---|---|---|
| **Microsoft Teams** | Publishing channel | Users chat with your agent directly in Teams |
| **Microsoft 365 Copilot** | Extension | Your agent appears as a capability inside M365 Copilot |
| **SharePoint** | Knowledge source | Agent answers from SharePoint content |
| **Outlook** | Tool (connector) | Agent sends emails, creates events, reads messages |
| **Microsoft Graph** | Data layer | Tenant-wide search, user profiles, calendar, files |

---

## Publishing to Microsoft Teams

Teams is the most common deployment channel for enterprise Copilot Studio agents.

### Setup

1. Go to your agent → **Channels** → **Microsoft Teams**
2. Configure the Teams app:
   - App name and description
   - App icon
   - Privacy and terms links
   - Scope: Personal chat / Group chat / Teams channels
3. Submit for admin approval (if required by your tenant)
4. Users install the agent as a Teams app

### What Users Experience

- Agent appears as a **chat contact** in Teams
- Users interact via natural language text
- Agent can send:
  - Text messages
  - Adaptive Cards (rich interactive cards)
  - Quick replies (suggested actions)
  - File links
- Agent can be added to **team channels** for shared access

### Best Practices for Teams

| Practice | Why |
|---|---|
| Use Adaptive Cards for structured data | Better UX than text for tables, forms, and buttons |
| Keep responses concise | Teams chat has limited display width |
| Support @mentions in channels | Users expect to mention the agent by name |
| Add a greeting topic | First impressions matter — welcome users clearly |
| Handle "hi", "help", "what can you do?" | Most common first messages in Teams |

---

## Extending Microsoft 365 Copilot

Your Copilot Studio agent can become a **plugin** (extension) for Microsoft 365 Copilot.

### What This Means

- Users access your agent's capabilities from **within M365 Copilot**
- They can say "Ask the HR Agent about parental leave policy" in M365 Copilot
- M365 Copilot routes the request to your Studio agent
- Results appear in the M365 Copilot interface

### How to Set Up

1. Create your agent in Copilot Studio
2. Configure it for M365 Copilot publishing:
   - Set agent scope and permissions
   - Define plugin capabilities and descriptions
3. Submit for admin approval in the M365 admin center
4. Admins enable the plugin for users

### Key Differences from Standalone

| Aspect | Standalone Agent (Teams/Web) | M365 Copilot Extension |
|---|---|---|
| Access | Separate chat / web widget | Inside M365 Copilot |
| User experience | Dedicated conversation | Mixed with other Copilot capabilities |
| Routing | Direct — user talks to your agent | M365 Copilot routes based on intent |
| Context | Agent-specific context | M365 Copilot's full tenant context available |
| Knowledge | Your configured sources | Your sources + M365 Copilot Graph grounding |

### When to Build a Standalone Agent vs M365 Extension

| Scenario | Recommendation |
|---|---|
| Dedicated workflow (IT helpdesk, HR assistant) | **Standalone** — users need a focused experience |
| Domain-specific knowledge queries | **Extension** — surface answers where users already work |
| Both | Build as standalone, also publish as extension |

---

## SharePoint Integration

### As a Knowledge Source

- Add SharePoint site URLs as knowledge sources
- Agent searches documents, pages, and list items
- **Respects permissions** — users only see content they have access to
- Uses Microsoft Search index (already maintained by M365)

### As a Tool

Via the SharePoint connector:
- Get file content
- Create/update list items
- Search files
- Upload documents

### Tips

- Ensure your SharePoint sites are indexed by Microsoft Search
- Structure content with clear headings for better retrieval
- Use metadata (columns, tags) to improve search relevance
- Test with users who have different permission levels

---

## Outlook Integration

Via the Outlook connector, your agent can:
- **Send emails** on behalf of the user (with end-user auth)
- **Create calendar events** 
- **Read messages** (search, get specific emails)
- **Create tasks** in Outlook/To Do

**Common patterns:**
- Agent collects information → sends a summary email
- Agent schedules follow-up meetings after completing a workflow
- Agent checks for new emails and summarizes them

---

## Microsoft Graph

Microsoft Graph is the unified API for M365 data. Copilot Studio connects to Graph through:

### Graph Connectors (for Knowledge)
- Index external data (ServiceNow, Salesforce, Confluence) into Microsoft Search
- Use as enterprise knowledge source in Copilot Studio

### Graph API (via HTTP or Custom Connector)
- User profiles and organizational hierarchy
- Calendar and scheduling
- Files (OneDrive, SharePoint)
- Teams messages and channels
- Planner tasks

### Tenant Graph Grounding
- Available for M365 Copilot extensions
- Semantic search across the entire M365 tenant
- Respects user permissions throughout

---

## Multi-Channel Strategy

| Channel | Best For | Limitations |
|---|---|---|
| **Microsoft Teams** | Internal enterprise users | Requires Teams license |
| **Web (demo site)** | Quick testing, external users | Basic UI, no rich auth |
| **Web (custom embed)** | Customer-facing websites | Requires web development |
| **Mobile** | On-the-go access | Via Teams mobile app |
| **M365 Copilot** | Integrated AI assistant experience | Requires M365 Copilot license |

Most enterprise deployments start with **Teams** and optionally add **M365 Copilot extension** later.

---

## Next Steps

- **[Copilot SDK Bridge](copilot-sdk-bridge.md)** — Bridging Studio and code-first approaches
- **[Power Platform Integration](power-platform.md)** — Connectors, flows, and Dataverse
- **[Agent Design Patterns](../02-agents/agent-design-patterns.md)** — Architectural patterns

---

*Sources: [Microsoft Learn — Copilot Studio Channels](https://learn.microsoft.com/en-us/microsoft-copilot-studio/), [Microsoft Learn — Microsoft Graph](https://learn.microsoft.com/en-us/graph/overview)*
