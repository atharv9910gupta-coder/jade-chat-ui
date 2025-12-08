import streamlit as st
import requests
import json

st.set_page_config(page_title="Jade AI", page_icon="🤖", layout="centered")

# ---------------- SECRET KEY ----------------
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("❌ Missing GROQ_API_KEY in Streamlit Secrets!")
    st.stop()

# ---------------- MEMORY ----------------
if "memory" not in st.session_state:
    st.session_state.memory = []

# ---------------- GROQ CHAT ----------------
def run_groq_chat(prompt, memory_list):
    try:
        # Build messages
        messages = []
        messages.append({"role": "system", "content": "You are Jade AI Assistant."})

        for m in memory_list:
            messages.append({"role": "user", "content": m})

        messages.append({"role": "user", "content": prompt})

        # Request headers
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        # Body
        body = {
            "model": "llama3-8b-8192",
            "messages": messages,
            "max_tokens": 200
        }

        # API Call
        url = "https://api.groq.com/openai/v1/chat/completions"
        response
