import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = "realbehindinfo@gmail.com"
SMTP_PASSWORD = "hcxa hdls gzwt ahuj"

print(f"Testing login for {SMTP_USER} with password {SMTP_PASSWORD}...")

try:
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)
    print("SUCCESS! Logged into SMTP.")
    server.quit()
except Exception as e:
    print(f"ERROR: {str(e)}")
