__author__ = 'jwely'

import urllib

def list_http_e4ftl01(site):
    """
    Lists contents of  http download site at [http://e4ftl01.cr.usgs.gov]
    which hosts select MODIS products, landsat WELD, and SRTM data.
    """

    website = urllib.urlopen(site)
    string  = website.readlines()

    files = []
    for line in string:
        try:
            files.append(line.replace('/','').split('"')[5])
        except:
            pass
    return files