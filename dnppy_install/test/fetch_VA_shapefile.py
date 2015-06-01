__author__ = 'jwely'

import os
import urllib
import zipfile


def fetch_VA_shapefile(test_dir):
    """
    downloads and unzips a shape file of VA for testing purposes
    """

    # set up path names
    url     = "http://www2.census.gov/geo/tiger/TIGER2013/COUSUB/tl_2013_51_cousub.zip"
    subdir  = os.path.join(test_dir, "raw", "VA_shapefile")
    fname   = os.path.join(subdir, "VA_shapefile.zip")

    if not os.path.exists(subdir):
        os.makedirs(subdir)

    # download the file
    urllib.urlretrieve(url, fname)

    # unzip it
    with zipfile.ZipFile(fname, "r") as z:
        z.extractall(os.path.join(test_dir, subdir))

    # delete the zip file
    os.remove(fname)

    print("Downloaded Virginia shapefile to {0}".format(os.path.join(test_dir,subdir)))
    shapefile_path = os.path.join(test_dir, subdir, "tl_2013_51_cousub.shp")

    return shapefile_path