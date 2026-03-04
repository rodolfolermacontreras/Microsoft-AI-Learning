# Knowledge Source Matrix

> Quick-reference for choosing the right knowledge source type. Scan the table, match your situation, done.

---

## Decision Matrix

| Factor | Public Websites | Uploaded Documents | SharePoint | Dataverse | Enterprise Connectors |
|---|---|---|---|---|---|
| **Content type** | Public web pages | PDFs, Word, Excel, PPT | Documents, pages, lists | Table records | External system content |
| **Content location** | Your public domain | Uploaded to Studio | SharePoint sites | Dataverse tables | ServiceNow, Confluence, etc. |
| **Freshness** | Real-time (Bing search) | Updated on re-upload | Uses M365 Search index | Auto-indexed | Depends on Graph connector sync |
| **Auth required** | None (public) | None (maker uploaded) | End-user (permissions) | End-user (security roles) | End-user |
| **Permission-aware** | No (public content) | No (everyone sees same) | **Yes** | **Yes** | **Yes** |
| **Setup complexity** | Low (paste URL) | Low (upload file) | Low (paste site URL) | Medium (select tables/columns) | High (Graph connector setup) |
| **Limit (gen. orch.)** | Part of 25 total | **No limit** | Part of 25 total | Part of 25 total | Part of 25 total |
| **Limit (classic)** | 4 URLs | No limit | 4 sources | 2 sources | 2 sources |
| **Best for** | Help sites, product docs | FAQ sheets, policy docs | Team knowledge bases | CRM data, business records | External SaaS content |

---

## Quick Selection Guide

### "I have internal documents..."

| Situation | Use |
|---|---|
| Few static documents (FAQ, policies, guides) | **Uploaded documents** — simplest, no permission complexity |
| Living documents on SharePoint | **SharePoint** — stays current, respects permissions |
| Both | Upload critical static docs + connect SharePoint for everything else |

### "I have structured data..."

| Situation | Use |
|---|---|
| Business records in Dataverse tables | **Dataverse** — direct search with security roles |
| Data in Fabric (Lakehouse/Warehouse) | **MCP** (Fabric Data Agent) — not a knowledge source, but a tool |
| Data in external system (ServiceNow, Salesforce) | **Enterprise connector** if Graph connector exists, otherwise **tool** via connector |

### "I have web content..."

| Situation | Use |
|---|---|
| Your organization's public website | **Public websites** — always current, Bing-powered |
| Third-party documentation | **Public websites** (if public) or **upload** key pages |
| Intranet (not public) | **SharePoint** or **upload** — not accessible via public web search |

---

## Combination Strategies

| Scenario | Recommended Stack |
|---|---|
| **General enterprise assistant** | SharePoint (main) + uploaded docs (critical policies) + Dataverse (business records) |
| **Customer-facing FAQ bot** | Public website (product docs) + uploaded docs (curated answers) |
| **Sales enablement** | SharePoint (playbooks) + Dataverse (CRM data) + enterprise connector (Salesforce) |
| **IT helpdesk** | Uploaded docs (IT procedures) + SharePoint (IT wiki) + enterprise connector (ServiceNow) |
| **Data analytics assistant** | Fabric Data Agent via MCP (primary) + uploaded docs (data dictionary, definitions) |

---

## Limits Quick Reference

### Generative Orchestration

```
Total knowledge sources: up to 25 (combined across types)
Uploaded documents:      unlimited (excluded from count)
```

### Classic Orchestration

```
Public websites:         up to 4 URLs
SharePoint:              up to 4 sources
Dataverse:               up to 2 sources
Enterprise connectors:   up to 2 sources
Uploaded documents:      unlimited
```

---

## Content Quality Tips

| Tip | Impact |
|---|---|
| Use clear headings and structure | Better retrieval — indexer follows document hierarchy |
| Break large docs into focused smaller ones | Reduces noise in search results |
| Remove outdated content | Prevents contradictory or stale answers |
| Add metadata and tags (SharePoint) | Improves search relevance |
| Keep language clear and direct | AI generates better answers from clear source material |
| Include Q&A pairs in documents | Direct matches produce the most accurate responses |

---

*For full details, see [Knowledge Sources](../02-agents/knowledge-sources.md)*
