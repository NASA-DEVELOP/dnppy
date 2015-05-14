__author__ = 'jwely'

import urllib

def list_http(site):
    """Lists contents of typical http download site at [http://e4ftl01.cr.usgs.gov]"""

    website = urllib.urlopen(site)
    string  = website.readlines()

    files = []
    for line in string:
        try:
            files.append(line.replace('/','').split('"')[5])
        except:
            pass
    return files