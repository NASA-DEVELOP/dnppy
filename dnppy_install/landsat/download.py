
import urllib
import urllib2
import os
from dnppy import download
from dnppy import core


__all__=['dl_test_data']          # planned development



def dl_test_data(landsat, outdir):
    """
    Downloads a dataset for testing from Landsat 4, 5, 7, or 8
    
    Inputs:
      landsat   4, 5, 7, or 8 - the desired Landsat satellite to sample data from
      outdir    Output directory to save the downloaded dataset
    """

##    if landsat == 8:
##        url = "https://s3-us-west-2.amazonaws.com/landsat-pds/L8/090/067/LC80900672015002LGN00/index.html"
##        name = "LC80900672015002LGN00"
##        i = 1
##        while i <= 11:
##            filename = name + "_B{0}.TIF".format(i)
##            urllib.urlretrieve(url, filename)
##              i = i + 1
##    elif landsat == 7:
##        url = ""
##    elif landsat == 5:
##        url = ""
##    elif landsat == 4:
##        url = ""
##    else:
##        print "Please enter 4, 5, 7, or 8 for your desired Landsat dataset"
    if landsat == 8:
        url = "https://s3-us-west-2.amazonaws.com/landsat-pds/L8/090/067/LC80900672015002LGN00/"
        filename = "LC80900672015002LGN00_B1.TIF"
        url_dl = url+filename
        urls_dl = []
        urls_dl.append(url_dl)
        download.urls(urls_dl, "TIF", outdir)
    
    return
