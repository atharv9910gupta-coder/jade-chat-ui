import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client

# If you want email sending:
def send_email(to_email, subject, message, sender_email, sender_password):
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return "Email Sent!"
    except Exception as e:
        return f"Error: {e}"


# If you want SMS sending:
def send_sms(account_sid, auth_token, from_number, to_number, text):
    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=text,
            from_=from_number,
            to=to_number
        )
        return f"SMS Sent! Message SID: {message.sid}"
    except Exception as e:
        return f"Error: {e}"

