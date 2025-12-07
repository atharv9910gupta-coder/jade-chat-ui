import streamlit as st
from modules.groq_client import run_groq_chat
from modules.memory import Memory
from modules.tools import send_email, send_sms

st.set_page_config(
    page_title="Jade — General AI Agent",
    page_icon="🤖",
    layout="wide"
)

# Initialize memory
memory = Memory()

# Sidebar Navigation
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio(
    "Select a page:",
    ["Home", "Chat", "Email", "SMS", "Admin Dashboard"]
)

# ----------------- HOME PAGE -----------------
if page == "Home":
    st.title("🤖 Jade — General AI Agent")
    st.write("Welcome! Use the menu on the left to explore features.")

# ----------------- CHAT PAGE -----------------
elif page == "Chat":
    st.title("💬 Chat with Jade")

    user_input = st.text_input("Type your message:")

    if st.button("Send"):
        if user_input.strip():
            memory.add("user", user_input)

            response = run_groq_chat(user_input, memory.get())
            memory.add("assistant", response)

            st.success(f"**Jade:** {response}")
        else:
            st.warning("Please type something.")

    st.subheader("Conversation Memory")
    st.json(memory.get())

# ----------------- EMAIL PAGE -----------------
elif page == "Email":
    st.title("📧 Send Email")

    to = st.text_input("Recipient email:")
    subject = st.text_input("Subject:")
    body = st.text_area("Message:")

    if st.button("Send Email"):
        send_email(to, subject, body)
        st.success("Email sent!")

# ----------------- SMS PAGE -----------------
elif page == "SMS":
    st.title("📱 Send SMS")

    number = st.text_input("Phone Number:")
    message = st.text_area("Message:")

    if st.button("Send SMS"):
        send_sms(number, message)
        st.success("SMS sent!")

# ----------------- ADMIN PAGE -----------------
elif page == "Admin Dashboard":
    st.title("🛠 Admin Dashboard")

    if st.button("Clear Conversation Memory"):
        memory.clear()
        st.success("Memory cleared!")

    st.subheader("Current Memory Data")
    st.json(memory.get())
