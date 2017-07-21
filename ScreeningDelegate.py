import logging
from simpleRequest import QuandlRequest
from ScreeningDepartment import ScreeningDepartment
class ScreeningDelegate:
    def __init__(self):
        self.request_handler = QuandlRequest()
        self.response = []
        self.screeners_list = []
        self.screening_department = ScreeningDepartment()


    """ given array of screeners and tickers, use all screener on each ticker"""
    def screen_all(self, screeners_json_list, tickers_arr, flags_dict):
        logging.info("Begin to screen all tickers {} through {}".format( tickers_arr, screeners_json_list))
        self.screening_department.init_screener_list(screeners_json_list)
        result = {}
        for ticker in tickers_arr:
            logging.info("========={}=========".format(ticker))
            try:
                ticker_dataframe = self.fetchStockData(ticker)
                if not ticker_dataframe.empty:
                    tick, screened_result_list = self.screening_department.run_all_screener_on_ticker(
                        ticker, ticker_dataframe)
                    result[ticker] = screened_result_list
            except Exception as e:
                logging.error("Failed ticker={} error={}".format(ticker, e))

        result = self.format_returned_results(result, flags_dict)
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

    def format_returned_results(self, screened_result, flags):
        formatted_result = {}
        logging.info("Begin formatting results")
        #if flag is not None
        if flags and flags.get("request_only_matched_criteria"):
            for ticker, screened_result_arr in screened_result.items():
                if self.pass_screening(screened_result_arr):
                    logging.info("ticker={} passed flag criteria".format(ticker))
                    formatted_result[ticker] = screened_result_arr
            return formatted_result
        return screened_result

    #given [{one_screener_result},{one_screener_result},{...}] return if pass all
    def pass_screening(self, screening_result_arr):
        for dict in screening_result_arr:
            if not dict["pass"]:
                return False
        return True




