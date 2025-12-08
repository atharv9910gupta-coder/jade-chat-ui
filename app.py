import streamlit as st
import requests

st.set_page_config(
    page_title="Jade AI",
    page_icon="🤖",
    layout="centered"
)

# LOAD SECRET
if "GROQ_API_KEY" not in st.secrets:
    st.error("Missing API key in Secrets.")
    st.stop()

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# MEMORY
if "memory" not in st.session_state:
    st.session_state.memory = []

# CHAT FUNCTION
def run_groq_chat(prompt, history):
    messages = []
    messages.append({"role": "system", "content": "You are Jade AI."})

    for h in history:
        messages.append({"role": "user", "content": h})

    messages.append({"role": "user", "content": prompt})

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "llama3-8b-8192",
        "messages": messages,
        "max_tokens": 200
    }

    url = "https://api.groq.com/openai/v1/chat/completions"

    try:
        response = requests.post(url, headers=headers, json=body)
        data = response.json()
    except:
        return "Error: Groq request failed."

    if "error" in data:
        return "API Error: " + data["error"]["message"]

    try:
        msg = data["choi]()
