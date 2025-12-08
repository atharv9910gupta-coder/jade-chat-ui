import streamlit as st
import requests

st.set_page_config(page_title="Jade AI", page_icon="🤖", layout="centered")

# -----------------------------------------
# LOAD SECRET
# -----------------------------------------
if "GROQ_API_KEY" not in st.secrets:
    st.error("❌ Missing GROQ_API_KEY in Streamlit Secrets!")
    st.stop()

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# -----------------------------------------
# MEMORY
# -----------------------------------------
if "memory" not in st.session_state:
    st.session_state.memory = []

# -----------------------------------------
# GROQ CHAT FUNCTION (SIMPLE + SAFE)
# -----------------------------------------
def run_groq_chat(prompt, history):
    messages = [{"role": "system", "content": "You are Jade AI Assistant."}]

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
    response = requests.post(url, headers=headers, json=body)

    # Convert API response safely
    try:
        data = response.json()
    except:
        return "❌ Error: Invalid response from Groq."

    if "error" in data:
        return "❌ API Error: " + data["error"]["message"]

    try:
        return data["choices"][0]["message"]["content"]
    except:
        return "❌ Error: Missing 'choices' in response."


# -----------------------------------------
# SIDEBAR NAVIGATION
# -----------------------------------------
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Select a page:", ["Home", "Chat", "Email", "SMS", "Admin Dashboard"])


# -----------------------------------------
# HOME PAGE
# -----------------------------------------
if page == "Home":
    st.title("🏠 Welcome to Jade AI")
    st.write("Your all-in-one AI assistant.")


# -----------------------------------------
# CHAT PAGE
# -----------------------------------------
elif page == "Chat":
    st.title("💬 Chat with Jade")

    user_input = st.text_input("Type your message:")

    if st.button("Send"):
        if user_input.strip() == "":
            st.warning("Please type something!")
        else:
            st.session_state.memory.append(user_input)
            reply = run_groq_chat(user_input, st.session_state.memory)

            st.subheader("Jade:")
            st.write(reply)


# -----------------------------------------
# EMAIL PAGE
# -----------------------------------------
elif page == "Email":
    st.title("📧 Email")
    st.info("Email system not conn
