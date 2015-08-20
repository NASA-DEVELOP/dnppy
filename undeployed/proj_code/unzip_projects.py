__author__ = 'jwely'

import os
import zipfile

def unzip_projects():
    """
    Quick script to perform mass unzipping on code packages collected
    for inclusion in proj_code.
    """

    # lists all zip files in the current directory non-recursively
    zips = [a for a in os.listdir(os.curdir) if ".zip" in a]

    for azip in zips:
        z = zipfile.ZipFile(azip)
        z.extractall()
        z.close()
        os.remove(os.path.abspath(azip))

    print("unzipped {0} project folders".format(len(zips)))


if __name__ == "__main__":
    unzip_projects()
