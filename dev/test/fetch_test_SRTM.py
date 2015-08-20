__author__ = 'jwely'

from dnppy import download
import os
import arcpy

def fetch_test_SRTM(test_dir):
    """
    grabs two example setss of SRTM data. One at low resolution for
    the state of VA, and some at high resolution for the LA metro area
    """

    srtm_dir = os.path.join(test_dir,"raw", "SRTM")
    dem_dir  = os.path.join(test_dir,"pre_processed", "SRTM")

    if not os.path.exists(srtm_dir):
        os.makedirs(srtm_dir)
        os.makedirs(dem_dir)

    # start with a DEM for hampton roads VA.
    print("Downloading SRTM test data for Hampton Roads VA!")
    lat_lon_pairs = [(37,-77),(37,-78),(37,-76),
                     (36,-77),(36,-78),(36,-76),
                     (38,-77),(38,-78),(38,-76)]

    dem_files = download.fetch_SRTM(lat_lon_pairs, "SRTMGL3", srtm_dir)
    arcpy.MosaicToNewRaster_management(dem_files, dem_dir, "VAcoast_DEM.tif",
                                       number_of_bands = 1, pixel_type = "32_BIT_SIGNED")

    # grab a DEM for the Los Angeles metro area
    print("Downloading SRTM test data for Los Angeles metro area!")
    lat_lon_pairs = [(34,-118),(34,-119),(34,-120),(34,-117),
                     (35,-118),(35,-119),(35,-120),(35,-117),
                     (33,-118),(33,-119),(33,-120),(33,-117)]

    dem_files = download.fetch_SRTM(lat_lon_pairs, "SRTMGL3", srtm_dir)
    arcpy.MosaicToNewRaster_management(dem_files, dem_dir, "LAmetro_DEM.tif",
                                       number_of_bands = 1, pixel_type = "32_BIT_SIGNED")

    return


if __name__ == "__main__":
    fetch_test_SRTM(r"C:\Users\jwely\Desktop\dnppytest")


