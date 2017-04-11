import TechnicalAlgorithms as ta
import numpy as np
import pandas as pd
class MacdScreener:
    #{"__type__": "MACD_SCREENER",
    #"trigger_cause": "FAST_SLOW_MA_CROSS",
    #"trigger_direction": "ABOVE", "BELOW", "BETWEEN"
    #"trigger_in_n_days":
    #}
    def __init__(self, json):
        self.__type__ = json["__type__"],
        self.trigger_cause = json["trigger_cause"]
        self.trigger_direction = json["trigger_direction"]
        self.trigger_in_n_days = json["trigger_in_n_days"]
        self.calculator = ta.Macd()
        self.data_parser = ta.DataParser()

    def screen(self, data):
        try:
            print("Begin calculating MACD")
            results = self.calculator.calculate(data_frame=data)
        except Exception as e:
            print("Does not have sufficient historical"
                  " data points to calculate MACD")
            raise e

        try:
            print("Begin parsing MACD")
            parsedResults = self.data_parser.parse_macd_signal_intersect(results[['date', 'center_line']])
        except RuntimeError as e:
            print("Error parsing MACD into intersecting segments: {}".format(e))
            raise e
        try:
            latestIndex = self.data_parser.parse_most_recent_macd_signal_intersect(results[['date', 'center_line']])
        except RuntimeError as e:
            print("Error parsing the most recent MACD segment from previous intersection: {}".format(e))
            raise e

        #create artificial dates 1,2,3,4,5...
        y_array = np.linspace(start=len(latestIndex), stop=1, num=len(latestIndex), dtype=int)
        data_frame = pd.concat([pd.DataFrame({'x': latestIndex.center_line}), pd.DataFrame({'y': y_array})], axis=1)
        forcaster = ta.ForcastAlgorithms()
        days = forcaster.predict_cross_above_zero_macd(data_frame)
        if ta.INVALID_PREDICTION or days > self.trigger_in_n_days:
            print("MACD fast MA breaching slow MA is not likely to happen or beyond filter setting")
        else:
            print("MACD fast MA will breach"
                  " slow MA in {} days".format(days))

        if days != ta.INVALID_PREDICTION:
            return [True, days]
        else:
            return [False, ta.INVALID_PREDICTION]

class StochasticScreener:
    #{
    # json_data["__type__"] = "STOCHASTIC_OSCILLATOR"
    # json_data["trigger_cause"] = "SLOW_MA"
    # json_data["trigger_direction"] = "BETWEEN"
    # json_data["upper_bound"] = 20
    # json_data["lower_bound"] = 0
    #}

    def __init__(self, json):
        self.__type__ = json["__type__"],
        self.trigger_cause = json["trigger_cause"]
        self.trigger_direction = json["trigger_direction"]
        self.upper_bound = json["upper_bound"]
        self.lower_bound = json["lower_bound"]
        self.calculator = ta.StochasticOscillator()
        self.data_parser = ta.DataParser()


    def screen(self, data):
        k_df = self.calculator.calculate(data)
        if self.lower_bound <= k_df.K_MA_3[0] <= self.upper_bound:
            return [True, k_df.K_MA_3[0]]
        else:
            return [False, ta.INVALID_PREDICTION]


