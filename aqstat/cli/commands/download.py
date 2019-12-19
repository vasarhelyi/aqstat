"""Implementation of the 'download' command for AQstat."""

import click
from datetime import datetime
import logging
import os
import re
import requests
import zipfile

# TODO: text wrapping is bad in click for --help, docsctring is ugly
@click.command()
@click.argument("outputdir", type=click.Path(exists=True))
@click.argument("sensor-ids", required=False)
def download(outputdir, sensor_ids=""):
    """Download luftdaten.info .csv files for a given sensor id to outputdir.

    Parameters:
        outputdir (Path): the path where data is to be downloaded, organized
            into subdirectories named after sensor IDs.
        sensor_ids (str): comma separated list of sensor IDs used for download.
            If empty, IDs will be inferred from directory names under 'outputdir'

    """
    # define download source
    baseurl = r"https://www.madavi.de/sensor/"

    # get list of sensor IDs from option
    if sensor_ids:
        sensor_ids = [int(x) for x in sensor_ids.split(",") if x.isdigit()]
    # or from subdirectory names
    else:
        sensor_ids = [int(x) for x in os.listdir(outputdir) if os.path.isdir(
            os.path.join(outputdir, x)) and x.isdigit()
        ]
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
        # remove today from files
        # TODO: this will not be needed when rsync will be used, but how?
        #filelist = [x for x in filelist if str(datetime.today().date()) not in x]
        # prepare output directory
        outdir = os.path.join(outputdir, str(sensor_id))
        os.makedirs(outdir, exist_ok=True)
        # download files
        for filename in filelist:
            outfile = os.path.join(outdir, os.path.split(filename)[1])
            if os.path.exists(outfile):
                continue
            with requests.get(os.path.join(baseurl, filename)) as r, open(outfile, "wb") as f:
                logging.info("Downloading {}".format(filename))
                f.write(r.content)
            if outfile.endswith(".zip"):
                logging.info("Extracting {}".format(filename))
                with zipfile.ZipFile(outfile, 'r') as zip_ref:
                    zip_ref.extractall(outdir)
