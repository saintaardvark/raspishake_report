import configparser
from dataclasses import dataclass
import math

from loguru import logger
from obspy.taup import TauPyModel


@dataclass(init=False)
class Station:
    """
    A class for stations
    """

    name: str
    lat: float
    lon: float
    elev: float

    def __init__(self, cfg_file):
        config = configparser.ConfigParser()
        config.read(cfg_file)
        self.name = config["station"]["name"]
        self.lat = config.getfloat("station", "lat")  # station latitude
        self.lon = config.getfloat("station", "lon")  # station longitude
        self.elev = config.getfloat("station", "elev")  # station elevation


class Event:
    """
    A class for earthquake events
    """

    def __init__(self, lat, lon, depth, mag, time, event_id, location, url):
        self._lat = lat
        self._lon = lon
        self._depth = depth
        self._mag = mag
        self._time = time
        self._event_id = event_id
        self._location = location
        self._url = url
        # FIXME: Make this a constant
        self._model = TauPyModel(model="iasp91")
        # for arrival times, maybe other things
        self._cache = {}

    def get_arrival_times(self, stn: Station):
        """
        Calculate arrival times
        """
        if "arrival_times" in self._cache:
            return self._cache["arrival_times"]
        # logger.debug("Calculating phase arrivals...")

        great_angle_deg = self.calculate_great_angle(stn)
        arrs = self._model.get_travel_times(self._depth, great_angle_deg)
        # logger.debug(
        #     arrs
        # )  # print the arrivals for reference when setting delay and duration
        return arrs

    def calculate_great_angle(self, stn: Station, units: str = "deg"):
        # convert angles to radians
        latSrad = math.radians(stn.lat)
        lonSrad = math.radians(stn.lon)
        latErad = math.radians(self._lat)
        lonErad = math.radians(self._lon)

        if lonSrad > lonErad:
            lon_diff = lonSrad - lonErad
        else:
            lon_diff = lonErad - lonSrad

        great_angle_rad = math.acos(
            math.sin(latErad) * math.sin(latSrad)
            + math.cos(latErad) * math.cos(latSrad) * math.cos(lon_diff)
        )
        if units == "rad":
            return great_angle_rad
        else:
            return math.degrees(great_angle_rad)

    def calculate_distance(self, stn: Station):
        """
        Calculate distance
        """
        great_angle_rad = self.calculate_great_angle(stn=stn, units="rad")
        return great_angle_rad * 12742 / 2
