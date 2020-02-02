"""Implementation of the 'test' command for AQstat."""

import click
from itertools import combinations
import matplotlib.pyplot as plt

from pandas.plotting import register_matplotlib_converters
from pandas import Timestamp

from aqstat.parse import parse_and_setup_sensors
from aqstat.stat import time_delay_correlation


@click.command()
@click.argument("inputdir", type=click.Path(exists=True))
@click.option("-i", "--chip-ids", default="", help="comma separated list of chip ids to plot.")
@click.option("-n", "--names", default="", help="comma separated list of sensor names to plot (partial matches accepted)")
@click.option('--date-start', type=click.DateTime(formats=["%Y-%m-%d"]), help="first date to include in the analysis")
@click.option('--date-end', type=click.DateTime(formats=["%Y-%m-%d"]), help="last date to include in the analysis")
def test(inputdir, chip_ids="", names="", date_start=None, date_end=None):
    """Arbitrary tests on AQ data in INPUTDIR for sensors in CHIP_IDS.

    CHIP_IDS should be a comma separated list of integers.
    If no CHIP_IDS are given, all data will be used under INPUTDIR.

    """
    # prepare all sensor data to use
    sensors = parse_and_setup_sensors(inputdir, chip_ids=chip_ids,
        names=names, exclude_names=None,
        geo_center=None, geo_radius=None,
        date_start=date_start, date_end=date_end
    )

    # test time delay correlation
    print()
    starttime = Timestamp("2020-01-12T12")
    endtime = Timestamp("2020-01-13T12")
    col = "pm2_5"
    dtmax = "6h"
    freq = "1m"
    window = "1h"
    for i, a in enumerate(sensors[:-1]):
        for b in sensors[i + 1:]:
            corr = time_delay_correlation(a.data[[col]], b.data[[col]],
                dtmin="-" + dtmax, dtmax=dtmax, freq=freq, window=window,
                starttime=starttime, endtime=endtime,
            )
            corr.plot()
            plt.ylim([0, 1])
            plt.title("\n".join([
                "{} - {}, {} time delay correlation".format(a.name, b.name, col),
                "period: {} - {}".format(starttime, endtime),
                "max: {:.2f} @ {}".format(corr[col].max(), corr[col].idxmax())
            ]))
            plt.savefig("{}_{}_{}_{}.png".format(a.name, b.name, col, dtmax))
