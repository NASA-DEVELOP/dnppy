__author__ = 'jwely'


from dnppy import download
from datetime import datetime

import os

def fetch_test_precip(test_dir):
    """
    fetches both TRMM and GPM test data
    """

    if not os.path.exists(test_dir):
        os.makedirs(os.path.join(test_dir, "raw"))


    print("Downloading GPM IMERG test data!")
    gpmdir = os.path.join(test_dir,"raw","GPM")
    download.fetch_GPM_IMERG(datetime(2015,4,1),
                             datetime(2015,4,2),
                             outdir = gpmdir,
                             product = "late")

    print("Downloading TRMM 3b42 test data!")
    trmmdir = os.path.join(test_dir,"raw","TRMM")
    download.fetch_TRMM(datetime(2014,1,1),
                        datetime(2014,1,2),
                        outdir = trmmdir,
                        product_string = "3B42")


if __name__ == "__main__":
    fetch_test_precip(r"C:\Users\jwely\Desktop\dnppytest")
