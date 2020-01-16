"""Parsing functions for AQData classes."""

from datetime import datetime
import json
import logging
import os
from pandas import read_csv
from pathlib import Path

def parse_metadata_from_madavi_csv_filename(filename):
    """Parse chip_id and date from a raw madavi.de AQ .csv filename.

    Parameters:
        filename (path): the file to parse. Format of the file is expected to be
            the one used by the luftdaten.info project and saved by madavi.de,
            for example as the one below:
            https://www.madavi.de/sensor/csvfiles.php?sensor=esp8266-11797099

    Return:
        tuple: (chip_id, date) of possible, (None, None) otherwise

    """
    tokens = os.path.basename(os.path.splitext(filename)[0]).split("-")
    if len(tokens) == 6 and tokens[0] == "data" and tokens[1] == "esp8266":
        chip_id = int(tokens[2])
        date = datetime(year=tokens[3], month=tokens[4], day=tokens[5])
        return (chip_id, date)

    # failure
    return (None, None)

def parse_metadata_from_sensorcommunity_csv_filename(filename):
    """Parse sensor id, sensor type and date from a raw luftdaten.info AQ .csv
    filename.

    Parameters:
        filename (path): the file to parse. Format of the file is expected to be
            the one used by the luftdaten.info project and saved by
            sensor.community, for example as in the one below:
            https://archive.sensor.community/2020-01-13/

            2020-01-12_sds011_sensor_35233.csv

    Return:
        tuple: (sensor_id, sensor_type, date) if possible,
            (None, None, None) otherwise

    """
    tokens = os.path.basename(os.path.splitext(filename)[0]).split("_")
    if len(tokens) == 4 and tokens[2] == "sensor":
        date = datetime.strptime(tokens[0], "%Y-%m-%d")
        sensor_type = tokens[1]
        sensor_id = int(tokens[3])
        return (sensor_id, sensor_type, date)

    # failure
    return (None, None, None)

def parse_metadata_from_filename(filename):
    """Parse chip_id, sensor_id, sensor_type and data from filename if possible.

    Parameters:
        filename (path): the file to parse. Format of the file is expected to be
            the one used by the luftdaten.info project and saved by
            sensor.community or madavi.de, for example as in the ones below:
            https://archive.sensor.community/2020-01-13/
            https://www.madavi.de/sensor/csvfiles.php?sensor=esp8266-11797099

            2020-01-12_sds011_sensor_35233.csv
            data-esp8266-11797099-2020-01-10.csv

    Returns:
        tuple: (chip_id, sensor_id, sensor_type, date) or None for some of them.
            If file is madavi.de file, only chip_id and date will be parsed,
            if it is a sensor.community file, only sensor_id, sensor_type and
            date will be parsed.

    """
    chip_id = sensor_id = sensor_type = date = None

    chip_id, date = parse_metadata_from_madavi_csv_filename(filename)
    if chip_id is None:
        sensor_id, sensor_type, date = \
            parse_metadata_from_sensorcommunity_csv_filename(filename)

    return (chip_id, sensor_id, sensor_type, date)

def parse_madavi_csv(filename):
    """Read raw AQ data from madavi.de .csv file.

    Parameters:
        filename (path): the file to parse. Format of the file is expected to be
            the one used by the luftdaten.info project, e.g. as here:
            https://www.madavi.de/sensor/csvfiles.php?sensor=esp8266-11797099

    Return:
        pandas DataFrame object containing the data stored in the .csv file,
        indexed with timestamps (by default defined in the "Time" column).

    """
    return read_csv(filename, sep=";", parse_dates=["Time"], index_col="Time",
        infer_datetime_format=True, skipinitialspace=True
    )

def parse_sensorcommunity_csv(filename):
    """Read raw AQ data from sensor.community .csv file.

    Parameters:
        filename (path): the file to parse. Format of the file is expected to be
            the one used by the luftdaten.info project, e.g. as here:
            https://archive.sensor.community/2020-01-13/

    Return:
        pandas DataFrame object containing the data stored in the .csv file,
        indexed with timestamps (by default defined in the "timestamp" column).

    """
    return read_csv(filename, sep=";", parse_dates=["timestamp"],
        index_col="timestamp", infer_datetime_format=True,
        skipinitialspace=True
    )

def parse_sensors_from_path(inputdir, chip_ids=[], names=[],
    date_start=None, date_end=None
):
    """Parse all sensor data and metadata for the given chip_ids in the given
    period from inputdir.

    Parameters:
        inputdir (Path): the path where sensor data and metadata is found.
            All .csv are treated as sensor data,
            all .json are treated as metadata.
        chip_ids (list): list of chip_ids to be parsed.
            If empty (and names is empty, too), parse all sensors found.
        names (list): list of sensor names to be parsed (partial match accepted)
            If empty (and chip_ids is empty, too), parse all sensors found.
        date_start (datetime): starting date limit or None if not used
        date_end (datetime): ending date limit or None if not used

    Return:
        list of AQData objects separated by chip id
    """

    # import here to avoid circular imports
    from .aqdata import AQData
    from .metadata import AQMetaData
    from .utils import find_sensor_with_id

    sensors = []

    # parse all metadata separated according to sensors
    # we need to parse this first as sensor.community data is stored in
    # separate files for different sensors with the same chip id and
    # we need to know the assignment before we load data
    for filename in sorted(Path(inputdir).glob("**/*.json")):
        # parse metadata file
        logging.info("Parsing {}".format(filename))
        metadata = AQMetaData.from_json(filename)
        # add chip_id if name matches
        if names and True in [name in metadata.name for name in names]:
            if metadata.chip_id not in chip_ids:
                chip_ids.append(metadata.chip_id)
        # skip chip id if needed
        if chip_ids and metadata.chip_id not in chip_ids:
            continue
        # add new metadata to list
        i = find_sensor_with_id(sensors, chip_id=metadata.chip_id)
        if i is None:
            sensors.append(AQData(metadata=metadata))
        else:
            sensors[i].metadata.merge(metadata, inplace=True)

    # parse all data separated according to sensors
    for filename in sorted(Path(inputdir).glob("**/*.csv")):
        # first only parse metadata
        chip_id, sensor_id, sensor_type, date = parse_metadata_from_filename(filename)
        # if we have sensor_id but no chip_id, try to infer chip_id from metadata
        if chip_id is None and sensor_id is not None:
            i = find_sensor_with_id(sensors, sensor_id=sensor_id)
            if i is not None:
                chip_id = sensors[i].chip_id
        # skip file if needed
        if chip_ids and chip_id not in chip_ids:
            continue
        if date and date_start and date < date_start:
            continue
        if date and date_end and date > date_end:
            continue
        # parse sensor file
        logging.info("Parsing {}".format(filename))
        newsensor = AQData.from_csv(filename, date_start=date_start,
            date_end=date_end
        )
        # add current sensor data to existing list
        i = find_sensor_with_id(sensors, chip_id=chip_id, sensor_id=sensor_id)
        if i is None:
            sensors.append(newsensor)
        else:
            sensors[i].merge(newsensor, inplace=True)

    return [s for s in sensors if not s.data.empty]

def parse_ids_from_string_or_dir(string=None, path=None):
    """Parse (sensor or chip) ids from a comma separated list or from
    subdirectory names at a given path.

    Parameters:
        string (str): a comma separated list of ids
        path (Path): an existing path under which first level integer
            subdirectory names will be parsed as ids

    Return:
        list of ids found

    """

    # get list of sensor IDs from string
    if string:
        ids = [int(x) for x in string.split(",") if x.isdigit()]
        if not ids:
            logging.warn("No valid ids could be parsed from string '{}'".format(string))
    # or from dir
    elif path:
        ids = [int(x) for x in os.listdir(path) if os.path.isdir(
            os.path.join(path, x)) and x.isdigit()
        ]
        if not ids:
            logging.warn("No valid ids could be parsed from path '{}'".format(path))
    else:
        ids = []

    return ids