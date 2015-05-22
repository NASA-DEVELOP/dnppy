__author__ = 'jwely'

from dnppy import core
from download_url import download_url
import os
import zipfile

def fetch_SRTM(lat_lon_pairs, product, outdir = None):
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

    Example:
        lat_lons = [(37,-76), (37,-77)]    # Two tiles
        prod = SRTMGL3                     #3 arc second DEM product)

        download.fetch_SRTM(lat_lons, prod)

    NOTE: arcmap will open the output hgt files ONLY if they are not renamed.
    turns out the way arcmap determines these are SRTM files is a cheap hack.
    """
    # sanitize input list
    lat_lon_pairs = core.enf_list(lat_lon_pairs)

    # determine product version
    if product is "SRTMGL30":
        raise Exception("This product is not yet supported, download it directly")
    else:
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

        # build up the filename and file link
        filename = "{0}{1}{2}{3}.{4}.hgt.zip".format(NS,
                                                     str(abs(lat)).zfill(2),
                                                     EW,
                                                     str(abs(lon)).zfill(3),
                                                     product)
        filelink = "{0}/{1}".format(subhost, filename)

        # decide where to put the file, then download it
        if outdir is not None:
            outpath  = os.path.join(outdir,filename)
        else:
            outpath = filename

        print("Downloading and extracting  {0}".format(filename))
        download_url(filelink, outpath)

        # unzip the file and reassemble descriptive name
        with zipfile.ZipFile(outpath, "r") as z:
            layername = filename[:7] + '.hgt'
            z.extractall(outdir)
            z.close()

        os.remove(outpath)

    return

if __name__ == "__main__":

    testdir = r"C:\Users\jwely\Desktop\troubleshooting"
    fetch_SRTM((37, -77), "SRTMGL1", testdir)



