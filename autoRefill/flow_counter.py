from datetime import date
from tinydb import TinyDB, Query


class FlowCounter:

    #  TODO run it as a separete thread on start of Main(). Purpose for this class is only to count flow, save to db and reset state on midnight
    def __init__(self, database=TinyDB('db.json')):
        self.database = database.table("auto_refill")
        # self.database.insert({'type': 'flow_count_date', 'date': "29-08-2022"})

    def run(self):
        # while True:
            # collect data
            # if data != 0:
              if self.should_daily_refill_counter_be_reset(): self.reset_counter()
            #  calculate water_amount
            #  amount_in_database += water_amount
            # pass

    def should_daily_refill_counter_be_reset(self):
        return self.database.get(Query().type == 'flow_count_date')['date'] != self.get_current_date()

    def reset_counter(self):
        self.database.update({'flow': 0}, Query().type == 'daily_refill_flow')
        self.database.update({'date': self.get_current_date()}, Query().type == 'flow_count_date')

    @staticmethod
    def get_current_date():
        return date.today().strftime("%d-%m-%Y")

if __name__ == "__main__":
    dupa = FlowCounter()
    print(dupa.should_daily_refill_counter_be_reset())
    dupa.run()