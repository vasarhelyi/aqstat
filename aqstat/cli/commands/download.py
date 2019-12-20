"""Implementation of the 'download' command for AQstat."""

import click
from datetime import datetime
import logging
import os
import re
import requests
import zipfile

from aqstat.parse import parse_sensor_ids_from_string_or_dir

@click.command()
@click.argument("outputdir", type=click.Path(exists=True))
@click.argument("sensor-ids", required=False)
def download(outputdir, sensor_ids=""):
    """Download luftdaten.info .csv files for the given SENSOR_IDS to OUTPUTDIR.

    Data is assumed to be and will be organized into subdirectories named
    after SENSOR_IDS.

    SENSOR_IDS should be a comma separated list of integers.
    If no SENSOR_IDS are given, they will be inferred from directory names
    under OUTPUTDIR.

    """
    # define download source
    baseurl = r"https://www.madavi.de/sensor/"
    # get list of sensor IDs from option or from subdirectory names
    sensor_ids = parse_sensor_ids_from_string_or_dir(sensor_ids, outputdir)
    if not sensor_ids:
        logging.warn("No valid sensor IDs are provided. Exiting.")
        return
    # download
    for sensor_id in sensor_ids:
        # get list of files to download
        logging.info("Requesting list of files to download for sensor id {}".format(sensor_id))
        url = r"{}csvfiles.php?sensor=esp8266-{}".format(baseurl, sensor_id)
        html_string = requests.get(url).text
        filelist = sorted(re.findall(
            r"href='(data_csv/.*/data-esp8266-[0-9]{0,12}-[0-9\-]{7,10}\.(?:zip|csv))'",
            html_string
        ))
        # prepare output directory
        outdir = os.path.join(outputdir, str(sensor_id))
        os.makedirs(outdir, exist_ok=True)
        # download files (only if not existing or today's is newer)
        for filename in filelist:
            outfile = os.path.join(outdir, os.path.split(filename)[1])
            # we skip existing older files and download today's again as it
            # might be newer since last download
            if os.path.exists(outfile) and str(datetime.today().date()) not in filename:
                continue
            url = os.path.join(baseurl, filename)
            r = requests.get(url)
            with open(outfile, "wb") as f:
                logging.info("Downloading {}".format(filename))
                f.write(r.content)
            if outfile.endswith(".zip"):
                logging.info("Extracting {}".format(filename))
                with zipfile.ZipFile(outfile, 'r') as zip_ref:
                    zip_ref.extractall(outdir)