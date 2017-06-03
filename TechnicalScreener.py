import TechnicalAlgorithms as ta
import numpy as np
import pandas as pd
from Utilities import AllConstants as CONSTANT
import logging

class ScreenerFactory:

    def create_screener(self, json):
        if "MACD" == json.get("__type__"):
            return self.create_macd(json)
        elif "STOCHASTIC_OSCILLATOR" == json.get("__type__"):
            return self.create_stochastic_oscillator(json)


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

    def create_stochastic_oscillator(self, json):
        '''
        :param json:
         {
            "__type__": "STOCHASTIC_OSCILLATOR_RSI",
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

        oscillator = StochasticScreener()
        oscillator.__type__ = json.get("__type__"),
        oscillator.trigger_cause = json.get("trigger_cause")
        #plain old oscillator no prediction
        if oscillator.trigger_direction == CONSTANT.BETWEEN:
            oscillator.upper_bound = json.get("upper_bound")
            oscillator.lower_bound = json.get("lower_bound")
        else:
            oscillator.trigger_direction = json.get("trigger_direction")
            oscillator.trigger_in_n_days = json("trigger_in_n_days")
            oscillator.trigger_target = json("trigger_target")

        #insert the type of calculator
        oscillator.__subtype__ = json.get("__subtype__")
        if "RSI" == self.__subtype__:
            self.calculator = ta.RSI()
        else:
            self.calculator = ta.StochasticOscillator()



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
        print("Begin {}".format(self.__type__))
        k_df = self.calculator.calculate(data)

        currentValue = k_df.K_MA_3[0]
        #check if it is nan
        currentValue = 'nan' if currentValue != currentValue else currentValue

        if self.lower_bound <= k_df.K_MA_3[0] <= self.upper_bound:
            logging.info("StochasticScreener meets required condition")
            return {"pass": True, "current_value": currentValue}
        else:
            logging.info("StochasticScreener fails to meet required condition")
            return {"pass":False, "current_value":currentValue}
