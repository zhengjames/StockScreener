import requests
from string import Template


class RequestHandler:
    url_template = Template("""http://ichart.finance.yahoo.com/table.csv?s=$TICKER&a=00&b=10&c=2016&d=
    {date.addMonths(-1).format('MM')}&e={date.today.format('dd')}&f={date.today.format('yyyy')}""");

    def get_response(self, ticker):
        response = requests.get(self.url_template.substitute(TICKER = ticker))
        if 200 != response.status_code:
            raise Exception('failed response from yahoo response status code {}'
                            .format(response.status_code))



        return response
