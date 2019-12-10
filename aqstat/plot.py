"""This script contains plotting functions for AQData classes."""

import matplotlib.pyplot as plt

from .stat import daily_average, pearson

# global parameters
markersize=3

def plot_humidity(data):
    """Plot time series of humidity data.

    Parameters:
        data (AQData): the dataset to plot

    """
    plt.plot(data.time, data.humidity, label="humidity")
    plt.ylabel("humidity (%)")
    plt.grid(axis='y')
    plt.show()

def plot_pm(data):
    """Plot time series of PM10 + PM2.5 data.

    Parameters:
        data (AQData): the dataset to plot

    """
    daily_data = daily_average(data)

    plt.tight_layout()
    plt.plot(data.time, data.pm10, label="PM10")
    plt.plot(data.time, data.pm2_5, label="PM2.5")
    plt.plot(daily_data.time, daily_data.pm10, 'o', label="daily PM10")
    plt.plot(daily_data.time, daily_data.pm2_5, 'o', label="daily PM2.5")
    plt.plot([data.time[0], data.time[-1]], [50, 50], 'r--', label="PM10 24h limit")
    plt.plot([data.time[0], data.time[-1]], [25, 25], 'k--', label="PM2.5 yearly limit")
    plt.ylabel(r"PM concentration ($\mathrm{\mu g/m^3}$)")
    plt.grid(axis='y')
    plt.legend()
    plt.show()

def plot_pm_ratio(data):
    """Plot time series of relative PM10 / PM2.5 data.

    Parameters:
        data (AQData): the dataset to plot

    """
    plt.plot(data.time, [x / y for x, y in zip(data.pm10, data.pm2_5)],
        label="PM10 / PM2.5"
    )
    plt.grid(axis='y')
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_temperature(data):
    """Plot time series of temperature data.

    Parameters:
        data (AQData): the dataset to plot

    """
    plt.plot(data.time, data.temperature, label="temperature")
    plt.ylabel(r"temperature ($\mathrm{\degree C}$)")
    plt.grid(axis='y')
    plt.tight_layout()
    plt.show()

def plot_pm_vs_humidity(data):
    """Plot PM vs humidity data.

    Parameters:
        data (AQData): the dataset to plot

    """
    plt.plot(data.humidity, data.pm10, 'o', markersize=markersize, label="PM10-humidity")
    plt.plot(data.humidity, data.pm2_5, 'o', markersize=markersize, label="PM2.5-humidity")
    plt.xlabel("humidity (%)")
    plt.ylabel(r"PM concentration ($\mathrm{\mu g/m^3}$)")
    plt.title("Pearson: {}".format(pearson(data.pm10, data.humidity)))
    plt.grid()
    plt.tight_layout()
    plt.show()

def plot_pm_vs_temperature(data):
    """Plot PM vs temperature data.

    Parameters:
        data (AQData): the dataset to plot

    """
    plt.plot(data.temperature, data.pm10, 'o', markersize=markersize, label="PM10-temp")
    plt.plot(data.temperature, data.pm2_5, 'o', markersize=markersize, label="PM2.5-temp")
    plt.xlabel(r"temperature ($\mathrm{\degree C}$)")
    plt.ylabel(r"PM concentration ($\mathrm{\mu g/m^3}$)")
    plt.title("Pearson: {}".format(pearson(data.pm10, data.temperature)))
    plt.grid()
    plt.tight_layout()
    plt.show()
