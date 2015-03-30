# local imports
from .figures import *
from .grab_data_info import *
from .null_values import *
from .project_resample import *
from .raster_clipping import *
from .raster_enforcement import *
from .raster_numpy_inter import *
from .raster_overlap import *
from .raster_stack import *
from .raster_statistics import *

def temporal_fill(filelist,Quiet=False):

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

    print 'This function will eventually be developed' 
    print 'if you need it ASAP, contact the geoinformatics Fellows!'
    
    return
