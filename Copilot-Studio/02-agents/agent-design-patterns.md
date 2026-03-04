# Agent Design Patterns

> **TL;DR:** Proven architectural patterns for building Copilot Studio agents. Start with the simplest pattern that meets your requirements, and evolve toward multi-agent or hybrid designs only when complexity demands it.

---

## Pattern 1: Single Knowledge Agent

**The simplest useful agent.** Answers questions grounded in a curated set of knowledge sources with no tool usage.

```
User ──▶ Agent ──▶ Knowledge Sources ──▶ Grounded Answer
```

**When to use:**
- FAQ bots, policy assistants, documentation helpers
- The agent only needs to answer questions, not take actions
- Knowledge sources are well-structured and up to date

**Setup:**
1. Create agent with clear instructions defining scope and tone
2. Add knowledge sources (SharePoint, documents, websites)
3. Use generative orchestration — let the AI find answers
4. Add a fallback topic for out-of-scope questions

**Example:** HR Policy Bot — answers questions about PTO, benefits, and company policies from SharePoint-hosted HR documents.

**Gotchas:**
- Knowledge quality determines answer quality — garbage in, garbage out
- Long documents may exceed effective context — break into smaller, focused files
- Set content moderation to match your risk tolerance

---

## Pattern 2: Task Agent (Knowledge + Tools)

Answers questions AND takes actions. The most common production pattern.

```
User ──▶ Agent ──┬──▶ Knowledge Sources ──▶ Answer
                 └──▶ Tools ──▶ Action + Confirmation
```

**When to use:**
- Agents that need to look up data AND create records, send emails, or trigger workflows
- IT helpdesk (answer questions + create tickets), sales assistant (answer questions + update CRM)

**Setup:**
1. Start with Pattern 1 (knowledge agent)
2. Add tools for each action the agent should perform
3. Write excellent tool descriptions (generative orchestration reads these)
4. Configure authentication (end-user vs maker-provided)
5. Add confirmation steps for destructive actions

**Example:** IT Helpdesk — answers common questions from a knowledge base, creates ServiceNow tickets via connector, sends confirmation in Teams.

**Gotchas:**
- Keep tool count reasonable (25-30 for best AI routing)
- Test tool selection — does the agent invoke the right tool at the right time?
- Always confirm before destructive actions (creating tickets, sending emails)

---

## Pattern 3: Guided Workflow Agent

Uses authored topics with deterministic flows for specific processes, combined with generative answers for everything else.

```
User ──▶ Agent ──┬──▶ Authored Topic (deterministic flow)
                 │    └── Question → Condition → Action → Message
                 └──▶ Generative Answers (for everything else)
```

**When to use:**
- Processes with specific steps that must happen in order
- Compliance-sensitive workflows where you can't rely on AI discretion
- Multi-step data collection (forms, applications, requests)

**Setup:**
1. Create authored topics for each structured workflow
2. Use question nodes to collect required data
3. Use condition nodes for branching logic
4. Use tool nodes for actions at specific steps
5. Let generative orchestration handle non-workflow questions

**Example:** Expense Report Submission — collect amount, category, receipt, approver via structured questions; validate against policy rules; submit via Power Automate flow.

**Gotchas:**
- Don't over-author — if generative orchestration handles it well, don't manually create a topic
- Keep deterministic flows for high-stakes processes; use generative for the long tail

---

## Pattern 4: Multi-Agent (Parent + Specialists)

A parent agent routes requests to specialized child agents, each with their own knowledge, tools, and instructions.

```
User ──▶ Parent Agent ──┬──▶ IT Specialist Agent
                        ├──▶ HR Specialist Agent
                        ├──▶ Facilities Agent
                        └──▶ (fallback) General Knowledge
```

**When to use:**
- Large organizations with many domains
- Each domain needs different knowledge sources, tools, and permissions
- You want separation of concerns for maintainability
- Individual agents approach the tool/knowledge limits

**Setup:**
1. Create specialist agents, each focused on one domain
2. Create a parent agent that acts as a router
3. Add specialist agents as tools in the parent agent
4. Write clear descriptions so the parent routes accurately
5. Configure permissions — parent needs access to invoke children

**Example:** Enterprise Copilot — parent routes to IT Agent (ServiceNow + IT docs), HR Agent (Workday + HR policies), Facilities Agent (room booking + office info).

**Gotchas:**
- Adds latency (parent → child → back)
- Conversation context may not fully transfer between agents
- Test routing accuracy — misroutes are confusing for users
- Keep the number of child agents manageable (under 10)

---

## Pattern 5: Event-Driven Autonomous Agent

Triggers on events or schedules rather than user messages. Runs without user interaction.

```
Event/Schedule ──▶ Agent ──▶ Process Data ──▶ Take Action ──▶ Notify
```

**When to use:**
- Monitoring and alerting (support queue, system health)
- Scheduled data processing or report generation
- Workflow triggers based on external events

**Setup:**
1. Create an agent with event or schedule triggers
2. Define the processing logic (topics + tools)
3. Add notification actions (Teams message, email, ticket creation)
4. Test with simulated events before going live

**Example:** Support Queue Monitor — triggers every 15 minutes, checks unassigned tickets, auto-categorizes based on content, assigns to appropriate team, sends summary to manager.

**Gotchas:**
- No user in the loop — errors are silent unless you add error notifications
- Monitor execution logs actively in early deployment
- Set clear boundaries on what the agent can do autonomously

---

## Pattern 6: Hybrid (Studio + Code)

Copilot Studio for the conversational front-end; custom code (SDK, Azure Functions, APIs) for complex backend logic.

```
User ──▶ Copilot Studio Agent ──▶ REST API / MCP Server
                                       │
                                  Custom Backend
                                  (Azure Function,
                                   FastAPI, etc.)
```

**When to use:**
- Need complex business logic that's hard to express in flows
- Require integrations not available as connectors
- Want Studio's UX and governance + code's flexibility

**Setup:**
1. Build your backend as a REST API or MCP server
2. In Copilot Studio, add the backend as a REST API tool or MCP server tool
3. Define clear input/output schemas
4. Studio handles conversation; backend handles logic

**Example:** Data Analytics Agent — Studio handles conversation and user queries, MCP server (Fabric Data Agent) runs SQL/DAX queries, results formatted by Studio.

**Gotchas:**
- Two systems to maintain and monitor
- Latency from external API calls
- Authentication needs careful planning (pass-through vs service-to-service)

---

## Pattern Selection Guide

| Your Situation | Start With | Evolve To |
|---|---|---|
| Simple FAQ / knowledge lookup | Pattern 1 | Pattern 2 (add tools later) |
| Help desk with ticket creation | Pattern 2 | Pattern 4 (if domains grow) |
| Compliance-critical form processing | Pattern 3 | Pattern 3 + 2 (add general Q&A) |
| Multi-department enterprise bot | Pattern 4 | Pattern 4 + 6 (add custom backends) |
| Background monitoring / automation | Pattern 5 | Pattern 5 + 6 (add complex processing) |
| Custom backend integration | Pattern 6 | Pattern 6 + 4 (scale with multi-agent) |

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Instead |
|---|---|---|
| **One giant agent** | Too many tools (128 limit), slow routing, confused responses | Split into multi-agent (Pattern 4) |
| **Over-authoring topics** | High maintenance, doesn't leverage AI's generative capabilities | Let generative orchestration handle the long tail |
| **No fallback** | Users get stuck or get wrong answers with no escape | Always have an escalation path and out-of-scope handling |
| **No tool confirmation** | Agent takes irreversible actions without user agreement | Add confirmation for any create/update/delete |
| **Mixing concerns** | One agent handles IT, HR, Finance, Facilities, etc. | Separate by domain (Pattern 4) |
| **Ignoring analytics** | No idea if the agent is helping or hurting | Review analytics weekly, iterate on low-performing topics |

---

## Next Steps

- **[Topics and Conversations](topics-and-conversations.md)** — Deep dive into topic design
- **[Tools and Actions](tools-and-actions.md)** — Complete tool reference
- **[MCP and Fabric](../03-integrations/mcp-and-fabric.md)** — Connecting to external AI resources

---

*Pattern names and structures are based on common Microsoft documentation patterns and real-world Copilot Studio deployments.*
