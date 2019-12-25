"""This script contains plotting functions for AQData classes."""

import logging
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from numpy.ma import masked_where
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


# global parameters
markersize=3
humidity_threshold = 70
# PM health limits from these sources:
# http://emiktf.hu/olm.html
# http://www.levegominoseg.hu/hatarertek
pm_limits = {
    "PM2.5 yearly limit": (25, "coral"),
    "PM10 daily health limit": (50, "red"),
    "PM10 daily notification limit": (75, "darkred"),
    "PM10 daily emergency limit": (100, "black"),
}

def highlight(x, condition, ax):
    """Highlight plot at the given indices.

    Parameters:
        x (pandas Series): the list of x values
        condition (pandas Series): list of bools whether to highlight or not
        ax: the matplotlib figure axes to draw onto.

    """
    start = 0
    stop = 0
    n = len(x)
    while start < n and stop < n:
        while start < n and not condition[start]:
            start += 1
        if start >= n:
            break
        stop = start
        while stop < len(x) and condition[stop]:
            stop += 1
        if stop >= n:
            stop -= 1
        ax.axvspan(x[start], x[stop], facecolor='black',
            edgecolor='none', alpha=0.2
        )
        start = stop + 1

def plot_daily_variation(sensor, keys):
    """Plot daily variation of data accumulated through several days.

    Parameters:
        sensor (AQData): the sensor containing the dataset to plot
        keys (list[str]): the list of keys of the data Series we need to plot
    """

    for i, key in enumerate(keys):
        daily_average = sensor.data[key].groupby(sensor.data.index.day).transform("mean")
        total_average = sensor.data[key].mean()
        data1 = (sensor.data[key] - total_average).groupby(sensor.data.index.hour).agg(["mean", "std"])
        data2 = (sensor.data[key] - daily_average).groupby(sensor.data.index.hour).agg(["mean", "std"])
        plt.errorbar(x=data1.index + i * 0.1, y=data1["mean"], yerr=data1["std"], label="{} - avg({:.1f})".format(key, total_average))
        plt.errorbar(x=data2.index + i * 0.1, y=data2["mean"], yerr=data2["std"], label="{} - daily_avg".format(key))
    plt.xlabel("hours of day")
    plt.ylabel("daily variation")
    plt.legend()
    plt.show()

def plot_humidity(sensor):
    """Plot time series of humidity data.

    Parameters:
        sensor (AQData): the sensor containing the dataset to plot

    """
    # plot time series
    sensor.data.plot(y="humidity", label="humidity (avg={:.1f})".format(
        sensor.data.humidity.mean())
    )
    # add min label
    minvalue = sensor.data.humidity.min()
    idxmin = sensor.data.humidity.idxmin()
    plt.text(idxmin, minvalue, "{:.1f} %".format(minvalue),
        ha="center", va="top"
    )
    # add max label
    maxvalue = sensor.data.humidity.max()
    idxmax = sensor.data.humidity.idxmax()
    plt.text(idxmax, maxvalue, "{:.1f} %".format(maxvalue),
        ha="center", va="bottom"
    )
    # setup additional stuff
    plt.ylabel("humidity (%)")
    plt.grid(axis='y')
    plt.title("Sensor ID: {}".format(sensor.sensor_id))
    plt.show()

def plot_multiple_humidity(sensors):
    """Plot time series of humidity data from multiple sensors.

    Parameters:
        sensors (list(AQData)): the sensors containing the dataset to plot

    """
    ax = plt.figure().gca()
    for sensor in sensors:
        sensor.data.plot(y="humidity", label="{} humidity".format(sensor.sensor_id), ax=ax)
        plt.ylabel("humidity (%)")
    plt.plot(plt.xlim(), [humidity_threshold, humidity_threshold], 'r--', label="PM sensor validity limit")
    plt.ylim([0, 100])
    plt.yticks([0, humidity_threshold, 100])
    plt.grid(axis='y')
    plt.legend()
    plt.show()

def plot_multiple_pm(sensors, pm10=True, pm2_5=True):
    """Plot time series of PM10 + PM2.5 data from multiple sensors.

    Parameters:
        sensors (list(AQData)): the sensors containing the dataset to plot
        pm10 (bool): should we plot pm10 data?
        pm2_5 (bool): should we plot pm2_5 data?

    """
    ax = plt.figure().gca()
    for sensor in sensors:
        if pm10:
            sensor.data.plot(y="pm10", label="{} PM10".format(sensor.sensor_id), ax=ax)
        if pm2_5:
            sensor.data.plot(y="pm2_5", label="{} PM2.5".format(sensor.sensor_id), ax=ax)
        plt.ylabel(r"PM concentration ($\mathrm{\mu g/m^3}$)")
    if pm10:
        for label in [x for x in pm_limits if x.startswith("PM10")]:
            plt.plot(plt.xlim(), [pm_limits[label][0]]*2, linestyle="--",
                color=pm_limits[label][1], label=label
            )
    if pm2_5:
        for label in [x for x in pm_limits if x.startswith("PM2.5")]:
            plt.plot(plt.xlim(), [pm_limits[label][0]]*2, linestyle="--",
                color=pm_limits[label][1], label=label
            )
    plt.grid(axis='y')
    plt.legend()
    plt.show()

def plot_multiple_temperature(sensors):
    """Plot time series of temperature data from multiple sensors.

    Parameters:
        sensors (list(AQData)): the sensors containing the dataset to plot

    """
    ax = plt.figure().gca()
    for sensor in sensors:
        sensor.data.plot(y="temperature", label="{} temperature".format(sensor.sensor_id), ax=ax)
        plt.ylabel(r"temperature ($\mathrm{\degree C}$)")
    plt.grid(axis='y')
    plt.legend()
    plt.show()

def plot_pm(sensor, maxy=None):
    """Plot time series of PM10 + PM2.5 data.

    Parameters:
        sensor (AQData): the sensor containing the dataset to plot
        maxy (float): ylim upper limit for the pm plot

    """
    # TODO: use resample instead
    daily_data = sensor.data.resample('d').mean()
    high_humidity = sensor.data.humidity > humidity_threshold

    f, (a0, a1) = plt.subplots(2, 1, sharex=True, gridspec_kw={'height_ratios': [1, 5]})
    a0.plot(sensor.data.index, masked_where(1 - high_humidity, sensor.data.humidity), 'r', ms=1)
    a0.plot(sensor.data.index, masked_where(high_humidity, sensor.data.humidity), 'b', ms=1)
    highlight(sensor.data.index, high_humidity, a0)
    a0.set_ylim([0, 100])
    a0.set_yticks([0, humidity_threshold, 100])
    a0.grid(axis='y')
    a0.set_ylabel("humidity (%)")

    sensor.data.plot(y="pm10", color="steelblue", label="PM10 (avg={:.1f})".format(sensor.data.pm10.mean()), ax=a1)
    sensor.data.plot(y="pm2_5", color="orange", label="PM2.5 (avg={:.1f})".format(sensor.data.pm2_5.mean()), ax=a1)
    sensor.data.plot(y="pm2_5_calib", color="olivedrab", label="PM2.5_calib (avg={:.1f})".format(sensor.data.pm2_5_calib.mean()), ax=a1)
    daily_data.plot(y="pm10", color="darkblue", marker="o", linestyle="", label="daily PM10 avg", ax=a1)
    daily_data.plot(y="pm2_5", color="red", marker="o", linestyle="", label="daily PM2.5 avg", ax=a1)
    daily_data.plot(y="pm2_5_calib", color="darkgreen", marker="o", linestyle="", label="daily calibrated PM2.5 avg", ax=a1)
    for label in pm_limits:
        a1.plot(a1.get_xlim(), [pm_limits[label][0]]*2,
            color=pm_limits[label][1], linestyle='--', label=label
        )
    highlight(sensor.data.index, high_humidity, a1)
    a1.set_ylabel(r"PM concentration ($\mathrm{\mu g/m^3}$)")
    a1.grid(axis='y')
    plt.legend()
    plt.title(r"Sensor ID: {}, PM10 polluted days: {}/{}".format(
        sensor.sensor_id,
        daily_data.pm10[daily_data.pm10 > pm_limits["PM10 daily health limit"][0]].count(),
        len(daily_data),
    ))
    a1.set_ylim([0, maxy or a1.get_ylim()[1]])
    plt.show()

def plot_pm_ratio(sensor):
    """Plot time series of relative PM10 / PM2.5 data.

    Parameters:
        sensor (AQData): the sensor containing the dataset to plot

    """
    sensor.data.plot(y="pm10_per_pm2_5", label="PM10 / PM2.5")
    plt.grid(axis='y')
    plt.legend()
    plt.title("Sensor ID: {}".format(sensor.sensor_id))
    plt.show()

def plot_temperature(sensor):
    """Plot time series of temperature data.

    Parameters:
        sensor (AQData): the sensor containing the dataset to plot

    """

    # plot time series
    sensor.data.plot(y="temperature", label="temperature (avg={:.1f})".format(
        sensor.data.temperature.mean())
    )
    # add min label
    minvalue = sensor.data.temperature.min()
    idxmin = sensor.data.temperature.idxmin()
    plt.text(idxmin, minvalue, "{:.1f}$\mathrm{{\degree C}}$".format(minvalue),
        ha="center", va="top"
    )
    # add max label
    maxvalue = sensor.data.temperature.max()
    idxmax = sensor.data.temperature.idxmax()
    plt.text(idxmax, maxvalue, "{:.1f}$\mathrm{{\degree C}}$".format(maxvalue),
        ha="center", va="bottom"
    )
    # setup additional stuff
    plt.ylabel(r"temperature ($\mathrm{\degree C}$)")
    plt.grid(axis='y')
    ylim = plt.ylim()
    if ylim[0] < 0 and ylim[1] > 0:
        plt.plot(plt.xlim(), [0, 0], "db--")
    plt.title("Sensor ID: {}".format(sensor.sensor_id))
    plt.show()

def plot_pm_vs_humidity(sensor):
    """Plot PM vs humidity data.

    Parameters:
        sensor (AQData): the sensor containing the dataset to plot

    """
    ax = plt.figure().gca()
    sensor.data.plot("humidity", "pm10", style='o', ms=markersize, label="PM10-humidity", ax=ax)
    sensor.data.plot("humidity", "pm2_5", style='o', ms=markersize, label="PM2.5-humidity", ax=ax)
    plt.xlabel("humidity (%)")
    plt.ylabel(r"PM concentration ($\mathrm{\mu g/m^3}$)")
    plt.title("\n".join([
        "Sensor ID: {}".format(sensor.sensor_id),
        "Pearson corr: {:.3f}".format(sensor.data[["pm10"]].corrwith(sensor.data.humidity)[0])
    ]))
    plt.grid()
    plt.show()

def plot_pm_vs_humidity_hist(sensor):
    """Plot PM vs humidity data as a binned histogram.

    Parameters:
        sensor (AQData): the sensor containing the dataset to plot

    Note that in the historgrams we assume that the weight of each measurement
    is the same, even if the time difference between them is different,
    i.e., all data points correspond to the same inner time-averaging period.

    """
    # PM10 vs Humidity heatmap subplots
    fig, axs = plt.subplots(2, 2, sharex=False, sharey=False, gridspec_kw={
        'height_ratios': [1, 5],
        'width_ratios': [5, 1]
    })
    plt.subplots_adjust(left=0.1, right=0.9, wspace=0.08, hspace=0.08)
    ax_main = axs[1, 0]
    ax_right = axs[1, 1]
    ax_top = axs[0, 0]
    ax_empty = axs[0, 1]
    print(ax_main.get_position())

    ############################################################################
    # main 2d histogram in the center

    # create colormap
    cmap = plt.cm.jet
    cmap.set_bad(color="black")
    # create histogram
    hist, xbins, ybins, im = ax_main.hist2d(
        sensor.data.humidity, sensor.data.pm10, bins=(20, 24),
        range=[[0, 100], [0, 300]], cmap=cmap, norm=mpl.colors.LogNorm())
    # show data as text in the center of bins
    for j in range(len(ybins) - 1):
        for i in range(len(xbins) - 1):
            if hist[i, j]:
                ax_main.text(xbins[i] + 2.5, ybins[j] + 5, int(hist[i, j]),
                    ha="center", va="center", fontsize=7
            )
    # plot health limits
    for label in [x for x in pm_limits if x.startswith("PM10")]:
        ax_main.plot(ax_main.get_xlim(), [pm_limits[label][0]]*2,
            linestyle="--", color=pm_limits[label][1], label=label
        )
    # place colorbar
    bottom = ax_main.get_position().y0
    height = ax_top.get_position().y1 - bottom
    cbaxes = fig.add_axes([0.92, bottom, 0.02, height])
    fig.colorbar(im, cax=cbaxes, label="number of measurements")
    # arbitrary texts
    ax_main.set_xlabel("humidity (%)")
    ax_main.set_ylabel(r"PM10 concentration ($\mathrm{\mu g/m^3}$)")
    ax_main.legend(loc="upper left")

    ############################################################################
    # 1d histogram of humidity at the top

    ax_top.hist(sensor.data.humidity, bins=20, range=[0, 100],
        histtype="step",
        weights=np.ones(len(sensor.data.humidity)) / len(sensor.data.humidity)
    )
    ax_top.set_xlim([0, 100])
    ax_top.get_xaxis().set_visible(False)
    ax_top.set_ylabel("percent")
    ax_top.grid()
    ax_top.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(1))
    # adjust bounding box of top plot to be consistent with main plot
    # as colorbar messes default up
    bb = ax_top.get_position()
    bb.x1 = ax_main.get_position().x1
    ax_top.set_position(bb)

    ############################################################################
    # 1d histogram of pollution at the right
    ax_right.hist(sensor.data.pm10, bins=24, range=[0, 300],
        histtype="step", orientation="horizontal",
        weights=np.ones(len(sensor.data.pm10)) / len(sensor.data.pm10))
    for label in [x for x in pm_limits if x.startswith("PM10")]:
        ax_right.plot(ax_right.get_xlim(), [pm_limits[label][0]]*2,
            linestyle="--", color=pm_limits[label][1], label=label
        )
    ax_right.set_ylim([0, 300])
    ax_right.get_yaxis().set_visible(False)
    ax_right.set_xlabel("percent")
    ax_right.grid()
    ax_right.xaxis.set_major_formatter(mpl.ticker.PercentFormatter(1))

    ############################################################################
    # global stuff

    ax_empty.axis("off")
    plt.suptitle("\n".join([
        "Sensor ID: {}".format(sensor.sensor_id),
        "Pearson corr: {:.3f}".format(sensor.data[["pm10"]].corrwith(sensor.data.humidity)[0])
    ]))
    plt.show()

def plot_pm_vs_temperature(sensor):
    """Plot PM vs temperature data.

    Parameters:
        sensor (AQData): the sensor containing the dataset to plot

    """
    ax = plt.figure().gca()
    sensor.data.plot("temperature", "pm10", style='o', ms=markersize, label="PM10-temp", ax=ax)
    sensor.data.plot("temperature", "pm2_5", style='o', ms=markersize, label="PM2.5-temp", ax=ax)
    plt.xlabel(r"temperature ($\mathrm{\degree C}$)")
    plt.ylabel(r"PM concentration ($\mathrm{\mu g/m^3}$)")
    plt.title("\n".join([
        "Sensor ID: {}".format(sensor.sensor_id),
        "Pearson corr: {:.3f}".format(sensor.data[["pm10"]].corrwith(sensor.data.temperature)[0])
    ]))
    plt.grid()
    plt.show()
