from simpleRequest import RequestHandler
from stockData import StockData
from TechnicalScreener import MacdScreener
import json
import pandas as pd

predictions = {}
ticker_list = ["IBM", "AZN", "BMY", "AAOI", "CMG", "BAC"]
request_handler = RequestHandler()

json_data = {}
# json_data["__type__"] = "MACD"
# json_data["trigger_type"] = "FAST_SLOW_MA_CROSS"
# json_data["trigger_direction"] = "ABOVE"
# json_data["trigger_in_n_days"] = 10
json_data["__type__"] = "STOCHASTIC_OSCILLATOR"
json_data["trigger_cause"] = "SLOW_MA"
json_data["trigger_direction"] = "BETWEEN"
json_data["upper_bound"] = 20
json_data["lower_bound"] = 0



# macd_screener = MacdScreener(json_data)
stochastic_oscillator = StochasticScreener(json_data)

for ticker in ticker_list:
    print("========={}=========".format(ticker))
    print("Sending request".format(ticker))
    try:
        response = request_handler.get_response(ticker)
        stock_response = StockData(response.text)
    except Exception:
        print("invalid request or response")
        continue
    print("Received response".format(ticker))
    """response.text.splitlines() is a list of strings"""

    # print(macd_screener.screen(stock_response.data_frame))

    # stochastic_oscillator = StochasticOscillator()
    print(stochastic_oscillator.screen(stock_response.data_frame))
    # stochastic_oscillator.calculate(stock_response.data_frame)

# print(predictions)