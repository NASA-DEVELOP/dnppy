__author__ = 'jwely'

import numpy
import os
from chunk import chunk
# from dnppy import raster      # please see chunk_bundle.read() for dnppy.raster import

class chunk_bundle():
    """
    Creates a chunk bundle object.

    it can be used to pass smaller pieces of raster data to complex functions
    and reduce memory consumption in those functions.

    Presently, chunks are not saved individually, but are always bundled to form the
    undivided raster image. This allows chunks to be individually passed through more
    complex processing tasks then re-assmbled. They can be passed sequentially to reduce
    memory consumption, or in parallel to increase performance where memory isn't as
    limited (for suitable tasks).

    In the future, writing chunks to disk and dropping them from memory may be a good
    idea to truly maximize the data volume that a limited memory space can handle.

    NOTE:
    For intended functionality, this module uses a dnppy wrapper of the
    arcpy.RasterToNumPyArray function that passes a numpy array and a metadata object.
    This module SHOULD allow non-arcmap users to import and export images without
    geospatial metadata associated with them. That requires the simple CV python module.
    """

    def __init__(self, rasterpath, num_chunks = 0, chunk_list = [],
                                             metadata = None, force_scv = False):
        """
        Creates a chunk bundle.

        Two probable use cases:
            1) loading raster to split into smaller chunks with:
                inchunks = chunk_bundle(rasterpath, num_chunks = #)
                inchunks.read()

            2) building new chunk_bundle with processed data, passing on old chunks metadata:
                outchunks = chunk_bundle(rasterpath,
                                        chunk_list = [chunk1, chunk2,...],
                                        metadata = metadata)
                outchunks.write()
        """

        self.rasterpath = rasterpath    # full filepath to raster location
        self.num_chunks = num_chunks    # number of chunks to subdivide or construct this into
        self.chunk_list = chunk_list    # list of chunk objects (consitutent chunks)
        self.metadata   = metadata      # raster metadata object for this chunk

        self.force_scv  = force_scv     # forces simple CV module to be used instead of dnppy.
                                            # good for machines without arcmap installed.

        return


    def __getitem__(self, index):
        """ allows builtin __getitem__ to be used to get chunks by their integer ID numbers """

        for chunk_obj in self.chunk_list:
            if chunk_obj.index == index:
                return chunk_obj.data

        else: raise Exception("No chunk with chunk_id = {0}".format(index))



    def __setitem__(self,index, item):
        """ allows chunk data to be altered easily from the chunk bundle"""

        for chunk_obj in self.chunk_list:
            if chunk_obj.index == index:
                chunk_obj = item
                return

        else: raise Exception("No chunk with chunk_id = {0}".format(index))


    def _assemble_chunks(self):
        """ stitches constituent chunks back together into one numpy array """

        # stitch chunks together
        if self.num_chunks == 1:
            bundle_data = self.chunk_list[0]
        else:

            # concatenate the first two chunks
            bundle_data = numpy.concatenate((self[0], self[1]), axis = 1)

            # concatenate the rest of them
            for i in range(2,len(self.chunk_list)):
                bundle_data = numpy.concatenate((bundle_data, self[i]), axis = 1)

        return bundle_data



    def read(self):
        """ loads a raster image and splits it into roughly equal width vertical slices"""

        print("Loading input raster {0} and splitting into {1} chunks!".format(
                                    os.path.basename(self.rasterpath), self.num_chunks))

        if self.num_chunks <1:
            raise Exception("Cannot split into any fewer than 1 chunk!")

        # loads entire raster as numpy array with metadata object
        if not self.force_scv:

            from dnppy import raster
            data, self.metadata = raster.to_numpy(self.rasterpath)

        # uses the simpleCV module to import raster without metadata
        else: pass


        # split the data and add new chunks to this raster
        ys, xs = data.shape
        width  = xs / float(self.num_chunks)

        for c in range(self.num_chunks):

            chunk_data  = data[:, int(c * width):int((c+1) * width)]
            new_chunk   = chunk(c, chunk_data)

            self.chunk_list.append(new_chunk)

        del data
        return


    def write(self, rasterpath):
        """
        writes the chunk_bundle to its rasterpath """


        # write with metadata using dnppy and arcpy.
        if self.metadata and not self.force_scv:
            from dnppy import raster
            raster.from_numpy(self._assemble_chunks(), self.metadata, rasterpath)

        # write without metadata using simple CV
        else: pass


        return


    def ingest(self, new_chunk_obj):
        """
        places a chunk into the chunk bundle.

        If chunk with that ID already exists, it will be replaced.
        """

        # delete any chunk already existing at the index location of the new chunk object
        for chunk_obj in self.chunk_list:
            if chunk_obj.index == new_chunk_obj.index:
                self.chunk_list.remove(new_chunk_obj.index)

        self.chunk_list.append(new_chunk_obj)
        return



# testing area
if __name__ == "__main__":

    path = r"C:\Users\jwely\Desktop\troubleshooting\test_in_MODIS\MYD11A1.A2013001_day_clip_W05_C2014001_Avg_K_C_p_GSC.tif"
    num  = 2

    c = chunk_bundle(path, num)
    c.read()

    c[0] += 10

    test = c.write(r"C:\Users\jwely\Desktop\troubleshooting\chunk_test.tif")