#!/usr/bin/env python3

import configparser
from datetime import datetime
import json
import math
import requests

import click
from loguru import logger
from obspy.core import UTCDateTime

from util import generate_report_url

from travel_times import Station, Event

USGS_FEEDS = {
    "LAST_DAY_OVER_4_POINT_5": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson",
    "LAST_DAY_OVER_2_POINT_5": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson",
    "LAST_DAY_OVER_1_POINT_0": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/1.0_day.geojson",
    "LAST_WEEK_OVER_4_POINT_5": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_week.geojson",
    "LAST_WEEK_OVER_2_POINT_5": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_week.geojson",
    "LAST_WEEK_OVER_1_POINT_0": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/1.0_week.geojson",
}

UNWANTED_GEOJSON_COLS = [
    "updated",
    "tz",
    "detail",
    "felt",
    "cdi",
    "mmi",
    "alert",
    "status",
    "ids",
    "sources",
    "types",
    "nst",
    "gap",
    "magType",
    "net",
    "dmin",
    "sig",
    "rms",
]


@click.group()
def usgs():
    """A tool to query the USGS for earthquake data, and to generate
    commands to run reports on them.
    """


@click.command("build_db", short_help="Build/update sqlite db")
@click.option(
    "--feed",
    type=click.Choice(list(USGS_FEEDS.keys())),
    default="LAST_DAY_OVER_4_POINT_5",
    show_default=True,
    help="Feed to use",
)
def build_db(feed):
    """
    Build/update sqlite db
    """
    # FIXME: Copy-pasta of query()
    feed_url = ""
    try:
        feed_url = USGS_FEEDS[feed]
    except IndexError:
        print("Invalid choice for feed!  Valid options: ")
        print(", ".join(list(USGS_FEEDS.keys())))

    logger.debug(f"Getting {feed_url}...")
    resp = requests.get(feed_url)
    quakes = resp.json()
    logger.debug(f"Got {len(quakes['features'])} quakes")
    for quake in quakes["features"]:
        # TODO: This is *huge* code duplication
        event_id = quake["properties"]["code"]
        logger.debug(f"Got {event_id=}")
        mag = quake["properties"]["mag"]
        location = quake["properties"]["place"]

        eventTime = UTCDateTime(quake["properties"]["time"] / 1000)  # ms since epoch
        pfile = "All"
        quake["properties"]["report_url"] = generate_report_url(event_id, eventTime)
        logger.debug(f"URL: {quake['properties']['report_url']}")
        for i in UNWANTED_GEOJSON_COLS:
            quake["properties"].pop(i, None)

        quake["properties"]["time"] = int(quake["properties"]["time"] / 1000)

    local_filename = feed_url.split("/")[-1]
    with open(local_filename, "w") as f:
        f.write(json.dumps(quakes, indent=2))




@click.command("query", short_help="query earthquakes")
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
def query(feed, distance_only):
    """
    Main entry point
    """
    feed_url = ""
    try:
        feed_url = USGS_FEEDS[feed]
    except IndexError:
        print("Invalid choice for feed!  Valid options: ")
        print(", ".join(list(USGS_FEEDS.keys())))
    resp = requests.get(feed_url)
    quakes = resp.json()
    # print(json.dumps(quakes, indent=2))

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


usgs.add_command(query)
usgs.add_command(build_db)

if __name__ == "__main__":
    usgs()
