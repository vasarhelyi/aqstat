"""AQ Class definition for Air Quality data analysis."""

from numpy import log
from pandas import DataFrame

from .parse import parse_id_from_luftdaten_csv, parse_luftdaten_csv

class AQData(object):
    """A generic class to store AQ sensor parameters and sensor data."""

    # TODO: parse and use adaptively, generalize to other sensor types
    sensors = {
        "pm10": "SDS011",
        "pm2_5": "SDS011",
        "temperature": "DHT22",
        "humidity": "DHT22",
    }
    data_columns = "time temperature humidity pm10 pm2_5".split()

    def __init__(self, sensor_id=None, location=None,
        data=DataFrame(columns=data_columns)
    ):
        self.sensor_id = sensor_id # integer
        self.location = location # lat [deg], lon [deg], amsl [m], agl[m]
        self.data = data # all the time series of AQ data as pandas DataFrame

    def calibrate(self):
        """Perform calibration on PM dataset."""

        # first just include PM ratio column
        self.data["pm10_per_pm2_5"] = self.data.pm10 / self.data.pm2_5
        # second, perform calibration according to this article:
        # @article{article,
        #     author = {Laquai, Bernd and Saur, Antonia},
        #     year = {2017},
        #     month = {12},
        #     pages = {},
        #     title = {Development of a Calibration Methodology for the SDS011
        #              Low-Cost PM-Sensor with respect to Professional
        #              Reference Instrumentation}
        # }
        # Note that this method is only valid (if valid) for SDS011
        self.data["pm2_5_calib"] = self.data.pm2_5 / (
            -0.509 * log(self.data.pm10_per_pm2_5) + 1.2203
        )

    @classmethod
    def from_csv(self, filename):
        """Create a new class from a csv file."""
        sensor_id = parse_id_from_luftdaten_csv(filename)
        raw_data = parse_luftdaten_csv(filename)
        data = raw_data[["Time", "Temp", "Humidity", "SDS_P1", "SDS_P2"]]
        data.columns = self.data_columns
        return self(sensor_id=sensor_id, data=data.sort_values(by=["time"]))

    # TODO: reimplement with 'resample', it might be better
    def groupby(self, freq):
        """Group data of self with a given temporal frequency.

        Parameters:
            freq (str): the frequency to group by. See possible values at
                pandas.DatetimeIndex.floor frequency aliases.

        Return:
            pandas DataFrameGroupBy object with groups of data
        """
        return self.data.groupby(by=self.data.time.dt.floor(freq))

    def merge(self, other, inplace=False):
        """Returns another sensor dataset that is the union of this sensor
        dataset and another one.

        Parameters:
            other (AQData): the other dataset to unite this with

        Returns:
            object: the union of this dataset and the other one
        """

        # check sensor_ids
        sensor_id = self.sensor_id or other.sensor_id
        if other.sensor_id is not None and sensor_id != other.sensor_id:
            raise ValueError("Cannot merge two datasets with different "
                             "sensor ids: {} and {}".format(
                self.sensor_id, other.sensor_id))
        # check locations
        location = self.location or other.location
        if other.location is not None and location != other.location:
            raise ValueError("Cannot merge two datasets with different "
                             "locations: {} and {}".format(
                self.location, other.location))
        # merge data
        data = self.data.append(other.data).sort_values(by=["time"])

        # change data inplace
        if inplace:
            self.sensor_id = sensor_id
            self.location = location
            self.data = data
            return None
        # or create new class with merged data
        return self.__class__(
            sensor_id=sensor_id,
            location=location,
            data=data
        )

    def sort(self, inplace=False):
        """Sort data according to time."""
        return self.data.sort_values(by=["time"], inplace=inplace)
