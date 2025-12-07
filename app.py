import streamlit as st
import requests
import json

st.set_page_config(page_title="Jade AI", page_icon="🤖", layout="centered")

# ------------------- MEMORY -------------------
if "memory" not in st.session_state:
    st.session_state.memory = []

# Load API key safely from Streamlit secrets (do NOT hardcode keys)
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = None

# ------------------- JADE ENGINE -------------------
def chat_with_groq(user_message):
    # Add user message to memory
    st.session_state.memory.append({"role": "user", "content": user_message})

    # Keep last 5 messages
    trimmed_memory = st.session_state.memory[-5:]

    messages = [
        {"role": "system",
         "content": "You are Jade — a friendly, polite, helpful general AI agent with memory."}
    ]
    messages.extend(trimmed_memory)

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": messages
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    result = response.json()

    if "error" in result:
        return "Groq Error: " + result["error"].get("message", str(result["error"]))

    reply = result["choices"][0]["message"]["content"]

    # Add Jade reply to memory
    st.session_state.memory.append({"role": "assistant", "content": reply})

    return reply

# ------------------- USER INTERFACE -------------------
st.markdown("<h1 style='text-align:center;'>🤖 Jade — General AI Agent</h1>", unsafe_allow_html=True)
st.write("")

# Show message if API key missing
if GROQ_API_KEY is None:
    st.error("Groq API key not found. Add it in the app's Secrets on Streamlit Cloud under 'Settings → Secrets'.")
    st.stop()

# Chat container (render history)
chat_box = st.container()

with chat_box:
    for msg in st.session_state.memory:
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div style='background:#DCF8C6;padding:10px;margin:6px;border-radius:8px;max-width:70%;float:right;'>
                    <b>You:</b> {msg['content']}
                </div>
                <div style='clear:both;'></div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style='background:#E8E8E8;padding:10px;margin:6px;border-radius:8px;max-width:70%;float:left;'>
                    <b>Jade:</b> {msg['content']}
                </div>
                <div style='clear:both;'></div>
                """,
                unsafe_allow_html=True
            )

# Input area
st.write("---")
user_input = st.text_input("Type your message:", "")

if st.button("Send"):
    if user_input.strip() != "":
        with st.spinner("Jade is thinking..."):
            reply = chat_with_groq(user_input)
        st.experimental_rerun()
