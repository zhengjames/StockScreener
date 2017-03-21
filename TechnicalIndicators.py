import numpy as np
import pandas as pd
class Macd:
    """Input should be data[0] is date and data[1] is price"""
    def __init__(self):
        self.slowEma = 26
        self.fastEma = 12
        self.macdEma = 9

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

    def calc_macd(self, data_frame, longer_window = 26, shorter_window = 12, macd_window = 9):
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




