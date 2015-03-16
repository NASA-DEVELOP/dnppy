"""
======================================================================================
                                   dnppy.landsat
======================================================================================
 The "landsat.py" module is part of the "dnppy" package (develop national program py).
 This module houses python functions for performing image processing tasks on Landsat 4,
 5, 7, and 8 data.

 If you wrote a function you think should be added to this module, or have an idea for one
 you wish was available, please email the Geoinformatics YP class or code it up yourself
 for future DEVELOP participants to use!

"""

__author__ = ["Jeffry Ely, jeff.ely.08@gmail.com",
              "Daniel Jensen, danieljohnjensen@gmail.com"]


__all__=['Grab_Meta',               # complete for landsat 4,5,7,8
         
         'TOA_Reflectance_8',       # complete       
         'TOA_Reflectance_457',     # complete
             'TOA_Reflectance',     # complete
         
         'Surf_Reflectance_8',      # planned development
         'Surf_Reflectance_7',      # planned development
         'Surf_Reflectance_45',     # planned development
             'Surf_Reflectance',    # planned development

         'TOA_Radiance_8',          # complete
         'TOA_Radiance_457',        # complete
             'TOA_Radiance',        # complete

         'Cloud_Mask_8',            # complete
         'Cloud_Mask_7',            # planned development (to include slc-off band gaps)
         'Cloud_Mask_45',           # planned development
             'Cloud_Mask',          # planned development
         
         'AtSat_Bright_Temp_8',     # complete
         'AtSat_Bright_Temp_457',   # complete

         'NDVI_8',                  # complete
         'NDVI_457',                # complete

         'Surface_Temp_8',          # planned development
         'Surface_Temp_7',          # planned development
         'Surface_Temp_45',]        # planned development
     

# attempt to import all the common modules and settings
from dnppy import core
from textwrap import dedent

if core.check_module("numpy"): import numpy

# from scipy import stats
import os, sys, time, math, arcpy, shutil
         
if arcpy.CheckExtension('Spatial')=='Available':
    arcpy.CheckOutExtension('Spatial')
    from arcpy.sa import *
    from arcpy import env
    arcpy.env.overwriteOutput = True

#======================================================================================
def Grab_Meta(filename, Quiet = True):

    """
    Parses the xml format landsat metadata "MTL.txt" file

     This function parses the xml format metadata file associated with landsat images.
     it outputs a class instance metadata object with all the attributes found in the MTL
     file for quick referencing by other landsat related functions.

     Inputs:
       filename    the filepath to a landsat MTL file.

     Returns:
       meta        class object with all metadata attributes

     Authors: Spring2015: Jeffry Ely
    """

    # if the "filename" input is actually already a metadata class object, return it back.
    import inspect
    if inspect.isclass(filename): return (filename)

    fields = []
    values = []

    class Object(object):pass
    meta = Object()

    if filename:
        metafile = open(filename,'r')
        metadata = metafile.readlines()

    for line in metadata:
        # skips lines that contain "bad flags" denoting useless data AND lines
        # greater than 1000 characters. 1000 character limit works around an odd LC5
        # issue where the metadata has 40,000+ erroneous characters of whitespace
        bad_flags = ["END","GROUP"]                 
        if not any(x in line for x in bad_flags) and len(line)<=1000:   
                line = line.replace("  ","")
                line = line.replace("\n","")
                field_name , field_value = line.split(' = ')
                fields.append(field_name)
                values.append(field_value)

    for i in range(len(fields)):
        
        #format fields without quotes,dates, or times in them as floats
        if not any(['"' in values[i],'DATE' in fields[i],'TIME' in fields[i]]):   
            setattr(meta,fields[i],float(values[i]))
        else:
            values[i] = values[i].replace('"','')
            setattr(meta,fields[i],values[i])   
        
    # print "{0} : {1}".format(fields[i],values[i])

    # Add a FILEPATH attribute for local filepath of MTL file.
    meta.FILEPATH = filename

    # only landsat 8 includes sun-earth-distance in MTL file, so calculate it for the others.
    # this equation is tuned to match [http://landsathandbook.gsfc.nasa.gov/data_prod/prog_sect11_3.html]
    # with a maximum error of 0.055%
    if not meta.SPACECRAFT_ID == "LANDSAT_8":
        j_day = int(meta.LANDSAT_SCENE_ID[13:16])
        ecc   = 0.01671123
        theta = j_day * (2 * math.pi / 369.7)    #see above url for why this number isn't 365.25
        sm_ax = 1.000002610
        meta.EARTH_SUN_DISTANCE = sm_ax*(1-(ecc*ecc))/(1+ecc*(math.cos(theta)))
        print "{Grab_Meta} Calculated Earth to Sun distance as",str(meta.EARTH_SUN_DISTANCE),"AU"
        
    return(meta)



def TOA_Reflectance_8(band_nums, meta_path, outdir = False):

    """
    Converts Landsat 8 bands to Top of atmosphere reflectance.

     To be performed on raw Landsat 8 level 1 data. See link below for details
     see here [http://landsat.usgs.gov/Landsat8_Using_Product.php]

     Inputs:
       band_nums   A list of desired band numbers such as [3,4,5]
       meta_path   The full filepath to the metadata file for those bands
       outdir      Output directory to save converted files. If left False it will save ouput
                   files in the same directory as input files.

     Authors: Spring2015: Daniel Jensen, Jeffry Ely
    """

    band_nums = core.Enforce_List(band_nums)
    band_nums = map(str, band_nums)
    OLI_bands = ['1','2','3','4','5','6','7','8','9']
    meta = Grab_Meta(meta_path)

    for band_num in band_nums:
        if band_num in OLI_bands:
            band_path = meta_path.replace("MTL.txt","B{0}.tif".format(band_num))
            Qcal = arcpy.Raster(band_path)                        
            Mp   = getattr(meta,"REFLECTANCE_MULT_BAND_" + band_num) # multiplicative scaling factor
            Ap   = getattr(meta,"REFLECTANCE_ADD_BAND_" + band_num)  # additive rescaling factor
            SEA  = getattr(meta,"SUN_ELEVATION")*(math.pi/180)       # sun elevation angle theta_se

            TOA_ref = (((Qcal * Mp) + Ap)/(math.sin(SEA)))
            
            metaname = core.Create_Outname(outdir, meta_path, "TOA-Ref", "txt")
            shutil.copyfile(meta_path,metaname)
            
            outname = core.Create_Outname(outdir, band_path, "TOA-Ref", "tif")
            TOA_ref.save(outname)
            print "{TOA_Reflectance_8} Saved output at "  + outname
        else:
            print "{TOA_Reflectance_8} Can only perform reflectance conversion on OLI sensor bands!"
            print "{TOA_Reflectance_8} Skipping band " + band_num
    return



def TOA_Reflectance_457(band_nums, meta_path, outdir = False):

   """
   This function is used to convert Landsat 4,5, or 7 pixel values from
   digital numbers to Radiance, Reflectance, or Temperature (if using Band 6)

   Inputs:
      band_nums   A list of desired band numbers such as [3,4,5]
      meta_path   The full filepath to the metadata file for those bands
      outdir      Output directory to save converted files. If left False it will save ouput
                   files in the same directory as input files.

   Authors: Spring2015: Quinten Geddes, Daniel Jensen
   """
   
   OutList = []

   band_nums = core.Enforce_List(band_nums)
   band_nums = map(str, band_nums)
   TM_ETM_bands = ['1','2','3','4','5','7','8']

   #metadata format was changed August 29, 2012. This tool can process either the new or old format
   f = open(meta_path)
   MText = f.read()

   metadata = Grab_Meta(meta_path)
   oldMeta = []
   newMeta = []
    
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
      TileName = getattr(metadata, "LANDSAT_SCENE_ID")
      year = TileName[9:13]
      jday = TileName[13:16]
      date = getattr(metadata, "DATE_ACQUIRED")
   elif Meta == oldMeta:
      TileName = getattr(metadata, "BAND1_FILE_NAME")
      year = TileName[13:17]
      jday = TileName[17:20]
      date = getattr(metadata, "ACQUISITION_DATE")

   #the spacecraft from which the imagery was capture is identified
   #this info determines the solar exoatmospheric irradiance (ESun) for each band
   spacecraft = getattr(metadata, "SPACECRAFT_ID")
    
   if   "7" in spacecraft:
      ESun = (1969.0, 1840.0, 1551.0, 1044.0, 255.700, 0., 82.07, 1368.00)
   elif "5" in spacecraft:
      ESun = (1957.0, 1826.0, 1554.0, 1036.0, 215.0, 0. ,80.67)
   elif "4" in spacecraft:
      ESun = (1957.0, 1825.0, 1557.0, 1033.0, 214.9, 0. ,80.72)
   else:
      arcpy.AddError("This tool only works for Landsat 4, 5, or 7")
      raise arcpy.ExecuteError()

   #determing if year is leap year and setting the Days in year accordingly
   if float(year) % 4 == 0: DIY = 366.
   else:DIY=365.

   #using the date to determing the distance from the sun
   theta = 2 * math.pi * float(jday)/DIY

   dSun2 = (1.00011 + 0.034221 * math.cos(theta) + 0.001280 * math.sin(theta) +
           0.000719 * math.cos(2*theta)+ 0.000077 * math.sin(2 * theta))

   SZA = 90. - float(getattr(metadata, "SUN_ELEVATION"))
    
   #Calculating values for each band
   for band_num in band_nums:
      if band_num in TM_ETM_bands:

         print "Processing Band {0}".format(band_num)
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
         Refraster = (math.pi * Radraster * dSun2) / (ESun[int(band_num[0])-1] * math.cos(SZA*(math.pi/180)))
         BandPath = "{0}\\{1}_B{2}_TOA-Ref.tif".format(outdir,TileName,band_num)
    
         Refraster.save(BandPath)
         OutList.append(arcpy.Raster(BandPath))
    
         del Refraster,Radraster
    
         arcpy.AddMessage("Reflectance Calculated for Band {0}".format(band_num))
         print "Reflectance Calculated for Band {0}".format(band_num)
   f.close()
   return OutList



def AtSat_Bright_Temp_8(band_nums, meta_path, outdir = False):

    """
    Converts Landsat 8 TIRS bands to at satellite brightnes temperature in Kelvins

     To be performed on raw Landsat 8 level 1 data. See link below for details
     see here http://landsat.usgs.gov/Landsat8_Using_Product.php

     Inputs:
       band_nums   A list of desired band numbers, which should be [10,11]
       meta_path   The full filepath to the metadata file for those bands
       outdir      Output directory to save converted files. If left False it will save ouput
                   files in the same directory as input files.

     Authors: Spring2015: Daniel Jensen, Jeffry Ely
    """
    

    band_nums = core.Enforce_List(band_nums)
    band_nums = map(str, band_nums)
    meta = Grab_Meta(meta_path)
    
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
            
            metaname = core.Create_Outname(outdir, meta_path, "Bright-Temp")
            shutil.copyfile(meta_path,metaname)
        
            outname = core.Create_Outname(outdir, band_path, "Bright-Temp")
            Bright_Temp.save(outname)
            print "{AtSat_Bright_Temp_8} Saved output at " + outname
            del TOA_rad
        else:
            print "{AtSat_Bright_Temp_8} Can only perform brightness temperature on TIRS sensor bands!"
            print "{AtSat_Bright_Temp_8} Skipping band " + outname
    return



def AtSat_Bright_Temp_457(meta_path, outdir = False):
   """
    Converts band 6 from Landsat 4 and 5 or bands 6 VCID 1 and 2 from Landsat 7
    to at satellite brightnes temperature in Kelvins

     To be performed on raw Landsat 4, 5, or 7 level 1 data.

     Inputs:
       meta_path   The full filepath to the metadata file, labeled '_MTL.txt', which must
                   be in the same folder as band 6 or 6_VCID_1 and 6_VCID_2
       outdir      Output directory to save converted files. If left False it will save ouput
                   files in the same directory as input files.

     Authors: Spring2015: Daniel Jensen, Quinten Geddes
    """
    
   OutList = []
   metadata = Grab_Meta(meta_path)
   spacecraft = getattr(metadata, "SPACECRAFT_ID")

   if "4" in spacecraft or "5" in spacecraft:
      band_nums = ["6"]
   elif "7" in spacecraft:
      band_nums = ["6_VCID_1", "6_VCID_2"]
   else:
      print "Enter the MTL file corresponding to a Landsat 4, 5, or 7 dataset"

   #These lists will be used to parse the meta data text file and locate relevant information
   #metadata format was changed August 29, 2012. This tool can process either the new or old format

   f = open(meta_path)
   MText = f.read()

   metadata = Grab_Meta(meta_path)
   oldMeta = []
   newMeta = []
    
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
      TileName = getattr(metadata, "LANDSAT_SCENE_ID")
      year = TileName[9:13]
      jday = TileName[13:16]
      date = getattr(metadata, "DATE_ACQUIRED")
   elif Meta == oldMeta:
      TileName = getattr(metadata, "BAND1_FILE_NAME")
      year = TileName[13:17]
      jday = TileName[17:20]
      date = getattr(metadata, "ACQUISITION_DATE")

   #the spacecraft from which the imagery was capture is identified
   #this info determines the solar exoatmospheric irradiance (ESun) for each band
   
   #Calculating values for each band
   for band_num in band_nums:
      print "Processing Band {0}".format(band_num)
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
         Refraster = 1260.56/(arcpy.sa.Ln((607.76/Radraster) + 1.0))
         BandPath = "{0}\\{1}_B{2}_Temp.tif".format(outdir,TileName,band_num)
      if "7" in spacecraft:
         Refraster = 1282.71/(arcpy.sa.Ln((666.09/Radraster) + 1.0))
         BandPath = "{0}\\{1}_B{2}_Temp.tif".format(outdir,TileName,band_num)

      Refraster.save(BandPath)
      OutList.append(arcpy.Raster(BandPath))

      del Refraster,Radraster

      arcpy.AddMessage("Temperature Calculated for Band {0}".format(band_num))
      print "Temperature Calculated for Band {0}".format(band_num)
        
   f.close()
   return OutList



def TOA_Radiance_8(band_nums, meta_path, outdir = False):

    """
    Top of Atmosphere radiance (in Watts/(square meter * steradians * micrometers)) conversion for landsat 8 data

     To be performed on raw Landsat 8 level 1 data. See link below for details
     see here http://landsat.usgs.gov/Landsat8_Using_Product.php

     Inputs:
       band_nums   A list of desired band numbers such as [3 4 5]
       meta_path   The full filepath to the metadata file for those bands
       outdir      Output directory to save converted files.

     Authors: Spring2015: Daniel Jensen, Jeffry Ely
    """

    band_nums = core.Enforce_List(band_nums)
    band_nums = map(str, band_nums)
    meta = Grab_Meta(meta_path)
    
    for band_num in band_nums:
        
        band_path = meta_path.replace("MTL.txt","B{0}.tif".format(band_num))
        Qcal = arcpy.Raster(band_path)
        
        Ml   = getattr(meta,"RADIANCE_MULT_BAND_" + band_num) # multiplicative scaling factor
        Al   = getattr(meta,"RADIANCE_ADD_BAND_" + band_num)  # additive rescaling factor

        TOA_rad = (Qcal * Ml) + Al

        metaname = core.Create_Outname(outdir, meta_path, "TOA-Rad", "txt")
        shutil.copyfile(meta_path,metaname)
        
        outname = core.Create_Outname(outdir, band_path, "TOA-Rad", "tif")
        TOA_rad.save(outname)
        
        print "{TOA_Radiance_8} Saved output at " + outname

    return



def TOA_Radiance_457(band_nums, meta_path, outdir = False):

   """
    Top of Atmosphere radiance (in Watts/(square meter * steradians * micrometers)) conversion
    for Landsat 4, 5, and 7 data. To be performed on raw Landsat 4, 5, or 7 level 1 data. 

     Inputs:
       band_nums   A list of desired band numbers such as [3 4 5]
       meta_path   The full filepath to the metadata file for those bands
       outdir      Output directory to save converted files.

     Authors: Spring2015: Daniel Jensen, Quinten Geddes
   """
   
   OutList = []
   band_nums = core.Enforce_List(band_nums)
   band_nums = map(str, band_nums)
   TM_ETM_bands = ['1','2','3','4','5','7','8']

   #metadata format was changed August 29, 2012. This tool can process either the new or old format
   f = open(meta_path)
   MText = f.read()

   metadata = Grab_Meta(meta_path)
   oldMeta = []
   newMeta = []
    
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
      TileName = getattr(metadata, "LANDSAT_SCENE_ID")
      year = TileName[9:13]
      jday = TileName[13:16]
      date = getattr(metadata, "DATE_ACQUIRED")
   elif Meta == oldMeta:
      TileName = getattr(metadata, "BAND1_FILE_NAME")
      year = TileName[13:17]
      jday = TileName[17:20]
      date = getattr(metadata, "ACQUISITION_DATE")

   #the spacecraft from which the imagery was capture is identified
   #this info determines the solar exoatmospheric irradiance (ESun) for each band
   spacecraft = getattr(metadata, "SPACECRAFT_ID")
    
   if   "7" in spacecraft:
      ESun = (1969.0, 1840.0, 1551.0, 1044.0, 255.700, 0., 82.07, 1368.00)
   elif "5" in spacecraft:
      ESun = (1957.0, 1826.0, 1554.0, 1036.0, 215.0, 0. ,80.67)
   elif "4" in spacecraft:
      ESun = (1957.0, 1825.0, 1557.0, 1033.0, 214.9, 0. ,80.72)
   else:
      arcpy.AddError("This tool only works for Landsat 4, 5, or 7")
      raise arcpy.ExecuteError()
   
   #Calculating values for each band
   for band_num in band_nums:
      if band_num in TM_ETM_bands:

         print "Processing Band {0}".format(band_num)
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
         BandPath = "{0}\\{1}_B{2}_TOA-Rad.tif".format(outdir,TileName,band_num)
         Radraster.save(BandPath)
         OutList.append(arcpy.Raster(BandPath))
    
         del Radraster
    
         arcpy.AddMessage("Radiance Calculated for Band {0}".format(band_num))
         print "Radiance Calculated for Band {0}".format(band_num)
   f.close()
   return OutList



def Cloud_Mask_8(band_nums, BQA_path, outdir = False):
   """
   Removal of cloud-covered pixels in raw Landsat 8 bands using the BQA file included.

   To be performed on raw Landsat 8 level 1 data.

   Inputs:
      band_nums   A list of desired band numbers such as [3 4 5]
      BQA_path    The full filepath to the BQA file for the Landsat 8 dataset
      outdir      Output directory to save cloudless band tifs and the cloud mask

   Authors: Spring2015: Daniel Jensen
   """

   #enforce the input band numbers as a list of strings
   band_nums = core.Enforce_List(band_nums)
   band_nums = map(str, band_nums)

   #define the range of values in the BQA file to be reclassified as cloud (0) or not cloud (1)
   outReclass = Reclassify(BQA_path, "Value", RemapRange([[50000,65000,0],[28670,32000,0],[2,28669,1],[32001,49999,1],[1,1,"NoData"]]))

   #set the name and save the binary cloud mask tiff file
   Mask_name = BQA_path.replace("_BQA","")  
   CloudMask_path = core.Create_Outname(outdir, Mask_name, "Mask", "tif")   
   outReclass.save(CloudMask_path)

   #for each band listed in band_nums, apply the Con tool to erase cloud pixels and save each band as a new tiff
   for band_num in band_nums:      
      band_path = BQA_path.replace("BQA.tif","B{0}.tif".format(band_num))            
      outname = core.Create_Outname(outdir, band_path, "NoClds", "tif")
      outCon = Con(outReclass, band_path, "", "VALUE = 1")
      outCon.save(outname)                 

   return



def Cloud_Mask_457(band_nums, BQA_path, outdir = False):
   """
   Removal of cloud-covered pixels in raw Landsat 4, 5, and 7 bands.

   To be performed on raw Landsat 8 level 1 data.

   Inputs:
      band_nums   A list of desired band numbers such as [3 4 5]
      BQA_path    The full filepath to the BQA file for the Landsat 8 dataset
      outdir      Output directory to save cloudless band tifs and the cloud mask

   Authors: Spring2015: Daniel Jensen
   """



def NDVI_8(B5, B4, outdir = False):
   """
   This tool calculates a normalized difference vegetation index on Landsat 8 OLI data.

   To be performed on raw or processed Landsat 8 OLI data.

   Inputs:
      B5          The full filepath to the band 5 tiff file, the OLI NIR band
      B4          The full filepath to the band 4 tiff file, the OLI Visible Red band
      outdir      Output directory to save NDVI tifs

   Authors: Spring2015: Daniel Jensen
   """

   Red = Float(B4)
   NIR = Float(B5)
   
   L8_NDVI = (NIR - Red)/(NIR + Red)

   band_path = B4.replace("_B4","")        
   outname = core.Create_Outname(outdir, band_path, "NDVI", "tif")
   L8_NDVI.save(outname)
        
   print "{NDVI_8} Saved output at " + outname
        


def NDVI_457(B4, B3, outdir = False):
   """
   This tool calculates a normalized difference vegetation index on Landsat 4/5/7 TM/ETM+ data.

   To be performed on raw or processed Landsat 4/5/7/ TM/ETM+ data.

   Inputs:
      B4          The full filepath to the band 4 tiff file, the TM/ETM+ NIR band
      B3          The full filepath to the band 3 tiff file, the TM/ETM+ Visible Red band
      outdir      Output directory to save NDVI tifs

   Authors: Spring2015: Daniel Jensen
   """
   
   Red = Float(B3)
   NIR = Float(B4)
   
   L457_NDVI = (NIR - Red)/(NIR + Red)

   band_path = B3.replace("_B3","")        
   outname = core.Create_Outname(outdir, band_path, "NDVI", "tif")
   L457_NDVI.save(outname)
        
   print "{NDVI} Saved output at " + outname














