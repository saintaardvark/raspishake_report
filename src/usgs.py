#!/usr/bin/env python3

import configparser
from datetime import datetime
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
def pretty_table(feed):
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
    for event in sorted(all_events, key=lambda x: x._time):
        arrs = event.get_arrival_times(stn)
        first_arr = event._time + arrs[0].time
        t.add_row(
            [
                datetime.utcfromtimestamp(event._time).strftime("%Y-%m-%d %H:%M:%S"),
                event._location,
                event._mag,
                int(event.calculate_distance(stn)),
                datetime.utcfromtimestamp(first_arr).strftime("%Y-%m-%d %H:%M:%S"),
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
