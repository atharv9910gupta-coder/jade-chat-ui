# app.py - Jade AI (Advanced: Chat + Memory + Email + SMS + Admin)
# Paste entire file contents into your repository's app.py

import streamlit as st
import requests
import smtplib
from email.message import EmailMessage
from base64 import b64encode
from typing import List, Tuple
import time
import json

# -------------------------
# Page / App Config
# -------------------------
st.set_page_config(page_title="Jade AI — Advanced", page_icon="🤖", layout="wide")

# -------------------------
# Helper: load secrets safely
# -------------------------
GROQ_KEY = st.secrets.get("GROQ_API_KEY")
SMTP_HOST = st.secrets.get("SMTP_HOST")
SMTP_PORT = st.secrets.get("SMTP_PORT")
SMTP_USER = st.secrets.get("SMTP_USER")
SMTP_PASS = st.secrets.get("SMTP_PASS")
TWILIO_SID = st.secrets.get("TWILIO_SID")
TWILIO_AUTH = st.secrets.get("TWILIO_AUTH")
TWILIO_FROM = st.secrets.get("TWILIO_FROM")

# -------------------------
# Session state init
# -------------------------
if "messages" not in st.session_state:
    # stored as list of dicts {role: "user"|"assistant", content: "..."}
    st.session_state.messages = []

if "logs" not in st.session_state:
    st.session_state.logs = []  # simple list of (ts, type, message)

if "max_memory" not in st.session_state:
    st.session_state.max_memory = 7  # remember last n messages (pairs)

# small helper to append logs
def append_log(level: str, text: str) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    st.session_state.logs.append((ts, level, text))


# -------------------------
# GROQ Chat call
# -------------------------
def run_groq_chat(prompt: str, history: List[dict]) -> Tuple[bool, str]:
    """
    Sends a chat request to Groq's OpenAI-compatible endpoint.
    Returns (success, reply_or_error)
    """
    if not GROQ_KEY:
        return False, "Groq API key is missing. Add GROQ_API_KEY to streamlit secrets."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json",
    }

    # Build messages: system + history + user prompt
    messages = [
        {
            "role": "system",
            "content": (
                "You are JADE, a polite and helpful customer-support style assistant. "
                "Answer clearly and concisely. If the user asks for sending email or SMS, "
                "ask for required fields and confirm before sending."
            ),
        }
    ]
    # Append trimmed history if present (history should already be list of dicts)
    if history:
        messages.extend(history[-(st.session_state.max_memory * 2):])  # last N messages

    messages.append({"role": "user", "content": prompt})

    body = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "max_tokens": 400,
        "temperature": 0.2,
    }

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=30)
    except Exception as e:
        append_log("ERROR", f"Network error to Groq: {e}")
        return False, f"Network error contacting Groq: {e}"

    if resp.status_code != 200:
        # capture body safely for debugging (but don't print secret)
        try:
            body_json = resp.json()
        except Exception:
            body_json = resp.text
        append_log("ERROR", f"Groq HTTP {resp.status_code}: {body_json}")
        # Provide short message to UI
        return False, f"Agent error: Groq HTTP {resp.status_code}: {body_json}"

    try:
        data = resp.json()
    except Exception as e:
        append_log("ERROR", f"Could not parse Groq JSON: {e}")
        return False, f"Could not parse Groq response: {e}"

    # graceful checks for structure variations
    # Common expected: {"choices":[{"message":{"content": "..."}}], ...}
    try:
        if "choices" in data and isinstance(data["choices"], list) and len(data["choices"]) > 0:
            choice = data["choices"][0]
            # new style: choice["message"]["content"]
            if isinstance(choice, dict) and "message" in choice and "content" in choice["message"]:
                content = choice["message"]["content"]
                return True, content
            # fallback: maybe "text" field
            if "text" in choice:
                return True, choice["text"]
        # error structure?
        if "error" in data:
            err_msg = data["error"].get("message", str(data["error"]))
            return False, f"Groq Error: {err_msg}"
    except Exception as e:
        append_log("ERROR", f"Parsing Groq response structure: {e}")
        return False, f"Unexpected Groq response format: {e}"

    # final fallback: return whole blob
    append_log("ERROR", f"Groq returned unexpected payload: {json.dumps(data)[:1000]}")
    return False, f"Unexpected Groq response: {json.dumps(data)[:1000]}"


# -------------------------
# Email (SMTP) helper
# -------------------------
def send_email_smtp(to_address: str, subject: str, content: str) -> Tuple[bool, str]:
    """Sends email using SMTP credentials in streamlit secrets"""
    if not all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS]):
        return False, "SMTP credentials missing in streamlit secrets."

    try:
        msg = EmailMessage()
        msg["From"] = SMTP_USER
        msg["To"] = to_address
        msg["Subject"] = subject
        msg.set_content(content)

        server = smtplib.SMTP(host=SMTP_HOST, port=int(SMTP_PORT), timeout=20)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        append_log("INFO", f"Email sent to {to_address}")
        return True, f"Email sent to {to_address}"
    except Exception as e:
        append_log("ERROR", f"Email send failed: {e}")
        return False, f"Email send failed: {e}"


# -------------------------
# SMS (Twilio REST) helper
# -------------------------
def send_sms_twilio(to_number: str, body_text: str) -> Tuple[bool, str]:
    """Send SMS via Twilio REST API (requires TWILIO_SID, TWILIO_AUTH, TWILIO_FROM in secrets)"""
    if not all([TWILIO_SID, TWILIO_AUTH, TWILIO_FROM]):
        return False, "Twilio credentials missing in streamlit secrets."

    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"
    payload = {
        "From": TWILIO_FROM,
        "To": to_number,
        "Body": body_text
    }
    # basic auth
    try:
        r = requests.post(url, data=payload, auth=(TWILIO_SID, TWILIO_AUTH), timeout=20)
    except Exception as e:
        append_log("ERROR", f"Twilio network error: {e}")
        return False, f"Twilio network error: {e}"

    if r.status_code >= 200 and r.status_code < 300:
        append_log("INFO", f"SMS sent to {to_number}")
        return True, f"SMS sent to {to_number}"
    else:
        try:
            err = r.json()
        except Exception:
            err = r.text
        append_log("ERROR", f"Twilio error {r.status_code}: {err}")
        return False, f"Twilio error {r.status_code}: {err}"


# -------------------------
# UI: Left sidebar / layout
# -------------------------
st.sidebar.title("Jade System")
st.sidebar.markdown("## Pages")
page = st.sidebar.radio("", ["Chat", "Home", "Email", "SMS", "Admin Dashboard"])

st.sidebar.markdown("---")
st.sidebar.markdown("### System status")
st.sidebar.write(f"- Groq: {'configured' if GROQ_KEY else 'missing'}")
st.sidebar.write(f"- SMTP: {'configured' if SMTP_HOST and SMTP_USER else 'missing'}")
st.sidebar.write(f"- Twilio: {'configured' if TWILIO_SID and TWILIO_AUTH else 'missing'}")

if st.sidebar.button("Clear local history (storage)"):
    st.session_state.messages = []
    append_log("WARN", "Local chat history cleared by user")
    st.sidebar.success("Local history cleared")


# -------------------------
# Page: Home
# -------------------------
if page == "Home":
    st.title("🤖 Jade AI — Home")
    st.write(
        "This is Jade — an advanced assistant app using Groq Llama models. "
        "Use the Chat page to talk, Email/SMS pages to test integrations, and Admin for logs."
    )

    st.markdown("### Quick start")
    st.markdown("1. Add Groq API key to streamlit secrets as GROQ_API_KEY.")
    st.markdown("2. (Optional) Add SMTP and Twilio credentials to send emails and SMS.")
    st.markdown("3. Open Chat, type in a message, press Send.")

# -------------------------
# Page: Chat (main)
# -------------------------
if page == "Chat":
    st.title("💬 Chat with Jade")
    st.markdown("Jade is polite and helpful. Temperature set low for stable replies.")

    # Input area
    user_input = st.text_input("Type your message:", key="chat_input")
    cols = st.columns([1, 0.2])
    with cols[1]:
        if st.button("Send"):
            text = st.session_state.get("chat_input", "").strip()
            if not text:
                st.warning("Please type a message first.")
            else:
                append_log("INFO", f"User: {text[:200]}")
                # Call Groq
                success, reply = run_groq_chat(text, st.session_state.messages)
                if success:
                    # Append both user and assistant for memory
                    st.session_state.messages.append({"role": "user", "content": text})
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    append_log("INFO", f"Assistant: {reply[:200]}")
                    st.success("Jade replied successfully.")
                else:
                    append_log("ERROR", f"Agent error: {reply}")
                    st.error(reply)

    # Display chat history
    st.markdown("### Conversation")
    if not st.session_state.messages:
        st.info("No messages yet — say hi!")
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"**You:** {msg['content']}")
            else:
                st.markdown(f"**Jade:** {msg['content']}")

    # Memory control
    mem = st.slider("Memory length (pairs of messages kept)", 1, 20, st.session_state.max_memory)
    st.session_state.max_memory = mem


# -------------------------
# Page: Email
# -------------------------
if page == "Email":
    st.title("📧 Email (SMTP)")
    st.markdown("Send a test email using SMTP configured in Streamlit secrets.")

    with st.form("email_form"):
        to_addr = st.text_input("To address", value="")
        subject = st.text_input("Subject", value="Hello from Jade")
        body = st.text_area("Message body", value="This is a test email from Jade.")
        submitted = st.form_submit_button("Send Email")
    if submitted:
        ok, msg = send_email_smtp(to_addr, subject, body)
        if ok:
            st.success(msg)
        else:
            st.error(msg)
            st.write("Make sure SMTP secrets (SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS) are set.")


# -------------------------
# Page: SMS
# -------------------------
if page == "SMS":
    st.title("📱 SMS (Twilio)")
    st.markdown("Send a test SMS using your Twilio credentials in Streamlit secrets.")

    with st.form("sms_form"):
        to_number = st.text_input("To phone number (+E.164)", value="")
        sms_body = st.text_area("SMS body", value="Hello from Jade (test SMS).")
        sent = st.form_submit_button("Send SMS")
    if sent:
        ok, msg = send_sms_twilio(to_number, sms_body)
        if ok:
            st.success(msg)
        else:
            st.error(msg)
            st.write("Make sure Twilio secrets (TWILIO_SID, TWILIO_AUTH, TWILIO_FROM) are set.")


# -------------------------
# Page: Admin Dashboard
# -------------------------
if page == "Admin Dashboard":
    st.title("🛠 Admin Dashboard")
    st.markdown("View logs and control the app.")

    # show logs
    st.subheader("Logs (most recent first)")
    logs_rev = list(reversed(st.session_state.logs))
    if not logs_rev:
        st.info("No logs yet.")
    else:
        for ts, level, text in logs_rev[:200]:
            if level == "ERROR":
                st.error(f"{ts} • {level} • {text}")
            elif level == "WARN":
                st.warning(f"{ts} • {level} • {text}")
            else:
                st.write(f"{ts} • {level} • {text}")

    st.markdown("---")
    st.subheader("Admin actions")
    if st.button("Clear logs"):
        st.session_state.logs = []
        st.success("Logs cleared.")
    if st.button("Reset chat memory"):
        st.session_state.messages = []
        st.success("Chat memory cleared.")


# -------------------------
# Footer / small note
# -------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ — JADE AI")
