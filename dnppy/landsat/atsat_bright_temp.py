
#standard imports
import arcpy
import os
from dnppy import core
from grab_meta import grab_meta

if arcpy.CheckExtension('Spatial')=='Available':
    arcpy.CheckOutExtension('Spatial')
    arcpy.env.overwriteOutput = True

__all__=['atsat_bright_temp_8',     # complete
         'atsat_bright_temp_457']   # complete


def atsat_bright_temp_8(meta_path, outdir = False):
    """
    Converts Landsat 8 TIRS bands to at satellite brightnes temperature in Kelvins

    To be performed on raw Landsat 8 level 1 data. See link below for details
    see here http://landsat.usgs.gov/Landsat8_Using_Product.php

    :param band_nums:   A list of desired band numbers, which should be [10,11]
    :param meta_path:   The full filepath to the metadata file for those bands
    :param outdir:      Output directory to save converted files. If left False it will save ouput
                        files in the same directory as input files.

    :return output_filelist: A list of all files created by this function
    """
    
    #enforce the list of band numbers and grab metadata from the MTL file
    band_nums = ["10", "11"]
    meta_path = os.path.abspath(meta_path)
    meta = grab_meta(meta_path)

    output_filelist = []

    #cycle through each band in the list for calculation, ensuring each is in the list of TIRS bands
    for band_num in band_nums:

        #scrape data from the given file path and attributes in the MTL file
        band_path = meta_path.replace("MTL.txt","B{0}.tif".format(band_num))
        Qcal = arcpy.Raster(band_path)
        
        #get rid of the zero values that show as the black background to avoid skewing values
        null_raster = arcpy.sa.SetNull(Qcal, Qcal, "VALUE = 0")

        #requires first converting to radiance
        Ml   = getattr(meta,"RADIANCE_MULT_BAND_{0}".format(band_num)) # multiplicative scaling factor
        Al   = getattr(meta,"RADIANCE_ADD_BAND_{0}".format(band_num))  # additive rescaling factor

        TOA_rad = (null_raster * Ml) + Al
        
        #now convert to at-sattelite brightness temperature
        K1   = getattr(meta,"K1_CONSTANT_BAND_{0}".format(band_num))  # thermal conversion constant 1
        K2   = getattr(meta,"K2_CONSTANT_BAND_{0}".format(band_num))  # thermal conversion constant 2

        #calculate brightness temperature at the satellite
        Bright_Temp = K2/(arcpy.sa.Ln((K1/TOA_rad) + 1))

        #save the data to the automated name if outdir is given or in the parent folder if not
        if outdir:
            outdir = os.path.abspath(outdir)
            outname = core.create_outname(outdir, band_path, "ASBTemp", "tif")
        else:
            folder = os.path.split(meta_path)[0]
            outname = core.create_outname(folder, band_path, "ASBTemp", "tif")
            
        Bright_Temp.save(outname)
        output_filelist.append(outname)

        print("Saved output at {0}".format(outname))
        del TOA_rad, null_raster
            
    return output_filelist



def atsat_bright_temp_457(meta_path, outdir = None):
    """
    Converts band 6 from Landsat 4 and 5 or bands 6 VCID 1 and 2 from Landsat 7
    to at satellite brightness temperature in Kelvins

    To be performed on raw Landsat 4, 5, or 7 level 1 data.

    :param meta_path:   The full filepath to the metadata file, labeled '_MTL.txt', which must
                        be in the same folder as band 6 or 6_VCID_1 and 6_VCID_2
    :param outdir:      Output directory to save converted files. If left False it will save ouput
                        files in the same directory as input files.

    :return output_filelist: A list of all files created by this function
    """

    output_filelist = []
    meta_path = os.path.abspath(meta_path)
    metadata = grab_meta(meta_path)
    spacecraft = getattr(metadata, "SPACECRAFT_ID")

    if "4" in spacecraft or "5" in spacecraft:
        band_nums = ["6"]
    elif "7" in spacecraft:
        band_nums = ["6_VCID_1", "6_VCID_2"]
    else:
      print("Enter the MTL file corresponding to a Landsat 4, 5, or 7 dataset")

    # These lists will be used to parse the meta data text file and locate relevant information
    # metadata format was changed August 29, 2012. This tool can process either the new or old format
    f = open(meta_path)
    MText = f.read()

    # the presence of a PRODUCT_CREATION_TIME category is used to identify old metadata
    # if this is not present, the meta data is considered new.
    # Band6length refers to the length of the Band 6 name string. In the new metadata this string is longer
    if "PRODUCT_CREATION_TIME" in MText:
        Meta = "oldMeta"
    else:
        Meta = "newMeta"

    # The tile name is located using the newMeta/oldMeta indixes and the date of capture is recorded
    if Meta == "newMeta":
        TileName  = getattr(metadata, "LANDSAT_SCENE_ID")
        year      = TileName[9:13]
        jday      = TileName[13:16]
        date      = getattr(metadata, "DATE_ACQUIRED")

    elif Meta == "oldMeta":
        TileName  = getattr(metadata, "BAND1_FILE_NAME")
        year      = TileName[13:17]
        jday      = TileName[17:20]
        date      = getattr(metadata, "ACQUISITION_DATE")

    # the spacecraft from which the imagery was capture is identified
    # this info determines the solar exoatmospheric irradiance (ESun) for each band

    # Calculating values for each band
    for band_num in band_nums:
        print("Processing Band {0}".format(band_num))

        pathname = meta_path.replace("MTL.txt", "B{0}.tif".format(band_num))
        Oraster = arcpy.Raster(pathname)

        # get rid of the zero values that show as the black background to avoid skewing values
        null_raster = arcpy.sa.SetNull(Oraster, Oraster, "VALUE = 0")

        # using the oldMeta/newMeta indixes to pull the min/max for radiance/Digital numbers
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

        # Calculating temperature for band 6 if present
        if "4" in spacecraft or "5" in spacecraft:
            Refraster  = 1260.56/(arcpy.sa.Ln((607.76/Radraster) + 1.0))

        if "7" in spacecraft:
            Refraster  = 1282.71/(arcpy.sa.Ln((666.09/Radraster) + 1.0))

        band_temp = "{0}_B{1}".format(TileName, band_num)

        # save the data to the automated name if outdir is given or in the parent folder if not
        if outdir:
            outdir = os.path.abspath(outdir)
            BandPath = core.create_outname(outdir, band_temp, "ASBTemp", "tif")
        else:
            folder = os.path.split(meta_path)[0]
            BandPath = core.create_outname(folder, band_temp, "ASBTemp", "tif")

        Refraster.save(BandPath)
        output_filelist.append(BandPath)

        del Refraster, Radraster, null_raster

        print("Temperature Calculated for Band {0}".format(band_num))

    f.close()
    return output_filelist
