"""This script contains plotting functions for AQData classes."""

import matplotlib.pyplot as plt

from .stat import daily_average, pearson

# global parameters
markersize=3

def plot_humidity(sensor):
    """Plot time series of humidity data.

    Parameters:
        sensor (AQSensor): the sensor containing the dataset to plot

    """
    plt.plot(sensor.data.time, sensor.data.humidity, label="humidity")
    plt.ylabel("humidity (%)")
    plt.grid(axis='y')
    plt.title("Sensor ID: {}".format(sensor.sensor_id))
    plt.show()

def plot_multiple_pm(sensors, pm10=True, pm2_5=True):
    """Plot time series of PM10 + PM2.5 data from multiple sensors.

    Parameters:
        sensors (list(AQSensor)): the sensors containing the dataset to plot
        pm10 (bool): should we plot pm10 data?
        pm2_5 (bool): should we plot pm2_5 data?

    """
    plt.tight_layout()
    for sensor in sensors:
        daily_data = daily_average(sensor.data)
        if pm10:
            plt.plot(sensor.data.time, sensor.data.pm10, label="{} PM10".format(sensor.sensor_id))
        if pm2_5:
            plt.plot(sensor.data.time, sensor.data.pm2_5, label="{} PM2.5".format(sensor.sensor_id))
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
        sensor (AQSensor): the sensor containing the dataset to plot

    """
    daily_data = daily_average(sensor.data)

    plt.tight_layout()
    plt.plot(sensor.data.time, sensor.data.pm10, label="PM10")
    plt.plot(sensor.data.time, sensor.data.pm2_5, label="PM2.5")
    plt.plot(daily_data.time, daily_data.pm10, 'ro', label="daily PM10")
    plt.plot(daily_data.time, daily_data.pm2_5, 'ko', label="daily PM2.5")
    plt.plot([sensor.data.time[0], sensor.data.time[-1]], [50, 50], 'r--', label="PM10 24h limit")
    plt.plot([sensor.data.time[0], sensor.data.time[-1]], [25, 25], 'k--', label="PM2.5 yearly limit")
    plt.ylabel(r"PM concentration ($\mathrm{\mu g/m^3}$)")
    plt.grid(axis='y')
    plt.legend()
    plt.title("Sensor ID: {}".format(sensor.sensor_id))
    plt.show()

def plot_pm_ratio(sensor):
    """Plot time series of relative PM10 / PM2.5 data.

    Parameters:
        sensor (AQSensor): the sensor containing the dataset to plot

    """
    plt.plot(sensor.data.time, [x / y for x, y in \
        zip(sensor.data.pm10, sensor.data.pm2_5)], label="PM10 / PM2.5"
    )
    plt.grid(axis='y')
    plt.legend()
    plt.tight_layout()
    plt.title("Sensor ID: {}".format(sensor.sensor_id))
    plt.show()

def plot_temperature(sensor):
    """Plot time series of temperature data.

    Parameters:
        sensor (AQSensor): the sensor containing the dataset to plot

    """
    plt.plot(sensor.data.time, sensor.data.temperature, label="temperature")
    plt.ylabel(r"temperature ($\mathrm{\degree C}$)")
    plt.grid(axis='y')
    plt.tight_layout()
    plt.title("Sensor ID: {}".format(sensor.sensor_id))
    plt.show()

def plot_pm_vs_humidity(sensor):
    """Plot PM vs humidity data.

    Parameters:
        sensor (AQSensor): the sensor containing the dataset to plot

    """
    plt.plot(sensor.data.humidity, sensor.data.pm10, 'o', markersize=markersize, label="PM10-humidity")
    plt.plot(sensor.data.humidity, sensor.data.pm2_5, 'o', markersize=markersize, label="PM2.5-humidity")
    plt.xlabel("humidity (%)")
    plt.ylabel(r"PM concentration ($\mathrm{\mu g/m^3}$)")
    plt.title("Pearson: {}".format(pearson(sensor.data.pm10, sensor.data.humidity)))
    plt.grid()
    plt.tight_layout()
    plt.title("Sensor ID: {}".format(sensor.sensor_id))
    plt.show()

def plot_pm_vs_temperature(sensor):
    """Plot PM vs temperature data.

    Parameters:
        sensor (AQSensor): the sensor containing the dataset to plot

    """
    plt.plot(sensor.data.temperature, sensor.data.pm10, 'o', markersize=markersize, label="PM10-temp")
    plt.plot(sensor.data.temperature, sensor.data.pm2_5, 'o', markersize=markersize, label="PM2.5-temp")
    plt.xlabel(r"temperature ($\mathrm{\degree C}$)")
    plt.ylabel(r"PM concentration ($\mathrm{\mu g/m^3}$)")
    plt.title("\n".join([
        "Sensor ID: {}".format(sensor.sensor_id),
        "Pearson corr: {}".format(pearson(sensor.data.pm10, sensor.data.temperature))
    ]))
    plt.grid()
    plt.tight_layout()
    plt.show()
