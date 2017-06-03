import requests
from string import Template
import logging
import pandas as pd
from io import StringIO

class QuandlRequest:

    def get_response(self, ticker):
        logging.info("Sending request for stock info on {}".format(ticker))
        response = requests.get(self.get_url_template().substitute(TICKER = ticker))

        if 200 != response.status_code:
            raise Exception('Failed response from data center response status code {}'
                            .format(response.status_code))
        return response

    def get_url_template(self):
        return Template("""https://www.quandl.com/api/v3/datasets/WIKI/$TICKER.csv?
        api_key=Pz4pH-vyzazGW9961wYm&&start_date=2016-01-01""")

    def get_response_dataframe(self, ticker):
        response = self.get_response(ticker)
        #turns to dataframe
        return pd.read_csv(StringIO(response.content.decode('utf-8')))

    def convert_csv_to_dataframe(self, csv):
        self.data = [row for row in csv.reader(csv.splitlines())]
        headers = self.data[0]
        del self.data[0]
        self.data_frame = pd.DataFrame(self.data, columns=headers)
        self.data_frame[['Open', 'High', 'Low', 'Close', 'Volume', 'Adj. Close']] = \
            self.data_frame[['Open', 'High', 'Low', 'Close', 'Volume', 'Adj. Close']].apply(pd.to_numeric)



