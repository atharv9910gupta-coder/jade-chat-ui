import streamlit as st

# Dummy email sender (works without any API)
def send_email(to, subject, body):
    # In real version you will add: SMTP or API (SendGrid, Mailgun, etc.)
    print("Email Sent!")
    print("To:", to)
    print("Subject:", subject)
    print("Body:", body)
    return True

# Dummy SMS sender (works without any API)
def send_sms(number, message):
    # In real version you will add: Twilio or SMS API
    print("SMS Sent!")
    print("Number:", number)
    print("Message:", message)
    return True

