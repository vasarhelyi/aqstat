"""This script contains plotting functions for AQData classes."""

import logging
import matplotlib.pyplot as plt

from numpy.ma import masked_where
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


# global parameters
markersize=3
humidity_threshold = 70


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
        while start < n and not condition.iloc[start]:
            start += 1
        if start >= n:
            break
        stop = start
        while stop < len(x) and condition.iloc[stop]:
            stop += 1
        if stop >= n:
            stop -= 1
        ax.axvspan(x.iloc[start], x.iloc[stop], facecolor='black',
            edgecolor='none', alpha=0.2
        )
        start = stop + 1

def plot_humidity(sensor):
    """Plot time series of humidity data.

    Parameters:
        sensor (AQData): the sensor containing the dataset to plot

    """
    sensor.data.plot("time", "humidity")
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
        sensor.data.plot("time", "humidity", label="{} humidity".format(sensor.sensor_id), ax=ax)
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
            sensor.data.plot("time", "pm10", label="{} PM10".format(sensor.sensor_id), ax=ax)
        if pm2_5:
            sensor.data.plot("time", "pm2_5", label="{} PM2.5".format(sensor.sensor_id), ax=ax)
        plt.ylabel(r"PM concentration ($\mathrm{\mu g/m^3}$)")
    if pm10:
        plt.plot(plt.xlim(), [50, 50], 'r--', label="PM10 24h limit")
    if pm2_5:
        plt.plot(plt.xlim(), [25, 25], 'k--', label="PM2.5 yearly limit")
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
        sensor.data.plot("time", "temperature", label="{} temperature".format(sensor.sensor_id), ax=ax)
        plt.ylabel(r"temperature ($\mathrm{\degree C}$)")
    plt.grid(axis='y')
    plt.legend()
    plt.show()

def plot_pm(sensor):
    """Plot time series of PM10 + PM2.5 data.

    Parameters:
        sensor (AQData): the sensor containing the dataset to plot

    """
    # TODO: use resample instead
    daily_data = sensor.groupby('d').mean().reset_index()
    high_humidity = sensor.data.humidity > humidity_threshold

    f, (a0, a1) = plt.subplots(2, 1, sharex=True, gridspec_kw={'height_ratios': [1, 5]})
    a0.plot(sensor.data.time, masked_where(1 - high_humidity, sensor.data.humidity), 'r', ms=1)
    a0.plot(sensor.data.time, masked_where(high_humidity, sensor.data.humidity), 'b', ms=1)
    highlight(sensor.data.time, high_humidity, a0)
    a0.set_ylim([0, 100])
    a0.set_yticks([0, humidity_threshold, 100])
    a0.grid(axis='y')
    a0.set_ylabel("humidity (%)")

    sensor.data.plot("time", "pm10", label="PM10", ax=a1)
    sensor.data.plot("time", "pm2_5", label="PM2.5", ax=a1)
    sensor.data.plot("time", "pm2_5_calib", label="PM2.5_calib", ax=a1)
    daily_data.plot("time", "pm10", style='ro', label="daily PM10", ax=a1)
    daily_data.plot("time", "pm2_5", style='ko', label="daily PM2.5", ax=a1)
    a1.plot([sensor.data.time.iloc[0], sensor.data.time.iloc[-1]], [50, 50], 'r--', label="PM10 24h limit")
    a1.plot([sensor.data.time.iloc[0], sensor.data.time.iloc[-1]], [25, 25], 'k--', label="PM2.5 yearly limit")
    highlight(sensor.data.time, high_humidity, a1)
    a1.set_ylabel(r"PM concentration ($\mathrm{\mu g/m^3}$)")
    a1.grid(axis='y')
    plt.legend()
    plt.title("Sensor ID: {}".format(sensor.sensor_id))
    plt.show()

def plot_pm_ratio(sensor):
    """Plot time series of relative PM10 / PM2.5 data.

    Parameters:
        sensor (AQData): the sensor containing the dataset to plot

    """
    sensor.data.plot("time", "pm10_per_pm2_5", label="PM10 / PM2.5")
    plt.grid(axis='y')
    plt.legend()
    plt.title("Sensor ID: {}".format(sensor.sensor_id))
    plt.show()

def plot_temperature(sensor):
    """Plot time series of temperature data.

    Parameters:
        sensor (AQData): the sensor containing the dataset to plot

    """
    sensor.data.plot("time", "temperature")
    plt.ylabel(r"temperature ($\mathrm{\degree C}$)")
    plt.grid(axis='y')
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
