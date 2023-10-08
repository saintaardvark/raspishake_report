import requests

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


class InvalidFeed(Exception):
    """
    Custom exception for invalid feeds
    """


def get_quakes_from_feed(feed: str):
    """
    Query feed & return quakes
    """
    feed_url = ""
    try:
        feed_url = USGS_FEEDS[feed]
    except IndexError:
        raise InvalidFeed(
            "Invalid choice for feed! Valid options: {}".format(
                ", ".join(list(USGS_FEEDS.keys()))
            )
        )
    resp = requests.get(feed_url)
    return resp.json()
