__author__ = 'jwely'

from fetch_test_landsat import fetch_test_landsat
from fetch_test_MODIS import fetch_test_MODIS
from fetch_VA_shapefile import fetch_VA_shapefile

def build_test_env(test_dir):
    """
    wraps each of the "fetch" functions for building a common
    testing environment for dnppy
    """

    fetch_test_landsat(test_dir)
    fetch_VA_shapefile(test_dir)
    fetch_test_MODIS(test_dir)

    return

if __name__ == "__main__":

    build_test_env(r"C:\Users\jwely\Desktop\dnppytest")