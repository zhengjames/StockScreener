from simpleRequest import RequestHandler
from stockData import StockData
from TechnicalIndicators import Macd
import csv
import pprint
request_handler = RequestHandler()
response = request_handler.get_response()
"""response.text.splitlines() is a list of strings"""
print(response.text)
stock_response = StockData(response.text)
my_macd = Macd()
results = my_macd.calc_macd(data_frame=stock_response.data_frame.iloc[::-1])


stock_response

print(stock_response.data_frame)