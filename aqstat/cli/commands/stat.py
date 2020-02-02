"""Implementation of the 'stat' command for AQstat."""

import click
from click_option_group import optgroup
from itertools import combinations
from pandas import DataFrame

from aqstat.parse import parse_and_setup_sensors
from aqstat.stat import time_delay_correlation
from aqstat.utils import print_title



@click.command()
@click.argument("inputdir", type=click.Path(exists=True))

@optgroup.group("Input data filters", help="Use these options to create spatial, temporal or ID-based filters on the data to be analyzed")
@optgroup.option("-i", "--chip-ids", metavar="ID1,ID2,..", default="", help="comma separated list of chip ids to analyze.")
@optgroup.option("-n", "--names", metavar="NAME1,NAME2,..", default="", help="comma separated list of sensor names to analyze (partial matches accepted)")
@optgroup.option("-x", "--exclude-names", metavar="NAME1,NAME2,..", default="", help="comma separated list of sensor names NOT to analyze (partial matches accepted)")
@optgroup.option("--geo-center", metavar="LAT,LON|NAME", default="", help="Define comma separated latitude and longitude in [deg] to specify center of geographical area to be used in plots, or, alternatively, define center with exact sensor name that has geolocation metadata")
@optgroup.option("--geo-radius", type=float, help="Define radius of geographical area to be used in the analysis in [m]")
@optgroup.option("--date-start", type=click.DateTime(formats=["%Y-%m-%d"]), help="first date to include in the analysis")
@optgroup.option("--date-end", type=click.DateTime(formats=["%Y-%m-%d"]), help="last date to include in the analysis")

def stat(inputdir, chip_ids="", names="", exclude_names="",
    geo_center="", geo_radius=None, date_start=None, date_end=None
):
    """Analyze AQ data in various ways from all .csv files in the directory tree
    under INPUTDIR

    All sensor data will be used under INPUTDIR by default, unless ID or NAME
    or geolocation based filters are given explicitely to specify sensors to use.

    """

    # prepare all sensor data to use
    sensors = parse_and_setup_sensors(inputdir, chip_ids=chip_ids,
        names=names, exclude_names=exclude_names,
        geo_center=geo_center, geo_radius=geo_radius,
        date_start=date_start, date_end=date_end
    )


    print_title("main frequencies")
    result = DataFrame(columns="min max mean median".split())
    result.index.name = "name"
    for sensor in sensors:
        df = sensor.data.index.to_series().diff()
        result.loc[sensor.name] = [df.min(), df.max(), df.mean(), df.median()]
    print(result)


    print_title("polluted days")
    result = DataFrame(columns="days PM10_avg PM2.5_avg temperature_avg"
        " humidity_avg PM10>50 PM10>75 PM10>100 PM2.5>25 PM2.5>50".split())
    result.index.name = "name"
    for sensor in sensors:
        daily_data = sensor.data.resample('d').mean()
        result.loc[sensor.name] = [
            len(daily_data),
            sensor.data.pm10.mean(),
            sensor.data.pm2_5.mean(),
            sensor.data.temperature.mean(),
            sensor.data.humidity.mean(),
            daily_data.pm10[daily_data.pm10 > 50].count(),
            daily_data.pm10[daily_data.pm10 > 75].count(),
            daily_data.pm10[daily_data.pm10 > 100].count(),
            daily_data.pm2_5[daily_data.pm2_5 > 25].count(),
            daily_data.pm2_5[daily_data.pm2_5 > 50].count(),
        ]
    result = result.astype({"days": int, "PM10>50": int, "PM10>75": int,
        "PM10>100": int, "PM2.5>25": int, "PM2.5>50": int
    })
    result.sort_values("PM10_avg", inplace=True, ascending=False)
    print(result)


    # # print correlation between datasets
    # print()
    # for a, b in combinations(sensors, 2):
    #     print()
    #     print("Correlations between {} and {}".format(
    #         a.name, b.name)
    #     )
    #     print(a.corrwith(b, tolerance=60))
