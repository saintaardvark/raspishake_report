#!/usr/bin/env python3

import configparser
from datetime import datetime
import json
import requests

import click
from loguru import logger
from obspy.core import UTCDateTime

USGS_FEEDS = {
    "LAST_DAY_OVER_4_POINT_5": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson",
    "LAST_DAY_OVER_2_POINT_5": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson",
    "LAST_DAY_OVER_1_POINT_0": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/1.0_day.geojson",
    "LAST_WEEK_OVER_4_POINT_5": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_week.geojson",
    "LAST_WEEK_OVER_2_POINT_5": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_week.geojson",
    "LAST_WEEK_OVER_1_POINT_0": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/1.0_week.geojson",
}


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
        config = configparser.ConfigParser()
        config.read("report.ini")
        filename = (
            config["DEFAULT"]["output_dir"]
            + "/"
            + f"{str(mag)}_Quake_{location}_{event_id}-"
            + eventTime.strftime("%Y-%m-%dT%H:%M:%S_UTC-")
            + pfile
            + ".png"
        )
        quake["properties"][
            "report_url"
        ] = f"https://home.saintaardvarkthecarpeted.com/earthquake_data/{filename}"
        for i in [
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
        ]:
            quake["properties"].pop(i, None)

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
def query(feed):
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

    # TODO: We should be parsing this w/geojson
    for quake in quakes["features"]:
        lon_e, lat_e, depth = quake["geometry"]["coordinates"]
        mag = quake["properties"]["mag"]
        time_e = quake["properties"]["time"] / 1000  # ms since epoch
        time_e_formatted = datetime.utcfromtimestamp(time_e).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )

        event_id = quake["properties"]["code"]
        location = quake["properties"]["place"]
        url = quake["properties"]["url"]
        print(
            f"./src/init/report.py main_plot "
            + f"--lat_e {lat_e} "
            + f"--lon_e {lon_e} "
            + f"--depth {depth} "
            + f"--mag {mag} "
            + f"--time_e {time_e_formatted} "
            + f"--event_id {event_id} "
            + f'--location "{location}" '
            + "--save_file"
        )
        print("sleep $(($RANDOM % 60))")


usgs.add_command(query)
usgs.add_command(build_db)

if __name__ == "__main__":
    usgs()
