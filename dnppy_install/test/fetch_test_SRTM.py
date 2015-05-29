__author__ = 'jwely'

from dnppy import download
import os

def fetch_test_SRTM(test_dir):
    """
    grabs two example setss of SRTM data. One at low resolution for
    the state of VA, and some at high resolution for the LA metro area
    """

    if not os.path.exists(test_dir):
        os.makedirs(os.path.join(test_dir, "raw"))

    lat_lon_pairs = [(37,-77),(37,-78),(37,-76),
                     (36,-77),(36,-78),(36,-76),   # hampton roads VA
                     (38,-77),(38,-78),(38,-76)]

    print("Downloading SRTM test data!")
    srtm_dir = os.path.join(test_dir,"raw", "SRTM")
    download.fetch_SRTM(lat_lon_pairs, "SRTMGL3", srtm_dir)
    return


