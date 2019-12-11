"""AQ Class definition for Air Quality data analysis."""

from collections import namedtuple

from .parse import parse_id_from_raw_aq_filename, parse_raw_aq_csv


class AQData(namedtuple("AQData", "time temperature humidity pm10 pm2_5")):
    """A generic class to store air quality data."""

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


class AQSensor(object):
    """A generic class to store AQ sensor parameters and sensor data."""
    def __init__(self, sensor_id=None, location=None, data=AQData()):
        self.sensor_id = sensor_id
        self.location = location # lat [deg], lon [deg], amsl [m]
        self.data = data # all the time series of AQ data

    @classmethod
    def from_csv(self, filename):
        """Create a new class from a csv file."""
        sensor_id = parse_id_from_raw_aq_filename(filename)
        raw_data = parse_raw_aq_csv(filename)
        data = AQData(time=raw_data["Time"], temperature=raw_data["Temp"],
            humidity=raw_data["Humidity"], pm10=raw_data["SDS_P1"],
            pm2_5=raw_data["SDS_P2"],
        )
        return self(sensor_id=sensor_id, data=data)

    def merge(self, other):
        """Returns another sensor dataset that is the union of this sensor
        dataset and another sensor dataset.

        Parameters:
            other (AQSensor): the other sensor dataset to unite this with

        Returns:
            object: the union of this sensor dataset and the other one
        """

        # check sensor_ids
        sensor_id = self.sensor_id or other.sensor_id
        if other.sensor_id is not None and sensor_id != other.sensor_id:
            raise ValueError("Cannot merge two sensor datasets with different "
                             "sensor ids: {} and {}".format(
                self.sensor_id, other.sensor_id))
        # check locations
        location = self.location or other.location
        if other.location is not None and location != other.location:
            raise ValueError("Cannot merge two sensor datasets with different "
                             "locations: {} and {}".format(
                self.location, other.location))
        # create new class with merged data
        return self.__class__(
            sensor_id=sensor_id,
            location=location,
            data=self.data.merge(other.data)
        )