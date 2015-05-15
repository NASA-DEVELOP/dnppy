__author__ = 'jwely'

import os
from exists import exists


def rename(filename, replacethis, withthis):
    """
    Simply renames files

     Inputs:
       filename        input file to rename
       replacethis     String to be replaced. such as " " (a space)
       withthis        What to replace the string with. such as "_" (an underscore)

     Outputs:
           newfilename     returns the new name of the renamed file.
     """

    if replacethis in filename:

        # make sure the filenameexists
        exists(filename)

        # define a new filename
        newfilename = filename.replace(replacethis, withthis)

        # rename the file
        os.rename(filename,newfilename)

        print("renamed" + filename + "to" + newfilename)
        return newfilename

    else:
        return filename
