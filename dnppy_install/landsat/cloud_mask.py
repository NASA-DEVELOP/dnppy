
# imports
from dnppy import core
import numpy

try: from scipy import stats
except: pass

import arcpy
import os
arcpy.CheckOutExtension("spatial")


__all__=['make_cloud_mask_457',     # complete
         'make_cloud_mask_8',       # complete
         'apply_cloud_mask']        # complete


def make_cloud_mask_8(BQA_path, outdir = False):
    """
    Creates a cloud mask tiff file from the Landsat 8 Quality Assessment Band (BQA) file.
    Requires only the BQA tiff file included in the dataset.

    Inputs:    
      BQA_path    The full filepath to the BQA file for the raw Landsat 8 dataset
      outdir      Output directory to save cloudless band tifs and the cloud mask
    """

    #define the range of values in the BQA file to be reclassified as cloud (0) or not cloud (1)
    remap = arcpy.sa.RemapRange([[50000,65000,0],[28670,32000,0],[2,28669,1],[32001,49999,1],[1,1,"NoData"]])
    outReclass = arcpy.sa.Reclassify(BQA_path, "Value", remap)

    #set the name and save the binary cloud mask tiff file
    if "\\" in BQA_path:
        BQA_split = BQA_path.split("\\")[-1]
    elif "//" in BQA_path:
        BQA_split = BQA_path.split("//")[-1]
    TileName = BQA_split.replace("_BQA.tif", "")

    #create an output name and save the mask tiff
    if outdir:
        CloudMask_path = core.create_outname(outdir, TileName, "Mask", "tif")
    else:
        folder = BQA_path.replace(BQA_split, "")
        CloudMask_path = core.create_outname(folder, TileName, "Mask", "tif")
        
    outReclass.save(CloudMask_path)

    return



def make_cloud_mask_457(B2_TOA_Ref, outdir = False, Filter5Thresh = 2.0, Filter6Thresh = 2.0):
    """
    Creates a binary mask raster for removal of cloud-covered pixels in raw Landsat 4, 5, and 7 bands.

    To be performed on Landsat 4, 5, or 7 data. Must be processed first with landsat.toa_reflectance_457
    for bands 2, 3, 4, and 5 and landsat.atsat_bright_temp_457 for band 6.

    *Note that for this function to run properly, bands 2, 3, 4, 5, and 6 must each be in the same folder
    and have the correct naming convention output by the landsat.toa_reflectance_457 and landsat.atsat_bright_temp_457
    functions (e.g. LT50410362011240PAC01_B2_TOA_Ref.tif, LT50410362011240PAC01_B6_Temp.tif).

    Inputs:
      B2_TOA-Ref.tif    The full filepath to the band 2 top-of-atmosphere reflectance tiff file
      outdir            Output directory to the cloud mask and TOA band tiffs
      Filter5Thresh     Optional threshhold value for Filter #5, default set at 2
      Filter6Thresh     Optional threshhold value for Filter #6, default set at 2
    """

    #discern if Landsat 4/5 or 7 for band 6 and designate rasters for bands 2, 3, 4, 5, and 6
    if "LT4" in B2_TOA_Ref or "LT5" in B2_TOA_Ref:
        band_6 = "6"
    elif "LE7" in B2_TOA_Ref:
        band_6 = "6_VCID_1"

    Band2 = arcpy.Raster(B2_TOA_Ref)
    band_path3 = B2_TOA_Ref.replace("B2_TOA_Ref.tif","B3_TOA_Ref.tif")
    Band3 = arcpy.Raster(band_path3)
    band_path4 = B2_TOA_Ref.replace("B2_TOA_Ref.tif","B4_TOA_Ref.tif")
    Band4 = arcpy.Raster(band_path4)
    band_path5 = B2_TOA_Ref.replace("B2_TOA_Ref.tif","B5_TOA_Ref.tif")
    Band5 = arcpy.Raster(band_path5)
    band_path6 = B2_TOA_Ref.replace("B2_TOA_Ref.tif","B{0}_ASBTemp.tif".format(band_6))
    Band6 = arcpy.Raster(band_path6)
    del band_path3, band_path4, band_path5, band_path6

    if "\\" in B2_TOA_Ref:
        name = B2_TOA_Ref.split("\\")[-1]
    elif "//" in B2_TOA_Ref:
        name = B2_TOA_Ref.split("//")[-1]
        
    if outdir == False:
        outdir = B2_TOA_Ref.replace(name, "")
            
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

    #Converting TempClouds to a text file and writing its non-zero/NAN values to a list
    outtxt = outdir + "\\tempclouds.txt"
    arcpy.RasterToASCII_conversion(outdir + "\\TempClouds.tif", outtxt)

    f = open(outtxt)
    list = []
    lines = f.readlines()[6:]
    for line in lines:
        for x in line.split(' '):
            try:
                x = float(x)
                if x > 0:
                    list.append(x)
            except ValueError:
                pass
    f.close()

    #Band6clouds = Band6array[np.where(Band6array > 0)]
    #del Band6array
    TempMin = min(list)
    TempMax = max(list)
    TempMean = numpy.mean(list)
    TempStd = numpy.std(list)
    TempSkew = stats.skew(list)
    Temp98perc = numpy.percentile(list, 98.75)
    Temp97perc = numpy.percentile(list, 97.50)
    Temp82perc = numpy.percentile(list, 82.50)
    del list

    #delete all intermediary files in the output directory
    for file in os.listdir(outdir):
        if "GapMask" in file:
            os.remove("{0}\\{1}".format(outdir, file))
        elif "TempClouds" in file:
            os.remove("{0}\\{1}".format(outdir, file))
        elif "tempclouds" in file:
            os.remove("{0}\\{1}".format(outdir, file))
            
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

    mask_path = B2_TOA_Ref.replace("_B2_TOA_Ref.tif", "")
    path = "{0}\\{1}".format(mask_path, file)

    #create output name
    mask_path = name.replace("_B2_TOA_Ref.tif", "")
    if outdir:
        outname = core.create_outname(outdir, mask_path, "Mask", "tif")
    else:
        folder = B2_TOA_Ref.replace(name, "")
        outname = core.create_outname(folder, mask_path, "Mask", "tif")

    print "Cloud mask saved at {0}".format(outname)
    Cloud_Mask.save(outname)

    del name, mask_path, Cloud_Mask, path, remap
    
    return



def apply_cloud_mask(mask_path, folder, outdir = False):
    """
    Removal of cloud-covered pixels in Landsat 4, 5, 7, or 8 bands using the mask created with
    landsat.make_cloud_mask_8 or landsat.make_cloud_mask_457.

    Inputs:
      folder        The folder containing the raw or processed band tiffs to remove clouds from  
      mask_path     The full filepath to the mask file created by make_cloud_mask_8 or make_cloud_mask_457
      outdir        Output directory to save cloudless band tiffs
                    *If left False the output tiffs will be saved in "folder"
    """

    #enforce the input band numbers as a list of strings
    if "\\" in mask_path:
        mask_split = mask_path.split("\\")[-1]
    elif "//" in mask_path:
        mask_split = mask_path.split("//")[-1]
    tilename = mask_split.replace("_Mask.tif", "")

    #loop through each file in folder
    inlist = []
    outlist = []
    x = 1
    for band in os.listdir(folder):
        band_name1 = "{0}_B{1}_".format(tilename, x)
        band_name2 = "{0}_B{1}.".format(tilename, x)
        
        #for each band (number 1-9) tif whose id matches the mask's, create an output name and append to the in and output lists
        if (band_name1 in band or band_name2 in band) and (".tif" in band or ".TIF" in band) and (".tif." not in band and ".TIF." not in band):
            name = band.replace(".tif", "")
            if outdir:
                outname = core.create_outname(outdir, name, "NoClds", "tif")
            else:
                outname = core.create_outname(folder, name, "NoClds", "tif")
            inlist.append("{0}\\{1}".format(folder, band))
            outlist.append(outname)
            x = x + 1

        #create separate names for Landsat 8 TIRS bands 10 and 11 if present and append to the lists
        tirs10 = "{0}_B10".format(tilename)
        tirs11 = "{0}_B11".format(tilename)
        if (tirs10 in band or tirs11 in band) and (".tif" in band or ".TIF" in band) and (".tif." not in band and ".TIF." not in band):
            name = band.replace(".tif", "")
            if outdir:
                outname = core.create_outname(outdir, name, "NoClds", "tif")
            else:
                outname = core.create_outname(folder, name, "NoClds", "tif")
            inlist.append("{0}\\{1}".format(folder, band))
            outlist.append(outname)

    #loop through the input list and apply the con to each file, saving to the corresponding path in the output list
    y = 0
    for file in inlist:
        outcon = arcpy.sa.Con(mask_path, file, "", "VALUE = 1")
        outcon.save(outlist[y])
        y = y + 1
        if y > (len(inlist) - 1):
            break

    return
