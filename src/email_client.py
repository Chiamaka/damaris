import base64
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, Email,
                                   FileContent, FileName,
                                   FileType)
from . import logger

log = logger.logger()


def send_email(email, text_file):
    """Send email with transcription attached"""
    mail = Mail(
        from_email=Email('chi@damaris.com', "Chi from Damaris"),
        to_emails=email,
        subject="Your transcription from Damaris 🔥",
        plain_text_content="Thank you for using Damaris. Please find \
        attached your transcribed file."
    )

    with open(text_file, 'rb') as f:
        data = f.read()

    encoded_text_file = base64.b64encode(data).decode()
    attachment = Attachment()
    attachment.file_content = FileContent(encoded_text_file)
    attachment.file_type = FileType("text/plain")
    attachment.file_name = FileName("transcription.txt")
    mail.attachment = attachment

    try:
        sg = SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        sg.send(mail)
        log.info('Email sent successfully!')
    except Exception as e:
        log.error("Could not send email {}".format(e))
