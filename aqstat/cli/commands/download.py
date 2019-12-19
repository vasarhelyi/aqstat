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
        # prepare output directory
        outdir = os.path.join(outputdir, str(sensor_id))
        os.makedirs(outdir, exist_ok=True)
        # download files (only if size differs from local)
        for filename in filelist:
            url = os.path.join(baseurl, filename)
            outfile = os.path.join(outdir, os.path.split(filename)[1])
            logging.info("Checking {}".format(filename))
            r = requests.get(url, stream=True)
            # TODO: compare current and cached ETag values instead of size
            #       hint: https://pypi.org/project/requests-etag-cache/
            if os.path.exists(outfile):
                remote_size = int(r.headers["Content-Length"])
                local_size = int(os.stat(outfile).st_size)
                if local_size == remote_size:
                    continue
            with open(outfile, "wb") as f:
                logging.info("Downloading {}".format(filename))
                f.write(r.content)
            if outfile.endswith(".zip"):
                logging.info("Extracting {}".format(filename))
                with zipfile.ZipFile(outfile, 'r') as zip_ref:
                    zip_ref.extractall(outdir)
        print(r.headers)