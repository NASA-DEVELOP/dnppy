
#standard imports
from dnppy import core
import arcpy


__all__=['ndvi_8',                  # complete
         'ndvi_457']                # complete


def ndvi_8(Band5, Band4, outdir = False):
    """
    calculates a normalized difference vegetation index on Landsat 8 OLI data.

    To be performed on raw or processed Landsat 8 OLI data, preferably TOA or Surface Reflectance.

    Inputs:
      Band5          The full filepath to the band 5 tiff file, the OLI NIR band
      Band4          The full filepath to the band 4 tiff file, the OLI Visible Red band
      outdir      Output directory to save NDVI tifs
    """

    #Set the input bands to float
    Red = arcpy.sa.Float(Band4)
    NIR = arcpy.sa.Float(Band5)

    #Calculate the NDVI
    L8_NDVI = (NIR - Red)/(NIR + Red)

    #Create the output name and save the NDVI tiff
    band_path   = Band4.replace("_B4","")

    if outdir:
        outname = core.create_outname(outdir, band_path, "NDVI", "tif")
    else:
        name = Band4.split("\\")[-1]
        folder = Band4.replace(name, "")
        outname = core.create_outname(folder, band_path, "NDVI", "tif")
    
    L8_NDVI.save(outname)
        
    print("saved ndvi_8 at {0}".format(outname))
    return

def ndvi_457(Band4, Band3, outdir = False):
    """
    calculates a normalized difference vegetation index on Landsat 4/5/7 TM/ETM+ data.

    To be performed on raw or processed Landsat 4/5/7/ TM/ETM+ data, preferably TOA or Surface Reflectance.

    Inputs:
      Band4          The full filepath to the band 4 tiff file, the TM/ETM+ NIR band
      Band3          The full filepath to the band 3 tiff file, the TM/ETM+ Visible Red band
      outdir      Output directory to save NDVI tifs
    """

    #Set the input bands to float
    Red = arcpy.sa.Float(Band3)
    NIR = arcpy.sa.Float(Band4)

    #Calculate the NDVI
    L457_NDVI = (NIR - Red)/(NIR + Red)

    #Create the output name and save the NDVI tiff
    band_path   = Band3.replace("_B3","")

    if outdir:
        outname = core.create_outname(outdir, band_path, "NDVI", "tif")
    else:
        name = Band4.split("\\")[-1]
        folder = Band4.replace(name, "")
        outname = core.create_outname(folder, band_path, "NDVI", "tif")
    
    L457_NDVI.save(outname)
        
    print("saved ndvi_457 at {0}".format(outname))
    return 
