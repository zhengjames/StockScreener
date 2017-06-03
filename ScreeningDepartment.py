from TechnicalScreener import ScreenerFactory
import logging
"""class that holds all of the screeners"""
class ScreeningDepartment:

    def __init__(self):
        self.screener_factory = ScreenerFactory()
        self.screener_list = []
    '''given blueprint in json, create screener'''
    def init_screener_list(self, screeners_json_list):
        logging.info("ScreeningDepartment attempt to construct all screeners")
        for screener_json in screeners_json_list:
            try:
                self.screener_list.append(self.screener_factory.create_screener(screener_json))
            except Exception as e:
                logging.ERROR("Failed Screener creation for screener={}".format(screener_json["__type__"]))
            logging.info("Successfully created screener={}".format(screener_json.get("__type__")))

    def run_all_screener_on_ticker(self, ticker, dataframe):
        if len(self.screener_list) == 0:
            logging.WARNING("List screener is empty for ticker={}", ticker)
            return
        result_arr = []
        for screener in self.screener_list:
            logging.info("Running screener __type__={} ticker={}".format(screener.__type__, ticker ))
            try:
                result_arr.append(screener.screen(dataframe))
            except Exception as e:
                logging.error("Failed screening for screener={} ticker={} error={}"
                              .format(screener.__type__, ticker, e))

        logging.info("Screened entire list screener={}".format(self.screener_list))
        return (ticker, result_arr)





