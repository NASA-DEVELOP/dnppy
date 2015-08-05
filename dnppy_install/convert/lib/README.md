The datatype_library.csv file contains the following fields:
##### Unique_Name
a simple unique identifier
##### projectionID
The ID number associated with the projection, use spatialreference.org or the EPSG website to find these
##### A, B, C, D, E, F
Geotransform coefficients used to perform a two dimensional coordinate transform between matrix space and projection space according to the equations:
            x = A + iB + jC
            y = D + iE + jF

##### download_source
The download location where data matching this format is typically retreived