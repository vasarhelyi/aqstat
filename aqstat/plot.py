"""This script contains plotting functions for AQData classes."""

import matplotlib.pyplot as plt

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

import logging

#from .stat import get_overlapping_data, pearson

# global parameters
markersize=3

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

def plot_multiple_pm(sensors, pm10=True, pm2_5=True):
    """Plot time series of PM10 + PM2.5 data from multiple sensors.

    Parameters:
        sensors (list(AQData)): the sensors containing the dataset to plot
        pm10 (bool): should we plot pm10 data?
        pm2_5 (bool): should we plot pm2_5 data?

    """
#    # log Pearson correlation values between different sensor data
#     for i in range(1, len(sensors)):
#         for j in range(i):
#             # TODO: time synchronization is not perfect, interpolation would be needed!
#             a, b = get_overlapping_data(sensors[i].data, sensors[j].data)
#             if pm10:
#                 logging.info("Pearson PM10 {}-{}: {:.3f}".format(
#                     sensors[i].sensor_id,
#                     sensors[j].sensor_id,
#                     pearson(a.pm10, b.pm10)
#                 ))
#             if pm2_5:
#                 logging.info("Pearson PM2.5 {}-{}: {:.3f}".format(
#                     sensors[i].sensor_id,
#                     sensors[j].sensor_id,
#                     pearson(a.pm2_5, b.pm2_5)
#                 ))

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

def plot_pm(sensor):
    """Plot time series of PM10 + PM2.5 data.

    Parameters:
        sensor (AQData): the sensor containing the dataset to plot

    """
    daily_data = sensor.groupby('d').mean().reset_index()

    ax = sensor.data.plot("time", "pm10", label="PM10")
    sensor.data.plot("time", "pm2_5", label="PM2.5", ax=ax)
    daily_data.plot("time", "pm10", style='ro', label="daily PM10", ax=ax)
    daily_data.plot("time", "pm2_5", style='ko', label="daily PM2.5", ax=ax)
    plt.plot([sensor.data.time.iloc[0], sensor.data.time.iloc[-1]], [50, 50], 'r--', label="PM10 24h limit")
    plt.plot([sensor.data.time.iloc[0], sensor.data.time.iloc[-1]], [25, 25], 'k--', label="PM2.5 yearly limit")
    plt.ylabel(r"PM concentration ($\mathrm{\mu g/m^3}$)")
    plt.grid(axis='y')
    plt.legend()
    plt.title("Sensor ID: {}".format(sensor.sensor_id))
    plt.show()

def plot_pm_ratio(sensor):
    """Plot time series of relative PM10 / PM2.5 data.

    Parameters:
        sensor (AQData): the sensor containing the dataset to plot

    """
    plt.plot(sensor.data.time, [x / y for x, y in \
        zip(sensor.data.pm10, sensor.data.pm2_5)], label="PM10 / PM2.5"
    )
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
    ax = sensor.data.plot("humidity", "pm10", style='o', ms=markersize, label="PM10-humidity")
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
    ax = sensor.data.plot("temperature", "pm10", style='o', ms=markersize, label="PM10-temp")
    sensor.data.plot("temperature", "pm2_5", style='o', ms=markersize, label="PM2.5-temp", ax=ax)
    plt.xlabel(r"temperature ($\mathrm{\degree C}$)")
    plt.ylabel(r"PM concentration ($\mathrm{\mu g/m^3}$)")
    plt.title("\n".join([
        "Sensor ID: {}".format(sensor.sensor_id),
        "Pearson corr: {:.3f}".format(sensor.data[["pm10"]].corrwith(sensor.data.temperature)[0])
    ]))
    plt.grid()
    plt.show()
