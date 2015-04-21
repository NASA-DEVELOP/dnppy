# local imports
from grab_meta import *

import os
import arcpy


__author__ = ["Jeffry Ely, jeff.ely.08@gmail.com"]


class scene:
    """
    Defines a landsat scene object. Used to track band filepaths
    and pass raster objects to functions.

    band filepaths are read from the MTL file and stored as a dict.
    you may access them with

        from dnppy import landsat
        s = landsat.scene(MTL_path)

        s[1]        # the first band of scene "s"
        s[2]        # the second band of scene "s"
        s["QA"]     # the QA band of scene "s"

    Development Note:
        1) This is arcpy dependent, but in the future it should utilize
             custom functions that emulate RasterToNumPyArray and the dnppy metadata
             objects for all returns, thus eliminating all non-open source
             dependencies
        2) for good interchangability between landsat versions, it might be better
            to construct a dict whos keys are color codes or even wavelength values
            instead of band index numbers (which are do not correspond to similar colors
            between landsat missions)
    """

    def __init__(self, MTL_path, tif_dir = None):
        """
        builds the scene.

        In some cases, users may have their MTL file located somewhere other than
        their landsat data. In this instance, users should input the path to
        the landsat images as tif_dir.
        """

        self.mtl_dir    = os.path.dirname(MTL_path) # directory of MTL file
        self.meta       = grab_meta(MTL_path)       # dnppy landsat_metadata object
        self.in_paths   = {}                        # dict of filepaths to tifs
        self.rasts      = {}                        # dict of arcpy raster objects

        if not tif_dir:
            self.tif_dir = self.mtl_dir

        self._find_bands()   
        return
    

    def __getitem__(self, index):
        """ returns arcpy.raster objects from getitem indices """

        if not "B{0}".format(index) in self.rasts:
            self.rasts["B{0}".format(index)] = arcpy.Raster(self.in_paths["B{0}".format(index)])

        return self.rasts["B{0}".format(index)]


    def __iter__(self):
        """ defines iterative behavior when cast on a scene object"""

        for key in self.in_paths:
            yield self[key.replace("B","")]
    
    
    def _find_bands(self):
        """
        builds filepaths for band filenames from the MTL file

        in the future, methods associated with landsat scenes,
        (for example: NDVI calculation) could save rasters in the scene
        directory with new suffixes then add attribute values to the MTL.txt
        file for easy reading later, such as:

        FILE_NAME_PROD_NDVI = [filepath to NDVI tif]
        """

        # build a band list based on the landsat version
        if self.meta.SPACECRAFT_ID == "LANDSAT_8":
            bandlist = [1,2,3,4,5,6,7,8,9,10,11]

            # add in landsat 8s QA band with shortened name
            QA_name = self.meta.FILE_NAME_BAND_QUALITY
            self.in_paths["BQA"] = os.path.join(self.tif_dir,QA_name)

        elif self.meta.SPACECRAFT_ID == "LANDSAT_7":
            bandlist = [1,2,3,4,5,"6_VCID_1","6_VCID_2",7,8]

        elif self.meta.SPACECRAFT_ID == "LANDSAT_5":
            bandlist = [1,2,3,4,5,6,7]

        elif self.meta.SPACECRAFT_ID == "LANDSAT_4":
            bandlist = [1,2,3,4,5,6,7]
            
        # populate self.bands dict
        for band in bandlist:
            filename = getattr(self.meta, "FILE_NAME_BAND_{0}".format(band))
            filepath = os.path.join(self.tif_dir, filename)
            self.in_paths["B{0}".format(band)] = filepath
                
        return


    def get_cloud_mask(self):
        """ wraps dnppy.landsat.cloud_mask functions and applies them to this scene"""
        pass


    def get_surface_reflectance(self):
        """ wraps dnppy.landsat.surface_reflecance functions and applies them to this scene"""

        pass


    def get_toa_reflectance(self):
        """ wraps dnppy.landsat.toa_reflectance functions and applies them to this scene"""

        pass


    def get_ndvi(self):
        """ wraps dnppy.landsat.ndvi functions and applies them to this scene"""

        pass


    def get_atsat_bright_temp(self):
        """ wraps dnppy.atsat_bright_temp functions and applies them to this scene"""

        pass


        


if __name__ == "__main__":

    MTL_8 = r"C:\Users\Jeff\Desktop\Github\dnppy\dnppy_install\landsat\test_meta\LC80140342014347LGN00_MTL.txt"
    MTL_7 = r"C:\Users\Jeff\Desktop\Github\dnppy\dnppy_install\landsat\test_meta\LE70140342014323EDC00_MTL.txt"
    MTL_5 = r"C:\Users\Jeff\Desktop\Github\dnppy\dnppy_install\landsat\test_meta\LT50140342011307EDC00_MTL.txt"

    lsc = scene(MTL_8)
    for a in lsc: print a
    lsc = scene(MTL_7)
    for a in lsc: print a
    lsc = scene(MTL_5)
    for a in lsc: print a
