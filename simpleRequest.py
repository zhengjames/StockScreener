import requests
from string import Template


class RequestHandler:

    def get_response(self, ticker):
        response = requests.get(self.get_url_template().substitute(TICKER = ticker))
        if 200 != response.status_code:
            raise Exception('failed response from data center response status code {}'
                            .format(response.status_code))
        return response

    def get_url_template(self):
        raise NotImplementedError("please implement get_url_template method")


class QuandlRequest(RequestHandler):

    url_template = Template("""https://www.quandl.com/api/v3/datasets/WIKI/$TICKER.csv?
    api_key=Pz4pH-vyzazGW9961wYm&&start_date=2016-01-01""")

    def get_url_template(self):
        return self.url_template
