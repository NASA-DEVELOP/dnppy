__author__ = 'jwely'

from dnppy import modis
from dnppy import raster
import os
from fetch_test_MODIS import fetch_test_MODIS
from fetch_VA_shapefile import fetch_VA_shapefile
from fetch_test_SRTM import fetch_test_SRTM

def test_raster_module(test_dir):
    """
    tests the following functions from the raster module:
        spatially_match
            cilp_and_snap
            project_resample
            enf_rastlist
                is_rast
        raster_overlap
            clip_and_snap
            null_define
            to_numpy
            from_numpy
        null_set_range
        clip_to_shape
        grab_info
    """

    # if no data folder exists at the location, build the test environment
    if not os.path.exists(os.path.join(test_dir,"raw","MODIS")):
        fetch_test_MODIS(test_dir)

    if not os.path.exists(os.path.join(test_dir,"raw","VA_shapefile")):
        fetch_VA_shapefile(test_dir)

    if not os.path.exists(os.path.join(test_dir, "raw","SRTM")):
        fetch_test_SRTM(test_dir)


    # first, lets extract some MODIS data over hampton roads
    print("preparing sample MODIS MOD10A1 data for raster opperations")
    product_dir = os.path.join(test_dir, "raw", "MODIS", "MOD10A1")
    extract_dir = os.path.join(test_dir, "pre_processed", "MODIS", "MOD10A1","0_extract")
    mosaic_dir  = os.path.join(extract_dir, "1_mosaic")

    modis.extract_from_hdf(product_dir, [3], "FracSnow", extract_dir)
    modis.mosaic(extract_dir, outdir = mosaic_dir, pixel_type = "8_BIT_UNSIGNED")


    # test spatially match function
    print("testing function 'spatially_match' and its dependencies")
    dem_path = os.path.join(test_dir, "pre_processed","SRTM","VAcoast_DEM.tif")
    sm_dir = os.path.join(test_dir,"pre_processed","MODIS","MOD10A1","2_spatially_match")

    raster.spatially_match(dem_path, mosaic_dir, sm_dir, resamp_type = "NEAREST")

    # set null values in MODIS data as well as in the DEM
    print("testing 'null_set_range' function")
    raster.null_set_range(dem_path,low_thresh = 0, NoData_Value = 0)
    raster.null_set_range(sm_dir, high_thresh = 101, NoData_Value = 101)


    # test overlap finding functions with just the first spatially matched image in modis series
    print("testing 'raster_overlap' function")
    sample_path = os.path.join(sm_dir, "MOD10A1.A2015031.mosaic.005.2015033065804_FracSnow_sm.tif")
    overshp_path = os.path.join(test_dir, "pre_processed/MODIS/MOD10A1/clip_extent/clip_extent.shp")
    raster.raster_overlap(dem_path, sample_path, overshp_path)


    # test the clip_to_shape function
    print("testing 'clip_to_shape' function")
    clipdir   = os.path.join(test_dir,"pre_processed","MODIS","MOD10A1","3_clipped")
    vashape   = os.path.join(test_dir,"raw","VA_shapefile","tl_2013_51_cousub.shp")
    raster.clip_to_shape(sm_dir, overshp_path, clipdir)



    return



if __name__ == "__main__":
    test_dir = r"C:\Users\jwely\Desktop\dnppytest"
    test_raster_module(test_dir)



