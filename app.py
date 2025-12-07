import streamlit as st
import json
from modules.groq_client import run_groq_chat
from modules.memory import Memory
from modules.tools import process_tool_request

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="Jade — General AI Agent",
    page_icon="🧠",
    layout="wide"
)

# ---------------------------
# INITIALIZE MEMORY
# ---------------------------
memory = Memory("data/memory.json")

# ---------------------------
# TITLE
# ---------------------------
st.markdown("""
# 🧠 Jade — General AI Agent
""")

# ---------------------------
# CHAT UI
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display saved messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
user_input = st.chat_input("Type your message...")

if user_input:
    # Show user bubble
    with st.chat_message("user"):
        st.write(user_input)

    st.session_state.messages.append({"role": "user", "content": user_input})

    # Save to memory
    memory.add("user", user_input)

    # Agent Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            ai_reply = run_groq_chat(user_input)

            # Check for tool actions (email, sms, search, etc.)
            tool_output = process_tool_request(ai_reply)

            final_reply = ai_reply
            if tool_output:
                final_reply += f"\n\n🔧 **Tool Result:**\n{tool_output}"

            st.write(final_reply)

            # Save reply to session + memory
            st.session_state.messages.append(
                {"role": "assistant", "content": final_reply}
            )
            memory.add("assistant", final_reply)
