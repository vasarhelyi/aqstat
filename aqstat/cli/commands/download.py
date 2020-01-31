"""Implementation of the 'download' command for AQstat."""

import click
import datetime
import logging
import os
import re
import requests
import zipfile

from aqstat.parse import create_id_dirs_from_json, \
    parse_ids_from_string_or_dir, parse_sensors_from_path
from aqstat.utils import last_day_of_month

def download_madavi(outputdir, chip_ids, date_start, date_end):
    """Download files from madavi.de/sensor.

    Parameters:
        outputdir (Path): path where files will be saved
        chip_ids (list[int]): list of chip ids to download
        date_start (datetime.date): start time of data to download
        date_end (datetime.date): end time of data to download

    """

    logging.info("TODO: date_start and date_end not implemented yet.")

    # define download source
    baseurl = r"https://www.madavi.de/sensor/"

    # download
    for chip_id in chip_ids:
        # get list of files to download
        logging.info("Requesting list of files to download for chip id {}".format(chip_id))
        url = r"{}csvfiles.php?sensor=esp8266-{}".format(baseurl, chip_id)
        html_string = requests.get(url).text
        filelist = sorted(re.findall(
            r"href='(data_csv/.*/data-esp8266-[0-9]{0,12}-[0-9\-]{7,10}\.(?:zip|csv))'",
            html_string
        ))
        # prepare output directory
        outdir = os.path.join(outputdir, str(chip_id))
        os.makedirs(outdir, exist_ok=True)
        # download files (only if size differs from local)
        for filename in filelist:
            url = os.path.join(baseurl, filename)
            outfile = os.path.join(outdir, os.path.split(filename)[1])
            r = requests.get(url, stream=True)
            # skip non-existing or not OK files
            if r.status_code != 200:
                continue
            # TODO: compare current and cached ETag values instead of size
            #       hint: https://pypi.org/project/requests-etag-cache/
            if os.path.exists(outfile):
                remote_size = int(r.headers["Content-Length"])
                local_size = int(os.stat(outfile).st_size)
                if local_size == remote_size:
                    logging.info("Skipping {}".format(filename))
                    continue
                else:
                    logging.info("Updating {}".format(filename))
            else:
                logging.info("Downloading {}".format(filename))
            with open(outfile, "wb") as f:
                for chunk in r:
                    f.write(chunk)
            if outfile.endswith(".zip"):
                logging.info("Extracting {}".format(filename))
                with zipfile.ZipFile(outfile, 'r') as zip_ref:
                    zip_ref.extractall(outdir)

def download_sensorcommunity(outputdir, sensor_ids, date_start, date_end,
    sensor_types=["sds011", "dht22", "bme280"]
):
    """Download files from archive.sensor.community.

    Parameters:
        outputdir (Path): path where files will be saved
        sensor_ids (list[int]): list of sensor ids to download
        date_start (datetime.date): start time of data to download
        date_end (datetime.date): end time of data to download
        sensor_types (list[str]): list of sensor types to search for
    """

    # define download source
    baseurl = r"https://archive.sensor.community/"

    # prepare list of files to download
    date = date_start
    delta = datetime.timedelta(days=1)
    urllist = []
    while date <= date_end:
        datestring = date.strftime("%Y-%m-%d")
        for sensor_id in sensor_ids:
            # note that many non existing ones are also added here, they will be
            # skipped later on requests.get's wrong status_code, but this is the
            # most convenient way to find out which sensor id belongs to what
            # sensor type
            for sensor_type in sensor_types:
                urllist.append(r"{}/{}/{}_{}_sensor_{}.csv".format(baseurl,
                    datestring, datestring, sensor_type.lower(), sensor_id))
        date += delta
    # download files (only if size differs from local)
    for url in urllist:
        filename = os.path.split(url)[1]
        sensor_id = os.path.splitext(filename)[0].split("_")[-1]
        outdir = os.path.join(outputdir, sensor_id)
        os.makedirs(outdir, exist_ok=True)
        outfile = os.path.join(outdir, filename)
        r = requests.get(url, stream=True)
        # skip non-existing or not OK files
        if r.status_code != 200:
            continue
        # TODO: compare current and cached ETag values instead of size
        #       hint: https://pypi.org/project/requests-etag-cache/
        if os.path.exists(outfile):
            remote_size = int(r.headers["Content-Length"])
            local_size = int(os.stat(outfile).st_size)
            if local_size == remote_size:
                logging.info("Skipping {}".format(filename))
                continue
            else:
                logging.info("Updating {}".format(filename))
        else:
            logging.info("Downloading {}".format(filename))
        with open(outfile, "wb") as f:
            for chunk in r:
                f.write(chunk)

@click.command()
@click.argument("outputdir", type=click.Path(exists=True))
@click.argument("ids", required=False)
@click.option('--date-start', type=click.DateTime(formats=["%Y-%m-%d"]), help="first date to include in the download. Default is beginning of this or date-end's month.")
@click.option('--date-end', type=click.DateTime(formats=["%Y-%m-%d"]), help="last date to include in the download. Default is now or end of date-start's month.")
@click.option("--use-madavi", is_flag=True, help="use madavi.de as download source instead of the default archive.sensor.community")
@click.option("--use-json", is_flag=True, help="parse all .json files found under OUTPUTDIR and create directories for all sensor IDs before download")
def download(outputdir, ids="", date_start=None, date_end=None,
    use_madavi=False, use_json=False):
    """Download luftdaten.info .csv files for the given IDS to OUTPUTDIR.

    Data is assumed to be and will be organized into subdirectories named
    after IDS.

    IDS should be a comma separated list of integers, corresponding to
    sensor_ids or chip_ids, depending on whether data is downloaded from
    archive.sensor.community or madavi.de, correspondingly.

    If no IDS are given, they will be inferred from directory names
    under OUTPUTDIR.

    DATE_START and DATE_END define the date range to look for.
    Default is this month if nothing specified, the given month if only half is
    specified.

    """
    # create directories first if needed
    if use_json:
        create_id_dirs_from_json(outputdir, sensor_id=not use_madavi,
            chip_id=use_madavi
        )
    # get list of chip IDs from option or from subdirectory names
    ids = parse_ids_from_string_or_dir(ids, outputdir)
    if not ids:
        logging.warn("No valid IDs are provided. Exiting.")
        return
    # get date_start and date_end properly
    if date_start:
        date_start = date_start.date()
    if date_end:
        date_end = date_end.date()
    if date_start is None:
        if date_end is None:
            date_end = datetime.date.today()
        date_start = date_end.replace(day=1)
    elif date_end is None:
        date_end = min(datetime.date.today(), last_day_of_month(date_start))
    if date_start > date_end:
        logging.warn("date-start should be before date-end. Exiting.")
        return

    if use_madavi:
        download_madavi(outputdir, chip_ids=ids,
            date_start=date_start, date_end=date_end
        )
    else:
        download_sensorcommunity(outputdir, sensor_ids=ids,
            date_start=date_start, date_end=date_end
        )
