import streamlit as st
import requests
import json

st.set_page_config(page_title="Jade AI", page_icon="🤖", layout="centered")

# ------------------- LOAD GROQ API KEY -------------------
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("❌ Missing GROQ_API_KEY in Streamlit Secrets!")
    st.stop()


# ------------------- MEMORY -------------------
if "memory" not in st.session_state:
    st.session_state.memory = []


# ------------------- GROQ CHAT FUNCTION -------------------
def run_groq_chat(prompt, memory_list):
    try:
        messages = [{"role": "system", "content": "You are Jade AI Assistant."}]

        # Add memory items
        for item in memory_list:
            messages.append({"role": "user", "content": item})

        # Add new user message
        messages.append({"role": "user", "content": prompt})

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
