
import numpy as np
import scipy.optimize as scopt
import matplotlib.pyplot as plt

def expFunc(x, a, b):
    return a*np.exp(b*x)

x = np.array([-0.323256, -0.453405, -0.532265, -0.570195, -0.699800, -0.850520, -1.005406])
y = np.array([13, 12, 11, 10,  9,  8,  7])
testX = np.append(x, 0)
popt, pcov = scopt.curve_fit(expFunc, x,y)
plt.figure()
plt.plot(x, y, 'ko', label="Original data")
plt.plot(testX, expFunc(testX, *popt), 'r-', label="Fitted Curve")
plt.legend()
plt.show()