import requests
from string import Template
import logging
import pandas as pd
import Utilities.DataPrepUtil as data_util
from io import StringIO

class QuandlRequest:
    def __init__(self):
        self.nMostRecentDays = 60
        self.date = 20170101


    def get_response(self, tickers_arr):
        logging.info("Sending request for stock info on {}".format(tickers_arr))
        #three seconds timeout
        # response = requests.get(self.get_url_template().substitute(TICKER = ticker), 3)
        tickers_string_csv = ','.join(tickers_arr)
        response = requests.get(self.get_url_multi_tickers_template().substitute(TICKER = tickers_string_csv))

        if 200 != response.status_code:
            raise Exception('Failed response from data center response status code {}'
                            .format(response.status_code))
        return response

    def get_url_template(self):
        return Template('https://www.quandl.com/api/v3/datasets/WIKI/$TICKER.csv?'
                        'api_key=Pz4pH-vyzazGW9961wYm&&limit={}'.format(self.nMostRecentDays))
    def get_url_multi_tickers_template(self):
        return Template('https://www.quandl.com/api/v3/datatables/WIKI/PRICES.csv?date.gte={}'
                        '&ticker=$TICKER&api_key=Pz4pH-vyzazGW9961wYm'.format(self.date))

    def get_response_dataframe(self, ticker):
        try:
            response = self.get_response(ticker)
            finalData = pd.read_csv(StringIO(response.content.decode('utf-8')))
        except Exception as e:
            raise e
        data_util.normalize_col_names(finalData)
        finalData = data_util.make_asc_date_order_quandl(finalData)
        return finalData

    def convert_csv_to_dataframe(self, csv):
        self.data = [row for row in csv.reader(csv.splitlines())]
        headers = self.data[0]
        del self.data[0]
        self.data_frame = pd.DataFrame(self.data, columns=headers)
        self.data_frame[['open', 'high', 'low', 'close', 'volume', 'adj. close']] = \
            self.data_frame[['open', 'high', 'low', 'close', 'volume', 'adj. close']].apply(pd.to_numeric)



