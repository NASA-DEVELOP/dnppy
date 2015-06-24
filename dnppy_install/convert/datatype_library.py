__author__ = 'jwely'
__all__ = ["datatype_library", "datatype"]

import os
from dnppy import textio

def datatype_library():
    """
    this function builds the datatype_library dict out of file
    datatype_library.csv and returns it. Adding to this datatype
    library should be done by editing the csv file, not this code.
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

        # read text file rows
        name = str(row[0].replace(" ",""))
        proj = str(row[1].replace(" ",""))
        xtl  = float(row[2])
        xps  = float(row[3])
        xpr  = float(row[4])
        ytl  = float(row[5])
        yps  = float(row[6])
        ypr  = float(row[7])

        # build projection text from projection ID file
        proj_fname = os.path.join(dirname,"lib","prj","{0}.prj".format(proj))
        with open(proj_fname, "r") as f:
            proj_text = f.read()

        # assemble the geotransform
        geotrans = (xtl, xps, xpr, ytl, ypr, yps)

        # create the datatype instance
        datatype_dict[name] = datatype(name = name,
                                       projectionID = proj,
                                       geotransform = geotrans,
                                       projectionTXT = proj_text)

    return datatype_dict


class datatype():
    """
    simple class for dnppy supported download and convert
    NASA/NOAA/WeatherService/USGS data types
    """

    def __init__(self, name= None, projectionID = None, geotransform = None, projectionTXT = None):
        """
        Inputs:
            name            (str) the product name, (descriptive)
            projectionID    (str) projection ID according to prj files
                                downloaded from "spatialreference.org"
            geotransform    (list floats) geotransform array, lsit of 6
                                float values in the gdal ordering:
                                [top left x,
                                w-e pixel resolution,
                                0,
                                top left y,
                                0,
                                n-s pixel resolution (negative value)]
        """

        self.name = name
        self.projectionID = projectionID
        self.geotransform = geotransform
        self.projectionTXT = projectionTXT



def main():
    """ print summary of entire datatype library
    """
    datalib = datatype_library()
    for entry in datalib:
        print("{0}: \n projectionID  = {1}\n projectionTXT = {2} \n geotransform  = {3}".format(datalib[entry].name,
              datalib[entry].projectionID,
              datalib[entry].projectionTXT,
              datalib[entry].geotransform))

    return


if __name__ == "__main__":
    main()

