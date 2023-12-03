import numpy as np
from abc import ABC, abstractmethod

class Interpolator:
    def __init__(self, x_values, y_values):
        self.x = x_values
        self.y = y_values

    @abstractmethod
    def value(self,x_value):
        pass


