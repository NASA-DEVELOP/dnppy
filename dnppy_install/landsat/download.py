import urllib
import webbrowser
from dnppy import download
from dnppy import core

__all__=['test_data'             # completed
         'landsat_8_series']        # planned development

def test_data(landsat_number):
    """
    Downloads a dataset for testing from Landsat 4, 5, 7, or 8

    *Note that you must be signed into earthexplorer.usgs.gov
    
    Inputs:
      landsat_number   4, 5, 7, or 8 - the desired Landsat satellites to sample data from

    """
    
    landsat = int(landsat_number)
    
    if landsat == 8:
        url = "http://earthexplorer.usgs.gov/download/4923/LC80410362014232LGN00/STANDARD"
        webbrowser.open(url)
    elif landsat == 7:
        url = "http://earthexplorer.usgs.gov/download/3372/LE70410362003114EDC00/STANDARD"
        webbrowser.open(url)
    elif landsat == 5:
        url = "http://earthexplorer.usgs.gov/download/3119/LT50410362011208PAC01/STANDARD"
        webbrowser.open(url)
    elif landsat == 4:
        url = "http://earthexplorer.usgs.gov/download/3119/LT40410361990014XXX01/STANDARD"
        webbrowser.open(url)
    else:
        print "Please enter 4, 5, 7, or 8"
    
    return

def landsat_8_series(path, row, start_day, end_day, outdir):
    """
    An idea for making use of the amazon web service hosted Landsat 8 OLI data.
    This will allow a user to identify the path/row and range of days to automatically download
    a time series of OLI data. The code below downloads each band tiff on the given url.
    """

    urls_dl = []
    url = "https://s3-us-west-2.amazonaws.com/landsat-pds/L8/041/036/LC80410362014280LGN00/"
    name = "LC80410362014280LGN00"
    i = 1
    while i <= 11:
        filename = url + name + "_B{0}.TIF".format(i)
        urls_dl.append(filename)
        i = i + 1
    BQA = url + name + "_BQA.TIF"
    urls_dl.append(BQA)
    meta = url + name + "_MTL.txt"
    urls_dl.append(meta)
    outfolder = "{0}\{1}".format(outdir, name)
    download.urls(urls_dl, ["TIF","txt"], outdir)
