"""Statistical functions related to the analysis of AQ data."""

from pandas import merge_asof

from .aqdata import AQData


def get_overlapping_data(a, b, max_dt=120):
    """Return the subsets of a and b where both of them have valid data.

    Parameters:
        a (AQData): the first AQ dataset to interleave
        b (AQData): the second AQ dataset to interleave
        max_dt (float): the max time difference we allow while interleaving [s]

    Return:
        overlapping subsets of a and b with same length

    """
    pandas.merge_asof(a.data, b.data,

    ia = 0
    ib = 0
    na = len(a.time)
    nb = len(b.time)
    newa = AQData()
    newb = AQData()
    while ia < len(a.time) and ib < len(b.time):
        if a.time[ia] < b.time[ib]:
            # forward a until it reaches b
            while ia < na and b.time[ib] > a.time[ia] + timedelta(seconds=max_dt):
                ia += 1
            if ia == na:
                break
        else:
            # forward b until it reaches a
            while ib < nb and a.time[ia] > b.time[ib] + timedelta(seconds=max_dt):
                ib += 1
            if ib == nb:
                break
        # TODO: this is awful complicated like this, I just want to append a row...
        newa = newa.merge(AQData(time=[a.time[ia]],
            temperature=[a.temperature[ia]], humidity=[a.humidity[ia]],
            pm10=[a.pm10[ia]], pm2_5=[a.pm2_5[ia]])
        )
        newb = newb.merge(AQData(time=[b.time[ib]],
            temperature=[b.temperature[ib]], humidity=[b.humidity[ib]],
            pm10=[b.pm10[ib]], pm2_5=[b.pm2_5[ib]])
        )
        # go to next one
        ia += 1
        ib += 1

    return newa, newb