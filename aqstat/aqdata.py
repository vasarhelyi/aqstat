"""AQ Class definition for Air Quality data analysis."""

from collections import namedtuple

from .parse import parse_id_from_raw_aq_filename, parse_raw_aq_csv

class AQData(namedtuple("AQData", "sensor_id time temperature humidity pm10 pm2_5")):
    """A generic class to store air quality data."""

    @classmethod
    def from_csv(self, filename):
        """Create a new class from a csv file."""
        sensor_id = parse_id_from_raw_aq_filename(filename)
        data = parse_raw_aq_csv(filename)
        return self(sensor_id=sensor_id, time=data["Time"],
            temperature=data["Temp"], humidity=data["Humidity"],
            pm10=data["SDS_P1"], pm2_5=data["SDS_P2"],
        )

    def __new__(self, sensor_id=None, time=[], temperature=[], humidity=[], pm10=[], pm2_5=[]):
        return super(AQData, self).__new__(self, sensor_id, time, temperature,
            humidity, pm10, pm2_5
        )

    def merge(self, other):
        """Returns another dataset that is the union of this dataset and another
        dataset.

        Parameters:
            other (AQData): the other dataset to unite this dataset with

        Returns:
            object: the union of this dataset and the other dataset
        """
        sensor_id = self.sensor_id or other.sensor_id
        if other.sensor_id is not None and sensor_id != other.sensor_id:
            raise ValueError("Cannot merge two datasets with different sensor ids: {} and {}".format(
                self.sensor_id, other.sensor_id))

        # TODO: sort according to time
        return self.__class__(
            sensor_id=sensor_id,
            time=self.time + other.time,
            temperature=self.temperature + other.temperature,
            humidity=self.humidity + other.humidity,
            pm10=self.pm10 + other.pm10,
            pm2_5=self.pm2_5 + other.pm2_5,
        )
