__author__ = 'jwely'

from dnppy import core
from download_urls import download_urls
import os, time

__all__ = ["download_filelist"]

def download_filelist(ftptexts, filetypes = False, outdir = False):

    """
    Reads text file of download links, downloads them.

     This script reads a text file with urls such as those output from ECHO REVERB
     and outputs them to an output directory. It will retry failed links 20 times before
     giving up and outputing a warning to the user.

     Inputs:
       ftptexts        array of txt files ordered from reverb containing ftp links
       filetype        file extension of the desired files, leave blank or False to grab all
                       types.
       outdir          folder where files are to be placed after download

     Outputs:
       failed          list of files which failed to download after the end of the script.
    """

    # force inputs to take list format
    ftptexts = core.enf_list(ftptexts)
    if filetypes:
        filetypes = core.enf_list(filetypes)

    for ftptext in ftptexts:
        #verify that things exist.
        core.exists(ftptext)

        if not outdir:
            outdir,_ = os.path.split(ftptext)

        ftp     = open(ftptext,'r')
        sites   = ftp.readlines()

        print("Attempting to download {0} files!".format(len(sites)))
        print("Saving all files to {0}".format(outdir))

        # perform the first attempt
        failed = download_urls(sites, outdir, filetypes)

        # for 19 more times, if there are still items in the failed list, try again
        for i in range(1,19):
            if len(failed)>0:
                print("retry number {0} to grab {1} failed downloads!".format(i,len(failed)))
                time.sleep(60)
                failed = download_urls(failed, filetypes, outdir)

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