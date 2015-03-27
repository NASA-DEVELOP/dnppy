

def stack(raster_paths):
    """
    Creates 3d numpy array from multiple coincident rasters
    
    This function is to create a 3d numpy array out of multiple coincident rasters.
    Usefull for layering multiple bands in a scene or bulding a time series "data brick".
    It is important that all layers that are stacked are perfectly coincident, having
    identical pixel dimensions, resolution, projection, and spatial referencing. 

    Inputs:
        raster_paths    list of filepaths to rasters to be stacked. They will be stacked in
                        the same order as they ar einput

    Returns:
        stack           3d numpy array containing stacked raster data
        meta            metadata of the first raster layer. All layers should have identical
                        metadata.
    """


    print("this function isn't finished!")
    
    for z, raster in enumerate(raster_paths):
        temp_image, temp_meta = to_numpy(raster)

        if z==0:
            stack = numpy.zeros((len(raster_paths), temp_meta.Ysize, temp_meta.Xsize))
        
        stack[z,:,:] = temp_image
        meta = temp_meta
        print(vars(meta))
        
    return stack, meta
