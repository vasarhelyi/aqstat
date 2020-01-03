"""Parsing functions for AQData classes."""

import json
import logging
import os
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
    tokens = os.path.basename(filename).split("-")
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

def parse_metadata_json(filename):
    """Read AQ metadata from a .json file.

    Parameters:
        filename (path): the file to parse. Format of the file is speicifed in
        aqstat\doc\examples\metadata.json

    Return:
        dictionary containing sensor metadata.

    """
    with open(filename, "r") as f:
        metadata = json.load(f)

    return metadata

def parse_sensors_from_path(inputdir, sensor_ids=None, date_start=None,
    date_end=None):
    """Parse all sensor data in the given period and all metadata from inputdir.

    Parameters:
        inputdir (Path): the path where sensor data and metadata is found,
            organized in directories according to sensor id. All .csv are
            treated as sensor data, all .json are treated as metadata.
        sensor_ids (list): list of sensor_ids to be parsed.
            If None or empty, use all sensor ids found.
        date_start (datetime): starting date limit or None if not used
        date_end (datetime): ending date limit or None if not used

    Return:
        list of AQData objects separated by sensor id
    """

    # import here to avoid circular imports
    from .aqdata import AQData
    from .metadata import AQMetaData
    from .utils import find_sensor_with_id

    # parse all data separated according to sensors
    sensors = []
    for filename in sorted(Path(inputdir).glob("**/*.csv")):
        # skip sensor id if needed
        if sensor_ids:
            sensor_id = parse_id_from_luftdaten_csv(filename)
            if sensor_id not in sensor_ids:
                continue
        # parse sensor file
        logging.info("Parsing {}".format(filename))
        newsensor = AQData.from_csv(filename, date_start=date_start,
            date_end=date_end
        )
        # add current sensor data to existing list
        i = find_sensor_with_id(sensors, newsensor.sensor_id)
        if i is None:
            sensors.append(AQData())
            i = -1
        sensors[i].merge(newsensor, inplace=True)

    # parse all metadata separated according to sensors
    for filename in sorted(Path(inputdir).glob("**/*.json")):
        # parse metadata file
        logging.info("Parsing {}".format(filename))
        metadata = AQMetaData.from_json(filename)
        # skip sensor id if needed
        if sensor_ids:
            if metadata.sensor_id not in sensor_ids:
                continue
        # add current metadata to existing list
        i = find_sensor_with_id(sensors, metadata.sensor_id)
        if i is not None:
            sensors[i].metadata.merge(metadata, inplace=True)

    return [s for s in sensors if not s.data.empty]

def parse_sensor_ids_from_string_or_dir(string=None, path=None):
    """Parse sensor ids from a comma separated list or from subdirectory names
    at a given path.

    Parameters:
        string (str): a comma separated list of ids
        path (Path): an existing path under which first level integer
            subdirectory names will be parsed as sensor ids

    Return:
        list of sensor ids found

    """

    # get list of sensor IDs from string
    if string:
        sensor_ids = [int(x) for x in string.split(",") if x.isdigit()]
        if not sensor_ids:
            logging.warn("No valid sensor ids could be parsed from string '{}'".format(string))
    # or from dir
    elif path:
        sensor_ids = [int(x) for x in os.listdir(path) if os.path.isdir(
            os.path.join(path, x)) and x.isdigit()
        ]
        if not sensor_ids:
            logging.warn("No valid sensor ids could be parsed from path '{}'".format(path))
    else:
        sensor_ids = []

    return sensor_ids