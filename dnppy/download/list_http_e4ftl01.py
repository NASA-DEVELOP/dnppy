__author__ = 'jwely'

import urllib

__all__ = ["list_http_e4ftl01"]

def list_http_e4ftl01(site):
    """
    Lists contents of  http download site at [http://e4ftl01.cr.usgs.gov]
    which hosts select MODIS products, landsat WELD, and SRTM data.

    :param site: a url to somewhere on the server at http://e4ftl01.cr.usgs.gov

    :return file_urls: returns a list of urls to files on that http page.
    """

    website = urllib.urlopen(site)
    string  = website.readlines()

    file_urls = []
    for line in string:
        try:
            file_urls.append(line.replace('/','').split('"')[5])
        except:
            pass
    return file_urls