# Platform Limits

> Hard limits, soft limits, and practical boundaries. Know these before you scale.

---

## Agent Limits

| Limit | Value | Notes |
|---|---|---|
| **Tools per agent** | 128 max | Recommend 25-30 for optimal AI routing |
| **Knowledge sources (generative orch.)** | 25 total | Uploaded documents excluded from count |
| **Knowledge sources (classic orch.)** | 4 URLs, 4 SharePoint, 2 Dataverse, 2 enterprise connectors | Lower limits than generative |
| **Uploaded documents** | No hard limit on count | Per-file size limits apply |
| **Per-file upload size** | Up to 512 MB | Varies by plan |
| **Agent instructions** | 15,000 chars (Fabric Data Agent) | Studio agent limits may vary |
| **Topics per agent** | No documented hard limit | Performance degrades with excessive topics |
| **Trigger phrases per topic (classic)** | Recommend 5-10 | Too few = poor matching; too many = overlap |

---

## Environment and Tenant Limits

| Limit | Value | Notes |
|---|---|---|
| **Trial environments** | 30-day lifespan | Auto-deleted with all agents inside |
| **Agents per environment** | No documented hard limit | Use solution management for organization |
| **Environments per tenant** | Configured by admin | Power Platform admin controls |
| **Concurrent sessions** | Varies by license | Check your specific Copilot Studio plan |

---

## Knowledge Source Limits (Detail)

### Generative Orchestration

| Source Type | Count Limit | Notes |
|---|---|---|
| Public websites | Part of 25 total | Bing-powered search |
| SharePoint | Part of 25 total | Uses M365 Search index |
| Dataverse | Part of 25 total | Requires Dataverse search enabled |
| Enterprise connectors | Part of 25 total | Requires Graph connector setup |
| Uploaded documents | **Unlimited** | Stored in Dataverse |

### Classic Orchestration

| Source Type | Count Limit | Notes |
|---|---|---|
| Public websites | 4 URLs | Bing Custom Search support |
| SharePoint | 4 sources | — |
| Dataverse | 2 sources | — |
| Enterprise connectors | 2 sources | — |
| Custom data | Supported | API-based custom sources |
| Uploaded documents | **Unlimited** | — |

---

## Tool Limits (Detail)

| Aspect | Limit | Impact |
|---|---|---|
| Max tools per agent | 128 | Hit this → use multi-agent pattern |
| Recommended tools | 25-30 | Beyond this, AI routing accuracy degrades |
| Tool description length | Keep to 2-3 sentences | AI reads these for routing; concise > verbose |
| Agent flow complexity | Practical, not hard limit | Very complex flows increase latency |
| MCP server connections | No documented limit per agent | Latency increases with more servers |

---

## Channel Limits

| Channel | Limit / Note |
|---|---|
| Teams | Subject to Teams app policies and admin approval |
| Web embed | No hard limit; performance depends on hosting |
| M365 Copilot | Requires admin enablement per user/group |
| Facebook | Requires Facebook page and app configuration |

---

## Performance Considerations

| Factor | Impact | Mitigation |
|---|---|---|
| **Too many tools** | Slower routing, more errors | Keep to 25-30; split with multi-agent |
| **Too many knowledge sources** | Longer search time, potential noise | Focus sources; remove low-value ones |
| **Large uploaded documents** | Lower retrieval precision | Break into smaller, focused files |
| **Complex agent flows** | Higher latency per turn | Simplify flows; pre-compute where possible |
| **External API latency** | Slow responses | Choose fast endpoints; add timeouts |
| **Generative orchestration overhead** | Slightly slower than classic | Acceptable for most scenarios; use classic only if speed is critical |

---

## Licensing and Billing

| Component | Billing Model |
|---|---|
| **Copilot Studio license** | Per user/month or per tenant |
| **Messages** | Metered (varies by plan) |
| **Premium connectors** | May require additional licensing |
| **Power Automate** | Cloud flows may need their own license |
| **Agent flows** | Included with Copilot Studio (native flows) |
| **Fabric Data Agent** | Fabric capacity units |
| **M365 Copilot extension** | Requires M365 Copilot license for users |

> **Tip:** Use agent flows (native) instead of cloud flows when possible to avoid separate Power Automate licensing.

---

## Regional Availability

- Copilot Studio is available in most Azure regions
- Some features (generative orchestration, MCP) may have limited regional availability during rollout
- Data residency follows the Power Platform environment region
- Check [Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-copilot-studio/) for current regional availability

---

*Limits current as of research date. Always verify against [Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-copilot-studio/) for the latest.*
