import streamlit as st
from modules.actions import send_email

def email_page():
    st.title("📧 Send Email")

    to = st.text_input("Send To:")
    subject = st.text_input("Subject:")
    body = st.text_area("Message:")

    st.write("### Sender Email Login")
    sender_email = st.text_input("Your Email:")
    sender_pass = st.text_input("Your Email Password:", type="password")

    if st.button("Send Email"):
        if not to or not subject or not body:
            st.warning("Fill all fields!")
        else:
            result = send_email(to, subject, body, sender_email, sender_pass)
            st.info(result)
