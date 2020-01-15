"""Arbitrary helper functions to be used in aqstat."""

from datetime import timedelta

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

def last_day_of_month(any_day):
    """Return the last day of month from a given date."""
    next_month = any_day.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)