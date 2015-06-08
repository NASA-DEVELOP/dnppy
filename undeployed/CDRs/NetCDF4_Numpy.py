import numpy as np
import arcpy
import netCDF4
from netCDF4 import Dataset

##read the netCDF file and print metadata

test_file = "C:\\Users\\Lance\\Documents\\GitHub\\dnppy\\undeployed\\CDRs\\PERSIANN-CDR_v01r01_19890523_c20140523.nc"
fh = Dataset(test_file,'r')
print(fh) #this prints all of the metadata info

variables =[] #variables hold the actual data like precipitation, lat values, lon values
dimensions = [] #hold A netCDF dimension used to define the x/y, or lat/lon, coordinates of variables will be placed.

#Below directly calls the attribute metadata info from the Ordered Dict of the Dataset Class. 
fh.cdr_variable #calls the cdr variable
fh.geospatial_lat_min
fh.geospatial_lat_max
fh.geospatial_lon_min
fh.geospatial_lon_max
fh.geospatial_lat_units
fh.geospatial_lat_resolution
fh.geospatial_lon_units
fh.geospatial_lon_resolution
fh.spatial_resolution

var_array = fh.variables[fh.cdr_variable][:] #creates a numpy array of variable, if masked it will be masked array.
v_obj = fh.variables[fh.cdr_variable]
v_obj.dimensions #tells you how the variable is stored.
lat_dim_name = v_obj.dimensions[2]
lon_dim_name = v_obj.dimensions[1]
time_dim_name = v_obj.dimensions[0]

var_array.shape #This returns the length of each dimension for the specified variable in the arrary
lat_dim_size = var_array.shape[2]
lon_dim_size = var_array.shape[1]
time_dim_size = var_array.shape[0]

#In this section I'm looking through the lat/lon variables to find how values are indexed
first_lat = fh.variables[lat_dim_name][0]
last_lat = fh.variables[lat_dim_name][lat_dim_size - 1]
first_lon = fh.variables[lon_dim_name][0]
last_lon = fh.variables[lon_dim_name][lon_dim_size - 1]

#precip_arr.shape = (480,1440) #reshapes the array to match the lat/long earth, lon = columns and lat = rows
"""
Subsetting a box should be easy. So long as I know the index values for corners
I should be able to call it from the value like so,
find the lats/lons of the data that are within the user provided lats/lons.

lat_int = fh.geospatial_lat_resolution
lon_int = fh.geospatial_lon_resolution
fh.variables[fh.cdr_variable][0,loni:lon+i,lati:lat+i]
#pull out specific chunks based on time, lon, lat indexed values.
#User input needs to match geospatial_lat_units and geospatial_lon_units and be divisable by resolution
I need to calculated my index values for lat and lon, which will be based on user input.
Steps:
1) Check to see if user lat/lon units match the data's lat/lon units, if so convert
2) Convert units if necessary
3) Find out where the user coordinates fall on the grid of lat/lons which set at resolution intervals

lat_arr[0] <- 59.875
lat_arr[479] <- -59.875
lon_arr[0] <- 0.125
lon_arr[1439] <- 359.875
"""
#User defined bounding box, format (lat,lon)
TL = [42.258,273.501]
TR = [42.258,275.503]
BR = [37.261,275.503]
BL = [37.261,273.501]
# Assume user defined bounding box will be decimal degree
# 1) Check to see if user lat/lon units match data's lat/lon
# I don't know that CDRs will all have same lat/long units. But makes sense that they would.
if fh.geospatial_lon_min < 0 & fh.geospatial_lon_min > -180:
    then units = 'Decimal Degree'
if fh.geospatial_lon_max > 180:
    then match
#Subset
subset_array = v_obj[0,lon1i:lon2i,lat1i:lat2i]
#Save numpy array as raster or tif
raster = arcpy.NumPyArrayToRaster(subset_array)
raster.save(output_workplace + // name)
