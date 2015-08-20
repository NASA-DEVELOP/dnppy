
# standard imports
from grab_meta import grab_meta
from dnppy import core
import math
import os
import arcpy
if arcpy.CheckExtension('Spatial')=='Available':
    arcpy.CheckOutExtension('Spatial')
    arcpy.env.overwriteOutput = True

__all__=['toa_reflectance_8',       # complete       
         'toa_reflectance_457']     # complete


def toa_reflectance_8(band_nums, meta_path, outdir = None):
    """
    Converts Landsat 8 bands to Top-of-Atmosphere reflectance. To be performed
    on raw Landsat 8 level 1 data. See link below for details
    see here [http://landsat.usgs.gov/Landsat8_Using_Product.php]

    :param band_nums:   A list of desired band numbers such as [3,4,5]
    :param meta_path:   The full filepath to the metadata file for those bands
    :param outdir:      Output directory to save converted files. If left False it will save ouput
                        files in the same directory as input files.

    :return outlist:    list of files created by this function
    """

    outlist = []

    # enforce the list of band numbers and grab metadata from the MTL file
    band_nums = core.enf_list(band_nums)
    band_nums = map(str, band_nums)
    OLI_bands = ['1','2','3','4','5','6','7','8','9']
    meta_path = os.path.abspath(meta_path)
    meta = grab_meta(meta_path)

    # cycle through each band in the list for calculation, ensuring each is in the list of OLI bands
    for band_num in band_nums:
        if band_num in OLI_bands:

            # scrape data from the given file path and attributes in the MTL file
            band_path = meta_path.replace("MTL.txt","B{0}.tif".format(band_num))
            Qcal = arcpy.Raster(band_path)                        
            Mp   = getattr(meta,"REFLECTANCE_MULT_BAND_{0}".format(band_num)) # multiplicative scaling factor
            Ap   = getattr(meta,"REFLECTANCE_ADD_BAND_{0}".format(band_num))  # additive rescaling factor
            SEA  = getattr(meta,"SUN_ELEVATION")*(math.pi/180)       # sun elevation angle theta_se

            # get rid of the zero values that show as the black background to avoid skewing values
            null_raster = arcpy.sa.SetNull(Qcal, Qcal, "VALUE = 0")

            # calculate top-of-atmosphere reflectance
            TOA_ref = (((null_raster * Mp) + Ap)/(math.sin(SEA)))


            # save the data to the automated name if outdir is given or in the parent folder if not
            if outdir is not None:
                outdir = os.path.abspath(outdir)
                outname = core.create_outname(outdir, band_path, "TOA_Ref", "tif")
            else:
                folder = os.path.split(meta_path)[0]
                outname = core.create_outname(folder, band_path, "TOA_Ref", "tif")
                
            TOA_ref.save(outname)
            outlist.append(outname)
            print("Saved output at {0}".format(outname))

        # if listed band is not an OLI sensor band, skip it and print message
        else:
            print("Can only perform reflectance conversion on OLI sensor bands")
            print("Skipping band {0}".format(band_num))

    return outlist


def toa_reflectance_457(band_nums, meta_path, outdir = None):
    """
    This function is used to convert Landsat 4, 5, or 7 pixel values from
    digital numbers to Top-of-Atmosphere Reflectance. To be performed on raw
    Landsat 4, 5, or 7 data.

    :param band_nums:   A list of desired band numbers such as [3,4,5]
    :param meta_path:   The full filepath to the metadata file for those bands
    :param outdir:      Output directory to save converted files. If left False it will save ouput
                        files in the same directory as input files.

    :return outlist:    list of files created by this function
    """
   
    outlist = []

    band_nums = core.enf_list(band_nums)
    band_nums = map(str, band_nums)

    # metadata format was changed August 29, 2012. This tool can process either the new or old format
    f = open(meta_path)
    MText = f.read()

    meta_path = os.path.abspath(meta_path)
    metadata = grab_meta(meta_path)
    
    # the presence of a PRODUCT_CREATION_TIME category is used to identify old metadata
    # if this is not present, the meta data is considered new.
    # Band6length refers to the length of the Band 6 name string. In the new metadata this string is longer
    if "PRODUCT_CREATION_TIME" in MText:
        Meta = "oldMeta"
        Band6length = 2
    else:
        Meta = "newMeta"
        Band6length = 8

    # The tilename is located using the newMeta/oldMeta indixes and the date of capture is recorded
    if Meta == "newMeta":
        TileName = getattr(metadata, "LANDSAT_SCENE_ID")
        year = TileName[9:13]
        jday = TileName[13:16]
        date = getattr(metadata, "DATE_ACQUIRED")
    elif Meta == "oldMeta":
        TileName = getattr(metadata, "BAND1_FILE_NAME")
        year = TileName[13:17]
        jday = TileName[17:20]
        date = getattr(metadata, "ACQUISITION_DATE")

    # the spacecraft from which the imagery was capture is identified
    # this info determines the solar exoatmospheric irradiance (ESun) for each band
    spacecraft = getattr(metadata, "SPACECRAFT_ID")
    
    if "7" in spacecraft:
        ESun = (1969.0, 1840.0, 1551.0, 1044.0, 255.700, 0., 82.07, 1368.00)
        TM_ETM_bands = ['1','2','3','4','5','7','8']
    elif "5" in spacecraft:
         ESun = (1957.0, 1826.0, 1554.0, 1036.0, 215.0, 0. ,80.67)
         TM_ETM_bands = ['1','2','3','4','5','7']
    elif "4" in spacecraft:
        ESun = (1957.0, 1825.0, 1557.0, 1033.0, 214.9, 0. ,80.72)
        TM_ETM_bands = ['1','2','3','4','5','7']
    else:
        arcpy.AddError("This tool only works for Landsat 4, 5, or 7")
        raise arcpy.ExecuteError()

    # determing if year is leap year and setting the Days in year accordingly
    if float(year) % 4 == 0: DIY = 366.
    else: DIY=365.

    # using the date to determining the distance from the sun
    theta = 2 * math.pi * float(jday)/DIY

    dSun2 = (1.00011 + 0.034221 * math.cos(theta) + 0.001280 * math.sin(theta) +
           0.000719 * math.cos(2*theta)+ 0.000077 * math.sin(2 * theta))

    SZA = 90. - float(getattr(metadata, "SUN_ELEVATION"))
    
    # Calculating values for each band
    for band_num in band_nums:
        if band_num in TM_ETM_bands:

            print("Processing Band {0}".format(band_num))
            pathname = meta_path.replace("MTL.txt", "B{0}.tif".format(band_num))
            Oraster = arcpy.Raster(pathname)
         
            null_raster = arcpy.sa.SetNull(Oraster, Oraster, "VALUE = 0")

            # using the oldMeta/newMeta indices to pull the min/max for radiance/Digital numbers
            if Meta == "newMeta":
                LMax    = getattr(metadata, "RADIANCE_MAXIMUM_BAND_{0}".format(band_num))
                LMin    = getattr(metadata, "RADIANCE_MINIMUM_BAND_{0}".format(band_num))  
                QCalMax = getattr(metadata, "QUANTIZE_CAL_MAX_BAND_{0}".format(band_num))
                QCalMin = getattr(metadata, "QUANTIZE_CAL_MIN_BAND_{0}".format(band_num))
            elif Meta == "oldMeta":
                LMax    = getattr(metadata, "LMAX_BAND{0}".format(band_num))
                LMin    = getattr(metadata, "LMIN_BAND{0}".format(band_num))  
                QCalMax = getattr(metadata, "QCALMAX_BAND{0}".format(band_num))
                QCalMin = getattr(metadata, "QCALMIN_BAND{0}".format(band_num))
    
            Radraster = (((LMax - LMin)/(QCalMax-QCalMin)) * (null_raster - QCalMin)) + LMin
            Oraster = 0
            del null_raster
    
            # Calculating temperature for band 6 if present
            Refraster = (math.pi * Radraster * dSun2) / (ESun[int(band_num[0])-1] * math.cos(SZA*(math.pi/180)))

            # construc output names for each band based on whether outdir is set (default is False)
            if outdir is not None:
                outdir = os.path.abspath(outdir)
                BandPath = core.create_outname(outdir, pathname, "TOA_Ref", "tif")
            else:
                folder = os.path.split(meta_path)[0]
                BandPath = core.create_outname(folder, pathname, "TOA_Ref", "tif")

            Refraster.save(BandPath)
            outlist.append(BandPath)

            del Refraster, Radraster
            print("Reflectance Calculated for Band {0}".format(band_num))

        # if listed band is not a TM/ETM+ sensor band, skip it and print message
        else:
            print("Can only perform reflectance conversion on TM/ETM+ sensor bands")
            print("Skipping band {0}".format(band_num))
         
    f.close()
    return outlist
