__author__ = 'jwely'

import os
from exists import exists


def rename(filename, replace_this, with_this):
    """
    renames a file

    :param filename:        input file to rename
    :param replace_this:    string to be replaced. such as " " (a space)
    :param with_this:       what to replace the string with. such as "_" (an underscore)

    :return newfilename:    the new name of the file.
    """

    if replace_this in filename:

        # make sure the filename exists
        exists(filename)

        # define a new filename
        newfilename = filename.replace(replace_this, with_this)

        # rename the file
        os.rename(filename, newfilename)

        print("renamed" + filename + "to" + newfilename)
        return newfilename

    else:
        return filename
