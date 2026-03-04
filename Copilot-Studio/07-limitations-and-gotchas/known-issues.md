# Known Issues and Gotchas

> Real-world friction points, workarounds, and things the documentation doesn't emphasize enough. Updated as new issues are discovered.

---

## Generative Orchestration Gotchas

### Tool Routing Accuracy

**Issue:** With many tools (30+), the AI may invoke the wrong tool or fail to invoke any tool.

**Why:** Generative orchestration reads tool descriptions to decide. Similar descriptions confuse the router.

**Workarounds:**
- Keep tool count to 25-30
- Write highly specific, differentiated descriptions
- If tools overlap conceptually, merge them or add disambiguation in descriptions
- Test routing systematically — create a spreadsheet of test queries and expected tool matches
- Use multi-agent pattern to separate tool domains

### Topic Selection Conflicts

**Issue:** AI selects a topic when a tool would be better (or vice versa).

**Why:** Topic descriptions and tool descriptions compete for the same user intent.

**Workaround:** Make topic descriptions and tool descriptions clearly distinct. If a topic exists for a specific workflow and a tool exists for a similar action, clarify in descriptions when each should be used.

---

## Knowledge Source Gotchas

### Stale SharePoint Content

**Issue:** Agent doesn't find recently updated SharePoint content.

**Why:** SharePoint knowledge relies on Microsoft Search indexing, which isn't instant.

**Workaround:** Wait for M365 Search to re-index (typically minutes to hours). For critical updates, consider also uploading the document directly.

### Large Document Retrieval Quality

**Issue:** Agent gives partial or inaccurate answers from very large documents.

**Why:** Retrieval chunks from large documents may not capture the full context needed.

**Workarounds:**
- Break large documents into smaller, focused files (one topic per file)
- Add clear headings and structure for better chunking
- Include Q&A pairs in documents — direct matches produce best results
- Test with specific questions and refine content structure based on results

### Permission-Based Knowledge Gaps

**Issue:** Agent says "I don't know" for content that exists in SharePoint/Dataverse.

**Why:** End-user auth means the agent can only find content the user has access to.

**Workaround:** This is by design (security feature). If users need access to content, update permissions in the source system. For content that all users should see, upload it as a document (maker-provided, no permissions).

---

## Authentication Gotchas

### OAuth Token Expiry

**Issue:** Tools fail mid-conversation with auth errors.

**Why:** OAuth tokens expire; long conversations may outlast the token lifetime.

**Workaround:** Handle auth errors gracefully in your topic flows. Add a retry mechanism or ask the user to try again.

### Connection Sharing

**Issue:** Maker-provided connections use the maker's credentials — if the maker leaves or their permissions change, all agents using that connection break.

**Workaround:** Use a service account for maker-provided connections. Document which agents use which connections. Set up monitoring for connection health.

---

## Conversation Design Gotchas

### Context Window Limitations

**Issue:** In long conversations, earlier context gets dropped, leading to surprising behavior.

**Why:** LLMs have finite context windows. Very long multi-turn conversations may exceed them.

**Workarounds:**
- Design conversations to be concise
- Use variables to store critical information rather than relying on conversation history
- For complex workflows, collect all needed info early in the flow
- Add "conversation summary" at key points in long flows

### Ambiguous User Input

**Issue:** Users provide vague requests ("help me with that thing") and the agent guesses wrong.

**Workarounds:**
- Add clarification questions for ambiguous intents
- Use Multiple Topics Matched system topic to let users choose
- Design the greeting topic to set expectations about what the agent can do
- Provide quick reply buttons for common next actions

---

## Deployment Gotchas

### Trial Environment Expiry

**Issue:** Trial environments are deleted after 30 days, including all agents.

**Workaround:** Convert to production BEFORE the 30-day mark. Export solutions as backup. Never build production-critical agents in trial environments.

### Teams Admin Approval

**Issue:** Publishing to Teams requires admin approval in many tenants. This can take days.

**Workaround:** Start the approval process early. Communicate with your Teams admin about timelines. Use the demo website channel for testing while awaiting approval.

### Channel-Specific Behavior

**Issue:** Agent behavior differs between channels (Teams vs web vs M365 Copilot).

**Why:** Each channel has different UX capabilities and message formatting.

**Workaround:** Test in each target channel. Adaptive Cards may render differently. Message length limits vary. Some rich content may not display in all channels.

---

## Fabric / MCP Gotchas

### Query Complexity

**Issue:** Fabric Data Agent generates incorrect or overly complex SQL/DAX for nuanced analytical questions.

**Why:** Natural language → SQL/DAX translation has limits, especially for multi-join, window function, or complex aggregation queries.

**Workarounds:**
- Write clear agent instructions with example query patterns
- Pre-create views or stored procedures for common complex queries
- Add column descriptions and table documentation to help the translator
- Test with representative questions and refine instructions based on failures

### MCP Latency

**Issue:** MCP tool calls add noticeable latency (2-5+ seconds per call).

**Why:** Chain: Studio → MCP server → backend data source → response → back.

**Workaround:** Acceptable for conversational flows. Set user expectations ("Let me look that up..."). For sub-second responses, consider caching or pre-computed results.

### Fabric Data Agent Instruction Limits

**Issue:** 15,000 character instruction limit may not cover complex schemas with many tables.

**Workaround:** Focus instructions on the most common query patterns. Group related tables. Use naming conventions that are self-documenting. Prioritize the top 10-15 query scenarios.

---

## General Platform Gotchas

### Analytics Lag

**Issue:** Analytics dashboard doesn't reflect recent sessions immediately.

**Workaround:** Wait 1-2 hours for analytics to catch up. Don't rely on real-time analytics for debugging — use the test chat and tracking feature instead.

### Solution Export/Import Inconsistencies

**Issue:** Importing a solution into a new environment occasionally has missing connections or configuration.

**Workaround:** Document all connections and environment variables. After import, verify all tools and connections are functional. Keep a deployment checklist.

### Generative AI Variability

**Issue:** The same question sometimes gets different answers or the agent sometimes fails to find content it found before.

**Why:** Generative AI is non-deterministic. Slight variations in phrasing, conversation history, or timing can affect results.

**Workaround:** 
- For critical responses, use authored topics (deterministic)
- Test extensively with natural variations of key questions
- Accept some variability for generative answers; focus on "good enough" rather than "exact"
- Use content moderation settings to narrow acceptable response range

---

## Issue Tracking

Use this section to track issues you encounter in your own projects:

| Date | Issue | Status | Resolution |
|---|---|---|---|
| *(add entries as you find issues)* | | | |

---

*Updated as new gotchas are discovered. For platform-managed limits, see [Platform Limits](platform-limits.md).*
