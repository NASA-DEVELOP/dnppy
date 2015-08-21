
__all__ = ["project_resample"]

# local imports
from dnppy import core
from enf_rastlist import enf_rastlist
from is_rast import is_rast

import os
import arcpy

def project_resample(filelist, reference_file, outdir = None,
                   resampling_type = None, cell_size = None):
    """
    Wrapper for multiple arcpy projecting functions. Projects to reference file. Inputs a
    filelist and a reference file, then projects all rasters or feature classes
    in the filelist to match the projection of the reference file. Writes new files with a
    in the filelist to match the projection of the reference file. Writes new files with a
    "_p" appended to the end of the input filenames. This also will perform resampling.

    :param filelist:            list of files to be projected
    :param outdir:              optional desired output directory. If none is specified, output files
                                will be named with '_p' as a suffix.
    :param reference_file:      Either a file with the desired projection, or a .prj file.
    :param resampling_type:     exactly as the input for arcmaps project_Raster_management function
    :param cell_size:           exactly as the input for arcmaps project_Raster_management function

    :return output_filelist:    list of files created by this function.
    """

    output_filelist = []

    # sanitize inputs
    if not core.exists(reference_file):
        raise ValueError("reference file does not exist!")

    rasterlist  = enf_rastlist(filelist)
    featurelist = [f for f in filelist if ".shp" in f]
    cleanlist   = rasterlist + featurelist

    # ensure output directory exists
    if outdir is not None and not os.path.exists(outdir):
        os.makedirs(outdir)
        
    # grab data about the spatial reference of the reference file. (prj or otherwise)
    if reference_file[-3:]=='prj':
        Spatial_Reference = arcpy.SpatialReference(reference_file)
    else:
        Spatial_Reference = arcpy.Describe(reference_file).spatialReference

        # determine cell size
        if cell_size is None:
            cx = arcpy.GetRasterProperties_management(reference_file, "CELLSIZEX").getOutput(0)
            cy = arcpy.GetRasterProperties_management(reference_file, "CELLSIZEY").getOutput(0)
            cell_size = "{0} {1}".format(cx,cy)

        
    # determine wether coordinate system is projected or geographic and print info
    if Spatial_Reference.type == 'Projected':
        print('Found {0} projected coord system'.format(Spatial_Reference.PCSName))
    else:
        print('Found {0} geographic coord system'.format(Spatial_Reference.GCSName))


    for filename in cleanlist:
        
        # create the output filename
        outname = core.create_outname(outdir, filename, 'p')
        output_filelist.append(Spatial_Reference)

        # use ProjectRaster_management for rast files
        if is_rast(filename):
            arcpy.ProjectRaster_management(filename,
                        outname, Spatial_Reference, resampling_type, cell_size)
            print('Wrote projected and resampled file to {0}'.format(outname))
                
        # otherwise, use Project_management for featureclasses and featurelayers
        else:
            arcpy.Project_management(filename,outname,Spatial_Reference)
            print('Wrote projected file to {0}'.format(outname))

    print("finished projecting!")
    return output_filelist
