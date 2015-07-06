__author__ = "jwely"
__all__ = ["gap_fill_temporal"]

def gap_fill_temporal(rasterlist, mode = "MOST_RECENT"):
    """
    This function is designed to input a time sequence of rasters with partial voids and
    output a copy of each input image with every pixel equal to the last good value taken.
    This function will step forward in time through each raster and fill voids from the values
    of previous rasters. The resulting output image will contain all the data that was in the
    original image, with the voids filled with older data. A second output image will be
    generated where the pixel values are equal to the age of each pixel in the image. So
    if a void was filled with data thats 5 days old, the "age" raster will have a value of
    "5" at that location.
    """
    print rasterlist
    print mode

    print("this function is a stub")