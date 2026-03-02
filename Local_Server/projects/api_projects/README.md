# API Projects -- Cloud-Powered Apps on a Local Server

Projects that call external APIs (OpenAI, HuggingFace Inference, Google, etc.) from the home server. The server manages API keys, caches responses, serves web UIs to the family, and can fall back to local GPU models when the API is too slow or expensive.

---

## Why Run API Projects on the Home Server?

- **API keys stay safe** -- stored in `.env` on the server, never on phones or laptops
- **Shared access** -- any family device on the LAN can use the apps
- **Caching** -- save API responses to avoid duplicate costs
- **Hybrid** -- try the API version first, then swap to a local model (Ollama) if it works well enough
- **Always on** -- chatbots, automations, and scheduled tasks run 24/7

---

## Project Ideas

| Idea | API Used | Description | Difficulty |
|---|---|---|---|
| Family chatbot | OpenAI GPT | A friendly assistant for homework help, recipes, trivia | Beginner |
| Story generator | OpenAI GPT | Kids describe a scene; GPT writes a bedtime story | Beginner |
| Image generator | OpenAI DALL-E / Stable Diffusion API | Family members describe images; server generates and displays them | Beginner |
| Voice assistant | OpenAI Whisper + GPT | Local microphone on a Pi captures voice, server transcribes + responds | Intermediate |
| Recipe planner | OpenAI GPT + grocery API | Input what is in the fridge; get meal suggestions | Beginner |
| Language tutor | OpenAI GPT | Conversational practice in Spanish/English with corrections | Beginner |
| Document summarizer | OpenAI GPT / HuggingFace | Drop a PDF; get a summary on a local web page | Intermediate |
| Garden advisor | OpenAI GPT + garden sensor data | "My tomatoes have yellow leaves" + sensor readings = diagnosis | Intermediate |
| Code reviewer | OpenAI GPT / Copilot API | Paste code; get review and suggestions (for your own learning) | Intermediate |

---

## Architecture

```
+----------------+        +-------------------+        +------------------+
|  Family device | -----> |   HP Z440 Server  | -----> |   OpenAI API     |
|  (phone/laptop)|  HTTP  |                   |  HTTPS |   HuggingFace    |
|                | <----- |  Flask / FastAPI   | <----- |   Google APIs    |
+----------------+        |  + SQLite cache    |        +------------------+
                          |  + .env (API keys) |
                          +-------------------+
```

---

## Base Template (FastAPI + OpenAI)

A reusable starting point for any API project:

```python
# api_app.py
# Minimal FastAPI server that proxies OpenAI calls with caching

import os
import hashlib
import json

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from openai import OpenAI

app = FastAPI()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Simple file-based cache
CACHE_DIR = "/opt/server/data/api_cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def get_cache_key(model: str, messages: list) -> str:
    """Generate a hash key from model + messages."""
    raw = json.dumps({"model": model, "messages": messages}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def check_cache(key: str) -> str | None:
    """Return cached response if it exists."""
    path = os.path.join(CACHE_DIR, f"{key}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)["response"]
    return None


def save_cache(key: str, response: str) -> None:
    """Save response to cache."""
    path = os.path.join(CACHE_DIR, f"{key}.json")
    with open(path, "w") as f:
        json.dump({"response": response}, f)


@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_message = body.get("message", "")
    model = body.get("model", "gpt-4o-mini")

    messages = [
        {"role": "system", "content": "You are a helpful family assistant."},
        {"role": "user", "content": user_message},
    ]

    # Check cache first
    cache_key = get_cache_key(model, messages)
    cached = check_cache(cache_key)
    if cached:
        return {"response": cached, "cached": True}

    # Call OpenAI
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    response_text = completion.choices[0].message.content

    # Cache the response
    save_cache(cache_key, response_text)

    return {"response": response_text, "cached": False}


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html><body>
    <h1>Family Assistant</h1>
    <textarea id="msg" rows="3" cols="50" placeholder="Ask anything..."></textarea><br>
    <button onclick="ask()">Ask</button>
    <pre id="result"></pre>
    <script>
    async function ask() {
        const msg = document.getElementById('msg').value;
        const res = await fetch('/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: msg})
        });
        const data = await res.json();
        document.getElementById('result').textContent = data.response;
    }
    </script>
    </body></html>
    """
```

### Docker Compose

```yaml
services:
  api-app:
    image: python:3.12-slim
    container_name: api_app
    command: >
      bash -c "pip install fastapi uvicorn openai &&
               uvicorn api_app:app --host 0.0.0.0 --port 8000"
    ports:
      - "8000:8000"
    volumes:
      - ./api_app.py:/app/api_app.py
      - /opt/server/data/api_cache:/opt/server/data/api_cache
    working_dir: /app
    env_file:
      - .env
    restart: unless-stopped
```

### .env File

```bash
OPENAI_API_KEY=sk-your-key-here
# Add other API keys as needed:
# HUGGINGFACE_API_KEY=hf_your-key-here
```

---

## Local vs Cloud Decision Guide

| Scenario | Use Cloud API | Use Local GPU (Ollama / HuggingFace) |
|---|---|---|
| Quick text generation | Yes (fast, cheap with gpt-4o-mini) | If you want zero cost and accept slower |
| Image generation | Yes (DALL-E) until you set up Stable Diffusion locally | Yes with ComfyUI or A1111 on the RTX 3080 |
| Speech-to-text | Either (Whisper API or local Whisper model) | Local Whisper runs great on RTX 3080 |
| Large context / complex reasoning | Yes (GPT-4o, Claude) | Local models struggle with very long context |
| Classification / embeddings | Local is better (fast on GPU, no API cost) | Yes -- CLIP, ViT, sentence-transformers |
| Cost-sensitive bulk tasks | Local | Yes |

---

## API Cost Management Tips

- Use `gpt-4o-mini` instead of `gpt-4o` for simple tasks (10-20x cheaper)
- Cache identical requests (the template above does this)
- Set monthly budget alerts in your OpenAI dashboard
- Move successful experiments to local models once proven

---

## Status

- [ ] FastAPI base template deployed
- [ ] .env file configured with API keys
- [ ] First family chatbot accessible from phone
- [ ] Response caching verified
- [ ] At least one project migrated to local model
