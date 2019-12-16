"""This is a first attempt to test-visualize some of the air quality data
coming from https://www.madavi.de/sensor/csvfiles.php?sensor=esp8266-11797099

Note: The script is mostly a "lab" test to catalyze thinking about how this whole
thing should be treated.

"""

import click
import logging
from pathlib import Path

from .aqdata import AQData
from .plot import plot_humidity, plot_multiple_pm, plot_multiple_humidity, \
    plot_multiple_temperature, plot_pm, plot_pm_ratio, plot_temperature, \
    plot_pm_vs_humidity, plot_pm_vs_temperature
from .utils import find_sensor_with_id

@click.group()
@click.option("-v", "--verbose", count=True, help="increase logging verbosity")
@click.option('--date-start', type=click.DateTime(formats=["%Y-%m-%d"]), help="first date to include in the analysis")
@click.option('--date-end', type=click.DateTime(formats=["%Y-%m-%d"]), help="last date to include in the analysis")
@click.argument("inputdir", type=click.Path(exists=True))
@click.pass_context
def main(ctx, inputdir, date_start=None, date_end=None, verbose=False):
    """Do all kinds of air quality related stuff from all .csv files in the
    directory tree within INPUTDIR."""

    # ensure that ctx.obj exists and is a dict (in case `main()` is called
    # by means other than the __main__ == "__name__" block at the bottom
    ctx.ensure_object(dict)

    # setup logging
    if verbose > 1:
        log_level = logging.DEBUG
    elif verbose > 0:
        log_level = logging.INFO
    else:
        log_level = logging.WARN
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")
    # parse all data separated according to sensors
    sensors = []
    for filename in sorted(Path(inputdir).glob("**/*.csv")):
        logging.info("Parsing {}".format(filename))
        newsensor = AQData.from_csv(filename, date_start=date_start,
            date_end=date_end
        )
        i = find_sensor_with_id(sensors, newsensor.sensor_id)
        if i is None:
            sensors.append(AQData())
            i = -1
        sensors[i].merge(newsensor, inplace=True)
    # perform calibration on sensor data
    for sensor in sensors:
        sensor.calibrate()

    # save sensors into the context
    ctx.obj['sensors'] = sensors

@main.command()
@click.option("-p", "--particle", is_flag=True, help="plot PM data")
@click.option("-h", "--humidity", is_flag=True, help="plot humidity data")
@click.option("-t", "--temperature", is_flag=True, help="plot temperature data")
@click.option("-mp", "--multiple-particle", is_flag=True, help="plot multiple PM data")
@click.option("-mh", "--multiple-humidity", is_flag=True, help="plot multiple humidity data")
@click.option("-mt", "--multiple-temperature", is_flag=True, help="plot multiple temperature data")
@click.pass_context
def plot(ctx, particle=False, humidity=False, temperature=False,
    multiple_particle=False, multiple_humidity=False, multiple_temperature=False):
    """Plot AQ data in various ways."""
    # if no specific argument is given, plot everything
    all = not (particle or humidity or temperature or
        multiple_particle or multiple_humidity or multiple_temperature)
    sensors = ctx.obj['sensors']

    # plot individual sensor data
    for sensor in sensors:
        # plot PM data
        if all or particle:
            plot_pm(sensor, maxy=None)
            plot_pm_ratio(sensor)
        # plot temperature date
        if all or temperature:
            plot_temperature(sensor)
            # plot pm vs temperature data
            plot_pm_vs_temperature(sensor)
        # plot humidity data
        if all or humidity:
            plot_humidity(sensor)
            # plot pm vs humidity data
            plot_pm_vs_humidity(sensor)

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
def test(ctx):
    """Arbitrary tests on AQ data."""

    # import some things we need only here
    from .utils import consecutive_pairs

    # get the sensor data from the context
    sensors = ctx.obj['sensors']

    # print correlation between datasets
    for a, b in consecutive_pairs(sensors):
        print(a.corrwith(b, tolerance=60))


if __name__ == '__main__':
    main(obj={})