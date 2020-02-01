"""Arbitrary helper functions to be used in aqstat."""

from datetime import timedelta
from math import atan2, cos, radians, sin, sqrt

def find_sensor_with_id(sensors, chip_id=None, sensor_id=None):
    """Find a sensor index with first matching chip_id or sensor_id.

    Parameters:
        sensors (list[AQData]): list of sensors
        chip_id (int): the chip id to look for.
        sensor_id (int): the sensor id to look for.

    Return:
        index if sensor in sensors with matching id or None if not found.

    """
    for i, sensor in enumerate(sensors):
        if chip_id is not None:
            if sensor.chip_id == chip_id:
                return i
        if sensor_id is not None:
            for sid in sensor.sensor_ids:
                if sid == sensor_id:
                    return i
    return None

def latlon_distance(lat1, lon1, lat2, lon2):
    """Return distance between two geographical points.

    Source: http://www.movable-type.co.uk/scripts/latlong.html

    Parameters:
        lat1(float): latitude of first coordinate [deg].
        lon1(float): longitude of first coordinate [deg].
        lat2(float): latitude of second coordinate [deg].
        lon2(float): longitude of second coordinate [deg].

    Return:
        distance between two points in [m].

    """
    radius_of_earth = 6378137.0
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    dLat = lat2 - lat1
    dLon = lon2 - lon1

    a = sin(0.5 * dLat)**2 + sin(0.5 * dLon)**2 * cos(lat1) * cos(lat2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return radius_of_earth * c

def last_day_of_month(any_day):
    """Return the last day of month from a given date."""
    next_month = any_day.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)

def merge_sensors_with_shared_name(sensors):
    """Merge sensors that share the same name.

    Parameters:
        sensors(list[AQData]): list of sensors

    Return:
        new list with unique names and merged data for same names

    """
    if len(sensors) < 2:
        return sensors

    i = 0
    while i < len(sensors) - 1:
        j = i + 1
        while j < len(sensors):
            if sensors[i].name and sensors[i].name == sensors[j].name:
                sensors[i].merge(sensors[j], inplace=True)
                del sensors[j]
            else:
                j += 1
        i += 1

    return sensors
