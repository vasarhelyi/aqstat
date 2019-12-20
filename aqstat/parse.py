"""Parsing functions for AQData classes."""

import logging
from os.path import basename
from pandas import read_csv
from pathlib import Path

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
        pandas DataFrame object containing the data stored in the .csv file,
        indexed with timestamps (by default defined in the "Time" column).

    """
    return read_csv(filename, sep=";", parse_dates=[0], index_col=0,
        infer_datetime_format=True, skipinitialspace=True)

def parse_sensors_from_path(inputdir, date_start=None, date_end=None):
    """Parse all sensor data in the given period from inputdir.

    Parameters:
        inputdir (Path): the path where sensor data is found, organized in
            directories according to sensor id.
        date_start (datetime): starting date limit or None if not used
        date_end (datetime): ending date limit or None if not used

    Return:
        list of AQData objects separated by sensor id
    """

    # import here to avoid circular imports
    from .aqdata import AQData
    from .utils import find_sensor_with_id

    # parse all data separated according to sensors
    sensors = []
    for filename in sorted(Path(inputdir).glob("**/*.csv")):
        logging.info("Parsing {}".format(filename))
        newsensor = AQData.from_csv(filename, date_start=date_start,
            date_end=date_end
        )
        i = find_sensor_with_id(sensors, newsensor.sensor_id)
        if i is None:
            sensors.append(AQData())
            i = -1
        sensors[i].merge(newsensor, inplace=True)

    return [s for s in sensors if not s.data.empty]
