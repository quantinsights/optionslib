import numpy as np
from algorithms import Interpolator

class LinearInterpolator:
    def __init__(self, x_values, y_values):
        self.x = x_values
        self.y = y_values

    def value(self, x_0):
        n = len(self.x)
        i = 0

        for i in range(n - 1):
            if (self.x[i] <= x_0) and (x_0 < self.x[i + 1]):
                break

        return (x_0 - self.x[i]) / (self.x[i + 1] - self.x[i]) * self.y[i + 1] + (self.x[i + 1] - x_0) / (self.x[i + 1] - self.x[i]) * self.y[i]
