import streamlit as st
import requests

# ==========================
# CONFIG
# ==========================
st.set_page_config(page_title="Jade AI", page_icon="🤖", layout="wide")

GROQ_KEY = st.secrets["GROQ_API_KEY"]  # Your secret key in Streamlit


# ==========================
# GROQ CHAT FUNCTION
# ==========================
def run_groq_chat(prompt, history):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json",
    }

    messages = [{"role": "system",
                 "content": "You are Jade, a helpful business assistant."}]
    messages.extend(history)
    messages.append({"role": "user", "content": prompt})

    body = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "max_tokens": 300,
        "temperature": 0.7,
    }

    try:
        r = requests.post(url, headers=headers, json=body)
        data = r.json()

        if "choices" not in data:
            return False, str(data)

        msg = data["choices"][0]["message"]["content"]
        return True, msg

    except E
