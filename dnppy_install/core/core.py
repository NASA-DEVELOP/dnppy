# loacal imports
from .enforce import *
import os, datetime, sys, shutil


__all__=['del_empty_dirs',      # complete
         'rename',              # complete
         'list_files',          # complete
         'move',                # complete
         'exists',              # complete
         'create_outname',      # complete
         'check_module']        # complete


def list_files(recursive, Dir, Contains = False, DoesNotContain = False):

    """
    Simple file listing function with more versatility than python builtins or arcpy.List
    
     This function sifts through a directory and returns a list of filepaths for all files
     meeting the input criteria. Useful for discriminatory iteration or recursive searches.
     Could be used to find all tiles with a given datestring such as 'MOD11A1.A2012', or
     perhaps all Band 4 tiles from a directory containing landsat 8 data.

     Inputs:
           recursive       'True' if search should search subfolders within the directory
                           'False'if search should ignore files in subfolders.
           Dir             The directory in which to search for files meeting the criteria
           Contains        search criteria to limit returned file list. File names must
                           contain parameters listed here. If no criteriaexists use 'False'
           DoesNotContain  search criteria to limit returned file list. File names must not
                           contain parameters listed here. If no criteriaexists use 'False'
     Outputs:
           filelist        An array of full filepaths meeting the criteria.

     Example Usage:
           import ND
           filelist=ND.list_files(True,r'E:\Landsat7','B1',['gz','xml','ovr'])

           The above statement will find all the Band 1 tifs in a landsat data directory
           without including the associated metadata and uncompressed gz files.
           "filelist" variable will contain full filepaths to all files found.
    """
    
    # import modules and set up empty lists
    filelist=[]
    templist=[]

    # ensure input directory actuallyexists
    if not exists(Dir): return(False)

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
    
    return(filelist)


def del_empty_dirs(path):
    """Removes empty folders, used for cleaning up temporary workspace."""


    # only continue if the pathexists
    if os.path.isdir(path):

        # list files in directory
        files = os.listdir(path)
        
        # if zero files exist inside it, delete it.
        if len(files)==0:
            os.rmdir(path)
            return(True)
        
    return(False)


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


def move(source, destination):
    """Moves a file"""

    dest_path, name = os.path.split(destination)

    # create that directory if it doesnt already exist
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    try:     
        shutil.move(source, destination)
        print('moved file from {0} to {1}'.format(source, destination))
    except:
        print("failed to move file from {0}".format(source))
        
    return(dest_path)


def exists(location):
    """Ensures inputlocation is either a file or a folder"""
    
    # if the object is neither a file or a location, return False.
    if not os.path.exists(location) and not os.path.isfile(location):
        print("{0} is not a valid file or folder!".format(location))
        return(False)
    
    else:
        return(True)



def create_outname(outdir, inname, suffix, ext = False):
    """
    Quick way to create unique output filenames within iterative functions

     This function is built to simplify the creation of output filenames. Function allows
     outdir = False and will create an outname in the same directory as inname. Function will
     add a the user input suffix, separated by an underscore "_" to generate an output name.
     this is usefull when performing a small modification to a file and saving new output with
     a new suffix. function returns an output name, it does not save the file as that name.


     Inputs:
       outdir      either the directory of the desired outname or False to create an outname
                   in the same directory as the inname
       inname      the input file from which to generate the output name "outname"
       suffix      suffix to attach to the end of the filename to mark it as output
       ext         specify the file extension of the output filename. Leave blank or False
                   and the outname will inherit the same extension as inname

     Example Usage:
       outdir = r"C:\Users\jwely\Desktop\output"
       inname = r"C:\Users\jwely\Desktop\folder\subfolder\Landsat_tile.tif"
       suffix = "adjusted"
       outname = core.create_outname(outdir,inname,suffix)

       will set outname equal to "C:\Users\jwely\Desktop\output\Landsat_tile_adjusted.tif" which
       can be passed to other functions that require an output filepath.
    """
    
    # isolate the filename from its directory and extension
    if os.path.isfile(inname):
        head, tail  = os.path.split(inname)
        noext       = tail.split('.')[:-1]
        noext       ='.'.join(noext)
    else:
        tail    = inname
        if "." in inname:
            noext   = tail.split('.')[:-1]
            noext   = '.'.join(noext)
        else:
            noext   = inname

    # create the suffix
    if ext:
        suffix = "_{0}.{1}".format(suffix,ext)
    else:
        ext = tail.split('.')[-1:]
        suffix = "_{0}.{1}".format(suffix,''.join(ext))

    if outdir:    
        outname = os.path.join(outdir,noext+suffix)
        return(outname)
    else:
        outname = os.path.join(head,noext+suffix)
        return(outname)



def check_module(module_name):

    """
    Checks for module installation and guides user to download source if not found

     Simple function that directs the user to download the input module if they do
     not already have it before returning a "False" value. This helps novice users quickly
     raster.identify that a missing module is the problem and attempt to correct it.

     modules with supported download help links are listed below
     module_list=['h5py','numpy','dbfpy','scipy','matplotlib','PIL','gdal']

     Example usage:
       if check_module('numpy'): import numpy
    """

    module_list=['h5py','numpy','dbfpy','scipy','matplotlib','PIL','gdal','pyhdf']
    
    import webbrowser,time,sys

    # try to import the module, if it works return True, otherwise continue
    try:
        modules = map(__import__,[module_name])
        return(True)
    except:

        for module in module_list:
            if module_name==module:
                print "You do not have " + module_name + ", opening download page for python 2.7 version!"

        # determine the correct url based on module name
        if module_name=='h5py':
            url='https://pypi.python.org/pypi/h5py'
    
        elif module_name=='numpy':
            url='http://sourceforge.net/projects/numpy/files/latest/download?source=files'
    
        elif module_name=='dbfpy':
            url='http://sourceforge.net/projects/dbfpy/files/latest/download'

        elif module_name=='pyhdf':
            url='http://hdfeos.org/software/pyhdf.php'
    
        elif module_name=='scipy':
            url='http://sourceforge.net/projects/scipy/files/latest/download?source=files'
    
        elif module_name=='matplotlib':
            url="""http://sourceforge.net/projects/matplotlib/files/matplotlib/
            matplotlib-1.4.1/windows/matplotlib-1.4.1.win-amd64-py2.7.exe/
            download?use_mirror=superb-dca3"""
    
        elif module_name=='PIL':
            url='http://www.pythonware.com/products/pil/'
    
        elif module_name=='gdal':
            print 'Follow this tutorial closely for installing gdal for 32 bit UNLESS you have intentionally installed 64 bit python'
            url='http://pythongisandstuff.wordpress.com/2011/07/07/installing-gdal-and-ogr-for-python-on-windows/'

        # open the url and HALT operation.
        time.sleep(3)
        webbrowser.open(url)
        sys.exit()
        return(False)































