import csv
import pandas as pd
from TechnicalAlgorithms import Macd

class StockData:

    def __init__(self, csv_response):
        self.date_index = 0
        self.open_index = 1
        self.high_index = 2
        self.low_index = 3
        self.close_index = 4
        self.volume_index = 5
        self.adj_close_index = 6
        self.init_data(csv_response)

    """parse csv response and store in dataframe"""
    def init_data(self, response_csv):
        self.data = [row for row in csv.reader(response_csv.splitlines())]
        headers = self.data[0]
        del self.data[0]
        self.data_frame = pd.DataFrame(self.data, columns=headers)
        self.data_frame[['Open', 'High', 'Low', 'Close', 'Volume','Adj. Close']] = \
            self.data_frame[['Open', 'High', 'Low', 'Close', 'Volume', 'Adj. Close']].apply(pd.to_numeric)


