"""
Page 1 -- Docker Concepts.

Visual, analogy-rich concept cards designed for data scientists.
Each concept includes:
  - A plain-English explanation with DS analogies
  - A 'Why this matters for DS' section
  - Key points to remember
  - A self-check quiz
  - An 'Ask AI' button for deeper exploration
"""

from __future__ import annotations

import os
import sys

import streamlit as st

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)


st.set_page_config(page_title="Concepts | Docker for DS", layout="wide")
st.title("Docker Concepts")
st.markdown(
    "Each card below explains a core Docker concept **using analogies you already know** "
    "from data science. Read them in order -- later concepts build on earlier ones."
)
st.markdown(
    "> **How to use this page:** Pick a concept from the dropdown (or scroll through all). "
    "Read the explanation, check the key points, then try the self-check quiz at the bottom "
    "of each card. If anything is unclear, hit *Ask AI* to get a personalised explanation."
)
st.markdown("---")

# ---- Concept data ----
CONCEPTS = [
    {
        "title": "1. What is Docker? (The Big Picture)",
        "ds_analogy": (
            "You know how `conda create -n myenv python=3.12` gives you an isolated Python environment? "
            "Docker does the same thing but for your **entire computer** -- the operating system, "
            "system libraries, Python, your packages, your code, and your config files, all frozen "
            "into one portable unit."
        ),
        "explanation": (
            "Docker is a platform that lets you package an application with everything it needs to run "
            "into a standardised unit called a **container**.\n\n"
            "Before Docker, deploying software meant writing long setup documents: "
            "'Install Python 3.12, then pip install these 47 packages, then set these 5 environment "
            "variables, then...'. Docker replaces all of that with a single file (Dockerfile) and a "
            "single command (`docker build`).\n\n"
            "The result is an **image** -- a frozen snapshot of your entire setup. Anyone can take "
            "that image and run it with `docker run`, and they get the exact same environment you had."
        ),
        "why_ds": (
            "- **Reproducibility:** Your model training environment is frozen and shareable.\n"
            "- **Collaboration:** No more 'works on my machine' -- your colleague runs the same image.\n"
            "- **Deployment:** The same image that runs on your laptop can run in the cloud.\n"
            "- **CI/CD:** Automated pipelines can build and test your code in identical environments.\n"
        ),
        "diagram": (
            "```\n"
            "Your laptop                        Any other machine\n"
            "+-----------+                       +-----------+\n"
            "| Dockerfile|  -- docker build -->  |   Image   |\n"
            "| + code    |                       | (portable)|\n"
            "+-----------+                       +-----+-----+\n"
            "                                          |\n"
            "                                    docker run\n"
            "                                          |\n"
            "                                    +-----v-----+\n"
            "                                    | Container  |\n"
            "                                    | (running)  |\n"
            "                                    +-----------+\n"
            "```"
        ),
        "key_points": [
            "Docker packages your code + dependencies + OS into one portable unit.",
            "A Dockerfile is the recipe. An image is the frozen result. A container is the running instance.",
            "If it runs in Docker on your machine, it runs on any machine with Docker installed.",
        ],
        "quiz": {
            "question": "What is the closest analogy to a Docker image in data science?",
            "options": [
                "A Jupyter notebook with all cells executed",
                "A trained model saved as a .pkl file",
                "A requirements.txt file",
                "A running Flask server",
            ],
            "answer_idx": 1,
            "explanation": (
                "A `.pkl` file is a frozen snapshot -- you do not 'run' it directly, you load it to create "
                "a working model. Similarly, a Docker image is a frozen snapshot of your environment that you "
                "'run' to create a container."
            ),
        },
    },
    {
        "title": "2. Docker Architecture (Client, Daemon, Registry)",
        "ds_analogy": (
            "Think of it like this:\n"
            "- **Docker CLI** = your Jupyter cell where you type commands\n"
            "- **Docker Daemon** = the Python kernel that actually runs the code\n"
            "- **Docker Hub** = PyPI where you `pip install` packages from\n"
        ),
        "explanation": (
            "Docker has three main components:\n\n"
            "1. **Docker CLI (client):** The command-line tool you type into (`docker run`, `docker build`). "
            "It does not do the actual work -- it sends instructions to the daemon.\n\n"
            "2. **Docker Daemon (server):** The background service (`dockerd`) that actually builds images, "
            "runs containers, and manages storage. It listens for commands from the CLI.\n\n"
            "3. **Registry (Docker Hub):** A remote storage service for images. When you `docker pull python:3.12-slim`, "
            "the daemon downloads the image from Docker Hub. You can also push your own images for others to use.\n\n"
            "This is a **client-server** architecture. The CLI is just a thin wrapper -- most of the time "
            "the daemon and CLI run on the same machine, but they can be separated."
        ),
        "why_ds": (
            "- Knowing this architecture helps you debug problems: 'Is the CLI working? Is the daemon running?'\n"
            "- Docker Hub is where you find pre-built images (Jupyter, TensorFlow, PyTorch) so you don't build from scratch.\n"
            "- If you later work with cloud container services (Azure, AWS), they replace the local daemon with a remote one.\n"
        ),
        "diagram": (
            "```\n"
            "You (terminal)                Docker Daemon              Docker Hub\n"
            "+------------+    REST API    +-------------+   pull    +----------+\n"
            "| docker run | ------------> | Build / Run  | <------> | Registry |\n"
            "| docker ps  |               | images,      |   push   | (images) |\n"
            "| docker ... |               | containers   |          |          |\n"
            "+------------+               +-------------+           +----------+\n"
            "```"
        ),
        "key_points": [
            "The CLI sends commands; the daemon executes them.",
            "Docker Hub is like PyPI for Docker images.",
            "When you type `docker run`, the CLI tells the daemon to create and start a container.",
            "`docker info` shows you whether the daemon is running and its configuration.",
        ],
        "quiz": {
            "question": "When you type `docker run python:3.12-slim`, what happens first?",
            "options": [
                "Python starts running in your terminal",
                "The CLI sends a request to the Docker daemon",
                "Docker downloads Python from python.org",
                "A new virtual machine is created",
            ],
            "answer_idx": 1,
            "explanation": (
                "The CLI is just a messenger. It sends the 'run' instruction to the daemon, "
                "which then checks if the image exists locally, pulls it from the registry if needed, "
                "and creates a container."
            ),
        },
    },
    {
        "title": "3. Images vs Containers",
        "ds_analogy": (
            "- **Image** = a trained model saved as `model.pkl` (frozen, read-only)\n"
            "- **Container** = `model.predict(X_test)` (a living process using that model)\n\n"
            "You can load the same `.pkl` file many times to serve different requests. "
            "Similarly, you can run many containers from the same image."
        ),
        "explanation": (
            "This is the **most important distinction** in Docker.\n\n"
            "**Image:**\n"
            "- Read-only template containing your OS, packages, code, and config\n"
            "- Built from a Dockerfile using `docker build`\n"
            "- Stored locally and can be pushed to a registry\n"
            "- Does NOT run -- it is a blueprint\n\n"
            "**Container:**\n"
            "- A running instance of an image\n"
            "- Created with `docker run`\n"
            "- Has its own filesystem, network, and process space\n"
            "- Can be started, stopped, restarted, and removed\n"
            "- You can run multiple containers from the same image simultaneously\n\n"
            "**Lifecycle:**\n"
            "```\n"
            "Dockerfile  --(docker build)-->  Image  --(docker run)-->  Container\n"
            "                                  |                         (running)\n"
            "                                  |---(docker run)-->  Container 2\n"
            "                                  |---(docker run)-->  Container 3\n"
            "```"
        ),
        "why_ds": (
            "- You build one image for your ML model, then run it N times for different datasets.\n"
            "- You can version images (`v1.0`, `v1.1`) just like you version model artifacts.\n"
            "- Containers are disposable -- if one crashes, just start a new one from the same image.\n"
        ),
        "diagram": None,
        "key_points": [
            "An image is a read-only blueprint. A container is a running instance.",
            "`docker build` creates images. `docker run` creates containers.",
            "One image can produce many containers.",
            "Deleting a container does NOT delete the image.",
            "Anything written inside a container is lost when the container is removed (unless you use a volume).",
        ],
        "quiz": {
            "question": "What happens to data written inside a container when you `docker rm` it?",
            "options": [
                "It is saved automatically to your home directory",
                "It goes into the image for next time",
                "It is lost forever (unless you used a volume)",
                "It is backed up to Docker Hub",
            ],
            "answer_idx": 2,
            "explanation": (
                "Containers have a thin writable layer on top of the image. When the container "
                "is removed, that layer is deleted. To persist data (like model files or datasets), "
                "you need to use a volume -- which you will learn about in concept 6."
            ),
        },
    },
    {
        "title": "4. Dockerfiles -- The Recipe",
        "ds_analogy": (
            "A Dockerfile is like a more powerful `requirements.txt`:\n\n"
            "- `requirements.txt` says: 'install these Python packages'\n"
            "- `Dockerfile` says: 'start with this OS, install these system packages, "
            "install these Python packages, copy my code, set config, and here is the command to run'\n\n"
            "It turns your entire project setup into something **repeatable and automated**."
        ),
        "explanation": (
            "A Dockerfile is a plain text file with a series of instructions. Docker reads "
            "them top to bottom and executes each one to build an image.\n\n"
            "**The key instructions (in order you will use them):**\n\n"
            "| Instruction | What it does | DS Example |\n"
            "| --- | --- | --- |\n"
            "| `FROM` | Start from a base image | `FROM python:3.12-slim` |\n"
            "| `WORKDIR` | Set the working directory | `WORKDIR /app` |\n"
            "| `COPY` | Copy files from your computer into the image | `COPY requirements.txt .` |\n"
            "| `RUN` | Execute a command during build | `RUN pip install -r requirements.txt` |\n"
            "| `ENV` | Set an environment variable | `ENV PYTHONUNBUFFERED=1` |\n"
            "| `EXPOSE` | Document which port the app uses | `EXPOSE 8888` |\n"
            "| `CMD` | Default command when container starts | `CMD [\"python\", \"train.py\"]` |\n\n"
            "**Example -- a minimal DS image:**\n"
            "```dockerfile\n"
            "FROM python:3.12-slim\n"
            "WORKDIR /app\n"
            "COPY requirements.txt .\n"
            "RUN pip install --no-cache-dir -r requirements.txt\n"
            "COPY . .\n"
            "CMD [\"python\", \"train.py\"]\n"
            "```\n\n"
            "**Why the order matters:** Docker creates a *layer* for each instruction and "
            "caches it. If you change line 5, Docker re-runs lines 5+ but reuses lines 1-4 "
            "from cache. That is why we copy `requirements.txt` *before* the rest of the code -- "
            "packages change less often than code, so the pip install layer stays cached."
        ),
        "why_ds": (
            "- Pin your exact environment so experiments are reproducible months later.\n"
            "- Share your whole setup with `docker build -t myproject .` instead of writing setup docs.\n"
            "- Layer caching means rebuilds after code changes take seconds, not minutes.\n"
        ),
        "diagram": (
            "```\n"
            "Dockerfile instructions           Image layers (cached)\n"
            "+----------------------------+    +-------------------+\n"
            "| FROM python:3.12-slim      | -> | Layer 1: base OS  |\n"
            "| WORKDIR /app               | -> | Layer 2: workdir  |\n"
            "| COPY requirements.txt .    | -> | Layer 3: req file |\n"
            "| RUN pip install -r req...  | -> | Layer 4: packages |\n"
            "| COPY . .                   | -> | Layer 5: your code|\n"
            "| CMD [\"python\",\"train.py\"]  | -> | Layer 6: metadata |\n"
            "+----------------------------+    +-------------------+\n"
            "\n"
            "Change your code? Only layers 5-6 rebuild. Layers 1-4 are cached.\n"
            "```"
        ),
        "key_points": [
            "A Dockerfile is a text file with instructions to build an image.",
            "Start with FROM (base image), then COPY + RUN to install deps, then COPY code, then CMD.",
            "Order matters for caching: put rarely-changing steps first.",
            "COPY requirements first, then pip install, then COPY code -- this is the standard DS pattern.",
            "Each instruction creates a cached layer -- change line N and only N+ re-runs.",
        ],
        "quiz": {
            "question": "Why do we COPY requirements.txt and pip install BEFORE copying the rest of the code?",
            "options": [
                "Because Python needs the packages before it can parse the code",
                "Because requirements.txt is smaller and copies faster",
                "To take advantage of layer caching -- packages change less often than code",
                "It does not matter; the order is just convention",
            ],
            "answer_idx": 2,
            "explanation": (
                "If you copy ALL code first and then pip install, every code change invalidates "
                "the pip install cache, causing a full reinstall. By installing packages in a separate "
                "earlier layer, Docker reuses that layer when only your code changes. "
                "This can save minutes on every rebuild."
            ),
        },
    },
    {
        "title": "5. Building and Running (docker build + docker run)",
        "ds_analogy": (
            "- `docker build` = `joblib.dump(model, 'model.pkl')` -- freeze your work into a file\n"
            "- `docker run` = `model = joblib.load('model.pkl'); model.predict(X)` -- load and use it\n"
        ),
        "explanation": (
            "**Building an image:**\n"
            "```bash\n"
            "docker build -t my-ds-project:v1 .\n"
            "```\n"
            "- `-t my-ds-project:v1` gives the image a name and tag (version)\n"
            "- `.` tells Docker to use the Dockerfile in the current directory\n"
            "- Docker reads the Dockerfile, executes each instruction, and saves the result as an image\n\n"
            "**Running a container:**\n"
            "```bash\n"
            "docker run my-ds-project:v1\n"
            "```\n"
            "- This creates a new container from the image and starts it\n"
            "- The container runs the CMD from the Dockerfile\n"
            "- When CMD finishes, the container stops\n\n"
            "**Common flags you will use often:**\n\n"
            "| Flag | What it does | Example |\n"
            "| --- | --- | --- |\n"
            "| `-d` | Run in background (detached) | `docker run -d myapp` |\n"
            "| `-p host:container` | Map a port | `docker run -p 8888:8888 jupyter` |\n"
            "| `-v host:container` | Mount a volume | `docker run -v ./data:/app/data ...` |\n"
            "| `--rm` | Auto-remove container on exit | `docker run --rm myapp` |\n"
            "| `--name` | Give the container a human name | `docker run --name trainer myapp` |\n"
            "| `-it` | Interactive terminal (for debugging) | `docker run -it myapp bash` |\n"
        ),
        "why_ds": (
            "- Build once, run anywhere: `docker run my-ds-project:v1` works on any machine with Docker.\n"
            "- Use `-v` to mount your local data directory into the container (so you don't bake data into the image).\n"
            "- Use `-p` to expose Jupyter or API ports to your browser.\n"
        ),
        "diagram": None,
        "key_points": [
            "`docker build -t name:tag .` reads the Dockerfile and creates an image.",
            "`docker run name:tag` creates and starts a container from that image.",
            "Use `-p` for ports, `-v` for volumes, `-d` for background, `--rm` for auto-cleanup.",
            "The `.` in `docker build` is the build context -- it tells Docker where your files are.",
        ],
        "quiz": {
            "question": "What does `docker run -d -p 8888:8888 --name jupyter my-jupyter-image` do?",
            "options": [
                "Builds an image named jupyter on port 8888",
                "Starts a background container named 'jupyter', maps port 8888, from my-jupyter-image",
                "Downloads Jupyter from Docker Hub and installs it",
                "Opens port 8888 on Docker Hub",
            ],
            "answer_idx": 1,
            "explanation": (
                "`-d` = background, `-p 8888:8888` = map port, `--name jupyter` = container name, "
                "`my-jupyter-image` = the image to run. This is exactly how you start Jupyter in Docker."
            ),
        },
    },
    {
        "title": "6. Volumes -- Persistent Data",
        "ds_analogy": (
            "When you train a model in a notebook, the `.pkl` file lives on your file system. "
            "If you close the notebook, the file is still there.\n\n"
            "Containers are different: by default, everything inside a container is **temporary**. "
            "When you remove the container, the data is gone.\n\n"
            "A **volume** is like a shared folder -- it connects a location on your host to a "
            "location inside the container, so data persists even after the container is removed."
        ),
        "explanation": (
            "There are two types of volumes:\n\n"
            "**1. Bind mount** -- map a specific host folder:\n"
            "```bash\n"
            "docker run -v ${PWD}/data:/app/data my-image\n"
            "```\n"
            "- `${PWD}/data` = folder on your computer\n"
            "- `/app/data` = folder inside the container\n"
            "- Files are shared in real-time -- edit on host, see in container, and vice versa\n\n"
            "**2. Named volume** -- managed by Docker:\n"
            "```bash\n"
            "docker volume create mydata\n"
            "docker run -v mydata:/app/data my-image\n"
            "```\n"
            "- Docker stores the data in its own internal location\n"
            "- Better for databases and things you don't need to browse from the host\n\n"
            "**When to use which:**\n"
            "- Bind mount: notebooks, datasets, code you are actively editing\n"
            "- Named volume: database files, model registry, things managed by the app"
        ),
        "why_ds": (
            "- Mount your `data/` folder so the container reads your datasets without copying them into the image.\n"
            "- Mount your `models/` folder so trained models are saved to your host (and survive container removal).\n"
            "- Mount your `notebooks/` folder so Jupyter inside Docker edits files on your real filesystem.\n"
            "- **Critical rule:** Never bake large datasets into images -- use volumes instead.\n"
        ),
        "diagram": (
            "```\n"
            "Your computer                      Container\n"
            "+-------------------+              +-------------------+\n"
            "| C:\\project\\data   | <-- -v -->   | /app/data         |\n"
            "| C:\\project\\models | <-- -v -->   | /app/models       |\n"
            "+-------------------+              +-------------------+\n"
            "\n"
            "Files written on either side appear on both sides instantly.\n"
            "```"
        ),
        "key_points": [
            "Without a volume, data inside a container is lost when the container is removed.",
            "Bind mounts (`-v ./data:/app/data`) share a specific host folder.",
            "Named volumes (`-v mydata:/app/data`) are managed by Docker internally.",
            "Use bind mounts for code and datasets; named volumes for databases.",
            "Never bake large datasets into images -- mount them at runtime.",
        ],
        "quiz": {
            "question": "You train a model inside a container and save it to `/app/models/model.pkl`. "
                        "You then `docker rm` the container. Where is the model file?",
            "options": [
                "Still at /app/models/model.pkl on your host",
                "Gone -- the container's filesystem was deleted",
                "Saved to Docker Hub automatically",
                "In the Docker image",
            ],
            "answer_idx": 1,
            "explanation": (
                "Without a volume, everything inside the container is temporary. The model is gone. "
                "To keep it, you should have used: `docker run -v ./models:/app/models ...` so the "
                "file is written to your host's `./models/` folder."
            ),
        },
    },
    {
        "title": "7. Networks -- How Containers Talk to Each Other",
        "ds_analogy": (
            "When your Jupyter notebook connects to a Postgres database at `localhost:5432`, "
            "both processes are on the same machine and can see each other.\n\n"
            "In Docker, each container is isolated -- it has its own `localhost`. "
            "For two containers to communicate, they need to be on the same **Docker network**."
        ),
        "explanation": (
            "Docker creates virtual networks that containers can join.\n\n"
            "**Default behavior:**\n"
            "- `docker run` puts the container on the default `bridge` network.\n"
            "- Containers on the same network can reach each other **by container name**.\n\n"
            "**Example -- Jupyter connecting to Postgres:**\n"
            "```bash\n"
            "# Create a shared network\n"
            "docker network create ds-net\n\n"
            "# Start Postgres on the network\n"
            "docker run -d --name my-pg --network ds-net postgres:16\n\n"
            "# Start Jupyter on the same network\n"
            "docker run -d --name jupyter --network ds-net -p 8888:8888 my-jupyter\n"
            "```\n"
            "Inside the Jupyter container, you connect to Postgres at `my-pg:5432` (the container name, not localhost).\n\n"
            "**Port publishing (`-p`):**\n"
            "- `-p 8888:8888` opens port 8888 on your host so your browser can reach Jupyter.\n"
            "- Without `-p`, the container's port is only accessible from other containers on the same network."
        ),
        "why_ds": (
            "- In Lab 05 you will run Jupyter + Postgres + pgAdmin together. They communicate via a shared network.\n"
            "- Docker Compose auto-creates a network for all services, so you rarely need to create one manually.\n"
            "- Understanding networks helps you debug 'connection refused' errors.\n"
        ),
        "diagram": (
            "```\n"
            "Docker network: ds-net\n"
            "+----------------------------------------------------------+\n"
            "|                                                          |\n"
            "|  Jupyter (jupyter:8888)  <----->  Postgres (my-pg:5432)  |\n"
            "|           |                                              |\n"
            "+-----------|----------------------------------------------+\n"
            "            |\n"
            "     -p 8888:8888\n"
            "            |\n"
            "     Your browser (http://localhost:8888)\n"
            "```"
        ),
        "key_points": [
            "Each container has its own localhost -- they are isolated by default.",
            "Containers on the same Docker network can reach each other by name.",
            "`-p host:container` publishes a port to your host machine.",
            "Docker Compose auto-creates a shared network for all services.",
        ],
        "quiz": {
            "question": "In a Docker Compose stack with Jupyter and Postgres, how does Jupyter connect to the database?",
            "options": [
                "Using localhost:5432",
                "Using the container name as hostname (e.g., postgres:5432)",
                "By sharing files through a volume",
                "It cannot -- Docker containers are completely isolated",
            ],
            "answer_idx": 1,
            "explanation": (
                "Docker Compose puts all services on a shared network. Each service name becomes "
                "a DNS hostname. So Jupyter connects to `postgres:5432`, not `localhost:5432`."
            ),
        },
    },
    {
        "title": "8. Docker Compose -- Multi-Service Stacks",
        "ds_analogy": (
            "Imagine you have a Makefile that says:\n"
            "1. Start Postgres\n"
            "2. Start Redis\n"
            "3. Start Jupyter\n"
            "4. Connect them all together\n\n"
            "Docker Compose is exactly that, but in a clean YAML file. "
            "One command (`docker compose up`) starts everything."
        ),
        "explanation": (
            "Docker Compose uses a `docker-compose.yml` file to define multiple services:\n\n"
            "```yaml\n"
            "services:\n"
            "  jupyter:\n"
            "    image: jupyter/datascience-notebook\n"
            "    ports:\n"
            "      - '8888:8888'\n"
            "    volumes:\n"
            "      - ./notebooks:/home/jovyan/work\n\n"
            "  postgres:\n"
            "    image: postgres:16\n"
            "    environment:\n"
            "      POSTGRES_PASSWORD: secret\n"
            "    volumes:\n"
            "      - pgdata:/var/lib/postgresql/data\n\n"
            "volumes:\n"
            "  pgdata:\n"
            "```\n\n"
            "**Key commands:**\n\n"
            "| Command | What it does |\n"
            "| --- | --- |\n"
            "| `docker compose up -d` | Start all services in background |\n"
            "| `docker compose down` | Stop and remove all containers |\n"
            "| `docker compose ps` | Show status of services |\n"
            "| `docker compose logs -f` | Follow logs from all services |\n"
            "| `docker compose logs jupyter` | Logs from one service |\n"
        ),
        "why_ds": (
            "- In practice, DS projects need multiple services: notebook server, database, dashboard, API.\n"
            "- Compose lets you define and start them all with one command.\n"
            "- You can version your `docker-compose.yml` in git alongside your code.\n"
            "- This is the stepping stone to Kubernetes (which handles the same problem at scale).\n"
        ),
        "diagram": (
            "```\n"
            "docker-compose.yml\n"
            "+----------------------------+\n"
            "| services:                  |          docker compose up\n"
            "|   jupyter: ...             |  --------------------------->\n"
            "|   postgres: ...            |       Starts 3 containers\n"
            "|   pgadmin: ...             |      on a shared network\n"
            "+----------------------------+\n"
            "```"
        ),
        "key_points": [
            "Compose defines multi-container apps in one YAML file.",
            "`docker compose up -d` starts everything; `docker compose down` stops everything.",
            "Services are automatically networked -- they can reach each other by name.",
            "Use `volumes:` for persistence and `environment:` for config.",
            "This is the foundation for production container orchestration.",
        ],
        "quiz": {
            "question": "What does `docker compose down` do?",
            "options": [
                "Deletes the docker-compose.yml file",
                "Stops and removes all containers defined in the compose file",
                "Pauses the containers so they can resume later",
                "Pushes all images to Docker Hub",
            ],
            "answer_idx": 1,
            "explanation": (
                "`docker compose down` stops all running containers, removes them, and removes "
                "the network. Named volumes are NOT removed by default (you need `--volumes` "
                "flag for that). Your data is safe."
            ),
        },
    },
]


# ---- Render ----
view_mode = st.radio(
    "View mode:",
    ["One concept at a time", "Show all concepts"],
    horizontal=True,
    key="concept_view_mode",
)

if view_mode == "One concept at a time":
    selected = st.selectbox(
        "Jump to concept:",
        options=[c["title"] for c in CONCEPTS],
        key="concept_select",
    )
    concepts_to_show = [c for c in CONCEPTS if c["title"] == selected]
else:
    concepts_to_show = CONCEPTS

for concept in concepts_to_show:
    st.markdown(f"## {concept['title']}")

    # DS analogy callout
    st.info(f"**Data Science analogy:**\n\n{concept['ds_analogy']}")

    # Full explanation
    st.markdown(concept["explanation"])

    # Diagram
    if concept.get("diagram"):
        with st.expander("Visual diagram", expanded=True):
            st.markdown(concept["diagram"])

    # Why this matters
    with st.expander("Why this matters for data scientists", expanded=False):
        st.markdown(concept["why_ds"])

    # Key points
    st.markdown("**Key points to remember:**")
    for point in concept["key_points"]:
        st.markdown(f"- {point}")

    # Self-check quiz
    quiz = concept.get("quiz")
    if quiz:
        st.markdown("---")
        st.markdown("**Self-check quiz:**")
        quiz_key = f"quiz_{concept['title'][:20]}"
        answer = st.radio(
            quiz["question"],
            options=quiz["options"],
            index=None,
            key=quiz_key,
        )

        if answer is not None:
            chosen_idx = quiz["options"].index(answer)
            if chosen_idx == quiz["answer_idx"]:
                st.success(f"Correct! {quiz['explanation']}")
                st.session_state.quiz_scores[quiz_key] = True
            else:
                st.error(
                    f"Not quite. The correct answer is: **{quiz['options'][quiz['answer_idx']]}**\n\n"
                    f"{quiz['explanation']}"
                )
                st.session_state.quiz_scores[quiz_key] = False

    # Ask AI button
    st.markdown("---")
    if st.button(f"Ask AI to explain '{concept['title']}' further", key=f"ask_{concept['title'][:30]}"):
        prompt = (
            f"I am a data scientist learning Docker. I just read about '{concept['title']}'. "
            f"Explain it to me in more depth with a practical example. "
            f"Use data science analogies I would understand."
        )
        st.session_state["chat_prefill"] = prompt
        st.switch_page("pages/04_chat.py")

    if view_mode == "Show all concepts":
        st.markdown("---")
        st.markdown("")
