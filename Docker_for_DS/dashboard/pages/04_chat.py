"""
Page 4 -- AI Tutor chat.

A conversational Docker tutor powered by LLMs (OpenAI, Azure OpenAI,
GitHub Copilot, or offline fallback).  Tailored for a data-scientist
audience transitioning to containerized, production-grade workflows.
"""

from __future__ import annotations

import os
import sys

import streamlit as st
from dotenv import load_dotenv

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

load_dotenv(os.path.join(_HERE, ".env"), override=False)

from utils.llm_client import chat


st.set_page_config(page_title="AI Tutor | Docker for DS", layout="wide")
st.title("AI Docker Tutor")
st.markdown(
    "Ask anything about Docker. The tutor is designed for data scientists "
    "and will explain concepts using analogies from pandas, scikit-learn, "
    "Jupyter, and the ML workflow you already know."
)


# ---- Quick prompts organised by topic ----
QUICK_PROMPTS = {
    "Basics": [
        "Explain Docker to me like I'm a pandas user",
        "What is the difference between an image and a container?",
        "Walk me through the Dockerfile -> Build -> Run cycle",
    ],
    "DS workflows": [
        "How do I Dockerize my scikit-learn training pipeline?",
        "How do I run Jupyter Lab inside Docker?",
        "How do I mount my local data folder into a container?",
    ],
    "Production": [
        "What is the Train -> Save -> Serve pattern in Docker?",
        "How do I use Docker Compose for an ML project with a database?",
        "How do I keep my Docker images small?",
    ],
    "Troubleshooting": [
        "My container exits immediately -- how do I debug it?",
        "I get a 'port already in use' error -- what do I do?",
        "Docker build is very slow -- how do I speed it up with layer caching?",
    ],
}


# ---- Session state ----
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []


# ---- Layout: chat + sidebar ----

with st.sidebar:
    st.subheader("Quick prompts")
    st.caption("Click any prompt to start a conversation.")
    for topic, prompts in QUICK_PROMPTS.items():
        with st.expander(topic, expanded=False):
            for prompt in prompts:
                if st.button(prompt, key=f"qp_{prompt[:30]}"):
                    st.session_state["chat_prefill"] = prompt

    st.markdown("---")
    if st.button("Clear conversation"):
        st.session_state["chat_history"] = []
        st.rerun()

    st.markdown("---")
    st.subheader("LLM backend")
    backend = st.selectbox(
        "Backend",
        ["openai", "azure", "copilot", "offline"],
        index=0,
        key="llm_backend_select",
    )
    st.session_state["llm_backend"] = backend

    if backend == "offline":
        st.info(
            "Offline mode uses pre-written answers for common questions. "
            "Set an API key in `.env` for full AI-powered responses."
        )
    else:
        st.caption(
            f"Using **{backend}** backend. Configure API keys in `.env`."
        )


# ---- Main chat area ----

# Display chat history
for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Prefill from other pages (e.g., "Ask AI" buttons)
prefill = st.session_state.pop("chat_prefill", None)

# Chat input
user_input = st.chat_input("Ask about Docker...")

# Use prefill if no direct input
if not user_input and prefill:
    user_input = prefill

if user_input:
    # Show user message
    st.session_state["chat_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Build conversation for the LLM
    messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state["chat_history"]]

    # Stream the response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_reply = ""

        try:
            for chunk in chat(
                messages=messages,
                backend=st.session_state.get("llm_backend", "openai"),
            ):
                full_reply += chunk
                placeholder.markdown(full_reply + " |")

            placeholder.markdown(full_reply)
        except Exception as exc:
            full_reply = (
                f"Sorry, I could not get a response from the **{backend}** backend.\n\n"
                f"**Error:** `{exc}`\n\n"
                f"**Suggestions:**\n"
                f"- Check that your API key is set in `.env`\n"
                f"- Try switching to **offline** mode in the sidebar\n"
                f"- Make sure you have network access"
            )
            placeholder.markdown(full_reply)

    st.session_state["chat_history"].append({"role": "assistant", "content": full_reply})


# ---- Starter suggestions when chat is empty ----
if not st.session_state["chat_history"] and not user_input:
    st.markdown("### Not sure where to start?")
    st.markdown(
        "Here are some questions other data scientists have asked when first learning Docker:"
    )

    suggestion_cols = st.columns(2)
    suggestions = [
        "I know Python and pandas. Why should I learn Docker?",
        "What is the simplest way to Dockerize a Python script?",
        "How is a Dockerfile different from a requirements.txt?",
        "Can I use my GPU inside a Docker container?",
    ]
    for i, suggestion in enumerate(suggestions):
        col = suggestion_cols[i % 2]
        with col:
            if st.button(suggestion, key=f"starter_{i}"):
                st.session_state["chat_prefill"] = suggestion
                st.rerun()
