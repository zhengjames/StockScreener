import numpy as np
import math as math
import pandas as pd
import queue as queue
import scipy.optimize as scopt
import matplotlib.pyplot as plt
from Utilities import AllConstants as CONSTANT
from Utilities import DataPrepUtil
import logging

INVALID_PREDICTION = 9999


class Calculator:
    def calc_simple_moving_average(self, values, window):
        weigths = np.repeat(1.0, window) / window
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
            values[len(values) - window:len(values)], window)[0])
        """given oct,sept,aug,jul,jun,may,apr we calculate from tail the oldest data to newest
            if window is three we calculate average jun,may,apr then next one will include jul...
            until reaches the head"""
        """calculate backward from tail to head new final values are inserted to position 0"""
        for i in reversed(range(0, len(values) - window)):
            """last element of the results"""
            most_recent_ema = result[0]
            result.insert(0, (values[i] - most_recent_ema) * (2 / (window + 1)) + most_recent_ema)

        return result


class Macd(Calculator):
    """Input should be data[0] is date and data[1] is price"""

    def __init__(self):
        Calculator.__init__(self)
        self.slowEma = 26
        self.fastEma = 12
        self.macdEma = 9

    # reference http://investexcel.net/how-to-calculate-macd-in-excel/
    def calculate(self, data_frame, longer_window=26, shorter_window=12, macd_window=9):
        values = data_frame['close']
        long_ema = self.calc_exponential_moving_average(values, longer_window)
        short_ema = self.calc_exponential_moving_average(values, shorter_window)

        """truncate to make same length for both ema"""
        diff_window = longer_window - shorter_window

        long_ema = np.array(long_ema)
        short_ema = np.array(short_ema)

        macd_ema = short_ema[:len(short_ema) - diff_window] - long_ema
        # signal is the exponential moving average of the macd
        signal_sma = np.array(self.calc_exponential_moving_average(macd_ema, macd_window))

        """add padding to make all same length"""
        padding = np.empty(len(values) - len(macd_ema)) * np.nan
        macd_ema = np.concatenate([macd_ema, padding])
        padding = np.empty(len(values) - len(signal_sma)) * np.nan
        signal_sma = np.concatenate([signal_sma, padding])
        padding = np.empty(len(values) - len(long_ema)) * np.nan
        long_ema = np.concatenate([long_ema, padding])
        padding = np.empty(len(values) - len(short_ema)) * np.nan
        short_ema = np.concatenate([short_ema, padding])
        center_line = macd_ema - signal_sma

        return pd.concat([
            pd.DataFrame({'date': data_frame['date']}),
            pd.DataFrame({'macd_ema': macd_ema}),
            pd.DataFrame({'signal_sma': signal_sma}),
            pd.DataFrame({'center_line': center_line}),
            pd.DataFrame({'short_ema': short_ema}),
            pd.DataFrame({'long_ema': long_ema})], axis=1)


class DataParser:
    # add a column that contains'start' and 'end' for every
    # consecutive positive or negative center signal index
    # dataframe of date, signal index 0 is most recent
    # returns a list of tuples[(start_index, end_index), ...]
    def parse_macd_signal_intersect(self, macd_df):

        macd_df['cross_over_indicator'] = np.NAN * len(macd_df)
        waveList = list()
        same_sign_num_count = 1
        i = 0
        # find first start
        while i < len(macd_df) and macd_df.center_line[i] == macd_df.center_line[i]:
            if ((macd_df.center_line[i] > 0 and macd_df.center_line[i + 1] < 0)
                or (macd_df.center_line[i] < 0 and macd_df.center_line[i + 1] > 0)
                or (math.isnan(macd_df.center_line[i + 1]))):
                    macd_df.loc[i, 'cross_over_indicator'] = 'start'
                    waveList.append((0, i))
                    i += 1
                    break
            i += 1

        while i < len(macd_df):

            if (macd_df.center_line[i] == 0):
                i += 1
                continue
            # current element sign differ from older element
            if ((macd_df.center_line[i] > 0 and macd_df.center_line[i + 1] < 0)
                or (macd_df.center_line[i] < 0 and macd_df.center_line[i + 1] > 0)
                or (macd_df.center_line[i + 1] != macd_df.center_line[i + 1])):
                # use this to ignore 1,-1,1,-1
                if same_sign_num_count > 1:
                    macd_df.loc[i, 'cross_over_indicator'] = 'start'
                    macd_df.loc[i - same_sign_num_count + 1, 'cross_over_indicator'] = 'end'
                    waveList.append((i, i - same_sign_num_count + 1))

                    # reset counter
                    same_sign_num_count = 1
            else:
                same_sign_num_count += 1

            i += 1
            # if it is at the end of the list where numbers start to be nan then break
            if np.isnan(macd_df.center_line[i]):
                break

        return waveList

    # parses out the most recent segment of zero intersection
    # for example -4,-3,-2,0,1,3,-5,-2,-1 will return [1,3,-5,-2,-1]
    def parse_most_recent_macd_signal_intersect(self, macd_df):
        for i in range(len(macd_df) - 1):
            if (macd_df.center_line[i] == 0):
                continue
            # sign different between current and next element
            if ((macd_df.center_line[i] > 0 and macd_df.center_line[i + 1] < 0)
                or (macd_df.center_line[i] < 0 and macd_df.center_line[i + 1] > 0)):
                return macd_df[:i + 1]


class StochasticOscillator(Calculator):
    # returns {[K][K_MA_3]}
    def calculate(self, data_frame, look_back_period=14, sma_period=3):
        '''
        :param data_frame: with column High and column Low
        :param look_back_period:
        :param sma_period:
        :return: two arrays

        Note: Stochastic Oscillator has two parts
        1. Stochastic calculation:
        2. Oscillation calculation: producing the set of oscillating arrays
        '''

        k_array = self.calc_stochastic_array(data_frame, look_back_period=look_back_period)
        # format the oscillating arrays
        k_array_sma = self.calc_simple_moving_average(k_array, 3)
        return pd.concat([pd.DataFrame({"K": k_array}), pd.DataFrame({"K_MA_3": k_array_sma})], axis=1)

    # applys the universal algorithm for basic stochastic
    def calc_stochastic_array(self, data_frame, look_back_period=14):
        '''

        :param data_frame: High, Low, Close
        :param look_back_period:
        :return: stochastic array
        '''
        # Algorithm: %K = (Current Close - Lowest Low)/(Highest High - Lowest Low) * 100
        k_array = np.empty(len(data_frame.index)) * np.nan

        index = len(data_frame) - look_back_period
        # calculate the stochastic point
        # iterate through data from last element(oldest) to most recent
        while (index >= 0):
            # 14 elements
            high_list = data_frame.high[index: index + look_back_period].tolist()
            low_list = data_frame.low[index: index + look_back_period].tolist()
            current_close = data_frame.close[index]
            high_list = np.sort(high_list)
            low_list = np.sort(low_list)
            highest_high = high_list[len(high_list) - 1]

            # np.nanmax finds max and ignore Nan from list
            highest_high = np.nanmax(high_list)
            lowest_low = np.nanmin(low_list)
            lowest_low = low_list[0]
            k = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
            k_array[index] = k
            index -= 1
        return k_array


# http://cns.bu.edu/~gsc/CN710/fincast/Technical%20_indicators/Relative%20Strength%20Index%20(RSI).htm
class Stochastic_RSI(StochasticOscillator):
    def calculate(self, data_frame, look_back_period=14, sma_period=3):
        # calculate rsi
        rsi_df = self.calculate_rsi(data_frame)
        # trim any nan from the tail

        # prepare data for standard stochastic calculation
        # High, Low, Close is exactly the same
        formatted_rsi_df = pd.DataFrame({'high': rsi_df['rsi'], 'low': rsi_df['rsi'], 'close': rsi_df['rsi']})
        stoch_rsi_arr = self.calc_stochastic_array(formatted_rsi_df, look_back_period=look_back_period)

        # format the rsi oscillation
        rsi_sma = self.calc_simple_moving_average(stoch_rsi_arr, 3)
        rsi_sma_sma = self.calc_simple_moving_average(rsi_sma, 3)

        return pd.concat([pd.DataFrame({"K": rsi_sma}), pd.DataFrame({"K_MA_3": rsi_sma_sma})], axis=1)

    def calculate_rsi(self, data_frame, look_back_period=14):
        closed_price = data_frame.close
        gain_loss_array = np.empty(len(data_frame)) * np.nan

        # cannot calculate gain or loss from the ipo date, first date therefore start with len()-1
        # index goes from back of array to front of array
        # if len is 5 (0,1,2,3,4) you want calculate (3,2,1,0) so 5 - 2
        for i in reversed(range(0, len(closed_price) - 1)):
            # today minus yesterday
            difference = closed_price[i] - closed_price[i + 1]
            gain_loss_array[i] = difference

        # queue max size 14
        gain_loss_queue = queue.Queue(look_back_period)
        total_gain = 0
        total_loss = 0

        # find the average for the first set
        # First Average Gain = Sum of Gains over the past 14 periods / 14.
        # if len of array is 5 (0,1,2,3,4) start with index 3
        for i in range(2, look_back_period + 2):
            value = gain_loss_array[len(gain_loss_array) - i]
            gain_loss_queue.put(value)
            if value > 0:
                total_gain += value
            elif value < 0:
                total_loss -= value

        output_len = len(data_frame) - look_back_period
        avg_gain_list = np.empty(output_len) * np.nan
        avg_loss_list = np.empty(output_len) * np.nan
        RS_list = np.empty(output_len) * np.nan
        RSI_list = np.empty(output_len) * np.nan
        # fill first set of values
        avg_gain_loss_index = len(data_frame) - look_back_period - 1
        avg_gain_list[avg_gain_loss_index] = total_gain / look_back_period
        avg_loss_list[avg_gain_loss_index] = abs(total_loss / look_back_period)
        RS_list[avg_gain_loss_index] = avg_gain_list[avg_gain_loss_index] / avg_loss_list[avg_gain_loss_index]
        RSI_list[avg_gain_loss_index] = 100 - (100 / (1 + RS_list[avg_gain_loss_index]))
        avg_gain_loss_index -= 1
        # --end first set calculation

        # find second and remaining average
        # Average Gain = [(previous Average Gain) x 13 + current Gain] / 14.
        # start filling array from the back
        while (avg_gain_loss_index >= 0):
            current_value = gain_loss_array[avg_gain_loss_index]
            current_gain = 0
            current_loss = 0
            if current_value > 0:
                current_gain = current_value
            elif current_value < 0:
                current_loss = current_value

            # recalculate average
            previous_avg_gain = avg_gain_list[avg_gain_loss_index + 1]
            previous_avg_loss = avg_loss_list[avg_gain_loss_index + 1]
            avg_gain_list[avg_gain_loss_index] = (previous_avg_gain * 13 + current_gain) / look_back_period
            avg_loss_list[avg_gain_loss_index] = (previous_avg_loss * 13 + abs(current_loss)) / look_back_period
            RS_list[avg_gain_loss_index] = avg_gain_list[avg_gain_loss_index] / avg_loss_list[avg_gain_loss_index]
            RSI_list[avg_gain_loss_index] = 100 - (100 / (1 + RS_list[avg_gain_loss_index]))
            avg_gain_loss_index -= 1

        return pd.concat([
            pd.DataFrame({'date': data_frame['date'][:output_len]}),
            pd.DataFrame({'avg_gain': avg_gain_list}),
            pd.DataFrame({'avg_loss': avg_loss_list}),
            pd.DataFrame({'rs': RS_list}),
            pd.DataFrame({'rsi': RSI_list})], axis=1);


class ForcastAlgorithms:
    """
        data_frame.x contains the macd difference
        data_frame.y contains the index 0,1,2,3..
    """

    def predict_cross_zero_macd(self, data_frame, trigger_direction):
        logging.info("Begin predict cross {} zero".format(trigger_direction))

        pattern_to_prepare = CONSTANT.ASCENDING if trigger_direction == CONSTANT.ABOVE else CONSTANT.DESCENDING

        x, y = DataPrepUtil.extract_most_recent_asc_desc_xy(
            data_frame, min_num_previous_data=CONSTANT.MIN_NUM_PREVIOUS_DATA, pattern=pattern_to_prepare)
        # if either x or y is empty
        if len(x) == 0 or len(y) == 0:
            return INVALID_PREDICTION
        # now x and y should have at least len of 2, min num data required to predict
        poly_coefficients = np.polyfit(x, y, 1)

        # store formula in calculator so we can just call it to predict
        calculator = np.poly1d(poly_coefficients)

        # number days until break above zero
        return abs(calculator(0) - y[0])

    # returns 0 if just crossed
    def predict_just_crossed_zero_macd(self, data_frame, direction="BOTH"):
        print("Begin predict just cross zero")
        if "BOTH" == direction:
            # yesterday and today's signs are different
            if data_frame.x[1] * data_frame.x[0] < 0:
                return 0
            else:
                return INVALID_PREDICTION
        elif "ABOVE" == direction:
            if data_frame.x[1] <= 0 and data_frame.x[0] >= 0:
                return 0
            else:
                return INVALID_PREDICTION
        # direction must be ABOVE
        else:
            if data_frame.x[1] >= 0 and data_frame.x[0] <= 0:
                return 0
            else:
                return INVALID_PREDICTION

    def linear_regression(self, x, y):
        poly_coefficients = np.polyfit(x, y, 1)
        # store formula in calculator so we can just call it to predict
        calculator = np.poly1d(poly_coefficients)
        testX = np.append(x, 0)

        plt.figure()
        plt.title("Linear Regression")
        plt.plot(x, y, 'ko', label="Original data")
        plt.plot(testX, calculator(testX), 'r-', label="Fitted Curve")
        plt.legend()
        plt.show()

    def exponential_regression(self, x, y):

        popt, pcov = scopt.curve_fit(self.expFunc, x, y)
        testX = np.append(x, 0)
        plt.figure()
        plt.title("Exponential Regression")
        plt.plot(x, y, 'ko', label="Original data")
        plt.plot(testX, self.expFunc(testX, *popt), 'r-', label="Fitted Curve")
        plt.legend()
        plt.show()

    def expFunc(self, x, a, b):
        return a * np.exp(b * x)
