"""This script contains math and stat functions for AQData classes."""

import logging
from pandas import date_range, Timedelta, DataFrame

def reindex_with_interpolation(data, freq):
    """Reindex pandas Series or DataFrame with interpolating to new indices.

    Parameters:
        data(Series|DataFrame): the data to be reindexed
        freq(str|DateOffset): the interpolation frequency to use

    Return:
        reindexed and interpolated data

    """
    desired_index = date_range(start=data.index[0].round(freq),
        end=data.index[-1].round(freq), freq=freq
    )

    return data.reindex(data.index.union(desired_index)).interpolate(
        method='time').reindex(desired_index)

def time_delay_correlation(a, b, dtmin, dtmax, freq, starttime=None, endtime=None):
    """Calculate the time delay correlation vector of two datetime indexed
    pandas Series or DataFrames between the given time period,
    with the given resolution.

    Parameters:
        a (Series): the first data vector to correlate. Should be pre-sorted
            by datetime index
        b (Series): the second data vector to correlate, this will be shifted
            in time relative to a. Should be pre-sorted by datetime index
        dtmin(str): the minimum (possibly negative) time delay to check
            (will be converted to pandas Timedelta)
        dtmax(str): the maximum time delay to check
            (will be converted to pandas Timedelta)
        freq(str): the time resolution of the time delay to check
            (will be converted to pandas Timedelta)
        starttime(datetime): the starting time of the subset of the data
            to check or None if the whole data should be used
        endtime(datetime): the ending time of the subset of the data
            to check or None if the whole data should be used

    Return:
        (Series): time delay correlation values indexed by the delay time
            of b shifted relative to a

    """
    dtmin = Timedelta(dtmin)
    dtmax = Timedelta(dtmax)
    freq = Timedelta(freq)
    starttime = starttime or max(a.index[0], b.index[0])
    endtime = endtime or min(a.index[-1], b.index[-1])
    # cut to [starttime, endtime] allowing enough slack for shifting operation
    aa = a[starttime - dtmin : endtime + dtmax]
    bb = b[starttime - dtmax : endtime + dtmin]
    # reindex with regular intervals using inner linear interpolation
    aa = reindex_with_interpolation(aa, freq)
    bb = reindex_with_interpolation(bb, freq)
    # calculate time delay correlations
    t = dtmin
    stat = DataFrame(columns=aa.columns)
    while t <= dtmax:
        stat.loc[t] = aa.corrwith(bb.shift(freq=t), method='pearson')
        t += freq

    return stat