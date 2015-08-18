__author__ = 'jwely'

from dnppy import core
from download_url import download_url
import os, time

__all__ = ["download_urls"]

def download_urls(url_list, outdir, file_types = None):
    """
    Downloads a list of files. Retries failed downloads

    This script downloads a list of files and places it in the output directory. It was
    built to be nested within "Download_filelist" to allow loops to continuously retry
    failed files until they are successful or a retry limit is reached.

    :param url_list:   array of urls, probably as read from a text file
    :param file_types: list of file types to download. Useful for excluding extraneous
                       metadata by only downloading 'hdf' or 'tif' for example. Please note
                       that often times, you actually NEED the metadata.
    :param outdir:     folder where files are to be placed after download

    :return failed:    list of files which failed download
    """

    failed   = []
    url_list = core.enf_list(url_list)

    # creates output folder at desired path if it doesn't already exist
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # establish a wait time that will increase when downloads fail. This helps to reduce
    # the frequency of REVERB server rejections for requesting too many downloads
    wait = 0

    for site in url_list:
        download = False
        url      = site.rstrip()
        sub      = url.split("/")
        leng     = len(sub)
        name     = sub[leng-1]

        # Determine whether or not to download the file based on filetype.
        if file_types is not None:
            for filetype in file_types:
                if filetype in name[-4:]:
                    download = True
        else:
            download = True

        # attempt download of the file, or skip it.
        if download:

            try:
                # wait for the wait time before attempting writing a file
                time.sleep(wait)
                download_url(url, os.path.join(outdir,name))
                print("{0} is downloaded {1}".format(name, wait))

                # reduce the wait time when downloads succeed.
                if wait >= 1:
                    wait -= wait

            # add to the fail count if the download is unsuccessful and wait longer next time.
            except:
                print("{0} will be retried! {1}".format(sub[leng-1], wait))
                wait += 5
                failed.append(url)

    print("Finished downloading urls!")
    return failed