import random

from database.db import Database
import datetime
import tqdm


class RandomDataGenerator:

    database = Database()
    today = datetime.date.today()
    now = datetime.datetime.now()
    current_day = today

    def generate_random_data_flow(self, days_amount: int):
        for _ in tqdm.tqdm(range(0, days_amount)):
            self.current_day = (self.current_day + datetime.timedelta(days=1))
            current_flow = random.randint(800, 1000)
            self.database.insert(table='auto_refill_history', columns=['date', 'flow'], values=[self.current_day, current_flow])
            print(f'Day: {self.current_day.strftime("%d-%m-%Y")}, flow: {current_flow}')

    def generate_random_data_temperature(self, sample_amount: int):
        for _ in tqdm.tqdm(range(0, sample_amount)):
            self.now = (self.now + datetime.timedelta(hours=1, minutes=random.randint(0, 60)))
            current_temp = round(random.uniform(20.0, 27.0), 2)
            self.database.insert(table='temperature_history', columns=['date_time', 'temperature'], values=[self.now, current_temp])


if __name__ == '__main__':
    RandomDataGenerator().generate_random_data_temperature(1000)


