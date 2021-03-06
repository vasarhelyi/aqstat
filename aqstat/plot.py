"""This script contains plotting functions for AQData classes."""

import logging
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from numpy.ma import masked_where
from pandas import concat
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()

from aqstat.cli.main import _

# note that these are needed for understanding  _(key) declaratinos as part of
# the .pot translation database that is automatically extracted by pygettext.py
_("temperature")
_("humidity")
_("pressure")

# global parameters
markersize = 3
humidity_threshold = 70
# PM health limits from these sources:
# http://emiktf.hu/olm.html
# http://www.levegominoseg.hu/hatarertek
pm_limits = {
    _("PM2.5 yearly limit"): (25, "coral"),
    _("PM10 daily health limit"): (50, "red"),
    _("PM10 daily notification limit"): (75, "darkred"),
    _("PM10 daily emergency limit"): (100, "black"),
}

# feasible measurement ranges for each sensor type
sensor_ranges = {
    "humidity": [0, 100],
    "temperature": [-15, 35],
    "pm10": [0, 300],
    "pm2_5": [0, 100],
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
        ax.axvspan(x[start], x[stop], facecolor="black", edgecolor="none", alpha=0.2)
        start = stop + 1


def add_pm_limits(keys, ax):
    """Add sensor limits to the plots.

    Parameters:
        keys(list[str]): list of keys that are plotted on the y axis
        ax(?): matplotlib axis

    """
    xlim = ax.get_xlim()
    if "pm10" in keys:
        for label in [x for x in pm_limits if x.startswith("PM10")]:
            ax.plot(
                xlim,
                [pm_limits[label][0]] * 2,
                linestyle="--",
                color=pm_limits[label][1],
                label=label,
            )
    if "pm2_5" in keys or "pm2_5_calib" in keys:
        for label in [x for x in pm_limits if x.startswith("PM2.5")]:
            ax.plot(
                xlim,
                [pm_limits[label][0]] * 2,
                linestyle="--",
                color=pm_limits[label][1],
                label=label,
            )


def plot_daily_variation(sensor, keys):
    """Plot daily variation of data accumulated through several days.

    Parameters:
        sensor (AQData): the sensor containing the dataset to plot
        keys (list[str]): the list of keys of the data Series we need to plot
    """

    for i, key in enumerate(keys):
        data = sensor.data[key]
        daily_average = data.groupby(data.index.day).transform("mean")
        total_average = data.mean()
        data1 = (data - total_average).groupby(data.index.hour).agg(["mean", "std"])
        data2 = (data - daily_average).groupby(data.index.hour).agg(["mean", "std"])
        plt.errorbar(
            x=data1.index + i * 0.1,
            y=data1["mean"],
            yerr=data1["std"],
            label="{} - {}({:.1f})".format(_(key), _("avg"), total_average),
        )
        plt.errorbar(
            x=data2.index + i * 0.1,
            y=data2["mean"],
            yerr=data2["std"],
            label="{} - {}".format(_(key), _("daily_avg")),
        )
    plt.grid(axis="y")
    plt.xlabel(_("time of day"))
    plt.ylabel(_("daily variation"))
    plt.title(sensor.name)
    plt.legend()
    plt.show()


def plot_daily_variation_hist(sensor, keys, mins=None):
    """Plot histogram of daily variation of data accumulated through several days.

    Parameters:
        sensor (AQData): the sensor containing the dataset to plot
        keys (list[str]): the list of keys of the data Series we need to plot
        mins (list[float]): the list of lower threshold values corresponding
            to the keys, or None if no lower threshold is used
    """

    for i, key in enumerate(keys):
        if mins is None:
            data = sensor.data[key]
        else:
            data = sensor.data[key][sensor.data[key] >= mins[i]]
        plt.hist(
            data.index.hour,
            bins=24,
            range=[0, 23],
            histtype="bar",
            weights=np.ones(len(data)) / len(data),
            label="{}{}".format(key, "" if mins is None else " > {}".format(mins[i])),
        )
    plt.grid(axis="y")
    plt.xlabel(_("time of day"))
    plt.ylabel(_("relative occurrence (%)"))
    plt.title(
        "\n".join(
            [
                "{}, period: {} - {}".format(
                    sensor.name,
                    sensor.data.index[0].date(),
                    sensor.data.index[-1].date(),
                ),
                "measurements: {}, sampling median: {}".format(
                    len(data), sensor.median_sampling_time
                ),
            ]
        )
    )
    plt.gca().yaxis.set_major_formatter(mpl.ticker.PercentFormatter(1))
    plt.legend()
    plt.show()


def plot_humidity(sensor):
    """Plot time series of humidity data.

    Parameters:
        sensor (AQData): the sensor containing the dataset to plot

    """
    # plot time series
    sensor.data.plot(
        y="humidity",
        label="{} ({} ={:.1f})".format(
            _("humidity"), _("avg"), sensor.data.humidity.mean()
        ),
    )
    # add min label
    minvalue = sensor.data.humidity.min()
    idxmin = sensor.data.humidity.idxmin()
    plt.text(idxmin, minvalue, "{:.1f} %".format(minvalue), ha="center", va="top")
    # add max label
    maxvalue = sensor.data.humidity.max()
    idxmax = sensor.data.humidity.idxmax()
    plt.text(idxmax, maxvalue, "{:.1f} %".format(maxvalue), ha="center", va="bottom")

    plt.ylabel("{} (%)".format(_("humidity")))
    plt.grid(axis="y")
    plt.title(sensor.name)
    plt.show()


def plot_multiple_altitude(sensors):
    """Plot averaged sensor data as a function of altitude from multiple sensors.

    Size of markers correspond to relative amount of data of each point.

    Parameters:
        sensors (list(AQData)): the sensors containing the dataset to plot

    """
    for key in ["temperature", "humidity", "pm10", "pm2_5", "pm2_5_calib"]:
        x = []
        y = []
        yerr = []
        names = []
        counts = []
        for sensor in sensors:
            xx = sensor.altitude
            yy = sensor.data[key].mean()
            yyerr = sensor.data[key].std()
            count = len(sensor.data[key])
            if xx != xx or yy != yy or yyerr != yyerr:
                continue
            if not x:
                date_start = sensor.data.index[0].date()
                date_end = sensor.data.index[-1].date()
            else:
                date_start = min(date_start, sensor.data.index[0].date())
                date_end = max(date_end, sensor.data.index[-1].date())
            x.append(xx)
            y.append(yy)
            yerr.append(yyerr)
            names.append(sensor.name)
            counts.append(count)
            plt.text(xx, yy, "  {}".format(sensor.name), va="center_baseline")
        # plot y errors as data standard deviation
        plt.errorbar(x, y, yerr=yerr, ls="None", color="b")
        # change marker size according to amount of data used
        areas = [100 * x / max(counts) for x in counts]
        plt.scatter(x, y, s=areas, color="b")
        # plot linear fit
        coef = np.polyfit(x, y, 1)
        poly1d_fn = np.poly1d(coef)
        plt.plot(x, poly1d_fn(x), "r--")
        # add pm limits
        if "pm" in key:
            add_pm_limits(key, plt.gca())
            plt.legend()
        # set labels
        plt.xlabel("Above mean sea level (m)")
        plt.ylabel(key)
        plt.title(
            "\n".join(
                [
                    "period: {} - {}".format(date_start, date_end),
                    "linear fit: {} = {:g} * altitude {} {:g}".format(
                        key, coef[0], "+" if coef[1] >= 0 else "-", abs(coef[1])
                    ),
                ]
            )
        )
        plt.show()


def plot_multiple_humidity(sensors):
    """Plot time series of humidity data from multiple sensors.

    Parameters:
        sensors (list(AQData)): the sensors containing the dataset to plot

    """
    ax = plt.figure().gca()
    for sensor in sensors:
        if sensor.data.humidity.isnull().all():
            continue
        sensor.data.plot(y="humidity", label="{} humidity".format(sensor.name), ax=ax)
        plt.ylabel("{} (%)".format(_("humidity")))
    plt.plot(
        plt.xlim(), [humidity_threshold] * 2, "r--", label="PM sensor validity limit"
    )
    plt.ylim([0, 100])
    plt.grid(axis="y")
    plt.legend()
    plt.show()


def plot_multiple_pm(sensors, key="pm10", window=None):
    """Plot time series of PM10/PM2.5/PM2.5_calib data from multiple sensors.

    Parameters:
        sensors (list(AQData)): the sensors containing the dataset to plot
        key (str): the key of the data Series we need to plot.
        window(int|offset): size of moving window averaging or None if not used.

    """
    ax = plt.figure().gca()
    alldata = None
    for sensor in sorted(sensors, key=lambda x: x.altitude, reverse=True):
        # smooth if rolling window is specified
        if window:
            data = sensor.data.rolling(window=window).mean()
        else:
            data = sensor.data
        # add data to alldata
        if alldata is None:
            alldata = sensor.data[[key]]
        else:
            alldata = concat([alldata, sensor.data[[key]]])
        # skip data if not valid
        if data[key].isnull().all():
            continue
        # add data to plot
        data.plot(
            y=key,
            label="{} {} @ {}m".format(sensor.name, key.upper(), sensor.altitude),
            ax=ax,
            linewidth=2
            if key == "pm10" and sensor.metadata.sensors["pm10"].type == "OLM"
            else 1,
        )
        plt.ylabel(r"PM {} ($\mathrm{{\mu g/m^3}}$)".format(_("concentration")))
    add_pm_limits([key], ax)
    # add alldata daily averages
    daily_data = alldata.resample("d").mean()
    daily_data.plot(
        y=key,
        color="darkblue",
        marker="o",
        linestyle="",
        label="{} {} {}".format(_("daily"), key.upper(), _("avg")),
        ax=ax,
    )
    titles = []
    if key == "pm10":
        titles.append(
            r"PM10 {}: {}/{}".format(
                _("polluted days"),
                daily_data.pm10[
                    daily_data.pm10 > pm_limits[_("PM10 daily health limit")][0]
                ].count(),
                len(daily_data),
            )
        )

    # set other attributes
    if window:
        titles.append("{}: {}".format(_("rolling window"), window))
    plt.title("\n".join(titles[::-1]))
    plt.grid(axis="y")
    ax.set_ylim([0, None])
    plt.legend()
    plt.show()


def plot_multiple_temperature(sensors):
    """Plot time series of temperature data from multiple sensors.

    Parameters:
        sensors (list(AQData)): the sensors containing the dataset to plot

    """
    ax = plt.figure().gca()
    for sensor in sensors:
        if sensor.data.temperature.isnull().all():
            continue
        sensor.data.plot(
            y="temperature", label="{} {}".format(sensor.name, _("temperature")), ax=ax
        )
        plt.ylabel(r"{} ($\mathrm{{\degree C}}$)".format(_("temperature")))
    plt.grid(axis="y")
    plt.legend()
    plt.show()


def plot_pm(sensor, gsod=None, window=None):
    """Plot time series of PM10 + PM2.5 data.

    Parameters:
        sensor (AQData): the sensor containing the dataset to plot
        gsod (DataFrame): GSOD data to use for the plot
        window(int|offset): size of moving window averaging or None if not used.

    """
    # create daily data
    daily_data = sensor.data.resample("d").mean()
    # create subplots
    f, (a0, a1) = plt.subplots(
        2, 1, sharex=False, gridspec_kw={"height_ratios": [1, 5]}
    )
    # create humidity plot
    high_humidity = sensor.data.humidity > humidity_threshold
    a0.plot(
        sensor.data.index,
        masked_where(1 - high_humidity, sensor.data.humidity),
        "r",
        ms=1,
    )
    a0.plot(
        sensor.data.index, masked_where(high_humidity, sensor.data.humidity), "b", ms=1
    )
    highlight(sensor.data.index, high_humidity, a0)
    a0.set_xlim(sensor.data.index[0], sensor.data.index[-1])
    a0.set_ylim([0, 100])
    a0.set_yticks([0, humidity_threshold, 100])
    a0.tick_params(axis="x", which="minor", bottom=False)
    a0.grid(axis="y")
    a0.set_ylabel("{} (%)".format(_("humidity")))
    # create wind plot
    if gsod is not None:
        a02 = a0.twinx()
        a02.plot(gsod.index, gsod.MXSPD, "o-g", ms=3)
        a02.set_xlim(sensor.data.index[0], sensor.data.index[-1])
        a02.set_ylim([0, None])
        a02.set_ylabel("wind (m/s)", color="g")
        a02.spines["right"].set_color("g")
        a02.tick_params(axis="y", colors="g")
        a02.legend()
    # use rolling window if needed
    if window:
        data = sensor.data.rolling(window=window).mean()
    else:
        data = sensor.data
    # plot data
    data.plot(
        y="pm10",
        color="steelblue",
        label="PM10 ({}={:.1f})".format(_("avg"), sensor.data.pm10.mean()),
        ax=a1,
    )
    data.plot(
        y="pm2_5",
        color="orange",
        label="PM2.5 ({}={:.1f})".format(_("avg"), sensor.data.pm2_5.mean()),
        ax=a1,
    )
    data.plot(
        y="pm2_5_calib",
        color="olivedrab",
        label="PM2.5_calib ({}={:.1f})".format(
            _("avg"), sensor.data.pm2_5_calib.mean()
        ),
        ax=a1,
    )
    daily_data.plot(
        y="pm10",
        color="darkblue",
        marker="o",
        linestyle="",
        label="{} PM10 {}".format(_("daily"), _("avg")),
        ax=a1,
    )
    daily_data.plot(
        y="pm2_5",
        color="red",
        marker="o",
        linestyle="",
        label="{} PM2.5 {}".format(_("daily"), _("avg")),
        ax=a1,
    )
    daily_data.plot(
        y="pm2_5_calib",
        color="darkgreen",
        marker="o",
        linestyle="",
        label="{} {} PM10 {}".format(_("daily"), _("calibrated"), _("avg")),
        ax=a1,
    )
    add_pm_limits(["pm10", "pm2_5", "pm2_5_calib"], a1)
    highlight(sensor.data.index, high_humidity, a1)
    a1.set_xlim(sensor.data.index[0], sensor.data.index[-1])
    a1.set_ylim(sensor_ranges["pm10"])
    a1.set_ylabel(r"PM {} ($\mathrm{{\mu g/m^3}}$)".format(_("concentration")))
    a1.grid(axis="y")
    a1.legend()
    a1.set_title(
        r"PM10 {}: {}/{}".format(
            _("polluted days"),
            daily_data.pm10[
                daily_data.pm10 > pm_limits[_("PM10 daily health limit")][0]
            ].count(),
            len(daily_data),
        )
    )
    title = sensor.name
    if window:
        title += "\n{}: {}".format(_("rolling window"), window)
    a0.set_title(title)
    # set common xlim (note: sharex does not work if there is no humidity but gsod data)
    a0.set_xticks(a1.get_xticks())
    plt.show()


def plot_pm_ratio(sensor):
    """Plot time series of relative PM10 / PM2.5 data.

    Parameters:
        sensor (AQData): the sensor containing the dataset to plot

    """
    sensor.data.plot(y="pm10_per_pm2_5", label="PM10 / PM2.5")
    plt.grid(axis="y")
    plt.legend()
    plt.title(sensor.name)
    plt.show()


def plot_temperature(sensor):
    """Plot time series of temperature data.

    Parameters:
        sensor (AQData): the sensor containing the dataset to plot

    """

    # plot time series
    sensor.data.plot(
        y="temperature",
        label="{} ({}={:.1f})".format(
            _("temperature"), _("avg"), sensor.data.temperature.mean()
        ),
    )
    # add min label
    minvalue = sensor.data.temperature.min()
    idxmin = sensor.data.temperature.idxmin()
    plt.text(
        idxmin,
        minvalue,
        r"{:.1f}$\mathrm{{\degree C}}$".format(minvalue),
        ha="center",
        va="top",
    )
    # add max label
    maxvalue = sensor.data.temperature.max()
    idxmax = sensor.data.temperature.idxmax()
    plt.text(
        idxmax,
        maxvalue,
        r"{:.1f}$\mathrm{{\degree C}}$".format(maxvalue),
        ha="center",
        va="bottom",
    )
    # setup additional stuff
    plt.ylabel(r"{} ($\mathrm{{\degree C}}$)".format(_("temperature")))
    plt.grid(axis="y")
    ylim = plt.ylim()
    if ylim[0] < 0 and ylim[1] > 0:
        plt.plot(plt.xlim(), [0, 0], "db--")
    plt.title(sensor.name)
    plt.show()


def plot_pm_vs_humidity(sensor):
    """Plot PM vs humidity data.

    Parameters:
        sensor (AQData): the sensor containing the dataset to plot

    """
    ax = plt.figure().gca()
    sensor.data.plot(
        "humidity", "pm10", style="o", ms=markersize, label="PM10-humidity", ax=ax
    )
    sensor.data.plot(
        "humidity", "pm2_5", style="o", ms=markersize, label="PM2.5-humidity", ax=ax
    )
    plt.xlabel("{} (%)".format(_("humidity")))
    plt.ylabel(r"PM {} ($\mathrm{{\mu g/m^3}}$)".format(_("concentration")))
    plt.title(
        "\n".join(
            [
                sensor.name,
                "Pearson corr: {:.3f}".format(
                    sensor.data[["pm10"]].corrwith(sensor.data.humidity)[0]
                ),
            ]
        )
    )
    plt.grid()
    plt.show()


def plot_pm_vs_environment_hist(sensor, key="humidity"):
    """Plot PM vs humidity/temperature data as a binned histogram.

    Parameters:
        sensor (AQData): the sensor containing the dataset to plot
        key (str): 'humidity' or 'temperature' on x axis

    Note that in the historgrams we assume that the weight of each measurement
    is the same, even if the time difference between them is different,
    i.e., all data points correspond to the same inner time-averaging period.

    """
    # PM10 vs Humidity/temperature heatmap subplots
    fig, axs = plt.subplots(
        2, 2, gridspec_kw={"height_ratios": [1, 5], "width_ratios": [5, 1]}
    )
    plt.subplots_adjust(left=0.1, right=0.9, wspace=0.08, hspace=0.08)
    ax_main = axs[1, 0]
    ax_right = axs[1, 1]
    ax_top = axs[0, 0]
    ax_empty = axs[0, 1]

    if key == "humidity":
        xdata = sensor.data.humidity
        xlabel = "{} (%)".format(_("humidity"))
    elif key == "temperature":
        xdata = sensor.data.temperature
        xlabel = r"{} ($\mathrm{{\degree C}}$)".format(_("temperature"))

    ############################################################################
    # main 2d histogram in the center

    # create colormap
    cmap = plt.cm.jet
    cmap.set_bad(color="black")
    # create histogram
    hist, xbins, ybins, im = ax_main.hist2d(
        xdata,
        sensor.data.pm10,
        bins=(20, 24),
        range=[sensor_ranges[key], sensor_ranges["pm10"]],
        cmap=cmap,
        norm=mpl.colors.LogNorm(),
    )
    # show data as text in the center of bins
    dx = (xbins[1] - xbins[0]) / 2
    dy = (ybins[1] - ybins[0]) / 2 - 1.5  # TODO: why va='center' does not work?
    for j in range(len(ybins) - 1):
        for i in range(len(xbins) - 1):
            if hist[i, j]:
                ax_main.text(
                    xbins[i] + dx,
                    ybins[j] + dy,
                    int(hist[i, j]),
                    ha="center",
                    va="center",
                    fontsize=7,
                )
    # plot health limits
    add_pm_limits(["pm10"], ax_main)
    # plot pm10 humidity working limit
    if key == "humidity":
        ax_main.plot(
            [humidity_threshold] * 2,
            ax_main.get_ylim(),
            "b--",
            label="humidity limit of PM sensor",
        )
    # place colorbar
    bottom = ax_main.get_position().y0
    height = ax_top.get_position().y1 - bottom
    cbaxes = fig.add_axes([0.92, bottom, 0.02, height])
    fig.colorbar(im, cax=cbaxes, label=_("number of measurements"))
    # arbitrary texts
    ax_main.set_xlabel(xlabel)
    ax_main.set_ylabel(r"PM10 {} ($\mathrm{{\mu g/m^3}}$)".format(_("concentration")))
    ax_main.legend(loc="upper left")

    ############################################################################
    # 1d histogram of humidity/temperature at the top

    ax_top.hist(
        xdata,
        bins=20,
        range=sensor_ranges[key],
        histtype="step",
        weights=np.ones(len(xdata)) / len(xdata),
    )
    ax_top.set_xlim(sensor_ranges[key])
    ax_top.get_xaxis().set_visible(False)
    ax_top.set_ylabel(_("percent"))
    ax_top.grid()
    ax_top.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(1))
    # adjust bounding box of top plot to be consistent with main plot
    # as colorbar messes default up
    bb = ax_top.get_position()
    bb.x1 = ax_main.get_position().x1
    ax_top.set_position(bb)

    ############################################################################
    # 1d histogram of pollution at the right
    ax_right.hist(
        sensor.data.pm10,
        bins=24,
        range=sensor_ranges["pm10"],
        histtype="step",
        orientation="horizontal",
        weights=np.ones(len(sensor.data.pm10)) / len(sensor.data.pm10),
    )
    add_pm_limits(["pm10"], ax_right)
    ax_right.set_ylim(sensor_ranges["pm10"])
    ax_right.get_yaxis().set_visible(False)
    ax_right.set_xlabel(_("percent"))
    ax_right.grid()
    ax_right.xaxis.set_major_formatter(mpl.ticker.PercentFormatter(1))

    ############################################################################
    # global stuff

    ax_empty.axis("off")
    plt.suptitle(
        "\n".join(
            [
                "{}, {}: {} - {}".format(
                    sensor.name,
                    _("period"),
                    sensor.data.index[0].date(),
                    sensor.data.index[-1].date(),
                ),
                "{}: {}, {}: {}".format(
                    _("measurements"),
                    len(sensor.data),
                    _("sampling median"),
                    sensor.median_sampling_time,
                ),
                "PM10 - {} Pearson {}: {:.3f}".format(
                    _(key), _("corr"), sensor.data[["pm10"]].corrwith(xdata)[0]
                ),
            ]
        )
    )
    plt.show()


def plot_pm_vs_temperature(sensor):
    """Plot PM vs temperature data.

    Parameters:
        sensor (AQData): the sensor containing the dataset to plot

    """
    ax = plt.figure().gca()
    sensor.data.plot(
        "temperature",
        "pm10",
        style="o",
        ms=markersize,
        label="PM10-{}".format(_("temp")),
        ax=ax,
    )
    sensor.data.plot(
        "temperature",
        "pm2_5",
        style="o",
        ms=markersize,
        label="PM2.5-{}".format(_("temp")),
        ax=ax,
    )
    plt.xlabel(r"{} ($\mathrm{{\degree C}}$)".format(_("temperature")))
    plt.ylabel(r"PM {} ($\mathrm{{\mu g/m^3}}$)".format(_("concentration")))
    plt.title(
        "\n".join(
            [
                sensor.name,
                "Pearson {}: {:.3f}".format(
                    _("corr"),
                    sensor.data[["pm10"]].corrwith(sensor.data.temperature)[0],
                ),
            ]
        )
    )
    plt.grid()
    plt.show()
