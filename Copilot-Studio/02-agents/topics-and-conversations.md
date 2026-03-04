# Topics and Conversations

> **TL;DR:** Topics are the building blocks of conversation in Copilot Studio. Each topic has a trigger (what activates it) and a set of nodes (what happens). In generative orchestration mode, the AI selects topics based on descriptions; in classic mode, it matches trigger phrases.

---

## What Is a Topic?

A **topic** is a discrete unit of conversation. Think of it as a mini-dialog that handles a specific user intent or scenario.

Every topic has:
1. **A trigger** — what activates this topic
2. **One or more nodes** — the steps that execute when the topic is active

```
Trigger (user says "reset my password")
   │
   ▼
Node 1: Message ("I can help you reset your password")
   │
   ▼
Node 2: Question ("Which system? A) Email  B) VPN  C) Laptop")
   │
   ▼
Node 3: Condition (branch based on answer)
   │
   ├── Email → Node 4a: Tool (call password reset API)
   ├── VPN   → Node 4b: Message ("Contact IT Security at x1234")
   └── Laptop → Node 4c: Topic Redirect (→ Laptop Reset topic)
   │
   ▼
Node 5: Message ("Is there anything else I can help with?")
```

---

## Topic Types

### Custom Topics (You Create These)

| Topic Type | Use For |
|---|---|
| **Simple Q&A** | Direct answer with optional variables |
| **Multi-step flow** | Structured process with questions, conditions, and actions |
| **Tool-calling** | Agent invokes a tool and presents results |
| **Redirect hub** | Routes to other topics based on user intent |

### System Topics (Pre-built, Customizable)

| System Topic | Purpose |
|---|---|
| **Greeting** | Handles initial user engagement |
| **End of Conversation** | Wraps up and confirms resolution |
| **Escalate** | Transfers to a human agent |
| **Fallback** | Handles unrecognized intents |
| **Multiple Topics Matched** | Disambiguates when multiple topics match |
| **On Error** | Handles runtime errors gracefully |
| **Reset Conversation** | Clears context and starts fresh |
| **Conversational Boosting** | Generates answers from knowledge (generative mode) |

> **Best practice:** Customize system topics to match your brand voice and process. Don't leave them as default — the greeting and fallback topics are your agent's first and last impressions.

---

## Triggers

### Generative Orchestration Triggers

In generative mode, topics are triggered based on their **name** and **description**:

- The AI reads the topic name and description
- It decides whether this topic is relevant to the user's current message
- **Write clear, specific descriptions** — they are the AI's primary routing signal

**Good description:**
> "Handles requests to reset a user's password for email, VPN, or laptop systems. Guides the user through verification and initiates the reset process."

**Bad description:**
> "Password stuff"

### Classic Orchestration Triggers

In classic mode, topics use **trigger phrases** — example sentences that represent the user's intent:

```
Trigger phrases for "Password Reset" topic:
- "I need to reset my password"
- "Forgot my password"
- "Can't log in"
- "Password expired"
- "How do I change my password?"
- "Reset password"
```

**Guideline:** 5-10 trigger phrases per topic, covering natural variations.

---

## Node Types Reference

### Message Node

Sends a message to the user. Supports:
- Plain text
- Rich text with formatting
- Variable interpolation: `"Hi {User.Name}, here's your answer"`
- Images (via URL)
- Quick replies (suggested actions)

### Question Node

Asks the user for input and stores the response in a variable.

| Response Type | Behavior |
|---|---|
| **Free text** | Accepts any text input |
| **Multiple choice** | Presents options (A, B, C) |
| **Boolean** | Yes/No |
| **Number** | Validates numeric input |
| **Date/Time** | Parses date/time input |
| **File** | File upload |
| **Email** | Validates email format |
| **Custom entity** | Matches against a defined entity list |

### Adaptive Card Node

Displays an interactive card (Microsoft Adaptive Cards format) with:
- Text, images, buttons
- Input fields (text, dropdown, date picker)
- Actions (submit, open URL)

Useful for complex forms, dashboards, and structured data display.

### Condition Node

Branches the conversation based on logic:

```
Condition: Is {UserRole} = "Admin"?
├── Yes → [admin-specific flow]
└── No  → [standard flow]
```

Supports:
- Variable comparisons (equals, not equals, greater than, contains)
- Multi-condition logic (AND, OR)
- Nested conditions

### Variable Management Node

- **Set variable:** Assign a value to a conversation variable
- **Parse value:** Extract structured data from text using AI
- **Clear variable:** Reset a variable to null

### Topic Management Node

- **Redirect to topic:** Jump to another topic (with or without returning)
- **End conversation:** Close the conversation
- **Transfer to agent:** Hand off to a human agent
- **Go to step:** Jump to a specific node within the current topic

### Tool Node

Invokes a tool (connector action, flow, API, MCP tool) within the topic flow.

- Configure input mapping from conversation variables
- Handle success and failure paths
- Store output in variables for use in later nodes

### Advanced Nodes

| Node | Purpose |
|---|---|
| **Generative answers** | Let AI generate a response using knowledge sources |
| **HTTP request** | Make a direct HTTP call (GET, POST, etc.) |
| **Send event** | Fire a custom event to the client channel |
| **Set speaker** | Switch the conversation persona |

---

## Topic Authoring: Visual vs YAML

### Visual Canvas (Default)

The drag-and-drop canvas where you add and connect nodes visually. Best for:
- Business users and citizen developers
- Quick prototyping
- Simple to moderate complexity

### YAML Code Editor

A text-based editor for topics. Better for:
- Bulk editing
- Copy/paste between topics
- Version control (export as YAML)
- Complex variable logic

You can switch between visual and YAML at any time — they're interchangeable representations.

**Example YAML:**
```yaml
kind: AdaptiveDialog
beginDialog:
  kind: OnRecognizedIntent
  id: main
  intent:
    triggerQueries:
      - "Reset my password"
      - "Forgot password"
  actions:
    - kind: SendActivity
      id: greeting
      activity:
        text: "I can help you reset your password."
    - kind: Question
      id: whichSystem
      variable: init.system
      prompt: "Which system needs the reset?"
      entity:
        kind: EmbeddedEntity
        definition:
          values:
            - id: email
              displayName: Email
            - id: vpn
              displayName: VPN
            - id: laptop
              displayName: Laptop
```

---

## Conversation Design Best Practices

### Structure

| Practice | Why |
|---|---|
| **Keep topics focused** | One intent per topic. If it's doing too much, split it. |
| **Use descriptive names** | "Password Reset Request" not "Topic 47" |
| **Write thorough descriptions** | Generative orchestration reads these to route |
| **Limit topic depth** | If a flow exceeds ~10 nodes deep, consider splitting into multiple topics |
| **Test with real phrases** | Users won't type what you expect — test with natural variations |

### Conversation UX

| Practice | Why |
|---|---|
| **Confirm critical actions** | Always confirm before creating, updating, or deleting anything |
| **Provide escape hatches** | Let users say "cancel" or "start over" at any point |
| **Show progress** | For multi-step flows, tell users where they are ("Step 2 of 4") |
| **Handle errors gracefully** | If a tool fails, tell the user and offer alternatives |
| **Close the loop** | End every completed interaction with "Is there anything else?" |

### Generative vs Authored

| When To... | Use Generative Answers | Use Authored Topic |
|---|---|---|
| Answer from knowledge base | Yes | Only if specific format required |
| Execute a specific workflow | Orchestration can trigger it | Yes, if steps must be exact |
| Collect structured data | Sometimes | Yes (question nodes are more reliable) |
| Handle error conditions | For informational responses | Yes (need deterministic branching) |

---

## Testing Topics

1. **Test chat** — Built into Studio, bottom-left corner
2. **Track between topics** — Toggle "Track" to see which topic/node fires for each message
3. **Variable inspector** — See current variable values during conversation
4. **Reset** — Clear conversation state to test from scratch
5. **Edge cases to test:**
   - Typos and misspellings
   - Off-topic messages mid-flow
   - Cancellation mid-process
   - Empty or invalid inputs
   - Rapid re-asking the same question

---

## Next Steps

- **[Knowledge Sources](knowledge-sources.md)** — Ground your topics in data
- **[Tools and Actions](tools-and-actions.md)** — Call tools from within topics
- **[Agent Design Patterns](agent-design-patterns.md)** — Proven structural patterns

---

*Sources: [Microsoft Learn — Create and Edit Topics](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-create-edit-topics), [Microsoft Learn — Add Tools](https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-tools-custom-agent)*
