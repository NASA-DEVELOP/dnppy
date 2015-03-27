


def extract_from_hdf(filelist, layerlist, layernames=False, outdir=False):

    """
    Extracts tifs from MODIS HDF files

     inputs:
       filelist    list of '.hdf' files from which data should be extracted
       layerlist   list of layer numbers to pull out as individual tifs should be integers
                   such as [0,4] for the 0th and 4th layer respectively.
       layernames  list of layer names to put more descriptive names to each layer
       outdir      directory to which tif files should be saved
                   if outdir is left as 'False', files are saved in the same directory as
                   the input file was found.
    """

    # enforce lists for iteration purposes and sanitize inputs
    filelist = core.enf_filelist(filelist)
    for filename in filelist:
        if '.xml' in filename:
            filelist.remove(filename)
            
    layerlist  = core.enf_list(layerlist)
    layernames = core.enf_list(layernames)
    
    # ignore user input layernames if they are invalid, but print warnings
    if layernames and not len(layernames)==len(layerlist):
        print('layernames must be the same length as layerlist!')
        print('ommiting user defined layernames!')
        layernames = False

    # create empty list to add failed file names into
    failed=[]

    # iterate through every file in the input filelist
    for infile in filelist:
        # pull the filename and path apart 
        path,name           = os.path.split(infile)
        arcpy.env.workspace = path

        for i in range(len(layerlist)):
            layer = layerlist[i]
            
            # specify the layer names.
            if layernames:
                layername = layernames[i]
            else:
                layername = str(layer).zfill(3)

            # use the input output directory if the user input one, otherwise build one  
            if outdir:
                if not os.path.exists(os.path.join(outdir,layername)):
                    os.makedirs(os.path.join(outdir,layername))
                    
                outname = os.path.join(outdir,layername,name[:-4] +'_'+ layername +'.tif')
            else:
                if not os.path.exists(os.path.join(path,layername)):
                    os.makedirs(os.path.join(path,layername))
                    
                outname = os.path.join(path,layername,name[:-4] +'_'+ layername +'.tif')

            # perform the extracting and projection definition
            try:
                # extract the subdataset
                arcpy.ExtractSubDataset_management(infile, outname, str(layer))
                
                # define the projection as the MODIS Sinusoidal
                define_projection(outname)
                
                print('Extracted ' + outname)
            except:
                print('Failed extract '+ outname + ' from ' + infile)
                failed.append(infile)
                
    print("Finished! \n") 
    return(failed)
