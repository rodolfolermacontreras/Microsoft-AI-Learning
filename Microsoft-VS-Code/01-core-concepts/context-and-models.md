# Context Window and Language Models

> How to choose models, manage context, and optimize for better agent performance.

---

## The Context Window

The context window is the total amount of information a model can process in a single
request. It includes **everything**: system prompt, custom instructions, conversation
history, file contents, tool outputs, and your current message.

When the context window fills up, VS Code automatically **summarizes** older parts of
the conversation to make room. Important details from early in a long conversation
may be compressed or lost.

### Manual Compaction

Type `/compact` in chat to manually trigger compaction. Optionally add instructions:

```
/compact focus on the API design decisions
```

### Context Management Best Practices

| Practice | Why |
|----------|-----|
| Start new sessions for new tasks | Avoids context pollution from unrelated work |
| Be selective with references | Adding your entire codebase is not always helpful |
| Use `#file` for specific files | Pinpoints exactly what the model should see |
| Put persistent rules in instructions | Instructions are included in every request |
| Use subagents for research | Isolates exploratory work from your main context |
| Delete irrelevant history | Remove past Q&A that no longer matters |

---

## Language Models

VS Code supports multiple models. Each has different strengths.

### Model Selection Strategy

| Task Type | Best Model Characteristics | Example Use |
|-----------|--------------------------|-------------|
| Quick completions | Fast, small context | Boilerplate, renaming |
| Complex reasoning | Large context, strong reasoning | Architecture, debugging |
| Code generation | Balanced speed and quality | Feature implementation |
| Planning | Strong reasoning, read-only | Plan mode research |
| Subagent tasks | Cost-effective, focused | Isolated research |

### Changing Models

1. **Chat**: Use the model picker dropdown in the Chat view
2. **Inline chat**: Configure via `inlineChat.defaultModel` setting
3. **Inline suggestions**: Chat menu > Configure Inline Suggestions > Change Completions Model
4. **Per-agent**: Set `model` in custom agent `.agent.md` frontmatter
5. **Per-prompt**: Set `model` in prompt file `.prompt.md` frontmatter

### Auto Model Selection

Select **Auto** from the model picker. VS Code automatically selects the optimal model
based on:
- Current task complexity
- Model availability and rate limits
- Degraded performance detection

Auto applies a variable request multiplier (cost discount) for paid users.

### Bring Your Own Key (BYOK)

For models not available as built-in:

1. Open model picker > Manage Models
2. Select Add Models
3. Choose a provider (OpenAI, Anthropic, Ollama, etc.)
4. Enter API key or endpoint URL
5. Select/configure the model

Built-in providers: OpenAI, Anthropic, Google, Azure OpenAI, Ollama (local), and custom
OpenAI-compatible endpoints.

**Requirements for agent mode**: The model must support **tool calling**. Models without
tool calling only work in Ask mode.

---

## Context Engineering

The quality of AI responses depends on the quality of context you provide.

### Automatic Context

VS Code gathers these automatically:
- Current file and selection
- Workspace index (semantic search)
- Git state (branch, changes)
- Conversation history
- Compiler/linter errors

### Explicit Context References

Add context manually with `#` references:

| Reference | What It Adds |
|-----------|-------------|
| `#file:path/to/file.ts` | Specific file contents |
| `#folder:src/utils` | Folder contents |
| `#symbol:MyClass` | Symbol definitions |
| `#codebase` | Semantic codebase search |
| `#web` | Web search results |
| `#fetch <url>` | Content from a URL |
| `#githubRepo owner/repo` | GitHub repository context |
| `#problems` | Current compiler/lint errors |
| `#changes` | Git changes |
| `#selection` | Current editor selection |
| `#terminalSelection` | Terminal output |
| `#testFailure` | Test failure details |

### Context Priority for Complex Tasks

```
1. Reference specific files      -- the model sees exactly what it needs
2. Use custom instructions       -- persistent rules without repetition
3. Start fresh sessions          -- clean context for new tasks
4. Use subagents for research    -- isolate exploration from main context
5. Run parallel sessions         -- separate contexts for independent work
```

---

## Workspace Indexing

VS Code automatically indexes your project for semantic search, language intelligence,
and cross-file reasoning. For large repositories, remote indexing provides fast results
across your repo and related repos on GitHub.

### Multi-Root Workspaces

For monorepos or multi-service projects, use multi-root workspaces to give the AI
clear boundaries and focused context per service.

---

## Next Steps

- [Local Agents](../02-agent-types/local-agents.md) -- interactive agent sessions
- [Custom Agents](../04-customization/custom-agents.md) -- define model preferences per agent
- [Subagents Guide](../03-subagents/subagents-guide.md) -- context isolation via subagents
