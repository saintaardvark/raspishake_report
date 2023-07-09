#!/usr/bin/env python3

from obspy.clients.fdsn import Client
from obspy.core import UTCDateTime
from obspy.signal import filter
from obspy.taup import TauPyModel
from obspy import read

def main():
    """
    Main entry point
    """
    # breakpoint()
    filt=[0.7, 0.7, 2, 2.1]
    rs = Client("RASPISHAKE")
    stn = "RAF36"
    inv = rs.get_stations(network="AM", station=stn, level="RESP")
    # inv = read("raf36.xml")
    # Cached data I have on hand
    t0 = read("event_data.mseed")
    t0.remove_response(inventory=inv, pre_filt=filt, water_level=60, plot=True)


if __name__ == "__main__":
    main()
