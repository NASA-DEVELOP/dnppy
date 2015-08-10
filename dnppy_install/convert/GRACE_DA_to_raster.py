__author__ = ['djjensen']

import numpy as np
import os
import arcpy

def GRACE_DA_to_raster(folder, outdir = False, npy_file = False):
    """
    This function will convert a folder of GRACE Data Assimilation product binary files into individual tiffs
    or a single three-dimensional NumPy array. The input folder should contain only the binary files.

    Inputs:

        folder      the full path to the folder containing the binary files to be converted
        outdir      optional; the full path to the desired output folder
                    *if left False by default, the output file(s) will be place in the input folder
        npy_file    optional; option to save the data as a 3-dimensional NumPy array file instead of tiffs
                    *enter True to convert data to a single .npy file
                    *if left False by default, each binary file will be converted to tiff format instead
    """

    #Enforce the input path folder to ensure proper name handling
    infolder = os.path.abspath(folder)

    #Set the output folder to either the input out directory or input folder if outdir is left False
    if outdir:
        outfolder = outdir
    else:
        outfolder = infolder

    #Set the current directory to the input folder and create a list of files in it    
    os.chdir(infolder)
    files = os.listdir('.')

    #Create an empty 3-dimensional array to be populated
    array = np.empty((np.size(files), 112, 244))

    #Loop through each binary file and fill the new array with corresponding values 
    for i,fil in enumerate(files):
        local_filename = os.path.join('', fil)
        if os.path.splitext(local_filename)[1] == ".bin":
            test = np.fromfile(local_filename, '>f32')
            test2 = np.reshape(test,(np.size(test)/(244*112), 112, 244))
            test2[test2 == -999] = np.NAN
            test3 = np.nanmean(test2, axis=0)
            array[i,:,:] = test3

    #If the "npy_file" parameter is set to true, save the array to a single .npy file instead of many tiffs      
    if npy_file == True:
        name = "{0}-{1}.npy".format(os.path.splitext(files[0])[0], files[-1][15:21])
        outnpy = os.path.join(outfolder, name)
        np.save(outnpy, array)
        
    #If "npy_file" is left false, save each segment of the new array as a tiff
    else:     

        #Establish the lower left corner coordinates and the coordinate system for the data and set the iterator
        corner = arcpy.Point(-126.875, 23.875)
        coor_sys = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
        i = 0

        #Loop through each file to create names and convert from NumPy array to raster
        #Use the "Flip" tool to save the files and define the projection
        for bin_name in files:
            name = bin_name.replace(".bin", ".tif")
            array_i = array[i,:,:]
            raster = arcpy.NumPyArrayToRaster(array_i, corner, 0.25, 0.25)
            outname = os.path.join(outfolder, name)
            arcpy.Flip_management(raster, outname)
            arcpy.DefineProjection_management(outname, coor_sys)
            i += 1
            
        #Delete the extraneous '1' folder created in the input
        files = os.listdir('.')
        if files[0] == '1':
            os.rmdir(os.path.join(folder, files[0]))