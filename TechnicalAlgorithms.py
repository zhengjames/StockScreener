import numpy as np
import pandas as pd
from TechnicalScreener import *

INVALID_PREDICTION = 9999

class ScreenerFactory:

    def create_screener(self, json):
        if "MACD" == json["__type__"]:
            return self.create_macd(json)
        elif "STOCHASTIC_OSCILLATOR" == json["__type__"]:
            return self.create_stochastic_oscillator(json)
        else:
            return

    def create_macd(self, json):
        return MacdScreener(json)
    def create_stochastic_oscillator(self, json):
        return StochasticScreener(json)





class Calculator:

    def calc_simple_moving_average(self, values, window):
        weigths = np.repeat(1.0, window)/window
        simple_moving_average = np.convolve(values, weigths, 'valid')
        return simple_moving_average

    def calc_exponential_moving_average(self, values, window):
        """when index is window - 1 which is the
            beginning of the serie we have to use simple moving average
            value[window-1] is the first value"""
        descending_index = 0
        result = list()

        final_result_size = len(values) - window + 1
        # calculate from the tail to the head
        result.insert(0, self.calc_simple_moving_average(
            values[len(values) - window :len(values)], window)[0])
        """given oct,sept,aug,jul,jun,may,apr we calculate from tail the oldest data to newest
            if window is three we calculate average jun,may,apr then next one will include jul...
            until reaches the head"""
        """calculate backward from tail to head new final values are inserted to position 0"""
        for i in reversed(range(0, len(values) - window)):
            """last element of the results"""
            most_recent_ema = result[0]
            result.insert(0, (values[i] - most_recent_ema) * (2/(window + 1))+ most_recent_ema)

        return result



class Macd(Calculator):

    """Input should be data[0] is date and data[1] is price"""
    def __init__(self):
        Calculator.__init__(self)
        self.slowEma = 26
        self.fastEma = 12
        self.macdEma = 9

    def calculate(self, data_frame, longer_window = 26, shorter_window = 12, macd_window = 9):
        values = data_frame['Close']
        long_ema = self.calc_exponential_moving_average(values, longer_window)
        short_ema = self.calc_exponential_moving_average(values, shorter_window)

        """truncate to make same length for both ema"""
        diff_window = longer_window - shorter_window

        long_ema = np.array(long_ema)
        short_ema = np.array(short_ema)

        macd_ema = short_ema[:len(short_ema)-diff_window] - long_ema
        signal_sma = np.array(self.calc_simple_moving_average(macd_ema, macd_window))

        """add padding to make all same length"""
        padding = np.empty(len(values) - len(macd_ema)) * np.nan
        macd_ema = np.concatenate([macd_ema, padding])
        padding = np.empty(len(values) - len(signal_sma)) * np.nan
        signal_sma = np.concatenate([signal_sma, padding])
        padding = np.empty(len(values) - len(long_ema)) * np.nan
        long_ema = np.concatenate([long_ema,padding])
        padding = np.empty(len(values) - len(short_ema)) * np.nan
        short_ema = np.concatenate([short_ema,padding])
        center_line = macd_ema - signal_sma

        return pd.concat([
            pd.DataFrame({'date': data_frame['Date']}),
            pd.DataFrame({'macd_ema': macd_ema}),
            pd.DataFrame({'signal_sma':signal_sma}),
            pd.DataFrame({'center_line':center_line}),
            pd.DataFrame({'short_ema':short_ema}),
            pd.DataFrame({'long_ema':long_ema})], axis=1)


class DataParser:
    #parses out the most many segment of zero intersection
    #for example 0,-4,-3,-2,0,1,3,-5,-2,-1 will return [[0,-4,-3,-2], [0,1,3,-5,-2,-1]]
    #dataframe of date, signal index 0 is most recent
    def parse_macd_signal_intersect(self, macd_df):
        end = 0

        waveList = list()
        for i in range(len(macd_df) - 1):
            if(macd_df.center_line[i] == 0):
                continue
            #sign different between current and next element
            if((macd_df.center_line[i] > 0 and macd_df.center_line[i+1] < 0)
               or (macd_df.center_line[i] < 0 and macd_df.center_line[i+1] > 0)):
                waveList.append(macd_df[end:i+1])
                end = i + 1

        return waveList

    #parses out the most recent segment of zero intersection
    #for example -4,-3,-2,0,1,3,-5,-2,-1 will return [1,3,-5,-2,-1]
    def parse_most_recent_macd_signal_intersect(self, macd_df):
        for i in range(len(macd_df) - 1):
            if(macd_df.center_line[i] == 0):
                continue
            #sign different between current and next element
            if((macd_df.center_line[i] > 0 and macd_df.center_line[i+1] < 0)
               or (macd_df.center_line[i] < 0 and macd_df.center_line[i+1] > 0)):
                return macd_df[:i+1]


class StochasticOscillator(Calculator):
    #returns {[K][K_MA_3]}
    def calculate(self, data_frame, look_back_period = 14, sma_period = 3):
        k_array = np.empty(len(data_frame.index)) * np.nan

        index = len(data_frame) - look_back_period
        #calculate the stochastic point
        #iterate through data from last element(oldest) to most recent
        while (index >= 0):
            #14 elements
            high_list = data_frame.High[index : index + look_back_period].tolist()
            low_list = data_frame.Low[index : index + look_back_period].tolist()
            current_close = data_frame.Close[index]
            high_list = np.sort(high_list)
            low_list = np.sort(low_list)
            highest_high = high_list[len(high_list) - 1]
            lowest_low = low_list[0]
            k = ((current_close - lowest_low)/(highest_high - lowest_low)) * 100
            k_array[index] = k
            index -= 1

        k_array_sma = self.calc_simple_moving_average(k_array, 3)
        return pd.concat([pd.DataFrame({"K":k_array}), pd.DataFrame({"K_MA_3":k_array_sma})], axis=1)

class ForcastAlgorithms:

    #assumes both are negative values
    def a_closer_to_zero_than_b(self, a, b):
        return a > b

    """
        data_frame.x contains the macd difference
        data_frame.y contains the index 0,1,2,3..

    """
    def predict_cross_above_zero_macd(self, data_frame, num_previous_data = 2):
        print("Begin predict cross above zero")
        #we are checking for breaking above zero so most recent data should be negative
        #if positive it already break above zero
        if data_frame.x[0] > 0:
            return INVALID_PREDICTION
        elif data_frame.x[0] == 0:
            return 0

        #predict using the last 2 points by default

        if num_previous_data < 2:
            num_previous_data = 2

        x = data_frame.x[:num_previous_data]
        y = data_frame.y[:num_previous_data]

        # find longest descending value that is equal or fewer than num_previous_data
        # this ensures a proper fit for 1 degree linear fit
        for i in range(1, num_previous_data):
            #breaks descending order
            recent_point = data_frame.x[i - 1]
            old_point = data_frame.x[i]

            #both should be negative
            if recent_point >= 0 or old_point >= 0:
                return INVALID_PREDICTION
            #more recent points should be reaching toward 0
            if not self.a_closer_to_zero_than_b(recent_point, old_point):
                if i == 1:
                    return INVALID_PREDICTION
                #this is the cutoff segment used for fitting
                x = data_frame.x[:i]
                y = data_frame.y[:i]


        # now x and y should have at least len of 2, min num data required to predict
        poly_coefficients = np.polyfit(x, y, 1)
        #store formula in calculator so we can just call it to predict
        calculator = np.poly1d(poly_coefficients)

        #number days until break above zero
        return abs(calculator(0) - y[0])


    def predict_cross_below_zero_macd(self, data_frame, num_previous_data = 2):
        print("Begin predict cross below zero")
        #we are checking for breaking below zero so most recent data should be positive
        #if negative it already break below zero
        if data_frame.x[0] < 0:
            return INVALID_PREDICTION
        elif data_frame.x[0] == 0:
            return 0

        #predict using the last 2 points by default

        if num_previous_data < 2:
            num_previous_data = 2

        x = data_frame.x[:num_previous_data]
        y = data_frame.y[:num_previous_data]

        # find longest descending value that is equal or fewer than num_previous_data
        # this ensures a proper fit for 1 degree linear fit
        for i in range(1, num_previous_data):
            #breaks descending order
            recent_point = data_frame.x[i - 1]
            old_point = data_frame.x[i]

            #both should be negative
            if recent_point <= 0 or old_point <= 0:
                return INVALID_PREDICTION
            #more recent points should be reaching toward 0
            if not self.a_closer_to_zero_than_b(recent_point, old_point):
                if i == 1:
                    return INVALID_PREDICTION
                #this is the cutoff segment used for fitting
                x = data_frame.x[:i]
                y = data_frame.y[:i]


        # now x and y should have at least len of 2, min num data required to predict
        poly_coefficients = np.polyfit(x, y, 1)
        #store formula in calculator so we can just call it to predict
        calculator = np.poly1d(poly_coefficients)

        #number days until break above zero
        return abs(calculator(0) - y[0])
    #returns 0 if just crossed
    def predict_just_crossed_zero_macd(self, data_frame, direction="BOTH"):
        print("Begin predict just cross zero")
        if "BOTH" == direction:
            #yesterday and today's signs are different
            if data_frame.x[1] * data_frame.x[0] < 0:
                return 0
            else:
                return INVALID_PREDICTION
        elif "ABOVE" == direction:
            if data_frame.x[1] <= 0 and data_frame.x[0] >= 0:
                return 0
            else:
                return INVALID_PREDICTION
        #direction must be ABOVE
        else:
            if data_frame.x[1] >= 0 and data_frame.x[0] <= 0:
                return 0
            else:
                return INVALID_PREDICTION







