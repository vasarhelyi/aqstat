"""Arbitrary helper functions to be used in aqstat."""

def consecutive_pairs(iterable, cyclic=False):
    """Given an iterable, returns a generator that generates consecutive pairs
    of objects from the iterable.

    Parameters:
        iterable (Iterable[object]): the iterable to process
        cyclic (bool): whether the iterable should be considered "cyclic".
            If this argument is ``True``, the function will yield a pair
            consisting of the last element of the iterable paired with
            the first one at the end.
    """
    it = iter(iterable)
    prev = next(it)
    first = prev if cyclic else None
    try:
        while True:
            curr = next(it)
            yield prev, curr
            prev = curr
    except StopIteration:
        pass
    if cyclic:
        yield prev, first

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