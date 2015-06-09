__author__ = ['jeff.ely.08@gmail.com']

from list_ftp import list_ftp
from download_url import download_url


from datetime import datetime, timedelta

import os

def fetch_GPM_IMERG(start_dto, end_dto, outdir, product = "gis", time_res = "1day"):

    """
    Fetches 30 minute resolution GPM IMERG data from an ftp server. Several restrictions exist
    for this relatively new dataset, please read in the input section carefully.

       http://pps.gsfc.nasa.gov/Documents/GPM_Data_Info_140616.pdf

     Input:
       start_dto    datetime object for starting time of study boundary
       end_dto      datetiem object for ending time of study boundary
       outdir       output directory to save the data
       product      either "early" , "late" or "final" for full HDF5 data stacks of the respective runs,
                    which are all at 30minute resolutions. OR product can be set equal to "gis"
                    (default) to find only tif averages of the precipitation estimates. This gis
                    tif data is only provided for data less than one year old.
       time_res     if "product"  is set to "gis", specify what time average period you want. options
                    are "30min", "3hr", "1day", "3day", "7day". Defaults to "1day"

       learn more at the link below
       [http://pmm.nasa.gov/data-access/downloads/gpm]
    """

    # set up empty list of downloaded filepaths on local dir
    download_list = []

    # username and password info, should eventually be some DEVELOP credential.
    # this information is not at all sensitive.
    un = "jeff.ely.08@gmail.com"
    pw = "jeff.ely.08@gmail.com"


    # special filtering for gis type tif data to minimize data representation overlap.
    if product == "gis":
        if time_res == "30min":
            ok_minutes = [str(x).zfill(4) for x in range(0, 1440, 30)]
        elif time_res == "3hr":
            ok_minutes = [str(x).zfill(4) for x in range(0, 1440, 180)]
        else:
            ok_minutes = "0000"


    # assemble address information
    pps_server  = r"ftp://jsimpson.pps.eosdis.nasa.gov"

    # set product directory
    prod_server = "/".join(["NRTPUB/imerg", product])

    # log in and list available month folders.
    foldnames, foldpaths = list_ftp(pps_server,
                                    dir = prod_server,
                                    username = un,
                                    password = pw)

    # perform a simple quick filtering of folders that definitely don't have data we want.
    for foldname in foldnames:
        try:
            int(foldname)
        except:
            foldnames.remove(foldname)



    for foldname in foldnames:
        print("exploring directory '{0}'".format(foldname))
        subdir = "/".join([prod_server, foldname])
        filenames, filepaths = list_ftp(pps_server,
                                        dir = subdir,
                                        username = un,
                                        password = pw)

        for filepath in filepaths:
            filename = os.path.basename(filepath)
            finfo = filename.split(".")
            prod       = finfo[3]
            date_cords = finfo[4]
            minutes    = finfo[5]
            time       = finfo[7]

            date_str = date_cords.split("-")[0]
            date = datetime.strptime(date_str, "%Y%m%d") + timedelta(minutes = int(minutes))

            # see if this file meets criteria for download
            good_date = start_dto <=  date  <= end_dto

            if product == "gis":
                good_minutes = minutes in ok_minutes
                good_time    = time_res == time
            else:
                good_minutes = True
                good_time    = True

            # download the files
            if good_date and good_time and good_minutes:
                outname = os.path.join(outdir, date.strftime("%Y-%m-%d"), filename)
                download_url(filepath, outname, username = un, password = pw)
                download_list.append(outname)
                print("saved '{0}' in '{1}'".format(filename, outdir))

    return download_list


if __name__ == "__main__":

    start_dto = datetime(2015,4,2)
    end_dto   = datetime(2015,4,3)
    testdir   = r"C:\Users\Jeff\Desktop\GPM_testing"

    prod = "late"
    time = "3day"

    download_list = fetch_GPM_IMERG(start_dto, end_dto, testdir, product = prod, time_res = time)