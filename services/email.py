import smtplib
from email.message import EmailMessage


def send_email(
    subject: str,
    content: str,
    *,
    smtp_server: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    notification_email: str,
) -> bool:
    if not smtp_user or not smtp_password or not notification_email:
        print("DEBUG: Email configuration missing. Skipping email.")
        return False

    msg = EmailMessage()
    msg.set_content(content)
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = notification_email

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"DEBUG: Email sent to {notification_email}")
        return True
    except Exception as exc:
        print(f"DEBUG: Failed to send email: {str(exc)}")
        return False
