__author__ = 'jwely'

from download_url import *

from datetime import timedelta, datetime
import os

def fetch_MPE(start_dto, end_dto, outdir, area = None):
    """
    Fetches Multisensor Precipitation Estimates data from
    weather/noaa server at:
        [http://water.weather.gov/precip/p_download_new/]

    Inputs:
        start_dto        datetime object for start date of desired range
        end_dto          datetime object for end date of desired range
        outdir           output directory where files should be saved (str)
        area             area of interest, either "conus", "ak" or "pr"
                         for continental us, alaska, or puerto rico respectively
    """

    # set defaults
    if area is None:
        area = "conus"

    server = "http://water.weather.gov"

    # use start and end datetimes to build list of dates
    dates = []
    output_files = []
    date_delta = end_dto - start_dto

    for i in range(date_delta.days +1):
        dates.append(start_dto + timedelta(days = i))

    # try to download all files for dates
    for date in dates:
        workdir = "/".join([server, "precip","p_download_new",
                            str(date.year),
                            str(date.month).zfill(2),
                            str(date.day).zfill(2)])

        filename = "nws_precip_{0}_{1}{2}{3}.nc".format(area,
                                                        str(date.year),
                                                        str(date.month).zfill(2),
                                                        str(date.day).zfill(2))
        try:
            full_url = "/".join([workdir, filename])
            outname = os.path.join(outdir, filename)
            download_url(full_url, outname)
            output_files.append(outname)
            print("Downloaded '{0}'".format(filename))

        except:
            print("Could not find MPE data for '{0}' on {0}".format(area, date))

    return output_files


if __name__ == "__main__":
    startdto = datetime(2015,1,1)
    enddto   = datetime(2015,12,31)
    fetch_MPE(startdto, enddto, r"C:\Users\jwely\Desktop\troubleshooting\MPE")