"""This is a first attempt to test-visualize some of the air quality data
coming from https://www.madavi.de/sensor/csvfiles.php?sensor=esp8266-11797099

Note: The script is mostly a "lab" test to catalyze thinking about how this whole
thing should be treated. See TODO-s below emerging through coding:

"""

import click
import logging
from pathlib import Path

from .aqdata import AQData
from .plot import plot_humidity, plot_multiple_pm, plot_pm, plot_pm_ratio, \
    plot_temperature, plot_pm_vs_humidity, plot_pm_vs_temperature

def find_sensor_with_id(sensors, sensor_id):
    """Find a sensor index with matching sensor_id. If not found but there is
    one with None, we return that. If none found, we return None."""
    first_none = None
    for i, s in enumerate(sensors):
        if s.sensor_id == sensor_id:
            return i
        if first_none is None and s.sensor_id is None:
            first_none = i
    if first_none is not None:
        return i
    return None


@click.command()
@click.option("-v", "--verbose", count=True, help="increase logging verbosity")
@click.argument("inputdir", type=click.Path(exists=True))
def main(inputdir, verbose=False):
    """Plot all kinds of air quality related stuff from all .csv files in the
    directory tree within INPUTDIR."""

    # setup logging
    if verbose > 1:
        log_level = logging.DEBUG
    elif verbose > 0:
        log_level = logging.INFO
    else:
        log_level = logging.WARN
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")
    # parse all data separated according to sensors
    sensors = []
    for filename in sorted(Path(inputdir).glob("**/*.csv")):
        logging.info("Parsing {}".format(filename))
        newsensor = AQData.from_csv(filename)
        i = find_sensor_with_id(sensors, newsensor.sensor_id)
        if i is None:
            sensors.append(AQData())
            i = -1
        sensors[i].merge(newsensor, inplace=True)

    # plot all kinds of things
    for sensor in sensors:
        # plot PM data
        plot_pm(sensor)
        plot_pm_ratio(sensor)
        # plot temperature date
        plot_temperature(sensor)
        # plot humidity data
        plot_humidity(sensor)
        # plot pm vs humidity data
        plot_pm_vs_humidity(sensor)
        # plot pm vs temperature data
        plot_pm_vs_temperature(sensor)

    if len(sensors) > 1:
        plot_multiple_pm(sensors, pm10=True, pm2_5=True)
