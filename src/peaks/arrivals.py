from scipy.signal import find_peaks
from loguru import logger


def find_arrivals_in_data(data, height, arrs):
    """
    Find peaks in data & see if they match arrival times
    """
    peaks = find_peaks(data, height=height, width=100)[0]
    logger.debug(f"{peaks=}")
    # 100 Hz sample rate
    # I *think* we need to add delay here?
    peak_times = [x/100 + 360 for x in peaks]
    # Arrival times after beginning of data in seconds
    logger.debug(f"{peak_times=}")
    logger.debug(arrs)

