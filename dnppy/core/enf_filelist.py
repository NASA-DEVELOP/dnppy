__author__ = 'jwely'

import os
from list_files import list_files


def enf_filelist(filelist, extension = None):
    """
    Sanitizes file list inputs

    This function checks that the input is a list of files and not a directory. If the input
    is a directory, then it returns a list of files in the directory which match the desired
    extension. This is to allow all functions which input filelists to be a little more
    flexible by accepting directories instead.

    :param filelist:        a list of filepath strings
    :param extension:       output list contains only files with this string extension. (txt, tif, etc)

    :return new_filelist:   sanitized file list
    """

    new_filelist = None

    if isinstance(filelist, str):
        if os.path.isdir(filelist):
            new_filelist = list_files(False, filelist, False, False)

        elif os.path.isfile(filelist):
            new_filelist = [filelist]

    elif isinstance(filelist, list):
        new_filelist = filelist

    elif isinstance(filelist, bool) or isinstance(filelist, None):
        raise TypeError('Expected file list or directory but received boolean or None type input!')


    if new_filelist is None:
        new_filelist = filelist

    if extension is not None:
        new_filelist = [new_file for new_file in new_filelist if extension in new_filelist]

    return new_filelist
