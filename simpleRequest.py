import requests


class RequestHandler:
    url = """http://ichart.finance.yahoo.com/table.csv?s=WU&a=00&b=19&c=2010&d=
    {date.addMonths(-1).format('MM')}&e={date.today.format('dd')}&f={date.today.format('yyyy')}""";

    def get_response(self):
        response = requests.get(self.url)

        return response
