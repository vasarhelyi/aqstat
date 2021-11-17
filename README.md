# AQStat

`aqstat` is a command line Python tool for visualizing air quality data
collected under the [luftdaten.info](https://luftdaten.info/) project.

# Install

`aqstat` is written in Python, so installation and usage is platform-independent.

## Prerequisites

* Install git
* Get Python 3.7 or later
* Install Poetry according to its [official install guide](https://python-poetry.org/docs/#installation).

## Install using Poetry

Installation should be as simple as running the following code:

```
git clone https://github.com/vasarhelyi/aqstat.git
cd aqstat
poetry install
```

As `aqstat` uses Poetry, all Python package dependencies will be installed
automatically in a local virtual environment under `.venv` in the project folder.

# Getting updates

If you `git pull` later on to get updates, it might be needed to rerun
`poetry install` to update possibly changed dependencies properly.


# Usage

## Basic usage

Run `poetry run aqstat --help` to get a quick overview on the usage of `aqstat`. There are three basic commands currently available:

  * `download` helps you retreive air quality sensor data from the net to your local computer for later analysis
  * `plot` lets you visualize air quality data of selected sensors
  * `stat` generates various statistical outputs for selected sensors

An additional `test` command is provided as a development section to test different work-in-progress stuff.

More detailed help on individual commands is also available. For example, run `poetry run aqstat download --help` to get help on data download options.

To get some examples on usage, check out the `doc\examples\commands.md` file.


## Sensor database

Local sensor data is stored in folders named after sensor IDs. There are two basic data sources supported currently, a bit of a problem is that they use different IDs for different sensors (madavi.de uses a single `chip_id`, sensor.community uses a `sensor_id` for all sensors in a given measurement unit. Furthermore, these two sources store slightly different information about the sensors.

To obtain a general easy-to-use reference for all sensor data, a local description of all sensors can be given optionally. A simple JSON format is used for that, please check out the `doc\examples\metadata.json` file as an example how to fill the JSON form for a single sensor, or use the `scripts\convert_luftdaten_csv_to_metadata_json.py` script to generate .json files from the sensor data directly.

The overall sensor database structure should look like something like this:

```
12345/
67890/
Budapest-12345.json
Verőce-67890.json
```

The name of the `.json` files is arbitrary, it is useful to include human readable information, such as the location of the sensor, as in the example above.

Later on, during the usage of the `plot` and `stat` commands, filters can be defined and several outputs can be generated based on various properties given in the .json files.

# Contact and collaboration

`aqstat` is made public and open-source to help each other in fighting air pollution. Please [contact](mailto:vasarhelyi@hal.elte.hu) if you have any questions on usage, something is not working properly, you have new ideas or feature requests or if you would like to help in development or collaboration or wish to support the project in any way.

