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
