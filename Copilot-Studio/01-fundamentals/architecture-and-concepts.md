# Architecture and Concepts

> **TL;DR:** Copilot Studio agents are built from five building blocks — instructions, topics, knowledge sources, tools, and triggers. The agent's orchestration mode (generative or classic) determines how it selects which building block to use for each user message.

---

## The Five Building Blocks of an Agent

Every Copilot Studio agent is composed of these primitives:

```
                    ┌─────────────┐
        User ──────│    Agent     │
                    │             │
                    │ Instructions│  ← "You are a helpful HR assistant..."
                    │   Topics    │  ← Conversation flows (dialog trees)
                    │  Knowledge  │  ← Data sources for grounding
                    │   Tools     │  ← Actions the agent can perform
                    │  Triggers   │  ← What starts the agent (message, event, schedule)
                    └─────────────┘
```

### 1. Instructions

Plain-language directives that shape the agent's behavior and personality.

- Define the agent's role, tone, and boundaries
- Example: "You are an HR assistant. Only answer questions about company policies. If unsure, direct users to HR."
- Up to 15,000 characters for Fabric Data Agent instructions; Studio agent instructions vary

### 2. Topics

**A topic is a portion of a conversational thread.** Each topic has:

- **Trigger:** What activates this topic (phrases, descriptions, or events)
- **Nodes:** The building blocks of the conversation flow

| Node Type | What It Does |
|---|---|
| **Message** | Send a message to the user |
| **Question** | Ask the user for information |
| **Adaptive Card** | Show an interactive card with buttons/inputs |
| **Condition** | Branch based on logic (if/else) |
| **Variable Management** | Set, parse, or clear variables |
| **Topic Management** | Redirect, transfer, or end the conversation |
| **Tool** | Call a connector, flow, API, or MCP tool |
| **Advanced** | Generative answers, HTTP requests, events |

**System topics** handle essential behaviors (greeting, escalation, conversation end) and come pre-built.
**Custom topics** are the ones you create for your specific use cases.

### 3. Knowledge Sources

Data that grounds the agent's responses in facts rather than hallucination.

| Source | Type | What It Does |
|---|---|---|
| **Public websites** | External | Searches via Bing, returns results from specified URLs |
| **Documents** | Internal | Searches uploaded files stored in Dataverse |
| **SharePoint** | Internal | Connects to SharePoint URLs via Graph Search |
| **Dataverse** | Internal | RAG over Dataverse tables |
| **Enterprise connectors** | Internal | Searches indexed data from Microsoft Search connectors |

### 4. Tools

Actions the agent can perform during a conversation:

| Tool Type | Description |
|---|---|
| **Prebuilt connector** | 1,100+ connections to Microsoft and third-party services |
| **Custom connector** | Your own API exposed as a Power Platform connector |
| **Agent flow** | Power Automate-style workflow created natively in Studio |
| **Prompt** | Single-turn model-based prompt with knowledge references |
| **REST API** | Direct connection to a REST endpoint |
| **MCP server** | Connect to a Model Context Protocol server for tools and resources |
| **Computer use** | GUI automation — click buttons, fill forms, navigate screens |

### 5. Triggers

What starts the agent or a specific topic:

| Trigger Type | Description |
|---|---|
| **User message** | Agent activated when user sends a message matching topic intent |
| **Event** | External event triggers a topic or flow |
| **Schedule** | Time-based trigger for autonomous agents |
| **Manual** | User explicitly invokes the agent |

---

## Orchestration Modes

The **orchestration mode** determines how the agent decides what to do with each user message. This is the single most important architectural decision.

### Generative Orchestration (Default, Recommended)

The agent uses AI to dynamically select the best combination of topics, tools, and knowledge for each user message.

```
User message
     │
     ▼
┌─────────────────────┐
│  Generative AI       │
│  Orchestrator        │
│                      │
│  Considers:          │
│  • Topic descriptions│
│  • Tool descriptions │
│  • Knowledge sources │
│  • Conversation ctx  │
│  • User intent       │
└────────┬────────────┘
         │
    ┌────┼────┬────────┐
    ▼    ▼    ▼        ▼
  Topic  Tool Knowledge  Fallback
  Flow   Call  Search    Response
```

**Key characteristics:**
- Agent reads descriptions of topics and tools to decide which to invoke
- Descriptions are critical — write clear, specific descriptions
- Max 128 tools per agent (recommend 25-30 for best performance)
- Max 25 knowledge sources searched (uploaded files don't count against this)
- More flexible and intelligent but less deterministic

### Classic Orchestration

The agent matches user messages against **trigger phrases** to select topics. It uses NLU pattern matching rather than generative AI.

```
User message
     │
     ▼
┌─────────────────────┐
│  NLU Engine          │
│  (Pattern Matching)  │
│                      │
│  Matches against:    │
│  • Trigger phrases   │
│  per topic           │
└────────┬────────────┘
         │
         ▼
  Best matching topic
  (or fallback)
```

**Key characteristics:**
- Each topic needs 5-10 trigger phrases
- More deterministic and predictable
- Lower knowledge source limits (4 URLs, 2 Dataverse sources, etc.)
- Supports custom data sources and Bing Custom Search
- Better when you need guaranteed routing for specific intents

### When to Use Which

| Scenario | Recommended Mode |
|---|---|
| Broad, unpredictable user questions | Generative |
| Many tools and knowledge sources | Generative |
| Need deterministic routing | Classic |
| Compliance-critical exact responses | Classic (with authored topics) |
| Starting a new agent | Generative (default) |
| Migrated PVA bot | Start with Classic, migrate gradually |

---

## Environments

Copilot Studio agents live in **Power Platform environments** — containers for data, apps, and agents.

| Environment Type | Purpose | Duration |
|---|---|---|
| **Default** | Auto-created on first sign-in | Permanent |
| **Production** | For deployed agents | Permanent |
| **Trial** | For testing | 30 days (then deleted) |
| **Developer** | For individual development | Permanent |
| **Sandbox** | For testing and training | Varies |

**Best practice:** Use a non-default production environment for agents you plan to deploy.

### Environment Strategy Examples

- **By team/department:** HR environment, IT environment, Sales environment
- **By lifecycle stage:** Dev → Staging → Production
- **By region:** EU environment, US environment (for data residency)

---

## Agent Conversation Flow (End to End)

Here's what happens when a user sends a message to a Copilot Studio agent:

```
1. User sends message via channel (Teams, web, etc.)
                    │
2. Agent receives message
                    │
3. Orchestration engine evaluates message
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
4a. Match to    4b. Search    4c. Invoke
    topic           knowledge     tool
        │           │           │
        ▼           ▼           ▼
5. Execute nodes / Generate response / Perform action
                    │
6. Agent composes final response
                    │
7. Response sent to user via channel
                    │
8. Conversation context updated
                    │
9. Wait for next user message (or end)
```

---

## Key Architectural Decisions

When designing a Copilot Studio agent, these are the decisions that matter most:

| Decision | Options | Impact |
|---|---|---|
| **Orchestration mode** | Generative vs Classic | Determines flexibility vs predictability |
| **Knowledge strategy** | SharePoint, Dataverse, documents, web | Determines answer quality and data freshness |
| **Tool architecture** | Connectors vs flows vs MCP vs REST | Determines integration complexity and maintainability |
| **Authentication model** | End-user credentials vs maker-provided | Determines data access scope and security |
| **Channel strategy** | Teams, web, multi-channel | Determines UX and reach |
| **Multi-agent vs single** | One agent vs parent/child agents | Determines scalability and separation of concerns |
| **Content moderation level** | Lowest → Highest | Tradeoff between answer volume and safety |

---

## Next Steps

- **[Topics and Conversations](../02-agents/topics-and-conversations.md)** — Deep dive into the topic system
- **[Knowledge Sources](../02-agents/knowledge-sources.md)** — Detailed guide to data grounding
- **[Tools and Actions](../02-agents/tools-and-actions.md)** — Complete tool type reference
- **[Getting Started Checklist](getting-started-checklist.md)** — Build your first agent

---

*Sources: [Microsoft Learn — Copilot Studio Overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/fundamentals-what-is-copilot-studio), [Microsoft Learn — Add Tools](https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-tools-custom-agent), [Microsoft Learn — Knowledge Sources](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio)*
