__author__ = 'jwely'

import os


def del_empty_dirs(path):
    """Removes empty folders, used for cleaning up temporary workspace."""


    # only continue if the pathexists
    if os.path.isdir(path):

        # list files in directory
        files = os.listdir(path)

        # if zero files exist inside it, delete it.
        if len(files)==0:
            os.rmdir(path)
            return True

    return False