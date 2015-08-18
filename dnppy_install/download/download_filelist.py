__author__ = 'jwely'

from dnppy_install import core
from download_urls import download_urls
import os, time

__all__ = ["download_filelist"]

def download_filelist(ftp_texts, file_type = None, outdir = None):
    """
    Reads text file of download links, downloads them.

    This script reads a text file with urls such as those output from ECHO REVERB
    and outputs them to an output directory. It will retry failed links 20 times before
    giving up and outputting a warning to the user.

    :param ftp_texts:    array of txt files ordered from reverb containing ftp links
    :param file_type:    file extension of the desired files, leave blank or False to grab all types.
    :param outdir:       folder where files are to be placed after download

    :return list failed: list of files which failed to download after the end of the script.
    """

    failed = []

    # force inputs to take list format
    ftp_texts = core.enf_list(ftp_texts)
    if file_type is not None:
        file_type = core.enf_list(file_type)

    for ftptext in ftp_texts:
        #verify that things exist.
        core.exists(ftptext)

        if not outdir:
            outdir,_ = os.path.split(ftptext)

        ftp     = open(ftptext,'r')
        sites   = ftp.readlines()

        print("Attempting to download {0} files!".format(len(sites)))
        print("Saving all files to {0}".format(outdir))

        # perform the first attempt
        failed = download_urls(sites, outdir, file_type)

        # for 19 more times, if there are still items in the failed list, try again
        for i in range(1,19):
            if len(failed)>0:
                print("retry number {0} to grab {1} failed downloads!".format(i,len(failed)))
                time.sleep(60)
                failed = download_urls(failed, file_type, outdir)

        # once all tries are complete, print a list of files which repeatedly failed
        if len(failed)>0:
            print('Files at the following URLs have failed 20 download attempts')
            print('Manually verify that these files exist on the server:')
            for i in failed:
                print(i)
        else:
            print('Finished with no errors!')

        # close the open text files and finish up
        ftp.close()

    return failed


# testing area
if __name__ == "__main__":

    download_filelist("reverb_filelist.txt",
                      outdir = r"C:\Users\jwely\Desktop\troubleshooting\rawMODIS")