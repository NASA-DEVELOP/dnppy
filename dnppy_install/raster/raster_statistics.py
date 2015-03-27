

def many_stats(rasterlist, outdir, outname, saves = ['AVG','NUM','STD'],
                                   low_thresh = None, high_thresh = None):
    """
    Take statitics across many input rasters
    
     this function is used to take statistics on large groups of rasters with identical
     spatial extents. Similar to Rolling_Raster_Stats

     Inputs:
        rasterlist      list of raster filepaths for which to take statistics
        outdir          Directory where output should be stored.
        saves           which statistics to save in a raster. In addition to the options
                        supported by 
                           
                        Defaults to all three ['AVG','NUM','STD'].
        low_thresh      values below low_thresh are assumed erroneous and set to NoData
        high_thresh     values above high_thresh are assumed erroneous and set to NoData.
    """

    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    
    rasterlist = enf_rastlist(rasterlist)

    # build the empty numpy array based on size of first raster
    temp_rast, metadata = to_numpy(rasterlist[0])
    xs, ys              = temp_rast.shape
    zs                  = len(rasterlist)
    rast_3d             = numpy.zeros((xs,ys,zs))

    metadata.NoData_Value = 'nan'

    # open up the initial figure
    fig, im = make_fig(temp_rast)

    # populate the 3d matrix with values from all rasters
    for i,raster in enumerate(rasterlist):

        # print a status and open a figure
        print('working on file {0}'.format(raster))
        new_rast, new_meta  = to_numpy(raster, 'float32')
        update_fig(new_rast, fig, im)

        if not new_rast.shape == (xs,ys):
            print new_rast.shape

        # set rasters to inherit the nodata value of first raster
        if new_meta.NoData_Value != metadata.NoData_Value:
            new_rast[new_rast == new_meta.NoData_Value] = metadata.NoData_Value
            
        # set values outside thresholds to nodata values
        if not low_thresh == None:
            new_rast[new_rast < low_thresh] = metadata.NoData_Value
        if not high_thresh == None:
            new_rast[new_rast > high_thresh] = metadata.NoData_Value

        rast_3d[:,:,i] = new_rast

    # build up our statistics by masking nan values and performin matrix opperations
    rast_3d_masked  = numpy.ma.masked_array(rast_3d, numpy.isnan(rast_3d))

    if "AVG" in saves:
        avg_rast        = numpy.mean(rast_3d_masked, axis = 2)
        avg_rast        = numpy.array(avg_rast)
        update_fig(avg_rast, fig, im, "Average")
        time.sleep(2)

        avg_name = core.create_outname(outdir, outname, 'AVG', 'tif')
        print("Saving AVERAGE output raster as {0}".format(avg_name))
        from_numpy(avg_rast, metadata, avg_name)

    if "STD" in saves:
        std_rast        = numpy.std(rast_3d_masked, axis = 2)
        std_rast        = numpy.array(std_rast)
        update_fig(avg_rast, fig, im, "Standard Deviation")
        time.sleep(2)

        std_name = core.create_outname(outdir, outname, 'STD', 'tif')
        print("Saving STANDARD DEVIATION output raster as {0}".format(std_name))
        from_numpy(std_rast, metadata, std_name)
        
    if "NUM" in saves:
        num_rast        = (numpy.zeros((xs,ys)) + zs) - numpy.sum(rast_3d_masked.mask, axis = 2)
        num_rast        = numpy.array(num_rast)
        update_fig(avg_rast, fig, im, "Good pixel count (NUM)")
        time.sleep(2)

        std_name = core.create_outname(outdir, outname, 'NUM', 'tif')
        print("Saving NUMBER output raster as {0}".format(std_name))
        from_numpy(num_rast, metadata, num_name)
                   
    close_fig(fig, im)

    return
