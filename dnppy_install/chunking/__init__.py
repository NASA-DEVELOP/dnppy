
"""
This little chunking module is used to subset raster images into slices
to allow tasks with large memory requirements to be subsetted a little more
easily.

It was not included in the raster module, because it has applicability
outside of an armap geospatial environment.
"""

__author__ = ["Jeffry Ely, jeff.ely.08@gmail.com"]


from .chunking import *
    
