"""This is a first attempt to test-visualize some of the air quality data
coming from https://www.madavi.de/sensor/csvfiles.php?sensor=esp8266-11797099

Note: The script is mostly a "lab" test to catalyze thinking about how this whole
thing should be treated. See TODO-s below emerging through coding:

TODO:

    - how to store data in a very efficient and stable database?
    - how to sort data in a very efficient way when adding two datasets?
    - how to parse/store other variables (e.g. Sensor ID, height, GPS loc etc.)
    - how to organize data from different sensors?

"""

import click
import logging
from pathlib import Path

from .aqdata import AQData
from .plot import plot_humidity, plot_pm, plot_pm_ratio, plot_temperature, \
    plot_pm_vs_humidity, plot_pm_vs_temperature

@click.command()
@click.option("-v", "--verbose", count=True, help="increase logging verbosity")
@click.argument("inputdir", type=click.Path(exists=True))
def main(inputdir, verbose=False):
    """Plot all kinds of air quality related stuff from .csv files in INPUTDIR."""

    # setup logging
    if verbose > 1:
        log_level = logging.DEBUG
    elif verbose > 0:
        log_level = logging.INFO
    else:
        log_level = logging.WARN
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")
    # initialize empty dataset
    data = AQData()
    # parse all data
    for filename in sorted(Path(inputdir).glob("*.csv")):
        logging.info("Parsing {}".format(filename))
        data = data.merge(AQData.from_csv(filename))

    # plot PM data
    plot_pm(data)
    plot_pm_ratio(data)
    # plot temperature date
    plot_temperature(data)
    # plot humidity data
    plot_humidity(data)
    # plot pm vs humidity data
    plot_pm_vs_humidity(data)
    # plot pm vs temperature data
    plot_pm_vs_temperature(data)