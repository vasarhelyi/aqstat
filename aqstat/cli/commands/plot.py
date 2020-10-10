"""Implementation of the 'plot' command for AQstat."""

import click
from click_option_group import optgroup
import logging

from aqstat.parse import parse_and_setup_sensors, parse_gsod_data
from aqstat.plot import plot_daily_variation, plot_daily_variation_hist, \
    plot_humidity, plot_multiple_pm, plot_multiple_humidity, \
    plot_multiple_temperature, plot_multiple_altitude, plot_pm, plot_pm_ratio, \
    plot_temperature, plot_pm_vs_environment_hist, plot_pm_vs_humidity, \
    plot_pm_vs_temperature



@click.command()
@click.argument("inputdir", type=click.Path(exists=True))

@optgroup.group("Input data", help="Use these options to define what kind of input data to use")
@optgroup.option("--gsod", type=click.Path(exists=True), help="define GSOD .csv file to use in the analysis")

@optgroup.group("Input data filters", help="Use these options to create spatial, temporal or ID-based filters on the data to be visualized")
@optgroup.option("-i", "--chip-ids", metavar="ID1,ID2,..", default="", help="comma separated list of chip ids to plot.")
@optgroup.option("-n", "--names", metavar="NAME1,NAME2,..", default="", help="comma separated list of sensor names to plot (partial matches accepted)")
@optgroup.option("-x", "--exclude-names", metavar="NAME1,NAME2,..", default="", help="comma separated list of sensor names NOT to plot (partial matches accepted)")
@optgroup.option("--geo-center", metavar="LAT,LON|NAME", default="", help="Define comma separated latitude and longitude in [deg] to specify center of geographical area to be used in plots, or, alternatively, define center with exact sensor name that has geolocation metadata")
@optgroup.option("--geo-radius", type=float, help="Define radius of geographical area to be used in plots in [m]")
@optgroup.option("--date-start", type=click.DateTime(formats=["%Y-%m-%d"]), help="first date to include in the analysis")
@optgroup.option("--date-end", type=click.DateTime(formats=["%Y-%m-%d"]), help="last date to include in the analysis")

@optgroup.group("Plot types", help="Use these options to define what to plot")
@optgroup.option("-p", "--particle", is_flag=True, help="plot PM-related data")
@optgroup.option("-h", "--humidity", is_flag=True, help="plot humidity-related data")
@optgroup.option("-t", "--temperature", is_flag=True, help="plot temperature-related data")
@optgroup.option("-mp", "--multiple-particle", is_flag=True, help="plot PM-related data for multiple sensors together")
@optgroup.option("-mh", "--multiple-humidity", is_flag=True, help="plot humidity-related data for multiple sensors together")
@optgroup.option("-mt", "--multiple-temperature", is_flag=True, help="plot temperature-related data for multiple sensors together")
@optgroup.option("-ma", "--multiple-altitude", is_flag=True, help="plot altitude-related data for multiple sensors together")

def plot(inputdir, gsod="", chip_ids="",
    names="", exclude_names="",
    geo_center="", geo_radius=None,
    date_start=None, date_end=None,
    particle=False, humidity=False, temperature=False,
    multiple_particle=False, multiple_humidity=False,
    multiple_temperature=False, multiple_altitude=False,
):
    """Plot AQ data in various ways from all .csv files in the directory tree
    under INPUTDIR

    All sensor data will be plotted under INPUTDIR by default, unless ID or NAME
    or geolocation based filters are given explicitely to specify sensors to use.

    """
    # prepare all sensor data to use
    sensors = parse_and_setup_sensors(inputdir, chip_ids=chip_ids,
        names=names, exclude_names=exclude_names,
        geo_center=geo_center, geo_radius=geo_radius,
        date_start=date_start, date_end=date_end
    )

    # parse gsod data if given
    if gsod:
        gsod = parse_gsod_data(gsod)
    else:
        gsod = None

    # if no specific argument is given, plot everything
    all = not (particle or humidity or temperature or
        multiple_particle or multiple_humidity or multiple_temperature or
        multiple_altitude)

    # plot individual sensor data
    for sensor in sensors:
        # plot PM data
        if all or particle:
            if sensor.data.pm10.count() or sensor.data.pm2_5.count():
                plot_pm(sensor, gsod)
                plot_pm(sensor, gsod, window="1h")
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
            plot_multiple_pm(sensors, "pm10")
            plot_multiple_pm(sensors, "pm10", window="1h")
            plot_multiple_pm(sensors, "pm2_5")
            plot_multiple_pm(sensors, "pm2_5", window="1h")
            plot_multiple_pm(sensors, "pm2_5_calib")
            plot_multiple_pm(sensors, "pm2_5_calib", window="1h")
        if all or multiple_humidity:
            plot_multiple_humidity(sensors)
        if all or multiple_temperature:
            plot_multiple_temperature(sensors)
        if all or multiple_altitude:
            plot_multiple_altitude(sensors)
