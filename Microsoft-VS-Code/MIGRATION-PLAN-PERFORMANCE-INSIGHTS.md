# Migration Plan: Sales Leader Performance Insights → Copilot Customization Framework

**Created**: March 5, 2026  
**Status**: PLANNING  
**Owner**: Rodolfo Lerma  
**Purpose**: North-star document for migrating the Sales Leader Performance Insights pipeline from the current Azure AI Foundry single-agent architecture to the GitHub Copilot Customization Framework for VS Code. Contains concept mapping, phased work breakdown, milestones, validation checkpoints, and risk assessment.  
**Branch**: `feat/copilot-framework-migration` (to be created from updated `main`)

> **Context**: This is an exploratory effort. The current production pipeline (`single_agent_pipeline.py` + `foundry_client.py` + 7 tools on gpt-5.2-chat, 184 leaders, 201 tests) remains fully operational and untouched. All migration work happens in parallel on a feature branch. If the exploration proves the framework is not viable for this use case, we roll back by deleting the branch and losing nothing.

---

## Table of Contents

1. [Concept Mapping: Current World to New World](#1-concept-mapping-current-world-to-new-world)
2. [Inventory of Components to Migrate](#2-inventory-of-components-to-migrate)
3. [Target Directory Structure](#3-target-directory-structure)
4. [Phase 1: MCP Server Foundation](#phase-1-mcp-server-foundation)
5. [Phase 2: Agent Definition](#phase-2-agent-definition)
6. [Phase 3: VS Code Integration](#phase-3-vs-code-integration)
7. [Phase 4: Instructions and Skills](#phase-4-instructions-and-skills)
8. [Phase 5: Multi-Agent Orchestration](#phase-5-multi-agent-orchestration-stretch-goal)
9. [Phase 6: Validation and Comparison](#phase-6-validation-and-comparison)
10. [Milestones and Checkpoints](#milestones-and-checkpoints)
11. [Architectural Decisions](#architectural-decisions)
12. [Risk Assessment](#risk-assessment)
13. [What Stays, What Goes, What Is New](#what-stays-what-goes-what-is-new)
14. [Open Questions](#open-questions)
15. [Progress Log](#progress-log)

---

## 1. Concept Mapping: Current World to New World

| Current Component | File(s) | New Component | Framework Type | Notes |
|---|---|---|---|---|
| **Orchestrator + System Prompt** | `reasoning_agent/single_agent_pipeline.py` (SYSTEM_PROMPT ~550 lines + knowledge base guardrails, `SingleAgentPipeline` class) | `.github/agents/performance-insights.agent.md` | Agent | YAML frontmatter + Markdown body replaces Python class + string prompt. ~550 lines get decomposed into agent body (~250), skills (~200), instructions (~100). |
| **LLM client + tool loop** | `tools/foundry_client.py` (`FoundryClient.chat_with_tools()`, retry logic, `tool_choice="required"`, 28-required + 7-buffer iteration budget) | **REMOVED** — Copilot Chat handles the LLM call loop natively | N/A | Biggest paradigm shift. No code-level iteration budget. No `tool_choice="required"`. Copilot decides when to stop calling tools. Agent body must guide behavior through prompt instructions. |
| **7 analysis tools** | `tools/modular_analyzer.py` (`detect_highlights`, `detect_lowlights`, `drill_down`, `compare_peers`, `explore_distribution`, `get_role_context`) + `get_business_context` (from knowledge base) | `mcp-server/server.py` with `@mcp.tool()` wrappers calling the same Python functions | MCP Server | Tool logic stays identical. Wrappers add type hints, docstrings, error handling, and dict returns. `get_business_context` becomes a skill instead of a tool (deliver as context, not tool call). |
| **Aggregation engine** | `tools/simplified_aggregator.py` (`SimplifiedAggregator` — person-level 2-step aggregation, org benchmark, distribution metrics) | `mcp-server/tools/simplified_aggregator.py` (imported by server, no changes) | MCP dependency | Unchanged. Imported by MCP server just like today. |
| **Hotspot detector** | `tools/hotspot_detector.py` (`HotspotDetector` — compensatory gating, priority scoring, P1/P2/P3 tiers) | `mcp-server/tools/hotspot_detector.py` (imported, no changes) | MCP dependency | Unchanged. |
| **Drill-down analyzer** | `tools/drilldown_analyzer.py` | `mcp-server/tools/drilldown_analyzer.py` (imported, no changes) | MCP dependency | Unchanged. |
| **HTML renderer** | `tools/json_to_html_renderer.py` (`JSONToHTMLRenderer` — 3 display modes, leader + SA report types) | `mcp-server/tools/json_to_html_renderer.py` + MCP `render_html_report` tool | MCP Server | Wrapping as tool allows agent to trigger rendering after generating JSON. |
| **Knowledge base loader** | `tools/knowledge_base_loader.py` (`load_prompt_guardrails`, `load_tool_context`) | **SPLIT**: Guardrails → agent body; Tool context → skill (`.github/skills/business-context/`) | Agent + Skill | Guardrails (~1.5K tokens) inline in agent body. Business context (~4.5K tokens) becomes a skill loaded on-demand. |
| **Kusto data extraction** | `tools/kusto_data_extractor.py`, `tools/kusto_connector.py` | `mcp-server/tools/` (copied) + optional MCP tool for interactive extraction | MCP dependency | Copy as-is. Optionally expose `extract_leader_data` as MCP tool for ad-hoc Kusto queries. Low priority (data pre-extracted to parquet). |
| **Leader discovery / init** | `SingleAgentPipeline._init_analyzer()` (leader resolution, parquet loading, ModularAnalyzer init) | **NEW** MCP tool: `load_leader_data(leader, period)` | MCP Server | Extracted into a standalone tool. Initializes server-side state (ModularAnalyzer, SimplifiedAggregator, HotspotDetector). Must be called before any analysis tool. |
| **Foundry memory manager** | `tools/foundry_memory_manager.py` (Azure AI Foundry threads, Cosmos DB) | **REMOVED** — not applicable in Copilot framework | N/A | Copilot Chat manages conversation history natively. |
| **Post-generation validation** | `SingleAgentPipeline._validate_report()`, `_validate_tool_coverage()`, `_force_missing_drilldowns()`, `_validate_p1_drilldown_coverage()` | **NEW** MCP tool: `validate_report(report_json)` + hooks for enforcement | MCP Server + Hooks | Workstream 1 (5A/5B/5C) validation logic reimplemented as an MCP tool the agent can call. Stop hook can enforce "run validation before finishing." |
| **Impact enrichment** | `SingleAgentPipeline._enrich_dimensions_with_impact_scores()` | Included in tool return values OR **NEW** MCP tool: `enrich_report(report_json)` | MCP Server | Option A: Include impact scores in detect_highlights/detect_lowlights returns. Option B: Post-processing tool. See Decision D7. |
| **Report metadata builder** | `SingleAgentPipeline._build_report_metadata()` | Agent generates metadata as part of output OR **NEW** MCP tool | MCP Server | Low priority. Metadata is mostly operational (tokens, cost, latency) — less relevant in Copilot framework. |
| **Batch pipeline** | `reasoning_agent/batch_pipeline.py` (184 leaders, sequential, retry logic) | Stays as standalone script. Not a Copilot Chat use case. | Standalone | Batch processing is not interactive. Keep existing architecture. |
| **Solution area pipeline** | `reasoning_agent/solution_area_pipeline.py`, `batch_solution_area_pipeline.py` | Stays as standalone. Optionally create a second `.agent.md` for SA analysis. | Standalone + Optional Agent | SA analysis uses same tools but different dimensions (3 vs 4). Could be a separate agent or a mode on the same agent. Phase 5 stretch goal. |
| **Configs** | `config/leaders.json`, `hotspot_config.json`, `report_schema.json`, `solution_areas.json`, `kusto_config.json` | MCP `@mcp.resource()` for read-only access + `.vscode/mcp.json` env vars for secrets | MCP Resources + Config | Configs stay in `config/`. MCP server reads them at startup. Secrets via env vars. |
| **Coding standards** | Embedded in SYSTEM_PROMPT (tone guidelines, abbreviation rules, collaborative language) | `.github/instructions/*.instructions.md` | Instructions | Scoped by file glob. Separate files for narrative style, data analysis rules, Python standards. |
| **Methodology docs** | `docs/HOTSPOT_METHODOLOGY.md`, `docs/SYSTEM_ARCHITECTURE_GUIDE.md` | `.github/skills/performance-methodology/` with SKILL.md + bundled references | Skills | On-demand knowledge for the agent. Progressive disclosure: loaded only when relevant. |
| **Report schema** | `config/report_schema.json` (JSON Schema for agent output) | `.github/skills/report-schema/references/report_schema.json` | Skill asset | Agent references this when generating output. |
| **Business context** | `tools/knowledge_base_loader.py` → `load_tool_context()` (glossary, insight examples, recommendation framework, ~4.5K tokens) | `.github/skills/business-context/` with SKILL.md + references | Skill | Currently delivered via `get_business_context()` tool call. In new framework, loaded as skill on-demand before Phase 3 output generation. |
| **Test suite** | `tests/*.py` (201 tests, pytest) | Stays as-is. Add MCP server tests. Add `.github/instructions/testing.instructions.md`. | Tests + Instructions | Tests validate tool logic. MCP wrapper tests validate protocol compliance. |
| **Eval framework** | `evals/run_evaluation.py`, `evals/test_cases.json` | Stays as-is. Add eval test cases that run through MCP. | Evals | Compare Copilot-generated reports vs current pipeline output. |

### Key Paradigm Shifts

1. **Agents are Markdown, not Python.** The system prompt, persona, tool list, and model selection are declared in YAML frontmatter + Markdown body. No `SingleAgentPipeline` class.

2. **No `foundry_client.py`.** Copilot Chat IS the LLM client. It manages messages, tool calling, retries, and conversation state. The code-level 28-required / 7-buffer iteration budget disappears. The 3-phase workflow (Discovery → Root Cause → JSON Generation) must be enforced through prompt instructions, not code.

3. **No `tool_choice="required"`.** Currently forces the first 28 iterations to use tools. In Copilot, the agent decides when to call tools. The agent body must be explicit about calling tools before generating output.

4. **Tools become MCP.** Same Python functions, different protocol. `@mcp.tool()` wrappers expose them over stdio to VS Code. Tool docstrings become critical — they're the primary way the model understands when/how to use each tool.

5. **Instructions replace in-prompt rules.** Tone guidelines, abbreviation rules, statistical methodology rules move to `.instructions.md` files. Always-on instructions reduce agent body size. Scoped instructions (e.g., Python conventions) only load when relevant.

6. **Skills replace bundled docs.** The methodology reference (Clean Approach, distribution patterns, compensatory gating) and business context (glossary, insight examples, recommendation framework) become on-demand skills. Loaded only when the task matches, saving context.

7. **Everything is file-based.** No Azure AI Foundry deployment, no Cosmos DB, no thread management. Just files in the repository that VS Code reads.

8. **Validation shifts from code to prompt + hooks.** The 5A/5B/5C validation workstream (`_validate_report`, `_validate_tool_coverage`, `_force_missing_drilldowns`) currently runs in Python after the agent finishes. In the new framework: (a) agent body includes a checklist it must verify, (b) a `validate_report` MCP tool lets the agent self-check, (c) a Stop hook can block completion until validation passes.

---

## 2. Inventory of Components to Migrate

### 2A. Tool Functions (7 existing + 2 new)

These are the functions registered in `SingleAgentPipeline.get_tools()` and dispatched in `execute_tool()`. Each needs an `@mcp.tool()` wrapper in `server.py`.

| # | Tool Name | Source Method | Parameters | Return Type | MCP Wrapper Notes |
|---|---|---|---|---|---|
| T1 | `detect_highlights` | `ModularAnalyzer.detect_highlights()` | `dimension: str (enum: geography/segment/role/solution_area)`, `top_n: int = 5` | `dict` with `highlights` list | Docstring: when to use, dimension enum, interpretation. Include `relative_impact_pct`, `gap_contribution_pct`, `org_share` in return (see D7). |
| T2 | `detect_lowlights` | `ModularAnalyzer.detect_lowlights()` | `dimension: str (enum)`, `top_n: int = 5` | `dict` with `lowlights` list | Mirror of T1 for underperformers. Same enrichment with impact scores. |
| T3 | `drill_down` | `ModularAnalyzer.drill_down()` | `dimension: str (enum)`, `segment_name: str`, `is_highlight: bool (optional)`, `parent_data_reference: str (optional)` | `dict` with `plan_breakdown`, `segment_name`, `population`, etc. | Critical tool. Docstring must explain `plan_breakdown` interpretation, `is_highlight` filtering, and data reference linking. |
| T4 | `compare_peers` | `ModularAnalyzer.compare_peers()` | `dimension: str (enum)`, `segment_names: list[str]` | `dict` with comparison data | Used less frequently. Include anyway. |
| T5 | `explore_distribution` | `ModularAnalyzer.explore_distribution()` | `dimension: str (enum)`, `segment_name: str` | `dict` with percentiles, outlier analysis, `distribution_type` | Triggered for high-CV (> 0.25) or extreme kurtosis (> 3) hotspots. |
| T6 | `get_role_context` | `ModularAnalyzer.get_role_context()` | `role_name: str` | `dict` with RSG matches, `core_priorities`, `success_metrics` | Required after every role dimension drill_down. |
| T7 | `load_leader_data` | **NEW** — extracted from `_init_analyzer()` | `leader: str`, `period: str` | `dict` with org benchmark, population, std, dimensions, leader level | Initializes server-side state. Must be called first. See Decision D2. |
| T8 | `render_html_report` | **NEW** — wraps `JSONToHTMLRenderer.render()` | `report_json: str`, `display_mode: str = "collapsible"` | `dict` with file path to generated HTML | Allows agent to render final report after generating JSON. |
| T9 | `validate_report` | **NEW** — extracted from `_validate_report()` + `_validate_p1_drilldown_coverage()` | `report_json: str` | `dict` with validation errors list | Self-check tool. Agent calls this before finishing. Returns pass/fail + specific issues. |

**Removed tool:**
- `get_business_context` — replaced by `.github/skills/business-context/` skill. Context is loaded on-demand by the AI when writing the final report, without a tool call.

### 2B. Configuration Files

| File | Size | MCP Treatment | Priority |
|---|---|---|---|
| `config/leaders.json` | 184 leaders | `@mcp.resource("config://leaders")` — read-only access | P1 — needed by `load_leader_data` |
| `config/hotspot_config.json` | Compensatory gating params | `@mcp.resource("config://hotspot")` — informational | P2 |
| `config/report_schema.json` | 273 lines, JSON Schema | Skill asset: `.github/skills/report-schema/references/report_schema.json` | P1 — agent needs this for output format |
| `config/solution_areas.json` | 15 solution areas | `@mcp.resource("config://solution-areas")` | P3 — only if SA agent is built |
| `config/kusto_config.json` | Kusto connection params | Server-side env var via `.vscode/mcp.json` | P3 |
| `config/foundry_config.json` | Azure AI Foundry config | **NOT MIGRATED** — not needed in Copilot framework | N/A |

### 2C. System Prompt Sections to Redistribute

The SYSTEM_PROMPT in `single_agent_pipeline.py` (~550 lines, plus knowledge base guardrails appended at runtime) contains these logical sections:

| Section | Lines (approx) | Destination | Priority |
|---|---|---|---|
| Core identity + task description | ~15 | Agent body: "You are..." section | P1 |
| Critical requirements (6 rules) | ~10 | Agent body: Critical Requirements section | P1 |
| ALL 4 DIMENSIONS ARE MANDATORY | ~10 | Agent body: Mandatory Dimensions section | P1 |
| Mandatory workflow (Phase 1/2/3 + 2.5) | ~80 | Agent body: Workflow section | P1 |
| Data reference system (ID format, examples) | ~40 | Agent body: Data References section | P1 |
| Methodology (Clean Approach overview) | ~15 | Agent body OR skill reference | P1 |
| Distribution shape metrics (CV, skewness, kurtosis) | ~60 | Skill: `.github/skills/performance-methodology/references/distribution-patterns.md` | P2 |
| Welch's t-test guidance | ~25 | Skill: `.github/skills/performance-methodology/references/welch-t-test.md` | P2 |
| Combined distribution pattern rubric (7 patterns) | ~50 | Skill: `.github/skills/performance-methodology/references/distribution-patterns.md` | P2 |
| Temporal trends (period-over-period) | ~20 | Agent body: Temporal Trends section | P1 |
| Distribution exploration tool usage | ~10 | Agent body: MCP Tools section | P1 |
| Analysis style guidance (verbose, practical) | ~15 | Agent body: Approach section | P1 |
| Executive summary guidelines (bullets, abbreviations) | ~30 | Agent body: Output Format section | P1 |
| Output JSON format specification | ~50 | Agent body: Output Format + skill reference to `report_schema.json` | P1 |
| Rules (attainment format, personal language, etc.) | ~15 | Agent body: Rules section | P1 |
| Narrative guidelines (good/bad examples) | ~25 | Instructions: `narrative-style.instructions.md` | P2 |
| Language and tone guidelines (collaborative vocabulary) | ~30 | Instructions: `narrative-style.instructions.md` | P2 |
| Leader level context (L4/L5/L6 scope) | ~30 | Agent body: Leader Level section | P1 |
| Knowledge base guardrails (~1.5K tokens) | ~50 | Agent body: Anti-Patterns section OR instructions | P2 |
| Knowledge base tool context (~4.5K tokens) | ~150 | Skill: `.github/skills/business-context/` | P2 |

**Total**: ~550+ lines to redistribute across agent body (~250 lines), skills (~200 lines), and instructions (~100 lines).

### 2D. Validation Logic to Migrate

The 5A/5B/5C validation workstream currently runs as Python post-processing:

| Validation | Current Implementation | New Implementation |
|---|---|---|
| **5A: Report structure** | `_validate_report()` — checks 4 dimensions present, P1 root_causes non-empty, exec summary bullet counts | MCP tool `validate_report` — agent calls before finishing |
| **5B: Tool coverage** | `_validate_tool_coverage()` — auto-executes missed Phase 1 calls | Agent body checklist: "Did I call detect_highlights for ALL 4 dimensions?" Cannot auto-execute in Copilot. Rely on prompt. |
| **5C: P1 drill-down** | `_force_missing_drilldowns()` — auto-executes missed drill-downs for P1 hotspots | Agent body: "Every P1 hotspot MUST have drill_down results." `validate_report` tool flags gaps. |
| **P1 coverage check** | `_validate_p1_drilldown_coverage()` — warns about P1 hotspots without root_causes | Merged into `validate_report` tool. |

### 2E. Dependencies

| Dependency | Needed in MCP Server | Reason |
|---|---|---|
| `pandas>=2.1.0` | YES | Core data processing in aggregator, analyzer, detector |
| `numpy>=1.24.0` | YES | Statistical calculations, NAType handling |
| `scipy>=1.10.0` | YES | Welch's t-test in hotspot_detector |
| `pyarrow` (implicit via pandas) | YES | Parquet file reading |
| `python-dotenv>=1.0.0` | YES | Environment variable loading |
| `pydantic>=2.5.0` | YES | MCP requires Pydantic for structured inputs |
| `jinja2>=3.1.2` | YES (if rendering) | HTML templating in renderer |
| `mcp[cli]>=1.0.0` | **NEW** | MCP server framework |
| `azure-identity`, `azure-kusto-data` | OPTIONAL | Only if exposing Kusto extraction as MCP tool |
| `openai`, `azure-ai-inference`, `azure-ai-projects` | **NO** | Copilot replaces the LLM client |
| `streamlit` | **NO** | Dashboard not part of MCP server |

---

## 3. Target Directory Structure

```
PerformanceMetricAgent/
├── .github/
│   ├── copilot-instructions.md                       # Global project rules (always active)
│   ├── instructions/
│   │   ├── python-standards.instructions.md           # Python coding rules (applyTo: **/*.py)
│   │   ├── data-analysis.instructions.md              # Statistical methodology (applyTo: tools/**, mcp-server/**)
│   │   ├── narrative-style.instructions.md            # Tone, language, abbreviation rules (applyTo: **)
│   │   └── testing.instructions.md                    # Test standards (applyTo: **/test_*.py)
│   └── agents/
│       ├── performance-insights.agent.md              # Leader analysis agent (main)
│       └── solution-area-insights.agent.md            # SA analysis agent (Phase 5 stretch)
├── .vscode/
│   └── mcp.json                                       # MCP server registration
│
│   # Skills under .github/ per framework convention (portable, discoverable by VS Code + CLI + coding agent)
├── .github/skills/
│   ├── performance-methodology/
│   │   ├── SKILL.md                                   # Entry point
│   │   └── references/
│   │       ├── clean-approach-overview.md              # Core methodology (aggregation, gating, prioritization)
│   │       ├── distribution-patterns.md                # CV/skewness/kurtosis 7-pattern rubric
│   │       └── welch-t-test.md                         # Statistical significance interpretation
│   ├── business-context/
│   │   ├── SKILL.md                                   # WWIC glossary, insight examples, recommendation framework
│   │   └── references/
│   │       ├── glossary.md                             # WWIC Business Glossary
│   │       ├── insight-examples.md                     # 5 good-vs-bad insight examples
│   │       └── recommendation-framework.md             # 5 approved recommendation categories
│   ├── report-schema/
│   │   ├── SKILL.md                                   # Report output format reference
│   │   └── references/
│   │       └── report_schema.json                      # JSON Schema (copied from config/)
│   └── data-schema/
│       ├── SKILL.md                                   # Kusto schema, column definitions
│       └── references/
│           └── data-schema.md                          # Copied from docs/data_schema.md
├── mcp-server/
│   ├── pyproject.toml                                  # MCP server project config
│   ├── server.py                                       # FastMCP server (9 tools + resources)
│   └── tools/                                          # Python modules (copied from tools/)
│       ├── __init__.py
│       ├── modular_analyzer.py                         # 6 analysis tool implementations
│       ├── simplified_aggregator.py                    # 2-step person-level aggregation
│       ├── hotspot_detector.py                         # Compensatory gating logic
│       ├── drilldown_analyzer.py                       # Plan/bucket drill-down
│       ├── json_to_html_renderer.py                    # JSON-to-HTML rendering
│       ├── knowledge_base_loader.py                    # Guardrails + tool context (if needed)
│       ├── kusto_connector.py                          # Kusto connection (optional)
│       └── kusto_data_extractor.py                     # Data extraction (optional)
├── config/                                             # UNCHANGED — referenced by MCP server
├── data/                                               # UNCHANGED — parquet files, role_context.json
├── reasoning_agent/                                    # UNCHANGED — backward compat for batch
├── tools/                                              # UNCHANGED — still used by batch pipeline
├── tests/                                              # EXISTING + new MCP server tests
├── docs/                                               # EXISTING docs
├── evals/                                              # EXISTING eval framework
└── ...existing project files...
```

**Key principle**: The MCP server's `tools/` directory contains COPIES of the analysis modules. The originals in the project-root `tools/` remain untouched for backward compatibility with the batch pipeline (184 leaders). If we later consolidate, we make one set canonical and have the other import from it.

---

## Phase 1: MCP Server Foundation

**Goal**: Stand up a working MCP server that exposes all 9 tools (7 existing + 2 new) and can be tested independently via the MCP Inspector.

**Branch**: `feat/copilot-framework-migration`

### Task 1.1: Scaffold MCP Server Directory

Create `mcp-server/` with initial file structure.

**Files to create**:
- `mcp-server/pyproject.toml`
- `mcp-server/server.py` (skeleton)
- `mcp-server/tools/__init__.py`

**pyproject.toml contents**:
```toml
[project]
name = "performance-insights-mcp-server"
version = "0.1.0"
description = "MCP server exposing Sales Performance Insights analysis tools to GitHub Copilot"
requires-python = ">=3.10"
dependencies = [
    "mcp[cli]>=1.0.0",
    "pandas>=2.1.0",
    "numpy>=1.24.0",
    "scipy>=1.10.0",
    "pyarrow>=14.0.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.5.0",
    "jinja2>=3.1.2",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project.scripts]
performance-insights-mcp = "server:main"
```

**Checkpoint 1.1**: `mcp-server/` directory exists with valid `pyproject.toml`.

### Task 1.2: Copy Tool Modules

Copy these files from `tools/` to `mcp-server/tools/`:
- `modular_analyzer.py`
- `simplified_aggregator.py`
- `hotspot_detector.py`
- `drilldown_analyzer.py`
- `json_to_html_renderer.py`
- `knowledge_base_loader.py` (if needed for guardrails/context loading)

**Import adjustments needed**:
- `modular_analyzer.py` imports `from tools.hotspot_detector import ...` → `from .hotspot_detector import ...`
- `modular_analyzer.py` imports `from tools.simplified_aggregator import ...` → `from .simplified_aggregator import ...`
- `modular_analyzer.py` imports `from tools.drilldown_analyzer import ...` → `from .drilldown_analyzer import ...`
- Any `sys.path` / `project_root` manipulation needs updating to resolve relative to MCP server

**Checkpoint 1.2**: All modules copied. `python -c "from mcp_server.tools.modular_analyzer import ModularAnalyzer"` succeeds.

### Task 1.3: Implement `load_leader_data` Tool (T7)

This is a NEW tool that replaces `SingleAgentPipeline._init_analyzer()`. It initializes server-side state that all other tools depend on.

**Signature**:
```python
@mcp.tool()
async def load_leader_data(leader: str, period: str) -> dict:
    """Load performance data for a specific leader and period.
    
    This MUST be called before any other analysis tool. It loads the leader's
    parquet data, initializes the aggregation engine, and returns organization-level
    metrics including benchmark, population, and available dimensions.
    
    Args:
        leader: Leader alias (e.g., "DEBCUPP", "NICKPA") or pipeline key (e.g., "deb_cupp")
        period: Analysis period in YYYYMM format (e.g., "202601")
    
    Returns:
        Organization benchmark including mean attainment, std, population, leader level,
        leader display name, reports_to, and available dimensions.
    """
```

**Server-side state management**:
```python
@dataclass
class ServerState:
    analyzer: Optional[ModularAnalyzer] = None
    aggregator: Optional[SimplifiedAggregator] = None
    detector: Optional[HotspotDetector] = None
    leader: str = ""
    leader_alias: str = ""
    period: str = ""
    leader_display_name: str = ""
    leader_level: int = 4
    reports_to_name: Optional[str] = None
    org_benchmark: float = 0.0
    org_std: float = 0.0
    population: int = 0
    raw_hotspot_data: dict = field(default_factory=dict)

state = ServerState()
```

**Logic** (extracted from `_init_analyzer()`):
1. Load `config/leaders.json`
2. Resolve leader alias from input (accepts alias, pipeline_key, or display_name)
3. Load parquet from `data/raw/{ALIAS}/{ALIAS}_{YEAR}.parquet`
4. Create `SimplifiedAggregator(raw_data)`
5. Create `HotspotDetector()`
6. Create `ModularAnalyzer(aggregator, detector)`
7. Set `analyzer._leader_alias` for role context loading
8. Set `analyzer._period` for temporal delta enrichment
9. Store everything in `state`
10. Return org benchmark summary + leader context

**Checkpoint 1.3**: `load_leader_data("DEBCUPP", "202601")` returns `{"status": "success", "leader": "DEBCUPP", "leader_display_name": "Deb Cupp", "leader_level": 4, "org_benchmark": 1.069, "org_std": ..., "population": 22183, "dimensions": ["geography", "segment", "role", "solution_area"]}` in MCP Inspector.

### Task 1.4: Implement Analysis Tool Wrappers (T1-T6)

Wrap each of the 6 existing tools. Pattern for each:

```python
@mcp.tool()
async def detect_highlights(dimension: str, top_n: int = 5) -> dict:
    """Identify overperforming segments above the organization benchmark.
    
    Call this for each dimension (geography, segment, role, solution_area) during
    Phase 1 Surface Discovery. Returns segments with positive gap_vs_org, ranked
    by volume_weighted_gap. Each highlight includes attainment, population, Cohen's d,
    priority tier (P1/P2/P3), distribution metrics (CV, skewness, kurtosis),
    Welch's t-test results, temporal trends, and data_reference ID.
    
    Args:
        dimension: One of: geography, segment, role, solution_area
        top_n: Maximum number of highlights to return (default: 5)
    """
    if state.analyzer is None:
        return {"status": "error", "message": "No leader data loaded. Call load_leader_data first."}
    try:
        result = state.analyzer.detect_highlights(dimension=dimension, top_n=top_n)
        state.raw_hotspot_data[(dimension, "highlights")] = result.get("highlights", [])
        return {"status": "success", **result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

Repeat for:
- `detect_lowlights` (T2) — mirror of T1, store in `raw_hotspot_data`
- `drill_down` (T3) — includes `is_highlight` and `parent_data_reference`
- `compare_peers` (T4) — takes `segment_names: list[str]`
- `explore_distribution` (T5) — percentile breakdown, outlier impact
- `get_role_context` (T6) — RSG data for role hotspots

**Critical**: Tool docstrings must be comprehensive. In the Copilot framework, the model reads docstrings to decide when/how to use each tool. Current `get_tools()` JSON descriptions are a good starting point but need enrichment.

**Checkpoint 1.4**: All 6 analysis tools callable in MCP Inspector. Test: `load_leader_data("DEBCUPP", "202601")` → `detect_highlights("geography")` — verify returns valid hotspot data matching current pipeline output.

### Task 1.5: Implement `render_html_report` Tool (T8)

```python
@mcp.tool()
async def render_html_report(report_json: str, display_mode: str = "collapsible") -> dict:
    """Render a JSON performance report into a self-contained HTML file.
    
    Call this after generating the final JSON report to produce a shareable HTML file.
    The report will be saved to output/reports/{LEADER}/{PERIOD}/.
    
    Args:
        report_json: The complete report JSON as a string (will be parsed)
        display_mode: collapsible (interactive, requires JS), expanded (email-safe),
                      or compact (exec summary only). Default: collapsible
    """
```

**Checkpoint 1.5**: Pass a known-good `report_data.json` to the tool. Open resulting HTML in browser. Visually confirm it matches current output.

### Task 1.6: Implement `validate_report` Tool (T9)

```python
@mcp.tool()
async def validate_report(report_json: str) -> dict:
    """Validate a performance report for completeness and correctness.
    
    REQUIRED: Call this before finishing to ensure report quality.
    Checks: 4 dimensions present, P1 hotspots have root_causes,
    executive summary has minimum bullet counts, data_references present.
    
    Args:
        report_json: The complete report JSON as a string
    
    Returns:
        {"status": "pass", "checks_passed": 8, "issues": []} or
        {"status": "fail", "checks_passed": 5, "issues": ["Missing dimensions: solution_area", ...]}
    """
```

**Validation checks** (extracted from 5A/5B/5C):
1. All 4 dimensions present (geography, segment, role, solution_area)
2. Every P1 hotspot has non-empty `root_causes`
3. `executive_summary.overall_performance` has >= 2 bullets
4. `executive_summary.highlights_summary` has >= 4 bullets
5. `executive_summary.lowlights_summary` has >= 4 bullets
6. Every hotspot has a `data_reference` field
7. Every root_cause has a `data_reference` field
8. Attainment values are decimals (not percentages > 2.0)

**Checkpoint 1.6**: Pass a known-good report → "pass". Pass a report with missing solution_area → "fail" with specific error.

### Task 1.7: Add MCP Resources for Configs

```python
@mcp.resource("config://leaders")
async def get_leaders_config() -> dict:
    """Return the leaders configuration including all 184 active leaders and their metadata."""

@mcp.resource("config://hotspot")
async def get_hotspot_config() -> dict:
    """Return hotspot detection parameters (compensatory gating, priority scoring)."""

@mcp.resource("config://report-schema")
async def get_report_schema() -> dict:
    """Return the JSON Schema that defines the expected report output format."""
```

**Checkpoint 1.7**: Resources accessible in MCP Inspector. Schema returns full JSON Schema.

### Task 1.8: Install and Test

```powershell
cd mcp-server
pip install -e .

# Test with MCP Inspector
mcp dev server.py
```

**Checkpoint 1.8 (Phase 1 Gate)**: ALL of the following pass:
- [ ] `mcp dev server.py` starts without errors
- [ ] MCP Inspector shows 9 tools listed (T1-T9)
- [ ] MCP Inspector shows 3+ resources
- [ ] `load_leader_data("DEBCUPP", "202601")` returns success with correct org benchmark (~106.9%)
- [ ] `detect_highlights("geography")` returns highlights matching current pipeline
- [ ] `detect_lowlights("segment")` returns lowlights matching current pipeline
- [ ] `drill_down("geography", "France", false)` returns plan_breakdown with data_references
- [ ] `get_role_context("ENT CSA - Copilot")` returns RSG data
- [ ] `explore_distribution("geography", "France")` returns percentile data
- [ ] `render_html_report(known_good_json)` produces valid HTML
- [ ] `validate_report(known_good_json)` returns "pass"
- [ ] `validate_report(incomplete_json)` returns "fail" with specific errors
- [ ] No logging to stdout (all logging to stderr)
- [ ] Server shuts down cleanly

**Estimated effort**: 10-14 hours

---

## Phase 2: Agent Definition

**Goal**: Create the `.agent.md` file that replaces `SYSTEM_PROMPT` and `SingleAgentPipeline` orchestration logic.

### Task 2.1: Create Agent File Skeleton

**File**: `.github/agents/performance-insights.agent.md`

**Frontmatter**:
```yaml
---
name: Performance Insights
description: >
  Analyze sales leader performance data across geography, segment, role,
  and solution_area dimensions. Detects hotspots, drills down to root causes,
  and generates structured JSON reports with actionable insights.
tools:
  - read
  - search
  - codebase
  - fetch
model: GPT-4.1 (copilot)
---
```

> **Note on tools list**: The MCP tools (load_leader_data, detect_highlights, etc.) are automatically available when the MCP server is running. The `tools` array in frontmatter lists VS Code built-in tools the agent can also use. Write tools (`edit`, `create`, `runInTerminal`) are deliberately excluded — this agent is a **read-only analyst** that generates JSON output via chat. File output is handled by the `render_html_report` MCP tool. See Decision D11 (read-only agent design) in the original migration framework.

**Checkpoint 2.1**: File exists at correct path. Frontmatter validates.

### Task 2.2: Write Agent Body — Core Identity

Extract from SYSTEM_PROMPT lines 1-15 (core identity, critical requirements).

```markdown
You are a Sales Performance Analyst AI expert on Sales Incentive Performance.
You generate structured JSON reports analyzing sales leader organizations.

## Critical Requirements
1. You MUST use the provided tools to gather data before generating any insights.
2. DO NOT make up any numbers. ALL metrics must come from tool calls.
3. This is a PERSONAL report — use "Your organization" not the leader's name.
4. If you respond without calling tools first, your analysis will be invalid.
5. You MUST call drill_down for EVERY P1 hotspot to get root causes.
6. If root_causes is empty for any P1 hotspot, your report is INCOMPLETE.
7. You MUST analyze ALL 4 dimensions: geography, segment, role, solution_area.
```

**Checkpoint 2.2**: Agent body clearly states identity and non-negotiable rules.

### Task 2.3: Write Agent Body — Mandatory Workflow

Encode the 3-phase workflow from SYSTEM_PROMPT. This is critical because without `foundry_client.py` enforcing iteration budgets, the agent prompt must guide behavior.

```markdown
## Mandatory Workflow

### Phase 1: Surface Discovery (8 tool calls minimum)
Call detect_highlights AND detect_lowlights for ALL 4 dimensions:
1. detect_highlights("geography")
2. detect_highlights("segment")
3. detect_highlights("role")
4. detect_highlights("solution_area")
5. detect_lowlights("geography")
6. detect_lowlights("segment")
7. detect_lowlights("role")
8. detect_lowlights("solution_area")

DO NOT skip solution_area. DO NOT re-call these tools with different top_n.

### Phase 2: Root Cause Analysis (12+ drill_down calls)
For EVERY P1 and P2 hotspot (both highlights and lowlights):
- Call drill_down with is_highlight=true for highlights, false for lowlights
- Pass parent_data_reference for traceability
- For role dimension: ALSO call get_role_context after each drill_down
- For high-CV segments (CV > 0.25): call explore_distribution
- Minimum 2 highlights + 2 lowlights per dimension = 16 drill_downs

### Phase 3: Generate JSON Report
BEFORE writing JSON, verify:
- [ ] All 4 dimensions discovered (8 detect calls made)
- [ ] At least 1 highlight AND 1 lowlight drilled down per dimension
- [ ] Every P1 hotspot has root_causes from drill_down
- [ ] Role hotspots have get_role_context data

Call validate_report with your JSON to verify completeness.
Output ONLY valid JSON matching the report schema.
```

**Checkpoint 2.3**: Workflow section matches current SYSTEM_PROMPT phases. Explicit checklist replaces code-level iteration budget.

### Task 2.4: Write Agent Body — MCP Tools Documentation

Document all 9 MCP tools with parameters and usage guidance.

```markdown
## Available MCP Tools

### load_leader_data (CALL FIRST)
Loads a leader's data and initializes the analysis engine.
- leader: Leader alias ("DEBCUPP") or pipeline key ("deb_cupp")
- period: Period in YYYYMM format ("202601")
Returns: org benchmark, population, std, leader level, dimensions available.

### detect_highlights / detect_lowlights
[Continue for all 9 tools with clear when-to-use guidance]
```

**Checkpoint 2.4**: All 9 tools documented.

### Task 2.5: Write Agent Body — Data Reference System

Extract from SYSTEM_PROMPT (reference ID format, examples, traceability rules).

**Checkpoint 2.5**: Data reference system fully documented with examples.

### Task 2.6: Write Agent Body — Output Format and Rules

Include the JSON output specification. Reference `.github/skills/report-schema/` for the full JSON Schema.

```markdown
## Output Format
Output ONLY valid JSON matching the report schema (see report-schema skill).

Key structure:
- executive_summary: { overall_performance: [...], highlights_summary: [...], lowlights_summary: [...] }
- overall_performance: { active_participants, avg_attainment, commentary: [...] }
- dimensions: [ { dimension_name, highlights: [...], lowlights: [...], drilldown: {...}, insights: [...], actions: [...] } ]

## Rules
- Attainment values as decimals (0.966 not 96.6%)
- Gaps as decimals (0.217 for +21.7pp)
- "Your organization" not leader name
- Full plan names on first mention
- Include data_reference for every hotspot and root_cause
```

**Checkpoint 2.6**: Output format and rules complete.

### Task 2.7: Write Agent Body — Leader Level Context

Extract L4/L5/L6 scope guidance.

**Checkpoint 2.7**: Leader level section explains scope boundaries per level.

### Task 2.8: Write Agent Body — Temporal Trends and Distribution Exploration

Extract temporal trend interpretation rules and distribution exploration trigger conditions.

**Checkpoint 2.8**: Both sections present.

### Task 2.9: Final Agent Review

Read the complete `.agent.md` end-to-end. Verify:
- [ ] No orphaned references to `foundry_client.py`, `SingleAgentPipeline`, or Azure AI Foundry
- [ ] No references to iteration budgets (28 required / 7 buffer)
- [ ] No reference to `tool_choice="required"` or `max_completion_tokens`
- [ ] All 9 MCP tools documented
- [ ] JSON output format fully specified
- [ ] Collaborative tone guidelines included (or referenced via instruction)
- [ ] Distribution pattern rubric referenced via skill (not inlined)
- [ ] Data reference system documented
- [ ] 4 mandatory dimensions stated
- [ ] Total agent body is between 200-350 lines
- [ ] `validate_report` tool usage documented in workflow

**Checkpoint 2.9 (Phase 2 Gate)**: Agent file is complete, self-consistent, and under 350 lines.

**Estimated effort**: 4-6 hours

---

## Phase 3: VS Code Integration

**Goal**: Wire the MCP server to VS Code so the agent can call tools from Copilot Chat.

### Task 3.1: Create `.vscode/mcp.json`

```json
{
  "servers": {
    "performance-insights": {
      "command": "${workspaceFolder}/.venv/Scripts/python.exe",
      "args": ["${workspaceFolder}/mcp-server/server.py"],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "DATA_ROOT": "${workspaceFolder}/data",
        "CONFIG_ROOT": "${workspaceFolder}/config"
      }
    }
  }
}
```

**Checkpoint 3.1**: File exists. VS Code Command Palette > "MCP: List Servers" shows "performance-insights".

### Task 3.2: Install MCP Dependencies into .venv

```powershell
.\.venv\Scripts\Activate.ps1
pip install "mcp[cli]>=1.0.0"
pip install -e mcp-server/
```

**Checkpoint 3.2**: `python -c "from mcp.server.fastmcp import FastMCP; print('OK')"` succeeds in `.venv`.

### Task 3.3: Start MCP Server from VS Code

1. Open Command Palette > "MCP: List Servers"
2. Start "performance-insights"
3. Open Copilot Chat
4. Verify tools appear in the tool picker

**Checkpoint 3.3**: MCP server starts. 9 tools visible in Copilot Chat.

### Task 3.4: Test Agent Invocation

Open Copilot Chat, select "Performance Insights" agent, and type:
```
Analyze DEBCUPP for period 202601
```

Expected behavior:
1. Agent calls `load_leader_data("DEBCUPP", "202601")`
2. Agent proceeds through Phase 1 discovery (8 detect calls)
3. Agent proceeds through Phase 2 drill-downs (12+ calls)
4. Agent calls role context for role hotspots
5. Agent calls `validate_report` on its output
6. Agent generates JSON output

**Checkpoint 3.4 (Phase 3 Gate)**: Agent responds with correct persona, calls MCP tools in the right order, and produces structured output. Output does NOT need to match current pipeline exactly — just needs to demonstrate the tools work end-to-end through Copilot.

**Estimated effort**: 2-3 hours

---

## Phase 4: Instructions and Skills

**Goal**: Move coding standards, methodology docs, business context, and reference materials into the framework's instruction and skill formats.

### Task 4.1: Create Global Project Instructions

**File**: `.github/copilot-instructions.md`

Contents:
- Project overview (Sales Performance Insights, 184 leaders, 4 dimensions)
- Data handling rules (person-level aggregation, never row-level, SUM buckets then AVERAGE people)
- Architecture overview (MCP tools in `mcp-server/`, analysis modules, data in `data/raw/`)
- Git practices (conventional commits, feature branches)
- Error handling standards (specific exceptions, never bare except)

**Checkpoint 4.1**: File exists. Concise (<100 lines).

### Task 4.2: Create Scoped Instruction Files

**File**: `.github/instructions/narrative-style.instructions.md`
```yaml
---
name: Narrative Style Guidelines
description: Tone, language, and formatting rules for performance reports
applyTo: '**'
---
```
Contents: Collaborative vocabulary shifts table, abbreviation rules (YTD, attn), plan name usage, avoidance of statistical jargon, framing lowlights as "areas to monitor", good/bad tone examples.

**File**: `.github/instructions/data-analysis.instructions.md`
```yaml
---
name: Data Analysis Rules
description: Statistical methodology and data handling conventions
applyTo: 'tools/**, mcp-server/**'
---
```
Contents: Person-level aggregation requirement, Cohen's d threshold, compensatory gating model, NAType handling.

**File**: `.github/instructions/python-standards.instructions.md`
```yaml
---
name: Python Standards
description: Python coding conventions
applyTo: '**/*.py'
---
```

**File**: `.github/instructions/testing.instructions.md`
```yaml
---
name: Testing Standards
description: pytest conventions and test standards
applyTo: '**/test_*.py'
---
```

**Checkpoint 4.2**: 4 instruction files with valid frontmatter.

### Task 4.3: Create Performance Methodology Skill

**Structure**:
```
.github/skills/performance-methodology/
├── SKILL.md
└── references/
    ├── clean-approach-overview.md
    ├── distribution-patterns.md
    └── welch-t-test.md
```

**SKILL.md**:
```yaml
---
name: performance-methodology
description: >
  Statistical methodology reference for sales performance hotspot detection.
  Covers the Clean Approach (person-level aggregation, compensatory gating,
  Cohen's d, volume-weighted gap), distribution pattern classification
  (7 patterns: Uniform Underperformance, Replicable Excellence, Bottom-Tail
  Outliers, Top-Tail Outliers, Natural Variation, Polarized, Star-Dependent),
  and Welch's t-test interpretation for business context.
---
```

**clean-approach-overview.md**: Extracted from `docs/HOTSPOT_METHODOLOGY.md` — the core methodology (2-step aggregation, dual-benchmark, compensatory gates, priority scoring, P1/P2/P3 tiers).

**distribution-patterns.md**: Extracted from SYSTEM_PROMPT — the 7-pattern rubric with CV/skewness/kurtosis thresholds and recommended actions per pattern.

**welch-t-test.md**: Extracted from SYSTEM_PROMPT — p-value interpretation thresholds (p ≤ 0.05, p ≤ 0.20, p > 0.20), when to use in narrative, combination with CV.

**Checkpoint 4.3**: SKILL.md `name` matches folder name. References exist and linked.

### Task 4.4: Create Business Context Skill

**Structure**:
```
.github/skills/business-context/
├── SKILL.md
└── references/
    ├── glossary.md
    ├── insight-examples.md
    └── recommendation-framework.md
```

**SKILL.md**:
```yaml
---
name: business-context
description: >
  WWIC Business Glossary, Insight Quality Examples, and Recommendation
  Framework. Load this skill before writing the final JSON report to ensure
  narratives explain WHY hotspots exist with specific numbers and plans,
  and that recommendations fit approved categories.
---
```

Contents extracted from whatever `load_tool_context()` currently returns (~4.5K tokens of glossary, 5 good-vs-bad examples, and 5 recommendation categories).

**Checkpoint 4.4**: Skill replaces the `get_business_context` tool call. Agent auto-loads when writing final JSON.

### Task 4.5: Create Report Schema Skill

**Structure**:
```
.github/skills/report-schema/
├── SKILL.md
└── references/
    └── report_schema.json
```

**SKILL.md**:
```yaml
---
name: report-schema
description: >
  JSON Schema defining the expected output format for performance insight
  reports. Reference this when generating the final JSON to ensure the
  report includes all required fields: executive_summary, overall_performance,
  and dimensions array with highlights, lowlights, drilldown, insights,
  and actions per dimension.
---
```

**Checkpoint 4.5**: Contains the authoritative 273-line JSON Schema.

### Task 4.6: Create Data Schema Skill

**Structure**:
```
.github/skills/data-schema/
├── SKILL.md
└── references/
    └── data-schema.md
```

**Checkpoint 4.6**: Contains column definitions and Kusto schema from `docs/data_schema.md`.

### Phase 4 Gate

- [ ] `.github/copilot-instructions.md` exists (< 100 lines)
- [ ] 4 instruction files in `.github/instructions/` with valid frontmatter
- [ ] 4 skill folders in `.github/skills/` with valid SKILL.md + references
- [ ] No duplicate content between agent body and skills (agent body references skills, does not inline methodology)
- [ ] All `name` fields in SKILL.md match their folder names exactly
- [ ] Narrative style guidelines extracted from SYSTEM_PROMPT to instructions
- [ ] Distribution pattern rubric extracted to skill (not in agent body)
- [ ] Business context extracted to skill (replaces `get_business_context` tool)

**Estimated effort**: 3-4 hours

---

## Phase 5: Multi-Agent Orchestration (Stretch Goal)

**Goal**: Explore multi-agent patterns using the Copilot Customization Framework. This is NOT required for parity with the current pipeline but demonstrates the framework's orchestration capabilities.

### Option A: Coordinator-Worker Pattern

A coordinator agent delegates to dimension-specific worker subagents:

**File**: `.github/agents/performance-coordinator.agent.md`
```yaml
---
name: Performance Coordinator
tools: ['agent', 'read']
agents: ['Geo-Analyst', 'Segment-Analyst', 'Role-Analyst', 'SolArea-Analyst', 'Report-Synthesizer']
---
```

**Workers**: 4 dimension analysts (each with restricted tools) + 1 report synthesizer.

Benefit: Each dimension analyst runs in its own context window. Parallel execution. Matches the multi-agent architecture already designed in `docs/AI_AGENT_IMPROVEMENTS.md`.

### Option B: Handoff Pipeline Pattern

Plan → Implement → Validate with user review gates:

```
Planner agent (read-only, researches data)
  → [Handoff: "Start Analysis"]
    → Performance Insights agent (full tools, generates report)
      → [Handoff: "Validate Report"]
        → Reviewer agent (read-only, checks report quality)
```

### Option C: Solution Area Agent

**File**: `.github/agents/solution-area-insights.agent.md`

A separate agent configured for SA analysis (3 dimensions instead of 4, SA as filter, product-level + bucket drill-down). Matches `solution_area_pipeline.py`.

### Phase 5 Deliverable

Pick ONE option and implement it. Recommended: **Option A** (Coordinator-Worker) — it directly maps to the multi-agent architecture already documented in `ARCHITECTURE_COMPARISON.md` and validates a real orchestration pattern.

**Estimated effort**: 4-6 hours

---

## Phase 6: Validation and Comparison

**Goal**: Verify the migrated framework produces output comparable to the current pipeline and that no regressions are introduced.

### Task 6.1: End-to-End Test with DEBCUPP

Run a complete analysis through Copilot Chat:
```
Select "Performance Insights" agent → "Analyze DEBCUPP for period 202601"
```

**Validation criteria**:
- [ ] Agent identifies itself with correct persona
- [ ] `load_leader_data` called first and succeeds
- [ ] All 4 dimensions analyzed (8 detect calls made)
- [ ] Phase 2 drill-downs produce 8+ calls
- [ ] Role context fetched for role hotspots
- [ ] `validate_report` called and passes
- [ ] Final output is valid JSON matching report_schema.json
- [ ] Executive summary has required sections and bullet counts
- [ ] P1 hotspots have non-empty root_causes
- [ ] Data references present throughout

### Task 6.2: Output Quality Comparison

Compare Copilot-generated report against the latest current-pipeline report for DEBCUPP.

| Metric | Current Pipeline (gpt-5.2) | Copilot Framework (GPT-4.1) | Acceptable? |
|---|---|---|---|
| Hotspots detected (total) | ? | ? | Within ±5 |
| P1 hotspots with root_causes | ? | ? | 100% coverage |
| Dimensions covered | 4 | 4 | Must be 4 |
| JSON valid | Yes | ? | Must be Yes |
| Executive summary quality | Baseline grade | ? | B or better |
| Tone compliance (collaborative) | Yes | ? | Must match guidelines |
| Factual accuracy (numbers match tools) | Yes | ? | Must be Yes |
| Distribution pattern insights | Yes | ? | At least 1 per dimension |
| Temporal trends mentioned | Yes | ? | When data available |

### Task 6.3: Verify Existing Tests Still Pass

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest tests/ -v
```

The existing 201 tests exercise the tool modules directly. Since we copied (not moved) the modules, all tests should continue to pass.

**Checkpoint 6.3**: 201/201 tests pass. No regressions.

### Task 6.4: Add MCP Server Tests

Create `tests/test_mcp_server.py` with:
- Server starts without error
- `load_leader_data` with valid leader returns success with correct benchmark
- `load_leader_data` with invalid leader returns error
- `detect_highlights` without loading data returns error
- `detect_highlights` after loading returns valid structure with expected fields
- `validate_report` with valid report returns "pass"
- `validate_report` with missing dimension returns "fail"
- Tool return types are all dicts (not raw strings)

**Checkpoint 6.4**: MCP server tests pass.

### Task 6.5: Second Leader Test (NICKPA)

Repeat Task 6.1 with NICKPA (smaller org: 2,873 people vs 22,183) to verify the flow works for different org sizes.

**Checkpoint 6.5**: NICKPA end-to-end produces valid report.

### Task 6.6: Update Project README.md

Add a section documenting the new Copilot agent invocation method alongside the existing CLI method.

### Phase 6 Gate (Migration Complete)

- [ ] DEBCUPP end-to-end produces valid report
- [ ] NICKPA end-to-end produces valid report
- [ ] 201 existing tests pass
- [ ] MCP server tests pass
- [ ] Output quality is B-grade or better
- [ ] README updated with Copilot invocation instructions
- [ ] No orphan scripts
- [ ] Branch committed with incremental conventional commits

**Estimated effort**: 5-7 hours

---

## Milestones and Checkpoints

| Milestone | Definition of Done | Phase | Gate Criteria |
|---|---|---|---|
| **M1: MCP Server Operational** | All 9 tools callable via MCP Inspector. DEBCUPP data loads, all analysis tools return valid results, validate_report works. | Phase 1 | Checkpoint 1.8 (14 verification items) |
| **M2: Agent Defined** | `.agent.md` complete with persona, 3-phase workflow, tool docs, output format, and all SYSTEM_PROMPT sections redistributed. Under 350 lines. | Phase 2 | Checkpoint 2.9 (11 verification items) |
| **M3: VS Code Wired** | MCP server starts from VS Code. Agent invocation triggers tool flow end-to-end. | Phase 3 | Checkpoint 3.4 |
| **M4: Framework Complete** | Instructions and skills created. Coding standards, methodology, business context, and schema in framework format. | Phase 4 | Phase 4 Gate (8 verification items) |
| **M5: Multi-Agent (Stretch)** | One orchestration pattern implemented and tested. | Phase 5 | One pattern works end-to-end |
| **M6: Validated** | Two leaders tested. Output quality comparable. All tests pass. README updated. | Phase 6 | Phase 6 Gate (8 verification items) |

### Progress Tracking

| Phase | Status | Started | Completed | Notes |
|---|---|---|---|---|
| Phase 1: MCP Server | NOT STARTED | - | - | - |
| Phase 2: Agent Definition | NOT STARTED | - | - | - |
| Phase 3: VS Code Integration | NOT STARTED | - | - | - |
| Phase 4: Instructions and Skills | NOT STARTED | - | - | - |
| Phase 5: Multi-Agent (Stretch) | NOT STARTED | - | - | - |
| Phase 6: Validation | NOT STARTED | - | - | - |

---

## Architectural Decisions

### D1: Copilot Model vs Current Model

**Current**: gpt-5.2-chat on Azure AI Foundry. Rate limit 601K TPM / 6K RPM. Sequential tool calls (1 per iteration). $0.00125/1K input, $0.01/1K output.

**New**: GPT-4.1 (or Claude Sonnet 4.5, or o4-mini) via Copilot Chat. Model selected in `.agent.md` frontmatter. Copilot manages rate limits. We do not control temperature or `max_completion_tokens`.

**Risk**: GPT-4.1 may not produce the same quality as gpt-5.2-chat. The ~550-line system prompt was heavily tuned for gpt-5.2 behavior, including sequential tool calling patterns and JSON output formatting.

**Mitigation**: Test multiple models in Phase 6 (GPT-4.1, Claude Sonnet 4.5, o4-mini). Keep current pipeline as production fallback. Model can be swapped in frontmatter without code changes.

### D2: State Management — Lazy Init via Tool Call

**Decision**: MCP server holds state in a module-level `ServerState` dataclass. `load_leader_data` tool initializes state. All other tools check `state.analyzer is not None`.

**Alternative considered**: Pass leader/period as env vars in `.vscode/mcp.json` and auto-load on server startup. Rejected because this couples the server to a single leader, making interactive multi-leader exploration impossible.

**Consequence**: Agent must call `load_leader_data` before any analysis. Agent body documents this prominently. `validate_report` tool checks if data was loaded.

### D3: Copy vs Symlink Tool Modules

**Decision**: COPY tool modules into `mcp-server/tools/`. Fix internal imports to use relative paths.

**Alternative considered**: Symlink or `sys.path` manipulation. Rejected: symlinks are fragile on Windows, `sys.path` manipulation is brittle.

**Consequence**: Two copies exist. Changes to analysis logic must be made in both places. Longer-term: consolidate by making one set canonical.

### D4: No Iteration Budget Enforcement

**Decision**: Accept that Copilot Chat manages its own tool loop. We cannot enforce "28 required tool calls before generating JSON."

**Mitigation**: 
1. Agent body describes 3-phase workflow with explicit call counts ("8 detect calls", "12+ drill-downs")
2. Agent body includes checklist: "Before generating JSON, verify..."
3. `validate_report` tool catches structural gaps
4. Stop hook (Phase 4) can block completion if validation fails

**Risk**: Agent may skip dimensions or generate output prematurely. Monitor in Phase 6 testing. If severe, add more explicit tool-call counts to the prompt or consolidate tools (e.g., a single `full_discovery` tool that runs all 8 detect calls at once).

### D5: Backward Compatibility

**Decision**: Current pipeline remains fully operational. Batch processing (184 leaders) continues using existing architecture. The Copilot framework is an ADDITION, not a replacement.

**Consequence**: Project has two parallel paths for generating reports. Intentional for exploration phase. If viable, deprecate old path later.

### D6: MCP Server Transport

**Decision**: Use stdio transport (default). VS Code connects to MCP server via stdin/stdout.

**Alternative**: HTTP transport for remote access. Not needed (single developer, local VS Code).

### D7: Impact Score Enrichment

**Decision**: Include `relative_impact_pct`, `gap_contribution_pct`, and `org_share` directly in the `detect_highlights` and `detect_lowlights` tool return values.

**Alternative**: Post-processing MCP tool `enrich_report(report_json)`. Rejected because it adds an extra tool call and the data is already available in `SimplifiedAggregator`.

**Consequence**: The agent receives impact scores as part of hotspot data and includes them in the JSON output naturally. No need for `_enrich_dimensions_with_impact_scores()` post-processing.

### D8: `get_business_context` Tool → Skill

**Decision**: Replace the `get_business_context` tool with a `.github/skills/business-context/` skill. The AI auto-loads the skill when writing the final report (progressive disclosure).

**Alternative**: Keep as MCP tool. Rejected because:
1. The content is static reference material (glossary, examples, framework), not dynamic data
2. Skills load on-demand without consuming a tool call
3. Matches the framework philosophy: tools for dynamic data, skills for reference knowledge

**Consequence**: Agent no longer needs to call a tool for business context. Content is available whenever the AI determines it's relevant. Saves 1 tool call per run.

### D9: Validation Approach

**Decision**: Three-layer validation replacing the current Python post-processing:
1. **Agent body checklist**: "Before generating JSON, verify..." (prompt-level)
2. **`validate_report` MCP tool**: Agent calls to self-check (tool-level)
3. **Stop hook (optional)**: Blocks completion if validation not run (enforcement-level)

**Alternative**: Accept no validation (let the model handle it). Rejected — the current 5A/5B/5C validation catches real issues (missing dimensions, empty root_causes).

**Trade-off**: We lose the ability to auto-execute missing tool calls (5B/5C currently auto-fills gaps). In the Copilot framework, if the agent missed a dimension, `validate_report` can tell it what's missing, but the agent must decide whether to go back and fix it.

---

## Risk Assessment

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | GPT-4.1 quality gap vs gpt-5.2-chat for this specific task | Medium | High | Test multiple models. Keep current pipeline as production fallback. |
| R2 | Agent skips dimensions without iteration budget enforcement | High | High | Strong prompt guidance with checklists. `validate_report` tool catches gaps. Stop hook for enforcement. |
| R3 | Agent generates output prematurely (before sufficient tool calls) | High | High | Explicit "do not generate JSON until..." instructions. `validate_report` rejects incomplete reports. |
| R4 | Large agent body (~250 lines) gets ignored or partially read by model | Medium | High | Split: core workflow in agent body, reference detail in skills. Test with progressively shorter bodies. |
| R5 | MCP server state management issues | Low | Low | Single-user VS Code scenario. Singleton state. Stateless requests after init. |
| R6 | Import path issues after copying tool modules | Medium | Low | Thorough testing in Task 1.2. Fix all imports before proceeding. |
| R7 | Two copies of tool modules diverge over time | Medium | Medium | Short-term: accept duplication. Long-term: make one canonical, have the other import. |
| R8 | MCP tool return sizes too large for Copilot context | Low | Medium | Current returns are compact dicts. `detect_highlights` returns ~5 items. `drill_down` returns < 20 plans. Monitor. |
| R9 | Batch pipeline (184 leaders) cannot use Copilot framework | Expected | Low | By design. Batch pipeline stays on current architecture. Copilot is for interactive single-leader analysis. |
| R10 | Loss of 5B/5C auto-execution (auto-filling missed tool calls) | Medium | Medium | `validate_report` tells agent what's missing. Agent must self-correct. Prompt must be explicit about this. |
| R11 | Skills not loading when expected (progressive disclosure failure) | Low | Medium | Verify SKILL.md descriptions match task context. Test in Phase 4. |
| R12 | No `tool_choice="required"` equivalent in Copilot | High | Medium | Strongest possible prompt language: "You MUST call tools. Do NOT generate text without data." |
| R13 | JSON output truncated (current fix: `max_completion_tokens=8000`) | Medium | High | Cannot control `max_completion_tokens` in Copilot. If truncation occurs, reduce output verbosity or split into multiple responses. |
| R14 | Copilot Chat cannot sustain 25-30 sequential tool calls | Medium | High | Critical test in Phase 3/6. If Copilot caps turns, consolidate tools (e.g., `full_discovery` runs all 8 detect calls at once). |

---

## What Stays, What Goes, What Is New

### Stays (Backward Compatibility)

| Component | Reason |
|---|---|
| `reasoning_agent/single_agent_pipeline.py` | Batch pipeline depends on it. Production reports. |
| `reasoning_agent/batch_pipeline.py` | 184-leader batch runs. Not a Copilot use case. |
| `reasoning_agent/solution_area_pipeline.py` | SA-specific reports. Phase 5 stretch may add agent equivalent. |
| `reasoning_agent/batch_solution_area_pipeline.py` | 15-SA batch runs. |
| `tools/*.py` (all modules) | Used by batch pipeline. Tests reference them. |
| `config/*.json` (all configs) | Referenced by both old and new paths. |
| `data/raw/**` | Parquet data. Both paths read from it. |
| `tests/*.py` | Validates tool logic. Shared by both paths. |
| `evals/` | Evaluation framework. Can test both paths. |
| `docs/*.md` | Project documentation. Unaffected. |
| `Dashboard.py` | Streamlit demo. Unaffected. |

### Goes (Replaced or Not Needed)

| Component | Replacement | When to Remove |
|---|---|---|
| `agent.yaml` | `.github/agents/performance-insights.agent.md` | After validation. Keep as historical artifact initially. |
| `tools/foundry_client.py` (for interactive use) | Copilot Chat native LLM client | Only if batch pipeline is also migrated (not planned). Stays for now. |
| `tools/foundry_memory_manager.py` (for interactive use) | Copilot Chat native conversation state | Same as above. |
| `get_business_context` tool | `.github/skills/business-context/` skill | Removed from MCP server tool list. |

### New (Created by Migration)

| Component | Purpose |
|---|---|
| `mcp-server/pyproject.toml` | MCP server project configuration |
| `mcp-server/server.py` | FastMCP server (9 tools + resources) |
| `mcp-server/tools/*.py` | Copies of analysis modules with adjusted imports |
| `.github/agents/performance-insights.agent.md` | Copilot agent definition (main) |
| `.github/copilot-instructions.md` | Global project rules |
| `.github/instructions/*.instructions.md` | Scoped rules (4 files) |
| `.vscode/mcp.json` | MCP server registration for VS Code |
| `.github/skills/performance-methodology/` | Methodology reference skill |
| `.github/skills/business-context/` | WWIC glossary, examples, recommendations skill |
| `.github/skills/report-schema/` | JSON Schema reference skill |
| `.github/skills/data-schema/` | Data schema reference skill |
| `tests/test_mcp_server.py` | MCP server tests |
| `.github/agents/solution-area-insights.agent.md` | SA analysis agent (Phase 5, optional) |
| `.github/agents/performance-coordinator.agent.md` | Orchestrator agent (Phase 5, optional) |

---

## Open Questions

| # | Question | Context | Status | Resolution |
|---|---|---|---|---|
| Q1 | Can Copilot Chat sustain 25-30 sequential tool calls? | Current workflow needs 8 discovery + 12 drill-downs + 4 role-context + 4 distribution + 1 validation = ~29 calls. If Copilot caps earlier, we may need to consolidate tools. | OPEN | Critical test in Phase 3/6. Fallback: create `full_discovery` tool that runs all 8 detect calls at once. |
| Q2 | What is the effective agent body length limit? | Current SYSTEM_PROMPT is ~550 lines. Agent body target is ~250 lines. If Copilot truncates long bodies, move more to skills. | OPEN | Test in Phase 2 with full-length agent. Shorten progressively if issues arise. |
| Q3 | Does the `model` field in `.agent.md` frontmatter control the model? | Or does Copilot always use its default? | OPEN | Test in Phase 3 with different model values. |
| Q4 | How does JSON truncation manifest in Copilot? | Currently mitigated with `max_completion_tokens=8000`. Cannot set this in Copilot. | OPEN | Test with DEBCUPP (22K people, large output). If truncated, reduce output verbosity or split. |
| Q5 | Can we use the project's `.venv` for the MCP server? | Want to avoid separate env. MCP's only new dep is `mcp[cli]`. | OPEN | Test in Phase 3 Task 3.2. Expected to work. |
| Q6 | How do distribution metrics (CV, skewness, kurtosis) appear in tool returns? | Currently enriched at Python level. Need to verify they flow through MCP wrappers as-is. | OPEN | Verify in Phase 1 Task 1.4. Expected to be in the existing tool return dicts. |
| Q7 | How to handle `_enrich_dimensions_with_impact_scores()` post-processing? | See Decision D7. Preferred: include scores in tool returns. Need to verify `SimplifiedAggregator` produces them. | OPEN | Verify in Phase 1 Task 1.4. |
| Q8 | Will the knowledge base guardrails (~1.5K tokens) inline in the agent body make it too long? | Currently appended to SYSTEM_PROMPT at runtime. In the new framework, they'd be in the agent body or a scoped instruction. | OPEN | If agent body exceeds 350 lines, move guardrails to an always-on instruction file. |
| Q9 | Can MCP resources be accessed by the agent automatically? | Or does the agent need to explicitly request them? | OPEN | Test in Phase 3. Resources may need to be added via "Add Context > MCP Resources." |
| Q10 | How does Copilot handle the user prompt with leader-specific context? | Currently, `SingleAgentPipeline.run()` builds a user prompt with leader, period, benchmark, population. In Copilot, the user just types "Analyze DEBCUPP." The agent must call `load_leader_data` to get this context. | OPEN | Verify the agent reliably calls `load_leader_data` first. If not, add even stronger prompt guidance. |

---

## Effort Summary

| Phase | Description | Estimated Hours | Dependencies |
|---|---|---|---|
| Phase 1 | MCP Server Foundation (9 tools + resources) | 10-14 | None |
| Phase 2 | Agent Definition (.agent.md) | 4-6 | Phase 1 (need tool names/signatures) |
| Phase 3 | VS Code Integration | 2-3 | Phase 1 + Phase 2 |
| Phase 4 | Instructions and Skills | 3-4 | Phase 2 (need to know what's NOT in agent body) |
| Phase 5 | Multi-Agent Orchestration (stretch) | 4-6 | Phase 3 (need working single agent first) |
| Phase 6 | Validation and Comparison | 5-7 | Phase 1-4 all complete |
| **Total** | | **28-40 hours** | |

Phases 1 and 2 can be partially parallelized (agent body written while MCP server is being tested). Phase 4 can overlap with Phase 3 testing.

---

## Progress Log

### March 5, 2026 — Planning Complete

- Created MIGRATION-PLAN-PERFORMANCE-INSIGHTS.md (this document)
- Completed full inventory: 7 existing tools + 2 new + 1 removed
- Mapped all ~550 lines of SYSTEM_PROMPT to destinations (agent body, skills, instructions)
- Identified 9 architectural decisions with alternatives
- Assessed 14 risks
- Identified 10 open questions
- Estimated total effort: 28-40 hours across 6 phases
- Key insight: The `get_business_context` tool becomes a skill (saves 1 tool call per run)
- Key insight: The validation workstream (5A/5B/5C) becomes a self-check tool + Stop hook
- Key concern: 25-30 sequential tool calls may exceed Copilot Chat's turn limit (Q1)

**Next action**: Create branch `feat/copilot-framework-migration` from updated `main` and begin Phase 1 (MCP Server Foundation).

---

*Cross-references*:
- Current pipeline: `reasoning_agent/single_agent_pipeline.py`
- Architecture docs: `docs/SYSTEM_ARCHITECTURE_GUIDE.md`
- Methodology: `docs/HOTSPOT_METHODOLOGY.md`
- Agent improvements: `docs/AI_AGENT_IMPROVEMENTS.md`
- Architecture comparison: `docs/ARCHITECTURE_COMPARISON.md`
- Copilot Framework reference: `Microsoft-VS-Code/DEEP-DIVE-CHEATSHEET.md`
- Task inventory: `docs/TASK_INVENTORY.md`
- Branch tracking: `docs/VERSIONS.md`
