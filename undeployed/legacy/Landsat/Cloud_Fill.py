import os
import numpy
import osr
from osgeo import gdal
from scipy import misc
import rasterio

folder_path=r"C:\Users\sbarron\Desktop\Test\Output\Newfolder"

#Part 1: Convert NoData values to -9999 in order to solve patching issue later on.
#Need to run first part of script for each individual file.
file1= "Clip_CGSM_1989_B3_atm.tif"

#Open raster twice, using rasterio and gdal
raster= rasterio.open(file1)
raster1= gdal.Open(file1)

#Create array of the same size as the input raster, but fill it with place holder values of 0.
Array= numpy.zeros(shape=(raster.height,raster.width))

raster.read_band(1)

#For loop reads each line in the input raster as an array, if pixel value== "nan", replaces value with -9999.
#During each iteration, values replace placeholder 0 values in the created array above.
x=0
for line in raster.read_band(1):
    List=list()
    for pixel in line:
        if str(pixel)== "nan":
            List.append("-9999.0")
        else:
            List.append(pixel)
    Array[x]= List
    x=x+1

#Once the for loop is finished, we need to conver the numpy array into a raster.
def array_to_raster(array, output_file):
    dst_filename = output_file

    #Get values 
    x_pixels = raster.width  # number of pixels in x
    y_pixels = raster.height  # number of pixels in y
    PIXEL_SIZE = 30  # size of the pixel...        
    x_min = raster1.GetGeoTransform()[0]  
    y_max = raster1.GetGeoTransform()[3]  # x_min & y_max are like the "top left" corner.
    wkt_projection = raster1.GetProjection()

    driver = gdal.GetDriverByName('GTiff')

    dataset = driver.Create(
        dst_filename,
        x_pixels,
        y_pixels,
        1,
        gdal.GDT_Float32, )

    dataset.SetGeoTransform((
        x_min,    # 0
        PIXEL_SIZE,  # 1
        0,                      # 2
        y_max,    # 3
        0,                      # 4
        -PIXEL_SIZE))  

    dataset.SetProjection(wkt_projection)
    dataset.GetRasterBand(1).WriteArray(array)
    dataset.FlushCache()  # Write to disk.
    return dataset, dataset.GetRasterBand(1)  #If you need to return, remenber to return  also the dataset because the band don`t live without dataset.


array_to_raster(Array, "CGSM_1989_B3_9999.tif")

print "Process Completed."

#Part 2
#This portion will then fill in the holes left by clouds in file1 with data from file2
file1= "Input1.tif"
file2= "Input2.tif"
Output_File= "Output_File.tif"

os.system('gdal_calc.py -A%s -B%s --outfile=%s --calc="((A==-9999)*B)+((A>=-9000)*A)" --type="Float32" --NoDataValue=-9999.0' % (file1,file2,Output_File))

