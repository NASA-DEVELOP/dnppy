__author__ = 'Jwely'

import os
import cookielib
import urllib, urllib2
import time
import tarfile

def fetch_test_landsat(test_dir):
    """
    downloading data from earth exploerer requires that users are logged in.
    This function opens a session and stores the required cookies to
    make automated download from earthexplorer.usgs possible.

    https://earthexplorer.usgs.gov/login/
    """

    print("This script downloads data from earth explorer by USGS")
    print("This server requires authentication to retrieve data")
    print("This script immediately discards this info after download is complete\n")
    username = raw_input("please type in your USGS username:")
    password = raw_input("please type in your USGS password:")

    if not os.path.exists(test_dir):
        os.makedirs(test_dir)

    # build a cookie jar.
    cookies = cookielib.CookieJar()

    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))

    # build payload
    url     = "https://earthexplorer.usgs.gov/login/"
    payload = {'username': username,
               'password': password,
               'rememberMe': "1"}

    logdata = urllib.urlencode(payload)

    # send the request and recieve the response
    opener.open(url, logdata)
    resp = opener.open("https://earthexplorer.usgs.gov/login/")
    text =  resp.read()

    if username in text:
        print("Logged into USGS Earth Explorer!")
        print("Begining downloads, please be patient!")
    else:
        print("Could not Log in!")

    # now lets download the data
    tiles = ["http://earthexplorer.usgs.gov/download/3119/LT40410361990014XXX01/STANDARD",
             "http://earthexplorer.usgs.gov/download/3119/LT50410362011208PAC01/STANDARD",
             "http://earthexplorer.usgs.gov/download/3372/LE70410362003114EDC00/STANDARD",
             "http://earthexplorer.usgs.gov/download/4923/LC80410362014232LGN00/STANDARD"]

    for tile in tiles:
        resp = opener.open(tile)
        attachments = resp.headers["Content-Disposition"].split('=')
        filename = attachments[1].replace('"',"").replace("'","")

        print("Downloading {0}".format(filename))
        outname = os.path.join(test_dir, 'raw', filename)

        try:
            urllib.urlretrieve(resp.url, outname)

        except urllib2.HTTPError:
            time.sleep(10)
            print("Working...")
            urllib.urlretrieve(resp.url, outname)

        # extract the archives and delete tar.gz files.
        print("Extracting tifs from tar.gz")
        tfile  = tarfile.open(outname, 'r:gz')
        outdir = os.path.join(test_dir, "raw", "Landsat", outname.replace(".tar.gz",""))
        tfile.extractall(outdir)
        tfile.close()
        os.remove(outname)

    return