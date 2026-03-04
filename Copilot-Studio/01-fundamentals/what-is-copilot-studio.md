# What is Microsoft Copilot Studio?

> **TL;DR:** Copilot Studio is Microsoft's low-code platform for building AI agents that converse with users, access enterprise data, and take actions across Microsoft 365 and external systems. It evolved from Power Virtual Agents and now orchestrates GPT models, connectors, and workflows.

---

## The One-Paragraph Explanation

Microsoft Copilot Studio is a **graphical, low-code tool** for building AI agents and agent flows. You describe what you want in plain English, and the platform generates conversation paths you can refine visually. Agents connect to enterprise data through 1,100+ connectors, use GPT-powered reasoning to handle questions they weren't explicitly programmed for, and publish to Teams, websites, and mobile apps. It sits inside the Microsoft 365 security and identity stack, so enterprise governance comes built-in.

**Access it at:** [https://copilotstudio.microsoft.com](https://copilotstudio.microsoft.com)

---

## Evolution: Power Virtual Agents → Copilot Studio

| Era | Platform | What Changed |
|---|---|---|
| **2019–2023** | Power Virtual Agents (PVA) | Rule-based chatbot builder with topic/trigger phrase model, basic NLU |
| **2023** | Copilot Studio (rebrand) | Added GPT-based authoring, generative answers, plugin system |
| **2024–2025** | Copilot Studio (expanded) | Generative orchestration, MCP support, agent flows, computer use, multi-agent patterns |
| **2026** | Copilot Studio (current) | Create inputs from conversations (GA March 2026), richer UX layouts, Fabric Data Agent integration via MCP |

**Key point:** PVA's topic model, analytics, and channel publishing are still there. Copilot Studio adds GPT-based authoring, plugins, MCP, and deeper M365 alignment. It's not just a rebrand — it's a platform generation shift.

---

## What You Can Build

### Agent Types

| Agent Type | Description | Example |
|---|---|---|
| **Conversational agent** | Handles multi-turn dialog with users | IT helpdesk bot answering "How do I get VPN access?" |
| **Task agent** | Performs actions in response to triggers or requests | Sales copilot that creates CRM opportunities from conversation |
| **Knowledge agent** | Answers questions grounded in enterprise data | HR policy assistant pulling from SharePoint docs |
| **M365 Copilot extension** | Extends Microsoft 365 Copilot with custom capabilities | Custom domain agent surfaced inside M365 Copilot chat |
| **Autonomous agent** | Triggered by events, runs without user interaction | Monitors support queue and auto-categorizes tickets |

### Concrete Use Cases

- **Internal IT helpdesk:** Answers common questions, opens ServiceNow tickets via connector, follows up in Teams
- **HR policy assistant:** Interprets HR documents from SharePoint, answers "What's our parental leave?", escalates edge cases via Power Automate
- **Sales workflow copilot:** Looks up Dataverse/Dynamics data, generates meeting briefs, creates opportunities and sends follow-up emails
- **Customer-facing FAQ bot:** Handles product questions, order lookups via API, hands off to human agents when confidence is low
- **Data analyst:** Routes analytical questions to a Fabric Data Agent via MCP, returns KPIs and charts

---

## Core Platform Capabilities

### 1. Building Agents and Flows

- **Natural language authoring:** Describe what you want → Studio auto-generates topics and conversation paths → you refine visually
- **Topic and workflow design:** Branch dialog, set conditions, call actions, reuse components for multi-step conversations
- **Agent flows:** Power Automate-style automations created natively in Studio, usable as tools within agents
- **Multi-channel publishing:** Teams, websites, mobile apps, Facebook, any Azure Bot Service channel

### 2. Data Access and Tools

- **1,100+ prebuilt connectors:** Dataverse, SharePoint, Dynamics, Salesforce, ServiceNow, custom APIs
- **Tool types:** Connectors, agent flows, prompts, REST APIs, MCP servers, computer use (GUI automation)
- **Controlled grounding:** You choose exactly which data sources the agent can access — no uncontrolled external content

### 3. Knowledge and AI

- **Generative answers:** Agent automatically finds and presents information from configured knowledge sources
- **Knowledge sources:** Public websites, uploaded documents, SharePoint, Dataverse, enterprise connectors
- **Generative orchestration:** AI dynamically selects the best combination of topics, tools, and knowledge
- **Web search:** Optional Bing-powered grounding for real-time public information
- **General knowledge:** Optional access to the LLM's foundational training knowledge

### 4. Microsoft 365 Integration

- **Extend M365 Copilot:** Build agents in Studio, publish them as extensions to Microsoft 365 Copilot
- **Enterprise governance:** Same security, compliance, and identity stack as M365
- **Admin controls:** Environment separation, role-based access, centralized management

### 5. Advanced Scenarios

- **Multi-agent orchestration:** Parent agents route to child agents, each with their own tools and orchestration
- **MCP integration:** Connect to Model Context Protocol servers (including Fabric Data Agents) as tools
- **Computer use:** Agents can interact with GUI applications — click buttons, fill forms, navigate menus

---

## Mental Model: How Copilot Studio Fits the Microsoft AI Landscape

```
┌─────────────────────────────────────────────────────────┐
│                  Microsoft 365 Copilot                    │
│              (End-user AI assistant in M365)              │
│                         ▲                                │
│                         │ Extends                        │
├─────────────────────────┼───────────────────────────────┤
│              Copilot Studio                              │
│         (Low-code agent builder)                         │
│    ┌──────────┬──────────┬──────────┐                   │
│    │  Topics  │Knowledge │  Tools   │                   │
│    │  & Flows │ Sources  │& Actions │                   │
│    └────┬─────┴────┬─────┴────┬─────┘                   │
│         │          │          │                          │
│    ┌────▼────┐ ┌───▼────┐ ┌──▼─────────┐               │
│    │Generative│ │SharePt │ │Connectors  │               │
│    │  Orch.  │ │Dataverse│ │Power Auto  │               │
│    │Classic  │ │Websites │ │REST APIs   │               │
│    │  Orch.  │ │Documents│ │MCP Servers │               │
│    └─────────┘ └────────┘ │Agent Flows │               │
│                           │Computer Use│               │
│                           └────────────┘               │
├─────────────────────────────────────────────────────────┤
│  Power Platform  │  Azure AI  │  Fabric  │  Dynamics   │
│  (Dataverse,     │  (Models,  │  (Data   │  (CRM/ERP  │
│   Automate)      │   Search)  │  Agents) │   data)     │
└─────────────────────────────────────────────────────────┘
```

---

## Strengths

| Strength | Why It Matters |
|---|---|
| **Low-code but powerful** | Business users create agents via natural language; devs plug in APIs and governance on top |
| **Deep M365 integration** | Native identity, permissions, and data access — no separate auth systems |
| **Rich connector ecosystem** | 1,100+ connectors + Power Automate for workflow-heavy agents touching many systems |
| **Centralized management** | Manage multiple agents, data sources, and workflows from one place |
| **Enterprise-grade security** | Built on Microsoft's compliance, identity, and governance stack |
| **Generative + structured** | Combine GPT reasoning with deterministic topic flows for predictable + flexible behavior |

---

## When Copilot Studio is the Right Tool

| Scenario | Fit | Why |
|---|---|---|
| Internal M365-centric workflows | **Strong** | Native identity, Teams/web channels, connectors to SharePoint, Dataverse |
| Low-code citizen developer bots | **Strong** | Natural language topic creation, visual editor, low-code automations |
| Heavy multi-system orchestration | **Good (with care)** | Works via connectors/Power Automate, but respect skill limits and complexity |
| High-stakes precision tasks | **Use cautiously** | Hallucination risks need strong guardrails and human-in-the-loop |
| Very large document agents | **Mixed** | Context window and plugin constraints can degrade retrieval quality |
| Non-Microsoft tech stacks | **Consider hybrid** | Possible via APIs, but less natural than a bespoke LLM stack if M365 isn't core |

---

## Next Steps

- **[Architecture and Concepts](architecture-and-concepts.md)** — How agents, topics, knowledge, and tools fit together
- **[Getting Started Checklist](getting-started-checklist.md)** — Build your first agent
- **[Copilot Studio vs Copilot SDK](copilot-studio-vs-copilot-sdk.md)** — When to use which approach

---

*Sources: [Microsoft Learn — Copilot Studio Overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/fundamentals-what-is-copilot-studio), [Argano](https://argano.com/insights/articles/dont-call-it-a-rebrand-power-virtual-agents-copilot-studio.html), [CloudThat](https://www.cloudthat.com/resources/blog/migration-from-power-virtual-agents-to-copilot-studio-what-you-need-to-know/)*
