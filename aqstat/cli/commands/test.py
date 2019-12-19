"""Implementation of the 'test' command for AQstat."""

import click
from itertools import combinations

from aqstat.parse import parse_sensors_from_path

@click.command()
@click.argument("inputdir", type=click.Path(exists=True))
@click.option('--date-start', type=click.DateTime(formats=["%Y-%m-%d"]), help="first date to include in the analysis")
@click.option('--date-end', type=click.DateTime(formats=["%Y-%m-%d"]), help="last date to include in the analysis")
def test(inputdir, date_start=None, date_end=None):
    """Arbitrary tests on AQ data."""

    # parse sensors from files
    sensors = parse_sensors_from_path(inputdir, date_start, date_end)
    # perform calibration on sensor data
    for sensor in sensors:
        sensor.calibrate()

    # print correlation between datasets
    for a, b in combinations(sensors, 2):
        print()
        print("Correlations between sensor ids {} and {}".format(
            a.sensor_id, b.sensor_id)
        )
        print(a.corrwith(b, tolerance=60))
