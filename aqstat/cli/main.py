"""This is a first attempt to test-visualize some of the air quality data
coming from https://www.madavi.de/sensor/csvfiles.php?sensor=esp8266-11797099

Note: The script is mostly a "lab" test to catalyze thinking about how this
whole AQ thing should be treated.

"""

import click
import logging


@click.group()
# TODO: enable this once setuptools is setup properly...
#@click.version_option()
@click.option("-v", "--verbose", count=True, help="increase logging verbosity")
def start(verbose=False):
    """AQStat is a tool to analyze and visualize air quality data collected
    under the luftdaten.info project. Main steps of usage are below.

    0. First of all, you need to know at least the sensor ID or device ID of
       the sensors you want to include in your analysis. Sensor IDs can be
       checked on the sensors.community map when you click on data hexagons.
       Device IDs are exposed at madavi.de archive but they are not associated
       with a location there.

    1. Any analysis or visualization is done offline on your computer, so to
       proceed, you need to download data from archive.sensor.community or
       madavi.de. You can do it with the 'aqstat download' command, see its
       help for details.

    2. For data analysis, visualization and to ease further download processes,
       you have to create metadata .json files for all the devices you
       want to analyze. An example on how a metadata .json file should look
       (one file for each device involved in the analysis) is found in
       aqstat\doc\examples\metadata.json

       Hint: to get started, download some .csv files based on your known
       sensor IDs and run the script
       aqstat\scripts\convert_luftdaten_csv_to_metadata_json.py
       to generate initial .json files for you. Then, supplement them manually
       with proper names and further descriptors for your own convenience.

    3. If all your data and metadata is available (they should be in a dedicated
       air quality directory on your computer, where .json files are in the
       main directory and data .csv files are organized into subdirectories
       according to device IDs or sensor IDs), run `aqstat plot` to visualize
       what you need. See its own help for more details.

       """

    # setup logging
    if verbose > 1:
        log_level = logging.DEBUG
    elif verbose > 0:
        log_level = logging.INFO
    else:
        log_level = logging.WARN
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")


# import commands
from .commands.download import download
from .commands.plot import plot
from .commands.test import test
# add commands from separate files
start.add_command(download)
start.add_command(plot)
start.add_command(test)


if __name__ == '__main__':
    start()