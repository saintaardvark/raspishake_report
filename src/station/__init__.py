import os

from loguru import logger
from obspy import read_inventory

def get_inv(cache_dir="", stn="", client=None):
    """Get response data for station.

    Uses cached data if present.
    """
    cache_file = f"{cache_dir}/{stn}.xml"
    if os.path.exists(cache_file):
        logger.debug("Reading in cached station response data...")
        return read_inventory(cache_file, format="STATIONXML")

    logger.debug(
        "Cached station response data not found -- will download & save for next time"
    )
    inv = client.get_stations(network="AM", station=stn, level="RESP")
    try:
        os.makedirs(cache_dir, exist_ok=True)
        inv.write(cache_file, format="STATIONXML")
    except Exception as exc:
        logger.warn(
            "Can't save response data for next time, continuing with what I've got: {exc}"
        )

    return inv

