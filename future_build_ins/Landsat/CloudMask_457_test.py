import arcpy
import numpy as np
import os

def Cloud_Mask_457(meta_path, outdir, Filter5Thresh=2.0, Filter6Thresh=2.0):
    
    #if pixelvalue == "Digital Numbers":
    TOA_Reflectance_457([2,3,4,5], meta_path, outdir)
    AtSat_Bright_Temp_457(meta_path, outdir)
    
    metadata = Grab_Meta(meta_path)
    spacecraft = getattr(metadata, "SPACECRAFT_ID")

    if "4" in spacecraft or "5" in spacecraft:
        band_6 = "6"
    elif "7" in spacecraft:
        band_6 = "6_VCID_1"

    band_path2 = meta_path.replace("MTL.txt","B2.tif")
    Band2name = core.Create_Outname(outdir, band_path2, "TOA-Ref", "tif")
    Band2 = arcpy.Raster(Band2name)
    band_path3 = meta_path.replace("MTL.txt","B3.tif")
    Band3name = core.Create_Outname(outdir, band_path3, "TOA-Ref", "tif")
    Band3 = arcpy.Raster(Band3name)
    band_path4 = meta_path.replace("MTL.txt","B4.tif")
    Band4name = core.Create_Outname(outdir, band_path4, "TOA-Ref", "tif")
    Band4 = arcpy.Raster(Band4name)
    band_path5 = meta_path.replace("MTL.txt","B5.tif")
    Band5name = core.Create_Outname(outdir, band_path5, "TOA-Ref", "tif")
    Band5 = arcpy.Raster(Band5name)
    band_path6 = meta_path.replace("MTL.txt","B{0}.tif".format(band_6))
    Band6name = core.Create_Outname(outdir, band_path6, "Temp", "tif")
    Band6 = arcpy.Raster(Band6name)

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
    Cloudmask=Band3 >.08

    #Filter 2 - Normalized Snow Difference Index--------------------------------
    NDSI=(Band2-Band5)/(Band2+Band5)
    Snow=(NDSI>.6)*Cloudmask
    Cloudmask=(NDSI<.6)*Cloudmask

    #Filter 3 - Temperature Threshold-------------------------------------------
    Cloudmask=(Band6<300)*Cloudmask

    #Filter 4 - Band 5/6 Composite----------------------------------------------
    Cloudmask=(((1-Band5)*Band6)<225)*Cloudmask
    Amb=(((1-Band5)*Band6)>225)

    #Filter 5 - Band 4/3 Ratio (eliminates vegetation)--------------------------
    #bright cloud tops are sometimes cut out by this filter. original threshold was
    #raising this threshold will make the algorithm more aggresive
    Cloudmask=((Band4/Band3)<Filter5Thresh)*Cloudmask
    Amb=((Band4/Band3)>Filter5Thresh)*Amb

    #Filter 6 - Band 4/2 Ratio (eliminates vegetation)--------------------------
    #bright cloud tops are sometimes cut out by this filter. original threshold was
    #raising this threshold will make the algorithm more aggresive
    Cloudmask=((Band4/Band2)<Filter6Thresh)*Cloudmask
    Amb=((Band4/Band2)>Filter6Thresh)*Amb

    #Filter 7 - Band 4/5 Ratio (Eliminates desert features)---------------------
    #   DesertIndex recorded
    DesertIndMask=((Band4/Band5)>1.0)
    Cloudmask=DesertIndMask*Cloudmask
    Amb=((Band4/Band5)<1.0)*Amb

    #Filter 8  Band 5/6 Composite (Seperates warm and cold clouds)--------------
    WarmCloud=(((1-Band5)*Band6)>210)*Cloudmask
    ColdCloud=(((1-Band5)*Band6)<210)*Cloudmask

    #Calculating percentage of the scene that is classified as Desert
    DesertGap=(DesertIndMask+1)*GapMask
    try:
        arcpy.CalculateStatistics_management(DesertGap,ignore_values="0")
        DesertIndex=DesertGap.mean-1
    except:
        DesertGap.save(outdir+"\\Desert.tif")
        arcpy.CalculateStatistics_management(DesertGap,ignore_values="0")
        DesertIndex=DesertGap.mean-1
        os.remove(outdir+"\\Desert.tif")
    del DesertIndMask, DesertGap, NDSI

    #Calculating percentage of the scene that is classified as Snow
    ColdCloudGap=(ColdCloud+1)*GapMask
    try:
        arcpy.CalculateStatistics_management(ColdCloudGap,ignore_values="0")
        ColdCloudMean=ColdCloudGap.mean-1
        del ColdCloudGap
    except:
        ColdCloudGap.save(outdir+"\\ColdCloud.tif")
        arcpy.CalculateStatistics_management(ColdCloudGap,ignore_values="0")
        ColdCloudMean=ColdCloudGap.mean-1
        os.remove(outdir+"\\ColdCloud.tif")
        del ColdCloudGap

    del Band2,Band3,Band4,Band5

    SnowGap=(Snow+1)*GapMask
    try:
        arcpy.CalculateStatistics_management(SnowGap,ignore_values="0")
        SnowPerc=SnowGap.mean-1
        del SnowGap
    except:
        SnowGap.save(outdir+"\\Snow.tif")
        arcpy.CalculateStatistics_management(SnowGap,ignore_values="0")
        SnowPerc=SnowGap.mean-1
        os.remove(outdir+"\\Snow.tif")
        del SnowGap
    del Snow

    #Determining whether or not snow is present and adjusting the Cloudmask
    #accordinging. If snow is present the Warm Clouds are reclassfied as ambigious
    if SnowPerc>.01:
        SnowPresent=True
        Cloudmask=ColdCloud
        Amb=Amb+WarmCloud
    else:
        SnowPresent=False

    #Collecting statistics for Cloud pixel Temperature values. These will be used in later conditionals
    Tempclouds=Cloudmask*Band6

    Tempclouds.save(outdir+"\\TempClouds.tif")
    Band6array=arcpy.RasterToNumPyArray(outdir+"\\TempClouds.tif")
    del Tempclouds
    os.remove(outdir+"\\TempClouds.tif")

    Band6clouds=Band6array[np.where(Band6array>0)]
    del Band6array
    TempMin=Band6clouds.min()
    TempMax=Band6clouds.max()
    TempMean=Band6clouds.mean()
    TempStd=Band6clouds.std()
    TempSkew=stats.skew(Band6clouds)
    Temp98perc=stats.scoreatpercentile(Band6clouds, 98.75)
    Temp97perc=stats.scoreatpercentile(Band6clouds, 97.50)
    Temp82perc=stats.scoreatpercentile(Band6clouds, 82.50)
    del Band6clouds

    #Pass 2 is run if the following conditionals are met
    if ColdCloudMean>.004 and DesertIndex>.5 and TempMean<295:
        #Pass 2
        arcpy.AddMessage("Second Pass underway")

        #Adjusting Temperature thresholds based on skew
        if TempSkew>0:
            if TempSkew>1:
                shift=TempStd
            else:
                shift = TempStd*TempSkew
        else: shift=0
        Temp97perc+=shift
        Temp82perc+=shift
        if Temp97perc>Temp98perc:
            Temp82perc=Temp82perc-(Temp97perc-Temp98perc)
            Temp97perc=Temp98perc

        warmAmbmask=((Band6*Amb)<Temp97perc)
        warmAmbmask=warmAmbmask*((Amb*Band6)>Temp82perc)

        coldAmbmask=(Band6*Amb)<Temp82perc
        coldAmbmask=coldAmbmask*((Amb*Band6)>0)

        warmAmb=warmAmbmask*Band6
        coldAmb=coldAmbmask*Band6

        ThermEffect1=warmAmbmask.mean
        ThermEffect2=coldAmbmask.mean

        arcpy.CalculateStatistics_management(warmAmb,ignore_values="0")
        arcpy.CalculateStatistics_management(coldAmb,ignore_values="0")

        if ThermEffect1<.4 and warmAmb.mean<295 and SnowPresent==False:
            Cloudmask=Cloudmask+warmAmbmask+coldAmbmask
            arcpy.AddMessage("Upper Threshold Used")
        elif ThermEffect2<.4 and coldAmb.mean<295:
            Cloudmask=Cloudmask+coldAmbmask
            arcpy.AddMessage("Lower Threshold Used")

    #switch legend to 1=good data 0 = cloud pixel

    Cloudmask = Reclassify(Cloudmask,"Value",RemapValue([[1,0],[0,1],["NODATA",1]]))
    mask_path = meta_path.replace("_MTL.txt",".tif")
    outname = core.Create_Outname(outdir, mask_path, "Mask")
    Cloudmask.save(outname)

    del GapMask
    os.remove(outdir+"\\GapMask.tif")

    return
