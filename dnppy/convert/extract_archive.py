__author__ = 'jwely'

import os
import tarfile
import gzip
import zipfile
from dnppy import core

__all__ = ["extract_archive"]

def extract_archive(filepaths):
    """
    Input list of filepaths OR a directory path with compressed
    files in it. Attempts to decompress the following formats

    formats:
        .tar.gz
        .tar
        .gz
        .zip
    """

    filepaths = core.enf_filelist(filepaths)

    for filepath in filepaths:

        head,tail = os.path.split(filepath)

        if ".tar.gz" in filepath:
            with tarfile.open(filepath, 'r:gz') as tfile:
                outdir = os.path.join(head, tail.replace(".tar.gz",""))
                tfile.extractall(outdir)

        # gzip only compresses single files
        elif ".gz" in filepath:
            with gzip.open(filepath, 'rb') as gzfile:
                outfile = os.path.join(head, tail.replace(".gz",""))
                content = gzfile.read()
                with open(outfile, 'wb') as of:
                    of.write(content)

        elif ".tar" in filepath:
            with tarfile.open(filepath, 'r') as tfile:
                outdir = os.path.join(head, tail.replace(".tar",""))
                tfile.extractall(outdir)

        elif ".zip" in filepath:
            with zipfile.ZipFile(filepath, "r") as zipf:
                outdir = os.path.join(head, tail.replace(".zip",""))
                zipf.extractall(outdir)

        else:
            return

        #os.remove(filepath)
        print("Extracted {0}".format(filepath))
    return

#testing area
if __name__ == "__main__":
    formats = [r"C:\Users\jwely\Desktop\troubleshooting\zips\MOD09A1.A2015033.h11v05.005.2015044233105_1_tar.tar",
               r"C:\Users\jwely\Desktop\troubleshooting\zips\MOD09A1.A2015033.h11v05.005.2015044233105_1_targz.tar.gz",
               r"C:\Users\jwely\Desktop\troubleshooting\zips\MOD09A1.A2015033.h11v05.005.2015044233105_1.tif.gz",
               r"C:\Users\jwely\Desktop\troubleshooting\zips\MOD09A1.A2015033.h11v05.005.2015044233105_1_zip.zip"]

    for format in formats:
        extract_archive(format)
