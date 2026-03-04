# Knowledge Sources

> **TL;DR:** Knowledge sources ground your agent's responses in real data instead of hallucination. Copilot Studio supports public websites, uploaded documents, SharePoint, Dataverse, and enterprise connectors. The source type, orchestration mode, and content moderation level all affect what the agent can find and how it responds.

---

## Why Knowledge Sources Matter

Without knowledge sources, your agent relies on either:
- **Authored topic responses** — manually written answers (don't scale)
- **General knowledge** — the LLM's training data (can hallucinate, not enterprise-specific)

Knowledge sources let the agent **search, retrieve, and cite** your actual data. This is the foundation of accurate enterprise AI agents.

---

## Knowledge Source Types

### 1. Public Websites

| Attribute | Detail |
|---|---|
| **How it works** | Bing-powered web search scoped to specified URLs |
| **URL limit** | Varies by orchestration mode (see limits table below) |
| **Best for** | Public-facing documentation, help sites, product pages |
| **Authentication** | None (public content only) |
| **Indexing** | Real-time search (no pre-indexing needed) |

**Setup:**
1. Knowledge → Add knowledge → Public websites
2. Enter URLs (e.g., `https://docs.contoso.com`)
3. Bing searches within those URLs at query time

**Tips:**
- Use specific base URLs, not broad domains
- Ensure pages are Bing-indexed (check with `site:yourdomain.com` in Bing)
- Content changes reflect quickly (no manual refresh needed)

### 2. Uploaded Documents (Files)

| Attribute | Detail |
|---|---|
| **How it works** | Documents are indexed in Dataverse |
| **Supported formats** | PDF, Word (.docx), Excel, PowerPoint, HTML, plain text |
| **Size limit** | Up to 512 MB per file (varies by plan) |
| **Best for** | Internal documents, FAQ sheets, policy manuals |
| **Authentication** | Maker-provided (anyone using the agent can access) |
| **Indexing** | Pre-indexed on upload, stored in Dataverse |

**Setup:**
1. Knowledge → Add knowledge → Files
2. Upload documents
3. Wait for indexing to complete (progress bar shown)

**Tips:**
- Break large documents into smaller, focused files for better retrieval
- Use clear headings and structure — the indexer follows document hierarchy
- Uploaded files do NOT count against the knowledge source limits

### 3. SharePoint

| Attribute | Detail |
|---|---|
| **How it works** | Microsoft Graph Search queries SharePoint content |
| **Best for** | Enterprise knowledge bases, team sites, shared documents |
| **Authentication** | End-user credentials (respects SharePoint permissions) |
| **Indexing** | Uses Microsoft Search index (already maintained by M365) |

**Setup:**
1. Knowledge → Add knowledge → SharePoint
2. Enter SharePoint site URL(s)
3. Agent will search content the current user has access to

**Tips:**
- Users only see content they're authorized for — this is a feature, not a bug
- If content isn't found, check that the SharePoint site is indexed by Microsoft Search
- SharePoint list items, pages, and documents are all searchable

### 4. Dataverse

| Attribute | Detail |
|---|---|
| **How it works** | Searches Dataverse tables using semantic search |
| **Best for** | CRM data, business records, custom tables with text content |
| **Authentication** | End-user credentials (respects Dataverse security roles) |
| **Indexing** | Auto-indexed via Dataverse search |
| **Limit** | Up to specific number of tables per orchestration mode |

**Setup:**
1. Knowledge → Add knowledge → Dataverse
2. Select the table(s)
3. Choose which columns to include in search

**Tips:**
- Works best with tables that have rich text content (descriptions, notes, articles)
- Ensure Dataverse search is enabled for the environment
- Column selection matters — include the columns with the actual knowledge content

### 5. Enterprise Data (Microsoft Graph Connectors)

| Attribute | Detail |
|---|---|
| **How it works** | Searches content indexed by Microsoft Graph connectors |
| **Best for** | ServiceNow, Salesforce, Confluence, and other external systems indexed via Graph |
| **Authentication** | End-user credentials |
| **Indexing** | Managed by the Graph connector configuration |

**Setup:**
1. Knowledge → Add knowledge → Enterprise data
2. Select configured Graph connectors
3. Agent searches the connector's indexed content

**Tips:**
- Requires Graph connectors to be set up by an admin first
- Powerful way to bring external data into Copilot Studio without direct integration

---

## Knowledge Limits by Orchestration Mode

| Source Type | Generative Orchestration | Classic Orchestration |
|---|---|---|
| **Public websites** | Up to 25 (combined with other sources) | Up to 4 URLs |
| **SharePoint** | Up to 25 (combined) | Up to 4 SharePoint sources |
| **Dataverse** | Up to 25 (combined) | Up to 2 Dataverse sources |
| **Enterprise connectors** | Up to 25 (combined) | Up to 2 sources |
| **Uploaded documents** | No limit (don't count) | No limit (don't count) |

> **Note:** In generative orchestration, the total of all source types combined can be up to 25. Uploaded documents are excluded from this count.

---

## Additional Knowledge Settings

### Web Search (Bing)

- **Optional:** Enable/disable at the agent level
- **Behavior:** Agent can search the open web via Bing for answers
- **Use when:** You want the agent to answer general questions beyond your configured sources
- **Caution:** May surface content outside your control — test thoroughly

### General Knowledge

- **Optional:** Enable/disable at the agent level
- **Behavior:** Agent uses the LLM's foundational training data to answer
- **Use when:** You want the agent to handle general knowledge questions
- **Caution:** Can hallucinate; no citations available for general knowledge answers

### Tenant Graph Grounding with Semantic Search

- Available when the agent extends Microsoft 365 Copilot
- Searches across the M365 tenant's Graph-indexed content
- Respects user permissions throughout

---

## Content Moderation

Controls how strictly the agent filters responses generated from knowledge:

| Level | Behavior |
|---|---|
| **Lowest** | Most permissive — agent answers more broadly |
| **Low** | Default for most scenarios |
| **Medium** | Moderate filtering |
| **High** | Strict — may refuse to answer edge cases |
| **Highest** | Most restrictive — may significantly reduce answer volume |

**Trade-off:** Higher moderation → fewer hallucination risks, but more "I can't answer that" responses.

---

## Knowledge Source Selection Guide

| Your Situation | Recommended Source |
|---|---|
| Static FAQ documents | **Uploaded files** — simple, no permissions complexity |
| SharePoint-based knowledge base | **SharePoint** — leverages existing M365 Search, respects permissions |
| CRM or business records | **Dataverse** — direct table search with security roles |
| External documentation site | **Public website** — Bing-powered, always up to date |
| ServiceNow / Confluence content | **Enterprise connector** — via Microsoft Graph connectors |
| Need all of the above | **Combine** — use multiple source types (stay within limits) |

---

## Troubleshooting Knowledge

| Problem | Possible Cause | Solution |
|---|---|---|
| Agent says "I don't know" for questions you expect it to answer | Source not indexed, bad content structure, wrong content moderation level | Check indexing status; restructure content with clear headings; lower moderation |
| Wrong answers | Content is ambiguous or sources conflict | Improve source content quality; remove conflicting sources; add more specific documents |
| Slow responses | Too many sources searched | Reduce source count; make sources more focused |
| User can't see content they should | SharePoint/Dataverse permissions | Verify user has access to the content in the source system |
| Citations missing | General knowledge used (not knowledge sources) | Ensure knowledge sources contain the relevant content |

---

## Next Steps

- **[Tools and Actions](tools-and-actions.md)** — Add actions your agent can perform
- **[Knowledge Source Matrix](../06-tipsheets/knowledge-source-matrix.md)** — Quick reference for choosing sources
- **[Platform Limits](../07-limitations-and-gotchas/platform-limits.md)** — Full limits reference

---

*Sources: [Microsoft Learn — Knowledge in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio), [Microsoft Learn — Create and Edit Topics](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-create-edit-topics)*
