# How It All Works -- Complete Overview

A plain-language explanation of what this home server project is, how you interact with it day-to-day, and what every piece does. Written for someone who has never run a server before.

---

## The Big Picture

You are building a **personal innovation lab** that lives in your house. It has three layers:

```
+------------------------------------------------------------------+
|                                                                  |
|  LAYER 3: CLOUD APIs                                            |
|  OpenAI, HuggingFace -- for tasks too big for your GPU          |
|  You pay per call; the server manages keys and caching           |
|                                                                  |
+------------------------------------------------------------------+
          ^
          | HTTPS (internet)
          v
+------------------------------------------------------------------+
|                                                                  |
|  LAYER 1: THE SERVER (HP Z440 + RTX 3080)                       |
|  Runs 24/7 in a closet. No monitor. Headless.                   |
|  Ubuntu + Docker + GPU = the brain of the house                  |
|                                                                  |
|  Every service is a Docker container with its own port:          |
|  :2283 photos | :4533 music | :5000 cameras | :8000 your apps   |
|  :3000 dashboards | :8123 home automation | :9443 management     |
|                                                                  |
+------------------------------------------------------------------+
          ^
          | LAN / Wi-Fi (your home network)
          v
+------------------------------------------------------------------+
|                                                                  |
|  LAYER 2: EDGE DEVICES + YOUR FAMILY                            |
|  Raspberry Pis -- sensors, cameras, toys, drones                 |
|  Phones, laptops, tablets, TVs -- access web UIs                 |
|  Your Windows PC -- develop and deploy via SSH                   |
|                                                                  |
+------------------------------------------------------------------+
```

---

## How You Interact With The Server (Day-to-Day)

### You never sit at the tower

The server has **no monitor, no keyboard, no mouse** after initial setup. It lives in a closet, under a desk, or in the garage. It boots to Ubuntu and just runs.

### From your Windows laptop, you do two things:

**1. SSH (terminal access) -- for deploying and managing**

```powershell
ssh rodolfo@192.168.1.10
```

This gives you a Linux terminal on the server. From here you:
- Start/stop Docker containers: `docker compose up -d`
- Check logs: `docker logs immich_server`
- Pull new images: `docker compose pull`
- Run GPU tasks: `python train_model.py`
- Monitor resources: `nvidia-smi`, `htop`, `docker stats`

**2. Browser (web UIs) -- for using the services**

Open any browser on any device and type the server IP + port:

| URL | What You See |
|---|---|
| `http://192.168.1.10:2283` | Immich -- upload and browse photos, search by face/object |
| `http://192.168.1.10:4533` | Navidrome -- stream music, create playlists |
| `http://192.168.1.10:5000` | Frigate -- live camera feeds, recorded events |
| `http://192.168.1.10:3000` | Grafana -- garden sensor dashboards, server health |
| `http://192.168.1.10:8000` | Your FastAPI apps -- family chatbot, tools |
| `http://192.168.1.10:8123` | Home Assistant -- control lights, automations |
| `http://192.168.1.10:9443` | Portainer -- see all containers, restart services |

**Your phone, your kids' tablets, the smart TV -- anything on your Wi-Fi can reach these.**

### The development cycle

```
1. Get an idea ("I want a family recipe chatbot")
      |
2. SSH into the server from your laptop
      |
3. Vibe-code it with AI (Copilot, Claude, etc.)
      |
4. Write a docker-compose.yml + Python script
      |
5. docker compose up -d  -->  it's live on port :XXXX
      |
6. Open browser on phone  -->  http://192.168.1.10:XXXX
      |
7. Family uses it. You iterate.
```

---

## What Is Docker and Why Do We Use It?

Docker is like a lightweight virtual machine. Each service (photos, music, cameras) runs in its own isolated container with its own dependencies. This means:

- **No conflicts** -- Immich uses PostgreSQL 16, Grafana uses its own database, they don't interfere
- **Easy to install** -- `docker compose up -d` pulls everything and starts it. No manual setup.
- **Easy to remove** -- `docker compose down` and it's gone. Clean.
- **Easy to update** -- `docker compose pull && docker compose up -d` gets the latest version
- **Portable** -- if you ever replace the server, you copy the compose files and data, done

Think of it this way: **each project = one `docker-compose.yml` file + a data folder.**

---

## What Is the GPU For?

The NVIDIA RTX 3080 handles tasks that a CPU would take 10-100x longer to do:

| Task | Without GPU | With GPU |
|---|---|---|
| Search photos by content ("find beach photos") | Minutes per 1000 photos | Seconds |
| Separate vocals from a song (karaoke) | 10+ minutes per song | 30-60 seconds |
| Detect people/animals on camera | 2-5 FPS | 30+ FPS real-time |
| Classify garden images (healthy/sick plant) | Slow | Near instant |
| Run a local chatbot (Ollama + Llama) | Unusable | Conversational speed |
| Train a custom image classifier | Hours | Minutes |

The GPU lives inside the server. Docker containers access it through the NVIDIA Container Toolkit. You never interact with the GPU directly -- you just run containers that use it.

---

## What Are the Raspberry Pis For?

The server is the brain. The Pis are the hands and eyes, placed around the house:

| Pi | Location | Sensors | What It Does |
|---|---|---|---|
| Garden Pi | Backyard | Temp, humidity, soil moisture | Sends readings to server every 5 min via MQTT |
| Camera Pi #1 | Front door | Pi Camera or USB webcam | Streams video to Frigate for person detection |
| Camera Pi #2 | Backyard | Pi Camera | Streams video for garden/animal monitoring |
| Toy Pi | Kids' room | Motors, LEDs, buttons | RC car, light show, or game controlled from phone |
| Drone/Rover Pi | Garden | Camera + motors | Patrols garden, sends photos for ML classification |

**Communication pattern:**
```
Pi ---(MQTT message: sensor data)---> Server ---(stores in InfluxDB)---> Grafana dashboard
Pi ---(RTSP video stream)-----------> Server ---(Frigate detects)-----> Alert on phone
Pi ---(Wi-Fi command)---------------> Server ---(OpenAI API)----------> Voice response
```

---

## What Are the Cloud APIs For?

Some tasks are too big or too specialized for a local RTX 3080:

| Task | Local (GPU) | Cloud API |
|---|---|---|
| Simple image classification | Use local (free, fast) | Not needed |
| Generate a 500-word story | Ollama works | OpenAI GPT is better quality |
| Generate an image from text | Stable Diffusion (slow but free) | DALL-E (fast, costs ~$0.04) |
| Transcribe speech to text | Local Whisper (great) | Whisper API (also great) |
| Complex reasoning / long documents | Local models struggle | GPT-4o excels |

**The server manages all API keys** in a `.env` file. Family devices never see the keys. The server also **caches responses** so identical questions don't cost twice.

---

## Budget Summary

| Category | Items | Cost |
|---|---|---|
| Server hardware | HP Z440, RTX 3080, SSD, HDD, Wi-Fi, fans, hub | ~$850-1,000 |
| Raspberry Pis (2-3) | Pi boards, sensors, cameras, chassis | ~$150-300 |
| Cloud APIs | OpenAI credits (pay as you go) | ~$5-20/month |
| **Ongoing** | Electricity (~50-80W idle, ~400W under GPU load) | ~$10-20/month |

---

## What We Built in This Repository

```
Local_Server/
|
|-- README.md                        Main project overview
|-- HARDWARE.md                      Shopping list + eBay search strings
|-- SERVER_SETUP.md                  Step-by-step: Ubuntu, GPU drivers, Docker
|-- OVERVIEW.md                      This file (how it all works)
|-- DEV_WORKFLOW.md                  How to develop with VS Code + AI agents
|
|-- projects/
|   |-- README.md                    All 8 projects at a glance
|   |-- photo_server/README.md       Immich: local Google Photos
|   |-- music_server/README.md       Navidrome + Demucs karaoke
|   |-- security_camera/README.md    Frigate + HuggingFace classifiers
|   |-- garden_monitor/README.md     Sensors -> InfluxDB -> Grafana
|   |-- home_assistant/README.md     Home automation hub
|   |-- pi_playground/README.md      Toys and games for kids (Pi-based)
|   |-- drone_monitor/README.md      Garden patrol rover + ML
|   |-- api_projects/README.md       OpenAI/HuggingFace powered apps
|
|-- docker/README.md                 Docker strategy, port map, GPU access
|-- network/README.md                IPs, MQTT topics, firewall, Pi setup
|-- research/
    |-- hardware_research.md         Decision rationale and comparisons
    |-- perplexity_raw.md            Full Perplexity research conversation
```

Each project README contains:
- What it does and why
- Docker Compose file (copy-paste ready)
- Configuration files
- Python scripts (working starter code)
- Status checklist

---

## Recommended Order of Operations

| Step | What | Time Estimate |
|---|---|---|
| 1 | Buy hardware (eBay + Amazon) | 1-2 weeks (shipping) |
| 2 | Assemble: GPU, SSD, fans into Z440 | 1-2 hours |
| 3 | Install Ubuntu 24.04 Server | 30 minutes |
| 4 | Install NVIDIA drivers + CUDA | 30 minutes |
| 5 | Install Docker + NVIDIA Container Toolkit | 15 minutes || 4 | Set up your dev workflow | [DEV_WORKFLOW.md](DEV_WORKFLOW.md) | 30 minutes || 6 | Deploy Portainer (container management UI) | 5 minutes |
| 7 | Deploy your first project (pick one!) | 30-60 minutes |
| 8 | Set up first Raspberry Pi | 1-2 hours |
| 9 | Connect Pi to server via MQTT | 30 minutes |
| 10 | Keep building. One project at a time. | Ongoing |

**Start with the project that excites you most.** If it is photos, start with Immich. If it is music, start with Navidrome. If it is the garden, start with a Pi + sensor. The infrastructure (Docker, MQTT, server) is the same for all of them -- once you do it once, every next project is faster.

---

## Key Concepts Glossary

| Term | What It Means |
|---|---|
| **Headless** | Server runs without a monitor; you access it remotely |
| **SSH** | Secure Shell -- terminal access to the server from your laptop |
| **Docker** | Each service runs in an isolated container with its own port |
| **Docker Compose** | A YAML file that defines which containers to run and how |
| **MQTT** | Lightweight messaging protocol; Pis publish data, server subscribes |
| **Port** | A number (like :8000) that identifies a service on the server |
| **CUDA** | NVIDIA's GPU computing platform; lets Docker containers use the GPU |
| **VRAM** | GPU memory (10-12 GB on the RTX 3080); limits model size |
| **Ollama** | Tool to run open-source LLMs locally on your GPU |
| **Immich** | Open-source Google Photos replacement |
| **Navidrome** | Open-source music streaming server |
| **Frigate** | Open-source NVR (camera recorder) with AI object detection |
| **Grafana** | Dashboard tool for visualizing data (sensor readings, metrics) |
| **InfluxDB** | Time-series database (stores sensor data efficiently) |
| **Home Assistant** | Home automation platform that ties everything together |
| **Portainer** | Web UI for managing Docker containers |
| **FastAPI** | Python web framework for building APIs quickly |
| **ONNX** | Format to export ML models for deployment on edge devices (Pis) |
