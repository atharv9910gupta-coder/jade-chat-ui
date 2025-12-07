import streamlit as st
import requests
import json
from modules.tools import send_email, send_sms

st.set_page_config(page_title="Jade AI", page_icon="🤖", layout="centered")

# ------------------- LOAD API KEY -------------------
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("❌ Missing GROQ_API_KEY in your Streamlit Secrets!")
    st.stop()

# ------------------- MEMORY -------------------
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = []


# ------------------- GROQ CHAT FUNCTION -------------------
def run_groq_chat(prompt, memory_list):
    """Send message + memory to Groq API"""
    try:
        messages = [{"role": "system", "content": "You are Jade AI Assistant."}]

        # Add memory
        for item in memory_list:
            messages.append({"role": "user", "content": item})

        messages.append({"role": "user", "content": prompt})

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "mixtral-8x7b-32768",
            "messages": messages,
            "max_tokens": 200
        }

        response = requests.post(url, headers=headers, json=data).json()
        
        return response["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Error: {e}"


# ------------------- SIDEBAR -------------------
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Select a page:", ["Home", "Chat", "Email", "SMS", "Admin Dashboard"])


# ------------------- HOME -------------------
if page == "Home":
    st.title("🏠 Welcome to Jade AI")
    st.write("Your personal AI agent system.")


# ------------------- CHAT PAGE -------------------
elif page == "Chat":
    st.title("💬 Chat with Jade")

    user_input = st.text_input("Type your message:")

    if st.button("Send"):
        if user_input.strip() != "":
            st.session_state.chat_memory.append(user_input)

            response = run_groq_chat(user_input, st.session_state.chat_memory)

            st.write("### Jade:")
            st.write(response)


# ------------------- EMAIL PAGE -------------------
elif page == "Email":
    st.title("📧 Send Email")

    to = st.text_input("Receiver Email:")
    subject = st.text_input("Subject:")
    body = st.text_area("Message:")

    if st.button("Send Email"):
        send_email(to, subject, body)
        st.success("Email sent! (Dummy mode)")


# ------------------- SMS PAGE -------------------
elif page == "SMS":
    st.title("📱 Send SMS")

    number = st.text_input("Phone Number:")
    message = st.text_area("Message:")

    if st.button("Send SMS"):
        send_sms(number, message)
        st.success("SMS sent! (Dummy mode)")


# ------------------- ADMIN PAGE -------------------
elif page == "Admin Dashboard":
    st.title("🔐 Admin Panel")
    st.write("Future admin controls will come here.")
