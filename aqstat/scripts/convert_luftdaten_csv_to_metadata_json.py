# -*- coding: utf-8 -*-

"""This is a helper script to convert a luftdaten.info or madavi.de .csv file
into metadata.json files that are compatible with AQStat.

The output, i.e., the metadata.json format is this one:

    aqstat\doc\examples\metadata.json

Note that luftdaten.info (archive.sensor.community) files are separated
according to sensors, so multiple files belong to one measurement (typically
one for particle matter and another one for temperature/humidity/pressure), so
we assume (what is the usual case) that particle matter sensor ID is exactly
temperature/humidity sensor ID -1

On the other hand, madavi.de files contain all sensor data together under one
device ID, but they do NOT contain geolocation and sensor IDs.

"""

import click
from pandas import read_csv
import json
import os

from aqstat.metadata import AQMetaData, SensorInfo, GPSCoordinate, ContactInfo
from aqstat.parse import parse_metadata_from_filename, parse_madavi_csv, \
    parse_sensorcommunity_csv


@click.command()
@click.argument("inputfile", type=click.Path(exists=True))
@click.argument("outputdir", type=click.Path(exists=True), required=False)
def main(inputfile="", outputdir=""):
    """Parse .csv INPUTFILE and convert to .json in OUTPUTDIR. if OUTPUTDIR
    is not defined, the path of INPUTFILE will be used as output.

    """
    outputdir = outputdir or os.path.split(os.path.abspath(inputfile))[0]

    chip_id, sensor_id, sensor_type, date = parse_metadata_from_filename(inputfile)
    if sensor_id:
        data = parse_sensorcommunity_csv(inputfile, sensor_type)
        lat = data["lat"][0]
        lon = data["lon"][0]
        if sensor_type == "dht22":
            sensors = {
                "pm10": SensorInfo("pm10", None, sensor_id - 1),
                "pm2_5": SensorInfo("pm2_5", None, sensor_id - 1),
                "temperature": SensorInfo("temperature", sensor_type, sensor_id),
                "humidity": SensorInfo("humidity", sensor_type, sensor_id)
            }
        elif sensor_type == "bme280":
            sensors = {
                "pm10": SensorInfo("pm10", None, sensor_id - 1),
                "pm2_5": SensorInfo("pm2_5", None, sensor_id - 1),
                "temperature": SensorInfo("temperature", sensor_type, sensor_id),
                "humidity": SensorInfo("humidity", sensor_type, sensor_id),
                "pressure": SensorInfo("pressure", sensor_type, sensor_id)
            }
        elif sensor_type == "sds011":
            sensors = {
                "pm10": SensorInfo("pm10", sensor_type, sensor_id ),
                "pm2_5": SensorInfo("pm2_5", sensor_type, sensor_id),
                "temperature": SensorInfo("temperature", None, sensor_id + 1),
                "humidity": SensorInfo("humidity", None, sensor_id + 1)
            }
        else:
            raise ValueError("Sensor type '{}' not supported.".format(sensor_type))
    elif chip_id:
        data = parse_madavi_csv(inputfile)
        lat = None
        lon = None
        sensors = {
            "pm10": SensorInfo("pm10", None, None),
            "pm2_5": SensorInfo("pm2_5", None, None),
            "temperature": SensorInfo("temperature", None, None),
            "humidity": SensorInfo("humidity", None, None)
        }
    else:
        raise ValueError("Either chip_id or sensor_id should be valid.")

    sensor_name = "{}-{}".format(chip_id, sensor_id)
    amsl=0 # TODO: get from Google Maps API
    agl=0

    # create metadata object
    metadata = AQMetaData(
        name=sensor_name,
        chip_id=chip_id,
        sensors = sensors,
        location=GPSCoordinate(lat, lon, amsl, agl),
    )
    # save to file
    outfile = os.path.join(outputdir, sensor_name + ".json")
    print("writing", outfile)
    with open(outfile, 'w', encoding='utf8') as f:
        r = json.dumps(metadata.as_dict(), indent=4, ensure_ascii=False)
        f.write(r)

if __name__ == "__main__":
    main()
