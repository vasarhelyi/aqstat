"""This is a first attempt to test-visualize some of the air quality data
coming from https://www.madavi.de/sensor/csvfiles.php?sensor=esp8266-11797099

Note: The script is mostly a "lab" test to catalyze thinking about how this whole
thing should be treated.

"""

import click
import logging
import os
import re
from urllib.request import urlopen, urlretrieve

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


@main.command()
@click.argument("sensor_id", type=int)
@click.argument("outputdir", type=click.Path(exists=True))
def download(sensor_id, outputdir):
    """Download luftdaten.info .csv files for a given sensor id to outputdir."""

    # download all data
    url = r"https://www.madavi.de/sensor/csvfiles.php?sensor=esp8266-{}".format(sensor_id).replace(" ","%20")
    string = urlopen(url).read().decode('utf-8')
    print(string)
    csv_filelist = set(re.findall(r'data-esp8266-{}-....-..-..\.csv'.format(sensor_id), string))
    zip_filelist = set(re.findall(r'data-esp8266-{}-....-..\.zip'.format(sensor_id), string))
    print(csv_filelist)
    print(zip_filelist)
    for filename in csv_filelist:
        urlretrieve(os.path.join(url, filename), outputdir)
    # extract monthly .zip files
    # TODO


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