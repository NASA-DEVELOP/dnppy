__author__ = 'jwely'

import os
from datetime import datetime

class modis_metadata():
    """
    Creates metadata object from MODIS filenames. these metadata objects
    help to interpret files with common MODIS naming conventions into meaningful
    metadata. In order for this to work, the begining of the filename must remain
    untouched from the original download name. In order to customize filenames, you should
    add only suffixes, usually separated by underscores.

    :param filename:        the filename or filepath to a MODIS named file.

    =============== ========================================================================
    Attribute       Description
    =============== ========================================================================
    product         the modis product, such as MOD10A1 or MYD11A1
    datetime_obj    a datetime object of tile date
    year            the year of the modis tile
    j_day           the julian day of the modis tile
    month           the number of the month (ex 1)
    month_name      the name of the month (ex January)
    day             the integer day of the month
    tile            the modis tile, usually of format "h##v##"
    type            always equal to "MODIS"
    version         the algorithm version, always 3 digits, usually 005 or 041
    tag             processing tag (used by the DAACs)
    suffix          additional file suffixes that are not part of standard naming convention
    extension       the file extension, such as "hdf", "tif", etc...
    =============== ========================================================================
    """

    def __init__(self, filename):

        # ensure only the filename is given
        self.filename = os.path.basename(filename)

        if "_L2." in filename:
            self._interpret_L2()
        else:
            self._interpret_default()


    def __str__(self):
        """ returns filename attribute """
        return self.filename


    def _interpret_L2(self):
        """
        Some level 2 data products use a different naming scheme, interpret those here

        example -  MOD11_L2.A2015001.1105.041.2015005192527.hdf
        """

        # split the filename by the "."
        n       = self.filename.split('.')
        end     = n[4]

        # assign attributes
        self.product        = n[0]
        self.datetime_obj   = datetime.strptime(n[1], "A%Y%j")
        self.year           = self.datetime_obj.year
        self.j_day          = self.datetime_obj.strftime("%j")
        self.month          = self.datetime_obj.month
        self.month_name     = self.datetime_obj.strftime("%b")
        self.day            = self.datetime_obj.day
        self.tile           = "h{0}v{1}".format(n[2][0:2],n[2][2:4])
        self.type           = 'MODIS'
        self.version        =  n[3]
        self.tag            = end[:13]
        self.suffix         = end[13:]
        self.extension      = n[5]


    def _interpret_default(self):
        """
        Parses the most universal format of MODIS naming conventions

        example - MYD11A1.A2013121.h11v05.041.2013122220607.hdf
        """
        # split the filename by the "."
        n       = self.filename.split('.')
        end     = n[4]

        # assign attributes
        self.product        = n[0]
        self.datetime_obj   = datetime.strptime(n[1], "A%Y%j")
        self.year           = self.datetime_obj.year
        self.j_day          = self.datetime_obj.strftime("%j")
        self.month          = self.datetime_obj.month
        self.month_name     = self.datetime_obj.strftime("%b")
        self.day            = self.datetime_obj.day
        self.tile           = n[2]
        self.type           = 'MODIS'
        self.version        =  n[3]
        self.tag            = end[:13]
        self.suffix         = end[13:]
        self.extension      = n[5]



if __name__ == "__main__":

    fpath = r"MYD11A1.A2013121.h11v05.041.2013122220607.hdf"
    mm = modis_metadata(fpath)
    print mm.__dict__

    fpath = r"MOD11_L2.A2015001.1105.041.2015005192527.hdf"
    mm = modis_metadata(fpath)
    print mm.__dict__