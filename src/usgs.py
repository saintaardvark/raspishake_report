#!/usr/bin/env python3

import configparser
from datetime import datetime, timedelta
import json
import math

import click
from loguru import logger
from obspy.core import UTCDateTime
from prettytable import PrettyTable

from util import generate_report_url

from travel_times import Station, Event
from usgs import USGS_FEEDS, UNWANTED_GEOJSON_COLS, get_quakes_from_feed


@click.group()
def usgs():
    """A tool to query the USGS for earthquake data, and to generate
    commands to run reports on them.
    """


@click.command("pretty_table", short_help="Pretty table")
@click.option(
    "--feed",
    type=click.Choice(list(USGS_FEEDS.keys())),
    default="LAST_DAY_OVER_4_POINT_5",
    show_default=True,
    help="Feed to use",
)
@click.option(
    "--radius",
    default=0,
    show_default=True,
    help="If > 0, only include quakes within this many km of the station.",
)
def pretty_table(feed, radius):
    """
    Print a pretty table
    """
    quakes = get_quakes_from_feed(feed)
    stn = Station(cfg_file="report.ini")
    t = PrettyTable()
    t.field_names = [
        "Time (UTC)",
        "Location",
        "Magnitude",
        "Distance (km)",
        "First arrival",
    ]
    # TODO: We should be parsing this w/geojson
    all_events = []
    for quake in quakes["features"]:
        lon_e, lat_e, depth = quake["geometry"]["coordinates"]
        event = Event(
            lat=lat_e,
            lon=lon_e,
            depth=depth,
            mag=quake["properties"]["mag"],
            time=quake["properties"]["time"] / 1000,  # ms since epoch
            event_id=quake["properties"]["code"],
            location=quake["properties"]["place"],
            url=quake["properties"]["url"],
        )
        all_events.append(event)

    if radius > 0:
        print(f"Filtering by radius {radius} from station")
        all_events = [
            event for event in all_events if event.calculate_distance(stn) <= radius
        ]

    for event in sorted(all_events, key=lambda x: x._time):
        quaketime = datetime.utcfromtimestamp(event._time).strftime("%Y-%m-%d %H:%M:%S")
        distance = event.calculate_distance(stn)
        try:
            arrs = event.get_arrival_times(stn)
            first_arr = event._time + arrs[0].time
            first_arr = datetime.utcfromtimestamp(first_arr).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        except Exception as e:
            # I'm getting errors like this for some close events: "No
            # layer contains this depth".  This is in the source code
            # (https://docs.obspy.org/_modules/obspy/taup/slowness_model.html),
            # but there doesn't seem to be any obvious solution.  This
            # only turned up when searching for nearby quakes, so all
            # of these are in North America. Given that, I'm going to
            # add a wild-ass guess derived from eyeballing travel
            # times for quakes within 1000km.
            print(
                f"Can't process quake {event._location}, {quaketime}: {e} -- will estimate time"
            )
            # Wild-ass guess:  about 15 seconds per 100 km
            arr_time = 15 * (distance / 100)
            first_arr = event._time + arr_time
            first_arr = datetime.utcfromtimestamp(first_arr).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            first_arr = f"ESTIMATE: {first_arr}"
        t.add_row(
            [
                quaketime,
                event._location,
                f"{event._mag:.2f}",
                int(distance),
                first_arr,
            ]
        )

    # print(t.get_string(sortby="Time", reversesort=True))
    print(t)


@click.command(
    "script_report", short_help="query earthquakes, and print report.py commands"
)
@click.option(
    "--feed",
    type=click.Choice(list(USGS_FEEDS.keys())),
    default="LAST_DAY_OVER_4_POINT_5",
    show_default=True,
    help="Feed to use",
)
@click.option(  # FIXME: This should be broken out
    "--distance-only/--no-distance-only",
    default=False,
    help="Just list earthquakes with distance from station",
)
def script_report(feed, distance_only):
    """
    Main entry point
    """
    quakes = get_quakes_from_feed(feed)
    stn = Station(cfg_file="report.ini")

    # TODO: We should be parsing this w/geojson
    for quake in quakes["features"]:
        lon_e, lat_e, depth = quake["geometry"]["coordinates"]
        event = Event(
            lat=lat_e,
            lon=lon_e,
            depth=depth,
            mag=quake["properties"]["mag"],
            time=quake["properties"]["time"] / 1000,  # ms since epoch
            event_id=quake["properties"]["code"],
            location=quake["properties"]["place"],
            url=quake["properties"]["url"],
        )
        time_e_formatted = datetime.utcfromtimestamp(event._time).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )

        distance = event.calculate_distance(stn=stn)
        #: FIXME: This is so not done yet
        if distance_only:
            print(
                f"Distance: {distance}, " f"Mag: {event._mag}, ",
                f"Event ID: {event._event_id}",
                f"Location: {event_location}, ",
                f"Time: {time_e_formatted}, ",
            )
            continue
        print(
            f"./src/report.py main_plot "
            + f"--lat_e {event._lat} "
            + f"--lon_e {event._lon} "
            + f"--depth {event._depth} "
            + f"--mag {event._mag} "
            + f"--time_e {time_e_formatted} "
            + f"--event_id {event._event_id} "
            + f'--location "{event._location}" '
            + "--save_file"
            + f" # {distance}"
        )
        print("sleep $(($RANDOM % 60))")


usgs.add_command(script_report)
usgs.add_command(pretty_table)

if __name__ == "__main__":
    usgs()
