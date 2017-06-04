import TechnicalAlgorithms as ta
import numpy as np
import pandas as pd
from Utilities import AllConstants as CONSTANT
import logging
"""class that holds all of the screeners"""
class ScreeningDepartment:

    def __init__(self):
        self.screener_factory = ScreenerFactory()
        self.screener_list = []
    '''given blueprint in json, create screener'''
    def init_screener_list(self, screeners_json_list):
        logging.info("ScreeningDepartment attempt to construct all screeners")
        self.screener_list = []
        for screener_json in screeners_json_list:
            try:
                self.screener_list.append(self.screener_factory.create_screener(screener_json))
            except Exception as e:
                logging.error("Failed Screener creation for screener={} error={}"
                              .format(screener_json.get("__type__"), e))
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

    def clean_up(self):
        self.screener_list = []



class ScreenerFactory:

    def create_screener(self, json):
        if "MACD" == json.get("__type__"):
            return self.create_macd(json)
        elif "STOCHASTIC_OSCILLATOR" == json.get("__type__"):
            return self.create_stochastic(json)

    #create and return macd screener
    def create_macd(self, json):
        # {"__type__": "MACD_SCREENER",
        # "trigger_cause": "FAST_SLOW_MA_CROSS",
        # "trigger_direction": "ABOVE", "BELOW"
        # "trigger_in_n_days":
        # "trigger_target": 0
        # }
        macd = MacdScreener()
        macd.__type__ = json.get("__type__")
        macd.trigger_cause = json.get("trigger_cause")
        macd.trigger_direction = json.get("trigger_direction")
        macd.trigger_in_n_days = json.get("trigger_in_n_days")
        macd.trigger_target = json.get("trigger_target")
        macd.calculator = ta.Macd()
        macd.data_parser = ta.DataParser()
        return macd

    #create and return stochastic_oscillator screener
    def create_stochastic(self, json):
        '''
        :param json:
         {
            "__type__": "STOCHASTIC_OSCILLATOR",
            "__subtype__": RSI
            "trigger_cause": "SLOW_MA",
            "trigger_direction": "BETWEEN",
            "upper_bound": 25,
            "lower_bound": 0,
            "trigger_cause": "FAST_SLOW_MA_CROSS", `
            "trigger_direction": "ABOVE", "BELOW" `
            "trigger_in_n_days": `
        },
        :return:
        '''

        stochastic = StochasticScreener()
        stochastic.__type__ = json.get("__type__")
        stochastic.__subtype__ = json.get("__subtype__")
        stochastic.trigger_cause = json.get("trigger_cause")
        #plain old oscillator no prediction
        if json.get("trigger_direction") == CONSTANT.BETWEEN:
            stochastic.trigger_direction = json.get("trigger_direction")
            stochastic.upper_bound = json.get("upper_bound")
            stochastic.lower_bound = json.get("lower_bound")
        #prediction oscillator
        else:
            stochastic.trigger_direction = json.get("trigger_direction")
            stochastic.trigger_in_n_days = json("trigger_in_n_days")
            stochastic.trigger_target = json("trigger_target")

        #insert the type of calculator
        if CONSTANT.STOCH_SUB_RSI == stochastic.__subtype__:
            stochastic.calculator = ta.Stochastic_RSI()
        else:
            stochastic.calculator = ta.StochasticOscillator()

        return stochastic



class MacdScreener:

    def extract_most_recent_segment(self, data_frame):
        i = 0
        while i < len(data_frame):
            if data_frame.cross_over_indicator[i] == 'start':
                return data_frame[0:i+1]
            i += 1
        return []

    def screen(self, data):
        try:
            logging.info("Begin MACD screening")
            result_df = self.calculator.calculate(data_frame=data)
        except Exception as e:
            logging.error("Does not have sufficient historical"
                          " data points to calculate MACD")
            raise e

        try:
            logging.info("Begin extracting the most recent segment of MA intersection")
            self.data_parser.parse_macd_signal_intersect(result_df)
            most_recent_segment_df = self.extract_most_recent_segment(data_frame = result_df)
        except RuntimeError as e:
            logging.error("Error parsing MACD into intersecting segments: {}".format(e))
            raise e

        latest_index = most_recent_segment_df
        #create artificial dates 1,2,3,4,5...
        y_array = np.linspace(start=len(latest_index), stop=1, num=len(latest_index), dtype=int)
        data_frame = pd.concat([pd.DataFrame({'x': latest_index.center_line}), pd.DataFrame({'y': y_array})], axis=1)
        forcaster = ta.ForcastAlgorithms()

        #macd was crossed today, so sign of delta yesterday and today is different
        if 0 == self.trigger_in_n_days:
            days = forcaster.predict_just_crossed_zero_macd(data, self.trigger_direction)
            if days == 0:
                return {"pass":True, "prediction":0}

        days = forcaster.predict_cross_zero_macd(data_frame, trigger_direction=self.trigger_direction)


        if days == ta.INVALID_PREDICTION or days > self.trigger_in_n_days:
            logging.info("MACD fast MA breaching slow MA is not likely to happen")
        else:
            logging.info("MACD fast MA will breach"
                  " slow MA in {} days".format(days))

        if days != ta.INVALID_PREDICTION:
            return {"__type__":self.__type__ ,"pass":True, "prediction":days}
        else:
            return {"__type__":self.__type__ ,"pass":False, "prediction":ta.INVALID_PREDICTION}

class StochasticScreener:

    def screen(self, data):
        logging.info("Begin {}".format(self.__type__))
        k_df = self.calculator.calculate(data)

        currentValue = k_df.K_MA_3[0]
        #check if it is nan
        currentValue = 'nan' if currentValue != currentValue else currentValue

        #list of tuples (which moving average, value)
        current_stoch_value_list = []
        if CONSTANT.TRIGGER_CAUSE_FAST_MA == self.trigger_cause:
            current_stoch_value_list.append({CONSTANT.TRIGGER_CAUSE_FAST_MA: k_df["K"][0]})
        elif CONSTANT.TRIGGER_CAUSE_SLOW_MA == self.trigger_cause:
            current_stoch_value_list.append({CONSTANT.TRIGGER_CAUSE_SLOW_MA: k_df["K_MA_3"][0]})
        elif CONSTANT.TRIGGER_CAUSE_FAST_AND_SLOW_MA == self.trigger_cause:
            current_stoch_value_list.append({CONSTANT.TRIGGER_CAUSE_FAST_MA: k_df["K"][0]})
            current_stoch_value_list.append({CONSTANT.TRIGGER_CAUSE_SLOW_MA: k_df["K_MA_3"][0]})
        else:
            raise RuntimeError("Unrecognized trigger_cause={}".format(self.trigger_cause))
        response = {"__type__": self.__type__, "__subtype__": self.__subtype__}
        #return the values
        for dict in current_stoch_value_list:
            for ma_type, stoch_value in dict.items():
                #if nan return false
                if stoch_value != stoch_value or\
                not self.lower_bound <= stoch_value <= self.upper_bound:
                    response.update({"pass": False, "current_value": current_stoch_value_list})
                    return response
        #still within range
        response.update({"pass": True, "calculations": current_stoch_value_list})
        return response






