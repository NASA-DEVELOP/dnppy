__author__ = 'jwely'
__all__ = ["datatype_library", "datatype"]

import os
from dnppy import textio

def datatype_library():
    """
    this function builds the datatype_library dict out of file
    datatype_library.csv and returns it. Adding to this datatype
    library should be done by editing the csv file, not this code.

    geotransform math used to create the array [A, B, C, D, E, F]
            x = A + iB + jC
            y = D + iE + jF

        where x,y are real spatial coordinates, nd i,j
        are matrix indices. A, B, C, D, E, F and are
        coefficients that make up the geotransformation array.
    """

    # empty dict
    datatype_dict = {}

    # find path of this installation
    dirname = os.path.dirname(__file__)

    # read in the library
    lib_path = os.path.join(dirname,"lib","datatype_library.csv")
    text_data = textio.read_csv(lib_path)
    rows = text_data.row_data

    for row in rows:

        # interpret text file rows
        name = str(row[0].replace(" ",""))
        proj = str(row[1].replace(" ",""))
        A  = float(row[2])
        B  = float(row[3])
        C  = float(row[4])
        D  = float(row[5])
        E  = float(row[6])
        F  = float(row[7])
        dls  = str(row[8])

        # build projection text from projection ID file
        proj_fname = os.path.join(dirname,"lib","prj","{0}.prj".format(proj))
        with open(proj_fname, "r") as f:
            proj_text = f.read()

        # assemble the geotransform
        geotrans = (A, B, C, D, E, F)

        # create the datatype instance
        datatype_dict[name] = datatype(name = name,
                                       projectionID = proj,
                                       geotransform = geotrans,
                                       projectionTXT = proj_text,
                                       downloadSource = dls)

    return datatype_dict


class datatype():
    """
    simple class for dnppy supported download and convert
    NASA/NOAA/WeatherService/USGS data types
    """

    def __init__(self, name= None, projectionID = None,
                 geotransform = None, projectionTXT = None, downloadSource = None):
        """
        Inputs:
            name            (str) the product name, (descriptive)
            projectionID    (str) projection ID according to prj files
                                downloaded from "spatialreference.org"
            geotransform    (list floats) geotransform array, lsit of 6
                                float values in the gdal ordering:

                                x = A + iB + jC
                                y = D + iE + jF

                                where x,y are real spatial coordinates,
                                and i,j are matrix indices.
                                A, B, C, D, E, F and are coefficients that make
                                up the geotransformation array.
        """

        self.name = name
        self.projectionID = projectionID
        self.geotransform = geotransform
        self.projectionTXT = projectionTXT
        self.downloadSource = downloadSource



def main():
    """ print summary of entire datatype library
    """
    datalib = datatype_library()
    for entry in datalib:
        print("{0}: from {1} \n\tprojectionID  = {2}\n\tprojectionTXT = {3} \n\tgeotransform  = {4}".format(
              datalib[entry].name,
              datalib[entry].downloadSource,
              datalib[entry].projectionID,
              datalib[entry].projectionTXT,
              datalib[entry].geotransform))

    return


if __name__ == "__main__":
    main()

