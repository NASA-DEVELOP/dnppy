"""
======================================================================================
                                   dnppy.core
======================================================================================
 This script is part of (dnppy) or "DEVELOP National Program py"
 It is maintained by the Geoinformatics YP class.

It contains some core functions to assist in data formatting , path manipulation, and
logical checks. It is commonly called by other modules in the dnppy package.


 Requirements:
   Python 2.7
   Arcmap 10.2 or newer for some functions

   Example:
   from dnppy import core
   Sample_Function('test',False)
"""

__author__ = ["Jeffry Ely, jeff.ely.08@gmail.com"]

__all__=['sample_function',     # complete
         'project',             # complete
         'rolling_window',      # complete
         'in_window',           # complete
         'del_empty_dirs',      # complete
         'rename',              # complete
         'enf_list',            # complete
         'enf_filelist',        # complete
         'enf_rastlist',        # complete
         'list_files',          # complete
         'move',                # complete
         'exists',              # complete
         'create_outname',      # complete
         'check_module']        # complete


import os
import datetime
import sys
import shutil

import arcpy
if arcpy.CheckExtension('Spatial')=='Available':
    arcpy.CheckOutExtension('Spatial')
    from arcpy import sa,env
    arcpy.env.overwriteOutput = True

#======================================================================================
def sample_function(inputs, Quiet=False):

    """
    this is an example docstring for our sample function

    This is where additional information goes like inputs/outputs/authors
    """

    outputs=inputs
    if not Quiet:
        print('This is a sample function!')
        print('try changing your statement to Sample_Function(str,True)')

    return(outputs)



def resample(rasterlist,reference_cellsize,resamp_type,outdir=False,Quiet=False):

    """
     Simple a batch processor for resampling with arcmap

     Inputs:
       rasterlist          list of rasters to resample
       reference_cellsize  Either a cell size writen as "10 10" for example or a reference
                           raster file to match cell sizes with. 
       resamp_type         The resampling type to use if images are not identical cell sizes.
                               "NEAREST","BILINEAR","CUBIC","MAJORITY" are the options.
       outdir              output directory to save files. if left "False" output files will
                           be saved in same folder as the input file.

     
    """

    # sanitize inputs and create directories
    reference_cellsize  = str(reference_cellsize)
    rasterlist          = enforce_rastlist(rasterlist)
    if outdir and not os.path.isdir(outdir):
        os.makedirs(outdir)
        
    # resample the files.
    for filename in rasterlist:

        # create output filename
        outname = create_outname(outdir,filename,'rs')
        
        #arcpy.Resample_management(filename,,reference_cellsize, resamp_type)
    
    return


def project(filelist, reference_file, outdir=False, resampling_type=False,
                      cell_size=False, Quiet=False):

    """
    Wrapper for multiple arcpy projecting functions. Projects to reference file
    
     Inputs a filelist and a reference file, then projects all rasters or feature classes
     in the filelist to match the projection of the reference file. Writes new files with a
     "_p" appended to the end of the input filenames.

     Inputs:
       filelist            list of files to be projected
       outdir              optional desired output directory. If none is specified, output files
                           will be named with '_p' as a suffix.
       reference_file      Either a file with the desired projection, or a .prj file.
       resampling type     exactly as the input for arcmaps project_Raster_management function
       cell_size           exactly as the input for arcmaps project_Raster_management function

     Output:
       Spatial reference   spatial referencing information for further checking.

     
    """

    # sanitize inputs 
    exists(reference_file)
    rasterlist  = enf_rastlist(filelist)
    featurelist = enf_featlist(filelist)
    cleanlist   = rasterlist + featurelist

    # ensure output directoryexists
    if not os.path.exists(outdir):
        os.makedirs(outdir)
        
    # grab data about the spatial reference of the reference file. (prj or otherwise)
    if reference_file[-3:]=='prj':
        Spatial_Reference=arcpy.SpatialReference(Spatial_Reference)
    else:
        Spatial_Reference=arcpy.Describe(reference_file).spatialReference
        
    # determine wether coordinate system is projected or geographic and print info
    if Spatial_Reference.type=='Projected':
        if not Quiet:
            print('{project} Found ['+ Spatial_Reference.PCSName +
                    '] Projected coordinate system')
    else:
        if not Quiet:
            print('{project} Found ['+ Spatial_Reference.GCSName +
                    '] Geographic coordinate system')

    for filename in cleanlist:
        
        # create the output filename
        outname = create_outname(outdir,filename,'p')

        # Perform the projection!...................................................
        # use ProjectRaster_management for rast files
        if raster.is_rast(filename):
            if resampling_type:
                arcpy.ProjectRaster_management(filename,outname,Spatial_Reference,
                            resampling_type)
            else:
                arcpy.ProjectRaster_management(filename,outname,Spatial_Reference)
                
        # otherwise, use Project_management for featureclasses and featurelayers
        else:
            arcpy.Project_management(filename,outname,Spatial_Reference)

        # print a status update    
        if not Quiet: print '{project} Wrote projected file to ' + outname

    if not Quiet: print '{project} Finished! \n '
    return(Spatial_Reference)


def rolling_window(filelist, window_size, start_jday, end_jday,
                                           start_year=False, end_year=False, Quiet=False):

    """
    Creates a list of windows each containing a list of files grouped by central date
    
     this function calls the 'in_window' function for a whole range of dates to produce
     rolling windows. Use this if you intend to iterate through many files for rolling
     statistics
     
     Inputs:
       filelist        the list of files to include in the rolling window. This could be
                       easily created with the list_files function.
       window_size     width of the window in days. used to group files
       start_jday      julian day on which to start the window centers
       end_jday        julian day on which to end the window centers
       start_year      year on which to start the window centers. If you wish to bin all days
                       at a given point in the year together for long term averages, leave
                       year inputs blank or set to 'False'. This will then consider all
                       julian days within the window for all years in 'filelist'
       end_year        year on which to end the window centers. If you wish to bin all days
                       at a given point in the year together for long term averages, leave
                       year inputs blank or set to 'False'. This will then consider all
                       julian days within the window for all years in 'filelist'

     Outputs:
       window_centers  list of window center names
       window_matrix   list of all files in grouping around each window center

     
    """
    
    # set intial conditions for while loop
    index=0
    current_jday=start_jday
    current_year=start_year
    window_matrix=[]
    window_centers=[]

    filelist=Enforce_Filelist(filelist)

    # if a start year and end year exist (not False)
    if start_year and end_year:

        # loop for as long as the current year and day do not exceed the ending year and day
        while current_jday <= end_jday and current_year <=end_year:
            center,window= in_window(filelist,window_size,current_jday,current_year,Quiet)
            window_matrix.append(window)
            window_centers.append(center)

            # if the current day counter has reached the end of the year, reset the day
            # and advance the year count forward
            if current_jday==365 and not current_year%4==0:
                current_jday=1
                current_year=current_year + 1
            elif current_jday==366 and current_year%4==0:
                current_jday==1
                current_year=current_year + 1
            else:
                current_jday=current_jday + 1
                index=index+1
                
    # if years are set to False, process based soley on julian days.
    else:
        
        # loop for as long as the current day does not exceed the ending day
        while current_jday <= end_jday:
            center,window= in_window(filelist,window_size,current_jday,False,Quiet)
            window_matrix.append(window)
            window_centers.append(center)
            
            # if the user has chosen to ignore years, the code must stop at day 366.
            if current_jday==366:
                return window_centers,window_matrix
            else:
                current_jday=current_jday + 1
            index=index+1

    if not Quiet: print '{rolling_window} Finished!'
        

    return window_centers,window_matrix


def in_window(filelist, window_size, jday, year=False, Quiet=False):

    """
    Uses raster.grab_info to bin raster data by date
    
     this function returns a list of files within the window designation.
     This is useful for feeding into functions that create weekly/monthly/annual statistics
     from daily data. Use the rolling_window function (which calls this one) if you intend
     to iterate through many files for rolling statistics.

     This function only works for files whos naming conventions are supported by the
     'Grab_Data_Info' function, and relies upon the attributes stored in info.year and
     info.j_day
     
     Inputs:
       filelist        the list of files to include in the window. This could be easily
                       created with the list_files function.
       window_size     width of the window in days. used to group files
       jday            the julian day at which to center the window
       year            the year on which to center the window. If you wish to bin all days
                       at a given point in the year together for long term averages, leave
                       year input blank or set to 'False'. This will then consider all
                       julian days within the window for all years in 'filelist'

     Outputs:
       center          A file representing the center of the window, useful in naming.
       in_window       outputs only the files within the specified window.

     
    """
    
    # initialize empty lists for tracking
    in_window=[]
    yearlist=[]
    jdaylist=[]
    center_file=False

    # sanitize inputs
    jday=int(jday)
    window_size=int(window_size)
    filelist=Enforce_Filelist(filelist)
    
    # define list of acceptable values
    
    # if the window is an even number, it has to be centered on the half day
    # if the window is an odd number, it can be centered exactly on the day
    if window_size%2==0:
        window=range(-(window_size/2)+1,(window_size/2)+1)                   
    else:
        window=range(-((window_size-1)/2),((window_size-1)/2)+1)

    # generate concurent lists of acceptable parameters
    for day in window:
        if year:
            date= datetime.datetime(year,1,1) + datetime.timedelta(day+jday-1)
            yearlist.append(str(date.year))
        else:
            date= datetime.datetime(2010,1,1) + datetime.timedelta(day+jday-1)
        jdaylist.append(str(date.strftime('%j')))

    # if window is not year specific, make sure we include 366 when appropriate
    if not year and '365' in jdaylist and '001' in jdaylist:
        jdaylist.append('366')

    # gather statistics on the filelist.
    for item in filelist:
        info=Grab_Data_Info(item,False,True)

        if year:
            # checks to see if both day and year are on the respective lists
            if info.j_day in jdaylist and info.year in yearlist:

                # further verifies that they are for concurent list entries (not mismatched)
                if yearlist[jdaylist.index(info.j_day)]==info.year:
                    in_window.append(item)
                    
                    # if this files info indicates it is on the center julian day, save this info
                    if info.j_day==str(jday).zfill(3):
                        center_file=item
        else:
            # checks to make sure day only is within the window, without considering year
            if info.j_day in jdaylist:
                in_window.append(item)

                # if this files info indicates it is on the center julian day, save this info
                if info.j_day==str(jday).zfill(3):
                    center_file=item
                
    if not Quiet:
        if year:
            print('{in_window} Found ' + str(len(in_window)) + ' files in ['+ str(window_size) + 
                  ']day window: '+ str(jday) +'-'+ str(year))
        else:
            print('{in_window} Found ' + str(len(in_window)) + ' files in ['+ str(window_size) + 
                  ']day window: '+ str(jday))
 
    return center_file,in_window


def list_files(recursive, Dir, Contains=False, DoesNotContain=False, Quiet=False):

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
           Quiet           Set Quiet to 'True' if you don't want anything printed to screen.
                           Defaults to 'False' if left blank.
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
    if not Quiet:
        print '{list_files} Files found which meet all input criteria: ' + str(len(filelist))
        print '{list_files} finished! \n'
    
    return(filelist)





def del_empty_dirs(path):

    """Removes empty folders, used for cleaning up temporary workspace."""

    import os

    # only continue if the pathexists
    if os.path.isdir(path):

        # list files in directory
        files = os.listdir(path)
        
        # if zero files exist inside it, delete it.
        if len(files)==0:
            os.rmdir(path)
            return(True)
        
    return(False)


def rename(filename,replacethis,withthis,Quiet=False):

    """
    Simply renames files

     Inputs:
       filename        input file to rename    
       replacethis     String to be replaced. such as " " (a space) 
       withthis        What to replace the string with. such as "_" (an underscore)
       Quiet           Set Quiet to 'True' if you don't want anything printed to screen.
                       Defaults to 'False' if left blank.

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

        # tell the user about it.
        if not Quiet: print '{rename} renamed',filename,'to',newfilename
        
        return newfilename
    else:
        return filename


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
    

def enf_rastlist(filelist):

    """
    Sanitizes raster list inputs

     This function works exactly like enf_filelist, with the added feature of removing
     all filenames that are not of a raster type recognized by Arcmap.

     Input:    filelist        any list of files
     Output:   new_filelist    New list with all non-raster files in filelist removed.

     
    """

    # first place the input through the same requirements of any filelist
    filelist = enf_filelist(filelist)
    new_filelist=[]

    for filename in filelist:
        if raster.is_rast(filename):
            new_filelist.append(filename)

    return(new_filelist)



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
    filelist=Enforce_Filelist(filelist)
    new_filelist=[]

    feat_types=['shp']

    for filename in filelist:
        ext=filename[-3:]

        if os.path.isfile(filename):
            for feat_type in feat_types:
                if ext == feat_type:
                    new_filelist.append(filename)

    return(new_filelist)




def move(source,destination,Quiet=False):

    """Moves a file"""

    dest_path,name=os.path.split(destination)

    # create that directory if it doesnt already exist
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    try:     
        shutil.move(source,destination)
        if not Quiet:
            print '{Move_File} moved file : [' + source + ']'
    except:
        if not Quiet:
            print '{Move_File} Failed to move file : [' + source + ']'
        
    return(dest_path)



def exists(location):

    """Ensures inputlocation is either a file or a folder"""
    
    # if the object is neither a file or a location, return False.
    if not os.path.exists(location) and not os.path.isfile(location):
        print '{Exists} '+location + ' is not a valid file or folder!'
        sys.exit()
        return(False)
    
    #otherwise, return True.
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
    head,tail = os.path.split(inname)
    noext = tail.split('.')[:-1]
    noext='.'.join(noext)

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































