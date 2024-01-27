# Discounting Curve

The `DiscountingCurve` object stores a vector of dates and discount factors.
There is a need to value all instruments consistently within a single valuation
framework. For this we need a risk-free discounting curve which will be a continuous
curve (because this is the standard format for all option pricing formulae).

We establish a few important results.

*Definition* (Risk-free asset). Consider an asset with the price process \f$(B_t:t \in [0,T])\f$
which has the dynamics:

$$dB(t) = r(t)B(t)dt$$

where \f$r(t)\f$ is any adapted process. \f$B_t\f$ has no driving Wiener process (\f$dW_t\f$ term).
Such an asset is said to be a risk-free asset. This corresponds to a bank account with (possibly stochastic
short interest rate \f$r(t)\f$. Note, that the bank-account is *locally risk-free*, in the sense that,
even if the short rate is a random process, the return \f$r(t)\f$ over an infinitesimal time-period
\f$dt\f$ is risk-free (that is deterministic, given the information available at time \f$t\f$). However,
the return of \f$B\f$ over a longer time period is typically stochastic.

Using ODE cookbook methods, we can solve the above equation using separation of variables:
$$B(t) = B(0) e^{\int_{0}^{t} r(s) ds}$$

Definition. (Discounting process). The discounting process is defined as \f$D(t)=\frac{1}{B(t)}\f$. It is
easy to see that the dynamics of \f$D(t)\f$ is:
$$D(t) = -r(t)D(t)dt$$

with solution
$$D(0) = D(t)e^{-\int_{0}^{t} r(s) ds}$$

Definition. (Stochastic Discount Factor). The (stochastic) discount factor between two time instants
\f$t\f$ and \f$T\f$ is the amount at time \f$t\f$ equal to one unit of currency payable at time \f$T\f$
and is given by:
$$D(t,T) = \frac{B(t)}{B(T)} = e^{-\int_{t}^{T} r(s) ds}$$

*Definition* (Zero coupon bond). A \f$T\f$ maturity zero-coupon bond is a contract that guarantees its holder
the payment of one unit of currency at time \f$T\f$, with no intermediate payments. The contract value at time
\f$t < T\f$ is denoted by \f$P(t,T)\f$. Clearly, \f$P(T,T) = 1\f$ for all \f$T\f$.

By the risk neutral pricing formula, the price \f$P(t,T)\f$ of this claim at time \f$t\f$ is given by:

$$\frac{P(t,T)}{B(t)} = \mathbb{E}^{\mathbb{Q}}\left[\frac{1}{B(T)}|\mathcal{F}_t\right]$$

In other words,
 $$P(t,T) = \mathbb{E}^{\mathbb{Q}}\left[\frac{B(t)}{B(T)}|\mathcal{F}_t\right]= \mathbb{E}^{\mathbb{Q}}\left[D(t,T)|\mathcal{F}_t\right]$$

What is the relationship between the stochastic discount factor \f$D(t,T)\f$ and the zero-coupon bond price \f$P(t,T)\f$
for each pair \f$(t,T)\f$? If the rates \f$r\f$ are deterministic, then \f$D\f$ is deterministic as well and
\f$D(t,T) = P(t,T)\f$. However, if the rates are stochastic, \f$D(t,T)\f$ is a random quantity at time \f$t\f$
depending on the future evolution of the rates \f$r\f$ between \f$t\f$ and \f$T\f$.

*Remark.* It is common to refer to the ZCB price \f$P(t,T)\f$ as just the discount factor.

*Definition* (Continuously compounded spot interest rate). The continuously compounded spot interest rate prevailing
at time \f$t\f$ for the maturity \f$T\f$ is denoted by \f$R(t,T)\f$ and is the constant rate at which an investment
of \f$P(t,T)\f$ units of currency at time \f$t\f$ accrues continuous to yield a unit amount of currency at
maturity \f$T\f$. In formulas:
$$ P(t,T)\exp{(R(t,T)\tau(t,T))} = 1$$

or
$$ R(t,T) = -\frac{\ln P(t,T)}{\tau(t,T)}$$

*Definition* (Annually compounded spot interest rate). The annually compounded spot interest rate prevailing at
time \f$t\f$ for the maturity \f$T\f$ is denoted by \f$Y(t,T)\f$ and is the constant rate at which
investment has to be made to produce an amount of one unit of currency at maturity starting from
\f$P(t,T)\f$ units of currency at time \f$t\f$, when reinvesting the obtained amounts once a year. In formulas,
$$P(t,T)[1 + Y(t,T)]^{\tau(t,T)} = 1$$

Solving for \f$Y(t,T)\f$, we have:

$$Y(t,T) := \frac{1}{[P(t,T)]^{\frac{1}{\tau(t,T)}}} - 1$$

Thus, zero-coupon bond prices can be expressed in terms of annually compounded rates as:

$$P(t,T) = \frac{1}{[1+Y(t,T)]^{\tau(t,T)}}$$

*Definition* (Simply-compounded spot interest rate). The simply compounded spot interest rate prevailing at
time \f$t\f$ for maturity \f$T\f$ is denoted by \f$L(t,T)\f$ and is the constant rate at which
an investment has to be made to produce one unit of currency at maturity, starting from \f$P(t,T)\f$
units of currency at time \f$t\f$, when accruing occurs proportionally to the investment time.
In formulas:
$$P(t,T)[1 + L(t,T) \times \tau(t,T)]=1$$

Solving for \f$L(t,T)\f$, we have:
$$L(t,T) := \frac{1 - P(t,T)}{\tau(t,T)P(t,T)}$$

Reference : http://www.deriscope.com/docs/Hagan_West_curves_AMF.pdf
