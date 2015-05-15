__author__ = 'jwely'

from dnppy import core

from is_rast import is_rast
import os

def enf_rastlist(filelist):

    """
    ensures a list of inputs filepaths contains only valid raster tyeps
    """

    # first place the input through the same requirements of any filelist
    filelist        = core.enf_filelist(filelist)
    new_filelist    = []

    for filename in filelist:
        ext=filename[-3:]

        if os.path.isfile(filename):
            if is_rast(filename):
                new_filelist.append(filename)

    return new_filelist
