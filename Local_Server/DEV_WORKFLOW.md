# Development Workflow -- How You Actually Build Things

How to use VS Code on your laptop to develop directly on the server, with AI agents doing the heavy lifting and voice control to go fully hands-free.

---

## The Key Insight

```
+---------------------------+          SSH          +---------------------------+
|     YOUR LAPTOP           | --------------------> |     HP Z440 SERVER        |
|     (Windows)             |                       |     (Ubuntu + GPU)        |
|                           |                       |                           |
|  VS Code (just the UI)   |                       |  VS Code Server (engine)  |
|  Microphone (voice)      |                       |  Files live here          |
|  Screen + keyboard       |                       |  Terminal runs here       |
|                           |                       |  Docker runs here         |
|  GitHub Copilot agent    |  works on server --->  |  GPU available            |
|  Claude Code agent       |  works on server --->  |  Python, Node, etc.       |
|  Polyclaw swarm          |  works on server --->  |  All code executes here   |
+---------------------------+                       +---------------------------+
```

**Your laptop is a thin client.** All computation, file storage, Docker, GPU access, and AI agent execution happens on the server. Your laptop just displays the VS Code window and sends your keystrokes (or voice) over SSH.

---

## Step 1: Install VS Code Remote - SSH

On your Windows laptop:

1. Open VS Code
2. Install the **Remote - SSH** extension (by Microsoft)
3. Press `Ctrl+Shift+P` -> "Remote-SSH: Add New SSH Host"
4. Enter: `ssh rodolfo@192.168.1.10`
5. Save to your SSH config

From now on, connecting is one click:
- `Ctrl+Shift+P` -> "Remote-SSH: Connect to Host" -> pick your server

VS Code will install its server component on the Z440 automatically. After that, everything you do in VS Code happens on the server.

---

## Step 2: Your Daily Development Cycle

```
Morning: Open VS Code -> Connect to server via SSH -> Pick a project
    |
    v
"Hey Copilot, create a FastAPI endpoint that classifies uploaded images
 using a HuggingFace ViT model and returns the top 3 labels"
    |
    v
Copilot/Claude writes the code ON THE SERVER
    |
    v
You review, tweak, press Ctrl+` to open terminal (runs on server)
    |
    v
$ docker compose up -d    # deploys on the server
    |
    v
Open phone browser: http://192.168.1.10:8000  -->  it works
    |
    v
Commit and push to GitHub (from server terminal)
```

---

## Step 3: AI Agent Workflows

### GitHub Copilot (in VS Code)

Works exactly as it does today, but executes on the server:
- Code completions use server-side files
- Copilot Chat has access to the server terminal
- Copilot agent mode can create files, run commands, install packages -- all on the server
- The GPU is available for any Python/ML work Copilot triggers

### Claude Code (terminal agent)

Install Claude Code on the server:

```bash
# On the server (via SSH)
npm install -g @anthropic-ai/claude-code
```

Then use it from VS Code's integrated terminal:

```bash
claude "Set up a Navidrome music server with Docker Compose,
       configure it for my /mnt/storage/music directory,
       and add a Demucs sidecar for karaoke generation"
```

Claude Code will:
- Create the docker-compose.yml
- Write configuration files
- Run `docker compose up -d`
- Test that the service responds
- All on the server, using the server's GPU if needed

### Polyclaw / OpenClaw (agent swarm)

Run the Polyclaw orchestrator on the server. Each agent in the swarm:
- Has access to the server filesystem
- Can spawn Docker containers
- Can use the GPU for ML tasks
- Can call OpenAI APIs (keys stored in server's .env)

Example workflow:

```bash
# On the server terminal (via VS Code Remote SSH)
cd /opt/server/projects/security_camera

polyclaw run --task "
  Agent 1: Set up Frigate NVR with Docker, configure for 2 RTSP cameras
  Agent 2: Write a Python classifier using CLIP for custom categories
  Agent 3: Create a Grafana dashboard showing detection events over time
  Agent 4: Write integration tests for the whole pipeline
"
```

Four agents work in parallel on the server, each handling their subtask.

---

## Step 4: Voice Control

### Option A: VS Code Voice (built-in)

VS Code has voice support via the **VS Code Speech** extension:

1. Install "VS Code Speech" extension
2. Click the microphone icon in the chat panel
3. Speak: "Create a Python function that reads temperature from DHT22 sensor and publishes to MQTT"
4. Copilot hears you, writes the code, you review

This works over Remote SSH -- your laptop's microphone captures audio, VS Code sends the text to Copilot, Copilot executes on the server.

### Option B: Claude Code + Whisper (full voice terminal)

For voice-controlled terminal on the server:

```bash
# On the server
pip install openai-whisper pyaudio

# Create a voice-to-command script
python voice_terminal.py
# Listens to your mic (via laptop audio forwarding)
# Transcribes with Whisper (runs on GPU -- fast)
# Sends command to Claude Code
# Claude executes on the server
```

### Option C: Pushover / Web Button (phone trigger)

Create a simple web endpoint on the server:

```
http://192.168.1.10:8080/trigger?task=patrol_garden
```

Tap a button on your phone -> server receives the task -> agents execute it.

---

## Step 5: File Organization on the Server

All project code lives on the server, organized like this:

```
/home/rodolfo/
+-- projects/               # All your code (Git repos)
|   +-- photo_server/       # Immich customizations
|   +-- music_server/       # Navidrome + karaoke scripts
|   +-- security_camera/    # Frigate + classifiers
|   +-- garden_monitor/     # Sensor pipeline
|   +-- family_chatbot/     # FastAPI + OpenAI
|   +-- pi_playground/      # Toy car, LED, robot code
|   +-- drone_monitor/      # Rover patrol scripts
|   +-- ...                 # New projects go here
|
+-- .env                    # API keys (OpenAI, HuggingFace, etc.)
+-- .ssh/                   # SSH keys for GitHub

/opt/server/
+-- data/                   # Docker persistent data
+-- compose/                # Docker Compose files

/mnt/storage/               # Bulk media (HDD)
+-- photos/
+-- music/
+-- cameras/
```

When you open VS Code Remote SSH, you open `/home/rodolfo/projects/` as your workspace. All your Git repos, Python environments, and Docker commands are right there.

---

## Step 6: Git Workflow

Code lives on the server. Push to GitHub from the server:

```bash
# On the server (VS Code terminal)
cd ~/projects/security_camera
git add .
git commit -m "feat: add CLIP classifier for camera events"
git push origin main
```

Or use VS Code's built-in Git panel (Source Control tab) -- it works identically over Remote SSH.

Your GitHub credentials are configured on the server (via `gh auth login` or SSH key). Your laptop never stores project code.

---

## What Your Laptop Needs

Almost nothing:

| Requirement | Details |
|---|---|
| VS Code | With Remote - SSH extension |
| SSH client | Built into Windows (OpenSSH) |
| Microphone | For voice commands (any USB mic or laptop mic) |
| Web browser | To access server web UIs |
| Stable Wi-Fi | To your home network |

Your laptop does NOT need:
- Python, Node, Docker, or any dev tools
- GPU
- Large storage
- Fast CPU

**All the power is on the server. Your laptop is just the window into it.**

---

## Comparison: Develop Locally vs Develop on Server

| Aspect | Develop on Laptop | Develop on Server (Remote SSH) |
|---|---|---|
| GPU access | None | RTX 3080 available |
| Docker | Must install Docker Desktop | Docker native on Linux |
| Files | On laptop SSD | On server SSD (faster for large datasets) |
| AI agents | Run on laptop CPU | Run on server CPU + GPU |
| Deploy to production | Copy files to server | Already there -- just `docker compose up` |
| Terminal | PowerShell | Linux bash (native for Docker/ML) |
| Multiple users | Just you | Any family member can SSH in |
| Power failure on laptop | Work lost if not saved | Server keeps running regardless |

**The Remote SSH approach eliminates the "works on my machine" problem.** You develop where you deploy.

---

## Quick Start Checklist

Once the server is running Ubuntu + Docker:

- [ ] Install OpenSSH server: `sudo apt install openssh-server`
- [ ] Set up SSH key auth (no password needed after this)
- [ ] Install VS Code Remote - SSH extension on your laptop
- [ ] Connect to server from VS Code
- [ ] Install server-side tools: Python, Node, Git, Docker (already done in SERVER_SETUP.md)
- [ ] Install AI tools: GitHub Copilot extension, Claude Code CLI
- [ ] Clone your repos into `~/projects/`
- [ ] Set up `.env` with API keys
- [ ] Install VS Code Speech extension for voice
- [ ] Start building
