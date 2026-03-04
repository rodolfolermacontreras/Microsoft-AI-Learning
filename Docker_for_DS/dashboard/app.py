"""
Docker Learning Dashboard -- main entry point.

A learning-first, interactive dashboard for data scientists
who are new to Docker and transitioning toward developer / AI engineer roles.

Run:
    streamlit run app.py
"""

from __future__ import annotations

import os
import sys

import streamlit as st
from dotenv import load_dotenv

# Ensure project root is on the path so utils imports work from sub-pages
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

load_dotenv(os.path.join(_HERE, ".env"), override=False)


# ---- Page config MUST be the first Streamlit call ----
st.set_page_config(
    page_title="Docker for Data Scientists",
    page_icon="whale",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": (
            "Interactive Docker learning dashboard for data scientists "
            "transitioning to developer and AI engineer roles."
        ),
    },
)


# ---- Session-state defaults ----
def _init_state() -> None:
    """Initialise session state keys on first load."""
    defaults: dict[str, object] = {
        "chat_history": [],
        "progress": {},
        "current_section": None,
        "llm_backend": os.environ.get("LLM_BACKEND", "openai"),
        "quiz_scores": {},
        "glossary_visited": set(),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


_init_state()


# ---- Sidebar ----
def _sidebar() -> None:
    st.sidebar.title("Docker Learner")
    st.sidebar.caption(
        "Built for data scientists moving into software engineering and AI engineering."
    )
    st.sidebar.markdown("---")

    # Progress
    total = 5
    done = sum(1 for v in st.session_state.progress.values() if v)
    st.sidebar.markdown(f"**Your progress:** {done} / {total} labs complete")
    st.sidebar.progress(done / total if total > 0 else 0)

    st.sidebar.markdown("---")

    with st.sidebar.expander("How to use this dashboard", expanded=False):
        st.markdown(
            "1. Start with **Concepts** -- read the visual cards to build your mental model.\n"
            "2. Move to **Commands** -- explore the reference table and use the sandbox to try commands live.\n"
            "3. Work through the **Exercises** labs in order (01 -> 05). Each lab builds on the previous one.\n"
            "4. Whenever you get stuck, open **AI Tutor** and ask your question in plain English.\n\n"
            "**Tip:** Every page has an *Ask AI* button that pre-fills the tutor with context about what "
            "you are looking at, so you never have to copy-paste."
        )

    with st.sidebar.expander("Glossary -- key terms", expanded=False):
        st.markdown(
            "| Term | Plain-English Meaning |\n"
            "| --- | --- |\n"
            "| **Image** | A snapshot of an environment (like a `.pkl` of your whole computer setup) |\n"
            "| **Container** | A running copy of an image (like loading that `.pkl` and using it) |\n"
            "| **Dockerfile** | A recipe that tells Docker how to build an image (like `requirements.txt` on steroids) |\n"
            "| **Volume** | A shared folder between your computer and the container (so files survive restarts) |\n"
            "| **Port mapping** | Connecting a network door on the container to one on your computer (`-p 8888:8888`) |\n"
            "| **Registry** | An online store for images (Docker Hub is like PyPI for Docker images) |\n"
            "| **Compose** | A YAML file that starts multiple containers together (e.g. Jupyter + Postgres in one command) |\n"
            "| **Layer** | Each instruction in a Dockerfile creates a cached layer (like git commits for your image) |\n"
        )

    st.sidebar.markdown("---")
    st.sidebar.caption("Powered by Streamlit + OpenAI")


_sidebar()


# ---- Home page ----
def _home_page() -> None:
    st.title("Docker for Data Scientists")
    st.markdown(
        "### Your interactive guide to Docker -- built for data scientists who are "
        "transitioning into developer and AI engineer roles."
    )

    # ---- Who is this for? ----
    st.markdown("---")
    st.subheader("Who is this for?")
    col_who1, col_who2 = st.columns(2)
    with col_who1:
        st.markdown(
            "**You, if you ...**\n\n"
            "- Know Python, pandas, scikit-learn, and Jupyter\n"
            "- Want to ship your work as reproducible, portable projects\n"
            "- Are moving from notebooks into production ML/AI pipelines\n"
            "- Keep hearing about Docker but never had a reason (or time) to learn it\n"
        )
    with col_who2:
        st.markdown(
            "**After this dashboard you will ...**\n\n"
            "- Understand images, containers, volumes, and networks\n"
            "- Build custom Docker images for your DS projects\n"
            "- Run Jupyter Lab inside Docker with persistent notebooks\n"
            "- Create a train-then-serve ML pipeline in containers\n"
            "- Orchestrate multi-service stacks (Jupyter + Postgres + pgAdmin)\n"
        )

    # ---- Why Docker matters ----
    st.markdown("---")
    st.subheader("Why Docker matters for you")

    why_tabs = st.tabs([
        "The \"works on my machine\" problem",
        "Reproducibility",
        "From notebooks to production",
        "AI Engineering pipelines",
    ])

    with why_tabs[0]:
        st.markdown(
            "You have probably experienced this: your model trains fine on your laptop, "
            "but when a colleague (or a CI server) tries to run it, something breaks -- "
            "wrong Python version, missing library, different OS.\n\n"
            "**Docker solves this** by packaging your code *together* with the exact Python "
            "version, libraries, system packages, and configuration it needs. "
            "If it runs in a Docker container on your machine, it runs **everywhere** -- "
            "your colleague's laptop, a cloud VM, a Kubernetes cluster.\n\n"
            "**DS analogy:** Think of it like `conda env export --from-history` but for your "
            "entire computer, not just Python packages."
        )

    with why_tabs[1]:
        st.markdown(
            "In data science, reproducibility is everything. You pin package versions in "
            "`requirements.txt`, but that only covers Python packages.\n\n"
            "A Dockerfile goes further: it pins the **base OS**, the **Python runtime**, "
            "the **system libraries** (like `libgomp` for XGBoost), and even environment "
            "variables. Think of it as `conda env export` for your entire computer.\n\n"
            "**Real scenario:** Your team trains a model on Ubuntu with Python 3.12 and numpy 2.2. "
            "Six months later, someone needs to retrain. Without Docker, they spend hours debugging "
            "version mismatches. With Docker: `docker build -t model-training .` and it works instantly."
        )

    with why_tabs[2]:
        st.markdown(
            "Notebooks are great for exploration. But when you need to:\n\n"
            "- Schedule a training job nightly\n"
            "- Serve predictions via an API\n"
            "- Hand off your pipeline to an engineering team\n\n"
            "...you need something more portable. Docker lets you wrap your Python script "
            "(or FastAPI server, or Streamlit app) into a single artifact that runs "
            "with one command: `docker run`.\n\n"
            "**Your path:** Jupyter notebook -> Python script -> Dockerfile -> `docker run` -> done. "
            "In Labs 04 and 05 you will do exactly this."
        )

    with why_tabs[3]:
        st.markdown(
            "Modern AI engineering means stitching together many services:\n\n"
            "- A **vector database** (Qdrant, Weaviate)\n"
            "- An **LLM gateway** or local model server (Ollama, vLLM)\n"
            "- A **backend API** that orchestrates agents (FastAPI)\n"
            "- A **frontend dashboard** (like this one!)\n\n"
            "Docker Compose lets you define all these in one YAML file and start them "
            "with `docker compose up`. You will build exactly this kind of stack in Lab 05.\n\n"
            "**Where this leads:** Once you are comfortable with Compose, Kubernetes "
            "and cloud deployment (Azure Container Apps, AWS ECS) are natural next steps."
        )

    # ---- DS->Docker analogy table ----
    st.markdown("---")
    st.subheader("Docker in Data Science terms")

    st.markdown(
        "If you already know pandas and scikit-learn, you already understand the "
        "*concepts* behind Docker. Here is the translation table:"
    )

    analogy_data = [
        ("Dockerfile", "`requirements.txt` + build script", "A recipe that lists every step to recreate your environment, from OS to pip packages."),
        ("Image", "A trained `.pkl` model file", "A frozen snapshot. You do not run it directly -- you *load* it to create something useful."),
        ("Container", "A loaded model making predictions", "A live, running instance created from an image. You can have many containers from one image."),
        ("Volume", "A shared folder / data mount", "A bridge between your local file system and the container, so data persists after the container stops."),
        ("Port mapping (`-p`)", "`flask.run(port=5000)`", "Opens a network door so your browser (or API client) can reach the app inside the container."),
        ("Docker Hub", "PyPI / conda-forge", "A public registry where you `pull` pre-built images instead of building from scratch."),
        ("Docker Compose", "A Makefile that starts your whole stack", "One YAML file that defines N services (Jupyter, Postgres, Redis) and starts them together."),
        ("Layer / cache", "Incremental `git commit`s", "Each Dockerfile instruction creates a cached layer. Change line 8? Docker re-runs only lines 8+."),
    ]

    col_a, col_b, col_c = st.columns([0.18, 0.25, 0.57])
    with col_a:
        st.markdown("**Docker term**")
    with col_b:
        st.markdown("**DS equivalent**")
    with col_c:
        st.markdown("**What it really means**")

    for docker, ds, explanation in analogy_data:
        col_a, col_b, col_c = st.columns([0.18, 0.25, 0.57])
        with col_a:
            st.markdown(f"**{docker}**")
        with col_b:
            st.markdown(ds)
        with col_c:
            st.markdown(explanation)

    # ---- Learning path ----
    st.markdown("---")
    st.subheader("Learning path")
    st.markdown(
        "Work through these five labs in order. Each one is designed to take "
        "**15-30 minutes** and teaches one new Docker capability that builds on the last."
    )

    sections = [
        (
            "Lab 01 -- Basics",
            "Pull an image, run a container, see what happened, clean up.",
            "You will be comfortable with `docker run`, `docker ps`, `docker stop`.",
            "Beginner",
            "This is like running `pip install` and `python script.py` for the first time. "
            "You are just getting familiar with the tool.",
        ),
        (
            "Lab 02 -- Python Environment",
            "Write a Dockerfile that installs numpy, pandas, and scikit-learn.",
            "You will know how to create a custom image for any DS project.",
            "Beginner",
            "Think of this as writing and freezing a perfect `conda environment.yml` that works on any machine.",
        ),
        (
            "Lab 03 -- Jupyter in Docker",
            "Run Jupyter Lab inside a container with your notebooks mounted.",
            "You will be able to share a fully reproducible Jupyter setup with anyone.",
            "Intermediate",
            "Instead of telling colleagues 'install these 15 packages', you say 'run this one command'.",
        ),
        (
            "Lab 04 -- ML Pipeline",
            "Train an Iris classifier in one container, serve predictions from another.",
            "You will understand the train/serve pattern used in production ML.",
            "Intermediate",
            "This is how ML models get deployed at companies -- separate training from serving.",
        ),
        (
            "Lab 05 -- Multi-container stack",
            "Compose Jupyter + PostgreSQL + pgAdmin into a single stack.",
            "You will be comfortable with Docker Compose for multi-service projects.",
            "Advanced",
            "This is the real-world pattern: multiple services working together, defined in one file.",
        ),
    ]

    for i, (title, what, outcome, level, ds_context) in enumerate(sections):
        done = st.session_state.progress.get(f"section_{i+1}", False)
        with st.expander(
            f"{'[DONE] ' if done else ''}{title}  |  {level}",
            expanded=(not done),
        ):
            st.markdown(f"**What you will do:** {what}")
            st.markdown(f"**Outcome:** {outcome}")
            st.markdown(f"**DS context:** _{ds_context}_")
            if st.button(f"Start {title}", key=f"go_lab_{i}"):
                st.switch_page("pages/03_exercises.py")

    # ---- Quick nav cards ----
    st.markdown("---")
    st.subheader("Jump to a section")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.info(
            "**Concepts**\n\n"
            "Visual cards that explain Docker ideas using Data Science analogies. "
            "Each card includes a 'why this matters' section and a self-check quiz."
        )
        if st.button("Open Concepts", key="btn_concepts"):
            st.switch_page("pages/01_concepts.py")

    with col2:
        st.info(
            "**Commands**\n\n"
            "Browse every Docker command you will need, grouped by what you are trying to do. "
            "Includes a live sandbox to try commands safely."
        )
        if st.button("Open Commands", key="btn_commands"):
            st.switch_page("pages/02_commands.py")

    with col3:
        st.info(
            "**Exercises**\n\n"
            "Five guided labs that take you from zero to multi-container stacks. "
            "Each step has a Run button, a hint, and an Ask AI button."
        )
        if st.button("Open Exercises", key="btn_exercises"):
            st.switch_page("pages/03_exercises.py")

    with col4:
        st.info(
            "**AI Tutor**\n\n"
            "A chat assistant that answers Docker questions using your DS vocabulary. "
            "Pre-loaded with common questions to get you started."
        )
        if st.button("Open AI Tutor", key="btn_chat"):
            st.switch_page("pages/04_chat.py")


_home_page()
