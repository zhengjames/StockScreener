import requests
from string import Template
import logging
import pandas as pd
import Utilities.DataPrepUtil as data_util
from io import StringIO

class DataRequest:
    def fetch_historical_time_series(self, tickers):
        if type(tickers) is list:
            request_url = self.multi_tickers_request_url_template.substitute(TICKER=','.join(tickers))

        else:
            request_url = self.one_ticker_request_url_template.substitute(TICKER=tickers)

        response = requests.get(request_url, 3)

        if 200 != response.status_code:
            raise Exception('Failed response from data center response status code {}'
                            .format(response.status_code))
        dataframe = pd.read_csv(StringIO(response.content.decode('utf-8')))
        data_util.normalize_col_names(dataframe)
        return dataframe

    def convert_csv_to_dataframe(self, csv):
        self.data = [row for row in csv.reader(csv.splitlines())]
        headers = self.data[0]
        del self.data[0]
        self.data_frame = pd.DataFrame(self.data, columns=headers)
        self.data_frame[['open', 'high', 'low', 'close', 'volume', 'adj. close']] = \
            self.data_frame[['open', 'high', 'low', 'close', 'volume', 'adj. close']].apply(pd.to_numeric)


class QuandlRequest(DataRequest):
    def __init__(self):
        self.nMostRecentDays = 60
        self.date = 20170101
        self.one_ticker_request_url_template = Template('https://www.quandl.com/api/v3/datasets/WIKI/$TICKER.csv?'
                        'api_key=Pz4pH-vyzazGW9961wYm&&limit={}'.format(self.nMostRecentDays))

        self.multi_tickers_request_url_template = Template('https://www.quandl.com/api/v3/datatables/WIKI/PRICES.csv?date.gte={}'
                        '&ticker=$TICKER&api_key=Pz4pH-vyzazGW9961wYm'.format(self.date))


class AlphavantageRequest(DataRequest):
    def __init__(self):
        self.one_ticker_request_url_template = Template('https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=$TICKER&datatype=csv&apikey=JF9VBJJRM1YDXH2W')






