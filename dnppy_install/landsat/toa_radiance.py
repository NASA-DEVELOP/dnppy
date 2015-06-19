
#standard imports
from dnppy.landsat import grab_meta
from dnppy import core
import arcpy
if arcpy.CheckExtension('Spatial')=='Available':
    arcpy.CheckOutExtension('Spatial')
    arcpy.env.overwriteOutput = True

__all__=['toa_radiance_8',          # complete
         'toa_radiance_457']        # complete


def toa_radiance_8(band_nums, meta_path, outdir = False):
    """
    Top of Atmosphere radiance (in Watts/(square meter * steradians * micrometers)) conversion for landsat 8 data

    To be performed on raw Landsat 8 level 1 data. See link below for details
    see here http://landsat.usgs.gov/Landsat8_Using_Product.php

    Inputs:
    band_nums   A list of desired band numbers such as [3, 4, 5]
    meta_path   The full filepath to the metadata file for those bands
    outdir      Output directory to save converted files.
    """

    outlist = []

    #enforce list of band numbers and grab the metadata from the MTL file
    band_nums = core.enf_list(band_nums)
    band_nums = map(str, band_nums)
    meta = grab_meta(meta_path)
    
    OLI_bands = ['1','2','3','4','5','6','7','8','9']
    
    #loop through each band
    for band_num in band_nums:
        if band_num in OLI_bands:

            #create the band name
            band_path   = meta_path.replace("MTL.txt","B{0}.tif".format(band_num))
            Qcal        = arcpy.Raster(band_path)

            null_raster = arcpy.sa.SetNull(Qcal, Qcal, "VALUE = 0")

            #scrape the attribute data
            Ml   = getattr(meta,"RADIANCE_MULT_BAND_{0}".format(band_num)) # multiplicative scaling factor
            Al   = getattr(meta,"RADIANCE_ADD_BAND_{0}".format(band_num))  # additive rescaling factor

            #calculate Top-of-Atmosphere radiance
            TOA_rad = (null_raster * Ml) + Al
            del null_raster
            
            #create the output name and save the TOA radiance tiff
            if "\\" in meta_path:
                name = meta_path.split("\\")[-1]
            elif "//" in meta_path:
                name = meta_path.split("//")[-1]
                
            rad_name = name.replace("_MTL.txt", "_B{0}".format(band_num))

            if outdir:
                outname = core.create_outname(outdir, rad_name, "TOA_Rad", "tif")
            else:
                if "\\" in meta_path:
                    name = meta_path.split("\\")[-1]
                elif "//" in meta_path:
                    name = meta_path.split("//")[-1]
                folder = meta_path.replace(name, "")
                outname = core.create_outname(folder, rad_name, "TOA_Rad", "tif")
                
            TOA_rad.save(outname)
            outlist.append(outname)
            print("Saved toa_radiance at {0}".format(outname))

        #if listed band is not a OLI sensor band, skip it and print message
        else:
            print("Can only perform reflectance conversion on OLI sensor bands")
            print("Skipping band {0}".format(band_num))

    return outlist



def toa_radiance_457(band_nums, meta_path, outdir = False):
    """
    Top of Atmosphere radiance (in Watts/(square meter * steradians * micrometers)) conversion
    for Landsat 4, 5, and 7 data. To be performed on raw Landsat 4, 5, or 7 level 1 data. 

     Inputs:
       band_nums   A list of desired band numbers such as [3, 4, 5]
       meta_path   The full filepath to the metadata file for those bands
       outdir      Output directory to save converted files.
    """

    outlist = []
    band_nums = core.enf_list(band_nums)
    band_nums = map(str, band_nums)

    #metadata format was changed August 29, 2012. This tool can process either the new or old format
    f = open(meta_path)
    MText = f.read()

    metadata = grab_meta(meta_path)

    #the presence of a PRODUCT_CREATION_TIME category is used to identify old metadata
    #if this is not present, the meta data is considered new.
    #Band6length refers to the length of the Band 6 name string. In the new metadata this string is longer
    if "PRODUCT_CREATION_TIME" in MText:
        Meta = "oldMeta"
        Band6length = 2
    else:
        Meta = "newMeta"
        Band6length = 8

    #The tilename is located using the newMeta/oldMeta indixes and the date of capture is recorded
    if Meta == "newMeta":
        TileName    = getattr(metadata, "LANDSAT_SCENE_ID")
        year        = TileName[9:13]
        jday        = TileName[13:16]
        date        = getattr(metadata, "DATE_ACQUIRED")
        
    elif Meta == "oldMeta":
        TileName    = getattr(metadata, "BAND1_FILE_NAME")
        year        = TileName[13:17]
        jday        = TileName[17:20]
        date        = getattr(metadata, "ACQUISITION_DATE")

    #the spacecraft from which the imagery was capture is identified
    #this info determines the solar exoatmospheric irradiance (ESun) for each band
    spacecraft = getattr(metadata, "SPACECRAFT_ID")

    if   "7" in spacecraft:
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

    #Calculating values for each band
    for band_num in band_nums:
        if band_num in TM_ETM_bands:

            print("Processing Band {0}".format(band_num))
            pathname = meta_path.replace("MTL.txt", "B{0}.tif".format(band_num))
            Oraster = arcpy.Raster(pathname)

            null_raster = arcpy.sa.SetNull(Oraster, Oraster, "VALUE = 0")

            #using the oldMeta/newMeta indixes to pull the min/max for radiance/Digital numbers
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

            band_rad = "{0}_B{1}".format(TileName, band_num)

            #create the output name and save the TOA radiance tiff
            if outdir:
                outname = core.create_outname(outdir, band_rad, "TOA_Rad", "tif")
            else:
                if "\\" in meta_path:
                    name = meta_path.split("\\")[-1]
                elif "//" in meta_path:
                    name = meta_path.split("//")[-1]
                folder = meta_path.replace(name, "")
                outname = core.create_outname(folder, band_rad, "TOA_Rad", "tif")
                
            Radraster.save(outname)
            outlist.append(outname)
            
            del Radraster

            print("toa radiance saved for Band {0}".format(band_num))

        #if listed band is not a TM/ETM+ sensor band, skip it and print message
        else:
            print("Can only perform reflectance conversion on TM/ETM+ sensor bands")
            print("Skipping band {0}".format(band_num))
         
    f.close()
    return outlist
