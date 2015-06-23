__author__ = 'jwely'

from dnppy import core
from download_url import download_url
import os
import zipfile

try: import arcpy
except: pass


def fetch_SRTM(lat_lon_pairs, product, outdir = None, mosaic = None):
    """
    downloads data from the Shuttle Radar Topography Mission (SRTM)
    [http://e4ftl01.cr.usgs.gov/SRTM/]

    This data can be used to create DEMS of a variety of resolutions.

    Inputs:
        lat_lon_pairs   tupled integer values of lat,lon combinations.
                        may be a list of tuples. (N positive, E positive)
        product         short name of product you want. See link below
                        https://lpdaac.usgs.gov/products/measures_products_table
        outdir          local directory to save downloaded files
        mosaic          Set to TRUE to mosaic all downloaded DEM tiles.

    Returns:
        tif_list        a list of all successfully downloaded tif filepaths
                        for further manipulation

    Example:
        lat_lons = [(37,-76), (37,-77)]    # Two tiles
        prod = "SRTMGL3"                   #3 arc second DEM product)

        download.fetch_SRTM(lat_lons, prod)

    NOTE: arcmap will open the output hgt files ONLY if they are not renamed.
    turns out arcmap does some funky things when interpreting these files.
    """

    # build empty return list
    tif_list = []

    # sanitize input list
    lat_lon_pairs = core.enf_list(lat_lon_pairs)

    # determine product version
    if product is "SRTMGL30":
        print("Download of product SRTMGL30 is supported, but arcmap does not support this filetype")
        format_string = "{2}{3}{0}{1}.{4}.dem.zip"
        version = "002"

    else:
        format_string = "{0}{1}{2}{3}.{4}.hgt.zip"
        version = "003"


    host = "http://e4ftl01.cr.usgs.gov/SRTM"
    subhost = "{0}/{1}.{2}/2000.02.11/".format(host, product, version)

    print("Connecting to host at {0}".format(subhost))


    for lat_lon_pair in lat_lon_pairs:
        lat, lon = lat_lon_pair

        # set North-south, East-West convention.
        if lat >= 0:
            NS = "N"
        else:
            NS = "S"

        if lon >= 0:
            EW = "E"
        else:
            EW = "W"

        if product is "SRTMGL30":

            if abs(lon) <= 20:
                lon = 20
            elif abs(lon) <=60:
                lon = 60
            elif abs(lon) <= 100:
                lon = 100
            else:
                lon = 140

            if abs(lat) <= 10:
                lat = 10
            elif abs(lat) <=40:
                lat = 40
            else:
                lat = 90

            NS = NS.lower()
            EW = EW.lower()

        # build up the filename and file link
        filename = format_string.format(NS, str(abs(lat)).zfill(2),
                                        EW, str(abs(lon)).zfill(3),
                                        product)

        filelink = "{0}/{1}".format(subhost, filename)

        # decide where to put the file, then download it
        if outdir is not None:
            outpath  = os.path.join(outdir, filename)
        else:
            outpath = filename

        print("Downloading and extracting  {0}".format(filename))
        download_url(filelink, outpath)

        # unzip the file and reassemble descriptive name
        with zipfile.ZipFile(outpath, "r") as z:

            itemname = "{0}{1}{2}{3}.hgt".format(NS, str(abs(lat)).zfill(2),
                                                 EW, str(abs(lon)).zfill(3))
            z.extract(itemname, outdir)
            z.close()

        # clean up and add this file to output list
        os.remove(outpath)
        tif_list.append(os.path.join(outdir,itemname))

    if mosaic is True:

        arcpy.MosaicToNewRaster_management(tif_list, outdir, "SRTM_mosaic.tif",
                                       number_of_bands = 1, pixel_type = "32_BIT_SIGNED")

    print("Finished download and extraction of SRTM data")

    return tif_list




if __name__ == "__main__":

    testdir = r"C:\Users\Jeff\Desktop\metric_testing"
    tiles = [(44, -118),(45, -118),(46, -118),(47, -118),
             (44, -119),(45, -119),(46, -119),(47, -119),
             (44, -120),(45, -120),(46, -120),(47, -120),
             (44, -121),(45, -121),(46, -121),(47, -121),]

    fetch_SRTM(tiles, "SRTMGL3", testdir, mosaic = True)



