__author__ = 'jwely'
__all__ = ["is_rast"]
import os

def is_rast(filename):
    """
    Verifies that input filename exists, and is of a valid raster format

    :param filename:  check if this filename is a valid accessible raster.
    :return <bool>: returns True if filename is valid accessible raster. False otherwise.
    """

    rast_types=['bil','bip','bmp','bsq','dat','gif','img','jpg','jp2','png','tif',
                'BIL','BIP','BMP','BSQ','DAT','GIF','IMG','JPG','JP2','PNG','TIF']
    ext = filename[-3:]

    if os.path.isfile(filename):
        for rast_type in rast_types:
            if ext == rast_type:
                return True

    return False
