__author__ = 'jwely'


import os
import tarfile
from dnppy import core

def extract_targz(filepaths):
    """
    Input list of filepaths or a directory with tar.gz files in it

    Simple batch extractor of files with tar.gz compression
    creates a folder for each input tar.gz file with its extracted
    contents, then deletes the original tar.gz file.

    Useful for bulk Landsat data extraction.
    """

    filepaths = core.enf_filelist(filepaths)

    for filepath in filepaths:
        if ".tar.gz" in filepath:
            head,tail = os.path.split(filepath)

            tfile = tarfile.open(filepath, 'r:gz')
            outdir = os.path.join(head, tail.replace(".tar.gz",""))
            tfile.extractall(outdir)
            tfile.close()
            os.remove(filepath)

    return