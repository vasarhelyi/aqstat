"""Implementation of the 'test' command for AQstat."""

import click
from itertools import combinations

from aqstat.parse import parse_sensor_ids_from_string_or_dir, \
    parse_sensors_from_path

@click.command()
@click.argument("inputdir", type=click.Path(exists=True))
@click.argument("sensor-ids", required=False)
@click.option('--date-start', type=click.DateTime(formats=["%Y-%m-%d"]), help="first date to include in the analysis")
@click.option('--date-end', type=click.DateTime(formats=["%Y-%m-%d"]), help="last date to include in the analysis")
def test(inputdir, sensor_ids=None, date_start=None, date_end=None):
    """Arbitrary tests on AQ data in INPUTDIR for sensors in SENSOR_IDS.

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

#     # print correlation between datasets
#     for a, b in combinations(sensors, 2):
#         print()
#         print("Correlations between sensor ids {} and {}".format(
#             a.sensor_id, b.sensor_id)
#         )
#         print(a.corrwith(b, tolerance=60))

    # print main frequencies
    for sensor in sensors:
        df = sensor.data.index.to_series().diff()
        print("sensor_id\tmin\tmax\mean\tmedian")
        print("\t".join(map(str, [sensor.sensor_id, df.min(), df.max(), df.mean(), df.median()])))

