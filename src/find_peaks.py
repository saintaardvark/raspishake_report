#!/usr/bin/env python3

import configparser

from obspy.clients.fdsn import Client
from obspy.core import stream

from peaks.arrivals import find_arrivals_in_data
from station import get_inv


# TODO: Note of where I am.
#
# I'm hoping the find_peaks function will turn up whether or not there
# are peaks seen from a given event -- and if not, maybe I can try
# adjusting the bandpass filter to do things right.
#
# To test that, I've saved (I think -- I may need to do this again)
# data in the two mseed files.  These are from this event:
#
# ./src/report.py main_plot --lat_e 17.0943 --lon_e -94.9609 --depth 108.369 --mag 5.9 --time_e 2023-10-07T05:06:55 --event_id 6000ldny --location '8 km W of Cuauhtémoc, Mexico' --bandpass_filter global
#
# What I'm trying to do is load the files, then play around with the
# find_peaks function to see what it finds.  At the moment, this is a
# big mix of hard-coded things, lines copy-pasta'd from report.py, and
#so on.
#
# The last bit I'm missing is the caculation of arrs (arrival times),
# which is only half-done by having the model there; I need to fill in
# data about the event as well.
#
# Honestly, I think this would be better in a Jupyter notebook -- this
# is exactly the kind of interactive exploration it excels at.

def main():
    """
    Main entry point
    """
    config = configparser.ConfigParser()
    config.read("report.ini")
    stn = config["station"]["name"]
    rs = Client("RASPISHAKE")
    inv = get_inv(cache_dir=config["DEFAULT"]["cache_dir"], stn=stn, client=rs)

    trace0 = stream.read("event_data.mseed")
    bn0 = stream.read("event_background.mseed")
    # Global
    filt = [0.1, 0.2, 0.9, 1.0]
    outdisp = trace0.remove_response(
        inventory=inv, pre_filt=filt, output="DISP", water_level=60, plot=False
    )  # convert to Disp
    disp_max = outdisp[0].max()
    model = TauPyModel(model="iasp91")
    arrs = model.get_travel_times(depth, great_angle_deg)
    find_arrivals_in_data(outdisp[0].data, disp_max / 4, arrs)


if __name__ == "__main__":
    main()
