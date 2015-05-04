
#standard imports
from .atsat_bright_temp import atsat_bright_temp_457
from .toa_reflectance import toa_reflectance_457
from .grab_meta import grab_meta
from dnppy import core
import arcpy


__all__=['cloud_mask_8',            # complete
         'cloud_mask_457']          # planned development (to include slc-off band gaps)


def cloud_mask_8(band_nums, BQA_path, outdir = False):
    """
    Removal of cloud-covered pixels in raw Landsat 8 bands using the BQA file included.

    To be performed on raw Landsat 8 level 1 data.

    Inputs:
      band_nums   A list of desired band numbers such as [3 4 5]
      BQA_path    The full filepath to the BQA file for the Landsat 8 dataset
      outdir      Output directory to save cloudless band tifs and the cloud mask
    """

    #enforce the input band numbers as a list of strings
    band_nums = core.enf_list(band_nums)
    band_nums = map(str, band_nums)

    #define the range of values in the BQA file to be reclassified as cloud (0) or not cloud (1)
    remap = arcpy.sa.RemapRange([[50000,65000,0],[28670,32000,0],[2,28669,1],[32001,49999,1],[1,1,"NoData"]])
    outReclass = arcpy.sa.Reclassify(BQA_path, "Value", remap)

    #set the name and save the binary cloud mask tiff file
    Mask_name = BQA_path.replace("_BQA", "")  
    CloudMask_path = core.create_outname(outdir, Mask_name, "Mask", "tif")   
    outReclass.save(CloudMask_path)

    #for each band listed in band_nums, apply the Con tool to erase cloud pixels and save each band as a new tiff
    for band_num in band_nums:      
        band_path = BQA_path.replace("BQA.tif", "B{0}.tif".format(band_num))            
        outname = core.create_outname(outdir, band_path, "NoClds", "tif")
        outCon = arcpy.sa.Con(outReclass, band_path, "", "VALUE = 1")
        outCon.save(outname)                 

    return



def cloud_mask_457(meta_path, outdir, Filter5Thresh=2.0, Filter6Thresh=2.0):
    """
    Creates a mask for removal of cloud-covered pixels in raw Landsat 4, 5, and 7 bands.

    To be performed on raw Landsat 4, 5, or 7 level 1 data.

    Inputs:
      meta_path         The full filepath to the MTL file for the Landsat dataset
      outdir            Output directory to the cloud mask and TOA band tiffs
      Filter5Thresh     Optional threshhold value for Filter #5, default set at 2
      Filter6Thresh     Optional threshhold value for Filter #6, default set at 2
    """
    
    #if pixelvalue == "Digital Numbers":
    toa_reflectance_457([2,3,4,5], meta_path, outdir)
    atsat_bright_temp_457(meta_path, outdir)
    
    metadata = grab_meta(meta_path)
    spacecraft = getattr(metadata, "SPACECRAFT_ID")

    if "4" in spacecraft or "5" in spacecraft:
        band_6 = "6"
    elif "7" in spacecraft:
        band_6 = "6_VCID_1"

    band_path2 = meta_path.replace("MTL.txt","B2.tif")
    Band2name = core.create_outname(outdir, band_path2, "TOA-Ref", "tif")
    Band2 = arcpy.Raster(Band2name)
    del band_path2, Band2name
    band_path3 = meta_path.replace("MTL.txt","B3.tif")
    Band3name = core.create_outname(outdir, band_path3, "TOA-Ref", "tif")
    Band3 = arcpy.Raster(Band3name)
    del band_path3, Band3name
    band_path4 = meta_path.replace("MTL.txt","B4.tif")
    Band4name = core.create_outname(outdir, band_path4, "TOA-Ref", "tif")
    Band4 = arcpy.Raster(Band4name)
    del band_path4, Band4name
    band_path5 = meta_path.replace("MTL.txt","B5.tif")
    Band5name = core.create_outname(outdir, band_path5, "TOA-Ref", "tif")
    Band5 = arcpy.Raster(Band5name)
    del band_path5, Band5name
    band_path6 = meta_path.replace("MTL.txt","B{0}.tif".format(band_6))
    Band6name = core.create_outname(outdir, band_path6, "Temp", "tif")
    Band6 = arcpy.Raster(Band6name)
    del band_path6, Band6name, band_6, metadata, spacecraft

    #elif pixelvalue == "Reflectance":
    #    for i,pathname in enumerate():
    #        exec("Band{0}=arcpy.Raster(pathname)".format(["1","3","4","5"][i]))
            
    #Establishing location of gaps in data. 0 = Gap, 1 = Data
    #This will be used multiple times in later steps
    arcpy.AddMessage("Creating Gap Mask")
    print "Creating Gap Mask"
    GapMask = ((Band2 > 0) * (Band3 > 0) * (Band4 > 0)*(Band5 > 0) * (Band6 > 0))
    GapMask.save(outdir+"\\GapMask.tif")

    arcpy.AddMessage("First pass underway")
    print "First pass underway"

    #Filter 1 - Brightness Threshold--------------------------------------------
    Cloudmask = Band3 > .08

    #Filter 2 - Normalized Snow Difference Index--------------------------------
    NDSI = (Band2 - Band5)/(Band2 + Band5)
    Snow = (NDSI > .6) * Cloudmask
    Cloudmask = (NDSI < .6) * Cloudmask

    #Filter 3 - Temperature Threshold-------------------------------------------
    Cloudmask = (Band6 < 300) * Cloudmask

    #Filter 4 - Band 5/6 Composite----------------------------------------------
    Cloudmask = (((1-Band5) * Band6) < 225) * Cloudmask
    Amb = (((1 - Band5) * Band6) > 225)

    #Filter 5 - Band 4/3 Ratio (eliminates vegetation)--------------------------
    #bright cloud tops are sometimes cut out by this filter. original threshold was
    #raising this threshold will make the algorithm more aggresive
    Cloudmask = ((Band4/Band3) < Filter5Thresh) * Cloudmask
    Amb = ((Band4/Band3) > Filter5Thresh) * Amb

    #Filter 6 - Band 4/2 Ratio (eliminates vegetation)--------------------------
    #bright cloud tops are sometimes cut out by this filter. original threshold was
    #raising this threshold will make the algorithm more aggresive
    Cloudmask = ((Band4/Band2) < Filter6Thresh) * Cloudmask
    Amb = ((Band4/Band2) > Filter6Thresh) * Amb

    #Filter 7 - Band 4/5 Ratio (Eliminates desert features)---------------------
    #   DesertIndex recorded
    DesertIndMask = ((Band4/Band5) > 1.0)
    Cloudmask = DesertIndMask * Cloudmask
    Amb = ((Band4/Band5) < 1.0) * Amb

    #Filter 8  Band 5/6 Composite (Seperates warm and cold clouds)--------------
    WarmCloud = (((1 - Band5) * Band6) > 210) * Cloudmask
    ColdCloud = (((1 - Band5) * Band6) < 210) * Cloudmask

    #Calculating percentage of the scene that is classified as Desert
    DesertGap = (DesertIndMask + 1) * GapMask
    try:
        arcpy.CalculateStatistics_management(DesertGap,ignore_values = "0")
        DesertIndex = DesertGap.mean - 1
    except:
        DesertGap.save(outdir + "\\Desert.tif")
        arcpy.CalculateStatistics_management(DesertGap,ignore_values = "0")
        DesertIndex=DesertGap.mean - 1
        os.remove(outdir + "\\Desert.tif")
    del DesertIndMask, DesertGap, NDSI

    #Calculating percentage of the scene that is classified as Snow
    ColdCloudGap = (ColdCloud + 1) * GapMask
    try:
        arcpy.CalculateStatistics_management(ColdCloudGap,ignore_values = "0")
        ColdCloudMean = ColdCloudGap.mean - 1
        del ColdCloudGap
    except:
        ColdCloudGap.save(outdir + "\\ColdCloud.tif")
        arcpy.CalculateStatistics_management(ColdCloudGap,ignore_values = "0")
        ColdCloudMean = ColdCloudGap.mean - 1
        os.remove(outdir + "\\ColdCloud.tif")
        del ColdCloudGap

    del Band2, Band3, Band4, Band5

    SnowGap = (Snow + 1) * GapMask
    try:
        arcpy.CalculateStatistics_management(SnowGap,ignore_values = "0")
        SnowPerc = SnowGap.mean - 1
        del SnowGap
    except:
        SnowGap.save(outdir + "\\Snow.tif")
        arcpy.CalculateStatistics_management(SnowGap,ignore_values = "0")
        SnowPerc = SnowGap.mean - 1
        os.remove(outdir + "\\Snow.tif")
        del SnowGap
    del Snow
    del GapMask
    
    #Determining whether or not snow is present and adjusting the Cloudmask
    #accordinging. If snow is present the Warm Clouds are reclassfied as ambigious
    if SnowPerc > .01:
        SnowPresent = True
        Cloudmask = ColdCloud
        Amb = Amb + WarmCloud
    else:
        SnowPresent = False
    del ColdCloud, WarmCloud, SnowPerc

    #Collecting statistics for Cloud pixel Temperature values. These will be used in later conditionals
    Tempclouds = Cloudmask * Band6
    Tempclouds.save(outdir + "\\TempClouds.tif")
    del Tempclouds

    #chunk the raster to be able to convert to a NumPy array

    
    Band6array = arcpy.RasterToNumPyArray(outdir + "\\TempClouds.tif")
    os.remove(outdir + "\\TempClouds.tif")
    os.remove(outdir + "\\TempClouds.tfw")

    Band6clouds = Band6array[np.where(Band6array > 0)]
    del Band6array
    TempMin = Band6clouds.min()
    TempMax = Band6clouds.max()
    TempMean = Band6clouds.mean()
    TempStd = Band6clouds.std()
    TempSkew = stats.skew(Band6clouds)
    Temp98perc = stats.scoreatpercentile(Band6clouds, 98.75)
    Temp97perc = stats.scoreatpercentile(Band6clouds, 97.50)
    Temp82perc = stats.scoreatpercentile(Band6clouds, 82.50)
    del Band6clouds

    #Pass 2 is run if the following conditionals are met
    if ColdCloudMean > .004 and DesertIndex > .5 and TempMean < 295:
        #Pass 2
        arcpy.AddMessage("Second Pass underway")

        #Adjusting Temperature thresholds based on skew
        if TempSkew > 0:
            if TempSkew > 1:
                shift = TempStd
            else:
                shift = TempStd * TempSkew
        else: shift = 0
        Temp97perc += shift
        Temp82perc += shift
        if Temp97perc > Temp98perc:
            Temp82perc = Temp82perc -(Temp97perc - Temp98perc)
            Temp97perc = Temp98perc

        warmAmbmask = ((Band6 * Amb) < Temp97perc)
        warmAmbmask = warmAmbmask * ((Amb * Band6) > Temp82perc)

        coldAmbmask = (Band6 * Amb ) < Temp82perc
        coldAmbmask = coldAmbmask * ((Amb * Band6) > 0)

        warmAmb = warmAmbmask * Band6
        coldAmb = coldAmbmask * Band6

        ThermEffect1 = warmAmbmask.mean
        ThermEffect2 = coldAmbmask.mean

        arcpy.CalculateStatistics_management(warmAmb, ignore_values = "0")
        arcpy.CalculateStatistics_management(coldAmb, ignore_values = "0")

        if ThermEffect1 < .4 and warmAmb.mean < 295 and SnowPresent == False:
            Cloudmask = Cloudmask + warmAmbmask + coldAmbmask
            arcpy.AddMessage("Upper Threshold Used")
        elif ThermEffect2 < .4 and coldAmb.mean < 295:
            Cloudmask = Cloudmask + coldAmbmask
            arcpy.AddMessage("Lower Threshold Used")

    #switch legend to 1=good data 0 = cloud pixel
    remap = arcpy.sa.RemapValue([[1,0],[0,1],["NODATA",1]])
    Cloud_Mask = arcpy.sa.Reclassify(Cloudmask, "Value", remap)
    mask_path = meta_path.split("\\")[-1]
    mask_path = mask_path.replace("_MTL", "")
    outname = core.create_outname(outdir, mask_path, "Mask", "tif")
    print outname
    Cloud_Mask.save(outname)

    os.remove(outdir + "\\GapMask.tif")
    os.remove(outdir + "\\GapMask.tfw")

    return
