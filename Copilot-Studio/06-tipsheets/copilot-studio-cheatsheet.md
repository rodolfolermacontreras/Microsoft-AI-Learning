# Copilot Studio Cheatsheet

> One-page quick reference. Print it, pin it, bookmark it.

---

## Access

| What | Where |
|---|---|
| Copilot Studio | [copilotstudio.microsoft.com](https://copilotstudio.microsoft.com) |
| Power Platform Admin | [admin.powerplatform.com](https://admin.powerplatform.com) |
| M365 Admin Center | [admin.microsoft.com](https://admin.microsoft.com) |

---

## Agent Building Blocks

| Block | What It Is | You Configure |
|---|---|---|
| **Instructions** | Agent personality and rules | Plain text, up to 15K chars |
| **Topics** | Conversation flows | Trigger + nodes (visual or YAML) |
| **Knowledge** | Data for grounding answers | Sources: SharePoint, docs, Dataverse, web, connectors |
| **Tools** | Actions the agent performs | Connectors, flows, prompts, REST, MCP, computer use |
| **Triggers** | What starts the agent/topic | Message, event, schedule, manual |

---

## Orchestration Modes

| Mode | Routing Mechanism | Best For |
|---|---|---|
| **Generative** (default) | AI reads descriptions, selects best topic/tool | Broad, unpredictable questions |
| **Classic** | NLU matches trigger phrases | Deterministic routing |

---

## Node Types (Topic Building)

| Node | What It Does |
|---|---|
| Message | Send text/card to user |
| Question | Ask for input (free text, choice, boolean, etc.) |
| Adaptive Card | Interactive card with buttons/inputs |
| Condition | If/else branching |
| Variable | Set, parse, or clear variables |
| Topic Management | Redirect, end, transfer, go-to |
| Tool | Call connector, flow, API, or MCP |
| Generative Answers | AI-generated response from knowledge |
| HTTP Request | Direct HTTP call |

---

## Tool Types

| Type | Use For |
|---|---|
| Prebuilt connector | SharePoint, Teams, Outlook, ServiceNow, etc. |
| Custom connector | Your APIs in Power Platform format |
| Agent flow | Multi-step automation (native in Studio) |
| Prompt | AI text processing (summarize, classify, extract) |
| REST API | Direct HTTP endpoint call |
| MCP server | Fabric Data Agents, custom MCP tools |
| Computer use | GUI automation (last resort) |

---

## Knowledge Sources

| Source | Auth | Notes |
|---|---|---|
| Public websites | None | Bing-powered, up to 25 (gen. orch.) |
| Uploaded documents | Maker | Stored in Dataverse, no source limit |
| SharePoint | User | Respects permissions, uses M365 Search |
| Dataverse | User | Security roles apply |
| Enterprise connectors | User | Via Microsoft Graph connectors |

---

## Key Limits

| Limit | Value |
|---|---|
| Tools per agent | 128 max (25-30 recommended) |
| Knowledge sources (gen.) | 25 total (files excluded) |
| Knowledge sources (classic) | 4 URLs, 2 Dataverse, 4 SharePoint |
| Trigger phrases (classic) | 5-10 per topic |
| Environments | Follow your dev/staging/prod strategy |

---

## Authentication Patterns

| Pattern | When |
|---|---|
| End-user credentials | User-specific data (their emails, their records) |
| Maker-provided | Shared data (knowledge bases, common APIs) |
| API key | Simple external APIs |
| No auth | Public endpoints |

---

## Content Moderation Levels

Lowest ← → Highest

More answers ← → More safety

Default: Low (balance of coverage and safety)

---

## Publishing Channels

| Channel | Setup Location |
|---|---|
| Demo website | Channels → Demo website (copy URL) |
| Microsoft Teams | Channels → Teams (configure + submit) |
| Web embed | Channels → Custom website (copy embed code) |
| M365 Copilot | Channels → M365 Copilot (admin approval) |
| Mobile | Via Teams mobile app |

---

## Quick Keyboard Shortcuts (Studio Web App)

| Action | Shortcut |
|---|---|
| Test agent | Click test icon (bottom-left) |
| Toggle tracking | In test pane, toggle "Track" |
| Switch visual/YAML | Code editor toggle in topic editor |
| Save | Ctrl+S (in topic editor) |

---

## Common Patterns (One-Liner)

| Pattern | Description |
|---|---|
| Knowledge Agent | Instructions + knowledge sources → Q&A |
| Task Agent | Knowledge + tools → Q&A + actions |
| Guided Workflow | Authored topics with deterministic flows |
| Multi-Agent | Parent routes to specialist child agents |
| Autonomous | Event/schedule trigger, no user interaction |
| Hybrid | Studio front-end + SDK/API back-end |

---

## Troubleshooting Quick Hits

| Symptom | Check |
|---|---|
| "I don't know" answers | Knowledge source indexed? Content moderation too high? |
| Wrong tool called | Tool descriptions clear and specific? |
| Slow responses | Too many tools/sources? External API latency? |
| Auth errors | Correct auth pattern? User has permissions? |
| Topic not triggered | Generative: check description. Classic: check trigger phrases. |

---

*Keep this handy. For full details, see the relevant section in this folder.*
