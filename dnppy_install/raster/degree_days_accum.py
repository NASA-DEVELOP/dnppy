__author__ = 'jwely'
__all__ = ["degree_days_accum"]

def degree_days_accum(rasterlist, critical_values = False, outdir = False):

    """
    Accumulates degree days in a time series rasterlist

     This function is the logical successor to calc.degree_days. Input a list of rasters
     containing daily data to be accumulated. Output raster for a given day will be the sum
     total of the input raster for that day and all preceding days. The last output raster in
     a years worth of data (image 356) would be the sum of all 365 images. The 25th output
     raster would be a sum of the first 25 days.
     Critical value rasters will also be created. Usefull for example: we wish to know on what day
     of our 365 day sequence every pixel hits a value of 100. Input 100 as a critical value
     and that output raster will be generated.

     Inputs:
       rasterlist          list of files, or directory containing rasters to accumulate
       critical_values     Values at which the user wishes to know WHEN the total accumulation
                           value reaches this point. For every critical value, an output
                           raster will be created. This raster contains integer values denoting
                           the index number of the file at which the value was reached.
                           This input must be a list of ints or floats, not strings.
       outdir              Desired output directory for all output files.
    """

    rasterlist = core.enf_rastlist(rasterlist)

    if critical_values:
        critical_values = core.enf_list(critical_values)

    # critical values of zero are problematic, so replace it with a small value.
    if 0 in critical_values:
        critical_values.remove(0)
        critical_values.append(0.000001)

    if outdir and not os.path.exists(outdir):
        os.makedirs(outdir)

    for i,raster in enumerate(rasterlist):

        image, meta = raster.to_numpy(raster,"float32")
        xs, ys = image.shape

        if i==0:
            Sum  = numpy.zeros((xs,ys))
            Crit = numpy.zeros((len(critical_values),xs,ys))

        if image.shape == Sum.shape:

            # only bother to proceed if at least one pixel is positive
            if numpy.max(image) >= 0:
                for x in range(xs):
                    for y in range(ys):

                        if image[x,y] >= 0:
                            Sum[x,y] = Sum[x,y]+image[x,y]

                        if critical_values:
                            for z,critical_value in enumerate(critical_values):
                                if Sum[x,y] >= critical_value and Crit[z,x,y]==0:
                                    Crit[z,x,y] = i
        else:
            print "Encountered an image of incorrect size! Skipping it!"

        Sum     = Sum.astype('float32')
        outname = core.create_outname(outdir, raster, "Accum")
        raster.from_numpy(Sum, meta, outname)

        del image

    # output critical accumulation rasters.
    Crit = Crit.astype('int16')
    crit_meta = meta
    crit_meta.NoData_Value = 0
    head , tail = os.path.split(outname)        # place these in the last raster output location
    for z, critical_value in enumerate(critical_values):
        outname = os.path.join(head,"Crit_Accum_Index_Val-{0}.tif".format(str(critical_value)))
        print "Saving :",outname
        raster.from_numpy(Crit[z,:,:], crit_meta, outname)

    return