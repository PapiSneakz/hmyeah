import smtplib
import os
from email.mime.text import MIMEText

class EmailNotifier:
    def __init__(self):
        self.user = os.getenv("EMAIL_USER")
        self.password = os.getenv("EMAIL_PASS")
        self.to = os.getenv("EMAIL_TO")

    def send(self, subject, body):
        if not self.user or not self.password or not self.to:
            print("[WARN] Email not configured")
            return
        
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.user
        msg["To"] = self.to

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.user, self.password)
                server.sendmail(self.user, [self.to], msg.as_string())
            print("[INFO] Email sent")
        except Exception as e:
            print("[ERROR] Failed to send email:", e)
