import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import logging


class SendEmail:

    def __init__(self, subject: str, body: str):
        self.subject = subject
        self.body = body

        self.sender = 'reefaquariumcontroller@gmail.com'
        self.password = os.getenv('GMAIL_API_KEY')
        self.receiver = 'marcin.lipinski5@gmail.com'
        if self.password is not None:
            self.send()
            logging.info(f"Email sent. Subject: {self.subject}; Body: {self.body}")
        else:
            logging.warning(f"Unable to send and email, api key is not set. Subject: {self.subject}; Body: {self.body}")

    def send(self):
        try:
            message = MIMEMultipart()
            message['From'] = self.sender
            message['To'] = self.receiver
            message['Subject'] = self.subject
            message.attach(MIMEText(self.body, 'plain'))
            session = smtplib.SMTP('smtp.gmail.com', 587)
            session.starttls()
            session.login(self.sender, self.password)
            text = message.as_string()
            session.sendmail(self.sender, self.receiver, text)
            session.quit()
        except Exception as e:
            logging.warning(f"Failed to send email, an error occurred: {e}")


if __name__ == "__main__":
    SendEmail('test', 'test2')