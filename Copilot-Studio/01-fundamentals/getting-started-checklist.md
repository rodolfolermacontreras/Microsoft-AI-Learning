# Getting Started Checklist

> **TL;DR:** Go from zero to a working Copilot Studio agent in under an hour. This is your step-by-step checklist covering account setup, environment creation, first agent build, and initial testing.

---

## Prerequisites

- [ ] **Microsoft work or school account** (Microsoft Entra ID)
- [ ] **Copilot Studio license** — one of:
  - Copilot Studio trial (free, 30 days) → [Start free trial](https://go.microsoft.com/fwlink/?LinkId=2107702)
  - Copilot Studio paid license
  - Microsoft 365 Copilot license (for extending M365 Copilot)
- [ ] **Modern browser** (Edge, Chrome, Firefox)

---

## Step 1: Access Copilot Studio

1. Go to [https://copilotstudio.microsoft.com](https://copilotstudio.microsoft.com)
2. Sign in with your work account
3. You'll land on the **Home page** — your agent dashboard

> **Alternative:** For Teams-only bots, add the Copilot Studio app in Teams via [this link](https://aka.ms/PVATeamsApp). Note: the Teams app supports classic chatbots only.

- [ ] **Checkpoint:** You can see the Copilot Studio home page

---

## Step 2: Set Up Your Environment

An **environment** is the container where your agents, data, and flows live.

1. On first sign-in, a **default environment** is created automatically
2. For anything beyond testing, create a dedicated environment:
   - Go to [Power Platform Admin Center](https://admin.powerplatform.com)
   - Select **Manage → Environments → New**
   - Fill in:
     - **Name:** Something descriptive (e.g., "Copilot-Studio-Dev")
     - **Region:** Your data residency region
     - **Type:** Trial (for experiments) or Production (for real use)
     - **Dataverse data store:** Yes (required for most features)
   - Select **Save**
3. Wait for the environment to provision (1-3 minutes)
4. Return to Copilot Studio and switch to your new environment via the top menu bar

> **Tip:** Use a **production** environment for agents you plan to deploy. Trial environments expire after 30 days, deleting all agents within them.

- [ ] **Checkpoint:** You have at least one environment ready

---

## Step 3: Create Your First Agent

1. From the Copilot Studio home page, select **Create** (or **+ New agent**)
2. **Describe your agent** in natural language:
   - Example: "An IT helpdesk agent that answers questions about VPN access, password resets, and software installation from our IT knowledge base"
3. Studio will auto-generate:
   - Agent instructions
   - Initial topics
   - Suggested knowledge sources
4. Review and refine what was generated
5. Give your agent a **name** (e.g., "IT Helpdesk Assistant")
6. Select **Create**

- [ ] **Checkpoint:** Your agent exists and you can see its overview page

---

## Step 4: Add Knowledge

Ground your agent in real data so it answers accurately:

1. Go to your agent's **Knowledge** page
2. Select **+ Add knowledge**
3. Choose a source type:
   - **Public website** — enter a URL your org owns
   - **Files** — upload documents (PDF, Word, etc.)
   - **SharePoint** — paste a SharePoint site URL
   - **Dataverse** — select tables from your Dataverse instance
4. For your first agent, try **uploading a document** (FAQ sheet, policy doc, or knowledge base export)
5. Wait for indexing to complete

> **Quick test content:** If you don't have enterprise docs ready, upload a simple FAQ markdown file or use a public website URL.

- [ ] **Checkpoint:** At least one knowledge source is added and indexed

---

## Step 5: Test Your Agent

1. Select **Test** (or the test chat icon) in the bottom-left corner
2. Type a question related to your knowledge source
   - Example: "How do I reset my password?"
3. Observe:
   - Did the agent find relevant information?
   - Are citations shown?
   - Is the tone appropriate?
4. Try edge cases:
   - Questions outside the agent's scope
   - Ambiguous questions
   - Multi-turn follow-ups

- [ ] **Checkpoint:** Your agent responds with grounded answers from your knowledge source

---

## Step 6: Add a Tool (Optional but Recommended)

Give your agent the ability to take action, not just answer questions:

1. Go to your agent's **Tools** page
2. Select **Add a tool**
3. For a first tool, try a **prebuilt connector:**
   - Search for "Microsoft Teams" or "Outlook"
   - Select an action like "Send a message" or "Send an email"
4. Configure the tool:
   - Name and description (important for generative orchestration!)
   - Input parameters
   - After-running behavior
5. Select **Save**

- [ ] **Checkpoint:** Your agent has at least one tool and can use it when relevant

---

## Step 7: Publish to a Channel

1. Go to your agent's **Channels** page (or **Settings → Channels**)
2. For testing, start with the **Demo website** channel:
   - Copy the demo URL
   - Share with colleagues for feedback
3. When ready, publish to **Teams:**
   - Select Microsoft Teams
   - Follow the prompts to configure and submit
4. For web embedding:
   - Select the web channel
   - Copy the embed code to your site

- [ ] **Checkpoint:** Your agent is accessible outside of Copilot Studio

---

## Step 8: Review Analytics

After your agent has been used for a while:

1. Go to the **Analytics** page
2. Review:
   - **Session count** and engagement metrics
   - **Resolution rate** — how often the agent resolved the user's question
   - **Escalation rate** — how often users were handed off to humans
   - **Knowledge source metrics** — which sources are used most
3. Identify topics or questions that need improvement

- [ ] **Checkpoint:** You understand your agent's performance baseline

---

## Quick Setup Reference

| Step | Action | Time |
|---|---|---|
| 1. Access | Sign in to copilotstudio.microsoft.com | 2 min |
| 2. Environment | Create or select a Power Platform environment | 5 min |
| 3. Create | Describe and create your agent | 5 min |
| 4. Knowledge | Add at least one data source | 10 min |
| 5. Test | Verify responses in test chat | 10 min |
| 6. Tool | Add a connector or flow (optional) | 10 min |
| 7. Publish | Deploy to demo website or Teams | 5 min |
| 8. Analytics | Review initial metrics after some usage | 5 min |
| **Total** | | **~50 min** |

---

## Common First-Timer Issues

| Problem | Solution |
|---|---|
| "You do not have permissions to any environments" | Create a new environment in the [Power Platform Admin Center](https://admin.powerplatform.com) |
| Environment not showing in dropdown | Ensure it has a Dataverse database and is in a supported region |
| Agent not finding knowledge content | Check that indexing completed; verify the source URL or file is accessible |
| Trial environment expiring | [Convert to production](https://learn.microsoft.com/en-us/power-platform/admin/trial-environments#convert-a-trial-environment-to-production) before the 30-day mark |
| Can't publish to Teams | Ensure you have the right admin permissions; may need Teams admin approval |

---

## Next Steps After Your First Agent

1. **[Topics and Conversations](../02-agents/topics-and-conversations.md)** — Create custom topic flows beyond generative answers
2. **[Tools and Actions](../02-agents/tools-and-actions.md)** — Add more powerful tools (MCP, REST APIs, flows)
3. **[Agent Design Patterns](../02-agents/agent-design-patterns.md)** — Learn proven patterns for common scenarios
4. **[Platform Limits](../07-limitations-and-gotchas/platform-limits.md)** — Know the boundaries before scaling

---

*Sources: [Microsoft Learn — Getting Started](https://learn.microsoft.com/en-us/microsoft-copilot-studio/fundamentals-what-is-copilot-studio), [Microsoft Learn — Environments](https://learn.microsoft.com/en-us/microsoft-copilot-studio/environments-first-run-experience)*
