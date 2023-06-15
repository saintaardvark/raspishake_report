#!/usr/bin/env python3

from datetime import datetime
import json
import requests

LAST_DAY_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"
LAST_WEEK_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_week.geojson"
LAST_DAY_25_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"
LAST_DAY_10_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/1.0_day.geojson"

def main():
    """
    Main entry point
    """
    resp = requests.get(LAST_WEEK_URL)
    quakes = resp.json()
    # print(json.dumps(quakes, indent=2))

    # TODO: We should be parsing this w/geojson
    for quake in quakes["features"]:
        lon_e, lat_e, depth = quake["geometry"]["coordinates"]
        mag = quake["properties"]["mag"]
        time_e = quake["properties"]["time"] / 1000  # ms since epoch
        time_e_formatted = datetime.utcfromtimestamp(time_e).strftime("%Y-%m-%dT%H:%M:%S")

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
            + f"--location \"{location}\""
        )


if __name__ == "__main__":
    main()
