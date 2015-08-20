__author__ = 'jwely'

import os
from exists import exists
from enf_list import enf_list


def list_files(recursive, directory, contains = None, not_contains = None):
    """
    Simple file listing function with more versatility than python builtins or arcpy.List

    This function sifts through a directory and returns a list of filepaths for all files
    meeting the input criteria. Useful for discriminatory iteration or recursive searches.
    Could be used to find all tiles with a given datestring such as 'MOD11A1.A2012', or
    perhaps all Band 4 tiles from a directory containing landsat 8 data.

    :param recursive:       'True' if search should search subfolders within the directory
                            'False' if search should ignore files in subfolders.
    :param directory:       The directory in which to search for files meeting the criteria
    :param contains:        search criteria to limit returned file list. File names must
                            contain parameters listed here. If no criteria exists use 'False'
    :param not_contains:    search criteria to limit returned file list. File names must not
                            contain parameters listed here. If no criteria exists use 'False'

    :return filelist:        An array of full filepaths meeting the criteria.
    """

    # import modules and set up empty lists
    filelist = []
    templist = []

    # ensure input directory actually exists
    if not exists(directory):
        raise Exception("{0} is not a valid file or folder!".format(directory))

    # Ensure single strings are in list format for the loops below
    if contains:
        contains = enf_list(contains)
    if not_contains:
        not_contains = enf_list(not_contains)
        not_contains.append('sr.lock')    # make sure lock files don't get counted
    else:
        not_contains = ['sr.lock']          # make sure lock files don't get counted

    # use os.walk commands to search through whole directory if recursive
    if recursive:
        for root, dirs, files in os.walk(directory):
            for basename in files:
                filename = os.path.join(root, basename)

                # if both conditions exist, add items which meet contains criteria
                if contains and not_contains:
                    for i in contains:
                        if i in basename:
                            templist.append(filename)
                    # if the entire array of 'contains' terms were found, add to list
                    if len(templist) == len(contains):
                        filelist.append(filename)
                    templist = []
                    # remove items which do not meet the DoesNotcontain criteria
                    for j in not_contains:
                        if j in basename:
                            try: filelist.remove(filename)
                            except: pass

                # If both conditions do not exist (one is false)
                else:
                    # determine if a file is good. if it is, add it to the list.
                    if contains:
                        for i in contains:
                            if i in basename:
                                templist.append(filename)
                        # if the entire array of 'contains' terms were found, add to list
                        if len(templist) == len(contains):
                            filelist.append(filename)
                        templist = []

                    # add all files to the list, then remove the bad ones.
                    elif not_contains:
                        filelist.append(filename)
                        for j in not_contains:
                            if j in basename:
                                try: filelist.remove(filename)
                                except: pass
                    else:
                        filelist.append(filename)

                # if neither conditionexists
                    if not contains and not not_contains:
                        filelist.append(filename)

    # use a simple listdir if recursive is False
    else:
        # list only files in current directory, not subdir and check criteria
        try:
            for basename in os.listdir(directory):
                filename = os.path.join(directory, basename)
                if os.path.isfile(filename):
                    if contains:
                        for i in contains:
                            if i in basename:
                                templist.append(filename)

                        # if the entire array of 'contains' terms were found, add to list
                        if len(templist) == len(contains):
                            filelist.append(filename)
                        templist = []
                    else:
                        filelist.append(filename)

                # Remove any files from the filelist that fail not_contains criteria
                if not_contains:
                    for j in not_contains:
                        if j in basename:
                            try: filelist.remove(filename)
                            except: pass
        except: pass

    print('Files found which meet all input criteria: {0}'.format(len(filelist)))

    return filelist


if __name__ == "__main__":
    print list_files(False, r"C:\Users\Jeff\Desktop\Github\dnppy\docs\build")