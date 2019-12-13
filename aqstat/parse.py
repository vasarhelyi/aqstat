"""Parsing functions for AQData classes."""

import logging
from os.path import basename
from pandas import read_csv

def parse_id_from_luftdaten_csv(filename):
    """Parse the sensor id from a raw luftdaten.info AQ filename.

    Parameters:
        filename (path): the file to parse. Format of the file is expected to be
            the one used by the luftdaten.info project, e.g. as here:
            https://www.madavi.de/sensor/csvfiles.php?sensor=esp8266-11797099

    Return:
        int: sensor id or None in case of format error.

    """
    tokens = basename(filename).split("-")
    if len(tokens) == 6 and tokens[0] == "data" and tokens[1] == "esp8266":
        return int(tokens[2])

    logging.warn("could not parse sensor id from filename: {}".format(filename))
    return None

def parse_luftdaten_csv(filename):
    """Read raw AQ data from luftdaten.info .csv file.

    Parameters:
        filename (path): the file to parse. Format of the file is expected to be
            the one used by the luftdaten.info project, e.g. as here:
            https://www.madavi.de/sensor/csvfiles.php?sensor=esp8266-11797099

    Return:
        pandas DataFrame object containing the data stored in the .csv file

    """
    return read_csv(filename, sep=";", parse_dates=[0])
