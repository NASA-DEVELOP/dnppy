__author__ = 'jwely'

import os
from exists import exists
from enf_list import enf_list


def list_files(recursive, Dir, Contains = False, DoesNotContain = False):

    """
    Simple file listing function with more versatility than python builtins or arcpy.List

     This function sifts through a directory and returns a list of filepaths for all files
     meeting the input criteria. Useful for discriminatory iteration or recursive searches.
     Could be used to find all tiles with a given datestring such as 'MOD11A1.A2012', or
     perhaps all Band 4 tiles from a directory containing landsat 8 data.

     Inputs:
           recursive       'True' if search should search subfolders within the directory
                           'False' if search should ignore files in subfolders.
           Dir             The directory in which to search for files meeting the criteria
           Contains        search criteria to limit returned file list. File names must
                           contain parameters listed here. If no criteriaexists use 'False'
           DoesNotContain  search criteria to limit returned file list. File names must not
                           contain parameters listed here. If no criteriaexists use 'False'
     Outputs:
           filelist        An array of full filepaths meeting the criteria.

     Example Usage:
           from dnppy import core
           filelist = core.list_files(True,r'E:\Landsat7','B1',['gz','xml','ovr'])

           The above statement will find all the Band 1 tifs in a landsat data directory
           without including the associated metadata and uncompressed gz files.
           "filelist" variable will contain full filepaths to all files found.
    """

    # import modules and set up empty lists
    filelist = []
    templist = []

    # ensure input directory actually exists
    if not exists(Dir):
        raise Exception("{0} is not a valid file or folder!".format(Dir))

    # Ensure single strings are in list format for the loops below
    if Contains:
        Contains = enf_list(Contains)
    if DoesNotContain:
        DoesNotContain = enf_list(DoesNotContain)
        DoesNotContain.append('sr.lock')    # make sure lock files don't get counted
    else:
        DoesNotContain=['sr.lock']          # make sure lock files don't get counted

    # use os.walk commands to search through whole directory if recursive
    if recursive:
        for root,dirs,files in os.walk(Dir):
            for basename in files:
                filename = os.path.join(root,basename)

                # if both conditions exist, add items which meet Contains criteria
                if Contains and DoesNotContain:
                    for i in Contains:
                        if i in basename:
                            templist.append(filename)
                    # if the entire array of 'Contains' terms were found, add to list
                    if len(templist)==len(Contains):
                        filelist.append(filename)
                    templist=[]
                    # remove items which do not meet the DoesNotcontain criteria
                    for j in DoesNotContain:
                        if j in basename:
                            try: filelist.remove(filename)
                            except: pass

                # If both conditions do not exist (one is false)
                else:
                    # determine if a file is good. if it is, add it to the list.
                    if Contains:
                        for i in Contains:
                            if i in basename:
                                templist.append(filename)
                        # if the entire array of 'Contains' terms were found, add to list
                        if len(templist)==len(Contains):
                            filelist.append(filename)
                        templist=[]

                    # add all files to the list, then remove the bad ones.
                    elif DoesNotContain:
                        filelist.append(filename)
                        for j in DoesNotContain:
                            if j in basename:
                                try: filelist.remove(filename)
                                except: pass
                    else:
                        filelist.append(filename)

                # if neither conditionexists
                    if not Contains and not DoesNotContain:
                        filelist.append(filename)

    # use a simple listdir if recursive is False
    else:
        # list only files in current directory, not subdir and check criteria
        try:
            for basename in os.listdir(Dir):
                filename = os.path.join(Dir,basename)
                if os.path.isfile(filename):
                    if Contains:
                        for i in Contains:
                            if i in basename:
                                templist.append(filename)

                        # if the entire array of 'Contains' terms were found, add to list
                        if len(templist)==len(Contains):
                            filelist.append(filename)
                        templist=[]
                    else:
                        filelist.append(filename)

                # Remove any files from the filelist that fail DoesNotContain criteria
                if DoesNotContain:
                    for j in DoesNotContain:
                        if j in basename:
                            try: filelist.remove(filename)
                            except: pass
        except: pass

    # Print a quick status summary before finishing up if Quiet is False
    print('Files found which meet all input criteria: {0}'.format(len(filelist)))

    return filelist