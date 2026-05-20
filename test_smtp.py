import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

def main():
    if not SMTP_USER or not SMTP_PASSWORD:
        raise SystemExit("SMTP_USER and SMTP_PASSWORD must be set to run this live check.")

    print(f"Testing login for {SMTP_USER}...")

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        print("SUCCESS! Logged into SMTP.")
        server.quit()
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    main()
