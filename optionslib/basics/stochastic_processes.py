"""
Module to support stochastic processes.
"""
import numpy as np
from typing import Callable, Union
from abc import ABC, abstractmethod

NumericType = Union[int, float, np.number]


class StochasticProcess1d(ABC):
    """Abstract base class for 1-D stochastic processes

    :param float drift: the local drift of the process
    :param float volatility: the local volatility of the process
    :param float T: the right hand endpoint of the time interval :math:`[0,t]`
    :param float x0: initial values
    """
    def __init__(self,
                 drift,
                 vol,
                 x0,
                 T=1.0,
                 timesteps_per_year=1000):
        self._drift = drift
        self._volatility = vol
        self._x0 = x0
        self._T = T
        self._timesteps_per_year = timesteps_per_year

        self._num_steps = self._timesteps_per_year * self._T
        self._dt = 1 / self._timesteps_per_year

    @abstractmethod
    def generate_path(self):
        """
        Generate a sample path.
        """
        pass

    def times(self):
        return np.linspace(0,self._T,self._num_steps+1)

    def generate_paths(self,n=10):
        """
        Generate n realizations of BM.
        """
        return [self.generate_path() for i in range(n)]

class BrownianMotion(StochasticProcess1d):
    """
    A standard brownian motion has independent and identically distributed Gaussian increments
    X(t) - X(s) = N(0,t-s).
    """
    def generate_path(self):
        """
        Generate 1 realization of brownian motion.
        dX_t = mu dt + sigma dW_t
        """
        z = np.random.standard_normal((1,self._num_steps))
        dx_t = self._drift * self._dt + self._volatility * np.sqrt(self._dt) * z
        x_t = np.cumsum(dx_t)
        x_t = np.insert(x_t,[0],0)
        return x_t

class OrnsteinUhlenbeckProcess(StochasticProcess1d):
    """
    An OU process.
    """
    def generate_path(self):
        """
        Generate a realization of ornstein uhlenbeck process.
        dY_t = - Y(t)dt + dW_t
        """
        z = np.random.standard_normal((1,self.num_steps))
        x_t = self.x_0
        y_t = np.array([x_t])
        for t in range(self.num_steps):
            dx_t = -x_t * self.dt + np.sqrt(self.dt) * z[t]
            x_t += dx_t
            np.append(y_t,x_t)

        y_t = np.insert(y_t,[0],0)
        return y_t

