import smtplib
import secrets
import time
from email.message import EmailMessage
import os

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Store OTP and timestamp
otp_store = {}  # Structure: {email: {"otp": str, "timestamp": float}}

OTP_EXPIRY_SECONDS = 600  

def generate_otp():
    return str(secrets.randbelow(900000) + 100000)

def send_otp_email(to_email, otp):
    msg = EmailMessage()
    msg['Subject'] = 'Your OTP Code'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg.set_content(f'Your OTP is: {otp}')

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception:
        raise Exception("Email sending failed.")

def store_otp(email, otp):
    otp_store[email] = {"otp": otp, "timestamp": time.time()}

def verify_otp(email, user_otp):
    record = otp_store.get(email)
    if not record:
        return False, "No OTP found."

    if time.time() - record["timestamp"] > OTP_EXPIRY_SECONDS:
        del otp_store[email]
        return False, "OTP expired."

    if record["otp"] != user_otp:
        return False, "Invalid OTP."

    del otp_store[email] 
    return True, "OTP verified."
