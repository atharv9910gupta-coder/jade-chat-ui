import streamlit as st
import requests
import json

st.set_page_config(page_title="Jade AI", page_icon="🤖", layout="centered")

# ------------------- MEMORY -------------------
if "memory" not in st.session_state:
    st.session_state.memory = []

# Load API key safely from Streamlit secrets
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("❌ Missing GROQ_API_KEY in Streamlit Secrets")
    st.stop()

# Groq API endpoint
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# ------------------- UI -------------------

st.title("🤖 Jade AI — Your AI Assistant")

user_input = st.text_input("Ask Jade anything:")

# Chat history UI
for mem in st.session_state.memory:
    st.chat_message(mem["role"]).markdown(mem["content"])

# ------------------- SEND REQUEST -------------------
if st.button("Send") and user_input.strip() != "":
    st.session_state.memory.append({"role": "user", "content": user_input})

    payload = {
        "model": "llama-3.1-70b-versatile",
        "messages": st.session_state.memory
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, data=json.dumps(payload))

        if response.status_code != 200:
            st.error("❌ API Error: " + response.text)
        else:
            data = response.json()
            msg = data["choices"][0]["message"]["content"]

            st.session_state.memory.append({"role": "assistant", "content": msg})
            st.chat_message("assistant").markdown(msg)

    except Exception as e:
        st.error(f"Unexpected Error: {e}")

# ------------------- SIDEBAR -------------------

st.sidebar.title("⚙️ System Settings")

st.sidebar.info("Email system not connected yet. More features coming soon!")

if st.sidebar.button("Clear Chat"):
    st.session_state.memory = []
    st.rerun()
