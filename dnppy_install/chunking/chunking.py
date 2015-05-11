

__author__ = ["Jeffry Ely, Jeff.ely.08@gmail.com"]

# standard imports
import numpy


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
                return chunk_obj
            
        else: raise Exception("No chunk with chunk_id = {0}".format(index))

        
    def read(self):
        """ loads a raster image and splits it into roughly equal width vertical slices"""

        if self.num_chunks <1:
            raise Exception("Cannot split into any fewer than 1 chunk!")

        # loads entire raster as numpy array with metadata object
        if not self.force_scv:
            
            from dnppy import raster
            data, self.metadata = raster.to_numpy(self.rasterpath)

        # uses the simpleCV module to import raster without metadata  
        else: pass
        

        # split the data and add new chunks to this raster
        xs, ys = data.shape
        width  = xs / float(self.num_chunks)

        for c in range(self.num_chunks):
            
            chunk_data  = data[int(c * width):int((c+1) * width),:]
            new_chunk   = chunk(c, chunk_data)
            
            self.chunk_list.append(new_chunk)

        del data
        return
    

    def write(self, rasterpath = None):
        """ writes the chunk_bundle to its rasterpath (allows new filepath input) """

        if not rasterpath:
            rasterpath = self.rasterpath
            
        # write with metadata using dnppy and arcpy.
        if self.metadata and not self.force_scv:
            raster.from_numpy()

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
            if chunk_obj.index == index:
                self.chunk_list.remove(new_chunk_obj.index)

        self.chunk_list.append(new_chunk_obj)
        return



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
            

    
if __name__ == "__main__":


    path = r"C:\Users\jwely\Desktop\troubleshooting\test_out_MODIS\2013-Feb_AVG.tif"
    num  = 3
    
    c = chunk_bundle(path, num)
    
