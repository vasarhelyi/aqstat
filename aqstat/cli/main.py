"""This is a first attempt to test-visualize some of the air quality data
coming from https://www.madavi.de/sensor/csvfiles.php?sensor=esp8266-11797099

Note: The script is mostly a "lab" test to catalyze thinking about how this
whole AQ thing should be treated.

"""

import click
import logging


@click.group()
# TODO: enable this once setuptools is setup properly...
#@click.version_option()
@click.option("-v", "--verbose", count=True, help="increase logging verbosity")
def start(verbose=False):
    """Do all kinds of air quality related stuff."""

    # setup logging
    if verbose > 1:
        log_level = logging.DEBUG
    elif verbose > 0:
        log_level = logging.INFO
    else:
        log_level = logging.WARN
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")


# import commands
from .commands.download import download
from .commands.plot import plot
from .commands.test import test
# add commands from separate files
start.add_command(download)
start.add_command(plot)
start.add_command(test)


if __name__ == '__main__':
    start()