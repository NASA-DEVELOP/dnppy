

__all__=['toa_radiance_8',          # complete
         'toa_radiance_457']        # complete


def toa_radiance_8(band_nums, meta_path, outdir = False):
    """
    Top of Atmosphere radiance (in Watts/(square meter * steradians * micrometers)) conversion for landsat 8 data

    To be performed on raw Landsat 8 level 1 data. See link below for details
    see here http://landsat.usgs.gov/Landsat8_Using_Product.php

    Inputs:
    band_nums   A list of desired band numbers such as [3 4 5]
    meta_path   The full filepath to the metadata file for those bands
    outdir      Output directory to save converted files.
    """

    band_nums = core.Enforce_List(band_nums)
    band_nums = map(str, band_nums)
    meta = grab_meta(meta_path)

    for band_num in band_nums:
        
        band_path   = meta_path.replace("MTL.txt","B{0}.tif".format(band_num))
        Qcal        = arcpy.Raster(band_path)

        Ml   = getattr(meta,"RADIANCE_MULT_BAND_" + band_num) # multiplicative scaling factor
        Al   = getattr(meta,"RADIANCE_ADD_BAND_" + band_num)  # additive rescaling factor

        TOA_rad = (Qcal * Ml) + Al

        metaname = core.create_outname(outdir, meta_path, "TOA-Rad", "txt")
        shutil.copyfile(meta_path,metaname)

        outname = core.create_outname(outdir, band_path, "TOA-Rad", "tif")
        TOA_rad.save(outname)

        print("Saved toa_radiance at {0}".format(outname))

    return



def toa_radiance_457(band_nums, meta_path, outdir = False):
    """
    Top of Atmosphere radiance (in Watts/(square meter * steradians * micrometers)) conversion
    for Landsat 4, 5, and 7 data. To be performed on raw Landsat 4, 5, or 7 level 1 data. 

     Inputs:
       band_nums   A list of desired band numbers such as [3 4 5]
       meta_path   The full filepath to the metadata file for those bands
       outdir      Output directory to save converted files.
    """

    OutList = []
    band_nums = core.Enforce_List(band_nums)
    band_nums = map(str, band_nums)
    TM_ETM_bands = ['1','2','3','4','5','7','8']

    #metadata format was changed August 29, 2012. This tool can process either the new or old format
    f = open(meta_path)
    MText = f.read()

    metadata = grab_meta(meta_path)
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
        TileName    = getattr(metadata, "LANDSAT_SCENE_ID")
        year        = TileName[9:13]
        jday        = TileName[13:16]
        date        = getattr(metadata, "DATE_ACQUIRED")
        
    elif Meta == oldMeta:
        TileName    = getattr(metadata, "BAND1_FILE_NAME")
        year        = TileName[13:17]
        jday        = TileName[17:20]
        date        = getattr(metadata, "ACQUISITION_DATE")

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
        BandPath = "{0}\\{1}_B{2}_TOA-Rad.tif".format(outdir,TileName,band_num)
        Radraster.save(BandPath)
        OutList.append(arcpy.Raster(BandPath))

        del Radraster

        arcpy.AddMessage("toa radiance saved for Band {0}".format(band_num))
        print("toa radiance saved for Band {0}".format(band_num))
         
    f.close()
    return OutList
