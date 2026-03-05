# Agent Hooks

> Execute custom commands at agent lifecycle points for automation and policy enforcement.

---

## What Hooks Are

Hooks are external shell commands that run at specific points during agent sessions.
They provide **deterministic, code-driven automation** -- unlike instructions that guide
behavior, hooks guarantee execution.

---

## Hook Events

| Event | When It Fires | Common Use |
|-------|---------------|-----------|
| `SessionStart` | First prompt of a session | Initialize resources, inject context |
| `UserPromptSubmit` | User sends a message | Audit requests, add context |
| `PreToolUse` | Before a tool is invoked | Block dangerous commands, modify input |
| `PostToolUse` | After a tool completes | Run formatters, log results |
| `PreCompact` | Before context compaction | Export state before truncation |
| `SubagentStart` | Subagent is spawned | Track subagent usage |
| `SubagentStop` | Subagent completes | Aggregate results, cleanup |
| `Stop` | Agent session ends | Generate reports, enforce final checks |

---

## Configuration

Hook files are JSON stored in:

| Location | Scope |
|----------|-------|
| `.github/hooks/*.json` | Workspace (shared with team) |
| `.claude/settings.json` | Workspace (Claude Code compatible) |
| `~/.claude/settings.json` | User (personal across workspaces) |

Customize with `chat.hookFilesLocations` setting.

### Hook Format

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "type": "command",
        "command": "python3 ./scripts/validate-tool.py",
        "timeout": 15
      }
    ],
    "PostToolUse": [
      {
        "type": "command",
        "command": "npx prettier --write \"$TOOL_INPUT_FILE_PATH\""
      }
    ]
  }
}
```

---

## Hook Input/Output

Hooks receive JSON on **stdin** and return JSON on **stdout**.

### Exit Codes

| Code | Effect |
|------|--------|
| 0 | Success -- parse stdout as JSON |
| 2 | Block -- stop processing, show error to model |
| Other | Warning -- show to user, continue |

### PreToolUse Output

Control tool execution:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Destructive command blocked",
    "updatedInput": {},
    "additionalContext": "..."
  }
}
```

Permission decisions: `allow` > `ask` > `deny` (most restrictive wins).

### Stop Hook Output

Prevent the agent from stopping:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "Stop",
    "decision": "block",
    "reason": "Run the test suite before finishing"
  }
}
```

**Warning**: Always check `stop_hook_active` to prevent infinite loops.

---

## OS-Specific Commands

```json
{
  "type": "command",
  "command": "./scripts/format.sh",
  "windows": "powershell -File scripts\\format.ps1",
  "linux": "./scripts/format-linux.sh",
  "osx": "./scripts/format-mac.sh"
}
```

---

## Practical Examples

### Block Dangerous Terminal Commands

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "type": "command",
        "command": "python3 ./scripts/block-dangerous.py",
        "timeout": 5
      }
    ]
  }
}
```

### Auto-Format After File Edits

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "type": "command",
        "command": "npx prettier --write \"$TOOL_INPUT_FILE_PATH\""
      }
    ]
  }
}
```

### Inject Context at Session Start

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "python3 ./scripts/inject-context.py"
      }
    ]
  }
}
```

---

## Generating Hooks

Type `/create-hook` in chat to generate a hook configuration with AI.

---

## Next Steps

- [MCP Servers](mcp-servers.md) -- extend agents with external tools
- [Agent Plugins](agent-plugins.md) -- prepackaged bundles
