"""Setup script for the AQ-stat command line tool."""

from glob import glob
from os.path import basename, splitext
from setuptools import setup, find_packages


requires = [
    "click>=7.0",
    "requests",
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
