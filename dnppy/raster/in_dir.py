__author__ = 'jwely'
__all__ = ["in_dir"]

from enf_rastlist import enf_rastlist
from dnppy import core

def in_dir(dir_name, recursive = False):
    """
    Lists all the rasters in an input directory. finds all formats
    supported by ``raster.enf_rastlist()``.

    :param dir_name:    directory to search rasters for
    :param recursive:   Set to "True" to search within subfolders of input
                        directory "dir_name"
    """

    rast_list = core.list_files(recursive, dir_name)
    rast_list = enf_rastlist(rast_list)

    print("Found {0} file with valid raster format".format(len(rast_list)))

    return rast_list
