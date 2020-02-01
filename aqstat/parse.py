"""Parsing functions for AQData classes."""

from datetime import datetime
import json
import logging
import os
from pandas import read_csv
from pathlib import Path

from .utils import find_sensor_with_id

def create_id_dirs_from_json(outputdir, sensor_id=False, chip_id=False):
    """Create subdirectories under outputdir for all IDs found in .json
    metadata files under outputdir.

    """
    sensors = parse_sensors_from_path(outputdir, chip_ids=[], names=[],
        only_metadata=True
    )
    for sensor in sensors:
        if sensor_id:
            for sid in sensor.sensor_ids:
                os.makedirs(os.path.join(outputdir, str(sid)),
                    exist_ok=True
                )
        if chip_id:
            os.makedirs(os.path.join(outputdir, str(sensor.chip_id)),
                exist_ok=True
            )

def parse_gsod_data(filename):
    """Parse Global Summary of the Day (GSOD) data from a comma separated
    .txt file.

    Source: https://www7.ncdc.noaa.gov/CDO/cdoselect.cmd?datasetabbv=GSOD&countryabbv=&georegionabbv=

    Format Specification: https://www7.ncdc.noaa.gov/CDO/GSOD_DESC.txt

    Parameters:
        filename(Path): the .txt/.csv file to parse

    Return:
        pandas DataFrame containing GSOD meteorological data converted into
        SI units (Fahrenheit -> Celsius, miles -> m, knots -> m/s)

    """
    # parse .csv
    data = read_csv(filename, sep=",", parse_dates=["YEARMODA"],
        index_col="YEARMODA", infer_datetime_format=True,
        skipinitialspace=True
    )
    # remove space from end of column names (reserved for flag indent)
    data.columns = [x.strip() for x in data.columns]
    # remove '*' flag from MAX and MIN
    for key in ["MAX", "MIN"]:
        data[key] = data[key].map(lambda x: float(x.strip("*")))
    # remove missing data
    for key in ["WBAN"]:
        data[key].replace({99999: None}, inplace=True)
    for key in ["TEMP", "DEWP", "SLP", "STP", "MAX", "MIN"]:
        data[key].replace({9999.9: None}, inplace=True)
    for key in ["VISIB", "WDSP", "MXSPD", "GUST", "SNDP"]:
        data[key].replace({999.9: None}, inplace=True)
    for key in ["PRCP"]:
        data[key].replace({99.99: None}, inplace=True)
    # convert Fahrenheit to Celsius
    for key in ["TEMP", "DEWP", "MAX", "MIN"]:
        data[key] = (data[key] - 32) / 1.8
    # convert miles to meters
    for key in ["VISIB"]:
        data[key] = data[key] * 1609.344
    # convert knots to m/s
    for key in ["WDSP", "MXSPD", "GUST"]:
        data[key] = data[key] * 0.51444444444444

    return data

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

def parse_sensors_from_path(inputdir, chip_ids=[], names=[], exclude_names=[],
    geo_center=None, geo_radius=None,
    date_start=None, date_end=None,
    only_metadata=False
):
    """Parse all sensor data and metadata for the given chip_ids in the given
    period from inputdir.

    Parameters:
        inputdir (Path): the path where sensor data and metadata is found.
            All .csv are treated as sensor data,
            all .json are treated as metadata.
        chip_ids (list): list of chip_ids to be parsed. If empty (and names
            and exclude_names is empty, too), parse all sensors found.
        names (list): list of sensor names to be parsed (partial match accepted)
            If empty (and chip_ids and exclude_names is empty, too), parse all
            sensors found.
        exclude_names (list): list of sensor names NOT to be parsed (partial
            match accepted) If empty (and chip_ids and names is empty, too),
            parse all sensors found.
        geo_center (float, float): latitude and longitude in [degrees], defining
            the center of the geographical filter to use on input devices.
            Should be used together with geo_radius.
        geo_radius (float): radius of the geographical filter to use on input
            devices in [m]. Should be used together with geo_center.
        date_start (datetime): starting date limit or None if not used
        date_end (datetime): ending date limit or None if not used
        only_metadata (bool): should we parse only metadata or data as well?

    Return:
        list of AQData objects separated by chip id. If only_metadata is used,
        the returned objects will contain no data. If it is not used, only
        those sensors will be returned that contain actual data.

    """

    # import here to avoid circular imports
    from .aqdata import AQData
    from .metadata import AQMetaData
    from .utils import latlon_distance

    sensors = []

    # parse all metadata separated according to sensors
    # we need to parse this first as sensor.community data is stored in
    # separate files for different sensors with the same chip id and
    # we need to know the assignment before we load data
    for filename in sorted(Path(inputdir).glob("**/*.json")):
        # parse metadata file
        logging.info("Parsing {}".format(filename))
        metadata = AQMetaData.from_json(filename)
        # skip if exclude_names matches
        if exclude_names and True in [name in metadata.name for name in exclude_names]:
            continue
        # skip if outside of defined geographical area
        if geo_center and geo_radius and latlon_distance(
                geo_center[0], geo_center[1],
                metadata.location.lat, metadata.location.lon) > geo_radius:
            continue
        # skip if names are defined and there is no match
        if names and True not in [name in metadata.name for name in names]:
            continue
        # skip if chip id list is defined and we are not on it
        if chip_ids and metadata.chip_id not in chip_ids:
            continue
        # add new metadata to list
        i = find_sensor_with_id(sensors, chip_id=metadata.chip_id)
        if i is None:
            sensors.append(AQData(metadata=metadata))
        else:
            sensors[i].metadata.merge(metadata, inplace=True)

    # if only metadata is needed or we found nothing, we quit here
    if (not sensors) or only_metadata:
        return sensors

    # update chip_ids with all sensors that we need to have a full list
    # note that this also means that we assume that metadata exists for all
    # chip ids
    chip_ids = [sensor.chip_id for sensor in sensors]

    # parse all data separated according to sensors
    for filename in sorted(Path(inputdir).glob("**/*.csv")):
        # first only parse metadata
        chip_id, sensor_id, sensor_type, date = parse_metadata_from_filename(filename)
        # if we have sensor_id but no chip_id, try to infer chip_id from metadata
        if chip_id is None and sensor_id is not None:
            i = find_sensor_with_id(sensors, sensor_id=sensor_id)
            if i is not None:
                chip_id = sensors[i].chip_id
        # skip file if it does not match
        if chip_id not in chip_ids:
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
        if i is not None:
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