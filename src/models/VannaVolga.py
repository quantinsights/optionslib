from typing import Dict, List
from datetime import date
from basics.DayCountBasis import Actual360, Actual365, ActualActual
import numpy as np
from market.EuropeanVanillaFxOptionQuote import EuropeanVanillaFxOptionQuote
from market.DiscountingCurve import DiscountingCurve
from basics.Enums import FxOptionsMarketQuoteType
from scipy.stats import norm

## An implementation of the Vanna-Volga method.
class VannaVolga:
    def __init__(
            self,
            fxOptionMarketQuotes : List[EuropeanVanillaFxOptionQuote],
            S_t : float,
            foreignCcyDiscountingCurve : DiscountingCurve,
            domesticCcyDiscountingCurve : DiscountingCurve
    ):
        self.fxOptionMarketQuotes = fxOptionMarketQuotes
        self.S_t = S_t
        self.foreignDiscountingCurve = foreignCcyDiscountingCurve
        self.domesticDiscountingCurve = domesticCcyDiscountingCurve

        self.valuationDate = fxOptionMarketQuotes[0].asOfDate \
            if len(fxOptionMarketQuotes) > 0 else date.today()

        self.rr = {}; self.stdl = {}; self.vwb = {}

        for i in range(len(fxOptionMarketQuotes)):
            if fxOptionMarketQuotes[i].quoteType == FxOptionsMarketQuoteType.ATM_STRADDLE:
                self.stdl[fxOptionMarketQuotes[i].expiryDate] = fxOptionMarketQuotes[i].vol
            elif fxOptionMarketQuotes[i].quoteType == FxOptionsMarketQuoteType.TWENTY_FIVE_DELTA_RISK_REVERSAL:
                self.rr[fxOptionMarketQuotes[i].expiryDate] = fxOptionMarketQuotes[i].vol
            elif fxOptionMarketQuotes[i].quoteType == FxOptionsMarketQuoteType.TWENTY_FIVE_DELTA_VEGA_WEIGHTED_BUTTERFLY:
                self.vwb[fxOptionMarketQuotes[i].expiryDate] = fxOptionMarketQuotes[i].vol

        self.expDates = np.array(self.stdl.keys())
        self.timeToExpiries = np.array([Actual365(self.valuationDate,expDate) for expDate in self.expDates])
        N = len(self.timeToExpiries)

        # Calculate the ATM, 25-Delta call and 25-Delta Put (pivot option) quotes
        sigmaATM = np.array(self.stdl.values())
        sigma25DRR = np.array(self.rr.values())
        sigma25DFly = np.array(self.vwb.values())

        self.sigmaATM = sigmaATM
        self.sigma25DCall = (sigma25DFly + sigmaATM) + 0.50 * sigma25DRR
        self.sigma25DPut = (sigma25DFly + sigmaATM) - 0.50 * sigma25DRR

        # Calculate the ATM, 25-Delta call and 25-Delta put strikes
        # for each expiry.
        self.F_T = np.array([self.forward(self.valuationDate,expDate) for expDate in self.expDates])
        self.KATM = self.F_T * np.exp((self.sigmaATM**2)/2 * self.timeToExpiries)
        self.compoundFactors = np.array([1/self.domesticDiscountingCurve.discountFactor(self.valuationDate,expDate)
                                for expDate in self.expDates])
        self.alpha = np.array([-norm.ppf(0.25*compoundFactor) for compoundFactor in self.compoundFactors])
        self.K25DCall = self.F_T * np.exp(
            self.alpha * self.sigma25DCall * np.sqrt(self.timeToExpiries) +
            0.50 * (self.sigma25DCall**2) * self.timeToExpiries
        )
        self.K25DPut = self.F_T * np.exp(
            -self.alpha * self.sigma25DPut * np.sqrt(self.timeToExpiries) +
            0.50 * (self.sigma25DPut**2) * self.timeToExpiries
        )

        self.dataByExpiry = {}
        for i in len(self.expDates):
            self.dataByExpiry[self.expDates[i]] = (
                self.timeToExpiries[i],
                self.sigmaATM[i],
                self.sigma25DCall[i],
                self.sigma25DPut[i],
                self.F_T[i],
                self.KATM[i],
                self.K25DCall[i],
                self.K25DPut[i]
            )

    def forward(self,t:date,T:date):
        foreignDF = self.foreignDiscountingCurve.discountFactor(t,T)
        domesticDF = self.domesticDiscountingCurve.discountFactor(t,T)
        fwdPoints = foreignDF / domesticDF
        F = fwdPoints * self.S_t
        return F

    def firstOrderApproximation(self, K:float, T:date):
        if T in self.dataByExpiry.keys():
            tau, sigma2, sigma3, sigma1, F_T, K2, K3, K1 = self.dataByExpiry[T]
            y1 = (np.log(K2/K) * np.log(K3/K))/(np.log(K3/K1) * np.log(K2/K1))
            y2 = (np.log(K/K1) * np.log(K3/K))/(np.log(K2/K1) * np.log(K3/K2))
            y3 = (np.log(K/K1) * np.log(K/K2))/(np.log(K3/K1) * np.log(K3/K2))
            return y1 * sigma1 + y2 * sigma2 + y3 * sigma3
        else:
            raise Exception(f"Market quotes for the expiry {date.strftime(T,'%Y-%m-%d')} "
                            f"were not supplied during VV calibration!")

    def secondOrderApproximation(self, K:float, T:date):
        if T in self.dataByExpiry.keys():
            tau, sigma2, sigma3, sigma1, F_T, K2, K3, K1 = self.dataByExpiry[T]
            xi1 = self.firstOrderApproximation(K,T)
            D1_K = xi1 - sigma2

            d_plus_K = self.dPlus(F_T,K,sigma2,tau)
            d_minus_K = self.dMinus(F_T,K,sigma2,tau)

            d_plus_K1 = self.dPlus(F_T,K1,sigma2,tau)
            d_minus_K1 = self.dMinus(F_T, K1, sigma2, tau)

            d_plus_K3 = self.dPlus(F_T, K3, sigma2, tau)
            d_minus_K3 = self.dMinus(F_T, K3, sigma2, tau)

            D2_K = ((d_plus_K1 * d_minus_K1 * (np.log(K3/K) * np.log(K2/K))/(np.log(K3/K1) * np.log(K2/K1)) *
                    (sigma1 - sigma2)**2 +
                    d_plus_K3 * d_minus_K3 * (np.log(K/K1) * np.log(K/K2))/(np.log(K3/K1) * np.log(K3/K2))) *
                    (sigma3 - sigma2)**2)

            return (sigma2 + (-sigma2 + np.sqrt(sigma2**2 - d_plus_K * d_minus_K * (2*sigma2*D1_K + D2_K)))/
                    (d_plus_K * d_minus_K))
        else:
            raise Exception(f"Market quotes for the expiry {date.strftime(T,'%Y-%m-%d')} "
                            f"were not supplied during VV calibration!")

    def dPlus(self, F, K, tau, sigma):
        return (np.log(F / K) + tau * (sigma ** 2) / 2) / (sigma * np.sqrt(tau))

    def dMinus(self, F, K, tau, sigma):
        return (np.log(F / K) - tau * (sigma ** 2) / 2) / (sigma * np.sqrt(tau))