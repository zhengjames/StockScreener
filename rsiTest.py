from TechnicalAlgorithms import *
import pandas as pd

rsiCalculator = RSI()
input = [46.125, 47.125, 46.4375, 46.9375, 44.9375, 44.25, 44.625, 45.75, 47.8125, 47.56, 47.00, 44.5625, 46.3125, 47.6875, 46.6875, 45.6875, 43.0625, 43.5625, 44.875, 43.6875]
input = input[::-1]
date = np.empty(len(input))
df = pd.concat([pd.DataFrame({'Date': date}),
               pd.DataFrame({'Close' : input})], axis=1)
result = rsiCalculator.calculate(df)