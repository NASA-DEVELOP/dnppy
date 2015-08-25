"""
This script will allow the user to download data from Landsat 4, 5, 7, and 8 and calculate Green Normalized
Difference Vegetation Index (GNDVI), Normalized Difference Pigment Index (NDPI), and a wetland discrimination index
(WDI) for each image.

The script uses functions from arcpy and dnppy (Develop National Program Python Library) and therefore requires an
ArcMap installation and a dnppy installation (https://github.com/nasa/dnppy).

The script first unzips the Landsat files and extracts them into their own folders. Images are group by year, with all
images taken in one year in separate folders within the year's folder. The script then calculates top of atmosphere
reflectance for each image band in order to reduce atmospheric influence in the calculation of the band ratios. The
three band ratios are then calculated and new raster images are created as results.
"""

__author__ = 'kapatel3'

#import libraries and modules needed for the code to run
import dnppy, gdal, numpy, gdalconst, os, sys, ogr, tarfile, arcpy
from arcpy import env
from arcpy.sa import *
from gdalconst import *
from dnppy import *

env.overwriteOutput = True
#Replace the text inside the quotation marks with the file path of the folder containing the Landsat tar.gz files.
directory = r"C:\Users\kapatel3\Desktop\NCEcoData\2005and2014LandsatData"
os.chdir(directory)

"""
DEFINE FUNCTIONS
below is where the functions used throughout the script are defined before they are called later on in the script.
"""

"""
The function UNTAR unzips the raw Landsat data into its own folder and groups the images by year it was taken. The
script will create new folders within the directory folder defined above.
"""
def untar(fname, fpath):
    if (fname.endswith("tar.gz")):
        tar = tarfile.open(fname)
        tar.extractall(path = fpath)
        tar.close()
        os.remove(fname)

        print "Extracted in directory" + fpath #as the script runs the file path of the extracted image will be printed.

    else:

        print "Not a tar.gz file %s" %sys.argv[0] #non tar.gz files won't be unzipped

"""
The function GNDVI_457 is used for calculating Green NDVI on Landsat 4, 5, and 7 data. The function uses the green and
NIR bands to calculate GNDVI the equation for which is Green band minus the Near InfraRed band divided by the Green band
plus the Near InfraRed band:

GNDVI = (green - NIR)/(green + NIR)

The function then reclasses the GNDVI image to a binary raster image, an image that only has two values: 0 and 1, by
applying and 0 threshold to the image. This threshold is the most common one found in the literature and classifies
values below 0 as water and values higher than 0 as land. The function then saves this threshold image as a new raster.
This band ratio is used to derive shoreline locations for each image to get a better sense of how
shoreline changes along the watershed are affecting wetlands. In addition, masking out areas defined as water place
more focus on the wetlands themselves and allow for a clearer visual analysis.
"""
def GNDVI_457(Band2, Band4, outdir = False): #inputs will be TOA reflectance calculated within the script

    #Set the input bands to float
    green = arcpy.sa.Float(Band2)
    NIR = arcpy.sa.Float(Band4)

    #Calculate the GNDVI:
    L457_GNDVI = (green - NIR)/(green + NIR)

    #reclass image to determine shoreline extent
    arcpy.CheckOutExtension("Spatial")
    inRaster = L457_GNDVI
    reclassField = "Value"
    min_val = arcpy.GetRasterProperties_management(inRaster, "MINIMUM")
    max_val = arcpy.GetRasterProperties_management(inRaster, "MAXIMUM")
    remap = RemapRange([[min_val,0,1],[0,max_val,0]]) #0 is water, 1 is land

    #call the arcpy Reclassify function
    outReclass = arcpy.sa.Reclassify(inRaster, reclassField, remap, "NODATA")

    #create the theshold image file name and save the new raster
    name = Band2.split("\\")[-1]
    GNDVIThresh_name = name.replace("_B2","")

    if outdir:
        thresh_outname = core.create_outname(outdir, GNDVIThresh_name, "GNDVI_threshold", "tif")
    else:
        folder = Band4.replace(name, "")
        thresh_outname = core.create_outname(folder, GNDVIThresh_name, "GNDVI_threshold", "tif")
    
    outReclass.save(thresh_outname)

"""
The function GNDVI_8 is used for calculating GNDVI on Landsat 8 data. A separate function has to be defined for Landsat
8 because of the different way bands are defined between the sensors. For Landsat 4, 5, and 7, band 1 is the blue, band
2 is green, and band 3 is red. For Landsat 8, band 2 is blue, band 3 is green, and band 4 is red. Therefore, a new GNDVI
function must be defined for Landsat 8 that uses these band numbers.

The function preforms the exact same calculation as the GNDVI_457 function above, but uses the different band numbers.
"""

def GNDVI_8(Band3, Band5, outdir = False): #Landsat 8 Bands 3 and 5 are used, instead of 2 and 4 like above.

    name = Band3.split("\\")[-1]
    GNDVIThresh_name = name.replace("_B3","")

    #Set the input bands to float
    green = arcpy.sa.Float(Band3)
    NIR = arcpy.sa.Float(Band5)

    #Calculate the NDVI
    L8_GNDVI = (green - NIR)/(green + NIR)

    #reclass image
    arcpy.CheckOutExtension("Spatial")
    inRaster = L8_GNDVI
    reclassField = "Value"
    min_val = arcpy.GetRasterProperties_management(inRaster, "MINIMUM")
    max_val = arcpy.GetRasterProperties_management(inRaster, "MAXIMUM")
    remap = RemapRange([[min_val,0,1],[0,max_val,0]]) #0 is water, 1 is land

    #call the arcpy Reclassify function
    outReclass = Reclassify(inRaster, reclassField, remap, "NODATA")

    #create the theshold image file name and save the new raster
    if outdir:
        thresh_outname = core.create_outname(outdir, GNDVIThresh_name, "GNDVI_threshold", "tif")
    else:
        folder = Band3.replace(name, "")
        thresh_outname = core.create_outname(folder, GNDVIThresh_name, "GNDVI_threshold", "tif")
    
    outReclass.save(thresh_outname) 

"""
The WDI_457 function is used to calculate wetland extent on Landsat 4, 5, and 7 data. This indicator is known for
highlighting wetlands and separating between wetlands and other land cover classes. The equation ratios the Near
InfraRed band and the Middle InfraRed band:

wetland discriminator index = (NIR*MIR)/(NIR+MIR)

The function calculates this band ratio and saves the output as a new raster image.
"""
def WDI_457(Band4, Band7, outdir = False): #inputs should be TOA reflectance

    #Set the input bands to float
    NIR = arcpy.sa.Float(Band4)
    MIR = arcpy.sa.Float(Band7)

    #Calculate the GNDVI
    L457_WDI = (NIR*MIR)/(NIR+MIR)

    #Create the output name and save the GNDVI tiff
    name = Band4.split("\\")[-1]
    GNDVI_name = name.replace("_B4","")

    if outdir:
        outname = core.create_outname(outdir, GNDVI_name, "WDI", "tif")
    else:
        folder = Band7.replace(name, "")
        outname = core.create_outname(folder, GNDVI_name, "WDI", "tif")
    
    L457_WDI.save(outname)
"""
The WDI_8 function is used to calculate wetland extent on Landsat 8 data. The function does the same thing the
WDI_457 function does but uses the Shortwave InfraRed and Middle InfraRed bands corresponding to Landsat 8.

The function calculates this band ratio and saves the output as a new raster image.
"""
def WDI_8(Band5, Band7, outdir = False): #inputs should be TOA reflectance

    #Set the input bands to float
    NIR = arcpy.sa.Float(Band5)
    MIR = arcpy.sa.Float(Band7)

    #Calculate the GNDVI
    L8_WDI = (NIR*MIR)/(NIR+MIR)

    #Create the output name and save the GNDVI tiff
    name = Band5.split("\\")[-1]
    GNDVI_name = name.replace("_B5","")

    if outdir:
        outname = core.create_outname(outdir, GNDVI_name, "WDI", "tif")
    else:
        folder = Band7.replace(name, "")
        outname = core.create_outname(folder, GNDVI_name, "WDI", "tif")

    L8_WDI.save(outname)
"""
The NDPI_457 function is used to calculate wetland extent on Landsat 4, 5, and 7 data. NDPI is used to assess pigment
levels in vegetation throughout the scene. Higher NPDI values indicates a higher amount of caroteniod which persists in
unhealthy leaves, therefore lower NDPI values show healthy vegetation. The equation uses the Red and Blue bands:

NDPI = (red-blue)/(red+blue)

The function calculates this band ratio and saves the output as a new raster image.
"""
def ndpi_457(Band1, Band3, outdir = False): #inputs should be TOA reflectance
    
    #Set the input bands to float
    blue = arcpy.sa.Float(Band1)
    red = arcpy.sa.Float(Band3)

    #Calculate the GNDVI
    L457_ndpi = (red-blue)/(red+blue)

    #Create the output name and save the GNDVI tiff
    name = Band1.split("\\")[-1]
    GNDVI_name = name.replace("_B1","")

    if outdir:
        outname = core.create_outname(outdir, GNDVI_name, "ndpi", "tif")
    else:
        folder = Band7.replace(name, "")
        outname = core.create_outname(folder, GNDVI_name, "ndpi", "tif")
    
    L457_ndpi.save(outname)
"""
The NDPI_8 function is used to calculate wetland extent on Landsat 8 data. The function does the same thing the
NDPI_457 function does but uses the Red and Blue bands corresponding to Landsat 8.

The function calculates this band ratio and saves the output as a new raster image.
"""
def ndpi_8(Band2, Band4, outdir = False): #inputs should be TOA reflectance
    
    #Set the input bands to float
    blue = arcpy.sa.Float(Band2)
    red = arcpy.sa.Float(Band4)

    #Calculate the GNDVI
    L8_ndpi = (red-blue)/(red+blue)

    #Create the output name and save the GNDVI tiff
    name = Band2.split("\\")[-1]
    GNDVI_name = name.replace("_B2","")

    if outdir:
        outname = core.create_outname(outdir, GNDVI_name, "ndpi", "tif")
    else:
        folder = Band7.replace(name, "")
        outname = core.create_outname(folder, GNDVI_name, "ndpi", "tif")
    
    L8_ndpi.save(outname)
"""
The MASK function is used to mask each NDPI and WDI image by the corresponding GNDVI image so that the changes in
shoreline extent are shown in the NDPI and WDI images and so that wetlands are highlighted in the images.
"""
def mask(threshold, image, outdir):
    con = Con(threshold,1,"","value > 0")
    mask = (image*con)

    name = str(image).split("\\")[-1]
    outname = core.create_outname(outdir, name, "_Masked", "tif")
    mask.save(outname)
    print "saved masked image"

"""
WHERE CODE THAT RUNS SCRIPT STARTS
here is where all the functions defined above are called and used in the script to preform the data processing
"""

"""
The code below will pull unzip all the .tar.gz files and extract them into their own folders and separate those folders
by the year the image comes from. As the code unzips each image, the image location will be printed in the interactive
window. When all images have been extracted "files have been extracted" will be printed.

Landsat images all have a set naming convention which this code makes use of. Therefore, it is important for the images
to all be original Landsat images and not the CDR correct images. This script would have to be altered to work with the
naming convention associated with the Landsat CDR images.
"""

for file in os.listdir(directory):#go through all the files in the directory
    if file.endswith("tar.gz"):#if the file ends with tar.gz it will be unzipped
        folderName = file[0:21]#set the folder name for the unzipped images to be the image name
        year = file[9:13]#set the year folder
        path = directory + "\\" + year + "\\" + folderName#set the path for the unzipped images
        if not os.path.exists(path):
            os.makedirs(path) #create the path and associated folders
        untar(directory + "\\" + file, path)#call the untar function to unzip the images into the correct folder

    print "files have been extracted"

"""
This part of the script looks through the entire directory and finds the data and converts the images to top of
atmosphere reflectance using a the landsat.toa_reflectance_457 and landsat.toa_reflectance_8 functions which are built
into the dnppy module. The function creates new top-of-atmosphere reflectance images for each band in image which are
then used as inputs for the band ratios.

Once the top of atmosphere calculations are complete for each folder "TOA calculated" will be printed.
"""
os.walk(directory)
temp = [x[1] for x in os.walk(directory)]
years = temp[0] #get a list of all the year folders

for year in years: #interate through the list to covert each image's bands
    yrfolder = directory + "\\" + year #build year folder path
    temp = [x[1] for x in os.walk(yrfolder)] #search through that folder for images
    imagefolders = temp[0] #create a list of the image folders
    for folder in imagefolders: #iterate through folders and define what to do for each type of image
        if "LE7" in folder:
            band_nums = [1,2,3,4,5,7]
            meta_path = yrfolder + "\\" + folder + "\\" + folder + "_MTL.txt"
            #outdir = folder
            landsat.toa_reflectance_457(band_nums, meta_path, False)#if it is a Landsat 7 image toa reflectance for Landsat 4, 5, and 7 images
        elif "LT5" in folder:
            band_nums = [1,2,3,4,5,7]
            meta_path = yrfolder + "\\" + folder + "\\" + folder + "_MTL.txt"
            #outdir = folder
            landsat.toa_reflectance_457(band_nums, meta_path, False)#if it is a Landsat 5 image toa reflectance for Landsat 4, 5, and 7 images
        elif "LC8" in folder:
            band_nums = [2,3,4,5,6,7]
            meta_path = yrfolder + "\\" + folder + "\\" + folder + "_MTL.txt"
            #outdir = folder
            landsat.toa_reflectance_8(band_nums, meta_path, False)#if it is a Landsat 8 image toa reflectance for Landsat 8 images

        print "TOA calculated"

"""
This section creates the directories for each of the band ratios that store the outputs from each of the image band
calculations. It goes into each year folder and creates a new folder for each of the different band ratios. When all
the directories are created "Band ratio directories have been created" will be printed.
"""

for year in years: #iterate through the list of years
    GNDVIDir = directory + "\\" + year + "\\" + year + '_GNDVI_outputs'#create the GNDVI folder path
    if not os.path.exists(GNDVIDir):
        os.makedirs(GNDVIDir)#create the directory if it doesn't already exist
    WDIDir = directory + "\\" + year + "\\" + year + '_WDI_outputs'#create the wetland discrimination index folder path
    if not os.path.exists(WDIDir):
        os.makedirs(WDIDir)#create the directory if it doesn't already exist
    ndpiDir = directory + "\\" + year + "\\" + year + '_ndpi_outputs'#create NDPI folder path
    if not os.path.exists(ndpiDir):
        os.makedirs(ndpiDir)#create the NDPI directory if it doesn't already exist
    print "Band ratio directories have been created"#print message when directories have been created

"""
This section of the code is where the band ratios are calculated. The code iterates through each folder and calculates
each of the different band ratio for each image. It calculates all the band ratios within the same for loop for each
image.
"""

for year in years:#iterate through each year folder
    yrfolder = directory + "\\" + year #create the path to the specific folder
    temp = [x[1] for x in os.walk(yrfolder)]#walk through the year folder to access the individual images
    imagefolders = temp[0]#create a list of the image folders
    GNDVIDir = directory + "\\" + year + "\\" + year + '_GNDVI_outputs' #set the path for each band ratio directory in the year folder
    WDIDir = directory + "\\" + year + "\\" + year + '_WDI_outputs'
    ndpiDir = directory + "\\" + year + "\\" + year + '_ndpi_outputs'
    for folder in imagefolders: #interate through each image folder in the particular year
        if "LT5" in folder: #process if the image is a Landsat 5 image
            #set the file paths for each of the necessary bands in the calculation of the band ratios
            blue = directory + "\\" + year + "\\" + folder + "\\" + folder + "_B1_TOA_Ref.tif"
            green = directory + "\\" + year + "\\" + folder + "\\" + folder + "_B2_TOA_Ref.tif"
            red = directory + "\\" + year + "\\" + folder + "\\" + folder + "_B3_TOA_Ref.tif"
            NIR = directory + "\\" + year + "\\" + folder + "\\" + folder + "_B4_TOA_Ref.tif" 
            SWIR1 = directory + "\\" + year + "\\" + folder + "\\" + folder + "_B5_TOA_Ref.tif"
            MIR = directory + "\\" + year + "\\" + folder + "\\" + folder + "_B7_TOA_Ref.tif"

            #call each of the band ratio functions defined above
            GNDVI_457(green, NIR, GNDVIDir)
            WDI_457(NIR, MIR, WDIDir)
            ndpi_457(blue, red, ndpiDir)
            print "GNDVI, wetland Extent index, and NDPI calculated" #once all the indices are calculated this message will be printed

            #access the threshold, the WDI, and the ndpi raster images
            threshold = Raster(GNDVIDir + "\\" + folder + "_TOA_Ref_GNDVI_threshold.tif")
            WDI = Raster(WDIDir + "\\" + folder + "_TOA_Ref_WDI.tif")
            ndpi = Raster(ndpiDir + "\\" + folder + "_TOA_Ref_ndpi.tif")

            #mask both images by the corresponding threshold image by calling the mask function defined earlier
            mask(threshold, WDI, WDIDir)
            mask(threshold, ndpi, ndpiDir)

        elif "LE7" in folder: #process if the image is a Landsat 7 image
            #set the file paths for each of the necessary bands in the calculation of the band ratios
            blue = directory + "\\" + year + "\\" + folder + "\\" + folder + "_B1_TOA_Ref.tif"
            green = directory + "\\" + year + "\\" + folder + "\\" + folder + "_B2_TOA_Ref.tif"
            red = directory + "\\" + year + "\\" + folder + "\\" + folder + "_B3_TOA_Ref.tif"
            NIR = directory + "\\" + year + "\\" + folder + "\\" + folder + "_B4_TOA_Ref.tif" 
            SWIR1 = directory + "\\" + year + "\\" + folder + "\\" + folder + "_B5_TOA_Ref.tif"
            MIR = directory + "\\" + year + "\\" + folder + "\\" + folder + "_B7_TOA_Ref.tif"

            #call each of the band ratio functions defined above
            GNDVI_457(green, NIR, GNDVIDir)
            WDI_457(NIR, MIR, WDIDir)
            ndpi_457(blue, red, ndpiDir)
            print "GNDVI, wetland Extent index, and NDPI calculated"

            #access the threshold, the WDI, and the ndpi raster images
            threshold = Raster(GNDVIDir + "\\" + folder + "_TOA_Ref_GNDVI_threshold.tif")
            WDI = Raster(WDIDir + "\\" + folder + "_TOA_Ref_WDI.tif")
            ndpi = Raster(ndpiDir + "\\" + folder + "_TOA_Ref_ndpi.tif")

            #mask both images by the corresponding threshold image by calling the mask function defined earlier
            mask(threshold, WDI, WDIDir)
            mask(threshold, ndpi, ndpiDir)

        elif "LC8" in folder: #process if the image is a Landsat 7 image
            #set the file paths for each of the necessary bands in the calculation of the band ratios
            blue = directory + "\\" + year + "\\" + folder + "\\" + folder + "_B2_TOA_Ref.tif"
            green = directory + "\\" + year + "\\" + folder + "\\" + folder + "_B3_TOA_Ref.tif"
            red = directory + "\\" + year + "\\" + folder + "\\" + folder + "_B4_TOA_Ref.tif"
            NIR = directory + "\\" + year + "\\" + folder + "\\" + folder + "_B5_TOA_Ref.tif" 
            SWIR1 = directory + "\\" + year + "\\" + folder + "\\" + folder + "_B6_TOA_Ref.tif"
            MIR = directory + "\\" + year + "\\" + folder + "\\" + folder + "_B7_TOA_Ref.tif"

            #call each of the band ratio functions defined above
            GNDVI_8(green, NIR, GNDVIDir)
            WDI_8(NIR, MIR, WDIDir)
            ndpi_8(blue, red, ndpiDir)
            print "GNDVI, wetland Extent index, and NDPI calculated"

            #access the threshold, the WDI, and the ndpi raster images
            threshold = Raster(GNDVIDir + "\\" + folder + "_TOA_Ref_GNDVI_threshold.tif")
            WDI = Raster(WDIDir + "\\" + folder + "_TOA_Ref_WDI.tif")
            ndpi = Raster(ndpiDir + "\\" + folder + "_TOA_Ref_ndpi.tif")

            #mask both images by the corresponding threshold image by calling the mask function defined earlier
            mask(threshold, WDI, WDIDir)
            mask(threshold, ndpi, ndpiDir)

"""
This section of the code calculate the average shoreline extent for each image. The code adds together each shoreline
image from each year and creates a generalized shoreline image that removes the influence of seasonal variations and
tides. Areas with a value of 4 were classified as land throughout every image, areas with a value of 3 were classified
as land in three of the four images, areas with a value of 2 were classified as land in two of the four scenes, areas
with a value of 1 were classified as land in one of the four scenes, and areas with a value of 0 were classified as
water in all the scenes.

Therefore, areas with values of 3 and 4 could be classified as land and areas with a value of 0, 1, or 2 could be
classified as water and a new image would be created that shows the general shoreline extent throughout the year and
incorporates seasonal and tidal variations.
"""
for year in years:#iterate through each year folder
    yrfolder = directory + "\\" + year #set image folder path
    temp = [x[1] for x in os.walk(yrfolder)]
    GNDVIDir = directory + "\\" + year + "\\" + year + '_GNDVI_outputs' #access GNDVI directory
    arcpy.env.workspace = GNDVIDir #set directory as workspace
    threshList = dnppy.core.list_files(True, GNDVIDir, "threshold",['.aux','.xml','.vat','.cpg','.dbf','.tfw'] )#get list of threshold images
    if threshList:
        rasObList = []
        for raster in threshList:
            rasObList.append(arcpy.Raster(raster))#create a list of threshold rasters
        out = sum(rasObList) #sum the threshold rasters together
        print rasObList
        out.save(year + "_shoreline.tif")#save the shoreline image to a new raster
        print "shorline image created" #print message once completed

print "Image processing completed." #message to print when code is done running

print "DONE" #message that will be printed with the entire code has been run for each image in the directory