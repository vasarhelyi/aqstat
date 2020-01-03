"""Implementation of the 'plot' command for AQstat."""

import click
import logging

from aqstat.plot import plot_daily_variation, plot_humidity, plot_multiple_pm, \
    plot_multiple_humidity, plot_multiple_temperature, plot_pm, plot_pm_ratio, \
    plot_temperature, plot_pm_vs_environment_hist, plot_pm_vs_humidity, \
    plot_pm_vs_temperature
from aqstat.parse import parse_sensor_ids_from_string_or_dir, \
    parse_sensors_from_path



@click.command()
@click.argument("inputdir", type=click.Path(exists=True))
@click.argument("sensor-ids", required=False)
@click.option('--date-start', type=click.DateTime(formats=["%Y-%m-%d"]), help="first date to include in the analysis")
@click.option('--date-end', type=click.DateTime(formats=["%Y-%m-%d"]), help="last date to include in the analysis")
@click.option("-p", "--particle", is_flag=True, help="plot PM data")
@click.option("-h", "--humidity", is_flag=True, help="plot humidity data")
@click.option("-t", "--temperature", is_flag=True, help="plot temperature data")
@click.option("-mp", "--multiple-particle", is_flag=True, help="plot multiple PM data")
@click.option("-mh", "--multiple-humidity", is_flag=True, help="plot multiple humidity data")
@click.option("-mt", "--multiple-temperature", is_flag=True, help="plot multiple temperature data")
def plot(inputdir, sensor_ids=None, date_start=None, date_end=None, particle=False,
    humidity=False, temperature=False, multiple_particle=False,
    multiple_humidity=False, multiple_temperature=False):
    """Plot AQ data in various ways from all .csv files in the directory tree
    under INPUTDIR, for the given SENSOR_IDS.

    SENSOR_IDS should be a comma separated list of integers.
    If no SENSOR_IDS are given, all data will be used under INPUTDIR.

    """

    # get list of sensor IDs from option
    sensor_ids = parse_sensor_ids_from_string_or_dir(string=sensor_ids)
    # parse sensors from files
    sensors = parse_sensors_from_path(inputdir, sensor_ids, date_start, date_end)
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
                plot_pm(sensor, maxy=300)
                plot_pm_ratio(sensor)
                plot_daily_variation(sensor, ["pm10", "pm2_5", "pm2_5_calib"])
            else:
                logging.warn("No valid PM data for sensor id {}".format(sensor.sensor_id))
        # plot temperature date
        if all or temperature:
            if sensor.data.temperature.count():
                plot_temperature(sensor)
                plot_pm_vs_temperature(sensor)
                plot_pm_vs_environment_hist(sensor, xtype="temperature")
                plot_daily_variation(sensor, ["temperature"])
            else:
                logging.warn("No valid temperature data for sensor id {}".format(sensor.sensor_id))
        # plot humidity data
        if all or humidity:
            if sensor.data.humidity.count():
                plot_humidity(sensor)
                plot_pm_vs_humidity(sensor)
                plot_pm_vs_environment_hist(sensor, xtype="humidity")
                plot_daily_variation(sensor, ["humidity"])
            else:
                logging.warn("No valid humidity data for sensor id {}".format(sensor.sensor_id))

    # plot multiple sensor data
    if len(sensors) > 1:
        if all or multiple_particle:
            plot_multiple_pm(sensors, pm10=True, pm2_5=True)
        if all or multiple_humidity:
            plot_multiple_humidity(sensors)
        if all or multiple_temperature:
            plot_multiple_temperature(sensors)
            pass
