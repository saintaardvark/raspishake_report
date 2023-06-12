#!/usr/bin/env python3

from datetime import datetime
import json
import requests

URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"


def main():
    """
    Main entry point
    """
    resp = requests.get(URL)
    quakes = resp.json()
    print(json.dumps(quakes, indent=2))

    # TODO: We should be parsing this w/geojson
    for quake in quakes["features"]:
        lat_e, lon_e, depth = quake["geometry"]["coordinates"]
        mag = quake["properties"]["mag"]
        time_e = quake["properties"]["time"] / 1000  # ms since epoch
        time_e_formatted = datetime.fromtimestamp(time_e).strftime("%Y-%m-%dT%H:%M:%S")
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
