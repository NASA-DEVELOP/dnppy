from dnppy import download
from dnppy import core

__all__=['dl_test_data']          # planned development

def dl_test_data(landsat_list, outdir):
    """
    Downloads a dataset for testing from Landsat 4, 5, 7, or 8

    *Note that for Landsat 4, 5, and 7 you must be signed into earthexplorer.usgs.gov
    *The Landsat 8 dataset is hosted on Amazon Web Services and is freely accessible
    
    Inputs:
      landsat   A list of [4, 5, 7, and/or 8] - the desired Landsat satellites to sample data from
      outdir    Output directory to save the downloaded dataset
    """

    core.enforce.enf_list(landsat_list)
    urls_dl = []
    
    for landsat in landsat_list:
        if landsat == 8:
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
        elif landsat == 7:
            url = "http://earthexplorer.usgs.gov/download/3372/LE70410362003114EDC00/STANDARD"
            name = "LE70410362003114EDC00"
            urls_dl.append(url)
        elif landsat == 5:
            url = "http://earthexplorer.usgs.gov/download/3119/LT50410362011208PAC01/STANDARD"
            name = "LT50410362011208PAC01"
            urls_dl.append(url)
        elif landsat == 4:
            url = "http://earthexplorer.usgs.gov/download/3119/LT40410361990014XXX01/STANDARD"
            name  = "LT40410361990014XXX01"
            urls_dl.append(url)
        else:
            print "Please enter 4, 5, 7, and/or 8 in list format"

    download.urls(urls_dl, ["TIF","txt","gz"], outdir)
    
    return