import logging
from simpleRequest import QuandlRequest
import StockData
from ScreeningDepartment import ScreeningDepartment
class ScreeningDelegate:
    def __init__(self):
        self.request_handler = QuandlRequest()
        self.response = []
        self.screeners_list = []
        self.screening_department = ScreeningDepartment()


    """ given array of screeners and tickers, use all screener on each ticker"""
    def screen_all(self, screeners_json_list, tickers_arr):
        logging.info("Begin to screen all tickers {} through {}".format( tickers_arr, screeners_json_list))
        self.screening_department.init_screener_list(screeners_json_list)
        result = {}
        for ticker in tickers_arr:
            logging.info("========={}=========".format(ticker))
            try:
                ticker_dataframe = self.fetchStockData(ticker)
                tick, screened_result_list = self.screening_department.run_all_screener_on_ticker(
                    ticker, ticker_dataframe)
                result[ticker] = screened_result_list
            except Exception as e:
                logging.error("Failed ticker={}".format(ticker))

        return result


    """ Given a ticker, call api to get stock data and return them in a dataframe"""
    def fetchStockData(self, ticker):
        logging.info("Fetching ticker={}".format(ticker))
        try:
            stock_data_df = self.request_handler.get_response_dataframe(ticker)
        except Exception as e:
            print(e)
            logging.error(e)
            raise e
        logging.info("Received response for {}".format(ticker))
        """response.text.splitlines() is a list of strings"""
        return stock_data_df

    """runs the ticker through all the screener"""

    def format_results(self, ticker, screened_result):
        return []

