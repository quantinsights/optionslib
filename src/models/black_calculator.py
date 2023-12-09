import numpy as np
from basics.DayCountBasis import Actual360, Actual365, ActualActual
from basics import Utils
from datetime import date
from product import EuropeanVanillaFxOption
from market.discounting_curve import DiscountingCurve
from basics.Enums import FxVanillaEuropeanOptionQuoteConvention, DeltaConvention
from scipy.stats import norm

# Standard Black formula for European vanilla calls/puts
class BlackCalculator:
    def __init__(
            self,
            valuationDate : date,
            europeanVanillaFxOption : EuropeanVanillaFxOption,
            fxSpot : float,
            foreignDiscountingCurve : DiscountingCurve,
            domesticDiscountingCurve : DiscountingCurve,
            sigma : float
    ):
        self.t = valuationDate
        self.europeanVanillaFxOption = europeanVanillaFxOption
        self.S_t = fxSpot
        self.foreignDiscountingCurve = foreignDiscountingCurve
        self.domesticDiscountingCurve = domesticDiscountingCurve
        self.tau = Actual365.year_fraction(self.t, self.T)
        self.sigma = sigma
        self.F = self.atTheMoneyForward()
        self.foreignDF = self.foreignDiscountingCurve.discountFactor(self.t,self.T)
        self.domesticDF = self.domesticDiscountingCurve.discountFactor(self.t,self.T)

    ## Returns the forward contract strike F(0,T)
    def atTheMoneyForward(self):
        fwdPoints = self.foreignDF / self.domesticDF
        F = fwdPoints * self.S_t
        return F

    def dPlus(self):
        return (np.log(self.F / self.K) + self.tau * (self.sigma ** 2) / 2) / (self.sigma * np.sqrt(self.tau))

    def dMinus(self):
        return (np.log(self.F / self.K) - self.tau * (self.sigma ** 2) / 2) / (self.sigma * np.sqrt(self.tau))

    def value(
            self,
            quoteConvention : FxVanillaEuropeanOptionQuoteConvention = FxVanillaEuropeanOptionQuoteConvention.DOMESTIC_PER_UNIT_OF_FOREIGN
    ):
        omega = self.europeanVanillaFxOption.optionType
        d_plus = self.dPlus()
        d_minus = self.dMinus()
        undiscountedPrice = omega * (self.F * norm.cdf(omega * d_plus) - self.K * norm.cdf(omega * d_minus))
        pv = self.domesticDF * undiscountedPrice
        signedPV = self.europeanVanillaFxOption.direction * pv

        if(quoteConvention == FxVanillaEuropeanOptionQuoteConvention.DOMESTIC_PER_UNIT_OF_FOREIGN):
            return signedPV * 100.0
        elif(quoteConvention == FxVanillaEuropeanOptionQuoteConvention.PERCENTAGE_DOMESTIC):
            return signedPV /self.S_t * 100.0
        elif(quoteConvention == FxVanillaEuropeanOptionQuoteConvention.PERCENTAGE_FOREIGN):
            return signedPV / self.K * 100.0
        else:
            return signedPV / (self.S_t * self.K) * 100

    def delta(
            self,
            deltaConvention : DeltaConvention = DeltaConvention.PIPS_SPOT_DELTA
    ):
        omega = self.europeanVanillaFxOption.optionType

        if(deltaConvention == DeltaConvention.PIPS_SPOT_DELTA):
            return omega * self.foreignDF * norm.cdf(omega * self.dPlus()) * 100.00
        elif(deltaConvention == DeltaConvention.PIPS_FORWARD_DELTA):
            return omega * norm.cdf(omega * self.dPlus()) * 100.0
        elif(deltaConvention == DeltaConvention.PREMIUM_ADJUSTED_DELTA):
            pips_spot_delta = omega * self.foreignDF * norm.cdf(omega * self.dPlus()) * 100.00
            return pips_spot_delta - self.value()/self.S_t

    def analyticGamma(self):
        omega = self.europeanVanillaFxOption.optionType
        return self.foreignDF * norm.cdf(omega * self.dPlus()) / (self.sigma * self.S_t * np.sqrt(Actual365.year_fraction(self.t, self.T)))

    def analyticTheta(self):
        omega = self.europeanVanillaFxOption.optionType
        Nd1 = norm.cdf(omega * self.dPlus())
        Nd2 = norm.cdf(omega * self.dMinus())
        r_FOR = Utils.df_to_rate(self.foreignDF, self.t, self.T)
        r_DOM = Utils.df_to_rate(self.domesticDF, self.t, self.T)
        theta = (omega * (self.S_t * r_FOR * self.foreignDF * Nd1 - self.K * r_DOM * self.domesticDF * Nd2)
                 - self.S_t * self.foreignDF * Nd1 * (self.sigma / (2 * np.sqrt(Actual365.year_fraction(self.t, self.T))))) * 100.0

        return theta

    def vega(self):
        return self.S_t * self.foreignDF * norm.pdf(self.dPlus()) * np.sqrt(Actual365.year_fraction(self.t, self.T))

    def vanna(self):
        return -self.foreignDF * norm.pdf(self.dPlus()) * (self.dMinus()/self.sigma)

    def volga(self):
        return self.S_t * self.foreignDF * np.sqrt(Actual365.year_fraction(self.t, self.T)) * \
            norm.pdf(self.dPlus()) * (self.dPlus() * self.dMinus())/self.sigma