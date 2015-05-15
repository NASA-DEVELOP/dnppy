__author__ = 'jwely'


import os
from enf_filelist import enf_filelist

def enf_featlist(filelist):

    """
    Sanitizes feature list inputs

     This function works exactly like enf_filelist, with the added feature of removing
     all filenames that are not of a feature class type recognized by arcmap.

     Input:    filelist        any list of files
     Output:   new_filelist    New list with all non-feature class files in filelist removed.

     Bugs:
       right now, all this does is check for a shape file extension. Sometimes shape files
       can be empty or otherwise contain no feature class data. This function does not check
       for this.
    """

    # first place the input through the same requirements of any filelist
    filelist        = enf_filelist(filelist)
    new_filelist    = []
    feat_types      = ['shp']

    for filename in filelist:
        ext=filename[-3:]

        if os.path.isfile(filename):
            for feat_type in feat_types:
                if ext == feat_type:
                    new_filelist.append(filename)

    return new_filelist