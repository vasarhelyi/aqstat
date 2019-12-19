"""This is a first attempt to test-visualize some of the air quality data
coming from https://www.madavi.de/sensor/csvfiles.php?sensor=esp8266-11797099

Note: The script is mostly a "lab" test to catalyze thinking about how this whole
thing should be treated.

"""

import click
from datetime import datetime
import logging
import os
import re
from urllib.request import urlopen, urlretrieve
import zipfile

from .parse import parse_sensors_from_path
from .plot import plot_daily_variation, plot_humidity, plot_multiple_pm, \
    plot_multiple_humidity, plot_multiple_temperature, plot_pm, plot_pm_ratio, \
    plot_temperature, plot_pm_vs_humidity, plot_pm_vs_temperature


@click.group()
@click.option("-v", "--verbose", count=True, help="increase logging verbosity")
def main(verbose=False):
    """Do all kinds of air quality related stuff."""

    # setup logging
    if verbose > 1:
        log_level = logging.DEBUG
    elif verbose > 0:
        log_level = logging.INFO
    else:
        log_level = logging.WARN
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")


# TODO: text wrapping is bad in click for --help, docsctring is ugly
@main.command()
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
        html_string = urlopen(url).read().decode('utf-8')
        filelist = sorted(re.findall(
            r"href='(data_csv/.*/data-esp8266-[0-9]{0,12}-[0-9\-]{7,10}\.(?:zip|csv))'",
            html_string
        ))
        # remove today from files
        # TODO: this will not be needed when rsync will be used, but how?
        filelist = [x for x in filelist if str(datetime.today().date()) not in x]
        # prepare output directory
        outdir = os.path.join(outputdir, str(sensor_id))
        os.makedirs(outdir, exist_ok=True)
        # download files
        for filename in filelist:
            outfile = os.path.join(outdir, os.path.split(filename)[1])
            if os.path.exists(outfile):
                continue
            logging.info("Downloading {}".format(filename))
            urlretrieve(os.path.join(baseurl, filename), outfile)
            if outfile.endswith(".zip"):
                logging.info("Extracting {}".format(filename))
                with zipfile.ZipFile(outfile, 'r') as zip_ref:
                    zip_ref.extractall(outdir)


@main.command()
@click.argument("inputdir", type=click.Path(exists=True))
@click.option('--date-start', type=click.DateTime(formats=["%Y-%m-%d"]), help="first date to include in the analysis")
@click.option('--date-end', type=click.DateTime(formats=["%Y-%m-%d"]), help="last date to include in the analysis")
@click.option("-p", "--particle", is_flag=True, help="plot PM data")
@click.option("-h", "--humidity", is_flag=True, help="plot humidity data")
@click.option("-t", "--temperature", is_flag=True, help="plot temperature data")
@click.option("-mp", "--multiple-particle", is_flag=True, help="plot multiple PM data")
@click.option("-mh", "--multiple-humidity", is_flag=True, help="plot multiple humidity data")
@click.option("-mt", "--multiple-temperature", is_flag=True, help="plot multiple temperature data")
#@click.pass_context
def plot(inputdir, date_start=None, date_end=None, particle=False,
    humidity=False, temperature=False, multiple_particle=False,
    multiple_humidity=False, multiple_temperature=False):
    """Plot AQ data in various ways from all .csv files in the
    directory tree within INPUTDIR.
    """

    # parse sensors from files
    sensors = parse_sensors_from_path(inputdir, date_start, date_end)
    # perform calibration on sensor data
    for sensor in sensors:
        sensor.calibrate()

    # if no specific argument is given, plot everything
    all = not (particle or humidity or temperature or
        multiple_particle or multiple_humidity or multiple_temperature)

    # plot individual sensor data
    for sensor in sensors:
        # plot PM data
        if all or particle:
            plot_pm(sensor, maxy=300)
            plot_pm_ratio(sensor)
            plot_daily_variation(sensor, ["pm10", "pm2_5", "pm2_5_calib"])
        # plot temperature date
        if all or temperature:
            plot_temperature(sensor)
            # plot pm vs temperature data
            plot_pm_vs_temperature(sensor)
            plot_daily_variation(sensor, ["temperature"])
        # plot humidity data
        if all or humidity:
            plot_humidity(sensor)
            # plot pm vs humidity data
            plot_pm_vs_humidity(sensor)
            plot_daily_variation(sensor, ["humidity"])

    # plot multiple sensor data
    if len(sensors) > 1:
        if all or multiple_particle:
            plot_multiple_pm(sensors, pm10=True, pm2_5=True)
        if all or multiple_humidity:
            plot_multiple_humidity(sensors)
        if all or multiple_temperature:
            plot_multiple_temperature(sensors)
            pass

@main.command()
@click.pass_context
def test():
    """Arbitrary tests on AQ data."""

    # import some things we need only here
    from .utils import consecutive_pairs

    # parse sensors from files
    sensors = parse_sensors_from_path(inputdir, date_start, date_end)
    # perform calibration on sensor data
    for sensor in sensors:
        sensor.calibrate()

    # print correlation between datasets
    for a, b in consecutive_pairs(sensors):
        print(a.corrwith(b, tolerance=60))


if __name__ == '__main__':
    main()