# local imports
from .cloud_mask import *
from .grab_meta import *
from .ndvi import *
from .scene import *
from .surface_reflectance import *
from .surface_temp import *
from .toa_radiance import *
from .toa_reflectance import *

from dnppy import core

__all__=['atsat_bright_temp_8',     # complete
         'atsat_bright_temp_457']   # complete


def atsat_bright_temp_8(band_nums, meta_path, outdir = False):

    """
    Converts Landsat 8 TIRS bands to at satellite brightnes temperature in Kelvins

     To be performed on raw Landsat 8 level 1 data. See link below for details
     see here http://landsat.usgs.gov/Landsat8_Using_Product.php

     Inputs:
       band_nums   A list of desired band numbers, which should be [10,11]
       meta_path   The full filepath to the metadata file for those bands
       outdir      Output directory to save converted files. If left False it will save ouput
                   files in the same directory as input files.
    """
    

    band_nums = core.enf_list(band_nums)
    band_nums = map(str, band_nums)
    meta = grab_meta(meta_path)
    
    for band_num in band_nums:
        if band_num in ["10","11"]:
            band_path = meta_path.replace("MTL.txt","B{0}.tif".format(band_num))
            Qcal = arcpy.Raster(band_path)

            # requires first converting to radiance
            Ml   = getattr(meta,"RADIANCE_MULT_BAND_" + band_num) # multiplicative scaling factor
            Al   = getattr(meta,"RADIANCE_ADD_BAND_" + band_num)  # additive rescaling factor

            TOA_rad = (Qcal * Ml) + Al
            
            # now convert to at-sattelite brightness temperature
            K1   = getattr(meta,"K1_CONSTANT_BAND_"+ band_num)  # thermal conversion constant 1
            K2   = getattr(meta,"K2_CONSTANT_BAND_"+ band_num)  # thermal conversion constant 2

            Bright_Temp = K2/(arcpy.sa.Ln((K1/TOA_rad) + 1))
            
            metaname = core.create_outname(outdir, meta_path, "Bright-Temp")
            shutil.copyfile(meta_path,metaname)
        
            outname = core.create_outname(outdir, band_path, "Bright-Temp")
            Bright_Temp.save(outname)
            print("Saved output at {0}".format(outname))
            del TOA_rad
            
        else:
            print("Can only perform brightness temperature on TIRS sensor bands!")
            print("Skipping band  {0}".format(outname))
    return



def atsat_bright_temp_457(meta_path, outdir = False):
   """
    Converts band 6 from Landsat 4 and 5 or bands 6 VCID 1 and 2 from Landsat 7
    to at satellite brightnes temperature in Kelvins

     To be performed on raw Landsat 4, 5, or 7 level 1 data.

     Inputs:
       meta_path   The full filepath to the metadata file, labeled '_MTL.txt', which must
                   be in the same folder as band 6 or 6_VCID_1 and 6_VCID_2
       outdir      Output directory to save converted files. If left False it will save ouput
                   files in the same directory as input files.
    """
    
   OutList      = []
   metadata     = grab_meta(meta_path)
   spacecraft   = getattr(metadata, "SPACECRAFT_ID")

   if "4" in spacecraft or "5" in spacecraft:
      band_nums = ["6"]
   elif "7" in spacecraft:
      band_nums = ["6_VCID_1", "6_VCID_2"]
   else:
      print("Enter the MTL file corresponding to a Landsat 4, 5, or 7 dataset")

   #These lists will be used to parse the meta data text file and locate relevant information
   #metadata format was changed August 29, 2012. This tool can process either the new or old format

   f = open(meta_path)
   MText = f.read()

   metadata = grab_meta(meta_path)
   oldMeta  = []
   newMeta  = []
    
   #the presence of a PRODUCT_CREATION_TIME category is used to identify old metadata
   #if this is not present, the meta data is considered new.
   #Band6length refers to the length of the Band 6 name string. In the new metadata this string is longer
   if "PRODUCT_CREATION_TIME" in MText:
      Meta = oldMeta
      Band6length = 2
   else:
      Meta = newMeta
      Band6length = 8

   #The tilename is located using the newMeta/oldMeta indixes and the date of capture is recorded
   if Meta == newMeta:
      TileName  = getattr(metadata, "LANDSAT_SCENE_ID")
      year      = TileName[9:13]
      jday      = TileName[13:16]
      date      = getattr(metadata, "DATE_ACQUIRED")
      
   elif Meta == oldMeta:
      TileName  = getattr(metadata, "BAND1_FILE_NAME")
      year      = TileName[13:17]
      jday      = TileName[17:20]
      date      = getattr(metadata, "ACQUISITION_DATE")

   #the spacecraft from which the imagery was capture is identified
   #this info determines the solar exoatmospheric irradiance (ESun) for each band
   
   #Calculating values for each band
   for band_num in band_nums:
      print("Processing Band {0}".format(band_num))
      pathname = meta_path.replace("MTL.txt", "B{0}.tif".format(band_num))
      Oraster = arcpy.Raster(pathname)

      #using the oldMeta/newMeta indixes to pull the min/max for radiance/Digital numbers
      if Meta == newMeta:
         LMax    = getattr(metadata, "RADIANCE_MAXIMUM_BAND_" + band_num)
         LMin    = getattr(metadata, "RADIANCE_MINIMUM_BAND_" + band_num)  
         QCalMax = getattr(metadata, "QUANTIZE_CAL_MAX_BAND_" + band_num)
         QCalMin = getattr(metadata, "QUANTIZE_CAL_MIN_BAND_" + band_num)
         
      elif Meta == oldMeta:
         LMax    = getattr(metadata, "LMAX_BAND" + band_num)
         LMin    = getattr(metadata, "LMIN_BAND" + band_num)  
         QCalMax = getattr(metadata, "QCALMAX_BAND" + band_num)
         QCalMin = getattr(metadata, "QCALMIN_BAND" + band_num)

      Radraster = (((LMax - LMin)/(QCalMax-QCalMin)) * (Oraster - QCalMin)) + LMin
      Oraster = 0

      #Calculating temperature for band 6 if present
      if "4" in spacecraft or "5" in spacecraft:
         Refraster  = 1260.56/(arcpy.sa.Ln((607.76/Radraster) + 1.0))
         BandPath   = "{0}\\{1}_B{2}_Temp.tif".format(outdir,TileName,band_num)
         
      if "7" in spacecraft:
         Refraster  = 1282.71/(arcpy.sa.Ln((666.09/Radraster) + 1.0))
         BandPath   = "{0}\\{1}_B{2}_Temp.tif".format(outdir,TileName,band_num)

      Refraster.save(BandPath)
      OutList.append(arcpy.Raster(BandPath))

      del Refraster,Radraster

      arcpy.AddMessage("Temperature Calculated for Band {0}".format(band_num))
      print("Temperature Calculated for Band {0}".format(band_num))
        
   f.close()
   return OutList
