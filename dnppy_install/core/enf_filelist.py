__author__ = 'jwely'

import os
from list_files import list_files

def enf_filelist(filelist):

    """
    Sanitizes file list inputs

    This function checks that the input is a list of files and not a directory. If the input
     is a directory, then it returns a list of ALL files in the directory. This is to allow
     all functions which input filelists to be more flexible by accepting directories instead.
    """

    if isinstance(filelist, str):
        if os.path.isdir(filelist):
            new_filelist = list_files(False, filelist, False, False)
            return new_filelist

        elif os.path.isfile(filelist):
            return [filelist]

    elif isinstance(filelist, bool):
        print 'Expected file list or directory but recieved boolean or None type input!'
        return False
    else:
        return filelist