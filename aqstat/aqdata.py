"""AQ Class definition for Air Quality data analysis."""

from numpy import log
from pandas import DataFrame, Timedelta, Timestamp

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
        data=DataFrame(columns=data_columns), date_start=None, date_end=None,
    ):
        self.sensor_id = sensor_id # integer
        self.location = location # lat [deg], lon [deg], amsl [m], agl[m]
        self.data = data.sort_values(by=["time"]).reset_index(drop=True) # all the time series of AQ data as pandas DataFrame
        if date_start is not None:
            self.data = self.data[self.data.time.dt.date >= Timestamp(date_start)]
        if date_end is not None:
            self.data = self.data[self.data.time.dt.date <= Timestamp(date_end)]

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

    def corrwith(self, other, method="pearson", tolerance=60):
        """Correlate self with another sensor dataset.

        Parameters:
            other (AQData): the other dataset to correlate with
            method (str or callable): 'pearson', 'kendall', 'spearman' or else,
                for more information see pandas.DataFrame.corrwith
            tolerance (float): maximum time difference allowed between matching
                timestamps in the two datasets, expressed as seconds.

                TODO: interpolate datasets to have more accurate matching on
                stochastically timestamped data
        Return:
            pandas Series object containing correlation values between datasets
        """
        # create dataframes with time index
        a = self.data.set_index('time')
        b = other.data.set_index('time')
        # create matching dataset with rows that have similar timestamps
        # TODO: interpolate datasets to have more accurate matching on
        #       stochastically timestamped data
        b_matched = b.reindex(a.index, method='nearest',
            tolerance=Timedelta(seconds=tolerance), axis=0
        )
        # calculate correlation
        result = a.corrwith(other=b_matched, method=method, drop=True)
        # add number of valid values that were compared to the output
        # TODO: this is not accurate if there are individual NaN-s in a or b
        #       in some columns only...
        result["count"] = b_matched.dropna().shape[0]

        return result

    @classmethod
    def from_csv(self, filename, date_start=None, date_end=None):
        """Create a new class from a csv file.

        Parameters:
            filename (Path): file to read (luftdaten.info .csv format so far)
            date_start (datetime): starting date limit or None if not used
            date_end (datetime): ending date limit or None if not used.

        Return:
            a new AQData class with parsed data
        """
        sensor_id = parse_id_from_luftdaten_csv(filename)
        raw_data = parse_luftdaten_csv(filename)
        data = raw_data[["Time", "Temp", "Humidity", "SDS_P1", "SDS_P2"]]
        data.columns = self.data_columns
        # TODO: do not parse outside date_start and date_end at all
        return self(sensor_id=sensor_id, data=data, date_start=date_start,
            date_end=date_end)

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
        data = self.data.append(other.data).sort_values(
            by=["time"]).reset_index(drop=True)

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
        return self.data.sort_values(
            by=["time"], inplace=inplace).reset_index(drop=True)
