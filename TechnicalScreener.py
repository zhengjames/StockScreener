import TechnicalAlgorithms as ta
import numpy as np
import pandas as pd

class ScreenerFactory:

    def create_screener(self, json):
        if "MACD" == json["__type__"]:
            return self.create_macd(json)
        elif "STOCHASTIC" in json["__type__"]:
            return self.create_stochastic_oscillator(json)
        else:
            return

    def create_macd(self, json):
        return MacdScreener(json)
    def create_stochastic_oscillator(self, json):
        return StochasticScreener(json)

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

    def extract_most_recent_segment(self, data_frame):
        i = 0
        while i < len(data_frame):
            if data_frame.cross_over_indicator[i] == 'start':
                return data_frame[0:i+1]
            i += 1
        return []

    def screen(self, data):
        try:
            print("Begin MACD")
            result_df = self.calculator.calculate(data_frame=data)
        except Exception as e:
            print("Does not have sufficient historical"
                  " data points to calculate MACD")
            raise e

        try:
            print("Begin parsing MACD")
            segment_tuple_list = self.data_parser.parse_macd_signal_intersect(result_df)
            most_recent_segment_df = self.extract_most_recent_segment(data_frame = result_df)
        except RuntimeError as e:
            print("Error parsing MACD into intersecting segments: {}".format(e))
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

        if "ABOVE" == self.trigger_direction:
            days = forcaster.predict_cross_above_zero_macd(data_frame)
        else:
            days = forcaster.predict_cross_below_zero_macd(data_frame)

        if days == ta.INVALID_PREDICTION or days > self.trigger_in_n_days:
            print("MACD fast MA breaching slow MA is not likely to happen")
        else:
            print("MACD fast MA will breach"
                  " slow MA in {} days".format(days))

        if days != ta.INVALID_PREDICTION:
            return {"pass":True, "prediction":days}
        else:
            return {"pass":False, "prediction":ta.INVALID_PREDICTION}

class StochasticScreener:
    #{
    # json_data["__type__"] = "STOCHASTIC_OSCILLATOR"
    # json_data["trigger_cause"] = "SLOW_MA"
    # json_data["trigger_direction"] = "BETWEEN"
    # json_data["upper_bound"] = 20
    # json_data["lower_bound"] = 0
    #}

    def __init__(self, json):
        self.__type__ = json["__type__"]
        self.trigger_cause = json["trigger_cause"]
        self.trigger_direction = json["trigger_direction"]
        self.upper_bound = json["upper_bound"]
        self.lower_bound = json["lower_bound"]
        if self.__type__ == "STOCHASTIC_OSCILLATOR":
            self.calculator = ta.StochasticOscillator()
        elif self.__type__ == "STOCHASTIC_OSCILLATOR_RSI":
            self.calculator = ta.RSI()
        self.data_parser = ta.DataParser()


    def screen(self, data):
        print("Begin Stochastic Oscillator")
        k_df = self.calculator.calculate(data)

        currentValue = k_df.K_MA_3[0]
        #check if it is nan
        currentValue = 'nan' if currentValue != currentValue else currentValue

        if self.lower_bound <= k_df.K_MA_3[0] <= self.upper_bound:
            print("meets required condition")
            return {"pass": True, "current_value": currentValue}
        else:
            print("fails to meet required condition")
            return {"pass":False, "current_value":currentValue}
