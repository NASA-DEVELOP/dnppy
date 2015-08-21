
__all__ = ["degree_days"]

from to_numpy import to_numpy
from from_numpy import from_numpy

import numpy

def degree_days(T_base, Max, Min, NoData_Value, outpath = False, roof = False, floor = False):
    """
    Inputs rasters for maximum and minimum temperatures, calculates Growing Degree Days

    this function is built to perform the common degree day calculation on either a pair
    of raster filepaths, a pair of numpy arrays It requires, at minimum a maximum
    temperature value, a minimum temperature value, and a base temperature. This
    equation could also be used to calculate Chill hours or anything similar.

    The equation is ``[(Max+Min)/2 + T_base]``

    where values in Max which are greater than roof are set equal to roof
    where values in Min which are less than floor are set equal to floor
    consult [https://en.wikipedia.org/wiki/Growing_degree-day] for more information.

    :param T_base:          base temperature to ADD, be mindful of sign convention.
    :param Max:             filepath, numpy array, or list of maximum temperatures
    :param Min:             filepath, numpy array, or list of minimum temperatures
    :param NoData_Value:    values to ignore (must be int or float)
    :param outpath:         filepath to which output should be saved. Only works if Max and Min inputs
                            are raster filepaths with spatial referencing.
    :param roof:            roof value above which Max temps do not mater
    :param floor:           floor value below which Min temps do not mater

    :return deg_days:       a numpy array of the output degree_days
    """

    #FIXME: doesn't fit styleguide. does not operate in batch and return list of output filepaths

    output_filelist = []

    # format numerical inputs as floating point values
    T_base = float(T_base)
    if roof:
        roof  = float(roof)
    if floor:
        floor = float(floor)

    # Determine the type of input and convert to useful format for calculation
    # acceptable input formats are filepaths to rasters, numpy arrays, or lists.
    if type(Max) is list and type(Min) is list:
        
        # if the first entry in a list is a string, assume it is a filename that has
        # been placed into a list.
        if type(Max[0]) is str and type(Min[0]) is str:
            Max = Max[0]
            Min = Min[0]

            # load in the min and max files.
            highs, meta = to_numpy(Max)
            lows, meta  = to_numpy(Min)

            print('Found spatially referenced image pair!')
        else:
            highs = numpy.array(Max)
            lows  = numpy.array(Min)
            
    # if they are already numpy arrays
    elif type(Max) is numpy.ndarray:
            highs = Max
            lows  = Min
    else:
        raise Exception("invalid inputs!")
            
    # Begin to perform the degree day calculations

    # apply roof and floor corrections if they have been specified
    if roof:
        highs[highs >= roof] = roof
    if floor:
        lows[lows <=floor] = floor

    # find the shapes of high and low arrays
    xsh, ysh = highs.shape
    xsl, ysl = lows.shape

    # only continue if min and max arrays have the same shape
    if xsh == xsl and ysh == ysl:
        
        # set empty degree day matrix
        deg_days = numpy.zeros((xsh,ysh))
        
        # perform the calculation
        for x in range(xsh):
            for y in range(ysh):
                if round(highs[x,y]/NoData_Value,10) !=1 and round(lows[x,y]/NoData_Value,10) != 1:
                    deg_days[x,y] =((highs[x,y] + lows[x,y])/2) + T_base
                else:
                    deg_days[x,y] = NoData_Value
                
    # print error if the arrays are not the same size
    else:
        print('Images are not the same size!, Check inputs!')
        return False

    # if an output path was specified, save it with the spatial referencing information.
    if outpath and type(Max) is str and type(Min) is str:
        from_numpy(deg_days, meta, outpath)
        print('Output saved at : ' + outpath)
        
    return deg_days



