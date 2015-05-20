
#standard imports
import arcpy
from dnppy import core
from dnppy.landsat import grab_meta


__all__=['surface_temp_8',          # planned development
         'surface_temp_457']        # planned development


def surface_temp_8(band4_toa, band10, meta_path, outdir = False, L = 0.5, path_rad = 0.91, nbt = 0.866, sky_rad = 1.32):
    
    """
    Inputs:
        L = 0.1 for SAVI_idaho or L = 0.5 for common SAVI
    """

    meta = grab_meta(meta_path)

    band5_toa = band4_toa.replace("_B4_", "_B5_")
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

    band_num = "10"

    #Get Initial Thermal Radiances
    Ml = getattr(meta, "RADIANCE_MULT_BAND_" + band_num)
    Al = getattr(meta, "RADIANCE_ADD_BAND_" + band_num)

    null_10 = arcpy.sa.SetNull(band10, band10, "VALUE <= 1")
    null_11 = arcpy.sa.SetNull(band11, band11, "VALUE <= 1")

    itr_10 = (null_10 * Ml) + Al
    itr_11 = (null_11 * Ml) + Al

    #Corrected Thermal Radiances
    ctr_10 = ((itr_10 - path_rad)/nbt) - ((1 - nbe) * sky_rad)
    ctr_11 = ((itr_11 - path_rad)/nbt) - ((1 - nbe) * sky_rad)

    #Surface Temperature
    K1 = getattr(meta, "K1_CONSTANT_BAND_" + band_num)
    K2 = getattr(meta, "K2_CONSTANT_BAND_" + band_num)

    st_10 = (K2/(arcpy.sa.Ln(((nbe * K1)/ctr_10) + 1)))
    st_11 = (K2/(arcpy.sa.Ln(((nbe * K1)/ctr_10) + 1)))

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


def surface_temp_457(): pass
