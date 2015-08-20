__author__ = 'jwely'


import urllib

def list_http_waterweather(site):
    """
    Lists contents of http directories at [http://water.weather.gov/precip/p_download_new/]
    which hosts MPE data.

    :param site: url to somewhere on the server at http://water.weather.gov/precip/p_download_new/

    :return file_urls: returns a list of file urls at input site.
    """

    website = urllib.urlopen(site)
    string  = website.readlines()

    file_urls = []
    for line in string:
        try:
            name = line.split('"')[7]
            if "." in name:
                file_urls.append(line.split('"')[7])
        except:
            pass
    return file_urls

if __name__ == "__main__":
    print list_http_waterweather("http://water.weather.gov/precip/p_download_new/2015/01/01")