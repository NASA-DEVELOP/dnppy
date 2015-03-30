from .core import *

__all__=['enf_list',            # complete
         'enf_filelist',        # complete
         'enf_featlist']        # complete


def enf_list(item):

    """
    Ensures input item is list format. 

     many functions within this module allow the user
     to input either a single input or list of inputs in string format. This function makes
     sure single inputs in string format are handled like single entry lists for iterative
     purposes. It also will output an error if it is given a boolean value to signal that
     an input somewhere else is incorrect.
     """

    if not isinstance(item,list) and item:
        return([item])
    
    elif isinstance(item,bool):
        print '{enf_list} Cannot enforce a bool to be list! at least one list type input is invalid!'
        return(False)
    else:
        return(item)
    

def enf_filelist(filelist):

    """
    Sanitizes file list inputs

    This function checks that the input is a list of files and not a directory. If the input
     is a directory, then it returns a list of ALL files in the directory. This is to allow
     all functions which input filelists to be more flexible by accepting directories instead.
    """
    
    if isinstance(filelist,str):
        if os.path.exists(filelist):
            new_filelist= list_files(False,filelist,False,False,True)
            return(new_filelist)
        elif os.path.isfile(filelist):
            return([filelist])
    
    elif isinstance(filelist,bool):
        print 'Expected file list or directory but recieved boolean or None type input!'
        return(False)
    else:        return(filelist)



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

    return(new_filelist)
