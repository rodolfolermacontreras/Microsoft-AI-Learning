# Multi-Agent Story Pipeline

## What this demonstrates

This project shows the **Command → Orchestrator Agent → Specialist Agents** pattern for automated multi-agent workflows in GitHub Copilot CLI.

```
/generate-story
      │
      ▼
story-orchestrator (agent)
      │
      ├─── Step 1 ──► plot-designer (subagent via Task tool)
      │                    └─ writes story-pipeline/plot.md
      │
      ├─── Step 2 ──► character-creator (subagent via Task tool)
      │                    └─ reads plot.md
      │                    └─ writes story-pipeline/characters.md
      │
      ├─── Step 3 ──► story-writer (subagent via Task tool)
      │                    └─ reads plot.md + characters.md
      │                    └─ writes story-pipeline/draft.md
      │
      └─── Step 4 ──► story-editor (subagent via Task tool)
                           └─ reads draft.md
                           └─ writes story-pipeline/final.md ✅
```

## How to run

1. Open this folder in a Copilot CLI terminal session
2. Edit `story-pipeline/input.md` to set your story preferences
3. Run `/generate-story`
4. Read the result in `story-pipeline/final.md`

## Key multi-agent concepts illustrated

| Concept | Where it's used |
|---|---|
| **Orchestrator agent** | `story-orchestrator` coordinates the whole pipeline |
| **Specialist agents** | Each of the 4 agents does one thing well |
| **File-based handoff** | Agents communicate by reading/writing files in `story-pipeline/` |
| **Sequential dependency** | Each step waits for the previous output before running |
| **Skills as instructions** | `.claude/skills/*/SKILL.md` define each agent's expertise |
| **Task tool** | Orchestrator spawns subagents without a new session |

## Project structure

```
multi-agent/
├── CLAUDE.md                            ← this file
├── README.md                            ← usage guide
├── .claude/
│   ├── agents/
│   │   └── story-orchestrator.md        ← main orchestrator
│   ├── skills/
│   │   ├── plot-designer/SKILL.md       ← plot outline instructions
│   │   ├── character-creator/SKILL.md   ← character profile instructions
│   │   ├── story-writer/SKILL.md        ← story writing instructions
│   │   └── story-editor/SKILL.md        ← editing/polishing instructions
│   └── commands/
│       └── generate-story.md            ← /generate-story entry point
└── story-pipeline/
    ├── input.md                          ← YOU edit this (story request)
    ├── plot.md                           ← written by plot-designer
    ├── characters.md                     ← written by character-creator
    ├── draft.md                          ← written by story-writer
    └── final.md                          ← written by story-editor ✅
```

## Why not separate sessions?

Agents spawned via the `Task` tool run in isolated context windows but are **coordinated by the orchestrator in one session**. This is better than separate sessions because:
- The orchestrator can pass context between steps
- No manual coordination needed
- Results are automatically chained
- Use `/fleet` to enable parallel execution where steps are independent

For truly separate sessions, use `isolation: worktree` in the agent frontmatter — each agent then gets its own git worktree and branch.
