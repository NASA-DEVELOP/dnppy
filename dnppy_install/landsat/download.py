#local imports
from .atsat_bright_temp import *
from .cloud_mask import *
from .grab_meta import *
from .ndvi import *
from .scene import *
from .surface_temp import *
from .toa_radiance import *
from .toa_reflectance import *
from .download import *

#external imports
import urllib
import webbrowser
import site
import datetime
from dnppy import download
from dnppy import core

__all__=['test_data',           # completed
         'landsat_8_scene',     # completed
         'landsat_8_series']    # planned development

def test_data(landsat_number):
    """
    Downloads a dataset for testing from Landsat 4, 5, 7, or 8

    *Note that you must be signed into earthexplorer.usgs.gov
    
    Inputs:
      landsat_number:   4, 5, 7, or 8 - the desired Landsat satellites to sample data from

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

def landsat_8_scene(path, row, year, day, outdir):
    """
    This function makes use of the amazon web service hosted Landsat 8 OLI data.
    This allows the user to identify the path/row and year/day to automatically download
    a scene of OLI data. The code below downloads each band tiff in the dataset.

    *Note: for best results, enter number inputs in quotemarks as strings.
    Some identifier integers may be read by Python wrong (e.g. 010 is read as 8 in binary)

    *You can use this tool to find the Path/Row values based on Latitude/Longitude coordinates.
    https://landsat.usgs.gov/tools_latlong.php

    *You can refer to this table to find the Julian Day value for your desired dataset
    http://amsu.cira.colostate.edu/julian.html
    
    Inputs:
        path:   the Landsat path number for the desired dataset
        row:    the Landsat row number for the desired dataset
        year:   the four digit year number the desired dataset was created
        day:    the three digit Julian Day number the desired dataset was created (e.g. January 1 = 001)
        outdir: the output location for the downloaded Landsat 8 dateset
        
    """

    urls_dl = []

    path_str = str(path)
    row_str = str(row)
    year_str = str(year)
    day_str = str(day)

    if len(path_str) == 2:
        path_str = "0" + path_str
    elif len(path_str) == 1:
        path_str = "00" + path_str
    if len(row_str) == 2:
        row_str = "0" + row_str
    elif len(row_str) == 1:
        row_str = "00" + row_str
    if len(day_str) == 2:
        day_str = "0" + day_str
    elif len(day_str) == 1:
        day_str = "00" + day_str

    name = "LC8{0}{1}{2}{3}LGN00".format(path_str, row_str, year_str, day_str)
    url = "https://s3-us-west-2.amazonaws.com/landsat-pds/L8/{0}/{1}/{2}/".format(path_str, row_str, name)

    i = 1
    while i <= 11:
        filename = "{0}{1}_B{2}.TIF".format(url,name,i)
        urls_dl.append(filename)
        i = i + 1
    BQA = url + name + "_BQA.TIF"
    urls_dl.append(BQA)
    meta = url + name + "_MTL.txt"
    urls_dl.append(meta)
    outfolder = "{0}\{1}".format(outdir, name)
    download.urls(urls_dl, outfolder, ["TIF","txt"])
    
    return

def landsat_8_series(path, row, start_date, end_date, outdir):
    """
    An idea for making use of the amazon web service hosted Landsat 8 OLI data.
    This will allow a user to identify the path/row and year/day to automatically download
    a time series of OLI data. The code below downloads each band tiff on the given url.

    Inputs:
    path:       the path number for the desired scene series, entered preferably as a
                    three-digit string, e.g. "xxx"
    row:        the row number for the desired scene series, entered preferably as a
                    three-digit string, e.g. "xxx"
    start_date: year-month-day ("xxxx-xx-xx" or "xxxx/xx/xx")
    end_date:   year-month-day ("xxxx-xx-xx" or "xxxx/xx/xx")
    outdir:     the folder to save the output files in
    """

    int_eday = int(end_date[8:10])
    int_sday = int(start_date[8:10])
    int_emonth = int(end_date[5:7])
    int_smonth = int(start_date[5:7])
    int_eyear = int(end_date[0:4])
    int_syear = int(start_date[0:4])

    path_str = str(path)
    row_str = str(row)

    if len(path_str) == 2:
        path_str = "0" + path_str
    elif len(path_str) == 1:
        path_str = "00" + path_str
    if len(row_str) == 2:
        row_str = "0" + row_str
    elif len(row_str) == 1:
        row_str = "00" + row_str

    directory = site.getsitepackages()[1]
    scene_list = "{0}\\dnppy\\landsat\\metadata\\scene_list.txt".format(directory)

    f = open(scene_list, 'r')
    content = f.readlines()

    start_dtdate = datetime.date(int_syear, int_smonth, int_sday)
    end_dtdate = datetime.date(int_eyear, int_emonth, int_eday)

    x = 1
    for line in content:
        year = int(content[x][22:26])
        month = int(content[x][27:29])
        day = int(content[x][30:32])
        date = datetime.date(year, month, day)
        pathrow_id = "LC8{0}{1}".format(path_str, row_str)
        if pathrow_id in content[x]:
            if date >= start_dtdate and date <= end_dtdate:
                jday = content[x][13:16]
                landsat_8_scene(path_str, row_str, year, jday, outdir)
        x = x + 1
        if date > end_dtdate:
            break

    return
