"""Arbitrary helper functions to be used in aqstat."""

def find_sensor_with_id(sensors, sensor_id):
    """Find a sensor index with matching sensor_id.

    Parameters:
        sensors (list[AQData]): list of sensors
        sensor_id (int): the sensor id to look for.

    Return:
        index if sensor in sensors with matching id. If not found but there is
        one sensor with None id, we return that. If none found, we return None.

    """
    first_none = None
    for i, s in enumerate(sensors):
        if s.sensor_id == sensor_id:
            return i
        if first_none is None and s.sensor_id is None:
            first_none = i
    if first_none is not None:
        return i
    return None