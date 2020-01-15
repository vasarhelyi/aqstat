"""AQ Metadata Class definition for Air Quality data analysis."""

from collections import namedtuple
import json

from .parse import parse_metadata_json

GPSCoordinate = namedtuple("GPSCoordinate", "lat lon amsl agl") # [deg deg m m]
ContactInfo = namedtuple("ContactInfo", "name email phone")
SensorInfo = namedtuple("SensorInfo", "name type sensor_id") # TODO: csvcolname, unit

class AQMetaData(object):
    """A generic class to store AQ sensor metadata."""

    def __init__(self, chip_id=None, sensors = {}, description=None,
        location=GPSCoordinate("", "", "", ""), owner=ContactInfo("", "" ,"")
    ):
        self.chip_id = chip_id # [int]
        self.sensors = sensors # [dict(SensorInfo)]
        self.description = description # [str]
        self.location = location # [GPSCoordinate]
        self.owner = owner # [ContactInfo]

    def as_dict(self):
        """Create a dictionary representation of self."""
        ret = {}

        ret["chip_id"] = self.chip_id
        ret["sensors"] = {}
        for key in self.sensors:
            ret["sensors"][key] = {
                "name": self.sensors[key].name,
                "type": self.sensors[key].type,
                "sensor_id": self.sensors[key].sensor_id,
            }
        ret["description"] = self.description
        ret["location"] = {
            "lat": self.location.lat,
            "lon": self.location.lon,
            "amsl": self.location.amsl,
            "agl": self.location.agl,
        }
        ret["owner"] = {
            "name": self.owner.name,
            "email": self.owner.email,
            "phone": self.owner.phone,
        }

    return ret

    @classmethod
    def from_json(self, filename):
        """Create a new class from a json file with the format specified in
        aqstat/data/examples/metadata.json

        Parameters:
            filename (Path): file to read (.json)

        Return:
            a new AQMetaData class with parsed metadata
        """
        # parse metadata
        with open(filename, "r") as f:
            metadata = json.load(f)

        # parse chip_id
        chip_id = metadata["chip_id"]
        # parse sensors
        sensors = {}
        for key in metadata["sensors"]:
            sensors[key] = SensorInfo(
                name=key,
                type=metadata["sensors"][key]["type"],
                sensor_id=metadata["sensors"][key]["sensor_id"],
            )
        # parse description
        description = metadata["description"],
        # parse location
        location = GPSCoordinate(
            lat=metadata["location"]["lat"],
            lon=metadata["location"]["lon"],
            amsl=metadata["location"]["amsl"],
            agl=metadata["location"]["agl"],
        )
        # parse owner
        owner = ContactInfo(
            name=metadata["owner"]["name"],
            email=metadata["owner"]["email"],
            phone=metadata["owner"]["phone"],
        )

        return self(
            chip_id=chip_id,
            sensors=sensors,
            description=description,
            location=location,
            owner=owner
        )

    def merge(self, other, inplace=False):
        """Returns sensor metadata that is the union of self's and other's
        metadata. If there are properties where both are set, self's value
        is preserved. 'chip_id' and 'sensor_id' values are special in the sense
        that they are explicitely checked to avoid merging different ones.

        Parameters:
            other (AQMetaData): metadata to unite self's metadata with

        Returns:
            object: the union of self's and other's metadata

        """

        # check chip_ids
        chip_id = self.chip_id or other.chip_id
        if other.chip_id is not None and chip_id != other.chip_id:
            raise ValueError("Cannot merge two datasets with different "
                             "chip ids: {} and {}".format(
                self.chip_id, other.chip_id))
        # merge sensor descriptions
        sensors = {}
        for key in other.sensors:
            if key in self.sensors:
                sensor_id = self.sensors[key].sensor_id or other.sensors[key].sensor_id
                if other.sensors[key].sensor_id is not None and sensor_id != other.sensors[key].sensor_id:
                    raise ValueError("Cannot merge two {} sensors with different "
                                     "sensor ids: {} and {}".format(
                        key, self.sensors[key].sensor_id, other.sensors[key].sensor_id))
                sensors[key] = SensorInfo(
                    name=key,
                    type=self.sensors[key].type or other.sensors[key].type,
                    sensor_id=sensor_id
                )
            else:
                sensors[key] = other.sensors[key]
        # prepare location
        location = GPSCoordinate(
            lat=self.location.lat or other.location.lat,
            lon=self.location.lon or other.location.lon,
            amsl=self.location.amsl or other.location.amsl,
            agl=self.location.agl or other.location.agl,
        )
        # prepare owner
        owner = ContactInfo(
            name=self.owner.name or other.owner.name,
            email=self.owner.email or other.owner.email,
            phone=self.owner.phone or other.owner.phone,
        )

        # change data inplace
        if inplace:
            self.chip_id = chip_id
            self.sensors = sensors
            self.description = self.description or other.description
            self.location = location
            self.owner = owner

            return None
        # or create new class with merged data
        return self.__class__(
            chip_id=chip_id,
            sensors=sensors,
            description=self.description or other.description,
            location=location,
            owner=owner,
        )

