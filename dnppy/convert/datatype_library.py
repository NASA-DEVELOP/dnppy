__author__ = 'jwely'
__all__ = ["datatype_library", "datatype"]

import os
from osgeo import osr
from dnppy import textio

def datatype_library():
    """
    This function builds the datatype_library dict out of file datatype_library.csv
    and returns it. Adding to this datatype library should be done by editing
    the csv file, not this code. Note that the standard format for names is
    ``<product short name>_<resolution identifier>_<coverage area>``, such as
    "TRMM_1.0_GLOBAL", or "GPM_IMERG_0.1_GLOBAL".

    Geotransform math used to create the array [A, B, C, D, E, F]

    .. code-block:: python

        x = A + iB + jC
        y = D + iE + jF

    Where x,y are real spatial coordinates, and i,j are matrix indices.
    A, B, C, D, E, F and are coefficients that make up the geotransformation array.

    :return datatype_library_dict: A dictionary
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
        proj = str(row[1].replace(" ","").split("-")[-1])
        proj_lib = str("-".join(row[1].replace(" ","").split("-")[:-1]))
        A  = float(row[2])
        B  = float(row[3])
        C  = float(row[4])
        D  = float(row[5])
        E  = float(row[6])
        F  = float(row[7])
        dls  = str(row[8])

        # build projection text from osr library
        if proj_lib == "EPSG":
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(int(proj))
            proj_text = srs.ExportToWkt()

        # read projection from SR-ORG prj file.
        else:
            proj_fname = os.path.join(dirname, "lib","prj","{0}.prj".format(proj))
            with open(proj_fname, "r") as f:
                proj_text = f.read()


        # assemble the geotransform
        geotrans = (A, B, C, D, E, F)

        # create the datatype instance
        datatype_dict[name] = datatype(name = name,
                                       projectionID = "-".join([proj_lib, proj]),
                                       geotransform = geotrans,
                                       projectionTXT = proj_text,
                                       downloadSource = dls)
    return datatype_dict



class datatype():
    """
    simple class for dnppy supported download and convert
    NASA/NOAA/WeatherService/USGS data types.

    :param name:            the product name (descriptive string)
    :param projectionID:    (str) projection ID according to spatialreference.org
    :param geotransform:    (list of floats) geotransform array, list of 6 float
                            values in  the gdal ordering.
    """
    def __init__(self, name= None, projectionID = None,
                 geotransform = None, projectionTXT = None, downloadSource = None):

        self.name = name
        self.projectionID = projectionID
        self.geotransform = geotransform
        self.projectionTXT = projectionTXT
        self.downloadSource = downloadSource


    def __str__(self):
        """ governs "print" behavior"""

        str = "{0}, {1}, {2}, [{3}]".format(self.name, self.projectionID,
                                          self.geotransform, self.downloadSource)
        return str


def main():
    """ print summary of entire datatype library """

    datalib = datatype_library()
    for data in datalib:
        print(datalib[data])


if __name__ == "__main__":
    main()

