

__author__ = ["Jeffry Ely, jeff.ely.08@gmail.com"]

class scene:
    """
    Defines a landsat scene object. Used to track band filepaths
    and pass raster objects to functions
    """

    def __init__(self, MTL_path):
        """ builds the scene"""
        
        self.meta       = landsat.grab_meta(MTL_path)
        self.mtl_dir    = os.path.dirname(MTL_path)
        return
    

    def __getitem__(self, index):
        """ returns arcpy.raster objects from getitem indices """

        rast_obj = arcpy.Raster(getattr(self, "band_{0}".format(i)))
        return rast_obj

    
    def find_raw_bands(self):
        """ builds filepaths for band filenames from MTL file """

        for i in range(1,11):
            filename = getattr(self.meta, "FILE_NAME_BAND_{0}".format(i))
            filepath = os.path.join(self.mtl_dir, filename)
            
            setattr(self, "band_{0}".format(i), filepath)

        QA_name      = self.meta.FILE_NAME_BAND_QUALITY
        self.band_QA = os.path.join(self.mtl_dir, QA_name)

        return


if __name__ == "__main__":

    MTL_8 = r"C:\dnppy_dev\0_Raw\Landsat 8\LC80140342014347LGN00\LC80140342014347LGN00_MTL.txt"
    MTL_7 = r"C:\dnppy_dev\0_Raw\Landsat 7\LE70140342014323EDC00\LE70140342014323EDC00_MTL.txt"
    MTL_5 = r"C:\dnppy_dev\0_Raw\Landsat 5\LT50140342011307EDC00\LT50140342011307EDC00_MTL.txt"


    lsc = scene(MTL_8)
