
#standard imports
import arcpy
from dnppy import core
from dnppy.landsat import grab_meta


__all__=['surface_temp_8',          # complete
         'surface_temp_457']        # complete


def surface_temp_8(band4_toa, meta_path, path_rad, nbt, sky_rad, outdir = False, L = 0.5):
    
    """
    Calculates surface temperature from Landsat 8 OLI and TIRS data.

    Requires band 4 and 5 Top-of-Atmosphere Reflectance tiffs and the unprocessed band 10 and 11 tiffs.

    Inputs:
        band4_toa       Filepath to the Band 4 Top-of-Atmosphere Reflectance tiff
                        *use landsat.toa_reflectance_8
        meta_path       Filepath to the metadata file (ending in _MTL.txt)
        path_rad        Path Radiance constant
                        *default 0
        nbt             Narrowband Transmissivity constant
                        *default 1
        sky_rad         Sky Radiance constant
                        *default 0
        outdir          Path to the desired output folder
                        *if left False the output tiff will be place in band4_toa's folder
        L               Soil brightness correction factor, between 0 and 1
                        *used to calculate Soil Adjusted Vegetation Index
                        *default L = 0.5 works well in most situations
                        *when L = 0, SAVI = NDVI
    """

    #Grab metadata from the MTL file and set the pathnames for Band 5 TOA Reflectance and the raw Band 11 tiffs
    meta = grab_meta(meta_path)

    band5_toa = band4_toa.replace("_B4_", "_B5_")
    band10 = meta_path.replace("_MTL.txt", "_B10.tif")
    band11 = band10.replace("_B10.tif", "_B11.tif")

    #Soil Adjusted Vegetation Index
    red = arcpy.sa.Float(band4_toa)
    nir = arcpy.sa.Float(band5_toa)
    
    savi = ((1 + L) * (nir - red))/(L + (nir - red))

    #Leaf Area Index
    #assigns LAI for 0.1 <= SAVI <= 0.687
    lai_1 = ((arcpy.sa.Ln((0.69 - savi)/0.59))/(-0.91))
    #assigns LAI for SAVI >= 0.687
    lai_2 = arcpy.sa.Con(savi, lai_1, 6, "VALUE < 0.687")
    #assigns LAI for SAVI <= 0.1
    lai = arcpy.sa.Con(savi, lai_2, 0, "VALUE >= 0.1")

    #Narrow Band Emissivity
    remap = 0.97 + (0.0033 * lai)
    nbe = arcpy.sa.Con(lai, remap, 0.98, "VALUE <= 3")

    #Get the radiance mult/add bands for bands 10 and 11
    Ml_10 = getattr(meta, "RADIANCE_MULT_BAND_10")
    Al_10 = getattr(meta, "RADIANCE_ADD_BAND_10")
    Ml_11 = getattr(meta, "RADIANCE_MULT_BAND_11")
    Al_11 = getattr(meta, "RADIANCE_ADD_BAND_11")
    
    #Set values in the TIRS band tiffs to null
    null_10 = arcpy.sa.SetNull(band10, band10, "VALUE <= 1")
    null_11 = arcpy.sa.SetNull(band11, band11, "VALUE <= 1")

    #Initial Thermal Radiances
    itr_10 = (null_10 * Ml_10) + Al_10
    itr_11 = (null_11 * Ml_11) + Al_11

    #Corrected Thermal Radiances
    ctr_10 = ((itr_10 - path_rad)/nbt) - ((1 - nbe) * sky_rad)
    ctr_11 = ((itr_11 - path_rad)/nbt) - ((1 - nbe) * sky_rad)

    #Get the K1 and K2 constants for bands 10 and 11
    K1_10 = getattr(meta, "K1_CONSTANT_BAND_10")
    K2_10 = getattr(meta, "K2_CONSTANT_BAND_10")
    K1_11 = getattr(meta, "K1_CONSTANT_BAND_11")
    K2_11 = getattr(meta, "K2_CONSTANT_BAND_11")

    #Calculate surface temperature based on bands 10 and 11 and average them for final output
    st_10 = (K2_10/(arcpy.sa.Ln(((nbe * K1_10)/ctr_10) + 1)))
    st_11 = (K2_11/(arcpy.sa.Ln(((nbe * K1_11)/ctr_10) + 1)))

    st = (st_10 + st_11)/2

    #Create output name and save the Surface Temperature tiff
    tilename = getattr(meta, "LANDSAT_SCENE_ID")
    
    if outdir:
        outname = core.create_outname(outdir, tilename, "Surf_Temp", "tif")
    else:
        if "\\" in band4_toa:
            name = band4_toa.split("\\")[-1]
            folder = band4_toa.replace(name, "")
        elif "//" in band4_toa:
            name = band4_toa.split("//")[-1]
            folder = band4_toa.replace(name, "")
        outname = core.create_outname(folder, tilename, "Surf_Temp", "tif")
        
    st.save(outname)

    return


def surface_temp_457(band3_toa, meta_path, path_rad, nbt, sky_rad, outdir = False, L = 0.5):
    """
    Calculates surface temperature from Landsat 4/5 TM or 7 ETM+ data.

    Requires band 3 and 4 Top-of-Atmosphere Reflectance tiffs and the unprocessed band 6 (or 6_VCID_1 for Landsat 7) tiff.

    Inputs:
        band3_toa       Filepath to the Band 3 Top-of-Atmosphere Reflectance tiff
                        *use landsat.toa_reflectance_457
        meta_path       Filepath to the metadata file (ending in _MTL.txt)
        path_rad        Path Radiance constant
                        *default 0
        nbt             Narrowband Transmissivity constant
                        *default 1
        sky_rad         Sky Radiance constant
                        *default 0
        outdir          Path to the desired output folder
                        *if left False the output tiff will be place in band4_toa's folder
        L               Soil brightness correction factor, between 0 and 1
                        *used to calculate Soil Adjusted Vegetation Index
                        *default L = 0.5 works well in most situations
                        *when L = 0, SAVI = NDVI
    """

    #Set the pathname for band 4
    band4_toa = band3_toa.replace("_B3_", "_B4_")

    #Grab metadata from the MTL file and identify the spacecraft ID
    meta = grab_meta(meta_path)
    spacecraft = getattr(meta, "SPACECRAFT_ID")

    #Set the band 6 number, K1 and K2 thermal constants, and band 6 pathname based on spacecraft ID
    if "4" in spacecraft or "5" in spacecraft:
        band_num = "6"
        K1 = 607.76
        K2 = 1260.56
        band6 = meta_path.replace("_MTL.txt", "_B6.tif")
    elif "7" in spacecraft:
        if "VCID_1" in band6:
            band_num = "6_VCID_1"
        elif "VCID_2" in band6:
            band_num = "6_VCID_2"
        K1 = 666.09
        K2 = 1282.71
        band6 = meta_path.replace("_MTL.txt", "_B6_VCID_1.tif")
    else:
        print("Enter the MTL file corresponding to a Landsat 4, 5, or 7 dataset")

    #Open the metadata text file and read to set the scene's tilename
    f = open(meta_path)
    MText = f.read()

    if "PRODUCT_CREATION_TIME" in MText:
        tilename = getattr(meta, "BAND1_FILE_NAME")
    else:
        tilename = getattr(meta, "LANDSAT_SCENE_ID")

    #Soil Adjusted Vegetation Index
    red = arcpy.sa.Float(band3_toa)
    nir = arcpy.sa.Float(band4_toa)
    
    savi = ((1 + L) * (nir - red))/(L + (nir - red))

    #Leaf Area Index
    #assigns LAI for 0.1 <= SAVI <= 0.687
    lai_1 = ((arcpy.sa.Ln((0.69 - savi)/0.59))/(-0.91))
    #assigns LAI for SAVI >= 0.687
    lai_2 = arcpy.sa.Con(savi, lai_1, 6, "VALUE < 0.687")
    #assigns LAI for SAVI <= 0.1
    lai = arcpy.sa.Con(savi, lai_2, 0, "VALUE >= 0.1")

    #Narrow Band Emissivity
    remap = 0.97 + (0.0033 * lai)
    nbe = arcpy.sa.Con(lai, remap, 0.98, "VALUE <= 3")

    #Get the radiance mult/add bands for bands 10 and 11
    Ml = getattr(meta, "RADIANCE_MULT_BAND_{0}".format(band_num))
    Al = getattr(meta, "RADIANCE_ADD_BAND_{0}".format(band_num))
 
    #Set values in the TIRS band tiffs to null
    null = arcpy.sa.SetNull(band6, band6, "VALUE <= 1")

    #Initial Thermal Radiances
    itr = (null * Ml) + Al

    #Corrected Thermal Radiances
    ctr = ((itr - path_rad)/nbt) - ((1 - nbe) * sky_rad)

    #Calculate surface temperature
    st = (K2/(arcpy.sa.Ln(((nbe * K1)/ctr) + 1)))

    #Create output name and save the surface temperature tiff   
    if outdir:
        outname = core.create_outname(outdir, tilename, "Surf_Temp", "tif")
    else:
        if "\\" in band3_toa:
            name = band3_toa.split("\\")[-1]
            folder = band4_toa.replace(name, "")
        elif "//" in band4_toa:
            name = band3_toa.split("//")[-1]
            folder = band3_toa.replace(name, "")
        outname = core.create_outname(folder, tilename, "Surf_Temp", "tif")
        
    st.save(outname)

    return
