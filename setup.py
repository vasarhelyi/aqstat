"""Setup script for the AQ-stat command line tool."""

from glob import glob
from os.path import basename, splitext
from setuptools import setup, find_packages


requires = [
    "click>=7.0",
    "click_option_group>=0.2.3",
    "requests>=2.22",
    "pandas>=0.25",
    "trio>=0.16.0",
    "asks",
]

__version__ = None
exec(open("aqstat/version.py").read())

setup(
    name="aqstat",
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=requires,
    entry_points={"console_scripts": ["aqstat = aqstat.cli.main:start"]},
)
