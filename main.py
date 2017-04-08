from simpleRequest import RequestHandler
from stockData import StockData
from TechnicalAlgorithms import *
import pandas as pd

predictions = {}
ticker_list = ["IBM"]
request_handler = RequestHandler()
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
    # my_macd = Macd()
    # stock_df = stock_response.data_frame
    #
    # try:
    #     print("Begin calculating MACD")
    #     results = my_macd.calc_macd(data_frame=stock_df)
    # except Exception as e:
    #     print("{} does not have sufficient historical"
    #           " data points to calculate MACD".format(ticker))
    #     print(e)
    #     continue
    #
    # my_data_parser = DataParser()
    # try:
    #     print("Begin parsing MACD")
    #     parsedResults = my_data_parser.parse_macd_signal_intersect(results[['date', 'center_line']])
    # except RuntimeError as e:
    #     print("Error parsing MACD into intersecting segments: {}".format(e))
    #     continue
    #
    # try:
    #     latestIndex = my_data_parser.parse_most_recent_macd_signal_intersect(results[['date', 'center_line']])
    # except RuntimeError as e:
    #     print("Error parsing the most recent MACD segment from previous intersection: {}".format(e))
    #     continue
    # #create artificial dates 1,2,3,4,5...
    # y_array = np.linspace(start=len(latestIndex), stop=1, num=len(latestIndex), dtype=int)
    # data_frame = pd.concat([pd.DataFrame({'x': latestIndex.center_line}), pd.DataFrame({'y': y_array})], axis=1)
    # forcaster = ForcastAlgorithms()
    # days = forcaster.predict_cross_above_zero_macd(data_frame, num_previous_data=4)
    # if INVALID_PREDICTION == days:
    #     print("MACD fast MA breaching slow MA is not likely to happen")
    # else:
    #     print("MACD fast MA will breach"
    #           " slow MA in {} days for {}".format(days, ticker))
    # predictions[ticker] = days

    stochastic_oscillator = StochasticOscillator()
    stochastic_oscillator.calculate(stock_response.data_frame)
    stochastic_oscillator.calculate(stock_response.data_frame)

# print(predictions)