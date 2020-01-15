"""AQ Class definition for Air Quality data analysis."""

from numpy import log
from pandas import DataFrame, Timedelta, Timestamp, to_datetime, merge

from .parse import parse_metadata_from_filename, parse_madavi_csv, \
    parse_sensorcommunity_csv

from .metadata import AQMetaData, SensorInfo

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

    def __init__(self, chip_id=None, metadata=AQMetaData(),
        data=DataFrame(columns=data_columns, index=to_datetime([])),
        date_start=None, date_end=None,
    ):
        self.metadata = metadata # metadata, useful descriptors
        self.chip_id = chip_id # special property from metadata with convenience usage
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

    @property
    def chip_id(self):
        return self.metadata.chip_id

    @chip_id.setter
    def chip_id(self, value):
        self.metadata.chip_id = value

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
            filename (Path): .csv file to read in format used by
                madavi.de or archive.sensor.community (autodetected).
            date_start (datetime): starting date limit or None if not used
            date_end (datetime): ending date limit or None if not used.

        Return:
            a new AQData class with parsed data
        """
        chip_id, sensor_id, sensor_type, date = parse_metadata_from_filename(filename)
        # error checking
        if chip_id is None and sensor_id is None:
            raise ValueError("Could not parse file {}".format(filename))
        # parse, select and rename data columns for madavi.de format
        if chip_id:
            raw_data = parse_madavi_csv(filename)
            data = raw_data[["Temp", "Humidity", "SDS_P1", "SDS_P2"]]
            data.columns = self.data_columns
            metadata = AQMetaData(chip_id=chip_id)
        # parse, select and rename data columns for sensor.community format,
        # which is separated to individual sensors
        else:
            raw_data = parse_sensorcommunity_csv(filename)
            if sensor_type == "sds011":
                data = raw_data[["P1", "P2"]]
                data.columns = ["pm10", "pm2_5"]
                data.reindex(self.data_columns)
                metadata = AQMetaData(sensors={
                    SensorInfo("pm10", sensor_type.upper(), sensor_id),
                    SensorInfo("pm2_5", sensor_type.upper(), sensor_id),
                })
            elif sensor_type == "dht22":
                data = raw_data[["temperature", "humidity"]]
                data.columns = ["temperature", "humidity"]
                data.reindex(self.data_columns)
                metadata = AQMetaData(sensors={
                    SensorInfo("temperature", sensor_type.upper(), sensor_id),
                    SensorInfo("humidity", sensor_type.upper(), sensor_id),
                })

        return self(chip_id=chip_id, data=data, metadata=metadata,
            date_start=date_start, date_end=date_end)

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
        # TODO: optimize inplace

        metadata = self.metadata.merge(other.metadata)
        data = self.data.append(other.data, sort=False).sort_index()
        #data = self.data.join(other.data, how="outer")
        #data = merge(self.data, other.data, how="outer", on=None, left_index=True, right_index=True)
        #data = merge_asof(self.data, other.data, left_index=True, right_index=True, tolerance=Timedelta(seconds=5), direction='nearest') # problem: other's unique parts are skipped...
        # TODO: in sensorcommunity data sensors are stored in separate files
        #   and timestamps are not matched perfectly. how to combine closeby
        #   timestamps?

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
    def sensor_ids(self):
        return list(set(self.metadata.sensors[key].sensor_id
            for key in self.metadata.sensors)
        )
