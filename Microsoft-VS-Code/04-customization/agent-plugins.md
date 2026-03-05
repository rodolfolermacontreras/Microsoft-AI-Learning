# Agent Plugins (Preview)

> Prepackaged bundles of commands, skills, agents, hooks, and MCP servers from plugin marketplaces.

---

## What Plugins Are

An agent plugin bundles multiple customizations into a single installable package:
- Slash commands
- Agent skills
- Custom agents
- Hooks
- MCP servers

Plugins work alongside your locally defined customizations.

---

## Discovering Plugins

```
Extensions view (Ctrl+Shift+X)  ->  Search "@agentPlugins"
```

Or: Extensions sidebar > More Actions > Views > Agent Plugins

---

## Installing

Select **Install** from the plugin listing. Plugin-provided customizations
appear alongside your local ones:
- Skills show in Configure Skills
- Agents show in the agent picker
- MCP servers appear in the server list

---

## Marketplaces

Default marketplaces: `copilot-plugins` and `awesome-copilot`.

Add additional marketplaces in settings:

```json
"chat.plugins.marketplaces": [
    "anthropics/claude-code",
    "owner/private-repo"
]
```

Supported formats: `owner/repo`, HTTPS git URL, SCP-style, `file:///` path.

---

## Local Plugins

Register local plugins:

```json
"chat.plugins.paths": {
    "/path/to/my-plugin": true,
    "/path/to/disabled-plugin": false
}
```

---

## Enable/Disable

Setting: `chat.plugins.enabled`

Manage installed plugins from Chat view: gear icon > Plugins.

---

## Next Steps

- [Agent Skills](agent-skills.md) -- create your own skills
- [MCP Servers](mcp-servers.md) -- add external tools
- [Hooks](hooks.md) -- lifecycle automation
