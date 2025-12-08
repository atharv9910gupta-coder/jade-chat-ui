# modules/tools.py
import smtplib
from email.message import EmailMessage
import requests
import os

def send_email_smtp(smtp_host, smtp_port, smtp_user, smtp_pass, sender, to_address, subject, body):
    """
    Sends email using SMTP (TLS).
    Returns (True, "OK") or (False, "error message")
    """
    try:
        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = to_address
        msg["Subject"] = subject
        msg.set_content(body)

        server = smtplib.SMTP(smtp_host, int(smtp_port), timeout=20)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        return True, "Email sent"
    except Exception as e:
        return False, str(e)


def send_sms_twilio(account_sid, auth_token, from_number, to_number, message):
    """
    Sends SMS via Twilio REST API.
    Returns (True, sid) or (False, error)
    """
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    data = {
        "From": from_number,
        "To": to_number,
        "Body": message
    }
    try:
        resp = requests.post(url, data=data, auth=(account_sid, auth_token), timeout=20)
        if resp.status_code in (200, 201):
            return True, resp.json().get("sid", "")
        else:
            # Return Twilio error message if present
            try:
                return False, resp.json()
            except:
                return False, resp.text
    except Exception as e:
        return False, str(e)
