"""
    @author : Grant Mercer
    gmercer015@gmail.com

    This script connects to http://water.weather.gov/precip/download.php
    and downloads all files from the specified start_date to end_date
    below. The downloaded files are initially in .tar.gz format and will
    be extracted and renamed to the yearmonthday.

"""
import os
from dateutil import rrule
from datetime import datetime, timedelta

# this is the part of the tar that remains the same no matter which day 
# we're downloading from
static_path = "nws_precip_1day_observed_shape_"

# loop through each day from start to end, yield the corresponding day
def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

# rename all files in the directory
def renameall(file_name, fdir):
    for fn in os.listdir(fdir + "/"):
        if fn.startswith("nws"):
            idx = fn.find(file_name)
            os.rename(fdir + "/" + fn, fdir + "/" + fn[idx:])
    os.remove(fdir + "/" + file_name + ".tar.gz")
    os.remove(fdir + "/" + file_name + ".tar")

# main part of the script, loops through the passed start and end date
# and calls wget and 7z to extract and rename all files
def getandextract(start_date, end_date):
    # if the directory does not exist, create it
    for date in daterange(start_date, end_date):
        if not os.path.exists("%04d" % date.year) : os.makedirs("%04d" % date.year)
        # create some variables for use with wget and such
        file_append = static_path + "%04d" % date.year + "%02d" % date.month + "%02d" % date.day + ".tar.gz"
        file_out = "%04d" % date.year + "%02d" % date.month + "%02d" % date.day
        fdir = "%04d" % date.year

        # string to be passed into os which calls wget and the corresponding file to download
        proc_wget = "wget -nd -O " + "%04d" % date.year + "/" + file_out + \
                ".tar.gz" + " http://water.weather.gov/precip/p_download_new/" + \
                "%04d" % date.year + "/" + "%02d" % date.month + "/" + \
                "%02d" % date.day + "/" + file_append

        # extract is two steps, extract to tar ... extract to files
        extract = ["7z e -o" + fdir + "/" + " " + fdir + "/" + file_out + ".tar.gz", 
                   "7z x -o" + fdir + "/" + " " + fdir + "/" + file_out + ".tar" ]

        # calls wget -> extract step 1 -> extract step 2 -> rename files
        os.system(proc_wget)
        os.system(extract[0])
        os.system(extract[1])
        renameall(file_out, fdir)


# GRAB DATES
#   range : 2010 - 2011
start_date = datetime(2011, 12, 27)
end_date = datetime(2011, 12, 31)
getandextract(start_date, end_date)

# GRAB DATES
#   range : 2014 - 2015
start_date = datetime(2014, 01, 01)
end_date = datetime(2015, 12, 31)
getandextract(start_date, end_date)
