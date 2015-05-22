__author__ = 'Jwely'

import os
import cookielib
import urllib, urllib2
import time
import tarfile

def fetch_test_landsat(test_dir):
    """
    downloading data from earth explorer requires that users are logged in.
    This function opens a session and stores the required cookies to
    make automated download from earthexplorer.usgs possible.

    https://earthexplorer.usgs.gov/login/
    """

    # list of tiles that will be downloaded by this function
    tiles = ["http://earthexplorer.usgs.gov/download/3119/LT40410361990014XXX01/STANDARD",
             "http://earthexplorer.usgs.gov/download/3119/LT50410362011208PAC01/STANDARD",
             "http://earthexplorer.usgs.gov/download/3372/LE70410362003114EDC00/STANDARD",
             "http://earthexplorer.usgs.gov/download/4923/LC80410362014232LGN00/STANDARD"]


    print("This script downloads data from earth explorer by USGS")
    print("This server requires authentication to retrieve data")
    print("This script immediately discards this info after download is complete\n")
    username = raw_input("please type in your USGS username:")
    password = raw_input("please type in your USGS password:")

    subdir = os.path.join(test_dir, "raw","Landsat")
    if not os.path.exists(subdir):
        os.makedirs(subdir)

    # build a cookie jar.
    cookies = cookielib.CookieJar()

    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))

    # build payload
    url     = "https://earthexplorer.usgs.gov/login/"
    payload = {'username': username,
               'password': password,
               'rememberMe': "1"}

    logdata = urllib.urlencode(payload)

    # send the request and receive the response
    opener.open(url, logdata)
    resp = opener.open("https://earthexplorer.usgs.gov/login/")
    text =  resp.read()


    if username in text:
        print("Logged into USGS Earth Explorer!")
        print("Beginning downloads, please be patient!")
    else:
        print("Could not Log in!")


    # now lets download the data
    for tile in tiles:
        resp = opener.open(tile)
        attachments = resp.headers["Content-Disposition"].split('=')
        filename = attachments[1].replace('"',"").replace("'","")

        print("Downloading {0}".format(filename))
        outname = os.path.join(subdir, filename)

        try:
            urllib.urlretrieve(resp.url, outname)

        except urllib2.HTTPError:
            time.sleep(10) # helps server overload errors
            print("Working...")
            urllib.urlretrieve(resp.url, outname)

        # extract the archives and delete tar.gz files.
        print("Extracting tifs from tar.gz")
        time.sleep(3)
        tfile  = tarfile.open(outname, 'r:gz')
        outdir = os.path.join(subdir, outname.replace(".tar.gz",""))
        tfile.extractall(outdir)
        tfile.close()
        os.remove(outname)

    return