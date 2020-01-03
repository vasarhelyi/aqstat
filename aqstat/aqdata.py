"""AQ Class definition for Air Quality data analysis."""

from numpy import log
from pandas import DataFrame, Timedelta, Timestamp, to_datetime

from .parse import parse_id_from_luftdaten_csv, parse_luftdaten_csv
from .metadata import AQMetaData

class AQData(object):
    """A generic class to store AQ sensor parameters and sensor data.

    The main .data is stored in a pandas DataFrame class, indexed by
    the datetime value of each measurement, always sorted according to time.

    """

    # TODO: parse and use adaptively, generalize to other sensor types
    sensors = {
        "pm10": "SDS011",
        "pm2_5": "SDS011",
        "temperature": "DHT22",
        "humidity": "DHT22",
    }
    data_columns = "temperature humidity pm10 pm2_5".split()

    def __init__(self, sensor_id=None, metadata=AQMetaData(),
        data=DataFrame(columns=data_columns, index=to_datetime([])),
        date_start=None, date_end=None,
    ):
        self.metadata = metadata # metadata, useful descriptors
        self.sensor_id = sensor_id # special property from metadata with convenience usage
        self.data = data.sort_index() # all the time series of AQ data as pandas DataFrame indexed by datetime
        if date_start is not None:
            self.data = self.data[self.data.index.date >= Timestamp(date_start)]
        if date_end is not None:
            self.data = self.data[self.data.index.date <= Timestamp(date_end)]

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
        # create matching dataset with rows that have similar timestamps
        # TODO: interpolate datasets to have more accurate matching on
        #       stochastically timestamped data
        other_matched = other.data.reindex(self.data.index, method='nearest',
            tolerance=Timedelta(seconds=tolerance), axis=0
        )
        # calculate correlation
        result = self.data.corrwith(other=other_matched, method=method, drop=True)
        # calculate number of not-NaNs for each column
        counts = (self.data + other_matched).count()
        return DataFrame({method: result, "count": counts})

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
        # parse data
        sensor_id = parse_id_from_luftdaten_csv(filename)
        raw_data = parse_luftdaten_csv(filename)
        # select and rename data columns
        data = raw_data[["Temp", "Humidity", "SDS_P1", "SDS_P2"]]
        data.columns = self.data_columns

        return self(sensor_id=sensor_id, data=data, date_start=date_start,
            date_end=date_end)

    @property
    def median_sampling_time(self):
        """Return the median of the sampling time of the data."""
        df = self.data.index.to_series().diff()

        return df.median()

    def merge(self, other, inplace=False):
        """Returns another sensor dataset that is the union of this sensor
        dataset and another one.

        Parameters:
            other (AQData): the other dataset to unite this with

        Returns:
            object: the union of this dataset and the other one

        """

        metadata = self.metadata.merge(other.metadata)
        data = self.data.append(other.data).sort_index()

        # change data inplace
        if inplace:
            self.metadata = metadata
            self.data = data
            return None
        # or create new class with merged data
        return self.__class__(
            metadata=metadata,
            data=data
        )

    @property
    def sensor_id(self):
        return self.metadata.sensor_id

    @sensor_id.setter
    def sensor_id(self, value):
        self.metadata.sensor_id = value
