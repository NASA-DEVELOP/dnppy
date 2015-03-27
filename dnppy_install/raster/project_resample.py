



def project_resamp(filelist, reference_file, outdir = False,
                   resampling_type = False, cell_size = False):

    """
    Wrapper for multiple arcpy projecting functions. Projects to reference file
    
     Inputs a filelist and a reference file, then projects all rasters or feature classes
     in the filelist to match the projection of the reference file. Writes new files with a
     "_p" appended to the end of the input filenames. This also will perform resampling.

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
    core.exists(reference_file)
           
    rasterlist  = enf_rastlist(filelist)
    featurelist = core.enf_featlist(filelist)
    cleanlist   = rasterlist + featurelist

    # ensure output directoryexists
    if not os.path.exists(outdir):
        os.makedirs(outdir)
        
    # grab data about the spatial reference of the reference file. (prj or otherwise)
    if reference_file[-3:]=='prj':
        Spatial_Reference = arcpy.SpatialReference(Spatial_Reference)
    else:
        Spatial_Reference = arcpy.Describe(reference_file).spatialReference
        
    # determine wether coordinate system is projected or geographic and print info
    if Spatial_Reference.type == 'Projected':
        print('Found {0} projected coord system'.format(Spatial_Reference.PCSName))
    else:
        print('Found {0} geographic coord system'.format(Spatial_Reference.GCSName))


    for filename in cleanlist:
        
        # create the output filename
        outname = core.create_outname(outdir, filename, 'p')

        # use ProjectRaster_management for rast files
        if is_rast(filename):
            if resampling_type:
                
                arcpy.ProjectRaster_management(
                    filename, outname, Spatial_Reference,resampling_type, cell_size)
                print('Wrote projected and resampled file to {0}'.format(outname))
                
            else:
                arcpy.ProjectRaster_management(filename, outname, Spatial_Reference)
                print('Wrote projected file to {0}'.format(outname))
                
        # otherwise, use Project_management for featureclasses and featurelayers
        else:
            arcpy.Project_management(filename,outname,Spatial_Reference)
            print('Wrote projected file to {0}'.format(outname))

    print("finished projecting!")
    return(Spatial_Reference)
