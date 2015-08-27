
# imports
from dnppy import core
import numpy
import arcpy
import os
try: from scipy import stats
except: pass
if arcpy.CheckExtension('Spatial')=='Available':
    arcpy.CheckOutExtension('Spatial')
    arcpy.env.overwriteOutput = True


__all__=['make_cloud_mask_457',     # complete
         'make_cloud_mask_8',       # complete
         'apply_cloud_mask']        # complete


def make_cloud_mask_8(BQA_path, outdir = None):
    """
    Creates a cloud mask tiff file from the Landsat 8 Quality Assessment Band (BQA) file.
    Requires only the BQA tiff file included in the dataset.

    :param BQA_path:    The full filepath to the BQA file for the raw Landsat 8 dataset
    :param outdir:      Output directory to save cloudless band tifs and the cloud mask

    :return cloud_mask_path: Filepath to newly created cloud mask
    """

    #define the range of values in the BQA file to be reclassified as cloud (0) or not cloud (1)
    remap = arcpy.sa.RemapRange([[50000,65000,0],[28670,32000,0],[2,28669,1],[32001,49999,1],[1,1,"NoData"]])
    outReclass = arcpy.sa.Reclassify(BQA_path, "Value", remap)

    #set the name and save the binary cloud mask tiff file
    BQA = os.path.abspath(BQA_path)
    name = os.path.split(BQA)[1]
    name_ext = os.path.splitext(name)[0]
    TileName = name_ext.replace("_BQA", "")

    #create an output name and save the mask tiff
    if outdir is not None:
        outdir = os.path.abspath(outdir)
        cloud_mask_path = core.create_outname(outdir, TileName, "Mask", "tif")
    else:
        folder = os.path.dirname(BQA)
        cloud_mask_path = core.create_outname(folder, TileName, "Mask", "tif")
        
    outReclass.save(cloud_mask_path)

    return cloud_mask_path



def make_cloud_mask_457(B2_TOA_Ref, outdir = None, Filter5Thresh = 2.0, Filter6Thresh = 2.0):
    """
    Creates a binary mask raster for removal of cloud-covered pixels in raw Landsat 4, 5, and 7 bands.

    To be performed on Landsat 4, 5, or 7 data. Must be processed first with landsat.toa_reflectance_457
    for bands 2, 3, 4, and 5 and landsat.atsat_bright_temp_457 for band 6.

    Note that for this function to run properly, bands 2, 3, 4, 5, and 6 must each be in the same folder
    and have the correct naming convention output by the landsat.toa_reflectance_457 and landsat.atsat_bright_temp_457
    functions (e.g. LT50410362011240PAC01_B2_TOA_Ref.tif, LT50410362011240PAC01_B6_Temp.tif).

    :param B2_TOA_Ref:      The full filepath to the band 2 top-of-atmosphere reflectance tiff file
    :param outdir:          Output directory to the cloud mask and TOA band tiffs
    :param Filter5Thresh:   Optional threshold value for Filter #5, default set at 2
    :param Filter6Thresh:   Optional threshold value for Filter #6, default set at 2

    :return cloud_mask_path: filepath to newly created cloud mask
    """

    #discern if Landsat 4/5 or 7 for band 6 and designate rasters for bands 2, 3, 4, 5, and 6
    if "LT4" in B2_TOA_Ref or "LT5" in B2_TOA_Ref:
        band_6 = "6"
    elif "LE7" in B2_TOA_Ref:
        band_6 = "6_VCID_1"
    else:
        band_6 = None

    B2_path = os.path.abspath(B2_TOA_Ref)

    Band2 = arcpy.Raster(B2_path)

    band_path3 = B2_path.replace("B2_TOA_Ref.tif", "B3_TOA_Ref.tif")
    band_path4 = B2_path.replace("B2_TOA_Ref.tif", "B4_TOA_Ref.tif")
    band_path5 = B2_path.replace("B2_TOA_Ref.tif", "B5_TOA_Ref.tif")
    band_path6 = B2_path.replace("B2_TOA_Ref.tif", "B{0}_ASBTemp.tif".format(band_6))

    Band3 = arcpy.Raster(band_path3)
    Band4 = arcpy.Raster(band_path4)
    Band5 = arcpy.Raster(band_path5)
    Band6 = arcpy.Raster(band_path6)
    
    del band_path3, band_path4, band_path5, band_path6

    name = os.path.split(B2_path)[1]

    if outdir is None:
        outdir = os.path.split(B2_path)[0]
            
    #Establishing location of gaps in data. 0 = Gap, 1 = Data
    #This will be used multiple times in later steps
    print("Creating Gap Mask")
    GapMask = ((Band2 > 0) * (Band3 > 0) * (Band4 > 0)*(Band5 > 0) * (Band6 > 0))
    GapMask.save(os.path.join(outdir,"GapMask.tif"))

    print("First pass underway")

    #Filter 1 - Brightness Threshold--------------------------------------------
    Cloudmask = Band3 > .08

    #Filter 2 - Normalized Snow Difference Index--------------------------------
    NDSI = (Band2 - Band5)/(Band2 + Band5)
    Snow = (NDSI > .6) * Cloudmask
    Cloudmask *= (NDSI < .6)

    #Filter 3 - Temperature Threshold-------------------------------------------
    Cloudmask *= (Band6 < 300)

    #Filter 4 - Band 5/6 Composite----------------------------------------------
    Cloudmask *= (((1-Band5) * Band6) < 225)
    Amb = (((1 - Band5) * Band6) > 225)

    #Filter 5 - Band 4/3 Ratio (eliminates vegetation)--------------------------
    #bright cloud tops are sometimes cut out by this filter. original threshold was
    #raising this threshold will make the algorithm more aggresive
    Cloudmask *= ((Band4/Band3) < Filter5Thresh)
    Amb *= ((Band4/Band3) > Filter5Thresh)

    #Filter 6 - Band 4/2 Ratio (eliminates vegetation)--------------------------
    #bright cloud tops are sometimes cut out by this filter. original threshold was
    #raising this threshold will make the algorithm more aggresive
    Cloudmask *= ((Band4/Band2) < Filter6Thresh)
    Amb *= ((Band4/Band2) > Filter6Thresh)

    #Filter 7 - Band 4/5 Ratio (Eliminates desert features)---------------------
    #   DesertIndex recorded
    DesertIndMask = ((Band4/Band5) > 1.0)
    Cloudmask *= DesertIndMask
    Amb *= ((Band4/Band5) < 1.0)

    #Filter 8  Band 5/6 Composite (Seperates warm and cold clouds)--------------
    WarmCloud = (((1 - Band5) * Band6) > 210) * Cloudmask
    ColdCloud = (((1 - Band5) * Band6) < 210) * Cloudmask

    #Calculating percentage of the scene that is classified as Desert
    DesertGap = (DesertIndMask + 1) * GapMask
    try:
        arcpy.CalculateStatistics_management(DesertGap,ignore_values = "0")
        DesertIndex = DesertGap.mean - 1
    except:
        DesertGap.save(os.path.join(outdir, "Desert.tif"))
        arcpy.CalculateStatistics_management(DesertGap,ignore_values = "0")
        DesertIndex = DesertGap.mean - 1
        os.remove(os.path.join(outdir, "Desert.tif"))
    del DesertIndMask, DesertGap, NDSI

    #Calculating percentage of the scene that is classified as Snow
    ColdCloudGap = (ColdCloud + 1) * GapMask
    try:
        arcpy.CalculateStatistics_management(ColdCloudGap,ignore_values = "0")
        ColdCloudMean = ColdCloudGap.mean - 1
        del ColdCloudGap
    except:
        ColdCloudGap.save(os.path.join(outdir, "ColdCloud.tif"))
        arcpy.CalculateStatistics_management(ColdCloudGap,ignore_values = "0")
        ColdCloudMean = ColdCloudGap.mean - 1
        os.remove(os.path.join(outdir, "ColdCloud.tif"))
        del ColdCloudGap

    del Band2, Band3, Band4, Band5

    SnowGap = (Snow + 1) * GapMask
    try:
        arcpy.CalculateStatistics_management(SnowGap,ignore_values = "0")
        SnowPerc = SnowGap.mean - 1
        del SnowGap
    except:
        SnowGap.save(os.path.join(outdir, "Snow.tif"))
        arcpy.CalculateStatistics_management(SnowGap,ignore_values = "0")
        SnowPerc = SnowGap.mean - 1
        os.remove(os.path.join(outdir, "Snow.tif"))
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
    Tempclouds.save(os.path.join(outdir, "TempClouds.tif"))
    del Tempclouds

    #Converting TempClouds to a text file and writing its non-zero/NAN values to a list
    outtxt = os.path.join(outdir, "tempclouds.txt")
    arcpy.RasterToASCII_conversion(os.path.join(outdir, "TempClouds.tif"), outtxt)

    f = open(outtxt)
    alist = []
    lines = f.readlines()[6:]
    for line in lines:
        for x in line.split(' '):
            try:
                x = float(x)
                if x > 0:
                    alist.append(x)
            except ValueError:
                pass
    f.close()

    #Band6clouds = Band6array[np.where(Band6array > 0)]
    #del Band6array
    TempMin = min(alist)
    TempMax = max(alist)
    TempMean = numpy.mean(alist)
    TempStd = numpy.std(alist)
    TempSkew = stats.skew(alist)
    Temp98perc = numpy.percentile(alist, 98.75)
    Temp97perc = numpy.percentile(alist, 97.50)
    Temp82perc = numpy.percentile(alist, 82.50)
    del alist

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
            Cloudmask += coldAmbmask
            arcpy.AddMessage("Lower Threshold Used")

    #switch legend to 1=good data 0 = cloud pixel
    remap = arcpy.sa.RemapValue([[1,0],[0,1],["NODATA",1]])
    Cloud_Mask = arcpy.sa.Reclassify(Cloudmask, "Value", remap)

    #create output name
    mask_path = name.replace("_B2_TOA_Ref.tif", "")
    if outdir:
        outdir = os.path.abspath(outdir)
        outname = core.create_outname(outdir, mask_path, "Mask", "tif")
    else:
        folder = B2_TOA_Ref.replace(name, "")
        outname = core.create_outname(folder, mask_path, "Mask", "tif")

    print "Cloud mask saved at {0}".format(outname)
    Cloud_Mask.save(outname)
    cloud_mask_path = arcpy.Raster(outname)

    del name, mask_path, Cloud_Mask, remap
    
    return cloud_mask_path



def apply_cloud_mask(mask_path, folder, outdir = None):
    """
    Removal of cloud-covered pixels in Landsat 4, 5, 7, or 8 bands using the mask created with
    landsat.make_cloud_mask_8 or landsat.make_cloud_mask_457.

    :param folder:        The folder containing the raw or processed band tiffs to remove clouds from
    :param mask_path:     The full filepath to the mask file created by make_cloud_mask_8 or make_cloud_mask_457
    :param outdir:        Output directory to save cloudless band tiffs, default is same as "folder"

    :return no_clouds_list: List of files created by this function with cloud mask applied.
    """

    no_clouds_list = []

    #enforce the input band numbers as a list of strings
    mpath = os.path.abspath(mask_path)
    mask_split = os.path.split(mpath)[1]
    name = os.path.splitext(mask_split)[0]
    tilename = name.replace("_Mask", "")
    folder = os.path.abspath(folder)

    #loop through each file in folder
    inlist = []
    outlist = []

    for band in os.listdir(folder):
        band_name = "{0}_B".format(tilename)
        
        #for each band (number 1-9) tif whose id matches the mask's, create an output name and append to the in and output lists
        if (band_name in band) and (band[-4:] == ".tif" or band[-4:] == ".TIF") and ("NoClds" not in band) and ("BQA" not in band):
            name = band.replace(".tif", "")
            if outdir is not None:
                outname = core.create_outname(outdir, name, "NoClds", "tif")
            else:
                outname = core.create_outname(folder, name, "NoClds", "tif")
            inlist.append("{0}\\{1}".format(folder, band))
            outlist.append(outname)

    #loop through the input list and apply the con to each file, saving to the corresponding path in the output list
    y = 0
    for afile in inlist:
        outcon = arcpy.sa.Con(mask_path, afile, "", "VALUE = 1")
        outcon.save(outlist[y])
        no_clouds_list.append(outlist[y])
        y += 1
        if y > (len(inlist) - 1):
            break

    return no_clouds_list
