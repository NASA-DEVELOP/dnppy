__author__ = 'jwely'

from dnppy import download
import os

def fetch_test_MODIS(test_dir):
    """
    Fetches MODIS test data with dnppy download module

    Data is targeted for February of 2015, but some data is 16-day
    and yearly which extends outside that boundary.
    """

    if not os.path.exists(test_dir):
        os.makedirs(os.path.join(test_dir, "raw"))

    print("Downloading MODIS test data!")
    # set up universal MODIS parameters
    modis_dir = os.path.join(test_dir,"raw","MODIS")
    years = [2015]
    days  = range(31,60)
    tiles = ['h11v05','h12v05']

    # download some test products

    prod = "MCD12Q1"    # yearly land cover type
    vers = "051"
    outdir = os.path.join(modis_dir, prod)
    download.fetch_MODIS(prod, vers, tiles, outdir, years)

    prod = "MOD13A1"    # 16 day vegetation indices
    vers = "005"
    outdir = os.path.join(modis_dir, prod)
    download.fetch_MODIS(prod, vers, tiles, outdir, years, days)

    prod = "MYD13A1"    # 16 day vegetation indices
    vers = "005"
    outdir = os.path.join(modis_dir, prod)
    download.fetch_MODIS(prod, vers, tiles, outdir, years, days)


    prod = "MYD11A1"    # daily surface temperature
    vers = "041"
    outdir = os.path.join(modis_dir, prod)
    download.fetch_MODIS(prod, vers, tiles, outdir, years, days)

    prod = "MOD10A1"    # daily snow cover
    vers = "005"
    outdir = os.path.join(modis_dir, prod)
    download.fetch_MODIS(prod, vers, tiles, outdir, years, days)

    prod = "MYD09A1"    # daily 500m surface reflectance
    vers = "005"
    outdir = os.path.join(modis_dir, prod)
    download.fetch_MODIS(prod, vers, tiles, outdir, years, days)

    prod = "MOD09A1"    # daily 500m surface reflectance
    vers = "005"
    outdir = os.path.join(modis_dir, prod)
    download.fetch_MODIS(prod, vers, tiles, outdir, years, days)
    return