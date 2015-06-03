__author__ = ['djjensen','jwely']

from dnppy import textio
from dnppy import core
from download_url import download_url
import datetime
import urllib
import site
import os


def fetch_Landsat8(path_row_pairs, start_dto, end_dto, outdir,
                   max_cloud_cover = 100, bands = [1,2,3,4,5,6,7,8,9,10,11,"QA"]):
    """
    An idea for making use of the amazon web service hosted Landsat 8 OLI data.
    This will allow a user to identify the path/row and year/day to automatically download
    a time series of OLI data. The code below downloads each band tiff on the given url.

    Inputs:
        path_row_pairs    tupled integer values of path,row coordinates of tile.
                          may be a list of several tuples. example: [(1,1),(1,2)]
        start_dto         python datetime object of start date of range
        end_dto           python datteime object of end date of range
        outdir            the folder to save the output landsat files in
        max_cloud_cover   maximum percent cloud cover that is acceptable to download the file.
    """

    path_row_pairs = core.enf_list(path_row_pairs)

    for path_row_pair in path_row_pairs:
        #format input strings
        path, row = path_row_pair
        path_str  = str(path).zfill(3)
        row_str   = str(row).zfill(3)

        #read the scene list text file from the metadata folder in the installed dnppy package
        directory  = site.getsitepackages()[1]
        scene_list = textio.text_data(text_filepath = "{0}/dnppy/landsat/metadata/scene_list.txt".format(directory))

        #loop through the scene list
        #if the date for the given path/row scene is within the date range, download it with landsat_8_scene

        for row in scene_list:
            tilename    = row[0]
            datestring  = row[1].split(".")[0] # removes fractional seconds from datestring
            date        = datetime.datetime.strptime(datestring,"%Y-%m-%d %H:%M:%S")
            pathrow_id  = "LC8{0}{1}".format(path_str, row_str)
            cloud_cover = float(row[2])

            if cloud_cover < max_cloud_cover:
                if pathrow_id in row[0]:
                    if start_dto <=  date  <= end_dto:
                        amazon_url = row[-1]
                        fetch_Landsat8_tile(amazon_url, tilename, outdir, bands)

    print("Finished retrieving landsat 8 data!")
    return



def fetch_Landsat8_tile(amazon_url, tilename, outdir, bands = [1,2,3,4,5,6,7,8,9,10,11,"QA"]):
    """
    This function makes use of the amazon web service hosted Landsat 8 OLI data.
    It recieves an amazon web url for a single landsat tile, and downloads the desired files

    defaults to downlod all bands, but users can call
        bands = [1,2,3,4,5,6,7,8,9,10,11,"QA"] to control which files are downloaded.
        The MTL file is ALWAYS downloaded.
    """

    bands = map(str,core.enf_list(bands))

    #create the scene name from the input parameters and use that to generate the scene's unique url
    connection = urllib.urlopen(amazon_url)
    page       = connection.read().split("\n")

    print("Downloading landsat tile {0}".format(tilename))
    for line in page:
        if "<li><a href=" in line:

            # pull filename from html code
            filename = line.split('"')[1]

            # pull out band information
            band_id   = filename.replace(tilename + "_","").split(".")[0].replace("B","")
            good_band = band_id in bands
            mtl_file  = "MTL" in band_id

            # download desired files.
            if good_band or mtl_file:
                link     = amazon_url.replace("index.html",filename)
                savename = os.path.join(outdir, tilename, filename)
                download_url(link, savename)
                print("\tDownloaded {0}".format(filename))
    return


if __name__ == "__main__":

    outdir = r"C:\Users\jwely\Desktop\troubleshooting\2015-summer\alaskdisasters"
    start = datetime.datetime(2015,1,1)
    end   = datetime.datetime(2015,6,3)
    path_row_pairs = [(56,21),(56,22)]

    fetch_Landsat8(path_row_pairs, start, end, outdir, bands = 1)