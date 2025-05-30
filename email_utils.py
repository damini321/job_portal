import os
import smtplib
from email.mime.text import MIMEText

def send_application_confirmation_email(to_email, candidate_name, job_title, company_name):
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    from_email = os.getenv('FROM_EMAIL')

    subject = "Job Application Confirmation"
    body = f"""Dear {candidate_name},

You have successfully applied for {job_title} at {company_name}.

We will review your application shortly.

Regards,
Job Portal Team
"""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(from_email, to_email, msg.as_string())
    except Exception as e:
        print("Error sending email:", e)
