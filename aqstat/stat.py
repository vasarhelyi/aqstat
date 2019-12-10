"""Statistical functions related to the analysis of AQ data."""

from datetime import datetime, timedelta
import numpy as np
import numpy.ma as ma

from .aqdata import AQData

def daily_average(data):
    """Calculate a daily average of air quality data.

    Parameters:
        data (AQData): the data to average

    Return:
        AQData object containing daily averages of variables.

    """
    days = np.array([(x - datetime(1970, 1, 1)).days for x in data.time])
    daydata = AQData()
    for d in set(days):
        d = int(d)
        where = np.where(days == d)
        daydata = daydata.merge(AQData(
            time=[datetime(1970, 1, 1) + timedelta(days=d)],
            pm10=[ma.mean(ma.masked_invalid(data.pm10)[where])],
            pm2_5=[ma.mean(ma.masked_invalid(data.pm2_5)[where])],
            temperature=[ma.mean(ma.masked_invalid(data.temperature)[where])],
            humidity=[ma.mean(ma.masked_invalid(data.humidity)[where])]
        ))
    return daydata


def pearson(a, b):
    """Return the Pearson correlation coefficient of two lists.

    Parameters:
        a (list): the first list to be correlated
        a (list): the second list to be correlated

    Returns:
        Pearson correlation coefficient of the two lists.

    Note that this version is 'nan' and 'inf' safe.

    """
    return ma.corrcoef(ma.masked_invalid(a), ma.masked_invalid(b))[0][1]

