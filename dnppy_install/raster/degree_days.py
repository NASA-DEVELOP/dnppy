
from to_numpy import to_numpy
from from_numpy import from_numpy

import numpy


def degree_days(T_base, Max, Min, NoData_Value, outpath = False, roof = False, floor = False):

    """
    Inputs rasters for maximum and minimum temperatures, calculates Growing Degree Days
    
     this function is built to perform the common degree day calculation on either a pair
     of raster filepaths, a pair of numpy arrays, or a pair of lists. It requires, at minimum
     A maximum temperature value, a minimum temperature value, and a base temperature.
     This equation could also be used to calculate Chill hours or anything similar. 

     The equation is as follows:
                                   [(Max+Min)/2 + T_base]

     where values in Max which are greater than roof are set equal to roof
     where values in Min which are lesser than floor are set equal to floor
     consult [https://en.wikipedia.org/wiki/Growing_degree-day] for more information.

     Inputs:
       T_base          base temperature to ADD, be mindful of sign convention.
       Max             filepath, numpy array, or list of maximum temperatures
       Min             filepath, numpy array, or list of minimum temperatures
       NoData_Value    values to ignore (must be int or float)
       outpath         filepath to which output should be saved. Only works if Max and Min inputs
                       are raster filepaths with spatial referencing.
       roof            roof value above which Max temps do not mater
       floor           floor value below which Min temps do not mater
       Quiet           Set True to suppress output

     Outputs:
       degree_days     numpy array of output values. This same data is saved if outpath is
                       not left at its default value of False.
    """

    # format numerical inputs as floating point values
    T_base = float(T_base)
    if roof:
        roof  = float(roof)
    if floor:
        floor = float(floor)

    # Determine the type of input and convert to useful format for calculation
    # acceptable input formats are filepaths to rasters, numpy arrays, or lists.
    if type(Max) is list and type(Min) is list:
        
        # if the first entry in a list is a string, asume it is a filename that has
        # been placed into a list.
        if type(Max[0]) is str and type(Min[0]) is str:
            Max = Max[0]
            Min = Min[0]

            # load in the min and max files.
            highs, meta = to_numpy(Max)
            lows, meta  = to_numpy(Min)

            print 'Found spatialy referenced image pair!'
        else:
            highs = numpy.array(Max)
            lows  = numpy.array(Min)
            
    # if they are already numpy arrays
    elif type(Max) is numpy.ndarray:
            highs = Max
            lows  = Min
            
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
        degree_days = numpy.zeros((xsh,ysh))
        
        # perform the calculation
        for x in range(xsh):
            for y in range(ysh):
                if round(highs[x,y]/NoData_Value,10) !=1 and round(lows[x,y]/NoData_Value,10) != 1:
                    degree_days[x,y]=((highs[x,y] + lows[x,y])/2) + T_base
                else:
                    degree_days[x,y]=NoData_Value
                
    # print error if the arrays are not the same size
    else:
        print 'Images are not the same size!, Check inputs!'
        return(False)

    # if an output path was specified, save it with the spatial referencing information.
    if outpath and type(Max) is str and type(Min) is str:
        from_numpy(degree_days, meta, outpath)
        print('Output saved at : ' + outpath)
        
    return degree_days



