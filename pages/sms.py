import streamlit as st
from modules.actions import send_sms

def sms_page():
    st.title("📱 Send SMS")

    to = st.text_input("Send To (phone number):")
    text = st.text_area("Message:")

    st.write("### Twilio Credentials")
    account_sid = st.text_input("Account SID:")
    auth_token = st.text_input("Auth Token:", type="password")
    from_num = st.text_input("Twilio Phone Number:")

    if st.button("Send SMS"):
        if not to or not text:
            st.warning("Fill all fields!")
        else:
            result = send_sms(account_sid, auth_token, from_num, to, text)
            st.info(result)
