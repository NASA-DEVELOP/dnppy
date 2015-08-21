__author__ = 'jwely'
__all__ = ["enf_rastlist"]

from dnppy import core

from is_rast import is_rast
import os

def enf_rastlist(filelist):
    """
    Ensures a list of inputs filepaths contains only valid raster types

    :param filelist:        a list of filepaths that contains some raster filetypes
    :return new_filelist:   a list of filepaths with all non-raster files removed
    """

    # first place the input through the same requirements of any filelist
    filelist        = core.enf_filelist(filelist)
    new_filelist    = []

    for filename in filelist:

        if os.path.isfile(filename):
            if is_rast(filename):
                new_filelist.append(filename)

    return new_filelist
