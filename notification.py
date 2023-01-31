from database.db import Database
from datetime import datetime
from send_email import SendEmail
import logging


class Notification:

    def __init__(self, database: Database, alert_type: str, email_subject='Reef Aquarium Notification'):
        self.timestamp = datetime.now().strftime('%d-%m-%y %H:%M')
        self.database = database
        self.alert_type = alert_type
        self.email_subject = email_subject

    def send(self):
        alert_status = self.database.select(table='alert', column='status', where=f'type="{self.alert_type}"', boolean_needed=True)
        email_status = self.database.select(table='alert', column='email_status', where=f'type="{self.alert_type}"', boolean_needed=True)
        if not alert_status:
            logging.info(f"Setting up alert notification for: {self.alert_type}")
            self.__set_up_alert()
        if not email_status:
            logging.info(f"Setting up email for: {self.alert_type}")
            self.__send_email()

    def reset(self):
        self.database.update(table='alert',
                             column='status',
                             value=False,
                             boolean_needed=True,
                             where=f'type="{self.alert_type}"')
        self.database.update(table='alert',
                             column='email_status',
                             value=False,
                             boolean_needed=True,
                             where=f'type="{self.alert_type}"')

    def __set_up_alert(self):
        self.database.update(table='alert',
                             column='status',
                             value=True,
                             boolean_needed=True,
                             where=f'type="{self.alert_type}"')
        self.database.update(table='alert',
                             column='date_time',
                             value=self.timestamp,
                             where=f'type="{self.alert_type}"')

    def __send_email(self):
        body = f'''
        {self.email_subject} \n
        {self.timestamp} \n
        {self.database.select(table='alert', column='description', where=f'type="{self.alert_type}"')}
        '''
        SendEmail(subject=self.email_subject, body=body)
        self.database.update(table='alert',
                             column='email_status',
                             value=True,
                             boolean_needed=True,
                             where=f'type="{self.alert_type}"')
