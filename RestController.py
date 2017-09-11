import bottle
from bottle import request, response, post, get, run, hook, app, Bottle
from simpleRequest import QuandlRequest
from ScreeningDelegate import ScreeningDelegate
import logging
import json
from bottledaemon import daemon_run

request_handler = QuandlRequest()
screening_delegate = ScreeningDelegate()


app = bottle.app()
logging.basicConfig(filename='example.log',level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())

@app.route('/cors', method=['OPTIONS', 'GET'])
def lvambience():
    response.headers['Content-type'] = 'application/json'
    return '[1]'

@bottle.route('/screen', method='POST')
def screen_stock():

    logging.info("received request on endpoint /screen")
    '''Handles name creation'''

    request_json = request.json
    screener_json_arr = request_json.get("screener_arr")
    ticker_arr = request_json.get("tickers_arr")
    flags_dict = {'request_only_matched_criteria': False}
    #request_json.get("flags")
    result = screening_delegate.screen_all(screener_json_arr, ticker_arr, flags_dict)

    response.content_type = 'application/json'
    logging.info("controller returning results: {}".format(json.dumps(result)))
    return json.dumps(result)

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

    '''allow only this ip address'''
    allowed_url = 'http://127.0.0.1:' + bottle.request.environ['HTTP_ORIGIN'][-4:]
    bottle.response.headers['Access-Control-Allow-Credentials'] = 'true'
    bottle.response.headers['Access-Control-Allow-Origin'] = allowed_url
    bottle.response.headers['Access-Control-Allow-Methods'] = \
        'GET, POST, PUT, OPTIONS'
    bottle.response.headers['Access-Control-Allow-Headers'] = \
        'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

app = bottle.app()
app.run(port=8070)
# run(server='gunicorn', host='localhost', port=8070, debug=True, timeout=9999)
# The following lines will call the BottleDaemon script and launch a daemon in the background.
# if __name__ == "__main__":
#     daemon_run()

