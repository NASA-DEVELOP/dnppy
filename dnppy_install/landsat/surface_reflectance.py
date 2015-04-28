# local imports
from .atsat_bright_temp import *
from .cloud_mask import *
from .grab_meta import *
from .ndvi import *
from .scene import *
from .surface_temp import *
from .toa_radiance import *
from .toa_reflectance import *

from dnppy import core
arcpy.CheckOutExtension("Spatial")

__all__=['surf_reflectance_8',      # planned development
         'surf_reflectance_457']    # planned development

def surf_reflectance_8():pass

def surf_reflectance_457(band_nums, meta_path, outdir):

    """
    Converts Landsat 4, 5, and 7 band DNs to surface reflectance using dark object subtraction.

     To be performed on raw Landsat 4,5, and 7 level 1 data. See link below for details
     see here [http://landsat.usgs.gov/Landsat8_Using_Product.php]

     Inputs:
       band_nums   A list of desired band numbers such as [3,4,5]
       meta_path   The full filepath to the metadata file for those bands
       outdir      Output directory to save converted files. If left False it will save ouput
                   files in the same directory as input files.
    """
    band_nums = core.enf_list(band_nums)
    band_nums = map(str, band_nums)
    TM_ETM_bands = ['1','2','3','4','5','7','8']

    #landsat.toa_reflectance_457(band_nums, meta_path, outdir)

    OutList = []

    f = open(meta_path)
    MText = f.read()

    metadata = landsat.grab_meta(meta_path)
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

    dSun2 = (1.00011 + 0.034221 * math.cos(theta) + 0.001280 * math.sin(theta) + 0.000719 * math.cos(2*theta)+ 0.000077 * math.sin(2 * theta))

    SZA = 90. - float(getattr(metadata, "SUN_ELEVATION"))

    for band_num in band_nums:
        if band_num in TM_ETM_bands:
            pathname = meta_path.replace("MTL.txt", "B{0}.tif".format(band_num))
            Oraster = arcpy.Raster(pathname)

            null_raster = arcpy.sa.SetNull(Oraster, Oraster, "VALUE = 0")

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
    
            Radraster = (((LMax - LMin)/(QCalMax-QCalMin)) * (null_raster - QCalMin)) + LMin
            Oraster = 0
            del null_raster
    
            #Calculating temperature for band 6 if present
            Refraster = (math.pi * Radraster * dSun2) / (ESun[int(band_num[0]) - 1] * math.cos(SZA * (math.pi/180)))            

            #Oraster = arcpy.Raster(raster_null)
            dark_object = arcpy.GetRasterProperties_management(Refraster, "MINIMUM")
            do_str = str(dark_object)
            do_flt = float(do_str)

            #Calculate the minimum value in each band and perform dark object subtraction          
            Surfrefraster = Refraster - do_flt

            BandPath = "{0}\\{1}_B{2}_SurfRef.tif".format(outdir, TileName, band_num)
            Surfrefraster.save(BandPath)
            OutList.append(arcpy.Raster(BandPath))

            del Refraster, Radraster, Surfrefraster
    
            arcpy.AddMessage("Surface Reflectance Calculated for Band {0}".format(band_num))
            print("Surface Reflectance Calculated for Band {0}".format(band_num))

    f.close()
    return OutList

