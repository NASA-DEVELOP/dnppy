__author__ = 'jwely'


import numpy

class chunk():
    """
    creates an individual chunk object (vertical slice of a 2 or 3d raster image).

    Individual chunks do NOT store metadata! Any metadata should be managed
    at the chunk_bundle level. Object chunk_bundles are made of chunk lists,
    ordered by index number.
    """

    def __init__(self, index, data = None):
        """ initializes a chunk object. """

        self.index  = index     # integer value denoting position within chunk_bundle
        self.data   = data      # a numpy masked_array type

        return

    def __getitem__(self):
        return self.data


    def __setitem__(self, item):

        con1 = isinstance(item, numpy.ma.core.MaskedArray)
        con2 = isinstance(item, numpy.ndarray)

        if con1 or con2:
            self.data = item

        return