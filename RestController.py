from bottle import request, response, post, get, run
from TechnicalAlgorithms import *
from simpleRequest import RequestHandler
from stockData import StockData
from TechnicalScreener import *

request_handler = RequestHandler()
screener_factory = ScreenerFactory()


@post('/names')
def screen_stock():
    '''Handles name creation'''
    screener_json_arr = request.json["screener_arr"]
    ticker_arr = request.json["tickers_arr"]
    result = {}
    for ticker in ticker_arr:
        #stores each ticker's results
        result[ticker] = []
        print("========={}=========".format(ticker))
        print("Sending request".format(ticker))
        try:
            stock_response = request_handler.get_response(ticker)
            stock_data_df = StockData(stock_response.text).data_frame
        except Exception as e:
            print(e)
            result[ticker].append(str(e))
            continue
        print("Received response".format(ticker))
        """response.text.splitlines() is a list of strings"""
        #run all screeners individually
        for screener_json in screener_json_arr:
            try:
                screener = screener_factory.create_screener(screener_json)
                result[ticker].append({screener_json["__type__"]: screener.screen(stock_data_df)})
            except Exception as e:
                result[ticker].append("error running screener {}, {}".format(screener_json["__type__"], e))
                break;


    response.content_type = 'application/json'
    return dict(result)


run(server='gunicorn', host='localhost', port=8080, debug=True, timeout=9999)