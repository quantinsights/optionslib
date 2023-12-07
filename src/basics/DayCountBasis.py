from datetime import date
from src.basics import Utils

class DayCountBase:
    ## Returns the number of calendar days in the period [startInclusive,endExclusive).
    #
    # Refer here: https://en.wikipedia.org/wiki/Day_count_convention.
    @staticmethod
    def daysBetween(startInclusive : date, endExlusive : date):
        return (endExlusive - startInclusive).days

class Actual360(DayCountBase):
    @staticmethod
    def yearFraction(d1:date, d2:date):
        return DayCountBase.daysBetween(d1,d2)/360

class Actual365(DayCountBase):
    @staticmethod
    def yearFraction(d1:date, d2:date):
        return DayCountBase.daysBetween(d1,d2)/365


class ActualActual(DayCountBase):

    ## Returns the year fraction between [d1,d2) in the ACT/ACT day count convention.
    #
    # ACT/ACT assumes that a year consists of 365 or 366 days (in case of a leap year), and that the days
    # between dates s and t, s prior to t, are counted as the actual number of calendar days between the two
    # dates, including the first but not the second.
    #
    # If \f$s\f$ and \f$t\f$ are dates belonging to the same year and n is the actual number of days in the year, then the
    # year fraction equals \f$(t - s)/n\f$.
    #
    # If \f$s\f$ and \f$t\f$ are dates belonging to two different years, let \f$J_i\f$ be the first of January of the second year,
    # \f$J_f\f$ be the first of January of the final year, \f$n_i\f$ be the number of days in the first year, \f$n_f\f$ be the number
    # of days of the final year, and \f$y\f$ the number of years between the first and the final year, then the year
    # fraction equals
    # $$(J_i - s)/n_i + y + (t - J_f)/n_f$$
    @staticmethod
    def yearFraction(d1:date, d2:date):
        y1 = d1.year
        y2 = d2.year

        if y1 == y2:
            return (d2 - d1).days/Utils.lengthOfYear(y1)
        else:
            j_i = date(y1+1,1,1)
            j_f = date(y2,1,1)
            n_i = Utils.lengthOfYear(y1)
            n_f = Utils.lengthOfYear(y2)
            y = y2 - y1
            return (j_i - d1).days/n_i + y + (d2 - j_f).days/n_f

class Thirty360(DayCountBase):
    @staticmethod
    def yearFraction(d1:date, d2:date):
        startDate = d1
        endDate = d2

        if(d2.day == 31 and d1.day > 29):
            endDate = date(d2.year, d2.month,30)

        if(d1.day == 31):
            startDate = date(d1.year,d1.month,30)

        return (360 * (endDate.year - startDate.year) + 30 * (endDate.month - startDate.month) + (endDate.day - startDate.day))/360
