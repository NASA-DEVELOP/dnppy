__author__ = 'jwely'

import os
from list_files import list_files

def enf_filelist(filelist, extension = None):

    """
    Sanitizes file list inputs

    This function checks that the input is a list of files and not a directory. If the input
    is a directory, then it returns a list of files in the directory which match the desired
    extension. This is to allow all functions which input filelists to be more flexible by
    accepting directories instead.
    """

    if isinstance(filelist, str):
        if os.path.isdir(filelist):
            new_filelist = list_files(False, filelist, False, False)

        elif os.path.isfile(filelist):
            new_filelist = [filelist]

    elif isinstance(filelist, bool):
        print 'Expected file list or directory but received boolean or None type input!'
        return False
    else:
        new_filelist = filelist

    if extension is not None:

        for new_file in new_filelist:

            if extension not in new_file:
                new_filelist.remove(new_file)

        return new_filelist

    else:
        return new_filelist