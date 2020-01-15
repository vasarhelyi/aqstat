"""Implementation of the 'plot' command for AQstat."""

import click
import logging

from aqstat.plot import plot_daily_variation, plot_daily_variation_hist, \
    plot_humidity, plot_multiple_pm, plot_multiple_humidity, \
    plot_multiple_temperature, plot_pm, plot_pm_ratio, \
    plot_temperature, plot_pm_vs_environment_hist, plot_pm_vs_humidity, \
    plot_pm_vs_temperature
from aqstat.parse import parse_ids_from_string_or_dir, \
    parse_sensors_from_path



@click.command()
@click.argument("inputdir", type=click.Path(exists=True))
@click.argument("ids", required=False)
@click.option('--date-start', type=click.DateTime(formats=["%Y-%m-%d"]), help="first date to include in the analysis")
@click.option('--date-end', type=click.DateTime(formats=["%Y-%m-%d"]), help="last date to include in the analysis")
@click.option("-p", "--particle", is_flag=True, help="plot PM data")
@click.option("-h", "--humidity", is_flag=True, help="plot humidity data")
@click.option("-t", "--temperature", is_flag=True, help="plot temperature data")
@click.option("-mp", "--multiple-particle", is_flag=True, help="plot multiple PM data")
@click.option("-mh", "--multiple-humidity", is_flag=True, help="plot multiple humidity data")
@click.option("-mt", "--multiple-temperature", is_flag=True, help="plot multiple temperature data")
def plot(inputdir, ids=None, date_start=None, date_end=None, particle=False,
    humidity=False, temperature=False, multiple_particle=False,
    multiple_humidity=False, multiple_temperature=False):
    """Plot AQ data in various ways from all .csv files in the directory tree
    under INPUTDIR, for the given IDS (sensor id or chip id).

    IDS should be a comma separated list of integers.
    If no IDS are given, all data will be used under INPUTDIR.

    """

    # get list of sensor IDs from option
    ids = parse_ids_from_string_or_dir(string=ids)
    # parse sensors from files
    # TODO: have option to specify sensor ids as well...
    sensors = parse_sensors_from_path(inputdir, chip_ids=ids,
        date_start=date_start, date_end=date_end)
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
            if sensor.data.pm10.count() or sensor.data.pm2_5.count():
                plot_pm(sensor)
                plot_pm_ratio(sensor)
                plot_daily_variation(sensor, ["pm10", "pm2_5", "pm2_5_calib"])
                plot_daily_variation_hist(sensor, keys=["pm10"], mins=[75])
                plot_daily_variation_hist(sensor, keys=["pm2_5"], mins=[50])
            else:
                logging.warn("No valid PM data for chip id {}, sensor id {}".format(
                    sensor.chip_id, sensor.metadata.sensors["pm10"].sensor_id))
        # plot temperature date
        if all or temperature:
            if sensor.data.temperature.count():
                plot_temperature(sensor)
                plot_daily_variation(sensor, ["temperature"])
                if sensor.data.pm10.count():
                    plot_pm_vs_temperature(sensor)
                    plot_pm_vs_environment_hist(sensor, key="temperature")
            else:
                logging.warn("No valid temperature data for chip id {}, sensor id {}".format(
                    sensor.chip_id, sensor.metadata.sensors["temperature"].sensor_id))
        # plot humidity data
        if all or humidity:
            if sensor.data.humidity.count():
                plot_humidity(sensor)
                plot_daily_variation(sensor, ["humidity"])
                if sensor.data.pm10.count():
                    plot_pm_vs_humidity(sensor)
                    plot_pm_vs_environment_hist(sensor, key="humidity")
            else:
                logging.warn("No valid humidity data for chip id{}, sensor id {}".format(
                    sensor.chip_id, sensor.metadata.sensors["humidity"].sensor_id))


    # plot multiple sensor data
    if len(sensors) > 1:
        if all or multiple_particle:
            plot_multiple_pm(sensors, keys=["pm10"])
            plot_multiple_pm(sensors, keys=["pm2_5"])
        if all or multiple_humidity:
            plot_multiple_humidity(sensors)
        if all or multiple_temperature:
            plot_multiple_temperature(sensors)
