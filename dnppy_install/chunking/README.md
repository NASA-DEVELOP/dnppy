# Chunking

This small module is intended to allow more scalable raster operations by making it very simple to split rasters into smaller
slices for processing with less memory consumption. 

The concept is simple, there are "chunk_bundle"s which are comprised of "chunk"s. A "chunk" object simply contains a numpy array and 
an index location that represents its position in a larger "chunk_bundle", which in turn posses just an object list of its constituent 
chunks, as well as the geospatial metadata associated with the entire image. A "chunk_bundle" posesses all the necessary methods
to load a new image and split it into chunks, as well as aggregate constituent chunks into a raster image to be saved to disk.

Each of the chunks within a chunk bundle may be accessed with simple indexing.
chunk_bund[i] will return the i'th chunks numpy array.
