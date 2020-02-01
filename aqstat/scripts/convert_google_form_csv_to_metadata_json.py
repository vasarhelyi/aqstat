# -*- coding: utf-8 -*-

"""This is a very arbitrary script to convert the metadata collected in a
google form to metadata.json files that are compatible with AQStat.

The input, i.e., the original google form is this one:

    https://docs.google.com/forms/d/17YaXP9Q1TQX7iOQv-7YJf9eukh-b-RuS7Am17adpbLY/edit

The output, i.e., the metadata.json format is this one:

    aqstat\doc\examples\metadata.json

"""

import click
from pandas import read_csv
import json
import os

from aqstat.metadata import AQMetaData, SensorInfo, GPSCoordinate, ContactInfo

@click.command()
@click.argument("inputfile", type=click.Path(exists=True))
@click.argument("outputdir", type=click.Path(exists=True), required=False)
def main(inputfile="", outputdir=""):
    """Parse .csv INPUTFILE and convert to .json in OUTPUTDIR. if OUTPUTDIR
    is not defined, the path of INPUTFILE will be used as output.

    """
    outputdir = outputdir or os.path.split(os.path.abspath(inputfile))[0]
    data = read_csv(inputfile)
    for i, d in data.iterrows():
        # parse fields (I know it is very arbitrary, sorry)
        sensor_name = "-".join([d["Város"],d["Utca"]]).replace(" ", "-")
        name = d["Név"]
        email = d["E-mail"]
        phone = d["Telefonszám"]
        chip_id=int(d["device ID"]) if d["device ID"] == d["device ID"] else None
        description=d["Az érzékelő elhelyezése"]
        lat, lon = [float(x.strip()) for x in d["Az érzékelő helyének koordinátái"].split(",")]
        amsl = float(d["AMSL"])
        agl = float(d["Az érzékelő magassága a földtől (AGL)"])
        sensor_id = int(d["sensor ID"]) if d["sensor ID"] == d["sensor ID"] else None
        sensors = {
            "pm10": SensorInfo("pm10", d["Szállópor érzékelő típusa"], sensor_id),
            "pm2_5": SensorInfo("pm2_5", d["Szállópor érzékelő típusa"], sensor_id),
            "temperature": SensorInfo("temperature", d["Hőmérséklet és páratartalom érzékelő típusa"], sensor_id + 1),
            "humidity": SensorInfo("humidity", d["Hőmérséklet és páratartalom érzékelő típusa"], sensor_id + 1)
        }
        if d["Hőmérséklet és páratartalom érzékelő típusa"].lower() == "bme280":
            sensors["pressure"] = SensorInfo("pressure", d["Hőmérséklet és páratartalom érzékelő típusa"], sensor_id + 1)
        # create metadata object
        metadata = AQMetaData(
            name=sensor_name,
            chip_id=chip_id,
            sensors = sensors,
            description=description,
            location=GPSCoordinate(lat, lon, amsl, agl),
            owner=ContactInfo(name, email, phone)
        )
        # save to file
        outfile = os.path.join(outputdir, "{}-{}-{}.json".format(
            metadata.name,
            metadata.chip_id,
            metadata.sensors["pm10"].sensor_id,
        ))
        print("writing", outfile)
        with open(outfile, 'w', encoding='utf8') as f:
            r = json.dumps(metadata.as_dict(), indent=4, ensure_ascii=False)
            f.write(r)

if __name__ == "__main__":
    main()
