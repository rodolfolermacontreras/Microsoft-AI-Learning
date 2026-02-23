# 📝 Workplace Documentation Tool

**Document workplace interactions • AI-powered pattern analysis • Build your case**

A complete tool for Microsoft employees to document toxic workplace patterns, 
analyze trends with AI, and build a solid case for HR or legal review.

---

## 🚀 Quick Start (ONE CLICK!)

### Quick Start
1. Double-click **`START.bat`**
2. Browser opens automatically
3. Start documenting!

### Sharing With Coworkers
1. Share the `workplace_docs.zip` package
2. Extract anywhere (Desktop is fine)
3. Double-click **`START.bat`**
4. That's it!

---

## 📋 First-Time Setup (Only Once)

### Step 1: Install Python (Required)
1. Go to **https://www.python.org/downloads/**
2. Click **Download Python** (big yellow button)
3. Run the installer
4. ⚠️ **CHECK THE BOX: "Add Python to PATH"**
5. Click "Install Now"
6. Restart your computer

### Step 2: Enable AI Features (Optional but Recommended)
The AI features require GitHub Copilot CLI. Without it, the tool still works 
but won't auto-detect patterns or generate narratives.

**To enable AI:**
1. Open PowerShell or Command Prompt
2. Run: `winget install GitHub.Copilot`
3. Run: `copilot auth login`
4. Follow the browser prompts to authenticate with GitHub

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **📝 Document Incidents** | Paste Teams chats, emails, or describe interactions |
| **💬 Add Your Notes** | Context, observations, how it made you feel |
| **🤖 AI Pattern Detection** | Auto-detects gaslighting, blame-shifting, etc. |
| **📊 Cross-Incident Analysis** | Finds patterns across ALL your data |
| **📄 HR Narrative** | Generates professional documentation |
| **❓ Protective Questions** | AI suggests what to ask in meetings |
| **🕸️ Knowledge Graph** | Visualize people, incidents, patterns |
| **📥 Team Import** | Combine data from coworkers |
| **📤 Export** | Download for HR, legal, or backup |

---

## 🔒 Privacy & Security

- **100% Local Storage**: All data stays on YOUR computer
- **Location**: `C:\Users\<YourName>\.workplace_docs\`
- **No Cloud**: Nothing uploaded anywhere (except Copilot AI queries)
- **Your Control**: Export, delete, or backup anytime

---

## 📤 Sharing with Coworkers

### To Share the Tool:
1. Zip the entire `workplace_docs` folder
2. Send via Teams, email, or OneDrive
3. Tell them to extract and double-click `START.bat`

### To Combine Data for Team Analysis:
1. Each person clicks **Export** → **Download JSON**
2. Share JSON files with each other
3. One person uses **Team Import** to merge all data
4. Run **AI Analysis** to find team-wide patterns

---

## 📁 Files in This Folder

| File | Purpose |
|------|---------|
| **`START.bat`** | 🖱️ **Double-click this to run!** |
| `app.py` | Main application (web interface + AI) |
| `README.md` | This file |
| `test_interactions.txt` | Example scenarios to practice |

---

## 🏷️ Pattern Categories

The AI can detect these patterns:

- **Unclear Expectations** - Vague instructions, moving goalposts
- **Shifting Priorities** - Constant changes without acknowledgment
- **Gaslighting** - Denying previous statements, rewriting history
- **Pressure Tactics** - Unreasonable deadlines, threats
- **Blame Shifting** - Making others responsible for systemic issues
- **Contradicting Requests** - Saying one thing, expecting another
- **Micromanagement** - Excessive control, lack of trust
- **Lack of Support** - No resources, no backup
- **Intimidation** - Threatening behavior or language

---

## 🧪 Testing the Tool

Open `test_interactions.txt` for 7 example scenarios:
1. Unclear Expectations
2. Shifting Priorities
3. Gaslighting
4. Pressure Tactics
5. No Accountability
6. Contradicting Requests
7. Blame Shifting

---

## ❓ Troubleshooting

**"Python is not installed" error**
- Make sure you checked "Add Python to PATH" during installation
- Restart your computer after installing Python

**AI says "Unavailable"**
- Install Copilot CLI: `winget install GitHub.Copilot`
- Authenticate: `copilot auth login`
- Tool still works without AI (manual categorization)

**Browser doesn't open**
- Manually open your browser
- Go to: http://localhost:8765

**Port already in use**
- Close any other instances of the tool
- Or restart your computer

---

## ⚠️ Important Disclaimer

This tool is for **personal documentation purposes only**. 

- **NOT legal advice** - Consult HR or legal professionals
- **Use ethically** - Document factually and objectively
- **Your responsibility** - Keep records safe and confidential

---

## 💡 Tips for Effective Documentation

1. **Document promptly** - Write things down right after they happen
2. **Be specific** - Include dates, times, exact quotes
3. **Stay factual** - Focus on what happened, not assumptions
4. **Add context** - Use the notes field to explain the situation
5. **Be consistent** - Regular documentation is more powerful
6. **Save evidence** - Screenshot emails/chats when possible
7. **Back up regularly** - Export your data periodically

---

*Built with ❤️ using the GitHub Copilot SDK*
