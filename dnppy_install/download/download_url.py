__author__ = 'jwely'

import urllib

def download_url(url, outname):
    """Download a single file. input source url and output filename"""

    writefile   = open(outname,'wb+')
    page        = urllib.urlopen(url).read()

    writefile.write(page)
    writefile.close()
    return