from datetime import date

class FxVolatilitySurfacePoint:
    def __init__(self, strike : float, maturity : date, vol : float):
        self.K = strike
        self.T = maturity
        self.sigma = vol
