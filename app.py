# app.py
import streamlit as st
import requests
import json
from datetime import datetime
from modules import storage, tools

st.set_page_config(page_title="Jade AI", page_icon="🤖", layout="wide")

# Load secrets
if "GROQ_API_KEY" not in st.secrets:
    st.error("Please add GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

GROQ_KEY = st.secrets["GROQ_API_KEY"]

# Optional services secrets — safe to be missing; pages will show not configured
SMTP_HOST = st.secrets.get("SMTP_HOST")
SMTP_PORT = st.secrets.get("SMTP_PORT")
SMTP_USER = st.secrets.get("SMTP_USER")
SMTP_PASS = st.secrets.get("SMTP_PASS")
EMAIL_FROM = st.secrets.get("EMAIL_FROM")

TWILIO_SID = st.secrets.get("TWILIO_SID")
TWILIO_AUTH = st.secrets.get("TWILIO_AUTH")
TWILIO_FROM = st.secrets.get("TWILIO_FROM")

ADMIN_PW = st.secrets.get("ADMIN_PASSWORD", "admin")  # default only for quick testing

storage.ensure_data_dir()

st.sidebar.title("Jade System")
page = st.sidebar.radio("Pages", ["Chat", "Home", "Email", "SMS", "Admin Dashboard"])

st.sidebar.markdown("### System status")
st.sidebar.write(f"- Groq: {'configured' if GROQ_KEY else 'missing'}")
st.sidebar.write(f"- SMTP: {'configured' if SMTP_USER and SMTP_PASS else 'missing'}")
st.sidebar.write(f"- Twilio: {'configured' if TWILIO_SID and TWILIO_AUTH and TWILIO_FROM else 'missing'}")
if st.sidebar.button("Clear local history (storage)"):
    storage.append_log({"time": str(datetime.utcnow()), "event": "clear_history_requested"})
    # clear chat file
    with open("data/chat_history.json", "w", encoding="utf8") as f:
        json.dump([], f)
    st.sidebar.success("Chat history cleared")

# ------------------------------
# Groq call (simple helper)
# ------------------------------
def run_groq_chat(prompt, history_messages):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}

    # Build messages: simple system + history + prompt
    messages = [{"role":"system", "content":"You are Jade, a helpful customer support assistant."}]
    messages.extend(history_messages)
    messages.append({"role":"user","content":prompt})

    body = {"model":"llama3-8b-8192", "messages": messages, "max_tokens": 300}

    try:
        r = requests.post(url, headers=headers, json=body, timeout=30)
        if r.status_code != 200:
            # return error text for debugging
            return False, f"Groq HTTP {r.status_code}: {r.text}"
        data = r.json()
        if "error" in data:
            return False, data["error"].get("message", str(data))
        content = data["choices"][0]["message"]["content"]
        return True, content
    except Exception as e:
        return False, str(e)

# ------------------------------
# Pages
# ------------------------------
if page == "Home":
    st.title("🏠 Jade AI — Home")
    st.markdown("Welcome — your agent is Jade. Use the Chat page to talk.")

elif page == "Chat":
    st.title("💬 Chat with Jade")
    # load recent chat as messages (list of dicts with role/content)
    chat_history = storage.read_chat()
    # show messages
    for msg in chat_history:
        role = msg.get("role","user")
        content = msg.get("content","")
        if role == "assistant":
            st.info(f"**Jade:** {content}")
        else:
            st.success(f"**You:** {content}")

    with st.form("chat_form"):
        txt = st.text_input("Type your message")
        submitted = st.form_submit_button("Send")
        if submitted:
            if not txt or txt.strip()=="":
                st.warning("Type a message first.")
            else:
                # append user msg to storage
                entry_user = {"role":"user","content":txt,"time":str(datetime.utcnow())}
                storage.append_chat(entry_user)

                # prepare history messages for Groq: convert stored chat to messages format
                stor = storage.read_chat()
                messages_for_api = []
                for e in stor:
                    messages_for_api.append({"role": e.get("role","user"), "content": e.get("content","")})

                ok, reply = run_groq_chat(txt, messages_for_api)
                if not ok:
                    st.error("Agent error: " + reply)
                    storage.append_log({"time":str(datetime.utcnow()), "event":"groq_error","detail":reply})
                else:
                    # show and store assistant reply
                    st.info(f"**Jade:** {reply}")
                    storage.append_chat({"role":"assistant","content":reply,"time":str(datetime.utcnow())})
                    storage.append_log({"time":str(datetime.utcnow()), "event":"chat","user_input":txt})

elif page == "Email":
    st.title("📧 Email — send a test email")
    st.write("This page uses SMTP. Add SMTP_* secrets to enable.")

    to_addr = st.text_input("To email")
    subject = st.text_input("Subject", value="Message from Jade")
    body = st.text_area("Body", value="Hello — this is a test from Jade.")

    if st.button("Send Email"):
        if not (SMTP_HOST and SMTP_PORT and SMTP_USER and SMTP_PASS and EMAIL_FROM):
            st.error("SMTP not configured in secrets.")
        elif not to_addr:
            st.warning("Enter recipient email.")
        else:
            ok, detail = tools.send_email_smtp(
                SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, EMAIL_FROM, to_addr, subject, body
            )
            if ok:
                st.success("Email sent")
                storage.append_log({"time":str(datetime.utcnow()), "event":"email_sent","to":to_addr})
            else:
                st.error("Email error: " + str(detail))
                storage.append_log({"time":str(datetime.utcnow()), "event":"email_error","detail":str(detail)})

elif page == "SMS":
    st.title("📱 SMS — send a test SMS")
    st.write("Requires Twilio secrets (TWILIO_SID, TWILIO_AUTH, TWILIO_FROM).")

    to_num = st.text_input("Recipient phone (+countrycode)")
    sms_text = st.text_area("Message", value="Hello from Jade!")

    if st.button("Send SMS"):
        if not (TWILIO_SID and TWILIO_AUTH and TWILIO_FROM):
            st.error("Twilio not configured in secrets.")
        elif not to_num:
            st.warning("Enter recipient phone number.")
        else:
            ok, detail = tools.send_sms_twilio(TWILIO_SID, TWILIO_AUTH, TWILIO_FROM, to_num, sms_text)
            if ok:
                st.success("SMS sent, sid: " + str(detail))
                storage.append_log({"time":str(datetime.utcnow()), "event":"sms_sent","to":to_num,"sid":str(detail)})
            else:
                st.error("SMS error: " + str(detail))
                storage.append_log({"time":str(datetime.utcnow()), "event":"sms_error","detail":str(detail)})

elif page == "Admin Dashboard":
    st.title("🛠 Admin Dashboard")
    st.write("Protected: enter admin password to view logs.")

    pw = st.text_input("Admin password", type="password")
    if st.button("Unlock Admin"):
        if pw == ADMIN_PW:
            st.success("Unlocked")
            logs = storage.read_logs()
            st.write("### Logs")
            st.write(logs[::-1])  # newest first

            st.write("### Chat history")
            st.write(storage.read_chat()[::-1])
            if st.button("Export chat as JSON"):
                st.download_button("Download JSON", json.dumps(storage.read_chat(), indent=2), file_name="chat_history.json")
        else:
            st.error("Wrong password.")
