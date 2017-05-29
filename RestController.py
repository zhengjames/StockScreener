import bottle
from bottle import request, response, post, get, run, hook, app, Bottle
from TechnicalScreener import *
from simpleRequest import QuandlRequest
from stockData import StockData
import json
import traceback
import numpy as np
request_handler = QuandlRequest()
screener_factory = ScreenerFactory()
app = bottle.app()

@app.route('/cors', method=['OPTIONS', 'GET'])
def lvambience():
    response.headers['Content-type'] = 'application/json'
    return '[1]'

@post('/screen')
def screen_stock():

    '''Handles name creation'''
    screener_json_arr = request.json["screener_arr"]
    ticker_arr = request.json["tickers_arr"]
    is_match_criterias = True
    if 'is_match_criteria' not in request.json or False == request.json['is_match_criteria']:
        is_match_criteria = False

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
        one_ticker_result = []
        #does it match all the filter criteria?
        is_pass_criterias = True
        #run all screeners individually
        for screener_json in screener_json_arr:
            try:
                screener = screener_factory.create_screener(screener_json)
                one_screener_result = {screener_json["__type__"]: screener.screen(stock_data_df)}
                if one_screener_result[screener_json["__type__"]]["pass"] \
                        == False and is_match_criterias:
                    is_pass_criterias = False
                one_ticker_result.append(one_screener_result)

            except Exception as e:
                result[ticker].append("error running screener {}, {}".format(screener_json["__type__"], e))
                traceback.print_exc()

                break;
        #only add to response when
        if True == is_pass_criterias:
            result[ticker].append(one_ticker_result)
        else:
            del result[ticker]

    response.content_type = 'application/json'

    return json.dumps(dict(result))

@bottle.route('/screen', method='OPTIONS')
def enable_cors_generic_route():
    """
    This route takes priority over all others. So any request with an OPTIONS
    method will be handled by this function.

    See: https://github.com/bottlepy/bottle/issues/402

    NOTE: This means we won't 404 any invalid path that is an OPTIONS request.
    """
    add_cors_headers()


@bottle.hook('after_request')
def enable_cors_after_request_hook():
    """
    This executes after every route. We use it to attach CORS headers when
    applicable.
    """
    add_cors_headers()

def add_cors_headers():
    bottle.response.headers['Access-Control-Allow-Origin'] = '*'
    bottle.response.headers['Access-Control-Allow-Methods'] = \
        'GET, POST, PUT, OPTIONS'
    bottle.response.headers['Access-Control-Allow-Headers'] = \
        'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

app = bottle.app()
app.run(port=8070)
# run(server='gunicorn', host='localhost', port=8070, debug=True, timeout=9999)