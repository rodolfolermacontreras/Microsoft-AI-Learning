# Third-Party Agents

> Using external AI providers like Anthropic Claude and OpenAI Codex alongside GitHub Copilot.

---

## What Third-Party Agents Are

VS Code supports agents from external AI providers. These agents run using their
own infrastructure and models but integrate into VS Code's unified session management
and Chat view.

Currently supported providers:
- **Anthropic** (Claude) -- local and cloud agent modes
- **OpenAI** (Codex) -- background and cloud agent modes

---

## Why Use Third-Party Agents

| Reason | Example |
|--------|---------|
| **Different model strengths** | Claude excels at certain reasoning tasks |
| **Model diversity** | Compare approaches across providers |
| **Specialized capabilities** | Codex for batch code generation |
| **Preference** | Use your preferred provider within VS Code |

---

## Enabling Third-Party Agents

1. Go to your GitHub Copilot account settings
2. Enable support for third-party agents in the cloud
3. Restart VS Code
4. Third-party agents appear in the agent type dropdown

You do **not** need to install the provider's VS Code extension separately.

---

## Using Third-Party Agents

### Starting a Session

```
Chat view  ->  New Session (+)  ->  Select agent type  ->  Choose provider
```

### Handoff

You can hand off sessions between any agent types:

```
Local (Copilot)  ->  Background (Codex)  ->  Cloud (Claude)
```

The full conversation history carries over with each handoff.

---

## Session Management

Third-party agent sessions appear alongside Copilot sessions in the unified
sessions list. You can:
- Track progress across all providers in one view
- Switch between sessions
- Review file changes
- Archive or delete sessions

---

## Considerations

| Aspect | Detail |
|--------|--------|
| **Billing** | Third-party usage may count against your Copilot premium requests |
| **Tool access** | Varies by provider -- check which tools the third-party agent supports |
| **MCP servers** | Cloud third-party agents may have limited MCP access |
| **Privacy** | Data flows through the third-party provider's infrastructure |

---

## Next Steps

- [Local Agents](local-agents.md) -- interactive Copilot agent sessions
- [Cloud Agents](cloud-agents.md) -- PR-based collaboration
- [Subagents Guide](../03-subagents/subagents-guide.md) -- delegation patterns
