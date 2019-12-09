"""This is a first attempt to test-visualize some of the air quality data
coming from https://www.madavi.de/sensor/csvfiles.php?sensor=esp8266-11797099

Usage:

    __file__ inputdir

    where 'inputdir' is the place where the AQ .csv files are found.

Note: The script is mostly a "lab" test to catalyze thinking about how this whole
thing should be treated. See TODO-s below emerging through coding:

TODO:

    - how to store data in a very efficient and stable database?
    - how to sort data in a very efficient way when adding two datasets?
    - how to parse/store other variables (e.g. Sensor ID, height, GPS loc etc.)
    - how to organize data from different sensors?

"""

from glob import glob
from pathlib import Path

from .aqdata import AQData
from .plot import plot_humidity, plot_pm, plot_pm_ratio, plot_temperature, \
    plot_pm_vs_humidity, plot_pm_vs_temperature

def main(argv=[]):
    """Main entry point."""

    # gt inputdir as first argument
    if len(argv) != 1:
        print(__doc__)
        return
    inputdir = Path(argv[0])

    # initialize empty dataset
    data = AQData()

    # parse all data
    for filename in glob(str(inputdir / "*.csv")):
        print("Parsing", filename)
        data = data.merge(AQData.from_csv(filename))

    # plot PM data
    plot_pm(data)
    plot_pm_ratio(data)
    # plot temperature date
    plot_temperature(data)
    # plot humidity data
    plot_humidity(data)
    # plot pm vs humidity data
    plot_pm_vs_humidity(data)
    # plot pm vs temperature data
    plot_pm_vs_temperature(data)

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])