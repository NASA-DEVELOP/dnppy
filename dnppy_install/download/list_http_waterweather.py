__author__ = 'jwely'


import urllib

def list_http_waterweather(site):
    """
    Lists contents of http directories at
    [http://water.weather.gov/precip/p_download_new/]
    which hosts MPE data.
    """

    website = urllib.urlopen(site)
    string  = website.readlines()

    files = []
    for line in string:
        try:
            name = line.split('"')[7]
            if "." in name:
                files.append(line.split('"')[7])
        except:
            pass
    return files

if __name__ == "__main__":
    print list_http_waterweather("http://water.weather.gov/precip/p_download_new/2015/01/01")