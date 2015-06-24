__author__ = 'jwely'

import os
from dnppy import textio
from datatype import datatype

def datatype_library():
    """
    this function builds the datatype_library dict out of file
    datatype_library.csv and returns it. Adding to this datatype
    library should be done by editing the csv file, not this code.
    """

    datatype_dict = {}

    text_data = textio.read_csv("datatype_library.csv")
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
        dirname = os.path.dirname(__file__)
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

