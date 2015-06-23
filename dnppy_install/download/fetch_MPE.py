__author__ = 'jwely'

from datetime import datetime, timedelta

def fetch_MPE(start_dto, end_dto):
    """
    Fetches Multisensor Precipitation Estimates data from
    weather/noaa server at:
        [http://water.weather.gov/precip/p_download_new/]
    """

    server = "http://water.weather.gov"

    # use start and end datetimes to build list of dates
    dates = []
    date_delta = end_dto - start_dto

    for i in range(date_delta.days +1):
        dates.append(start_dto + timedelta(days = i))

    for date in dates:
        workdir = "/".join([server, "precip","p_download_new",
                            str(date.year),
                            str(date.month),
                            str(date.day)])