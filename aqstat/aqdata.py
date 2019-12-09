"""AQ Class definition for Air Quality data analysis."""

from collections import namedtuple

from .parse import parse_raw_aq_csv

class AQData(namedtuple("AQData", "time temperature humidity pm10 pm2_5")):
    """A generic class to store air quality data."""

    @classmethod
    def from_csv(self, filename):
        """Create a new class from a csv file."""
        data = parse_raw_aq_csv(filename)
        return self(time=data["Time"], temperature=data["Temp"],
            humidity=data["Humidity"], pm10=data["SDS_P1"],
            pm2_5=data["SDS_P2"],
        )

    def __new__(self, time=[], temperature=[], humidity=[], pm10=[], pm2_5=[]):
        return super(AQData, self).__new__(self, time, temperature, humidity,
            pm10, pm2_5
        )

    def merge(self, other):
        """Returns another dataset that is the union of this dataset and another
        dataset.

        Parameters:
            other (AQData): the other dataset to unite this dataset with

        Returns:
            object: the union of this dataset and the other dataset
        """
        # TODO: sort according to time
        return self.__class__(
            time=self.time + other.time,
            temperature=self.temperature + other.temperature,
            humidity=self.humidity + other.humidity,
            pm10=self.pm10 + other.pm10,
            pm2_5=self.pm2_5 + other.pm2_5,
        )
